"""Apply the accepted seven-field ORCS profile to saved metadata only.

Native rows and exact Cellosaurus joins remain separate. Every screen receives
one outcome; publication siblings are context relationships, never extra hits.
The runner has no network client and refuses unsupported profile semantics.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .orcs_paths import resolve_historical

VERSION = 'orcs-filter-v1.0'
PROFILE = 'searches/orcs/cancer-cell-crispr-knockout-v01/profile.json'
CACHE = 'data/orcs/screen-index.json'
ANNOTATIONS = 'data/cellosaurus/orcs-annotations/annotations.json'
WORKBOOK = 'data/templates/DeathMap-AI-v1-reference-output.xlsx'
EXPECTED = {'CELL_LINE': ['Cancer cell line'], 'ENZYME': ['Cas9'],
 'LIBRARY_TYPE': ['CRISPRn'], 'METHODOLOGY': ['Knockout'], 'SCREEN_FORMAT': ['Pool'],
 'ORGANISM_OFFICIAL': ['Homo sapiens', 'Mus musculus'],
 'PHENOTYPE': ['cell proliferation', 'cell viability', 'cell cycle progression', 'cell migration']}


def sha(path):
    """Return a byte hash without interpreting historical scientific content."""
    h = hashlib.sha256()
    with resolve_historical(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    """Read UTF-8 JSON, rejecting malformed data before execution."""
    return json.loads(resolve_historical(path).read_text(encoding='utf-8'))


def write(path, value):
    """Write a new, reviewable JSON artifact in an exclusively created run."""
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def publication_key(row):
    """Return an exact valid PMID/DOI pair, or None; do not normalize identities."""
    typ, identifier = row.get('SOURCE_TYPE'), row.get('SOURCE_ID')
    if not isinstance(identifier, str):
        return None
    if typ == 'pubmed' and re.fullmatch(r'[1-9][0-9]*', identifier):
        return typ, identifier
    if typ == 'doi' and re.fullmatch(r'10\.\d{4,9}/\S+', identifier):
        return typ, identifier
    return None


def validate_profile(p):
    """Accept only the owner's current profile, failing on unknown operations."""
    keys = {'profile_id','profile_version','created_date','resource','purpose','status','path_base',
            'input','annotation_join','filter_logic','filters','unfiltered_fields','review_handling'}
    if set(p) != keys or p['profile_id'] != 'orcs-cancer-cell-crispr-knockout-v01' or p['profile_version'] != 1:
        raise ValueError('Unsupported profile identity or keys')
    if p['resource'] != 'ORCS' or p['path_base'] != 'repository_root' or p['input'] != {'screen_metadata': CACHE, 'reference_annotations': ANNOTATIONS}:
        raise ValueError('Unsupported resource/input paths')
    if p['filter_logic'] != {'between_fields':'AND','within_each_value_list':'OR','comparison':'exact_case_sensitive'}:
        raise ValueError('Unsupported filter logic')
    expected_filters = {k: {'values': v} for k,v in EXPECTED.items()}
    expected_filters['CELL_LINE'].update(source='joined_reference_annotation',field='category')
    if p['filters'] != expected_filters or list(p['filters']) != list(EXPECTED):
        raise ValueError('Profile differs from approved seven criteria')
    join = {'screen_field':'CELL_LINE','annotation_collection':'cell_lines','annotation_key':'value','comparison':'exact','category_field':'category','missing_category':'does_not_satisfy_category_filter','preserve_annotation_fields':['accession','secondary_accessions','match_method','reference_locator','review_issues']}
    review = {'annotation_review_issues':'preserve_and_flag_without_an_additional_exclusion_rule','missing_category':'retain_in_a_separate_unresolved_review_list_if_other_filters_pass','interpretation':'Matching screens form a candidate subset for review, not confirmed qualifying studies.'}
    if p['annotation_join'] != join or p['unfiltered_fields'] != ['EXPERIMENTAL_SETUP'] or p['review_handling'] != review:
        raise ValueError('Unsupported join/review handling')


