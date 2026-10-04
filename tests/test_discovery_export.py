"""Small offline fixtures test entity boundaries, provenance and reproducibility."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from deathmap_ai.discovery_v02 import route,admit,QUERIES,VERSION,checkpoint
from deathmap_ai.discovery_export import build,validate,export,SCHEMA
from deathmap_ai.resource_migration import write_json
from deathmap_ai.omicsdi_field_guide import inventory,write_guide

class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.s={'routing':route('CRISPR'),'records':{},'queries':{q:{'offset':0,'buffer':[],'keys':[],'exhausted':True,'blocked':False,'pages':[]} for q in QUERIES},'query_hits':[], 'candidate_cap':5000,'new_detail_attempt_cap':50,'detail_attempts':{},'issues':[],'stop_reasons':['queries_exhausted'],'historical_state_ref':'history.json','queries_config':QUERIES}
        write_json(self.root/'history.json',{'preserved':'historical'})
        cache=self.root/'outputs/orcs/cache/legacy/20260904T213941Z'
        write_json(cache/'orcs-screens.raw.json',[{'SCREEN_ID':'s1','SOURCE_TYPE':'pubmed','SOURCE_ID':'101','NOTES':'CRISPR T cell','CELL_LINE':'reported line'}])
        write_json(cache/'summary.json',{'screens_retrieved':1,'retrieved_at':'original-orcs-date'})
    def add(self,ident='a',pubmed=None,doi=None,source='geo',extra=None):
        metadata={'source':source,'id':ident,'description':'unaltered description','additional':extra or {},'cross_references':{}}
        if pubmed:metadata['cross_references']['PMID']=pubmed
        if doi:metadata['cross_references']['doi']=doi
        ref='raw-'+ident+'.json';write_json(self.root/ref,{'count':1,'datasets':[metadata]})
        q=self.s['queries']['Q01'];q['pages'].append(ref);q['buffer']=[{'metadata':metadata,'retrieved_at':'original-date','raw_response_ref':ref}];admit(self.s,'Q01')
        return list(self.s['records'].values())[-1]
    def test_multiplicity_orcs_unmatched_and_no_fabricated_links(self):
        self.add(pubmed=['[101]','102'],extra={'pubmed_title':['title one','title two']})
        t,*_=build(self.root,self.s);validate(t)
        self.assertEqual(len(t['publications']),2);self.assertEqual(len(t['datasets'][0]['publication_id']),2)
        self.assertEqual(len(t['screens']),1);self.assertIsNone(t['screens'][0]['screen_group_id'])
        self.assertEqual(t['screen_groups'],[]);self.assertEqual(t['screen_dataset_links'],[])
        self.assertTrue(all(r['title_original'] is None for r in t['publications']))
        self.assertEqual(t['screens'][0]['publication_id'][0],t['datasets'][0]['publication_id'][0])
    def test_conflicting_publication_ids_do_not_transitively_merge(self):
        self.add('a',['101'],['10.1234/example']);self.add('b',['102'],['10.1234/example'])
        t,_,_,issues=build(self.root,self.s);validate(t)
        self.assertEqual(len(t['publications']),2)
        self.assertIn('conflicting_publication_identifiers',[i['type'] for i in issues])
    def test_native_unknowns_conflicts_and_literature_meaning(self):
        r=self.add(source='biostudies-literature',extra={'unfamiliar':{'keep':'native'},'pubmed_abstract':'abstract'})
        r.update(detail_metadata={'database':'other','accession':'a','description':'wrong identity'},detail_parse_status='identity_conflict',identifier_conflicts=[{'requested':'biostudies-literature','returned':'other'}],detail_allowance_band='excess',detail_retrieval_ordinal=89)
        t,s,_,_=build(self.root,self.s);validate(t)
        self.assertEqual(t['datasets'][0]['description_reported'],'unaltered description')
        self.assertEqual(t['datasets'][0]['_native_entity_category'],'literature_record')
        self.assertFalse(t['datasets'][0]['_independent_experimental_deposit'])
        self.assertEqual(s[0]['native_metadata']['detail_metadata']['description'],'wrong identity')
        self.assertEqual(s[0]['provenance']['historical_detail_retrieval_ordinal'],89)
        self.assertIsNone(t['datasets'][0]['raw_data_available'])
        inv=inventory(self.root,self.s);self.assertIn('additional.unfamiliar.keep',inv['sources']['biostudies-literature']['fields'])
    def test_all_reference_fields_deferred_fields_and_offline_reproducibility(self):
        self.add(pubmed=['101']);before=copy.deepcopy(self.s)
        with patch('deathmap_ai.omicsdi.fetch_metadata',side_effect=AssertionError('offline only')):
            export(self.root,self.s);export(self.root,self.s,verify=True)
        self.assertEqual(self.s,before)
        mapping=json.loads((self.root/'outputs'/VERSION/'reference_mapping.json').read_text(encoding='utf-8'))
        self.assertEqual(mapping,SCHEMA)
        t,*_=build(self.root,self.s)
        for rows in t.values():
            for row in rows:
                for f,status in row['_field_status'].items():
                    if status=='deliberately_deferred':self.assertIsNone(row[f])
        self.assertEqual(len(SCHEMA['tables']),7)
        # No reference/example workbook or ICRAFT tree exists in this root.
        # Export depends only on the checked header schema and metadata fixtures.
        self.assertFalse((self.root/'data').exists())
    def test_non_crispr_does_not_open_orcs(self):
        self.s['routing']=route('proteomics');self.add()
        with patch('deathmap_ai.discovery_export.orcs_package',side_effect=AssertionError('must not route')):
            t,*_=build(self.root,self.s);validate(t)
        self.assertEqual(t['screens'],[])
    def test_checkpoint_retries_local_lock_only(self):
        with patch('deathmap_ai.discovery_v02._write_json',side_effect=[PermissionError('locked'),None]) as write,patch('deathmap_ai.discovery_v02.time.sleep'):
            checkpoint(self.root,self.s)
        self.assertEqual(write.call_count,2)
    def test_dangling_entity_or_evidence_rejected(self):
        self.add();t,*_=build(self.root,self.s)
        t['datasets'][0]['publication_id']=['unknown']
        with self.assertRaisesRegex(ValueError,'Dangling'):validate(t)
    def test_guide_preserves_case_different_native_labels_on_windows(self):
        r=self.add(source='geo');ref='detail.json'
        write_json(self.root/ref,{'database':'GEO','accession':'a','name':'detail name'})
        r['detail_response_ref']=ref
        write_guide(self.root,self.s);write_guide(self.root,self.s,verify=True)
        folder=self.root/'docs/field guide/omicsdi'
        self.assertTrue((folder/'geo.md').exists());self.assertTrue((folder/'geo-detail-label.md').exists())
        self.assertIn('detail name',(folder/'geo-detail-label.md').read_text(encoding='utf-8'))
