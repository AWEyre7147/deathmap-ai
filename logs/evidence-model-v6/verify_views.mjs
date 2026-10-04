/** Read-only visual checks of the saved, preservation-verified template. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire(path.join(process.env.ARTIFACT_NODE_MODULES,'resolver.cjs'));
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const w=await SpreadsheetFile.importXlsx(await FileBlob.load('data/templates/DeathMap-AI-output-v6.xlsx'));
for(const [sn,range,label] of [['Evidence','I1:M3','saved-review'],['Screens','AL1:AM3','saved-accession'],['Publications','O1:P3','saved-publication-link'],['Definitions','A7:C8','saved-definitions'],...['Scientific Glossary','Source Glossary','Technical Glossary','Pipeline Glossary'].map((s,i)=>[s,'A115:C116',`saved-glossary-${i}`])]){
 const b=await w.render({sheetName:sn,range,scale:1});await fs.writeFile(`logs/evidence-model-v6/previews/${label}.png`,new Uint8Array(await b.arrayBuffer()));
}
