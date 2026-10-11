"""Verify and publish the completed ORCS metadata pass and approved workbook.

Canonical native Series/Sample records are stored once; publication membership
and discovery evidence retain their identifiers separately. A portable source
package preserves the exact responses behind every locator. No prior database,
owner template or earlier run is replaced.
"""
import hashlib
import json
from pathlib import Path
import shutil
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlsplit

from deathmap_ai.geo_collection import enrich_collection

BASE = Path(__file__).parent
ROOT = BASE.parents[3]


def load(name):
    """Read an existing run record without mutating its metadata."""
    return json.loads((BASE / name).read_text(encoding='utf-8'))


def digest(path):
    """Hash bytes, including source responses and generated artifacts."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Publish one completed, verified enrichment pass into data/orcs.

    Returns
    -------
    None
        Writes the database, source package, workbook and verification manifest.

    Raises
    ------
    ValueError
        Publications, sample coverage or provenance are incomplete.
    FileExistsError
        A destination already exists; previous authoritative outputs are protected.
    """
    selected = load('selected-publications.json')
    results = load('discovery-results.json')
    expected = {str(p.get('PMID') or 'orcs-' + str(p['PUBLICATION_ID'])) for p in selected}
    if set(results) != expected or load('issues.json'):
        raise ValueError('Incomplete discovery or unresolved retrieval issues')
    if load('sample-retrieval-status.json')['missing_gsms']:
        raise ValueError('Sample metadata incomplete')
    source = ROOT / 'data/orcs/geo-enrichment-source/20261011'
    database_path = ROOT / 'data/orcs/geo-enrichment.json'
    manifest_path = ROOT / 'data/orcs/geo-enrichment.manifest.json'
    workbook = ROOT / 'data/orcs/GEO-Enrichment.xlsx'
    for path in (source, database_path, manifest_path, workbook):
        if path.exists():
            raise FileExistsError(path)
    series, samples = load('series-metadata.json'), load('sample-metadata.json')
    series_count, sample_count = len(series), len(samples)
    receipts, byte_count, reused, live = [], 0, 0, 0
    # Validate every successful source response and every selected batch parent
    # before publication. Empty results remain in route states, not invented rows.
    for path in BASE.glob('**/requests.json'):
        for receipt in json.loads(path.read_text()):
            if not receipt.get('file'):
                continue
            url = urlsplit(receipt['url'])
            query = parse_qs(url.query)
            if url.netloc == 'www.ncbi.nlm.nih.gov':
                if not (url.path == '/geo/query/acc.cgi' and query.get('view') == ['brief']
                        and query.get('form') == ['text'] and query.get('targ') in (['self'], ['gsm'])):
                    raise ValueError('Unexpected GEO request outside brief metadata scope')
            elif url.netloc == 'eutils.ncbi.nlm.nih.gov':
                if query.get('db') == ['sra'] or query.get('dbfrom') == ['sra']:
                    raise ValueError('Deferred SRA route used')
            elif url.netloc == 'www.ebi.ac.uk':
                if not (url.path.endswith('/annotationsByArticleIds') or url.path.endswith('/datalinks')):
                    raise ValueError('Unexpected Europe PMC request outside accession metadata scope')
            else:
                raise ValueError('Unapproved metadata host')
            native = path.parent / receipt['file']
            if digest(native) != receipt['sha256']:
                raise ValueError('Native response changed: ' + str(native))
            for parent in receipt.get('parents', []):
                if digest(BASE / parent['file']) != parent['sha256']:
                    raise ValueError('Selected response parent changed')
            receipts.append({'receipt_file': str(path.relative_to(BASE)), **receipt})
            byte_count += native.stat().st_size
            if receipt.get('reused_from') or receipt.get('parents'):
                reused += 1
            else:
                live += 1
    tables = load('workbook-data.json')
    # Reject oversized cells before the sole full workbook export; native JSON
    # remains complete if a template/Excel limit needs owner review.
    registration = json.loads((ROOT / 'data/templates/GEO-Enrichment.manifest.json').read_text())
    for sheet in registration['sheets']:
        for row in tables[sheet['source_table']]:
            for column in sheet['columns']:
                value = row.get(column['source_key'])
                if isinstance(value, str) and len(value) > 32767:
                    raise ValueError(f"Excel text limit: {sheet['name']} {row.get('GSE')} {column['source_key']}")
    # Do not hold a second full table/native-record copy during the large export.
    del tables, series, samples
    receipt = enrich_collection(ROOT / 'data/orcs/publication-index.json', BASE,
                                repository_root=ROOT, phase='export')
    shutil.copyfile(BASE / 'GEO-Enrichment.xlsx', workbook)
    source.mkdir(parents=True)
    for path in BASE.rglob('*'):
        if path.is_file() and (path.suffix == '.response' or 'saved-sources' in path.parts
                               or 'executed-code' in path.parts
                               or path.name in ('requests.json', 'manifest.json', 'run-manifest.json',
                                                'selected-publications.json', 'retrieve.py', 'saved_native.py',
                                                'finalize.py', 'projection-verification.json', 'sample-retrieval-status.json',
                                                'initial-run-manifest.json', 'accessions.json', 'series-identities.json',
                                                'partial-evidence.json', 'pipeline-projection-receipt.json',
                                                'workbook-verification.json')):
            target = source / path.relative_to(BASE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    database = load('geo-enrichment.json')
    database['source_package'] = str(source.relative_to(ROOT))
    database['publication_index']['file'] = 'data/orcs/publication-index.json'
    database_path.write_text(json.dumps(database, indent=2, ensure_ascii=False), encoding='utf-8')
    associations = sum(result['total_gse_count'] for result in results.values())
    manifest = {'schema_version': 'geo-enrichment-v1', 'status': 'complete',
                'finished_utc': datetime.now(timezone.utc).isoformat(), 'publication_index_count': len(selected),
                'publications_with_gses': sum(bool(r['candidates']) for r in results.values()),
                'unique_gses': series_count, 'unique_gsms': sample_count, 'publication_gse_associations': associations,
                'source_package': str(source.relative_to(ROOT)), 'database_sha256': digest(database_path),
                'successful_responses': len(receipts), 'live_responses': live, 'reused_responses': reused,
                'response_bytes_in_run': byte_count, 'workbook': receipt,
                'metadata_only_request_check': 'passed',
                'issues': [], 'coverage_claim': 'No adjudicated completeness benchmark; accepted routes completed'}
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    (source / 'README.md').write_text(
        '# GEO source package — 2026-10-11\n\n'
        'Exact native responses, selected batch parents, request receipts and executed-code snapshots.\n'
        'The canonical native records and candidate relationships are in ../../geo-enrichment.json.\n'
        'Series/sample source_file paths are relative to this package. Publication evidence source_file\n'
        'paths are relative to that publication’s _run_directory. Parent batch files are package-relative.\n'
        'Cached retrieval dates span 2026-10-08 through this collection; reuse is not a new retrieval.\n'
        'Initial consolidated Europe PMC responses were retained; subsequent requests use category=GEO.\n'
        'A prior interrupted manifest can retain status=running; completed retries are selected by the canonical database.\n', encoding='utf-8')
    print(json.dumps(manifest), flush=True)


if __name__ == '__main__':
    main()
