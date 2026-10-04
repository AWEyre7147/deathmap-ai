"""Verify the owner template changes without rewriting either workbook."""
import copy
from pathlib import Path
import unittest
import zipfile
from openpyxl import load_workbook
from deathmap_ai.evidence_model import HEADERS

ROOT=Path(__file__).resolve().parents[1]


class TemplateTests(unittest.TestCase):
    def test_template_schema_and_only_affected_glossary_cells_change(self):
        old=load_workbook(ROOT/'data/templates/DeathMap-AI-output-v5.xlsx')
        new=load_workbook(ROOT/'data/templates/DeathMap-AI-output-v6.xlsx')
        self.assertEqual(new.sheetnames,[s if s!='Sources & Evidence' else 'Evidence' for s in old.sheetnames])
        self.assertEqual([c.value for c in new['Evidence'][1]],HEADERS)
        self.assertEqual(new['Screens']['AM1'].value,'cellosaurus_accession')
        self.assertEqual(new['Publications']['P1'].value,'evidence_id_link')
        refs={'Scientific Glossary','Source Glossary','Technical Glossary','Pipeline Glossary'}
        for sheet in old:
            if sheet.title=='Sources & Evidence':continue
            for row in sheet:
                for cell in row:
                    target=new[sheet.title][cell.coordinate]
                    authorized=(sheet.title in refs and cell.row>=102) or (sheet.title=='Definitions' and cell.row in [7,8])
                    if not authorized:self.assertEqual(cell.value,target.value,(sheet.title,cell.coordinate))
                    if sheet.title=='Definitions' and cell.row==8:continue
                    for attr in ['font','fill','border','alignment','protection','number_format']:
                        self.assertEqual(copy.copy(getattr(cell,attr)),copy.copy(getattr(target,attr)),(sheet.title,cell.coordinate,attr))
        self.assertEqual(new['Evidence']['L2'].fill.fgColor.rgb,'FFFFF2CC')
        for sn in refs:self.assertEqual(next(iter(new[sn].tables.values())).ref, 'A1:E116' if sn in {'Source Glossary','Technical Glossary'} else 'A1:F116')
        old.close();new.close()

    def test_fixed_reference_parts_have_identical_bytes(self):
        with zipfile.ZipFile(ROOT/'data/templates/DeathMap-AI-output-v5.xlsx') as a,zipfile.ZipFile(ROOT/'data/templates/DeathMap-AI-output-v6.xlsx') as b:
            for index in [7,8,11,12]:
                part=f'xl/worksheets/sheet{index}.xml'
                self.assertEqual(a.read(part),b.read(part))


if __name__=='__main__':unittest.main()
