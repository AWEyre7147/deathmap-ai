"""Export registered ENA rows using the existing template-preserving XML writer.

This CLI is metadata-only and portable with the project's existing dependencies.
It reuses the registration/mapping checks shared with GEO; no ENA retrieval,
screen classification or experimental-file access occurs during export.
"""
import argparse
import json
from pathlib import Path
from .geo_workbook import export_workbook as _registered_export


def export_workbook(database_path, template, output):
    """Write and verify selected ENA rows without a full spreadsheet-engine model.

    Parameters
    ----------
    database_path, template, output : Path or str
        Completed canonical ENA metadata, registered template and fresh output.

    Returns
    -------
    dict
        Template/output hashes and per-sheet counts, also saved as a receipt.

    Raises
    ------
    ValueError
        Retrieval is unfinished or registered fields/template do not match.
    FileExistsError
        An existing workbook would be overwritten.
    """
    database_path, template, output = map(Path, (database_path, template, output))
    database = json.loads(database_path.read_text(encoding='utf-8'))
    if database['status'] not in ('complete', 'complete_with_issues', 'complete_with_omissions'):
        raise ValueError('ENA retrieval is unfinished')
    result = _registered_export(template, output, database['rows'])
    result['exporter'] = 'existing-template-preserving-XML-writer'
    result['spreadsheet_engine_attempt'] = 'Memory limit reached before save; no source retrieval repeated'
    result['projected_cells'] = sum(len(rows) * len(database['rows'][name][0]) for name, rows in database['rows'].items() if rows)
    (output.parent / 'workbook-receipt.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def main():
    """Export one completed canonical ENA run into a fresh registered workbook."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', type=Path)
    parser.add_argument('template', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(export_workbook(args.database, args.template, args.output)))


if __name__ == '__main__':
    main()
