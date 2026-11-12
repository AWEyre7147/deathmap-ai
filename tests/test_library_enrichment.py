"""Offline fixtures for publisher sections, stable links and owner-template export."""
import json
from pathlib import Path
import tempfile
import unittest
from openpyxl import load_workbook
from deathmap_ai.library_content import extract, json_sections, video_material
from deathmap_ai.library_enrichment import prepare, project, export_run, save, TEMPLATE

ROOT=Path(__file__).resolve().parents[1]
PUB={'Publication Index':'PUB-0001','Title':'Cancer screen','DOI':'10.1234/example','Journal':'Example Journal','PMID':'123'}
HTML=b'''<html><head><meta name="citation_doi" content="10.1234/example"></head><body><article>
<h1>A screen</h1><h2>Methods</h2><h3>Screen procedure</h3><p>Source-written experimental design.</p>
<figure><p>Main figure caption is not a methods paragraph.</p></figure>
<h2>Results</h2><h3>Screen procedure</h3><p>A biological finding.</p>
<h2>Data availability</h2><p>Data are available as GSE12345 and code at https://github.com/example/repository.</p>
<h2>Supporting Information</h2><a href="files/table.xlsx?token=private">Table S1</a>
</article></body></html>'''


def attempt(data, outcome='retrieved',mode='automatic',number=0):
    return {'publication_index':'PUB-0001','mode':mode,'pass_number':number,'outcome':outcome,'data':data,'destination':'https://publisher.example/article','platform':'Example'}


class LibraryContentTests(unittest.TestCase):
    def test_untitled_nature_supplement_is_retained_without_inventing_a_title(self):
        body=b'<html><head><meta name="citation_doi" content="10.1234/example"></head><body><div id="MOESM3"><p>Additional supporting description.</p></div></body></html>'
        result=extract(body,'https://www.nature.com/articles/example',PUB)
        self.assertEqual(result['outcome'],'retrieved')
        self.assertEqual(result['materials'][0]['label'],'')
        self.assertEqual(result['materials'][0]['description'],'Additional supporting description.')
        self.assertEqual(result['materials'][0]['native_id'],'MOESM3')
        self.assertEqual(result['materials'][0]['url'],'')

    def test_description_only_video_does_not_crash_or_enter_output(self):
        body=b'<meta name="citation_doi" content="10.1234/example"><div id="MOESM3"><p>Supplementary Video 1.</p></div>'
        result=extract(body,'https://www.nature.com/articles/example',PUB)
        self.assertTrue(result['doi_verified']);self.assertEqual(result['materials'],[])

    def test_video_detection_preserves_nonvideo_data_references(self):
        self.assertTrue(video_material({'label':'Movie S1','url':'https://example.org/download'}))
        self.assertTrue(video_material({'url':'https://example.org/movie.mp4'}))
        self.assertTrue(video_material({'description':'Supplementary Video 1.'}))
        self.assertFalse(video_material({'label':'Table S1','description':'Measurements corresponding to Video 1.','url':'https://example.org/table.xlsx'}))

    def test_native_headings_and_blank_generated_content_type(self):
        result=extract(HTML,'https://publisher.example/article',PUB)
        self.assertTrue(result['doi_verified'])
        self.assertEqual([p['heading'] for p in result['context']],['Screen procedure','Data availability'])
        self.assertEqual(result['context'][0]['ancestors'],['A screen','Methods','Screen procedure'])
        self.assertEqual(result['context'][0]['native_type'],'')
        self.assertNotIn('A biological finding.',str(result))
        self.assertNotIn('Main figure caption',str(result))

    def test_only_explicit_support_listing_and_no_transient_query(self):
        body=HTML.replace(b'<h2>Methods</h2>',b'<h2>Methods</h2><a href="/article#supp1">Supplementary Table</a>')
        result=extract(body,'https://publisher.example/article',PUB)
        self.assertEqual(len(result['materials']),1)
        self.assertEqual(result['materials'][0]['url'],'https://publisher.example/files/table.xlsx')
        self.assertNotIn('private',json.dumps(result))

    def test_exact_doi_not_substring_or_conflicting_metadata(self):
        self.assertFalse(extract(HTML.replace(b'10.1234/example',b'10.1234/example-other'),'https://example.org/a',PUB)['doi_verified'])
        self.assertFalse(extract(HTML.replace(b'</head>',b'<meta name="citation_doi" content="10.1234/other"></head>'),'https://example.org/a',PUB)['doi_verified'])

    def test_clear_boundaries_required_not_scientific_keywords(self):
        body=HTML.replace(b'Methods',b'Genome-wide CRISPR screen')
        result=extract(body,'https://example.org/a',PUB)
        self.assertEqual(len(result['context']),1)
        self.assertEqual(result['context'][0]['heading'],'Data availability')

    def test_missing_content_stays_incomplete_and_challenge_is_not_access(self):
        self.assertEqual(extract(b'<meta name="citation_doi" content="10.1234/example">','https://example.org/a',PUB)['outcome'],'parser_incomplete')
        result=extract(b'<title>Verify you are human</title>','https://example.org/a',PUB)
        self.assertEqual(result['outcome'],'challenge');self.assertFalse(result['doi_verified'])

    def test_source_text_guard_reports_omission_without_truncation(self):
        result=extract(HTML,'https://example.org/a',PUB,max_text=4)
        self.assertEqual(result['context'],[])
        self.assertTrue(any('size guard' in n for n in result['notes']))

    def test_publisher_xml_native_section_type_is_preserved(self):
        body=b'''<article><front><article-meta><article-id pub-id-type="doi">10.1234/example</article-id></article-meta></front><body><sec sec-type="methods"><title>Materials and methods</title><p>Native procedure text.</p></sec><sec><title>Results</title><p>Finding.</p></sec><supplementary-material id="S1"><label>Table S1</label><caption><p>Description.</p></caption><media xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="table.xlsx"/></supplementary-material></body></article>'''
        result=extract(body,'https://example.org/a',PUB,'xml')
        self.assertEqual(result['context'][0]['native_type'],'methods')
        self.assertEqual(result['materials'][0]['native_reference'],'table.xlsx')
        self.assertEqual(len(result['context']),1)

    def test_json_keeps_ancestors_and_requires_verified_article_binding(self):
        def section(title,children):return {'#name':'ce:section','$$':[{'#name':'ce:section-title','_':title},*children]}
        para={'#name':'ce:para','_':'Source text.'}
        payload={'article':{'content':[section('Results',[section('Methods',[para])]),section('Experimental Procedures',[section('Culture',[para])])]}}
        result=extract(json.dumps(payload).encode(),'https://example.org/body',PUB,'json',True)
        self.assertEqual(len(result['context']),1)
        self.assertEqual(result['context'][0]['ancestors'],['Experimental Procedures','Culture'])
        self.assertFalse(extract(json.dumps(payload).encode(),'https://example.org/body',PUB,'json')['doi_verified'])


