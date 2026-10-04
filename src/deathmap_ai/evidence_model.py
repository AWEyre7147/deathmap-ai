"""V6 evidence projection: compact reviewer rows and lossless JSONL provenance.

Observations are supplied by resource adapters, never retrieved here. Grouping
preserves source/entity/basis/status boundaries; references remain independent
of discovery records. Existing v01 projections are not rewritten.
"""
import copy
import hashlib
import json
from pathlib import Path

VERSION = 'evidence-model-v6.0'
HEADERS = ['evidence_id', 'supports_entity_type', 'supports_entity_id', 'claim',
           'fields_supported', 'source_name', 'source_link', 'supporting_value',
           'supporting_value_truncated', 'evidence_basis', 'evidence_status',
           'reviewer_check', 'reviewer_note']
BASES = {'structured_field', 'text_quote', 'text_mined_identifier', 'inferred',
         'reviewer_assertion', 'reference_lookup'}
STATUSES = {'direct', 'indirect', 'inferred', 'conflicting', 'unresolved'}


def canonical(value):
    """Serialize preserved evidence deterministically, without dropping fields."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def display_value(value, target=300):
    """Abbreviate the reviewer display only; the ledger retains the full value."""
    if target < 3:
        raise ValueError('Display target must accommodate the […] marker')
    text = value if isinstance(value, str) else canonical(value)
    return (text, False) if len(text) <= target else (text[:target-3] + '[…]', True)


def v6_allowed(profile_id, profile_version, profile_schema=None):
    """Allow later outputs and the owner-authorized new CRISPR pilot family."""
    return profile_version >= 2 or (profile_schema == 'deathmap-orcs-pilot-profile/1.0' and
        profile_id == 'orcs-crispr-biological-classes-pilot-v01')


def build_evidence(observations, *, run_id, profile_id, profile_version, tool=None, profile_schema=None):
    """Return Evidence rows and ledger entries for v02-or-later observations.

    Each observation has source metadata, raw_record, one supports entity with
    fields, a claim, supporting_value, basis/status, and optional transformations
    and annotation_targets. Duplicate observations coalesce without losing their
    individual provenance. Conflicting/inferred observations never merge into
    direct ones. Cell-line annotation targets are kept solely in the ledger.
    """
    if not v6_allowed(profile_id,profile_version,profile_schema):
        raise ValueError('V6 starts with v02; v01 conversion needs separate authorization')
    groups = {}
    for original in observations:
        o = copy.deepcopy(original)
        source = o['source']; support = o['supports']
        basis, status = o['evidence_basis'], o['evidence_status']
        if basis not in BASES or status not in STATUSES:
            raise ValueError('Unsupported evidence basis/status')
        if basis == 'inferred' and status not in {'inferred', 'conflicting', 'unresolved'}:
            raise ValueError('An inferred claim cannot be direct')
        if not source.get('native_record_id') or not support.get('entity_id'):
            raise ValueError('Missing source or entity identity')
        if source.get('name') == 'Cellosaurus':
            if basis != 'reference_lookup' or support['entity_type'] != 'cell_line':
                raise ValueError('Cellosaurus must be separate cell_line reference evidence')
            if support['entity_id'] != source['native_record_id'] or not support['entity_id'].startswith('CVCL_'):
                raise ValueError('Cell-line identity must be its Cellosaurus accession')
        if not isinstance(o['claim'], str) or not o['claim'].strip():
            raise ValueError('Evidence requires a readable claim')
        # Native IDs are namespaced by resource/type to avoid merging a screen
        # and publication whose native numeric identifiers happen to coincide.
        key = (source['name'], source.get('type'), source['native_record_id'],
               support['entity_type'], support['entity_id'], basis, status)
        groups.setdefault(key, []).append(o)
    rows, ledger = [], []
    for key, members in sorted(groups.items(), key=lambda pair: canonical(pair[0])):
        eid = 'EVI-' + hashlib.sha256(canonical(key).encode()).hexdigest()[:24]
        fields = sorted({f for m in members for f in m['supports']['fields']})
        claims = list(dict.fromkeys(m['claim'] for m in members))
        values = list({canonical(m['supporting_value']):m['supporting_value'] for m in members}.values())
        full = values[0] if len(values) == 1 else values
        display, truncated = display_value(full)
        if len(claims)==1:claim=claims[0]
        elif key[5]=='inferred':claim=f"Inferred from {key[0]} record {key[2]} for {key[3]} {key[4]}, as detailed in the ledger."
        else:claim=f"{key[0]} provides the observations for {key[3]} {key[4]} in the listed fields."
        sources = list({canonical(m['source']):m['source'] for m in members}.values())
        entry = {'evidence_id':eid, 'run_id':run_id, 'profile_id':profile_id,
                 'supports':[{'entity_type':key[3], 'entity_id':key[4], 'fields':fields}],
                 'claim':claim, 'evidence_basis':key[5], 'evidence_status':key[6],
                 'source':sources[0], 'source_observations':sources,
                 'supporting_value_full':full, 'observations':members,
                 'tool':copy.deepcopy(tool or {'name':VERSION}),
                 'annotation_targets':list({canonical(t):t for m in members for t in m.get('annotation_targets', [])}.values())}
        ledger.append(entry)
        rows.append(dict(zip(HEADERS, [eid,key[3],key[4],claim,'; '.join(fields),
                    key[0],sources[0].get('native_url'),display,truncated,key[5],key[6],None,None])))
    return rows, ledger


def write_ledger(path, entries):
    """Write a new UTF-8 JSONL ledger; refuse to overwrite historical evidence."""
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        for entry in entries:
            stream.write(canonical(entry) + '\n')


def validate_evidence(rows, ledger):
    """Check one-to-one workbook/ledger IDs, display flags, and source separation."""
    index = {e['evidence_id']:e for e in ledger}
    if len(index) != len(ledger) or len({r['evidence_id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate evidence identity')
    if {r['evidence_id'] for r in rows} != set(index):
        raise ValueError('Workbook/ledger evidence IDs differ')
    for row in rows:
        e = index[row['evidence_id']]
        value, flag = display_value(e['supporting_value_full'])
        if row['supporting_value'] != value or row['supporting_value_truncated'] != flag:
            raise ValueError('Display differs from full ledger evidence')
        if row['source_name'] == 'Cellosaurus' and (row['evidence_basis'] != 'reference_lookup' or row['supports_entity_type'] != 'cell_line'):
            raise ValueError('Invalid Cellosaurus evidence boundary')
        for field in ('claim','evidence_basis','evidence_status'):
            if row[field] != e[field]:
                raise ValueError('Workbook claim differs from ledger')
        support=e['supports'][0]
        if (row['supports_entity_type'],row['supports_entity_id']) != (support['entity_type'],support['entity_id']) or row['fields_supported'] != '; '.join(support['fields']):
            raise ValueError('Workbook support target differs from ledger')
        if row['source_name'] != e['source']['name'] or row['source_link'] != e['source'].get('native_url'):
            raise ValueError('Workbook source differs from ledger')
    return True
