"""CLI bridge for the approved browser library collector and offline exports.

Preparation normalizes publication inputs. Parsing receives transient response
bytes on stdin. Export uses saved selected records and the owner's registered
template. Network and login control belong to the Node browser controller.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from .enrichment_export import export_registered
from .enrichment_indices import DEFAULT_REGISTRY, assign_indices, native_key
from .library_content import extract, normalize_doi, repository_references, video_material

ROOT=Path(__file__).resolve().parents[2]
TEMPLATE=ROOT/'data/templates/Library-Enrichment-Template.xlsx'


def save(path, value):
    """Atomically checkpoint machine data into a collector-owned path."""
    path=Path(path);temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temporary.replace(path)


def prepare(source, registry, template=TEMPLATE):
    """Normalize selected publications without querying or changing identities.

    Parameters
    ----------
    source, registry, template : Path
        Publication JSON, existing publication registry, and registered template.

    Returns
    -------
    dict
        Bound input manifest, including publications without a DOI.
    """
    source,registry,template=map(Path,(source,registry,template))
    raw=json.loads(source.read_bytes()); records=raw.get('publications',[]) if isinstance(raw,dict) else raw
    mapping=json.loads(registry.read_bytes());by_id={str(r.get('ORCS Publication ID')):r for r in mapping};by_pmid={str(r['PMID']):r for r in mapping if r.get('PMID')}
    publications=[]
    for item in records:
        item=item.get('publication',item)
        known=by_id.get(str(item.get('PUBLICATION_ID') or item.get('ORCS Publication ID'))) or by_pmid.get(str(item.get('PMID'))) or {}
        index=item.get('Publication Index') or known.get('Publication index')
        if not index:raise ValueError('Each input needs a Publication Index or registry match')
        if known and item.get('Publication Index') and index!=known['Publication index']:raise ValueError('Publication registry identity conflict')
        if known and known.get('PMID') and item.get('PMID') and str(known['PMID'])!=str(item['PMID']):raise ValueError('Registry PMID conflict')
        if item.get('DOI') and not re.fullmatch(r'10\.\d{4,9}/\S+',normalize_doi(item['DOI'])):raise ValueError('Invalid DOI for '+index)
        publications.append({'Publication Index':index,'DOI':normalize_doi(item.get('DOI')),'PMID':str(item.get('PMID') or ''),
                             'Title':item.get('Title') or item.get('TITLE') or item.get('Publication Title') or '',
                             'Journal':item.get('Journal') or item.get('JOURNAL') or ''})
    if not publications or len({p['Publication Index'] for p in publications})!=len(publications):raise ValueError('Empty or duplicate publication input')
    registration=json.loads(template.with_suffix('.manifest.json').read_bytes())
    digest=hashlib.sha256(template.read_bytes()).hexdigest()
    if registration['sha256']!=digest:raise ValueError('Registered template hash mismatch')
    return {'schema':'library-input/1','publications':sorted(publications,key=lambda p:p['Publication Index']),
            'source_path':str(source.resolve()),'publication_registry':str(registry.resolve()),
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'registry_sha256':hashlib.sha256(registry.read_bytes()).hexdigest(),
            'template':str(template.resolve()),'template_sha256':digest,
            'template_manifest_sha256':hashlib.sha256(template.with_suffix('.manifest.json').read_bytes()).hexdigest(),
            'content_parser_sha256':hashlib.sha256(Path(__file__).with_name('library_content.py').read_bytes()).hexdigest(),
            'content_rules':'native-sections/2-nonvideo'}


def alma_services(body):
    """Read article-delivery URLs from Alma XML, preserving service identities."""
    root=ET.fromstring(body)
    for node in root.iter():node.tag=node.tag.split('}')[-1]
    result=[]
    for service in root.iter('context_service'):
        fields={}
        for key in service.iter('key'):fields.setdefault(key.get('id'),[]).append(key.text or '')
        result.append({'service_id':service.get('context_service_id'),'service_type':service.get('service_type'),
                       'resolution_url':service.findtext('resolution_url'),'fields':fields})
    return result


def project(manifest, attempts, index_registry=DEFAULT_REGISTRY):
    """Project successful selected records into the four owner-approved tables.

    Parameters
    ----------
    manifest : dict
        Normalized input manifest. Every input remains a Publications row.
    attempts : list of dict
        Durable attempt ledger. Later failures never erase prior retained data.
    index_registry : Path or None
        Shared persistent resource-index registry, or deterministic fixture mode.

    Returns
    -------
    dict
        Four canonical tables plus internal provenance. No errors are columns.
    """
    rows={name:[] for name in ('Publications','Article Context','Supporting Materials','Repository References')}
    contexts=[];materials=[];repositories=[];sources=[]
    for pub in manifest['publications']:
        index=pub['Publication Index'];successful=[a for a in attempts if a['publication_index']==index and a.get('data',{}).get('doi_verified')]
        text_seen={};material_seen={}
        for attempt in successful:
            data=attempt['data'];source=data.get('source_url') or attempt.get('destination','')
            for p in data.get('context',[]):
                value=p['text'];key=native_key(pub['DOI'],value)
                if key in text_seen:continue
                text_seen[key]=True
                row={'Publication Index':index,'Content Type':p.get('native_type',''),'Section Heading':p['heading'],
                     'Text':value,'Source Format':p['source_format'],'_key':key}
                contexts.append(row);sources.append({'kind':'context','key':key,'publication_index':index,'source_url':p.get('source_url') or source,'source_sha256':p.get('source_sha256'),'native_id':p.get('native_id'),'ancestors':p.get('ancestors',[])})
                for ref in repository_references(value):repositories.append({'Publication Index':index,**ref,'_context':key})
            for m in data.get('materials',[]):
                # Apply the owner's video exclusion to inherited records as well
                # as new responses, preserving original checkpoint evidence.
                if video_material(m):continue
                key=native_key(pub['DOI'],m.get('url') or m.get('native_reference') or m.get('native_id') or m['description'])
                if key in material_seen:continue
                material_seen[key]=True
                materials.append({'Publication Index':index,'Label':m['label'],'Description':m['description'],
                                  'Native Reference':m.get('native_reference',''),'Native ID':m.get('native_id',''),
                                  'File Type':Path(m.get('url') or m.get('native_reference','')).suffix.lower(),
                                  'File URL':m.get('url',''),'_key':key})
                sources.append({'kind':'material','key':key,'publication_index':index,'source_url':m.get('source_url') or source,'source_sha256':m.get('source_sha256'),'native_id':m.get('native_id')})
                for ref in repository_references(' '.join([m['label'],m['description'],m.get('url','')])):repositories.append({'Publication Index':index,**ref,'_context':''})
        latest=successful[-1] if successful else {}
        rows['Publications'].append({**{k:pub[k] for k in ('Publication Index','Title','Journal','DOI')},
                                      'Hosting Platform':latest.get('platform',''),'Article URL':latest.get('destination','')})
    context_ids=assign_indices('LCTX',[r['_key'] for r in contexts],index_registry) if contexts else {}
    material_ids=assign_indices('LSUP',[r['_key'] for r in materials],index_registry) if materials else {}
    unique={}
    for r in repositories:
        key=native_key(r['Publication Index'],r['Repository'],r['Accession'] or r['Repository URL'])
        if key not in unique or r['_context']:unique[key]={**r,'_key':key}
    repo_ids=assign_indices('LREP',list(unique),index_registry) if unique else {}
    for r in contexts:rows['Article Context'].append({**{k:v for k,v in r.items() if k!='_key'},'Context Index':context_ids[r['_key']]})
    for r in materials:rows['Supporting Materials'].append({**{k:v for k,v in r.items() if k!='_key'},'Supporting Material Index':material_ids[r['_key']]})
    for r in unique.values():rows['Repository References'].append({**{k:v for k,v in r.items() if not k.startswith('_')},'Repository Reference Index':repo_ids[r['_key']],'Context Index':context_ids.get(r['_context'],'')})
    return {'schema_version':'library-enrichment/1','rows':rows,'provenance':sources}


def export_run(run_dir, output, index_registry=DEFAULT_REGISTRY):
    """Export saved enrichment and separate per-pass status into a new directory.

    Parameters
    ----------
    run_dir, output : Path
        Collector checkpoint directory and nonexisting export directory.
    index_registry : Path
        Persistent registry for resource IDs.

    Returns
    -------
    dict
        Export paths and independently checked table counts.
    """
    run_dir,output=Path(run_dir),Path(output)
    manifest=json.loads((run_dir/'manifest.json').read_bytes());state=json.loads((run_dir/'state.json').read_bytes())
    template=Path(manifest['template'])
    if hashlib.sha256(template.read_bytes()).hexdigest()!=manifest['template_sha256']:raise ValueError('Run template changed')
    if manifest.get('template_manifest_sha256') and hashlib.sha256(template.with_suffix('.manifest.json').read_bytes()).hexdigest()!=manifest['template_manifest_sha256']:raise ValueError('Run template mapping changed')
    if output.exists():raise FileExistsError(output)
    output.mkdir(parents=True)
    data=project(manifest,state['attempts'],index_registry);save(output/'database.json',data)
    workbook=output/'Library-Enrichment.xlsx';receipt=export_registered(template,workbook,data['rows'],overflow_sidecar=True)
    save(workbook.with_suffix('.manifest.json'),receipt)
    # This is application export code using the project's existing Excel dependency.
    # A wide status view derives from the normalized attempt ledger; user output
    # fields never need to change when another assisted pass is performed.
    from openpyxl import Workbook
    from openpyxl.styles import Font,PatternFill,Alignment
    from openpyxl.worksheet.table import Table,TableStyleInfo
    from openpyxl.utils import get_column_letter
    assisted=max((a.get('pass_number',0) for a in state['attempts'] if a.get('mode')=='assisted'),default=0)
    headers=['Publication Index','Title','Automatic Pass']+[f'Assisted Pass {i}' for i in range(1,assisted+1)]+['Current Outcome','Next Action','Retry Not Before (UTC)','Review Notes']
    book=Workbook();sheet=book.active;sheet.title='Publication Status';sheet.append(headers)
    labels={'retrieved':'Selected metadata retrieved','parser_incomplete':'Article verified; no qualifying sections/listings',
            'rate_limited':'Rate limited','authentication_expired':'Login renewal required','article_identity_unverified':'Article identity not verified',
            'challenge':'CAPTCHA or access challenge','library_route_unavailable':'Library article route unavailable',
            'unsupported_platform':'Unrecognized or nonpublisher destination','missing_doi':'Missing DOI','deferred':'Deferred',
            'request_error':'Request failed','access_block':'Publisher access block','skipped':'Skipped by user',
            'institutional_access_required':'Additional institutional selection or login required',
            'external_authentication_required':'External service login reached',
            'repository_redirect':'Repository route reached instead of publisher',
            'delivery_intermediary':'Aggregator or delivery intermediary reached',
            'connection_interrupted':'Connection interrupted','service_unavailable':'Service unavailable',
            'navigation_incomplete':'Article navigation incomplete','article_http_error':'Article HTTP error'}
    status_rows=[]
    for pub in manifest['publications']:
        attempts=[a for a in state['attempts'] if a['publication_index']==pub['Publication Index']]
        latest=attempts[-1] if attempts else {};outcome=latest.get('outcome','pending')
        automatic=next((a['outcome'] for a in reversed(attempts) if a['mode']=='automatic'),'Not attempted')
        passes=[next((a['outcome'] for a in reversed(attempts) if a['mode']=='assisted' and a['pass_number']==i),'') for i in range(1,assisted+1)]
        retry=latest.get('cooldown',{}).get('not_before_utc','')
        action='No access retry needed' if outcome=='retrieved' else 'Resume automatic pass' if outcome=='pending' else 'Supply DOI' if outcome=='missing_doi' else 'Remain deferred' if outcome=='deferred' else 'Renew login and resume' if outcome=='authentication_expired' else 'Review delivery route and platform adapter' if outcome=='unsupported_platform' else 'Assisted access or adapter review'
        if outcome=='rate_limited':
            active=bool(retry and datetime.fromisoformat(retry.replace('Z','+00:00'))>datetime.now(timezone.utc))
            exhausted=sum(a['outcome']=='rate_limited' and a['mode']=='automatic' for a in attempts)>=2
            action='Wait for cooldown' if active else 'Assisted retry after cooldown' if exhausted else 'Resume automatic pass'
        if outcome in ('institutional_access_required','external_authentication_required'):action='Review route or complete access in assisted pass'
        if outcome in ('connection_interrupted','service_unavailable'):action='Keep stopped; investigate connection or service before resuming'
        note='; '.join(latest.get('data',{}).get('notes',[]))
        row=[pub['Publication Index'],pub['Title'],labels.get(automatic,automatic)]+[labels.get(o,o) for o in passes]+[labels.get(outcome,outcome),action,retry,note]
        display=list(row)
        if retry:display[-2]=datetime.fromisoformat(retry.replace('Z','+00:00')).replace(tzinfo=None)
        sheet.append(display)
        if retry:sheet.cell(sheet.max_row,len(headers)-1).number_format='yyyy-mm-dd hh:mm:ss'
        status_rows.append(dict(zip(headers,row)))
    sheet.freeze_panes='C2';last=get_column_letter(len(headers));table=Table(displayName='LibraryStatus',ref=f'A1:{last}{sheet.max_row}');table.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=True);sheet.add_table(table)
    for c in sheet[1]:c.font=Font(name='Arial',bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='243C5A')
    for row in sheet.iter_rows(min_row=2):
        for c in row:c.alignment=Alignment(vertical='top',wrap_text=True)
    for i,h in enumerate(headers,1):sheet.column_dimensions[get_column_letter(i)].width=65 if h=='Title' else 48 if h=='Review Notes' else 35 if i>2 else 20
    book.save(output/'Library-Enrichment-Status.xlsx');save(output/'status.json',status_rows)
    result={'publications':len(manifest['publications']),'sheet_rows':receipt['sheet_rows'],'verified_cells':receipt['verified_cells'],'assisted_passes':assisted,'output':str(output)}
    save(output/'summary.json',result)
    return result


def main():
    """Dispatch one metadata bridge operation; stdout is UTF-8 JSON only."""
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    prep=commands.add_parser('prepare');prep.add_argument('--input',type=Path,required=True);prep.add_argument('--registry',type=Path,required=True);prep.add_argument('--template',type=Path,default=TEMPLATE)
    parse=commands.add_parser('parse');parse.add_argument('--publication',required=True);parse.add_argument('--address',required=True);parse.add_argument('--kind',choices=['html','xml','json'],default='html');parse.add_argument('--article-bound',action='store_true');parse.add_argument('--max-text',type=int,default=60000)
    commands.add_parser('alma')
    export=commands.add_parser('export');export.add_argument('--run-dir',type=Path,required=True);export.add_argument('--output',type=Path,required=True);export.add_argument('--index-registry',type=Path,default=DEFAULT_REGISTRY)
    args=parser.parse_args()
    if args.command=='prepare':result=prepare(args.input,args.registry,args.template)
    elif args.command=='alma':result=alma_services(sys.stdin.buffer.read(2_000_001))
    elif args.command=='parse':result=extract(sys.stdin.buffer.read(10_000_001),args.address,json.loads(args.publication),args.kind,args.article_bound,args.max_text)
    else:result=export_run(args.run_dir,args.output,args.index_registry)
    sys.stdout.buffer.write((json.dumps(result,ensure_ascii=False)+'\n').encode('utf-8'))


if __name__=='__main__':main()
