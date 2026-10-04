"""Regression fixtures for exact filtering, provenance and conservative entity projection."""
import copy
import json
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from deathmap_ai.orcs_filters import EXPECTED, evaluate, read, validate_profile, validate_inputs, publication_key
from deathmap_ai.orcs_filter_projection import stable_id, merge_rows, project
ROOT=Path(__file__).resolve().parents[1]

class OrcsFilterTests(unittest.TestCase):
    def setUp(self):
        self.profile=read(ROOT/'searches/orcs/cancer-cell-crispr-knockout-v01/profile.json')
        self.row={k:v[0] for k,v in EXPECTED.items()};self.row.update(SCREEN_ID='x1',SOURCE_TYPE='pubmed',SOURCE_ID='123',CELL_LINE='Fixture cancer',SCREEN_NAME='fixture',AUTHOR='A (2020)')
        self.ann={'cache_sha256':'abc','cell_lines':[{'value':'Fixture cancer','category':'Cancer cell line','accession':'CVCL_TEST','review_issues':[]}]}
    def test_profile_and_unknown_operations(self):
        validate_profile(self.profile)
        for section,key,val in [('filter_logic','between_fields','OR'),('annotation_join','comparison','fuzzy'),('filters','IMMUNE',{'values':['T']})]:
            p=copy.deepcopy(self.profile);p[section][key]=val
            with self.assertRaises(ValueError):validate_profile(p)
    def test_exact_and_or_and_each_failure(self):
        for field in EXPECTED:
            r=copy.deepcopy(self.row);a=copy.deepcopy(self.ann)
            if field=='CELL_LINE':a['cell_lines'][0]['category']='Normal cell line'
            else:r[field]='wrong'
            self.assertEqual(evaluate([r],a,self.profile)['summary']['excluded'],1)
        for field in ['ORGANISM_OFFICIAL','PHENOTYPE']:
            for value in EXPECTED[field]:
                r={**self.row,field:value};self.assertEqual(evaluate([r],self.ann,self.profile)['summary']['matched'],1)
        for field,value in [('ENZYME','Cas9 variant'),('ENZYME','cas9'),('PHENOTYPE','viability'),('CELL_LINE','fixture cancer')]:
            x=evaluate([{**self.row,field:value}],self.ann,self.profile)
            self.assertEqual(x['summary']['matched'],0)
    def test_missing_only_when_other_six_pass(self):
        a=copy.deepcopy(self.ann);a['cell_lines'][0]['category']=None
        self.assertEqual(evaluate([self.row],a,self.profile)['summary']['unresolved_category'],1)
        self.assertEqual(evaluate([{**self.row,'ENZYME':'dCas9'}],a,self.profile)['summary']['excluded'],1)
    def test_conflicts_preserved_not_excluded(self):
        a=copy.deepcopy(self.ann);a['cell_lines'][0]['review_issues']=['Species conflict']
        out=evaluate([self.row],a,self.profile)
        self.assertEqual(out['summary']['matched'],1);self.assertEqual(out['matched_screens'][0]['review_issues'],['Species conflict'])
    def test_sibling_separation_and_native_identity(self):
        rows=[self.row,{**self.row,'SCREEN_ID':'x2','CELL_LINE':'primary T cells'},{**self.row,'SCREEN_ID':'x3','SOURCE_ID':'124','ENZYME':'dCas9'}]
        out=evaluate(rows,self.ann,self.profile)
        self.assertEqual(out['summary']['matched'],1);self.assertEqual(out['summary']['publication_siblings'],1)
        self.assertEqual(out['publication_siblings'][0]['anchor_screen_ids'],['x1'])
        self.assertEqual(out['publication_siblings'][0]['outcome'],'unresolved_category')
        self.assertEqual(sum(out['summary'][k] for k in ['matched','excluded','unresolved_category']),3)
    def test_validation_failures(self):
        validate_inputs([self.row],self.ann,{'screens_retrieved':1},'abc',1)
        for rows,a,summary,h,count in [([self.row],self.ann,{'screens_retrieved':2},'abc',1),([self.row],self.ann,{'screens_retrieved':1},'bad',1),([self.row,self.row],self.ann,{'screens_retrieved':2},'abc',2),([self.row],{**self.ann,'cell_lines':self.ann['cell_lines']*2},{'screens_retrieved':1},'abc',1),([{**self.row,'ENZYME':[]}],self.ann,{'screens_retrieved':1},'abc',1)]:
            with self.assertRaises(ValueError):validate_inputs(rows,a,summary,h,count)
    def test_valid_publication_only(self):
        for typ,identifier in [('pubmed','-'),('other','123'),('doi','notdoi')]:self.assertIsNone(publication_key({'SOURCE_TYPE':typ,'SOURCE_ID':identifier}))
        self.assertEqual(publication_key({'SOURCE_TYPE':'doi','SOURCE_ID':'10.1234/ABC'}),('doi','10.1234/ABC'))
    def test_stable_ids_and_merge_preserve_review(self):
        self.assertEqual(stable_id('SCR','ORCS','1'),stable_id('SCR','ORCS','1'))
        self.assertNotEqual(stable_id('SCR','ORCS','1'),stable_id('PUB','ORCS','1'))
        rows,conflicts=merge_rows([{'id':'a','review':'owner','value':None,'formula':'=1+1'}],[{'id':'a','review':'new','value':'reported','formula':'=2'}],'id')
        self.assertEqual(rows[0],{'id':'a','review':'owner','value':'reported','formula':'=1+1'});self.assertEqual(len(conflicts),2)
    def test_projection_dedup_foreign_keys_no_datasets_no_network(self):
        out=evaluate([self.row,{**self.row,'SCREEN_ID':'x2'}],self.ann,self.profile)
        manifest={'started_at':'2026-10-03','cache_retrieved_at':'2026-09-04','reference_retrieval_date':'2026-10-01'}
        with patch.object(socket,'socket',side_effect=AssertionError('network forbidden')):
            p=project(out,manifest,ROOT/'data/templates/DeathMap-AI-v1-reference-output.xlsx')
        self.assertEqual(p['proposed_counts']['Publications'],1);self.assertEqual(p['proposed_counts']['Screens'],2)
        for key in ['Screen Groups','Datasets','Screen-Dataset Links']:self.assertEqual(p['proposed_counts'][key],0)
        self.assertEqual(len({x['publication_id'] for x in p['sheets']['Screens'] if x['screen_id'] in p['roles']}),1)
        pubs=[x for x in p['sheets']['Publications'] if x.get('pmid')=='123'];self.assertIsNone(pubs[0].get('publication_year'))
    def test_execution_refuses_existing_directory(self):
        from deathmap_ai.orcs_filters import execute, PROFILE, CACHE, ANNOTATIONS
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for name,value in [(PROFILE,self.profile),(CACHE,[self.row]),(ANNOTATIONS,self.ann),('data/orcs/cache-summary.json',{'screens_retrieved':1})]:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(value))
            out=root/'outputs/orcs'/self.profile['profile_id'].removeprefix('orcs-')/'existing';out.mkdir(parents=True)
            # Vocabulary coverage is separately validated in real preflight.
            with patch('deathmap_ai.orcs_filters.validate_inputs'), patch('deathmap_ai.orcs_filters.validate_profile'), patch('deathmap_ai.orcs_filters.EXPECTED',{'ENZYME':['Cas9']}):
                with self.assertRaises(FileExistsError):execute(root,'existing')
            self.assertEqual(list(out.iterdir()),[])

    def test_authorized_workbook_transition_is_narrow_and_hash_verified(self):
        from deathmap_ai.sq01_io import preservation
        from deathmap_ai.orcs_filters import sha, write
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);target=root/'data/output-example/DeathMap-AI-v1-reference-output.xlsx'
            target.parent.mkdir(parents=True);target.write_bytes(b'original')
            original_hash=sha(target)
            backup=root/'outputs/orcs/filter-runs/fixture/workbook-original.xlsx';backup.parent.mkdir(parents=True);backup.write_bytes(b'original')
            (root/'docs').mkdir();write(root/'docs/sq01-preservation.json',{'before':{target.relative_to(root).as_posix():original_hash}})
            target.write_bytes(b'populated')
            with self.assertRaises(ValueError):preservation(root)
            write(root/'docs/orcs-workbook-transition.json',{'authority':'11 ORCS Filter Run and Excel Handoff.md','backup_path':backup.relative_to(root).as_posix(),'original_sha256':original_hash,'replacement_sha256':sha(target)})
            self.assertEqual(preservation(root)['changed_files'],[])
            backup.write_bytes(b'corrupted')
            with self.assertRaises(ValueError):preservation(root)

    def test_corrupt_json(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json';p.write_text('{')
            with self.assertRaises(json.JSONDecodeError):read(p)

if __name__=='__main__':unittest.main()
