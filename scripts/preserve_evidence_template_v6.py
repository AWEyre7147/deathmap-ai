"""Restore exact template features that the artifact XLSX round trip changes.

Artifact Tool authors the changed cells and previews. Its import/export changes
unrelated styles, so this narrowly scoped OOXML preservation stage transplants
only authorized edits into the original package. Unaffected parts retain their
original bytes, and original style indexes are never reordered.
"""
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as E
import zipfile
import sys

N='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
Q=lambda name:f'{{{N}}}{name}'


def main():
    """Create v6 from the original v5 package and the artifact-authored edit plan."""
    plan=json.loads(Path(sys.argv[1] if len(sys.argv)>1 else 'logs/evidence-model-v6/template-plan.json').read_text(encoding='utf-8'))
    destination=Path(plan.get('destination','data/templates/DeathMap-AI-output-v6.xlsx'))
    if destination.exists(): raise FileExistsError(destination)
    with zipfile.ZipFile(plan['input']) as old, zipfile.ZipFile(plan['artifact_output']) as new:
        parts={name:old.read(name) for name in old.namelist()}
        source_strings=E.fromstring(new.read('xl/sharedStrings.xml')) if 'xl/sharedStrings.xml' in new.namelist() else []
        original_styles=E.fromstring(parts['xl/styles.xml']); generated_styles=E.fromstring(new.read('xl/styles.xml'))
        maps={}
        for kind in ['fonts','fills','borders','cellStyleXfs']:
            dest=original_styles.find(Q(kind)); src=generated_styles.find(Q(kind)); maps[kind]={}
            for i,item in enumerate(src):
                adjusted=copy.deepcopy(item)
                if kind=='cellStyleXfs':
                    for attr,collection in [('fontId','fonts'),('fillId','fills'),('borderId','borders')]:
                        if attr in adjusted.attrib:adjusted.set(attr,str(maps[collection][int(adjusted.get(attr))]))
                dest.append(adjusted);maps[kind][i]=len(dest)-1
            dest.set('count',str(len(dest)))
        # Preserve original custom formats and allocate new IDs only as needed.
        num_map={};dest=original_styles.find(Q('numFmts'));src=generated_styles.find(Q('numFmts'))
        if src is not None:
            if dest is None:dest=E.Element(Q('numFmts'));original_styles.insert(0,dest)
            by_code={x.get('formatCode'):int(x.get('numFmtId')) for x in dest}
            for x in src:
                code=x.get('formatCode'); ident=by_code.get(code)
                if ident is None:
                    ident=max([163,*by_code.values()])+1; added=copy.deepcopy(x);added.set('numFmtId',str(ident));dest.append(added);by_code[code]=ident
                num_map[int(x.get('numFmtId'))]=ident
            dest.set('count',str(len(dest)))
        dest=original_styles.find(Q('cellXfs'));style_map={}
        for i,x in enumerate(generated_styles.find(Q('cellXfs'))):
            added=copy.deepcopy(x)
            for attr,collection in [('fontId','fonts'),('fillId','fills'),('borderId','borders'),('xfId','cellStyleXfs')]:
                if attr in added.attrib:added.set(attr,str(maps[collection][int(added.get(attr))]))
            num=int(added.get('numFmtId','0'));added.set('numFmtId',str(num_map.get(num,num)))
            dest.append(added);style_map[i]=len(dest)-1
        dest.set('count',str(len(dest)));parts['xl/styles.xml']=E.tostring(original_styles,encoding='utf-8',xml_declaration=True)
        book=E.fromstring(parts['xl/workbook.xml']);sheets=list(book.find(Q('sheets')))
        for index,sheet in enumerate(sheets,1):
            sn=sheet.get('name'); part=f'xl/worksheets/sheet{index}.xml'
            edits=[e for e in plan['edits'] if e['sheet']==sn]
            if sn in plan['added_glossary_rows']:
                edits += [{'cell':f'{chr(65+i)}{115+r}'} for r,values in enumerate(plan['added_glossary_rows'][sn]) for i in range(len(values))]
            root=E.fromstring(parts[part]);authored=E.fromstring(new.read(part))
            styled = sn in plan.get('styled_sheets',['Sources & Evidence'])
            if sn=='Sources & Evidence':
                edits += [{'cell':f'{chr(65+i)}{r}'} for i in range(13) for r in [1,2]]
                sheet.set('name','Evidence')
            if styled:
                # The authorized evidence view needs wider columns and yellow
                # reviewer cells. Other views retain original dimensions/styles.
                for tag in ['cols','sheetViews']:
                    current=root.find(Q(tag));replacement=authored.find(Q(tag))
                    if current is not None:root.remove(current)
                    if replacement is not None:root.insert(0,copy.deepcopy(replacement))
            if not edits:continue
            if sn in plan.get('column_edits',{}):
                cols=root.find(Q('cols'))
                if cols is None:cols=E.Element(Q('cols'));root.insert(0,cols)
                for letters,width in plan['column_edits'][sn].items():
                    ident=0
                    for ch in letters:ident=ident*26+ord(ch)-64
                    cols.append(E.Element(Q('col'),{'min':str(ident),'max':str(ident),'width':str(width),'customWidth':'1'}))
            data=root.find(Q('sheetData'));cells={c.get('r'):c for c in data.iter(Q('c'))}
            rows_by_number={int(row.get('r')):row for row in data}
            authored_rows={int(row.get('r')):row for row in authored.find(Q('sheetData'))}
            authored_cells={c.get('r'):c for c in authored.iter(Q('c'))}
            for edit in edits:
                addr=edit['cell'];c=authored_cells.get(addr)
                if c is None:continue
                c=copy.deepcopy(c)
                if c.get('t')=='s':
                    text=''.join(source_strings[int(c.find(Q('v')).text)].itertext())
                    for child in list(c):c.remove(child)
                    c.set('t','inlineStr');t=E.SubElement(E.SubElement(c,Q('is')),Q('t'));t.text=text
                prior=cells.get(addr)
                if styled:c.set('s',str(style_map[int(c.get('s','0'))]))
                elif prior is not None:c.set('s',prior.get('s','0'))
                else:
                    # New glossary rows inherit the owner's previous row style.
                    letters=''.join(ch for ch in addr if ch.isalpha());number=int(addr[len(letters):])
                    model=cells.get(f'{letters}{number-1}')
                    if model is None:model=next(iter(cells.values()),None)
                    c.set('s',model.get('s','0') if model is not None else '0')
                number=int(''.join(ch for ch in addr if ch.isdigit()))
                row=rows_by_number.get(number)
                if row is None:
                    row=E.SubElement(data,Q('row'),{'r':str(number)});rows_by_number[number]=row
                if prior is not None:row.remove(prior)
                row.append(c);cells[addr]=c
                if styled:
                    authored_row=authored_rows.get(number)
                    if authored_row is not None:
                        for key in ['ht','customHeight']:
                            if key in authored_row.attrib:row.set(key,authored_row.get(key))
            # Spreadsheet rows/cells must be ordered for interoperable readers.
            def order(addr):
                n=0
                for ch in addr:
                    if ch.isalpha():n=n*26+ord(ch)-64
                return n
            for row in data:row[:]=sorted(list(row),key=lambda c:order(c.get('r')))
            data[:]=sorted(list(data),key=lambda r:int(r.get('r')))
            for number,height in plan.get('row_edits',{}).get(sn,{}).items():
                row=rows_by_number.get(int(number))
                if row is not None:row.set('ht',str(height));row.set('customHeight','1')
            dimension=root.find(Q('dimension'))
            if dimension is not None:
                if styled and authored.find(Q('dimension')) is not None:dimension.set('ref',authored.find(Q('dimension')).get('ref'))
                elif sn in plan['added_glossary_rows']:dimension.set('ref',f'A1:{"E" if len(plan["added_glossary_rows"][sn][0])==5 else "F"}{114+len(plan["added_glossary_rows"][sn])}')
                elif sn=='Definitions':dimension.set('ref','A1:F8')
                elif sn=='Publications':dimension.set('ref','A1:P3')
                elif sn=='Screens':dimension.set('ref','A1:AM13')
            # Excel expects worksheet elements in the schema's order even when
            # more tolerant readers accept a misplaced cols/sheetViews element.
            sequence=['sheetPr','dimension','sheetViews','sheetFormatPr','cols','sheetData','sheetCalcPr','sheetProtection',
                'protectedRanges','scenarios','autoFilter','sortState','dataConsolidate','customSheetViews','mergeCells',
                'phoneticPr','conditionalFormatting','dataValidations','hyperlinks','printOptions','pageMargins',
                'pageSetup','headerFooter','rowBreaks','colBreaks','customProperties','cellWatches','ignoredErrors',
                'smartTags','drawing','legacyDrawing','legacyDrawingHF','picture','oleObjects','controls',
                'webPublishItems','tableParts','extLst']
            ranks={Q(tag):i for i,tag in enumerate(sequence)}
            root[:]=sorted(list(root),key=lambda node:ranks.get(node.tag,len(ranks)))
            parts[part]=E.tostring(root,encoding='utf-8',xml_declaration=True)
        parts['xl/workbook.xml']=E.tostring(book,encoding='utf-8',xml_declaration=True)
        for name in list(parts):
            if name.startswith('xl/tables/') and name.endswith('.xml'):
                table=E.fromstring(parts[name]);tab_name=table.get('name')
                if not plan['added_glossary_rows']:continue
                if tab_name=='DefinitionsTable':ref='A1:F8'
                elif tab_name in {'ScientificGlossaryV4','PipelineGlossaryV4'}:ref='A1:F116'
                elif tab_name in {'SourceGlossaryV4','TechnicalGlossaryV4'}:ref='A1:E116'
                else:continue
                table.set('ref',ref)
                if table.find(Q('autoFilter')) is not None:table.find(Q('autoFilter')).set('ref',ref)
                parts[name]=E.tostring(table,encoding='utf-8',xml_declaration=True)
        with zipfile.ZipFile(destination,'x',zipfile.ZIP_DEFLATED) as out:
            for name,value in parts.items():out.writestr(name,value)
    print(destination)


if __name__=='__main__':main()
