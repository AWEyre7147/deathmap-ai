"""Small native fixtures verify CRISPR gates, inference boundaries and expansion."""
import copy
import json
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch
from deathmap_ai import orcs_crispr_pilot as pilot
from deathmap_ai.orcs_crispr_pilot import evaluate,test_rule,project
from deathmap_ai.evidence_model import v6_allowed

ROOT=Path(__file__).resolve().parents[1]


class PilotTests(unittest.TestCase):
    def test_flat_profiles_preserve_output_namespaces_and_overwrite_refusal(self):
        # Reach the real overwrite guard with tiny saved-input stand-ins, before
        # evaluation or export. Flattening must not pool every search under "orcs".
        profiles = {p.name: json.loads(p.read_text(encoding='utf-8'))
                    for p in (ROOT / 'searches/orcs').glob('*.json')}
        self.assertEqual(len(profiles), 4)
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as temporary:
            root = Path(temporary)
            (root / 'scripts').mkdir()
            (root / 'scripts/validate_orcs_pilot_profiles.py').write_text(
                "def preflight(*args):\n    return {'input_hashes': {}}\n", encoding='utf-8')

            def read_fixture(path):
                name = Path(path).name
                if name in profiles:
                    return copy.deepcopy(profiles[name])
                return {'annotations.json': {'cache_sha256': 'fixture'},
                        'cache-summary.json': {'screens_retrieved': 0},
                        'publication-index.manifest.json': {'publication_count': 0},
                        'screen-index.json': [], 'publication-index.json': []}[name]

            with patch.object(pilot, '_read', side_effect=read_fixture), \
                    patch.object(pilot, '_hash', return_value='fixture'), \
                    patch('deathmap_ai.orcs_filters.validate_inputs'):
                for name in profiles:
                    with self.subTest(profile=name):
                        destination = root / 'outputs/orcs' / Path(name).stem / 'existing'
                        destination.mkdir(parents=True)
                        with self.assertRaises(FileExistsError):
                            pilot.execute(root, run_id='existing', profile_path='searches/orcs/' + name)

    def setUp(self):
        self.p=json.loads((ROOT/'searches/orcs/orcs-crispr-biological-classes-pilot-v01.json').read_text(encoding='utf-8'))
        self.pub=[{'PUBLICATION_ID':'1','SOURCE_TYPE':'pubmed','SOURCE_ID':'123','TITLE':'Fixture','PUBLICATION_DATE':'2020-01-01'}]
        self.refs={'cell_lines':[{'value':'cancer','category':'Cancer cell line','accession':'CVCL_0001'}]}
    def row(self,sid='1',**changes):
        return {'SCREEN_ID':sid,'SOURCE_TYPE':'pubmed','SOURCE_ID':'123','CELL_LINE':'cancer','CELL_TYPE':'T cells',
            'ORGANISM_OFFICIAL':'Homo sapiens','LIBRARY_TYPE':'CRISPRn',**changes}
    def test_companion_expansion_retains_common_failures_and_overlap(self):
        rows=[self.row(),self.row('2',LIBRARY_TYPE='unrelated'),self.row('3',SOURCE_ID='999',LIBRARY_TYPE='unrelated')]
        frozen=copy.deepcopy(rows);audit,s=evaluate(rows,self.pub,self.refs,self.p)
        self.assertEqual([x['role'] for x in audit],['direct_rule_candidate','publication_companion','excluded'])
        self.assertEqual(s['companions_failing_common_filters'],1)
        self.assertEqual(s['rule_seed_counts']['C1_cancer_reference'],1)
        self.assertEqual(s['rule_seed_counts']['C3_immune_lineage'],1)
        self.assertEqual(rows,frozen)
    def test_missing_only_fallback_and_multivalue(self):
        rows=[self.row(CELL_LINE='unknown',CELL_TYPE='carcinoma',LIBRARY_TYPE='CRISPRn | CRISPRi')]
        audit,s=evaluate(rows,self.pub,self.refs,self.p)
        self.assertEqual(s['direct_rule_candidates'],1)
        self.assertEqual(audit[0]['matched_rule_ids'],['C2_cancer_native_fallback'])
        refs={'cell_lines':[{'value':'unknown','category':'Normal cell line'}]}
        _,s=evaluate(rows,self.pub,refs,self.p);self.assertEqual(s['direct_rule_candidates'],0)
    def test_regex_independent_fields_no_dotall_and_spans(self):
        node={'scope':'screen','fields':['A','B'],'operator':'regex','pattern':'single.{0,10}RNA','flags':'IGNORECASE'}
        self.assertEqual(test_rule(node,{'A':'single','B':'RNA'},None)['status'],'fail')
        self.assertEqual(test_rule(node,{'A':'single\nRNA'},None)['status'],'fail')
        result=test_rule(node,{'A':'Single RNA'},None)
        self.assertEqual(result['observations'][0]['matches'][0]['span'],[0,10])
    def test_ambiguous_keys_fail(self):
        with self.assertRaises(ValueError):evaluate([self.row()],self.pub*2,self.refs,self.p)
        with self.assertRaises(ValueError):evaluate([self.row(),self.row()],self.pub,self.refs,self.p)
    def test_publication_projection_and_empty_dataset_entities(self):
        audit,_=evaluate([self.row()],self.pub,self.refs,self.p);p=project(audit,self.pub)
        self.assertEqual(p['sheets']['Screens'][0]['publication_id'],'PUB-0001')
        self.assertEqual(p['sheets']['Datasets'],[]);self.assertEqual(p['sheets']['Screen Groups'],[])
    def test_family_guard_preserves_old_v01_boundary(self):
        self.assertTrue(v6_allowed(self.p['profile_id'],1,self.p['schema_version']))
        self.assertTrue(v6_allowed('orcs-cancer-cell-crispr-knockout-v01',1))
        self.assertFalse(v6_allowed('orcs-clinical-omics-publication-candidates-pilot-v01',1,self.p['schema_version']))

    def test_inclusive_publication_year_bounds_and_missing_dates(self):
        self.p['publication_year_range']={'start':2014,'end':2022}
        for reported, expected in [('2013-12-31',0),('2014',1),('2022-12-31',1),('2023',0),('',0),('unknown',0)]:
            self.pub[0]['PUBLICATION_DATE']=reported
            audit,summary=evaluate([self.row(),self.row('2',LIBRARY_TYPE='unrelated')],self.pub,self.refs,self.p)
            self.assertEqual(summary['direct_rule_candidates'],expected,reported)
            self.assertEqual(summary['publication_companions'],expected,reported)
            self.assertIn('publication_year_filter',audit[0])

    def test_unbounded_copy_preserves_criteria_and_missing_date_behavior(self):
        unbounded=json.loads((ROOT/'searches/orcs/orcs-crispr-biological-classes-pilot-v02.json').read_text(encoding='utf-8'))
        self.assertNotIn('publication_year_range',unbounded)
        for key in ('common_filters','candidate_rules','expansion','constraints','evidence','input'):
            self.assertEqual(self.p[key],unbounded[key])
        self.pub[0].pop('PUBLICATION_DATE')
        _,summary=evaluate([self.row()],self.pub,self.refs,unbounded)
        self.assertEqual(summary['direct_rule_candidates'],1)
        self.assertTrue(v6_allowed(unbounded['profile_id'],1,unbounded['schema_version']))


if __name__=='__main__':unittest.main()
