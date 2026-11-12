"""Metadata-only publication enrichment across every BioStudies collection.

Exact DOI, PMID, PMCID and complete-title searches are combined with Europe PMC's
precomputed accession annotations. These nominate candidate associations, not
screen ownership. Only API metadata and file inventories are retrieved.
"""
from .json_storage import load_json, resolve_json_path
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, quote, urlencode, urlsplit
from urllib.request import Request, urlopen

from .enrichment_export import export_registered
from .enrichment_indices import DEFAULT_REGISTRY, assign_indices, native_key
from .pmc_supplemental_collection import load_publications

API = 'https://www.ebi.ac.uk/biostudies/api/v1/'
ANNOTATIONS = 'https://www.ebi.ac.uk/europepmc/annotations_api/annotationsByArticleIds'
ACCESSION = re.compile(r'(?<![A-Z0-9_-])(?:E-[A-Z][A-Z0-9]*-\d+|S-[A-Z][A-Z0-9_-]*[A-Z0-9])(?![A-Z0-9_-])')
TEMPLATE = Path(__file__).resolve().parents[2] / 'data/templates/BioStudies-Enrichment-Template.xlsx'


def digest(body):
    return hashlib.sha256(body).hexdigest()


def save(path, data):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def walk(value, location='$'):
    """Walk all PageTab objects, preserving their original source locations."""
    if isinstance(value, dict):
        yield location, value
        for key, child in value.items():
            yield from walk(child, location + '.' + key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, f'{location}[{i}]')


def flattened(value):
    if isinstance(value, dict):
        yield value
    elif isinstance(value, list):
        for child in value:
            yield from flattened(child)


def attributes(value):
    """Preserve distinct repeated attribute values rather than choosing one."""
    result = {}
    for a in value.get('attributes', []):
        if a.get('value') is not None:
            result.setdefault(a['name'].casefold(), [])
            if a['value'] not in result[a['name'].casefold()]:
                result[a['name'].casefold()].append(a['value'])
    return {k: '\n'.join(map(str, v)) for k, v in result.items()}


def phrase(text):
    return '"' + str(text).strip().replace('\\', '\\\\').replace('"', '\\"') + '"'


def select_publications(source, registry=None, pubmed=None):
    """Retain explicit study accessions and optional saved PubMed accession links."""
    selected = load_publications(source, registry)
    raw = json.loads(Path(source).read_text(encoding='utf-8-sig'))
    raw = raw['publications'] if isinstance(raw, dict) else raw
    for p, item in zip(selected, raw, strict=True):
        p['input_accessions'] = []
        for field in ('BioStudies Accession', 'BioStudies Accessions', 'ArrayExpress Accession',
                      'ArrayExpress Study Accession', 'ArrayExpress Accessions', 'Accession', 'Accessions'):
            values = item.get(field) or []
            values = values if isinstance(values, list) else str(values).splitlines()
            for value in values:
                if isinstance(value, str) and ACCESSION.fullmatch(value.strip()):
                    p['input_accessions'].append({'accession': value.strip(), 'source_field': field})
    if pubmed:
        saved = load_json(pubmed)
        columns = saved.get('repository_columns', ['PMID', 'Resource', 'Accession'])
        by_pmid = {str(p['PMID']): p for p in selected if p.get('PMID')}
        for number, row in enumerate(saved['rows'].get('Repository Records', [])):
            row = row if isinstance(row, dict) else dict(zip(columns, row))
            p = by_pmid.get(str(row.get('PMID')))
            accession = str(row.get('Accession') or '')
            if p and ACCESSION.fullmatch(accession):
                p['input_accessions'].append({'accession': accession, 'source_field': 'saved_pubmed.Repository Records', 'source_row': number})
    return selected


def routes(publication):
    """Use only input publication identifiers/title, never benchmark accessions."""
    result = []
    for name, value in [('doi', publication.get('DOI')), ('pmid', publication.get('PMID')), ('pmcid', publication.get('PMCID')), ('complete_title', publication.get('Title'))]:
        if value:
            result.append((name, API + 'search?' + urlencode({'query': phrase(value), 'pagination': 'cursor', 'pageSize': 100})))
    if publication.get('PMID'):
        result.append(('europepmc_annotations', ANNOTATIONS + '?' + urlencode({
            'articleIds': 'MED:' + str(publication['PMID']), 'type': 'Accession Numbers', 'format': 'JSON'})))
    return result


