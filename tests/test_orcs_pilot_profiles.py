"""Pilot preflight catches unsupported rules before candidate discovery."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pilot_preflight',ROOT/'scripts/validate_orcs_pilot_profiles.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class PilotProfileTests(unittest.TestCase):
    def setUp(self):
        self.profile=json.loads((ROOT/'searches/orcs/orcs-crispr-biological-classes-pilot-v01/profile.json').read_text(encoding='utf-8'))
        self.columns={'screen':{'ORGANISM_OFFICIAL','LIBRARY_TYPE','CELL_TYPE','NOTES','SCREEN_RATIONALE'},
                      'publication':{'TITLE','ABSTRACT'},'annotation':{'category'}}

    def test_active_owner_profile_validates(self):
        # The owner removed the other pilot families before authorizing CRISPR.
        # Tests must not recreate or depend on those abandoned configurations.
        names={'orcs-crispr-biological-classes-pilot-v01':4}
        for name,count in names.items():
            p=json.loads((ROOT/'searches/orcs'/name/'profile.json').read_text(encoding='utf-8'))
            baseline=copy.deepcopy(p)
            self.assertEqual(module.validate_profile(p,self.columns),count)
            self.assertEqual(p,baseline)

    def test_invalid_regex_or_unknown_field_fails(self):
        p=copy.deepcopy(self.profile);p['candidate_rules'][2]['test']['pattern']='['
        with self.assertRaises(ValueError):module.validate_profile(p,self.columns)
        p=copy.deepcopy(self.profile);p['candidate_rules'][2]['test']['fields']=['TYPO_FIELD']
        with self.assertRaises(ValueError):module.validate_profile(p,self.columns)

    def test_duplicate_rules_or_disabled_boundary_fails(self):
        p=copy.deepcopy(self.profile);p['candidate_rules'].append(copy.deepcopy(p['candidate_rules'][0]))
        with self.assertRaises(ValueError):module.validate_profile(p,self.columns)
        p=copy.deepcopy(self.profile);p['constraints']['no_icraft_runtime_dependency']=False
        with self.assertRaises(ValueError):module.validate_profile(p,self.columns)

    def test_unsupported_operator_or_changed_join_fails(self):
        p=copy.deepcopy(self.profile);p['candidate_rules'][0]['test']['operator']='contains'
        with self.assertRaises(ValueError):module.validate_profile(p,self.columns)
        p=copy.deepcopy(self.profile);p['filter_logic']['publication_join']='TITLE'
        with self.assertRaises(ValueError):module.validate_profile(p,self.columns)


if __name__=='__main__':unittest.main()
