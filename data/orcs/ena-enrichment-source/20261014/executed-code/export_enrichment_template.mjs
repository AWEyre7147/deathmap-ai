/** Populate a registered metadata template from completed canonical source rows.
 * Exact headers, source keys and template hash are validated before export.
 * No retrieval, scientific adjudication, source modification or cell truncation.
 * A new output workbook is required; owner templates remain byte-for-byte intact.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const [databasePath, templatePath, target] = process.argv.slice(2);
if (!databasePath || !templatePath || !target) throw Error('Usage: node export_enrichment_template.mjs DATABASE TEMPLATE NEW_OUTPUT');
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const registration = JSON.parse(await fs.readFile(templatePath.replace(/\.xlsx$/i, '.manifest.json'), 'utf8'));
if (hash(await fs.readFile(templatePath)) !== registration.sha256) throw Error('Registered template hash mismatch');
try { await fs.access(target); throw Error('Existing export refused'); } catch (error) { if (error.code !== 'ENOENT') throw error; }
const database = JSON.parse(await fs.readFile(databasePath, 'utf8'));
if (!['complete', 'complete_with_issues', 'complete_with_omissions'].includes(database.status)) throw Error('Metadata retrieval is unfinished');
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(templatePath));
const sheets = [];
const numeric = new Set(['Samples in report', 'Experiments in report', 'Runs in report', 'Read count', 'Base count', 'File position', 'Size (bytes)']);
for (const spec of registration.sheets) {
  const sheet = workbook.worksheets.getItem(spec.name);
  const headers = sheet.getRangeByIndexes(0, 0, 1, spec.headers.length).values[0];
  if (JSON.stringify(headers) !== JSON.stringify(spec.headers)) throw Error('Template header mismatch: ' + spec.name);
  const rows = database.rows[spec.source_table];
  if (!rows || rows.length > 1048575) throw Error('Missing or oversized projected sheet: ' + spec.name);
  const values = rows.map(row => spec.columns.map(c => row[c.source_key] ?? null));
  for (const row of values) for (const value of row) {
    if (typeof value === 'string' && value.length > 32767) throw Error('Excel text limit exceeded; preserved JSON remains authoritative: ' + spec.name);
  }
  if (values.length) {
    const range = sheet.getRangeByIndexes(1, 0, values.length, headers.length);
    // Literal source text cannot execute spreadsheet formulas. Identifiers and
    // variable-precision publication dates remain text; true counts are numeric.
    for (let c = 0; c < headers.length; c++) {
      sheet.getRangeByIndexes(1, c, values.length, 1).setNumberFormat(numeric.has(headers[c]) ? '#,##0' : '@');
    }
    for (let start = 0; start < values.length; start += 1000) {
      const block = values.slice(start, start + 1000).map(row => row.map(value => typeof value === 'string' && value.startsWith('=') ? "'" + value : value));
      sheet.getRangeByIndexes(start + 1, 0, block.length, headers.length).values = block;
    }
    range.format.font = { name: 'Carlito', size: 11, bold: false, color: '#000000' };
    range.format.verticalAlignment = 'top';
    range.format.wrapText = true;
    for (let r = 0; r < values.length; r++) {
      const lines = Math.max(...values[r].map((value, c) => String(value ?? '').split('\n').reduce((n, s) => n + Math.max(1, Math.ceil(s.length / ((spec.columns[c].width || 22) * 0.9))), 0)));
      sheet.getRangeByIndexes(r + 1, 0, 1, headers.length).format.rowHeight = Math.max(30, Math.min(409, lines * 16 + 6));
    }
  }
  sheets.push({ name: spec.name, rows: values.length, columns: headers.length });
  console.log(JSON.stringify(sheets.at(-1)));
}
workbook.recalculate();
const folder = path.dirname(target);
const inspection = await workbook.inspect({ kind: 'table', range: 'Studies!A1:F4', include: 'values,formulas', tableMaxRows: 4, tableMaxCols: 6, maxChars: 1500 });
await fs.writeFile(path.join(folder, 'workbook-inspection.ndjson'), inspection.ndjson);
await fs.mkdir(path.join(folder, 'workbook-previews'), { recursive: true });
for (const spec of registration.sheets) {
  const image = await workbook.render({ sheetName: spec.name, range: 'A1:F4', scale: 1, format: 'png' });
  await fs.writeFile(path.join(folder, 'workbook-previews', spec.name + '.png'), new Uint8Array(await image.arrayBuffer()));
}
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(target);
if (hash(await fs.readFile(templatePath)) !== registration.sha256) throw Error('Template changed during export');
await fs.writeFile(path.join(folder, 'workbook-receipt.json'), JSON.stringify({ template_sha256: registration.sha256,
  workbook_sha256: hash(await fs.readFile(target)), sheets, projected_cells: sheets.reduce((n, s) => n + s.rows * s.columns, 0),
  exporter_sha256: hash(await fs.readFile(new URL(import.meta.url))) }, null, 2));
console.log(JSON.stringify({ workbook: target, sheets: sheets.length }));
