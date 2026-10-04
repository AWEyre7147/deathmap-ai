"""Inspectable fixtures for identity, ontology and vocabulary preservation."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('annotations', Path(__file__).resolve().parents[1] / 'scripts/annotate_orcs_vocabularies.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ReferenceAnnotationTests(unittest.TestCase):
    def test_ambiguous_name_does_not_become_cancer_classification(self):
        records = {'one': {'species': ['9606']}, 'two': {'species': ['9606']}}
        result = module.select_identity('PC-3', {'9606'}, records, {'pc-3': {'one', 'two'}}, {})
        self.assertIsNone(result[0])
        self.assertEqual(result[1], 'ambiguous')

    def test_species_disambiguates_and_conflicting_source_is_preserved(self):
        records = {'human': {'species': ['9606']}, 'mouse': {'species': ['10090']}}
        exact = {'same': {'human', 'mouse'}}
        self.assertEqual(module.select_identity('same', {'10090'}, records, exact, {})[0], 'mouse')
        result = module.select_identity('same', {'9606'}, records, exact, {}, ['mouse'])
        self.assertEqual(result[:2], ('mouse', 'ORCS-linked accession with species conflict'))

    def test_derivative_qualifier_is_not_stripped(self):
        records = {'parent': {'species': ['9606']}}
        result = module.select_identity('A549-Cas9', {'9606'}, records, {'a549': {'parent'}}, {'a549': {'parent'}})
        self.assertIsNone(result[0])

    def test_obo_native_ids_missing_definitions_and_synonym_scope(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'efo.obo'
            path.write_text('format-version: 1.2\ndata-version: example-v1\n\n[Term]\nid: efo:EFO_0000001\nname: Example\nsynonym: "Precise" EXACT []\nsynonym: "Similar" RELATED []\n\n[Term]\nid: efo:EFO_0000002\nname: Second\ndef: "Reported definition." []\nis_obsolete: true\n', encoding='utf-8')
            terms, version = module.parse_obo(path, 'EFO')
            self.assertEqual(version, 'example-v1')
            self.assertEqual(terms['EFO:0000001']['definition'], '')
            self.assertEqual(terms['EFO:0000001']['synonyms'], ['Precise'])
            self.assertTrue(terms['EFO:0000002']['obsolete'])
            self.assertEqual(terms['EFO:0000002']['native_id'], 'efo:EFO_0000002')

    def test_description_retains_tissue_and_deduplicates_disease(self):
        record = {'names': ['A-549'], 'native_fields': {'OX': ['NCBI_TaxID=9606; ! Homo sapiens (Human)'],
            'DI': ['NCIt; C3512; Lung adenocarcinoma', 'Other; 1; Lung adenocarcinoma'],
            'CC': ['Derived from site: In situ; Lung; UBERON=UBERON_0002048.']}}
        text = module.reference_description(record)
        self.assertIn('In situ; Lung', text)
        self.assertEqual(text.count('Lung adenocarcinoma'), 1)
        self.assertNotIn('! ', text)

    def test_padded_owner_table_and_revision_preserve_terms(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'CELL_LINE.md'
            path.write_text('# CELL_LINE\n\nSelected descriptions are a pilot.\n\n| ORCS value | Old |\n| --- | --- |\n| A-549    |     |\n| Case+qualifier | |\n', encoding='utf-8')
            before = module.vocabulary_terms(path)
            module.render(path, ['ORCS value', 'Accession'], [[before[0], 'CVCL_0023'], [before[1], '']])
            self.assertEqual(before, module.vocabulary_terms(path))
            self.assertIn('All values were checked', path.read_text())

if __name__ == '__main__':
    unittest.main()
