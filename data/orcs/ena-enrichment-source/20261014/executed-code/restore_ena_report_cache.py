"""Restore completed run reports after a size checkpoint, without new retrieval.

All response hashes are checked. Missing reports remain explicitly pending with
blank counts, never zero; final outlier scope still requires an owner decision.
"""
import csv
import io
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import hashlib
import re
from deathmap_ai.ena_collection import REPORT_FIELDS, _load, _save

folder = Path(__import__('sys').argv[1])
database = _load(folder / 'database.json')
receipts = _load(folder / 'requests.json')
restored = 0
for receipt in receipts:
    if '/portal/api/filereport?' not in receipt['url'] or receipt.get('error') or not receipt.get('file'):
        continue
    query = parse_qs(urlsplit(receipt['url']).query)
    accession = query.get('accession', [''])[0]
    if accession not in database['studies']:
        continue
    body = (folder / receipt['file']).read_bytes()
    assert hashlib.sha256(body).hexdigest() == receipt['sha256']
    reader = csv.DictReader(io.StringIO(body.decode('utf-8')), delimiter='\t')
    assert set(REPORT_FIELDS) <= set(reader.fieldnames or [])
    rows = list(reader)
    if any(not re.fullmatch(r'[SED]RR\d+', row.get('run_accession') or '') for row in rows):
        study = database['studies'][accession]
        study.update(runs=[], run_report_status='pending-report-recovery', invalid_run_report_response=receipt['file'])
        for key in ('run_count', 'sample_count', 'experiment_count'):
            study.pop(key, None)
        receipt['incomplete'] = True
        receipt['schema_error'] = 'Server error text in place of sequencing-run records'
        continue
    database['studies'][accession].update(runs=rows, run_report_response=receipt['file'], run_report_url=receipt['url'],
        run_count=len({r['run_accession'] for r in rows}), sample_count=len({r['sample_accession'] for r in rows}),
        experiment_count=len({r['experiment_accession'] for r in rows}), run_report_status='complete')
    restored += 1
pending = []
for accession, study in database['studies'].items():
    if study.get('run_report_status') != 'complete':
        if study.get('run_report_status') != 'pending-report-recovery':
            study['run_report_status'] = 'pending-size-checkpoint'
        pending.append({'study': accession, 'title': study['title'], 'description': study['description'],
                        'reason': 'No complete report preserved when per-response size boundary stopped the run'})
database['status'] = 'pending-size-checkpoint'
_save(folder / 'database.json', database)
_save(folder / 'requests.json', receipts)
_save(folder / 'size-checkpoint.json', {'response_limit_bytes': 32 * 1024**2, 'restored_complete_reports': restored,
    'pending_collections': pending, 'new_network_requests': 0})
print(json.dumps({'restored_complete_reports': restored, 'pending_collections': [x['study'] for x in pending]}))
