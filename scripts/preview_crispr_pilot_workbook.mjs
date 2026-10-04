/** Read-only visual verification of a saved CRISPR pilot review workbook. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire(path.join(process.env.ARTIFACT_NODE_MODULES,'resolver.cjs'));
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const run=path.resolve(process.argv[2]);
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(run,'DeathMap-AI-output-v6.xlsx')));
const dir=path.join(run,'previews');await fs.mkdir(dir,{recursive:true});
for(const [sheet,range,label] of [['Publications','A1:F4','publications'],['Screens','H1:N4','screens'],['Screens','AM1:AO4','screen-review'],['Evidence','H1:M4','evidence-review']]){
 const b=await w.render({sheetName:sheet,range,scale:1});await fs.writeFile(path.join(dir,`${label}.png`),new Uint8Array(await b.arrayBuffer()));
}
