"""Small offline fixtures for PMC collection, linkage and final template export."""
from pathlib import Path
import json,tempfile,unittest
from unittest.mock import patch
from deathmap_ai.pmc_supplemental_collection import (
    extract_entries, collect_one, project, load_publications, Transport,
    run_collection, sha, write_json, EFETCH, BUCKET,
)
ROOT=Path(__file__).resolve().parents[1]
PUB={'Publication Index':'PUB-0001','PMCID':'PMC123','PMID':'456','DOI':None,'Title':'Input title'}
XML=b'''<pmc-articleset><article><front><article-meta><article-id pub-id-type="pmcid">PMC123</article-id><article-id pub-id-type="pmid">456</article-id><article-id pub-id-type="pmcid-ver">PMC123.1</article-id><title-group><article-title>A study</article-title></title-group></article-meta></front><body><supplementary-material id="S1"><object-id pub-id-type="doi">10.1/supp</object-id><label>Additional Files</label><caption><title>Screen results</title><p>All comparisons</p></caption><media xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="supp.xlsx"/><permissions><license xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="https://creativecommons.org/licenses/by/4.0/">License</license></permissions></supplementary-material></body><back><ref-list><ref><supplementary-material id="other"/></ref></ref-list></back></article></pmc-articleset>'''
LIST=b'''<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><IsTruncated>false</IsTruncated><Contents><Key>PMC123.1/PMC123.1.json</Key><Size>100</Size></Contents><Contents><Key>PMC123.1/supp.xlsx</Key><Size>20</Size></Contents><Contents><Key>PMC123.1/unmatched.xlsx</Key><Size>30</Size></Contents></ListBucketResult>'''
META={'pmcid':'PMC123','pmid':456,'version':1,'title':'A study','is_pmc_openaccess':True,'is_manuscript':False,'is_retracted':False,'citation':'A citation','pdf_url':'s3://pmc-oa-opendata/PMC123.1/PMC123.1.pdf?md5=123','media_urls':[]}


def fake_fetch(self,url):
    body=XML if url.startswith(EFETCH) else LIST if '?' in url else json.dumps(META).encode()
    return body,{'url':url,'retrieved_utc':'2026-01-01T00:00:00Z','sha256':sha(body)}


class CollectionTests(unittest.TestCase):
    def test_explicit_entries_have_doi_and_no_license_as_file(self):
        r=extract_entries(XML,PUB)
        self.assertEqual(r['entry_count'],1)
        e=r['supplementary_entries'][0]
        self.assertEqual(e['Title'],'Screen results')
        self.assertEqual(e['Supplemental DOI'],'10.1/supp')
        self.assertEqual([f['href'] for f in e['files']],['supp.xlsx'])
        self.assertEqual(e['Supplemental Index'],extract_entries(XML,{**PUB,'Publication Index':'PUB-0099'})['supplementary_entries'][0]['Supplemental Index'])

    def test_file_linkage_retains_unmatched_workbooks(self):
        with patch.object(Transport,'fetch',fake_fetch):
            r=collect_one(PUB,Transport.__new__(Transport))
        rows=project([r])
        self.assertEqual(len(rows['Cloud Files']),2)
        self.assertTrue(rows['Cloud Files'][0]['Supplemental Index'])
        self.assertEqual(rows['Cloud Files'][0]['Caption'],'Screen results All comparisons')
        self.assertIsNone(rows['Cloud Files'][1]['Supplemental Index'])
        self.assertIsNone(rows['Cloud Files'][1]['Caption'])
        self.assertEqual(rows['Cloud Files'][1]['File Type'],'.xlsx')
        self.assertTrue(rows['Publications'][0]['Article PDF URL'].endswith('.pdf'))
        self.assertNotIn('md5=',rows['Publications'][0]['Article PDF URL'])

    def test_other_version_filename_does_not_assert_relationship(self):
        with patch.object(Transport,'fetch',fake_fetch):r=collect_one(PUB,Transport.__new__(Transport))
        for f in r['cloud_files']:f['version']='PMC123.2'
        rows=project([r])
        self.assertIsNone(rows['Cloud Files'][0]['Supplemental Index'])
        self.assertTrue(r['cloud_files'][0]['filename_candidates'])

    def test_identity_conflict_is_explicit(self):
        with self.assertRaises(ValueError):extract_entries(XML,{**PUB,'PMID':'999'})

    def test_registry_crosswalk_does_not_renumber_pilot(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            t=Path(t);write_json(t/'pubs.json',[PUB]);write_json(t/'registry.json',[{'Publication index':'PUB-0099','ORCS Publication ID':'7','PMID':'456'}])
            p=load_publications(t/'pubs.json',t/'registry.json')[0]
            self.assertEqual(p['Publication Index'],'PUB-0001')
            self.assertEqual(p['ORCS Publication Index'],'PUB-0099')

    def test_verified_request_cache_is_reused_without_network(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            t=Path(t);out=t/'out';out.mkdir();cache=t/'cache/native';cache.mkdir(parents=True)
            url=EFETCH+'db=pmc&id=123';key=sha(url.encode())
            (cache/(key+'.body')).write_bytes(XML)
            write_json(cache/(key+'.json'),{'url':url,'sha256':sha(XML),'retrieved_utc':'2026-01-01'})
            transport=Transport(out,[t/'cache'])
            with patch('deathmap_ai.pmc_supplemental_collection.build_opener',side_effect=AssertionError('Network forbidden')):
                body,receipt=transport.fetch(url)
            self.assertEqual(body,XML);self.assertEqual(transport.reused,1)
            self.assertEqual(receipt['retrieved_utc'],'2026-01-01')
            (cache/(key+'.body')).write_bytes(b'corrupt')
            other=t/'other';other.mkdir()
            with self.assertRaises(ValueError):Transport(other,[t/'cache']).fetch(url)

    def test_final_three_sheet_export_and_missing_pmcid(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            t=Path(t);write_json(t/'input.json',[PUB,{**PUB,'Publication Index':'PUB-0002','PMCID':None}])
            with patch.object(Transport,'fetch',fake_fetch):
                d=run_collection(t/'input.json',t/'run',ROOT/'data/templates/PMC-Supplemental-Enrichment.xlsx',workers=1)
            self.assertEqual(len(d['rows']['Publications']),2)
            self.assertEqual(d['summary']['supplementary_entries'],1)
            self.assertEqual(d['summary']['cloud_files'],2)
            self.assertEqual(d['summary']['unmatched_cloud_files'],1)
            self.assertEqual(d['publications'][1]['xml_result'],'no_pmcid')
            self.assertTrue((t/'run/PMC-Supplemental-Enrichment.xlsx').exists())
            with self.assertRaises(FileExistsError):run_collection(t/'input.json',t/'run',ROOT/'data/templates/PMC-Supplemental-Enrichment.xlsx')

if __name__=='__main__':unittest.main()
