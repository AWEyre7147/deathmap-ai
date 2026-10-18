"""Prepare compact review tables without changing native scientific evidence.

These imported helpers orient explicit hierarchy edges, pivot native attributes
and collect repeated entity values. They never infer dataset equivalence or
replace the saved observations that explain conflicting values.
"""
from datetime import date, datetime
import re


def publication_date(value):
    """Return literal ISO dates, preserving incomplete or free-text precision.

    Parameters
    ----------
    value : str, date or None
        Saved date, including the former MM;DD;YYYY display convention.

    Returns
    -------
    str
        YYYY-MM-DD when complete; YYYY-MM, YYYY or unchanged native text otherwise.
    """
    if isinstance(value, (date, datetime)):
        return value.strftime('%Y-%m-%d')
    value = str(value or '')
    if re.fullmatch(r'\d{2};\d{2};\d{4}', value):
        return datetime.strptime(value, '%m;%d;%Y').strftime('%Y-%m-%d')
    if re.fullmatch(r'\d{2};\d{4}', value):
        return datetime.strptime(value, '%m;%Y').strftime('%Y-%m')
    return value


def unique_entities(rows, keys):
    """Collect exact native identities, preserving all distinct field values.

    Parameters
    ----------
    rows : iterable of dict
        Source review rows. Originals remain in the evidence package.
    keys : sequence of str
        Repository/study-scoped identity fields; blank identities are rejected.

    Returns
    -------
    list of dict
        One row per identity, with distinct reported values joined by newlines.

    Raises
    ------
    ValueError
        An identity is absent; unrelated anonymous records must not be merged.
    """
    groups = {}
    for row in rows:
        identity = tuple(row.get(k) for k in keys)
        if any(v is None or v == '' for v in identity):
            raise ValueError('Missing native identity: ' + repr(identity))
        fields = groups.setdefault(identity, {})
        for key, value in row.items():
            if value is not None and value != '':
                values = fields.setdefault(key, [])
                if value not in values:
                    values.append(value)
            else:
                fields.setdefault(key, [])
    return [{k: vs[0] if len(vs) == 1 else '\n'.join(map(str, vs)) if vs else ''
             for k, vs in fields.items()} for fields in groups.values()]


def hierarchy_rows(rows, source, target, repository):
    """Orient only explicit inverse edges parent-first and deduplicate them.

    Parameters
    ----------
    rows : iterable of dict
        GEO or ENA hierarchy projection; raw relationship claims stay unchanged.
    source, target : str
        Column names for the two endpoints.
    repository : str
        GEO or ENA; unknown relationships retain their original direction.

    Returns
    -------
    list of dict
        Unique endpoint/relationship triples; context fields retain all values.
    """
    result = []
    for row in rows:
        row = dict(row)
        relation = row['Relationship']
        inverse = relation == ('SubSeries of' if repository == 'GEO' else 'Parent project')
        forward = 'SuperSeries of' if repository == 'GEO' else 'Child project'
        if inverse:
            row[source], row[target] = row[target], row[source]
            row['Relationship'] = forward
        result.append(row)
    return unique_entities(result, [source, 'Relationship', target])


def pivot_attributes(rows, identity, exclude=()):
    """Pivot exact native field names without conflating study-scoped IDs.

    Parameters
    ----------
    rows : iterable of dict
        Long-form native attributes with Field and Original value.
    identity : str
        Native protocol ID or Native section ID.
    exclude : sequence of str
        Attributes intentionally omitted from review, such as protocol Contact.

    Returns
    -------
    list of dict
        One study/identity row with distinct repeated values preserved in cells.
        Value state is omitted from review; native evidence remains unchanged.
    """
    projected = []
    for row in rows:
        field = row['Field']
        if field in exclude:
            continue
        out = {k: row[k] for k in ('Study accession', identity, 'Native section type') if k in row}
        out[field] = row.get('Original value', '')
        projected.append(out)
    return unique_entities(projected, ['Study accession', identity])
