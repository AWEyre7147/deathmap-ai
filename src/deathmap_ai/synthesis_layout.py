"""Apply owner-selected synthesis labels without altering native source keys.

Each column retains an explicit source-header mapping. Cosmetic case collisions
receive numbered labels rather than merging scientifically distinct attributes.
This imported layout helper performs no retrieval or scientific normalization.
"""


NAMES = {
    'Publications': 'Publications', 'Publication-repository links': 'PUB-Repository Links',
    'PubMed - Repository Records': 'PubMed-Repository Links', 'PubMed - SRA Accessions': 'PubMed-SRA Links',
    'PubMed - MeSH': 'PubMed-MeSH Terms', 'PubMed - MeSH Links': 'PubMed-MeSH Links',
    'GEO - Series Records': 'GEO Series Records', 'GEO - Series Hierarchy': 'GEO Series Hierarchy',
    'GEO - Repository Identifiers': 'GEO Repository Links', 'GEO - Sample Metadata': 'GEO Sample Records',
    'ENA - Studies': 'ENA Study Records', 'ENA - Study hierarchy': 'ENA Study Hierarchy',
    'ENA - Samples': 'ENA Sample Records', 'ENA - Experiments': 'ENA Experiment Records', 'ENA - Runs': 'ENA Run Records',
    'AE - Studies': 'ArrayExpress Study Records', 'AE - Protocols': 'ArrayExpress Protocol Records',
    'AE - Sample metadata': 'ArrayExpress Sample Records', 'AE - Assay metadata': 'ArrayExpress Assay Records',
    'AE - IDF metadata': 'ArrayExpress IDF Metadata', 'AE - SDRF metadata': 'ArrayExpress SDRF Metadata',
}

ORDERS = {
    'PubMed - Repository Records': ['Publication index', 'Accession', 'Resource', 'Title', 'Description', 'Native Entity Level', 'Reported Data Type'],
    'PubMed - SRA Accessions': ['Publication index', 'Study Accession', 'Sample Accession', 'Experiment Accession', 'Run Accession', 'BioProject Accession', 'BioSample Accession'],
    'PubMed - MeSH Links': ['Publication index', 'Descriptor UI', 'Descriptor Major Topic', 'Qualifier UI', 'Qualifier Major Topic'],
    'GEO - Series Records': ['Publication index', 'geo_accession', 'platform_organism', 'platform_taxid', 'sample_organism', 'sample_taxid', 'sample_count', 'title', 'summary', 'overall_design', 'type'],
    'GEO - Repository Identifiers': ['Publication index', 'GSE', 'Identifier', 'GSM', 'Entity Level', 'Resource', 'Native Field'],
    'ENA - Studies': ['Publication index', 'Study accession', 'SRA study accession', 'Organism', 'Samples in report', 'Experiments in report', 'Runs in report', 'Study title', 'Study description'],
    'ENA - Samples': ['Publication index', 'Sample accession', 'Reporting studies', 'Run accessions', 'Sample title', 'Sample description', 'Organism'],
    'ENA - Experiments': ['Publication index', 'Experiment accession', 'Sample accession', 'Reporting studies', 'Run accessions', 'Experiment title', 'Library strategy', 'Library source', 'Library selection', 'Library layout', 'Instrument platform', 'Instrument model', 'Library construction protocol'],
    'ENA - Runs': ['Publication index', 'Run accession', 'Native study accession', 'Sample accession', 'Experiment accession', 'Read count', 'Base count', 'Reporting studies', 'SRA study accession'],
    'AE - IDF metadata': ['Publication index', 'Study accession', 'Native field', 'Original value', 'Native line', 'Native column'],
    'AE - SDRF metadata': ['Publication index', 'Study accession', 'Source name', 'Native field', 'Original value', 'Native data row', 'Native column'],
}


def _title(header):
    acronyms = {'id': 'ID', 'ui': 'UI', 'pmid': 'PMID', 'doi': 'DOI', 'pmcid': 'PMCID', 'geo': 'GEO',
                'sra': 'SRA', 'ena': 'ENA', 'rna': 'RNA', 'dna': 'DNA', 'url': 'URL', 'gbm': 'GBM',
                'biosample': 'BioSample', 'bioproject': 'BioProject', 'taxid': 'TaxID'}
    return ' '.join(acronyms.get(word.lower(), word.capitalize()) for word in header.replace('_ch1', '').replace('_', ' ').split())


