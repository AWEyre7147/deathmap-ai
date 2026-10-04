"""Inventory saved OmicsDI metadata and generate the observed-field guide offline.

Coverage includes complete search pages (also buffered/unadmitted entries) and
all preserved detail receipts. Wildcard array paths describe structure, not an
inference about experimental entities. Unknown fields are retained verbatim in
raw responses and enumerated here without invented semantics.
"""
import json,re
from collections import Counter,defaultdict
from pathlib import Path
from deathmap_ai.discovery_v02 import VERSION,read

MEANINGS={
 'id':('Native search identifier','accession_reported; dataset_id identity'),
 'accession':('Native detail identifier','accession_reported after identity validation'),
 'source':('Native search repository label','repository_normalized, unchanged'),
 'database':('Native detail repository label','identity validation; conflicts retained'),
 'title':('Resource record title','datasets.title_original'),
 'name':('Resource record name','datasets.title_original'),
 'description':('Resource record description; not an adjudicated experiment','datasets.description_reported'),
 'additional.organism':('Reported organism label','datasets.organism_reported'),
 'additional.species':('Reported species label','datasets.organism_reported'),
 'additional.scientific_name':('Reported organism name','datasets.organism_reported'),
 'additional.study_type':('Source study-type label','datasets.experiment_type_reported'),
 'additional.gds_type':('Source study-type label','datasets.experiment_type_reported'),
 'additional.full_dataset_link':('Source-reported record link; not visited','datasets.dataset_url; no availability inference'),
 'additional.pubmed_title':('Reported associated publication title','publications.title_original only when association unambiguous'),
 'additional.pubmed_authors':('Reported associated publication authors','publications.author_list_reported only when unambiguous'),
 'additional.journal':('Reported publication journal','publications.journal_reported only when unambiguous'),
 'additional.pubmed_abstract':('Publication abstract, distinct from dataset description','native evidence only; never dataset description'),
 'additional.sample_protocol':('Reported sample protocol; narrative may cover multiple entities','datasets._native_protocols and evidence; no NLP extraction'),
 'additional.data_protocol':('Reported data protocol','datasets._native_protocols and evidence; no NLP extraction'),
 'additional':('Repository-dependent additional metadata object','native evidence; recognized child mappings below'),
 'cross_references':('Source-reported external associations; not verified externally','native evidence; named publication IDs only mapped'),
 'dates':('Source dates; not our retrieval timestamp','native evidence only'),
 'scores':('Source index scores; not scientific qualification','native evidence only'),
 'file_versions':('Source file/version metadata; no files retrieved','native evidence only'),
 'is_claimable':('Source claimability flag; not accessibility','native evidence only')}


def explain(path):
    """Return a deliberately narrow observed meaning and mapping for a native path."""
    plain=path.replace('[]','')
    if plain in MEANINGS:return MEANINGS[plain]
    if plain.casefold() in ('cross_references.pubmed','cross_references.pmid','cross_references.doi','cross_references.pmcid','additional.doi','additional.pmcid','additional.pmid','additional.pubmed'):
        return ('Named publication identifier association','publications identifier and association; exact syntax normalization, no screen link')
    return ('Source-reported '+plain+'; detailed semantics not independently established','native evidence only; no structured target assignment')


def inventory(root,state):
    """Read complete saved responses without requests; return source/path coverage."""
    groups={};bad=[];refs=sorted({p for q in state['queries'].values() for p in q['pages']})
    def add(source,endpoint,obj,ref):
        group=groups.setdefault(source,{'objects':0,'endpoints':Counter(),'fields':{}})
        group['objects']+=1;group['endpoints'][endpoint]+=1;seen=set()
        def visit(v,path):
            if path:
                f=group['fields'].setdefault(path,{'types':Counter(),'objects_present':0,'example':None,'example_ref':ref})
                f['types'][type(v).__name__]+=1
                if path not in seen:f['objects_present']+=1;seen.add(path)
                if f['example'] is None and not isinstance(v,(dict,list)) and v is not None:
                    # Personal contact fields stay in native evidence, not repeated
                    # in a public-facing field glossary.
                    f['example']='[contact value retained in native response]' if re.search('mail|phone',path,re.I) else str(v)[:100]
            if isinstance(v,dict):
                for k,c in v.items():visit(c,path+'.'+k if path else k)
            elif isinstance(v,list):
                for c in v:visit(c,path+'[]')
        visit(obj,'')
    for ref in refs:
        try:
            payload=read(root/ref)
            for row in payload['datasets']:add(str(row.get('source',row.get('database','unknown'))),'search',row,ref)
        except (ValueError,KeyError,TypeError) as e:bad.append({'ref':ref,'error':str(e)})
    detailrefs={r['detail_response_ref']:r['repository_original'] for r in state['records'].values() if r.get('detail_response_ref')}
    for event in state['detail_attempts'].values():
        ref=event.get('raw_response_ref')
        if ref and (root/ref).is_file():detailrefs.setdefault(ref,json.loads(event['record_key'])[0])
    for ref,requested in sorted(detailrefs.items()):
        try:
            obj=read(root/ref)
            if not isinstance(obj,dict):raise ValueError('Detail not an object')
            add(str(obj.get('database',obj.get('source',requested))),'detail',obj,ref)
        except (ValueError,KeyError,TypeError) as e:bad.append({'ref':ref,'error':str(e)})
    for group in groups.values():
        for path,f in group['fields'].items():
            f['objects_absent']=group['objects']-f['objects_present'];f['meaning'],f['mapping']=explain(path)
            f['status']='observed; detailed field semantics not guaranteed by API help'
    return {'version':VERSION,'documentation_checked':'2026-09-19','documentation_url':'https://www.omicsdi.org/help/api',
        'coverage':'All referenced search pages and saved details; duplicate observations included, not unique dataset counts',
        'search_pages':len(refs),'detail_responses':len(detailrefs),'unparseable':bad,'sources':groups}


