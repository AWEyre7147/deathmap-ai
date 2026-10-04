"""One local ORCS pass with named-field evidence and explicit sibling context.

Only accepted SQ01 term sets and the complete cached index are inputs. Matching
uses each field separately; identifiers, authors, URLs and numeric result columns
are not search text. No publication lookup or network request is available here.
"""
from collections import Counter
import re
from deathmap_ai.sq01_plan import INDEX, INDEX_SUMMARY, FIELDS, RUN_ID, build_plan, digest
from deathmap_ai.sq01_io import read, write, now, sha


def initial(plan_digest):
    return {'run_id':RUN_ID,'plan_digest':plan_digest,'resource_name':'ORCS','status':'prepared',
        'created_at':now(),'completed_at':None,'source_records':[],'candidates':[],'query_hits':[],
        'issues':[],'invocations':[],'counts':{}}


def load_index(root):
    """Validate the complete cache and required schema before any matching."""
    rows = read(root/INDEX); metadata = read(root/INDEX_SUMMARY)
    if not isinstance(rows,list) or not rows or metadata.get('screens_retrieved') != len(rows) or not metadata.get('retrieved_at'):
        raise ValueError('ORCS index completeness/schema check failed')
    seen = set()
    # NOTES is absent in 81 cached rows; optional descriptions cannot be
    # required to recognize an otherwise complete native screen record.
    required = {'SCREEN_ID','SOURCE_ID','SOURCE_TYPE','SCREEN_NAME','SCREEN_FORMAT','METHODOLOGY'}
    for row in rows:
        if not isinstance(row,dict) or not required<=row.keys():
            raise ValueError('Unrecognized required ORCS schema')
        if not isinstance(row['SCREEN_ID'],str) or not row['SCREEN_ID'] or row['SCREEN_ID'] in seen:
            raise ValueError('Invalid/duplicate native ORCS screen identifier')
        seen.add(row['SCREEN_ID'])
        if any(value is not None and not isinstance(value,str) for key,value in row.items() if key in FIELDS or key in ('SOURCE_ID','SOURCE_TYPE')):
            raise ValueError('Unrecognized ORCS field type')
    return rows,metadata


def match_row(row, rules):
    """Return all field occurrences for satisfied all-of rules, preserving originals."""
    hits = []
    for rule in rules:
        by_term = []
        for term in rule['terms']:
            occurrences = []
            pattern = re.compile(r'(?<!\w)'+re.escape(term)+r'(?!\w)', re.IGNORECASE)
            for field in FIELDS:
                value = row.get(field)
                if not isinstance(value,str):
                    continue
                for match in pattern.finditer(value):
                    occurrences.append({'query_id':rule['rule_id'],'rule_id':rule['rule_id'],
                        'matched_term':term,'matched_text_original':match.group(),
                        'source_field_name':field,'source_field_value':value,
                        'normalized_comparison_form':value.casefold(),'comparison_term':term.casefold(),
                        'character_span':[match.start(),match.end()],
                        'match_operation':'case-insensitive bounded literal word/phrase; all-of terms across named fields',
                        'direct_match':True,'scientific_question_id':'SQ01'})
            if not occurrences:
                break
            by_term.extend(occurrences)
        else:
            hits.extend(by_term)
    return hits


