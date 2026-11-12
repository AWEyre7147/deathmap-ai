"""Project saved ENA records into the owner's linked, six-sheet workbook.

Native accessions define stable entity indices. Rows retain reporting-study
context, so overlapping reports cannot create false sample-study combinations.
Publication links remain candidate associations, not experimental attribution.
The older native projection remains available to the existing synthesis layout.
"""
import json
from pathlib import Path
from itertools import zip_longest

from .enrichment_indices import assign_indices, native_key


def _join(values):
    return '\n'.join(sorted(set(str(v) for v in values if v not in (None, ''))))


def _number(value):
    return int(value) if value not in (None, '') else None


def _publications(database, registry):
    registrations = json.loads(Path(registry).read_text(encoding='utf-8')) if registry else []
    by_native, by_pmid = {}, {}
    for entry in registrations:
        for field, target in [('ORCS Publication ID', by_native), ('PMID', by_pmid)]:
            value = str(entry.get(field) or '')
            if value:
                if value in target:
                    raise ValueError('Ambiguous ENA publication registry')
                target[value] = entry['Publication index']
    result, used = {}, set()
    for record in database['publications']:
        pub = record['publication']
        matches = {value for value in (
            by_native.get(str(pub.get('PUBLICATION_ID') or pub.get('ORCS Publication ID') or '')),
            by_pmid.get(str(pub.get('PMID') or ''))) if value}
        if len(matches) > 1:
            raise ValueError('Conflicting ENA publication identities')
        # An explicitly supplied cohort index takes precedence over the ORCS
        # registry crosswalk, as in the other repository enrichment stages.
        index = pub.get('Publication Index') or pub.get('Publication index') or next(iter(matches), None)
        if not index or index in used or record['key'] in result:
            raise ValueError('Unique Publication Index or matching registry entry required')
        used.add(index)
        result[record['key']] = { 'Publication Index': index, 'PMID': pub.get('PMID'),
            'DOI': pub.get('DOI'), 'PMCID': pub.get('PMCID'),
            'Publication Title': pub.get('TITLE') or pub.get('Publication Title') or pub.get('Title')}
    return result


def project(database, publication_registry=None, index_registry=None):
    """Build linked workbook rows without fetching or changing native metadata.

    Parameters
    ----------
    database : dict
        Canonical ENA publications and studies with saved read-run reports.
    publication_registry : Path, optional
        Existing PUB index crosswalk; required unless inputs carry their indices.
    index_registry : Path, optional
        Append-only shared resource index registry. None uses in-memory indices.

    Returns
    -------
    dict
        Six sheet tables. Child entities repeat only when study context or
        reported metadata differs; their accession-based indices remain stable.

    Raises
    ------
    ValueError
        Publication identities conflict, links dangle, or native IDs are missing.
    """
    pubs = _publications(database, publication_registry)
    studies = database['studies']
    identities = {prefix: set() for prefix in ('ENST', 'ENSA', 'ENEX', 'ENRU')}
    for accession, study in studies.items():
        if not {a['publication_key'] for a in study['associations']} <= pubs.keys():
            raise ValueError('ENA study references an unknown publication')
        identities['ENST'].add(native_key(accession))
        for row in study['runs']:
            for prefix, field in [('ENSA', 'sample_accession'), ('ENEX', 'experiment_accession'), ('ENRU', 'run_accession')]:
                if not row.get(field):
                    raise ValueError('Missing native ENA identity: ' + field)
                identities[prefix].add(native_key(row[field]))
    indices = {prefix: assign_indices(prefix, keys, index_registry) for prefix, keys in identities.items()}
    sheets = {name: [] for name in ('Publications', 'Studies', 'Samples', 'Experiments', 'Runs', 'Files')}
    found, seen = set(), {name: set() for name in sheets}

    def append(name, row):
        identity = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if identity not in seen[name]:
            seen[name].add(identity)
            sheets[name].append(row)

    for accession, study in sorted(studies.items()):
        keys = {a['publication_key'] for a in study['associations']}
        found.update(keys)
        context = {'Publication Index': _join(pubs[key]['Publication Index'] for key in keys),
                   'Study Index': indices['ENST'][native_key(accession)]}
        append('Studies', {**context, 'Study Accession': accession,
            'Study Title': study.get('title'), 'Study Description': study.get('description'),
            'Organism': _join(study.get('organism', [])), 'Sample Count': study.get('sample_count'),
            'Experiment Count': study.get('experiment_count'), 'Run Count': study.get('run_count'),
            'Source URL': study.get('source_url')})
        for row in study['runs']:
            sample = {**context, 'Sample Index': indices['ENSA'][native_key(row['sample_accession'])]}
            append('Samples', {**sample, 'Sample Accession': row['sample_accession'],
                'Sample Title': row.get('sample_title'), 'Sample Description': row.get('sample_description'),
                'Organism': row.get('scientific_name')})
            experiment = {**sample, 'Experiment Index': indices['ENEX'][native_key(row['experiment_accession'])]}
            append('Experiments', {**experiment, **{header: row.get(field) for header, field in (
                ('Experiment Accession', 'experiment_accession'), ('Experiment Title', 'experiment_title'),
                ('Library Strategy', 'library_strategy'), ('Library Source', 'library_source'),
                ('Library Selection', 'library_selection'), ('Library Layout', 'library_layout'),
                ('Instrument Platform', 'instrument_platform'), ('Instrument Model', 'instrument_model'),
                ('Library Construction Protocol', 'library_construction_protocol'))}})
            run = {**experiment, 'Run Index': indices['ENRU'][native_key(row['run_accession'])]}
            append('Runs', {**run, 'Run Accession': row['run_accession'],
                'Read Count': _number(row.get('read_count')), 'Base Count': _number(row.get('base_count'))})
            # ENA's semicolon-separated FASTQ arrays share a one-based position.
            # Preserve unmatched metadata and missing sizes rather than truncate.
            arrays = [row.get(k, '').split(';') if row.get(k) else [] for k in ('fastq_ftp', 'fastq_md5', 'fastq_bytes')]
            for position, (location, checksum, size) in enumerate(zip_longest(*arrays), 1):
                append('Files', {**run, 'Native FTP Location': location, 'File Position': position,
                    'File Format': 'FASTQ' if location else None, 'Size (Bytes)': _number(size)})
    sheets['Publications'] = sorted((pubs[key] for key in found), key=lambda p: p['Publication Index'])
    return sheets
