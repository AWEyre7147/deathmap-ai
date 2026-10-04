"""Small inspectable fixtures for publication headers and direct screen joins."""
import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
from deathmap_ai.orcs_publications import excerpt, association_index, parse_publication, build


HEADER = """<h1>CRISPR Publication Summary</h1><div id='resultsHeaderBlock'>
<h1>A &amp; B study</h1><div class='subhead'>Smith A, Doe B</div>
<div class='bgGrey'>Reported abstract.</div>
<div class='linkouts'><strong>Cell</strong> | 2020-01-02 | PUBMED:
<a href='https://pubmed.ncbi.nlm.nih.gov/123'>123</a></div>
<div class='linkouts'><strong>Supplementary Files:</strong>
<a href='/uploads/table.csv'>table.csv</a></div></div>
<input type='hidden' id='datasetID' value='2' /><div>Excluded results</div>"""


class PublicationMetadataTests(unittest.TestCase):
    def test_header_fields_assets_and_native_identity(self):
        html = excerpt(HEADER, '2')
        self.assertNotIn('Excluded results', html)
        row = parse_publication(html, '2', {'SOURCE_TYPE':'pubmed','SOURCE_ID':'123','SCREEN_IDS':['12','1']})
        self.assertEqual(row['TITLE'], 'A & B study')
        self.assertEqual(row['AUTHORS'], 'Smith A, Doe B')
        self.assertEqual(row['ABSTRACT'], 'Reported abstract.')
        self.assertEqual(row['JOURNAL'], 'Cell')
        self.assertEqual(row['PUBLICATION_DATE'], '2020-01-02')
        self.assertEqual(row['PMID'], '123')
        self.assertEqual(row['SUPPLEMENTARY_FILES'][0]['url'], 'https://orcs.thebiogrid.org/uploads/table.csv')
        self.assertEqual(row['SCREEN_IDS'], ['1','12'])
        self.assertEqual(row['REVIEW_ISSUES'], [])

    def test_prepub_conflict_keeps_page_assertion_without_false_pmid(self):
        row = parse_publication(excerpt(HEADER, '2'), '2',
              {'SOURCE_TYPE':'prepub','SOURCE_ID':'10.1101/example','SCREEN_IDS':['1']})
        self.assertEqual(row['SOURCE_ID'], '10.1101/example')
        self.assertEqual(row['PAGE_SOURCE_ID'], '123')
        self.assertIsNone(row['PMID'])
        self.assertEqual(row['DOI'], '10.1101/example')
        self.assertTrue(row['REVIEW_ISSUES'])

    def test_missing_journal_and_abstract_remain_null(self):
        body = HEADER.replace('<strong>Cell</strong>', '').replace("<div class='bgGrey'>Reported abstract.</div>", '')
        row = parse_publication(excerpt(body, '2'), '2', {'SOURCE_TYPE':'pubmed','SOURCE_ID':'123','SCREEN_IDS':['1']})
        self.assertIsNone(row['JOURNAL'])
        self.assertIsNone(row['ABSTRACT'])

    def test_wrong_page_identity_fails(self):
        with self.assertRaises(ValueError):
            excerpt(HEADER, '3')

    def test_complete_association_coverage_and_conflicts(self):
        screens=[{'SCREEN_ID':'1','SOURCE_TYPE':'pubmed','SOURCE_ID':'123'}]
        browse={'recordsFiltered':'1','data':[['checkbox','1',"<a href='/Dataset/2'>Smith</a>"]]}
        groups, links=association_index(browse,screens)
        self.assertEqual(groups['2']['SCREEN_IDS'], ['1'])
        self.assertEqual(links[0]['PUBLICATION_ID'], '2')
        browse['data'].append(browse['data'][0])
        with self.assertRaises(ValueError):
            association_index(browse,screens)
        browse['data']=[]
        with self.assertRaises(ValueError):
            association_index(browse,screens)

    def test_successful_capture_resumes_without_requests_or_screen_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            folder=root/'data/orcs'
            source=folder/'publication-source/20261004-v01'
            source.mkdir(parents=True)
            cache=folder/'screen-index.json'
            cache.write_text(json.dumps([{'SCREEN_ID':'1','SOURCE_TYPE':'pubmed','SOURCE_ID':'123'}]),encoding='utf-8')
            original=cache.read_bytes()
            (source/'browse-metadata.json').write_text(json.dumps({'recordsFiltered':'1','data':[['x','1',"<a href='/Dataset/2'>Smith</a>"]]}),encoding='utf-8')
            (source/'homepage.html').write_text('searches <strong>1</strong> publications',encoding='utf-8')
            with patch('deathmap_ai.orcs_publications.fetch',return_value=(HEADER.encode(),200)) as request, patch('deathmap_ai.orcs_publications.time.sleep'):
                manifest=build(root)
                self.assertEqual(request.call_count,1)
                self.assertEqual(manifest['status'],'complete')
            with patch('deathmap_ai.orcs_publications.fetch',side_effect=AssertionError('unexpected retrieval')):
                self.assertEqual(build(root)['publication_count'],1)
            self.assertEqual(cache.read_bytes(),original)
            self.assertEqual(len(json.loads((folder/'publication-screen-links.json').read_text())),1)


if __name__ == '__main__':
    unittest.main()
