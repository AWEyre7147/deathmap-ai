"""Readable spreadsheet labels without changing canonical scientific fields.

Only display labels are normalized. Source keys remain in template manifests;
duplicate case variants share one label while distinct source values survive.
"""
import re


ACRONYMS = {
    word.lower(): word for word in (
        'ID', 'IDs', 'UI', 'PMID', 'PMIDs', 'PMCID', 'PMCIDs', 'DOI', 'DOIs',
        'URL', 'URLs', 'XML', 'RNA', 'DNA', 'GBM', 'GEO', 'GSE', 'GSM', 'GPL',
        'SRA', 'ENA', 'NCBI', 'FTP', 'MD5', 'IDF', 'SDRF', 'CRISPR', 'Cas9',
        'MeSH', 'PMC', 'BioProject', 'BioSample', 'TaxID', 'FASTA', 'FASTQ', 'ArrayExpress', 'PubMed',
    )
}


def readable_title(header):
    """Return a title-case label, preserving acronyms and scientific qualifiers."""
    value = re.sub(r'(?i)(?:_|\s)ch1\b', '', header).replace('_', ' ')
    value = re.sub(r'(?i)\bno\.?(?=\s)', 'Number', value)
    value = re.sub(r'(?i)\bhyb\b', 'Hybridization', value)
    value = re.sub(r'\s*\([2-9][0-9]*\)$', '', value)
    return re.sub(r'[A-Za-z][A-Za-z0-9]*',
                  lambda m: ACRONYMS.get(m[0].lower(), m[0].capitalize()),
                  ' '.join(value.split()))


def readable_headers(headers):
    """Normalize labels; duplicate source fields are consolidated by the caller."""
    return [None if h is None else readable_title(h) for h in headers]


def merge_display_values(values):
    """Combine duplicate-field values, preserving distinct reported text.

    Repeated identical values appear once. Conflicting values remain newline-
    separated; this display operation does not choose a scientific interpretation.
    The original keys and values remain in canonical source records.
    """
    distinct = []
    for value in values:
        if value is None or value == '':
            continue
        if not any(type(value) is type(v) and value == v for v in distinct):
            distinct.append(value)
    if not distinct:
        return None
    return distinct[0] if len(distinct) == 1 else '\n'.join(str(v) for v in distinct)


def identifier_label(resource, sheet, source_key, fallback):
    """Name identifier namespaces consistently, using source-field semantics.

    ENA project/sample fields contain BioProject/BioSample identifiers; SRA
    studies and samples are different namespaces. GEO accession meaning depends
    on whether its native record is a Series or Sample. Unrecognized fields keep
    their existing readable label rather than being guessed into a namespace.
    """
    mappings = {
        'GEO': {'GSE': 'GEO Series Accession', 'Related GSE': 'Related GEO Series Accession',
                'GSM': 'GEO Sample Accession', 'Identifier': 'Accession'},
        'ENA': {'Study accession': 'BioProject Accession',
                'Native study accession': 'BioProject Accession',
                'Related study accession': 'Related BioProject Accession',
                'SRA study accession': 'SRA Study Accession',
                'Sample accession': 'BioSample Accession',
                'Experiment accession': 'SRA Experiment Accession',
                'Run accession': 'SRA Run Accession',
                'Run accessions': 'SRA Run Accessions',
                'Reporting studies': 'Reported BioProject Accessions'},
        'PubMed': {'Study Accession': 'SRA Study Accession',
                   'Sample Accession': 'SRA Sample Accession',
                   'Experiment Accession': 'SRA Experiment Accession',
                   'Run Accession': 'SRA Run Accession',
                   'BioProject Accession': 'BioProject Accession',
                   'BioSample Accession': 'BioSample Accession'},
        'AE': {'Study accession': 'ArrayExpress Study Accession',
               'Native protocol ID': 'ArrayExpress Protocol ID'},
        'Main': {'accession_reported': 'Accession',
                 'parent_accession_reported': 'Parent Accession'},
    }
    if resource == 'GEO' and source_key == 'geo_accession':
        return 'GEO Sample Accession' if 'Sample' in sheet else 'GEO Series Accession'
    return mappings.get(resource, {}).get(source_key, fallback)
