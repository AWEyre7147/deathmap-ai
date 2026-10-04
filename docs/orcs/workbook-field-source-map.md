# Workbook field-source map

## [WM1] Purpose and scope

This map considers the complete shared ORCS databases: 2,217 screens and 418 publications. It is independent of all prior filtered analyses. It plans future pipeline population; no workbook has been filled or assessed here.

Sources: [screen-index.json](../../data/orcs/screen-index.json), [publication-index.json](../../data/orcs/publication-index.json), and [publication-screen-links.json](../../data/orcs/publication-screen-links.json). Publication header evidence and request receipts are preserved in data/orcs/publication-source.

Availability counts describe source fields across the complete databases, not populated workbook cells or qualifying-study coverage. Direct facts, derived values, review decisions and unresolved fields remain distinct.

## [WM2] Column mapping

### Publications

| Exact workbook header | Evidence / transformation | Status |
|---|---|---|
| publication_id | Generate an internal publication key while preserving ORCS PUBLICATION_ID and exact SOURCE_TYPE/SOURCE_ID; retain the ID mapping. | Derived |
| title_original | Publication TITLE; available for 418/418 records. | Reported |
| publication_type_reported | SOURCE_TYPE identifies the native source namespace (including prepub); it does not establish article/review/publication type. | Unresolved |
| journal_reported | Publication JOURNAL; available for 411/418 records. | Reported |
| publication_year | Extract the year from reported PUBLICATION_DATE; retain the original full date as evidence. | Derived |
| author_list_ reported | Publication AUTHORS; available for 418/418 records. | Reported |
| pmid | Publication PMID; available for 412/418 records. PMID is promoted only when cached and page-reported identifiers agree. | Reported |
| pmid_link | Build the corresponding URL from the supported PMID/DOI; a generated URL is not a fetched record. | Derived |
| pmcid | No structured PMCID field was obtained from the ORCS publication headers; do not derive it from a PMID. | Unresolved |
| pmc_link | No structured PMCID field was obtained from the ORCS publication headers; do not derive it from a PMID. | Unresolved |
| doi | Publication DOI; available for 5/418 records. DOI-format cached SOURCE_ID only; prepub URLs remain preserved separately. | Reported |
| doi_link | Build the corresponding URL from the supported PMID/DOI; a generated URL is not a fetched record. | Derived |
| retrival_sources | ORCS website publication header plus cached screen/source-identity association. | Provenance |
| evidence_status | Record reported, unresolved or conflicting status from field-specific source checks; preserve source review issues. | Derived |
| publication_notes | Preserve ABSTRACT, PUBLICATION_DATE, ORCS PUBLICATION_ID, raw source assertions, supplementary links and REVIEW_ISSUES; do not flatten source conflicts. | Reported + provenance |

### Screen Groups

| Exact workbook header | Evidence / transformation | Status |
|---|---|---|
| screen_group_id | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| publication_id | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| group_name_curated | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| group_name_reported | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| group_stage_normalized | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| group_objective_curated | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| perturbation_type_normalized | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| library_name_reported | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| library_scope_normalized | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| experimental_setting_normalized | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| shared_design_summary | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| source_evidence_ids | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| curation_status | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |
| group_notes | Shared experimental objective/design must be established by review; do not create one group per ORCS publication. | Review required |

### Screens

