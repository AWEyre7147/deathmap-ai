"""Exercise DOI-only discovery, evidence integrity and hits-only template export."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import openpyxl
from deathmap_ai.figshare_enrichment import API, SEARCH, PAGE_SIZE, Transport, collect_one, project, run_collection
from deathmap_ai.enrichment_commands import run_stage

ROOT = Path(__file__).resolve().parents[1]
PUB = {'Publication Index': 'PUB-0001', 'DOI': '10.1000/example', 'Title': 'Publication'}


def metadata():
    return {'id': 1, 'resource_doi': PUB['DOI'], 'title': '=native title', 'description': '<p>=native description</p>',
        'doi': '10.1371/example.g001', 'defined_type_name': 'figure', 'version': 1,
        'is_public': True, 'is_confidential': False, 'is_metadata_record': False, 'download_disabled': False,
        'size': 0, 'keywords': ['CRISPR'], 'tags': None, 'categories': [{'title': 'Genetics'}],
        'license': {'name': 'CC BY 4.0'}, 'files': [{'id': 10, 'name': 'data.xlsx', 'size': 0,
            'is_link_only': False, 'download_url': 'https://ndownloader.figshare.com/files/10'}]}


def cached(folder, url, query, value):
    native = folder / 'native'
    native.mkdir(parents=True, exist_ok=True)
    key = Transport._key(url, query)
    body = json.dumps(value).encode()
    (native / (key + '.body')).write_bytes(body)
    (native / (key + '.json')).write_text(json.dumps({'url': url, 'query': query,
        'sha256': hashlib.sha256(body).hexdigest(), 'http_status': 200, 'retrieved_utc': '2026-01-01T00:00:00Z'}))
    return native / (key + '.body')


class FigshareTests(unittest.TestCase):
    def test_pagination_dedup_and_no_citation_substitution(self):
        calls = []
        class Fake:
            def get(self, url, query=None):
                calls.append((url, query))
                if query is not None:
                    self_outer.assertEqual(set(query), {'resource_doi', 'page', 'page_size'})
                    return ([{'id': 1}] * PAGE_SIZE if query['page'] == 1 else []), {'file': 'fixture'}
                return metadata(), {'file': 'fixture'}
        self_outer = self
        result = collect_one(PUB, Fake())
        self.assertEqual(result['outcome'], 'retrieved')
        self.assertTrue(result['search_complete'])
        self.assertEqual(len(result['items']), 1)
        self.assertEqual(len(calls), 3)
        wrong = metadata()
        wrong['resource_doi'] = '10.1000/other'
        wrong['related_materials'] = [{'identifier': PUB['DOI'], 'relation': 'References'}]
        with patch.object(Fake, 'get', side_effect=[([{'id': 1}], {}), (wrong, {})]):
            rejected = collect_one(PUB, Fake())
        self.assertEqual(rejected['outcome'], 'failed')
        self.assertFalse(project([rejected])['Publications'])

    def test_failures_and_pagination_cap_are_not_no_hits(self):
        class Broken:
            def get(self, *args):
                raise OSError('connection reset')
        self.assertEqual(collect_one(PUB, Broken())['outcome'], 'failed')
        class Endless:
            def get(self, url, query=None):
                return ([{'id': 1}] * PAGE_SIZE, {}) if query else (metadata(), {})
        with patch('deathmap_ai.figshare_enrichment.MAX_PAGES', 1):
            capped = collect_one(PUB, Endless())
        self.assertEqual(capped['outcome'], 'partial')
        self.assertFalse(capped['search_complete'])

    def test_transport_refuses_other_searches_and_file_downloads(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            transport = Transport(Path(directory), offline=True)
            for query in [{'search_for': 'CRISPR'}, {'pmid': '123'}, {'resource_doi': PUB['DOI'], 'page': 1, 'page_size': PAGE_SIZE, 'search_for': 'title'}]:
                with self.assertRaisesRegex(ValueError, 'scope'):
                    transport.get(SEARCH, query)
            with self.assertRaisesRegex(ValueError, 'scope'):
                transport.get('https://ndownloader.figshare.com/files/10')

    def test_cache_hash_and_request_body_identity(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            folder = Path(directory)
            cache = folder / 'cache'
            query = {'resource_doi': PUB['DOI'], 'page': 1, 'page_size': PAGE_SIZE}
            body = cached(cache, SEARCH, query, [])
            output = folder / 'run'
            output.mkdir()
            transport = Transport(output, [cache], offline=True)
            _, receipt = transport.get(SEARCH, query)
            self.assertEqual(receipt['retrieved_utc'], '2026-01-01T00:00:00Z')
            with self.assertRaisesRegex(ValueError, 'offline cache'):
                transport.get(SEARCH, {**query, 'page': 2})
            body.write_bytes(b'tampered')
            fresh = folder / 'fresh'
            fresh.mkdir()
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                Transport(fresh, [cache], offline=True).get(SEARCH, query)

    def test_shared_entities_keep_indices_and_no_hits_have_no_rows(self):
        first = {'publication': PUB, 'items': [{'metadata': metadata()}], 'issues': []}
        second = copy.deepcopy(first)
        second['publication']['Publication Index'] = 'PUB-0002'
        empty = {'publication': {'Publication Index': 'PUB-0003'}, 'items': [], 'issues': []}
        result = project([first, second, empty])
        self.assertEqual(len(result['Publications']), 2)
        for name, key in [('Items', 'Figshare Item Index'), ('Files', 'Figshare File Index')]:
            self.assertEqual(len({r[key] for r in result[name]}), 1)
            self.assertEqual({r['Publication Index'] for r in result[name]}, {'PUB-0001', 'PUB-0002'})
        self.assertEqual(result['Publications'][0]['License'], 'CC BY 4.0')

    def test_shared_pipeline_export_and_empty_results(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            root = Path(directory)
            templates = root / 'data/templates'
            templates.mkdir(parents=True)
            for name in ['Figshare-Enrichment-Template.xlsx', 'Figshare-Enrichment-Template.manifest.json']:
                shutil.copyfile(ROOT / 'data/templates' / name, templates / name)
            source = root / 'publications.json'
            source.write_text(json.dumps([PUB, {**PUB, 'Publication Index': 'PUB-0002', 'DOI': '10.1000/missing'},
                {**PUB, 'Publication Index': 'PUB-0003', 'DOI': None}]))
            cache = root / 'cache'
            for doi, rows in [(PUB['DOI'], [{'id': 1}]), ('10.1000/missing', [])]:
                cached(cache, SEARCH, {'resource_doi': doi, 'page': 1, 'page_size': PAGE_SIZE}, rows)
            cached(cache, API + '/articles/1', None, metadata())
            args = argparse.Namespace(root=root, output_dir=root / 'run', stage='figshare',
                publication_index=source, registry=None, template=None, cache_root=[cache], offline=True)
            receipt = run_stage(args)
            self.assertEqual(receipt['publications_with_hits'], 1)
            self.assertEqual(receipt['publications_without_hits'], 1)
            self.assertEqual(receipt['publications_without_doi'], 1)
            book = openpyxl.load_workbook(args.output_dir / 'Figshare-Enrichment.xlsx')
            self.assertEqual(book.sheetnames, ['Publications', 'Items', 'Files'])
            self.assertEqual(book['Publications'].max_row, 2)
            headers = [c.value for c in book['Items'][1]]
            cell = book['Items'].cell(2, headers.index('Description') + 1)
            self.assertEqual(cell.value, '=native description')
            self.assertEqual(cell.data_type, 's')
            self.assertEqual(book['Files'].cell(2, 7).value, 0)
            book.close()
            with self.assertRaises(FileExistsError):
                run_collection(source, args.output_dir, template=templates / 'Figshare-Enrichment-Template.xlsx', resume=True)
            source.write_text(json.dumps([{**PUB, 'DOI': '10.1000/missing'}]))
            empty = run_collection(source, root / 'empty', template=templates / 'Figshare-Enrichment-Template.xlsx',
                caches=[cache], offline=True, index_registry=root / 'indices.json')
            self.assertEqual(empty['rows'], {'Publications': [], 'Items': [], 'Files': []})

