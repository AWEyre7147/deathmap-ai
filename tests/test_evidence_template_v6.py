"""Verify current owner template and recovery copy."""
from pathlib import Path
import json,unittest
from openpyxl import load_workbook
from deathmap_ai.evidence_model import HEADERS
from deathmap_ai.excel_export import approved_template
ROOT=Path(__file__).resolve().parents[1]
class TemplateTests(unittest.TestCase):
    def test_current_schema(self):
        book=load_workbook(approved_template(ROOT))
        self.assertEqual([c.value for c in book['Evidence'][1]],HEADERS)
        self.assertEqual(book['Screens']['AM1'].value,'cellosaurus_accession')
        self.assertEqual(book['Publications']['P1'].value,'evidence_id_link')
        self.assertFalse(any(c.value=='Cell line' for row in book['Definitions'] for c in row))
        book.close()
    def test_backup_and_manifest(self):
        main=approved_template(ROOT)
        manifest=json.loads((ROOT/'data/templates/current-template.json').read_text())
        self.assertEqual(main.read_bytes(),(ROOT/manifest['backup']).read_bytes())
