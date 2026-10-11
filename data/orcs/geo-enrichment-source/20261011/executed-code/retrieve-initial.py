"""Bounded whole-ORCS metadata run; reuse verified metadata and fetch brief GSMs.

Run-local orchestration around the accepted production accession adapter. Native
metadata and route evidence remain separate from workbook projection. No file
contents, article bodies, experimental tables or screen classification are used.
"""
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import time
from urllib.parse import parse_qsl, urlencode, urlsplit
from unittest.mock import patch

from deathmap_ai import geo_enrichment as geo
import saved_native

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
PMIDS = []
ORIGINAL_GET = geo._Requests.get
CACHE = {}
GLOBAL_START = time.monotonic()


def _save(name, value):
    (BASE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


def _load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def _key(url):
    parsed = urlsplit(url)
    return (parsed.netloc, parsed.path, tuple(sorted(parse_qsl(parsed.query))))


def _cache_inventory():
    """Index receipts only; verify saved bytes when a matching response is reused."""
    saved_native.inventory(ROOT)
    for path in sorted((ROOT / 'outputs/geo').glob('**/requests.json')):
        if BASE in path.parents:
            continue
        for receipt in _load(path):
            member = receipt.get('file') or receipt.get('raw_file')
            if member and receipt.get('sha256') and not receipt.get('error'):
                CACHE[_key(receipt['url'])] = (path.parent / member, receipt)


def _get(transport, url):
    """Copy byte-verified cached responses with original time/hash provenance."""
    if time.monotonic() - GLOBAL_START > 7200:
        raise RuntimeError('120-minute full-ORCS checkpoint reached')
    derived = saved_native.selected_response(url)
    if derived:
        body, sources = derived
        filename = f'selected-{len(transport.receipts):04d}.response'
        (transport.folder / filename).write_bytes(body)
        transport.receipts.append({'url': url, 'file': 'raw/' + filename,
            'sha256': hashlib.sha256(body).hexdigest(), 'response_kind': 'selected_cached_native_records',
            'selection_utc': datetime.now(timezone.utc).isoformat(), 'parents': sources})
        geo._save(transport.folder.parent / 'requests.json', transport.receipts)
        return body, 'raw/' + filename
    match = CACHE.get(_key(url))
    if match:
        path, old = match
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != old['sha256']:
            raise ValueError('Source cache hash mismatch: ' + str(path))
        filename = f'cache-{len(transport.receipts):04d}.response'
        (transport.folder / filename).write_bytes(body)
        transport.receipts.append({
            'url': url, 'file': 'raw/' + filename, 'sha256': old['sha256'],
            'retrieved_utc': old.get('retrieved_utc') or old.get('retrieved_at'),
            'reused_utc': datetime.now(timezone.utc).isoformat(),
            'reused_from': str(path), 'original_url': old['url']})
        geo._save(transport.folder.parent / 'requests.json', transport.receipts)
        return body, 'raw/' + filename
    existing = len(transport.receipts)
    body, member = ORIGINAL_GET(transport, url)
    original = transport.folder.parent / member
    unique = transport.folder / f'live-{existing:05d}.response'
    original.rename(unique)
    member = 'raw/' + unique.name
    transport.receipts[-1]['file'] = member
    geo._save(transport.folder.parent / 'requests.json', transport.receipts)
    receipt = transport.receipts[-1]
    CACHE[_key(url)] = (transport.folder.parent / member, receipt)
    return body, member


def _soft_records(body, prefix):
    """Retain every repeated native metadata field and reject experimental tables."""
    records, current = {}, None
    for line in body.decode('utf-8').splitlines():
        if '_table_begin' in line.lower():
            raise ValueError('Experimental data table returned in metadata-only request')
        if line.startswith('^' + prefix.upper() + ' = '):
            identifier = line.split(' = ', 1)[1]
            if identifier in records:
                raise ValueError('Duplicate native record identity')
            current = {}
            records[identifier] = current
        elif current is not None and line.startswith('!' + prefix + '_') and ' = ' in line:
            key, value = line.split(' = ', 1)
            current.setdefault(key[1:], []).append(value)
    for accession, fields in records.items():
        if fields.get(prefix + '_geo_accession') != [accession]:
            raise ValueError('SOFT identity mismatch')
    return records


def _discover():
    _cache_inventory()
    index_path = ROOT / 'data/orcs/publication-index.json'
    index = _load(index_path)
    global PMIDS
    selected = []
    for original in index:
        publication = dict(original)
        publication['_input_provenance'] = {
            'file': str(index_path), 'sha256': hashlib.sha256(index_path.read_bytes()).hexdigest(),
            'locator': 'PUBLICATION_ID=' + str(publication['PUBLICATION_ID'])}
        selected.append(publication)
    PMIDS = [str(p.get('PMID') or 'orcs-' + str(p['PUBLICATION_ID'])) for p in selected]
    _save('selected-publications.json', selected)
    _save('run-manifest.json', {'started_utc': datetime.now(timezone.utc).isoformat(),
                              'pmids': PMIDS, 'selection': 'All ORCS publication-index records; candidate retrieval, not a coverage benchmark',
                              'scope': 'Accession routes, brief Series and GSM metadata; one plain workbook',
                              'python': sys.version, 'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                              'adapter_sha256': hashlib.sha256(Path(geo.__file__).read_bytes()).hexdigest(),
                              'limits': {'minutes': 120, 'unique_gsms': 50000, 'sample_batches': 600,
                                         'sample_batch_bytes': 20_000_000},
                              'status': 'discovering'})
    failures, results = [], {}
    with patch.object(geo._Requests, 'get', _get):
        for publication in selected:
            pmid = str(publication.get('PMID') or 'orcs-' + str(publication['PUBLICATION_ID']))
            target = BASE / 'publications' / pmid
            try:
                if target.exists():
                    manifest = _load(target / 'manifest.json')
                    if manifest['status'] != 'complete':
                        raise ValueError('Existing partial publication run needs a separate resume decision')
                    for receipt in _load(target / 'requests.json'):
                        if receipt.get('file') and hashlib.sha256((target / receipt['file']).read_bytes()).hexdigest() != receipt['sha256']:
                            raise ValueError('Prior response hash mismatch')
                    result = _load(target / 'accessions.json')
                else:
                    result = geo.identify_geo(publication, target)
                results[pmid] = result
                print(json.dumps({'pmid': pmid, 'gses': result['total_gse_count']}), flush=True)
            except Exception as error:
                failures.append({'pmid': pmid, 'stage': 'accession_identification', 'error': str(error)})
                print(json.dumps(failures[-1]), flush=True)
            _save('discovery-results.json', results)
            _save('issues.json', failures)
    series = {}
    for pmid, result in results.items():
        directory = BASE / 'publications' / pmid
        identities = _load(directory / 'series-identities.json')
        for accession, identity in identities.items():
            raw = directory / identity['source_file']
            record = _soft_records(raw.read_bytes(), 'Series')
            if set(record) != {accession}:
                raise ValueError('Series response coverage mismatch')
            series.setdefault(accession, {'fields': record[accession], 'pmids': [],
                                         'source_file': str(raw.relative_to(BASE))})['pmids'].append(pmid)
    _save('series-metadata.json', series)
    samples = {gsm for record in series.values() for gsm in record['fields'].get('Series_sample_id', [])}
    count = {'publications_completed': len(results), 'publications_failed': len(failures),
             'unique_gses': len(series), 'unique_gsms': len(samples),
             'series_sample_counts': {g: len(r['fields'].get('Series_sample_id', [])) for g, r in series.items()}}
    _save('sample-count-checkpoint.json', count)
    print(json.dumps(count), flush=True)


def _samples():
    _cache_inventory()
    series = _load(BASE / 'series-metadata.json')
    expected_all = {gsm for record in series.values() for gsm in record['fields'].get('Series_sample_id', [])}
    if len(expected_all) > 50000:
        raise RuntimeError(f'{len(expected_all)} unique GSMs exceeds the 50000-sample checkpoint')
    native = _load(BASE / 'sample-metadata.json') if (BASE / 'sample-metadata.json').exists() else {}
    folder = BASE / 'samples'
    if folder.exists():
        transport = object.__new__(geo._Requests)
        transport.folder = folder / 'raw'
        transport.receipts = _load(folder / 'requests.json') if (folder / 'requests.json').exists() else []
        transport.started, transport.attempts = time.monotonic(), 0
        for receipt in transport.receipts:
            if receipt.get('file'):
                path = folder / receipt['file']
                if hashlib.sha256(path.read_bytes()).hexdigest() != receipt['sha256']:
                    raise ValueError('Sample response cache hash mismatch')
                CACHE[_key(receipt['url'])] = (path, receipt)
    else:
        folder.mkdir()
        transport = geo._Requests(folder / 'raw')
    issues = _load(BASE / 'issues.json')
    sample_sets = sorted(series, key=lambda g: (len(series[g]['fields'].get('Series_sample_id', [])), g))
    for accession in sample_sets:
        expected = set(series[accession]['fields'].get('Series_sample_id', []))
        if expected <= set(native):
            continue
        if transport.attempts >= 80:
            transport.attempts = 0
            transport.started = time.monotonic()
        url = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?' + urlencode(
            {'acc': accession, 'targ': 'gsm', 'form': 'text', 'view': 'brief'})
        try:
            body, source = _get(transport, url)
            if len(body) > 20_000_000:
                raise RuntimeError('Sample batch exceeds the 20 MB metadata checkpoint')
            returned = _soft_records(body, 'Sample')
            if set(returned) != expected:
                raise ValueError(f'Sample coverage mismatch for {accession}: expected {len(expected)}, returned {len(returned)}')
            for gsm, fields in returned.items():
                if gsm in native and native[gsm]['fields'] != fields:
                    issues.append({'gse': accession, 'gsm': gsm, 'stage': 'sample_metadata',
                                   'error': 'Conflicting metadata in repeated sample response; first record retained, both raw responses preserved'})
                else:
                    native[gsm] = {'fields': fields, 'source_file': 'samples/' + source}
            _save('sample-metadata.json', native)
            print(json.dumps({'gse': accession, 'samples_in_batch': len(returned), 'unique_samples_so_far': len(native)}), flush=True)
        except Exception as error:
            issues.append({'gse': accession, 'stage': 'sample_metadata', 'error': str(error)})
            print(json.dumps(issues[-1]), flush=True)
        _save('issues.json', issues)
    _save('sample-metadata.json', native)
    _save('sample-retrieval-status.json', {'expected_unique_gsms': len(expected_all),
                                        'retrieved_unique_gsms': len(native), 'missing_gsms': sorted(expected_all - set(native)),
                                        'requests': len(transport.receipts)})


