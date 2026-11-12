"""Run independently selectable ORCS enrichment, registry and synthesis stages.

All stages accept explicit inputs and create new outputs. Retrieval stages reuse
hash-verified native caches, never validation reference lists. Synthesis/export
are offline and cannot launch enrichment. The CLI requires no Codex runtime.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .enrichment_export import export_registered
from .json_storage import load_json, compress_stage_output


def _load(path):
    return load_json(path)


def _save(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def legacy_synthesis_template(root):
    """Locate the archived four-source layout for historical projections."""
    folder = Path(root) / 'data/templates'
    archived = folder / 'history/synthesis-four-source/Enrichment-Synthesis-Template.xlsx'
    return archived if archived.exists() else folder / 'Enrichment-Synthesis-Template.xlsx'


def publication_registry(publications, previous=()):
    """Allocate persistent publication indices, including records without PMIDs.

    Parameters
    ----------
    publications : list of dict
        ORCS records carrying unique PUBLICATION_ID and optional PMID.
    previous : list of dict
        An explicitly supplied prior registry. Existing indices never change.

    Returns
    -------
    list of dict
        Current selected publication mappings with stable ORCS native IDs.

    Raises
    ------
    ValueError
        Source identifiers, PMIDs or registry keys are ambiguous.
    """
    by_id = {str(p['ORCS Publication ID']): p for p in previous if p.get('ORCS Publication ID')}
    by_pmid = {str(p['PMID']): p for p in previous if p.get('PMID')}
    keys = [p['Publication index'] for p in previous]
    if len(set(keys)) != len(keys) or len(by_id) != sum(bool(p.get('ORCS Publication ID')) for p in previous) or len(by_pmid) != sum(bool(p.get('PMID')) for p in previous):
        raise ValueError('Ambiguous previous registry')
    ids = [str(p['PUBLICATION_ID']) for p in publications]
    pmids = [str(p['PMID']) for p in publications if p.get('PMID')]
    if len(ids) != len(set(ids)) or len(pmids) != len(set(pmids)):
        raise ValueError('Ambiguous publication identity')
    next_id = max([int(k.split('-')[1]) for k in keys] or [0]) + 1
    result = []
    for p in sorted(publications, key=lambda p: int(p['PUBLICATION_ID'])):
        old = by_id.get(str(p['PUBLICATION_ID'])) or by_pmid.get(str(p.get('PMID')))
        if old and old.get('ORCS Publication ID') and old['ORCS Publication ID'] != str(p['PUBLICATION_ID']):
            raise ValueError('Registry PMID/native publication conflict')
        key = old['Publication index'] if old else f'PUB-{next_id:04d}'
        if not old:
            next_id += 1
        result.append({'Publication index': key, 'ORCS Publication ID': str(p['PUBLICATION_ID']), 'PMID': p.get('PMID')})
    return result


def synthesis_tables(data, root):
    """Map native synthesis rows into the registered owner-facing layout.

    Parameters
    ----------
    data : dict
        Offline synthesis projection.
    root : Path
        Repository containing the original native header registrations.

    Returns
    -------
    dict
        Display sheet names mapped to owner-labeled record dictionaries.
    """
    from .synthesis_layout import layout_sheet
    target_specs = {s['name']: s for s in _load(legacy_synthesis_template(root).with_suffix('.manifest.json'))['sheets']}
    sources = {'PubMed': 'PubMed-Enrichment', 'GEO': 'GEO-Enrichment', 'ENA': 'ENA-Enrichment', 'BioStudies': 'BioStudies-Enrichment'}
    result = {}
    for name, rows in data['tables'].items():
        if name in ('Publications', 'Publication-repository links'):
            headers = list(rows[0]) if rows else (['Publication index', 'Repository', 'Accession'] if name != 'Publications' else [])
        else:
            repository, native = name.split(' - ', 1)
            if repository in ('ENA', 'GEO', 'PubMed'):
                # Synthesis owns its layout independently of later repository template edits.
                spec = {'columns': [
                    {'header': c['header'], 'source_keys': c.get('native_source_keys', [c['native_source_key']])}
                    for target in target_specs.values()
                    if target.get('native_source_table') == name for c in target['columns']]}
            else:
                registration = _load(Path(root) / f'data/templates/{sources[repository]}-Template.manifest.json')
                spec = next(s for s in registration['sheets'] if s['name'] == native)
            # Keep every raw source key until layout consolidation, even when
            # multiple capitalization variants share one displayed column.
            headers = [] if native == 'MeSH' else ['Publication index']
            for column in spec['columns']:
                for key in column.get('source_keys', [column.get('source_key', column['header'])]):
                    if key not in ('PMID', 'Publication Index', 'Publication index') and key not in headers:
                        headers.append(key)
            if 'Associated PMIDs' in headers:
                headers[headers.index('Associated PMIDs')] = 'Publication indices'
            rows = [{h: row.get(h, '') for h in headers} for row in rows]
        displayed = layout_sheet({'name': name, 'headers': headers, 'rows': [[row.get(h) for h in headers] for row in rows]})
        records = [dict(zip(displayed['headers'], values)) for values in displayed['rows']]
        # Source column moves must not change a separately registered output order.
        target_keys = [c['source_key'] for c in target_specs[displayed['name']]['columns']]
        if any(set(row) != set(target_keys) for row in records):
            raise ValueError('Source/synthesis registration fields differ: ' + displayed['name'])
        result[displayed['name']] = [{key: row[key] for key in target_keys} for row in records]
    return result


def run_stage(args):
    """Execute exactly one selected stage; offline stages never call retrieval.

    Parameters
    ----------
    args : argparse.Namespace
        Explicit CLI stage, input, output, cache and template paths.

    Returns
    -------
    dict
        Stage receipt with hashes, counts and final output references.

    Raises
    ------
    ValueError
        Inputs are incomplete, registry relationships conflict or retrieval fails.
    FileExistsError
        A stage output directory already exists.
    """
    root, folder = args.root.resolve(), args.output_dir.resolve()
    publications = _load(args.publication_index)
    if args.stage == 'synthesize':
        from .enrichment_synthesis import synthesize
        if not all((args.pubmed, args.geo, args.biostudies, args.ena, args.registry)):
            raise ValueError('Synthesis requires four explicit completed source paths and a registry; no retrieval is launched')
        registry = _load(args.registry)
        data = synthesize(root, registry, folder, publication_index=args.publication_index,
                          pubmed=args.pubmed, geo=args.geo, biostudies=args.biostudies, ena=args.ena, compress=True)
        # Native tables and original value combinations are retained once in a
        # compressed canonical file. Display tables need not duplicate them on
        # disk: the registered layout reproducibly derives them for export.
        display_tables = synthesis_tables(data, root)
        receipt = export_registered(args.template or legacy_synthesis_template(root),
                                    folder / 'Enrichment-Synthesis.xlsx', display_tables, overflow_sidecar=True)
        receipt['canonical_database'] = str(folder / 'synthesis.json.gz')
    else:
        if folder.exists():
            raise FileExistsError(folder)
        if args.stage == 'registry':
            folder.mkdir(parents=True)
            registry = publication_registry(publications, _load(args.registry) if args.registry else [])
            _save(folder / 'publication-registry.json', registry)
            receipt = {'publications': len(registry), 'without_pmid': sum(not p['PMID'] for p in registry)}
        elif args.stage == 'pubmed':
            from .pubmed_enrichment import Retrieval
            from .pubmed_projection import project_saved
            from .pubmed_layout import indexed_tables
            transport = Retrieval(folder, args.cache_root)
            pmids = sorted({str(p['PMID']) for p in publications if p.get('PMID')}, key=int)
            transport.retrieve(pmids)
            data = project_saved(folder, pmids)
            data.update(schema_version='pubmed-enrichment/1', orcs_publications=publications,
                        unresolved_publications=[p for p in publications if not p.get('PMID')], status='complete',
                        retrieval_date_policy='Original native receipt dates; this run may reuse exact verified requests')
            selected_registry = publication_registry(publications, _load(args.registry) if args.registry else [])
            _save(folder / 'publication-registry.json', selected_registry)
            data['display_rows'] = indexed_tables(data, selected_registry,
                root / 'data/identifiers/supplemental-index-registry.json')
            data['source_directory'] = str(folder)
            data['summary'] = {'publications': len(publications), 'retrieved_pmids': len(pmids),
                'without_pmid': len(data['unresolved_publications']),
                'sheet_rows': {name: len(rows) for name, rows in data['display_rows'].items()}}
            _save(folder / 'database.json', data)
            receipt = export_registered(args.template or root / 'data/templates/PubMed-Enrichment-Template.xlsx', folder / 'PubMed-Enrichment.xlsx', data['display_rows'], overflow_sidecar=True)
            receipt.update(publications=len(publications), pmids=len(pmids), live_attempts=transport.attempts,
                           cached_responses=sum(bool(r.get('reused_from')) for r in transport.receipts))
        elif args.stage == 'geo':
            from .geo_collection import enrich_collection
            for phase in ('discover', 'samples', 'project'):
                enrich_collection(args.publication_index, folder, repository_root=root, phase=phase,
                                  cache_roots=args.cache_root, publication_registry=args.registry)
            receipt = enrich_collection(args.publication_index, folder, repository_root=root,
                phase='export', template=args.template, publication_registry=args.registry)
        elif args.stage == 'biostudies':
            from .biostudies_collection import run_collection
            data = run_collection(args.publication_index, folder, registry=args.registry, pubmed=args.pubmed,
                template=args.template or root / 'data/templates/BioStudies-Enrichment-Template.xlsx',
                caches=args.cache_root, index_registry=root / 'data/identifiers/supplemental-index-registry.json')
            if data['status'] != 'complete':
                raise ValueError('BioStudies retrieval incomplete; checkpoint retained')
            receipt = _load(folder / 'BioStudies-Enrichment.manifest.json')
            receipt.update(data['summary'])
        elif args.stage == 'figshare':
            from .figshare_enrichment import run_collection
            data = run_collection(args.publication_index, folder, registry=args.registry,
                template=args.template or root / 'data/templates/Figshare-Enrichment-Template.xlsx',
                caches=args.cache_root, offline=getattr(args, 'offline', False),
                index_registry=root / 'data/identifiers/supplemental-index-registry.json')
            if data['status'] != 'complete':
                raise ValueError('Figshare retrieval incomplete; canonical checkpoints retained')
            receipt = _load(folder / 'Figshare-Enrichment.manifest.json')
            receipt.update(data['summary'])
        elif args.stage == 'mendeley':
            from .mendeley_data_enrichment import run_collection
            data = run_collection(args.publication_index, folder, registry=args.registry,
                template=args.template or root / 'data/templates/Mendeley-Data-Enrichment-Template.xlsx',
                caches=args.cache_root, token_file=getattr(args, 'access_token_file', None),
                client_file=getattr(args, 'client_credentials_file', None),
                doi_only=True, offline=getattr(args, 'offline', False),
                index_registry=root / 'data/identifiers/supplemental-index-registry.json')
            if data['status'] != 'complete':
                raise ValueError('Mendeley discovery/retrieval incomplete; metadata checkpoints retained')
            receipt = _load(folder / 'Mendeley-Data-Enrichment.manifest.json')
            receipt.update(data['summary'])
        elif args.stage == 'ena':
            from .ena_collection import run
            if not args.geo or not args.pubmed:
                raise ValueError('ENA requires the selected GEO and PubMed canonical databases')
            data = run(root, folder, args.cache_root, metadata_only_projects=args.metadata_only_project,
                       publication_index=args.publication_index, geo_database=args.geo, pubmed_database=args.pubmed,
                       template=args.template or root / 'data/templates/ENA-Enrichment-Template.xlsx',
                       publication_registry=args.registry)
            if data['status'] not in ('complete', 'complete_with_omissions'):
                raise ValueError('ENA retrieval incomplete; checkpoint retained')
            receipt = export_registered(args.template or root / 'data/templates/ENA-Enrichment-Template.xlsx', folder / 'ENA-Enrichment.xlsx', data['rows'])
            receipt.update(data['summary'])
    if getattr(args, 'compress_json', False):
        receipt = compress_stage_output(folder, receipt)
    receipt.update(stage=args.stage, completed_utc=datetime.now(timezone.utc).isoformat(),
                   publication_index=str(args.publication_index.resolve()),
                   publication_index_sha256=hashlib.sha256(args.publication_index.read_bytes()).hexdigest(),
                   command_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    _save(folder / 'stage-receipt.json', receipt)
    return receipt


def main():
    """Run one explicit stage; use --help for the independent command contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', required=True, choices=('registry', 'pubmed', 'geo', 'biostudies', 'mendeley', 'figshare', 'ena', 'synthesize'))
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--publication-index', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--cache-root', action='append', type=Path, default=[])
    parser.add_argument('--registry', type=Path)
    parser.add_argument('--template', type=Path)
    for name in ('pubmed', 'geo', 'biostudies', 'ena'):
        parser.add_argument('--' + name, type=Path)
    parser.add_argument('--access-token-file', type=Path)
    parser.add_argument('--client-credentials-file', type=Path)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--compress-json', action='store_true',
                        help='Losslessly gzip the completed canonical JSON and remove its plain copy')
    parser.add_argument('--metadata-only-project', action='append', default=[])
    print(json.dumps(run_stage(parser.parse_args())))


if __name__ == '__main__':
    main()
