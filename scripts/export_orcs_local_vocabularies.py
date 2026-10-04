"""Export exact cached ORCS values for fields selected in the owner's index.

The Markdown index controls vocabulary generation independently of optional
filter eligibility. Original values are not normalized or split. Annotation
columns stay empty. Existing files are protected to avoid erasing future curation.
This local-only exporter does not modify the cache or execute discovery rules.
"""
import argparse
import json
import re
from pathlib import Path


def selections(text):
    """Read included vocabulary fields and notes from the four-column owner table."""
    result = []
    for line in text.splitlines():
        if not re.match(r'^\|\s*`[^`]+`', line):
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(cells) != 4:
            raise ValueError('Unrecognized owner selection row')
        field = cells[0].strip('`')
        if cells[1].casefold() == 'include':
            result.append((field, 'annotate' in cells[3].casefold()))
    if not result:
        raise ValueError('No included vocabulary fields found')
    return result


def escape(value):
    """Escape Markdown syntax without changing the underlying source term."""
    return (value.replace('\\', '\\\\').replace('|', '\\|')
            .replace('[', '\\[').replace(']', '\\]').replace('`', '\\`')
            .replace('\r', '&#13;').replace('\n', '<br>'))


def render(rows, fields, annotated, source_ref):
    """Render sorted exact values and separate missing-value counts for native fields.

    Score-type aggregation unions labels only; it does not merge screen entities.
    Missing counts are field occurrences rather than distinct screens for a union.
    Non-string native values fail explicitly rather than being silently coerced.
    """
    values = set()
    missing = null = empty = 0
    for row in rows:
        for field in fields:
            if field not in row:
                missing += 1
            elif row[field] is None:
                null += 1
            elif not isinstance(row[field], str):
                raise ValueError(f'Non-string value in {field}')
            elif row[field] == '':
                empty += 1
            else:
                values.add(row[field])
    label = fields[0] if len(fields) == 1 else 'SCORE.#_TYPE'
    ordered = sorted(values, key=lambda value: (value.casefold(), value))
    lines = [f'# {label}', '',
             'Native fields: ' + ', '.join(f'`{field}`' for field in fields) + '.', '',
             f'Source: [cached screen metadata]({source_ref}).', '',
             f'Screens examined: {len(rows)}. Unique nonempty values: {len(values)}.',
             f'Field occurrences absent: {missing}; null: {null}; empty string: {empty}.', '',
             'Values are exact source strings, sorted case-insensitively with an exact-text tie-break.',
             'Source placeholders are retained. Combined field values are not split.', '']
    if annotated:
        lines += ['Descriptions await a separately selected reference source.', '',
                  '| Value | Description |', '|---|---|']
        lines += [f'| {escape(value)} | |' for value in ordered]
    else:
        lines += ['| Value |', '|---|']
        lines += [f'| {escape(value)} |' for value in ordered]
    return '\n'.join(lines) + '\n'


def export(snapshot, index):
    """Create selected vocabulary files; refuse all writes if any target exists.

    Inputs are a JSON array of native screens and the owner's Markdown index.
    Returns created paths. Schema errors or existing targets leave files untouched.
    """
    rows = json.loads(snapshot.read_text(encoding='utf-8'))
    if not isinstance(rows, list) or not rows or not all(isinstance(row, dict) for row in rows):
        raise ValueError('Unrecognized or empty ORCS cache')
    known = {key for row in rows for key in row}
    planned = {}
    score_fields = []
    score_annotated = False
    source_ref = '../../../../data/orcs/screen-index.json'
    for field, annotated in selections(index.read_text(encoding='utf-8')):
        if field not in known:
            raise ValueError(f'Unknown selected field: {field}')
        if re.fullmatch(r'SCORE\.[1-5]_TYPE', field):
            score_fields.append(field)
            score_annotated |= annotated
            continue
        filename = field + '.md'
        planned[index.parent / filename] = render(rows, [field], annotated, source_ref)
    if score_fields:
        planned[index.parent / 'SCORE.#_TYPE.md'] = render(rows, score_fields, score_annotated, source_ref)
    if any(path.exists() for path in planned):
        raise FileExistsError('Vocabulary target exists; preserve annotations and review refresh separately')
    for path, content in planned.items():
        path.write_text(content, encoding='utf-8')
    return list(planned)


def main():
    """Generate the current local vocabularies from the specified repository root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    snapshot = args.root / 'data/orcs/screen-index.json'
    index = args.root / 'docs/vocabularies/orcs/local/index.md'
    paths = export(snapshot, index)
    print(f'Created {len(paths)} vocabulary files; annotations remain blank.')


if __name__ == '__main__':
    main()
