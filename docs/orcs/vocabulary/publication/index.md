---
field: "publication fields"
entity: publication
entity_source: BioGRID ORCS cached metadata
unique_values: 14
description_basis: "hand-authored by Perplexity"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, publication]
---

# ORCS publication fields

Source: `data/orcs/publication-index.json` (418 publications). Fields such as TITLE, AUTHORS, PMID, and URLs are self-explanatory and are not described here.

## Fields

| Field | Technical definition | Plain-language note | Where it goes in DeathMap |
|---|---|---|---|
| `PUBLICATION_ID` | ORCS internal publication (dataset) identifier; the URL is https://orcs.thebiogrid.org/Dataset/<id>. |  | Sources & Evidence.native_record_id |
| `SOURCE_TYPE` | 'pubmed' or 'prepub'; see the screen vocabulary. | Whether the paper is published or a preprint. | Publications.publication_type_reported (candidate) |
| `ABSTRACT` | Abstract text from PubMed. Main free-text input for later screen-category and immune-context extraction. | The paper's summary paragraph. | Not stored in the workbook; evidence input |
| `JOURNAL` | Journal name as given by PubMed (often the abbreviated or ISO form). |  | Publications.journal_reported |
| `PUBLICATION_DATE` | Publication date (YYYY-MM-DD) from PubMed; the year feeds publication_year. |  | Publications.publication_year |
| `PAGE_SOURCE_TYPE / PAGE_SOURCE_ID` | Identifier type and value shown on the ORCS publication page; normally identical to SOURCE_TYPE / SOURCE_ID. A mismatch is a review issue. |  | Exception review only |
| `DOI` | Digital Object Identifier, if ORCS exposes it; often null in ORCS and filled later by bibliographic enrichment. |  | Publications.doi |
| `SUPPLEMENTARY_FILES` | List of {label, url} for supplementary files hosted by ORCS (usually author tables of gene scores). These are supporting assets, not repository datasets. | Extra data files from the paper that ORCS keeps a copy of. | Datasets.supporting_asset_urls_reported (as ORCS-hosted assets) |
| `LINKS` | List of {label, url} links shown on the ORCS page: always 'Pubmed' and 'Google Scholar', plus any supplementary-file links. |  | Publications.pmid_link |
| `SCREEN_IDS / SCREEN_COUNT` | ORCS screen IDs belonging to this publication, and their count. | How many screens the paper contains in ORCS. | Screen Groups (candidate grouping input); Screen-Dataset Links context |
| `PUBLICATION_URL` | ORCS publication page URL. |  | Sources & Evidence.source_locator |
| `FIELD_LOCATORS` | Pipeline-added map from each field to where on the ORCS page it was read. |  | JSON evidence ledger only |
| `REVIEW_ISSUES` | Pipeline-added list of detected problems (e.g., identifier mismatch, missing DOI). |  | Exception review |
| `RETRIEVED_AT / SOURCE_METADATA_FILE / SOURCE_METADATA_SHA256` | Pipeline-added retrieval provenance. |  | JSON evidence ledger only |

## SOURCE_TYPE values

| Value | Publications | Technical | Plain-language |
|---|---:|---|---|
| `pubmed` | 412 | SOURCE_ID is a PubMed identifier (PMID) for a peer-reviewed or indexed publication. | The screen comes from a published paper listed in PubMed, the main index of biomedical papers. |
| `prepub` | 6 | SOURCE_ID refers to a preprint or pre-publication record not yet indexed with a PMID. | The screen comes from a paper that was shared before formal peer review (a preprint). |

## SUPPLEMENTARY_FILES by file type

ORCS-hosted supplementary files are supporting assets (usually author gene-score tables). Under pilot-scope PS12 their contents are not downloaded during discovery.

| Extension | Files |
|---|---:|
| `.xlsx` | 489 |
| `.txt` | 41 |
| `.pdf` | 26 |
| `.csv` | 20 |
| `.xls` | 11 |
| `.docx` | 7 |
| `.xlsb` | 6 |
| `.tsv` | 4 |
| `.jpg` | 1 |
| `.png` | 1 |
| `.xlsm` | 1 |

## REVIEW_ISSUES values

| Value | Publications | Meaning |
|---|---:|---|
| Page-labelled source identifier differs from cached SOURCE_TYPE/SOURCE_ID; both preserved. | 6 | The ORCS page shows a different identifier than the cached screen index. Both are kept and the reviewer decides which is the version of record. |

DOI is missing for 413 of 418 publications in ORCS; it will be filled by bibliographic enrichment.

