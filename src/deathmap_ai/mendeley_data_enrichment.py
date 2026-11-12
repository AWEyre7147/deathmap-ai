"""Mendeley Data metadata discovery, accession enrichment and template export.

Publication searches and supplied/BioStudies references nominate datasets. Native
responses, identifier routes and unresolved outcomes are retained. Associations
are candidate evidence; this CLI/imported collector never downloads data files.
"""
from .json_storage import load_json, resolve_json_path
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from .enrichment_export import export_registered
from .enrichment_indices import DEFAULT_REGISTRY, assign_indices, native_key

PUBLIC = 'https://data.mendeley.com/public-api/datasets/'
API = 'https://api.data.mendeley.com/datasets'
SEARCH = 'https://search.dcd.ipi-prod.cortex.elsevier.systems/search'
TOKEN = 'https://auth.data.mendeley.com/oauth2/token'
TEMPLATE = Path(__file__).resolve().parents[2] / 'data/templates/history/mendeley-before-title-20261107/Mendeley-Data-Enrichment-Template.xlsx'
ACCESSION = re.compile(r'[a-z0-9]{10}')
DATA_DOI = re.compile(r'10\.17632/([a-z0-9]{10})(?:\.(\d+))?', re.I)


def _sha(body):
    return hashlib.sha256(body).hexdigest()


def _save(path, data):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def _doi(value):
    if isinstance(value, dict):
        value = value.get('id') or value.get('doi')
    return re.sub(r'(?i)^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', str(value or '').strip()).lower()


def _strings(value, locator='$'):
    if isinstance(value, str):
        yield locator, value
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from _strings(child, f'{locator}[{i}]')
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _strings(child, locator + '.' + key)


def _reference(value):
    """Resolve explicit identifiers; never identify arbitrary ten-letter words."""
    value = str(value or '').strip()
    match = DATA_DOI.fullmatch(_doi(value))
    if match:
        return match[1].lower(), _doi(value)
    parsed = urlsplit(value)
    if parsed.hostname == 'data.mendeley.com':
        match = re.fullmatch(r'/datasets/([a-z0-9]{10})(?:/(\d+))?/?', parsed.path)
        if match:
            return match[1], '10.17632/' + match[1] + ('.' + match[2] if match[2] else '')
    return None


