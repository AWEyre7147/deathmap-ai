"""Repair parser-only issues from the completed ORCS inventory; preserve original exports."""
import hashlib,json
from pathlib import Path
import deathmap_ai.biostudies_collection as b
from deathmap_ai.enrichment_export import export_registered
root=Path('data/orcs/biostudies-enrichment/run-20261030')
source=root/'database.json'
output=root/'BioStudies-Enrichment-Validated.xlsx'
if output.exists():raise SystemExit('Validated export already exists; refusing to overwrite it.')
d=json.loads(source.read_text(encoding='utf-8'))
transport=b.Transport(root)
for number,record in enumerate(d['publications']):
    if record['issues']:
        updated=b.discover(record['publication'],transport)
        d['publications'][number]=updated
        print('Rechecked',record['publication']['Publication Index'],flush=True)
accessions=sorted({o['accession'] for p in d['publications'] for o in p['observations']})
retrieval_issues=[]
for accession in accessions:
    record=d['studies'].get(accession)
    if not record or record['issues']:
        try:
            d['studies'][accession]=b.study_record(accession,transport)
            print('Validated',accession,flush=True)
        except (ValueError,OSError) as error:
            retrieval_issues.append({'accession':accession,'error':str(error)})
d['issues']=retrieval_issues
for publication in d['publications']:
    p=publication['publication']
    for observation in publication['observations']:
        if observation['accession'] in d['studies']:
            observation.update(b.association(p,d['studies'][observation['accession']]))
    d['issues'].extend({'Publication Index':p['Publication Index'],**i} for i in publication['issues'])
for accession,study in d['studies'].items():
    d['issues'].extend({'accession':accession,**i} for i in study['issues'])
b.save(root/'validation-requests.json',transport.requests)
if d['issues']:
    b.save(root/'validation-issues.json',d['issues'])
    raise SystemExit('Validation still has issues; original exports preserved. See validation-issues.json.')
d['rows']=b.project(d,b.DEFAULT_REGISTRY)
d['status']='complete'
d['collector_sha256']=b.digest(Path(b.__file__).read_bytes())
d['parent_database_sha256']=b.digest(source.read_bytes())
d['index_registry_sha256']=b.digest(Path(b.DEFAULT_REGISTRY).read_bytes())
d['summary']={'publications':len(d['publications']),'studies':len(d['studies']),
 'publications_with_studies':sum(any(o['accession'] in d['studies'] for o in p['observations']) for p in d['publications']),
 'publications_with_file_records':sum(any(o['accession'] in d['studies'] and d['studies'][o['accession']]['files'] for o in p['observations']) for p in d['publications']),
 'distinct_files':len({r['BioStudies Index'] for r in d['rows']['Supplementary Files']}),
 'publication_file_rows':len(d['rows']['Supplementary Files']),'issues':0,
 'requests_this_execution':len(transport.requests),'verified_reused_responses':transport.reused,'supplemental_downloads':0}
b.save(root/'database-validated.json',d)
b.save(root/'summary-validated.json',d['summary'])
receipt=export_registered(b.TEMPLATE,output,d['rows'],overflow_sidecar=True)
receipt['source_database_sha256']=b.digest((root/'database-validated.json').read_bytes())
b.save(output.with_suffix('.manifest.json'),receipt)
print(json.dumps(d['summary'],indent=2),flush=True)
print('Workbook:',output.resolve(),flush=True)
