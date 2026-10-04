"""Regression checks for relocation without altered metadata or rewritten history."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from deathmap_ai.orcs_paths import resolve_historical, RELOCATIONS, INDEX, CSV

class OrcsRelocationTests(unittest.TestCase):
    def test_missing_legacy_resolves_only_expected_bytes(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);old='outputs/orcs/cache/legacy/20260904T213941Z/orcs-screens.raw.json'
            target=root/INDEX;target.parent.mkdir(parents=True);target.write_bytes(b'fixture')
            expected=hashlib.sha256(b'fixture').hexdigest()
            with patch.dict(RELOCATIONS,{old:(INDEX,expected)},clear=True):
                self.assertEqual(resolve_historical(root/old),target)
                target.write_bytes(b'changed')
                with self.assertRaises(ValueError):resolve_historical(root/old)
    def test_existing_fixture_and_unrelated_missing_path_unchanged(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'example.json';p.write_bytes(b'original')
            self.assertEqual(resolve_historical(p),p)
            q=Path(t)/'unrelated/missing.json';self.assertEqual(resolve_historical(q),q)
    def test_real_relocated_files_match_recorded_hashes(self):
        root=Path(__file__).resolve().parents[1]
        for old,(new,expected) in RELOCATIONS.items():
            self.assertFalse((root/old).exists())
            self.assertEqual(resolve_historical(root/old),root/new)
            self.assertEqual(hashlib.sha256((root/new).read_bytes()).hexdigest(),expected)

if __name__=='__main__':unittest.main()
