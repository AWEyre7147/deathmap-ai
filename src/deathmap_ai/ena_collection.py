"""Collect metadata-only ENA evidence for the saved ORCS publication database.

This CLI uses exact PubMed cross-references, complete publication titles and saved
GEO/PubMed study identifiers. Native study XML resolves aliases; run reports
describe child records without downloading experimental files. Ambiguous source
publication links survive separately from discovery observations. Exact cached
responses preserve their original retrieval date. This is not screen attribution.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import platform
import re
import shutil
import threading
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit
from urllib.request import Request, urlopen

API = 'https://www.ebi.ac.uk/ena/'
STRATEGY = 'ena-orcs-metadata-v1'
STUDY_ID = re.compile(r'(?:PRJ[A-Z]+|[SED]RP)\d+')
REPORT_FIELDS = ['run_accession', 'study_accession', 'secondary_study_accession',
    'sample_accession', 'experiment_accession', 'scientific_name', 'sample_title',
    'sample_description', 'experiment_title', 'library_strategy', 'library_source',
    'library_selection', 'library_layout', 'instrument_platform', 'instrument_model',
    'library_construction_protocol', 'read_count', 'base_count', 'fastq_ftp',
    'fastq_md5', 'fastq_bytes']


def _load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def _save(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _key(url):
    parsed = urlsplit(url)
    return parsed.netloc, parsed.path, tuple(sorted(parse_qsl(parsed.query)))


def _phrase(value):
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


class LimitReached(RuntimeError):
    """Stop the run at an operational boundary without reporting zero hits."""


class Transport:
    """Preserve and cache exact HTTP responses under bounded concurrent access.

    Parameters
    ----------
    folder : Path
        New or explicitly resumed run directory.
    cache_roots : iterable of Path
        Prior metadata receipt directories. These supply responses, not queries.
    opener : callable
        Injectable HTTP opener for offline testing.

    Notes
    -----
    Four workers share a 0.2-second request-start interval. Limits: 3,000 live
    attempts, four hours, 32 MiB per response and 2 GiB preserved response bytes.
    Transient failures allow two retries. Failed responses never become no hits.
    """
    def __init__(self, folder, cache_roots=(), opener=urlopen):
        self.folder, self.opener = Path(folder), opener
        (self.folder / 'raw').mkdir(exist_ok=True)
        self.lock = threading.Lock()
        self.started, self.last = time.monotonic(), 0.0
        self.receipts = _load(self.folder / 'requests.json') if (self.folder / 'requests.json').exists() else []
        self.attempts = sum(not x.get('reused_from') for x in self.receipts)
        self.total = sum(x.get('bytes', 0) for x in self.receipts)
        self.cache = {}
        for root in [*cache_roots, self.folder]:
            for receipt in sorted(Path(root).rglob('requests.json')):
                for item in _load(receipt):
                    if item.get('file') and item.get('sha256') and not item.get('error') and not item.get('incomplete'):
                        self.cache[_key(item['url'])] = (receipt.parent / item['file'], item)

    def _record(self, entry, body=None):
        with self.lock:
            if body is not None:
                if self.total + len(body) > 2 * 1024**3:
                    raise LimitReached('2 GiB metadata response budget reached')
                name = 'raw/' + hashlib.sha256(entry['url'].encode()).hexdigest()[:24] + '-' + hashlib.sha256(body).hexdigest()[:24] + '.response'
                (self.folder / name).write_bytes(body)
                entry.update(file=name, bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
                self.total += len(body)
                if not entry.get('error'):
                    self.cache[_key(entry['url'])] = (self.folder / name, dict(entry))
            self.receipts.append(entry)
            _save(self.folder / 'requests.json', self.receipts)

    def get(self, url):
        """Return response bytes and its receipt, preserving failures explicitly.

        Parameters
        ----------
        url : str
            Public ENA metadata endpoint URL.

        Returns
        -------
        tuple
            Raw bytes and provenance receipt; cached bytes are hash checked.

        Raises
        ------
        LimitReached
            An operational request, time or response-size boundary was reached.
        OSError
            Retrieval fails after bounded retries.
        """
        with self.lock:
            cached = self.cache.get(_key(url))
        if cached:
            path, old = cached
            body = path.read_bytes()
            if hashlib.sha256(body).hexdigest() != old['sha256']:
                raise ValueError('Cached metadata hash mismatch: ' + str(path))
            entry = dict(old, url=url, reused_from=str(path), reused_utc=_now())
            self._record(entry, body)
            return body, entry
        for attempt in range(3):
            with self.lock:
                if self.attempts >= 3000 or time.monotonic() - self.started > 14400:
                    raise LimitReached('Live request/time checkpoint reached')
                time.sleep(max(0, self.last + 0.2 - time.monotonic()))
                self.last = time.monotonic()
                self.attempts += 1
            entry = {'url': url, 'retrieved_utc': _now(), 'attempt': attempt + 1}
            body = None
            try:
                with self.opener(Request(url, headers={'User-Agent': 'DeathMap-AI/0.1 ENA metadata'}), timeout=40) as response:
                    body = response.read(32 * 1024**2 + 1)
                    entry['status'] = response.status
                if len(body) > 32 * 1024**2:
                    raise LimitReached('32 MiB response checkpoint: ' + url)
                self._record(entry, body)
                return body, entry
            except LimitReached:
                raise
            except (HTTPError, URLError, TimeoutError, OSError) as error:
                entry['error'] = str(error)
                if isinstance(error, HTTPError):
                    entry['status'] = error.code
                    body = error.read(100000)
                self._record(entry, body)
                transient = not isinstance(error, HTTPError) or error.code in (408, 429) or error.code >= 500
                if not transient or attempt == 2:
                    raise OSError(str(error)) from error
                time.sleep(2 ** attempt)


def parse_study(body):
    """Read one native PROJECT/STUDY XML, retaining aliases and exact links.

    Parameters
    ----------
    body : bytes or str
        Browser API XML for a single study accession.

    Returns
    -------
    dict
        Native identifiers, citations, hierarchy, descriptions and attributes.

    Raises
    ------
    ValueError
        XML does not contain exactly one project/study with a valid identifier.
    """
    root = ET.fromstring(body)
    records = [x for x in root.iter() if x.tag in ('PROJECT', 'STUDY')]
    if len(records) != 1:
        raise ValueError('Expected one PROJECT/STUDY XML record')
    record = records[0]
    primary = record.findtext('./IDENTIFIERS/PRIMARY_ID') or record.get('accession')
    if not STUDY_ID.fullmatch(primary or ''):
        raise ValueError('Invalid native study identifier')
    identifiers = [{'type': x.tag, 'value': x.text, 'attributes': x.attrib} for x in record.findall('./IDENTIFIERS/*')]
    links = [{'db': x.findtext('DB'), 'id': x.findtext('ID')} for x in record.iter('XREF_LINK')]
    return {'accession': primary, 'aliases': sorted({primary, *[x['value'] for x in identifiers if STUDY_ID.fullmatch(x['value'] or '')]}),
        'identifiers': identifiers, 'native_record_type': record.tag, 'native_attributes': record.attrib,
        'title': record.findtext('TITLE') or record.findtext('./DESCRIPTOR/STUDY_TITLE'),
        'description': record.findtext('DESCRIPTION') or record.findtext('./DESCRIPTOR/STUDY_DESCRIPTION'),
        'organism': [x.text for x in record.iter('SCIENTIFIC_NAME')], 'links': links,
        'pmids': sorted({x['id'] for x in links if (x['db'] or '').upper() == 'PUBMED' and x['id']}),
        'attributes': [{'tag': x.findtext('TAG'), 'value': x.findtext('VALUE')} for x in record.iter() if x.tag in ('PROJECT_ATTRIBUTE', 'STUDY_ATTRIBUTE')],
        'hierarchy': [{'relationship': 'Parent project' if x.tag == 'PARENT_PROJECT' else 'Child project', 'accession': x.get('accession')} for x in record.iter() if x.tag in ('PARENT_PROJECT', 'CHILD_PROJECT')]}


def _search(transport, endpoint, params, route):
    """Page a complete bounded study search; unknown schema is not an empty hit."""
    observations, receipts = [], []
    for page in range(20):
        query = dict(params, limit=1000, offset=page * 1000)
        url = endpoint + '?' + urlencode(query)
        body, receipt = transport.get(url)
        rows = json.loads(body)
        if not isinstance(rows, list):
            raise ValueError('Unexpected search schema: ' + body[:150].decode(errors='replace'))
        receipts.append({'url': url, 'file': receipt['file'], 'sha256': receipt['sha256']})
        for i, row in enumerate(rows):
            accession = row.get('Target Primary Accession') if route == 'pmid-xref' else row.get('study_accession')
            if not STUDY_ID.fullmatch(accession or ''):
                raise ValueError('Unexpected study search identifier')
            observations.append({'accession': accession, 'route': route, 'evidence': {'response': receipt['file'], 'row': page * 1000 + i, 'native_record': row}})
        if len(rows) < 1000:
            return observations, receipts
    raise LimitReached('20-page study search checkpoint reached')


def _recover_title(transport, title):
    """Retry failed full-title syntax as TSV, then the same complete EBI phrase.

    This is a bounded alternate encoding of the accepted route, never a shorter
    title search. Invalid/error responses remain failures, not empty hits.
    """
    with transport.lock:
        transport.title_recoveries = getattr(transport, 'title_recoveries', 0) + 1
        if transport.title_recoveries > 10:
            raise LimitReached('More than ten failed full-title queries; checkpoint required')
    params = {'result': 'study', 'query': 'study_title=' + _phrase(title), 'format': 'tsv',
              'fields': 'study_accession,study_title', 'limit': 1000}
    try:
        body, receipt = transport.get(API + 'portal/api/search?' + urlencode(params))
        reader = csv.DictReader(io.StringIO(body.decode()), delimiter='\t')
        if 'study_accession' not in (reader.fieldnames or []):
            raise ValueError('Invalid full-title TSV response')
        rows = list(reader)
        if len(rows) >= 1000:
            raise LimitReached('Full-title recovery page cap')
    except LimitReached:
        raise
    except Exception:
        url = 'https://www.ebi.ac.uk/ebisearch/ws/rest/sra-study?' + urlencode(
            {'query': _phrase(title), 'format': 'json', 'fields': 'acc,study_title,PUBMED', 'size': 100})
        body, receipt = transport.get(url)
        native = json.loads(body)
        if 'hitCount' not in native or native['hitCount'] > len(native.get('entries', [])):
            raise ValueError('Incomplete full-title recovery response')
        rows = [dict(row, study_accession=row['id']) for row in native.get('entries', [])]
    if any(not STUDY_ID.fullmatch(row.get('study_accession', '')) for row in rows):
        raise ValueError('Invalid recovered study accession')
    return ([{'accession': row['study_accession'], 'route': 'complete-title',
              'evidence': {'response': receipt['file'], 'row': i, 'native_record': row,
                           'recovery_interface': receipt['url']}} for i, row in enumerate(rows)], [receipt])


def _discover(transport, pub, saved):
    key = pub.get('PMID') or 'ORCS:' + pub['PUBLICATION_ID']
    result = {'key': key, 'publication': pub, 'observations': list(saved), 'routes': [], 'issues': []}
    queries = [('complete-title', API + 'portal/api/search', {'result': 'study', 'query': 'study_title=' + _phrase(pub['TITLE']), 'format': 'json'})]
    if pub.get('PMID'):
        queries.insert(0, ('pmid-xref', API + 'xref/rest/json/search', {'source': 'PubMed', 'source_accession': pub['PMID'], 'target': 'study'}))
    for route, endpoint, params in queries:
        try:
            found, receipts = _search(transport, endpoint, params, route)
            result['observations'].extend(found)
            result['routes'].append({'route': route, 'status': 'complete', 'hits': len(found), 'requests': receipts})
        except LimitReached:
            raise
        except Exception as error:
            if route == 'complete-title':
                try:
                    found, receipts = _recover_title(transport, pub['TITLE'])
                    result['observations'].extend(found)
                    result['routes'].append({'route': route, 'status': 'recovered', 'hits': len(found), 'requests': receipts})
                    result.setdefault('resolved_issues', []).append({'route': route, 'error': str(error)})
                    continue
                except LimitReached:
                    raise
                except Exception as recovery_error:
                    result['issues'].append({'route': route, 'error': str(error), 'recovery_error': str(recovery_error)})
            else:
                result['issues'].append({'route': route, 'error': str(error)})
    result['status'] = 'complete_with_issues' if result['issues'] else 'complete'
    return result


def _seeds(publications, geo, pubmed):
    """Preserve each source association while collapsing exact duplicate seeds."""
    saved, geo_map = {}, {}
    for pub in publications:
        key = pub.get('PMID') or 'ORCS:' + pub['PUBLICATION_ID']
        saved[key] = []
    for accession, series in geo['series'].items():
        ids = sorted(set(STUDY_ID.findall(' '.join(series['fields'].get('Series_relation', [])))))
        for key in series['publication_keys']:
            if key.startswith('orcs-'):
                key = 'ORCS:' + key.removeprefix('orcs-')
            if key not in saved:
                continue
            geo_map.setdefault(key, []).append({'accession': accession, 'seed_accessions': ids, 'source_file': series['source_file']})
            for identifier in ids:
                saved[key].append({'accession': identifier, 'route': 'saved-geo-study-link', 'evidence': {'source': 'geo-enrichment', 'series': accession,
                    'source_file': series['source_file'], 'native_geo_pmids': series['fields'].get('Series_pubmed_id', []), 'native_relations': series['fields'].get('Series_relation', [])}})
    for i, row in enumerate(pubmed['rows']['Repository Records']):
        if row[0] in saved and row[1] == 'BioProject' and STUDY_ID.fullmatch(row[2] or ''):
            saved[row[0]].append({'accession': row[2], 'route': 'saved-pubmed-study-link', 'evidence': {'source': 'pubmed-enrichment', 'table': 'Repository Records', 'row': i}})
    for i, row in enumerate(pubmed['rows']['SRA Accessions']):
        if row[0] in saved:
            for accession in set((row[2], row[5])):
                if STUDY_ID.fullmatch(accession or ''):
                    saved[row[0]].append({'accession': accession, 'route': 'saved-pubmed-study-link', 'evidence': {'source': 'pubmed-enrichment', 'table': 'SRA Accessions', 'row': i}})
    # Preserve one observation per accession/route/source locator; don't multiply
    # requests or study counts for the many runs supplying the same study link.
    for key, rows in saved.items():
        unique = {}
        for row in rows:
            identity = row['accession'], row['route'], row['evidence'].get('series')
            if identity in unique:
                unique[identity].setdefault('additional_source_locators', []).append(row['evidence'])
            else:
                unique[identity] = row
        saved[key] = list(unique.values())
    return saved, geo_map


def _apply_metadata_only_policy(studies, accessions):
    """Keep selected broad records, leaving unexpanded child counts unavailable."""
    for accession in accessions:
        if accession in studies:
            study = studies[accession]
            study.update(run_report_status='not-expanded-broad-collection',
                run_report_omission='Owner-selected project-level relationship; collection-wide child metadata not expanded', runs=[])
            for field in ('sample_count', 'experiment_count', 'run_count'):
                study.pop(field, None)


def run(root, folder, cache_roots=(), resume=False, metadata_only_projects=(),
        publication_index=None, geo_database=None, pubmed_database=None, template=None):
    """Enrich all saved ORCS publications in one new or explicitly resumed run.

    Parameters
    ----------
    root : Path
        Repository root containing the three saved source databases.
    folder : Path
        Run directory; existing files are refused unless resume is explicit.
    cache_roots : iterable of Path
        Prior metadata caches; hashes are verified before response reuse.
    resume : bool
        Reuse completed request responses in this same run, without overwriting
        experimental or reviewer-owned artifacts.
    metadata_only_projects : iterable of str
        Owner-selected broad projects whose native descriptions and hierarchy
        are retained without expanding collection-wide sequencing runs.

    Returns
    -------
    dict
        Native canonical metadata, route observations, issues and selected rows.

    Raises
    ------
    LimitReached
        Operational checkpoint reached; receipts and completed state survive.
    ValueError
        Resume inputs or saved source metadata do not match the manifest.
    """
    from .ena_projection import project
    root, folder = Path(root), Path(folder)
    if folder.exists() and not resume:
        raise FileExistsError('Use a new ENA run directory or explicit resume')
    folder.mkdir(parents=True, exist_ok=True)
    paths = {name: root / ('data/orcs/' + name + '.json') for name in ('publication-index', 'geo-enrichment', 'pubmed-enrichment')}
    for key, value in [('publication-index', publication_index), ('geo-enrichment', geo_database), ('pubmed-enrichment', pubmed_database)]:
        if value is not None:
            paths[key] = Path(value)
    hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
    template_path = Path(template or root / 'data/templates/ENA-Enrichment.xlsx')
    template_manifest = _load(template_path.with_suffix('.manifest.json'))
    if hashlib.sha256(template_path.read_bytes()).hexdigest() != template_manifest['sha256']:
        raise ValueError('Registered ENA template hash mismatch')
    hashes['ena-template'] = template_manifest['sha256']
    manifest_path = folder / 'manifest.json'
    if manifest_path.exists() and _load(manifest_path)['input_hashes'] != hashes:
        raise ValueError('ENA resume input hashes changed')
    manifest = {'strategy': STRATEGY, 'started_utc': _now(), 'python': platform.python_version(), 'input_hashes': hashes,
        'source_paths': {k: str(p.resolve()) for k, p in paths.items()},
        'template': template_manifest,
        'metadata_only_projects': sorted(set(metadata_only_projects)),
        'limits': {'workers': 4, 'minimum_start_interval_seconds': 0.2, 'request_attempts': 3000, 'response_bytes': 32 * 1024**2,
            'total_response_bytes': 2 * 1024**3, 'hours': 4, 'retries': 2, 'search_page_rows': 1000, 'search_pages': 20,
            'full_passes': 1}, 'routes': ['pmid-xref', 'complete-title', 'saved-geo-study-link', 'saved-pubmed-study-link', 'geo-accession-fallback'],
        'exclusions': ['shorter titles', 'DOI/PMCID searches', 'duplicate EBI PMID search', 'experimental files', 'parent project traversal', 'screen attribution']}
    if not manifest_path.exists():
        _save(manifest_path, manifest)
        snapshots = folder / 'executed-code'
        snapshots.mkdir(exist_ok=True)
        for name in ('ena_collection.py', 'ena_projection.py'):
            shutil.copyfile(Path(__file__).with_name(name), snapshots / name)
        for name, path in paths.items():
            shutil.copyfile(path, folder / (name + '-input.json'))
    inputs = {k: _load(p) for k, p in paths.items()}
    saved, geo_map = _seeds(inputs['publication-index'], inputs['geo-enrichment'], inputs['pubmed-enrichment'])
    transport = Transport(folder, cache_roots)
    database = {'schema_version': 'ena-enrichment/1.0', 'strategy': STRATEGY, 'source_package': str(folder.resolve()),
        'publications': [], 'studies': {}, 'study_failures': {}, 'issues': [], 'status': 'running'}
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = [pool.submit(_discover, transport, pub, saved[pub.get('PMID') or 'ORCS:' + pub['PUBLICATION_ID']]) for pub in inputs['publication-index']]
        for job in as_completed(jobs):
            database['publications'].append(job.result())
            if len(database['publications']) % 20 == 0:
                _save(folder / 'database.json', database)
                print(json.dumps({'stage': 'publications', 'processed': len(database['publications']), 'total': len(jobs)}), flush=True)
    database['publications'].sort(key=lambda x: int(x['publication']['PUBLICATION_ID']))
    _save(folder / 'database.json', database)
    # Project IDs resolve first. XML aliases avoid a second request for the same
    # study nominated as both PRJNA and SRP; unexpected aliases remain conflicts.
    candidates = sorted({o['accession'] for p in database['publications'] for o in p['observations']}, key=lambda x: (not x.startswith('PRJ'), x))
    aliases = {}

    def retrieve(accession):
        body, receipt = transport.get(API + 'browser/api/xml/' + accession)
        record = parse_study(body)
        record.update(source_response=receipt['file'], source_url=receipt['url'], source_sha256=receipt['sha256'], associations=[], runs=[])
        return accession, record

    def collect(accessions):
        with ThreadPoolExecutor(max_workers=4) as pool:
            jobs = {pool.submit(retrieve, accession): accession for accession in accessions}
            for number, job in enumerate(as_completed(jobs), 1):
                accession = jobs[job]
                try:
                    _, study = job.result()
                    primary = study['accession']
                    for alias in study['aliases']:
                        if alias in aliases and aliases[alias] != primary:
                            raise ValueError('Native study alias conflict: ' + alias)
                    if accession not in study['aliases']:
                        raise ValueError('Requested accession not present in native identifiers')
                    database['studies'].setdefault(primary, study)
                    aliases.update({alias: primary for alias in study['aliases']})
                except LimitReached:
                    raise
                except Exception as error:
                    database['study_failures'][accession] = {'error': str(error)}
                if number % 20 == 0:
                    _save(folder / 'database.json', database)
                    print(json.dumps({'stage': 'study-xml', 'processed': number, 'batch': len(jobs), 'studies': len(database['studies']), 'failed': len(database['study_failures'])}), flush=True)
    collect([x for x in candidates if x.startswith('PRJ')])
    collect([x for x in candidates if x not in aliases and not x.startswith('PRJ')])
    # Only GEO records without a resolved saved study ID need a live GEO query.
    fallback = [(p, g) for p in database['publications'] for g in geo_map.get(p['key'], []) if not any(x in aliases for x in g['seed_accessions'])]
    for pub, geo in fallback:
        try:
            found, receipts = _search(transport, API + 'portal/api/search', {'result': 'study', 'query': 'geo_accession=' + _phrase(geo['accession']), 'format': 'json'}, 'geo-accession-fallback')
            pub['observations'].extend(found)
            pub['routes'].append({'route': 'geo-accession-fallback', 'geo': geo['accession'], 'hits': len(found), 'status': 'complete', 'requests': receipts})
            collect([x['accession'] for x in found if x['accession'] not in aliases])
        except LimitReached:
            raise
        except Exception as error:
            pub['issues'].append({'route': 'geo-accession-fallback', 'geo': geo['accession'], 'error': str(error)})
    for pub in database['publications']:
        for observation in pub['observations']:
            primary = aliases.get(observation['accession'])
            if primary:
                study = database['studies'][primary]
                pmid = pub['publication'].get('PMID')
                status = ('search-pmid-unavailable' if not pmid else 'native-pmid-match' if pmid in study['pmids']
                          else 'native-pmid-differs' if study['pmids'] else 'no-native-pmid')
                study['associations'].append(dict(observation, publication_key=pub['key'], search_pmid=pmid, publication_association=status, screen_attribution='unassessed'))
    _save(folder / 'database.json', database)
    schema, schema_receipt = transport.get(API + 'portal/api/returnFields?result=read_run')
    available = {row['columnId'] for row in csv.DictReader(io.StringIO(schema.decode('utf-8')), delimiter='\t')}
    if not set(REPORT_FIELDS) <= available:
        raise ValueError('Required run metadata fields missing: ' + str(set(REPORT_FIELDS) - available))

    def report(accession):
        url = API + 'portal/api/filereport?' + urlencode({'accession': accession, 'result': 'read_run', 'fields': ','.join(REPORT_FIELDS), 'format': 'tsv'})
        for attempt in range(2):
            body, receipt = transport.get(url)
            reader = csv.DictReader(io.StringIO(body.decode('utf-8')), delimiter='\t')
            rows = list(reader)
            valid = (set(REPORT_FIELDS) <= set(reader.fieldnames or []) and
                     all(re.fullmatch(r'[SED]RR\d+', row.get('run_accession') or '') for row in rows))
            if valid:
                return accession, rows, receipt
            # HTTP 200 can contain an ENA error line. Keep those bytes as failed
            # evidence and prevent cache reuse; retry this report only once.
            with transport.lock:
                receipt['incomplete'] = True
                _save(folder / 'requests.json', transport.receipts)
                transport.cache.pop(_key(url), None)
                if attempt == 0:
                    transport.report_recoveries = getattr(transport, 'report_recoveries', 0) + 1
                    if transport.report_recoveries > 10:
                        raise LimitReached('More than ten invalid run reports; checkpoint required')
        raise ValueError('Invalid run report after bounded recovery')
    _apply_metadata_only_policy(database['studies'], metadata_only_projects)
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(report, accession): accession for accession in database['studies'] if accession not in metadata_only_projects}
        for number, job in enumerate(as_completed(jobs), 1):
            accession = jobs[job]
            try:
                _, rows, receipt = job.result()
                database['studies'][accession].update(runs=rows, run_report_response=receipt['file'], run_report_url=receipt['url'],
                    run_count=len({r['run_accession'] for r in rows}), sample_count=len({r['sample_accession'] for r in rows}),
                    experiment_count=len({r['experiment_accession'] for r in rows}), run_report_status='complete')
            except LimitReached:
                raise
            except Exception as error:
                database['studies'][accession]['run_report_status'] = 'failed'
                database['issues'].append({'study': accession, 'stage': 'run-report', 'error': str(error)})
            if number % 20 == 0:
                _save(folder / 'database.json', database)
                print(json.dumps({'stage': 'run-reports', 'processed': number, 'total': len(jobs), 'issues': len(database['issues'])}), flush=True)
    database['rows'] = project(database)
    route_sets = {}
    for accession, study in database['studies'].items():
        for observation in study['associations']:
            route_sets.setdefault(observation['route'], set()).add((observation['publication_key'], accession))
    title_only = route_sets.get('complete-title', set()) - set().union(*(v for k, v in route_sets.items() if k != 'complete-title'))
    database['summary'] = {'publications_processed': len(database['publications']), 'studies': len(database['studies']),
        'publications_with_candidates': len({a['publication_key'] for s in database['studies'].values() for a in s['associations']}),
        'association_pairs': len(set().union(*route_sets.values())) if route_sets else 0,
        'route_counts': {k: {'studies': len({x[1] for x in v}), 'publication_study_pairs': len(v)} for k, v in route_sets.items()},
        'title_only_pairs': sorted(title_only), 'distinct_runs': len({r['run_accession'] for s in database['studies'].values() for r in s['runs']}),
        'sheet_rows': {k: len(v) for k, v in database['rows'].items()},
        'failed_study_accessions': len(database['study_failures']), 'run_report_issues': len(database['issues']),
        'discovery_issues': sum(len(p['issues']) for p in database['publications']), 'live_attempts': transport.attempts,
        'cached_responses': sum(bool(x.get('reused_from')) for x in transport.receipts)}
    database['summary']['metadata_only_projects'] = sorted(set(metadata_only_projects) & set(database['studies']))
    database['status'] = 'complete_with_issues' if database['study_failures'] or database['issues'] or any(p['issues'] for p in database['publications']) else 'complete'
    if database['status'] == 'complete' and database['summary']['metadata_only_projects']:
        database['status'] = 'complete_with_omissions'
    database['finished_utc'] = _now()
    _save(folder / 'database.json', database)
    _save(folder / 'summary.json', database['summary'])
    print(json.dumps(database['summary']), flush=True)
    return database


def main():
    """Parse explicit repository, output directory and same-run cache options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--cache-root', type=Path, action='append', default=[])
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--metadata-only-project', action='append', default=[])
    args = parser.parse_args()
    run(args.root, args.output_dir, args.cache_root, args.resume, args.metadata_only_project)


if __name__ == '__main__':
    main()
