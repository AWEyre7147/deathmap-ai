"""Small metadata fixtures check collection boundaries and safe resumption."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import shutil
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch

from deathmap_ai.geo_collection import _Collection, enrich_collection
from deathmap_ai.geo_cache import _SavedNativeCache


class GeoCollectionTests(unittest.TestCase):
    def test_complete_command_with_offline_routes_and_export_resume(self):
        """Exercise the default pipeline path without contacting live repositories."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            index = root / 'data/orcs/publication-index.json'
            index.parent.mkdir(parents=True)
            index.write_text(json.dumps([{'PMID': '1', 'PUBLICATION_ID': '14', 'TITLE': 'Example'}]))
            templates = root / 'data/templates'
            templates.mkdir()
            actual = Path(__file__).resolve().parents[1] / 'data/templates'
            for name in ('GEO-Enrichment.xlsx', 'GEO-Enrichment.manifest.json'):
                shutil.copyfile(actual / name, templates / name)

            def response(collection, transport, url):
                parsed = urlsplit(url)
                query = parse_qs(parsed.query)
                if parsed.path.endswith('elink.fcgi'):
                    name = query['linkname'][0]
                    links = ['101'] if name == 'pubmed_gds' else []
                    body = json.dumps({'linksets': [{'ids': ['1'], 'linksetdbs': [{'linkname': name, 'links': links}]}]}).encode()
                elif parsed.path.endswith('efetch.fcgi'):
                    body = b'<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>1</PMID><Article/></MedlineCitation></PubmedArticle></PubmedArticleSet>'
                elif parsed.path.endswith('esearch.fcgi'):
                    body = b'{"esearchresult":{"count":"0","idlist":[]}}'
                elif parsed.path.endswith('esummary.fcgi'):
                    body = b'<eSummaryResult><DocSum><Id>101</Id><Item Name="Accession">GSE1</Item></DocSum></eSummaryResult>'
                elif parsed.path.endswith('annotationsByArticleIds'):
                    body = b'[]'
                elif parsed.path.endswith('datalinks'):
                    self.assertEqual(query['category'], ['GEO'])
                    body = b'{"request":{"id":"1","source":"MED"},"hitCount":0}'
                elif query.get('targ') == ['gsm']:
                    body = b'^SAMPLE = GSM1\n!Sample_geo_accession = GSM1\n!Sample_title = =Example\n'
                else:
                    accession = query['acc'][0]
                    other = 'GSE2' if accession == 'GSE1' else 'GSE1'
                    body = (f'^SERIES = {accession}\n!Series_geo_accession = {accession}\n'
                            f'!Series_sample_id = GSM1\n!Series_relation = SubSeries of: {other}\n').encode()
                filename = f'fixture-{len(transport.receipts):03d}.response'
                (transport.folder / filename).write_bytes(body)
                transport.receipts.append({'url': url, 'file': 'raw/' + filename,
                                           'sha256': hashlib.sha256(body).hexdigest()})
                (transport.folder.parent / 'requests.json').write_text(json.dumps(transport.receipts))
                return body, 'raw/' + filename

            with patch.object(_Collection, '_get', response):
                receipt = enrich_collection(index, root / 'run', repository_root=root)
            self.assertEqual(receipt['sheet_rows']['Series Records'], 2)
            self.assertEqual(receipt['sheet_rows']['Sample Metadata'], 2)
            resumed = enrich_collection(index, root / 'run', repository_root=root, phase='export')
            self.assertEqual(receipt, resumed)

    def test_soft_identity_and_experimental_tables(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            index = root / 'index.json'
            index.write_text('[]')
            collection = _Collection(index, root / 'run', root)
            body = b'^SAMPLE = GSM1\n!Sample_geo_accession = GSM1\n!Sample_characteristics_ch1 = A\n!Sample_characteristics_ch1 = B\n'
            self.assertEqual(collection._soft_records(body, 'Sample')['GSM1']['Sample_characteristics_ch1'], ['A', 'B'])
            with self.assertRaises(ValueError):
                collection._soft_records(body + b'!sample_table_begin\n', 'Sample')
            with self.assertRaises(ValueError):
                collection._soft_records(body.replace(b'^SAMPLE = GSM1', b'^SAMPLE = GSM2'), 'Sample')

    def test_optional_cache_and_batch_selection_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'run').mkdir()
            cache = _SavedNativeCache(root / 'run')
            cache._inventory(root)
            self.assertIsNone(cache._selected_response('https://example.invalid'))
            folder = root / 'data/orcs/pubmed-enrichment-source/fixture'
            folder.mkdir(parents=True)
            url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=gds&linkname=pubmed_gds&id=1&id=2'
            body = json.dumps({'linksets': [{'ids': ['1']}, {'ids': ['2']}]}).encode()
            (folder / 'batch.json').write_bytes(body)
            receipt = {'url': url, 'file': 'batch.json', 'sha256': hashlib.sha256(body).hexdigest(), 'retrieved_utc': '2026-10-11'}
            (folder / 'requests.json').write_text(json.dumps([receipt]))
            cache._inventory(root)
            selected, parents = cache._selected_response(url.replace('&id=2', ''))
            self.assertEqual(json.loads(selected)['linksets'], [{'ids': ['1']}])
            self.assertEqual(parents[0]['locator'], 'linksets[0]')
            self.assertEqual((root / 'run' / parents[0]['file']).read_bytes(), body)
            (folder / 'batch.json').write_bytes(b'changed')
            with self.assertRaises(ValueError):
                cache._inventory(root)

    def test_sample_dedup_projection_and_changed_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            index = root / 'index.json'
            index.write_text(json.dumps([{'PMID': '1', 'PUBLICATION_ID': '14', 'TITLE': 'Example'}]))
            collection = _Collection(index, root / 'run', root)
            publication = {'PMID': '1', 'PUBLICATION_ID': '14', 'TITLE': 'Example',
                           '_input_provenance': {'sha256': hashlib.sha256(index.read_bytes()).hexdigest()}}
            collection._save('selected-publications.json', [publication])
            collection._save('run-manifest.json', {'status': 'metadata_retrieving'})
            collection._save('issues.json', [])
            series = {gse: {'fields': {'Series_geo_accession': [gse], 'Series_sample_id': ['GSM1']},
                            'pmids': ['1'], 'source_file': 'series.response'} for gse in ('GSE1', 'GSE2')}
            collection._save('series-metadata.json', series)
            collection._save('discovery-results.json', {'1': {'publication': publication,
                'total_gse_count': 2, 'candidates': [{'gse': 'GSE1'}, {'gse': 'GSE2'}],
                'evidence': [], 'routes': {}, '_run_directory': 'publications/1'}})
            calls = []

            def sample_response(transport, url):
                calls.append(url)
                body = b'^SAMPLE = GSM1\n!Sample_geo_accession = GSM1\n!Sample_title = Example\n'
                (transport.folder / 'fixture.response').write_bytes(body)
                transport.receipts.append({'url': url, 'file': 'raw/fixture.response',
                                           'sha256': hashlib.sha256(body).hexdigest()})
                collection._save('samples/requests.json', transport.receipts)
                return body, 'raw/fixture.response'

            with patch.object(collection, '_cache_inventory'), patch.object(collection, '_get', sample_response):
                collection._samples()
                collection._samples()
            self.assertEqual(len(calls), 1)
            self.assertEqual(collection._load(collection.base / 'sample-retrieval-status.json')['missing_gsms'], [])
            receipt = enrich_collection(index, collection.base, repository_root=root, phase='project')
            self.assertEqual(receipt['unique_gsms'], 1)
            tables = collection._load(collection.base / 'workbook-data.json')
            self.assertEqual(len(tables['Sample Metadata']), 2)
            database = collection._load(collection.base / 'geo-enrichment.json')
            self.assertEqual(database['series']['GSE1']['publication_keys'], ['1'])
            index.write_text('[]')
            with self.assertRaises(ValueError):
                _Collection(index, collection.base, root)

    def test_curated_geo_cache_without_working_runs(self):
        """Archived working directories must not force retrieval of preserved responses."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            index = root / 'index.json'
            index.write_text('[]')
            folder = root / 'data/orcs/geo-enrichment-source/fixture/publications/1'
            folder.mkdir(parents=True)
            url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=gds&linkname=pubmed_gds&id=1'
            body = b'{"linksets":[{"ids":["1"]}]}'
            sample_url = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE1&targ=gsm&view=brief&form=text'
            sample = b'^SAMPLE = GSM1\n!Sample_geo_accession = GSM1\n'
            receipts = []
            for name, address, content in [('link.response', url, body), ('sample.response', sample_url, sample)]:
                (folder / name).write_bytes(content)
                receipts.append({'url': address, 'file': name,
                                 'sha256': hashlib.sha256(content).hexdigest(),
                                 'retrieved_utc': '2026-10-11'})
            (folder / 'requests.json').write_text(json.dumps(receipts))
            collection = _Collection(index, root / 'run', root)
            collection._cache_inventory()
            selected, parents = collection.native._selected_response(url)
            self.assertEqual(json.loads(selected), json.loads(body))
            self.assertEqual((collection.base / parents[0]['file']).read_bytes(), body)
            transport = type('Transport', (), {'folder': collection.base / 'raw', 'receipts': []})()
            transport.folder.mkdir()
            collection.original_get = lambda *args: self.fail('Cache reuse must not contact the network')
            returned, member = collection._get(transport, sample_url)
            self.assertEqual(returned, sample)
            self.assertEqual((collection.base / member).read_bytes(), sample)
            self.assertEqual(transport.receipts[0]['retrieved_utc'], '2026-10-11')
            (folder / 'sample.response').write_bytes(b'changed')
            with self.assertRaises(ValueError):
                collection._get(transport, sample_url)


if __name__ == '__main__':
    unittest.main()
