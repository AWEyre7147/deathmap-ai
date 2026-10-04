"""Apply owner-approved workbook IDs and field mappings to offline projections.

Sequential IDs follow canonical row order and keep a reversible old/new registry.
Every reference is rewritten together. FULL_SIZE is copied under the owner's
output convention; this transformation does not independently validate library
size. Catalogs, native identifiers and historical output files remain unchanged.
"""
import copy
import re

VERSION = 'orcs-publication-enrichment-v1.1'


def revise(projection, native_screens, starting_workbook):
    """Return revised JSON with ID registry, evidence column and change receipts.

    Inputs are canonical projection rows, native screen dictionaries and read-only
    workbook rows. Duplicate identities, broken evidence links and invalid count
    values fail explicitly. Existing short IDs are reused when revising again.
    """
    maps = {}; registry = []
    for sheet, key, prefix, width in [('Publications','publication_id','PUB',4),
                                     ('Screens','screen_id','SCR',4),
                                     ('Sources & Evidence','evidence_id','EVI',5)]:
        rows = projection['sheets'][sheet]; ids = [row[key] for row in rows]
        if len(set(ids)) != len(ids): raise ValueError('Duplicate migration identity: ' + sheet)
        reserved = {x for x in ids if re.fullmatch(prefix+r'-\d{'+str(width)+r'}',x)}
        counter = 1
        for old in ids:
            if old in reserved: new = old
            else:
                while f'{prefix}-{counter:0{width}d}' in reserved: counter += 1
                new = f'{prefix}-{counter:0{width}d}'; reserved.add(new); counter += 1
            maps[old] = new; registry.append({'entity_type':sheet,'old_id':old,'new_id':new})
    pattern = re.compile(r'(?<![A-Za-z0-9_-])(?:'+ '|'.join(re.escape(x) for x in sorted(maps,key=len,reverse=True))+r')(?![A-Za-z0-9_-])')

    def replace(value):
        if isinstance(value,str): return pattern.sub(lambda m:maps[m[0]],value)
        if isinstance(value,list): return [replace(x) for x in value]
        if isinstance(value,dict): return {maps.get(k,k):replace(v) for k,v in value.items()}
        return value

    p = replace(copy.deepcopy(projection)); p['version'] = VERSION
    p['id_migration'] = registry
    headers = p['headers']['Publications']
    source_field = 'retrival_sources' if 'retrival_sources' in headers else 'retrieval_sources'
    if 'evidence_id_link' not in headers: headers.insert(headers.index(source_field)+1,'evidence_id_link')
    eids = {r['evidence_id'] for r in p['sheets']['Sources & Evidence']}
    for row in p['sheets']['Publications']:
        text = row.get(source_field) or ''
        identifiers = re.findall(r'evidence_id=(EVI-\d{5})',text)
        existing = re.findall(r'EVI-\d{5}',row.get('evidence_id_link') or '')
        identifiers = list(dict.fromkeys(existing+identifiers))
        if any(x not in eids for x in identifiers): raise ValueError('Publication evidence link missing')
        row['evidence_id_link'] = '; '.join(identifiers) or None
        row[source_field] = re.sub(r';?\s*evidence_id=EVI-\d{5}', '',text)
    si = {r['SCREEN_ID']:r for r in native_screens}
    for row in p['sheets']['Screens']:
        native = p['roles'][row['screen_id']]['SCREEN_ID']; value = si[native].get('FULL_SIZE')
        if value not in (None,'','-'):
            if not str(value).isdigit(): raise ValueError('FULL_SIZE is not a nonnegative integer: ' + native)
            row['library_gene_count_reported'] = int(value)
        else: row['library_gene_count_reported'] = None
        p['cell_audit'].append({'sheet':'Screens','id':row['screen_id'],'field':'library_gene_count_reported',
            'status':'added' if value not in (None,'','-') else 'unresolved','proposed':row['library_gene_count_reported'],
            'source_locator':'data/orcs/screen-index.json; SCREEN_ID='+native+'; FULL_SIZE',
            'transformation':'Owner-approved FULL_SIZE output mapping, 2026-10-04; source result-size meaning retained; no independent library validation'})
    # Changed cells are explicit, so workbook preservation permits only the
    # requested migration, provenance separation and field mapping.
    p['approved_changes'] = []
    for sheet, before in starting_workbook.items():
        key = before['headers'][0]; after = {r[key]:r for r in p['sheets'][sheet]}
        for row in before['rows']:
            identity = maps.get(row[key],row[key]); target = after[identity]
            for field, value in row.items():
                new = target.get(field)
                if field=='retrieved_at': continue
                if new != value and not (new in (None,'') and value in (None,'')):
                    p['approved_changes'].append({'sheet':sheet,'id':identity,'field':field,'retained':value,'value':new,
                        'reason':'Owner revision or retained-prefix provenance append'})
    p['mapping']['owner_revision'] = {'authority':'Owner explicit request, 2026-10-04','sequential_ids':'Canonical row order; retained in id-migration.json',
        'evidence_id_link':'Immediately right of historical retrival_sources; publication-level evidence IDs',
        'library_gene_count_reported':'FULL_SIZE -> integer under owner-approved mapping; not independently verified library size'}
    return p
