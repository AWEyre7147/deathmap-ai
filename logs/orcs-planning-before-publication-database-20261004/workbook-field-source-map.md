# Workbook field-source map

## [WM1] Scope and reading guide

Every header below is copied exactly from the saved workbook, including historical spellings. Counts describe populated cells in the existing 20261003T173643920687Z run, not retrieval coverage. No cells were edited. Blank cells remain unknown unless an explicit source and interpretation support them.

The workbook has 92 publications, 1,176 screens, 2,349 evidence rows and two resource rows. Screen Groups, Datasets and Screen-Dataset Links have no rows. The filter has 1,020 direct hits; context and unresolved records are distinct roles.

Direct = reported metadata; derived = transparent identifiers, links, crosswalks or run bookkeeping. Proposed sources are a plan requiring review, not completed enrichment. The Cellosaurus cancer category remains in reference evidence; it is not silently copied into disease_context_normalized because the annotation describes a cell-line category rather than a study-level disease interpretation.

## [WM2] Columns

### Publications

92 existing rows.

| Exact workbook header | Populated cells | Current source or reason blank | Next candidate source / decision |
|---|---:|---|---|
| publication_id | 92 | Derived stable ID and exact SOURCE_TYPE/SOURCE_ID association; no inferred dataset relationship. | No additional source needed for current meaning. |
| title_original | 0 | Unresolved; not supplied by the current projection. | ORCS publication page for title/authors/journal/date; type and PMCID require explicit evidence. |
| publication_type_reported | 0 | Unresolved; not supplied by the current projection. | ORCS publication page for title/authors/journal/date; type and PMCID require explicit evidence. |
| journal_reported | 0 | Unresolved; not supplied by the current projection. | ORCS publication page for title/authors/journal/date; type and PMCID require explicit evidence. |
| publication_year | 0 | Unresolved; not supplied by the current projection. | ORCS publication page for title/authors/journal/date; type and PMCID require explicit evidence. |
| author_list_ reported | 0 | Unresolved; not supplied by the current projection. | ORCS publication page for title/authors/journal/date; type and PMCID require explicit evidence. |
| pmid | 92 | Direct SOURCE_ID when SOURCE_TYPE=pubmed. | No additional source needed for current meaning. |
| pmid_link | 92 | Derived PubMed URL from reported PMID; page not retrieved. | No additional source needed for current meaning. |
| pmcid | 0 | Unresolved; not supplied by the current projection. | ORCS publication page for title/authors/journal/date; type and PMCID require explicit evidence. |
| pmc_link | 0 | Unresolved; not supplied by the current projection. | ORCS publication page for title/authors/journal/date; type and PMCID require explicit evidence. |
| doi | 0 | Direct SOURCE_ID when SOURCE_TYPE=doi. | No additional source needed for current meaning. |
| doi_link | 0 | Derived DOI URL; no bibliographic lookup. | No additional source needed for current meaning. |
| retrival_sources | 92 | Run provenance: BioGRID ORCS cached metadata. | No additional source needed for current meaning. |
| evidence_status | 92 | Explicit pipeline evidence status; not a quality score. | No additional source needed for current meaning. |
| publication_notes | 92 | Reported SOURCE_TYPE/SOURCE_ID and abbreviated AUTHOR attribution; not full author list. | No additional source needed for current meaning. |

### Screen Groups

0 existing rows.

| Exact workbook header | Populated cells | Current source or reason blank | Next candidate source / decision |
|---|---:|---|---|
| screen_group_id | 0 | No justified screen grouping has been established. | Review shared design before generating groups. |
| publication_id | 0 | Derived stable ID and exact SOURCE_TYPE/SOURCE_ID association; no inferred dataset relationship. | No additional source needed for current meaning. |
| group_name_curated | 0 | Unresolved; not supplied by the current projection. | Owner-reviewed shared experimental design; publication membership alone is insufficient. |
| group_name_reported | 0 | Unresolved; not supplied by the current projection. | Owner-reviewed shared experimental design; publication membership alone is insufficient. |
| group_stage_normalized | 0 | Unresolved; not supplied by the current projection. | Owner-reviewed shared experimental design; publication membership alone is insufficient. |
| group_objective_curated | 0 | Unresolved; not supplied by the current projection. | Owner-reviewed shared experimental design; publication membership alone is insufficient. |
| perturbation_type_normalized | 0 | Explicit METHODOLOGY crosswalk: Knockout -> CRISPR knockout. | No additional source needed for current meaning. |
| library_name_reported | 0 | Unresolved; not supplied by the current projection. | Owner-reviewed shared experimental design; publication membership alone is insufficient. |
| library_scope_normalized | 0 | Unresolved; not supplied by the current projection. | Owner-reviewed shared experimental design; publication membership alone is insufficient. |
| experimental_setting_normalized | 0 | Unresolved; not supplied by the current projection. | Owner-reviewed shared experimental design; publication membership alone is insufficient. |
| shared_design_summary | 0 | Unresolved; not supplied by the current projection. | Owner-reviewed shared experimental design; publication membership alone is insufficient. |
| source_evidence_ids | 0 | Derived references to saved ORCS and annotation evidence rows. | No additional source needed for current meaning. |
| curation_status | 0 | Run role plus unreviewed status; not scientific eligibility. | No additional source needed for current meaning. |
| group_notes | 0 | Unresolved; not supplied by the current projection. | Owner-reviewed shared experimental design; publication membership alone is insufficient. |

