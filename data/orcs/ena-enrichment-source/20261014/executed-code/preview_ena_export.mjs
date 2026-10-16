/** Render small, value/style-matched excerpts read from the saved workbook.
 * This avoids loading 600,000 cells into the spreadsheet engine for preview.
 * No XLSX is authored or changed by this visual check.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook } from '@oai/artifact-tool';
const folder = process.argv[2];
const samples = JSON.parse(await fs.readFile(path.join(folder, 'exported-preview-data.json'), 'utf8'));
const book = Workbook.create();
for (const sample of samples) {
  const sheet = book.worksheets.add(sample.name);
  const range = sheet.getRangeByIndexes(0, 0, sample.values.length, sample.widths.length);
  range.values = sample.values;
  range.format.font = { name: 'Carlito', size: 11 };
  range.format.wrapText = false;
  range.format.rowHeight = sample.body_height;
  const header = sheet.getRangeByIndexes(0, 0, 1, sample.widths.length);
  header.format.font = { name: 'Carlito', size: 11, bold: true };
  header.format.wrapText = true;
  header.format.rowHeight = sample.header_height;
  sample.widths.forEach((width, c) => sheet.getRangeByIndexes(0, c, sample.values.length, 1).format.columnWidth = width);
}
book.recalculate();
await fs.mkdir(path.join(folder, 'exported-previews'), { recursive: true });
for (const sample of samples) {
  const image = await book.render({ sheetName: sample.name, range: 'A1:F4', scale: 1, format: 'png' });
  await fs.writeFile(path.join(folder, 'exported-previews', sample.name + '.png'), new Uint8Array(await image.arrayBuffer()));
}
console.log('Rendered exported excerpts for seven sheets.');
