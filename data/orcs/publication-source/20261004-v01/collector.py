"""Build shared ORCS publication metadata alongside the complete screen index.

The public browse listing supplies explicit SCREEN_ID -> /Dataset/ publication
page associations. Publication headers supply bibliographic text and asset links.
No linked files, screen-score endpoints or external bibliographic sites are read.
Page-reported identifiers remain separate from cached source identifiers when
they disagree; publication pages named Dataset are not repository datasets.
"""
import argparse
import csv
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

BASE = 'https://orcs.thebiogrid.org'
VERSION = 'orcs-publications-v1.0'
VOID = {'input', 'meta', 'link', 'br', 'img', 'hr', 'source', 'area', 'wbr'}


def now():
    """UTC timestamp for source receipts, independent of local display time."""
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    """Hash saved source bytes for reproducibility and corruption detection."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    """Atomically persist a resumable receipt or metadata table as UTF-8 JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


class Element:
    """Minimal HTML tree, used only for the bounded publication header."""
    def __init__(self, tag, attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def text(self):
        return ' '.join(' '.join(x.text() if isinstance(x, Element) else x for x in self.children).split())

    def find(self, tag=None, cls=None):
        result = []
        for child in self.children:
            if isinstance(child, Element):
                if (tag is None or child.tag == tag) and (cls is None or cls in child.attrs.get('class', '').split()):
                    result.append(child)
                result.extend(child.find(tag, cls))
        return result


class HeaderParser(HTMLParser):
    """Parse reported text and links without executing scripts or opening assets."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element('root')
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Element(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, text):
        self.stack[-1].children.append(text)


def excerpt(body, publication_id):
    """Validate native page identity and retain only the publication header HTML.

    A missing boundary fails explicitly instead of saving unexpected screen or
    results content. The returned excerpt excludes the dynamically loaded list.
    """
    text = body.decode('utf-8') if isinstance(body, bytes) else body
    identity = re.search(r"<input\b[^>]*id=['\"]datasetID['\"][^>]*value=['\"](\d+)['\"]", text)
    start = re.search(r"<div\b[^>]*id=['\"]resultsHeaderBlock['\"]", text)
    if not identity or identity[1] != str(publication_id) or not start or 'CRISPR Publication Summary' not in text:
        raise ValueError('Publication identity/header boundary missing or mismatched')
    return text[start.start():identity.start()]


def association_index(browse, screens):
    """Require the whole website screen set and preserve direct page associations.

    Native cache SOURCE_TYPE/SOURCE_ID pairs are retained exactly, including
    prepub identifiers. A page must correspond to one unambiguous native pair.
    """
    native = {s['SCREEN_ID']: s for s in screens}
    if len(native) != len(screens):
        raise ValueError('Duplicate cached SCREEN_ID')
    groups, links, seen = {}, [], set()
    for row in browse['data']:
        sid = str(row[1])
        match = re.search(r'/Dataset/(\d+)', row[2])
        if sid not in native or sid in seen or not match:
            raise ValueError('Unknown/duplicate screen or missing publication page association')
        seen.add(sid)
        pid = match[1]
        pair = (native[sid]['SOURCE_TYPE'], native[sid]['SOURCE_ID'])
        group = groups.setdefault(pid, {'SOURCE_TYPE': pair[0], 'SOURCE_ID': pair[1], 'SCREEN_IDS': []})
        if pair != (group['SOURCE_TYPE'], group['SOURCE_ID']):
            raise ValueError('Conflicting cached identities for one ORCS publication page')
        group['SCREEN_IDS'].append(sid)
        links.append({'SCREEN_ID': sid, 'PUBLICATION_ID': pid, 'SOURCE_TYPE': pair[0], 'SOURCE_ID': pair[1],
                      'PUBLICATION_URL': BASE + '/Dataset/' + pid,
                      'EVIDENCE_STATUS': 'direct website browse association; cached source identity'})
    if seen != set(native) or int(browse['recordsFiltered']) != len(native):
        raise ValueError('Website browse coverage differs from the saved complete screen index')
    return groups, links


def parse_publication(html, pid, group):
    """Extract source-reported bibliography, preserving identifier conflicts.

    PUBMED-labelled small numbers on prepub pages are retained as page assertions
    rather than promoted to verified PMIDs. Missing journal/abstract fields stay
    null. Supplementary URLs are mentions, not confirmed experimental datasets.
    """
    parser = HeaderParser()
    parser.feed(html)
    root = parser.root
    titles = root.find('h1')
    if len(titles) != 1 or not titles[0].text():
        raise ValueError('Missing or ambiguous publication title')
    authors, abstracts = root.find('div', 'subhead'), root.find('div', 'bgGrey')
    citations = [n for n in root.find('div', 'linkouts') if 'PUBMED:' in n.text() or 'DOI:' in n.text()]
    if len(citations) != 1:
        raise ValueError('Missing or ambiguous publication citation')
    citation = citations[0]
    text = citation.text()
    date = re.search(r'\b\d{4}-\d{2}-\d{2}\b', text)
    assertion = re.search(r'(PUBMED|DOI):\s*(\S+)', text)
    journal_nodes = citation.find('strong')
    links = [{'label': a.text(), 'url': urljoin(BASE, a.attrs['href'])}
             for a in root.find('a') if a.attrs.get('href')]
    assets = []
    for node in root.find('div', 'linkouts'):
        if 'Supplementary Files:' in node.text():
            assets.extend({'label': a.text(), 'url': urljoin(BASE, a.attrs['href'])}
                          for a in node.find('a') if a.attrs.get('href'))
    page_type = {'PUBMED': 'pubmed', 'DOI': 'doi'}.get(assertion[1]) if assertion else None
    page_id = assertion[2] if assertion else None
    agreed = page_type == group['SOURCE_TYPE'] and page_id == group['SOURCE_ID']
    issues = [] if agreed else ['Page-labelled source identifier differs from cached SOURCE_TYPE/SOURCE_ID; both preserved.']
    if '\ufffd' in root.text():
        issues.append('Source page includes Unicode replacement characters; reported text preserved.')
    return {'PUBLICATION_ID': str(pid), 'SOURCE_TYPE': group['SOURCE_TYPE'], 'SOURCE_ID': group['SOURCE_ID'],
            'TITLE': titles[0].text(), 'AUTHORS': authors[0].text() if authors else None,
            'ABSTRACT': abstracts[0].text() if abstracts else None,
            'JOURNAL': journal_nodes[0].text() if journal_nodes else None,
            'PUBLICATION_DATE': date[0] if date else None,
            'PAGE_SOURCE_TYPE': page_type, 'PAGE_SOURCE_ID': page_id,
            'PMID': group['SOURCE_ID'] if group['SOURCE_TYPE'] == 'pubmed' and agreed else None,
            'DOI': group['SOURCE_ID'] if group['SOURCE_TYPE'] in ('doi', 'prepub') and re.fullmatch(r'10\.\d{4,9}/\S+', group['SOURCE_ID']) else None,
            'SUPPLEMENTARY_FILES': assets, 'LINKS': links,
            'SCREEN_IDS': sorted(group['SCREEN_IDS'], key=int), 'SCREEN_COUNT': len(group['SCREEN_IDS']),
            'PUBLICATION_URL': BASE + '/Dataset/' + str(pid),
            'FIELD_LOCATORS': {'TITLE': '#resultsHeaderBlock h1', 'AUTHORS': '#resultsHeaderBlock .subhead',
                               'ABSTRACT': '#resultsHeaderBlock .bgGrey', 'JOURNAL': '.linkouts citation strong',
                               'PUBLICATION_DATE': '.linkouts citation', 'SUPPLEMENTARY_FILES': '.linkouts Supplementary Files'},
            'REVIEW_ISSUES': issues}


def export_csv(path, rows):
    """Export the same JSON records as a rectangular UTF-8 table; lists stay JSON."""
    with Path(path).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()})


def fetch(url, data=None, publication_id=None):
    """Request public ORCS metadata with a 30-second timeout and bounded response.

    Publication reads stop at the header's native datasetID marker. Reads never
    follow supplementary links, downloads or screen-score routes.
    """
    request = Request(url, data=data, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
    body = b''
    start = time.monotonic()
    limit = 131072 if publication_id else 8388608
    with urlopen(request, timeout=30) as response:
        while len(body) <= limit:
            part = response.read(4096)
            if not part:
                break
            body += part
            if publication_id and re.search(br"<input\b[^>]*id=['\"]datasetID['\"][^>]*>", body):
                break
            if time.monotonic() - start > 30:
                raise TimeoutError('Metadata request time budget exceeded')
        if len(body) > limit:
            raise ValueError('Metadata response byte budget exceeded')
        return body, response.status


def build(root):
    """Resume all website-indexed publications and publish JSON/CSV only when complete.

    Durable per-page receipts reserve attempts before requests, with at most three
    cumulative attempts per publication, one-second pacing and retained failures.
    Existing scientific result workbooks and screen inputs are never modified.
    """
    folder = Path(root) / 'data/orcs'
    cache = folder / 'screen-index.json'
    cache_hash = digest(cache)
    source = folder / 'publication-source/20261004-v01'
    source.mkdir(parents=True, exist_ok=True)
    browse_file = source / 'browse-metadata.json'
    if not browse_file.exists():
        payload = {'tool': 'serverSideRows', 'type': 'browse', 'start': 0, 'length': 10000, 'draw': 1,
                   'search': {'value': '', 'regex': False}, 'order': [{'column': 1, 'dir': 'desc'}]}
        body, status = fetch(BASE + '/scripts/datatableTools.php', urlencode({'expData': json.dumps(payload)}).encode())
        browse_file.write_bytes(body)
        write(source / 'browse-receipt.json', {'retrieved_at': now(), 'http_status': status,
              'url': BASE + '/scripts/datatableTools.php', 'parameters': payload, 'sha256': digest(browse_file)})
    screens = json.loads(cache.read_text(encoding='utf-8'))
    groups, associations = association_index(json.loads(browse_file.read_text(encoding='utf-8')), screens)
    home_file = source / 'homepage.html'
    if not home_file.exists():
        home_file.write_bytes(fetch(BASE + '/')[0])
    home = home_file.read_text(encoding='utf-8')
    homepage_parser = HeaderParser()
    homepage_parser.feed(home)
    expected = re.search(r'searches\s+([\d,]+) publications', homepage_parser.root.text())
    if not expected or int(expected[1].replace(',', '')) != len(groups):
        raise ValueError('Website publication count disagrees with discovered page index')
    manifest = {'resource': 'BioGRID ORCS', 'tool_version': VERSION, 'scope': 'All ORCS publication headers; no gene-level or asset contents',
                'publication_count_expected': len(groups), 'screen_count': len(screens), 'screen_index_sha256': cache_hash,
                'browse_sha256': digest(browse_file), 'source_directory': source.relative_to(root).as_posix(),
                'timeout_seconds': 30, 'spacing_seconds': 1, 'max_cumulative_attempts_per_page': 3,
                'status': 'in_progress', 'authority': 'Owner shared publication-database request, 2026-10-04'}
    write(source / 'manifest.json', manifest)
    rows, failures = [], []
    for i, (pid, group) in enumerate(sorted(groups.items(), key=lambda x: int(x[0]))):
        raw, receipt_path = source / (pid + '.metadata.html'), source / (pid + '.receipt.json')
        receipt = json.loads(receipt_path.read_text(encoding='utf-8')) if receipt_path.exists() else {'attempts': []}
        successful = receipt.get('status') == 'success' and raw.exists() and digest(raw) == receipt.get('sha256')
        if not successful:
            while len(receipt['attempts']) < 3:
                attempt = {'reserved_at': now(), 'url': BASE + '/Dataset/' + pid, 'status': 'reserved'}
                receipt['attempts'].append(attempt)
                write(receipt_path, receipt)
                try:
                    body, status = fetch(attempt['url'], publication_id=pid)
                    html = excerpt(body, pid)
                    raw.write_text(html, encoding='utf-8')
                    parse_publication(html, pid, group)
                    attempt.update(status='success', http_status=status, completed_at=now(), response_bytes=len(body))
                    receipt.update(status='success', sha256=digest(raw), retrieved_at=now())
                    write(receipt_path, receipt)
                    successful = True
                    time.sleep(1)
                    break
                except Exception as error:
                    attempt.update(status='failed', error=str(error), completed_at=now())
                    receipt['status'] = 'failed'
                    write(receipt_path, receipt)
                    time.sleep(1)
        if successful:
            row = parse_publication(raw.read_text(encoding='utf-8'), pid, group)
            row.update(RETRIEVED_AT=receipt['retrieved_at'], SOURCE_METADATA_FILE=raw.relative_to(root).as_posix(),
                       SOURCE_METADATA_SHA256=digest(raw))
            rows.append(row)
        else:
            failures.append(pid)
        if (i + 1) % 20 == 0 or i + 1 == len(groups):
            print(f'{i+1}/{len(groups)} publication pages examined; {len(rows)} captured; {len(failures)} failed', flush=True)
    if digest(cache) != cache_hash:
        raise ValueError('Shared screen index changed during publication retrieval')
    manifest.update(publications_captured=len(rows), failed_publication_ids=failures, completed_at=now())
    if failures:
        manifest['status'] = 'incomplete'
        write(source / 'manifest.json', manifest)
        raise ValueError('Incomplete publication capture: ' + repr(failures))
    write(folder / 'publication-index.json', rows)
    export_csv(folder / 'publication-metadata.csv', rows)
    write(folder / 'publication-screen-links.json', associations)
    export_csv(folder / 'publication-screen-links.csv', associations)
    manifest.update(status='complete', publication_count=len(rows), unique_publication_ids=len({r['PUBLICATION_ID'] for r in rows}),
                    associations_count=len(associations), field_names=list(rows[0]),
                    fields_populated={k: sum(row[k] not in (None, '', [], {}) for row in rows) for k in rows[0]},
                    review_publication_ids=[r['PUBLICATION_ID'] for r in rows if r['REVIEW_ISSUES']],
                    files={name: {'sha256': digest(folder/name), 'bytes': (folder/name).stat().st_size}
                           for name in ['publication-index.json','publication-metadata.csv','publication-screen-links.json','publication-screen-links.csv']})
    write(folder / 'publication-index.manifest.json', manifest)
    write(source / 'manifest.json', manifest)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(build(args.root), indent=2))
