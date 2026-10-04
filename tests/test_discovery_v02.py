"""Bounded v02 scheduling tests with metadata-only fake transports."""
import copy,json,tempfile,unittest
from pathlib import Path
from deathmap_ai.discovery_v02 import QUERIES,VERSION,route,admit,run,next_detail,key_for

class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.s={'routing':route('CRISPR'),'candidate_cap':5000,'new_detail_attempt_cap':50,'page_size':50,'timeout_seconds':1,
                'minimum_request_interval_seconds':0,'search_attempts_per_page':2,'records':{},'query_hits':[],
                'queries':{q:{'offset':0,'buffer':[],'keys':[],'exhausted':False,'blocked':False,'pages':[]} for q in QUERIES},
                'detail_attempts':{},'search_attempts':{},'requests':[],'issues':[],'turn':0,'detail_turn':0,'invocations':[],'stop_reasons':[]}
    def rows(self,n):
        return [{'metadata':{'source':'test','id':str(i),'description':'native'},'retrieved_at':'original','raw_response_ref':'saved'} for i in range(n)]
    def test_routing(self):
        self.assertTrue(route('Study cRiSpR interactions')['orcs']);self.assertFalse(route('proteomics')['orcs'])
    def test_5000_cap_buffer_and_duplicate_observation(self):
        self.s['queries']['Q01']['buffer']=self.rows(5002);admit(self.s,'Q01')
        self.assertEqual(len(self.s['records']),5000);self.assertEqual(len(self.s['queries']['Q01']['buffer']),2)
        self.s['queries']['Q02']['buffer']=self.rows(1);admit(self.s,'Q02');self.assertEqual(len(self.s['query_hits']),5001)
    def test_detail_cap_parsing_failure_resume(self):
        self.s['queries']['Q01']['buffer']=self.rows(55);admit(self.s,'Q01')
        for q in self.s['queries'].values():q['exhausted']=True
        calls=[]
        def fetch(url,timeout):calls.append(url);return b'not json'
        run(self.root,self.s,fetch,lambda _:None)
        self.assertEqual(len(calls),50);self.assertEqual(len(self.s['detail_attempts']),50)
        loaded=json.loads((self.root/'outputs/omicsdi'/VERSION/'resume_state.json').read_text())
        run(self.root,loaded,fetch,lambda _:None);self.assertEqual(len(calls),50)
        self.assertTrue(all(x['status']=='received' for x in loaded['detail_attempts'].values()))
    def test_query_pages_exhaustion_duplicates_and_reuse(self):
        self.s['new_detail_attempt_cap']=0
        def fetch(url,timeout):return json.dumps({'count':1,'datasets':[{'source':'test','id':'same'}]}).encode()
        run(self.root,self.s,fetch,lambda _:None)
        self.assertEqual(len(self.s['records']),1);self.assertEqual(len(self.s['query_hits']),6)
        run(self.root,self.s,lambda *a: self.fail('repeat'),lambda _:None)
    def test_persistent_failure_and_uncertain_reservation(self):
        def fetch(*args):raise TimeoutError('timeout')
        run(self.root,self.s,fetch,lambda _:None)
        self.assertEqual(len(self.s['requests']),3);self.assertIn('persistent_service_failure',self.s['stop_reasons'])
        self.s['queries']['Q03']['buffer']=self.rows(1);admit(self.s,'Q03');key=next(iter(self.s['records']))
        self.s['detail_attempts'][key]={'status':'reserved_or_uncertain'}
        self.assertIsNone(next_detail(self.s))
    def test_reused_records_not_new_detail_targets(self):
        self.s['queries']['Q01']['buffer']=self.rows(1);admit(self.s,'Q01')
        next(iter(self.s['records'].values()))['reuse_origin']='v01_repaired';self.assertIsNone(next_detail(self.s))
