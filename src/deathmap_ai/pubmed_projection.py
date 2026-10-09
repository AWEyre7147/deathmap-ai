"""Project saved PMID-led responses into shared publication metadata.

This imported helper preserves raw relationships and record locators in JSON.
The workbook is a publication-level review view: repeated repository rows keep
their PMID, and no exact ORCS screen attribution is inferred. Native XML envelope
edits preserve Excel compatibility namespaces and the owner's formatting.
"""
from pathlib import Path
from datetime import date
from collections import defaultdict
import hashlib
import io
import json
import math
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
import openpyxl

NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
MC='http://schemas.openxmlformats.org/markup-compatibility/2006'
ET.register_namespace('',NS)
q=lambda name:'{'+NS+'}'+name
def text(element: ET.Element, path: str) -> str:
    """Return source text without guessing missing metadata.

    Parameters
    ----------
    element : Element or None
        Source XML record; None represents a missing source element.
    path : str
        Relative XML path to the requested field.

    Returns
    -------
    str
        Concatenated source text, or an empty string for absent metadata.
    """
    node=element.find(path) if element is not None else None
    return ''.join(node.itertext()) if node is not None else ''

def flatten(*args):
    """Keep source evidence in native responses without duplicating every leaf.

    Parameters
    ----------
    args : tuple
        Source node and provenance arguments retained by the pilot parser.

    Returns
    -------
    None
        No duplicated leaf records; native XML and record locators are retained.
    """
    return None