| Exact workbook header | Evidence / transformation | Status |
|---|---|---|
| screen_id | Generate an internal screen key while retaining native SCREEN_ID. | Derived |
| screen_group_id | Publication membership does not establish shared experimental design; grouping requires review. | Review required |
| publication_id | Join SCREEN_ID through publication-screen-links to the publication ID mapping. This is a direct publication association, not a dataset attribution. | Reported relationship + derived key |
| screen_name_curated | Neither shared database supplies a defensible direct value for this field. | Unresolved |
| screen_name_reported | Screen SCREEN_NAME; non-placeholder values in 2217/2217 records. | Reported |
| screen_category_normalized | Neither shared database supplies a defensible direct value for this field. | Unresolved |
| experimental_setting_normalized | EXPERIMENTAL_SETUP and NOTES may support interpretation; a reviewed crosswalk is needed. | Review required |
| screen_format_normalized | Explicit reviewed SCREEN_FORMAT crosswalk (Pool -> pooled; Array -> arrayed); leave unsupported values unmapped. | Derived |
| perturbation_type_normalized | Explicit reviewed METHODOLOGY crosswalk (Knockout -> CRISPR knockout); retain original methodology. | Derived |
| methodology_reported | Screen METHODOLOGY; non-placeholder values in 2217/2217 records. | Reported |
| enzyme_reported | Screen ENZYME; non-placeholder values in 2217/2217 records. | Reported |
| library_name_reported | Screen LIBRARY; non-placeholder values in 2217/2217 records. | Reported |
| library_type_reported | Screen LIBRARY_TYPE; non-placeholder values in 2217/2217 records. | Reported |
| library_scope_normalized | Neither shared database supplies a defensible direct value for this field. | Unresolved |
| library_gene_count_reported | FULL_SIZE/SCORES_SIZE describe screen result metadata; they do not establish library gene or guide counts. | Unresolved |
| library_guide_count_reported | FULL_SIZE/SCORES_SIZE describe screen result metadata; they do not establish library gene or guide counts. | Unresolved |
| perturbed_population_reported | CELL_LINE/CELL_TYPE, EXPERIMENTAL_SETUP and NOTES are candidate evidence; structured participant roles, ratios and co-culture assignments are not established automatically. | Review / additional evidence |
| interacting_population_reported | CELL_LINE/CELL_TYPE, EXPERIMENTAL_SETUP and NOTES are candidate evidence; structured participant roles, ratios and co-culture assignments are not established automatically. | Review / additional evidence |
| cell_line_reported | Screen CELL_LINE; non-placeholder values in 2217/2217 records. | Reported |
| organism_reported | Screen ORGANISM_OFFICIAL; non-placeholder values in 2217/2217 records. | Reported |
| disease_context_normalized | CELL_LINE can join saved Cellosaurus categories/descriptions; a cancer-cell-line category is not automatically a study-level disease context. | Reference + review required |
| immune_interaction_mode_normalized | CELL_LINE/CELL_TYPE, EXPERIMENTAL_SETUP and NOTES are candidate evidence; structured participant roles, ratios and co-culture assignments are not established automatically. | Review / additional evidence |
| immune_cell_population_reported | CELL_LINE/CELL_TYPE, EXPERIMENTAL_SETUP and NOTES are candidate evidence; structured participant roles, ratios and co-culture assignments are not established automatically. | Review / additional evidence |
| immune_cell_population_normalized | CELL_LINE/CELL_TYPE, EXPERIMENTAL_SETUP and NOTES are candidate evidence; structured participant roles, ratios and co-culture assignments are not established automatically. | Review / additional evidence |
| coculture_configuration_normalized | CELL_LINE/CELL_TYPE, EXPERIMENTAL_SETUP and NOTES are candidate evidence; structured participant roles, ratios and co-culture assignments are not established automatically. | Review / additional evidence |
| effector_target_ratio_reported | CELL_LINE/CELL_TYPE, EXPERIMENTAL_SETUP and NOTES are candidate evidence; structured participant roles, ratios and co-culture assignments are not established automatically. | Review / additional evidence |
| condition_name_reported | Screen CONDITION_NAME; non-placeholder values in 1013/2217 records. | Reported |
| condition_dosage_reported | Screen CONDITION_DOSAGE; non-placeholder values in 803/2217 records. | Reported |
| duration_reported | Screen DURATION; non-placeholder values in 2196/2217 records. | Reported |
| comparator_reported | Neither shared database supplies a defensible direct value for this field. | Unresolved |
| phenotype_original | Screen PHENOTYPE; non-placeholder values in 2217/2217 records. | Reported |
| readout_reported | Neither shared database supplies a defensible direct value for this field. | Unresolved |
| replicate_design_reported | Neither shared database supplies a defensible direct value for this field. | Unresolved |
| statistical_analysis_reported | Screen ANALYSIS; non-placeholder values in 2217/2217 records. | Reported |
| source_evidence_ids | Generate references to screen metadata, publication associations and any separately joined reference annotations. | Derived |
| curation_status | Owner/pipeline review state, independent of source facts; reviewer entry columns remain rightmost. | Review bookkeeping |
| screen_notes | Preserve SCREEN_ID, SCREEN_RATIONALE, NOTES, EXPERIMENTAL_SETUP, MOI, SCREEN_TYPE, significance metadata and FULL_SIZE with their native meanings. | Reported |
| immune_context_notes | CELL_LINE/CELL_TYPE, EXPERIMENTAL_SETUP and NOTES are candidate evidence; structured participant roles, ratios and co-culture assignments are not established automatically. | Review / additional evidence |
| reviewer_decision | Owner/pipeline review state, independent of source facts; reviewer entry columns remain rightmost. | Review bookkeeping |
| reviewer_notes | Owner/pipeline review state, independent of source facts; reviewer entry columns remain rightmost. | Review bookkeeping |

### Datasets

| Exact workbook header | Evidence / transformation | Status |
|---|---|---|
| dataset_id | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| publication_id | A publication association can be recorded after an actual dataset has been identified; publication /Dataset/ page IDs are not dataset IDs. | Unresolved |
| repository_normalized | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| accession_reported | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| accession_level_normalized | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| parent_accession_reported | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| title_original | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| description_reported | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| dataset_type_normalized | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| experiment_type_reported | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| organism_reported | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| sample_count_reported | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| bioproject_accession | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| sra_study_accession | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| raw_data_available | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| processed_data_available | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| screen_data_available | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| library_definition_available | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| availability_reported | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| dataset_url | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| supporting_asset_urls_reported | Publication SUPPLEMENTARY_FILES supplies asset URLs/labels. Keep them as publication-associated asset mentions until a defined dataset attribution supports this field. | Asset metadata only |
| source_evidence_ids | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| attribution_status | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |
| dataset_notes | ORCS publication records and supplementary links do not establish a repository dataset identity or its availability. | Unresolved |

