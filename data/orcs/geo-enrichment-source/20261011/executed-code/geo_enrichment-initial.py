"""Identify GEO Series from publication metadata, with inspectable route evidence.

Imported adapter and command-line entry point. Inputs are ORCS publication
records; outputs are accession candidates, native responses and request receipts.
Only Series identity, citations and explicit hierarchy are projected at this
stage. Accession association does not establish ownership or CRISPR screen role.
"""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

API = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
STRATEGY = 'geo-accession-identification-v1'
GSE = re.compile(r'GSE\d+')


def _save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


class _Requests:
    """Preserve native bytes before parsing; enforce serial request/time budgets."""

    def __init__(self, folder):
        self.folder = folder
        folder.mkdir()
        self.receipts = []
        self.started = time.monotonic()
        self.attempts = 0

    def get(self, url):
        for attempt in (1, 2):
            if self.attempts >= 100 or time.monotonic() - self.started > 600:
                raise RuntimeError('100-request/10-minute checkpoint reached')
            self.attempts += 1
            receipt = {'url': url, 'attempt': attempt,
                       'retrieved_utc': datetime.now(timezone.utc).isoformat()}
            try:
                with urlopen(Request(url, headers={'User-Agent': 'DeathMap-AI/0.1 GEO metadata'}), timeout=30) as response:
                    body = response.read()
                    receipt['http_status'] = response.status
                filename = f'{self.attempts:03d}.response'
                (self.folder / filename).write_bytes(body)
                receipt.update(file='raw/' + filename, sha256=hashlib.sha256(body).hexdigest())
                self.receipts.append(receipt)
                _save(self.folder.parent / 'requests.json', self.receipts)
                time.sleep(0.4)
                return body, receipt['file']
            except Exception as error:
                receipt['error'] = str(error)
                self.receipts.append(receipt)
                _save(self.folder.parent / 'requests.json', self.receipts)
                if attempt == 2:
                    raise
                time.sleep(2)


def _xml(body):
    root = ET.fromstring(body)
    error = root.find('.//ERROR')
    if error is not None:
        raise ValueError('Entrez error: ' + ''.join(error.itertext()))
    return root


def _json(body):
    native = json.loads(body)
    if isinstance(native, dict) and native.get('error'):
        raise ValueError('API error: ' + str(native['error']))
    return native


def _link_targets(native, source, linkname):
    """Require the requested source identity; zero links is a successful empty result."""
    linksets = native.get('linksets', [])
    if len(linksets) != 1 or [str(x) for x in linksets[0].get('ids', [])] != [source]:
        raise ValueError('ELink source identity mismatch')
    targets = set()
    for group in linksets[0].get('linksetdbs', []):
        if group.get('linkname') != linkname:
            raise ValueError('Unexpected ELink relationship')
        targets.update(str(x) for x in group.get('links', []))
    if not all(x.isdigit() for x in targets):
        raise ValueError('Invalid Entrez target UID')
    return sorted(targets, key=int)


def _summary_series(body, requested):
    """Keep only native GSE accessions; never derive an accession from a UID."""
    root = _xml(body)
    rows = {}
    for doc in root.findall('DocSum'):
        uid = doc.findtext('Id')
        if uid in rows:
            raise ValueError('Duplicate summary UID')
        fields = {item.get('Name'): item.text for item in doc.findall('Item')}
        rows[uid] = fields.get('Accession')
    if set(rows) != set(requested):
        raise ValueError('GEO summary UID coverage mismatch')
    return {uid: accession for uid, accession in rows.items()
            if accession and GSE.fullmatch(accession)}


def _series(body, accession):
    """Follow explicit hierarchy assertions only, excluding arbitrary textual mentions."""
    fields = {}
    for line in body.decode('utf-8').splitlines():
        if line.startswith('!Series_') and ' = ' in line:
            key, value = line.split(' = ', 1)
            fields.setdefault(key, []).append(value)
    if fields.get('!Series_geo_accession') != [accession]:
        raise ValueError('Native Series identity mismatch')
    links = []
    for relation in fields.get('!Series_relation', []):
        match = re.fullmatch(r'(SuperSeries of|SubSeries of): (GSE\d+)', relation)
        if match:
            links.append({'from_gse': accession, 'to_gse': match[2],
                          'relation': match[1], 'native_value': relation})
    return {'gse': accession, 'native_pmids': fields.get('!Series_pubmed_id', []),
            'hierarchy': links}


