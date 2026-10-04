"""Version-02 OmicsDI intake with independent bounded retrieval accounting.

Compatible v01 pages/details retain their native bytes and dates by reference.
Only the new ledger admits up to 5,000 repository/identifier pairs and reserves
50 new detail attempts. A reservation consumes capacity even after interruption,
network uncertainty or parsing failure; historical accounting is never reset.
"""
import argparse
import copy
import hashlib
import json
import time
from pathlib import Path
from urllib.parse import quote, urlencode

from deathmap_ai.omicsdi import BASE, fetch_metadata, utc_now, _write_json
from deathmap_ai.omicsdi_metadata import native_identity, normalize_detail
from deathmap_ai.omicsdi_queries import QUERIES

VERSION = 'immune-crispr-coculture-v02'
QUESTION = 'Discover CRISPR cancer-immune coculture studies, with either perturbed population.'
LIMIT = 5000
DETAIL_LIMIT = 50
PAGE_SIZE = 50


def route(question):
    """Literal routing only; record the original question and exact trigger rule."""
    return {'original_question': question, 'omicsdi': True, 'orcs': 'crispr' in question.casefold(),
            'trigger': 'case-insensitive substring CRISPR; no intent classifier'}


def key_for(row):
    """Preserve both native identifier strings without aliasing repositories."""
    return json.dumps(native_identity(row)[0], ensure_ascii=False)


def rid(key):
    """Generate an intake ID from the unchanged repository/native-ID pair."""
    return 'omicsdi-native-' + hashlib.sha256(key.encode()).hexdigest()[:20]


def read(path):
    """Read UTF-8 saved metadata, raising on invalid JSON instead of inventing data."""
    return json.loads(path.read_text(encoding='utf-8'))


def checkpoint(root, state):
    """Atomically persist a complete ledger before the next network operation."""
    folder = root / 'outputs/omicsdi' / VERSION
    folder.mkdir(parents=True, exist_ok=True)
    # OneDrive/Windows readers can briefly lock replacement. Retry the local
    # checkpoint only; never issue a request until its reservation is durable.
    for attempt in range(5):
        try:
            _write_json(folder / 'resume_state.json', state)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.2 * (attempt + 1))


def initialize(root, question=QUESTION):
    """Reuse the repaired intake and buffers; never mutate its blocked v01 state."""
    path = root / 'outputs/omicsdi' / VERSION / 'resume_state.json'
    if path.exists():
        state = read(path)
        if state['routing'] != route(question):
            raise ValueError('Question differs from saved iteration')
        return state
    legacy = root / 'outputs/omicsdi/cache/legacy/20260908T144947226699Z-repair-v2'
    old = read(legacy / 'resume_state.json')
    if old['config']['queries'] != QUERIES:
        raise ValueError('Historical query configuration is not compatible')
    # References are repository-relative so copied state cannot accidentally
    # address another raw directory or relabel old responses as fresh.
    def convert(value):
        if isinstance(value, dict):
            return {k: ((legacy / v).relative_to(root).as_posix() if k in ('raw_response_ref','detail_response_ref') and isinstance(v,str) else convert(v)) for k,v in value.items()}
        if isinstance(value,list): return [convert(v) for v in value]
        return value
    records = convert(copy.deepcopy(old['records']))
    queries = convert(copy.deepcopy(old['queries']))
    for q in queries.values():
        q['pages'] = [(legacy / p).relative_to(root).as_posix() for p in q['pages']]
        q['blocked'] = False
    for record in records.values():
        record['reuse_origin'] = 'v01_repaired'
    state = {'version': VERSION, 'adapter_version': 'v02.1', 'created_at': utc_now(),
             'routing': route(question), 'queries_config': QUERIES, 'candidate_cap': LIMIT,
             'new_detail_attempt_cap': DETAIL_LIMIT, 'page_size': PAGE_SIZE, 'timeout_seconds':20,
             'minimum_request_interval_seconds':1.0, 'search_attempts_per_page':2,
             'queries':queries, 'records':records, 'query_hits':convert(old['query_hits']),
             'historical_detail_receipts':89, 'historical_within_allowance':50, 'historical_excess':39,
             'historical_state_ref':(legacy/'resume_state.json').relative_to(root).as_posix(),
             'historical_state_sha256':hashlib.sha256((legacy/'resume_state.json').read_bytes()).hexdigest(),
             'detail_attempts':{}, 'search_attempts':{}, 'requests':[], 'issues':[],
             'turn':0, 'detail_turn':0, 'invocations':[], 'stop_reasons':[]}
    checkpoint(root,state)
    return state


