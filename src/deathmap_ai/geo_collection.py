"""Run accepted GEO discovery, brief metadata and owner-template export for a collection.

All retrieval is serial and resumable, with native response hashes and explicit
publication/Series/sample boundaries. This module does not classify screens or
fetch article bodies or experimental files. Prior PubMed enrichment is optional;
verified native caches are reused when available.
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

from deathmap_ai import geo_enrichment as geo
from .geo_cache import _SavedNativeCache
from .geo_workbook import export_workbook
import argparse

class _Collection:
    """Isolate one serial, resumable collection's inputs, caches and checkpoints."""

    def __init__(self, index, base, root, cache_roots=()):
        self.index, self.base, self.root = Path(index).resolve(), Path(base).resolve(), Path(root).resolve()
        self.base.mkdir(parents=True, exist_ok=True)
        self.keys, self.cache = [], {}
        self.cache_roots = list(cache_roots)
        self.started, self.original_get = time.monotonic(), geo._Requests.get
        self.native = _SavedNativeCache(self.base)
        saved = self.base / 'selected-publications.json'
        if saved.exists():
            expected_hash = hashlib.sha256(self.index.read_bytes()).hexdigest()
            for publication in self._load(saved):
                if publication['_input_provenance']['sha256'] != expected_hash:
                    raise ValueError('Publication index changed; use a fresh collection directory')

    def _save(self, name, value):
        (self.base / name).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


    def _load(self, path):
        return json.loads(path.read_text(encoding='utf-8-sig'))


    def _key(self, url):
        parsed = urlsplit(url)
        return (parsed.netloc, parsed.path, tuple(sorted(parse_qsl(parsed.query))))


    def _cache_inventory(self):
        """Index receipts only; verify saved bytes when a matching response is reused."""
        self.native._inventory(self.root, self.cache_roots)
        # Keep exact GEO response reuse independent of temporary development runs.
        paths = sorted((self.root / 'data/orcs/geo-enrichment-source').glob('**/requests.json'))
        paths += sorted((self.root / 'outputs/geo').glob('**/requests.json'))
        paths += [p for cache in self.cache_roots for p in Path(cache).rglob('requests.json')]
        for path in paths:
            for receipt in self._load(path):
                member = receipt.get('file') or receipt.get('raw_file')
                if member and receipt.get('sha256') and not receipt.get('error'):
                    self.cache[self._key(receipt['url'])] = (path.parent / member, receipt)


    def _get(self, transport, url):
        """Copy byte-verified cached responses with original time/hash provenance."""
        if time.monotonic() - self.started > 7200:
            raise RuntimeError('120-minute full-ORCS checkpoint reached')
        derived = self.native._selected_response(url)
        if derived:
            body, sources = derived
            filename = f'selected-{len(transport.receipts):04d}.response'
            (transport.folder / filename).write_bytes(body)
            transport.receipts.append({'url': url, 'file': 'raw/' + filename,
                'sha256': hashlib.sha256(body).hexdigest(), 'response_kind': 'selected_cached_native_records',
                'selection_utc': datetime.now(timezone.utc).isoformat(), 'parents': sources})
            geo._save(transport.folder.parent / 'requests.json', transport.receipts)
            return body, 'raw/' + filename
        match = self.cache.get(self._key(url))
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
                'reused_from': str(path), 'original_url': old['url'],
                **{key: old[key] for key in ('parents', 'response_kind') if key in old}})
            geo._save(transport.folder.parent / 'requests.json', transport.receipts)
            return body, 'raw/' + filename
        existing = len(transport.receipts)
        body, member = self.original_get(transport, url)
        original = transport.folder.parent / member
        unique = transport.folder / f'live-{existing:05d}.response'
        original.rename(unique)
        member = 'raw/' + unique.name
        transport.receipts[-1]['file'] = member
        geo._save(transport.folder.parent / 'requests.json', transport.receipts)
        receipt = transport.receipts[-1]
        self.cache[self._key(url)] = (transport.folder.parent / member, receipt)
        return body, member


    def _soft_records(self, body, prefix):
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


    def _discover(self):
        """Resume identity-verified publication routes without losing empty outcomes."""
        self._cache_inventory()
        index_path = self.index
        index = self._load(index_path)
        selected = []
        for original in index:
            publication = dict(original)
            publication['_input_provenance'] = {
                'file': str(index_path), 'sha256': hashlib.sha256(index_path.read_bytes()).hexdigest(),
                'locator': 'PUBLICATION_ID=' + str(publication['PUBLICATION_ID'])}
            selected.append(publication)
        self.keys = [str(p.get('PMID') or 'orcs-' + str(p['PUBLICATION_ID'])) for p in selected]
        self._save('selected-publications.json', selected)
        if (self.base / 'run-manifest.json').exists():
            attempt = len(list(self.base.glob('attempt-*.manifest.json')))
            shutil.copyfile(self.base / 'run-manifest.json', self.base / f'attempt-{attempt}.manifest.json')
        self._save('run-manifest.json', {'started_utc': datetime.now(timezone.utc).isoformat(),
                                  'pmids': self.keys, 'selection': 'All ORCS publication-index records; candidate retrieval, not a coverage benchmark',
                                  'scope': 'Accession routes, brief Series and GSM metadata; one plain workbook',
                                  'python': sys.version, 'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                  'adapter_sha256': hashlib.sha256(Path(geo.__file__).read_bytes()).hexdigest(),
                                  'limits': {'minutes': 120, 'unique_gsms': 50000, 'sample_batches': 600,
                                             'sample_batch_bytes': 20_000_000},
                                  'status': 'discovering'})
        failures, results = [], {}
        for publication in selected:
            pmid = str(publication.get('PMID') or 'orcs-' + str(publication['PUBLICATION_ID']))
            target = self.base / 'publications' / pmid
            attempt = 0
            while target.exists() and self._load(target / 'manifest.json')['status'] != 'complete':
                target = self.base / 'retries' / (pmid if attempt == 0 else f'{pmid}-{attempt}')
                attempt += 1
            try:
                if target.exists():
                    manifest = self._load(target / 'manifest.json')
                    if manifest['status'] != 'complete':
                        raise ValueError('Existing partial publication run needs a separate resume decision')
                    for receipt in self._load(target / 'requests.json'):
                        if receipt.get('file') and hashlib.sha256((target / receipt['file']).read_bytes()).hexdigest() != receipt['sha256']:
                            raise ValueError('Prior response hash mismatch')
                    result = self._load(target / 'accessions.json')
                else:
                    result = geo.identify_geo(publication, target, request_get=self._get)
                result['_run_directory'] = str(target.relative_to(self.base))
                results[pmid] = result
                print(json.dumps({'pmid': pmid, 'gses': result['total_gse_count']}), flush=True)
            except Exception as error:
                failures.append({'pmid': pmid, 'stage': 'accession_identification', 'error': str(error)})
                print(json.dumps(failures[-1]), flush=True)
            self._save('discovery-results.json', results)
            self._save('issues.json', failures)
        series = {}
        for pmid, result in results.items():
            directory = self.base / result['_run_directory']
            identities = self._load(directory / 'series-identities.json')
            for accession, identity in identities.items():
                raw = directory / identity['source_file']
                record = self._soft_records(raw.read_bytes(), 'Series')
                if set(record) != {accession}:
                    raise ValueError('Series response coverage mismatch')
                series.setdefault(accession, {'fields': record[accession], 'pmids': [],
                                             'source_file': str(raw.relative_to(self.base))})['pmids'].append(pmid)
        self._save('series-metadata.json', series)
        samples = {gsm for record in series.values() for gsm in record['fields'].get('Series_sample_id', [])}
        count = {'publications_completed': len(results), 'publications_failed': len(failures),
                 'unique_gses': len(series), 'unique_gsms': len(samples),
                 'series_sample_counts': {g: len(r['fields'].get('Series_sample_id', [])) for g, r in series.items()}}
        self._save('sample-count-checkpoint.json', count)
        print(json.dumps(count), flush=True)


    def _samples(self):
        """Match metadata-only sample batches against explicit Series memberships."""
        self._cache_inventory()
        series = self._load(self.base / 'series-metadata.json')
        expected_all = {gsm for record in series.values() for gsm in record['fields'].get('Series_sample_id', [])}
        if len(expected_all) > 50000:
            raise RuntimeError(f'{len(expected_all)} unique GSMs exceeds the 50000-sample checkpoint')
        native = self._load(self.base / 'sample-metadata.json') if (self.base / 'sample-metadata.json').exists() else {}
        folder = self.base / 'samples'
        if folder.exists():
            transport = object.__new__(geo._Requests)
            transport.folder = folder / 'raw'
            transport.receipts = self._load(folder / 'requests.json') if (folder / 'requests.json').exists() else []
            transport.started, transport.attempts = time.monotonic(), 0
            for receipt in transport.receipts:
                if receipt.get('file'):
                    path = folder / receipt['file']
                    if hashlib.sha256(path.read_bytes()).hexdigest() != receipt['sha256']:
                        raise ValueError('Sample response cache hash mismatch')
                    self.cache[self._key(receipt['url'])] = (path, receipt)
        else:
            folder.mkdir()
            transport = geo._Requests(folder / 'raw')
        issues = self._load(self.base / 'issues.json')
        sample_sets = sorted(series, key=lambda g: (len(series[g]['fields'].get('Series_sample_id', [])), g))
        for accession in sample_sets:
            expected = set(series[accession]['fields'].get('Series_sample_id', []))
            if expected <= set(native):
                continue
            if len(transport.receipts) >= 600:
                raise RuntimeError('600-sample-batch checkpoint reached')
            if transport.attempts >= 80:
                transport.attempts = 0
                transport.started = time.monotonic()
            url = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?' + urlencode(
                {'acc': accession, 'targ': 'gsm', 'form': 'text', 'view': 'brief'})
            try:
                body, source = self._get(transport, url)
                if len(body) > 20_000_000:
                    raise RuntimeError('Sample batch exceeds the 20 MB metadata checkpoint')
                returned = self._soft_records(body, 'Sample')
                if set(returned) != expected:
                    raise ValueError(f'Sample coverage mismatch for {accession}: expected {len(expected)}, returned {len(returned)}')
                for gsm, fields in returned.items():
                    if gsm in native and native[gsm]['fields'] != fields:
                        issues.append({'gse': accession, 'gsm': gsm, 'stage': 'sample_metadata',
                                       'error': 'Conflicting metadata in repeated sample response; first record retained, both raw responses preserved'})
                    else:
                        native[gsm] = {'fields': fields, 'source_file': 'samples/' + source}
                self._save('sample-metadata.json', native)
                print(json.dumps({'gse': accession, 'samples_in_batch': len(returned), 'unique_samples_so_far': len(native)}), flush=True)
            except Exception as error:
                issues.append({'gse': accession, 'stage': 'sample_metadata', 'error': str(error)})
                print(json.dumps(issues[-1]), flush=True)
            self._save('issues.json', issues)
        self._save('sample-metadata.json', native)
        self._save('sample-retrieval-status.json', {'expected_unique_gsms': len(expected_all),
                                            'retrieved_unique_gsms': len(native), 'missing_gsms': sorted(expected_all - set(native)),
                                            'requests': len(transport.receipts)})


    def _join(self, fields, key):
        return '\n'.join(fields.get(key, [])) or None


    def _project(self):
        """Produce plain data tables, preserving repeated fields and PMID/GSE/GSM membership."""
        series = self._load(self.base / 'series-metadata.json')
        samples = self._load(self.base / 'sample-metadata.json')
        results = self._load(self.base / 'discovery-results.json')
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
                self._files_contacts(tables, base, fields, 'Series', record['source_file'])
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
                    self._files_contacts(tables, {**base, 'GSM': gsm}, native['fields'], 'Sample', native['source_file'])
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
                row['Source File'] = result['_run_directory'] + '/' + evidence['source_file']
                tables['Discovery Evidence'].append(row)
            # Successful empty routes must remain visible without inventing GSE records.
            for route, state in result['routes'].items():
                tables['Discovery Evidence'].append({'PMID': pmid, 'GSE': None, 'Record Kind': 'route_status',
                                                     'route': route, 'status': state['status'],
                                                     'distinct_gse_count': state['distinct_gse_count'],
                                                     'Route Details': json.dumps(state, ensure_ascii=False)})
        issues = self._load(self.base / 'issues.json')
        if issues:
            tables['Retrieval Issues'] = issues
        # Review removes redundant inverse claims; native series fields above
        # and the canonical source package still preserve each original claim.
        from .review_projection import hierarchy_rows
        tables['Series Hierarchy'] = hierarchy_rows(tables['Series Hierarchy'], 'GSE', 'Related GSE', 'GEO')
        for row in tables['Series Records']:
            row.pop('citation', None)
        for name, identifier in (('Repository Identifiers', 'Identifier'), ('Sample Metadata', 'GSM')):
            tables[name] = [{key: row.get(key) for key in ('PMID', identifier)} |
                            {key: value for key, value in row.items() if key not in ('PMID', identifier)}
                            for row in tables[name]]
        self._save('workbook-data.json', tables)
        verification = {'sheet_rows': {name: len(rows) for name, rows in tables.items()},
                        'unique_gses': len(series), 'unique_gsms': len(samples), 'pmids': list(results),
                        'issues': len(issues)}
        for path in self.base.glob('**/requests.json'):
            for receipt in self._load(path):
                if receipt.get('file'):
                    if hashlib.sha256((path.parent / receipt['file']).read_bytes()).hexdigest() != receipt['sha256']:
                        raise ValueError('Run response hash mismatch')
        self.keys = [str(p.get('PMID') or 'orcs-' + str(p['PUBLICATION_ID'])) for p in self._load(self.base / 'selected-publications.json')]
        if set(results) != set(self.keys):
            verification['incomplete_publications'] = sorted(set(self.keys) - set(results))
        self._save('projection-verification.json', verification)
        manifest = self._load(self.base / 'run-manifest.json')
        manifest.update(status='metadata_projected', finished_utc=datetime.now(timezone.utc).isoformat(),
                        projection=verification)
        self._save('run-manifest.json', manifest)
        print(json.dumps(verification), flush=True)


    def _files_contacts(self, tables, base, fields, entity, source):
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


