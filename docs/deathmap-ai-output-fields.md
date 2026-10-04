---
aliases:
  - DeathMap-AI output fields
tags:
  - deathmap-ai
  - data-dictionary
  - provenance
---

# DeathMap-AI discovery and review fields

This data dictionary describes the pilot's standardized fields. The design keeps
source claims, derived discovery logic, and human review separate so later
reasoning can cite the evidence behind each relationship.

| Field | Ownership | Description | Why it is retained |
|---|---|---|---|
| `record_id` | DeathMap-AI | Stable identifier for one resource result in one run. | Preserves individual retrieval observations. |
| `run_id` | DeathMap-AI | Search execution identifier. | Reproducibility and version comparison. |
| `resource_name` | DeathMap-AI | Resource that supplied the result. | Provenance and per-resource evaluation. |
| `resource_version` | source/run | Resource version when available. | Reproducibility. |
| `retrieved_at` | run | Retrieval timestamp. | Time-specific provenance. |
| `query_strategy_id` | DeathMap-AI | Versioned retrieval and matching strategy. | Separates changes in search behavior. |
| `native_record_id` | source | Source database identifier. | Links back to the native record. |
| `native_url` | derived link | Source landing-page URL built from the native identifier. | Manual verification. |
| `candidate_type` | DeathMap-AI | Entity type represented by the record, currently `screen` for ORCS. | Keeps screens distinct from publications and datasets. |
| `title_original` | source | Publication or record title when the source provides one. | Preserves source wording; null is meaningful. |
| `screen_name_reported` | source | Screen name supplied by ORCS. | Prevents a screen name from being used as a publication title. |
| `pmid_reported` | source claim | PMID supplied through a typed ORCS source identifier. | Candidate publication link, pending review. |
| `doi_reported` | source claim | DOI supplied by the resource when available. | Candidate publication deduplication. |
| `accessions_reported` | source claim | Dataset accessions supplied by the resource. | Candidate dataset links, not proof of attribution. |
| `evidence_text_original` | source/derived | Matched text, rule, and source field that produced the candidate. | Explains why the result was retrieved. |
| `inclusion_basis` | DeathMap-AI | `direct_rule_match` or `publication_sibling_context`. | Distinguishes direct discovery evidence from sibling controls. |
| `anchor_screen_ids` | derived relationship | Candidate direct co-culture screen anchors that caused publication expansion. | Auditable screen-family relationship. |
| `screen_format_reported` | source | ORCS screen format. | Pooled/arrayed classification evidence. |
| `experimental_setup_reported` | source | ORCS experimental setup. | Experiment classification evidence. |
| `condition_name_reported` | source | ORCS condition. | Co-culture, cytokine, control, or other context. |
| `condition_dosage_reported` | source | ORCS dose or ratio. | Contrast definition. |
| `library_name_reported` | source | ORCS library name. | Library identity and scope evidence. |
| `library_type_reported` | source | ORCS library/modality type. | Perturbation classification. |
| `library_size_reported` | source | ORCS `FULL_SIZE` value. Its unit is not inferred. | Preserves potentially useful coverage metadata safely. |
| `methodology_reported` | source | ORCS methodology. | Knockout/activation/inhibition distinction. |
| `enzyme_reported` | source | ORCS enzyme or nuclease. | Cas9/Cas12a and future enzyme-aware searches. |
| `cell_line_reported` | source | ORCS cell-line wording. | Biological model evidence. |
| `cell_type_reported` | source | ORCS broader cell type. | Normalization input. |
| `phenotype_original` | source | Original ORCS phenotype. | Preserves the source term before harmonization. |
| `organism_reported` | source | ORCS organism name or identifier. | Species eligibility and normalization. |
| `raw_response_ref` | DeathMap-AI | Relative path to the preserved native response. | Audit trail. |
| `source_metadata` | source | Complete native record. | Prevents lossy transformation. |
| `screen_evidence_role_reviewed` | reviewer | Reviewed role such as direct co-culture anchor, comparator, or control. | Scientific relationship semantics. |
| `perturbed_population_reviewed` | reviewer | Population receiving the CRISPR perturbation. | Directional biological reasoning. |
| `interacting_population_reviewed` | reviewer | Co-cultured or interacting population. | Cell-cell relationship modeling. |
| `library_scope_reviewed` | reviewer | Genome-wide, near-genome-wide, partial/custom, targeted, or unclear. | Library breadth without using it as an eligibility gate. |
| `library_scope_evidence` | reviewer | Source supporting the reviewed library scope. | Traceable normalization. |
| `phenotype_normalized` | reviewer | Harmonized phenotype category. | Cross-study comparison without overwriting the source. |
| `review_status` | reviewer/workflow | Current adjudication state. | Separates candidates from accepted evidence. |
| `reviewer_notes` | reviewer | Free-text scientific qualification or unresolved issue. | Preserves nuance and conflicts. |

## [DF1] Relationship pattern

```text
Publication anchor
  -> direct co-culture screen anchor
  -> publication sibling screen or control
  -> reported supplementary asset
  -> reported dataset/accession
```

Every arrow is an evidence link with its own source and review status. Sharing a
publication does not prove that a dataset contains a particular screen.

## [DF2] Proposed supporting-asset fields

The ORCS pilot has exposed supplementary files that may later connect a
publication or screen to additional evidence. The following fields are proposed
for that relationship and are not yet part of the standard discovery record:

| Proposed field | Description |
|---|---|
| `supporting_asset_type` | Supplementary workbook, supplementary PDF, repository record, or another asset type. |
| `supporting_asset_url_reported` | URL exposed by the source resource. |
| `supporting_asset_availability` | Reported, reachable, unavailable, restricted, or unresolved. |
| `supporting_asset_access_checked_at` | Date and time accessibility was tested, when tested. |
| `supporting_asset_scope` | Brief description of the tables or evidence the asset contains. |
| `supporting_asset_relationship` | Publication-level, screen-group-level, screen-level, or unresolved link. |
| `supporting_asset_evidence_source` | ORCS screen/page or other source that exposed the relationship. |

These fields would let a future reasoning layer know that an asset exists and
how it is linked without requiring the pilot to ingest its experimental data.