def admit(state, qid):
    """Admit buffered rows within the cap; preserve duplicates as separate hits."""
    q = state['queries'][qid]
    while q['buffer']:
        entry=q['buffer'][0]
        try:key=key_for(entry['metadata'])
        except ValueError as error:
            state['issues'].append({'type':'invalid_native_identity','query_id':qid,'entry':entry,'error':str(error)})
            q['buffer'].pop(0);continue
        if key not in state['records']:
            if len(state['records']) >= state['candidate_cap']:break
            row=entry['metadata'];repo,identifier=json.loads(key)
            state['records'][key]={'record_id':rid(key),'repository_original':repo,'native_record_id':identifier,
                'retrieved_at':entry['retrieved_at'],'title_original':row.get('title',row.get('name')),
                'evidence_text_original':row.get('description'),'search_observations':[],
                'detail_metadata':None,'detail_retrieval_status':'not_requested','detail_parse_status':'not_requested',
                'identifier_conflicts':[],'reuse_origin':'v02_admitted'}
        record=state['records'][key]
        hit={k:v for k,v in entry.items() if k!='metadata'}
        hit.update(query_id=qid,record_id=record['record_id'],intended_query=QUERIES[qid],submitted_query=QUERIES[qid])
        state['query_hits'].append(hit);record['search_observations'].append({**hit,'metadata':entry['metadata']})
        if key not in q['keys']:q['keys'].append(key)
        q['buffer'].pop(0)


def next_detail(state):
    """Round-robin query queues; skip reused receipts and every prior attempt."""
    if len(state['detail_attempts'])>=state['new_detail_attempt_cap']:return None
    ids=list(QUERIES)
    for _ in ids:
        qid=ids[state['detail_turn']%len(ids)];state['detail_turn']+=1
        for key in state['queries'][qid]['keys']:
            rec=state['records'][key]
            if key not in state['detail_attempts'] and rec.get('reuse_origin') != 'v01_repaired' and rec.get('detail_retrieval_status')!='received':return key
    return None


