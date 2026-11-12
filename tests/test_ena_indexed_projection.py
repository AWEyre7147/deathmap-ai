"""Check ENA identity stability and reporting-study relationship boundaries."""
import copy
import argparse
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

import openpyxl

from deathmap_ai.ena_indexed_projection import project

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    row = {'run_accession': 'SRR1', 'study_accession': 'PRJNA2',
        'sample_accession': 'SAMN1', 'experiment_accession': 'SRX1',
        'sample_title': 'Sample one', 'sample_description': 'Native sample',
        'scientific_name': 'Homo sapiens', 'experiment_title': 'Experiment',
        'read_count': '0', 'fastq_ftp': 'a.fastq.gz;b.fastq.gz',
        'fastq_md5': 'x;y', 'fastq_bytes': '12'}
    studies = {key: {'title': key, 'runs': [copy.deepcopy(row)], 'associations': [
        {'publication_key': pmid}], 'source_url': 'https://example.org/' + key,
        'sample_count': 1, 'experiment_count': 1, 'run_count': 1}
        for key, pmid in [('PRJNA1', '123'), ('PRJNA2', '456')]}
    pubs = [{'key': pmid, 'publication': {'PMID': pmid, 'Publication Index': index,
        'TITLE': 'Title'}} for pmid, index in [('123', 'PUB-0001'), ('456', 'PUB-0002'), ('789', 'PUB-0003')]]
    return {'publications': pubs, 'studies': studies}