def layout_sheet(sheet):
    """Return a renamed/reordered sheet and its lossless source-column mapping.

    Parameters
    ----------
    sheet : dict
        Native synthesis sheet name, headers and rectangular source rows.

    Returns
    -------
    dict
        Owner-facing labels and copied values with explicit original headers.

    Raises
    ------
    ValueError
        A requested column is missing or an unexpected sheet is supplied.
    """
    name = sheet['name']
    if name not in NAMES:
        raise ValueError('Unknown synthesis sheet: ' + name)
    headers = list(sheet['headers'])
    remove = {'Publication Count'} if name == 'PubMed - MeSH' else {'Publication association', 'Source URL'} if name == 'AE - Studies' else {'Part'} if name == 'AE - SDRF metadata' else set()
    if name == 'GEO - Sample Metadata':
        remove.update(('geo_accession', 'series_id'))
    order = ORDERS.get(name, [h for h in headers if h not in remove])
    if name == 'AE - Protocols':
        order = ['Publication index', 'Native protocol ID'] + [h for h in headers if h not in ('Publication index', 'Native protocol ID')]
    if any(h not in headers for h in order):
        raise ValueError('Requested header missing: ' + name)
    aliases = {'BioProject Accession': 'NCBI BioProject', 'BioSample Accession': 'NCBI BioSample'}
    if name == 'PubMed - Repository Records':
        aliases['Resource'] = 'Repository'
    if name == 'PubMed - SRA Accessions':
        aliases.update({'Study Accession': 'PubMed Study', 'Sample Accession': 'PubMed Sample',
                        'Experiment Accession': 'PubMed Experiment', 'Run Accession': 'PubMed Run'})
    if name.startswith('GEO - '):
        aliases.update({'GSE': 'GEO Study', 'GSM': 'GEO Sample', 'Related GSE': 'Related GEO Study',
                        'geo_accession': 'GEO Study'})
        if name == 'GEO - Repository Identifiers':
            aliases.update({'Native Field': 'GEO Field', 'Entity Level': 'GEO Level', 'Identifier': 'Accession'})
    if name.startswith('ENA - '):
        aliases.update({'Study accession': 'ENA Study', 'Related study accession': 'Related ENA Study', 'SRA study accession': 'SRA Accession',
                        'Sample accession': 'ENA Sample', 'Reporting studies': 'Reported ENA Studies', 'Run accessions': 'ENA Runs',
                        'Experiment accession': 'ENA Experiment', 'Run accession': 'ENA Run', 'Native study accession': 'ENA Study',
                        'Samples in report': 'Samples', 'Experiments in report': 'Experiments', 'Runs in report': 'Runs'})
        if name == 'ENA - Experiments':
            aliases['Run accessions'] = 'ENA Run'
    if name.startswith('AE - '):
        aliases.update({'Study accession': 'ArrayExpress Study', 'Native protocol ID': 'ArrayExpress Protocol',
                        'Native section ID': 'ArrayExpress Section ID', 'Native section type': 'ArrayExpress Section Type',
                        'Native line': 'ArrayExpress Line', 'Native column': 'ArrayExpress Column',
                        'Native field': 'ArrayExpress Field', 'Native data row': 'ArrayExpress Row'})
    labels, counts = [], {}
    for h in order:
        label = aliases.get(h, _title(h))
        counts[label] = counts.get(label, 0) + 1
        labels.append(label if counts[label] == 1 else f'{label} ({counts[label]})')
    positions = [headers.index(h) for h in order]
    # Change repository labels, not identifiers or scientific prose. Original
    # source rows/keys remain in the companion evidence, including native labels.
    def display(value):
        return 'NCBI BioProject' if value == 'BioProject' else 'NCBI BioSample' if value == 'BioSample' else value
    return {'name': NAMES[name], 'headers': labels,
            'rows': [[display(row[i]) for i in positions] for row in sheet['rows']],
            'source_sheet': name, 'columns': [{'header': label, 'source_header': h} for label, h in zip(labels, order)],
            'removed_headers': [h for h in headers if h not in order]}
