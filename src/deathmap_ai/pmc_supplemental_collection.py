"""Collect PMC supplementary metadata and export the registered three-sheet view.

Inputs are publication JSON and an optional persistent publication registry.
Only article identity, explicit supplementary entries, cloud listings and cloud
JSON are interpreted. Raw article XML is preserved but prose is never searched;
media objects are listed, never downloaded. Different identifier namespaces and
article versions remain separate in canonical evidence.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
import re
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
import xml.etree.ElementTree as ET

from .enrichment_export import export_registered
from .supplemental_enrichment import parse_xml, text

BUCKET = 'https://pmc-oa-opendata.s3.amazonaws.com/'
EFETCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'
S3NS = {'s': 'http://s3.amazonaws.com/doc/2006-03-01/'}
XLINK = '{http://www.w3.org/1999/xlink}href'


def utc():
    """Return a timezone-qualified retrieval/execution timestamp."""
    return datetime.now(timezone.utc).isoformat()


def sha(body):
    """Hash exact saved bytes, not decoded or reserialized text."""
    return hashlib.sha256(body).hexdigest()


def write_json(path, value):
    """Replace one owned checkpoint atomically; caller owns its run directory."""
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


class NoRedirect(HTTPRedirectHandler):
    """Reject unaccounted redirects; authorized endpoints are already canonical."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Transport:
    """Bounded metadata transport with exact-URL, hash-verified cache reuse.

    Workers share rate/request/byte accounting. Each request is limited to 10 MB,
    30 seconds and one transient retry. Receipt and raw bytes are saved separately;
    a reused response keeps its original retrieval date and names its source.
    """

    def __init__(self, output, caches=(), max_requests=2000, max_bytes=300_000_000):
        self.output = Path(output)
        self.native = self.output / 'native'
        self.native.mkdir(exist_ok=True)
        self.caches = [Path(c) / 'native' for c in caches]
        self.max_requests, self.max_bytes = max_requests, max_bytes
        self.requests, self.total_bytes, self.reused = [], 0, 0
        self.lock = threading.Lock()
        self.key_locks = {}
        self.last_eutils = 0.0

    def fetch(self, url):
        """Return native response bytes and receipt; never request attachments."""
        if not (url.startswith(BUCKET) or url.startswith(EFETCH)):
            raise ValueError('Endpoint outside PMC metadata scope')
        if url.startswith(BUCKET) and '?' not in url and not url.endswith('.json'):
            raise ValueError('Cloud media/object download excluded')
        key = sha(url.encode())
        with self.lock:
            key_lock = self.key_locks.setdefault(key, threading.Lock())
        with key_lock:
            for base in [self.native, *self.caches]:
                rp, bp = base / (key + '.json'), base / (key + '.body')
                if rp.exists() and bp.exists():
                    receipt = json.loads(rp.read_text(encoding='utf-8'))
                    body = bp.read_bytes()
                    if receipt.get('url') != url or receipt.get('sha256') != sha(body):
                        raise ValueError('Cache request identity or hash mismatch')
                    if base != self.native:
                        (self.native / bp.name).write_bytes(body)
                        receipt = {**receipt, 'reused_from': str(bp.resolve()), 'reused_utc': utc()}
                        write_json(self.native / rp.name, receipt)
                        with self.lock:
                            self.reused += 1
                    return body, receipt
            for attempt in range(2):
                with self.lock:
                    if len(self.requests) >= self.max_requests or self.total_bytes >= self.max_bytes:
                        raise RuntimeError('Run metadata request/byte cap reached')
                    if url.startswith(EFETCH):
                        delay = .4 - (time.monotonic() - self.last_eutils)
                        if delay > 0:
                            time.sleep(delay)
                        self.last_eutils = time.monotonic()
                    receipt = {'url': url, 'attempt': attempt + 1, 'retrieved_utc': utc()}
                    self.requests.append(receipt)
                try:
                    opener = build_opener(NoRedirect())
                    with opener.open(Request(url, headers={'User-Agent': 'DeathMap-AI/0.1 pmc-supplemental'}), timeout=30) as response:
                        body = response.read(10_000_001)
                        receipt.update(http_status=response.status, bytes=len(body), final_url=response.url)
                    with self.lock:
                        self.total_bytes += len(body)
                    if len(body) > 10_000_000 or self.total_bytes > self.max_bytes:
                        raise RuntimeError('Metadata response/run byte cap reached')
                    receipt.update(sha256=sha(body), body=str(Path('native') / (key + '.body')))
                    (self.native / (key + '.body')).write_bytes(body)
                    write_json(self.native / (key + '.json'), receipt)
                    return body, receipt
                except Exception as exc:
                    receipt['error'] = f'{type(exc).__name__}: {exc}'
                    transient = isinstance(exc, (URLError, TimeoutError, ConnectionError))
                    if isinstance(exc, HTTPError):
                        transient = exc.code in (429, 500, 502, 503, 504)
                    if attempt or not transient:
                        raise
                    wait = 2
                    if isinstance(exc, HTTPError) and exc.headers.get('Retry-After'):
                        value = exc.headers['Retry-After']
                        wait = int(value) if value.isdigit() else max(0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
                    if wait > 60:
                        raise RuntimeError('Retry-After exceeds bounded retry allowance') from exc
                    time.sleep(max(2, wait))


def load_publications(path, registry=None):
    """Read publication records, preserving pilot indices and registry identities.

    Native ORCS IDs or exact PMIDs join the registry. An existing input Publication
    Index is retained; the registry index remains a separate canonical crosswalk.
    Titles are display metadata, never discovery queries.
    """
    payload = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    source = payload.get('publications') if isinstance(payload, dict) else payload
    if not isinstance(source, list):
        raise ValueError('Expected publication array')
    registrations = json.loads(Path(registry).read_text()) if registry else []
    native = {str(r['ORCS Publication ID']): r for r in registrations}
    pmids = {str(r['PMID']): r for r in registrations if r.get('PMID')}
    result = []
    for item in source:
        pmid = str(item['PMID']) if item.get('PMID') else None
        match = native.get(str(item.get('PUBLICATION_ID'))) or pmids.get(pmid)
        if match and pmid and str(match.get('PMID')) != pmid:
            raise ValueError('Registry/native publication identity conflict')
        index = item.get('Publication Index') or (match or {}).get('Publication index')
        if not index:
            raise ValueError('Publication Index or matching registry entry required')
        pmcid = item.get('PMCID')
        if pmcid:
            pmcid = str(pmcid).strip().upper()
            if not re.fullmatch(r'PMC[1-9][0-9]*', pmcid):
                raise ValueError('Invalid PMCID')
        result.append({'Publication Index': index, 'PMID': pmid, 'DOI': item.get('DOI'),
                       'PMCID': pmcid, 'Title': item.get('TITLE') or item.get('Publication Title') or item.get('Title'),
                       'ORCS Publication ID': item.get('PUBLICATION_ID') or (match or {}).get('ORCS Publication ID'),
                       'ORCS Publication Index': (match or {}).get('Publication index')})
    if len({p['Publication Index'] for p in result}) != len(result):
        raise ValueError('Duplicate selected Publication Index')
    return result


def extract_entries(body, publication):
    """Validate XML identity and retain explicit supplemental entries only."""
    # PMCID/PMID constrain article identity. Missing DOI is not a conflicting DOI.
    parsed = parse_xml(body, {k: publication[k] for k in ('PMCID', 'PMID')})
    observed_dois = parsed['identifiers'].get('DOI', [])
    if publication.get('DOI') and observed_dois and any(v.lower() != publication['DOI'].lower() for v in observed_dois):
        raise ValueError('XML DOI conflicts with input')
    root = ET.fromstring(body)
    for node in root.iter():
        node.tag = node.tag.split('}')[-1]
    article = root if root.tag == 'article' else root.find('article')
    entries = []

    def walk(node, location):
        if node.tag in ('ref-list', 'sub-article'):
            return
        if node.tag in ('supplementary-material', 'inline-supplementary-material'):
            native = node.get('id') or location
            sid = 'SUP-' + publication['PMCID'] + '-' + sha(native.encode())[:12]
            record = {'Supplemental Index': sid, 'Label': text(node.find('label')),
                      'Title': text(node.find('./caption/title')), 'Caption': text(node.find('caption')),
                      'Supplemental DOI': '\n'.join(filter(None, [text(n) for n in node.findall('object-id') if n.get('pub-id-type') == 'doi'])) or None,
                      'native_id': node.get('id'), 'xml_locator': location, 'files': []}

            def files(element, loc):
                if element is not node and element.tag in ('permissions', 'license', 'ref-list', 'supplementary-material', 'inline-supplementary-material'):
                    return
                href = element.get(XLINK) or element.get('href')
                if href:
                    record['files'].append({'href': href, 'filename': unquote(urlsplit(href).path.rsplit('/', 1)[-1]),
                                            'xml_locator': loc, 'media_type': '/'.join(filter(None, [element.get('mimetype'), element.get('mime-subtype')]))})
                counts = {}
                for child in element:
                    counts[child.tag] = counts.get(child.tag, 0) + 1
                    files(child, f'{loc}/{child.tag}[{counts[child.tag]}]')
            files(node, location)
            # The same native ID may occur in inline and back-matter entries;
            # keep both observations with separate keys rather than merging them.
            if any(e['Supplemental Index'] == sid for e in entries):
                sid += '-' + sha(location.encode())[:6]
                record['Supplemental Index'] = sid
            entries.append(record)
        counts = {}
        for child in node:
            counts[child.tag] = counts.get(child.tag, 0) + 1
            walk(child, f'{location}/{child.tag}[{counts[child.tag]}]')
    walk(article, '/article')
    parsed['supplementary_entries'] = entries
    parsed['entry_count'] = len(entries)
    return parsed


def http_url(key):
    """Convert a verified cloud object key to the documented HTTPS location."""
    return BUCKET + quote(key, safe='/')


def collect_one(publication, transport):
    """Collect one publication's XML and every distributed cloud version."""
    p = dict(publication)
    result = {'publication': p, 'issues': [], 'xml': None, 'versions': [], 'cloud_files': []}
    pmc = p['PMCID']
    if not pmc:
        result.update(xml_result='no_pmcid', cloud_result='no_pmcid')
        return result
    try:
        url = EFETCH + urlencode({'db': 'pmc', 'id': pmc[3:], 'rettype': 'full', 'retmode': 'xml'})
        body, receipt = transport.fetch(url)
        result['xml'] = {**extract_entries(body, p), 'receipt': receipt}
        result['xml_result'] = 'full_xml' if result['xml']['has_body'] else 'metadata_only'
    except Exception as exc:
        result['xml_result'] = 'failed'
        result['issues'].append({'route': 'xml', 'error': f'{type(exc).__name__}: {exc}'})
    try:
        objects, token = [], None
        for page in range(10):
            query = {'list-type': '2', 'prefix': pmc + '.', 'max-keys': '1000'}
            if token:
                query['continuation-token'] = token
            url = BUCKET + '?' + urlencode(query)
            body, receipt = transport.fetch(url)
            tree = ET.fromstring(body)
            objects.extend({'key': n.findtext('s:Key', namespaces=S3NS), 'size': int(n.findtext('s:Size', namespaces=S3NS)),
                            'receipt': receipt} for n in tree.findall('s:Contents', S3NS))
            if tree.findtext('s:IsTruncated', namespaces=S3NS) != 'true':
                break
            token = tree.findtext('s:NextContinuationToken', namespaces=S3NS)
            if not token:
                raise ValueError('Truncated listing has no continuation token')
        else:
            raise RuntimeError('Article prefix listing exceeds pagination cap')
        json_keys = [o['key'] for o in objects if re.fullmatch(re.escape(pmc) + r'\.[0-9]+/' + re.escape(pmc) + r'\.[0-9]+\.json', o['key'])]
        for key in json_keys:
            body, receipt = transport.fetch(http_url(key))
            metadata = json.loads(body)
            observed = str(metadata.get('pmcid', ''))
            if not observed.startswith('PMC'):
                observed = 'PMC' + observed
            if observed != pmc:
                raise ValueError('Cloud metadata PMCID conflict')
            for field, expected in [('pmid', p.get('PMID')), ('doi', p.get('DOI'))]:
                if metadata.get(field) and expected and str(metadata[field]).lower() != str(expected).lower():
                    raise ValueError('Cloud metadata identifier conflict: ' + field)
            version = key.split('/')[0]
            result['versions'].append({'version': version, 'metadata': metadata, 'receipt': receipt})
            for obj in objects:
                if not obj['key'].startswith(version + '/'):
                    continue
                filename = obj['key'].rsplit('/', 1)[-1]
                if filename in {version + suffix for suffix in ('.xml', '.json', '.txt', '.pdf')}:
                    continue
                result['cloud_files'].append({**obj, 'version': version, 'filename': filename})
        result['cloud_result'] = 'listed' if json_keys else 'no_distributed_version'
    except Exception as exc:
        result['cloud_result'] = 'failed'
        result['issues'].append({'route': 'cloud', 'error': f'{type(exc).__name__}: {exc}'})
    return result


def joined(values):
    """Keep distinct supplied strings in order, leaving absent values blank."""
    present = list(dict.fromkeys(str(v) for v in values if v is not None and v != ''))
    return '\n'.join(present) or None


def consensus(values):
    """Return a supplied flag only when all available versions agree."""
    present = [v for v in values if v is not None]
    return present[0] if present and all(v == present[0] for v in present) else None


def project(records):
    """Project canonical observations into the owner-selected three sheets.

    Entry/file links require the same PMCID, XML version and exact filename.
    Other-version name matches remain candidates in JSON rather than asserted
    links. Multiple matching entry indices/captions remain newline-separated.
    Unmatched cloud files are retained with blank supplemental fields.
    """
    rows = {'Publications': [], 'Supplementary Entries': [], 'Cloud Files': []}
    for record in records:
        p, xml, versions = record['publication'], record.get('xml'), record['versions']
        entries = xml['supplementary_entries'] if xml else []
        xml_versions = xml['identifiers'].get('versions', []) if xml else []
        selected = [v for v in versions if v['version'] in xml_versions] or versions
        metadata = [v['metadata'] for v in selected]
        pub = {**{k: p.get(k) for k in ('Publication Index', 'PMCID', 'PMID', 'DOI')},
               'Title': (xml or {}).get('title') or p.get('Title') or joined(m.get('title') for m in metadata),
               'Citation': joined(m.get('citation') for m in metadata),
               'XML Version': joined(xml_versions), 'XML Source': xml['receipt']['url'] if xml else None,
               'XML Entries': len(entries) if xml else None,
               'Distinct XML File References': len({f['href'] for e in entries for f in e['files']}) if xml else None,
               'Cloud Versions': len(versions) if record['cloud_result'] in ('listed', 'no_distributed_version') else None,
               'Cloud Media Files': len(record['cloud_files']) if record['cloud_result'] in ('listed', 'no_distributed_version') else None,
               'Open Access': consensus([m.get('is_pmc_openaccess') for m in metadata]),
               'Author Manuscript': consensus([m.get('is_manuscript') for m in metadata]),
               'Retracted': consensus([m.get('is_retracted') for m in metadata]),
               'Article PDF URL': joined(http_url(unquote(urlsplit(m['pdf_url']).path).lstrip('/')) for m in metadata if m.get('pdf_url'))}
        if not metadata and xml:
            flags = xml.get('pmc_properties', {})
            pub['Open Access'] = {'yes': True, 'no': False}.get(flags.get('pmc-prop-open-access'))
            pub['Author Manuscript'] = {'yes': True, 'no': False}.get(flags.get('pmc-prop-manuscript'))
        rows['Publications'].append(pub)
        for e in entries:
            rows['Supplementary Entries'].append({'Publication Index': p['Publication Index'],
                **{k: e.get(k) for k in ('Supplemental Index', 'Label', 'Title', 'Caption', 'Supplemental DOI')},
                'Filename': joined(f['filename'] for f in e['files']),
                'Native Reference File': joined(f['href'] for f in e['files'])})
        for obj in record['cloud_files']:
            matches = [e for e in entries if obj['version'] in xml_versions and any(f['filename'] == obj['filename'] for f in e['files'])]
            candidates = [e['Supplemental Index'] for e in entries if any(f['filename'] == obj['filename'] for f in e['files'])]
            obj['matching_supplemental_indices'] = [e['Supplemental Index'] for e in matches]
            obj['filename_candidates'] = candidates
            rows['Cloud Files'].append({'Publication Index': p['Publication Index'],
                'Supplemental Index': joined(e['Supplemental Index'] for e in matches),
                'Cloud Index': 'CLD-' + obj['version'] + '-' + sha(obj['key'].encode())[:12],
                'Filename': obj['filename'], 'File Type': Path(obj['filename']).suffix.lower() or None,
                'Size (bytes)': obj['size'], 'Label': joined(e.get('Label') for e in matches),
                'Title': joined(e.get('Title') for e in matches), 'Caption': joined(e.get('Caption') for e in matches),
                'File URL': http_url(obj['key'])})
    return rows


def run_collection(input_path, output, template, *, registry=None, caches=(), workers=4, resume=False):
    """Run/resume a bounded collection; save JSON and one registered workbook."""
    source, output, template = Path(input_path), Path(output), Path(template)
    publications = load_publications(source, registry)
    input_hash, template_hash = sha(source.read_bytes()), sha(template.read_bytes())
    registration = json.loads(template.with_suffix('.manifest.json').read_text())
    if registration['sha256'] != template_hash:
        raise ValueError('Template registration hash mismatch')
    if output.exists() and not resume:
        raise FileExistsError(output)
    output.mkdir(parents=True, exist_ok=resume)
    state_path = output / 'state.json'
    state = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {}
    if state and (state['input_sha256'] != input_hash or state['template_sha256'] != template_hash):
        raise ValueError('Input/template changed since checkpoint')
    if not state:
        write_json(state_path, {'input_sha256': input_hash, 'template_sha256': template_hash, 'records': []})
    record_dir = output / 'records'
    record_dir.mkdir(exist_ok=True)
    saved = [json.loads(path.read_text(encoding='utf-8')) for path in record_dir.glob('*.json')]
    results = {r['publication']['Publication Index']: r for r in saved if not r['issues']}
    transport = Transport(output, caches)
    pending = [p for p in publications if p['Publication Index'] not in results]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(collect_one, p, transport): p for p in pending}
        for future in as_completed(futures):
            item = future.result()
            results[item['publication']['Publication Index']] = item
            ordered = [results[p['Publication Index']] for p in publications if p['Publication Index'] in results]
            write_json(record_dir / (item['publication']['Publication Index'] + '.json'), item)
            n = len(results)
            if n % 20 == 0 or n == len(publications):
                write_json(state_path, {'input_sha256': input_hash, 'template_sha256': template_hash, 'records': ordered})
                write_json(output / 'requests.json', transport.requests)
                print(f'{n}/{len(publications)} publications; {len(transport.requests)} requests; {sum(bool(r["issues"]) for r in ordered)} with retrieval issues', flush=True)
    records = [results[p['Publication Index']] for p in publications]
    rows = project(records)
    issues = [{'Publication Index': r['publication']['Publication Index'], **i} for r in records for i in r['issues']]
    summary = {'publications': len(publications), 'with_pmcid': sum(bool(p['PMCID']) for p in publications),
               'with_supplementary_entries': sum(bool(r.get('xml') and r['xml']['entry_count']) for r in records),
               'supplementary_entries': len(rows['Supplementary Entries']), 'cloud_files': len(rows['Cloud Files']),
               'unmatched_cloud_files': sum(not row['Supplemental Index'] for row in rows['Cloud Files']),
               'publications_with_issues': sum(bool(r['issues']) for r in records),
               'network_requests_this_execution': len(transport.requests), 'verified_reused_responses': transport.reused,
               'metadata_bytes_this_execution': transport.total_bytes, 'completed_utc': utc(),
               'supplement_downloads': 0, 'article_prose_extracted': False}
    data = {'schema_version': 'pmc-supplemental-enrichment/1', 'input_sha256': input_hash,
            'template_sha256': template_hash, 'publications': records, 'rows': rows, 'issues': issues, 'summary': summary}
    data['collector_sha256'] = sha(Path(__file__).read_bytes())
    data['registry_sha256'] = sha(Path(registry).read_bytes()) if registry else None
    write_json(output / 'selected-publications.json', publications)
    write_json(output / 'database.json', data)
    write_json(output / 'summary.json', summary)
    workbook = output / 'PMC-Supplemental-Enrichment.xlsx'
    if workbook.exists():
        raise FileExistsError('Use a new export path after an already completed run')
    receipt = export_registered(template, workbook, rows, overflow_sidecar=True)
    receipt.update(source_database_sha256=sha((output / 'database.json').read_bytes()))
    write_json(workbook.with_suffix('.manifest.json'), receipt)
    print(json.dumps(summary, indent=2), flush=True)
    return data


def main():
    """CLI: independently collect any selected publications, without ORCS queries."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--registry', type=Path)
    parser.add_argument('--template', type=Path, default=Path(__file__).resolve().parents[2] / 'data/templates/PMC-Supplemental-Enrichment.xlsx')
    parser.add_argument('--cache-root', type=Path, action='append', default=[])
    parser.add_argument('--workers', type=int, choices=range(1, 5), default=4)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    result = run_collection(args.input, args.output_dir, args.template, registry=args.registry,
                            caches=args.cache_root, workers=args.workers, resume=args.resume)
    return 1 if result['issues'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
