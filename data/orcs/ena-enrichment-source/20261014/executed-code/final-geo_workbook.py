"""Populate the registered owner GEO template from projected metadata tables.

No retrieval or scientific classification occurs here. Native repeated values
stay joined in the supplied projection; evidence remains in saved JSON/native
responses and is deliberately absent from this repository-specific workbook.
"""
import hashlib
import json
from pathlib import Path

import openpyxl

from .pubmed_workbook import export_workbook as _write_template


def export_workbook(template, output, tables, manifest=None):
    """Fill a hash-registered GEO template using its explicit column mapping.

    Parameters
    ----------
    template : Path or str
        Owner-approved header-only GEO workbook; its bytes are never changed.
    output : Path or str
        Fresh workbook destination; an existing file is refused.
    tables : dict
        Sheet names mapped to lists of projected record dictionaries, such as
        Series Records and Sample Metadata. Unmapped fields stay in source JSON.
    manifest : Path or str, optional
        Registration JSON; defaults to template.with_suffix('.manifest.json').

    Returns
    -------
    dict
        Template hash, output hash and per-sheet row counts for a run receipt.

    Raises
    ------
    ValueError
        Template hash, sheets or headers differ from the accepted manifest,
        mapped tables are missing, or text exceeds Excel's 32767-character limit.
    FileExistsError
        Output already exists.

    Notes
    -----
    Missing source fields become blank cells. It never guesses a native citation
    from an originating PMID or promotes dataset association into screen evidence.
    The existing XML-preserving writer retains owner headers and sheet settings,
    then independently reopens the output and compares every projected value.
    """
    template = Path(template)
    registration = json.loads(Path(manifest or template.with_suffix('.manifest.json')).read_text(encoding='utf-8'))
    digest = hashlib.sha256(template.read_bytes()).hexdigest()
    if digest != registration['sha256']:
        raise ValueError('GEO template changed; register the edited template before export')
    sheets = registration['sheets']
    book = openpyxl.load_workbook(template, read_only=True)
    try:
        if book.sheetnames != [sheet['name'] for sheet in sheets]:
            raise ValueError('GEO template sheets differ from the manifest')
        for sheet in sheets:
            if list(next(book[sheet['name']].values)) != sheet['headers']:
                raise ValueError('GEO template headers differ from the manifest')
    finally:
        book.close()
    rows = {}
    for sheet in sheets:
        name = sheet['name']
        source_table = sheet['source_table']
        if source_table not in tables:
            raise ValueError('Missing projected table: ' + source_table)
        rows[name] = []
        for record in tables[source_table]:
            values = []
            for column in sheet['columns']:
                value = record.get(column['source_key'])
                if value is None:
                    value = ''
                if isinstance(value, str) and len(value) > 32767:
                    raise ValueError('Excel cell limit exceeded; source metadata remains intact')
                values.append(value)
            rows[name].append(values)
    _write_template(template, output, rows)
    return {'template_sha256': digest,
            'workbook_sha256': hashlib.sha256(Path(output).read_bytes()).hexdigest(),
            'sheet_rows': {name: len(values) for name, values in rows.items()}}