def write_guide(root,state,verify=False):
    """Generate deterministic inventory JSON and Markdown from current saved intake."""
    inv=inventory(root,state);folder=root/'docs/field guide/omicsdi'
    def emit(path,text):
        if verify:
            if path.read_text(encoding='utf-8')!=text:raise ValueError('Field guide mismatch: '+str(path))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
    emit(root/'outputs'/VERSION/'field_inventory.json',json.dumps(inv,ensure_ascii=False,indent=2)+'\n')
    sources=inv['sources'];dates=sorted({r['retrieved_at'] for r in state['records'].values()})
    intro=f'''# Observed OmicsDI field guide

API help checked 2026-09-19: [official documentation](https://www.omicsdi.org/help/api).
No server API version was reported. This guide covers the six unchanged v02
queries, {inv['search_pages']} saved search pages and {inv['detail_responses']} saved detail responses.
Search observation dates span {dates[0]} through {dates[-1]}.
Original historical dates remain in source records; this is a cached/live mixture.
Counts include duplicate observations and whole pages, including any unadmitted entries.
Historical 89 receipts retain their 50-within/39-excess accounting. New reservations
are counted separately, including uncertain attempts without usable responses.

These are observed fields, not an exhaustive OmicsDI schema. Search and detail
shapes vary. For identity, search source/id and detail database/accession are
observed; conflicting alternatives are preserved, never silently merged.
Detail repository aliases differing from requested identity are withheld from
structured mapping; their complete native metadata remains in source_records.
Repository labels listed below are exactly those observed. Any repository absent
from this list was not observed; this guide makes no completeness claim about the
universe of repositories. No additional searches were used to fill this guide.

Per-source tables count presence across that source's search/detail objects. An
absent field is not evidence of scientific absence. Types and examples describe
native JSON; objects/arrays also have child rows. Examples are truncated, and
contact values are not repeated here. Every field and raw response remains saved.
Unknown fields have no invented semantic definition or target assignment.

Mapping applies only after identity/association checks. Structured publication
identifiers are syntax-normalized; multiple associations use arrays. Publication
sharing never creates a screen–dataset link. Narrative protocols and publication
abstracts remain separate evidence; no experiment extraction or scientific review
is performed. Source-native repository labels are preserved rather than aliased.

[Common fields](common-fields.md). Machine inventory: `outputs/{VERSION}/field_inventory.json`.
Regenerate offline: `python -B -m deathmap_ai.discovery_v02 export` (after package installation).

| Source | Search objects | Detail objects | Notes |
|---|---:|---:|---|
'''
    # Windows filenames are case-insensitive. Preserve native labels in content,
    # and give differing case labels distinct filenames rather than overwriting.
    def filename(source):
        return source.lower()+('-detail-label' if source!=source.lower() else '')+'.md'
    for source,g in sorted(sources.items()):intro+=f"| {source} | {g['endpoints']['search']} | {g['endpoints']['detail']} | [{source}]({filename(source)}) |\n"
    emit(folder/'README.md',intro)
    common='# Common response fields\n\nAll per-field statements below are observed, not a complete documented schema.\nThe API help documents the search envelope `count`, `datasets`, and `facets`;\nthese are pagination/result-container metadata, not dataset attributes. `count`\nmay change between cached and live pages. Native result order is retained.\n\n| Native path | Observed meaning | Target mapping |\n|---|---|---|\n'
    for path,(meaning,mapping) in MEANINGS.items():common+=f'| `{path}` | {meaning} | {mapping} |\n'
    common+='\nSee source tables for exact types, presence counts, variability and source-grounded examples. Unrecognized dates, links and cross-references remain native evidence. Neither a URL nor a repository name establishes data or screen availability.\n'
    emit(folder/'common-fields.md',common)
    for source,g in sorted(sources.items()):
        level='literature-associated native record; not an independent experimental deposit' if source=='biostudies-literature' else 'ENA/project record; may aggregate experiments' if source=='project' else 'repository native record; experimental granularity not assumed'
        text=f'# {source}\n\nEntity level: {level}. Field status: observed on saved responses; detailed semantics are not guaranteed by the API help. Search/detail variability is retained. No external source was visited.\n\nCoverage: {g["objects"]} response objects. Presence is across both endpoint shapes; types count occurrences, not unique records. Container examples are represented by their child rows. Full examples and source paths are in field_inventory.json. Native values are neither terminology-normalized nor interpreted scientifically.\n\n| Native path | Types | Present / absent objects | Example | Meaning | Mapping / caution |\n|---|---|---|---|---|---|\n'
        for path,f in sorted(g['fields'].items()):
            clean=lambda x:str(x if x is not None else '(container or null)').replace('|','\\|').replace('\n',' ').replace('\r',' ').replace('`',"'")
            text+=f'| `{path}` | {", ".join(sorted(f["types"]))} | {f["objects_present"]} / {f["objects_absent"]} | {clean(f["example"])} | {clean(f["meaning"])} | {clean(f["mapping"])} |\n'
        emit(folder/filename(source),text)
    return inv
