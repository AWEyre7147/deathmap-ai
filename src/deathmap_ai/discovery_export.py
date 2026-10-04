"""Evidence-backed projection to the seven reference tables; no text extraction.

All reference columns are emitted, including deferred curator fields. Native
record objects, publications, and ORCS screens retain distinct identities. Exact
structured publication identifiers may join publications; they never generate
screen–dataset links. Native literature records remain explicitly distinguished.
"""
import copy
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from deathmap_ai.discovery_v02 import VERSION, read, rid, route
from deathmap_ai.omicsdi import utc_now
from deathmap_ai.resource_migration import write_json, digest
from deathmap_ai.shared_search import orcs_package

SCHEMA = json.loads(Path(__file__).with_name('reference_schema.json').read_text(encoding='utf-8'))
TABLES = {'Publications':'publications','Screen Groups':'screen_groups','Screens':'screens','Datasets':'datasets',
          'Screen-Dataset Links':'screen_dataset_links','Sources & Evidence':'sources_evidence','Discovery Resources':'discovery_resources'}
DEFER = {'curation_status','attribution_status','evidence_status','evidence_text_summary'}


def stable(prefix,value):
    """Return a deterministic opaque entity ID from a typed identity value."""
    return prefix+'-'+hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:20]


def values(value):
    """Flatten only arrays, preserving strings and objects without prose parsing."""
    if value is None or value == '' or value == '-': return []
    return value if isinstance(value,list) else [value]


def unique(items):
    """Retain distinct native values in first-observed order, including objects."""
    result=[]
    for item in items:
        if item not in result:result.append(item)
    return result


def scalar(items):
    """Represent absence by null, a singleton directly, and multiplicity by array."""
    items=unique(items)
    return None if not items else items[0] if len(items)==1 else items


def blank(table,source):
    """Retain every reference field and explicit population state, even if empty."""
    fields=SCHEMA['tables'][table]['fields']
    row={f['key']:None for f in fields}
    row['_sources']=[source];row['_field_evidence']={}
    row['_field_status']={f['key']:('deliberately_deferred' if f.get('population_class')=='reviewer_entered' or '_curated' in f['key'] or f['key'] in DEFER else 'unavailable') for f in fields}
    return row


def put(row,field,value,evidence,path,transformation='direct structured field'):
    """Preserve distinct source values as arrays and explicitly flag conflicts."""
    if field not in row or row['_field_status'][field]=='deliberately_deferred' or value is None or value==[] or value=='':return
    old=values(row[field]);new=values(value)
    combined=unique(old+new)
    multiple = field in ('source_evidence_ids','publication_id','retrieval_sources','author_list_reported','organism_reported')
    # Entity primary keys remain scalar; relationship columns carry arrays.
    multiple = multiple and not (field == 'publication_id' and 'title_original' in row and 'pmid' in row)
    row[field]=combined if multiple else scalar(combined)
    conflict = not multiple and old and any(v not in old for v in new)
    row['_field_status'][field]='conflicting' if conflict or row['_field_status'][field]=='conflicting' else 'populated'
    ref={'evidence_id':evidence,'native_path':path,'transformation':transformation}
    row['_field_evidence'].setdefault(field,[])
    if ref not in row['_field_evidence'][field]:row['_field_evidence'][field].append(ref)


def identifiers(metadata):
    """Recognize publication IDs only in named structured fields, never prose.

    One surrounding bracket pair is removed from a wholly numeric PMID value
    (observed GEO shape). DOI URL/prefix removal and case folding are identity
    normalization only; complete original metadata stays in source_records.
    """
    ids=[];cross=metadata.get('cross_references',{}) or {};additional=metadata.get('additional',{}) or {}
    for container,prefix in ((cross,'cross_references'),(additional,'additional')):
        if not isinstance(container,dict):continue
        for key,value in container.items():
            kind=key.casefold()
            if kind in ('pubmed','pmid'):kind='pmid'
            elif kind not in ('doi','pmcid'):continue
            for original in values(value):
                if not isinstance(original,str):continue
                normalized=original.strip()
                if kind=='pmid':
                    if re.fullmatch(r'\[\d+\]',normalized):normalized=normalized[1:-1]
                    if not normalized.isdigit():continue
                if kind=='doi':
                    normalized=re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)','',normalized,flags=re.I).casefold()
                    if not re.fullmatch(r'10\.\d{4,9}/\S+',normalized):continue
                if kind=='pmcid':
                    normalized=normalized.upper()
                    if not re.fullmatch(r'PMC\d+',normalized):continue
                item={'kind':kind,'value':normalized,'original':original,'path':prefix+'.'+key}
                if item not in ids:ids.append(item)
    return ids