class LibraryProjectionTests(unittest.TestCase):
    def test_inherited_video_entries_are_filtered_without_editing_evidence(self):
        data=extract(HTML,'https://example.org/a',PUB)
        data['materials'].append({'label':'Supplementary Video 1','description':'A movie.','url':'https://example.org/a.mp4','native_reference':'a.mp4','native_id':'V1','source_format':'HTML'})
        rows=project({'publications':[PUB]},[attempt(data)],None)['rows']
        self.assertEqual(len(data['materials']),2)
        self.assertEqual(len(rows['Supporting Materials']),1)
        self.assertEqual(rows['Supporting Materials'][0]['File Type'],'.xlsx')

    def test_failed_later_attempt_does_not_erase_retained_content(self):
        data=extract(HTML,'https://example.org/a',PUB)
        rows=project({'publications':[PUB]},[attempt(data),attempt({},'access_block','assisted',1)],None)['rows']
        self.assertEqual(len(rows['Article Context']),2)
        self.assertEqual(rows['Article Context'][0]['Content Type'],'')
        context_ids={r['Context Index'] for r in rows['Article Context']}
        self.assertTrue(all(r['Context Index'] in context_ids for r in rows['Repository References']))

    def test_persistent_resource_ids_survive_reordered_attempts(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as tmp:
            registry=Path(tmp)/'ids.json';data=extract(HTML,'https://example.org/a',PUB)
            first=project({'publications':[PUB]},[attempt(data)],registry)
            data['context'].reverse()
            second=project({'publications':[PUB]},[attempt(data)],registry)
            self.assertEqual({r['Text']:r['Context Index'] for r in first['rows']['Article Context']},{r['Text']:r['Context Index'] for r in second['rows']['Article Context']})

    def test_owner_template_and_separate_status_workbook(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as tmp:
            folder=Path(tmp);data=extract(HTML,'https://example.org/a',PUB)
            manifest={'publications':[PUB,{**PUB,'Publication Index':'PUB-0002','DOI':''}],
                      'template':str(TEMPLATE),'template_sha256':__import__('hashlib').sha256(TEMPLATE.read_bytes()).hexdigest()}
            save(folder/'manifest.json',manifest)
            save(folder/'state.json',{'attempts':[attempt(data),attempt({},'access_block','assisted',1)]})
            result=export_run(folder,folder/'export',folder/'ids.json')
            self.assertEqual(result['publications'],2)
            book=load_workbook(folder/'export/Library-Enrichment.xlsx',read_only=True)
            self.assertEqual(book.sheetnames,['Publications','Article Context','Supporting Materials','Repository References'])
            self.assertEqual(book['Publications'].max_row,3)
            self.assertEqual(book['Repository References']['B1'].value,'Contex Index')
            self.assertTrue(book['Repository References']['B2'].value.startswith('LCTX-'))
            book.close()
            status=load_workbook(folder/'export/Library-Enrichment-Status.xlsx',read_only=True)
            self.assertIn('Assisted Pass 1',[c.value for c in status.active[1]])
            status.close()
            with self.assertRaises(FileExistsError):export_run(folder,folder/'export',folder/'ids.json')

    def test_input_preparation_preserves_missing_doi_and_rejects_conflicts(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as tmp:
            folder=Path(tmp);save(folder/'registry.json',[{'Publication index':'PUB-0001','ORCS Publication ID':'1','PMID':'123'}])
            save(folder/'input.json',[{'PUBLICATION_ID':'1','TITLE':'Example','PMID':'123'}])
            self.assertEqual(prepare(folder/'input.json',folder/'registry.json')['publications'][0]['DOI'],'')
            save(folder/'input.json',[{'PUBLICATION_ID':'1','PMID':'456'}])
            with self.assertRaises(ValueError):prepare(folder/'input.json',folder/'registry.json')


if __name__=='__main__':unittest.main()