def validate_inputs(rows, annotations, summary, cache_hash, expected_count=2217):
    """Check completeness, scalar schema, exact unique keys and reference cache hash."""
    if not isinstance(rows, list) or len(rows) != expected_count or summary.get('screens_retrieved') != len(rows):
        raise ValueError('Incomplete ORCS cache')
    if annotations.get('cache_sha256') != cache_hash:
        raise ValueError('Annotation/cache hash mismatch')
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or not all(isinstance(row.get(k), str) for k in ['SCREEN_ID','SOURCE_TYPE','SOURCE_ID',*EXPECTED]):
            raise ValueError('Missing or non-string native core field')
        if not row['SCREEN_ID'] or row['SCREEN_ID'] in seen:
            raise ValueError('Missing/duplicate SCREEN_ID')
        if any(v is not None and not isinstance(v, str) for v in row.values()):
            raise ValueError('Unrecognized native metadata shape')
        seen.add(row['SCREEN_ID'])
    joined = {}
    if not isinstance(annotations.get('cell_lines'), list):
        raise ValueError('Missing annotation collection')
    for a in annotations['cell_lines']:
        if not isinstance(a, dict) or not isinstance(a.get('value'), str) or a['value'] in joined:
            raise ValueError('Invalid/duplicate annotation key')
        if a.get('category') is not None and not isinstance(a['category'], str):
            raise ValueError('Ambiguous category')
        if not isinstance(a.get('review_issues', []), list):
            raise ValueError('Invalid annotation review issues')
        joined[a['value']] = a
    return joined


def evaluate(rows, annotations, profile):
    """Evaluate each native row once and retain criterion evidence and context anchors."""
    joined = {a['value']: (i,a) for i,a in enumerate(annotations['cell_lines'])}
    audit, matched, unresolved = [], [], []
    independent = {k: Counter() for k in EXPECTED}
    cumulative = {k: 0 for k in EXPECTED}
    for index, native in enumerate(rows):
        ai, annotation = joined.get(native['CELL_LINE'], (None,None))
        criteria = {}; still_passes = True
        for field, specification in profile['filters'].items():
            value = (annotation or {}).get('category') if field == 'CELL_LINE' else native.get(field)
            status = 'missing' if value in (None, '', '-') else ('pass' if value in specification['values'] else 'fail')
            criteria[field] = {'value': value, 'accepted_values': specification['values'], 'status': status,
                'locator': f'reference_annotations.json#/cell_lines/{ai}/category' if field == 'CELL_LINE' else f'{CACHE}#/{index}/{field}'}
            independent[field][status] += 1
            still_passes = still_passes and status == 'pass'
            cumulative[field] += int(still_passes)
        native_pass = all(criteria[k]['status'] == 'pass' for k in EXPECTED if k != 'CELL_LINE')
        outcome = 'matched' if still_passes else ('unresolved_category' if native_pass and criteria['CELL_LINE']['status'] == 'missing' else 'excluded')
        row = {'SCREEN_ID':native['SCREEN_ID'],'SOURCE_TYPE':native['SOURCE_TYPE'],'SOURCE_ID':native['SOURCE_ID'],
               'native':native,'native_locator':f'{CACHE}#/{index}', 'annotation':annotation,
               'annotation_locator':f'reference_annotations.json#/cell_lines/{ai}' if annotation else None,
               'criteria':criteria,'outcome':outcome,'role': 'direct_filter_hit' if outcome=='matched' else outcome,
               'review_issues':(annotation or {}).get('review_issues',[])}
        audit.append(row)
        if outcome == 'matched': matched.append(row)
        if outcome == 'unresolved_category': unresolved.append(row)
    anchors = {}
    for row in matched:
        key = publication_key(row)
        if key: anchors.setdefault(key, []).append(row['SCREEN_ID'])
    siblings = []
    for row in audit:
        key = publication_key(row)
        if row['outcome'] != 'matched' and key in anchors:
            siblings.append({**row,'role':'publication_sibling_context','anchor_screen_ids':anchors[key]})
    counts = Counter(row['outcome'] for row in audit)
    summary = {'examined':len(rows),'matched':len(matched),'unresolved_category':len(unresolved),
        'excluded':counts['excluded'],'distinct_matched_publications':len(anchors),
        'matched_invalid_publication_keys':sum(publication_key(x) is None for x in matched),
        'publication_siblings':len(siblings),'unresolved_also_sibling':sum(x['outcome']=='unresolved_category' for x in siblings),
        'annotation_issue_screens':sum(bool(x['review_issues']) for x in audit),
        'matched_annotation_issue_screens':sum(bool(x['review_issues']) for x in matched),
        'annotation_issue_values':len({x['native']['CELL_LINE'] for x in audit if x['review_issues']}),
        'independent_counts':{k:{status:v[status] for status in ['pass','fail','missing']} for k,v in independent.items()},
        'cumulative_pass_counts':cumulative,'network_requests':0,
        'interpretation':'Filter hits only; immune interaction and scientific eligibility are not established.'}
    assert summary['matched'] + summary['unresolved_category'] + summary['excluded'] == len(rows)
    return {'matched_screens':matched,'unresolved_screens':unresolved,'publication_siblings':siblings,'screen_audit':audit,'summary':summary}


