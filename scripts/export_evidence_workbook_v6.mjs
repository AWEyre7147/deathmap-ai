/** Populate a new v6 review workbook from canonical entity/evidence JSON.
 * Fixed reference/Sources sheets are copied, not written. An OOXML preservation
 * pass restores parts the artifact importer otherwise restyles. This accepts
 * only v6 projections prepared for v02 onward; no search or retrieval occurs.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const require=createRequire(path.join(process.env.ARTIFACT_NODE_MODULES,'resolver.cjs'));
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const run=path.resolve(process.argv[2]);
const finishLayout=process.argv[3]==='--finish-layout';
const template=path.resolve('data/templates/DeathMap-AI-output-v6.xlsx');
const p=JSON.parse(await fs.readFile(path.join(run,'projection.json'),'utf8'));
if(p.template_version!=='v6')throw new Error('Expected v6 projection');
const destination=path.join(run,finishLayout?'workbook-layout-verified.xlsx':'DeathMap-AI-output-v6.xlsx');
try{await fs.access(destination);throw new Error('Refusing to overwrite output');}catch(e){if(e.code!=='ENOENT')throw e;}
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(finishLayout?path.join(run,'workbook-authored.xlsx'):template));
const plan=finishLayout?JSON.parse(await fs.readFile(path.join(run,'workbook-preservation-plan.json'),'utf8')):
  {input:template,artifact_output:path.join(run,'workbook-authored.xlsx'),destination,edits:[],styled_sheets:[],added_glossary_rows:{}};
if(finishLayout){plan.destination=destination;plan.artifact_output=path.join(run,'workbook-layout-authored.xlsx');}
const col=n=>{let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const allowed=new Set(['Publications','Screen Groups','Screens','Datasets','Screen-Dataset Links','Evidence']);
for(const [name,rows] of Object.entries(p.sheets)){
 if(!allowed.has(name))throw new Error(`Unexpected writable sheet: ${name}`);
 if(!rows.length)continue;
 const sheet=w.worksheets.getItem(name);
 const headers=sheet.getRange('A1:AZ1').values[0].filter(x=>x!=null&&x!=='');
 if(finishLayout){
  // Finalize only display dimensions and explicit unresolved-reference flags.
  // Reuse the authored workbook to avoid repeating thousands of link writes.
  if(name==='Publications'||name==='Screens')sheet.getRange(`A2:${col(headers.length-1)}${rows.length+1}`).format.rowHeight=name==='Screens'?96:108;
  if(name==='Screens')for(let i=0;i<rows.length;i++)if(rows[i].curation_status?.includes('unresolved reference accession')){
   for(const field of ['curation_status','screen_notes'])sheet.getRange(`${col(headers.indexOf(field))}${i+2}`).values=[[rows[i][field]]];
   for(const field of ['reviewer_decision','reviewer_notes'])sheet.getRange(`${col(headers.indexOf(field))}${i+2}`).format.fill='#F4B183';
  }
  continue;
 }
 for(const field of ['reviewer_decision','reviewer_notes'])if(rows.some(r=>field in r)&&!headers.includes(field))headers.push(field);
 const matrix=[headers,...rows.map(r=>headers.map(h=>{const v=r[h]??null;return typeof v==='string'&&v.startsWith('=')?`'${v}`:v;}))];
 for(const r of rows)for(const [key,value] of Object.entries(r))if(value!=null&&value!==''&&!headers.includes(key))throw new Error(`Unmapped populated column: ${name}/${key}`);
 const last=col(headers.length-1),range=sheet.getRange(`A1:${last}${matrix.length}`);
 range.values=matrix;range.format.wrapText=true;range.format.verticalAlignment='top';
 sheet.getRange(`A1:${last}1`).format.rowHeight=72;
 for(let c=0;c<headers.length;c++){
  const h=headers[c];let width=/claim|supporting_value$|notes|note$/.test(h)?64:/fields_supported|link|url/.test(h)?48:28;
  sheet.getRange(`${col(c)}1:${col(c)}${matrix.length}`).format.columnWidth=width;
  if(h==='source_link'){
   for(let i=0;i<rows.length;i++){
    const url=rows[i][h];if(url==null||url==='')continue;
    if(!/^https?:\/\//.test(url))throw new Error('Source link must be an HTTP(S) native URL');
    const escaped=url.replaceAll('"','""');
    sheet.getRange(`${col(c)}${i+2}`).formulas=[[`=HYPERLINK("${escaped}","${escaped}")`]];
   }
   sheet.getRange(`${col(c)}2:${col(c)}${matrix.length}`).format.font={color:'#0563C1'};
  }
  if(h.startsWith('reviewer_')){
   sheet.getRange(`${col(c)}2:${col(c)}${matrix.length}`).format.fill='#FFF2CC';
   for(let i=0;i<rows.length;i++)if(['conflicting','unresolved'].includes(rows[i].evidence_status)||/unresolved|conflict/.test(rows[i].curation_status??''))sheet.getRange(`${col(c)}${i+2}`).format.fill='#F4B183';
  }
 }
 if(name==='Evidence')sheet.getRange(`A2:${last}${matrix.length}`).format.rowHeight=110;
 if(name==='Screens')sheet.getRange(`A2:${last}${matrix.length}`).format.rowHeight=96;
 if(name==='Publications')sheet.getRange(`A2:${last}${matrix.length}`).format.rowHeight=108;
 sheet.freezePanes.freezeRows(1);
 plan.styled_sheets.push(name);
 for(let r=0;r<matrix.length;r++)for(let c=0;c<headers.length;c++)plan.edits.push({sheet:name,cell:`${col(c)}${r+1}`,value:matrix[r][c]});
}
await (await SpreadsheetFile.exportXlsx(w)).save(plan.artifact_output);
const planPath=path.join(run,'workbook-preservation-plan.json');await fs.writeFile(planPath,JSON.stringify(plan));
if(!process.env.BUNDLED_PYTHON)throw new Error('Set BUNDLED_PYTHON to the bundled Python executable');
const result=spawnSync(process.env.BUNDLED_PYTHON,['scripts/preserve_evidence_template_v6.py',planPath],{encoding:'utf8'});
if(result.status!==0)throw new Error(result.stderr||result.stdout);
const blob=await w.render({sheetName:'Evidence',range:'A1:D4',scale:1});
await fs.writeFile(path.join(run,'evidence-preview.png'),new Uint8Array(await blob.arrayBuffer()));
console.log(destination);
