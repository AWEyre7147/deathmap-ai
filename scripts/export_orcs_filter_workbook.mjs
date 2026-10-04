/** Populate the selected entity workbook from canonical projection JSON.
 * Existing nonempty cells and formulas are never replaced. Native data are
 * written as literal values; reviewer fields are distinct, rightmost columns.
 * This command reads local files only and emits an archived result for verification.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const dep=process.env.ARTIFACT_NODE_MODULES;
if(!dep) throw new Error('Set ARTIFACT_NODE_MODULES to the bundled node_modules directory');
const require=createRequire(path.join(dep,'resolver.cjs'));
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const run=path.resolve(process.argv[2]);
const projection=JSON.parse(await fs.readFile(path.join(run,'projection.json'),'utf8'));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(run,'workbook-original.xlsx')));
console.log((await wb.inspect({kind:'sheet',include:'id,name',maxChars:1600})).ndjson);
const enriched=projection.version.startsWith('orcs-publication-enrichment-v1.');
const revised=Boolean(projection.id_migration);
const changes=new Map((projection.approved_changes??[]).map(x=>[JSON.stringify([x.sheet,x.id,x.field]),x]));
const appends=new Map((projection.approved_appends??[]).map(x=>[JSON.stringify([x.sheet,x.id,x.field]),x]));
function col(n){let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
const literal=v=>typeof v==='string'&&v.startsWith('=')?"'"+v:v;
for(const [name,rows] of Object.entries(projection.sheets)){
  if(!rows.length)continue;
  const sheet=wb.worksheets.getItem(name),headers=[...projection.headers[name]];
  if(revised&&name==='Publications'){
    // Shift complete source columns right, in reverse order to avoid overlap.
    // This preserves reviewer values, formulas and styles beside the new field.
    const inserted=headers.indexOf('evidence_id_link');
    const originalHeaders=sheet.getRange(`A1:${col(headers.length-1)}1`).values[0];
    if(!originalHeaders.includes('evidence_id_link')){
      for(let c=headers.length-2;c>=inserted;c--)sheet.getRange(`${col(c+1)}1:${col(c+1)}${rows.length+1}`).copyFrom(sheet.getRange(`${col(c)}1:${col(c)}${rows.length+1}`),'all');
      sheet.getRange(`${col(inserted)}1:${col(inserted)}${rows.length+1}`).clear({applyTo:'contents'});
    }
  }
  if(name==='Screens'||(enriched&&name==='Publications'))for(const h of ['reviewer_decision','reviewer_notes'])if(!headers.includes(h))headers.push(h);
  // Existing rows retain their original cells. Projection merge has already
  // reconciled stable keys and preserved any reviewer changes or formulas.
  const old=sheet.getRange(`A1:${col(headers.length-1)}${rows.length+1}`).values;
  const formulas=sheet.getRange(`A1:${col(headers.length-1)}${rows.length+1}`).formulas;
  // New header columns may already be listed in the enriched projection. Write
  // only absent headers, preserving exact historical spelling and order.
  for(let c=0;c<headers.length;c++)if(old[0]?.[c]==null)sheet.getRange(`${col(c)}1`).values=[[headers[c]]];
  for(let c=projection.headers[name].length;c<headers.length;c++)sheet.getRange(`${col(c)}1`).values=[[headers[c]]];
  for(let c=0;c<headers.length;c++){
    const values=rows.map(row=>[headers[c]==='retrieved_at' && row[headers[c]] ? new Date(row[headers[c]]) : literal(row[headers[c]]??null)]);
    // Preserve formula cells by leaving their entire column writes fragmented
    // around nonempty cells; only newly appended or blank cells are populated.
    let start=null,block=[];
    const flush=()=>{if(block.length){sheet.getRange(`${col(c)}${start+2}:${col(c)}${start+1+block.length}`).values=block;block=[];start=null;}};
    for(let i=0;i<rows.length;i++){
      const append=appends.get(JSON.stringify([name,rows[i][headers[0]],headers[c]]));
      const change=changes.get(JSON.stringify([name,rows[i][headers[0]],headers[c]]));
      if(formulas[i+1]?.[c]){
        flush();
        if(change){
          if(formulas[i+1][c]!==change.retained)throw new Error('Formula migration baseline differs');
          sheet.getRange(`${col(c)}${i+2}`).formulas=[[rows[i][headers[c]]]];
        }
        continue;
      }
      if(old[i+1]?.[c]!=null&&old[i+1]?.[c]!==''){
        const approved=change??append;
        if(!approved){flush();continue;}
        if(old[i+1][c]!==approved.retained||rows[i][headers[c]]!==approved.value)throw new Error('Change baseline differs');
      }
      if(start===null)start=i;block.push(values[i]);
    }flush();
  }
  // The owner selected a header-only template whose default widths clip every
  // long header. Fit the populated view while retaining fonts, fills and headers.
  const last=col(headers.length-1),range=sheet.getRange(`A1:${last}${rows.length+1}`);
  range.format.verticalAlignment='top';range.format.wrapText=true;
  for(let c=0;c<headers.length;c++){
    const h=headers[c];let width=24;
    if(/notes|summary/.test(h))width=90;
    else if(/locator/.test(h))width=58;
    else if(/id$|ids$|link$|url$/.test(h))width=36;
    if(enriched&&name==='Publications'){
      if(h==='title_original')width=64;
      if(h==='author_list_ reported')width=80;
      if(h==='retrival_sources')width=60;
      if(h==='publication_notes')width=220;
    }
    if(enriched&&name==='Sources & Evidence'&&h==='evidence_text_summary')width=220;
    sheet.getRange(`${col(c)}1:${col(c)}${rows.length+1}`).format.columnWidth=width;
  }
  sheet.getRange(`A1:${last}1`).format.rowHeight=45;
  sheet.getRange(`A2:${last}${rows.length+1}`).format.autofitRows();
  if(name==='Sources & Evidence'&&!enriched)sheet.getRange(`E2:E${rows.length+1}`).setNumberFormat('yyyy-mm-dd hh:mm:ss.000');
  if(name==='Sources & Evidence'&&enriched){
    const oldDates=sheet.getRange(`E2:E${rows.length+1}`).values;
    for(let i=0;i<rows.length;i++)if(oldDates[i]?.[0]!=null&&sheet.getRange(`E${i+2}`).values[0][0] instanceof Date)sheet.getRange(`E${i+2}`).setNumberFormat('yyyy-mm-dd hh:mm:ss.000');
  }
  sheet.freezePanes.freezeRows(1);
  if(name==='Screens'||(enriched&&name==='Publications')){
    const start=headers.indexOf('reviewer_decision');
    sheet.getRange(`${col(start)}1:${last}${rows.length+1}`).format.fill='#FFF2CC';
    for(let i=0;i<rows.length;i++)if((name==='Screens'?projection.roles[rows[i].screen_id]:projection.publication_review[rows[i].publication_id])&&!rows[i].reviewer_decision)
      sheet.getRange(`${col(start)}${i+2}:${last}${i+2}`).format.fill='#F4B183';
  }
}
wb.recalculate();
const checks={errors:(await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1500})).ndjson};
await fs.writeFile(path.join(run,'artifact-checks.json'),JSON.stringify(checks,null,2));
await fs.mkdir(path.join(run,'verification-previews'),{recursive:true});
for(const [sheetName,range,file] of [['Publications','A1:C5','publications'],['Screens','A1:E5','screens'],['Screens','AJ1:AN4','review'],['Sources & Evidence','A1:E4','evidence'],['Discovery Resources','A1:D3','resources']]){
 const blob=await wb.render({sheetName,range,scale:1.3});
 await fs.writeFile(path.join(run,'verification-previews',file+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
if(enriched){
 const ranges=[['Publications','D1:H5','bibliography'],['Publications',revised?'O92:R94':'N92:Q94','publication-review'],['Sources & Evidence','H2350:M2353','publication-evidence']];
 if(revised)ranges.push(['Publications','M1:O4','evidence-links'],['Screens','M1:P4','gene-counts']);
 for(const [sheetName,range,file] of ranges){
  const blob=await wb.render({sheetName,range,scale:1});
  await fs.writeFile(path.join(run,'verification-previews',file+'.png'),new Uint8Array(await blob.arrayBuffer()));
 }
 for(const sheetName of ['Publications','Screens','Sources & Evidence'])checks[sheetName]=(await wb.inspect({kind:'table',range:`'${sheetName}'!A1:H4`,include:'values,formulas',tableMaxRows:4,tableMaxCols:8,maxChars:1600})).ndjson;
 await fs.writeFile(path.join(run,'artifact-checks.json'),JSON.stringify(checks,null,2));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(run,'DeathMap-AI-v1-reference-output.xlsx'));
console.log(JSON.stringify({exported:true,counts:projection.proposed_counts,checks}));