### Screens

1,176 existing rows.

| Exact workbook header | Populated cells | Current source or reason blank | Next candidate source / decision |
|---|---:|---|---|
| screen_id | 1176 | Derived stable ID from ORCS SCREEN_ID; native identifier retained in notes/evidence. | No additional source needed for current meaning. |
| screen_group_id | 0 | No justified screen grouping has been established. | Review shared design before generating groups. |
| publication_id | 1175 | Derived stable ID and exact SOURCE_TYPE/SOURCE_ID association; no inferred dataset relationship. | No additional source needed for current meaning. |
| screen_name_curated | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| screen_name_reported | 1176 | Direct ORCS SCREEN_NAME. | No additional source needed for current meaning. |
| screen_category_normalized | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| experimental_setting_normalized | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| screen_format_normalized | 1155 | Explicit SCREEN_FORMAT crosswalk: Pool -> pooled; Array -> arrayed. | No additional source needed for current meaning. |
| perturbation_type_normalized | 1175 | Explicit METHODOLOGY crosswalk: Knockout -> CRISPR knockout. | No additional source needed for current meaning. |
| methodology_reported | 1176 | Direct ORCS METHODOLOGY. | No additional source needed for current meaning. |
| enzyme_reported | 1176 | Direct ORCS ENZYME. | No additional source needed for current meaning. |
| library_name_reported | 1176 | Direct ORCS LIBRARY. | No additional source needed for current meaning. |
| library_type_reported | 1176 | Direct ORCS LIBRARY_TYPE. | No additional source needed for current meaning. |
| library_scope_normalized | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| library_gene_count_reported | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| library_guide_count_reported | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| perturbed_population_reported | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| interacting_population_reported | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| cell_line_reported | 1176 | Direct ORCS CELL_LINE. | No additional source needed for current meaning. |
| organism_reported | 1176 | Direct ORCS ORGANISM_OFFICIAL. | No additional source needed for current meaning. |
| disease_context_normalized | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| immune_interaction_mode_normalized | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| immune_cell_population_reported | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| immune_cell_population_normalized | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| coculture_configuration_normalized | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| effector_target_ratio_reported | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| condition_name_reported | 176 | Direct ORCS CONDITION_NAME. | No additional source needed for current meaning. |
| condition_dosage_reported | 103 | Direct ORCS CONDITION_DOSAGE. | No additional source needed for current meaning. |
| duration_reported | 1162 | Direct ORCS DURATION. | No additional source needed for current meaning. |
| comparator_reported | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| phenotype_original | 1176 | Direct ORCS PHENOTYPE. | No additional source needed for current meaning. |
| readout_reported | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| replicate_design_reported | 0 | Unresolved; not supplied by the current projection. | ORCS screen-page metadata plus owner interpretation; compare with cached fields first. Detailed methods may require a later publication stage. |
| statistical_analysis_reported | 1176 | Direct ORCS ANALYSIS. | No additional source needed for current meaning. |
| source_evidence_ids | 1176 | Derived references to saved ORCS and annotation evidence rows. | No additional source needed for current meaning. |
| curation_status | 1176 | Run role plus unreviewed status; not scientific eligibility. | No additional source needed for current meaning. |
| screen_notes | 1176 | Native SCREEN_ID, role, design/notes/significance fields and review issues; preserves reported text. | No additional source needed for current meaning. |
| immune_context_notes | 1176 | Pipeline statement that immune context is unresolved, not a source observation. | No additional source needed for current meaning. |
| reviewer_decision | 0 | Owner entry; intentionally blank pending review. | Owner workbook review; reviewer columns remain at far right. |
| reviewer_notes | 0 | Owner entry; intentionally blank pending review. | Owner workbook review; reviewer columns remain at far right. |

### Datasets

0 existing rows.

