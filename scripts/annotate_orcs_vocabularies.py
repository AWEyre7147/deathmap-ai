"""Annotate the owner's exact ORCS vocabulary values from saved references.

Cellosaurus identity is matched using names/synonyms and species, never a cancer
keyword. Ontology accessions linked by ORCS take precedence over name matching.
Unresolved identities, obsolete concepts, and conflicts remain review issues.
This stage leaves the cached ORCS screens and discovery outputs unchanged.
"""
import hashlib
import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from deathmap_ai.repository_paths import resolve_relocation

FOLDER = ROOT / 'data/cellosaurus/orcs-annotations'
RAW = FOLDER / 'raw'
CACHE = ROOT / 'data/orcs/screen-index.json'
VOCABS = ROOT / 'docs/vocabularies/orcs/local'

def key(value):
    """Compare casing and repeated spaces without erasing biological qualifiers."""
    return ' '.join(value.casefold().split())

def punctuation_key(value):
    """Permit only spacing/hyphen/underscore/period variants, preserving qualifiers."""
    value = key(value).translate(str.maketrans({'β': 'beta', 'α': 'alpha', 'γ': 'gamma', '–': '-', '−': '-'}))
    return re.sub(r'[\s_.-]', '', value)

def parse_cellosaurus(path):
    """Parse provider flat-file records; retain native tags for selected evidence."""
    records, current = {}, defaultdict(list)
    with path.open(encoding='utf-8') as source:
        for line in source:
            if line.startswith('//'):
                if current.get('AC'):
                    accession = current['AC'][0]
                    names = current['ID'] + [s.strip() for text in current.get('SY', []) for s in text.split(';')]
                    records[accession] = {'accession': accession, 'names': names,
                        'category': current['CA'][0], 'secondary': [s.strip() for t in current.get('AS', []) for s in t.split(';')],
                        'species': re.findall(r'NCBI_TaxID=(\d+)', ' '.join(current.get('OX', []))),
                        'native_fields': dict(current)}
                current = defaultdict(list)
            elif re.match(r'^[A-Z]{2}   ', line):
                current[line[:2]].append(line[5:].strip())
    if not records:
        raise ValueError('Unrecognized Cellosaurus file')
    return records

def parse_obo(path, prefix):
    """Retain native ontology definitions and exact synonyms, including obsolete flags."""
    text = path.read_text(encoding='utf-8')
    version = re.search(r'^data-version: (.+)$', text, re.M)
    records = {}
    for stanza in text.split('\n[Term]\n')[1:]:
        stanza = stanza.split('\n[Typedef]')[0]
        identifier = re.search(r'^id: (.+)$', stanza, re.M)
        label = re.search(r'^name: (.+)$', stanza, re.M)
        native_id = identifier.group(1) if identifier else ''
        canonical_id = re.sub(r'^efo:EFO_', 'EFO:', native_id)
        if not identifier or not label or not canonical_id.startswith(prefix + ':'):
            continue
        definition = re.search(r'^def: "((?:\\.|[^"\\])*)"', stanza, re.M)
        records[canonical_id] = {'id': canonical_id, 'native_id': native_id, 'label': label.group(1),
            'definition': definition.group(1).replace('\\"', '"').replace('\\n', ' ') if definition else '',
            'synonyms': re.findall(r'^synonym: "((?:\\.|[^"\\])*)" EXACT ', stanza, re.M),
            'obsolete': 'is_obsolete: true' in stanza, 'native_stanza': stanza.strip(),
            'alt_ids': re.findall(r'^alt_id: (.+)$', stanza, re.M)}
    if not records:
        raise ValueError(f'Unrecognized {prefix} ontology')
    return records, version.group(1) if version else None

def select_identity(value, species, records, exact, normalized, direct=()):
    """Return a unique species-compatible identity or preserve candidate ambiguity."""
    candidates, method = set(direct), 'ORCS-linked accession'
    if not candidates:
        candidates, method = set(exact.get(key(value), [])), 'Exact name/synonym (case-insensitive)'
    if not candidates:
        candidates, method = set(normalized.get(punctuation_key(value), [])), 'Name/synonym punctuation variant'
    candidates = {a for a in candidates if a in records}
    if direct and len(candidates) == 1 and not set(species) <= set(records[next(iter(candidates))]['species']):
        return next(iter(candidates)), 'ORCS-linked accession with species conflict', sorted(candidates)
    compatible = {a for a in candidates if not species or set(species) <= set(records[a]['species'])}
    if len(compatible) == 1:
        return next(iter(compatible)), method, sorted(candidates)
    return None, 'species_conflict' if candidates and not compatible else 'ambiguous' if candidates else 'unmatched', sorted(candidates)

