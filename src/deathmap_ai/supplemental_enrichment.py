"""Retrieve PMC supplementary-listing metadata from exact article identifiers.

Standalone CLI: JSON publication records in, native XML and JSON/CSV inventories
out. No ORCS dependency, article-prose extraction or supplementary-file fetching.
Internal XML attributes remain available in raw evidence rather than cluttering
reader-facing records. Listing presence does not establish scientific relevance.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


def text(element):
    """Return readable mixed XML text, retaining nested caption content."""
    return ' '.join(' '.join(element.itertext()).split()) if element is not None else None


def parse_xml(body, publication):
    """Extract identity, supplement flags and listings without searching prose.

    Parameters
    ----------
    body : bytes
        Native EFetch article XML.
    publication : dict
        PMCID required; PMID and DOI optionally constrain identity.

    Returns
    -------
    dict
        Article metadata and one record per native supplement entry.

    Raises
    ------
    ValueError
        XML has no unique article or conflicts with an input identifier.
    """
    root = ET.fromstring(body)
    # Namespace removal affects only the parsed view; original bytes are saved.
    for node in root.iter():
        node.tag = node.tag.split('}')[-1]
    articles = [root] if root.tag == 'article' else root.findall('./article')
    if len(articles) != 1:
        raise ValueError('Expected exactly one article in EFetch XML')
    article = articles[0]
    meta = article.find('./front/article-meta')
    if meta is None:
        raise ValueError('Missing article identity metadata')
    identifiers = {}
    for node in meta.findall('article-id'):
        identifiers.setdefault(node.get('pub-id-type'), []).append(text(node))
    pmcs = identifiers.get('pmcid', []) + identifiers.get('pmcaid', []) + identifiers.get('pmc', [])
    pmcs = {p if p.startswith('PMC') else 'PMC' + p for p in pmcs}
    if publication['PMCID'] not in pmcs or len(pmcs) != 1:
        raise ValueError('Article PMCID mismatch or conflict')
    for key, kind in [('PMID', 'pmid'), ('DOI', 'doi')]:
        expected = publication.get(key)
        observed = identifiers.get(kind, [])
        if expected and (not observed or any(v.lower() != str(expected).lower() for v in observed)):
            raise ValueError(f'Article {key} mismatch or unavailable for verification')
    flags = {}
    for node in meta.findall('./custom-meta-group/custom-meta'):
        name = text(node.find('meta-name'))
        if name and name.startswith('pmc-'):
            flags[name] = text(node.find('meta-value'))
    entries = []
    # Avoid counting reference-list supplements as attachments of this article.
    def walk(node, location):
        if node.tag in ('ref-list', 'sub-article'):
            return
        if node.tag in ('supplementary-material', 'inline-supplementary-material'):
            files = []
            for child in node.iter():
                href = child.get('{http://www.w3.org/1999/xlink}href') or child.get('href')
                if href:
                    files.append({k: v for k, v in {
                        'href': href, 'label': child.get('title') or child.get('{http://www.w3.org/1999/xlink}title'),
                        'media_type': '/'.join(filter(None, [child.get('mimetype'), child.get('mime-subtype')])),
                        'filename': child.get('filename'), 'size': child.get('size'),
                        'content_type': child.get('content-type'), 'description': text(child),
                    }.items() if v})
            entries.append({'label': text(node.find('label')), 'caption': text(node.find('caption')),
                            'description': text(node), 'files': files, 'xml_locator': location})
        counts = {}
        for child in node:
            counts[child.tag] = counts.get(child.tag, 0) + 1
            walk(child, f'{location}/{child.tag}[{counts[child.tag]}]')
    walk(article, '/article')
    return {'title': text(meta.find('./title-group/article-title')),
            'journal': text(article.find('./front/journal-meta/journal-title-group/journal-title')),
            'identifiers': {k: identifiers.get(v, []) for k, v in [('PMID', 'pmid'), ('DOI', 'doi'), ('versions', 'pmcid-ver')]},
            'pmc_properties': flags, 'has_body': article.find('body') is not None,
            'supplementary_entries': entries, 'entry_count': len(entries)}


def run(input_path, output_dir, xml_cache=None):
    """Run a fresh metadata pass, preserving responses and explicit failures.

    Input is a JSON array or an object with a publications array. A cache directory
    optionally supplies PMCID.xml files: their identities are revalidated and their
    hashes recorded, without claiming a new retrieval date. Existing output folders
    are refused. HTTP failures never become successful empty inventories.
    """
    source = Path(input_path)
    payload = json.loads(source.read_text(encoding='utf-8-sig'))
    publications = payload.get('publications') if isinstance(payload, dict) else payload
    if not isinstance(publications, list) or not all(isinstance(p, dict) for p in publications):
        raise ValueError('Expected a JSON publication array')
    for p in publications:
        if p.get('PMCID'):
            p['PMCID'] = str(p['PMCID']).strip().upper()
            if not re.fullmatch(r'PMC[1-9][0-9]*', p['PMCID']):
                raise ValueError('Invalid PMCID: ' + p['PMCID'])
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'input.json').write_bytes(source.read_bytes())
    results, requests = [], []
    for p in publications:
        record = {k: p.get(k) for k in ('Publication Index', 'PMCID', 'PMID', 'DOI')}
        pmc = p.get('PMCID')
        if not pmc:
            record['status'] = 'no_pmcid'
            results.append(record)
            continue
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?' + urlencode(dict(db='pmc', id=pmc[3:], rettype='full', retmode='xml'))
        record['url'] = url
        cache = Path(xml_cache) / (pmc + '.xml') if xml_cache else None
        try:
            if cache and cache.is_file():
                body = cache.read_bytes()
                record['reused_from'] = str(cache.resolve())
            else:
                for attempt in range(2):
                    receipt = dict(url=url, attempted_utc=datetime.now(timezone.utc).isoformat(), attempt=attempt + 1)
                    requests.append(receipt)
                    time.sleep(0.4)
                    try:
                        with urlopen(Request(url, headers={'User-Agent': 'DeathMap-AI/0.1 supplemental-metadata'}), timeout=30) as response:
                            body = response.read(10_000_001)
                            receipt.update(http_status=response.status, final_url=response.url, bytes=len(body))
                        break
                    except (HTTPError, URLError, TimeoutError) as exc:
                        receipt['error'] = str(exc)
                        transient = not isinstance(exc, HTTPError) or exc.code in (429, 500, 502, 503, 504)
                        if attempt or not transient:
                            raise
                        delay = exc.headers.get('Retry-After', '2') if isinstance(exc, HTTPError) else '2'
                        # Long server backoffs are reported, not ignored or retried early.
                        if not delay.isdigit() or int(delay) > 60:
                            raise
                        time.sleep(max(2, int(delay)))
            if len(body) > 10_000_000:
                raise ValueError('XML exceeds 10 MB limit')
            target = output / (pmc + '.xml')
            target.write_bytes(body)
            record.update(xml_file=target.name, sha256=hashlib.sha256(body).hexdigest())
            record.update(parse_xml(body, p))
            record['status'] = 'verified_xml' if record['has_body'] else 'verified_metadata_only'
        except Exception as exc:
            record.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        results.append(record)
        # Checkpoints survive interruption without overwriting any reviewer files.
        (output / 'results.json').write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
        (output / 'requests.json').write_text(json.dumps(requests, indent=2), encoding='utf-8')
    counts = {status: sum(r['status'] == status for r in results) for status in sorted({r['status'] for r in results})}
    summary = dict(publications=len(results), statuses=counts,
                   publications_with_entries=sum(bool(r.get('entry_count')) for r in results),
                   supplementary_entries=sum(r.get('entry_count', 0) for r in results),
                   input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   completed_utc=datetime.now(timezone.utc).isoformat(),
                   note='No listed entries does not establish absence of supplements. Relative hrefs are native references, not verified download URLs.')
    for name, value in [('results', results), ('requests', requests), ('summary', summary)]:
        (output / f'{name}.json').write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')
    with (output / 'supplementary-inventory.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=['PMCID', 'PMID', 'label', 'caption', 'description', 'files', 'xml_locator'])
        writer.writeheader()
        for r in results:
            for entry in r.get('supplementary_entries', []):
                writer.writerow(dict(PMCID=r['PMCID'], PMID=r.get('PMID'), **{**entry, 'files': json.dumps(entry['files'], ensure_ascii=False)}))
    return summary


def main():
    """CLI entry point; nonzero exit means at least one retrieval/parse failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--xml-cache', type=Path)
    args = parser.parse_args()
    summary = run(args.input, args.output_dir, args.xml_cache)
    print(json.dumps(summary, indent=2))
    return 1 if summary['statuses'].get('failed') else 0


if __name__ == '__main__':
    raise SystemExit(main())
