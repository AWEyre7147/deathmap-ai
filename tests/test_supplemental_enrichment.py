"""Offline checks for identity, unfiltered listings and retrieval failures."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError
from deathmap_ai.supplemental_enrichment import parse_xml, run

XML = b'''<pmc-articleset><article><front><article-meta>
<article-id pub-id-type="pmcaid">PMC123</article-id><article-id pub-id-type="pmid">456</article-id>
<title-group><article-title>A study</article-title></title-group>
<custom-meta-group><custom-meta><meta-name>pmc-prop-has-supplement</meta-name><meta-value>yes</meta-value></custom-meta></custom-meta-group>
</article-meta></front><body><supplementary-material id="internal123"><label>Additional Files</label>
<caption><p>Methods and <italic>source data</italic>.</p></caption><media xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="file.odd" mimetype="application" mime-subtype="octet-stream"/>
</supplementary-material></body><back><ref-list><ref><supplementary-material/></ref></ref-list></back></article></pmc-articleset>'''


class SupplementalTests(unittest.TestCase):
    def test_metadata_and_no_relevance_filter(self):
        result = parse_xml(XML, {'PMCID': 'PMC123', 'PMID': '456'})
        self.assertEqual(result['entry_count'], 1)
        entry = result['supplementary_entries'][0]
        self.assertEqual(entry['label'], 'Additional Files')
        self.assertIn('source data', entry['caption'])
        self.assertEqual(entry['files'][0]['href'], 'file.odd')
        self.assertNotIn('internal123', json.dumps(result))
        self.assertEqual(result['pmc_properties']['pmc-prop-has-supplement'], 'yes')

    def test_identity_conflict(self):
        for p in [{'PMCID': 'PMC999'}, {'PMCID': 'PMC123', 'PMID': '999'}]:
            with self.assertRaises(ValueError):
                parse_xml(XML, p)

    def test_metadata_only_and_missing_flag(self):
        body = b'<article><front><article-meta><article-id pub-id-type="pmcid">123</article-id></article-meta></front></article>'
        result = parse_xml(body, {'PMCID': 'PMC123'})
        self.assertFalse(result['has_body'])
        self.assertEqual(result['pmc_properties'], {})
        self.assertEqual(result['entry_count'], 0)

    def test_cache_and_output_preservation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'PMC123.xml').write_bytes(XML)
            source = root/'input.json'
            source.write_text(json.dumps([{'PMCID': 'PMC123', 'PMID': '456'}, {'PMID': '789'}]))
            before = source.read_bytes()
            with patch('deathmap_ai.supplemental_enrichment.urlopen', side_effect=AssertionError('Network forbidden')):
                summary = run(source, root/'out', root)
            self.assertEqual(summary['statuses'], {'no_pmcid': 1, 'verified_xml': 1})
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual((root/'out/PMC123.xml').read_bytes(), XML)
            with self.assertRaises(FileExistsError):
                run(source, root/'out', root)

    def test_failure_is_not_empty_success(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root/'input.json'
            source.write_text('[{"PMCID":"PMC123"}]')
            with patch('deathmap_ai.supplemental_enrichment.urlopen', side_effect=URLError('DNS failed')), patch('deathmap_ai.supplemental_enrichment.time.sleep'):
                summary = run(source, root/'out')
            self.assertEqual(summary['statuses'], {'failed': 1})
            requests = json.loads((root/'out/requests.json').read_text())
            self.assertEqual(len(requests), 2)


if __name__ == '__main__':
    unittest.main()