### Screen-Dataset Links

| Exact workbook header | Evidence / transformation | Status |
|---|---|---|
| link_id | No exact screen-repository dataset relation is established by either shared database; retain unresolved status until explicit evidence supports one. | Unresolved |
| screen_id | No exact screen-repository dataset relation is established by either shared database; retain unresolved status until explicit evidence supports one. | Unresolved |
| dataset_id | No exact screen-repository dataset relation is established by either shared database; retain unresolved status until explicit evidence supports one. | Unresolved |
| relationship_type_normalized | No exact screen-repository dataset relation is established by either shared database; retain unresolved status until explicit evidence supports one. | Unresolved |
| evidence_basis | No exact screen-repository dataset relation is established by either shared database; retain unresolved status until explicit evidence supports one. | Unresolved |
| evidence_source_id | No exact screen-repository dataset relation is established by either shared database; retain unresolved status until explicit evidence supports one. | Unresolved |
| evidence_locator | No exact screen-repository dataset relation is established by either shared database; retain unresolved status until explicit evidence supports one. | Unresolved |
| attribution_status | No exact screen-repository dataset relation is established by either shared database; retain unresolved status until explicit evidence supports one. | Unresolved |
| link_notes | No exact screen-repository dataset relation is established by either shared database; retain unresolved status until explicit evidence supports one. | Unresolved |

### Sources & Evidence

| Exact workbook header | Evidence / transformation | Status |
|---|---|---|
| evidence_id | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |
| source_type_normalized | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |
| source_name | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |
| native_record_id | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |
| retrieved_at | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |
| retrieval_method | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |
| tool_or_package | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |
| source_locator | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |
| evidence_text_summary | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |
| supports_entity_type | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |
| supports_entity_id | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |
| evidence_status | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |
| evidence_notes | Use native screen/publication identifiers, original field paths/header locators, saved files, SHA-256 hashes and UTC request receipts; generate evidence keys and supported entity references. | Provenance + derived keys |

### Discovery Resources

| Exact workbook header | Evidence / transformation | Status |
|---|---|---|
| resource_name | Use the screen/publication manifests and receipts to report resource, tool/version, metadata access, actual counts and limitations; this catalog build is not a filtered discovery run. | Provenance |
| resource_type | Use the screen/publication manifests and receipts to report resource, tool/version, metadata access, actual counts and limitations; this catalog build is not a filtered discovery run. | Provenance |
| programmatic_access | Use the screen/publication manifests and receipts to report resource, tool/version, metadata access, actual counts and limitations; this catalog build is not a filtered discovery run. | Provenance |
| access_method | Use the screen/publication manifests and receipts to report resource, tool/version, metadata access, actual counts and limitations; this catalog build is not a filtered discovery run. | Provenance |
| authentication_required | Original screen REST retrieval used a key; public publication headers and browse metadata did not. Preserve that distinction. | Provenance |
| queried_in_this_version | Use the screen/publication manifests and receipts to report resource, tool/version, metadata access, actual counts and limitations; this catalog build is not a filtered discovery run. | Provenance |
| publications_discovered | Catalog counts describe resource inventory, not qualifying discoveries. A future search must report its own direct-hit counts. | Run-dependent |
| datasets_discovered | Catalog counts describe resource inventory, not qualifying discoveries. A future search must report its own direct-hit counts. | Run-dependent |
| screens_discovered | Catalog counts describe resource inventory, not qualifying discoveries. A future search must report its own direct-hit counts. | Run-dependent |
| unique_contribution | Use the screen/publication manifests and receipts to report resource, tool/version, metadata access, actual counts and limitations; this catalog build is not a filtered discovery run. | Provenance |
| limitations | Use the screen/publication manifests and receipts to report resource, tool/version, metadata access, actual counts and limitations; this catalog build is not a filtered discovery run. | Provenance |
| documentation_url | Use the screen/publication manifests and receipts to report resource, tool/version, metadata access, actual counts and limitations; this catalog build is not a filtered discovery run. | Provenance |
| discovery_resources_notes | Use the screen/publication manifests and receipts to report resource, tool/version, metadata access, actual counts and limitations; this catalog build is not a filtered discovery run. | Provenance |

## [WM3] Review checkpoints

1. Integrate these sources through native ID mappings and field-level evidence, preserving cached/page identifier conflicts.
2. Keep screen, publication and supporting-asset entities distinct. ORCS /Dataset/ pages describe publications.
3. Resolve scientific normalization and screen grouping only through reviewed rules.
4. Generate any future workbook as a new version, preserving reviewer entries and source identifiers.

[Enrichment plan](enrichment-plan.md) describes the local integration stage and evidence that remains unavailable.
