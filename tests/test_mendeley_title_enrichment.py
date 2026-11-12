"""Small offline contracts for the accepted title-first Mendeley stage."""
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import urlsplit
from unittest.mock import patch

import openpyxl
from deathmap_ai import mendeley_title_enrichment as m

ACC = 'abc123def4'
FILE = '12345678-abcd'


class Metadata:
    requests = []

    def get(self, url):
        path = urlsplit(url).path
        if path == '/search':
            body = {'total_records': 140000, 'records': [
                {'id': ACC, 'title': 'Figure 4 - A complete article title'},
                {'id': 'other12345', 'title': 'An unrelated article'}]}
        elif path.endswith('/folders'):
            body = [{'id': 'root', 'name': 'Screens', 'description': 'Screen documentation', 'parent_id': None}]
        elif path.endswith('/files'):
            body = [dict(id=FILE, filename='Readouts.CSV', folder_id='root', size=12)]
        elif '/files/' in path:
            body = dict(id=FILE, filename='Readouts.CSV', folder_id='root', size=12, description='Readcounts')
        else:
            body = dict(id=ACC, version=2, doi={'id': f'10.17632/{ACC}.2'},
                        name='Figure 4 - A complete article title', description='Source data', files=[{'id': FILE}])
        return body, {'url': url}


class TitleTests(unittest.TestCase):
    def test_match_retains_all_words_and_boundaries(self):
        self.assertTrue(m.title_matches('A complete article title.', 'Figure 4: A COMPLETE article title'))
        self.assertFalse(m.title_matches('A complete article title', 'A complete title'))
        self.assertFalse(m.title_matches('cell', 'cells'))

    def test_projection_and_template_export(self):
        datasets = {}
        p = {'Publication Index': 'PUB-0001', 'Title': 'A complete article title.', 'DOI': None}
        record = m.collect(p, Metadata(), datasets)
        self.assertEqual(record['issues'], [])
        rows = m.project({'publications': [record], 'datasets': datasets})
        self.assertEqual(rows['Publications'][0]['Page Size Returned'], 2)
        self.assertEqual(rows['Datasets'][0]['MD Dataset Index'], 'MDD-0001')
        file = rows['Files'][0]
        self.assertEqual(file['MD File Index'], 'MDF-0001')
        self.assertEqual(file['Folder Description'], 'Screens: Screen documentation')
        self.assertEqual(file['File Type'], '.csv')
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / 'outputs') as folder:
            path = Path(folder) / 'review.xlsx'
            m.export_registered(m.TEMPLATE, path, rows)
            workbook = openpyxl.load_workbook(path)
            self.assertEqual(workbook['Files']['J2'].value, 'Readcounts')
            self.assertEqual(workbook['Files']['F2'].value, 'Screens: Screen documentation')

    def test_errors_are_distinct_from_zero_matches(self):
        class Failed:
            def get(self, url):
                raise ValueError('Connection failed')
        p = {'Title': 'A complete article title'}
        record = m.collect(p, Failed(), {})
        self.assertNotIn('search', record)
        self.assertEqual(record['issues'], ['Connection failed'])

    def test_normal_run_entry_point_exports_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / 'outputs') as folder:
            root = Path(folder)
            source = root / 'publications.json'
            source.write_text(json.dumps([{'Publication Index': 'PUB-0001',
                'Title': 'A complete article title.'}]), encoding='utf-8')
            with patch.object(m, 'Transport', return_value=Metadata()):
                result = m.run(source, root / 'run', index_registry=root / 'indices.json', offline=True)
                self.assertEqual(result['status'], 'complete')
                self.assertTrue((root / 'run' / 'Mendeley-Data-Enrichment.xlsx').exists())
                with self.assertRaises(FileExistsError):
                    m.run(source, root / 'run', index_registry=root / 'indices.json', offline=True)

    def test_folder_cycle_and_missing_parent_fail(self):
        with self.assertRaises(ValueError):
            m.folder_context({'folder_id': 'missing'}, [])
        with self.assertRaises(ValueError):
            m.folder_context({'folder_id': 'x'}, [{'id': 'x', 'name': 'Cycle', 'parent_id': 'x'}])

    def test_download_endpoints_remain_forbidden(self):
        from deathmap_ai.mendeley_data_enrichment import Transport
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / 'outputs') as folder:
            transport = Transport(folder, offline=True)
            for suffix in ('/contents', '/file_downloaded'):
                with self.assertRaisesRegex(ValueError, 'outside'):
                    transport.get(f'{m.GATEWAY}/datasets/publics/{ACC}/files/{FILE}{suffix}')

    def test_search_requests_json_instead_of_dataset_media_type(self):
        from deathmap_ai.mendeley_data_enrichment import Transport
        from types import SimpleNamespace
        class Response:
            status = 200
            headers = {'Content-Type': 'application/json'}
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self, limit):
                return b'{"records": [], "total_records": 0}'
        def open_request(request, timeout):
            self.assertEqual(request.get_header('Accept'), 'application/json')
            return Response()
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / 'outputs') as folder:
            transport = Transport(folder, credentials=SimpleNamespace(header=lambda: 'Bearer fixture', secrets=set()))
            transport.opener = SimpleNamespace(open=open_request)
            transport.get(m.GATEWAY + '/search?query=title')


if __name__ == '__main__':
    unittest.main()
