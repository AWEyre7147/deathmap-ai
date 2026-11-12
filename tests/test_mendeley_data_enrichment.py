"""Offline contracts for Mendeley routes, identity, credentials and owner exports."""
import argparse
from contextlib import redirect_stdout
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import openpyxl
import deathmap_ai.mendeley_data_enrichment as m

ROOT=Path(__file__).resolve().parents[1]
ACC='abc123def4'
PUB={'Publication Index':'PUB-0001','PMID':'123','PMCID':'PMC123','DOI':'10.1016/example','Title':'A complete publication title.',
     'ORCS Publication ID':'1','references':[{'accession':ACC,'dataset_doi':'10.17632/'+ACC+'.1','route':'supplied_identifier'}]}
NATIVE={'id':ACC,'doi':{'id':'10.17632/'+ACC+'.2'},'version':2,'name':'Dataset title','description':'=literal metadata\r\nNative continuation',
        'categories':[{'label':'CRISPR'}],'available':True,'confidential':False,'size':10,
        'files':[{'id':'file-one','filename':'design.xlsx','folder_id':'nested-folder','size':10,
                  'description':'Experimental design','content_details':{'download_url':'https://data.mendeley.com/public-files/dataset/file_downloaded'}}]}


def cache(root, url=m.PUBLIC+ACC, value=None):
    native=root/'native';native.mkdir(parents=True,exist_ok=True)
    body=json.dumps(NATIVE if value is None else value).encode();key=m._sha(url.encode())
    (native/(key+'.body')).write_bytes(body)
    m._save(native/(key+'.json'),{'url':url,'sha256':m._sha(body),'retrieved_utc':'2020-01-01T00:00:00Z'})
    return native/(key+'.body')


class Fake:
    def __init__(self,value=None):self.value=copy.deepcopy(value or NATIVE);self.calls=[]
    def get(self,url):self.calls.append(url);return self.value,{'url':url,'retrieved_utc':'2020-01-01T00:00:00Z'}


