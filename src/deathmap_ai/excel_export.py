"""Portable Excel export from canonical entity JSON and a reviewed template.

Uses openpyxl, installed with the project, without Codex or a Node runtime.
Preserves template colors/styles and keeps source claims separate from reviewer
fields. Existing output files are refused; user-reviewed workbooks are inputs
to neither this exporter nor template preparation.
"""
import argparse
from copy import copy
import hashlib
import json
from pathlib import Path
from openpyxl import load_workbook


def body_style(sheet, column):
    """Use explicit body formatting, falling back to Excel column formatting.

    An owner may delete all example rows while retaining whole-column colors.
    Grouped column dimensions can cover several columns, so resolve their span
    rather than assuming every column has a separately stored dimension.
    """
    cell = sheet.cell(2, column)
    if cell.has_style:
        return copy(cell._style)
    for key, dimension in sheet.column_dimensions.items():
        first = dimension.min or sheet[key + '1'].column
        last = dimension.max or first
        if first <= column <= last and dimension.has_style:
            return copy(dimension._style)
    return copy(cell._style)

ENTITY_SHEETS={'Publications','Screen Groups','Screens','Datasets','Screen-Dataset Links','Evidence'}
REVIEW_FIELDS={'Publications':{'publication_notes'},'Screens':{'screen_notes'},'Evidence':{'reviewer_check','reviewer_note'}}


def export(run, template):
    """Create a new workbook from one run; return its path and record provenance.

    Run supplies projection.json. Template supplies header/schema and cell
    styles. Missing sheets, unsupported populated columns, populated reviewer
    fields or an existing authored workbook fail before anything is saved.
    """
    run=Path(run).resolve();template=Path(template).resolve();destination=run/'workbook-authored.xlsx'
    if destination.exists():raise FileExistsError('Refusing to overwrite existing workbook-authored.xlsx; use a new run directory')
    projection=json.loads((run/'projection.json').read_text(encoding='utf-8'))
    workbook=load_workbook(template)
    try:
        for name,rows in projection['sheets'].items():
            if name not in ENTITY_SHEETS or name not in workbook:raise ValueError(f'Unsupported entity sheet: {name}')
            sheet=workbook[name];headers=[c.value for c in sheet[1]]
            if any(not isinstance(h,str) for h in headers) or len(headers)!=len(set(headers)):raise ValueError(f'Invalid template headers: {name}')
            for row in rows:
                if any(k not in headers and v not in (None,'') for k,v in row.items()):raise ValueError(f'Unmapped populated field: {name}')
                if any(row.get(k) not in (None,'') for k in REVIEW_FIELDS.get(name,set())):raise ValueError('Fresh export cannot contain generated reviewer notes')
            # Capture one body style per column before clearing example values.
            # Copying styles within this workbook preserves theme-based colors.
            styles=[body_style(sheet,c) for c in range(1,len(headers)+1)]
            height=sheet.row_dimensions[2].height
            for row in sheet.iter_rows(min_row=2):
                for cell in row:cell.value=None;cell.hyperlink=None
            for number,row in enumerate(rows,2):
                if height is not None:sheet.row_dimensions[number].height=height
                for c,field in enumerate(headers,1):
                    cell=sheet.cell(number,c);cell._style=copy(styles[c-1]);value=row.get(field)
                    cell.value=value
                    # A repository's text is never executable spreadsheet code.
                    if isinstance(value,str):cell.data_type='s'
                    if field in {'source_link','pmid_link','doi_link'} and value:
                        if not isinstance(value,str) or not value.startswith(('http://','https://')):raise ValueError('Invalid native URL')
                        cell.hyperlink=value
                    if field in REVIEW_FIELDS.get(name,set()):
                        cell.value=None
                        # Keep template fills; flag unresolved evidence using
                        # its established review accent only, without inference.
                        if name=='Evidence' and row.get('evidence_status') in {'conflicting','unresolved'}:
                            from openpyxl.styles import PatternFill
                            cell.fill=PatternFill('solid',fgColor='F4B183')
            sheet.freeze_panes='A2'
        # The repaired template already carries the approved Definitions layout.
        # Do not copy data or reviewer edits from any historical workbook.
        with destination.open('xb') as stream:workbook.save(stream)
    finally:workbook.close()
    digest=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
    receipt={'primary_workbook':'workbook-authored.xlsx','writer':'openpyxl',
        'template_path':str(template),'template_sha256':digest(template),'projection_sha256':digest(run/'projection.json'),
        'writer_sha256':digest(__file__),'workbook_sha256':digest(destination),
        'compatibility':'Native hyperlinks; no template-transplant stage. Structural tests do not prove Excel opening.'}
    (run/'workbook-export-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return destination


def approved_template(root):
    """Resolve the registered template and detect unintended template changes."""
    root=Path(root)
    manifest=json.loads((root/'data/templates/current-template.json').read_text(encoding='utf-8'))
    if manifest.get('status')!='approved_portable_template':
        raise ValueError('Template approval pending')
    template=root/manifest['template']
    if hashlib.sha256(template.read_bytes()).hexdigest()!=manifest['sha256']:
        raise ValueError('Active template hash mismatch; register the reviewed revision first')
    return template


def main():
    """Export a new run using the active approved template or an explicit draft."""
    root=Path(__file__).resolve().parents[2]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    parser.add_argument('--template',type=Path)
    args=parser.parse_args()
    if args.template is None:
        try:args.template=approved_template(root)
        except ValueError as error:parser.error(str(error))
    print(export(args.run,args.template))


if __name__=='__main__':main()
