"""Read-only preflight for the three owner-supplied ORCS pilot search profiles.

Check JSON structure, supported rule operations, regular expressions, local
input schemas and common-filter vocabularies. This does not evaluate candidate
rules, generate hits, download metadata or establish scientific eligibility.
The legacy v01 filter command does not execute this pilot profile schema.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

SCHEMA = 'deathmap-orcs-pilot-profile/1.0'
INPUTS = {'screen_metadata':'data/orcs/screen-index.json',
          'publication_metadata':'data/orcs/publication-index.json',
          'reference_annotations':'data/cellosaurus/orcs-annotations/annotations.json'}
CONSTRAINTS = {'no_named_cell_line_allowlist','no_named_library_allowlist',
    'no_pmid_doi_or_accession_allowlist','no_icraft_runtime_dependency',
    'no_dataset_access_claim_from_publication_match','no_full_size_scope_filter'}


def validate_profile(profile, columns):
    """Check one pilot definition against available source-column sets.

    Return the number of candidate rules; raise ValueError for unsupported or
    incomplete semantics. Column sets are keyed by screen/publication/annotation.
    No source values or classification decisions are changed.
    """
    required={'schema_version','profile_id','profile_version','created_date','resource',
        'classification_target','purpose','status','input','filter_logic','common_filters',
        'candidate_rules','expansion','constraints','evidence','scope_notes'}
    if not required <= set(profile) or set(profile)-required-{'tags'}:
        raise ValueError('Missing or unknown profile keys')
    if profile['schema_version'] != SCHEMA or profile['resource'] != 'ORCS' or profile['profile_version'] != 1:
        raise ValueError('Unsupported pilot schema/version/resource')
    if not re.fullmatch(r'orcs-[a-z0-9-]+',profile['profile_id']):
        raise ValueError('Unsafe or missing profile identity')
    if profile['classification_target'] not in {'crispr','scrna','clinical'}:
        raise ValueError('Unsupported pilot classification target')
    if profile['input'] != INPUTS:
        raise ValueError('Pilot must use the shared local ORCS/reference inputs')
    if profile['filter_logic'] != {'common_filters':'AND','candidate_rules':'OR',
        'multi_value_separator':'|','trim_tokens':True,'case_sensitive_exact':True,
        'publication_join':'SOURCE_TYPE + SOURCE_ID'}:
        raise ValueError('Unsupported filter/join semantics')
    if set(profile['constraints']) != CONSTRAINTS or any(v is not True for v in profile['constraints'].values()):
        raise ValueError('Pilot preservation/discovery constraints must remain enabled')
    def check(node):
        if not isinstance(node,dict):raise ValueError('Rule must be an object')
        if 'all' in node:
            if set(node) != {'all'} or not isinstance(node['all'],list) or not node['all']:
                raise ValueError('Invalid conjunction')
            for child in node['all']:check(child)
            return
        scope=node.get('scope');op=node.get('operator')
        if scope not in columns:raise ValueError('Unsupported rule scope')
        fields=node.get('fields',[node.get('field')])
        if not isinstance(fields,list) or not fields or any(not isinstance(f,str) or f not in columns[scope] for f in fields):
            raise ValueError(f'Unknown {scope} source field')
        if op=='regex':
            if set(node) != {'scope','fields','operator','pattern','flags'} or node['flags'] != 'IGNORECASE':
                raise ValueError('Unsupported regex keys/flags')
            try:re.compile(node['pattern'],re.IGNORECASE)
            except (re.error,TypeError) as exc:raise ValueError(f'Invalid regex: {exc}') from exc
        elif op=='any_exact':
            if set(node) != {'scope','field','operator','values'} or not isinstance(node['values'],list) or not node['values'] or any(not isinstance(v,str) or not v for v in node['values']):
                raise ValueError('Invalid exact-value rule')
        elif op=='missing':
            if set(node) != {'scope','field','operator'}:raise ValueError('Invalid missing-value rule')
        else:raise ValueError('Unsupported rule operator')
    if not isinstance(profile['common_filters'],list) or not profile['common_filters']:
        raise ValueError('Missing common filters')
    for node in profile['common_filters']:check(node)
    if not isinstance(profile['candidate_rules'],list) or not profile['candidate_rules']:
        raise ValueError('Missing candidate rules')
    ids=set()
    for rule in profile['candidate_rules']:
        if set(rule) != {'rule_id','test'} or not rule['rule_id'] or rule['rule_id'] in ids:
            raise ValueError('Missing/duplicate rule identity')
        ids.add(rule['rule_id']);check(rule['test'])
    if profile['expansion'] != {'enabled':True,'key_fields':['SOURCE_TYPE','SOURCE_ID'],
        'include_all_screens_from_matched_publications':True,'retain_common_filter_failures_as_companions':True,
        'label_seed':'direct_rule_candidate','label_companion':'publication_companion'}:
        raise ValueError('Unsupported expansion/companion policy')
    if profile['evidence'] != {'preserve_native_values':True,'emit_matched_rule_ids':True,
        'normalized_candidate_status':'inferred','publication_presence_status':'direct','dataset_access_status':'not_assessed'}:
        raise ValueError('Unsupported candidate evidence policy')
    if 'tags' in profile:
        if set(profile['tags']) != {'icb_mention_pattern'}:raise ValueError('Unknown tag')
        try:re.compile(profile['tags']['icb_mention_pattern'],re.IGNORECASE)
        except (re.error,TypeError) as exc:raise ValueError(f'Invalid tag regex: {exc}') from exc
    return len(ids)


def preflight(root, profile_path):
    """Read local inputs and return integrity/vocabulary diagnostics, not hits.

    All paths resolve inside root. Shared catalogs are hashed; duplicate native
    publication join keys are reported rather than silently resolved. This is a
    readiness check, not successful execution or a claim of retrieval coverage.
    """
    root=Path(root).resolve();profile_path=Path(profile_path).resolve()
    if not profile_path.is_relative_to(root/'searches/orcs'):
        raise ValueError('Profile must be in searches/orcs')
    read=lambda path:json.loads(path.read_text(encoding='utf-8'))
    profile=read(profile_path)
    if profile.get('input') != INPUTS:raise ValueError('Unsupported input paths')
    data={k:read(root/v) for k,v in INPUTS.items()}
    sources={'screen':data['screen_metadata'],'publication':data['publication_metadata'],
        'annotation':data['reference_annotations'].get('cell_lines')}
    for scope,rows in sources.items():
        if not isinstance(rows,list) or not rows or any(not isinstance(r,dict) for r in rows):
            raise ValueError(f'Empty or malformed {scope} catalog')
    columns={scope:set().union(*(set(row) for row in rows)) for scope,rows in sources.items()}
    rules=validate_profile(profile,columns)
    vocab=[]
    for node in profile['common_filters']:
        if node['operator'] != 'any_exact':raise ValueError('Common filters require exact vocabularies')
        values=set()
        for row in sources[node['scope']]:
            value=row.get(node['field'])
            if value is None:continue
            if not isinstance(value,str):raise ValueError('Non-string common-filter metadata')
            values.update(token.strip() for token in value.split('|'))
        missing=sorted(set(node['values'])-values)
        if missing:raise ValueError(f'Common-filter vocabulary not present: {node["field"]}: {missing}')
        vocab.append({'scope':node['scope'],'field':node['field'],'requested_values_present':node['values']})
    joined={};bad_identity=0
    for pub in sources['publication']:
        key=(pub.get('SOURCE_TYPE'),pub.get('SOURCE_ID'))
        if any(not isinstance(v,str) or not v for v in key):bad_identity+=1;continue
        joined.setdefault(key,[]).append(pub.get('PUBLICATION_ID'))
    duplicates=[{'SOURCE_TYPE':k[0],'SOURCE_ID':k[1],'PUBLICATION_IDS':v} for k,v in joined.items() if len(v)>1]
    return {'profile_id':profile['profile_id'],'schema_version':SCHEMA,'configuration_valid':True,
        'candidate_rule_count':rules,'common_filter_vocabularies':vocab,
        'input_record_counts':{scope:len(rows) for scope,rows in sources.items()},
        'input_hashes':{v:hashlib.sha256((root/v).read_bytes()).hexdigest() for v in INPUTS.values()},
        'profile_sha256':hashlib.sha256(profile_path.read_bytes()).hexdigest(),
        'duplicate_publication_join_keys':duplicates,'publications_missing_join_identity':bad_identity,
        'runner_support':'available: python -m deathmap_ai.orcs_crispr_pilot' if profile['profile_id']=='orcs-crispr-biological-classes-pilot-v01' and (root/'src/deathmap_ai/orcs_crispr_pilot.py').is_file() else 'pending: legacy runner does not implement pilot schema',
        'evidence_export_support':'v6 enabled for active CRISPR pilot; historical knockout-v01 remains protected',
        'candidate_rules_evaluated':False,'network_requests':0}


def main():
    """Print preflight JSON for explicitly selected profiles without writing outputs."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',type=Path,required=True,action='append')
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    print(json.dumps([preflight(args.root,p) for p in args.profile],ensure_ascii=False,indent=2))


if __name__=='__main__':main()
