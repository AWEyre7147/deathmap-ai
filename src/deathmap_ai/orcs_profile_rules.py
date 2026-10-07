"""Interpret the two categorical ORCS profiles using saved native metadata.

Returns the same audited entity input as the biological-classes pilot. Native
values, missing-category review records and descriptive tags remain explicit;
tags never exclude screens or establish an adjudicated biological context.
"""
import re
from collections import Counter
from .orcs_filters import evaluate as evaluate_v01, validate_profile


def evaluate(screens, publications, annotations, profile):
    """Return audited screens and counts for an explicitly supported profile.

    v01 retains its original scalar comparisons and unresolved-category list.
    v02 splits on its literal separator, applies fallback only to missing
    categories, and retains fallback-negative missing-category records for
    review when all other filters pass. Regex tags use IGNORECASE field searches.
    """
    refs = {a['value']:a for a in annotations['cell_lines']}
    pubs = {(p.get('SOURCE_TYPE'),p.get('SOURCE_ID')):p for p in publications}
    if len(refs)!=len(annotations['cell_lines']) or len(pubs)!=len(publications):
        raise ValueError('Ambiguous source join keys')
    if profile['profile_id']=='orcs-cancer-cell-crispr-knockout-v01':
        validate_profile(profile)
        result=evaluate_v01(screens,annotations,profile)
        retained={r['SCREEN_ID']:r for r in result['publication_siblings']+result['unresolved_screens']+result['matched_screens']}
        audit=[]
        for r in result['screen_audit']:
            chosen=retained.get(r['SCREEN_ID'],r)
            role={'direct_filter_hit':'direct_rule_candidate','publication_sibling_context':'publication_companion','unresolved_category':'unresolved_category'}.get(chosen['role'],'excluded')
            pub=pubs.get((r['SOURCE_TYPE'],r['SOURCE_ID']))
            audit.append({'SCREEN_ID':r['SCREEN_ID'],'native':r['native'],'role':role,
                'matched_rule_ids':['categorical_filters'] if role=='direct_rule_candidate' else [],
                'common_filters_pass':r['outcome']=='matched','candidate_rules':r['criteria'],
                'seed_screen_ids':chosen.get('anchor_screen_ids',[]),'PUBLICATION_ID':pub['PUBLICATION_ID'] if pub else None,
                'annotation_review_issues':r['review_issues'],'publication_join_status':'direct' if pub else 'unresolved'})
    elif profile['profile_id']=='orcs-cancer-cell-crispr-v02':
        if set(profile['filters'])!={'ORGANISM_OFFICIAL','SCREEN_FORMAT','PHENOTYPE','CELL_LINE'} or profile['optional_restriction']['knockout_only']['enabled']:
            raise ValueError('Unsupported v02 gates or enabled optional restriction')
        audit=[];anchors={}
        for n in screens:
            ann=refs.get(n.get('CELL_LINE'),{});criteria={}
            for field,spec in profile['filters'].items():
                value=ann.get('category') if field=='CELL_LINE' else n.get(field)
                missing=value in (None,'','-')
                passed=not missing and any(t in spec['values'] for t in str(value).split(profile['filter_logic']['multi_value_separator']))
                criteria[field]={'native_value':value,'accepted_values':spec['values'],'status':'pass' if passed else 'missing' if missing else 'fail'}
            fallback=profile['filters']['CELL_LINE']['fallback']
            match=re.search(fallback['pattern'],n.get('CELL_TYPE') or '',re.IGNORECASE) if criteria['CELL_LINE']['status']=='missing' else None
            if match:criteria['CELL_LINE'].update(status='pass',fallback_label=fallback['result_label'],fallback_native_value=n.get('CELL_TYPE'),span=list(match.span()),matched_text=match.group())
            other=all(v['status']=='pass' for k,v in criteria.items() if k!='CELL_LINE')
            direct=other and criteria['CELL_LINE']['status']=='pass'
            unresolved=other and criteria['CELL_LINE']['status']=='missing'
            tags=profile['tags'];setting='in_vivo' if n.get('SCREEN_FORMAT')=='in vivo' or n.get('EXPERIMENTAL_SETUP')=='Implantation to Mouse Model' else 'in_vitro'
            labels=[]
            for token,label in [('T cell exposure','direct_setup_T_cell'),('NK cell exposure','direct_setup_NK_cell')]:
                if n.get('EXPERIMENTAL_SETUP')==token:labels.append(label)
            if any(re.search(tags['immune_pressure_candidate']['immune_keyword_pattern'],n.get(f) or '',re.IGNORECASE) for f in ['CONDITION_NAME','SCREEN_RATIONALE']):labels.append('keyword_in_condition_or_rationale')
            if setting=='in_vivo':labels.append('in_vivo_host_immunity_unresolved')
            pub=pubs.get((n.get('SOURCE_TYPE'),n.get('SOURCE_ID')))
            item={'SCREEN_ID':n['SCREEN_ID'],'native':n,'role':'direct_rule_candidate' if direct else 'unresolved_category' if unresolved else 'excluded',
                'matched_rule_ids':['cancer_by_orcs_cell_type' if match else 'cancer_reference'] if direct else [],
                'common_filters_pass':other,'candidate_rules':criteria,'seed_screen_ids':[],
                'PUBLICATION_ID':pub['PUBLICATION_ID'] if pub else None,'annotation_review_issues':ann.get('review_issues',[]),
                'publication_join_status':'direct' if pub else 'unresolved',
                'descriptive_tags':{'perturbation_modality':tags['perturbation_modality']['map'].get(f"{n.get('LIBRARY_TYPE')}|{n.get('METHODOLOGY')}",'unresolved'),
                    'experimental_setting_candidate':setting,'immune_pressure_candidate':labels,
                    'in_vivo_host_contrast':bool(re.search(r'nu/nu|Foxn1|Rag1|Rag2|NSG|SCID|immunodeficient|immunocompetent| VS\. ',n.get('CONDITION_NAME') or '',re.IGNORECASE))}}
            audit.append(item)
            if direct and pub:anchors.setdefault((n['SOURCE_TYPE'],n['SOURCE_ID']),[]).append(n['SCREEN_ID'])
        for item in audit:
            ids=anchors.get((item['native'].get('SOURCE_TYPE'),item['native'].get('SOURCE_ID')),[])
            if ids and item['role']!='direct_rule_candidate':
                item['also_unresolved_category']=item['role']=='unresolved_category'
                item.update(role='publication_companion',seed_screen_ids=ids)
    else:raise ValueError('Unsupported categorical profile')
    counts=Counter(i['role'] for i in audit)
    return audit,{'examined':len(audit),'direct_rule_candidates':counts['direct_rule_candidate'],
        'fallback_candidates':sum('cancer_by_orcs_cell_type' in i['matched_rule_ids'] for i in audit),
        'publication_companions':counts['publication_companion'],'unresolved_category':counts['unresolved_category'],
        'excluded':counts['excluded'],'retained_screens':sum(i['role']!='excluded' for i in audit),
        'retained_publications':len({i['PUBLICATION_ID'] for i in audit if i['role']!='excluded' and i['PUBLICATION_ID'] is not None}),
        'network_requests':0,'interpretation':'Unadjudicated candidates. Modality tags and publication association do not establish qualifying CRISPR data.'}
