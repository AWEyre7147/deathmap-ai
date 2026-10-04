"""Independent SQ01 search-page scheduling and cumulative durable accounting.

Each query is exhausted before the next. No successful-pagination cap exists.
Reservations precede transport; response bytes plus a receipt are durable before
state is advanced. A crash may leave an uncertain reservation, never an implicit
empty result. Native identity and duplicate observations survive deduplication.
"""
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urlencode

from deathmap_ai.omicsdi_metadata import native_identity
from deathmap_ai.sq01_plan import ENDPOINT, RUN_ID, build_plan, digest
from deathmap_ai.sq01_io import now, read, write, atomic_bytes, sha
from deathmap_ai.sq01_transport import fetch_search, validate_url


def initial(plan_digest):
    """Create new empty accounting; no v01/v02 records or attempts are consulted."""
    return {'run_id': RUN_ID, 'resource_name': 'OmicsDI', 'plan_digest': plan_digest,
        'created_at': now(), 'status': 'prepared', 'completed_at': None,
        'queries': {q['query_id']: {'status':'pending','offset':0,'reported_totals':[],
            'pages':[],'buffer':[],'block_reason':None} for q in build_plan()['resources'][0]['queries']},
        'attempts': [], 'observations': [], 'records': {}, 'issues': [], 'invocations': []}


def check_state(state, plan_digest):
    """Reject mismatched accounting or any non-search URL before scheduling."""
    if state['plan_digest'] != plan_digest or state['run_id'] != RUN_ID:
        raise ValueError('SQ01 state/plan digest mismatch')
    expected = [q['query_id'] for q in build_plan()['resources'][0]['queries']]
    if list(state['queries']) != expected:
        raise ValueError('Query ledger differs from accepted family')
    counts = Counter()
    for event in state['attempts']:
        validate_url(event['url'])
        counts[(event['query_id'],event['offset'])] += 1
        if event.get('kind') != 'search' or event['query_id'] not in expected:
            raise ValueError('Unexpected request kind or query')
        query = next(q for q in build_plan()['resources'][0]['queries'] if q['query_id']==event['query_id'])
        if event['url'] != search_url(query, event['offset']):
            raise ValueError('Request does not match its query/offset')
    if any(n>2 for n in counts.values()):
        raise ValueError('Cumulative attempt bound exceeded')


def search_url(query, offset):
    return ENDPOINT+'?'+urlencode({'query':query['submitted_query'],'start':offset,'size':50})


def checkpoint(folder, state):
    write(folder/'resume_state.json', state)


def _block(state, qid, reason, status='blocked'):
    state['queries'][qid].update(status=status, block_reason=reason)
    state['issues'].append({'query_id':qid,'type':reason})


def _admit(state, qid):
    """Consume valid buffered rows; leave the invalid row and remainder intact."""
    query = state['queries'][qid]
    while query['buffer']:
        item = query['buffer'][0]
        try:
            pair, original_fields = native_identity(item['native_metadata'])
        except ValueError as error:
            _block(state,qid,'invalid_native_identity')
            state['issues'][-1].update(raw_response_ref=item['raw_response_ref'],position=item['page_position'],error=str(error))
            return
        key = json.dumps(pair, ensure_ascii=False)
        candidate_id = 'omicsdi-sq01-'+digest(pair)[:20]
        observation_id = 'obs-'+digest([qid,item['offset'],item['page_position']])[:24]
        observation = {**item, 'record_id':observation_id, 'observation_id':observation_id,
            'source_record_id':'source-'+observation_id,'candidate_id':candidate_id,
            'query_id':qid, 'scientific_question_id':'SQ01','repository_original':pair[0],
            'native_record_id':pair[1],'native_identity_fields':original_fields}
        state['observations'].append(observation)
        record = state['records'].setdefault(key, {'record_id':candidate_id,'repository_original':pair[0],
            'native_record_id':pair[1],'source_record_refs':[],'query_ids':[]})
        record['source_record_refs'].append(observation['source_record_id'])
        if qid not in record['query_ids']:
            record['query_ids'].append(qid)
        query['buffer'].pop(0)


