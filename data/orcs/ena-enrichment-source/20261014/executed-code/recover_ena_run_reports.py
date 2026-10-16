"""Retry only malformed cached run reports; leave large-collection scope pending.

Each of up to ten invalid reports is retried once at the application level, with
the transport's bounded transient retries. Native error responses remain evidence.
"""
import csv
import io
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from deathmap_ai.ena_collection import API, REPORT_FIELDS, Transport, _load, _save

folder = Path(__import__('sys').argv[1])
database = _load(folder / 'database.json')
transport = Transport(folder)
pending = [(k, s) for k, s in database['studies'].items() if s.get('run_report_status') == 'pending-report-recovery']
assert len(pending) <= 10
receipt = []
for accession, study in pending:
    url = API + 'portal/api/filereport?' + urlencode({'accession': accession, 'result': 'read_run', 'fields': ','.join(REPORT_FIELDS), 'format': 'tsv'})
    try:
        body, source = transport.get(url)
        reader = csv.DictReader(io.StringIO(body.decode('utf-8')), delimiter='\t')
        assert set(REPORT_FIELDS) <= set(reader.fieldnames or [])
        rows = list(reader)
        assert all(re.fullmatch(r'[SED]RR\d+', x.get('run_accession') or '') for x in rows)
        study.update(runs=rows, run_report_status='complete', run_report_response=source['file'], run_report_url=url,
            run_count=len({r['run_accession'] for r in rows}), sample_count=len({r['sample_accession'] for r in rows}),
            experiment_count=len({r['experiment_accession'] for r in rows}))
        receipt.append({'study': accession, 'status': 'recovered', 'runs': study['run_count'], 'response': source['file']})
    except Exception as error:
        study['run_report_status'] = 'failed'
        database['issues'].append({'study': accession, 'stage': 'run-report-recovery', 'error': str(error)})
        receipt.append({'study': accession, 'status': 'failed', 'error': str(error)})
    _save(folder / 'database.json', database)
    print(json.dumps(receipt[-1]), flush=True)
_save(folder / 'run-report-recovery.json', receipt)
