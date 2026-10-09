"""PMID-led metadata enrichment, shared by the ORCS catalog and saved searches.

Only publication metadata and direct GEO/BioProject/SRA links are retrieved.
Repository association never establishes which ORCS screen a dataset contains.
Native responses and request receipts are retained so empty links are distinct
from retrieval failures and future repository-specific stages can review them.
"""
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import hashlib
import json
import time
import xml.etree.ElementTree as ET

RESOURCES = ('gds', 'bioproject', 'sra')
API = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'


def save_json(path, value):
    """Write readable Unicode metadata separately from native response bytes.

    Parameters
    ----------
    path : Path or str
        Destination metadata path, with an existing parent directory.
    value : object
        JSON-serializable metadata; identifiers remain strings.

    Returns
    -------
    None
        Writes the destination file.
    """
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


class Retrieval:
    """Bounded serial requests with durable receipts and byte-checked resumption.

    Parameters
    ----------
    folder : Path or str
        Native response cache, created if absent. Existing receipts are loaded
        and checked against saved bytes before reuse.

    Notes
    -----
    At most two attempts/request, 30-second timeout, 0.4-second pacing, 250 requests,
and 15 minutes total per invocation. Reusing a receipt requires the same URL and
saved-byte hash. An error stops the stage; it is never treated as an empty result.
"""
    def __init__(self, folder):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.receipts = []
        path = self.folder / 'requests.json'
        if path.exists():
            self.receipts = json.loads(path.read_text(encoding='utf-8'))
        self.started = time.monotonic()
        self.attempts = 0

    def request(self, endpoint, params, filename):
        """Retrieve or reuse one response with a durable URL/date/hash receipt.

        Parameters
        ----------
        endpoint : str
            NCBI E-utilities endpoint filename.
        params : dict
            Literal request parameters; repeated IDs preserve PMID provenance.
        filename : str
            Cache member name within the configured folder.

        Returns
        -------
        bytes
            Verified cached bytes or a newly saved native response.

        Raises
        ------
        RuntimeError
            API error or an invocation resource checkpoint is reached.
        AssertionError
            Cached URL/hash no longer agrees with its receipt.
        URLError
            Network retrieval fails after the bounded attempts.
        """
        url = API + endpoint + '?' + urlencode(params, doseq=True)
        path = self.folder / filename
        for receipt in self.receipts:
            if receipt['file'] == filename:
                assert receipt['url'] == url
                assert hashlib.sha256(path.read_bytes()).hexdigest() == receipt['sha256']
                return path.read_bytes()
        for attempt in (1, 2):
            if self.attempts >= 250 or time.monotonic() - self.started > 900:
                raise RuntimeError('Request/time checkpoint reached; saved responses remain resumable')
            self.attempts += 1
            try:
                with urlopen(Request(url, headers={'User-Agent': 'DeathMap-AI/0.1 PubMed metadata enrichment'}), timeout=30) as response:
                    body = response.read()
                    status = response.status
                # Parse before accepting a response; API errors may use HTTP 200.
                if params.get('retmode') == 'json':
                    document = json.loads(body)
                    if document.get('error'):
                        raise RuntimeError(document['error'])
                else:
                    document = ET.fromstring(body)
                    error = document.find('.//ERROR')
                    if error is not None:
                        raise RuntimeError(''.join(error.itertext()))
                path.write_bytes(body)
                self.receipts.append({'file': filename, 'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                                      'http_status': status, 'attempt': attempt, 'sha256': hashlib.sha256(body).hexdigest()})
                save_json(self.folder / 'requests.json', self.receipts)
                time.sleep(0.4)
                return body
            except Exception as error:
                save_json(self.folder / 'last-failure.json', {'file': filename, 'url': url, 'attempt': attempt, 'error': str(error)})
                if attempt == 2:
                    raise
                time.sleep(2)

    def retrieve(self, pmids):
        """Retrieve PMID metadata and direct linked summaries in bounded batches.

        Parameters
        ----------
        pmids : list of str
            Distinct verified PMIDs; no title-based or preprint matching.

        Returns
        -------
        dict
            Distinct linked native-ID counts per GEO/BioProject/SRA resource.

        Raises
        ------
        RuntimeError
            A resource exceeds 10,000 summaries or request/time limits.

        Notes
        -----
        Writes native batches, merged parsing inputs and receipts. Empty links
        remain distinct from failed requests; no experimental files are fetched.
        """
        articles = ET.Element('PubmedArticleSet')
        for offset in range(0, len(pmids), 100):
            body = self.request('efetch.fcgi', {'db': 'pubmed', 'id': ','.join(pmids[offset:offset+100]), 'retmode': 'xml'}, f'pubmed-{offset//100}.xml')
            articles.extend(ET.fromstring(body))
        (self.folder / 'pubmed.xml').write_bytes(ET.tostring(articles, encoding='utf-8', xml_declaration=True))
        link_counts = {}
        for resource in RESOURCES:
            combined = {'linksets': []}
            for offset in range(0, len(pmids), 50):
                body = self.request('elink.fcgi', {'dbfrom': 'pubmed', 'db': resource, 'linkname': 'pubmed_' + resource,
                                                  'id': pmids[offset:offset+50], 'cmd': 'neighbor', 'retmode': 'json'}, f'links-{resource}-{offset//50}.json')
                combined['linksets'].extend(json.loads(body)['linksets'])
            save_json(self.folder / f'links-{resource}.json', combined)
            ids = sorted({str(uid) for linkset in combined['linksets'] for group in linkset.get('linksetdbs', []) for uid in group.get('links', [])}, key=int)
            link_counts[resource] = len(ids)
            save_json(self.folder / 'link-counts.json', link_counts)
            # A large per-sample expansion needs a separate resource decision.
            # No IDs are discarded: the complete link responses remain saved.
            if len(ids) > 10000:
                raise RuntimeError(f'{resource}: {len(ids)} summaries exceeds the 10000-record checkpoint')
            for offset in range(0, len(ids), 100):
                self.request('esummary.fcgi', {'db': resource, 'id': ','.join(ids[offset:offset+100]), 'retmode': 'xml'}, f'summary-{resource}-{offset//100}.xml')
        save_json(self.folder / 'retrieval-issues.json', [])
        return link_counts
