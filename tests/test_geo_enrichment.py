"""Small metadata fixtures exercise identity, failure and cyclic hierarchy handling."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from deathmap_ai.geo_enrichment import (
    _annotations, _datalinks, _link_targets, _series, _summary_series, identify_geo,
)


class GeoEnrichmentTests(unittest.TestCase):
    def test_link_source_and_successful_empty(self):
        self.assertEqual(_link_targets({'linksets': [{'ids': ['1']}]}, '1', 'pubmed_gds'), [])
        with self.assertRaises(ValueError):
            _link_targets({'linksets': [{'ids': ['2']}]}, '1', 'pubmed_gds')

    def test_summary_filters_samples_and_requires_coverage(self):
        body = b'<eSummaryResult><DocSum><Id>1</Id><Item Name="Accession">GSE2</Item></DocSum><DocSum><Id>3</Id><Item Name="Accession">GSM4</Item></DocSum></eSummaryResult>'
        self.assertEqual(_summary_series(body, ['1', '3']), {'1': 'GSE2'})
        with self.assertRaises(ValueError):
            _summary_series(body, ['1'])

    def test_hierarchy_requires_explicit_relation_and_native_identity(self):
        body = b'!Series_geo_accession = GSE1\r\r\n!Series_summary = Mentions GSE99\n!Series_relation = SuperSeries of: GSE2\n'
        record = _series(body, 'GSE1')
        self.assertEqual([r['to_gse'] for r in record['hierarchy']], ['GSE2'])
        with self.assertRaises(ValueError):
            _series(body, 'GSE3')

    def test_annotations_exact_identifier_and_source(self):
        native = [{'source': 'MED', 'extId': '1', 'annotations': [
            {'type': 'Accession Numbers', 'exact': 'GSE2'},
            {'type': 'Accession Numbers', 'exact': 'GSE2 is mentioned'}]}]
        self.assertEqual([r['gse'] for r in _annotations(native, '1')], ['GSE2'])
        with self.assertRaises(ValueError):
            _annotations(native, '2')

    def test_datalinks_reject_incomplete_results(self):
        self.assertEqual(_datalinks({'request': {'id': '1', 'source': 'MED'},
                                    'hitCount': 0}, '1'), [])
        with self.assertRaises(ValueError):
            _datalinks({'request': {'id': '1', 'source': 'MED'}, 'hitCount': 1}, '1')

    def test_complete_routes_cycle_dedup_and_missing_citation(self):
        """The production query inputs contain no benchmark accession seeds."""
        calls = []

        def response(transport, url):
            calls.append(url)
            query = parse_qs(urlparse(url).query)
            path = urlparse(url).path
            if path.endswith('elink.fcgi'):
                name = query['linkname'][0]
                ids = ['101'] if name == 'pubmed_gds' else []
                body = json.dumps({'linksets': [{'ids': ['1'], 'linksetdbs':
                                                 [{'linkname': name, 'links': ids}]}]}).encode()
            elif path.endswith('efetch.fcgi'):
                body = b'<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>1</PMID><Article/></MedlineCitation></PubmedArticle></PubmedArticleSet>'
            elif path.endswith('esearch.fcgi'):
                body = b'{"esearchresult":{"count":"1","idlist":["101"]}}'
            elif path.endswith('esummary.fcgi'):
                body = b'<eSummaryResult><DocSum><Id>101</Id><Item Name="Accession">GSE1</Item></DocSum></eSummaryResult>'
            elif path.endswith('annotationsByArticleIds'):
                body = b'[]'
            elif path.endswith('datalinks'):
                body = b'{"request":{"id":"1","source":"MED"},"hitCount":0}'
            elif query.get('acc') == ['GSE1']:
                body = b'!Series_geo_accession = GSE1\n!Series_pubmed_id = 1\n!Series_relation = SuperSeries of: GSE2\n'
            else:
                body = b'!Series_geo_accession = GSE2\n!Series_relation = SubSeries of: GSE1\n'
            return body, 'fixture/native'

        with tempfile.TemporaryDirectory() as temporary, patch('deathmap_ai.geo_enrichment._Requests.get', response):
            output = Path(temporary) / 'run'
            result = identify_geo({'PMID': '1', 'TITLE': 'Example title'}, output)
            self.assertEqual(result['total_gse_count'], 2)
            self.assertEqual(result['hierarchy_added'], ['GSE2'])
            self.assertEqual(result['candidates'][1]['citation_comparison'], 'not_reported')
            self.assertEqual(sum('acc=' in url for url in calls), 2)
            self.assertTrue(all('sra' not in url for url in calls))
            data_query = parse_qs(urlparse(next(url for url in calls if '/datalinks?' in url)).query)
            self.assertEqual(data_query['category'], ['GEO'])
            self.assertEqual(data_query['sectionLimit'], ['1000'])
            self.assertNotIn('pageSize', data_query)
            self.assertEqual(json.loads((output / 'manifest.json').read_text())['status'], 'complete')
            with self.assertRaises(FileExistsError):
                identify_geo({'PMID': '1', 'TITLE': 'Example title'}, output)

    def test_failure_preserves_partial_state(self):
        with tempfile.TemporaryDirectory() as temporary, patch(
                'deathmap_ai.geo_enrichment._Requests.get', side_effect=ValueError('fixture failure')):
            output = Path(temporary) / 'run'
            with self.assertRaises(ValueError):
                identify_geo({'PMID': '1', 'TITLE': 'Example title'}, output)
            self.assertTrue((output / 'partial-evidence.json').exists())
            self.assertEqual(json.loads((output / 'manifest.json').read_text())['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
