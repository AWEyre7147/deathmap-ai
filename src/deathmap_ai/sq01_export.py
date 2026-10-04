"""Offline resource-native SQ01 export and integrity checks, without entity projection.

OmicsDI observations remain one row per returned position. Candidates deduplicate
only unchanged repository/native-ID pairs and retain every source observation.
ORCS evidence references its complete cached screen record and the exact field.
"""
from pathlib import Path
from deathmap_ai.sq01_plan import RUN_ID, build_plan
from deathmap_ai.sq01_io import encoded, read, write, sha, freeze, verify_freeze
from deathmap_ai import sq01_omicsdi as omics
from deathmap_ai import sq01_orcs as orcs


def omics_outputs(state):
    """Project native observations, standard records and independent query counts."""
    sources=[]; hits=[]; first={}
    definitions={q['query_id']:q for q in build_plan()['resources'][0]['queries']}
    for observation in state['observations']:
        native=observation['native_metadata']; candidate=observation['candidate_id']
        first.setdefault(candidate,observation)
        sources.append({'source_record_id':observation['source_record_id'],'native_metadata':native,
            'provenance':{k:v for k,v in observation.items() if k!='native_metadata'}})
        hit={k:v for k,v in observation.items() if k!='native_metadata'}
        hit.update(run_id=RUN_ID,resource_name='OmicsDI',resource_version=None,
            query_strategy_id='omicsdi-sq01-v03.2',result_rank=native.get('rank'),native_url=native.get('url'),
            candidate_type='native_repository_record',title_original=native.get('title',native.get('name')),
            pmid_reported=native.get('pubmed'),doi_reported=native.get('doi'),accessions_reported=[observation['native_record_id']],
            evidence_text_original=native.get('description'),review_status='unreviewed',
            intended_query=definitions[observation['query_id']]['intended_query'],
            submitted_query=definitions[observation['query_id']]['submitted_query'])
        hits.append(hit)
    hit_by_candidate={}
    for hit in hits:
        hit_by_candidate.setdefault(hit['candidate_id'],hit)
    candidates=[]
    for record in state['records'].values():
        hit=hit_by_candidate[record['record_id']]
        candidate={k:v for k,v in hit.items() if k not in ('observation_id','source_record_id','record_id','candidate_id')}
        candidate.update(record)
        candidate['first_observation_id']=hit['record_id']
        candidate['scientific_question_ids']=['SQ01']
        candidates.append(candidate)
    counts=omics.summary(state)
    manifest={'run_id':RUN_ID,'resource_name':'OmicsDI','resource_version':None,'adapter_version':'sq01-v03.2',
        'plan_digest':state['plan_digest'],'created_at':state['created_at'],'completed_at':state['completed_at'],
        'status':state['status'],'query_strategy':build_plan()['resources'][0],
        'counts':counts,'requests':state['attempts'],'invocations':state['invocations'],
        'proof_of_request_scope':{'only_search_endpoint':True,'detail_requests':0,'enrichment_requests':0},
        'interpretation':'Unreviewed native index observations; no scientific eligibility or entity projection.'}
    return {'source_records.json':{'records':sources},'candidates.json':{'candidates':candidates},
        'query_hits.json':{'hits':hits},'candidate_summary.json':counts,
        'issues.json':{'issues':state['issues']},'search_manifest.json':manifest}


def orcs_outputs(state):
    """Export saved match results without traversing or matching the index again."""
    counts=orcs.summary(state)
    return {'source_records.json':{'records':state['source_records']},
        'candidates.json':{'candidates':state['candidates']},'query_hits.json':{'hits':state['query_hits']},
        'candidate_summary.json':counts,'issues.json':{'issues':state['issues']},
        'search_manifest.json':{'run_id':RUN_ID,'resource_name':'ORCS','adapter_version':'sq01-v03.2',
            'plan_digest':state['plan_digest'],'status':state['status'],'created_at':state['created_at'],
            'completed_at':state['completed_at'],'rules_and_fields':build_plan()['resources'][1],
            'source_hashes':state.get('source_hashes',{}),'counts':counts,'invocations':state['invocations']}}


def validate_outputs(outputs):
    """Check native observation/candidate/evidence references without scientific merging."""
    sources=outputs['source_records.json']['records']; candidates=outputs['candidates.json']['candidates']; hits=outputs['query_hits.json']['hits']
    sids={r['source_record_id'] for r in sources}; cids={r['record_id'] for r in candidates}
    if len(sids)!=len(sources) or len(cids)!=len(candidates):
        raise ValueError('Duplicate source/candidate IDs')
    for candidate in candidates:
        if not set(candidate['source_record_refs'])<=sids:
            raise ValueError('Dangling source reference')
        for parent in candidate.get('parent_match_references',[]):
            if parent['candidate_id'] not in cids or not set(parent['evidence_ids'])<={h.get('evidence_id') for h in hits}:
                raise ValueError('Dangling sibling parent evidence')
    for hit in hits:
        source=hit.get('source_record_id',hit.get('source_record_ref'))
        if hit['candidate_id'] not in cids or source not in sids:
            raise ValueError('Dangling hit reference')


def verify_raw(folder,state):
    """Check receipt/raw hashes and each native observation's precise page location."""
    cache={}
    for event in state['attempts']:
        if event['status'] in ('received','http_failed'):
            if sha(folder/event['raw_file'])!=event['raw_sha256']:
                raise ValueError('Changed raw response')
            receipt=read(folder/event['receipt_file'])
            if any(receipt[k]!=event[k] for k in ('attempt_id','url','raw_sha256','http_status','status','received_at')):
                raise ValueError('Changed request receipt')
    for observation in state['observations']:
        ref=observation['raw_response_ref']
        if ref not in cache:
            cache[ref]=read(folder/ref)['datasets']
        if cache[ref][observation['page_position']-1] != observation['native_metadata']:
            raise ValueError('Observation differs from raw response')


def export(root, folder, state, verify=False):
    """Reproduce resource outputs; completed packages are frozen and never rewritten."""
    if state['resource_name']=='OmicsDI':
        omics.check_state(state,state['plan_digest']); verify_raw(folder,state)
        outputs=omics_outputs(state)
    else:
        for ref,value in state.get('source_hashes',{}).items():
            if sha(root/ref)!=value:
                raise ValueError('ORCS cache changed after pass')
        outputs=orcs_outputs(state)
    validate_outputs(outputs)
    frozen=(folder/'freeze_manifest.json').exists()
    if frozen:
        verify_freeze(folder,state['plan_digest'])
    for name,value in outputs.items():
        path=folder/name
        if verify or frozen:
            if path.read_bytes()!=encoded(value):
                raise ValueError('Offline export mismatch: '+str(path))
        else:
            write(path,value)
    if not verify and state['status']=='complete' and not frozen:
        freeze(folder,state['plan_digest'])
    return outputs['candidate_summary.json']
