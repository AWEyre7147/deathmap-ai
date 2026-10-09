"""Inspectable exact-match fixtures; no live API dependency."""
import json,tempfile,unittest
from deathmap_ai.publication_identifiers import Resolver,normalize


class IdentifierTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(normalize('doi','https://doi.org/10.1234/ABC'),'10.1234/abc')
        with self.assertRaises(ValueError):normalize('pmid','abc')

    def test_mapping_and_conflict(self):
        with tempfile.TemporaryDirectory() as cache:
            resolver=Resolver(cache)
            def request(url):
                body=json.dumps({'records':[{'pmid':'123','doi':'10.1234/x','pmcid':'PMC456'}]}) if 'idconv' in url else '<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>123</PMID></MedlineCitation><PubmedData><ArticleIdList><ArticleId IdType="doi">10.1234/x</ArticleId></ArticleIdList></PubmedData></PubmedArticle></PubmedArticleSet>'
                return {'url':url,'body':body,'retrieved_at':'fixture','response_sha256':'fixture'}
            resolver.request=request
            results=resolver.resolve([{'pmid':'123'},{'pmid':'123','doi':'10.1234/wrong'}])
            self.assertEqual(results[0]['identifiers']['pmcid'],'PMC456')
            self.assertEqual(results[1]['status'],'conflicting')
            self.assertEqual(results[1]['identifiers']['doi'],'10.1234/wrong')
            self.assertIsNone(results[1]['identifiers']['pmcid'])

    def test_missing_mapping_and_shared_requests(self):
        with tempfile.TemporaryDirectory() as cache:
            resolver=Resolver(cache);calls=[]
            def request(url):
                calls.append(url)
                return {'url':url,'body':'{"records":[]}' if 'idconv' in url else '<PubmedArticleSet/>','retrieved_at':'fixture','response_sha256':'fixture'}
            resolver.request=request
            result=resolver.resolve([{'pmid':'123'},{'pmid':'123'}])
            self.assertEqual(len(calls),2)
            self.assertEqual(result[0]['status'],'unresolved')
            self.assertEqual(result[0]['identifiers']['pmid'],'123')
            self.assertIsNone(result[0]['identifiers']['doi'])

    def test_cached_response_avoids_network(self):
        from pathlib import Path
        import hashlib
        with tempfile.TemporaryDirectory() as cache:
            url='https://example.org/metadata';receipt={'url':url,'body':'{}'}
            (Path(cache)/(hashlib.sha256(url.encode()).hexdigest()+'.json')).write_text(json.dumps(receipt))
            self.assertEqual(Resolver(cache).request(url),receipt)
