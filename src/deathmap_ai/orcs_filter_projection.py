"""Project ORCS filter evidence into the owner's existing entity-sheet schema.

Only reported publication identities and native screens become entities. No
screen group, repository dataset or exact dataset link is inferred from a paper.
Existing workbook identities and nonempty reviewer values take precedence.
"""
import hashlib
import json
from urllib.parse import quote
from openpyxl import load_workbook
from .orcs_filters import publication_key, VERSION

DIRECT = {'SCREEN_NAME':'screen_name_reported','METHODOLOGY':'methodology_reported',
 'ENZYME':'enzyme_reported','LIBRARY':'library_name_reported','LIBRARY_TYPE':'library_type_reported',
 'CELL_LINE':'cell_line_reported','ORGANISM_OFFICIAL':'organism_reported',
 'CONDITION_NAME':'condition_name_reported','CONDITION_DOSAGE':'condition_dosage_reported',
 'DURATION':'duration_reported','PHENOTYPE':'phenotype_original','ANALYSIS':'statistical_analysis_reported'}
# These narrowly defined crosswalks describe reported technology, not eligibility.
CROSSWALKS={'SCREEN_FORMAT':{'Pool':'pooled','Array':'arrayed'},
            'METHODOLOGY':{'Knockout':'CRISPR knockout'}}