def omics_views(record):
    """Separate compatible mapping views from retained conflicting detail evidence."""
    views=[('search_observations['+str(i)+'].metadata',o['metadata']) for i,o in enumerate(record['search_observations'])]
    if record.get('detail_metadata') and record.get('detail_parse_status')=='parsed':
        views.append(('detail_metadata',record['detail_metadata']))
    return views


def source_records(state):
    """Keep all native search and detail fields, including conflicts and protocols."""
    return [{'source_record_id':r['record_id'],'native_metadata':r,'provenance':{'reuse_origin':r['reuse_origin'],
        'original_retrieved_at':r['retrieved_at'],'historical_detail_allowance_band':r.get('detail_allowance_band'),
        'historical_detail_retrieval_ordinal':r.get('detail_retrieval_ordinal')}} for r in state['records'].values()]


def build(root,state):
    """Construct resource outputs and entity tables entirely from saved metadata."""
    out=root/'outputs'/VERSION;tables={name:[] for name in TABLES.values()};issues=[]
    omics=source_records(state)
    orcs_sources=[];orcs_candidates=[];orcs_hits=[];orcs_info={};orcs_issues=[]
    if state['routing']['orcs']:
        orcs_sources,orcs_candidates,orcs_hits,orcs_issues,orcs_info=orcs_package(root/'outputs/orcs/cache',root/'outputs/orcs'/VERSION)
        # Native screen identity is stable across versions, while the package
        # context and provenance state that the full index was searched again.
    candidates={r['record_id']:r for r in state['records'].values()}
    contexts=[]
    for key,record in state['records'].items():
        views=omics_views(record);ids=[]
        for path,m in views:ids.extend({**i,'path':path+'.'+i['path']} for i in identifiers(m))
        contexts.append({'resource':'OmicsDI','key':key,'record':record,'views':views,'ids':ids})
    orcs_by_id={s['source_record_id']:s for s in orcs_sources}
    for c in orcs_candidates:
        row=orcs_by_id[c['record_id']]['native_metadata'];ids=[]
        if str(row.get('SOURCE_TYPE','')).casefold()=='pubmed' and str(row.get('SOURCE_ID','')).isdigit():
            ids=[{'kind':'pmid','value':str(row['SOURCE_ID']),'original':row['SOURCE_ID'],'path':'SOURCE_ID'}]
        contexts.append({'resource':'ORCS','key':row['SCREEN_ID'],'record':row,'views':[('',row)],'ids':ids,'candidate':c})
    # Union only unambiguous singleton identifier types within a native record.
    # Multiple PMIDs are separate associations; a list of DOIs is not positionally
    # paired with a list of PMIDs or titles.
    parent={}
    def find(x):
        parent.setdefault(x,x)
        if parent[x]!=x:parent[x]=find(parent[x])
        return parent[x]
    def union(a,b):
        x,y=find(a),find(b)
        if x!=y:
            members=[n for n in parent if find(n) in (x,y)]
            kinds=defaultdict(set)
            for kind,value in members:kinds[kind].add(value)
            if any(len(v)>1 for v in kinds.values()):
                issues.append({'type':'conflicting_publication_identifiers','identifiers':members,'action':'not merged'})
                return
            parent[max(x,y)]=min(x,y)
    for ctx in contexts:
        by=defaultdict(set)
        for i in ctx['ids']:by[i['kind']].add(i['value']);find((i['kind'],i['value']))
        if by and all(len(v)==1 for v in by.values()):
            nodes=[(k,next(iter(v))) for k,v in by.items()]
            for node in nodes[1:]:union(nodes[0],node)
    components=defaultdict(list)
    for node in list(parent):components[find(node)].append(node)
    pubs={}
    def pub_for(node):
        group=components[find(node)];canonical=min(group,key=lambda p:({'pmid':0,'doi':1,'pmcid':2}[p[0]],p[1]))
        return stable('publication',canonical)
    for ctx in contexts:
        resource=ctx['resource'];record=ctx['record'];key=ctx['key']
        eid=stable('evidence',[resource,key]);ctx['eid']=eid
        ev=blank('Sources & Evidence',resource)
        nativeid=record['native_record_id'] if resource=='OmicsDI' else record['SCREEN_ID']
        sourceid=record['record_id'] if resource=='OmicsDI' else ctx['candidate']['record_id']
        retrieved=record['retrieved_at'] if resource=='OmicsDI' else ctx['candidate']['retrieved_at']
        for field,value in {'evidence_id':eid,'source_type_normalized':'resource_metadata','source_name':resource,
                'native_record_id':nativeid,'retrieved_at':retrieved,'retrieval_method':'cached_and_fresh_metadata' if resource=='OmicsDI' else 'cached_index_literal_search',
                'tool_or_package':'deathmap-ai v02.1','source_locator':{'file':f'outputs/{resource.lower()}/{VERSION}/source_records.json','source_record_id':sourceid}}.items():
            put(ev,field,value,eid,'provenance','source provenance or generated stable identifier')
        ev['_native_descriptions_and_protocols']=[{'path':path,'metadata':m} for path,m in ctx['views']]
        tables['sources_evidence'].append(ev)
        by=defaultdict(list)
        for i in ctx['ids']:by[i['kind']].append(i)
        anchor='pmid' if by['pmid'] else 'doi' if by['doi'] else 'pmcid'
        pubids=unique([pub_for((i['kind'],i['value'])) for i in by[anchor]])
        if len(by['pmid'])>1 and by['doi']:
            issues.append({'type':'unpaired_publication_identifiers','source_record_id':sourceid,'identifiers':ctx['ids']})
        # Explicit publication-title metadata can support one source-scoped
        # publication when no identifier exists. Titles never merge resources.
        titles=[]
        for path,m in ctx['views']:
            titles+=values((m.get('additional') or {}).get('pubmed_title'))
        if not pubids and len(unique(titles))==1:pubids=[stable('publication-source',[resource,key])]
        ctx['pubids']=pubids
        for pid in pubids:
            pub=pubs.setdefault(pid,blank('Publications',resource))
            if resource not in pub['_sources']:pub['_sources'].append(resource)
            put(pub,'publication_id',pid,eid,'structured publication identifiers','stable identifier from exact structured identifiers')
            for i in ctx['ids']:
                if pub_for((i['kind'],i['value']))==pid:
                    put(pub,i['kind'],i['value'],eid,i['path'],'documented identifier syntax normalization')
            put(pub,'retrieval_sources',resource,eid,'resource')
            # No positional title/author attribution across several publications.
            if len(pubids)==1:
                for path,m in ctx['views']:
                    additional=m.get('additional') or {}
                    for native,target in [('pubmed_title','title_original'),('pubmed_authors','author_list_reported'),('journal','journal_reported')]:
                        put(pub,target,additional.get(native),eid,path+'.additional.'+native)
                if resource=='ORCS':pub['_reported_citation']=record.get('AUTHOR')
            else:
                for f in ('title_original','author_list_reported','journal_reported'):
                    if pub[f] is None:pub['_field_status'][f]='unresolved'
        if resource=='OmicsDI':
            row=blank('Datasets',resource);did=stable('dataset-native',json.loads(key));ctx['entity_id']=did
            source=record['repository_original'];category='literature_record' if source=='biostudies-literature' else 'repository_project_record' if source=='project' else 'repository_dataset_record'
            row['_native_entity_category']=category;row['_independent_experimental_deposit']=None if category!='literature_record' else False
            for field,value,path in [('dataset_id',did,'native identity'),('accession_reported',record['native_record_id'],'native_record_id'),('repository_normalized',source,'repository_original')]:put(row,field,value,eid,path,'native identity preserved; no repository alias merge')
            row['publication_id']=pubids or None
            if pubids:
                row['_field_status']['publication_id']='populated';row['_field_evidence']['publication_id']=[{'evidence_id':eid,'native_path':'structured publication association','transformation':'array for all supported associations; no screen attribution'}]
            else:row['_field_status']['publication_id']='unresolved'
            for path,m in ctx['views']:
                put(row,'title_original',m.get('title',m.get('name')),eid,path+'.title/name')
                put(row,'description_reported',m.get('description'),eid,path+'.description')
                additional=m.get('additional') or {}
                for native,target in [('organism','organism_reported'),('scientific_name','organism_reported'),('species','organism_reported'),('study_type','experiment_type_reported'),('gds_type','experiment_type_reported'),('full_dataset_link','dataset_url')]:
                    put(row,target,additional.get(native),eid,path+'.additional.'+native)
                row.setdefault('_native_protocols',[])
                for native in ('sample_protocol','data_protocol'):
                    if additional.get(native):row['_native_protocols'].append({'evidence_id':eid,'path':path+'.additional.'+native,'value':additional[native]})
            if record.get('identifier_conflicts'):
                row['_identity_conflicts']=record['identifier_conflicts'];issues.append({'type':'detail_identity_conflict','dataset_id':did,'conflicts':record['identifier_conflicts']})
                row['_withheld_detail_mapping']=True
            put(row,'source_evidence_ids',[eid],eid,'source association')
            row['_unresolved_screen_link']=True;tables['datasets'].append(row)
        else:
            row=blank('Screens',resource);sid=stable('screen',['ORCS',key]);ctx['entity_id']=sid
            put(row,'screen_id',sid,eid,'SCREEN_ID','stable native screen identifier')
            if pubids:put(row,'publication_id',pubids,eid,'SOURCE_TYPE/SOURCE_ID','exact publication identifier association')
            else:row['_field_status']['publication_id']='unresolved'
            mapping={'SCREEN_NAME':'screen_name_reported','SCREEN_FORMAT':'screen_format_normalized','METHODOLOGY':'methodology_reported','ENZYME':'enzyme_reported','LIBRARY':'library_name_reported','LIBRARY_TYPE':'library_type_reported','CELL_LINE':'cell_line_reported','ORGANISM_OFFICIAL':'organism_reported','CONDITION_NAME':'condition_name_reported','CONDITION_DOSAGE':'condition_dosage_reported','DURATION':'duration_reported','PHENOTYPE':'phenotype_original','ANALYSIS':'statistical_analysis_reported'}
            for native,target in mapping.items():
                v=record.get(native)
                if v not in (None,'','-'):put(row,target, v.casefold() if native=='SCREEN_FORMAT' else v,eid,native,'case folding of source format label' if native=='SCREEN_FORMAT' else 'direct structured field')
            row['_field_status']['screen_group_id']='unresolved';row['_dataset_link_status']='unresolved'
            row['_source_screen_id']=key;row['_source_notes']=record.get('NOTES')
            put(row,'source_evidence_ids',[eid],eid,'source association');tables['screens'].append(row)
        put(ev,'supports_entity_type','dataset_native_record' if resource=='OmicsDI' else 'screen',eid,'native entity type')
        put(ev,'supports_entity_id',ctx['entity_id'],eid,'native identity')
        ev['_publication_ids']=pubids
    tables['publications']=list(pubs.values())
    pipeline=blank('Sources & Evidence','pipeline')
    for field,value in {'evidence_id':'pipeline-manifest','source_type_normalized':'software_provenance',
                        'source_name':'DeathMap-AI','source_locator':f'outputs/{VERSION}/manifest.json',
                        'retrieval_method':'offline projection','tool_or_package':'deathmap-ai v02.1'}.items():
        put(pipeline,field,value,'pipeline-manifest','manifest','software provenance')
    tables['sources_evidence'].append(pipeline)
    for resource in ('OmicsDI','ORCS'):
        row=blank('Discovery Resources',resource);eid='pipeline-manifest'
        relevant=[c for c in contexts if c['resource']==resource]
        nums={'publications_discovered':len({p for c in relevant for p in c['pubids']}),
              'datasets_discovered':sum(d['_native_entity_category']!='literature_record' for d in tables['datasets']) if resource=='OmicsDI' else 0,
              'screens_discovered':len(tables['screens']) if resource=='ORCS' else 0}
        vals={'resource_name':resource,'resource_type':'dataset index' if resource=='OmicsDI' else 'screen database',
              'programmatic_access':True,
              'authentication_required':False if resource=='OmicsDI' and any(e.get('status')=='received' for e in state['detail_attempts'].values()) else None,
              'access_method':'OmicsDI REST metadata; saved responses' if resource=='OmicsDI' else 'complete cached index',
              'queried_in_this_version':state['routing'][resource.lower()],
              'documentation_url':'https://www.omicsdi.org/help/api' if resource=='OmicsDI' else 'https://orcs.thebiogrid.org/',**nums}
        for f,v in vals.items():put(row,f,v,eid,'run manifest and output counts','software provenance or population count; not scientific correctness')
        tables['discovery_resources'].append(row)
    return tables,omics,(orcs_sources,orcs_candidates,orcs_hits,orcs_issues,orcs_info),issues