def preservation(root):
    """Hash existing resource outputs and saved reference facts; never use them as filters."""
    paths = list((root/'outputs').rglob('*')) + list((root/'data/cellosaurus').rglob('*')) + list((root/'data/orcs').rglob('*')) + list((root/'data/templates').rglob('*'))
    return {p.relative_to(root).as_posix():sha(p) for p in paths if p.is_file()}


def execute(root, run_id=None):
    """Validate then execute a new offline run, backing up the selected workbook exactly."""
    root = Path(root).resolve(); p = read(root/PROFILE); validate_profile(p)
    rows, annotations = read(root/CACHE), read(root/ANNOTATIONS)
    summary_path = root/'data/orcs/cache-summary.json'; original_summary=read(summary_path)
    validate_inputs(rows,annotations,original_summary,sha(root/CACHE))
    for field, values in EXPECTED.items():
        observed={a.get('category') for a in annotations['cell_lines']} if field=='CELL_LINE' else {r[field] for r in rows}
        if not set(values)<=observed: raise ValueError(f'Accepted values absent from source vocabulary: {field}')
    now=datetime.now(timezone.utc); run_id=run_id or now.strftime('%Y%m%dT%H%M%S%fZ')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', run_id): raise ValueError('Unsafe run ID')
    out=root/'outputs/orcs'/p['profile_id'].removeprefix('orcs-')/run_id
    if out.exists(): raise FileExistsError(out)
    baseline=preservation(root)
    out.mkdir(parents=True)
    for source,name in [(PROFILE,'profile.json'),(ANNOTATIONS,'reference_annotations.json'),(WORKBOOK,'workbook-original.xlsx')]:
        shutil.copyfile(root/source,out/name)
    manifest={'run_id':run_id,'status':'started','started_at':now.isoformat(),'tool_version':VERSION,
       'input_hashes':{x:sha(root/x) for x in [PROFILE,CACHE,ANNOTATIONS,WORKBOOK,str(summary_path.relative_to(root))]},
       'cache_retrieved_at':original_summary['retrieved_at'],'reference_retrieval_date':annotations['retrieval_date'],
       'code_hashes':{p.relative_to(root).as_posix():sha(p) for p in [Path(__file__),root/'src/deathmap_ai/orcs_filter_projection.py',root/'scripts/export_orcs_filter_workbook.mjs']},
       'network_policy':'No network; saved cache and annotations only','network_requests':0}
    write(out/'run_manifest.json',manifest);write(out/'preservation.json',{'before':baseline})
    results=evaluate(rows,annotations,p)
    for name,value in results.items(): write(out/f'{name}.json',value)
    from .orcs_filter_projection import project
    projection=project(results,manifest,root/WORKBOOK)
    write(out/'projection.json',projection)
    manifest.update(status='filter_complete_excel_pending' if results['matched_screens'] else 'complete_no_hits',filter_completed_at=datetime.now(timezone.utc).isoformat())
    write(out/'run_manifest.json',manifest)
    return out


def main():
    """Run one local invocation from an explicitly selected repository root."""
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);args=parser.parse_args()
    print(execute(args.root))

if __name__=='__main__': main()
