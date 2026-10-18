"""Layout-only fixtures prove source values follow their renamed columns."""
import unittest
from deathmap_ai.synthesis_layout import layout_sheet


class SynthesisLayoutTests(unittest.TestCase):
    def test_repository_column_order_preserves_values(self):
        columns = ['Publication index', 'Resource', 'Accession', 'Native Entity Level', 'Reported Data Type', 'Title', 'Description']
        out = layout_sheet({'name': 'PubMed - Repository Records', 'headers': columns, 'rows': [columns]})
        self.assertEqual(out['name'], 'PubMed-Repository Links')
        self.assertEqual(out['headers'], ['Publication Index', 'Accession', 'Repository', 'Title', 'Description', 'Native Entity Level', 'Reported Data Type'])
        self.assertEqual(out['rows'][0][1], 'Accession')

    def test_native_case_variants_are_not_merged(self):
        out = layout_sheet({'name': 'AE - Sample metadata', 'headers': ['Study accession', 'Age', 'age'], 'rows': [['S1', 'adult', '10']]})
        self.assertEqual(out['headers'], ['ArrayExpress Study', 'Age', 'Age (2)'])
        self.assertEqual(out['rows'], [['S1', 'adult', '10']])
        self.assertEqual(out['columns'][-1]['source_header'], 'age')

    def test_sdrf_removal_is_explicit_and_row_coordinates_move_last(self):
        headers = ['Publication index', 'Study accession', 'Source name', 'Native data row', 'Native column', 'Native field', 'Original value', 'Part']
        out = layout_sheet({'name': 'AE - SDRF metadata', 'headers': headers, 'rows': [headers]})
        self.assertEqual(out['removed_headers'], ['Part'])
        self.assertEqual(out['headers'][-2:], ['ArrayExpress Row', 'ArrayExpress Column'])
        self.assertEqual(out['rows'][0][-2:], ['Native data row', 'Native column'])

    def test_geo_channel_suffix_is_only_removed_from_label(self):
        out = layout_sheet({'name': 'GEO - Sample Metadata', 'headers': ['GSM', 'organism_ch1'], 'rows': [['GSM1', 'human']]})
        self.assertEqual(out['headers'], ['GEO Sample', 'Organism'])
        self.assertEqual(out['columns'][1]['source_header'], 'organism_ch1')

    def test_repository_label_changes_preserve_accessions(self):
        out = layout_sheet({'name': 'Publication-repository links', 'headers': ['Publication index', 'Repository', 'Accession'],
                            'rows': [['PUB-0001', 'BioProject', 'PRJNA1']]})
        self.assertEqual(out['rows'], [['PUB-0001', 'NCBI BioProject', 'PRJNA1']])

    def test_geo_duplicate_display_columns_are_removed(self):
        out = layout_sheet({'name': 'GEO - Sample Metadata', 'headers': ['Publication index', 'GSM', 'GSE', 'series_id', 'geo_accession'],
                            'rows': [['PUB-0001', 'GSM1', 'GSE1', 'GSE1', 'GSM1']]})
        self.assertEqual(out['headers'], ['Publication Index', 'GEO Sample', 'GEO Study'])
        self.assertEqual(out['removed_headers'], ['series_id', 'geo_accession'])


if __name__ == '__main__':
    unittest.main()
