"""Build a review projection from explicit, already-saved enrichment outputs.

This offline CLI accepts an explicit persistent publication registry. It writes
new JSON only: no network calls, enrichment launches, dataset merges or source
edits. Source row mappings accompany each table so joined cell values do not
erase conflicting native observations. Excel is a derived review view.
"""
import argparse
import hashlib
import gzip
import json
from pathlib import Path
import re

import openpyxl
from .arrayexpress_collection import project as arrayexpress_project
from .ena_projection import project as ena_project
from .pubmed_workbook import subset_rows
from .review_projection import hierarchy_rows, publication_date, unique_entities


def _tokens(value):
    return set(re.findall(r'PUB-\d+|ORCS:\d+|orcs-\d+|\d+', str(value or '')))


def _read_book(path):
    book = openpyxl.load_workbook(path, read_only=True)
    try:
        tables = {}
        for sheet in book:
            rows = sheet.iter_rows(values_only=True)
            headers = next(rows)
            tables[sheet.title] = [dict(zip(headers, row)) for row in rows]
        return tables
    finally:
        book.close()


def synthesize(root, registry, output, *, publication_index=None, pubmed=None, geo=None, arrayexpress=None, ena=None, compress=False):
    """Write an offline selected-publication projection into a fresh directory.

    Parameters
    ----------
    root : Path
        Repository containing completed data/orcs enrichment packages.
    registry : list of dict
        Persistent Publication index and PMID entries; IDs must be unique.
    output : Path
        New directory. Existing outputs are refused.

    Returns
    -------
    dict
        Review sheets, source-row evidence, input hashes and selection registry.

    Raises
    ------
    ValueError
        Publication keys are duplicated or a requested publication is absent.
    FileExistsError
        Output directory already exists.
    """
    root, output = Path(root), Path(output)
    keys = [p['Publication index'] for p in registry]
    pmids = [str(p['PMID']) for p in registry if p.get('PMID')]
    if len(set(keys)) != len(keys) or len(set(pmids)) != len(pmids):
        raise ValueError('Publication registry identities must be unique')
    if not all(re.fullmatch(r'PUB-\d{4,}', key) for key in keys):
        raise ValueError('Invalid publication index')
    mapping = {str(p['PMID']): p['Publication index'] for p in registry if p.get('PMID')}
    for p in registry:
        if p.get('ORCS Publication ID'):
            for prefix in ('ORCS:', 'orcs-'):
                mapping[prefix + str(p['ORCS Publication ID'])] = p['Publication index']
    if output.exists():
        raise FileExistsError(output)
    sources = {}
    def load(name, override=None):
        path = Path(override) if override else root / 'data/orcs' / name
        sources[str(path.resolve())] = hashlib.sha256(path.read_bytes()).hexdigest()
        return json.loads(path.read_text(encoding='utf-8'))
    ena = load('ena-enrichment.json', ena)
    ae = load('arrayexpress-enrichment.json', arrayexpress)
    pm = load('pubmed-enrichment.json', pubmed)
    publications = load('publication-index.json', publication_index)
    for label, database in [('PubMed', pm), ('ArrayExpress', ae), ('ENA', ena)]:
        if database.get('status') and database['status'] not in ('complete', 'complete_with_omissions'):
            raise ValueError(label + ' source is incomplete; synthesis cannot hide retrieval failures')
    if not set(pmids) <= {str(row[0]) for row in pm['rows']['Publication']}:
        raise ValueError('Selected PMIDs are absent from the PubMed source coverage')
    expected_keys = {str(p.get('PMID') or 'ORCS:' + str(p['ORCS Publication ID'])) for p in registry}
    if not expected_keys <= {str(p['key']) for p in ena['publications']}:
        raise ValueError('ENA source does not cover the selected publication registry')
    if not expected_keys <= {str(p['publication'].get('PMID') or 'ORCS:' + str(p['publication']['PUBLICATION_ID'])) for p in ae['publications']}:
        raise ValueError('ArrayExpress source does not cover the selected publication registry')
    if geo:
        native_geo = load('geo-enrichment.json', geo)
        covered = {key.replace('orcs-', 'ORCS:') for key in native_geo['publications']}
        if not expected_keys <= covered:
            raise ValueError('GEO source does not cover the selected publication registry')
        geo = project_geo(native_geo)
    else:
        geo_path = root / 'data/orcs/GEO-Enrichment.xlsx'
        sources[str(geo_path.resolve())] = hashlib.sha256(geo_path.read_bytes()).hexdigest()
        geo = _read_book(geo_path)
    tables, evidence, links = {}, {}, []
    memberships = {}

    def indices(value):
        return '\n'.join(sorted(mapping[p] for p in _tokens(value) if p in mapping))

    def member(repository, accession, pubs):
        if not accession or not pubs:
            return
        memberships.setdefault((repository, accession), set()).update(pubs.split('\n'))

    def store(name, rows, identity=None):
        # Row indices point into these copied source observations, not into an
        # unrelated global row order. Values and identities remain inspectable.
        evidence[name] = rows
        tables[name] = unique_entities(rows, identity) if identity else rows

    pubs = []
    for p in publications:
        key = str(p.get('PMID') or 'ORCS:' + p['PUBLICATION_ID'])
        if key in mapping:
            pubs.append({'Publication index': mapping[key], 'PMID': p.get('PMID'), 'DOI': p.get('DOI'),
                         'PMCID': p.get('PMCID'), 'Publication title': p['TITLE'], 'Authors': p.get('AUTHORS'),
                         'Journal': p.get('JOURNAL'), 'Publication date': publication_date(p.get('PUBLICATION_DATE'))})
    if len(pubs) != len(registry):
        raise ValueError('Selected publication missing from the saved ORCS publication index')
    tables['Publications'] = sorted(pubs, key=lambda r: r['Publication index'])

    # PubMed row layouts come from the registered source headers, not guessed
    # accession types. Grouped MeSH counts are recomputed for this selection.
    projected_pm = subset_rows(pm, pmids)
    registration = json.loads((root / 'data/templates/PubMed-Enrichment.manifest.json').read_text(encoding='utf-8'))
    for sheet in registration['sheets']:
        name = sheet['name']
        if name == 'Publication':
            continue
        rows = [dict(zip(sheet['headers'], row)) for row in projected_pm[name]]
        for row in rows:
            if 'PMID' in row:
                row['Publication index'] = indices(row.pop('PMID'))
            if 'Associated PMIDs' in row:
                row['Publication indices'] = indices(row.pop('Associated PMIDs'))
            if name == 'Repository Records':
                member(row['Resource'], row['Accession'], row['Publication index'])
        store('PubMed - ' + name, rows, ['Resource', 'Accession'] if name == 'Repository Records' else None)

    selected_series = set()
    for row in geo['Series Records']:
        if indices(row.get('PMID')):
            selected_series.add(row['geo_accession'])
            member('GEO', row['geo_accession'], indices(row['PMID']))
    for name, original in geo.items():
        rows = []
        for original_row in original:
            p = indices(original_row.get('PMID'))
            if not p:
                continue
            row = {'Publication index': p, **{k: v for k, v in original_row.items() if k not in ('PMID', 'citation')}}
            rows.append(row)
        if name == 'Series Hierarchy':
            rows = hierarchy_rows(rows, 'GSE', 'Related GSE', 'GEO')
            identity = ['GSE', 'Relationship', 'Related GSE']
        else:
            identity = {'Series Records': ['geo_accession'], 'Repository Identifiers': ['Identifier'], 'Sample Metadata': ['GSM']}[name]
        # Missing accession fields remain independent evidence, never grouped
        # into a false shared entity. Such rows receive an explicit issue below.
        missing = [r for r in rows if any(not r.get(k) for k in identity)]
        store('GEO - ' + name, [r for r in rows if r not in missing], identity)
        if missing:
            evidence['GEO - ' + name + ' - unidentified'] = missing

    study_pubs = {}
    for accession, study in ena['studies'].items():
        pubs = sorted({mapping[a['publication_key']] for a in study['associations'] if a['publication_key'] in mapping})
        if pubs:
            study_pubs[accession] = '\n'.join(pubs)
            member('ENA', accession, study_pubs[accession])
    sub_ena = {**ena, 'studies': {k: v for k, v in ena['studies'].items() if k in study_pubs}, 'issues': list(ena['issues'])}
    projected_ena = ena_project(sub_ena)
    for name in ('Studies', 'Study hierarchy', 'Samples', 'Experiments', 'Runs'):
        rows = []
        for row in projected_ena[name]:
            if name == 'Study hierarchy':
                associated = {study_pubs[k] for k in (row['Study accession'], row['Related study accession']) if k in study_pubs}
            elif name == 'Studies':
                associated = {study_pubs[row['Study accession']]}
            else:
                associated = {study_pubs[k] for k in row.get('Reporting studies', '').split('\n') if k in study_pubs}
            p = '\n'.join(sorted(set('\n'.join(associated).split('\n')) - {''}))
            rows.append({'Publication index': p, **row})
        identity = {'Studies': ['Study accession'], 'Study hierarchy': ['Study accession', 'Relationship', 'Related study accession'],
                    'Samples': ['Sample accession'], 'Experiments': ['Experiment accession'], 'Runs': ['Run accession']}[name]
        store('ENA - ' + name, rows, identity)

    ae_members = {}
    for publication in ae['publications']:
        p = publication['publication']
        key = str(p.get('PMID') or 'ORCS:' + str(p['PUBLICATION_ID']))
        if key in mapping:
            for observation in publication['observations']:
                accession = observation['accession']
                if accession in ae['studies'] and ae['studies'][accession].get('arrayexpress_membership_confirmed'):
                    current = set(ae_members.get(accession, '').split('\n')) - {''}
                    ae_members[accession] = '\n'.join(sorted(current | {mapping[key]}))
    for row in ae['rows']['Studies']:
        if indices(row.get('PMID')):
            accession = row['Study accession']
            current = set(ae_members.get(accession, '').split('\n')) - {''}
            ae_members[accession] = '\n'.join(sorted(current | set(indices(row['PMID']).split('\n'))))
    for accession, pubs in ae_members.items():
        member('ArrayExpress', accession, pubs)
    projected_ae = arrayexpress_project({**ae, 'studies': {k: v for k, v in ae['studies'].items() if k in ae_members}})
    for name in ('Studies', 'Protocols', 'Sample metadata', 'Assay metadata', 'IDF metadata', 'SDRF metadata'):
        rows = [{'Publication index': ae_members[r['Study accession']], **{k: v for k, v in r.items() if k != 'PMID'}}
                for r in projected_ae[name]]
        store('AE - ' + name, rows)
    for (repository, accession), pubs in sorted(memberships.items()):
        links.extend({'Publication index': p, 'Repository': repository, 'Accession': accession}
                     for p in sorted(pubs))
    tables = {'Publications': tables.pop('Publications'), 'Publication-repository links': links, **tables}
    result = {'schema_version': 'enrichment-synthesis/2', 'registry': registry, 'input_sha256': sources,
        'tables': tables, 'source_rows': evidence,
        'policies': {'retrieval': 'none; saved outputs only', 'association': 'candidate; qualifying screens unassessed',
            'entity_values': 'distinct native values joined by newline; source_rows retain original combinations',
            'dates': 'literal ISO; preserve reported precision', 'repository_relationships': 'general sheet omitted pending owner review; native hierarchy retained'},
        'sheet_rows': {k: len(v) for k, v in tables.items()}}
    output.mkdir(parents=True)
    if compress:
        with gzip.open(output / 'synthesis.json.gz', 'wt', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, separators=(',', ':'))
    else:
        (output / 'synthesis.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return result


def project_geo(database):
    """Project canonical GEO records without reading a reviewer workbook.

    Parameters
    ----------
    database : dict
        Saved series, samples and publication memberships, with raw fields.

    Returns
    -------
    dict
        The four accepted GEO tables; native observation combinations remain
        separate until the synthesis entity grouping stage.
    """
    tables = {name: [] for name in ('Series Records', 'Series Hierarchy', 'Repository Identifiers', 'Sample Metadata')}
    for accession, record in database['series'].items():
        fields = record['fields']
        members = record.get('publication_keys', record.get('pmids', []))
        for pmid in members:
            base = {'PMID': pmid, 'GSE': accession}
            row = {**base, **{k.removeprefix('Series_'): '\n'.join(v) for k, v in fields.items()
                             if not any(x in k for x in ('contact_', 'contributor', 'supplementary_file', 'sample_id', 'relation', 'citation'))}}
            row['sample_count'] = len(fields.get('Series_sample_id', []))
            tables['Series Records'].append(row)
            for relation in fields.get('Series_relation', []):
                found = re.fullmatch(r'(SuperSeries of|SubSeries of): (GSE\d+)', relation)
                if found:
                    tables['Series Hierarchy'].append({**base, 'Relationship': found[1], 'Related GSE': found[2]})
                else:
                    identifier = re.search(r'(PRJ(?:NA|EB|DB)\d+|[SED]RP\d+)', relation)
                    tables['Repository Identifiers'].append({**base, 'GSM': None, 'Identifier': identifier[0] if identifier else None,
                        'Entity Level': 'Series', 'Resource': relation.split(':', 1)[0], 'Native Field': 'Series_relation'})
            for key in ('Series_platform_id', 'Series_sample_id'):
                for value in fields.get(key, []):
                    tables['Repository Identifiers'].append({**base, 'GSM': value if key.endswith('sample_id') else None,
                        'Identifier': value, 'Entity Level': 'Series', 'Resource': 'GEO Sample' if key.endswith('sample_id') else 'GEO Platform', 'Native Field': key})
            for gsm in fields.get('Series_sample_id', []):
                native = database['samples'][gsm]['fields']
                tables['Sample Metadata'].append({**base, 'GSM': gsm,
                    **{k.removeprefix('Sample_'): '\n'.join(v) for k, v in native.items()
                       if not any(x in k for x in ('contact_', 'contributor', 'supplementary_file', 'relation'))}})
                for key in ('Sample_relation', 'Sample_platform_id'):
                    for value in native.get(key, []):
                        found = re.search(r'(SAM(?:N|EA|D)\d+|[SED]RX\d+|GPL\d+)', value)
                        tables['Repository Identifiers'].append({**base, 'GSM': gsm, 'Entity Level': 'Sample',
                            'Resource': value.split(':', 1)[0] if key == 'Sample_relation' else 'GEO Platform',
                            'Identifier': found[0] if found else None, 'Native Field': key})
    return tables


def main():
    """Project an explicit registry into a new offline synthesis directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--registry', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = synthesize(args.root, json.loads(args.registry.read_text(encoding='utf-8')), args.output)
    print(json.dumps(result['sheet_rows']))


if __name__ == '__main__':
    main()
