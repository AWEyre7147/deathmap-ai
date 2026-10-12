/** Populate the final owner template from canonical ArrayExpress projected rows.
 * This is an export only: no retrieval, scientific adjudication or data truncation.
 * The registered template is imported and remains unchanged on disk.
 */
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const base='C:/Users/aweyr/Documents/Repositories/deathmap-ai';
const output=base+'/outputs/arrayexpress-orcs-20261011-S-network';
const target=output+'/BioStudies-ArrayExpress-Enrichment.xlsx';
const template=base+'/data/templates/BioStudies-ArrayExpress-Enrichment.xlsx';
const registration=JSON.parse(await fs.readFile(template.replace('.xlsx','.manifest.json'),'utf8'));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
if(hash(await fs.readFile(template))!==registration.sha256)throw Error('Registered template hash mismatch');
try{await fs.access(target);throw Error('Existing export refused');}catch(e){if(e.code!=='ENOENT')throw e;}
const database=JSON.parse(await fs.readFile(output+'/database.json','utf8'));
if(!['complete','complete_with_issues'].includes(database.status))throw Error('Retrieval has not finished');
const book=await SpreadsheetFile.importXlsx(await FileBlob.load(template));
let cellCount=0;
for(const t of registration.sheets){
 const sheet=book.worksheets.getItem(t.name);
 const headers=sheet.getRangeByIndexes(0,0,1,t.headers.length).values[0];
 if(JSON.stringify(headers)!==JSON.stringify(t.headers))throw Error('Header mismatch: '+t.name);
 const rows=database.rows[t.source_table];
 if(!rows||rows.length>1048575)throw Error('Missing/oversized projection: '+t.name);
 const values=rows.map(row=>t.columns.map(c=>row[c.source_key]??null));
 for(const row of values)for(const value of row){
  if(typeof value==='string'&&value.length>32767)throw Error('Excel cell text limit: '+t.name);
 }
 if(values.length){
  const range=sheet.getRangeByIndexes(1,0,values.length,t.headers.length);
  const numeric=new Set(['Samples reported','Assays reported','Size (bytes)','Native data row','Native column','Native line','Part']);
  // Metadata dates/identifiers in Original value are literal source text, not
  // dates to reinterpret. Counts and native row/column indices remain numeric.
  for(let c=0;c<t.headers.length;c++)if(!numeric.has(t.headers[c]))sheet.getRangeByIndexes(1,c,values.length,1).setNumberFormat('@');
  range.values=values;
  range.format.font={name:'Carlito',size:11,bold:false};
  // Follow the owner's plain, uniform-width template; full strings remain in
  // cells and canonical JSON even when a narrow display column shows a prefix.
  range.format.verticalAlignment='top';
  range.format.wrapText=false;
 }
 cellCount+=values.length*t.headers.length;
 console.log(JSON.stringify({sheet:t.name,rows:values.length}));
}
book.recalculate();
console.log((await book.inspect({kind:'table',range:'Studies!A1:G5',include:'values',tableMaxRows:5,tableMaxCols:7,maxChars:1500})).ndjson);
console.log((await book.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:20},maxChars:500})).ndjson);
for(const t of registration.sheets){
 const preview=await book.render({sheetName:t.name,range:'A1:F5',scale:1,format:'png'});
 await fs.writeFile(output+'/'+t.name.replace(/ /g,'-')+'-preview.png',new Uint8Array(await preview.arrayBuffer()));
}
const file=await SpreadsheetFile.exportXlsx(book);await file.save(target);
if(hash(await fs.readFile(template))!==registration.sha256)throw Error('Template changed during export');
await fs.writeFile(output+'/workbook-receipt.json',JSON.stringify({template_sha256:registration.sha256,
 workbook_sha256:hash(await fs.readFile(target)),projected_cells:cellCount,
 sheet_rows:Object.fromEntries(registration.sheets.map(t=>[t.name,database.rows[t.source_table].length]))},null,2));
console.log(JSON.stringify({workbook:target,projected_cells:cellCount}));