| Exact workbook header | Populated cells | Current source or reason blank | Next candidate source / decision |
|---|---:|---|---|
| dataset_id | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| publication_id | 0 | Derived stable ID and exact SOURCE_TYPE/SOURCE_ID association; no inferred dataset relationship. | No additional source needed for current meaning. |
| repository_normalized | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| accession_reported | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| accession_level_normalized | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| parent_accession_reported | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| title_original | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| description_reported | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| dataset_type_normalized | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| experiment_type_reported | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| organism_reported | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| sample_count_reported | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| bioproject_accession | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| sra_study_accession | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| raw_data_available | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| processed_data_available | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| screen_data_available | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| library_definition_available | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| availability_reported | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| dataset_url | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| supporting_asset_urls_reported | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| source_evidence_ids | 0 | Derived references to saved ORCS and annotation evidence rows. | No additional source needed for current meaning. |
| attribution_status | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |
| dataset_notes | 0 | Unresolved; not supplied by the current projection. | Explicit dataset identity/availability evidence; source supplement URL alone is insufficient. External repository attribution is a separate later stage. |

### Screen-Dataset Links

0 existing rows.

| Exact workbook header | Populated cells | Current source or reason blank | Next candidate source / decision |
|---|---:|---|---|
| link_id | 0 | Unresolved; not supplied by the current projection. | Screen-specific evidence connecting a defined dataset to the screen; preserve uncertainty. |
| screen_id | 0 | Derived stable ID from ORCS SCREEN_ID; native identifier retained in notes/evidence. | No additional source needed for current meaning. |
| dataset_id | 0 | Unresolved; not supplied by the current projection. | Screen-specific evidence connecting a defined dataset to the screen; preserve uncertainty. |
| relationship_type_normalized | 0 | Unresolved; not supplied by the current projection. | Screen-specific evidence connecting a defined dataset to the screen; preserve uncertainty. |
| evidence_basis | 0 | Unresolved; not supplied by the current projection. | Screen-specific evidence connecting a defined dataset to the screen; preserve uncertainty. |
| evidence_source_id | 0 | Unresolved; not supplied by the current projection. | Screen-specific evidence connecting a defined dataset to the screen; preserve uncertainty. |
| evidence_locator | 0 | Unresolved; not supplied by the current projection. | Screen-specific evidence connecting a defined dataset to the screen; preserve uncertainty. |
| attribution_status | 0 | Unresolved; not supplied by the current projection. | Screen-specific evidence connecting a defined dataset to the screen; preserve uncertainty. |
| link_notes | 0 | Unresolved; not supplied by the current projection. | Screen-specific evidence connecting a defined dataset to the screen; preserve uncertainty. |

### Sources & Evidence

2,349 existing rows.

| Exact workbook header | Populated cells | Current source or reason blank | Next candidate source / decision |
|---|---:|---|---|
| evidence_id | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |
| source_type_normalized | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |
| source_name | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |
| native_record_id | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |
| retrieved_at | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |
| retrieval_method | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |
| tool_or_package | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |
| source_locator | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |
| evidence_text_summary | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |
| supports_entity_type | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |
| supports_entity_id | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |
| evidence_status | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |
| evidence_notes | 2349 | Saved ORCS/reference evidence and run provenance; IDs, locators and relationships derived explicitly. | No additional source needed for current meaning. |

### Discovery Resources

2 existing rows.

| Exact workbook header | Populated cells | Current source or reason blank | Next candidate source / decision |
|---|---:|---|---|
| resource_name | 2 | Run resource bookkeeping and limitations. | No additional source needed for current meaning. |
| resource_type | 2 | Run resource bookkeeping and limitations. | No additional source needed for current meaning. |
| programmatic_access | 1 | Run resource bookkeeping and limitations. | No additional source needed for current meaning. |
| access_method | 2 | Run resource bookkeeping and limitations. | No additional source needed for current meaning. |
| authentication_required | 0 | Not recorded in the current projection. | Resource documentation; distinguish original authenticated retrieval from offline reuse. |
| queried_in_this_version | 2 | Run resource bookkeeping and limitations. | No additional source needed for current meaning. |
| publications_discovered | 1 | Run resource bookkeeping and limitations. | No additional source needed for current meaning. |
| datasets_discovered | 1 | Run resource bookkeeping and limitations. | No additional source needed for current meaning. |
| screens_discovered | 1 | Run resource bookkeeping and limitations. | No additional source needed for current meaning. |
| unique_contribution | 1 | Run resource bookkeeping and limitations. | No additional source needed for current meaning. |
| limitations | 2 | Run resource bookkeeping and limitations. | No additional source needed for current meaning. |
| documentation_url | 1 | Run resource bookkeeping and limitations. | No additional source needed for current meaning. |
| discovery_resources_notes | 2 | Run resource bookkeeping and limitations. | No additional source needed for current meaning. |

## [WM3] Review checkpoints

1. Review direct hits, unresolved categories and context separately; workbook counts are not hit counts.
2. Agree publication and screen enrichment scope before retrieval.
3. Preserve stable IDs and native ORCS identifiers. A future display-index change must not break evidence links.
4. Decide screen groups and dataset attribution only with explicit evidence. FULL_SIZE is not a library gene/guide or sample count.

See [enrichment plan](enrichment-plan.md), [output field definitions](output-fields.md) and the saved run projection.json for exact current mappings.
