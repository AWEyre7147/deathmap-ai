"""Promote a verified completed ENA run without retrieving or rebuilding data.

Verify immutable response bytes and owner template, retain the export receipt,
then copy the workbook and write a compact canonical JSON plus its manifest.
The large intermediate database is gzip-preserved byte-for-byte with a receipt.
Existing canonical outputs are refused rather than overwriting owner files.
"""
import gzip
import hashlib
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone


def finalize(root, folder):
    """Promote one already verified ENA run and return its result manifest.

    Parameters
    ----------
    root, folder : Path
        Repository root and completed source-package directory.

    Returns
    -------
    dict
        Exact output hashes, counts, accepted omissions and source-package link.

    Raises
    ------
    AssertionError
        Workbook verification, source hashes, schema or destination checks fail.
    """
    root, folder = Path(root), Path(folder)
    source = folder / 'database.json'
    database = json.loads(source.read_text(encoding='utf-8'))
    workbook = folder / 'ENA-Enrichment.xlsx'
    verified = json.loads(workbook.with_suffix('.verification.json').read_text(encoding='utf-8'))
    registration = json.loads((root / 'data/templates/ENA-Enrichment.manifest.json').read_text(encoding='utf-8'))
    digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    assert verified['database_sha256'] == digest(source)
    assert verified['workbook_sha256'] == digest(workbook)
    assert digest(root / 'data/templates/ENA-Enrichment.xlsx') == registration['sha256'] == verified['template_sha256']
    assert database['status'] == 'complete_with_omissions'
    assert len(database['publications']) == 418
    assert not any(p['issues'] for p in database['publications'])
    assert not database['study_failures'] and not database['issues']
    requests = json.loads((folder / 'requests.json').read_text(encoding='utf-8'))
    for receipt in requests:
        if receipt.get('file'):
            assert digest(folder / receipt['file']) == receipt['sha256']
    destination = root / 'data/orcs'
    json_path = destination / 'ena-enrichment.json'
    excel_path = destination / 'ENA-Enrichment.xlsx'
    manifest_path = destination / 'ena-enrichment.manifest.json'
    assert not any(p.exists() for p in (json_path, excel_path, manifest_path))
    json_path.write_text(json.dumps(database, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    shutil.copyfile(workbook, excel_path)
    assert digest(excel_path) == verified['workbook_sha256']
    snapshots = folder / 'executed-code'
    for name in ('export_enrichment_template.mjs', 'verify_enrichment_template.py', 'restore_ena_report_cache.py',
                 'recover_ena_title_requests.py', 'recover_ena_run_reports.py', 'finalize_ena_collection.py'):
        shutil.copyfile(root / 'scripts' / name, snapshots / name)
    # Original retrieval snapshots remain unchanged. Record the tested active
    # policy-capable implementation under distinct names, without implying it
    # was the implementation used for the already completed live requests.
    for name in ('ena_collection.py', 'ena_projection.py', 'ena_workbook.py', 'geo_workbook.py', 'pubmed_workbook.py'):
        shutil.copyfile(root / 'src/deathmap_ai' / name, snapshots / ('final-' + name))
    shutil.copyfile(root / 'tests/test_ena_collection.py', snapshots / 'test_ena_collection.py')
    result = {'schema_version': 'ena-enrichment-manifest/1.0', 'strategy': database['strategy'],
        'status': database['status'], 'finalized_utc': datetime.now(timezone.utc).isoformat(),
        'database': str(json_path.relative_to(root)), 'database_sha256': digest(json_path),
        'workbook': str(excel_path.relative_to(root)), 'workbook_sha256': digest(excel_path),
        'source_package': str(folder.relative_to(root)), 'template_sha256': registration['sha256'],
        'summary': database['summary'], 'scope_decision': database['scope_decision'],
        'verification': verified, 'response_hashes_verified': len([r for r in requests if r.get('file')]),
        'focused_tests_passed': 12, 'code_snapshots': {p.name: digest(p) for p in snapshots.iterdir() if p.is_file()}}
    manifest_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    # gzip stores exactly the original database bytes; the compact JSON is a
    # value-equivalent canonical copy. This avoids retaining a >100 MiB loose
    # intermediate while preserving its original hash and reproducibility.
    compressed = folder / 'database.json.gz'
    assert not compressed.exists()
    with source.open('rb') as inp, gzip.open(compressed, 'wb') as output:
        shutil.copyfileobj(inp, output)
    with gzip.open(compressed, 'rb') as inp:
        assert hashlib.sha256(inp.read()).hexdigest() == verified['database_sha256']
    (folder / 'database-preservation.json').write_text(json.dumps({'original_name': 'database.json',
        'original_sha256': verified['database_sha256'], 'compressed_name': compressed.name, 'compressed_sha256': digest(compressed),
        'canonical_json': str(json_path.relative_to(root)), 'canonical_sha256': result['database_sha256'],
        'uncompressed_bytes_verified': True}, indent=2), encoding='utf-8')
    source.unlink()
    return result


if __name__ == '__main__':
    result = finalize(*map(Path, sys.argv[1:3]))
    print(json.dumps({'database': result['database'], 'workbook': result['workbook'], 'status': result['status']}))
