"""Build one shared PubMed database and PMID subsets for existing ORCS runs.

This command never rebuilds ORCS searches or resolves preprint identifiers.
Saved-response mode performs no network work. Existing outputs are refused,
and separate workbook receipts bind each subset to the shared database hash.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from .pubmed_enrichment import Retrieval, save_json
from .pubmed_projection import project_saved
from .pubmed_workbook import export_workbook, subset_rows


def digest(path):
    """Read a file's SHA-256 for source and output provenance.

    Parameters
    ----------
    path : Path or str
        Existing file whose bytes are hashed without mutation.

    Returns
    -------
    str
        Lowercase hexadecimal digest.
    """
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(root, source, saved_only=False):
    """Build a shared metadata database and views for retained ORCS searches.

    Parameters
    ----------
    root : Path or str
        Repository containing the approved template and shared ORCS index.
    source : Path or str
        Native-response folder with the index-bound PMID selection.
    saved_only : bool
        Skip network requests and use previously saved responses only.

    Returns
    -------
    dict
        Completed database/output manifest with unresolved publications.

    Raises
    ------
    FileExistsError
        A database or workbook output would overwrite an existing artifact.
    ValueError
        Source index changed or a search PMID is absent from the shared index.

    Notes
    -----
    Writes the shared database, workbooks and receipts. Direct associations
    do not establish repository coverage or exact CRISPR screen attribution.
    """
    root, source = Path(root), Path(source)
    index = root / 'data/orcs/publication-index.json'
    publications = json.loads(index.read_text(encoding='utf-8-sig'))
    selection = json.loads((source / 'selection.json').read_text(encoding='utf-8'))
    if digest(index) != selection['index_sha256']:
        raise ValueError('ORCS publication index changed after selection; review before retrieval')
    pmids = selection['pmids']
    if not saved_only:
        Retrieval(source).retrieve(pmids)
    # Verify every native response receipt before creating a shared projection.
    requests = json.loads((source / 'requests.json').read_text(encoding='utf-8'))
    for request in requests:
        assert digest(source / request['file']) == request['sha256']
    database = project_saved(source, pmids)
    database.update({'schema_version': 'pubmed-enrichment-v1', 'retrieved_at': max(r['retrieved_utc'] for r in requests),
                     'source_directory': str(source.relative_to(root)).replace('\\', '/'),
                     'publication_index_sha256': digest(index), 'repository_columns': ['PMID', 'Resource', 'Accession', 'Native Entity Level', 'Reported Data Type', 'Title', 'Description'],
                     'orcs_publications': [{'publication_id': p['PUBLICATION_ID'], 'pmid': p.get('PMID'),
                                            'status': 'retrieved' if p.get('PMID') in pmids else 'no_verified_pmid'} for p in publications],
                     'scope': 'Direct PubMed links only; no repository hierarchy expansion or exact screen attribution',
                     'tool': 'NCBI E-utilities EFfetch/ELink/ESummary', 'python_version': sys.version.split()[0]})
    database_path = root / 'data/orcs/pubmed-enrichment.json'
    if database_path.exists():
        raise FileExistsError(database_path)
    save_json(database_path, database)
    template = root / 'data/templates/PubMed-Enrichment.xlsx'
    outputs = [(root / 'data/orcs/PubMed-Enrichment.xlsx', pmids, selection['unresolved'], 'whole_orcs')]
    for projection in sorted((root / 'outputs/orcs').glob('*/*/projection.json')):
        records = json.loads(projection.read_text(encoding='utf-8-sig'))['sheets']['Publications']
        search_pmids = sorted({str(p['pmid']) for p in records if p.get('pmid')}, key=int)
        if not set(search_pmids).issubset(pmids):
            raise ValueError(f'Search PMID outside the shared index: {projection}')
        unresolved = [{'publication_id': p.get('publication_id'), 'status': 'no_verified_pmid'} for p in records if not p.get('pmid')]
        outputs.append((projection.parent / 'pubmed-enrichment/PubMed-Enrichment.xlsx', search_pmids, unresolved, str(projection.relative_to(root))))
    receipts = []
    for workbook, ids, unresolved, input_name in outputs:
        rows = subset_rows(database, ids)
        export_workbook(template, workbook, rows)
        receipt = {'input': input_name, 'publication_count': len(ids) + len(unresolved), 'retrieved_publications': len(ids),
                   'unresolved_publications': unresolved, 'row_counts': {name: len(values) for name, values in rows.items()},
                   'database': 'data/orcs/pubmed-enrichment.json', 'database_sha256': digest(database_path),
                   'template_sha256': digest(template), 'workbook_sha256': digest(workbook),
                   'scope': database['scope'], 'date_policy': 'Literal text MM;DD;YYYY; partial MM;YYYY or YYYY',
                   'created_utc': datetime.now(timezone.utc).isoformat(), 'verification': 'Every projected row, XML compatibility namespaces and template preservation checked'}
        save_json(workbook.with_suffix('.manifest.json'), receipt)
        receipts.append({'workbook': str(workbook.relative_to(root)).replace('\\', '/'), **receipt})
    manifest = {'schema_version': database['schema_version'], 'publication_index_count': len(publications),
                'retrieved_pmids': len(pmids), 'unresolved': selection['unresolved'], 'requests': len(requests),
                'database_sha256': digest(database_path), 'source': database['source_directory'],
                'row_counts': {name: len(values) for name, values in database['rows'].items()},
                'unique_repository_records': len({(row[1], row[2]) for row in database['rows']['Repository Records']}),
                'source_code_sha256': {name: digest(Path(__file__).parent / name) for name in ['pubmed_enrichment.py', 'pubmed_projection.py', 'pubmed_workbook.py', 'pubmed_milestone.py']},
                'outputs': receipts, 'native_excel_open': 'pending'}
    save_json(root / 'data/orcs/pubmed-enrichment.manifest.json', manifest)
    return manifest


def main():
    """Run the command-line enrichment milestone using explicit source paths.

    Returns
    -------
    None
        Parses command-line arguments, writes authorized outputs and prints
        the manifest summary. Retrieval and overwrite errors propagate.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--saved-only', action='store_true')
    args = parser.parse_args()
    manifest = build(args.root, args.source, args.saved_only)
    print(json.dumps({key: value for key, value in manifest.items() if key != 'outputs'}, indent=2))


if __name__ == '__main__':
    main()