def run(root,state,fetch=fetch_metadata,sleep=time.sleep):
    """Continue bounded query pages and one detail per scheduling turn.

    Search retries are limited cumulatively to two per offset. Detail retries are
    never automatic. Three consecutive failed network operations stop the pass;
    explicit resume cannot reset attempts or replay an uncertain reservation.
    """
    if not 0 <= state['candidate_cap'] <= LIMIT or not 0 <= state['new_detail_attempt_cap'] <= DETAIL_LIMIT:
        raise ValueError('Iteration authorization limits exceeded')
    reconcile(root,state)
    folder=root/'outputs/omicsdi'/VERSION
    raw=folder/'raw';(raw/'details').mkdir(parents=True,exist_ok=True)
    invocation={'started_at':utc_now(),'requests_before':len(state['requests'])};state['invocations'].append(invocation)
    failures=0;last_request=0.0
    def request(url,ref,event):
        nonlocal failures,last_request
        sleep(max(0,state['minimum_request_interval_seconds']-(time.monotonic()-last_request)))
        event.update(url=url,raw_response_ref=ref,status='reserved_or_uncertain',started_at=utc_now())
        state['requests'].append(event);checkpoint(root,state);last_request=time.monotonic();tick=last_request
        try:
            body=fetch(url,state['timeout_seconds'])
            event.update(status='received',received_at=utc_now(),elapsed_seconds=time.monotonic()-tick)
            # Receipt and capacity survive a parse failure or a failed raw save.
            checkpoint(root,state);(root/ref).write_bytes(body)
            event['sha256']=hashlib.sha256(body).hexdigest();failures=0;checkpoint(root,state)
            return body
        except Exception as error:
            event.update(status='failed_or_uncertain',error_type=type(error).__name__,error=str(error)[-1200:],elapsed_seconds=time.monotonic()-tick)
            failures+=1;state['issues'].append({'type':'request_failure','request_index':len(state['requests'])-1});checkpoint(root,state)
            return None
    # A search reservation from an interrupted process is never automatically
    # repeated. A received raw page can be safely parsed again without network.
    for qid in QUERIES:admit(state,qid)
    checkpoint(root,state)
    idle=0;state['stop_reasons']=[]
    while idle<len(QUERIES) and failures<3:
        qid=list(QUERIES)[state['turn']%len(QUERIES)];state['turn']+=1;q=state['queries'][qid];progress=False
        if not q['buffer'] and not q['exhausted'] and not q['blocked'] and len(state['records'])<state['candidate_cap']:
            offset=q['offset'];token=f'{qid}:{offset}';events=state['search_attempts'].setdefault(token,[])
            ref=(raw/f'search_{qid}_{offset}.json').relative_to(root).as_posix()
            body=None;event=None
            if (root/ref).exists():
                body=(root/ref).read_bytes();event=events[-1] if events else {'received_at':utc_now()}
            elif events and events[-1]['status'] in ('reserved_or_uncertain','received'):
                q['blocked']=True;state['issues'].append({'type':'uncertain_search_not_repeated','query_id':qid,'offset':offset})
            else:
                while len(events)<state['search_attempts_per_page'] and failures<3:
                    event={'kind':'search','query_id':qid,'offset':offset};events.append(event)
                    body=request(BASE+'search?'+urlencode({'query':QUERIES[qid],'start':offset,'size':state['page_size']}),ref,event)
                    if body is not None:break
                    sleep(2)
            progress=True
            if body is None:q['blocked']=True
            else:
                try:
                    payload=json.loads(body);rows=payload['datasets']
                    if not isinstance(rows,list) or not all(isinstance(x,dict) for x in rows):raise ValueError('Unexpected datasets field')
                    q['pages'].append(ref);q['reported_total']=payload.get('count');q['offset']+=len(rows)
                    q['exhausted']=not rows or (isinstance(payload.get('count'),int) and q['offset']>=payload['count'])
                    q['buffer']=[{'metadata':row,'page_offset':offset,'page_position':i,'result_position':offset+i,
                        'native_rank':row.get('rank'),'retrieved_at':event['received_at'],'raw_response_ref':ref,'reuse':'fresh_v02'} for i,row in enumerate(rows,1)]
                    admit(state,qid)
                except (ValueError,KeyError,TypeError) as error:
                    q['blocked']=True;state['issues'].append({'type':'search_parse_failure','ref':ref,'error':str(error)})
            checkpoint(root,state)
        key=next_detail(state) if failures<3 else None
        if key is not None:
            record=state['records'][key];repo,identifier=json.loads(key)
            ref=(raw/'details'/f'{record["record_id"]}.json').relative_to(root).as_posix()
            event={'kind':'detail','record_key':key};state['detail_attempts'][key]=event
            body=request(BASE+quote(repo,safe='')+'/'+quote(identifier,safe=''),ref,event);progress=True
            if body is not None:
                normalize_detail(record,body,ref,key);record['detail_retrieved_at']=event['received_at']
            else:record.update(detail_retrieval_status='failed_or_uncertain',detail_parse_status='not_attempted')
            checkpoint(root,state)
        idle=0 if progress else idle+1
    if failures>=3:state['stop_reasons'].append('persistent_service_failure')
    if len(state['records'])>=state['candidate_cap']:state['stop_reasons'].append('candidate_cap')
    if len(state['detail_attempts'])>=state['new_detail_attempt_cap']:state['stop_reasons'].append('new_detail_attempt_cap')
    if all(q['exhausted'] and not q['buffer'] for q in state['queries'].values()):state['stop_reasons'].append('queries_exhausted')
    if any(q['blocked'] for q in state['queries'].values()):state['stop_reasons'].append('queries_blocked')
    invocation.update(finished_at=utc_now(),stop_reasons=state['stop_reasons']);checkpoint(root,state)
    return state


def reconcile(root,state):
    """Finish parsing durable detail receipts offline after an interrupted save."""
    for key,event in state['detail_attempts'].items():
        path=root/event.get('raw_response_ref','missing')
        if event.get('status')=='received' and path.is_file():
            normalize_detail(state['records'][key],path.read_bytes(),event['raw_response_ref'],key)
            state['records'][key]['detail_retrieved_at']=event.get('received_at')
        elif event.get('status') in ('reserved_or_uncertain','failed_or_uncertain'):
            state['records'][key].update(detail_retrieval_status=event['status'],detail_parse_status='not_attempted')


def main():
    """Dispatch preparation, authorized retrieval, or deterministic offline export."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','run','export','verify'])
    parser.add_argument('--root',type=Path,default=Path.cwd());parser.add_argument('--question',default=QUESTION)
    args=parser.parse_args();root=args.root.resolve();state=initialize(root,args.question)
    if args.action=='run':run(root,state)
    if args.action in ('run','export','verify'):
        reconcile(root,state)
        from deathmap_ai.discovery_export import export
        export(root,state,verify=args.action=='verify')
        from deathmap_ai.omicsdi_field_guide import write_guide
        write_guide(root,state,verify=args.action=='verify')
    print(json.dumps({'records':len(state['records']),'new_detail_attempts':len(state['detail_attempts']),'stop_reasons':state['stop_reasons']}))


if __name__=='__main__':main()