def stable_id(kind, *identity):
    """Generate an order-independent namespace ID from the complete native identity."""
    digest=hashlib.sha256(json.dumps(identity,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()[:24]
    return f'DM-{kind}-{digest}'


def existing_rows(path):
    """Read workbook values without modifying it, retaining formulas and reviewer text."""
    workbook=load_workbook(path,data_only=False)
    result={}
    for sheet in workbook:
        values=list(sheet.values);headers=list(values[0])
        if len(set(headers))!=len(headers) or any(not isinstance(h,str) for h in headers):
            raise ValueError(f'Invalid headers: {sheet.title}')
        result[sheet.title]={'headers':headers,'rows':[dict(zip(headers,row)) for row in values[1:] if any(v is not None for v in row)]}
    return result


def merge_rows(existing, proposed, key):
    """Fill only empty existing fields; retain edits and expose conflicting values."""
    rows=[dict(x) for x in existing];index={};conflicts=[]
    for i,row in enumerate(rows):
        value=row.get(key)
        if value in (None,'') or value in index: raise ValueError(f'Ambiguous existing identity: {key}')
        index[value]=i
    for row in proposed:
        identity=row[key]
        if identity not in index:
            index[identity]=len(rows);rows.append(dict(row));continue
        target=rows[index[identity]]
        for field,value in row.items():
            if target.get(field) in (None,''): target[field]=value
            elif value not in (None,'') and target[field]!=value:
                conflicts.append({'id':identity,'field':field,'retained':target[field],'proposed':value})
    return rows,conflicts


def project(results, manifest, workbook_path):
    """Return entity rows plus exact crosswalks and evidence, resolving existing foreign keys."""
    existing=existing_rows(workbook_path)
    expected=['Publications','Screen Groups','Screens','Datasets','Screen-Dataset Links','Sources & Evidence','Discovery Resources']
    if any(s not in existing for s in expected): raise ValueError('Required entity sheet missing')
    pubs={};screens=[];evidence=[];native_ids={};pub_ids={}
    for row in existing['Publications']['rows']:
        for typ,field in [('pubmed','pmid'),('doi','doi')]:
            if row.get(field):
                key=(typ,str(row[field]))
                if key in pub_ids and pub_ids[key]!=row['publication_id']: raise ValueError('Duplicate publication identity')
                pub_ids[key]=row['publication_id']
    # Native IDs are preserved in our explicit notes token. Unknown legacy rows
    # remain untouched instead of being guessed from a similar screen name.
    import re
    for row in existing['Screens']['rows']:
        match=re.search(r'(?:^|; )ORCS SCREEN_ID=([^;]+)',str(row.get('screen_notes') or ''))
        if match:
            if match[1] in native_ids and native_ids[match[1]]!=row['screen_id']: raise ValueError('Duplicate ORCS screen identity')
            native_ids[match[1]]=row['screen_id']
    selected={x['SCREEN_ID']:dict(x) for x in results['publication_siblings']}
    for x in results['unresolved_screens']:
        if x['SCREEN_ID'] in selected: selected[x['SCREEN_ID']]['also_unresolved_category']=True
        else: selected[x['SCREEN_ID']]=dict(x)
    for x in results['matched_screens']: selected[x['SCREEN_ID']]=dict(x)
    roles={};projection_issues=[]
    def evidence_row(eid,source,native,entity,locator,text,date,status='reported'):
        return {'evidence_id':eid,'source_type_normalized':'saved_reference' if source=='Cellosaurus' else 'discovery_resource',
            'source_name':source,'native_record_id':native,'retrieved_at':date,
            'retrieval_method':'offline saved metadata; no new retrieval','tool_or_package':VERSION,
            'source_locator':locator,'evidence_text_summary':text,'supports_entity_type':'screen',
            'supports_entity_id':entity,'evidence_status':status,'evidence_notes':'Original retrieval date retained; current filter execution '+manifest['started_at']}
    for native_id,item in sorted(selected.items(),key=lambda pair: ({'direct_filter_hit':0,'unresolved_category':1,'publication_sibling_context':2}[pair[1]['role']], list(selected).index(pair[0]))):
        n=item['native'];key=publication_key(n);pid=None
        if key:
            pid=pub_ids.get(key,stable_id('PUB',*key))
            if pid not in pubs:
                pubs[pid]={'publication_id':pid,'retrival_sources':'BioGRID ORCS cached metadata',
                    'evidence_status':'reported publication identifier; bibliographic enrichment pending','publication_notes':''}
                if key[0]=='pubmed': pubs[pid].update(pmid=key[1],pmid_link=f'https://pubmed.ncbi.nlm.nih.gov/{key[1]}/')
                else: pubs[pid].update(doi=key[1],doi_link='https://doi.org/'+quote(key[1],safe='/'))
            attribution=f"ORCS SOURCE_TYPE={key[0]}; SOURCE_ID={key[1]}; AUTHOR attribution={n.get('AUTHOR','')}"
            if attribution not in pubs[pid]['publication_notes']: pubs[pid]['publication_notes']+=attribution+' | '
        else: projection_issues.append({'SCREEN_ID':native_id,'issue':'No valid exact publication identity'})
        sid=native_ids.get(native_id,stable_id('SCR','ORCS',native_id));roles[sid]={'SCREEN_ID':native_id,'role':item['role'],'filter_outcome':item['outcome'],'anchor_screen_ids':item.get('anchor_screen_ids',[]),'also_unresolved_category':item.get('also_unresolved_category',False)}
        eid=stable_id('EVI','ORCS',native_id,'native-metadata');eids=[eid]
        reported={k:v for k,v in n.items() if v not in (None,'','-')}
        evidence.append(evidence_row(eid,'BioGRID ORCS',native_id,sid,item['native_locator'],json.dumps(reported,ensure_ascii=False),manifest['cache_retrieved_at']))
        ann=item.get('annotation')
        if ann:
            ae=stable_id('EVI','Cellosaurus',native_id,ann.get('accession'),ann['value']);eids.append(ae)
            evidence.append(evidence_row(ae,'Cellosaurus',ann.get('accession') or ann['value'],sid,
                item['annotation_locator']+'; '+str(ann.get('reference_locator','')),
                json.dumps({k:ann.get(k) for k in ['value','category','accession','secondary_accessions','match_method','reference_locator','review_issues','description']},ensure_ascii=False),manifest['reference_retrieval_date'],'saved reference annotation; exact CELL_LINE join'))
        row={'screen_id':sid,'publication_id':pid,'source_evidence_ids':'; '.join(eids),
             'curation_status':item['role']+'; unreviewed',
             'reviewer_decision':None,'reviewer_notes':None}
        for source,dest in DIRECT.items():
            if n.get(source) not in (None,'','-'): row[dest]=n[source]
        for source,dest in [('SCREEN_FORMAT','screen_format_normalized'),('METHODOLOGY','perturbation_type_normalized')]:
            if n.get(source) in CROSSWALKS[source]: row[dest]=CROSSWALKS[source][n[source]]
        # Preserve unsupported descriptive fields verbatim in notes, without
        # turning result-set size into library/sample counts or dataset evidence.
        additional={k:n.get(k) for k in ['SCREEN_FORMAT','EXPERIMENTAL_SETUP','SCREEN_TYPE','MOI','SCREEN_RATIONALE','SIGNIFICANCE_INDICATOR','SIGNIFICANCE_CRITERIA','NOTES','FULL_SIZE','FULL_SIZE_AVAILABLE'] if n.get(k) not in (None,'','-')}
        row['screen_notes']=f'ORCS SCREEN_ID={native_id}; role={item["role"]}; filter_outcome={item["outcome"]}; '+json.dumps(additional,ensure_ascii=False)
        if item.get('anchor_screen_ids'): row['screen_notes']+='; publication anchors='+','.join(item['anchor_screen_ids'])
        if item['review_issues']: row['screen_notes']+='; annotation review='+json.dumps(item['review_issues'],ensure_ascii=False)
        row['immune_context_notes']='Immune partners, co-culture design and eligibility unresolved; no immune gate applied.'
        screens.append(row)
    resources=[{'resource_name':'BioGRID ORCS','resource_type':'discovery resource','programmatic_access':'saved metadata',
      'access_method':'offline complete-cache filter','queried_in_this_version':'local filtering only; no network',
      'publications_discovered':results['summary']['distinct_matched_publications'],'screens_discovered':results['summary']['matched'],
      'datasets_discovered':0,'unique_contribution':'Direct filter hits only; context and unresolved rows excluded from this count',
      'limitations':'No bibliographic enrichment, exact dataset attribution, immune interaction adjudication or screen-group inference',
      'documentation_url':'https://orcs.thebiogrid.org/', 'discovery_resources_notes':json.dumps(results['summary'],ensure_ascii=False)},
      {'resource_name':'Cellosaurus saved annotations','resource_type':'reference annotation','access_method':'exact CELL_LINE join to saved annotation',
      'queried_in_this_version':'saved reference reused; no network','limitations':'Categories and review issues preserved; no overwrite of ORCS facts',
      'discovery_resources_notes':'Reference retrieval date '+manifest['reference_retrieval_date']}]
    proposed={'Publications':list(pubs.values()),'Screen Groups':[],'Screens':screens,'Datasets':[],
              'Screen-Dataset Links':[],'Sources & Evidence':evidence,'Discovery Resources':resources}
    merged={};conflicts=[]
    for sheet,rows in proposed.items():
        key=existing[sheet]['headers'][0]
        # Generated IDs cannot silently claim an unrelated existing entity.
        for row in rows:
            collisions=[x for x in existing[sheet]['rows'] if x.get(key)==row.get(key)]
            if collisions and sheet=='Publications' and any(collisions[0].get(f) and row.get(f) and str(collisions[0][f])!=str(row[f]) for f in ['pmid','doi']): raise ValueError('Publication ID collision')
            if collisions and sheet=='Screens' and row[key] not in native_ids.values(): raise ValueError('Unresolved existing screen ID collision')
        merged[sheet],c=merge_rows(existing[sheet]['rows'],rows,key);conflicts.extend({'sheet':sheet,**x} for x in c)
    pubset={x['publication_id'] for x in merged['Publications']}
    if any(x.get('publication_id') and x['publication_id'] not in pubset for x in screens): raise ValueError('Publication foreign key missing')
    return {'version':VERSION,'sheets':merged,'proposed_counts':{k:len(v) for k,v in proposed.items()},
       'headers':{k:v['headers'] for k,v in existing.items()},'roles':roles,'existing_value_conflicts':conflicts,'issues':projection_issues,
       'mapping':{'direct_fields':DIRECT,'crosswalks':CROSSWALKS,'missing_markers':[None,'','-'],
          'notes_fields':['NOTES','SCREEN_TYPE','EXPERIMENTAL_SETUP','MOI','SCREEN_RATIONALE','SIGNIFICANCE_INDICATOR','SIGNIFICANCE_CRITERIA','FULL_SIZE','FULL_SIZE_AVAILABLE'],
          'publication':'Exact SOURCE_TYPE/SOURCE_ID; AUTHOR retained only as abbreviated attribution; no derived year',
          'datasets_and_links':'No explicit dataset identity fields in the accepted cache schema; no text-mined accessions or inferred links',
          'screen_groups':'No shared design established; none generated',
          'review':'Screens reviewer_decision and reviewer_notes appended at far right; orange requests review; roles remain text',
          'reference':'No glossary sheet exists in the selected template; docs/orcs/output-fields.md consulted; OFH5 overrides older FULL_SIZE breadth interpretation'}}
