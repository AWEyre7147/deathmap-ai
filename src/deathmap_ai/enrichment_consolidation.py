"""Offline, source-preserving consolidation of the eight current enrichments.

The registered workbook is a review view. Source files remain authoritative;
their hashes, retrieval issues and locations accompany the consolidated tables.
No retrieval or persistent identifier allocation occurs here.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path

from .enrichment_export import export_registered
from .json_storage import load_json, resolve_json_path


SHEETS = {
    'PubMed': [('PubMed Repository Records', 'Repository Records'),
               ('PubMed SRA Accessions', 'SRA Accessions'),
               ('PubMed MeSH Terms', 'MeSH'), ('PubMed MeSH Links', 'MeSH Links')],
    'PMC': [('PMC Publication Records', 'Publications'),
            ('PMC Supplemental Records', 'Supplementary Entries'), ('PMC Cloud Records', 'Cloud Files')],
    'GEO': [('GEO Series Records', 'Series Records'), ('GEO Sample Records', 'Sample Metadata'),
            ('GEO Repository Identifiers', 'Repository Identifiers')],
    'ENA': [('ENA Study Records', 'Studies'), ('ENA Sample Records', 'Samples'),
            ('ENA Experiment Records', 'Experiments'), ('ENA Run Records', 'Runs'), ('ENA File Records', 'Files')],
    'BioStudies': [('BioStudies Publication Records', 'Publications'),
                  ('BioStudies Supplemental Records', 'Supplementary Files')],
    'Figshare': [('Figshare Publication Records', 'Publications'), ('Figshare Item Records', 'Items'),
                ('Figshare File Records', 'Files')],
    'Mendeley': [('Mendeley Publication Records', 'Publications'), ('Mendeley Dataset Record', 'Datasets'),
                ('Mendeley File Records', 'Files')],
    'Library': [('Library Publication Records', 'Publications'), ('Library Context Records', 'Article Context'),
               ('Library Supplemental Records', 'Supporting Materials'), ('Library Repository Links', 'Repository References')],
}

COUNTS = {
    'PMC Supplemental Entries': ('PMC Supplemental Records', 'Supplemental Index'),
    'GEO Series': ('GEO Series Records', 'Series Index'),
    'ENA Studies': ('ENA Study Records', 'Study Index'),
    'BioStudies Files': ('BioStudies Supplemental Records', 'BioStudies Index'),
    'Figshare Items': ('Figshare Item Records', 'Figshare Item Index'),
    'Mendeley Datasets': ('Mendeley Dataset Record', 'MD Dataset Index'),
    'Library Supporting Materials': ('Library Supplemental Records', 'Supporting Material Index'),
}


def load(path):
    return load_json(path)


def digest(path):
    with resolve_json_path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def master_rows(publications, registry, pubmed, tables):
    """Join the cohort to saved PubMed metadata and distinct resource counts."""
    by_native = {str(r['ORCS Publication ID']): r['Publication index'] for r in registry}
    if len(by_native) != len(registry) or len(set(by_native.values())) != len(registry):
        raise ValueError('Publication registry is ambiguous')
    records = {r['Publication Index']: r for r in pubmed}
    if len(records) != len(pubmed):
        raise ValueError('Duplicate PubMed publication records')
    counts = {}
    for label, (sheet, key) in COUNTS.items():
        identities = defaultdict(set)
        for row in tables[sheet]:
            if not row.get(key):
                raise ValueError(f'Missing resource identifier: {sheet}: {key}')
            identities[row['Publication Index']].add(row[key])
        counts[label] = identities
    result = []
    for p in publications:
        index = by_native[str(p['PUBLICATION_ID'])]
        r = records.get(index, {})
        row = {'Publication Index': index, 'Title': r.get('Title') or p.get('TITLE'),
               'Journal': p.get('JOURNAL'), 'PMID': r.get('PMID') or p.get('PMID'),
               'PMCID': r.get('PMCID') or p.get('PMCID'), 'DOI': r.get('DOI') or p.get('DOI'),
               'Publication Date': r.get('Publication Date', ''), 'PubMed Records': int(index in records)}
        row.update({label: len(identities[index]) for label, identities in counts.items()})
        result.append(row)
    if len({r['Publication Index'] for r in result}) != len(result):
        raise ValueError('Duplicate cohort publication')
    return result


def consolidate(publication_index, registry, index_registry, sources):
    """Load all eight explicit canonical sources without changing any input."""
    if set(sources) != set(SHEETS):
        raise ValueError('Exactly eight sources required: ' + ', '.join(SHEETS))
    tables, provenance, pubmed = {}, {}, []
    for name, mappings in SHEETS.items():
        path = resolve_json_path(sources[name]).resolve()
        data = load(path)
        if name == 'GEO':
            from .geo_indexed_projection import project
            # The saved GEO export uses accession-sorted in-memory indices,
            # rather than allocations in the persistent supplemental registry.
            # Reproduce that source policy without adding registry namespaces.
            rows = project(data, registry, None)
        else:
            rows = data['display_rows'] if name == 'PubMed' else data['rows']
        if name == 'PubMed':
            pubmed = rows['Publication']
        for sheet, native in mappings:
            tables[sheet] = rows[native]
        provenance[name] = {'path': str(path), 'sha256': digest(path),
                            'schema_version': data.get('schema_version'),
                            'status': data.get('status', 'See saved source provenance'),
                            'issues': data.get('issues', []), 'summary': data.get('summary', {})}
        del data
    tables['Publication Records'] = master_rows(load(publication_index), load(registry), pubmed, tables)
    allowed = {r['Publication Index'] for r in tables['Publication Records']}
    for name, rows in tables.items():
        if name == 'PubMed MeSH Terms':
            continue
        if any(r.get('Publication Index') not in allowed for r in rows):
            raise ValueError('Source publication lies outside selected cohort: ' + name)
    return {'schema_version': 'enrichment-consolidation/1',
            'created_utc': datetime.now(timezone.utc).isoformat(),
            'policy': 'Saved source observations; counts are distinct resource identifiers, not validated datasets or screens. Zero means no saved record, not verified absence.',
            'inputs': {str(Path(p).resolve()): digest(p) for p in (publication_index, registry, index_registry)},
            'sources': provenance, 'tables': tables}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publication-index', type=Path, required=True)
    parser.add_argument('--registry', type=Path, required=True)
    parser.add_argument('--index-registry', type=Path, required=True)
    parser.add_argument('--source', action='append', required=True, help='Resource=canonical.json; repeat for all eight resources')
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    sources = dict(item.split('=', 1) for item in args.source)
    if len(sources) != len(args.source):
        raise ValueError('Duplicate source argument')
    data = consolidate(args.publication_index, args.registry, args.index_registry, sources)
    args.output_dir.mkdir(parents=True)
    database = args.output_dir / 'synthesis.json.gz'
    with gzip.open(database, 'wt', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False)
    receipt = export_registered(args.template, args.output_dir / 'Enrichment-Synthesis.xlsx',
                                data['tables'], overflow_sidecar=True)
    receipt.update(canonical_database=str(database), canonical_sha256=digest(database), sources=data['sources'],
                   projection_code_sha256=digest(__file__),
                   registration_sha256=digest(args.template.with_suffix('.manifest.json')))
    (args.output_dir / 'stage-receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8', newline='\n')
    print(json.dumps({'workbook': str(args.output_dir / 'Enrichment-Synthesis.xlsx'),
                      'sheet_rows': receipt['sheet_rows'], 'verified_cells': receipt.get('verified_cells')}))


if __name__ == '__main__':
    main()
