"""Bounded full-title Mendeley discovery and owner-template metadata export.

Title matches nominate publication associations for review. Native metadata and
receipts retain the evidence independently of the workbook's selected columns.
No reference expansion or experimental content retrieval is performed.
"""
import argparse
from datetime import datetime, timezone
import json
import platform
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlencode

from .mendeley_data_enrichment import (
    ACCESSION, Credentials, Transport, _save, _sha, _doi,
    select_publications,
)
from .enrichment_indices import DEFAULT_REGISTRY, assign_indices, native_key
from .enrichment_export import export_registered

GATEWAY = 'https://api.data.mendeley.com'
TEMPLATE = Path(__file__).resolve().parents[2] / 'data/templates/Mendeley-Data-Enrichment-Template.xlsx'


def normalized_title(value):
    """Keep every title word in order while ignoring case and punctuation."""
    return ' '.join(re.sub(r'[^\w]+|_', ' ',
        unicodedata.normalize('NFC', value).casefold()).split())


def title_matches(article, dataset):
    """Require the complete normalized title, permitting deposit prefixes/suffixes."""
    title = normalized_title(article)
    return bool(title) and (' ' + title + ' ') in (' ' + normalized_title(dataset) + ' ')


def folder_context(file, folders):
    """Resolve full folder paths and labeled ancestor descriptions without guessing.

    Missing parents and cycles fail visibly rather than fabricating a path.
    """
    mapping = {f['id']: f for f in folders}
    chain, seen = [], set()
    parent = file.get('folder_id')
    while parent:
        if parent in seen or parent not in mapping:
            raise ValueError('Unresolved or cyclic file folder hierarchy')
        seen.add(parent)
        folder = mapping[parent]
        chain.insert(0, folder)
        parent = folder.get('parent_id')
    descriptions = '\n'.join(f"{f['name']}: {f['description']}" for f in chain if f.get('description'))
    return '/'.join(f['name'] for f in chain) or None, descriptions or None


def retrieve_dataset(accession, transport):
    """Retrieve a version-pinned inventory, individual file metadata and folders.

    Each successful response is retained by Transport. Paginated file listings
    are checked against the native inventory before being marked complete.
    """
    metadata, source = transport.get(GATEWAY + '/datasets/' + accession)
    if not isinstance(metadata, dict) or metadata.get('id') != accession:
        raise ValueError('Dataset identity mismatch')
    version = metadata.get('version')
    if type(version) is not int or version < 1:
        raise ValueError('Invalid dataset version')
    if _doi(metadata.get('doi')) != f'10.17632/{accession}.{version}':
        raise ValueError('Dataset DOI/version mismatch')
    base = GATEWAY + '/datasets/publics/' + accession
    folders, folder_source = transport.get(base + '/folders?' + urlencode({'version': version}))
    if not isinstance(folders, list):
        raise ValueError('Invalid folder response')
    files, file_sources, seen = [], [], set()
    for start in range(0, 10000, 500):
        page, receipt = transport.get(base + '/files?' + urlencode({
            'version': version, '$limit': 500, '$start': start}))
        file_sources.append(receipt)
        if not isinstance(page, list):
            raise ValueError('Invalid file-list response')
        for file in page:
            identity = file.get('id')
            if not isinstance(identity, str) or not re.fullmatch(r'[a-zA-Z0-9-]+', identity) or identity in seen:
                raise ValueError('Invalid or repeated file identity')
            seen.add(identity)
            detail, receipt = transport.get(base + '/files/' + identity + '?' + urlencode({'version': version}))
            if not isinstance(detail, dict) or detail.get('id') != identity or not detail.get('filename'):
                raise ValueError('Individual file identity mismatch')
            files.append({'metadata': {**file, **detail}, 'source': receipt})
        if len(page) < 500:
            break
    else:
        raise ValueError('File inventory exceeds 10000-file limit')
    native = metadata.get('files')
    if not isinstance(native, list) or {f['id'] for f in native} != seen:
        raise ValueError('Listed files differ from dataset inventory')
    return dict(metadata=metadata, source=source, folders=folders,
                folder_source=folder_source, files=files, file_sources=file_sources)


def collect(publication, transport, datasets):
    """Record one search page and enrich only complete normalized title matches."""
    result = dict(publication=publication, matches=[], issues=[])
    title = str(publication.get('Title') or '').strip().rstrip('.')
    if not title or len(title) > 255:
        result['issues'].append('Missing title or title exceeds 255 characters; not truncated')
        return result
    url = GATEWAY + '/search?' + urlencode(dict(query=title, page=1, page_size=10,
                                               data_type='DATASET', include_external='false'))
    try:
        response, receipt = transport.get(url)
        if not isinstance(response, dict) or not isinstance(response.get('records'), list) or len(response['records']) > 10:
            raise ValueError('Invalid first-page search response')
        result.update(search=response, source=receipt)
        for rank, hit in enumerate(response['records'], 1):
            if not isinstance(hit, dict) or not isinstance(hit.get('title'), str):
                raise ValueError('Invalid search record')
            if not title_matches(title, hit['title']):
                continue
            accession = hit.get('id')
            if not isinstance(accession, str) or not ACCESSION.fullmatch(accession):
                raise ValueError('Invalid matching dataset accession')
            match = dict(accession=accession, rank=rank, title=hit['title'],
                         relationship='title-match candidate; screen attribution unassessed')
            result['matches'].append(match)
            if accession not in datasets:
                try:
                    datasets[accession] = retrieve_dataset(accession, transport)
                except ValueError as error:
                    result['issues'].append(f'{accession}: {error}')
    except ValueError as error:
        result['issues'].append(str(error))
    return result