def _apply_page(folder, state, event):
    """Parse one durable HTTP-200 receipt offline; no receipt is fetched twice."""
    qid = event['query_id']; query = state['queries'][qid]
    if event.get('applied') or query['status'] in ('blocked','failed','exhausted'):
        return
    raw = folder/event['raw_file']
    try:
        payload = json.loads(raw.read_bytes())
        rows, total = payload['datasets'], payload['count']
        if not isinstance(rows,list) or not all(isinstance(r,dict) for r in rows) or type(total)!=int or total<0:
            raise ValueError('Unexpected datasets/count structure')
    except (ValueError,KeyError,TypeError) as error:
        _block(state,qid,'unrecognized_search_response')
        state['issues'][-1].update(raw_file=event['raw_file'],error=str(error))
        event['applied'] = True
        return
    signature = digest(rows)
    repeated = bool(rows) and any(p['rows_sha256']==signature for p in query['pages'])
    previous = query['reported_totals'][-1]['count'] if query['reported_totals'] else None
    if previous is not None and total != previous:
        state['issues'].append({'type':'reported_total_changed','query_id':qid,'previous':previous,'current':total,'offset':event['offset']})
    if len(rows)>50 or (rows and event['offset']+len(rows)>total):
        state['issues'].append({'type':'pagination_count_anomaly','query_id':qid,'offset':event['offset'],'rows':len(rows),'count':total})
    query['reported_totals'].append({'count':total,'received_at':event['received_at'],'offset':event['offset']})
    query['pages'].append({'raw_file':event['raw_file'],'offset':event['offset'],'rows':len(rows),'count':total,'rows_sha256':signature,'received_at':event['received_at']})
    query['buffer'] = [{'native_metadata':row,'offset':event['offset'],'page_position':i,
        'result_position':event['offset']+i,'retrieved_at':event['received_at'],
        'raw_response_ref':event['raw_file']} for i,row in enumerate(rows,1)]
    query['offset'] = event['offset']+len(rows)
    _admit(state,qid)
    event['applied'] = True
    if query['status']=='blocked':
        return
    if repeated:
        _block(state,qid,'repeated_nonempty_page')
    elif not rows or query['offset']>=total:
        query.update(status='exhausted',block_reason=None)
    else:
        query['status']='running'


def reconcile(folder, state):
    """Recover completed receipts; unresolved reservations block instead of retry."""
    for event in state['attempts']:
        receipt_path = folder/event['receipt_file']
        if event['status']=='reserved':
            if receipt_path.exists():
                receipt = read(receipt_path)
                if receipt['attempt_id'] != event['attempt_id'] or receipt['url'] != event['url'] or sha(folder/event['raw_file'])!=receipt['raw_sha256']:
                    raise ValueError('Durable receipt integrity mismatch')
                event.update(receipt)
            else:
                event['status']='uncertain'
                _block(state,event['query_id'],'reserved_without_durable_outcome')
        if event['status']=='received':
            if not receipt_path.exists() or sha(folder/event['raw_file'])!=event['raw_sha256']:
                raise ValueError('Missing/changed search response')
            _apply_page(folder,state,event)


def _retry_wait(headers):
    value = next((v for k,v in headers.items() if k.casefold()=='retry-after'),None)
    if value is None:
        return 2
    try:
        seconds = float(value)
    except ValueError:
        try:
            seconds = (parsedate_to_datetime(value)-datetime.now(timezone.utc)).total_seconds()
        except (ValueError,TypeError):
            return None
    return max(2,seconds) if 0<=seconds<=60 else None