class ENAIndexedTests(unittest.TestCase):
    def test_pipeline_collection_and_standalone_export_share_atomic_publication_rows(self):
        from deathmap_ai.ena_collection import Transport, REPORT_FIELDS
        from deathmap_ai.enrichment_commands import run_stage
        from deathmap_ai.ena_workbook import export_workbook

        def opener(request, timeout):
            path = urlsplit(request.full_url).path
            if '/xref/' in path:
                body = b'[{"Target Primary Accession":"PRJNA1"}]'
            elif path.endswith('/search'):
                body = b'[]'
            elif '/browser/api/xml/' in path:
                body = b'<PROJECT accession="PRJNA1"><IDENTIFIERS><PRIMARY_ID>PRJNA1</PRIMARY_ID></IDENTIFIERS><TITLE>Shared study</TITLE></PROJECT>'
            elif path.endswith('/returnFields'):
                body = ('columnId\n' + '\n'.join(REPORT_FIELDS) + '\n').encode()
            elif path.endswith('/filereport'):
                native = fixture()['studies']['PRJNA1']['runs'][0]
                native['fastq_bytes'] = '12;13'
                body = ('\t'.join(REPORT_FIELDS) + '\n' + '\t'.join(native.get(k, '') for k in REPORT_FIELDS) + '\n').encode()
            else:
                self.fail('Unexpected metadata request: ' + request.full_url)
            response = io.BytesIO(body)
            response.status = 200
            return response

        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as folder:
            folder = Path(folder)
            publications = folder / 'publications.json'
            publications.write_text(json.dumps([{'PUBLICATION_ID': str(i), 'PMID': str(i),
                'TITLE': 'Paper ' + str(i), 'Publication Index': f'PUB-{i:04d}'} for i in (1, 2)]))
            geo, pubmed = folder / 'geo.json', folder / 'pubmed.json'
            geo.write_text('{"series":{}}')
            pubmed.write_text('{"rows":{"Repository Records":[],"SRA Accessions":[]}}')
            registry = folder / 'publications-registry.json'
            registry.write_text('[]')
            indices = folder / 'entity-indices.json'
            args = argparse.Namespace(stage='ena', root=ROOT, output_dir=folder / 'run',
                publication_index=publications, geo=geo, pubmed=pubmed, registry=registry,
                template=None, cache_root=[], metadata_only_project=[])
            with patch('deathmap_ai.ena_collection.Transport',
                       side_effect=lambda path, caches: Transport(path, caches, opener=opener)), \
                 patch('deathmap_ai.enrichment_indices.DEFAULT_REGISTRY', indices), redirect_stdout(io.StringIO()):
                run_stage(args)
            source = args.output_dir / 'database.json'
            standalone = folder / 'standalone.xlsx'
            export_workbook(source, ROOT / 'data/templates/ENA-Enrichment-Template.xlsx', standalone,
                publication_registry=registry, index_registry=indices)
            for output in (args.output_dir / 'ENA-Enrichment.xlsx', standalone):
                book = openpyxl.load_workbook(output, read_only=True)
                try:
                    for name in ('Studies', 'Samples', 'Experiments', 'Runs', 'Files'):
                        records = list(book[name].values)[1:]
                        self.assertEqual({r[0] for r in records}, {'PUB-0001', 'PUB-0002'})
                        self.assertTrue(all('\n' not in r[0] for r in records))
                        self.assertEqual(len({r[1] for r in records}), 1)
                finally:
                    book.close()

    def test_shared_study_has_one_publication_per_row_at_every_level(self):
        database = fixture()
        # Repeated discovery evidence must not multiply publication associations.
        database['studies']['PRJNA1']['associations'].extend([
            {'publication_key': '456'}, {'publication_key': '456'}])
        result = project(database)
        expected = {('PUB-0001', 'ENST-0001'), ('PUB-0002', 'ENST-0001'),
                    ('PUB-0002', 'ENST-0002')}
        for sheet, entity in [('Studies', 'Study Index'), ('Samples', 'Sample Index'),
                              ('Experiments', 'Experiment Index'), ('Runs', 'Run Index'),
                              ('Files', 'Run Index')]:
            self.assertEqual({(r['Publication Index'], r['Study Index']) for r in result[sheet]}, expected)
            self.assertTrue(all('\n' not in r['Publication Index'] for r in result[sheet]))
            self.assertEqual(len(result[sheet]), 6 if sheet == 'Files' else 3)
            same_study = [r for r in result[sheet] if r['Study Index'] == 'ENST-0001']
            self.assertEqual(len({r[entity] for r in same_study}), 1)
        self.assertEqual(len(result['Publications']), 2)
        self.assertEqual({r['Run Accession'] for r in result['Runs']}, {'SRR1'})

    def test_contexts_are_not_cross_joined_and_entities_keep_indices(self):
        result = project(fixture())
        self.assertEqual(len(result['Publications']), 2)
        self.assertEqual(len(result['Samples']), 2)
        self.assertEqual(len({r['Sample Index'] for r in result['Samples']}), 1)
        for sheet in ('Samples', 'Experiments', 'Runs', 'Files'):
            contexts = {(r['Publication Index'], r['Study Index']) for r in result[sheet]}
            self.assertEqual(contexts, {('PUB-0001', 'ENST-0001'), ('PUB-0002', 'ENST-0002')})
        for row in result['Files']:
            self.assertEqual(row['Run Index'], result['Runs'][0]['Run Index'])
        self.assertEqual(result['Runs'][0]['Read Count'], 0)
        self.assertIsNone(result['Runs'][0]['Base Count'])
        self.assertEqual([r['File Position'] for r in result['Files']], [1, 2, 1, 2])
        self.assertIsNone(result['Files'][1]['Size (Bytes)'])

    def test_conflicting_source_values_survive_and_no_input_is_mutated(self):
        database = fixture()
        database['studies']['PRJNA1']['runs'].append(copy.deepcopy(database['studies']['PRJNA1']['runs'][0]))
        database['studies']['PRJNA1']['runs'][-1]['sample_title'] = 'Different title'
        before = copy.deepcopy(database)
        result = project(database)
        self.assertEqual(len(result['Samples']), 3)
        self.assertEqual(len(result['Runs']), 2)
        self.assertEqual(database, before)

    def test_stable_registry_and_unexpanded_counts(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as folder:
            registry = Path(folder) / 'indices.json'
            database = fixture()
            initial = project(database, index_registry=registry)
            database['studies']['PRJNA0'] = {'runs': [], 'associations': [], 'title': 'Broad'}
            revised = project(database, index_registry=registry)
            self.assertEqual(initial['Runs'], revised['Runs'])
            broad = revised['Studies'][0]
            self.assertIsNone(broad['Run Count'])
            self.assertIsNone(broad['Sample Count'])

    def test_publication_registry_conflict_and_dangling_links_fail(self):
        database = fixture()
        database['studies']['PRJNA1']['associations'].append({'publication_key': 'missing'})
        with self.assertRaisesRegex(ValueError, 'unknown publication'):
            project(database)
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as folder:
            registry = Path(folder) / 'pubs.json'
            registry.write_text(json.dumps([
                {'ORCS Publication ID': '1', 'PMID': '999', 'Publication index': 'PUB-0010'},
                {'ORCS Publication ID': '2', 'PMID': '123', 'Publication index': 'PUB-0011'}]))
            database = fixture()
            database['publications'][0]['publication']['PUBLICATION_ID'] = '1'
            with self.assertRaisesRegex(ValueError, 'Conflicting'):
                project(database, registry)
