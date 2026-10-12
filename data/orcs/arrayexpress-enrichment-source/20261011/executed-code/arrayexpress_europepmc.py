"""Europe PMC metadata supplement for a bounded ArrayExpress publication pilot.

Uses saved publication IDs/titles, precomputed annotations and repository data
links. No article contents, references/citation network or supplements are fetched.
Native ArrayExpress citations remain distinct from Europe PMC associations.
"""
from __future__ import annotations

import json
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, quote

from .arrayexpress_enrichment import API, _Transport, _save, _phrase

ACCESSION = re.compile(r'E-[A-Z][A-Z0-9]*-\d+')
REST = 'https://www.ebi.ac.uk/europepmc/webservices/rest/'
ANNOTATIONS = 'https://www.ebi.ac.uk/europepmc/annotations_api/annotationsByArticleIds'


def annotation_candidates(native: list, pmid: str) -> list[dict]:
    """Extract repository-like identifiers without assigning screen ownership.

    Parameters
    ----------
    native : list
        Accession Numbers response from annotationsByArticleIds.
    pmid : str
        Requested MED publication identity.

    Returns
    -------
    list
        Observations retaining the annotation and field locator. Empty is valid.

    Raises
    ------
    ValueError
        Wrong publication identity, type or response schema.
    """
    if not isinstance(native, list):
        raise ValueError('Unexpected annotation schema')
    observations = []
    for article_index, article in enumerate(native):
        if article.get('source') != 'MED' or str(article.get('extId')) != pmid:
            raise ValueError('Annotation publication identity mismatch')
        for index, annotation in enumerate(article.get('annotations', [])):
            if annotation.get('type') != 'Accession Numbers':
                raise ValueError('Unexpected annotation type')
            # An accession shape nominates a candidate, not collection membership.
            # Native AttachTo metadata is checked after identification.
            values = [str(annotation.get('exact', ''))]
            values.extend(str(tag.get('uri', '')) for tag in annotation.get('tags', []))
            for accession in sorted({a for value in values for a in ACCESSION.findall(value)}):
                observations.append({'accession': accession,
                    'locator': f'$[{article_index}].annotations[{index}]',
                    'evidence_kind': 'precomputed_accession_mention', 'native': annotation})
    return observations


def datalink_candidates(native: dict, pmid: str) -> list[dict]:
    """Check complete ArrayExpress data-link sections and retain native assertions.

    Parameters
    ----------
    native : dict
        ArrayExpress-category data-link response.
    pmid : str
        Requested MED publication identity.

    Returns
    -------
    list
        Native accession observations with source locators and evidence kinds.

    Raises
    ------
    ValueError
        Identity mismatch, unexpected category or incomplete counts.
    """
    request = native.get('request', {})
    if str(request.get('id')) != pmid or request.get('source') != 'MED':
        raise ValueError('Data-link publication identity mismatch')
    observations, total = [], 0
    for c, category in enumerate(native.get('dataLinkList', {}).get('Category', [])):
        # Preserve a category name for diagnostics rather than accepting an
        # unrelated repository if the service ignores the requested filter.
        name = category.get('Name', category.get('name'))
        if name and str(name).lower() != 'arrayexpress':
            raise ValueError('Unexpected data-link category: ' + str(name))
        count = 0
        for s, section in enumerate(category.get('Section', [])):
            links = section.get('Linklist', {}).get('Link', [])
            if len(links) != section.get('SectionLinkCount'):
                raise ValueError('Incomplete data-link section')
            count += len(links)
            for i, link in enumerate(links):
                if str(link.get('Source', {}).get('Identifier', {}).get('ID')) != pmid:
                    raise ValueError('Data-link source identity mismatch')
                accession = link.get('Target', {}).get('Identifier', {}).get('ID', '')
                if ACCESSION.fullmatch(accession):
                    observations.append({'accession': accession,
                        'locator': f'$.dataLinkList.Category[{c}].Section[{s}].Linklist.Link[{i}]',
                        'evidence_kind': 'europepmc_repository_association', 'native': link})
        if count != category.get('CategoryLinkCount'):
            raise ValueError('Incomplete category')
        total += count
    if total != native.get('hitCount'):
        raise ValueError('Incomplete data links')
    return observations