def validate(tables):
    """Check complete reference field coverage and all populated entity references."""
    ids={table:set() for table in TABLES.values()};idfields={'publications':'publication_id','datasets':'dataset_id','screens':'screen_id','screen_groups':'screen_group_id','screen_dataset_links':'link_id','sources_evidence':'evidence_id'}
    for sheet,table in TABLES.items():
        fields={f['key'] for f in SCHEMA['tables'][sheet]['fields']}
        for row in tables[table]:
            if not fields.issubset(row):raise ValueError('Missing reference fields: '+table)
            if table in idfields:
                identity=row[idfields[table]]
                if identity in ids[table]:raise ValueError('Duplicate entity identifier')
                ids[table].add(identity)
    targets={'publication_id':'publications','screen_group_id':'screen_groups','screen_id':'screens','dataset_id':'datasets','source_evidence_ids':'sources_evidence','evidence_source_id':'sources_evidence'}
    for table,rows in tables.items():
        for row in rows:
            for field,target in targets.items():
                if field==idfields.get(table):continue
                for value in values(row.get(field)):
                    if value not in ids[target]:raise ValueError('Dangling '+field)
            for evidence in row['_field_evidence'].values():
                for item in evidence:
                    if item['evidence_id'] not in ids['sources_evidence']:raise ValueError('Dangling field evidence')
            if row.get('supports_entity_id') is not None:
                target='datasets' if row['supports_entity_type']=='dataset_native_record' else 'screens'
                if row['supports_entity_id'] not in ids[target]:raise ValueError('Dangling supported entity')


