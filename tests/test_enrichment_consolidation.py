"""Offline joins and coverage semantics for the eight-source review workbook."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import openpyxl

from deathmap_ai.enrichment_consolidation import COUNTS, SHEETS, consolidate, master_rows


class ConsolidationTests(unittest.TestCase):
    def test_owner_template_aliases_export_without_changing_labels(self):
        from deathmap_ai.enrichment_export import export_registered
        root = Path(__file__).resolve().parents[1]
        template = root / 'data/templates/Enrichment-Synthesis-Template.xlsx'
        registration = json.loads(template.with_suffix('.manifest.json').read_text(encoding='utf-8'))
        tables = {s['source_table']: [] for s in registration['sheets']}
        tables['Library Supplemental Records'] = [{'Publication Index': 'PUB-0001',
                                                  'Supporting Material Index': 'LSUP-0001'}]
        tables['GEO Series Records'] = [{'Publication Index': 'PUB-0001', 'sample_organism': '=literal organism'}]
        tables['BioStudies Publication Records'] = [{'Publication Index': 'PUB-0001', 'Publication Date': '2022'}]
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'review.xlsx'
            export_registered(template, output, tables)
            book = openpyxl.load_workbook(output, read_only=True)
            self.assertEqual(book['Library Supplemental Records']['B2'].value, 'LSUP-0001')
            self.assertEqual(book['GEO Series Records']['I1'].value, 'Psample Organism')
            self.assertEqual(book['GEO Series Records']['I2'].value, '=literal organism')
            self.assertEqual(book['GEO Series Records']['I2'].data_type, 's')
            owner = openpyxl.load_workbook(template)
            expected_style = owner['GEO Series Records'].column_dimensions['A'].style
            self.assertEqual(book['GEO Series Records']['I2']._style_id, expected_style)
            self.assertEqual(book['GEO Series Records']['I2'].alignment,
                             owner._alignments[owner._cell_styles[expected_style].alignmentId])
            owner.close()
            self.assertEqual(book['BioStudies Publication Records']['E1'].value, 'Publication Date')
            self.assertEqual(book['BioStudies Publication Records']['E2'].value, '2022')
            book.close()

    def test_master_counts_distinct_resources_and_keeps_missing_publication(self):
        pubs = [{'PUBLICATION_ID': '1', 'TITLE': 'Fallback', 'JOURNAL': 'Journal'},
                {'PUBLICATION_ID': '2', 'TITLE': 'Missing metadata'}]
        registry = [{'ORCS Publication ID': str(i), 'Publication index': f'PUB-{i:04d}'} for i in (1, 2)]
        tables = {sheet: [] for sheet, _ in COUNTS.values()}
        tables['Figshare Item Records'] = [{'Publication Index': 'PUB-0001', 'Figshare Item Index': 'FGI-0001'}] * 2
        rows = master_rows(pubs, registry, [{'Publication Index': 'PUB-0001', 'Title': 'Retrieved',
                                           'Publication Date': '2022'}], tables)
        self.assertEqual(rows[0]['Figshare Items'], 1)
        self.assertEqual(rows[0]['Title'], 'Retrieved')
        self.assertEqual(rows[0]['Publication Date'], '2022')
        self.assertEqual(rows[1]['PubMed Records'], 0)
        self.assertEqual(rows[1]['Title'], 'Missing metadata')

    def test_invalid_resource_identity_is_rejected(self):
        tables = {sheet: [] for sheet, _ in COUNTS.values()}
        tables['ENA Study Records'] = [{'Publication Index': 'PUB-0001', 'Study Index': ''}]
        with self.assertRaisesRegex(ValueError, 'Missing resource identifier'):
            master_rows([], [], [], tables)

    def test_all_eight_sources_preserve_issues_and_never_modify_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def save(name, value):
                path = root / name
                path.write_text(json.dumps(value), encoding='utf-8')
                return path
            pubs = save('publications.json', [{'PUBLICATION_ID': '1', 'TITLE': 'Example'}])
            registry = save('registry.json', [{'ORCS Publication ID': '1', 'Publication index': 'PUB-0001'}])
            indices = save('indices.json', {'schema_version': 'enrichment-indices/1', 'namespaces': {}})
            sources = {}
            geo = {}
            for resource, mappings in SHEETS.items():
                rows = {native: [] for _, native in mappings}
                if resource == 'PubMed':
                    rows['Publication'] = [{'Publication Index': 'PUB-0001', 'Title': 'Retrieved'}]
                if resource == 'GEO':
                    geo = rows
                sources[resource] = save(resource + '.json', {
                    'display_rows' if resource == 'PubMed' else 'rows': rows,
                    'issues': ['Unresolved source request'] if resource == 'BioStudies' else [],
                    'status': 'incomplete' if resource == 'BioStudies' else 'complete'})
            before = {p: p.read_bytes() for p in root.iterdir()}
            with patch('deathmap_ai.geo_indexed_projection.project', return_value=geo):
                data = consolidate(pubs, registry, indices, sources)
                self.assertEqual(len(data['tables']), 28)
                self.assertEqual(data['sources']['BioStudies']['issues'], ['Unresolved source request'])
                self.assertEqual(data['sources']['BioStudies']['status'], 'incomplete')
                self.assertEqual(data['tables']['Publication Records'][0]['PubMed Records'], 1)
                self.assertEqual(before, {p: p.read_bytes() for p in root.iterdir()})
                sources.pop('Library')
                with self.assertRaisesRegex(ValueError, 'Exactly eight'):
                    consolidate(pubs, registry, indices, sources)


if __name__ == '__main__':
    unittest.main()