def supplement(publications: list[dict], output_dir: Path, *, cached_run: Path | None = None) -> dict:
    """Run one metadata supplement for at most five saved ORCS publications.

    Parameters
    ----------
    publications : list of dict
        Saved ORCS records with PMID/TITLE and input provenance. No answer seeds.
    output_dir : Path
        New exclusive run directory; native bytes and a partial manifest survive.
    cached_run : Path, optional
        Prior partial run; reuse only hash-verified successful native bytes.

    Returns
    -------
    dict
        Routes, title observations, query hits and collection-checked studies.

    Raises
    ------
    Exception
        Invalid inputs, network/schema failure or the ten-study pilot boundary.

    Notes
    -----
    One serial pass within the existing 99-attempt/15-minute/byte limits. No
    experimental or metadata-file download; IDF/SDRF has its separate pilot record.
    """
    if not 1 <= len(publications) <= 5:
        raise ValueError('One to five publications required')
    output_dir.mkdir(parents=True, exist_ok=False)
    transport = _Transport(output_dir)
    previous = json.loads((cached_run / 'requests.json').read_text(encoding='utf-8')) if cached_run else []
    # A continuation spends the remaining original budget, including retries.
    transport.attempt_limit = 99 - len(previous)
    transport.total = sum(receipt.get('bytes', 0) for receipt in previous)
    if previous:
        elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(previous[0]['retrieved_utc'])).total_seconds()
        transport.started -= max(0., elapsed)
    reused = []

    def get(url):
        for receipt in previous:
            if receipt['url'] == url and 'file' in receipt and not receipt.get('incomplete'):
                path = cached_run / receipt['file']
                body = path.read_bytes()
                if hashlib.sha256(body).hexdigest() != receipt['sha256']:
                    raise ValueError('Cached response hash mismatch')
                reused.append({'original_receipt': receipt, 'source': str(path),
                               'reused_utc': datetime.now(timezone.utc).isoformat()})
                return body, str(path)
        if len(previous) + len(transport.receipts) >= 99:
            raise RuntimeError('Combined attempt boundary reached')
        return transport.get(url)
    result = {'strategy': 'arrayexpress-europepmc-metadata-v1', 'status': 'running',
              'publications': publications, 'routes': [], 'observations': [],
              'title_results': [], 'studies': [],
              'source_code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'transport_code_sha256': hashlib.sha256(Path(__file__).with_name('arrayexpress_enrichment.py').read_bytes()).hexdigest()}
    try:
        for publication in publications:
            pmid = str(publication['PMID'])
            if not pmid.isdigit():
                raise ValueError('Valid saved PMID required')
            # Preserve the saved title's punctuation. Escaping query syntax must
            # not shorten the publication phrase or substitute a repository title.
            title_query = 'TITLE:' + _phrase(publication['TITLE'])
            url = REST + 'search?' + urlencode({'query': title_query, 'format': 'json', 'resultType': 'lite', 'pageSize': 20})
            body, source = get(url)
            title_native = json.loads(body)
            if int(title_native.get('hitCount', -1)) > 20 or 'resultList' not in title_native:
                raise ValueError('Title result exceeds twenty-article diagnostic boundary or invalid schema')
            hits = title_native['resultList'].get('result', [])
            if len(hits) != int(title_native['hitCount']):
                raise ValueError('Incomplete title search')
            # Title hits are diagnostic publication candidates. Different article
            # identities are recorded without expanding their accession lookups.
            result['title_results'].append({'origin_pmid': pmid, 'query': title_query,
                'source': source, 'native_results': hits,
                'origin_recovered': any(h.get('source') == 'MED' and str(h.get('id')) == pmid for h in hits)})
            urls = [('annotations', ANNOTATIONS + '?' + urlencode({'articleIds': 'MED:' + pmid,
                       'type': 'Accession Numbers', 'format': 'JSON'}), annotation_candidates),
                    ('datalinks', REST + f'MED/{pmid}/datalinks?' + urlencode({'format': 'json',
                       'category': 'ArrayExpress', 'sectionLimit': 1000}), datalink_candidates)]
            for route, url, parse in urls:
                state = {'pmid': pmid, 'route': route, 'status': 'running', 'url': url}
                result['routes'].append(state)
                body, source = get(url)
                native = json.loads(body)
                observations = parse(native, pmid)
                for observation in observations:
                    observation.update(origin_pmid=pmid, publication_id=publication['PUBLICATION_ID'],
                                       route=route, source=source)
                result['observations'].extend(observations)
                state.update(status='complete' if observations else 'no_results',
                             candidates=sorted({o['accession'] for o in observations}),
                             interface_version=native.get('version') if isinstance(native, dict) else 'Annotations API (not exposed)')
                if len({o['accession'] for o in result['observations']}) > 10:
                    raise RuntimeError('Ten-study supplement boundary reached')
                _save(output_dir / 'result.json', result)
        for accession in sorted({o['accession'] for o in result['observations']}):
            body, source = get(API + 'studies/' + quote(accession, safe=''))
            native = json.loads(body)
            if native.get('accno') != accession:
                raise ValueError('Native study identity mismatch')
            members = [a.get('value') for a in native.get('attributes', []) if a.get('name') == 'AttachTo']
            result['studies'].append({'accession': accession, 'source': source, 'native': native,
                'arrayexpress_membership_confirmed': 'ArrayExpress' in members,
                'association_scope': 'publication_candidate; exact screen attribution unresolved'})
            _save(output_dir / 'result.json', result)
        result['status'] = 'complete'
    except Exception as error:
        result.update(status='incomplete', error=str(error))
        raise
    finally:
        result['attempts'] = len(transport.receipts)
        result['previous_attempts'] = len(previous)
        result['reused_responses'] = reused
        _save(output_dir / 'result.json', result)
    return result
