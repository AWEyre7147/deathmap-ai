"""Offline evidence, coverage and no-download checks for all BioStudies collections."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from deathmap_ai.biostudies_collection import (
    API, ANNOTATIONS, Transport, attributes, association, digest, discover,
    project, routes, run_collection, save, select_publications, study_record,
)

ROOT=Path(__file__).resolve().parents[1]
PUB={'Publication Index':'PUB-0131','PMID':'123','PMCID':'PMC123','DOI':'10.1/example','Title':'A complete title.'}
NATIVE={'accno':'S-EPMC123','attributes':[{'name':'AttachTo','value':'EuropePMC'}],
        'section':{'type':'Study','attributes':[{'name':'Title','value':'A complete title.'}, {'name':'Description','value':'=literal metadata'}],
          'files':[{'path':'results.xlsx','size':10,'type':'file'}],
          'links':[[{'url':'123','attributes':[{'name':'Type','value':'PMID'}]}]]}}


class Fake:
    def __init__(self, accession='S-EPMC123'):
        self.calls=[];self.accession=accession
    def get(self,url):
        self.calls.append(url)
        receipt={'url':url,'sha256':'fixture','retrieved_utc':'2020-01-01T00:00:00Z'}
        if url.startswith(ANNOTATIONS):return [],receipt
        if '/search?' in url:return {'hits':[{'accession':self.accession,'type':'study'}],'totalHits':1,'nextCursor':None},receipt
        if url.endswith('/info'):return {'files':1,'isPublic':True,'httpLink':'https://ftp.ebi.ac.uk/example'},receipt
        return {**NATIVE,'accno':self.accession},receipt


class BioStudiesTests(unittest.TestCase):
    def test_routes_search_all_collections_and_preserve_full_identifiers(self):
        r=dict(routes(PUB));self.assertEqual(len(r),5)
        self.assertTrue(all('/ArrayExpress/' not in u for u in r.values()))
        self.assertEqual(parse_qs(urlsplit(r['doi']).query)['query'],['"10.1/example"'])
        self.assertEqual(parse_qs(urlsplit(r['complete_title']).query)['query'],['"A complete title."'])
        self.assertEqual(parse_qs(urlsplit(r['pmcid']).query)['query'],['"PMC123"'])

    def test_sourcedata_accessions_with_underscores_are_preserved(self):
        accession='S-SCDT-10_15252-EMMM_202318014'
        result=discover(PUB,Fake(accession))
        self.assertEqual(result['issues'],[])
        self.assertEqual({o['accession'] for o in result['observations']},{accession})

    def test_native_total_may_count_identical_repeated_file_paths(self):
        import copy
        class Repeated(Fake):
            def get(self,url):
                value,receipt=super().get(url)
                value=copy.deepcopy(value)
                if url.endswith('/info'):value['files']=2
                elif '/studies/' in url:
                    value['section']['subsections']=[{'type':'Other','files':[copy.deepcopy(value['section']['files'][0])]}]
                return value,receipt
        study=study_record('S-EPMC123',Repeated())
        self.assertEqual(study['issues'],[])
        self.assertEqual(study['file_occurrences'],2)
        self.assertEqual(len(study['files']),1)

    def test_both_collection_types_are_retained_without_file_downloads(self):
        for accession in ('S-EPMC123','E-MTAB-1'):
            fake=Fake(accession);study=study_record(accession,fake)
            self.assertEqual(study['accession'],accession)
            self.assertEqual(study['files'][0]['path'],'results.xlsx')
            self.assertEqual(len(fake.calls),2)
            self.assertTrue(all(u.startswith(API) for u in fake.calls))
            self.assertEqual(association(PUB,study)['matched_identifiers'],['PMID'])

    def test_annotation_route_preserves_old_accession_discovery(self):
        class Annotation(Fake):
            def get(self,url):
                if url.startswith(ANNOTATIONS):return [{'source':'MED','extId':'123','annotations':[
                    {'type':'Accession Numbers','exact':'E-MTAB-8125','tags':[]}]}],{'url':url}
                return {'hits':[],'totalHits':0,'nextCursor':None},{'url':url}
        result=discover(PUB,Annotation())
        self.assertEqual(result['outcome'],'complete')
        self.assertEqual(result['observations'][0]['accession'],'E-MTAB-8125')
        self.assertEqual(result['observations'][0]['evidence_kind'],'precomputed_accession_mention')

    def test_truncation_and_failed_routes_are_not_empty_success(self):
        class Broken(Fake):
            def get(self,url):
                if url.startswith(ANNOTATIONS):return [],{'url':url}
                return {'hits':[],'totalHits':2,'nextCursor':None},{'url':url}
        result=discover(PUB,Broken())
        self.assertEqual(result['outcome'],'incomplete')
        self.assertEqual(len(result['issues']),4)

    def test_supplied_and_pubmed_study_accessions_are_retained(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            root=Path(t);save(root/'input.json',[{**PUB,'BioStudies Accession':'S-EPMC123'}])
            save(root/'pm.json',{'repository_columns':['PMID','Resource','Accession'],
                               'rows':{'Repository Records':[['123','ArrayExpress','E-MTAB-8125']]}})
            p=select_publications(root/'input.json',pubmed=root/'pm.json')[0]
            self.assertEqual({o['accession'] for o in p['input_accessions']},{'S-EPMC123','E-MTAB-8125'})
            result=discover(p,Fake())
            self.assertTrue(any(o['accession']=='E-MTAB-8125' and o['route']=='supplied_accession' for o in result['observations']))

    def test_external_file_lists_and_count_mismatch_remain_incomplete(self):
        class Lists(Fake):
            def get(self,url):
                value,receipt=super().get(url)
                if url.endswith('/info'):value['files']=200
                return value,receipt
        study=study_record('S-EPMC123',Lists())
        rows=project({'publications':[{'publication':PUB,'observations':[{'accession':'S-EPMC123'}]}], 'studies':{'S-EPMC123':study}})
        self.assertIsNone(rows['Publications'][0]['File Count'])
        self.assertEqual(len(rows['Supplementary Files']),1)
        self.assertEqual(rows['Supplementary Files'][0]['BioStudies Index'],'BST-0001')

    def test_projection_preserves_accession_and_cross_publication_file_identity(self):
        study=study_record('E-MTAB-1',Fake('E-MTAB-1'))
        study['native']['attributes']=[{'name':'AttachTo','value':'ArrayExpress'}]
        database={'studies':{'E-MTAB-1':study},'publications':[
            {'publication':PUB,'observations':[{'accession':'E-MTAB-1'}]},
            {'publication':{**PUB,'Publication Index':'PUB-0999'},'observations':[{'accession':'E-MTAB-1'}]}]}
        rows=project(database)
        self.assertEqual(rows['Publications'][0]['Collection'],'ArrayExpress')
        self.assertEqual(rows['Publications'][0]['BioStudies Accession'],'E-MTAB-1')
        self.assertEqual(rows['Supplementary Files'][0]['BioStudies Index'],rows['Supplementary Files'][1]['BioStudies Index'])
        self.assertTrue(rows['Supplementary Files'][0]['File URL'].endswith('/Files/results.xlsx'))
        self.assertEqual(rows['Publications'][0]['Abstract'],'=literal metadata')

    def test_publications_export_only_retrieved_study_hits(self):
        study=study_record('S-EPMC123',Fake())
        records=[
            {'publication':PUB,'observations':[{'accession':'S-EPMC123'}]},
            {'publication':{**PUB,'Publication Index':'PUB-0002'},'observations':[]},
            {'publication':{**PUB,'Publication Index':'PUB-0003'},'observations':[{'accession':'S-EPMC999'}]},
        ]
        database={'publications':records,'studies':{'S-EPMC123':study}}
        rows=project(database)
        self.assertEqual([r['Publication Index'] for r in rows['Publications']],[PUB['Publication Index']])
        self.assertEqual(len(rows['Supplementary Files']),1)
        self.assertEqual(len(database['publications']),3)
        empty=project({'publications':records[1:],'studies':{}})
        self.assertEqual(empty,{'Publications':[],'Supplementary Files':[]})

    def test_offline_cache_preserves_source_dates_and_detects_corruption(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            root=Path(t);cache=root/'cache/native';cache.mkdir(parents=True)
            url=API+'studies/S-EPMC123';body=json.dumps(NATIVE).encode();key=digest(url.encode())
            (cache/(key+'.body')).write_bytes(body)
            save(cache/(key+'.json'),{'url':url,'sha256':digest(body),'retrieved_utc':'2020-01-01T00:00:00Z'})
            out=root/'out';out.mkdir();tr=Transport(out,[root/'cache'],offline=True)
            _,receipt=tr.get(url);self.assertEqual(receipt['retrieved_utc'],'2020-01-01T00:00:00Z')
            self.assertEqual(tr.reused,1);self.assertEqual(tr.requests,[])
            (cache/(key+'.body')).write_bytes(b'changed')
            other=root/'other';other.mkdir()
            with self.assertRaisesRegex(ValueError,'hash'):Transport(other,[root/'cache'],offline=True).get(url)

    def test_complete_collection_exports_two_owner_sheets_and_no_contents(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            root=Path(t);save(root/'input.json',[PUB])
            with patch.object(Transport,'get',Fake().get):
                result=run_collection(root/'input.json',root/'run',index_registry=root/'ids.json')
            self.assertEqual(result['status'],'complete')
            manifest=json.loads((root/'run/BioStudies-Enrichment.manifest.json').read_text())
            self.assertEqual(manifest['sheet_rows'],{'Publications':1,'Supplementary Files':1})
            self.assertEqual(result['summary']['supplemental_downloads'],0)
            with self.assertRaises(FileExistsError):run_collection(root/'input.json',root/'run',resume=True)
