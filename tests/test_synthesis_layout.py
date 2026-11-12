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

    def test_biostudies_native_indices_and_accessions_survive_layout(self):
        headers=['Publication index','BioStudies Accession','BioStudies Index','File URL']
        values=['PUB-0001','E-MTAB-1','BST-0001','https://example.org/file']
        result=layout_sheet({'name':'BioStudies - Supplementary Files','headers':headers,'rows':[values]})
        self.assertEqual(result['name'],'BioStudies Files')
        self.assertEqual(result['headers'],['Publication Index','BioStudies Accession','BioStudies Index','File URL'])
        self.assertEqual(result['rows'],[values])

    def test_geo_channel_suffix_is_only_removed_from_label(self):
        out = layout_sheet({'name': 'GEO - Sample Metadata', 'headers': ['GSM', 'organism_ch1'], 'rows': [['GSM1', 'human']]})
        self.assertEqual(out['headers'], ['GEO Sample Accession', 'Organism'])
        self.assertEqual(out['columns'][1]['source_header'], 'organism_ch1')

    def test_repository_label_changes_preserve_accessions(self):
        out = layout_sheet({'name': 'Publication-repository links', 'headers': ['Publication index', 'Repository', 'Accession'],
                            'rows': [['PUB-0001', 'BioProject', 'PRJNA1']]})
        self.assertEqual(out['rows'], [['PUB-0001', 'NCBI BioProject', 'PRJNA1']])

    def test_geo_duplicate_display_columns_are_removed(self):
        out = layout_sheet({'name': 'GEO - Sample Metadata', 'headers': ['Publication index', 'GSM', 'GSE', 'series_id', 'geo_accession'],
                            'rows': [['PUB-0001', 'GSM1', 'GSE1', 'GSE1', 'GSM1']]})
        self.assertEqual(out['headers'], ['Publication Index', 'GEO Sample Accession', 'GEO Series Accession'])
        self.assertEqual(out['removed_headers'], ['series_id', 'geo_accession'])


if __name__ == '__main__':
    unittest.main()
