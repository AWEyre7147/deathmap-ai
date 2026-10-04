"""Document workbook mappings from the complete shared ORCS metadata databases.

This is a planning projection only: it reads the template header schema and the
shared screen/publication sources, never a previous analysis or populated Excel.
The generated map distinguishes reported facts, explicit derivations, reference
annotations and fields requiring scientific review. It does not fill a workbook.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    """Read local UTF-8 metadata after the full publication capture completes."""
    return json.loads(Path(path).read_text(encoding='utf-8'))


def build(root):
    """Rewrite the field map and enrichment plan using both complete ORCS files.

    Preserve the previous draft in logs. No publication selection, retrieval,
    scientific adjudication, source editing or workbook writing occurs here.
    """
    root = Path(root)
    data = root/'data/orcs'
    screens, pubs = read(data/'screen-index.json'), read(data/'publication-index.json')
    manifest = read(data/'publication-index.manifest.json')
    if manifest['status'] != 'complete' or len(pubs) != manifest['publication_count_expected']:
        raise ValueError('A complete shared publication database is required before planning')
    schema = read(root/'src/deathmap_ai/reference_schema.json')['tables']
    docs = root/'docs/orcs'
    backup = root/'logs/orcs-planning-before-publication-database-20261004'
    backup.mkdir(parents=True,exist_ok=True)
    for name in ['workbook-field-source-map.md','enrichment-plan.md']:
        if (docs/name).exists() and not (backup/name).exists():
            shutil.copyfile(docs/name,backup/name)
    # Mapping names retain exact workbook headers; native sources stay uppercase.
    screen_direct = {'screen_name_reported':'SCREEN_NAME','methodology_reported':'METHODOLOGY',
        'enzyme_reported':'ENZYME','library_name_reported':'LIBRARY','library_type_reported':'LIBRARY_TYPE',
        'cell_line_reported':'CELL_LINE','organism_reported':'ORGANISM_OFFICIAL',
        'condition_name_reported':'CONDITION_NAME','condition_dosage_reported':'CONDITION_DOSAGE',
        'duration_reported':'DURATION','phenotype_original':'PHENOTYPE','statistical_analysis_reported':'ANALYSIS'}
    pub_direct = {'title_original':'TITLE','journal_reported':'JOURNAL','author_list_ reported':'AUTHORS','pmid':'PMID','doi':'DOI'}

    def count(rows,field):
        return sum(x.get(field) not in (None,'','-',[],{}) for x in rows)

    lines=['# Workbook field-source map','', '## [WM1] Purpose and scope','',
        f'This map considers the complete shared ORCS databases: {len(screens):,} screens and {len(pubs):,} publications. It is independent of all prior filtered analyses. It plans future pipeline population; no workbook has been filled or assessed here.','',
        'Sources: [screen-index.json](../../data/orcs/screen-index.json), [publication-index.json](../../data/orcs/publication-index.json), and [publication-screen-links.json](../../data/orcs/publication-screen-links.json). Publication header evidence and request receipts are preserved in data/orcs/publication-source.','',
        'Availability counts describe source fields across the complete databases, not populated workbook cells or qualifying-study coverage. Direct facts, derived values, review decisions and unresolved fields remain distinct.','',
        '## [WM2] Column mapping','']
    for sheet, table in schema.items():
        headers=[x['header'] for x in table['fields']]
        if sheet=='Screens':
            headers += ['reviewer_decision','reviewer_notes']
        lines += ['### '+sheet,'','| Exact workbook header | Evidence / transformation | Status |','|---|---|---|']
        for h in headers:
            status='Unresolved'
            origin='Neither shared database supplies a defensible direct value for this field.'
            if sheet=='Publications':
                if h in pub_direct:
                    f=pub_direct[h];origin=f'Publication {f}; available for {count(pubs,f)}/{len(pubs)} records.';status='Reported'
                    if h=='pmid':origin+=' PMID is promoted only when cached and page-reported identifiers agree.'
                    if h=='doi':origin+=' DOI-format cached SOURCE_ID only; prepub URLs remain preserved separately.'
                elif h=='publication_id':origin='Generate an internal publication key while preserving ORCS PUBLICATION_ID and exact SOURCE_TYPE/SOURCE_ID; retain the ID mapping.';status='Derived'
                elif h=='publication_year':origin='Extract the year from reported PUBLICATION_DATE; retain the original full date as evidence.';status='Derived'
                elif h in ('pmid_link','doi_link'):origin='Build the corresponding URL from the supported PMID/DOI; a generated URL is not a fetched record.';status='Derived'
                elif h=='retrival_sources':origin='ORCS website publication header plus cached screen/source-identity association.';status='Provenance'
                elif h=='publication_notes':origin='Preserve ABSTRACT, PUBLICATION_DATE, ORCS PUBLICATION_ID, raw source assertions, supplementary links and REVIEW_ISSUES; do not flatten source conflicts.';status='Reported + provenance'
                elif h=='evidence_status':origin='Record reported, unresolved or conflicting status from field-specific source checks; preserve source review issues.';status='Derived'
                elif h=='publication_type_reported':origin='SOURCE_TYPE identifies the native source namespace (including prepub); it does not establish article/review/publication type.'
                elif h in ('pmcid','pmc_link'):origin='No structured PMCID field was obtained from the ORCS publication headers; do not derive it from a PMID.'
            elif sheet=='Screens':
                if h in screen_direct:
                    f=screen_direct[h];origin=f'Screen {f}; non-placeholder values in {count(screens,f)}/{len(screens)} records.';status='Reported'
                elif h=='screen_id':origin='Generate an internal screen key while retaining native SCREEN_ID.';status='Derived'
                elif h=='publication_id':origin='Join SCREEN_ID through publication-screen-links to the publication ID mapping. This is a direct publication association, not a dataset attribution.';status='Reported relationship + derived key'
                elif h=='screen_format_normalized':origin='Explicit reviewed SCREEN_FORMAT crosswalk (Pool -> pooled; Array -> arrayed); leave unsupported values unmapped.';status='Derived'
                elif h=='perturbation_type_normalized':origin='Explicit reviewed METHODOLOGY crosswalk (Knockout -> CRISPR knockout); retain original methodology.';status='Derived'
                elif h=='screen_notes':origin='Preserve SCREEN_ID, SCREEN_RATIONALE, NOTES, EXPERIMENTAL_SETUP, MOI, SCREEN_TYPE, significance metadata and FULL_SIZE with their native meanings.';status='Reported'
                elif h=='experimental_setting_normalized':origin='EXPERIMENTAL_SETUP and NOTES may support interpretation; a reviewed crosswalk is needed.';status='Review required'
                elif h=='disease_context_normalized':origin='CELL_LINE can join saved Cellosaurus categories/descriptions; a cancer-cell-line category is not automatically a study-level disease context.';status='Reference + review required'
                elif h=='source_evidence_ids':origin='Generate references to screen metadata, publication associations and any separately joined reference annotations.';status='Derived'
                elif h in ('reviewer_decision','reviewer_notes','curation_status'):origin='Owner/pipeline review state, independent of source facts; reviewer entry columns remain rightmost.';status='Review bookkeeping'
                elif h=='screen_group_id':origin='Publication membership does not establish shared experimental design; grouping requires review.';status='Review required'
                elif h in ('library_gene_count_reported','library_guide_count_reported'):origin='FULL_SIZE/SCORES_SIZE describe screen result metadata; they do not establish library gene or guide counts.'
                elif h in ('perturbed_population_reported','interacting_population_reported','immune_cell_population_reported','immune_cell_population_normalized','immune_interaction_mode_normalized','coculture_configuration_normalized','effector_target_ratio_reported','immune_context_notes'):
                    origin='CELL_LINE/CELL_TYPE, EXPERIMENTAL_SETUP and NOTES are candidate evidence; structured participant roles, ratios and co-culture assignments are not established automatically.';status='Review / additional evidence'
            elif sheet=='Screen Groups':
                origin='Shared experimental objective/design must be established by review; do not create one group per ORCS publication.';status='Review required'
            elif sheet=='Datasets':
                origin='ORCS publication records and supplementary links do not establish a repository dataset identity or its availability.'
                if h=='supporting_asset_urls_reported':origin='Publication SUPPLEMENTARY_FILES supplies asset URLs/labels. Keep them as publication-associated asset mentions until a defined dataset attribution supports this field.';status='Asset metadata only'
                elif h=='publication_id':origin='A publication association can be recorded after an actual dataset has been identified; publication /Dataset/ page IDs are not dataset IDs.'
            elif sheet=='Screen-Dataset Links':
                origin='No exact screen-repository dataset relation is established by either shared database; retain unresolved status until explicit evidence supports one.'
            elif sheet=='Sources & Evidence':
                origin='Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references.';status='Provenance + derived keys'
            elif sheet=='Discovery Resources':
                origin='Use the screen/publication manifests and receipts to report resource, tool/version, metadata access, actual counts and limitations; this catalog build is not a filtered discovery run.';status='Provenance'
                if h=='authentication_required':origin='Original screen REST retrieval used a key; public publication headers and browse metadata did not. Preserve that distinction.'
                elif h in ('publications_discovered','screens_discovered','datasets_discovered'):origin='Catalog counts describe resource inventory, not qualifying discoveries. A future search must report its own direct-hit counts.';status='Run-dependent'
            lines.append(f'| {h} | {origin} | {status} |')
        lines.append('')
    lines += ['## [WM3] Review checkpoints','',
        '1. Integrate these sources through native ID mappings and field-level evidence, preserving cached/page identifier conflicts.',
        '2. Keep screen, publication and supporting-asset entities distinct. ORCS /Dataset/ pages describe publications.',
        '3. Resolve scientific normalization and screen grouping only through reviewed rules.',
        '4. Generate any future workbook as a new version, preserving reviewer entries and source identifiers.',
        '', '[Enrichment plan](enrichment-plan.md) describes the local integration stage and evidence that remains unavailable.']
    (docs/'workbook-field-source-map.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    plan=f'''# ORCS enrichment plan
## [EP1] Objective and boundary
Use the two complete shared ORCS metadata databases in future pipeline runs: {len(screens):,} screen records and {len(pubs):,} publication records. This plan is independent of the previous filtered analysis. No historical workbook is enriched or changed by building these databases or this map.

The shared catalogs belong in data/orcs; search configurations belong in searches/orcs; each future run owns its own outputs. This separation allows different filters to reuse the same bibliography without repeated publication retrieval.

## [EP2] Available shared tables
| File | Entity / role | Evidence supplied |
|---|---|---|
| screen-index.json / screen-metadata.csv | Native ORCS screens | Reported screen design, model, phenotype, methods, notes and source identifiers |
| publication-index.json / publication-metadata.csv | ORCS publication pages | Titles, full reported author strings, abstracts, journals, dates, page source assertions and supplementary-file link metadata |
| publication-screen-links.json / .csv | Explicit screen-publication associations | Native SCREEN_ID -> ORCS PUBLICATION_ID from the public browse listing, with cached SOURCE_TYPE/SOURCE_ID preserved |
| publication-index.manifest.json and publication-source/ | Provenance | Complete-inventory checks, saved header excerpts, hashes, retrieval times, attempt receipts and review issues |
| Saved reference annotation bundle | Cellosaurus and BTO/CL/EFO | Existing identity/category/accession/definition evidence, separately attributed |

The publication database is extracted website metadata, not a native ORCS REST publication response. The API screen index remains unchanged. ORCS's use of /Dataset/ in publication URLs does not imply repository dataset identities.

## [EP3] Local enrichment sequence for a future run
1. Apply the owner-defined filter to the shared screen index and saved reference annotations.
2. Resolve selected SCREEN_ID values through publication-screen-links; retrieve corresponding publication rows locally without another website search.
3. Attach source-backed bibliographic fields and preserve full abstract/date, native identifiers, raw page assertions and source locators in evidence.
4. Keep supplementary links as publication-associated asset mentions with labels and URLs. Do not download their contents or convert each link into a dataset or exact screen-dataset relationship.
5. Produce a new projection/workbook when separately requested. Maintain a native-to-internal ID mapping; preserve owner review entries and distinguish reported facts from normalization.

No prior filter run is selected as an enrichment target here. The source catalogs cover all indexed ORCS screens and publications.

## [EP4] Remaining decisions and missing evidence
- The page-labelled identifiers on some prepub records differ from cached source identifiers. Preserve both; do not promote the displayed small numbers into verified PMIDs. Source encoding issues also remain visible.
- Bibliography and abstracts may help manual interpretation, but they do not automatically identify immune partners, co-culture ratios, comparators, detailed readouts or replicate designs for individual screens.
- A supplement link is direct evidence of a listed asset, not proof of its contents, availability at a repository, or the screen it contains.
- Shared screen groups and exact repository datasets/links require additional explicit evidence and reviewed rules. External publication/repository retrieval, full screen-page collection and asset-content inspection are separate possible stages, not implemented by this task.

## [EP5] Refresh and learning checkpoint
Retain immutable source snapshots and compare resource versions before refreshing. Publication receipts support restart without repeating successful requests; updates must revalidate changed existing records as well as new IDs. The current builder resumes the dated source collection; a new resource snapshot needs a new dated collection rather than silently replacing source evidence.

Learning checkpoint: an association table connects native screens to bibliographic records while keeping their identities and provenance distinct. It enables efficient local joins without turning a publication into an experimental dataset.

See the [field-source map](workbook-field-source-map.md) and [shared database guide](../../data/orcs/README.md). No gene-level result rows, scores, linked supplements or external records were retrieved.
'''
    (docs/'enrichment-plan.md').write_text(plan,encoding='utf-8')
    return sum(len(x['fields']) for x in schema.values())+2


if __name__=='__main__':
    print(f'Documented {build(ROOT)} template/reviewer headers from shared source catalogs.')
