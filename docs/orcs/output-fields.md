---
aliases:
  - ORCS output fields
tags:
  - deathmap-ai
  - orcs
  - data-dictionary
---

# ORCS screen metadata fields

This note describes the native fields observed in the BioGRID ORCS `screens`
metadata response used by the pilot. Names and values are preserved in
[screen-metadata.csv](../../data/orcs/screen-metadata.csv).

Descriptions explain how DeathMap-AI currently interprets a field for review.
They do not replace the original ORCS value. Fields with uncertain units are
marked explicitly so they are not given stronger scientific meaning than the
source supports.

| ORCS field               | Category         | Working description                                                                                                                                                                           | Reasoning-layer relevance                                          |
| ------------------------ | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `SCREEN_ID`              | identity         | ORCS identifier for one screen record.                                                                                                                                                        | Stable screen node and source link.                                |
| `SOURCE_ID`              | publication link | Identifier for the linked source described by `SOURCE_TYPE`; currently a PMID when the type is `pubmed`.                                                                                      | Candidate screen-to-publication edge.                              |
| `SOURCE_TYPE`            | publication link | Identifier system used by `SOURCE_ID`.                                                                                                                                                        | Prevents another identifier from being mislabeled as a PMID.       |
| `AUTHOR`                 | citation         | ORCS citation label for the screen source.                                                                                                                                                    | Human-readable provenance.                                         |
| `SCREEN_NAME`            | identity         | ORCS name for the screen record.                                                                                                                                                              | Screen label; not a publication title.                             |
| `SCORES_SIZE`            | count            | ORCS-reported size of the scored content. Reviewed examples show that it may contain only the subset of scores available to ORCS, so it must not be used alone to infer library breadth.      | Result-availability evidence, not a genome-wide classifier.        |
| `FULL_SIZE`              | count            | ORCS-reported full size. It is more informative about underlying screen breadth than `SCORES_SIZE` in the reviewed examples, but remains source evidence rather than a sufficient classifier. | Possible library-breadth and result-coverage evidence.             |
| `FULL_SIZE_AVAILABLE`    | availability     | ORCS availability flag associated with the full-size content. The exact downloadable object is not assumed.                                                                                   | Accessibility claim requiring interpretation.                      |
| `NUMBER_OF_HITS`         | result summary   | ORCS-reported hit count under the stated significance criteria.                                                                                                                               | Screen summary; not a substitute for gene-level results.           |
| `ANALYSIS`               | analysis         | Analysis method named by ORCS, such as MaGeCK.                                                                                                                                                | Method provenance and comparability.                               |
| `SIGNIFICANCE_INDICATOR` | analysis         | ORCS label for the significance measure.                                                                                                                                                      | Interpretation of reported hits.                                   |
| `SIGNIFICANCE_CRITERIA`  | analysis         | Threshold or rule used to call hits.                                                                                                                                                          | Interpretation and reproducibility.                                |
| `THROUGHPUT`             | design           | ORCS throughput category.                                                                                                                                                                     | Screen-scale classification.                                       |
| `SCREEN_TYPE`            | design           | ORCS selection or screen-type category.                                                                                                                                                       | Direction and meaning of selection.                                |
| `SCREEN_FORMAT`          | design           | ORCS format such as `Pool`.                                                                                                                                                                   | Distinguishes pooled and arrayed designs.                          |
| `EXPERIMENTAL_SETUP`     | design           | ORCS controlled term describing the experimental setup.                                                                                                                                       | Candidate experiment classification.                               |
| `DURATION`               | design           | Reported screen or treatment duration.                                                                                                                                                        | Timing and comparability.                                          |
| `CONDITION_NAME`         | condition        | Source-normalized condition name.                                                                                                                                                             | Treatment, co-culture, or comparator identity.                     |
| `CONDITION_DOSAGE`       | condition        | Dose, concentration, ratio, or other condition quantity.                                                                                                                                      | Contrast definition and experimental context.                      |
| `MOI`                    | design           | Reported multiplicity of infection.                                                                                                                                                           | Perturbation-design context.                                       |
| `LIBRARY`                | perturbation     | ORCS library name or description.                                                                                                                                                             | Library identity and scope evidence.                               |
| `LIBRARY_TYPE`           | perturbation     | ORCS perturbation/library category, such as `CRISPRn`.                                                                                                                                        | Perturbation modality.                                             |
| `METHODOLOGY`            | perturbation     | ORCS methodology, such as `Knockout`.                                                                                                                                                         | Distinguishes knockout, activation, inhibition, and other designs. |
| `ENZYME`                 | perturbation     | Nuclease or enzyme named by ORCS, such as Cas9.                                                                                                                                               | Supports future Cas9/Cas12a distinctions.                          |
| `CELL_LINE`              | biological model | Specific cell-line or primary-model wording.                                                                                                                                                  | Candidate perturbed population and model identity.                 |
| `CELL_TYPE`              | biological model | Broader ORCS cell-type category.                                                                                                                                                              | Cell-type normalization and grouping.                              |
| `PHENOTYPE`              | phenotype        | Original ORCS phenotype term.                                                                                                                                                                 | Preserved source phenotype before normalization.                   |
| `SCORE_COL_COUNT`        | result schema    | Number of score columns described by ORCS.                                                                                                                                                    | Parsing and interpretation of result schemas.                      |
| `SCORE.1_TYPE`           | result schema    | Meaning of score column 1.                                                                                                                                                                    | Result-column provenance.                                          |
| `SCORE.2_TYPE`           | result schema    | Meaning of score column 2.                                                                                                                                                                    | Result-column provenance.                                          |
| `SCORE.3_TYPE`           | result schema    | Meaning of score column 3.                                                                                                                                                                    | Result-column provenance.                                          |
| `SCORE.4_TYPE`           | result schema    | Meaning of score column 4, or `-` when unused.                                                                                                                                                | Result-column provenance.                                          |
| `SCORE.5_TYPE`           | result schema    | Meaning of score column 5, or `-` when unused.                                                                                                                                                | Result-column provenance.                                          |
| `ORGANISM_ID`            | organism         | NCBI taxonomy identifier reported by ORCS.                                                                                                                                                    | Stable organism normalization.                                     |
| `ORGANISM_OFFICIAL`      | organism         | Official organism name reported by ORCS.                                                                                                                                                      | Human-readable organism label.                                     |
| `NOTES`                  | evidence text    | ORCS description of hit interpretation or screen behavior.                                                                                                                                    | Direct review evidence; preserve verbatim.                         |
| `SOURCE`                 | provenance       | Database/source label supplied in the ORCS record.                                                                                                                                            | Source attribution.                                                |
| `SCREEN_RATIONALE`       | interpretation   | ORCS statement of the screen's scientific rationale.                                                                                                                                          | Candidate mechanism or objective; not a reviewed conclusion.       |

