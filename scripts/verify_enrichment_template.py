"""Check every exported ENA cell against canonical metadata and template mapping.

Read-only checks cover identifiers, complete native text, numeric counts and the
unchanged registered template. No network calls, workbook edits or rebuilds.
"""
import argparse
import hashlib
import json
from pathlib import Path
from openpyxl import load_workbook


def verify(database_path, template_path, workbook_path):
    """Verify a completed template export and save its cell-comparison receipt.

    Parameters
    ----------
    database_path, template_path, workbook_path : Path
        Canonical JSON, registered header template, and new populated workbook.

    Returns
    -------
    dict
        Counts and exact-file hashes for all checked output cells.

    Raises
    ------
    AssertionError
        A cell, header, sheet, template hash or native data type differs.
    """
    database_path, template_path, workbook_path = map(Path, (database_path, template_path, workbook_path))
    database = json.loads(database_path.read_text(encoding='utf-8'))
    manifest = json.loads(template_path.with_suffix('.manifest.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(template_path.read_bytes()).hexdigest() == manifest['sha256']
    workbook = load_workbook(workbook_path, read_only=True, data_only=False)
    assert workbook.sheetnames == [s['name'] for s in manifest['sheets']]
    checked, counts = 0, {}
    for spec in manifest['sheets']:
        sheet = workbook[spec['name']]
        rows = database['rows'][spec['source_table']]
        iterator = sheet.iter_rows()
        assert [c.value for c in next(iterator)] == spec['headers']
        assert sheet.max_row == len(rows) + 1
        for number, (actual, row) in enumerate(zip(iterator, rows), 2):
            for column, (cell, mapping) in enumerate(zip(actual, spec['columns']), 1):
                expected = row.get(mapping['source_key'])
                if expected == '':
                    expected = None
                # Inline-string blanks and absent cells both display as blank.
                # Do not conflate them with numeric zero or the text "None".
                observed = None if cell.value == '' else cell.value
                assert observed == expected, (spec['name'], number, column, str(observed)[:100], str(expected)[:100])
                assert cell.data_type != 'f', (spec['name'], number, column)
                checked += 1
        counts[spec['name']] = len(rows)
    workbook.close()
    result = {'all_projected_cells_verified': checked, 'sheet_rows': counts,
        'template_sha256': manifest['sha256'], 'workbook_sha256': hashlib.sha256(workbook_path.read_bytes()).hexdigest(),
        'database_sha256': hashlib.sha256(database_path.read_bytes()).hexdigest(), 'native_application_opening': 'not tested'}
    workbook_path.with_suffix('.verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', type=Path)
    parser.add_argument('template', type=Path)
    parser.add_argument('workbook', type=Path)
    arguments = parser.parse_args()
    print(json.dumps(verify(arguments.database, arguments.template, arguments.workbook)))