def project(database, registry=None):
    """Populate accepted columns while preserving candidate relationships in JSON.

    Dataset/file indices are version-specific and shared across publications.
    Each publication association receives its own workbook rows.
    """
    datasets = database['datasets']
    ds = assign_indices('MDD', {native_key(a, str(d['metadata']['version'])) for a, d in datasets.items()}, registry)
    fi = assign_indices('MDF', {native_key(a, str(d['metadata']['version']), f['metadata']['id'])
                              for a, d in datasets.items() for f in d['files']}, registry)
    tables = dict(Publications=[], Datasets=[], Files=[])
    for record in database['publications']:
        p = record['publication']
        tables['Publications'].append({**p, 'Search Pages': 1 if 'search' in record else 0,
            'Page Size Returned': len(record['search']['records']) if 'search' in record else None,
            'Title Matches': len(record['matches']) if 'search' in record else None,
            'Reported Total': record.get('search', {}).get('total_records')})
        # Duplicate search appearances retain their ranks in JSON, but export one association.
        seen = set()
        for match in record['matches']:
            a = match['accession']
            if a not in datasets or a in seen:
                continue
            seen.add(a)
            d = datasets[a]
            m = d['metadata']
            index = ds[native_key(a, str(m['version']))]
            common = {'Publication Index': p['Publication Index'], 'MD Dataset Index': index}
            tables['Datasets'].append({**common, 'MD Dataset Accession': a,
                'Dataset DOI ID': _doi(m.get('doi')), 'Dataset Title': m.get('name'),
                'Dataset Description': m.get('description'), 'File Count': len(d['files']),
                'Search Rank': match['rank'], 'Dataset URL': f"https://data.mendeley.com/datasets/{a}/{m['version']}"})
            for file in d['files']:
                f = file['metadata']
                folder, description = folder_context(f, d['folders'])
                tables['Files'].append({**common,
                    'MD File Index': fi[native_key(a, str(m['version']), f['id'])],
                    'MD File Accession': f['id'], 'Folder': folder, 'Folder Description': description,
                    'File': f['filename'], 'File Type': Path(f['filename']).suffix.lower() or None,
                    'Size (bytes)': f.get('size', f.get('content_details', {}).get('size')),
                    'File Description': f.get('description')})
    return tables


def run(source, output, *, registry=None, index_registry=DEFAULT_REGISTRY,
        template=TEMPLATE, caches=(), credentials=None, offline=False):
    """Create a new run with raw receipts, candidate JSON and a template workbook.

    Parameters are explicit source/output paths, optional publication/index
    registries, template, verified caches, in-memory credential provider and
    offline switch. Existing output directories are refused. Interrupted runs
    can be recovered into a new directory using their native response cache.
    """
    publications = select_publications(source, registry)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    transport = Transport(output, caches, credentials, offline)
    database = dict(schema_version='mendeley-title-enrichment/1',
        tool_version='DeathMap-AI 0.1.0; Python ' + platform.python_version(),
        input_sha256=_sha(Path(source).read_bytes()), collector_sha256=_sha(Path(__file__).read_bytes()),
        retrieved_utc=datetime.now(timezone.utc).isoformat(),
        strategy='full title, unquoted query, page 1, 10 records; complete normalized title match',
        datasets={}, publications=[])
    for publication in publications:
        database['publications'].append(collect(publication, transport, database['datasets']))
        _save(output / 'database.json', database)
        _save(output / 'requests.json', transport.requests)
    database['status'] = 'incomplete' if any(p['issues'] for p in database['publications']) else 'complete'
    try:
        database['rows'] = project(database, index_registry)
        _save(output / 'database.json', database)
        database['export'] = export_registered(template, output / 'Mendeley-Data-Enrichment.xlsx', database['rows'], overflow_sidecar=True)
    except (ValueError, OSError) as error:
        database['status'] = 'incomplete'
        database['export_error'] = type(error).__name__
        raise
    finally:
        _save(output / 'database.json', database)
    return database


def main():
    """Run the owner-approved metadata enrichment workflow from explicit inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('input', 'output-dir'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--registry', type=Path)
    parser.add_argument('--index-registry', type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument('--template', type=Path, default=TEMPLATE)
    parser.add_argument('--cache-root', type=Path, action='append', default=[])
    parser.add_argument('--offline', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--access-token-file', type=Path)
    group.add_argument('--client-credentials-file', type=Path)
    group.add_argument('--client-id-file', type=Path)
    parser.add_argument('--client-secret-file', type=Path)
    args = parser.parse_args()
    if bool(args.client_id_file) != bool(args.client_secret_file):
        parser.error('Supply both client ID and client secret files')
    client = (args.client_id_file, args.client_secret_file) if args.client_id_file else args.client_credentials_file
    result = run(args.input, args.output_dir, registry=args.registry, index_registry=args.index_registry,
        template=args.template, caches=args.cache_root, offline=args.offline,
        credentials=Credentials(args.access_token_file, client))
    print(result['status'])
    return 0 if result['status'] == 'complete' else 1


if __name__ == '__main__':
    raise SystemExit(main())
