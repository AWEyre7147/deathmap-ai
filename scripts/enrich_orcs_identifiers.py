"""Owner-authorized identifier enrichment of the shared ORCS publication catalog.

Archives catalog bytes before updating missing DOI/PMID/PMCID values. Resolution
is independent of ORCS and reusable by future resources. Existing values and
conflicts remain intact; sources are cached for offline replay. Does not rerun
searches or replace output directories automatically.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from deathmap_ai.publication_identifiers import Resolver
from deathmap_ai.orcs_publications import export_csv


def enrich(root,archive):
    """Back up catalog files, resolve identifiers, and update JSON/CSV/manifest."""
    root=Path(root).resolve();archive=Path(archive).resolve()
    folder=root/'data/orcs';rows=json.loads((folder/'publication-index.json').read_text(encoding='utf-8'))
    target=archive/'publication-identifiers'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    target.mkdir(parents=True);backups=[]
    for name in ['publication-index.json','publication-metadata.csv','publication-index.manifest.json']:
        path=folder/name;shutil.copyfile(path,target/name)
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if hashlib.sha256((target/name).read_bytes()).hexdigest()!=digest:raise ValueError('Backup mismatch')
        backups.append({'file':name,'sha256':digest})
    eligible=[row for row in rows if any(row.get(k) for k in ['PMID','DOI','PMCID'])]
    results=Resolver(root/'data/publication-identifiers/cache').resolve([{k.lower():row.get(k) for k in ['PMID','DOI','PMCID']} for row in eligible])
    for row in rows:row.setdefault('PMCID',None);row.setdefault('IDENTIFIER_ENRICHMENT',{})
    for row,result in zip(eligible,results):
        added=list(row.get('IDENTIFIER_ENRICHMENT',{}).get('added_fields',[]))
        for key,value in result['identifiers'].items():
            if not row.get(key.upper()) and value:row[key.upper()]=value;added.append(key.upper())
        row['IDENTIFIER_ENRICHMENT']={'added_fields':added,'resolution':result}
        if result['status']=='conflicting':row.setdefault('REVIEW_ISSUES',[]).append('Conflicting external publication identifiers; existing values preserved')
    (folder/'publication-index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    export_csv(folder/'publication-metadata.csv',rows)
    manifest=json.loads((folder/'publication-index.manifest.json').read_text(encoding='utf-8'))
    manifest['identifier_enrichment']={'tool':'publication_identifiers v1','retrieved_at':datetime.now(timezone.utc).isoformat(),'backup_directory':str(target),'backup_files':backups,'records_attempted':len(results),'status_counts':{s:sum(x['status']==s for x in results) for s in ['resolved','partial','unresolved','conflicting']}}
    manifest['field_names']=list(rows[0]);manifest['fields_populated']={k:sum(bool(row.get(k)) for row in rows) for k in rows[0]}
    for name in ['publication-index.json','publication-metadata.csv']:
        p=folder/name;manifest['files'][name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    (folder/'publication-index.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest['identifier_enrichment'],indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--archive',type=Path,required=True);args=p.parse_args();enrich(args.root,args.archive)
