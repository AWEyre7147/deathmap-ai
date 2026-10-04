/** Revise only the evidence-related regions of the preserved owner v5 model.
 * The plan records exact cell edits. Glossary rows outside that plan are never
 * intentionally changed; preservation is verified against the original file.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire(path.join(process.env.ARTIFACT_NODE_MODULES,'resolver.cjs'));
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const plan=JSON.parse(await fs.readFile(process.argv[2],'utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(plan.input));
for(const edit of plan.edits) w.worksheets.getItem(edit.sheet).getRange(edit.cell).values=[[edit.value]];
for(const [sn,columns] of Object.entries(plan.column_edits??{}))for(const [column,width] of Object.entries(columns))w.worksheets.getItem(sn).getRange(`${column}1:${column}2`).format.columnWidth=width;
for(const [sn,rows] of Object.entries(plan.row_edits??{}))for(const [row,height] of Object.entries(rows))w.worksheets.getItem(sn).getRange(`A${row}:F${row}`).format.rowHeight=height;
const s=w.worksheets.getItem('Sources & Evidence');
s.getRange('A1:M1').values=[plan.evidence_headers];
s.getRange('A1:M1').format.rowHeight=72;
s.getRange('A1:M2').format.wrapText=true;
s.getRange('A1:M2').format.verticalAlignment='top';
for(const [col,width] of [['A',31],['B',23],['C',31],['D',64],['E',52],['F',22],['G',48],['H',70],['I',26],['J',24],['K',22],['L',22],['M',56]])s.getRange(`${col}1:${col}2`).format.columnWidth=width;
s.getRange('L2:M2').format.fill='#FFF2CC';
s.freezePanes.freezeRows(1);
for(const sn of ['Scientific Glossary','Source Glossary','Technical Glossary','Pipeline Glossary']){
 const sheet=w.worksheets.getItem(sn);
 // Extend the existing owner table for the newly documented accession field.
 const existing=sheet.tables.items[0];
 if(existing) existing.rows.add(null,plan.added_glossary_rows[sn]);
}
await fs.mkdir(plan.preview_dir,{recursive:true});
for(const [name,range,file] of [['Sources & Evidence','A1:D3','evidence-left'],['Sources & Evidence','I1:M3','evidence-review'],['Screens','AL1:AM3','screen-accession'],['Definitions','A7:C8','definitions'],['Scientific Glossary','A102:C106','glossary']]){
 const b=await w.render({sheetName:name,range,scale:1});
 await fs.writeFile(path.join(plan.preview_dir,`${file}.png`),new Uint8Array(await b.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(w)).save(plan.artifact_output);
console.log('Artifact workbook created; exact-preservation verification follows.');