class Transport:
    """Bounded API reads and hash-verified native response reuse."""
    def __init__(self, folder, caches=(), offline=False, opener=None):
        self.folder = Path(folder)
        self.native = self.folder / 'native'
        self.native.mkdir(exist_ok=True)
        self.opener = opener or urlopen
        self.offline = offline
        self.requests, self.cache, self.reused, self.total_bytes = [], {}, 0, 0
        self.last = 0
        for root in [self.folder, *map(Path, caches)]:
            for path in sorted((root/'native').glob('*.json')):
                r = json.loads(path.read_text(encoding='utf-8'))
                if r.get('sha256') and r.get('url'):
                    self.cache[r['url']] = (path.with_suffix('.body'), r)
            # Existing source packages have request arrays and relative files.
            for path in [root/'requests.json', root/'metadata.json']:
                if not path.exists():
                    continue
                old = json.loads(path.read_text(encoding='utf-8'))
                old = old.get('requests', []) if isinstance(old, dict) else old
                for r in old:
                    if r.get('sha256') and r.get('url') and r.get('file') and not r.get('error'):
                        self.cache[r['url']] = (root/r['file'], r)

    def get(self, url):
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname != 'www.ebi.ac.uk' or not (
                url.startswith(API) or url.startswith(ANNOTATIONS + '?')):
            raise ValueError('Only BioStudies/Europe PMC API metadata is permitted')
        key = digest(url.encode())
        if url in self.cache:
            path, receipt = self.cache[url]
            body = path.read_bytes()
            if len(body) > 10_000_000 or digest(body) != receipt['sha256']:
                raise ValueError('Cached response hash/size mismatch')
            self.reused += 1
            receipt = {**receipt, 'body': 'native/' + key + '.body'}
        else:
            if self.offline:
                raise ValueError('No verified response in offline cache')
            for attempt in range(2):
                if len(self.requests) >= 5000 or self.total_bytes >= 300_000_000:
                    raise ValueError('Run request/byte limit reached')
                time.sleep(max(0, 1 - (time.monotonic() - self.last)))
                self.last = time.monotonic()
                receipt = {'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'attempt': attempt + 1}
                self.requests.append(receipt)
                try:
                    with self.opener(Request(url, headers={'Accept': 'application/json', 'User-Agent': 'DeathMap-AI/0.1 BioStudies metadata'}), timeout=30) as response:
                        body = response.read(10_000_001)
                        receipt.update(http_status=response.status, content_type=response.headers.get('Content-Type'))
                    if len(body) > 10_000_000 or self.total_bytes + len(body) > 300_000_000:
                        raise ValueError('Metadata response/run byte limit reached')
                    json.loads(body)  # HTML/error pages must never become empty hits.
                    self.total_bytes += len(body)
                    receipt.update(sha256=digest(body), body='native/' + key + '.body')
                    break
                except (HTTPError, URLError, TimeoutError, ConnectionError) as error:
                    receipt['error'] = type(error).__name__
                    transient = not isinstance(error, HTTPError) or error.code in (408, 429, 500, 502, 503, 504)
                    delay = error.headers.get('Retry-After', '2') if isinstance(error, HTTPError) else '2'
                    if isinstance(error, HTTPError):
                        receipt['http_status'] = error.code
                        error.close()
                    if attempt or not transient:
                        raise ValueError('Metadata request failed: ' + receipt['error']) from None
                    if not delay.isdigit() or int(delay) > 30:
                        raise ValueError('Retry-After exceeds bounded retry allowance') from None
                    time.sleep(max(2, int(delay)))
        (self.native/(key+'.body')).write_bytes(body)
        save(self.native/(key+'.json'), receipt)
        self.cache[url] = (self.native/(key+'.body'), receipt)
        return json.loads(body), receipt


def discover(publication, transport):
    result = {'publication': publication, 'observations': [], 'routes': [], 'issues': []}
    for supplied in publication.get('input_accessions', []):
        result['observations'].append({**supplied, 'route': 'supplied_accession', 'evidence_kind': 'supplied_study_identifier'})
    if publication.get('input_accessions'):
        result['routes'].append({'name': 'supplied_accession', 'outcome': 'complete'})
    if not routes(publication) and not result['observations']:
        result['issues'].append({'route': 'selection', 'error': 'No usable publication identifiers, title or study accession'})
    for name, first_url in routes(publication):
        route = {'name': name, 'url': first_url, 'outcome': 'complete'}
        result['routes'].append(route)
        try:
            if name == 'europepmc_annotations':
                data, receipt = transport.get(first_url)
                if not isinstance(data, list):
                    raise ValueError('Unexpected annotation schema')
                for article_number, article in enumerate(data):
                    if article.get('source') != 'MED' or str(article.get('extId')) != str(publication['PMID']):
                        raise ValueError('Annotation PMID mismatch')
                    for i, annotation in enumerate(article.get('annotations', [])):
                        if annotation.get('type') != 'Accession Numbers':
                            raise ValueError('Unexpected annotation type')
                        values = [str(annotation.get('exact', ''))] + [str(t.get('uri', '')) for t in annotation.get('tags', [])]
                        for accession in sorted({a for v in values for a in ACCESSION.findall(v)}):
                            result['observations'].append({'accession': accession, 'route': name, 'receipt': receipt,
                                'locator': f'$[{article_number}].annotations[{i}]', 'evidence_kind': 'precomputed_accession_mention'})
                continue
            seen, url, count = set(), first_url, 0
            for page in range(10):
                data, receipt = transport.get(url)
                if not isinstance(data, dict) or not isinstance(data.get('hits'), list):
                    raise ValueError('Unexpected search schema')
                if data.get('expandedSynonyms') or data.get('expandedEfoTerms'):
                    raise ValueError('Unexpected native query expansion')
                for rank, hit in enumerate(data['hits']):
                    accession = hit.get('accession')
                    if hit.get('type') != 'study' or not isinstance(accession, str) or not ACCESSION.fullmatch(accession):
                        raise ValueError('Invalid BioStudies search identity')
                    result['observations'].append({'accession': accession, 'route': name, 'receipt': receipt,
                        'locator': f'$.hits[{rank}]', 'page': page + 1, 'evidence_kind': 'native_search_candidate'})
                count += len(data['hits'])
                if count > 500:
                    raise ValueError('Publication search exceeds 500 candidate checkpoint')
                cursor = data.get('nextCursor')
                if cursor is None:
                    if int(data.get('totalHits', count)) > count:
                        raise ValueError('Search results truncated without a next cursor')
                    break
                if not isinstance(cursor, str) or not cursor or cursor in seen:
                    raise ValueError('Repeated/invalid search cursor')
                seen.add(cursor)
                parts = urlsplit(url)
                params = dict(parse_qsl(parts.query)); params.pop('pagination', None); params['cursor'] = cursor
                url = parts._replace(query=urlencode(params)).geturl()
            else:
                raise ValueError('Ten-page search checkpoint reached')
        except (ValueError, OSError) as error:
            route.update(outcome='failed', error=str(error))
            result['issues'].append({'route': name, 'error': str(error)})
    result['outcome'] = 'incomplete' if result['issues'] else 'complete'
    return result


def study_record(accession, transport):
    """Collect PageTab/file-location metadata for any collection, preserving all fields."""
    native, source = transport.get(API+'studies/'+quote(accession, safe=''))
    if native.get('accno') != accession:
        raise ValueError('BioStudies accession identity mismatch')
    record = {'accession': accession, 'native': native, 'source': source, 'info': None, 'files': [], 'issues': []}
    try:
        info, receipt = transport.get(API+'studies/'+quote(accession, safe='')+'/info')
        record.update(info=info, info_source=receipt)
    except (ValueError, OSError) as error:
        record['issues'].append({'field': 'file_location_metadata', 'error': str(error)})
    seen = {}
    file_occurrences = 0
    for location, section in walk(native.get('section', {})):
        for f in flattened(section.get('files', [])):
            file_occurrences += 1
            path = f.get('path')
            if not isinstance(path, str) or not path or path.startswith('/') or '..' in path.split('/'):
                raise ValueError('Invalid native file path')
            entry = {'path': path, 'size': f.get('size'), 'context': section.get('type'),
                     'attributes': f.get('attributes', []), 'locator': location+'.files', 'native': f}
            if path in seen and seen[path]['native'] != f:
                raise ValueError('Conflicting repeated native file path')
            if path not in seen:
                seen[path] = entry
                record['files'].append(entry)
        if any(k.casefold() in ('filelist', 'filelists') for k in section):
            record['issues'].append({'field': 'files', 'error': 'External file-list metadata requires expansion', 'locator': location})
    record['file_occurrences'] = file_occurrences
    # Native totals can count the same file path in several sections.
    if record['info'] and isinstance(record['info'].get('files'), int) and record['info']['files'] not in (len(record['files']), file_occurrences):
        record['issues'].append({'field': 'files', 'error': 'Listed file count differs from API total; inventory incomplete'})
    # Keep native publication/ontology links for association checking and future use.
    record['links'] = [link for _, section in walk(native.get('section', {})) for link in flattened(section.get('links', []))]
    return record


def association(publication, study):
    """Report explicit identifier support without treating a search hit as proof."""
    observed = {(attributes(link).get('type', '').casefold(), str(link.get('url', '')).casefold()) for link in study['links']}
    confirmed = []
    for label, value in [('DOI', publication.get('DOI')), ('PMID', publication.get('PMID')), ('PMC', publication.get('PMCID'))]:
        if value and (label.casefold(), str(value).casefold()) in observed:
            confirmed.append(label)
    return {'evidence_kind': 'native_publication_identifier' if confirmed else 'search_or_annotation_candidate', 'matched_identifiers': confirmed}


def project(database, index_registry=None):
    """Export retrieved study hits; retain every search outcome in canonical records."""
    rows = {'Publications': [], 'Supplementary Files': []}
    studies = database['studies']
    keys = {native_key(acc, f['path']) for acc, study in studies.items() for f in study['files']}
    indices = assign_indices('BST', keys, index_registry) if keys else {}
    for publication in database['publications']:
        p = publication['publication']
        accessions = sorted({o['accession'] for o in publication['observations'] if o['accession'] in studies})
        for accession in accessions:
            row = {k: p.get(k) for k in ('Publication Index', 'PMID', 'PMCID', 'DOI', 'Title')}
            study = studies[accession]; native = study['native']; top = attributes(native)
            section = native.get('section', {}); root_attributes = attributes(section) if isinstance(section, dict) else {}
            publication_attributes = {}
            for _, node in walk(section):
                if node.get('type') == 'Publication':
                    for key, value in attributes(node).items():
                        previous = publication_attributes.get(key)
                        publication_attributes[key] = value if not previous or previous == value else previous+'\n'+value
            info = study.get('info') or {}
            files = study['files']
            row.update({'BioStudies Accession': accession, 'Collection': top.get('attachto'), 'Data Source': top.get('datasource'),
                'Release Date': top.get('releasedate'), 'Public': info.get('isPublic'),
                'Title': root_attributes.get('title') or top.get('title') or p.get('Title'),
                'Journal': publication_attributes.get('journal'), 'Publication Date': publication_attributes.get('publication date'),
                'Volume': publication_attributes.get('volume'), 'Pages': publication_attributes.get('pages'),
                'Abstract': root_attributes.get('abstract') or root_attributes.get('description'),
                'File Count': None if study['issues'] else len(files),
                'Total Size (Bytes)': sum(f['size'] for f in files) if not study['issues'] and all(isinstance(f.get('size'), int) for f in files) else None,
                'Study URL': 'https://www.ebi.ac.uk/biostudies/studies/'+accession,
                'Metadata API URL': API+'studies/'+accession, 'HTTP Files Root': info.get('httpLink'), 'FTP Files Root': info.get('ftpLink')})
            rows['Publications'].append(row)
            for f in files:
                path = f['path']
                url = path if urlsplit(path).scheme in ('https', 'http', 'ftp') else None
                if not url and info.get('httpLink'):
                    url = info['httpLink'].rstrip('/') + '/Files/' + quote(path, safe='/')
                rows['Supplementary Files'].append({'Publication Index': p['Publication Index'], 'BioStudies Accession': accession,
                    'BioStudies Index': indices[native_key(accession, path)], 'Filename': path.rsplit('/', 1)[-1],
                    'File Type': Path(urlsplit(path).path).suffix.lower() or None, 'Size (Bytes)': f.get('size'),
                    'Context': f.get('context'), 'File URL': url})
    return rows


def run_collection(source, output, *, registry=None, pubmed=None, template=TEMPLATE, caches=(), offline=False, resume=False, index_registry=DEFAULT_REGISTRY):
    """Run or resume bounded discovery; preserve failures distinctly from no hits."""
    source, output, template = Path(source), Path(output), Path(template)
    selected = select_publications(source, registry, pubmed)
    binding = {'input_sha256': digest(source.read_bytes()), 'registry_sha256': digest(Path(registry).read_bytes()) if registry else None,
               'template_sha256': digest(template.read_bytes()), 'index_registry': str(Path(index_registry).resolve()),
               'pubmed_sha256': digest(resolve_json_path(pubmed).read_bytes()) if pubmed else None}
    registration = json.loads(template.with_suffix('.manifest.json').read_text(encoding='utf-8'))
    if registration['sha256'] != binding['template_sha256']:
        raise ValueError('Template registration hash mismatch')
    if output.exists() and not resume:
        raise FileExistsError(output)
    if (output/'BioStudies-Enrichment.xlsx').exists():
        raise FileExistsError('Completed output exists; use a new run directory')
    output.mkdir(parents=True, exist_ok=resume)
    state = output/'state.json'
    if state.exists() and json.loads(state.read_text()) != binding:
        raise ValueError('Input, template, registry or index configuration changed since checkpoint')
    save(state, binding)
    (output/'source-publications.json').write_bytes(source.read_bytes())
    pubs_dir, studies_dir = output/'publications', output/'studies'
    pubs_dir.mkdir(exist_ok=True); studies_dir.mkdir(exist_ok=True)
    transport = Transport(output, caches, offline)
    database = {'schema_version': 'biostudies-enrichment/1', **binding, 'publications': [], 'studies': {}, 'issues': []}
    for p in selected:
        checkpoint = pubs_dir/(p['Publication Index']+'.json')
        record = json.loads(checkpoint.read_text(encoding='utf-8')) if checkpoint.exists() else None
        if not record or record['issues']:
            record = discover(p, transport)
            save(checkpoint, record)
        elif record['publication'] != p:
            raise ValueError('Checkpoint publication identity conflict')
        database['publications'].append(record)
        save(output/'requests.json', transport.requests)
        print(f'{len(database["publications"])}/{len(selected)} publication searches; {len(record["observations"])} observations', flush=True)
    for accession in sorted({o['accession'] for p in database['publications'] for o in p['observations']}):
        checkpoint = studies_dir/(accession+'.json')
        record = json.loads(checkpoint.read_text(encoding='utf-8')) if checkpoint.exists() else None
        try:
            if not record or record['issues']:
                record = study_record(accession, transport)
                save(checkpoint, record)
            database['studies'][accession] = record
        except (ValueError, OSError) as error:
            database['issues'].append({'accession': accession, 'error': str(error)})
        save(output/'requests.json', transport.requests)
    for publication in database['publications']:
        p = publication['publication']
        for observation in publication['observations']:
            if observation['accession'] in database['studies']:
                observation.update(association(p, database['studies'][observation['accession']]))
        database['issues'].extend({'Publication Index': p['Publication Index'], **i} for i in publication['issues'])
    for accession, study in database['studies'].items():
        database['issues'].extend({'accession': accession, **i} for i in study['issues'])
    database['rows'] = project(database, index_registry)
    database['status'] = 'incomplete' if database['issues'] else 'complete'
    database['collector_sha256'] = digest(Path(__file__).read_bytes())
    if Path(index_registry).exists():
        database['index_registry_sha256'] = digest(Path(index_registry).read_bytes())
    database['summary'] = {'publications': len(selected), 'studies': len(database['studies']),
        'publications_with_studies': sum(any(o['accession'] in database['studies'] for o in p['observations']) for p in database['publications']),
        'distinct_files': len({r['BioStudies Index'] for r in database['rows']['Supplementary Files']}),
        'publication_file_rows': len(database['rows']['Supplementary Files']), 'issues': len(database['issues']),
        'requests_this_execution': len(transport.requests), 'verified_reused_responses': transport.reused, 'supplemental_downloads': 0}
    save(output/'database.json', database); save(output/'summary.json', database['summary'])
    if database['studies'] or (not database['issues']):
        path = output/'BioStudies-Enrichment.xlsx'
        receipt = export_registered(template, path, database['rows'], overflow_sidecar=True)
        receipt['source_database_sha256'] = digest((output/'database.json').read_bytes())
        save(path.with_suffix('.manifest.json'), receipt)
    print(json.dumps(database['summary'], indent=2), flush=True)
    return database


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--registry', type=Path)
    parser.add_argument('--pubmed', type=Path, help='Optional saved PubMed enrichment with explicit study accession links')
    parser.add_argument('--template', type=Path, default=TEMPLATE)
    parser.add_argument('--cache-root', type=Path, action='append', default=[])
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--index-registry', type=Path, default=DEFAULT_REGISTRY)
    a = parser.parse_args()
    result = run_collection(a.input, a.output_dir, registry=a.registry, pubmed=a.pubmed, template=a.template,
                            caches=a.cache_root, offline=a.offline, resume=a.resume, index_registry=a.index_registry)
    return 0 if result['status'] == 'complete' else 1


if __name__ == '__main__':
    raise SystemExit(main())
