"""Verify stable GEO indices and atomic publication/series/sample memberships."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from deathmap_ai.geo_indexed_projection import project

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    return {'publications': {
        '1': {'publication': {'PMID': '1', 'PUBLICATION_ID': '10', 'Publication Index': 'PUB-0001'}},
        'orcs-20': {'publication': {'PUBLICATION_ID': '20', 'Publication Index': 'PUB-0002'}}},
        'series': {gse: {'publication_keys': ['1', 'orcs-20'], 'fields': {
            'Series_geo_accession': [gse], 'Series_summary': ['First', 'Second'],
            'Series_sample_id': ['GSM1'], 'Series_platform_id': ['GPL1']}}
            for gse in ('GSE1', 'GSE2')},
        'samples': {'GSM1': {'fields': {'Sample_geo_accession': ['GSM1'],
            'Sample_characteristics_ch1': ['A', 'B'], 'Sample_platform_id': ['GPL1'],
            'Sample_relation': ['BioSample: SAMN1']}}}}


class GeoIndexedTests(unittest.TestCase):
    def test_shared_entities_keep_indices_and_one_publication_per_row(self):
        database = fixture()
        original = copy.deepcopy(database)
        rows = project(database)
        self.assertEqual(len(rows['Series Records']), 4)
        self.assertEqual(len(rows['Sample Metadata']), 4)
        self.assertEqual(len({r['Sample Index'] for r in rows['Sample Metadata']}), 1)
        expected = {('PUB-0001', 'GESE-0001'), ('PUB-0001', 'GESE-0002'),
                    ('PUB-0002', 'GESE-0001'), ('PUB-0002', 'GESE-0002')}
        self.assertEqual({(r['Publication Index'], r['Series Index']) for r in rows['Sample Metadata']}, expected)
        self.assertEqual(rows['Sample Metadata'][0]['characteristics_ch1'], 'A\nB')
        self.assertEqual(rows['Series Records'][0]['summary'], 'First\nSecond')
        self.assertEqual(database, original)
        identifiers = rows['Repository Identifiers']
        visible = [tuple(r.get(k) for k in ('Publication Index', 'Identifier', 'Resource', 'Entity Level', 'Native Field')) for r in identifiers]
        self.assertEqual(len(visible), len(set(visible)))
        self.assertTrue(all('\n' not in r['Publication Index'] for table in rows.values() for r in table))

    def test_registry_stability_and_identity_conflicts(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            indices = Path(directory) / 'indices.json'
            database = fixture()
            first = project(database, index_registry=indices)
            database['series']['GSE0'] = copy.deepcopy(database['series']['GSE1'])
            database['series']['GSE0']['fields']['Series_geo_accession'] = ['GSE0']
            again = project(database, index_registry=indices)
            self.assertEqual(first['Sample Metadata'], again['Sample Metadata'][:4])
            registry = Path(directory) / 'pubs.json'
            registry.write_text(json.dumps([
                {'Publication index': 'PUB-0010', 'ORCS Publication ID': '10', 'PMID': '9'},
                {'Publication index': 'PUB-0020', 'ORCS Publication ID': '99', 'PMID': '1'}]))
            with self.assertRaisesRegex(ValueError, 'Conflicting'):
                project(database, registry)
            database['series']['GSE1']['publication_keys'].append('unknown')
            with self.assertRaisesRegex(ValueError, 'unknown publication'):
                project(database)