## [OF1] Important distinctions

- `SCREEN_NAME` is not the publication title.
- `SOURCE_ID` becomes `pmid_reported` only when `SOURCE_TYPE` is `pubmed`.
- `FULL_SIZE` and `SCORES_SIZE` remain source-reported counts until their units
  are verified.
- `PHENOTYPE` remains unchanged when a separate normalized phenotype is added.
- Score descriptions are metadata. The metadata-only pilot does not download
  the gene-level score rows they describe.

## [OF3] Screen-page accession fields

The ORCS screen pages display external identifiers that are not included in the
native `screens` metadata response. The pilot preserves these identifiers in a
separate enrichment layer rather than altering the native response.

| Derived field | ORCS page field | Description |
|---|---|---|
| `CONDITION_OLS_ACCESSIONS` | Condition | Identifiers linked by ORCS to the EMBL-EBI Ontology Lookup Service. |
| `CELL_LINE_OLS_ACCESSIONS` | Cell Line | OLS identifiers displayed for the cell line. |
| `CELL_LINE_CELLOSAURUS_ACCESSIONS` | Cell Line | Cellosaurus identifiers displayed for the cell line. |
| `CELL_TYPE_OLS_ACCESSIONS` | Cell Type | OLS identifiers displayed for the cell type. |
| `CELL_TYPE_CELLOSAURUS_ACCESSIONS` | Cell Type | Cellosaurus identifiers displayed for the cell type. |
| `PHENOTYPE_OLS_ACCESSIONS` | Phenotype | OLS identifiers displayed for the phenotype. |

Blank values mean that the ORCS page did not display an identifier for that
field. They do not establish that the biological entity lacks an external
identifier.

## [OF2] Source

- BioGRID ORCS: `https://orcs.thebiogrid.org/`
- Pilot source: the preserved ORCS `screens` metadata response.
- Accession-enrichment source: the public ORCS screen pages documented in
  [[accession-enrichment]].