def run(root, folder, state, plan_digest):
    """Persist one completed pass; a completed state is reused, never re-searched."""
    if state['plan_digest'] != plan_digest or state['run_id'] != RUN_ID:
        raise ValueError('ORCS semantic plan mismatch')
    if state['status']=='complete':
        return state
    invocation = {'started_at':now(),'status':'running'}
    state['invocations'].append(invocation)
    write(folder/'resume_state.json',state)
    try:
        rows,metadata = load_index(root)
        sources=[]; all_hits=[]; matches={}; publications={}
        rules=build_plan()['resources'][1]['rules']
        for index,row in enumerate(rows):
            sid='orcs-source-'+digest(row['SCREEN_ID'])[:20]
            candidate='orcs-sq01-'+digest(row['SCREEN_ID'])[:20]
            source={'source_record_id':sid,'native_metadata':row,
                'provenance':{'raw_response_ref':INDEX,'json_index':index,'retrieved_at':metadata['retrieved_at'],'reuse':'complete_cached_native_index'}}
            sources.append(source)
            evidence=match_row(row,rules)  # Exactly one matching traversal per native screen.
            matches[row['SCREEN_ID']]=evidence
            for hit in evidence:
                hit.update(evidence_id='evidence-'+digest([row['SCREEN_ID'],hit['query_id'],hit['matched_term'],hit['source_field_name'],hit['character_span']])[:24],
                    candidate_id=candidate,native_record_id=row['SCREEN_ID'],source_record_ref=sid,
                    run_id=RUN_ID,resource_name='ORCS',resource_version=None,query_strategy_id='orcs-sq01-v03.2',
                    retrieved_at=metadata['retrieved_at'],result_rank=None,review_status='unreviewed',raw_response_ref=INDEX)
                hit['record_id']=hit['evidence_id']
            all_hits.extend(evidence)
            pair=(row['SOURCE_TYPE'],row['SOURCE_ID'])
            if evidence and (row['SOURCE_TYPE'] or '').casefold() in ('pubmed','doi') and all(isinstance(v,str) and v not in ('','-') for v in pair):
                publications.setdefault(pair,[]).append({'candidate_id':candidate,'evidence_ids':[h['evidence_id'] for h in evidence]})
        candidates=[]
        for source in sources:
            row=source['native_metadata']; evidence=matches[row['SCREEN_ID']]
            parents=publications.get((row['SOURCE_TYPE'],row['SOURCE_ID']),[])
            if not evidence and not parents:
                continue
            identifier='orcs-sq01-'+digest(row['SCREEN_ID'])[:20]
            candidates.append({'record_id':identifier,'run_id':RUN_ID,'resource_name':'ORCS',
                'resource_version':None,'retrieved_at':metadata['retrieved_at'],'query_strategy_id':'orcs-sq01-v03.2',
                'result_rank':None,'native_record_id':row['SCREEN_ID'],'native_url':None,'candidate_type':'screen',
                'title_original':row.get('TITLE'),'screen_name_reported':row['SCREEN_NAME'],
                'pmid_reported':row['SOURCE_ID'] if (row['SOURCE_TYPE'] or '').casefold()=='pubmed' else None,
                'doi_reported':None,'accessions_reported':None,'evidence_text_original':row.get('NOTES'),
                'raw_response_ref':INDEX,'source_record_refs':[source['source_record_id']],
                'review_status':'unreviewed','scientific_question_ids':['SQ01'],
                'query_ids':list(dict.fromkeys(h['query_id'] for h in evidence)),
                'inclusion_basis':'direct_match' if evidence else 'publication_sibling_context',
                'direct_match':bool(evidence),'parent_match_references':[] if evidence else parents})
        state.update(status='complete',completed_at=now(),source_records=sources,candidates=candidates,query_hits=all_hits,
            source_hashes={INDEX:sha(root/INDEX),INDEX_SUMMARY:sha(root/INDEX_SUMMARY)},
            counts={'cached_screens':len(rows),'examined_screens':len(sources),'candidates':len(candidates),
                'direct_matches':sum(c['direct_match'] for c in candidates),
                'publication_siblings':sum(not c['direct_match'] for c in candidates),'field_match_evidence':len(all_hits),
                'network_requests':0,'detail_requests':0,'enrichment_requests':0})
        invocation.update(status='complete',finished_at=state['completed_at'])
    except (ValueError,OSError,KeyError,TypeError) as error:
        state.update(status='failed',completed_at=None)
        state['issues'].append({'type':'orcs_cache_or_processing_failure','error':str(error)})
        invocation.update(status='failed',finished_at=now())
    write(folder/'resume_state.json',state)
    return state


def summary(state):
    rules=build_plan()['resources'][1]['rules']
    return {'status':state['status'],**state['counts'],'queries':{
        r['rule_id']:{'direct_screens':len({h['native_record_id'] for h in state['query_hits'] if h['query_id']==r['rule_id']}),
                      'field_evidence_rows':sum(h['query_id']==r['rule_id'] for h in state['query_hits'])} for r in rules}}
