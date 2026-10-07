"""Execute the owner-authorized CRISPR biological-classes pilot offline.

The profile supplies every gate and regex. Each native screen is audited once;
publication companions retain their separate role. New canonical JSON, evidence
ledger and workbook inputs are written in an exclusive run directory. No network,
experimental data or validation-only study inventory is accessed.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
from urllib.parse import quote

from .orcs_fields import DIRECT,CROSSWALKS
from .orcs_evidence_v6 import adapt
from .evidence_model import build_evidence,validate_evidence,write_ledger

PROFILE='searches/orcs/orcs-crispr-biological-classes-pilot-v01/profile.json'
VERSION='orcs-profile-refresh-v1.1'


def _hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _write(path,value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def _key(record):
    pair=(record.get('SOURCE_TYPE'),record.get('SOURCE_ID'))
    return pair if all(isinstance(x,str) and x.strip() not in ('','-') for x in pair) else None


def test_rule(node,screen,annotation):
    """Evaluate a supplied rule and return status plus exact values/match spans.

    Regex searches each field independently, with IGNORECASE and no DOTALL.
    Missing means absent/null/blank/dash, not failed scientific eligibility.
    Exact rules tokenize only for comparison; all native values stay unchanged.
    """
    if 'all' in node:
        children=[test_rule(n,screen,annotation) for n in node['all']]
        status='pass' if all(c['status']=='pass' for c in children) else ('fail' if any(c['status']=='fail' for c in children) else 'missing')
        return {'status':status,'children':children}
    record=screen if node['scope']=='screen' else (annotation or {})
    op=node['operator'];fields=node.get('fields',[node.get('field')]);observations=[]
    for field in fields:
        value=record.get(field);missing=value is None or (isinstance(value,str) and value.strip() in ('','-'))
        matches=[]
        if not missing:
            if not isinstance(value,str):raise ValueError(f'Non-string rule field: {field}')
            if op=='any_exact':
                matches=[{'token':t.strip()} for t in value.split('|') if t.strip() in node['values']]
            elif op=='regex':
                matches=[{'text':m.group(),'span':[m.start(),m.end()]} for m in re.finditer(node['pattern'],value,re.IGNORECASE)]
        observations.append({'scope':node['scope'],'field':field,'native_value':value,'missing':missing,'matches':matches})
    if op=='missing':status='pass' if observations[0]['missing'] else 'fail'
    else:status='pass' if any(o['matches'] for o in observations) else ('missing' if all(o['missing'] for o in observations) else 'fail')
    return {'status':status,'observations':observations}


def evaluate(screens,publications,annotations,profile):
    """Audit screens and expand seed publications without excluding companions.

    Exact publication pairs and annotation values must be unique. Ambiguous
    inputs raise an error instead of manufacturing an association. Missing joins
    remain explicit and cannot seed publication expansion.
    """
    pubs={};refs={};seen=set()
    for pub in publications:
        key=_key(pub)
        if key is None:continue
        if key in pubs:raise ValueError('Ambiguous publication pair')
        pubs[key]=pub
    for ann in annotations['cell_lines']:
        if ann['value'] in refs:raise ValueError('Ambiguous annotation value')
        refs[ann['value']]=ann
    audit=[];anchors={}
    for native in screens:
        sid=native['SCREEN_ID']
        if sid in seen:raise ValueError('Duplicate native screen ID')
        seen.add(sid);ann=refs.get(native.get('CELL_LINE'))
        gates=[test_rule(n,native,ann) for n in profile['common_filters']]
        rules={r['rule_id']:test_rule(r['test'],native,ann) for r in profile['candidate_rules']}
        passed=[rid for rid,result in rules.items() if result['status']=='pass']
        seed=all(g['status']=='pass' for g in gates) and bool(passed)
        key=_key(native);pub=pubs.get(key)
        item={'SCREEN_ID':sid,'native':native,'common_gates':gates,'candidate_rules':rules,
            'matched_rule_ids':passed,'common_filters_pass':all(g['status']=='pass' for g in gates),
            'role':'direct_rule_candidate' if seed else 'excluded','PUBLICATION_ID':pub['PUBLICATION_ID'] if pub else None,
            'annotation_review_issues':(ann or {}).get('review_issues',[]),'publication_join_status':'direct' if pub else 'unresolved'}
        audit.append(item)
        if seed and key and pub:anchors.setdefault(key,[]).append(sid)
    for item in audit:
        key=_key(item['native'])
        if item['role']!='direct_rule_candidate' and key in anchors:item['role']='publication_companion'
        item['seed_screen_ids']=anchors.get(key,[]) if item['role']=='publication_companion' else []
    counts=Counter(i['role'] for i in audit)
    summary={'examined':len(audit),'direct_rule_candidates':counts['direct_rule_candidate'],
        'publication_companions':counts['publication_companion'],'excluded':counts['excluded'],
        'retained_screens':counts['direct_rule_candidate']+counts['publication_companion'],
        'seed_publications':len(anchors),'retained_publications':len({i['PUBLICATION_ID'] for i in audit if i['role']!='excluded' and i['PUBLICATION_ID'] is not None}),
        'rule_seed_counts':{r['rule_id']:sum(i['role']=='direct_rule_candidate' and r['rule_id'] in i['matched_rule_ids'] for i in audit) for r in profile['candidate_rules']},
        'companions_failing_common_filters':sum(i['role']=='publication_companion' and not i['common_filters_pass'] for i in audit),
        'retained_missing_publication_join':sum(i['role']!='excluded' and i['PUBLICATION_ID'] is None for i in audit),
        'retained_annotation_review_issues':sum(i['role']!='excluded' and bool(i['annotation_review_issues']) for i in audit),
        'network_requests':0,'interpretation':'Unadjudicated candidates; no qualifying-study coverage or dataset accessibility claim.'}
    return audit,summary


def project(audit,publications):
    """Project native metadata and explicit identities, leaving unsupported entities empty."""
    retained=[i for i in audit if i['role']!='excluded'];native_pubs={r['PUBLICATION_ID']:r for r in publications}
    pubids=sorted({i['PUBLICATION_ID'] for i in retained if i['PUBLICATION_ID'] is not None},key=lambda x:int(x))
    mapping={key:f'PUB-{i:04d}' for i,key in enumerate(pubids,1)};pubrows=[]
    for key in pubids:
        n=native_pubs[key];row={'publication_id':mapping[key],'retrieval_sources':'BioGRID ORCS saved publication metadata',
            'evidence_status':'conflicting' if n.get('REVIEW_ISSUES') else 'direct',
            'publication_notes':None}
        for source,dest in [('TITLE','title_original'),('AUTHORS','author_list_reported'),('JOURNAL','journal_reported'),('PMID','pmid'),('DOI','doi')]:
            if n.get(source) not in (None,'','-'):row[dest]=n[source]
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}',n.get('PUBLICATION_DATE') or ''):row['publication_year']=int(n['PUBLICATION_DATE'][:4])
        if row.get('pmid'):row['pmid_link']=f'https://pubmed.ncbi.nlm.nih.gov/{row["pmid"]}/'
        if row.get('doi'):row['doi_link']='https://doi.org/'+quote(row['doi'],safe='/')
        pubrows.append(row)
    rows=[];roles={}
    for index,item in enumerate(sorted(retained,key=lambda i:int(i['SCREEN_ID'])),1):
        n=item['native'];sid=f'SCR-{index:04d}';roles[sid]={k:item[k] for k in ['SCREEN_ID','role','matched_rule_ids','seed_screen_ids','common_filters_pass']}
        review=bool(item['annotation_review_issues']) or item['publication_join_status']=='unresolved'
        row={'screen_id':sid,'publication_id':mapping.get(item['PUBLICATION_ID']),
            'curation_status':item['role']+'; inferred class candidate; unreviewed'+('; unresolved review issue' if review else ''),
            'screen_notes':None}
        for source,dest in DIRECT.items():
            if n.get(source) not in (None,'','-'):row[dest]=n[source]
        for source,dest in [('SCREEN_FORMAT','screen_format_normalized'),('METHODOLOGY','perturbation_type_normalized')]:
            if n.get(source) in CROSSWALKS[source]:row[dest]=CROSSWALKS[source][n[source]]
        rows.append(row)
    return {'sheets':{'Publications':pubrows,'Screen Groups':[],'Screens':rows,'Datasets':[],'Screen-Dataset Links':[]},
        'roles':roles,'native_mapping':{'publications':[{'PUBLICATION_ID':k,'publication_id':v} for k,v in mapping.items()]}}


def execute(root,run_id=None,profile_path=PROFILE):
    """Validate, run and write a new offline CRISPR package; refuse existing output paths."""
    root=Path(root).resolve();profile_path=Path(profile_path).as_posix();profile=_read(root/profile_path)
    allowed={PROFILE,'searches/orcs/cancer-cell-crispr-knockout-v01/profile.json','searches/orcs/cancer-cell-crispr-knockout-v02/profile.json'}
    if profile_path not in allowed:raise ValueError('Only the three owner-authorized profiles are supported')
    categorical=profile_path!=PROFILE
    spec=importlib.util.spec_from_file_location('pilot_preflight',root/'scripts/validate_orcs_pilot_profiles.py')
    validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
    preflight=validator.preflight(root,root/profile_path) if not categorical else {'profile_sha256':_hash(root/profile_path),'input_hashes':{v:_hash(root/v) for v in profile['input'].values()},'network_requests':0}
    native=_read(root/profile['input']['screen_metadata']);pubs=_read(root/'data/orcs/publication-index.json');anns=_read(root/profile['input']['reference_annotations'])
    from .orcs_filters import validate_inputs
    validate_inputs(native,anns,_read(root/'data/orcs/cache-summary.json'),_hash(root/profile['input']['screen_metadata']))
    cache=_read(root/'data/orcs/cache-summary.json');pubmanifest=_read(root/'data/orcs/publication-index.manifest.json')
    if len(native)!=cache['screens_retrieved'] or len(pubs)!=pubmanifest['publication_count'] or anns['cache_sha256']!=_hash(root/profile['input']['screen_metadata']):raise ValueError('Catalog completeness or annotation hash mismatch')
    stamp=datetime.now(timezone.utc);run_id=run_id or stamp.strftime('%Y%m%dT%H%M%S%fZ')
    if not re.fullmatch(r'[A-Za-z0-9_-]+',run_id):raise ValueError('Unsafe run ID')
    out=root/'outputs/orcs'/Path(profile_path).parent.name/run_id
    if out.exists():raise FileExistsError(out)
    # Existing outputs are frozen inputs to the preservation check, never seeds.
    preserve_paths=[p for folder in ['outputs','data/orcs','data/cellosaurus','data/templates'] for p in (root/folder).rglob('*') if p.is_file()]
    before={p.relative_to(root).as_posix():_hash(p) for p in preserve_paths}
    if categorical:
        from .orcs_profile_rules import evaluate as evaluate_categorical
        audit,summary=evaluate_categorical(native,pubs,anns,profile)
    else:audit,summary=evaluate(native,pubs,anns,profile)
    original=project(audit,pubs)
    manifest={'run_id':run_id,'profile_id':profile['profile_id'],'profile_version':profile['profile_version'],
        'tool_version':VERSION,'started_at':stamp.isoformat(),'cache_retrieved_at':cache['retrieved_at'],
        'reference_retrieval_date':anns['retrieval_date'],'network_requests':0,
        'input_hashes':{**preflight['input_hashes'],profile_path:_hash(root/profile_path),'data/orcs/publication-index.json':_hash(root/'data/orcs/publication-index.json'),'data/templates/DeathMap-AI-output.xlsx':_hash(root/'data/templates/DeathMap-AI-output.xlsx')},
        'code_hashes':{p.relative_to(root).as_posix():_hash(p) for p in [Path(__file__),root/'src/deathmap_ai/orcs_profile_rules.py',root/'src/deathmap_ai/orcs_filters.py',root/'src/deathmap_ai/orcs_fields.py',root/'src/deathmap_ai/evidence_model.py',root/'src/deathmap_ai/orcs_evidence_v6.py']},
        'semantics':{'missing':[None,'','-'],'regex':'independent field search; IGNORECASE; no DOTALL','exact_values':'scalar case-sensitive' if profile['profile_id']=='orcs-cancer-cell-crispr-knockout-v01' else 'literal separator, case-sensitive' if categorical else 'split |, trim, case-sensitive','annotations':'exact native CELL_LINE lookup','classification':'candidate; no immune-pressure gate'},'status':'json_complete_workbook_pending'}
    projection,ledger=adapt(original,native,pubs,anns,manifest,profile)
    # Class inference is independent of direct source metadata and reference
    # annotations. Rule traces/spans remain in the ledger, not promoted to facts.
    inference=[];sidmap={v['SCREEN_ID']:k for k,v in projection['roles'].items()}
    annotation_evidence={t['entity_id']:e['evidence_id'] for e in ledger if e['source']['name']=='Cellosaurus' for t in e['annotation_targets']}
    for item in audit:
        if item['role']!='direct_rule_candidate':continue
        sid=sidmap[item['SCREEN_ID']];n=item['native']
        inference.append({'source':{'name':'BioGRID ORCS','type':'screen','native_record_id':n['SCREEN_ID'],
            'native_url':f'https://orcs.thebiogrid.org/Screen/{n["SCREEN_ID"]}','local_path':'data/orcs/screen-index.json',
            'retrieved_at':cache['retrieved_at']},'supports':{'entity_type':'screen','entity_id':sid,'fields':['curation_status']},
            'claim':'The configured profile retains this screen as a candidate; scientific eligibility remains unreviewed.',
            'supporting_value':'Matched rules: '+', '.join(item['matched_rule_ids']),
            'raw_record':n,'evidence_basis':'inferred','evidence_status':'inferred',
            'rule_evidence':item['candidate_rules'],'descriptive_tags':item.get('descriptive_tags',{}),'reference_lookup_evidence_id':annotation_evidence.get(sid)})
    extra,extra_ledger=build_evidence(inference,run_id=run_id,profile_id=profile['profile_id'],profile_version=profile['profile_version'],profile_schema=profile.get('schema_version'),first_index=len(ledger)+1,tool={'name':VERSION,'code_hashes':manifest['code_hashes']})
    projection['sheets']['Evidence'].extend(extra);ledger.extend(extra_ledger)
    extra_by_sid={r['supports_entity_id']:r['evidence_id'] for r in extra}
    for row in projection['sheets']['Screens']:
        if row['screen_id'] in extra_by_sid:row['source_evidence_ids']+='; '+extra_by_sid[row['screen_id']]
    validate_evidence(projection['sheets']['Evidence'],ledger)
    out.mkdir(parents=True)
    shutil.copyfile(root/profile_path,out/'profile.json');shutil.copyfile(root/profile['input']['reference_annotations'],out/'reference_annotations.json')
    for name,value in [('run_manifest',manifest),('preflight',preflight),('screen_audit',audit),('summary',summary),('source-projection',original),('projection',projection)]:_write(out/f'{name}.json',value)
    write_ledger(out/'evidence-ledger.jsonl',ledger)
    changed=[rel for rel,h in before.items() if _hash(root/rel)!=h]
    _write(out/'preservation.json',{'before':before,'changed_original_files':changed})
    if changed:raise ValueError('Original input/output changed during execution')
    return out


def run_and_export(root,run_id=None,profile_path=PROFILE):
    """Run metadata discovery and export a new workbook from the active template.

    Validate the template first to avoid an expensive run with an unusable model.
    Canonical JSON survives any export failure, with explicit manifest status.
    Existing run directories and owner-authored workbooks are never overwritten.
    """
    from .excel_export import approved_template,export
    template=approved_template(root)
    out=execute(root,run_id=run_id,profile_path=profile_path)
    manifest=_read(out/'run_manifest.json')
    try:
        workbook=export(out,template)
    except Exception as error:
        manifest.update(status='json_complete_workbook_failed',workbook_error=str(error))
        _write(out/'run_manifest.json',manifest)
        raise
    manifest.update(status='json_and_workbook_complete',primary_workbook=workbook.name,
                    workbook_sha256=_hash(workbook),excel_writer='openpyxl')
    _write(out/'run_manifest.json',manifest)
    return out


def main():
    """Run the selected cached search and export its portable review workbook."""
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--profile',default=PROFILE);args=p.parse_args()
    print(run_and_export(args.root,profile_path=args.profile))


if __name__=='__main__':main()