def export(root,state,verify=False):
    """Deterministic offline exports using a saved transformation timestamp."""
    tables,omics,orcs,issues=build(root,state);validate(tables)
    out=root/'outputs'/VERSION
    manifest_path=out/'manifest.json'
    transformed=read(manifest_path)['transformed_at'] if verify else utc_now()
    def emit(path,value):
        encoded=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
        if verify:
            if path.read_text(encoding='utf-8')!=encoded:raise ValueError('Offline mismatch: '+str(path))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(encoded,encoding='utf-8')
    for table,rows in tables.items():emit(out/(table+'.json'),{'schema_version':'reference-v02','table':table,'records':rows})
    population={}
    for sheet,table in TABLES.items():
        population[table]={}
        for source in ('OmicsDI','ORCS','pipeline'):
            rows=[r for r in tables[table] if source in r['_sources']]
            population[table][source]={f['key']:dict(Counter(r['_field_status'][f['key']] for r in rows)) for f in SCHEMA['tables'][sheet]['fields']}
    emit(out/'field_population.json',{'interpretation':'Software population only, not scientific correctness; zero rows means no identified entities','tables':population})
    emit(out/'reference_mapping.json',SCHEMA)
    manifest={'version':VERSION,'transformed_at':transformed,'routing':state['routing'],'counts':{t:len(rows) for t,rows in tables.items()},
              'native_entity_categories':dict(Counter(r['_native_entity_category'] for r in tables['datasets'])),
              'new_detail_attempts':len(state['detail_attempts']),'reused_detail_receipts':89,
              'historical_within_allowance':50,'historical_excess':39,'search_stop_reasons':state['stop_reasons'],
              'issues':issues,'reference_sha256':SCHEMA['sha256'],'cached_live_mixture':True}
    emit(out/'manifest.json',manifest)
    od=root/'outputs/omicsdi'/VERSION
    emit(od/'source_records.json',{'records':omics})
    emit(od/'candidates.json',{'candidates':[{'record_id':r['record_id'],'candidate_type':'native_resource_record',
        'source_record_refs':[r['record_id']],'repository_original':r['repository_original'],'native_record_id':r['native_record_id'],
        'title':r['title_original'],'description':r['evidence_text_original'],'retrieved_at':r['retrieved_at'],
        'detail_retrieval_status':r['detail_retrieval_status'],'detail_parse_status':r['detail_parse_status'],
        'identifier_conflicts':r.get('identifier_conflicts',[]),'review_status':'unreviewed'} for r in state['records'].values()]})
    emit(od/'query_hits.json',{'hits':state['query_hits']})
    emit(od/'candidate_summary.json',{'candidates':len(omics),'query_hits':len(state['query_hits']), 'by_source':dict(Counter(r['repository_original'] for r in state['records'].values())),'review_status':'unreviewed'})
    emit(od/'issues.json',{'issues':state['issues']+issues+[{'type':'historical_cap_violation','receipts':89,'within_allowance':50,'excess':39,'ref':state['historical_state_ref']}]})
    refs=sorted(set([state['historical_state_ref']]+[p for q in state['queries'].values() for p in q['pages']]+[r['detail_response_ref'] for r in state['records'].values() if r.get('detail_response_ref')]))
    emit(od/'search_manifest.json',{'version':VERSION,'adapter_version':'v02.1','resource_version':None,'routing':state['routing'],'queries':state['queries_config'],'counts':{'native_records':len(omics),'query_hits':len(state['query_hits']),'new_detail_attempts':len(state['detail_attempts']),'new_details_received':sum(x['status']=='received' for x in state['detail_attempts'].values()),'reused_detail_receipts':89},
        'query_progress':{q:{k:v for k,v in data.items() if k not in ('keys','buffer')}|{'buffered_rows':len(data['buffer'])} for q,data in state['queries'].items()},
        'stop_reasons':state['stop_reasons'],'transformed_at':transformed,'mixed_cache_dates':True,'source_hashes':{ref:digest(root/ref) for ref in refs},
        'candidate_cap':state['candidate_cap'],'new_detail_attempt_cap':state['new_detail_attempt_cap'],'original_question':state['routing']['original_question']})
    sources,candidates,hits,errors,info=orcs;oc=root/'outputs/orcs'/VERSION
    for name,value in [('source_records',{'records':sources}),('candidates',{'candidates':candidates}),('query_hits',{'hits':hits}),('issues',{'issues':errors})]:emit(oc/(name+'.json'),value)
    emit(oc/'search_manifest.json',{'version':VERSION,'adapter_version':'v02.1','resource_version':None,'routing':state['routing'],'queried':state['routing']['orcs'],'transformed_at':transformed,'counts':{'source_records':len(sources),'candidates':len(candidates),'query_hits':len(hits)},
        'source_hashes':{ref:digest((oc/ref).resolve()) for ref in info.get('source_references',[])},**info})
    emit(oc/'candidate_summary.json',{'candidates':len(candidates),'query_hits':len(hits),'review_status':'unreviewed','candidate_cap':None})
    return manifest