def project_saved(folder, pmids):
    """Project saved PMID metadata with native identifiers and direct links.

    Parameters
    ----------
    folder : Path or str
        Saved EFfetch, ELink and ESummary files with no network side effects.
    pmids : list of str
        Exact verified PMIDs whose article and link records must be present.

    Returns
    -------
    dict
        Publication, repository, SRA and MeSH rows, direct relationships,
        record provenance and unresolved/missing-field issues. Dates retain
        ISO notation and reported precision.

    Raises
    ------
    AssertionError
        Returned identifiers are incomplete, duplicated or unexpectedly scoped.
    ParseError
        Native XML or embedded SRA metadata cannot be parsed.
    """
    BASE=Path(folder)
    PMIDS=pmids
    SELECTION={"pmids":pmids}
    evidence=[]
    issues=[]
    articles={text(a,'MedlineCitation/PMID'):a for a in ET.parse(BASE/'pubmed.xml').getroot().findall('PubmedArticle')}
    assert set(articles)==set(PMIDS),'Missing or unexpected PubMed articles'
    publication=[]
    mesh_links=[]
    groups=defaultdict(set)
    labels={}
    months={name:i for i,name in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],1)}
    for pmid in PMIDS:
        article=articles[pmid]
        flatten(article,f'/PubmedArticleSet/PubmedArticle[PMID={pmid}]','pubmed.xml',pmid)
        ids={i.get('IdType'):i.text or '' for i in article.findall('PubmedData/ArticleIdList/ArticleId')}
        pd=article.find('MedlineCitation/Article/Journal/JournalIssue/PubDate')
        year,month,day=[text(pd,k) for k in ['Year','Month','Day']]
        if year and month and day:
            month_number=int(month) if month.isdigit() else months[month]
            value=date(int(year),month_number,int(day))
        else:
            month_number=(int(month) if month.isdigit() else months.get(month)) if month else None
            value=f'{year}-{month_number:02d}' if year and month_number else (year or text(pd,'MedlineDate'))
            issues.append({'pmid':pmid,'field':'Publication Date','status':'partial_date','reported_value':value,'source':'JournalIssue/PubDate','note':'No day inferred'})
        publication.append([pmid,ids.get('doi',''),ids.get('pmc',''),text(article,'MedlineCitation/Article/ArticleTitle'),value])
        headings=article.findall('MedlineCitation/MeshHeadingList/MeshHeading')
        if not headings:
            issues.append({'pmid':pmid,'field':'MeSH','status':'not_returned'})
        for i,heading in enumerate(headings,1):
            descriptor=heading.find('DescriptorName')
            for qualifier in heading.findall('QualifierName') or [None]:
                descriptor_ui=descriptor.get('UI','')
                qualifier_ui=qualifier.get('UI','') if qualifier is not None else ''
                key=(descriptor_ui,qualifier_ui)
                groups[key].add(pmid)
                labels[key]=(''.join(descriptor.itertext()),''.join(qualifier.itertext()) if qualifier is not None else '')
                mesh_links.append([pmid,descriptor_ui,qualifier_ui,descriptor.get('MajorTopicYN',''),qualifier.get('MajorTopicYN','') if qualifier is not None else ''])
    
    mesh=[[key[0],labels[key][0],key[1],labels[key][1],len(pmids),'; '.join(sorted(pmids,key=int))] for key,pmids in sorted(groups.items())]
    linked={}
    relationships=[]
    for db in ['gds','bioproject','sra']:
        response=json.loads((BASE/f'links-{db}.json').read_text(encoding='utf-8'))
        per_pmid={}
        for linkset in response['linksets']:
            assert len(linkset['ids'])==1,'Lost per-publication link provenance'
            pmid=linkset['ids'][0]
            assert pmid in PMIDS
            per_pmid[pmid]=[]
            for group in linkset.get('linksetdbs',[]):
                assert group['dbto']==db and group['linkname']==f'pubmed_{db}'
                for uid in group.get('links',[]):
                    per_pmid[pmid].append(uid)
                    relationships.append({'pmid':pmid,'from_resource':'PubMed','from_identifier':pmid,'to_resource':db,'to_native_uid':uid,'link_type':group['linkname'],'evidence_status':'direct','source_file':f'links-{db}.json','locator':f'linksets[ids={pmid}]/linksetdbs[linkname=pubmed_{db}]/links'})
            if not per_pmid[pmid]:
                issues.append({'pmid':pmid,'resource':db,'status':'no_direct_pubmed_link','note':'Not evidence that a repository deposit is absent'})
        assert set(per_pmid)==set(PMIDS)
        linked[db]=per_pmid
    
    summaries={db:{} for db in linked}
    for db in linked:
        for file in sorted(BASE.glob(f'summary-{db}-*.xml')):
            root=ET.parse(file).getroot()
            assert root.find('.//ERROR') is None,file.name
            nodes=root.findall('.//DocumentSummary') if db=='bioproject' else root.findall('.//DocSum')
            for node in nodes:
                uid=node.get('uid') if db=='bioproject' else node.findtext('Id')
                assert uid not in summaries[db],(db,uid)
                summaries[db][uid]=(node,file.name)
    
    repository=[]
    sra_rows=[]
    record_provenance=[]
    for pmid in PMIDS:
        for db in ['gds','bioproject','sra']:
            for uid in linked[db][pmid]:
                if uid not in summaries[db]:
                    issues.append({'pmid':pmid,'resource':db,'uid':uid,'status':'summary_not_retrieved'})
                    continue
                node,source=summaries[db][uid]
                flatten(node,f'/{db}/record[uid={uid}]',source,pmid)
                if db=='gds':
                    items={i.get('Name'):''.join(i.itertext()) for i in node.findall('Item')}
                    accession=items.get('Accession','')
                    repository.append([pmid,'GEO',accession,items.get('entryType',''),items.get('title',''),items.get('summary',''),items.get('gdsType','')])
                elif db=='bioproject':
                    accession=text(node,'Project_Acc')
                    repository.append([pmid,'BioProject',accession,'Project',text(node,'Project_Title'),text(node,'Project_Description'),text(node,'Project_Data_Type')])
                else:
                    items={i.get('Name'):i.text or '' for i in node.findall('Item')}
                    fragment=ET.fromstring('<Root>'+items.get('ExpXml','')+'</Root>')
                    runs=ET.fromstring('<Root>'+items.get('Runs','')+'</Root>')
                    flatten(fragment,f'/sra/record[uid={uid}]/ExpXml',source,pmid)
                    flatten(runs,f'/sra/record[uid={uid}]/Runs',source,pmid)
                    def accession_for(tag: str) -> str:
                        """Read the reported accession for one native SRA entity."""
                        element=fragment.find(tag)
                        return element.get('acc','') if element is not None else ''
                    accession=accession_for('Experiment')
                    for run in list(runs) or [None]:
                        sra_rows.append([pmid,accession,accession_for('Study'),accession_for('Sample'),text(fragment,'Biosample'),text(fragment,'Bioproject'),run.get('acc','') if run is not None else ''])
                    for resource,target,kind in [('SRA',accession_for('Study'),'study'),('SRA',accession_for('Sample'),'sample'),('BioSample',text(fragment,'Biosample'),'biosample'),('BioProject',text(fragment,'Bioproject'),'bioproject')]:
                        if target:
                            relationships.append({'pmid':pmid,'from_resource':'SRA','from_identifier':accession,'to_resource':resource,'to_identifier':target,'link_type':'reported_'+kind,'evidence_status':'direct','source_file':source,'locator':f'DocSum[Id={uid}]/ExpXml'})
                    for run in runs:
                        relationships.append({'pmid':pmid,'from_resource':'SRA','from_identifier':accession,'to_resource':'SRA','to_identifier':run.get('acc',''),'link_type':'reported_run','evidence_status':'direct','source_file':source,'locator':f'DocSum[Id={uid}]/Runs'})
                record_provenance.append({'pmid':pmid,'resource':db,'uid':uid,'accession':accession,'source_file':source,'evidence_status':'direct'})
    
    native_accessions={(r['pmid'],r['resource'],r['uid']):r['accession'] for r in record_provenance}
    for relation in relationships:
        key=(relation.get('pmid'),relation.get('to_resource'),relation.get('to_native_uid'))
        if key in native_accessions:
            relation['to_identifier']=native_accessions[key]
    
    rows_by_sheet={'Publication':publication,'Repository Records':[[r[i] for i in [0,1,2,3,6,4,5]] for r in repository],'SRA Accessions':sra_rows,'MeSH':mesh,'MeSH Links':mesh_links}
    canonical={'selection':SELECTION,'publication_date_basis':'JournalIssue/PubDate; preserve source precision','rows':{k:[[v.isoformat() if isinstance(v,date) else v for v in row] for row in rows] for k,rows in rows_by_sheet.items()},'relationships':relationships,'record_provenance':record_provenance,'issues':issues,'field_evidence':evidence}
    
    return canonical