def run(folder, state, plan_digest, fetch=fetch_search, sleep=time.sleep, monotonic=time.monotonic, emit=print):
    """Execute the accepted sequential search schedule; retain partial work safely.

    fetch is injectable for offline tests and returns HTTP status/headers/bytes.
    A transport exception means uncertainty, not a safely repeatable empty result.
    Known HTTP failures may use the single cumulative retry. Local I/O failure
    propagates immediately, leaving the pre-request reservation durable.
    """
    check_state(state,plan_digest)
    if state['status']=='complete':
        return state
    reconcile(folder,state)
    for prior in state['invocations']:
        if prior['status']=='running':
            prior.update(status='interrupted',reconciled_at=now())
    invocation = {'started_at':now(),'attempts_before':len(state['attempts']),'status':'running'}
    state['invocations'].append(invocation); state['status']='running'
    checkpoint(folder,state)
    failures = 0; last_start = monotonic()
    for definition in build_plan()['resources'][0]['queries']:
        qid = definition['query_id']; query = state['queries'][qid]
        while query['status'] not in ('exhausted','blocked','failed') and failures<3:
            offset = query['offset']
            attempts = [e for e in state['attempts'] if e['query_id']==qid and e['offset']==offset]
            if len(attempts)>=2:
                _block(state,qid,'two_failed_attempts',status='failed');checkpoint(folder,state);break
            if attempts:
                last = attempts[-1]
                if last['status']!='http_failed':
                    _block(state,qid,'uncertain_request_not_repeated');checkpoint(folder,state);break
                wait = _retry_wait(last.get('headers',{}))
                if wait is None:
                    _block(state,qid,'service_retry_delay_requires_review');checkpoint(folder,state);break
                sleep(wait)
            sleep(max(0,1-(monotonic()-last_start)))
            attempt_id = f'{qid}-s{offset}-a{len(attempts)+1}'
            event = {'attempt_id':attempt_id,'kind':'search','query_id':qid,'offset':offset,
                'url':search_url(definition,offset),'status':'reserved','started_at':now(),
                'raw_file':f'raw/{attempt_id}.body','receipt_file':f'raw/{attempt_id}.receipt.json'}
            state['attempts'].append(event); query['status']='running'
            checkpoint(folder,state)  # Transport cannot run until this succeeds.
            last_start = monotonic()
            try:
                response = fetch(event['url'],20)
            except Exception as error:
                event.update(status='uncertain',finished_at=now(),error_type=type(error).__name__,error=str(error)[-1500:],elapsed_seconds=monotonic()-last_start)
                failures += 1
                _block(state,qid,'uncertain_transport_outcome')
                checkpoint(folder,state)
                break
            # Save original bytes for every HTTP outcome, including error bodies.
            body = response['body']; code = response['http_status']
            atomic_bytes(folder/event['raw_file'],body)
            receipt = {**event,'http_status':code,'headers':response.get('headers',{}),
                'status':'received' if code==200 else 'http_failed','received_at':now(),
                'elapsed_seconds':monotonic()-last_start,'raw_sha256':hashlib.sha256(body).hexdigest()}
            write(folder/event['receipt_file'],receipt)
            event.update(receipt)
            checkpoint(folder,state)
            if code==200:
                failures=0
                _apply_page(folder,state,event)
            else:
                failures+=1
                state['issues'].append({'type':'http_failure','query_id':qid,'attempt_id':attempt_id,'http_status':code})
                if code in (301,302,303,307,308):
                    _block(state,qid,'redirect_not_followed')
                elif len(attempts)+1>=2:
                    _block(state,qid,'two_failed_attempts',status='failed')
            checkpoint(folder,state)
            if code==200 and len(query['pages'])%10==0 and query['status']=='running':
                emit(json.dumps({'checkpoint':True,'query_id':qid,'offset':query['offset'],'pages':len(query['pages']),'unique_records':len(state['records'])}))
        emit(json.dumps({'query_id':qid,'status':query['status'],'offset':query['offset'],'pages':len(query['pages']),'admitted_unique_total':len(state['records']),'attempts':len(state['attempts'])}))
        if failures>=3:
            state['issues'].append({'type':'three_consecutive_failed_network_operations'})
            break
    state['status'] = 'complete' if all(q['status']=='exhausted' for q in state['queries'].values()) else 'partial'
    if state['status']=='complete':
        state['completed_at']=now()
    invocation.update(finished_at=now(),status=state['status'],consecutive_failures_at_stop=failures)
    checkpoint(folder,state)
    return state


def summary(state):
    """Count each independent query, within-query duplicates and cross-query overlap."""
    sets = {qid:{o['candidate_id'] for o in state['observations'] if o['query_id']==qid} for qid in state['queries']}
    previous = set(); per_query = {}
    for qid,q in state['queries'].items():
        observations = [o for o in state['observations'] if o['query_id']==qid]
        others = set().union(*(ids for k,ids in sets.items() if k!=qid))
        per_query[qid] = {'status':q['status'],'reason':q['block_reason'],'pages':len(q['pages']),
            'requests':sum(e['query_id']==qid for e in state['attempts']), 'observations':len(observations),
            'unique_records':len(sets[qid]),'duplicate_observations_within_query':len(observations)-len(sets[qid]),
            'overlap_with_other_queries':len(sets[qid]&others),'exclusive_to_query':len(sets[qid]-others),
            'new_unique_in_query_order':len(sets[qid]-previous),'buffered_rows':len(q['buffer']),
            'next_offset':q['offset'],'reported_totals':q['reported_totals']}
        previous.update(sets[qid])
    groups = {'complete':[], 'incomplete':[], 'blocked':[], 'failed':[]}
    for qid,q in state['queries'].items():
        group = 'complete' if q['status']=='exhausted' else q['status'] if q['status'] in ('blocked','failed') else 'incomplete'
        groups[group].append(qid)
    return {'status':state['status'],'query_status_groups':groups,'unique_records':len(state['records']),'observations':len(state['observations']),
        'requests':len(state['attempts']),'detail_requests':0,'enrichment_requests':0,
        'native_repository_counts':dict(Counter(r['repository_original'] for r in state['records'].values())),
        'queries':per_query}
