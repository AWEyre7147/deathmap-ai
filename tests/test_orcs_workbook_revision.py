"""Inspectable migration fixtures: sequential keys, references and native counts."""
import copy
import socket
import unittest
from unittest.mock import patch
from deathmap_ai.orcs_workbook_revision import revise


class WorkbookRevisionTests(unittest.TestCase):
    def setUp(self):
        self.p={'sheets':{'Publications':[{'publication_id':'old-p','retrival_sources':'ORCS; evidence_id=old-e'}],
            'Screens':[{'screen_id':'old-s','publication_id':'old-p','source_evidence_ids':'old-e','reviewer_notes':'retain me','library_gene_count_reported':None}],
            'Sources & Evidence':[{'evidence_id':'old-e','supports_entity_type':'publication','supports_entity_id':'old-p'}]},
            'headers':{'Publications':['publication_id','retrival_sources','reviewer_decision','reviewer_notes'],
                       'Screens':['screen_id','publication_id','source_evidence_ids','reviewer_notes','library_gene_count_reported'],
                       'Sources & Evidence':['evidence_id','supports_entity_type','supports_entity_id']},
            'roles':{'old-s':{'SCREEN_ID':'native1','anchor_screen_ids':['native2'],'role':'direct_filter_hit'}},
            'native_mapping':{'publications':[{'PUBLICATION_ID':'nativepub','publication_id':'old-p','evidence_id':'old-e'}]},
            'cell_audit':[],'mapping':{},'publication_review':{'old-p':['conflict']}}
        self.wb={s:{'headers':self.p['headers'][s],'rows':copy.deepcopy(rows)} for s,rows in self.p['sheets'].items()}
        self.native=[{'SCREEN_ID':'native1','FULL_SIZE':'12345'}]

    def test_all_identifiers_and_foreign_keys_migrate(self):
        p=revise(self.p,self.native,self.wb)
        self.assertEqual(p['sheets']['Publications'][0]['publication_id'],'PUB-0001')
        self.assertEqual(p['sheets']['Screens'][0]['screen_id'],'SCR-0001')
        self.assertEqual(p['sheets']['Sources & Evidence'][0]['evidence_id'],'EVI-00001')
        self.assertEqual(p['sheets']['Screens'][0]['publication_id'],'PUB-0001')
        self.assertEqual(p['sheets']['Sources & Evidence'][0]['supports_entity_id'],'PUB-0001')
        self.assertEqual(p['native_mapping']['publications'][0]['PUBLICATION_ID'],'nativepub')
        self.assertEqual(p['roles']['SCR-0001']['anchor_screen_ids'],['native2'])
        self.assertEqual(len(p['id_migration']),3)

    def test_evidence_column_placement_and_attribution_preservation(self):
        p=revise(self.p,self.native,self.wb); headers=p['headers']['Publications']
        self.assertEqual(headers[headers.index('retrival_sources')+1],'evidence_id_link')
        self.assertEqual(headers[-2:],['reviewer_decision','reviewer_notes'])
        row=p['sheets']['Publications'][0]; self.assertEqual(row['retrival_sources'],'ORCS')
        self.assertEqual(row['evidence_id_link'],'EVI-00001')

    def test_count_typed_and_review_preserved(self):
        p=revise(self.p,self.native,self.wb); row=p['sheets']['Screens'][0]
        self.assertEqual(row['library_gene_count_reported'],12345)
        self.assertEqual(row['reviewer_notes'],'retain me')
        self.assertIn('FULL_SIZE',p['cell_audit'][0]['source_locator'])

    def test_missing_zero_and_invalid_counts(self):
        for value in [None,'','-','0']:
            self.native[0]['FULL_SIZE']=value
            self.assertEqual(revise(self.p,self.native,self.wb)['sheets']['Screens'][0]['library_gene_count_reported'],0 if value=='0' else None)
        self.native[0]['FULL_SIZE']='bad'
        with self.assertRaises(ValueError): revise(self.p,self.native,self.wb)

    def test_existing_sequential_ids_reserved_and_repeatable(self):
        p=revise(self.p,self.native,self.wb)
        secondwb={s:{'headers':p['headers'][s],'rows':copy.deepcopy(rows)} for s,rows in p['sheets'].items()}
        second=revise(p,self.native,secondwb)
        self.assertEqual(second['sheets'],p['sheets'])

    def test_formulas_and_identifier_references(self):
        self.p['sheets']['Screens'][0]['reviewer_notes']='=IF(A2="old-s",1,0)'
        p=revise(self.p,self.native,self.wb)
        self.assertEqual(p['sheets']['Screens'][0]['reviewer_notes'],'=IF(A2="SCR-0001",1,0)')

    def test_no_network_and_inputs_unchanged(self):
        before=copy.deepcopy(self.p)
        with patch.object(socket,'socket',side_effect=AssertionError('network forbidden')): revise(self.p,self.native,self.wb)
        self.assertEqual(self.p,before)

    def test_duplicate_id_is_error(self):
        self.p['sheets']['Publications']*=2
        with self.assertRaises(ValueError): revise(self.p,self.native,self.wb)

if __name__=='__main__': unittest.main()
