"""Inspect profile boundaries and corrected reviewer/evidence workbook behavior."""
import json
from pathlib import Path
import unittest
from deathmap_ai.evidence_model import build_evidence
from deathmap_ai.orcs_profile_rules import evaluate
from deathmap_ai.orcs_evidence_v6 import adapt

ROOT=Path(__file__).resolve().parents[1]


class RefreshTests(unittest.TestCase):
    def test_v02_fallback_missing_only_multivalue_and_companion(self):
        p=json.loads((ROOT/'searches/orcs/cancer-cell-crispr-knockout-v02/profile.json').read_text())
        def row(sid,**changes):
            return {'SCREEN_ID':sid,'SOURCE_TYPE':'pubmed','SOURCE_ID':'123','CELL_LINE':'unknown','CELL_TYPE':'carcinoma',
                'ORGANISM_OFFICIAL':'Homo sapiens','SCREEN_FORMAT':'Pool','PHENOTYPE':'cell viability | cell migration',**changes}
        rows=[row('1'),row('2',CELL_LINE='normal'),row('3',SOURCE_ID='999',CELL_TYPE='unknown'),row('4',ORGANISM_OFFICIAL='wrong')]
        pubs=[{'PUBLICATION_ID':'1','SOURCE_TYPE':'pubmed','SOURCE_ID':'123'}]
        audit,summary=evaluate(rows,pubs,{'cell_lines':[{'value':'normal','category':'Normal cell line'}]},p)
        self.assertEqual([i['role'] for i in audit],['direct_rule_candidate','publication_companion','unresolved_category','publication_companion'])
        self.assertEqual(summary['fallback_candidates'],1)
        self.assertEqual(audit[0]['descriptive_tags']['perturbation_modality'],'unresolved')
        self.assertNotIn('fallback_label',audit[1]['candidate_rules']['CELL_LINE'])

    def test_numbering_across_source_and_inference_batches(self):
        def observation(status):
            return {'source':{'name':'ORCS','type':'screen','native_record_id':'1'},'supports':{'entity_type':'screen','entity_id':'SCR-0001','fields':['x']},
                'claim':'Fixture claim','supporting_value':'x','raw_record':{},'evidence_basis':'inferred' if status=='inferred' else 'structured_field','evidence_status':status}
        a,ledger=build_evidence([observation('direct')],run_id='test',profile_id='x',profile_version=2)
        b,_=build_evidence([observation('inferred')],run_id='test',profile_id='x',profile_version=2,first_index=len(ledger)+1)
        self.assertEqual([r['evidence_id'] for r in a+b],['EVI-00001','EVI-00002'])
        self.assertEqual(len(ledger[0]['source_identity_sha256']),64)

    def test_adapter_clears_reviewer_notes_and_removed_columns(self):
        projection={'sheets':{'Screens':[{'screen_id':'SCR-0001','screen_notes':'generated diagnostic','reviewer_decision':None,'reviewer_notes':None}],
            'Publications':[]},'roles':{'SCR-0001':{'SCREEN_ID':'1'}}}
        p,_=adapt(projection,[{'SCREEN_ID':'1'}],[],{'cell_lines':[]},{'run_id':'test'},{'profile_id':'x','profile_version':2})
        row=p['sheets']['Screens'][0]
        self.assertIsNone(row['screen_notes']);self.assertNotIn('reviewer_decision',row);self.assertNotIn('reviewer_notes',row)
        self.assertIn('unresolved reference accession',row['curation_status'])
        self.assertTrue(p['evidence_issues'])
