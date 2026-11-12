"""Enrich publication DOIs using Figshare's linked-publication field only.

Public POST /articles/search requests contain resource_doi, page and page_size;
public GET /articles/{id} supplies full item/file metadata. No text, PMID, PMCID
or title searches are implemented, and file URLs are never requested. Native
evidence and unsuccessful outcomes survive in JSON; workbook rows require a
retrieved item whose resource_doi matches the selected publication exactly.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import unquote
from urllib.request import Request, HTTPRedirectHandler, build_opener

from .enrichment_export import export_registered
from .enrichment_indices import DEFAULT_REGISTRY, assign_indices, native_key
from .pmc_supplemental_collection import load_publications

API = 'https://api.figshare.com/v2'
SEARCH = API + '/articles/search'
TEMPLATE = Path(__file__).resolve().parents[2] / 'data/templates/Figshare-Enrichment-Template.xlsx'
PAGE_SIZE, MAX_PAGES = 100, 20


def digest(body):
    """Hash exact native or registered file bytes."""
    return hashlib.sha256(body).hexdigest()


def save(path, value):
    """Atomically save a collector-owned checkpoint."""
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())
    temporary.replace(path)


def doi(value):
    """Normalize only DOI wrappers, escaping and case; never infer an identifier."""
    value = unquote(str(value or '').strip())
    return re.sub(r'(?i)^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value).lower()


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'div', 'br', 'li'):
            self.parts.append('\n')


def plain(value):
    """Make metadata HTML readable; exact original descriptions remain in JSON."""
    parser = _Text()
    parser.feed(str(value or ''))
    return '\n'.join(v.strip() for v in ''.join(parser.parts).splitlines() if v.strip())


def joined(values):
    return '\n'.join(dict.fromkeys(str(v) for v in values if v not in (None, '')))


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Figshare metadata redirect refused')


class Transport:
    """Bounded public metadata transport with method/body/hash-verified reuse.

    Parameters
    ----------
    output : Path
        New or resumed run directory.
    caches : iterable of Path
        Earlier native response caches, including the reviewed metadata pilot.
    offline : bool
        Require verified responses; never attempt a network request.

    Notes
    -----
    One request starts per second. Each execution allows at most 2,000 attempts,
    150 MB total and 10 MB per response, with a 30-second timeout and one bounded
    transient retry. No credentials are needed or read.
    """
    def __init__(self, output, caches=(), offline=False):
        self.output = Path(output)
        self.native = self.output / 'native'
        self.native.mkdir(exist_ok=True)
        self.offline, self.last, self.total, self.reused = offline, 0, 0, 0
        self.requests, self.cache = [], {}
        self.opener = build_opener(_NoRedirect())
        for root in [self.output, *map(Path, caches)]:
            for path in sorted((root / 'native').glob('*.json')):
                receipt = json.loads(path.read_text(encoding='utf-8'))
                if receipt.get('sha256') and receipt.get('url') and path.with_suffix('.body').exists() and not receipt.get('error'):
                    self.cache.setdefault(self._key(receipt['url'], receipt.get('query')), (path.with_suffix('.body'), receipt))

    @staticmethod
    def _key(url, query):
        return digest(json.dumps([url, query], sort_keys=True).encode())

    def get(self, url, query=None):
        """Read linked-DOI search or public item JSON; reject every other route.

        Parameters
        ----------
        url : str
            Fixed public search or numeric item-detail endpoint.
        query : dict, optional
            Search body containing exactly resource_doi, page and page_size.

        Returns
        -------
        tuple
            Parsed JSON and original byte/date receipt, with reuse recorded.

        Raises
        ------
        ValueError, OSError
            Scope, cache integrity, operational bound or HTTP retrieval fails.
        """
        if query is not None:
            valid = (url == SEARCH and set(query) == {'resource_doi', 'page', 'page_size'}
                and re.fullmatch(r'10\.\d{4,9}/\S+', query['resource_doi'])
                and type(query['page']) is int and 1 <= query['page'] <= MAX_PAGES
                and query['page_size'] == PAGE_SIZE)
        else:
            valid = re.fullmatch(re.escape(API) + r'/articles/[1-9][0-9]*', url)
        if not valid:
            raise ValueError('Endpoint/query outside linked-publication DOI metadata scope')
        key = self._key(url, query)
        cached = self.cache.get(key)
        if cached:
            path, source = cached
            body = path.read_bytes()
            if len(body) > 10_000_000 or digest(body) != source['sha256']:
                raise ValueError('Figshare cached response hash mismatch')
            receipt = {**source, 'reused_from': str(path)}
            self.reused += 1
        else:
            if self.offline:
                raise ValueError('No verified Figshare metadata response in offline cache')
            for attempt in range(2):
                if len(self.requests) >= 2000 or self.total >= 150_000_000:
                    raise ValueError('Figshare metadata request/byte budget reached')
                time.sleep(max(0, 1 - (time.monotonic() - self.last)))
                self.last = time.monotonic()
                receipt = {'url': url, 'method': 'POST' if query is not None else 'GET', 'query': query,
                    'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'attempt': attempt + 1}
                self.requests.append(receipt)
                headers = {'Accept': 'application/json', 'User-Agent': 'DeathMap-AI Figshare metadata enrichment'}
                if query is not None:
                    headers['Content-Type'] = 'application/json'
                try:
                    with self.opener.open(Request(url, data=json.dumps(query).encode() if query is not None else None,
                                                 headers=headers), timeout=30) as response:
                        body = response.read(10_000_001)
                        receipt['http_status'] = response.status
                    if len(body) > 10_000_000 or self.total + len(body) > 150_000_000:
                        raise ValueError('Figshare response exceeds metadata byte limit')
                    self.total += len(body)
                    break
                except (HTTPError, URLError, TimeoutError, OSError) as error:
                    code = error.code if isinstance(error, HTTPError) else None
                    receipt.update(error=str(error))
                    if code is not None:
                        receipt['http_status'] = code
                        error.close()
                    if attempt or (code is not None and code not in (429, 500, 502, 503, 504)):
                        raise OSError(str(error)) from None
                    time.sleep(2)
                finally:
                    save(self.output / 'requests.json', self.requests)
        parsed = json.loads(body)
        receipt = {**receipt, 'sha256': digest(body), 'bytes': len(body), 'file': 'native/' + key + '.body'}
        (self.native / (key + '.body')).write_bytes(body)
        save(self.native / (key + '.json'), receipt)
        self.cache[key] = (self.native / (key + '.body'), receipt)
        return parsed, receipt


def collect_one(publication, transport):
    """Retrieve only explicitly linked records, preserving no-hit/error evidence."""
    record = {'publication': publication, 'outcome': 'no_hits', 'search_complete': False,
              'search_receipts': [], 'items': [], 'issues': []}
    identities = set()
    try:
        for page in range(1, MAX_PAGES + 1):
            rows, receipt = transport.get(SEARCH, {'resource_doi': publication['DOI'], 'page': page, 'page_size': PAGE_SIZE})
            record['search_receipts'].append(receipt)
            if not isinstance(rows, list):
                raise ValueError('Unexpected Figshare search response schema')
            for row in rows:
                if not isinstance(row, dict) or type(row.get('id')) is not int or row['id'] < 1:
                    raise ValueError('Invalid Figshare search item identity')
                identities.add(row['id'])
            if len(rows) < PAGE_SIZE:
                record['search_complete'] = True
                break
        if not record['search_complete']:
            record['issues'].append({'stage': 'search', 'error': 'Linked-DOI pagination cap reached; results are incomplete'})
    except (ValueError, OSError) as error:
        record['issues'].append({'stage': 'search', 'error': str(error)})
    for item_id in sorted(identities):
        try:
            metadata, receipt = transport.get(API + '/articles/' + str(item_id))
            if not isinstance(metadata, dict) or metadata.get('id') != item_id:
                raise ValueError('Figshare item identity mismatch')
            # A DOI appearing in References never substitutes for resource_doi.
            if doi(metadata.get('resource_doi')) != publication['DOI']:
                raise ValueError('Figshare resource_doi differs from selected publication')
            files = metadata.get('files')
            if not isinstance(files, list):
                raise ValueError('Missing Figshare native file inventory')
            file_ids = set()
            for file in files:
                if not isinstance(file, dict) or type(file.get('id')) is not int or file['id'] < 1 or file['id'] in file_ids:
                    raise ValueError('Missing or duplicate native Figshare file ID')
                file_ids.add(file['id'])
                if file.get('size') is not None and (type(file['size']) is not int or file['size'] < 0):
                    raise ValueError('Invalid Figshare file byte size')
            record['items'].append({'metadata': metadata, 'receipt': receipt})
        except (ValueError, OSError) as error:
            record['issues'].append({'stage': 'item', 'id': item_id, 'error': str(error)})
    record['outcome'] = 'partial' if record['issues'] and record['items'] else 'failed' if record['issues'] else 'retrieved' if record['items'] else 'no_hits'
    return record


def project(records, index_registry=None):
    """Map verified hits into three sheets, with one publication per row.

    Parameters
    ----------
    records : list of dict
        Per-publication outcomes and verified linked item metadata.
    index_registry : Path, optional
        Shared append-only FGI/FGF identities; None uses in-memory assignments.

    Returns
    -------
    dict
        Publications, Items and Files; no-hit or wholly failed inputs have no rows.
    """
    all_items = [i['metadata'] for r in records for i in r['items']]
    item_indices = assign_indices('FGI', [native_key(str(m['id'])) for m in all_items], index_registry)
    file_indices = assign_indices('FGF', [native_key(str(m['id']), str(f['id'])) for m in all_items for f in m['files']], index_registry)
    sheets = {'Publications': [], 'Items': [], 'Files': []}
    for record in records:
        p = record['publication']
        metadata = [i['metadata'] for i in record['items']]
        if not metadata:
            continue
        sheets['Publications'].append({'Publication Index': p['Publication Index'], 'DOI': p['DOI'], 'Title': p.get('Title'),
            'Linked Items': len(metadata), 'Listed Files': sum(len(m['files']) for m in metadata),
            'Keywords': joined(v for m in metadata for v in (m.get('keywords') or [])),
            'Tags': joined(v for m in metadata for v in (m.get('tags') or [])),
            'Categories': joined(c.get('title') for m in metadata for c in (m.get('categories') or [])),
            'License': joined((m.get('license') or {}).get('name') for m in metadata)})
        for m in metadata:
            context = {'Publication Index': p['Publication Index'], 'Figshare Item Index': item_indices[native_key(str(m['id']))]}
            sheets['Items'].append({**context, 'Figshare Item ID': m['id'], 'Item DOI': m.get('doi'), 'Title': m.get('title'),
                'Description': plain(m.get('description')), 'Item Type': m.get('defined_type_name'),
                'File Types': joined(sorted({Path(f.get('name') or '').suffix.lower() for f in m['files']})),
                'Reported Size (Bytes)': m.get('size'), 'Public': m.get('is_public'), 'Confidential': m.get('is_confidential'),
                'Metadata Only': m.get('is_metadata_record'), 'Download Disabled': m.get('download_disabled'),
                'Item URL': m.get('url_public_html') or m.get('figshare_url'), 'Metadata URL': API + '/articles/' + str(m['id'])})
            for f in m['files']:
                sheets['Files'].append({**context, 'Figshare File Index': file_indices[native_key(str(m['id']), str(f['id']))],
                    'Figshare File ID': f['id'], 'Filename': f.get('name'), 'File Type': Path(f.get('name') or '').suffix.lower(),
                    'Size (Bytes)': f.get('size'), 'Link Only': f.get('is_link_only'), 'Download Disabled': m.get('download_disabled'),
                    'File URL': f.get('download_url')})
    return sheets


def run_collection(source, output, *, registry=None, template=TEMPLATE, caches=(), offline=False, resume=False, index_registry=DEFAULT_REGISTRY):
    """Collect/checkpoint public metadata and fill the registered owner template.

    Parameters
    ----------
    source, output : Path
        Any supported publication JSON selection and a fresh/resumable directory.
    registry, template, caches, index_registry : Path or iterable of Path
        Existing publication crosswalk, registered workbook, verified caches and
        persistent resource indices. No validation cohort is a code dependency.
    offline, resume : bool
        Disable network or continue an unfinished run bound to the same inputs.

    Returns
    -------
    dict
        Canonical metadata, issues, projected rows and explicit retrieval summary.

    Raises
    ------
    ValueError, FileExistsError
        Registration/bindings conflict or a completed workbook would be replaced.
    """
    source, output, template = map(Path, (source, output, template))
    selected = load_publications(source, registry)
    registration = json.loads(template.with_suffix('.manifest.json').read_text(encoding='utf-8'))
    binding = {'input_sha256': digest(source.read_bytes()), 'template_sha256': digest(template.read_bytes()),
        'registry_sha256': digest(Path(registry).read_bytes()) if registry else None,
        'index_registry': str(Path(index_registry).resolve()), 'search_strategy': 'linked-publication-doi-only/1'}
    if registration['sha256'] != binding['template_sha256']:
        raise ValueError('Figshare template registration hash mismatch')
    if output.exists() and not resume:
        raise FileExistsError(output)
    if (output / 'Figshare-Enrichment.xlsx').exists():
        raise FileExistsError('Completed workbook exists; use a fresh run directory')
    output.mkdir(parents=True, exist_ok=resume)
    state = output / 'state.json'
    if state.exists() and json.loads(state.read_text(encoding='utf-8')) != binding:
        raise ValueError('Figshare input/template/registry changed since checkpoint')
    save(state, binding)
    records_dir = output / 'publications'
    records_dir.mkdir(exist_ok=True)
    transport = Transport(output, caches, offline)
    records = []
    for p in selected:
        p['DOI'] = doi(p.get('DOI'))
        checkpoint = records_dir / (p['Publication Index'] + '.json')
        record = json.loads(checkpoint.read_text(encoding='utf-8')) if checkpoint.exists() else None
        if record and record['publication'] != p:
            raise ValueError('Checkpoint publication identity conflict')
        if not record or record['issues']:
            if not p['DOI']:
                record = {'publication': p, 'outcome': 'no_doi', 'items': [], 'issues': []}
            elif not re.fullmatch(r'10\.\d{4,9}/\S+', p['DOI']):
                record = {'publication': p, 'outcome': 'invalid_doi', 'items': [], 'issues': [{'stage': 'selection', 'error': 'Invalid publication DOI'}]}
            else:
                record = collect_one(p, transport)
            save(checkpoint, record)
        records.append(record)
        print(f'{len(records)}/{len(selected)} publications; {record["outcome"]}', flush=True)
    rows = project(records, index_registry)
    issues = [{'Publication Index': r['publication']['Publication Index'], **i} for r in records for i in r['issues']]
    summary = {'publications': len(records), 'publications_with_hits': len(rows['Publications']),
        'publications_without_hits': sum(r['outcome'] == 'no_hits' for r in records),
        'publications_without_doi': sum(r['outcome'] == 'no_doi' for r in records),
        'unique_items': len({r['Figshare Item Index'] for r in rows['Items']}),
        'item_rows': len(rows['Items']), 'unique_files': len({r['Figshare File Index'] for r in rows['Files']}),
        'file_rows': len(rows['Files']), 'issues': len(issues), 'requests_this_execution': len(transport.requests),
        'verified_reused_responses': transport.reused, 'experimental_downloads': 0}
    data = {'schema_version': 'figshare-enrichment/1', **binding, 'publications': records, 'rows': rows, 'issues': issues,
        'summary': summary, 'status': 'incomplete' if issues else 'complete',
        'collector_sha256': digest(Path(__file__).read_bytes()),
        'association_policy': 'Exact resource_doi match; qualifying screen content is unassessed'}
    save(output / 'database.json', data)
    save(output / 'summary.json', summary)
    save(output / 'requests.json', transport.requests)
    if rows['Items'] or not issues:
        receipt = export_registered(template, output / 'Figshare-Enrichment.xlsx', rows, overflow_sidecar=True)
        receipt.update(source_database_sha256=digest((output / 'database.json').read_bytes()), retrieval_issues=len(issues))
        save(output / 'Figshare-Enrichment.manifest.json', receipt)
    print(json.dumps(summary, indent=2), flush=True)
    return data


def main():
    """Run the same DOI-only enrichment independently of the shared pipeline."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--registry', type=Path)
    parser.add_argument('--template', type=Path, default=TEMPLATE)
    parser.add_argument('--cache-root', type=Path, action='append', default=[])
    parser.add_argument('--index-registry', type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    result = run_collection(args.input, args.output_dir, registry=args.registry, template=args.template,
        caches=args.cache_root, offline=args.offline, resume=args.resume, index_registry=args.index_registry)
    return 0 if result['status'] == 'complete' else 1


if __name__ == '__main__':
    raise SystemExit(main())