def select_publications(source, registry=None, biostudies=None):
    """Normalize publication identities and explicit dataset-reference evidence.

    Parameters
    ----------
    source, registry, biostudies : Path or str
        Publication JSON, optional persistent publication registry, and optional
        saved BioStudies database. Pilot publication wrappers are also accepted.

    Returns
    -------
    list of dict
        Publication identities and source-specific dataset reference observations.

    Raises
    ------
    ValueError
        Identity conflicts, unsafe/duplicate indices or invalid input structure.
    """
    payload = json.loads(Path(source).read_text(encoding='utf-8-sig'))
    items = payload.get('publications') if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        raise ValueError('Expected a publication array')
    registrations = json.loads(Path(registry).read_text(encoding='utf-8-sig')) if registry else []
    by_native = {str(r['ORCS Publication ID']): r for r in registrations}
    by_pmid = {str(r['PMID']): r for r in registrations if r.get('PMID')}
    selected = []
    for wrapper in items:
        item = wrapper.get('publication', wrapper)
        pmid = str(item['PMID']) if item.get('PMID') else None
        native = item.get('PUBLICATION_ID') or item.get('ORCS Publication ID')
        n, m = by_native.get(str(native)), by_pmid.get(pmid)
        if n and m and n != m:
            raise ValueError('Publication registry identity conflict')
        match = n or m or {}
        if n and pmid and str(n.get('PMID')) != pmid:
            raise ValueError('Publication registry PMID conflict')
        index = item.get('Publication Index') or match.get('Publication index')
        if not index or not re.fullmatch(r'[A-Za-z0-9_-]+', index):
            raise ValueError('Safe Publication Index or registry match required')
        doi = _doi(item.get('DOI'))
        if doi and not re.fullmatch(r'10\.\d{4,9}/\S+', doi):
            raise ValueError('Invalid publication DOI')
        p = {'Publication Index': index, 'PMID': pmid, 'PMCID': item.get('PMCID'), 'DOI': doi or None,
             'Title': item.get('Title') or item.get('TITLE') or item.get('Publication Title'),
             'ORCS Publication ID': str(native or match.get('ORCS Publication ID') or '') or None, 'references': []}
        fields = ('Mendeley Data Accession', 'Mendeley Data Accessions', 'Mendeley Dataset ID',
                  'Mendeley Dataset IDs', 'Mendeley Dataset DOI', 'Mendeley Dataset DOIs')
        for field in fields:
            values = item.get(field) or []
            values = values if isinstance(values, list) else str(values).splitlines()
            for value in values:
                ref = _reference(value)
                if not ref and ACCESSION.fullmatch(str(value).strip()):
                    ref = str(value).strip(), None
                if ref:
                    p['references'].append({'accession': ref[0], 'dataset_doi': ref[1], 'route': 'supplied_identifier', 'source_field': field})
        for ref in wrapper.get('dataset_references', item.get('dataset_references', [])):
            value = ref.get('dataset_doi') if isinstance(ref, dict) else ref
            resolved = _reference(value)
            if resolved:
                p['references'].append({'accession': resolved[0], 'dataset_doi': resolved[1],
                    'route': 'supplied_dataset_reference', 'source_reference': ref})
        selected.append(p)
    if len({p['Publication Index'] for p in selected}) != len(selected):
        raise ValueError('Duplicate publication indices')
    if biostudies:
        saved = load_json(biostudies)
        for record in saved['publications']:
            old = record['publication']
            matches = [p for p in selected if (p.get('PMID') and str(old.get('PMID')) == p['PMID']) or (
                p.get('ORCS Publication ID') and str(old.get('ORCS Publication ID') or old.get('PUBLICATION_ID')) == p['ORCS Publication ID']) or (
                p.get('DOI') and _doi(old.get('DOI')) == p['DOI'])]
            for accession in sorted({o['accession'] for o in record['observations']}):
                study = saved['studies'].get(accession)
                if not study:
                    continue
                # Use repository link fields, rather than searching article prose.
                links = study.get('links', [])
                if not links:
                    def sections(v):
                        if isinstance(v, dict):
                            if 'links' in v:
                                yield v['links']
                            for child in v.values():
                                yield from sections(child)
                        elif isinstance(v, list):
                            for child in v:
                                yield from sections(child)
                    links = list(sections(study.get('native', {})))
                for p in matches:
                    if p.get('PMID') and old.get('PMID') and p['PMID'] != str(old['PMID']):
                        raise ValueError('Conflicting BioStudies publication identity')
                for locator, value in _strings(links):
                    resolved = _reference(value)
                    if resolved:
                        for p in matches:
                            p['references'].append({'accession': resolved[0], 'dataset_doi': resolved[1],
                                'route': 'biostudies_link', 'biostudies_accession': accession, 'locator': locator})
    return selected


