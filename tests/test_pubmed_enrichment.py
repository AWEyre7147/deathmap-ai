"""Small inspectable tests for direct links, date precision and subset MeSH counts."""
import json
from pathlib import Path
import tempfile
import unittest
from deathmap_ai.pubmed_projection import project_saved
from deathmap_ai.pubmed_workbook import date_text, subset_rows, validate_namespaces


def test_dates_keep_source_precision():
    assert date_text('2014-01-03') == '01;03;2014'
    assert date_text('2016-06') == '06;2016'
    assert date_text('2020') == '2020'
    assert date_text('2020 Spring') == '2020 Spring'


def test_mesh_counts_are_recomputed_for_subset():
    database = {'rows': {'Publication': [['1', '', '', 'a', '2020']], 'Repository Records': [], 'SRA Accessions': [],
                         'MeSH': [['D1', 'Cancer', 'Q1', 'genetics', 2, '1; 2']],
                         'MeSH Links': [['1', 'D1', 'Q1', 'Y', 'N'], ['2', 'D1', 'Q1', 'N', 'Y']]}}
    assert subset_rows(database, ['1'])['MeSH'] == [['D1', 'Cancer', 'Q1', 'genetics', 1, '1']]
    assert database['rows']['MeSH'][0][4] == 2


def test_missing_links_are_not_failed_retrieval_or_screen_evidence(tmp_path):
    (tmp_path / 'pubmed.xml').write_text('<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>1</PMID><Article><ArticleTitle>Example</ArticleTitle><Journal><JournalIssue><PubDate><Year>2020</Year><Month>Jun</Month></PubDate></JournalIssue></Journal></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>')
    for resource in ('gds', 'bioproject', 'sra'):
        (tmp_path / f'links-{resource}.json').write_text(json.dumps({'linksets': [{'ids': ['1']}]}))
    data = project_saved(tmp_path, ['1'])
    assert data['rows']['Publication'][0][-1] == '2020-06'
    assert data['rows']['Repository Records'] == []
    assert data['relationships'] == []
    assert len([i for i in data['issues'] if i.get('status') == 'no_direct_pubmed_link']) == 3


def test_excel_compatibility_prefixes_must_be_declared():
    validate_namespaces(b'<sheet xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:x14="urn:example" mc:Ignorable="x14"/>')
    with unittest.TestCase().assertRaises(AssertionError):
        validate_namespaces(b'<sheet xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" mc:Ignorable="x14"/>')


class PubMedChecks(unittest.TestCase):
    """Standard-library runner keeps focused verification dependency-free."""
    def test_dates(self):
        test_dates_keep_source_precision()

    def test_mesh(self):
        test_mesh_counts_are_recomputed_for_subset()

    def test_links(self):
        fixture_root = Path(__file__).resolve().parents[1] / 'logs/pubmed-milestone-20261008'
        fixture_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=fixture_root) as folder:
            test_missing_links_are_not_failed_retrieval_or_screen_evidence(Path(folder))

    def test_namespaces(self):
        test_excel_compatibility_prefixes_must_be_declared()
