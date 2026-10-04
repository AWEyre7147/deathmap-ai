/** Read-only inspection of the starting workbook using the bundled renderer. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire(path.join(process.env.ARTIFACT_NODE_MODULES,'resolver.cjs'));
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(process.argv[2]));
console.log((await wb.inspect({kind:'sheet',include:'id,name',maxChars:2000})).ndjson);
const blob=await wb.render({sheetName:'Publications',range:'A1:F4',scale:1});
await fs.writeFile(process.argv[3],new Uint8Array(await blob.arrayBuffer()));
