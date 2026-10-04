"""Inspectable native-value fixtures for owner-directed local vocabulary export."""
import importlib.util
from pathlib import Path
import tempfile
import json
import unittest

spec = importlib.util.spec_from_file_location('local_vocabs', Path(__file__).resolve().parents[1] / 'scripts/export_orcs_local_vocabularies.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LocalVocabularyTests(unittest.TestCase):
    def test_independent_selections(self):
        text = '| `A` | include | exclude | extract uniques; annotate |\n| `B` | exclude | include | |'
        self.assertEqual(module.selections(text), [('A', True)])

    def test_exact_values_missing_counts_and_blank_annotations(self):
        result = module.render([{'A': 'z'}, {'A': 'Alpha'}, {'A': 'alpha'},
                                {'A': 'z'}, {'A': '-'}, {}, {'A': None}, {'A': ''}],
                               ['A'], True, 'source.json')
        self.assertIn('Unique nonempty values: 4', result)
        self.assertIn('absent: 1; null: 1; empty string: 1', result)
        self.assertTrue(result.index('| Alpha | |') < result.index('| alpha | |') < result.index('| z | |'))
        self.assertIn('| - | |', result)

    def test_score_union_and_markdown_escaping(self):
        result = module.render([{'SCORE.1_TYPE': 'A|B', 'SCORE.2_TYPE': 'A|B'},
                                {'SCORE.1_TYPE': 'C', 'SCORE.2_TYPE': '-'}],
                               ['SCORE.1_TYPE', 'SCORE.2_TYPE'], False, 'source.json')
        self.assertIn('SCORE.#_TYPE', result)
        self.assertIn('Unique nonempty values: 3', result)
        self.assertEqual(result.count('| A\\|B |'), 1)

    def test_existing_files_protected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            snapshot = root / 'source.json'
            snapshot.write_text(json.dumps([{'A': 'x', 'B': 'y'}]), encoding='utf-8')
            index = root / 'index.md'
            index.write_text('| `A` | include | include | |\n| `B` | include | include | |', encoding='utf-8')
            (root / 'B.md').write_text('Curated description', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                module.export(snapshot, index)
            self.assertFalse((root / 'A.md').exists())
            self.assertEqual((root / 'B.md').read_text(), 'Curated description')


if __name__ == '__main__':
    unittest.main()
