"""Check shared record identity, run parents, and publication-aware MeSH links."""
import copy
import tempfile
import unittest
from pathlib import Path

from deathmap_ai.pubmed_layout import indexed_tables


class IndexedPubMedTests(unittest.TestCase):
    def fixture(self):
        return {'rows': {
            'Publication': [['1', 'doi1', '', 'First', '2020'], ['2', 'doi2', '', 'Second', '2021-02']],
            'Repository Records': [['1', 'GEO', 'GSE1', 'Series', '', 'Series title', '']],
            'SRA Accessions': [
                ['1', 'SRX1', 'SRP1', 'SRS1', 'SAMN1', 'PRJNA1', 'SRR1'],
                ['1', 'SRX1', 'SRP1', 'SRS1', 'SAMN1', 'PRJNA1', 'SRR2'],
                ['2', 'SRX1', 'SRP1', 'SRS1', 'SAMN1', 'PRJNA1', 'SRR1']],
            'MeSH': [['D1', 'Cancer', '', '', 999, 'wrong']],
            'MeSH Links': [['1', 'D1', '', 'Y', ''], ['2', 'D1', '', 'N', '']]}}

    def test_shared_indices_and_distinct_publication_rows(self):
        data = self.fixture()
        before = copy.deepcopy(data)
        registry = [{'PMID': '1', 'Publication index': 'PUB-0001'},
                    {'PMID': '2', 'Publication index': 'PUB-0002'}]
        with tempfile.TemporaryDirectory() as folder:
            indices = Path(folder) / 'indices.json'
            result = indexed_tables(data, registry, indices)
            self.assertEqual(result, indexed_tables(data, registry, indices))
            expanded = copy.deepcopy(data)
            expanded['rows']['Repository Records'].append(['2', 'GEO', 'GSE0', 'Series', '', '', ''])
            later = indexed_tables(expanded, registry, indices)
            self.assertEqual(result['Repository Records'][0]['PubMed Index'],
                             later['Repository Records'][0]['PubMed Index'])
        self.assertEqual(data, before)
        sra = result['SRA Accessions']
        self.assertEqual(sra[0]['PubMed SRA Index'], sra[2]['PubMed SRA Index'])
        self.assertNotEqual(sra[0]['PubMed SRA Index'], sra[1]['PubMed SRA Index'])
        parents = {(r['Publication Index'], r['PubMed Index']) for r in result['Repository Records']}
        self.assertTrue(all((r['Publication Index'], r['PubMed Index']) in parents for r in sra))
        self.assertEqual(result['MeSH'][0]['Publication Count'], 2)
        self.assertEqual(result['MeSH'][0]['Associated Publication Index'], 'PUB-0001; PUB-0002')
        self.assertEqual(result['Repository Records'][0]['PubMed Accession'], 'GSE1')

    def test_unmapped_publications_fail(self):
        with self.assertRaises(ValueError):
            indexed_tables(self.fixture(), [{'PMID': '1', 'Publication index': 'PUB-0001'}])

    def test_native_sra_description_and_absent_run_survive(self):
        data = self.fixture()
        data['rows']['SRA Accessions'][0][-1] = ''
        data['sra_repository_records'] = [{'PMID': '1', 'Accession': 'SRX1',
            'Title': 'Native experiment title', 'Reported Data Type': 'RNA-Seq'}]
        tables = indexed_tables(data, [{'PMID': '1', 'Publication index': 'PUB-0001'},
                                       {'PMID': '2', 'Publication index': 'PUB-0002'}])
        parent = next(r for r in tables['Repository Records'] if r['Resource'] == 'SRA'
                      and r['Publication Index'] == 'PUB-0001')
        self.assertEqual(parent['Title'], 'Native experiment title')
        self.assertEqual(parent['Reported Data Type'], 'RNA-Seq')
        self.assertEqual(tables['SRA Accessions'][0]['SRA Run Accession'], '')