def enrich_collection(publication_index, output_dir, *, repository_root=None, phase='all', template=None, cache_roots=()):
    """Run or resume a GEO metadata collection using the approved repository template.

    Parameters
    ----------
    publication_index : Path or str
        ORCS publication-index JSON, with titles and optional resolved identifiers.
    output_dir : Path or str
        Collection directory. Successful native responses are verified and reused.
    repository_root : Path or str, optional
        Repository containing optional caches and the approved template. Defaults
        to the root above data/orcs/publication-index.json.
    phase : str, optional
        Operational resume stage: all, discover, samples, project or export.
        The default performs every stage and exports one workbook.
    template : Path or str, optional
        Registered owner GEO template; defaults to data/templates/GEO-Enrichment.xlsx.

    Returns
    -------
    dict
        Stage receipt or complete workbook receipt, including artifact hashes.

    Raises
    ------
    ValueError
        Inputs changed, native identities or response coverage differ, or required
        retrievals remain incomplete. Checkpoints preserve completed work.
    RuntimeError
        A configured request, elapsed-time or sample-volume limit is reached.
    FileExistsError
        An existing workbook cannot be verified against its saved receipt.

    Notes
    -----
    Native Series and GSM records are stored once in geo-enrichment.json. Candidate
    publication relationships and discovery evidence remain separate. No article
    bodies, experimental files or screen classification are retrieved. Prior
    PubMed enrichment is not required; available native caches are optional.
    """
    if phase not in ('all', 'discover', 'samples', 'project', 'export'):
        raise ValueError('Unknown GEO collection phase')
    index = Path(publication_index).resolve()
    root = Path(repository_root).resolve() if repository_root else index.parents[2]
    collection = _Collection(index, output_dir, root, cache_roots)
    if phase in ('all', 'discover'):
        collection._discover()
        if collection._load(collection.base / 'issues.json'):
            raise ValueError('Incomplete discovery; see preserved issues.json and resume')
        if phase == 'discover':
            return collection._load(collection.base / 'sample-count-checkpoint.json')
    if phase in ('all', 'samples'):
        collection.started = time.monotonic()
        collection._samples()
        status = collection._load(collection.base / 'sample-retrieval-status.json')
        if status['missing_gsms'] or collection._load(collection.base / 'issues.json'):
            raise ValueError('Incomplete sample metadata; see preserved issues.json and resume')
        if phase == 'samples':
            return status
    if phase in ('all', 'project'):
        selected = collection._load(collection.base / 'selected-publications.json')
        results = collection._load(collection.base / 'discovery-results.json')
        series = collection._load(collection.base / 'series-metadata.json')
        samples = collection._load(collection.base / 'sample-metadata.json')
        expected = {str(p.get('PMID') or 'orcs-' + str(p['PUBLICATION_ID'])) for p in selected}
        expected_samples = {gsm for r in series.values() for gsm in r['fields'].get('Series_sample_id', [])}
        if set(results) != expected or set(samples) != expected_samples or collection._load(collection.base / 'issues.json'):
            raise ValueError('Canonical projection requires complete publications and exact sample coverage')
        collection._project()
        canonical_series = {gse: {**{key: value for key, value in r.items() if key != 'pmids'},
                                  'publication_keys': r['pmids']} for gse, r in series.items()}
        database = {'schema_version': 'geo-enrichment-v1',
                    'publication_index': {'file': str(index), 'sha256': hashlib.sha256(index.read_bytes()).hexdigest()},
                    'source_package': '.', 'publications': results, 'series': canonical_series, 'samples': samples,
                    'publication_key_policy': 'PMID when available; orcs-{PUBLICATION_ID} otherwise. Fallback keys are not PubMed identifiers.',
                    'relationship_policy': 'Candidate publication associations; ownership and screen roles not assessed',
                    'evidence_policy': 'Separate route evidence and native response locators; no discovery-evidence workbook sheet'}
        collection._save('geo-enrichment.json', database)
        receipt = {'status': 'projected', 'publications': len(results), 'unique_gses': len(series),
                   'unique_gsms': len(samples), 'source_code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'database_sha256': hashlib.sha256((collection.base / 'geo-enrichment.json').read_bytes()).hexdigest()}
        collection._save('pipeline-projection-receipt.json', receipt)
        if phase == 'project':
            return receipt
    template = Path(template or root / 'data/templates/GEO-Enrichment.xlsx')
    output = collection.base / 'GEO-Enrichment.xlsx'
    receipt_path = collection.base / 'workbook-verification.json'
    database_hash = hashlib.sha256((collection.base / 'geo-enrichment.json').read_bytes()).hexdigest()
    if output.exists():
        # Resumption verifies the completed workbook rather than exporting again.
        if not receipt_path.exists():
            raise FileExistsError('Workbook exists without a verification receipt')
        receipt = collection._load(receipt_path)
        if (receipt['workbook_sha256'] != hashlib.sha256(output.read_bytes()).hexdigest()
                or receipt['template_sha256'] != hashlib.sha256(template.read_bytes()).hexdigest()
                or receipt['database_sha256'] != database_hash):
            raise ValueError('Existing workbook or inputs changed; use a fresh export directory')
        return receipt
    receipt = export_workbook(template, output, collection._load(collection.base / 'workbook-data.json'))
    receipt['database_sha256'] = database_hash
    collection._save('workbook-verification.json', receipt)
    return receipt


def main():
    """Execute the resumable collection command.

    Returns
    -------
    None
        Writes collection artifacts and prints compact stage counts and hashes.
    """
    parser = argparse.ArgumentParser(description='Resumable metadata-only GEO collection enrichment')
    parser.add_argument('--publication-index', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--repository-root', type=Path)
    parser.add_argument('--template', type=Path)
    parser.add_argument('--phase', choices=('all', 'discover', 'samples', 'project', 'export'), default='all')
    args = parser.parse_args()
    print(json.dumps(enrich_collection(args.publication_index, args.output_dir,
                     repository_root=args.repository_root, phase=args.phase, template=args.template)), flush=True)


if __name__ == '__main__':
    main()