def _annotations(native, pmid):
    """Retain structured accession annotations without fetching their source text."""
    if not isinstance(native, list):
        raise ValueError('Unexpected Europe PMC annotation schema')
    rows = []
    for article in native:
        if article.get('source') != 'MED' or str(article.get('extId')) != pmid:
            raise ValueError('Annotation publication identity mismatch')
        for index, annotation in enumerate(article.get('annotations', [])):
            if annotation.get('type') != 'Accession Numbers':
                raise ValueError('Unexpected annotation type')
            accession = annotation.get('exact', '')
            if GSE.fullmatch(accession):
                rows.append({'gse': accession, 'locator': f'annotations[{index}]',
                             'native_annotation': annotation})
    return rows


def _datalinks(native, pmid):
    """Reject incomplete data-link pages instead of interpreting them as complete hits."""
    if native.get('request', {}).get('id') != pmid or native['request'].get('source') != 'MED':
        raise ValueError('Data-link publication identity mismatch')
    rows, total = [], 0
    for c, category in enumerate(native.get('dataLinkList', {}).get('Category', [])):
        category_count = 0
        for s, section in enumerate(category.get('Section', [])):
            links = section.get('Linklist', {}).get('Link', [])
            if len(links) != section['SectionLinkCount']:
                raise ValueError('Incomplete data-link section')
            category_count += len(links)
            for i, link in enumerate(links):
                accession = link.get('Target', {}).get('Identifier', {}).get('ID', '')
                if GSE.fullmatch(accession):
                    if link.get('Source', {}).get('Identifier', {}).get('ID') != pmid:
                        raise ValueError('Data-link source identity mismatch')
                    rows.append({'gse': accession,
                                 'locator': f'Category[{c}]/Section[{s}]/Link[{i}]',
                                 'native_link': link})
        if category_count != category['CategoryLinkCount']:
            raise ValueError('Incomplete data-link category')
        total += category_count
    if total != native['hitCount']:
        raise ValueError('Incomplete data-link response; pagination requires a separate checkpoint')
    return rows


