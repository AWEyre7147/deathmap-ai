---
aliases:
  - ORCS ontology accessions
tags:
  - deathmap-ai
  - orcs
  - provenance
  - ontology
---

# ORCS ontology-accession enrichment

## [OA1] Purpose

The native ORCS `screens` response contains normalized cell-line, cell-type,
condition, and phenotype names but not the external identifiers displayed on
the corresponding ORCS screen pages. This enrichment preserves those
ORCS-displayed identifiers separately from the native metadata.

## [OA2] Source and run

- Source: `https://orcs.thebiogrid.org/Screen/{SCREEN_ID}`
- Retrieval date: 2026-09-06
- ORCS site version displayed during retrieval: 2.0.18.1
- Screen pages requested: 2,217
- Screen pages retrieved successfully: 2,217
- Pages displaying at least one mapped accession: 2,193
- Elapsed time: 54.61 seconds
- Experimental or gene-level screen data downloaded: no

The local JSON and CSV enrichment records preserve the ORCS screen identifier,
screen URL, retrieval time, and field-specific accessions.

## [OA3] Identifier systems observed

ORCS linked identifiers from the following prefixes through the EMBL-EBI
Ontology Lookup Service:

`APO`, `BTO`, `CL`, `CLO`, `CMPO`, `COVOC`, `DEPMAP`, `EFO`, `GENBANK`, `GO`,
and `TAXID`.

ORCS also linked `CELLOSAURUS` identifiers directly to Cellosaurus. No other
external identifier service was observed in the parsed screen-detail fields.

## [OA4] Field coverage

| ORCS page field | Identifier destination | Screens with an accession |
|---|---|---:|
| Condition | OLS | 9 |
| Cell Line | OLS | 1,844 |
| Cell Line | Cellosaurus | 2,013 |
| Cell Type | OLS | 2,040 |
| Cell Type | Cellosaurus | 9 |
| Phenotype | OLS | 228 |

## [OA5] Interpretation boundary

These are source-reported mappings displayed by ORCS. DeathMap-AI has not yet
validated the identifiers against OLS or Cellosaurus, selected preferred terms,
or resolved conflicting mappings. A blank field means only that ORCS did not
display an accession on that screen page.

## [OA6] Library-breadth observation

The reviewed records show that `SCORES_SIZE` may describe the score rows
available in ORCS rather than the breadth of the experimental library. A screen
can therefore use a genome-wide library while exposing only tens or hundreds of
scores. `FULL_SIZE`, `FULL_SIZE_AVAILABLE`, and the reported library name should
be considered together. No automatic genome-wide/targeted classifier has been
adopted from this observation.
