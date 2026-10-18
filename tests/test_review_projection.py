"""Inspectable offline fixtures for owner-selected review transformations."""
import unittest
from deathmap_ai.review_projection import hierarchy_rows, pivot_attributes, publication_date, unique_entities


class ReviewProjectionTests(unittest.TestCase):
    def test_inverse_edges_collapse_without_losing_publication_context(self):
        rows = [{'GSE': 'GSE1', 'Related GSE': 'GSE2', 'Relationship': 'SuperSeries of', 'PMID': '1'},
                {'GSE': 'GSE2', 'Related GSE': 'GSE1', 'Relationship': 'SubSeries of', 'PMID': '2'}]
        result = hierarchy_rows(rows, 'GSE', 'Related GSE', 'GEO')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['GSE'], 'GSE1')
        self.assertEqual(result[0]['PMID'], '1\n2')
        self.assertEqual(rows[1]['GSE'], 'GSE2')

    def test_ena_parent_reference_inverts_to_parent_first(self):
        row = {'Study accession': 'CHILD', 'Relationship': 'Parent project', 'Related study accession': 'PARENT'}
        result = hierarchy_rows([row], 'Study accession', 'Related study accession', 'ENA')[0]
        self.assertEqual(result['Study accession'], 'PARENT')
        self.assertEqual(result['Relationship'], 'Child project')

    def test_pivot_is_study_scoped_and_preserves_repeated_values(self):
        rows = [{'Study accession': s, 'Native protocol ID': 'P1', 'Field': f, 'Original value': v, 'Value state': 'Reported'}
                for s, f, v in [('S1', 'Name', 'one'), ('S1', 'Name', 'two'), ('S1', 'Contact', 'omit'), ('S2', 'Name', 'other')]]
        result = pivot_attributes(rows, 'Native protocol ID', ('Contact',))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['Name'], 'one\ntwo')
        self.assertNotIn('Contact', result[0])
        self.assertNotIn('Value state', result[0])

    def test_one_entity_keeps_all_native_values_and_zero(self):
        result = unique_entities([{'ID': 'A', 'Count': 0, 'Title': 'one'}, {'ID': 'A', 'Count': None, 'Title': 'two'}], ['ID'])
        self.assertEqual(result, [{'ID': 'A', 'Count': 0, 'Title': 'one\ntwo'}])
        with self.assertRaises(ValueError):
            unique_entities([{'ID': ''}], ['ID'])

    def test_dates_remain_literal_and_do_not_invent_components(self):
        for native, expected in [('01;03;2014', '2014-01-03'), ('06;2016', '2016-06'),
                                 ('2020', '2020'), ('2020 Spring', '2020 Spring'), ('2021-02-03', '2021-02-03')]:
            self.assertEqual(publication_date(native), expected)


if __name__ == '__main__':
    unittest.main()
