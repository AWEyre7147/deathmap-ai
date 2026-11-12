"""Explicit Nature listing fixtures for the maintained library adapter only."""
import unittest
from deathmap_ai.library_nature import extract_listing


class LibraryNatureTests(unittest.TestCase):
    def test_native_listing_preserves_caption_and_supplied_link(self):
        html = '''<meta name="citation_doi" content="10.1234/example">
        <div id="MOESM1"><h3><a href="https://static-content.springer.com/esm/MediaObjects/table.xlsx">Supplementary Data 1</a></h3><p>Native table description.</p></div>'''
        result = extract_listing(html, 'https://www.nature.com/articles/example', '10.1234/example')
        self.assertEqual(result['supplements'][0]['title'], 'Supplementary Data 1')
        self.assertEqual(result['supplements'][0]['description'], 'Native table description.')
        self.assertEqual(result['supplements'][0]['links'], ['https://static-content.springer.com/esm/MediaObjects/table.xlsx'])
        self.assertNotIn('article_context', result)

    def test_untitled_listing_is_not_assigned_an_invented_title(self):
        html = '<meta name="citation_doi" content="10.1234/example"><div id="MOESM1">Native description.</div>'
        self.assertIsNone(extract_listing(html, 'https://www.nature.com/articles/example', '10.1234/example')['supplements'][0]['title'])

    def test_wrong_identity_or_challenge_produces_no_listing(self):
        for html in ['<meta name="citation_doi" content="10.1234/other"><div id="MOESM1">Data</div>', '<title>Client Challenge</title>']:
            self.assertEqual(extract_listing(html, 'https://www.nature.com/articles/example', '10.1234/example')['supplements'], [])
