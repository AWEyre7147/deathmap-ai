"""Reuse batch native records with explicit parent hashes and selection locators.

These are selected response projections, not newly retrieved native responses.
Original bytes are copied once to the run's source directory. Title searches
may be reused only when their full ID list was returned for the identical term.
"""
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import xml.etree.ElementTree as ET

class _SavedNativeCache:
    """Select verified native batch records without requiring prior PubMed enrichment."""

    def __init__(self, base):
        self.base = Path(base)
        self.links, self.articles, self.summaries, self.titles = {}, {}, {}, {}

    def _inventory(self, root):
        """Validate eligible native receipts and index records independently of projections."""
        paths = sorted((root / 'data/orcs/pubmed-enrichment-source').glob('*/requests.json'))
        paths += sorted((root / 'outputs/geo').glob('**/requests.json'))
        for receipts in paths:
            for receipt in json.loads(receipts.read_text()):
                member = receipt.get('file') or receipt.get('raw_file')
                if not member or receipt.get('error') or not receipt.get('sha256') or receipt.get('parents'):
                    continue
                path = receipts.parent / member
                url = urlsplit(receipt['url'])
                params = parse_qs(url.query)
                if ('sra' in params.get('dbfrom', []) or 'sra' in params.get('db', [])):
                    continue
                if not any(url.path.endswith(x) for x in ('elink.fcgi', 'efetch.fcgi', 'esummary.fcgi', 'esearch.fcgi')):
                    continue
                body = path.read_bytes()
                if hashlib.sha256(body).hexdigest() != receipt['sha256']:
                    raise ValueError('Native source hash mismatch: ' + str(path))
                parent = {'path': str(path), **receipt}
                if url.path.endswith('elink.fcgi'):
                    native = json.loads(body)
                    for i, record in enumerate(native.get('linksets', [])):
                        ids = record.get('ids', [])
                        if len(ids) == 1:
                            key = (params['dbfrom'][0], params['linkname'][0], str(ids[0]))
                            self.links[key] = (record, parent, f'linksets[{i}]')
                elif url.path.endswith('efetch.fcgi') and params.get('db') == ['pubmed']:
                    for i, article in enumerate(ET.fromstring(body).findall('PubmedArticle')):
                        self.articles[article.findtext('MedlineCitation/PMID')] = (article, parent, f'PubmedArticle[{i}]')
                elif url.path.endswith('esummary.fcgi') and params.get('db') == ['gds']:
                    for i, item in enumerate(ET.fromstring(body).findall('DocSum')):
                        self.summaries[item.findtext('Id')] = (item, parent, f'DocSum[{i}]')
                elif url.path.endswith('esearch.fcgi') and params.get('db') == ['gds']:
                    result = json.loads(body).get('esearchresult', {})
                    if not result.get('errorlist') and int(result.get('count', -1)) == len(result.get('idlist', [])):
                        self.titles[params['term'][0]] = (body, parent, 'complete esearchresult')


    def _selected_response(self, url):
        """Return a recorded selection only if every requested identity is available."""
        parsed = urlsplit(url)
        params = parse_qs(parsed.query)
        selected, parents = None, []
        if parsed.path.endswith('elink.fcgi'):
            key = (params['dbfrom'][0], params['linkname'][0], params['id'][0])
            if key in self.links:
                record, parent, locator = self.links[key]
                selected = json.dumps({'linksets': [record]}).encode()
                parents = [(parent, locator)]
        elif parsed.path.endswith('efetch.fcgi') and params.get('db') == ['pubmed']:
            if params['id'][0] in self.articles:
                record, parent, locator = self.articles[params['id'][0]]
                result = ET.Element('PubmedArticleSet')
                result.append(record)
                selected = ET.tostring(result)
                parents = [(parent, locator)]
        elif parsed.path.endswith('esummary.fcgi') and params.get('db') == ['gds']:
            ids = params['id'][0].split(',')
            if all(uid in self.summaries for uid in ids):
                result = ET.Element('eSummaryResult')
                for uid in ids:
                    record, parent, locator = self.summaries[uid]
                    result.append(record)
                    parents.append((parent, locator))
                selected = ET.tostring(result)
        elif parsed.path.endswith('esearch.fcgi') and params.get('term', [''])[0] in self.titles:
            selected, parent, locator = self.titles[params['term'][0]]
            parents = [(parent, locator)]
        if selected is None:
            return None
        sources = []
        for parent, locator in parents:
            source = Path(parent['path'])
            folder = self.base / 'saved-sources'
            folder.mkdir(exist_ok=True)
            target = folder / (parent['sha256'] + source.suffix)
            if not target.exists():
                target.write_bytes(source.read_bytes())
            sources.append({'file': str(target.relative_to(self.base)), 'sha256': parent['sha256'],
                            'original_file': str(source), 'url': parent['url'], 'locator': locator,
                            'retrieved_utc': parent.get('retrieved_utc') or parent.get('retrieved_at')})
        return selected, sources
