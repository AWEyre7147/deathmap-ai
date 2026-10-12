"""Inspectable fixtures for full-run boundaries and lossless metadata projection."""
import json
import unittest
from urllib.parse import parse_qs, urlsplit
from deathmap_ai.arrayexpress_collection import discovery_routes, _discover, parse_metadata_file, project, _study, annotation_candidates


class CollectionTests(unittest.TestCase):
    def test_only_declared_metadata_files_are_followed(self):
        native={'accno':'E-MTAB-1','attributes':[{'name':'AttachTo','value':'ArrayExpress'}],
            'section':{'type':'Study','files':[
                {'type':'file','path':'E-MTAB-1.idf.txt','attributes':[{'name':'Type','value':'IDF File'}]},
                {'type':'file','path':'reads.fastq.gz','attributes':[{'name':'Type','value':'Raw data'}]},
                {'type':'file','path':'E-MTAB-1.sdrf.txt','attributes':[{'name':'Type','value':'Unknown'}]}]}}
        calls=[]
        def get(url):
            calls.append(url)
            return (json.dumps(native).encode() if '/api/' in url else b'Title\tExample\n'),'raw/1'
        result=_study(get,'E-MTAB-1')
        self.assertEqual(len(calls),2)
        self.assertTrue(calls[1].endswith('.idf.txt'))
        self.assertEqual(result['metadata_files'][0]['kind'],'idf')
        self.assertEqual(len(result['issues']),1)

    def test_out_of_collection_study_is_preserved_without_file_fetch(self):
        native={'accno':'E-X-1','attributes':[{'name':'AttachTo','value':'OtherCollection'}]}
        result=_study(lambda u:(json.dumps(native).encode(),'raw/1'),'E-X-1')
        self.assertFalse(result['arrayexpress_membership_confirmed'])
        self.assertEqual(result['native'],native)
        self.assertEqual(result['metadata_files'],[])

    def test_retained_routes_preserve_full_title_and_omit_retired_doi(self):
        routes=dict(discovery_routes({'PMID':'123','DOI':'10.1/a:b','TITLE':'A: title.'}))
        self.assertEqual(len(routes),2)
        self.assertEqual(parse_qs(urlsplit(routes['native_complete_title']).query)['query'],['"A: title."'])
        self.assertNotIn('native_quoted_doi',routes)
        self.assertEqual(len(discovery_routes({'TITLE':'Only a title.'})),1)

    def test_annotation_identity_and_mention_provenance(self):
        annotation={'type':'Accession Numbers','exact':'E-MTAB-12','tags':[]}
        native=[{'source':'MED','extId':'123','annotations':[annotation]}]
        rows=annotation_candidates(native,'123')
        self.assertEqual(rows[0]['native'],annotation)
        self.assertEqual(rows[0]['evidence_kind'],'precomputed_accession_mention')
        with self.assertRaisesRegex(ValueError,'identity'):annotation_candidates(native,'124')

    def test_cursor_completion_and_repetition(self):
        native={'hits':[{'accession':'E-MTAB-1','type':'study'}],'nextCursor':None}
        rows=_discover(lambda u:(json.dumps(native).encode(),'raw/1'),'native_complete_title','https://example/search',{})
        self.assertEqual(rows[0]['source'],'raw/1')
        native['nextCursor']='same'
        with self.assertRaisesRegex(ValueError,'cursor'):
            _discover(lambda u:(json.dumps(native).encode(),'raw/1'),'native_complete_title','https://example/search',{})

    def test_metadata_preserves_repeated_headers_empty_cells_and_rows(self):
        rows=parse_metadata_file(b'Source Name\tComment[x]\tComment[x]\na\t\tb\na\t\tb\n','sdrf')
        self.assertEqual(rows[0],['Source Name','Comment[x]','Comment[x]'])
        self.assertEqual(rows[1],rows[2]);self.assertEqual(rows[1][1],'')
        with self.assertRaisesRegex(ValueError,'width'):parse_metadata_file(b'a\tb\nx\n','sdrf')
        with self.assertRaisesRegex(ValueError,'markup'):parse_metadata_file(b'<html>error','idf')

    def test_projection_keeps_whole_description_and_missing_counts(self):
        description='x'*4000
        native={'accno':'E-MTAB-1','section':{'type':'Study','attributes':[{'name':'Description','value':description}]}}
        study={'native':native,'arrayexpress_membership_confirmed':True,'metadata_files':[
            {'kind':'sdrf','rows':[['Source Name','Field','Field'],['a','','b']]},
            {'kind':'idf','rows':[['Title','A title']]}]}
        db={'publications':[{'publication':{'PMID':'123'},'observations':[{'accession':'E-MTAB-1','evidence_kind':'precomputed_accession_mention'}]}],
            'studies':{'E-MTAB-1':study}}
        tables=project(db)
        self.assertEqual(tables['Studies'][0]['Study description'],description)
        self.assertIsNone(tables['Studies'][0]['Samples reported'])
        self.assertEqual(len(tables['SDRF metadata']),3)
        self.assertEqual(tables['SDRF metadata'][1]['Original value'],'')
        self.assertNotIn('Part',tables['IDF metadata'][0])


if __name__=='__main__':unittest.main()
