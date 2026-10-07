"""Adapt local ORCS entity projections to the owner-approved v6 evidence model.

This is an output stage for v02 onward, not a filtering engine or retrieval
stage. Native screen/publication records and saved reference annotations remain
separate. No historical workbook or evidence identifier is rewritten in place.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from .evidence_model import HEADERS, VERSION, build_evidence, canonical, validate_evidence, write_ledger, v6_allowed
from .orcs_fields import DIRECT, CROSSWALKS

PUBLICATION_FIELDS = {'TITLE':'title_original','AUTHORS':'author_list_reported',
    'JOURNAL':'journal_reported','PMID':'pmid','DOI':'doi'}


def adapt(projection, native_screens, publications, annotations, manifest, profile):
    """Return a v6 projection and ledger from explicit local source records.

    Projection roles must contain native SCREEN_ID mappings. Unmatched or
    accession-less cell-line annotations are retained as issues; no cell_line
    entity or accession is guessed. Input projections are never modified.
    """
    if not v6_allowed(profile['profile_id'],profile.get('profile_version',0),profile.get('schema_version')):
        raise ValueError('Only v02-or-later output is authorized')
    p = copy.deepcopy(projection)
    native = {str(r['SCREEN_ID']):r for r in native_screens}
    refs = {r['value']:r for r in annotations['cell_lines']}
    issues = []; observations = []; ref_groups = {}
    def source(name, typ, key, raw, url, local_path, date):
        return {'name':name,'type':typ,'native_record_id':str(key),'native_url':url,
                'local_path':local_path,'retrieved_at':date,
                'retrieval_method':'offline saved metadata; no new retrieval',
                'record_sha256':hashlib.sha256(canonical(raw).encode()).hexdigest(),
                'release':annotations.get('cellosaurus_version') if name == 'Cellosaurus' else manifest.get('orcs_release')}
    def observe(src, entity_type, entity_id, fields, claim, values, raw, basis='structured_field', status='direct', **extra):
        observations.append({'source':src,'supports':{'entity_type':entity_type,'entity_id':entity_id,'fields':fields},
            'claim':claim,'supporting_value':values,'raw_record':raw,
            'evidence_basis':basis,'evidence_status':status,**extra})
    for row in p['sheets']['Screens']:
        sid = row['screen_id']; role = p['roles'].get(sid)
        if not role or str(role['SCREEN_ID']) not in native:
            raise ValueError(f'Missing native screen mapping: {sid}')
        n = native[str(role['SCREEN_ID'])]; fields = []; values = {}; transforms = []
        if row.get('publication_id'):
            pub = next((r for r in p['sheets'].get('Publications',[]) if r['publication_id']==row['publication_id']),None)
            mappings=p.get('native_mapping',{}).get('publications',[])
            native_pub_ids={str(m['PUBLICATION_ID']) for m in mappings if m['publication_id']==row['publication_id']}
            explicit=pub and ((n.get('SOURCE_TYPE')=='pubmed' and str(pub.get('pmid'))==n.get('SOURCE_ID')) or
                (n.get('SOURCE_TYPE')=='doi' and pub.get('doi')==n.get('SOURCE_ID')) or
                any(str(r['PUBLICATION_ID']) in native_pub_ids and str(n['SCREEN_ID']) in [str(x) for x in r.get('SCREEN_IDS',[])] for r in publications))
            if not explicit:raise ValueError(f'Publication association lacks explicit native identity: {sid}')
            fields.append('publication_id');values.update(SOURCE_TYPE=n.get('SOURCE_TYPE'),SOURCE_ID=n.get('SOURCE_ID'))
            transforms.append({'rule':'Exact native publication identity or shared publication SCREEN_IDS membership',
                'target_field':'publication_id','target_value':row['publication_id']})
        for key, dest in DIRECT.items():
            if row.get(dest) not in (None, ''):
                if row[dest] != n.get(key):
                    raise ValueError(f'Screen field needs separately attributed evidence: {sid}/{dest}')
                fields.append(dest); values[key] = n[key]
        for key, dest in [('SCREEN_FORMAT','screen_format_normalized'),('METHODOLOGY','perturbation_type_normalized')]:
            if row.get(dest) not in (None, ''):
                if CROSSWALKS[key].get(n.get(key)) != row[dest]:
                    raise ValueError(f'Unsupported normalization: {sid}/{dest}')
                fields.append(dest); values[key] = n[key]
                transforms.append({'source_field':key,'target_field':dest,'reported':n[key],'normalized':row[dest],'rule':CROSSWALKS[key]})
        src = source('BioGRID ORCS','screen',n['SCREEN_ID'],n,
            f"https://orcs.thebiogrid.org/Screen/{n['SCREEN_ID']}", 'data/orcs/screen-index.json',manifest.get('cache_retrieved_at'))
        src['native_field_paths'] = sorted(values)
        observe(src,'screen',sid,fields,
            f"ORCS reports the listed metadata values for screen {n['SCREEN_ID']}.",
            '; '.join(f'{k}={v}' for k,v in values.items()),n,transformations=transforms,
            filter_role=copy.deepcopy(role))
        ann = refs.get(n.get('CELL_LINE')); accession = (ann or {}).get('accession')
        row['cellosaurus_accession'] = None
        if not accession or not str(accession).startswith('CVCL_'):
            issues.append({'screen_id':sid,'cell_line_reported':n.get('CELL_LINE'),'issue':'No resolved Cellosaurus accession; no cell_line entity generated'})
            row['curation_status']=(row.get('curation_status') or '')+'; unresolved reference accession'
            continue
        row['cellosaurus_accession'] = accession
        group = ref_groups.setdefault(accession, {'annotations':{},'targets':[]})
        group['annotations'][canonical(ann)] = ann
        group['targets'].append({'entity_type':'screen','entity_id':sid,'fields':['cellosaurus_accession'],
            'reported_cell_line':n.get('CELL_LINE'),'match_method':ann.get('match_method'),
            'secondary_accessions':ann.get('secondary_accessions'),'review_issues':ann.get('review_issues',[])})
    for acc, group in sorted(ref_groups.items()):
        records = list(group['annotations'].values())
        categories = {r.get('category') for r in records}
        status = 'conflicting' if len(categories) > 1 else ('unresolved' if None in categories or any(r.get('review_issues') for r in records) else 'direct')
        raw = {'saved_annotation_records':records}
        src = source('Cellosaurus','cell_line',acc,raw,f'https://www.cellosaurus.org/{acc}',
            'data/cellosaurus/orcs-annotations/annotations.json',annotations.get('retrieval_date'))
        supported = [field for field in ['accession','category','description'] if any(r.get(field) not in (None,'') for r in records)]
        src['native_field_paths'] = supported
        src['reference_locators'] = [r.get('reference_locator') for r in records]
        observe(src,'cell_line',acc,supported,
            'Cellosaurus provides the accession, category, and available description for this cell line in the saved reference annotations.',
            '; '.join(f"{r['value']}: "+'; '.join(f'{k}={r[k]}' for k in supported if r.get(k) not in (None,'')) for r in records),
            raw,basis='reference_lookup',status=status,annotation_targets=group['targets'])
    for row in p['sheets'].get('Publications', []):
        # Header aliases change presentation only, not the scientific record.
        for old,new in [('author_list_ reported','author_list_reported'),('retrival_sources','retrieval_sources')]:
            if old in row:
                if row.get(new) not in (None,'',row[old]):raise ValueError(f'Conflicting legacy header values: {new}')
                row[new] = row.pop(old)
        mappings = p.get('native_mapping', {}).get('publications', [])
        keys = {str(m['PUBLICATION_ID']) for m in mappings if m['publication_id'] == row['publication_id']}
        matched = [r for r in publications if str(r['PUBLICATION_ID']) in keys or
            (row.get('pmid') and str(r.get('PMID')) == str(row['pmid'])) or
            (row.get('doi') and r.get('DOI') == row['doi'])]
        if not matched:issues.append({'publication_id':row['publication_id'],'issue':'No exact shared publication source matched; retained values require separately attributed evidence'})
        for raw in matched:
            fields = [dest for key,dest in PUBLICATION_FIELDS.items() if row.get(dest) not in (None,'') and str(row[dest]) == str(raw.get(key))]
            if not fields: continue
            transforms=[]
            if row.get('publication_year') is not None and str(raw.get('PUBLICATION_DATE',''))[:4] == str(row['publication_year']):
                fields.append('publication_year')
                transforms.append({'source_field':'PUBLICATION_DATE','target_field':'publication_year','rule':'Reported date year component','reported':raw['PUBLICATION_DATE'],'normalized':row['publication_year']})
            src = source('BioGRID ORCS','publication',raw['PUBLICATION_ID'],raw,
                raw.get('PUBLICATION_URL',f"https://orcs.thebiogrid.org/Dataset/{raw['PUBLICATION_ID']}"),
                'data/orcs/publication-index.json',raw.get('RETRIEVED_AT',manifest.get('publication_retrieved_at')))
            src['raw_source_file']=raw.get('SOURCE_METADATA_FILE')
            src['raw_source_sha256']=raw.get('SOURCE_METADATA_SHA256')
            src['native_field_paths'] = [k for k,v in PUBLICATION_FIELDS.items() if v in fields]
            if 'publication_year' in fields:src['native_field_paths'].append('PUBLICATION_DATE')
            observe(src,'publication',row['publication_id'],fields,
                'ORCS reports the publication identifiers and available bibliographic metadata in the listed fields.',
                '; '.join(f'{k}={raw[k]}' for k in src['native_field_paths']),raw,
                status='conflicting' if raw.get('REVIEW_ISSUES') else 'direct',transformations=transforms)
    rows, ledger = build_evidence(observations,run_id=manifest['run_id'],profile_id=profile['profile_id'],
        profile_version=profile['profile_version'],profile_schema=profile.get('schema_version'),tool={'name':VERSION,'input_tool_version':manifest.get('tool_version'),'input_hashes':manifest.get('input_hashes',{}),'code_hashes':manifest.get('code_hashes',{})})
    validate_evidence(rows,ledger)
    p['sheets'].pop('Sources & Evidence',None); p['sheets'].pop('Discovery Resources',None)
    p['sheets']['Evidence'] = rows
    for row in p['sheets']['Screens']:
        row['source_evidence_ids'] = '; '.join(e['evidence_id'] for e in ledger if
            any(s['entity_id'] == row['screen_id'] and s['entity_type']=='screen' for s in e['supports']) or
            any(t['entity_id'] == row['screen_id'] for t in e['annotation_targets']))
    for row in p['sheets'].get('Publications',[]):
        row['evidence_id_link'] = '; '.join(e['evidence_id'] for e in ledger if any(s['entity_id']==row['publication_id'] and s['entity_type']=='publication' for s in e['supports']))
    p['version'] = VERSION; p['template_version'] = 'v6'; p['evidence_issues'] = issues
    # The complete original projection remains a separately hashed snapshot in
    # the output package, including old evidence and diagnostic/reviewer fields.
    for e in ledger:e['input_projection_snapshot']='source-projection.json'
    p['headers'] = {name:list(headers) for name,headers in p.get('headers',{}).items() if name not in {'Sources & Evidence','Discovery Resources'}}
    p['headers']['Evidence'] = HEADERS
    p['sources_policy']='Preserved template example content; Sources counts are not measured run results.'
    # Source diagnostics remain in the snapshot, roles and ledger. These two
    # notes fields belong to the reviewer and must start empty on every new run.
    for sheet, field in [('Publications','publication_notes'),('Screens','screen_notes')]:
        for row in p['sheets'].get(sheet,[]):
            row[field] = None
            row.pop('reviewer_decision',None)
            row.pop('reviewer_notes',None)
        if sheet in p['headers']:
            p['headers'][sheet] = [h for h in p['headers'][sheet] if h not in {'reviewer_decision','reviewer_notes'}]
    return p,ledger


def main():
    """Prepare a new v6 output package from a v02+ run; never mutate its inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    root=args.root; run=args.run
    manifest=read(run/'run_manifest.json')
    manifest['code_hashes']={**manifest.get('code_hashes',{}),**{str(x.relative_to(root)):hashlib.sha256(x.read_bytes()).hexdigest() for x in
        [root/'src/deathmap_ai/evidence_model.py',Path(__file__)]}}
    p,ledger = adapt(read(run/'projection.json'),read(root/'data/orcs/screen-index.json'),
        read(root/'data/orcs/publication-index.json'),read(run/'reference_annotations.json'),
        manifest,read(run/'profile.json'))
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'source-projection.json').write_bytes((run/'projection.json').read_bytes())
    (args.output/'projection.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
    write_ledger(args.output/'evidence-ledger.jsonl',ledger)
    (args.output/'evidence-model-manifest.json').write_text(json.dumps({'version':VERSION,
        'input_run':str(run.resolve()),'template':'data/templates/DeathMap-AI-output.xlsx',
        'input_files':{str(x.resolve()):hashlib.sha256(x.read_bytes()).hexdigest() for x in
            [run/'projection.json',run/'run_manifest.json',run/'profile.json',run/'reference_annotations.json',root/'data/orcs/screen-index.json',root/'data/orcs/publication-index.json']},
        'issues':p['evidence_issues'],'evidence_count':len(ledger),'network_requests':0},indent=2),encoding='utf-8')
    print(args.output)


if __name__ == '__main__':
    main()
