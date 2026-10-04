"""Save public reference metadata for the owner-authorized ORCS vocabulary pass.

This independent annotation stage does not refresh ORCS or retrieve experimental
results. Durable receipts and bounded requests allow interrupted retrieval to
resume without silently replacing already saved reference versions.
"""
import argparse
import hashlib
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/cellosaurus/orcs-annotations/raw'
SOURCES = {
    'cellosaurus.txt': 'https://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt',
    'bto.obo': 'https://raw.githubusercontent.com/BRENDA-Enzymes/BTO/refs/heads/master/bto.obo',
    'cl.obo': 'https://raw.githubusercontent.com/obophenotype/cell-ontology/master/cl.obo',
    'efo.obo': 'https://www.ebi.ac.uk/efo/efo.obo',
}

def fetch(item):
    """Save one fixed public source and receipt, reusing verified successes."""
    name, url = item
    destination = RAW / name
    receipt = RAW / (name + '.receipt.json')
    if receipt.exists():
        old = json.loads(receipt.read_text(encoding='utf-8'))
        if old['status'] == 'received' and destination.exists():
            assert hashlib.sha256(destination.read_bytes()).hexdigest() == old['sha256']
            return name, 'reused', destination.stat().st_size
    record = {'url': url, 'requested_at': datetime.now(timezone.utc).isoformat(),
              'status': 'reserved', 'timeout_seconds': 30, 'attempt': 1,
              'purpose': 'Public reference metadata only; owner-authorized full vocabulary annotation'}
    if receipt.exists():
        record['previous_receipt'] = old
    receipt.write_text(json.dumps(record, indent=2), encoding='utf-8')
    try:
        temporary = destination.with_suffix(destination.suffix + '.part')
        if not (name.startswith('screen-') and temporary.exists()):
            if name.startswith('screen-'):
                time.sleep(1)
            request = urllib.request.Request(url, headers={'User-Agent': 'DeathMap-AI/0.1 reference-annotation'})
            started = time.monotonic()
            with urllib.request.urlopen(request, timeout=30) as response, temporary.open('wb') as output:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
                    if time.monotonic() - started > 180:
                        raise TimeoutError('Reference-file download exceeded 180 seconds')
                record.update(http_status=response.status, final_url=response.url)
        else:
            record['transport'] = 'Reparsed the previous locally saved HTML response; no new request'
        # ORCS pages contain screen results as well as metadata. Preserve only
        # the Cell Type/Cell Line metadata excerpt for this annotation stage.
        if name.startswith('screen-'):
            html = temporary.read_text(encoding='utf-8')
            fields = re.findall(r'<li>[^\n]*<strong>Cell (?:Type|Line)</strong>[^\n]*</li>', html)
            if len(fields) != 2:
                raise ValueError('Unrecognized ORCS metadata section')
            excerpt = '\n'.join(fields)
            temporary.write_text(excerpt, encoding='utf-8')
            record['saved_scope'] = 'Cell Type and Cell Line HTML excerpt only; result content omitted'
        temporary.replace(destination)
        record.update(status='received', sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                      raw_file=name, bytes=destination.stat().st_size)
    except Exception as error:
        record.update(status='failed', error=str(error))
    record['completed_at'] = datetime.now(timezone.utc).isoformat()
    receipt.write_text(json.dumps(record, indent=2), encoding='utf-8')
    return name, record['status'], record.get('bytes', record.get('error'))

def main():
    """Fetch fixed reference files; at most three independent providers in parallel."""
    RAW.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument('--orcs-types', action='store_true')
    parser.add_argument('--unresolved-lines', action='store_true')
    args = parser.parse_args()
    sources = SOURCES
    if args.orcs_types or args.unresolved_lines:
        screens = json.loads((ROOT / 'data/orcs/screen-index.json').read_text(encoding='utf-8'))
        representatives = {}
        unresolved = set()
        if args.unresolved_lines:
            annotations = json.loads((RAW.parent / 'annotations.json').read_text(encoding='utf-8'))
            unresolved = {r['value'] for r in annotations['cell_lines'] if not r['accession']}
        for screen in screens:
            if args.unresolved_lines:
                if screen['CELL_LINE'] not in unresolved:
                    continue
                group = (screen['CELL_LINE'], screen['ORGANISM_ID'])
            else:
                group = screen['CELL_TYPE']
            representatives.setdefault(group, screen['SCREEN_ID'])
        sources = {f'screen-{identifier}.html': f'https://orcs.thebiogrid.org/Screen/{identifier}'
                   for identifier in representatives.values()}
    with ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(fetch, sources.items()):
            print(result, flush=True)
            if args.orcs_types:
                time.sleep(0.4)

if __name__ == '__main__':
    main()