def identify_geo(publication: dict, output_dir: Path | str) -> dict:
    """Identify GSE candidates for one publication under the accepted six-route contract.

    Parameters
    ----------
    publication : dict
        ORCS record with TITLE and optional PMID, PMCID, DOI and PUBLICATION_ID.
        Missing PMID disables identifier routes but retains title discovery.
    output_dir : Path or str
        New run directory; existing directories are refused.

    Returns
    -------
    dict
        Deduplicated candidates, route counts and unweighted evidence records.

    Raises
    ------
    ValueError
        Missing title, invalid PMID, incomplete responses or identity mismatch.
    RuntimeError
        Request/time, summary or Series limits require an owner checkpoint.
    FileExistsError
        Output directory exists; prior runs are never overwritten.

    Notes
    -----
    Writes native responses, hashes, JSON and a compact accession report. Network
    requests are serial: two attempts, 30-second timeout, 0.4-second pacing,
    100 attempts/10 minutes, 1000 target UIDs and 100 Series per publication.
    A failed route stops the run with partial evidence and a failure manifest.
    No article bodies, experimental files, SRA or broad title-word searches.
    """
    title = publication.get('TITLE', '').strip()
    pmid = str(publication.get('PMID') or '').strip()
    if not title or (pmid and not pmid.isdigit()):
        raise ValueError('A title and a valid optional PMID are required')
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=False)
    transport = _Requests(folder / 'raw')
    evidence, routes, records = [], {}, {}
    manifest = {'strategy': STRATEGY, 'package_version': '0.1.0',
                'started_utc': datetime.now(timezone.utc).isoformat(),
                'publication': publication, 'status': 'running',
                'source_code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'limits': {'request_attempts': 100, 'seconds': 600, 'series': 100,
                           'target_uids_per_route': 1000, 'attempts_per_request': 2,
                           'timeout_seconds': 30, 'pacing_seconds': 0.4}}
    _save(folder / 'manifest.json', manifest)

    def get_entrez(endpoint, params):
        return transport.get(API + endpoint + '?' + urlencode(params, doseq=True))

    def emit(route, gse, source_file, locator, **native):
        evidence.append({'pmid': pmid or None, 'publication_id': publication.get('PUBLICATION_ID'),
                         'gse': gse, 'route': route, 'source_file': source_file,
                         'locator': locator, 'data_role': 'not_assessed', **native})

    def resolve(uids, route, link_file, **native):
        if len(uids) > 1000:
            raise RuntimeError('GEO target UID limit exceeded; native link response preserved')
        for offset in range(0, len(uids), 100):
            batch = uids[offset:offset + 100]
            body, source = get_entrez('esummary.fcgi', {'db': 'gds', 'id': ','.join(batch), 'retmode': 'xml'})
            for uid, accession in _summary_series(body, batch).items():
                emit(route, accession, link_file, f'target_uid={uid}',
                     summary_source=source, native_uid=uid, **native)

    def links(dbfrom, db, source, linkname):
        body, file = get_entrez('elink.fcgi', {'dbfrom': dbfrom, 'db': db, 'id': source,
                                            'linkname': linkname, 'cmd': 'neighbor', 'retmode': 'json'})
        return _link_targets(_json(body), source, linkname), file

    try:
        if pmid:
            uids, source = links('pubmed', 'gds', pmid, 'pubmed_gds')
            resolve(uids, 'pubmed_geo_links', source, evidence_kind='direct_repository_link')
            routes['pubmed_geo_links'] = {'status': 'complete', 'native_target_count': len(uids)}
            body, source = get_entrez('efetch.fcgi', {'db': 'pubmed', 'id': pmid, 'retmode': 'xml'})
            articles = _xml(body).findall('PubmedArticle')
            if len(articles) != 1 or articles[0].findtext('MedlineCitation/PMID') != pmid:
                raise ValueError('PubMed record identity mismatch')
            for bank in articles[0].findall('MedlineCitation/Article/DataBankList/DataBank'):
                if bank.findtext('DataBankName') == 'GEO':
                    for accession in bank.findall('AccessionNumberList/AccessionNumber'):
                        if GSE.fullmatch(accession.text or ''):
                            emit('pubmed_accession_list', accession.text, source,
                                 'MedlineCitation/Article/DataBankList/GEO/AccessionNumberList',
                                 evidence_kind='reported_accession')
            routes['pubmed_accession_list'] = {'status': 'complete'}
        else:
            for route in ('pubmed_geo_links', 'pubmed_accession_list'):
                routes[route] = {'status': 'skipped_missing_pmid'}

        # Complete publication phrase, not the repository title or broad word overlap.
        phrase = title.replace('"', ' ').strip().rstrip('.')
        query = f'"{phrase}"[All Fields] AND gse[Entry Type]'
        body, source = get_entrez('esearch.fcgi', {'db': 'gds', 'term': query, 'retmode': 'json', 'retmax': 1000})
        search = _json(body)['esearchresult']
        uids = search['idlist']
        if search.get('errorlist') or len(uids) != int(search['count']) or len(set(uids)) != len(uids):
            raise ValueError('Incomplete or invalid title search')
        resolve(uids, 'publication_title_phrase', source, evidence_kind='title_candidate', query=query)
        routes['publication_title_phrase'] = {'status': 'complete', 'query': query,
                                              'count': int(search['count']),
                                              'query_translation': search.get('querytranslation'),
                                              'warnings': search.get('warninglist')}

        if pmid:
            url = 'https://www.ebi.ac.uk/europepmc/annotations_api/annotationsByArticleIds?' + urlencode(
                {'articleIds': 'MED:' + pmid, 'type': 'Accession Numbers', 'format': 'JSON'})
            body, source = transport.get(url)
            for row in _annotations(_json(body), pmid):
                emit('europepmc_annotations', row.pop('gse'), source, row.pop('locator'),
                     evidence_kind='precomputed_accession_annotation', **row)
            routes['europepmc_annotations'] = {'status': 'complete'}
            url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/MED/{pmid}/datalinks?format=json&pageSize=1000'
            body, source = transport.get(url)
            native = _json(body)
            for row in _datalinks(native, pmid):
                emit('europepmc_datalinks', row.pop('gse'), source, row.pop('locator'),
                     evidence_kind='service_reported_literature_data_link', **row)
            routes['europepmc_datalinks'] = {'status': 'complete', 'service_version': native.get('version')}
            projects, project_source = links('pubmed', 'bioproject', pmid, 'pubmed_bioproject')
            if len(projects) > 100:
                raise RuntimeError('BioProject count checkpoint exceeded')
            for project in projects:
                uids, source = links('bioproject', 'gds', project, 'bioproject_gds')
                resolve(uids, 'pubmed_bioproject_geo', source, evidence_kind='indirect_repository_path',
                        bioproject_uid=project, publication_project_source=project_source)
            routes['pubmed_bioproject_geo'] = {'status': 'complete', 'bioproject_uids': projects}
        else:
            for route in ('europepmc_annotations', 'europepmc_datalinks', 'pubmed_bioproject_geo'):
                routes[route] = {'status': 'skipped_missing_pmid'}

        seeds = {row['gse'] for row in evidence}
        queue = deque(sorted(seeds))
        queued = set(seeds)
        while queue:
            if len(queued) > 100:
                raise RuntimeError('100-Series hierarchy checkpoint reached')
            accession = queue.popleft()
            url = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?' + urlencode(
                {'acc': accession, 'targ': 'self', 'form': 'text', 'view': 'brief'})
            body, source = transport.get(url)
            record = _series(body, accession)
            record['source_file'] = source
            records[accession] = record
            for relation in record['hierarchy']:
                emit('series_hierarchy', relation['to_gse'], source, '!Series_relation',
                     evidence_kind='inferred_publication_association', **relation)
                if relation['to_gse'] not in queued:
                    queued.add(relation['to_gse'])
                    queue.append(relation['to_gse'])
        routes['series_hierarchy'] = {'status': 'complete'}
        candidates = []
        for accession in sorted(records):
            candidate_routes = sorted({row['route'] for row in evidence if row['gse'] == accession})
            native_pmids = records[accession]['native_pmids']
            citation = ('matches_origin' if pmid and pmid in native_pmids else
                        'different_publication' if native_pmids else 'not_reported')
            candidates.append({'gse': accession, 'pmid': pmid or None, 'routes': candidate_routes,
                               'hierarchy_only': accession not in seeds, 'native_pmids': native_pmids,
                               'citation_comparison': citation, 'data_role': 'not_assessed'})
        for route in routes:
            routes[route]['distinct_gse_count'] = len({row['gse'] for row in evidence if row['route'] == route})
        result = {'publication': publication, 'candidates': candidates, 'routes': routes,
                  'seed_count': len(seeds), 'total_gse_count': len(records),
                  'hierarchy_added': sorted(set(records) - seeds), 'evidence': evidence}
        _save(folder / 'accessions.json', result)
        _save(folder / 'series-identities.json', records)
        lines = [f'# GEO accessions — PMID {pmid or "unavailable"}', '', title, '',
                 f'{len(seeds)} seed accessions; {len(records)} after explicit hierarchy expansion.', '',
                 '| GSE | Hierarchy only | Native PMID(s) | Citation comparison |',
                 '|---|---|---|---|']
        lines.extend(f"| {c['gse']} | {c['hierarchy_only']} | {', '.join(c['native_pmids']) or '(none)'} | {c['citation_comparison']} |" for c in candidates)
        lines.extend(['', 'Publication association and accession mentions do not establish dataset ownership or screen role.'])
        lines.extend(['', '| Route | Status | Distinct GSEs |', '|---|---|---|'])
        lines.extend(f"| {route} | {state['status']} | {state['distinct_gse_count']} |" for route, state in routes.items())
        (folder / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        manifest.update(status='complete', total_gse_count=len(records))
        return result
    except Exception as error:
        manifest.update(status='failed', error=str(error))
        _save(folder / 'partial-evidence.json', {'routes': routes, 'evidence': evidence, 'series': records})
        raise
    finally:
        manifest.update(finished_utc=datetime.now(timezone.utc).isoformat(), request_attempts=transport.attempts)
        _save(folder / 'manifest.json', manifest)


def main() -> None:
    """Run accession identification for one selected ORCS publication.

    Returns
    -------
    None
        Writes a fresh run directory and prints compact accession counts.

    Raises
    ------
    ValueError
        The PMID does not select exactly one input publication.
    """
    parser = argparse.ArgumentParser(description='Metadata-only GEO accession identification')
    parser.add_argument('--publication-index', type=Path, required=True)
    parser.add_argument('--pmid', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    selected = [p for p in json.loads(args.publication_index.read_text(encoding='utf-8'))
                if str(p.get('PMID')) == args.pmid]
    if len(selected) != 1:
        raise ValueError('PMID must select exactly one ORCS publication')
    publication = dict(selected[0])
    publication['_input_provenance'] = {
        'file': str(args.publication_index.resolve()),
        'sha256': hashlib.sha256(args.publication_index.read_bytes()).hexdigest(),
        'locator': 'PUBLICATION_ID=' + str(publication.get('PUBLICATION_ID'))}
    result = identify_geo(publication, args.output_dir)
    print(json.dumps({'output_dir': str(args.output_dir), 'seed_count': result['seed_count'],
                      'total_gse_count': result['total_gse_count'], 'hierarchy_added': result['hierarchy_added'],
                      'routes': result['routes']}, indent=2))


if __name__ == '__main__':
    main()