def vocabulary_terms(path):
    """Read exact first-column values even after the owner reformats Markdown spacing."""
    rows = [line for line in path.read_text(encoding='utf-8').splitlines() if line.startswith('|')]
    return [line.strip().strip('|').split('|')[0].strip() for line in rows[2:]]

def render(path, headers, rows):
    """Replace the table only, retaining the owner-visible source context and term order."""
    text = path.read_text(encoding='utf-8')
    intro = text[:text.index('\n|')]
    intro = re.sub(r'(?:Selected descriptions|All values were checked).*?(?:\n\n|$)',
        'All values were checked against saved reference metadata. Unavailable fields are blank; unresolved matches are recorded in the review column. See the [annotation evidence](../../../../data/cellosaurus/orcs-annotations/README.md).\n\n', intro, flags=re.S)
    def escape(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    table = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    table += ['| ' + ' | '.join(escape(c) for c in row) + ' |' for row in rows]
    path.write_text(intro.rstrip() + '\n\n' + '\n'.join(table) + '\n', encoding='utf-8')

def reference_description(record):
    """Summarize reported species, disease and origin; do not infer cancer status."""
    tags = record['native_fields']
    species = [s.split(';', 1)[1].strip().lstrip('! ').strip() for s in tags.get('OX', []) if ';' in s]
    disease = list(dict.fromkeys(s.split(';', 2)[2].strip().rstrip('.') for s in tags.get('DI', []) if s.count(';') >= 2))
    sites = [re.sub(r';\s*(?:UBERON|PO)=.*', '', s.split('Derived from site: ', 1)[1]).rstrip('.')
             for s in tags.get('CC', []) if s.startswith('Derived from site: ')]
    chunks = ['Species: ' + '; '.join(species)] if species else []
    if disease:
        chunks.append('Reported disease: ' + '; '.join(disease))
    if sites:
        chunks.append('Origin: ' + '; '.join(sites))
    if not disease and not sites:
        chunks.append('Reference name: ' + record['names'][0])
    return '. '.join(chunks) + '.'

def main():
    """Check every vocabulary row, write traceable annotations and review counts."""
    screens = json.loads(CACHE.read_text(encoding='utf-8'))
    initial_hash = hashlib.sha256(CACHE.read_bytes()).hexdigest()
    lines = vocabulary_terms(VOCABS / 'CELL_LINE.md')
    types = vocabulary_terms(VOCABS / 'CELL_TYPE.md')
    cells = parse_cellosaurus(RAW / 'cellosaurus.txt')
    exact, normalized = defaultdict(set), defaultdict(set)
    for accession, record in cells.items():
        for name in record['names']:
            exact[key(name)].add(accession)
            normalized[punctuation_key(name)].add(accession)
    ontologies, versions, aliases = {}, {}, {}
    for prefix in ['BTO', 'CL', 'EFO']:
        terms, version = parse_obo(RAW / (prefix.lower() + '.obo'), prefix)
        ontologies[prefix], versions[prefix] = terms, version
        for identifier, term in terms.items():
            for alias in term['alt_ids']:
                aliases[alias] = identifier
    contexts = {field: defaultdict(list) for field in ['CELL_LINE', 'CELL_TYPE']}
    for screen in screens:
        for field in contexts:
            contexts[field][screen[field]].append({k: screen[k] for k in ['SCREEN_ID', 'SOURCE_ID', 'SOURCE_TYPE', 'CELL_LINE', 'CELL_TYPE', 'ORGANISM_ID']})
    mapping, direct_lines = defaultdict(lambda: defaultdict(set)), defaultdict(set)
    mapping_sources, line_mapping_sources, label_conflicts = defaultdict(list), defaultdict(list), []
    for path in RAW.glob('screen-*.html'):
        identifier = path.stem.removeprefix('screen-')
        screen = next(s for s in screens if s['SCREEN_ID'] == identifier)
        excerpt = path.read_text(encoding='utf-8')
        for line in excerpt.splitlines():
            if '<strong>Cell Type</strong>' in line:
                visible = re.search(r'Cell Type</strong></span> : <a[^>]*>([^<]+)', line)
                if visible and key(html.unescape(visible.group(1))) != key(screen['CELL_TYPE']):
                    label_conflicts.append({'screen_id': identifier, 'field': 'CELL_TYPE', 'cached': screen['CELL_TYPE'], 'live': html.unescape(visible.group(1))})
                    continue
                mapping_sources[screen['CELL_TYPE']].append(str(path.relative_to(FOLDER)))
                for prefix, number in re.findall(r'\b(BTO|CL|EFO)[:_]([0-9]+)', html.unescape(line)):
                    mapping[screen['CELL_TYPE']][prefix].add(prefix + ':' + number)
            elif '<strong>Cell Line</strong>' in line:
                visible = re.search(r'Cell Line</strong></span> : <a[^>]*>([^<]+)', line)
                if visible and key(html.unescape(visible.group(1))) != key(screen['CELL_LINE']):
                    label_conflicts.append({'screen_id': identifier, 'field': 'CELL_LINE', 'cached': screen['CELL_LINE'], 'live': html.unescape(visible.group(1))})
                    continue
                line_mapping_sources[screen['CELL_LINE']].append(str(path.relative_to(FOLDER)))
                direct_lines[screen['CELL_LINE']].update(re.findall(r'CVCL_[A-Z0-9]+', line))
    pilot = json.loads(resolve_relocation(ROOT / 'docs/references/orcs-cell-annotation-pilot/annotations.json').read_text(encoding='utf-8'))
    pilot_lines = {row['value']: row for row in pilot['cell_lines']}
    line_annotations, line_rows, selected = [], [], {}
    for value in lines:
        context = contexts['CELL_LINE'][value]
        species = {c['ORGANISM_ID'] for c in context if c['ORGANISM_ID']}
        accession, method, candidates = select_identity(value, species, cells, exact, normalized, direct_lines[value])
        issue = ''
        if not accession and value in pilot_lines and pilot_lines[value].get('accession'):
            accession = pilot_lines[value]['accession']
            method = pilot_lines[value].get('match_label', 'Previously verified pilot match')
            issue = pilot_lines[value].get('issue', '')
        annotation = {'value': value, 'match_method': method, 'candidate_accessions': candidates,
                      'orcs_mapping_evidence': line_mapping_sources[value],
                      'orcs_context': context, 'accession': accession, 'review_issues': []}
        if accession:
            record = cells[accession]
            selected[accession] = record
            annotation.update(category=record['category'], secondary_accessions=record['secondary'],
                              description=reference_description(record), reference_locator=f'cellosaurus.txt: AC {accession}')
            cautions = [s for s in record['native_fields'].get('CC', []) if s.startswith(('Problematic cell line:', 'Caution:'))]
            if method not in ['Exact name/synonym (case-insensitive)', 'ORCS-linked accession']:
                issue = (issue + ' ' + method + '; review identity.').strip()
            if cautions:
                issue = (issue + ' ' + ' '.join(cautions)).strip()
            if value in pilot_lines and pilot_lines[value].get('issue'):
                issue = (issue + ' ' + pilot_lines[value]['issue']).strip() if pilot_lines[value]['issue'] not in issue else issue
            link = f'[{accession}](https://www.cellosaurus.org/{accession})'
            secondary = '; '.join(f'[{a}](https://www.cellosaurus.org/{a})' for a in record['secondary'])
            line_rows.append([value, record['category'], annotation['description'], link, secondary, issue])
        else:
            issue = 'No unique species-compatible name/synonym match; study/model review needed.'
            if candidates:
                issue += ' Candidates: ' + '; '.join(candidates) + '.'
            if value in pilot_lines and pilot_lines[value].get('issue'):
                issue += ' ' + pilot_lines[value]['issue']
            line_rows.append([value, '', '', '', '', issue])
        annotation['review_issues'] = [issue] if issue else []
        line_annotations.append(annotation)
    type_annotations, type_rows, selected_terms = [], [], {}
    for value in types:
        row, issues, references = [value], [], {}
        for prefix in ['BTO', 'CL', 'EFO']:
            identifiers = mapping[value][prefix]
            basis = 'ORCS-linked metadata'
            if not identifiers:
                identifiers = {a for a, term in ontologies[prefix].items() if not term['obsolete']
                               and key(value) in {key(term['label']), *(key(s) for s in term['synonyms'])}}
                basis = 'Exact ontology label/synonym (case-insensitive)'
                if len(identifiers) > 1:
                    issues.append(prefix + ' ambiguous exact matches: ' + '; '.join(sorted(identifiers)))
                    identifiers = set()
            ids, definitions = [], []
            for accession in sorted(identifiers):
                canonical = aliases.get(accession, accession)
                term = ontologies[prefix].get(canonical)
                ids.append(accession)
                if term:
                    selected_terms[canonical] = term
                    if term['definition']:
                        definitions.append(term['definition'])
                    if term['obsolete']:
                        issues.append(accession + ' is obsolete; retain source assignment pending review.')
                    references[accession] = {'canonical_id': canonical, 'basis': basis, 'label': term['label'],
                        'definition': term['definition'], 'reference_locator': f'{prefix.lower()}.obo: id {canonical}'}
                else:
                    issues.append(accession + ' is linked by ORCS but absent from saved ontology release.')
                    references[accession] = {'basis': basis, 'definition': None}
            row += ['; '.join(ids), '; '.join(dict.fromkeys(definitions))]
        if not references:
            issues.append('No ORCS-linked or unique exact ontology label/synonym assignment found; review needed.')
        if value == 'Regulatory T cell':
            issues.append('Reference definition does not verify the subtype of each ORCS population.')
        if value == 'Glioblastoma Cell Line':
            issues.append('Screen 27 assigns 143B here; Cellosaurus reports osteosarcoma. Both observations retained.')
        row.append(' '.join(issues))
        type_rows.append(row)
        type_annotations.append({'value': value, 'references': references, 'review_issues': issues,
                                 'mapping_scope': 'Checked representative ORCS metadata pages and exact ontology names/synonyms; not verification of every screen assignment',
                                 'orcs_mapping_evidence': mapping_sources[value],
                                 'orcs_context': contexts['CELL_TYPE'][value]})
    for field, rows, headers in [
        ('CELL_LINE', line_rows, ['ORCS value', 'Cellosaurus category', 'Reference Description', 'Accession', 'Secondary Accession', 'Review Issue']),
        ('CELL_TYPE', type_rows, ['ORCS value', 'BTO Accession', 'BTO Definition', 'CL Accession', 'CL Definition', 'EFO Accession', 'EFO Definition', 'Review Issues'])]:
        path = VOCABS / (field + '.md')
        backup = FOLDER / (field + '-before-full-annotation.md')
        if not backup.exists():
            backup.write_bytes(path.read_bytes())
        original_terms = vocabulary_terms(path)
        render(path, headers, rows)
        assert vocabulary_terms(path) == original_terms
    receipts = {p.name: json.loads(p.read_text(encoding='utf-8')) for p in RAW.glob('*.receipt.json')}
    counts = {'cell_lines_checked': len(line_annotations), 'cell_lines_with_accession': sum(bool(r['accession']) for r in line_annotations),
              'cell_lines_without_accession': sum(not r['accession'] for r in line_annotations),
              'cell_types_checked': len(type_annotations), 'cell_types_with_reference': sum(bool(r['references']) for r in type_annotations)}
    payload = {'stage': 'Owner-authorized full vocabulary reference annotation; no discovery or eligibility filtering',
               'retrieval_date': '2026-10-01', 'cache_ref': str(CACHE.relative_to(ROOT)), 'cache_sha256': initial_hash,
               'tool_version': 'annotate_orcs_vocabularies.py v1', 'ontology_versions': versions,
               'cellosaurus_version': re.search(r'Version: ([^\n]+)', (RAW / 'cellosaurus.txt').read_text(encoding='utf-8')[:3000]).group(1),
               'source_label_conflicts': label_conflicts,
               'reference_receipts': receipts, 'counts': counts, 'cell_lines': line_annotations, 'cell_types': type_annotations,
               'selected_cellosaurus_evidence': selected, 'selected_ontology_evidence': selected_terms}
    (FOLDER / 'annotations.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    assert initial_hash == hashlib.sha256(CACHE.read_bytes()).hexdigest()
    print(json.dumps(counts), flush=True)
    print('Unmatched cell lines:', json.dumps([r['value'] for r in line_annotations if not r['accession']]), flush=True)

if __name__ == '__main__':
    main()