def _join(fields, key):
    return '\n'.join(fields.get(key, [])) or None


def _project():
    """Produce plain data tables, preserving repeated fields and PMID/GSE/GSM membership."""
    series = _load(BASE / 'series-metadata.json')
    samples = _load(BASE / 'sample-metadata.json')
    results = _load(BASE / 'discovery-results.json')
    tables = {name: [] for name in ['Series Records', 'Series Hierarchy', 'File Inventory',
                                   'Repository Identifiers', 'Sample Metadata',
                                   'Contributors and Contacts', 'Discovery Evidence']}
    for gse, record in series.items():
        fields = record['fields']
        for pmid in record['pmids']:
            base = {'PMID': None if pmid.startswith('orcs-') else pmid, 'GSE': gse}
            row = dict(base)
            for key, values in fields.items():
                if not any(x in key for x in ('contact_', 'contributor', 'supplementary_file', 'sample_id', 'relation')):
                    row[key.removeprefix('Series_')] = '\n'.join(values)
            row['sample_count'] = len(fields.get('Series_sample_id', []))
            row['Source File'] = record['source_file']
            tables['Series Records'].append(row)
            for relation in fields.get('Series_relation', []):
                hierarchy = re.fullmatch(r'(SuperSeries of|SubSeries of): (GSE\d+)', relation)
                if hierarchy:
                    tables['Series Hierarchy'].append({**base, 'Related GSE': hierarchy[2],
                                                       'Relationship': hierarchy[1], 'Native Value': relation,
                                                       'Source File': record['source_file']})
                else:
                    matched = re.search(r'(PRJ(?:NA|EB|DB)\d+|SRP\d+|ERP\d+|DRP\d+)', relation)
                    tables['Repository Identifiers'].append({**base, 'GSM': None, 'Entity Level': 'Series',
                        'Resource': relation.split(':', 1)[0], 'Identifier': matched[0] if matched else None,
                        'Native Field': 'Series_relation', 'Native Value': relation, 'Source File': record['source_file']})
            for key in ('Series_platform_id', 'Series_sample_id'):
                for value in fields.get(key, []):
                    tables['Repository Identifiers'].append({**base, 'GSM': value if key.endswith('sample_id') else None,
                        'Entity Level': 'Series', 'Resource': 'GEO Sample' if key.endswith('sample_id') else 'GEO Platform',
                        'Identifier': value, 'Native Field': key, 'Native Value': value, 'Source File': record['source_file']})
            _files_contacts(tables, base, fields, 'Series', record['source_file'])
            for gsm in fields.get('Series_sample_id', []):
                if gsm not in samples:
                    continue
                native = samples[gsm]
                sample_row = {**base, 'GSM': gsm}
                for key, values in native['fields'].items():
                    if not any(x in key for x in ('contact_', 'contributor', 'supplementary_file', 'relation')):
                        sample_row[key.removeprefix('Sample_')] = '\n'.join(values)
                sample_row['Source File'] = native['source_file']
                tables['Sample Metadata'].append(sample_row)
                _files_contacts(tables, {**base, 'GSM': gsm}, native['fields'], 'Sample', native['source_file'])
                for key, values in native['fields'].items():
                    if key in ('Sample_relation', 'Sample_platform_id'):
                        for value in values:
                            matched = re.search(r'(SAM(?:N|EA|D)\d+|SRX\d+|ERX\d+|DRX\d+|GPL\d+)', value)
                            tables['Repository Identifiers'].append({**base, 'GSM': gsm, 'Entity Level': 'Sample',
                                'Resource': value.split(':', 1)[0] if key == 'Sample_relation' else 'GEO Platform',
                                'Identifier': matched[0] if matched else None, 'Native Field': key,
                                'Native Value': value, 'Source File': native['source_file']})
    for pmid, result in results.items():
        for evidence in result['evidence']:
            row = {'PMID': pmid, 'GSE': evidence['gse'], 'Record Kind': 'discovery_observation'}
            row.update({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value
                        for key, value in evidence.items()})
            row['Source File'] = 'publications/' + pmid + '/' + evidence['source_file']
            tables['Discovery Evidence'].append(row)
        # Successful empty routes must remain visible without inventing GSE records.
        for route, state in result['routes'].items():
            tables['Discovery Evidence'].append({'PMID': pmid, 'GSE': None, 'Record Kind': 'route_status',
                                                 'route': route, 'status': state['status'],
                                                 'distinct_gse_count': state['distinct_gse_count'],
                                                 'Route Details': json.dumps(state, ensure_ascii=False)})
    issues = _load(BASE / 'issues.json')
    if issues:
        tables['Retrieval Issues'] = issues
    _save('workbook-data.json', tables)
    verification = {'sheet_rows': {name: len(rows) for name, rows in tables.items()},
                    'unique_gses': len(series), 'unique_gsms': len(samples), 'pmids': list(results),
                    'issues': len(issues)}
    for path in BASE.glob('**/requests.json'):
        for receipt in _load(path):
            if receipt.get('file'):
                if hashlib.sha256((path.parent / receipt['file']).read_bytes()).hexdigest() != receipt['sha256']:
                    raise ValueError('Run response hash mismatch')
    PMIDS = [str(p.get('PMID') or 'orcs-' + str(p['PUBLICATION_ID'])) for p in _load(BASE / 'selected-publications.json')]
    if set(results) != set(PMIDS):
        verification['incomplete_publications'] = sorted(set(PMIDS) - set(results))
    _save('projection-verification.json', verification)
    manifest = _load(BASE / 'run-manifest.json')
    manifest.update(status='metadata_projected', finished_utc=datetime.now(timezone.utc).isoformat(),
                    projection=verification)
    _save('run-manifest.json', manifest)
    print(json.dumps(verification), flush=True)


def _files_contacts(tables, base, fields, entity, source):
    """Keep deposit file names and contact fields without following any file URLs."""
    for key, values in fields.items():
        if 'supplementary_file' in key:
            for value in values:
                tables['File Inventory'].append({**base, 'Entity Level': entity, 'Native Field': key,
                    'Filename': urlsplit(value).path.rsplit('/', 1)[-1] if value.startswith(('ftp:', 'http:','https:')) else value,
                    'File URL or Native Value': value, 'Source File': source})
    row = {**base, 'Entity Level': entity}
    for key, values in fields.items():
        if 'contact_' in key or 'contributor' in key:
            row[key.removeprefix(entity + '_')] = '\n'.join(values)
    if len(row) > len(base) + 1:
        row['Source File'] = source
        tables['Contributors and Contacts'].append(row)


if __name__ == '__main__':
    {'discover': _discover, 'samples': _samples, 'project': _project}[sys.argv[1]]()
