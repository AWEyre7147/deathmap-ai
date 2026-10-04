"""Small offline fixtures for bibliography joins and conservative preservation."""
import copy
import socket
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from deathmap_ai.orcs_filter_projection import existing_rows
from deathmap_ai.orcs_publication_enrichment import enrich, validate_catalogs, field_map, prepare

ROOT = Path(__file__).resolve().parents[1]


class PublicationEnrichmentTests(unittest.TestCase):
    def setUp(self):
        self.wb = existing_rows(ROOT/'data/templates/DeathMap-AI-v1-reference-output.xlsx')
        for name, value in self.wb.items(): value['rows'] = []
        self.wb['Screens']['headers'] += ['reviewer_decision','reviewer_notes']
        self.wb['Publications']['rows'] = [{'publication_id':'old-pub','pmid':'123','retrival_sources':'old source','publication_notes':'owner note'}]
        self.wb['Screens']['rows'] = [
            {'screen_id':'s1','publication_id':'old-pub','source_evidence_ids':'old-evidence','screen_notes':'native one','reviewer_decision':'retain','reviewer_notes':'owner review'},
            {'screen_id':'s2','publication_id':'old-pub','source_evidence_ids':'old-evidence','screen_notes':'native two'},
            {'screen_id':'s3','publication_id':None,'source_evidence_ids':'old-evidence','screen_notes':'native three'}]
        self.wb['Sources & Evidence']['rows'] = [{'evidence_id':'old-evidence','supports_entity_type':'screen','supports_entity_id':'s1'}]
        self.screens = [{'SCREEN_ID':str(i),'SOURCE_TYPE':typ,'SOURCE_ID':identifier,'SCREEN_NAME':'screen '+str(i)}
                        for i,typ,identifier in [(1,'pubmed','123'),(2,'pubmed','123'),(3,'prepub','10.1101/fixture')]]
        self.pubs = [self.publication('p1','pubmed','123',['1','2']),self.publication('p2','prepub','10.1101/fixture',['3'])]
        self.links = [{'SCREEN_ID':s['SCREEN_ID'],'PUBLICATION_ID':'p1' if s['SOURCE_TYPE']=='pubmed' else 'p2','SOURCE_TYPE':s['SOURCE_TYPE'],'SOURCE_ID':s['SOURCE_ID']} for s in self.screens]
        self.original = {'sheets':{n:copy.deepcopy(v['rows']) for n,v in self.wb.items()},
                         'roles':{f's{i}':{'SCREEN_ID':str(i),'role':'unresolved_category' if i==3 else 'direct_filter_hit'} for i in range(1,4)}}

    def publication(self, pid, typ, identity, screens):
        return {'PUBLICATION_ID':pid,'SOURCE_TYPE':typ,'SOURCE_ID':identity,'SCREEN_IDS':screens,
                'PAGE_SOURCE_TYPE':'pubmed','PAGE_SOURCE_ID':identity if typ=='pubmed' else '28',
                'PMID':identity if typ=='pubmed' else None,'DOI':identity if typ=='prepub' else None,
                'TITLE':'Exact reported title','AUTHORS':'A, B','JOURNAL':None,'PUBLICATION_DATE':'2025-08-26',
                'ABSTRACT':'Reported abstract','SUPPLEMENTARY_FILES':[{'label':'asset','url':'https://example.org/asset'}],
                'REVIEW_ISSUES':[] if typ=='pubmed' else ['cached/page identifier conflict'],
                'SOURCE_METADATA_FILE':pid+'.html','SOURCE_METADATA_SHA256':'abc','RETRIEVED_AT':'2026-10-04T05:00:00+00:00','FIELD_LOCATORS':{}}

    def project(self):
        return enrich(self.original,self.wb,self.screens,self.pubs,self.links,'2026-10-04T10:00:00+00:00')

    def test_bibliography_shared_publication_and_evidence_foreign_keys(self):
        p = self.project(); self.assertEqual(p['proposed_counts']['Publications'],2)
        pub = p['sheets']['Publications'][0]
        self.assertEqual(pub['publication_id'],'old-pub'); self.assertEqual(pub['title_original'],'Exact reported title')
        self.assertEqual(pub['author_list_ reported'],'A, B'); self.assertEqual(pub['publication_year'],2025)
        self.assertEqual(pub['pmid_link'],'https://pubmed.ncbi.nlm.nih.gov/123/')
        headers = [e for e in p['sheets']['Sources & Evidence'] if e.get('supports_entity_type')=='publication']
        self.assertEqual(len(headers),2)
        self.assertEqual({e['supports_entity_id'] for e in headers},{r['publication_id'] for r in p['sheets']['Publications']})

    def test_prepub_page_conflict_and_absent_journal(self):
        p = self.project(); pub = p['sheets']['Publications'][1]
        self.assertIsNone(pub.get('pmid')); self.assertIsNone(pub.get('journal_reported'))
        self.assertEqual(pub['doi'],'10.1101/fixture'); self.assertIn(pub['publication_id'],p['publication_review'])
        self.assertEqual(p['sheets']['Screens'][2]['publication_id'],pub['publication_id'])
        self.assertIn('PAGE_SOURCE_ID',pub['publication_notes']); self.assertIn('28',pub['publication_notes'])
        self.assertEqual(p['roles'],self.original['roles'])

    def test_existing_values_formulas_and_reviewer_entries(self):
        self.wb['Publications']['rows'][0]['title_original']='=1+1'
        self.wb['Publications']['rows'][0]['reviewer_notes']='owner publication review'
        self.wb['Publications']['headers'] += ['reviewer_decision','reviewer_notes']
        p = self.project(); pub = p['sheets']['Publications'][0]
        self.assertEqual(pub['title_original'],'=1+1'); self.assertEqual(pub['reviewer_notes'],'owner publication review')
        self.assertTrue(pub['publication_notes'].startswith('owner note\n'))
        self.assertTrue(pub['retrival_sources'].startswith('old source\n'))
        self.assertEqual(p['sheets']['Screens'][0]['reviewer_notes'],'owner review')
        conflict = next(x for x in p['existing_value_conflicts'] if x['field']=='title_original')
        self.assertEqual(conflict['retained'],'=1+1'); self.assertIn('source_locator',conflict)

    def test_duplicate_missing_and_ambiguous_associations(self):
        for links in [self.links+self.links[:1],self.links[:-1],[{**self.links[0],'SOURCE_ID':'wrong'}]+self.links[1:]]:
            with self.subTest(links=links),self.assertRaises(ValueError): validate_catalogs(self.screens,self.pubs,links)

    def test_missing_publication_and_duplicate_catalog_ids(self):
        with self.assertRaises(ValueError): validate_catalogs(self.screens,self.pubs[:1],self.links)
        with self.assertRaises(ValueError): validate_catalogs(self.screens+self.screens[:1],self.pubs,self.links)
        with self.assertRaises(ValueError): validate_catalogs(self.screens,self.pubs+self.pubs[:1],self.links)

    def test_unsupported_pmid_is_error(self):
        self.pubs[1]['PMID']='28'
        with self.assertRaises(ValueError): self.project()

    def test_supplementary_links_not_attributed_and_no_network(self):
        with patch.object(socket,'socket',side_effect=AssertionError('network forbidden')): p=self.project()
        for sheet in ['Screen Groups','Datasets','Screen-Dataset Links']: self.assertEqual(p['sheets'][sheet],[])
        self.assertIn('https://example.org/asset',p['sheets']['Publications'][0]['publication_notes'])
        self.assertNotIn('Reported abstract',p['sheets']['Screens'][0]['screen_notes'])

    def test_invalid_date_is_unresolved(self):
        self.pubs[0]['PUBLICATION_DATE']='2025-02-30'
        p=self.project(); self.assertIsNone(p['sheets']['Publications'][0].get('publication_year'))
        self.assertTrue(any(a['field']=='publication_year' and a['status']=='unresolved' for a in p['cell_audit']))

    def test_field_map_covers_exact_128_headers(self):
        result=field_map((ROOT/'docs/orcs/workbook-field-source-map.md').read_text(encoding='utf-8'))
        self.assertEqual(len(result),128); self.assertEqual(len({(r['sheet'],r['field']) for r in result}),128)
        self.assertEqual({r['classification'] for r in result},{'reported','explicitly derived','provenance','review-dependent','unsupported'})

    def test_preserve_owner_dataset_rows(self):
        self.wb['Datasets']['rows']=[{'dataset_id':'owner-dataset','dataset_notes':'owner entry'}]
        self.assertEqual(self.project()['sheets']['Datasets'],self.wb['Datasets']['rows'])

    def test_refuse_existing_output(self):
        with self.assertRaises(FileExistsError): prepare(ROOT,ROOT,ROOT)

    def test_excel_date_preserves_full_receipt_precision(self):
        self.original['sheets']['Sources & Evidence'][0]['retrieved_at']='2026-09-04T21:39:41.990988+00:00'
        self.wb['Sources & Evidence']['rows'][0]['retrieved_at']=datetime(2026,9,4,21,39,41,991000)
        p=self.project()
        self.assertEqual(p['sheets']['Sources & Evidence'][0]['retrieved_at'],'2026-09-04T21:39:41.990988+00:00')

if __name__ == '__main__': unittest.main()