class MendeleyTests(unittest.TestCase):
    def test_registry_and_biostudies_links_remap_native_identity_not_cohort_index(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            root=Path(t)
            m._save(root/'input.json',[{'PUBLICATION_ID':'1','PMID':'123','DOI':'10.1016/example','TITLE':'Paper'}])
            m._save(root/'registry.json',[{'Publication index':'PUB-0042','ORCS Publication ID':'1','PMID':'123'}])
            saved={'publications':[{'publication':{'Publication Index':'OTHER-0001','PMID':'123','ORCS Publication ID':'1'},
                'observations':[{'accession':'S-EPMC123'}]}],
                'studies':{'S-EPMC123':{'links':[{'url':'https://doi.org/10.17632/'+ACC+'.1'}],
                    'native':{'abstract':'10.17632/notlinked1.1'}}}}
            m._save(root/'bio.json',saved)
            result=m.select_publications(root/'input.json',root/'registry.json',root/'bio.json')
            self.assertEqual(result[0]['Publication Index'],'PUB-0042')
            self.assertEqual([r['accession'] for r in result[0]['references']],[ACC])
            self.assertEqual(result[0]['references'][0]['route'],'biostudies_link')
            saved['publications'][0]['publication']['PMID']='999'
            m._save(root/'bio.json',saved)
            with self.assertRaisesRegex(ValueError,'Conflicting BioStudies'):m.select_publications(root/'input.json',root/'registry.json',root/'bio.json')

    def test_explicit_references_and_unsafe_indices(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            root=Path(t)
            m._save(root/'input.json',[{**PUB,'Mendeley Data Accession':ACC,'dataset_references':[{'dataset_doi':'10.17632/'+ACC+'.1'}]}])
            result=m.select_publications(root/'input.json')
            self.assertEqual({r['accession'] for r in result[0]['references']},{ACC})
            m._save(root/'input.json',[{**PUB,'Publication Index':'../escape'}])
            with self.assertRaises(ValueError):m.select_publications(root/'input.json')

    def test_blocked_searches_retain_references_and_reference_only_is_explicit(self):
        class Blocked(Fake):
            def get(self,url):self.calls.append(url);raise m.AuthenticationRequired('HTTP 401')
        transport=Blocked();record=m.discover(PUB,transport)
        self.assertEqual(len(record['issues']),3)
        self.assertTrue(all(r['outcome']=='blocked_authentication' for r in record['routes']))
        self.assertEqual(record['observations'][0]['accession'],ACC)
        transport=Blocked();record=m.discover(PUB,transport,reference_only=True)
        self.assertEqual(transport.calls,[])
        self.assertEqual(record['routes'][0]['outcome'],'not_attempted_reference_only')

    def test_doi_and_full_title_routes_paginate_and_exclude_external_hits(self):
        class Search(Fake):
            def get(self,url):
                self.calls.append(url);query=parse_qs(urlsplit(url).query)
                if url.startswith(m.API):
                    value={'results':[] if 'marker' in query else [{'id':ACC}],'next_marker':None if 'marker' in query else 'second'}
                else:value={'records':[{'doi':['10.17632/'+ACC+'.2'],'source':{'external':False}},
                    {'id':'other12345','source':{'external':True}}]}
                return value,{'url':url}
        transport=Search();record=m.discover(PUB,transport)
        self.assertEqual(record['issues'],[])
        self.assertEqual({r['route'] for r in record['routes']},{'article_doi','doi_text','complete_title'})
        self.assertEqual(parse_qs(urlsplit(transport.calls[0]).query)['article_doi'],[PUB['DOI']])
        self.assertEqual(parse_qs(urlsplit(transport.calls[-1]).query)['query'],['"'+PUB['Title']+'"'])
        self.assertEqual(len(record['excluded_hits']),2)
        self.assertEqual({o['accession'] for o in record['observations']},{ACC})

    def test_pipeline_doi_search_does_not_promote_reference_hits(self):
        class Empty(Fake):
            def get(self, url):
                self.calls.append(url)
                return {'results': []}, {'url': url}
        transport = Empty()
        record = m.discover(PUB, transport, doi_only=True)
        self.assertEqual(record['observations'], [])
        self.assertEqual(record['issues'], [])
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(parse_qs(urlsplit(transport.calls[0]).query)['article_doi'], [PUB['DOI']])

    def test_truncated_pages_are_issues_not_complete_coverage(self):
        class Truncated(Fake):
            def get(self,url):
                return ({'results':[{'id':ACC}]*100} if url.startswith(m.API) else {'records':[]}),{'url':url}
        record=m.discover(PUB,Truncated())
        self.assertEqual(len(record['issues']),1)
        self.assertIn('pagination',record['issues'][0]['error'])

    def test_dataset_versions_and_file_identity_are_checked(self):
        transport=Fake();record=m.collect_dataset(ACC,transport)
        self.assertEqual(transport.calls,[m.PUBLIC+ACC])
        self.assertEqual(record['metadata']['version'],2)
        self.assertEqual(record['issues'],[])
        for field,value in [('id','wrong12345'),('version',1)]:
            bad=copy.deepcopy(NATIVE);bad[field]=value
            with self.assertRaises(ValueError):m.collect_dataset(ACC,Fake(bad))
        bad=copy.deepcopy(NATIVE);bad['files'].append({**bad['files'][0],'filename':'other.xlsx'})
        with self.assertRaisesRegex(ValueError,'Conflicting'):m.collect_dataset(ACC,Fake(bad))

    def test_size_mismatch_keeps_unknown_count_and_file_metadata(self):
        bad=copy.deepcopy(NATIVE);bad['size']=99
        record=m.collect_dataset(ACC,Fake(bad))
        rows=m.project({'publications':[{'publication':PUB,'observations':[{'accession':ACC}]}],'datasets':{ACC:record}})
        self.assertIsNone(rows['Datasets'][0]['File Count'])
        self.assertEqual(rows['Datasets'][0]['Reported Dataset Size (Bytes)'],99)
        self.assertEqual(rows['Files'][0]['Size (Bytes)'],10)

    def test_hits_only_projection_shares_native_dataset_and_file_indices(self):
        record=m.collect_dataset(ACC,Fake())
        publications=[{'publication':PUB,'observations':[{'accession':ACC}]},
            {'publication':{**PUB,'Publication Index':'PUB-0002'},'observations':[{'accession':ACC}]},
            {'publication':{**PUB,'Publication Index':'PUB-0003'},'observations':[]}]
        rows=m.project({'publications':publications,'datasets':{ACC:record}})
        self.assertEqual(len(rows['Publications']),2);self.assertEqual(len(rows['Datasets']),1);self.assertEqual(len(rows['Files']),1)
        self.assertEqual(rows['Datasets'][0]['Publication Index'],'PUB-0001\nPUB-0002')
        self.assertEqual(rows['Datasets'][0]['Mendeley Dataset Index'],'MDS-0001')
        self.assertEqual(rows['Files'][0]['Mendeley File Index'],'MND-0001')
        self.assertNotIn('Mendeley Dataset Index', rows['Publications'][0])
        self.assertNotIn('Mendeley Data Accession', rows['Publications'][0])
        self.assertEqual(rows['Datasets'][0]['Mendeley Dataset Index'], rows['Files'][0]['Mendeley Dataset Index'])
        self.assertEqual(rows['Datasets'][0]['Dataset DOI'],'10.17632/'+ACC+'.2')

    def test_cache_hash_dates_and_file_download_refusal(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            root=Path(t);body=cache(root/'cache');out=root/'out';out.mkdir()
            transport=m.Transport(out,[root/'cache'],offline=True)
            _,receipt=transport.get(m.PUBLIC+ACC)
            self.assertEqual(receipt['retrieved_utc'],'2020-01-01T00:00:00Z')
            self.assertEqual(transport.requests,[])
            with self.assertRaisesRegex(ValueError,'scope'):transport.get(m.PUBLIC+ACC+'/files/id/file_downloaded')
            body.write_bytes(b'corrupted');other=root/'other';other.mkdir()
            with self.assertRaisesRegex(ValueError,'hash'):m.Transport(other,[root/'cache'],offline=True).get(m.PUBLIC+ACC)

    def test_offline_collection_fills_registered_owner_sheets(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            root=Path(t);cache(root/'cache')
            m._save(root/'input.json',[{'publication':PUB,'dataset_references':[{'dataset_doi':'10.17632/'+ACC+'.1'}]}])
            with patch('urllib.request.urlopen',side_effect=AssertionError('Unexpected network')),redirect_stdout(io.StringIO()):
                data=m.run_collection(root/'input.json',root/'run',caches=[root/'cache'],reference_only=True,offline=True,index_registry=root/'indices.json')
            self.assertEqual(data['status'],'complete');self.assertEqual(data['scope'],'reference_expansion_only')
            self.assertEqual(data['summary']['verified_reused_responses'],1)
            self.assertEqual(data['summary']['experimental_file_downloads'],0)
            self.assertEqual(data['publications'][0]['observations'][0]['dataset_doi'],'10.17632/'+ACC+'.1')
            self.assertEqual(data['publications'][0]['observations'][0]['returned_dataset_doi'],'10.17632/'+ACC+'.2')
            book=openpyxl.load_workbook(root/'run/Mendeley-Data-Enrichment.xlsx')
            self.assertEqual(book.sheetnames,['Publications','Datasets','Files'])
            headers=[c.value for c in book['Datasets'][1]]
            cell=book['Datasets'].cell(2,headers.index('Description')+1)
            self.assertEqual(cell.value,NATIVE['description']);self.assertEqual(cell.data_type,'s');book.close()
            with self.assertRaises(FileExistsError):m.run_collection(root/'input.json',root/'run',resume=True,reference_only=True,offline=True,index_registry=root/'indices.json')

    def test_bearer_credentials_are_scoped_and_never_persisted(self):
        class Response:
            status=200;headers={}
            def __init__(self,body):self.body=body
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return self.body
        class Opener:
            def __init__(self,echo=False):self.calls=[];self.echo=echo
            def open(self,request,timeout):
                self.calls.append(request)
                value=({'echo':'private-token'} if self.echo else {'results':[]}) if request.full_url.startswith(m.API) else NATIVE
                return Response(json.dumps(value).encode())
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            root=Path(t);token=root/'token.txt';token.write_text('private-token')
            out=root/'out';out.mkdir();transport=m.Transport(out,credentials=m.Credentials(token_file=token));opener=Opener();transport.opener=opener
            with patch.object(m.time,'sleep'):
                transport.get(m.PUBLIC+ACC);transport.get(m.API+'?article_doi=10.1016/example')
            self.assertIsNone(opener.calls[0].get_header('Authorization'))
            self.assertEqual(opener.calls[1].get_header('Authorization'),'Bearer private-token')
            self.assertNotIn('private-token',json.dumps(transport.requests))
            self.assertTrue(all(b'private-token' not in p.read_bytes() for p in (out/'native').iterdir()))
            other=root/'echo';other.mkdir();echo=m.Transport(other,credentials=m.Credentials(token_file=token));echo.opener=Opener(echo=True)
            with self.assertRaisesRegex(ValueError,'Credential in response'):echo.get(m.API+'?article_doi=10.1016/example')
            self.assertEqual(list((other/'native').iterdir()),[])

    def test_client_credentials_refresh_without_persisting_token_responses(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return b'{"access_token":"test-bearer","expires_in":300}'
        class Opener:
            def __init__(self):self.calls=[]
            def open(self,request,timeout):self.calls.append(request);return Response()
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            root=Path(t);path=root/'client.json';m._save(path,{'client_id':'client','client_secret':'private-secret','scope':'read'})
            c=m.Credentials(client_file=path);opener=Opener()
            with patch.object(m,'build_opener',return_value=opener),patch.object(m.time,'monotonic',side_effect=[100,101,500,501]):
                self.assertEqual(c.header(),'Bearer test-bearer')
                self.assertEqual(c.header(),'Bearer test-bearer')
                self.assertEqual(c.header(),'Bearer test-bearer')
            self.assertEqual(c.requests,2)
            self.assertTrue(all(r.full_url==m.TOKEN for r in opener.calls))
            self.assertTrue(all(r.get_header('Authorization').startswith('Basic ') for r in opener.calls))
            self.assertEqual(list(root.iterdir()),[path])

    def test_missing_credentials_keep_reference_hits_and_mark_discovery_incomplete(self):
        class NeverNetwork:
            def open(self,*args,**kwargs):raise AssertionError('Unexpected uncached request')
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as t:
            root=Path(t);cache(root/'cache')
            m._save(root/'input.json',[{'publication':PUB,'dataset_references':[{'dataset_doi':'10.17632/'+ACC+'.1'}]}])
            with patch.dict(m.os.environ,{},clear=True),patch.object(m,'build_opener',return_value=NeverNetwork()),redirect_stdout(io.StringIO()):
                data=m.run_collection(root/'input.json',root/'run',caches=[root/'cache'],index_registry=root/'indices.json')
            self.assertEqual(data['status'],'incomplete')
            self.assertEqual(data['summary']['blocked_search_routes'],3)
            self.assertEqual(data['summary']['network_requests_this_execution'],0)
            self.assertEqual(data['summary']['publications_with_datasets'],1)
            self.assertTrue((root/'run/Mendeley-Data-Enrichment.xlsx').exists())
