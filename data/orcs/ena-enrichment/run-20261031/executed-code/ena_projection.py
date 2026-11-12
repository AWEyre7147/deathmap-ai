"""Project canonical ENA metadata into the seven owner-selected template tables.

Exact native child-record duplicates are merged across overlapping study reports,
while differing source values remain separate rows. Study associations preserve
native publication observations outside the selected study table. Missing evidence is blank; no screen classification
or repository hierarchy traversal is introduced by this workbook projection.
"""
from __future__ import annotations
import json
from itertools import zip_longest
from .review_projection import hierarchy_rows, publication_date


def _join(values):
    return '\n'.join(sorted({str(v) for v in values if v is not None and v != ''}))


def _number(value):
    return int(value) if value not in (None, '') else None


def project(database):
    """Return source-keyed rows matching the registered ENA template mappings.

    Parameters
    ----------
    database : dict
        Canonical publications, studies, association observations and run reports.

    Returns
    -------
    dict
        Seven sheet-name keys containing projected record dictionaries.

    Notes
    -----
    Duplicate run records share reporting-study sets; conflicting metadata remains
    in additional rows. File arrays are aligned by position, with absent checksum
    or size preserved as missing and recorded as a projection issue.
    """
    sheets = {name: [] for name in ('Studies', 'Publications', 'Study hierarchy', 'Samples', 'Experiments', 'Runs', 'File listings')}
    records = {}
    for accession, study in sorted(database['studies'].items()):
        sheets['Studies'].append({'Study accession': accession,
            'SRA study accession': _join(x for x in study['aliases'] if x.startswith(('SRP', 'ERP', 'DRP'))),
            'Study title': study['title'], 'Organism': _join(study['organism']),
            'Samples in report': study.get('sample_count'), 'Experiments in report': study.get('experiment_count'),
            'Runs in report': study.get('run_count'), 'Study description': study['description']})
        for relation in study['hierarchy']:
            sheets['Study hierarchy'].append({'Study accession': accession, 'Relationship': relation['relationship'], 'Related study accession': relation['accession']})
        for index, row in enumerate(study['runs']):
            identity = json.dumps(row, sort_keys=True)
            record = records.setdefault(identity, {'native': row, 'reporting_studies': set(), 'source_locators': []})
            record['reporting_studies'].add(accession)
            record['source_locators'].append({'study': accession, 'response': study.get('run_report_response'), 'row': index})
    # Keep the many reporting-study memberships in canonical evidence even though
    # the owner excluded the separate membership sheet from the workbook.
    database['native_run_records'] = [dict(x, reporting_studies=sorted(x['reporting_studies'])) for x in records.values()]
    for pub in database['publications']:
        p = pub['publication']
        found = any(any(a['publication_key'] == pub['key'] for a in s['associations']) for s in database['studies'].values())
        status = 'Candidates retrieved' if found else 'Candidates unresolved' if pub['observations'] else 'No candidates retrieved'
        if pub['issues']:
            status += '; discovery incomplete'
        sheets['Publications'].append({'PMID': p.get('PMID'), 'DOI': p.get('DOI'), 'PMCID': p.get('PMCID'),
            'Publication title': p['TITLE'], 'Authors': p.get('AUTHORS'), 'Journal': p.get('JOURNAL'),
            'Publication date': publication_date(p.get('PUBLICATION_DATE')), 'Retrieval result': status})
    samples, experiments = {}, {}
    sample_keys = ['sample_accession', 'sample_title', 'sample_description', 'scientific_name']
    experiment_keys = ['experiment_accession', 'experiment_title', 'sample_accession', 'library_strategy', 'library_source',
        'library_selection', 'library_layout', 'instrument_platform', 'instrument_model', 'library_construction_protocol']
    sample_headers = ['Sample accession', 'Sample title', 'Sample description', 'Organism']
    experiment_headers = ['Experiment accession', 'Experiment title', 'Sample accession', 'Library strategy', 'Library source',
        'Library selection', 'Library layout', 'Instrument platform', 'Instrument model', 'Library construction protocol']
    for record in records.values():
        row = record['native']
        for store, keys in ((samples, sample_keys), (experiments, experiment_keys)):
            identity = tuple(row.get(k, '') for k in keys)
            entry = store.setdefault(identity, {'studies': set(), 'runs': set()})
            entry['studies'].update(record['reporting_studies'])
            entry['runs'].add(row['run_accession'])
        sheets['Runs'].append({'Run accession': row['run_accession'], 'Native study accession': row['study_accession'],
            'SRA study accession': row['secondary_study_accession'], 'Sample accession': row['sample_accession'],
            'Experiment accession': row['experiment_accession'], 'Read count': _number(row.get('read_count')),
            'Base count': _number(row.get('base_count')), 'Reporting studies': _join(record['reporting_studies'])})
        arrays = [row.get(k, '').split(';') if row.get(k) else [] for k in ('fastq_ftp', 'fastq_md5', 'fastq_bytes')]
        if len({len(x) for x in arrays}) > 1:
            database['issues'].append({'stage': 'file-projection', 'run': row['run_accession'], 'error': 'File metadata arrays have unequal lengths'})
        for index, (location, checksum, size) in enumerate(zip_longest(*arrays), 1):
            sheets['File listings'].append({'Run accession': row['run_accession'], 'Native study accession': row['study_accession'],
                'Sample accession': row['sample_accession'], 'Experiment accession': row['experiment_accession'], 'File position': index,
                'Native FTP location': location, 'MD5 checksum': checksum, 'Size (bytes)': _number(size), 'File format': 'FASTQ' if location else None})
    for name, store, headers in (('Samples', samples, sample_headers), ('Experiments', experiments, experiment_headers)):
        for values, record in sorted(store.items()):
            sheets[name].append(dict(zip(headers, values), **{'Reporting studies': _join(record['studies']), 'Run accessions': _join(record['runs'])}))
    for name in ('Runs', 'File listings'):
        sheets[name].sort(key=lambda r: (r['Run accession'], r.get('File position', 0)))
    sheets['Study hierarchy'] = hierarchy_rows(sheets['Study hierarchy'], 'Study accession', 'Related study accession', 'ENA')
    return sheets
