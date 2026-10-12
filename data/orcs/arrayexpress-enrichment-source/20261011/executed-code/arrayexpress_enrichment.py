"""Bounded publication-led ArrayExpress metadata pilot and command-line entry.

Preserves native searches and PageTab records in a new run directory. Publication
citations and sample/file relationships remain observations, not CRISPR screen
attribution. Optional IDF/SDRF retrieval evaluates metadata only; it never follows
experimental file links or expands external repository identifiers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

API = 'https://www.ebi.ac.uk/biostudies/api/v1/'
STRATEGY = 'arrayexpress-publication-metadata-v1.1'
LIMIT = 10 * 1024 * 1024


def _save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


def _phrase(value):
    return '"' + value.strip().replace('\\', '\\\\').replace('"', '\\"') + '"'


def publication_routes(publication: dict) -> list[tuple[str, dict]]:
    """Build literal query parameters from saved identifiers and complete title.

    Parameters
    ----------
    publication : dict
        Saved ORCS record; PMID, DOI and PMCID are optional, TITLE is required.

    Returns
    -------
    list
        Named routes and parameters; missing identifiers omit their routes.

    Raises
    ------
    ValueError
        Missing title or malformed supplied PMID.
    """
    title = str(publication.get('TITLE') or '').strip()
    pmid = str(publication.get('PMID') or '').strip()
    if not title or (pmid and not pmid.isdigit()):
        raise ValueError('Complete title and valid optional PMID required')
    routes = []
    for field, kind in [('PMID', 'pmid'), ('DOI', 'doi'), ('PMCID', 'pmc')]:
        value = str(publication.get(field) or '').strip()
        if value:
            # URL encoding alone does not quote Lucene punctuation. The live
            # pilot showed a bare DOI can produce thousands of unrelated hits.
            routes.append((kind + '_link', {'link_type': kind, 'link_value': _phrase(value)}))
    if publication.get('DOI'):
        routes.append(('doi_phrase', {'query': _phrase(publication['DOI'])}))
    routes.append(('publication_title_phrase', {'query': _phrase(title)}))
    return routes


def walk_metadata(value, locator='$'):
    """Yield every native mapping with its JSON locator, retaining list positions.

    Parameters
    ----------
    value : object
        Parsed native PageTab JSON.
    locator : str
        Root locator for evidence paths.

    Yields
    ------
    tuple
        Locator and mapping; no entity merging or field normalization.
    """
    if isinstance(value, dict):
        yield locator, value
        for key, item in value.items():
            yield from walk_metadata(item, locator + '.' + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_metadata(item, f'{locator}[{index}]')


class _Transport:
    """Store bytes before parsing and enforce serial pilot budgets."""

    def __init__(self, folder, opener=urlopen):
        self.folder, self.opener = folder, opener
        (folder / 'raw').mkdir()
        self.receipts = []
        self.attempt_limit = 99
        self.started, self.last_start, self.total = time.monotonic(), 0., 0

    def get(self, url):
        for attempt in (1, 2):
            if len(self.receipts) >= self.attempt_limit or time.monotonic() - self.started >= 900:
                raise RuntimeError('Pilot attempt/time limit reached')
            time.sleep(max(0., 1. - (time.monotonic() - self.last_start)))
            self.last_start = time.monotonic()
            receipt = {'url': url, 'attempt': attempt,
                       'retrieved_utc': datetime.now(timezone.utc).isoformat()}
            self.receipts.append(receipt)
            try:
                request = Request(url, headers={'User-Agent': 'DeathMap-AI/0.1 ArrayExpress metadata',
                                               'Accept': 'application/json' if any(part in url for part in
                                                   ('/api/', '/webservices/rest/', '/annotations_api/')) else 'text/plain'})
                with self.opener(request, timeout=30) as response:
                    cap = min(LIMIT, 100 * 1024 * 1024 - self.total)
                    body = response.read(cap + 1)
                    receipt.update(http_status=response.status,
                                   content_type=response.headers.get('Content-Type'))
                name = f'raw/{len(self.receipts):03d}.response'
                (self.folder / name).write_bytes(body)
                self.total += len(body)
                receipt.update(file=name, bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
                if len(body) > cap:
                    receipt['incomplete'] = True
                    raise RuntimeError('Response/total byte limit reached')
                return body, name
            except (HTTPError, URLError, TimeoutError) as error:
                receipt['error'] = str(error)
                retry = not isinstance(error, HTTPError) or error.code in (408, 429) or error.code >= 500
                if not retry or attempt == 2:
                    raise
                delay = 5
                if isinstance(error, HTTPError):
                    retry_after = error.headers.get('Retry-After')
                    if retry_after:
                        # Unknown HTTP-date delays are a checkpoint, not an excuse
                        # to retry earlier than the service requested.
                        if not retry_after.isdigit():
                            raise RuntimeError('Retry-After requires a checkpoint') from error
                        delay = max(delay, int(retry_after))
                if delay > 60 or time.monotonic() - self.started + delay >= 900:
                    raise RuntimeError('Retry delay exceeds pilot budget') from error
                time.sleep(delay)
            finally:
                _save(self.folder / 'requests.json', self.receipts)


def _search(get, params, observations):
    """Require terminal cursor and retain every hit, including duplicates."""
    seen, cursor = set(), None
    for page in range(10):
        query = dict(params, pageSize=100)
        query.update({'cursor': cursor} if cursor else {'pagination': 'cursor'})
        body, source = get(API + 'ArrayExpress/search?' + urlencode(query))
        data = json.loads(body)
        if not isinstance(data.get('hits'), list) or 'nextCursor' not in data:
            raise ValueError('Incomplete search schema')
        if data.get('expandedSynonyms') or data.get('expandedEfoTerms'):
            raise ValueError('Unexpected query expansion requires review')
        for rank, hit in enumerate(data['hits']):
            accession = hit.get('accession')
            if not accession or hit.get('type') != 'study':
                raise ValueError('Search hit is not a named study')
            observations.append({'accession': accession, 'source': source,
                                 'locator': f'$.hits[{rank}]', 'page': page + 1, 'native': hit})
        if len({row['accession'] for row in observations}) > 10:
            raise RuntimeError('Ten-study pilot limit reached')
        cursor = data['nextCursor']
        if cursor is None:
            return
        if not isinstance(cursor, str) or not cursor or cursor in seen:
            raise ValueError('Invalid or repeated cursor')
        seen.add(cursor)
    raise RuntimeError('Ten-page route limit reached')


def run_pilot(publication: dict, output_dir: Path, *, metadata_files=False, opener=urlopen):
    """Discover and inspect one publication's ArrayExpress metadata.

    Parameters
    ----------
    publication : dict
        Saved ORCS publication with input provenance; no expected accession seed.
    output_dir : Path
        New exclusive output directory. Existing directories are refused.
    metadata_files : bool
        Evaluate at most native declared IDF and SDRF files per discovered study.
    opener : callable
        HTTP opener; injectable for small offline fixtures.

    Returns
    -------
    dict
        Publication, route states, query observations and native study projections.

    Raises
    ------
    Exception
        Retrieval, schema or budget failure; partial results and receipts survive.

    Notes
    -----
    Creates files and makes network requests. Exact native citation evidence must
    be inspected before asserting a publication relationship. No screen grouping.
    """
    routes = publication_routes(publication)
    output_dir.mkdir(parents=True, exist_ok=False)
    transport = _Transport(output_dir, opener)
    result = {'strategy': STRATEGY, 'publication': publication, 'status': 'running',
              'python_version': platform.python_version(), 'interface': 'BioStudies API v1',
              'source_code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'routes': {}, 'observations': [], 'studies': [], 'metadata_file_evaluation': metadata_files}
    try:
        for kind in ('pmid', 'doi', 'pmc'):
            if not any(name == kind + '_link' for name, _ in routes):
                result['routes'][kind + '_link'] = {'status': 'skipped_missing_identifier'}
        for name, params in routes:
            result['routes'][name] = {'status': 'running', 'parameters': params}
            hits = []
            try:
                _search(transport.get, params, hits)
            except Exception:
                result['routes'][name]['status'] = 'incomplete'
                raise
            finally:
                # Partial hits remain inspectable even when the count/cursor
                # boundary stops this route; they are never completed matches.
                for hit in hits:
                    hit['route'] = name
                result['observations'].extend(hits)
            result['routes'][name].update(status='complete' if hits else 'no_results',
                                         distinct_studies=len({h['accession'] for h in hits}))
            if len({h['accession'] for h in result['observations']}) > 10:
                raise RuntimeError('Ten-study pilot limit reached')
            _save(output_dir / 'result.json', result)
        for accession in sorted({h['accession'] for h in result['observations']}):
            body, source = transport.get(API + 'studies/' + quote(accession, safe=''))
            native = json.loads(body)
            if native.get('accno') != accession:
                raise ValueError('Study identity mismatch')
            study = {'accession': accession, 'source': source, 'native': native,
                     'attributes': [], 'links': [], 'files': [], 'metadata_files': []}
            result['studies'].append(study)
            for locator, node in walk_metadata(native):
                if 'name' in node and 'value' in node:
                    study['attributes'].append({'locator': locator, 'native': node})
                if 'url' in node:
                    study['links'].append({'locator': locator, 'native': node})
                if 'path' in node:
                    study['files'].append({'locator': locator, 'native': node})
            if metadata_files:
                chosen = {}
                for entry in study['files']:
                    file = entry['native']
                    path = str(file['path'])
                    kind = next((k for k in ('idf', 'sdrf') if path.lower().endswith('.' + k + '.txt')), None)
                    if not kind:
                        continue
                    if kind in chosen:
                        raise ValueError('Multiple metadata files of one type require review')
                    # A native format declaration prevents a suffix alone from
                    # authorizing arbitrary content or archive retrieval.
                    declaration = json.dumps(file.get('attributes', [])).lower()
                    if kind not in declaration:
                        raise ValueError('Metadata file lacks native IDF/SDRF declaration')
                    if path.startswith('/') or '..' in path.split('/') or '://' in path:
                        raise ValueError('Unsafe native metadata path')
                    chosen[kind] = entry
                for kind, entry in chosen.items():
                    url = 'https://www.ebi.ac.uk/biostudies/files/' + quote(accession, safe='') + '/' + quote(entry['native']['path'], safe='/')
                    data, file_source = transport.get(url)
                    text = data.decode('utf-8-sig')
                    if text.lstrip().startswith('<'):
                        raise ValueError('Metadata file returned markup')
                    study['metadata_files'].append({'kind': kind, 'source': file_source,
                                                    'listing_locator': entry['locator'],
                                                    'lines': len(text.splitlines())})
            _save(output_dir / 'result.json', result)
        result['status'] = 'complete'
    except Exception as error:
        result.update(status='incomplete', error=str(error))
        raise
    finally:
        result['attempts'] = len(transport.receipts)
        _save(output_dir / 'result.json', result)
    return result


def main():
    """Run a uniquely selected saved publication pilot, preserving input hash."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publication-index', type=Path, required=True)
    parser.add_argument('--pmid', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--evaluate-metadata-files', action='store_true')
    args = parser.parse_args()
    data = args.publication_index.read_bytes()
    matches = [p for p in json.loads(data) if str(p.get('PMID')) == args.pmid]
    if len(matches) != 1:
        raise ValueError('PMID must select exactly one publication')
    publication = dict(matches[0])
    publication['_input_provenance'] = {'file': str(args.publication_index.resolve()),
        'sha256': hashlib.sha256(data).hexdigest(), 'locator': 'PUBLICATION_ID=' + publication['PUBLICATION_ID']}
    result = run_pilot(publication, args.output_dir, metadata_files=args.evaluate_metadata_files)
    print(json.dumps({'status': result['status'], 'studies': [s['accession'] for s in result['studies']],
                      'routes': result['routes'], 'attempts': result['attempts']}, indent=2))


if __name__ == '__main__':
    main()