class AuthenticationRequired(ValueError):
    """An uncached metadata route requires a registered Mendeley credential."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('Metadata/authentication redirect refused')


class Credentials:
    """Supply bearer tokens without persisting secrets or token responses.

    Parameters
    ----------
    token_file, client_file : Path or str, optional
        Single-line access token, or JSON with client_id, client_secret and
        optional scope. Some routes require a user-authorized access token.
    """
    def __init__(self, token_file=None, client_file=None):
        self.token_file = token_file
        self.client_file = client_file or os.environ.get('MENDELEY_CLIENT_CREDENTIALS_FILE')
        self.token, self.expires, self.requests, self.secrets = None, 0, 0, set()
        if self.token_file and self.client_file:
            raise ValueError('Choose a token file or client credentials file')

    def header(self):
        """Return Authorization, refreshing client tokens shortly before expiry."""
        if self.token_file:
            token = Path(self.token_file).read_text(encoding='utf-8-sig').strip()
        elif self.client_file:
            if self.token and time.monotonic() < self.expires:
                return 'Bearer ' + self.token
            if isinstance(self.client_file, tuple):
                config = dict(zip(('client_id', 'client_secret'),
                    (Path(p).read_text(encoding='utf-8-sig').strip() for p in self.client_file)))
            else:
                config = json.loads(Path(self.client_file).read_text(encoding='utf-8-sig'))
            client, secret = config.get('client_id'), config.get('client_secret')
            if not isinstance(client, str) or not isinstance(secret, str) or not client or not secret or ':' in client:
                raise ValueError('Expected client_id and client_secret')
            self.secrets.add(secret)
            if self.requests >= 20:
                raise ValueError('Authentication request cap reached')
            fields = {'grant_type': 'client_credentials'}
            if config.get('scope'):
                fields['scope'] = config['scope']
            header = base64.b64encode((client + ':' + secret).encode()).decode()
            request = Request(TOKEN, data=urlencode(fields).encode(), headers={
                'Authorization': 'Basic ' + header, 'Content-Type': 'application/x-www-form-urlencoded'})
            self.requests += 1
            try:
                with build_opener(_NoRedirect()).open(request, timeout=30) as response:
                    body = response.read(100001)
                if len(body) > 100000:
                    raise ValueError('Authentication response too large')
                result = json.loads(body)
            except HTTPError as error:
                code = error.code; error.close()
                raise AuthenticationRequired('Mendeley token HTTP ' + str(code)) from None
            except (URLError, OSError):
                raise AuthenticationRequired('Mendeley token connection failed') from None
            token = result.get('access_token')
            self.expires = time.monotonic() + max(0, int(result.get('expires_in', 0)) - 20)
        else:
            token = os.environ.get('MENDELEY_ACCESS_TOKEN', '').strip()
        if not isinstance(token, str) or not token or '\n' in token or '\r' in token:
            raise AuthenticationRequired('Mendeley access token or registered client credentials required')
        self.token = token; self.secrets.add(token)
        return 'Bearer ' + token


class Transport:
    """Read bounded JSON metadata and reuse URL/hash-verified native responses.

    Parameters
    ----------
    output : Path
        New/resumable run directory.
    caches : iterable of Path
        Existing native response caches, including the publication pilot.
    credentials : Credentials, optional
        Used only for uncached authenticated hosts.
    offline : bool
        Prohibit network access, including credential reads and token refresh.
    """
    def __init__(self, output, caches=(), credentials=None, offline=False):
        self.output = Path(output); self.native = self.output / 'native'; self.native.mkdir(exist_ok=True)
        self.credentials = credentials or Credentials(); self.offline = offline
        self.requests, self.reused, self.bytes, self.last = [], 0, 0, 0
        self.cache = {}; self.opener = build_opener(_NoRedirect())
        for root in [self.output, *map(Path, caches)]:
            for path in sorted((root / 'native').glob('*.json')):
                receipt = json.loads(path.read_text(encoding='utf-8'))
                if receipt.get('url') and receipt.get('sha256'):
                    self.cache.setdefault(receipt['url'], (path.with_suffix('.body'), receipt))

    def get(self, url):
        """Return parsed JSON and receipt; refuse experimental-file endpoints."""
        parts = urlsplit(url)
        public = parts.scheme == 'https' and parts.netloc == 'data.mendeley.com' and bool(re.fullmatch(r'/public-api/datasets/[a-z0-9]{10}', parts.path)) and not parts.query
        # Allow metadata routes explicitly; download and content redirects stay excluded.
        metadata_path = re.fullmatch(r'/datasets/[a-z0-9]{10}', parts.path) or re.fullmatch(
            r'/datasets/publics/[a-z0-9]{10}/(?:folders|files(?:/[a-zA-Z0-9-]+)?)', parts.path)
        authenticated = parts.scheme == 'https' and ((parts.netloc == 'api.data.mendeley.com' and (
            parts.path in ('/datasets', '/search') or metadata_path)) or (
            parts.netloc == 'search.dcd.ipi-prod.cortex.elsevier.systems' and parts.path == '/search'))
        if parts.fragment or not (public or authenticated):
            raise ValueError('Endpoint outside Mendeley dataset metadata scope')
        key = _sha(url.encode())
        if url in self.cache:
            path, source = self.cache[url]; body = path.read_bytes()
            if len(body) > 10000000 or _sha(body) != source['sha256']:
                raise ValueError('Cached Mendeley response hash mismatch')
            receipt = {**source, 'reused_from': str(path)}; self.reused += 1
        else:
            if self.offline:
                raise ValueError('No verified response in offline cache')
            # Search and file/folder routes serve ordinary JSON. The dataset
            # representation applies only to dataset retrieval/listing routes.
            dataset_route = parts.path == '/datasets' or bool(re.fullmatch(r'/datasets/[a-z0-9]{10}', parts.path))
            headers = {'Accept': 'application/vnd.mendeley-public-dataset.1+json' if parts.netloc == 'api.data.mendeley.com' and dataset_route else 'application/json', 'User-Agent': 'DeathMap-AI/0.1 Mendeley metadata'}
            if authenticated:
                headers['Authorization'] = self.credentials.header()
            for attempt in range(2):
                if len(self.requests) >= 2000 or self.bytes >= 100000000:
                    raise ValueError('Mendeley run request/byte limit reached')
                time.sleep(max(0, 1 - (time.monotonic() - self.last))); self.last = time.monotonic()
                receipt = {'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'attempt': attempt + 1}
                self.requests.append(receipt)
                try:
                    with self.opener.open(Request(url, headers=headers), timeout=30) as response:
                        body = response.read(10000001)
                        receipt.update(http_status=response.status, content_type=response.headers.get('Content-Type'))
                        if response.headers.get('Link'):
                            receipt['pagination_link'] = response.headers.get('Link')
                    if len(body) > 10000000 or self.bytes + len(body) > 100000000:
                        raise ValueError('Mendeley metadata byte limit reached')
                    if any(s.encode() in body for s in self.credentials.secrets):
                        raise ValueError('Credential in response; refusing evidence write')
                    json.loads(body); self.bytes += len(body); receipt['sha256'] = _sha(body)
                    break
                except HTTPError as error:
                    code = error.code; delay = error.headers.get('Retry-After', '2'); error.close()
                    receipt.update(http_status=code, error='HTTP ' + str(code))
                    if code in (401, 403):
                        raise AuthenticationRequired('Mendeley HTTP ' + str(code)) from None
                    if attempt or code not in (408, 429, 500, 502, 503, 504):
                        raise ValueError('Mendeley HTTP ' + str(code)) from None
                    if not delay.isdigit() or int(delay) > 30:
                        raise ValueError('Retry-After exceeds retry allowance')
                    time.sleep(max(2, int(delay)))
                except (URLError, TimeoutError, ConnectionError):
                    receipt['error'] = 'Connection failed'
                    if attempt:
                        raise ValueError('Mendeley metadata connection failed') from None
                    time.sleep(2)
        value = json.loads(body)
        (self.native / (key + '.body')).write_bytes(body)
        _save(self.native / (key + '.json'), receipt)
        self.cache[url] = (self.native / (key + '.body'), receipt)
        return value, receipt


def _hit_accession(hit):
    candidates = set()
    if isinstance(hit.get('id'), str) and ACCESSION.fullmatch(hit['id']):
        candidates.add(hit['id'])
    for _, value in _strings({k: hit.get(k) for k in ('doi', 'url')}):
        resolved = _reference(value)
        if resolved:
            candidates.add(resolved[0])
    if len(candidates) > 1:
        raise ValueError('Conflicting native dataset search identities')
    return next(iter(candidates), None)


def discover(publication, transport, reference_only=False, *, doi_only=False):
    """Retain candidate references and authenticated DOI/full-title search evidence.

    Parameters
    ----------
    publication : dict
        Normalized input identifiers and explicit dataset references.
    transport : Transport
        Bounded metadata reader.
    reference_only : bool
        Explicitly omit independent searches; do not call omissions no-hit results.

    Returns
    -------
    dict
        Candidate observations, per-route outcomes and unresolved issues.
    """
    result = {'publication': publication, 'observations': [dict(r) for r in publication['references']], 'routes': [], 'issues': []}
    if doi_only:
        result['observations'] = []
    if reference_only:
        result['routes'].append({'route': 'publication_search', 'outcome': 'not_attempted_reference_only'})
        return result
    routes = []
    if publication.get('DOI'):
        routes.append(('article_doi', API, {'article_doi': publication['DOI'], 'fields': 'results.*', 'limit': 10 if doi_only else 100}))
        if not doi_only:
            routes.append(('doi_text', SEARCH, {'query': '"' + publication['DOI'] + '"', 'page_size': 100, 'page': 1, 'include_external': 'false', 'data_type': 'DATASET'}))
    if not doi_only and publication.get('Title'):
        query = '"' + publication['Title'].replace('"', '\\"') + '"'
        if len(query) <= 255:
            routes.append(('complete_title', SEARCH, {'query': query, 'page_size': 100, 'page': 1, 'include_external': 'false', 'data_type': 'DATASET'}))
        else:
            result['issues'].append({'route': 'complete_title', 'error': 'Complete title exceeds API query length; not truncated'})
    if not routes:
        result['issues'].append({'route': 'publication_search', 'error': 'No usable DOI or complete title'})
    for name, base, parameters in routes:
        route = {'route': name, 'outcome': 'complete'}; result['routes'].append(route)
        url = base + '?' + urlencode(parameters); seen, count = set(), 0
        try:
            for page in range(10):
                if url in seen:
                    raise ValueError('Repeated pagination cursor')
                seen.add(url); value, receipt = transport.get(url)
                hits = value.get('results' if base == API else 'records') if isinstance(value, dict) else None
                if not isinstance(hits, list):
                    raise ValueError('Unexpected Mendeley search schema')
                for rank, hit in enumerate(hits):
                    if not isinstance(hit, dict):
                        raise ValueError('Invalid Mendeley search record')
                    origin = hit.get('source') or {}
                    if not isinstance(origin, dict):
                        raise ValueError('Unexpected search source schema')
                    if origin.get('external'):
                        result.setdefault('excluded_hits', []).append({'route': name, 'record': hit, 'reason': 'external_repository'})
                        continue
                    accession = _hit_accession(hit)
                    if accession:
                        result['observations'].append({'accession': accession, 'route': name, 'receipt': receipt, 'locator': f'page[{page + 1}].hits[{rank}]'})
                    else:
                        raise ValueError('Missing Mendeley dataset search identity')
                count += len(hits)
                if count > 500:
                    raise ValueError('Search exceeds 500 candidate limit')
                total = next((value[k] for k in ('total', 'total_results', 'total_count') if isinstance(value.get(k), (str, int))), None)
                if base == SEARCH:
                    if total is not None and count >= int(total):
                        break
                    if len(hits) < 100:
                        if total is not None and count < int(total):
                            raise ValueError('Text search truncated without a complete page')
                        break
                    parameters['page'] = page + 2; url = base + '?' + urlencode(parameters)
                else:
                    next_value = value.get('next') or value.get('next_marker') or value.get('nextMarker')
                    link_match = re.search(r'<([^>]+)>;\s*rel="?next"?', receipt.get('pagination_link', ''))
                    if link_match:
                        next_value = link_match[1]
                    if not next_value:
                        if (total is not None and count < int(total)) or (total is None and len(hits) >= parameters['limit']):
                            raise ValueError('Dataset search pagination is incomplete/unspecified')
                        break
                    if isinstance(next_value, dict):
                        next_value = next_value.get('href') or next_value.get('url')
                    if not isinstance(next_value, str):
                        raise ValueError('Invalid dataset pagination cursor')
                    if next_value.startswith('https://'):
                        if urlsplit(next_value).netloc != 'api.data.mendeley.com' or urlsplit(next_value).path != '/datasets':
                            raise ValueError('Unexpected pagination target')
                        url = next_value
                    else:
                        parameters['marker'] = next_value; url = base + '?' + urlencode(parameters)
            else:
                raise ValueError('Search exceeds ten-page limit')
        except AuthenticationRequired as error:
            route.update(outcome='blocked_authentication', error=str(error)); result['issues'].append({'route': name, 'error': str(error)})
        except (ValueError, OSError) as error:
            route.update(outcome='failed', error=str(error)); result['issues'].append({'route': name, 'error': str(error)})
    return result


def _number(value):
    return int(value) if not isinstance(value, bool) and str(value).isdigit() else None


def _file_size(file):
    return _number(file.get('size', (file.get('content_details') or {}).get('size')))


def collect_dataset(accession, transport):
    """Validate public dataset identity and the returned flat file inventory.

    Parameters
    ----------
    accession : str
        Native ten-character repository ID.
    transport : Transport
        Metadata reader; only one public record endpoint is requested.

    Returns
    -------
    dict
        Complete native metadata, validated file records, receipt and issues.

    Raises
    ------
    ValueError
        A dataset/version or file identity conflicts with the response.
    """
    metadata, receipt = transport.get(PUBLIC + accession)
    if not isinstance(metadata, dict) or metadata.get('id') != accession or not isinstance(metadata.get('files'), list):
        raise ValueError('Mendeley dataset identity/file-list mismatch')
    version = metadata.get('version'); doi = _doi(metadata.get('doi')); parsed = _reference(doi)
    if not isinstance(version, int) or isinstance(version, bool) or version < 1 or not parsed or parsed[0] != accession:
        raise ValueError('Mendeley dataset DOI/version identity mismatch')
    match = DATA_DOI.fullmatch(doi)
    if match[2] and int(match[2]) != version:
        raise ValueError('Mendeley dataset DOI and returned version disagree')
    files, seen = [], {}
    for file in metadata['files']:
        if not isinstance(file, dict) or not file.get('id') or not isinstance(file.get('filename'), str) or not file['filename']:
            raise ValueError('Missing native Mendeley file identity/filename')
        identity = str(file['id'])
        if identity in seen and seen[identity] != file:
            raise ValueError('Conflicting repeated Mendeley file identity')
        if identity not in seen:
            files.append(file); seen[identity] = file
    issues = []; sizes = [_file_size(f) for f in files]; reported = _number(metadata.get('size'))
    if reported is not None and all(n is not None for n in sizes) and sum(sizes) != reported:
        issues.append({'field': 'file_inventory', 'error': 'Listed file sizes differ from reported dataset total'})
    return {'accession': accession, 'metadata': metadata, 'source': receipt, 'files': files, 'issues': issues}


def _categories(value):
    return '\n'.join(str(v.get('label') or v.get('name')) for v in value if isinstance(v, dict) and (v.get('label') or v.get('name'))) or None


def project(database, index_registry=None):
    """Project retrieved hits into the owner's sheets with stable two-level indices.

    Parameters
    ----------
    database : dict
        Canonical publication observations and retrieved dataset records.
    index_registry : Path, optional
        Append-only shared registry. None gives deterministic fixture indices.

    Returns
    -------
    dict
        Publications, Datasets and Files in the registered template field names.
    """
    datasets = database['datasets']
    dataset_indices = assign_indices('MDS', {native_key(a, str(r['metadata']['version'])) for a, r in datasets.items()}, index_registry) if datasets else {}
    file_indices = assign_indices('MND', {native_key(a, str(r['metadata']['version']), str(f['id'])) for a, r in datasets.items() for f in r['files']}, index_registry) if datasets else {}
    memberships = {a: set() for a in datasets}
    evidence = {a: set() for a in datasets}
    tables = {'Publications': [], 'Datasets': [], 'Files': []}
    for record in database['publications']:
        p = record['publication']; accessions = sorted({o['accession'] for o in record['observations']} & set(datasets))
        if not accessions:
            continue
        for a in accessions:
            memberships[a].add(p['Publication Index'])
        for observation in record['observations']:
            a = observation['accession']
            if a not in datasets:
                continue
            route = observation.get('route')
            labels = {
                'biostudies_link': 'BioStudies dataset reference',
                'supplied_identifier': 'Supplied dataset identifier',
                'supplied_dataset_reference': 'Supplied dataset reference',
                'article_doi': 'Article DOI lookup',
                'doi_text': 'DOI text search candidate',
                'complete_title': 'Title search candidate',
            }
            label = labels.get(route)
            if route == 'biostudies_link' and observation.get('biostudies_accession'):
                label += ' (' + observation['biostudies_accession'] + ')'
            if label:
                evidence[a].add(f"{p['Publication Index']}: {label}")
            metadata = datasets[a]['metadata']
            article_doi = _doi(p.get('DOI'))
            # Keep discovery routes distinct from corroboration in the dataset record.
            if article_doi and any(_doi(v) == article_doi for _, v in _strings(metadata.get('articles', []))):
                evidence[a].add(f"{p['Publication Index']}: DOI in structured article links")
            if article_doi and any(_doi(v.rstrip('.,);')) == article_doi for v in
                    re.findall(r'10\.\d{4,9}/[^\s<>"]+', str(metadata.get('description') or ''), re.I)):
                evidence[a].add(f"{p['Publication Index']}: DOI in dataset description")
        tables['Publications'].append({**{k: p.get(k) for k in ('Publication Index', 'Title', 'PMID', 'PMCID', 'DOI')},
            'Dataset Count': len(accessions)})
    for accession, record in sorted(datasets.items()):
        if not memberships[accession]:
            continue
        metadata = record['metadata']; version = metadata['version']; doi = _doi(metadata.get('doi'))
        index = dataset_indices[native_key(accession, str(version))]; pubs = '\n'.join(sorted(memberships[accession]))
        common = {'Publication Index': pubs, 'Mendeley Dataset Index': index, 'Mendeley Data Accession': accession, 'Dataset DOI': doi}
        licence = metadata.get('data_licence') or {}
        license_label = (licence.get('short_name') or licence.get('full_name') or licence.get('url')) if isinstance(licence, dict) else None
        tables['Datasets'].append({**common, 'Title': metadata.get('name'), 'Description': metadata.get('description'),
            'License': license_label, 'Publication Link Evidence': '\n'.join(sorted(evidence[accession])) or None,
            'Categories': _categories(metadata.get('categories') or []), 'File Count': None if record['issues'] else len(record['files']),
            'Reported Dataset Size (Bytes)': _number(metadata.get('size')), 'Available': metadata.get('available'),
            'Confidential': metadata.get('confidential'), 'Dataset URL': f'https://data.mendeley.com/datasets/{accession}/{version}', 'Metadata URL': PUBLIC + accession})
        for file in record['files']:
            content = file.get('content_details') or {}
            tables['Files'].append({**common, 'Mendeley File Index': file_indices[native_key(accession, str(version), str(file['id']))],
                'Filename': file['filename'], 'File Type': Path(file['filename']).suffix.lower() or None,
                'Size (Bytes)': _file_size(file), 'Description': file.get('description'), 'File URL': content.get('download_url')})
    return tables


def run_collection(source, output, *, registry=None, biostudies=None, template=TEMPLATE, caches=(),
                   token_file=None, client_file=None, reference_only=False, offline=False, resume=False,
                   index_registry=DEFAULT_REGISTRY, doi_only=False):
    """Collect/resume metadata and export a new registered workbook.

    Parameters
    ----------
    source, output : Path or str
        Publication JSON input and fresh run directory.
    registry, biostudies : Path or str, optional
        Publication identity registry and saved BioStudies reference evidence.
    template, caches, index_registry : Path or iterable of Path
        Registered workbook, verified response caches and persistent indices.
    token_file, client_file : Path or str, optional
        Private access token or registered OAuth client-credentials JSON.
    reference_only, offline, resume : bool
        Expand references only, prohibit network, or continue the same inputs.
        Reference-only completion does not establish DOI discovery coverage.

    Returns
    -------
    dict
        Canonical identities, observations, source receipts, issues and rows.

    Raises
    ------
    FileExistsError
        A run/export already exists without valid resume authorization.
    ValueError
        Input, template or checkpoint bindings conflict.
    """
    source, output, template = Path(source), Path(output), Path(template)
    if doi_only and (reference_only or biostudies):
        raise ValueError('DOI enrichment cannot use reference expansion')
    selected = select_publications(source, registry, biostudies)
    binding = {'input_sha256': _sha(source.read_bytes()), 'template_sha256': _sha(template.read_bytes()),
        'registry_sha256': _sha(Path(registry).read_bytes()) if registry else None,
        'biostudies_sha256': _sha(resolve_json_path(biostudies).read_bytes()) if biostudies else None,
        'reference_only': reference_only, 'doi_only': doi_only, 'index_registry': str(Path(index_registry).resolve())}
    registration = json.loads(template.with_suffix('.manifest.json').read_text(encoding='utf-8'))
    if registration['sha256'] != binding['template_sha256']:
        raise ValueError('Mendeley template registration hash mismatch')
    if output.exists() and not resume:
        raise FileExistsError(output)
    if (output / 'Mendeley-Data-Enrichment.xlsx').exists():
        raise FileExistsError('Completed workbook exists; use a new run directory')
    output.mkdir(parents=True, exist_ok=resume)
    state = output / 'state.json'
    if state.exists() and json.loads(state.read_text(encoding='utf-8')) != binding:
        raise ValueError('Input, template or collection scope changed since checkpoint')
    _save(state, binding); (output / 'source-publications.json').write_bytes(source.read_bytes())
    pubdir, datadir = output / 'publications', output / 'datasets'; pubdir.mkdir(exist_ok=True); datadir.mkdir(exist_ok=True)
    credentials = Credentials(token_file, client_file); transport = Transport(output, caches, credentials, offline)
    database = {'schema_version': 'mendeley-data-enrichment/1', **binding, 'publications': [], 'datasets': {}, 'issues': []}
    for p in selected:
        path = pubdir / (p['Publication Index'] + '.json')
        record = json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
        if record and record['publication'] != p:
            raise ValueError('Checkpoint publication identity changed')
        if not record or record['issues']:
            record = discover(p, transport, reference_only, doi_only=doi_only); _save(path, record)
        database['publications'].append(record)
        _save(output / 'requests.json', transport.requests)
        print(f'{len(database["publications"])}/{len(selected)} publication metadata routes examined', flush=True)
    for accession in sorted({o['accession'] for p in database['publications'] for o in p['observations']}):
        path = datadir / (accession + '.json')
        try:
            record = json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
            if not record or record['issues']:
                record = collect_dataset(accession, transport); _save(path, record)
            database['datasets'][accession] = record
        except (ValueError, OSError) as error:
            database['issues'].append({'accession': accession, 'error': str(error)})
        _save(output / 'requests.json', transport.requests)
    for record in database['publications']:
        p = record['publication']
        database['issues'].extend({'Publication Index': p['Publication Index'], **i} for i in record['issues'])
        for observation in record['observations']:
            dataset = database['datasets'].get(observation['accession'])
            if dataset:
                metadata = dataset['metadata']; doi = p.get('DOI')
                article_dois = {_doi(v) for _, v in _strings(metadata.get('articles', []))}
                description_dois = {_doi(v.rstrip('.,);')) for v in re.findall(r'10\.\d{4,9}/[^\s<>\"]+', str(metadata.get('description') or ''))}
                observation['publication_doi_in_article_links'] = bool(doi and doi in article_dois)
                observation['publication_doi_in_description'] = bool(doi and doi in description_dois)
                observation['returned_dataset_doi'] = _doi(metadata.get('doi'))
    for accession, dataset in database['datasets'].items():
        database['issues'].extend({'accession': accession, **i} for i in dataset['issues'])
    database['rows'] = project(database, index_registry)
    database['collector_sha256'] = _sha(Path(__file__).read_bytes())
    database['index_registry_sha256'] = _sha(Path(index_registry).read_bytes()) if Path(index_registry).exists() else None
    database['status'] = 'incomplete' if database['issues'] else 'complete'
    database['scope'] = ('article_doi_search' if doi_only else
        'reference_expansion_only' if reference_only else 'publication_search_and_reference_expansion')
    database['summary'] = {'publications': len(selected), 'publications_with_datasets': len(database['rows']['Publications']),
        'datasets': len(database['rows']['Datasets']), 'files': len(database['rows']['Files']), 'issues': len(database['issues']),
        'blocked_search_routes': sum(r['outcome'] == 'blocked_authentication' for p in database['publications'] for r in p['routes']),
        'network_requests_this_execution': len(transport.requests), 'verified_reused_responses': transport.reused,
        'authentication_requests': credentials.requests, 'experimental_file_downloads': 0}
    _save(output / 'database.json', database); _save(output / 'summary.json', database['summary'])
    if database['datasets'] or not database['issues']:
        workbook = output / 'Mendeley-Data-Enrichment.xlsx'
        receipt = export_registered(template, workbook, database['rows'], overflow_sidecar=True)
        receipt['source_database_sha256'] = _sha((output / 'database.json').read_bytes())
        _save(workbook.with_suffix('.manifest.json'), receipt)
    print(json.dumps(database['summary'], indent=2), flush=True)
    return database


def main():
    """Run the independently installable metadata enrichment CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--registry', type=Path)
    parser.add_argument('--template', type=Path, default=TEMPLATE)
    parser.add_argument('--cache-root', type=Path, action='append', default=[])
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--access-token-file', type=Path)
    group.add_argument('--client-credentials-file', type=Path)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--index-registry', type=Path, default=DEFAULT_REGISTRY)
    a = parser.parse_args()
    data = run_collection(a.input, a.output_dir, registry=a.registry, template=a.template,
        caches=a.cache_root, token_file=a.access_token_file, client_file=a.client_credentials_file,
        doi_only=True, offline=a.offline, resume=a.resume, index_registry=a.index_registry)
    return 0 if data['status'] == 'complete' else 1


if __name__ == '__main__':
    raise SystemExit(main())
