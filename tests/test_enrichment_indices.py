"""Sequential identifiers retain record identity as cohorts change."""
from pathlib import Path
import tempfile
import unittest
from deathmap_ai.enrichment_indices import assign_indices, native_key

ROOT = Path(__file__).resolve().parents[1]


class IndexTests(unittest.TestCase):
    def test_appending_and_reordering_never_renumber_existing_keys(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            path=Path(t)/'indices.json'
            b=native_key('study','b.xlsx');c=native_key('study','c.xlsx');a=native_key('study','a.xlsx')
            first=assign_indices('BST',[c,b],path)
            self.assertEqual(first,{b:'BST-0001',c:'BST-0002'})
            second=assign_indices('BST',[a,c,b],path)
            self.assertEqual(second[b],first[b]);self.assertEqual(second[c],first[c])
            self.assertEqual(second[a],'BST-0003')
            self.assertEqual(assign_indices('ELS',[b],path)[b],'ELS-0001')
            self.assertFalse(path.with_suffix('.json.lock').exists())

    def test_existing_lock_is_not_removed(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            path=Path(t)/'indices.json';lock=path.with_suffix('.json.lock');lock.write_text('busy')
            with self.assertRaises(FileExistsError):assign_indices('BST',[native_key('a')],path)
            self.assertEqual(lock.read_text(),'busy')
