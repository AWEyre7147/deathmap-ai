"""Map native GEO metadata to the owner's indexed, three-sheet workbook.

Native GSE/GSM accessions define stable entities. Each displayed row carries one
publication association; samples can recur across series without renumbering.
The saved native metadata retains hierarchy and parent links omitted by the
simplified template. This imported helper performs no retrieval.
"""
import json
from pathlib import Path

from .enrichment_indices import assign_indices, native_key


def project(database, publication_registry=None, index_registry=None):
    """Return native-keyed tables for the registered GEO template.

    Parameters
    ----------
    database : dict
        Canonical GEO publications, series and samples with exact memberships.
    publication_registry : Path, optional
        PUB crosswalk; unnecessary when inputs carry explicit Publication Index.
    index_registry : Path, optional
        Append-only resource indices; None uses deterministic in-memory indices.

    Returns
    -------
    dict
        Series Records, Sample Metadata and Repository Identifiers tables.

    Raises
    ------
    ValueError
        Publication identities conflict or a series has an unknown membership.
    """
    from .enrichment_synthesis import project_geo
    registrations = json.loads(Path(publication_registry).read_text(encoding='utf-8')) if publication_registry else []
    identities = {}
    for field in ('ORCS Publication ID', 'PMID'):
        mapping = {}
        for entry in registrations:
            value = str(entry.get(field) or '')
            if value:
                if value in mapping:
                    raise ValueError('Ambiguous GEO publication registry')
                mapping[value] = entry['Publication index']
        identities[field] = mapping
    pubs = {}
    for key, record in database['publications'].items():
        pub = record['publication']
        matches = {v for v in (
            identities['ORCS Publication ID'].get(str(pub.get('PUBLICATION_ID') or pub.get('ORCS Publication ID') or '')),
            identities['PMID'].get(str(pub.get('PMID') or ''))) if v}
        if len(matches) > 1:
            raise ValueError('Conflicting GEO publication identities')
        index = pub.get('Publication Index') or pub.get('Publication index') or next(iter(matches), None)
        if not index or index in pubs.values():
            raise ValueError('Unique Publication Index or matching registry entry required for GEO')
        pubs[key] = index
    for record in database['series'].values():
        if not set(record.get('publication_keys', record.get('pmids', []))) <= pubs.keys():
            raise ValueError('GEO series references an unknown publication')
    # Allocate by accession, independent of cohort order and publication count.
    series = assign_indices('GESE', [native_key(k) for k in database['series']], index_registry)
    samples = assign_indices('GESA', [native_key(k) for k in database['samples']], index_registry)
    native = project_geo(database)
    result = {name: [] for name in ('Series Records', 'Sample Metadata', 'Repository Identifiers')}
    seen = set()
    for name in result:
        for row in native[name]:
            row = {**row, 'Publication Index': pubs[row['PMID']]}
            if name in ('Series Records', 'Sample Metadata'):
                row['Series Index'] = series[native_key(row['GSE'])]
            if name == 'Sample Metadata':
                row['Sample Index'] = samples[native_key(row['GSM'])]
            if name == 'Repository Identifiers':
                # The owner omitted parent GSE/GSM columns here. Collapse exact
                # visible duplicates; native canonical records preserve parents.
                identity = tuple(row.get(k) for k in ('Publication Index', 'Identifier', 'Resource', 'Entity Level', 'Native Field'))
                if identity in seen:
                    continue
                seen.add(identity)
            result[name].append(row)
    return result
