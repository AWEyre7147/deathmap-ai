"""Project PMID-based evidence into the indexed PubMed review template.

PMR identifies a resource/accession; PMS identifies an SRA experiment/run pair.
Raw parser rows stay unchanged for downstream repository adapters. Shared records
repeat once per publication association, using persistent resource indices.
"""
from collections import defaultdict
from .enrichment_indices import assign_indices, native_key


# Canonical parser contracts are independent of the editable Excel layout.
NATIVE_HEADERS = {
    'Publication': ['PMID', 'DOI', 'PMCID', 'Title', 'Publication Date'],
    'Repository Records': ['PMID', 'Resource', 'Accession', 'Native Entity Level',
                           'Reported Data Type', 'Title', 'Description'],
    'SRA Accessions': ['PMID', 'SRA Experiment Accession', 'SRA Study Accession',
                       'SRA Sample Accession', 'BioSample Accession',
                       'BioProject Accession', 'SRA Run Accession'],
    'MeSH': ['Descriptor UI', 'Descriptor', 'Qualifier UI', 'Qualifier',
             'Publication Count', 'Associated PMIDs'],
    'MeSH Links': ['PMID', 'Descriptor UI', 'Qualifier UI',
                   'Descriptor Major Topic', 'Qualifier Major Topic'],
}


def indexed_tables(database, registry, index_registry=None):
    """Generate indexed display tables without mutating native evidence.

    Parameters
    ----------
    database : dict
        Canonical PMID rows and optional SRA experiment descriptions.
    registry : list of dict
        Selected PMID and Publication index/Publication Index mappings.
    index_registry : Path or None
        Persistent PMR/PMS allocation file; None uses deterministic local IDs.

    Returns
    -------
    dict
        Five display tables, with MeSH counts recomputed from selected links.

    Raises
    ------
    ValueError
        Publication identities conflict, a source PMID is unselected, or an
        experiment/repository accession is missing. Registry writes may fail.
    """
    by_pmid = defaultdict(set)
    for p in registry:
        if p.get('PMID'):
            index = p.get('Publication Index') or p.get('Publication index')
            if not index:
                raise ValueError('Missing Publication Index')
            by_pmid[str(p['PMID'])].add(index)
    if any(len(v) != 1 for v in by_pmid.values()):
        raise ValueError('Ambiguous PMID-to-publication mapping')

    def publication(pmid):
        if str(pmid) not in by_pmid:
            raise ValueError('Source PMID outside selected registry: ' + str(pmid))
        return next(iter(by_pmid[str(pmid)]))

    raw = database['rows']
    repository = [dict(zip(NATIVE_HEADERS['Repository Records'], r)) for r in raw['Repository Records']]
    sra = [dict(zip(NATIVE_HEADERS['SRA Accessions'], r)) for r in raw['SRA Accessions']]
    descriptions = {(r['PMID'], r['Accession']): r for r in database.get('sra_repository_records', [])}
    # ESummary describes SRA experiments. Make their parent records explicit
    # rather than attaching a run to an unrelated GEO or BioProject record.
    for pmid, accession in sorted({(r['PMID'], r['SRA Experiment Accession']) for r in sra}):
        if not accession:
            raise ValueError('SRA summary lacks an experiment accession')
        repository.append({'PMID': pmid, 'Resource': 'SRA', 'Accession': accession,
            'Native Entity Level': 'Experiment', 'Reported Data Type': '',
            'Title': '', 'Description': '', **descriptions.get((pmid, accession), {})})
    if any(not r['Accession'] for r in repository):
        raise ValueError('Repository record lacks an accession')
    pmr = assign_indices('PMR', {native_key(r['Resource'], r['Accession']) for r in repository}, index_registry)
    # A blank run means the experiment summary reported none, not an invented ID.
    def run_key(r):
        return native_key(r['SRA Experiment Accession'], r['SRA Run Accession'] or '<no-run>')
    pms = assign_indices('PMS', {run_key(r) for r in sra}, index_registry)
    tables = {name: [] for name in NATIVE_HEADERS}
    for r in raw['Publication']:
        tables['Publication'].append({'Publication Index': publication(r[0]),
                                     **dict(zip(NATIVE_HEADERS['Publication'], r))})
    seen = set()
    for r in repository:
        identity = (publication(r['PMID']), r['Resource'], r['Accession'])
        if identity in seen:
            continue
        seen.add(identity)
        tables['Repository Records'].append({**r, 'Publication Index': identity[0],
            'PubMed Index': pmr[native_key(r['Resource'], r['Accession'])],
            'PubMed Accession': r['Accession']})
    seen = set()
    for r in sra:
        identity = (publication(r['PMID']), run_key(r))
        if identity in seen:
            continue
        seen.add(identity)
        tables['SRA Accessions'].append({**r, 'Publication Index': identity[0],
            'PubMed Index': pmr[native_key('SRA', r['SRA Experiment Accession'])],
            'PubMed SRA Index': pms[run_key(r)]})
    groups = defaultdict(set)
    for r in raw['MeSH Links']:
        index = publication(r[0])
        tables['MeSH Links'].append({'Publication Index': index,
                                     **dict(zip(NATIVE_HEADERS['MeSH Links'], r))})
        groups[(r[1], r[2])].add(index)
    for r in raw['MeSH']:
        indices = groups[(r[0], r[2])]
        if indices:
            tables['MeSH'].append({**dict(zip(NATIVE_HEADERS['MeSH'], r)),
                'Publication Count': len(indices),
                'Associated Publication Index': '; '.join(sorted(indices))})
    return tables
