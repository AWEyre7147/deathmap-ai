"""Regression fixtures for exact filtering, provenance and conservative entity projection."""
import copy
import json
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from deathmap_ai.orcs_filters import EXPECTED, evaluate, read, validate_profile, validate_inputs, publication_key
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
    def test_corrupt_json(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json';p.write_text('{')
            with self.assertRaises(json.JSONDecodeError):read(p)

if __name__=='__main__':unittest.main()
