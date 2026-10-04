"""Small offline checks for the bounded metadata-only page parser."""
import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/'scripts/orcs_page_capability.py'
spec=importlib.util.spec_from_file_location('page_capability',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class PageCapabilityTests(unittest.TestCase):
 def setUp(self):
  self.native={'SCREEN_ID':'16','SCREEN_NAME':'1-PMID123','SOURCE_TYPE':'pubmed','SOURCE_ID':'123'}
  self.html='<nav>navigation</nav><h1>CRISPR Screen Dataset</h1><h2>1-PMID123</h2><div>Title: Synthetic title</div><h4>Screen Details</h4><li>Cell Line: fixture <a href="https://www.cellosaurus.org/CVCL_TEST">CVCL_TEST</a></li><script>unwanted()</script><h3>Score Distribution</h3><table>GENE_SCORES</table>'
 def test_metadata_boundary_and_links(self):
  raw,result=m.parse(self.html,self.native)
  self.assertEqual(result['publication_title'],'Synthetic title');self.assertNotIn('GENE_SCORES',raw);self.assertNotIn('unwanted()',raw);self.assertTrue(result['identity_verified']);self.assertEqual(result['repository_accession_mentions'],[])
 def test_embedded_marker_is_not_results_boundary(self):
  html=self.html.replace('<h1>', '<script type="application/ld+json">{"description":"Score Distribution"}</script><h1>',1)
  raw,result=m.parse(html,self.native)
  self.assertEqual(result['publication_title'],'Synthetic title');self.assertNotIn('GENE_SCORES',raw)
 def test_wrong_identity_rejected(self):
  with self.assertRaises(ValueError):m.parse(self.html,{**self.native,'SCREEN_NAME':'wrong'})
 def test_missing_result_boundary_rejected(self):
  with self.assertRaises(ValueError):m.metadata_excerpt('<h1>CRISPR Screen Dataset</h1>')
if __name__=='__main__':unittest.main()
