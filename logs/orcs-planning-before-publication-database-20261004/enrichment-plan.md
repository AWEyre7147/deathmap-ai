# ORCS enrichment plan
## [EP1] Objective and boundary
Improve the existing ORCS workbook using ORCS metadata and clearly attributed saved reference facts. This document proposes the next stage; no retrieval, workbook editing or external enrichment was performed during repository organization.

The ORCS-only boundary shows what ORCS contributes. For example, its publication page can supply a title while an ORCS publication-summary URL is not a repository dataset accession. Later exact dataset attribution may require a separately authorized publication/repository stage.

## [EP2] Evidence already available
The [saved five-screen capability test](../../data/orcs/website-capability/20261003-five-screen-v01/summary.md) found publication titles, reference identifiers, descriptive links and source-supplement URLs on screen pages. Most design text was already in the native screen index. Four programmatic metadata excerpts succeeded and one failed; this small sample is not a coverage estimate.

One ORCS publication page was independently observed to contain title, authors, abstract, journal, date, PMID and a supplementary-file link. These observations justify testing publication enrichment, not assuming every publication has all fields. ORCS /Dataset/ pages represented publication summaries in this sample; do not turn their IDs into repository datasets.

No repository accession was found in the four saved excerpts. That does not establish that none exist elsewhere. Addgene/material links and supplements must retain their stated roles.

## [EP3] Proposed companion tables
Keep shared source observations separate from workbook presentation.

| Proposed table | Native key and contents | Why separate |
|---|---|---|
| publication-details | ORCS publication-page ID plus exact reported PMID/DOI; title, authors, journal, date, abstract, source URL | Retrieve one publication once and link its screens without merging screen entities |
| screen-details | SCREEN_ID; page-reported metadata, ontology/reference links and source-supplement links | Preserve screen-specific facts and compare additions with the existing index |
| publication-screen-associations | SCREEN_ID and original SOURCE_TYPE/SOURCE_ID; direct cached association | Existing explicit link, not proof of a screen-dataset relationship |
| supporting-assets | Native screen/publication key, exact link label, URL and page location | A reported link is an asset mention; content/type and attribution remain unresolved |
| retrieval-receipts | Source URL/key, UTC retrieval time, resource/version, tool/parser version, response hash, status and failures | Reproducibility, failed-page review and resumability |

Saved Cellosaurus/BTO/CL/EFO annotations remain their own reference bundle. Do not create duplicate definitions or replace conflicting native observations. The table names are proposals, not implemented schema.

## [EP4] Suggested sequence
1. Review the present workbook and agree scope: 76 direct-hit publications or all 92 workbook publications; 1,020 direct-hit screens or all 1,176 workbook screens. Retain roles in either choice.
2. Test a small ORCS publication-page extraction with manually checked fields and failures. Populate title, full reported authors, journal and year only when the page provides supporting evidence. Preserve full date separately.
3. Compare saved screen-page metadata with the bulk index before collecting redundant pages. Target missing link/reference evidence; do not assume website retrieval reveals co-culture eligibility.
4. Save source observations, receipt hashes and field-level locators before projecting additions into a new workbook/run version. Keep conflicting values and reviewer edits.
5. Reconcile entity IDs, foreign keys, counts and exact source-backed cells, then review unresolved fields.

No gene-level screen results, guide counts files, FASTQ, processed matrices or supplements are downloaded in this metadata stage. The singular results endpoint is outside scope. Establish resource pacing, bounded retries, a stopping rule and resumable receipts before any full collection.

## [EP5] What may remain missing
Immune populations, ratios, comparators, detailed readouts, replicate designs and exact screen-dataset links may require publications or repository records. A publication's dataset association alone does not prove that dataset contains the qualifying screen. Leave these fields unresolved and propose that later stage explicitly.

[Workbook field-source map](workbook-field-source-map.md) lists every current column and populated-cell count. The next learning checkpoint is whether ORCS publication and screen pages supply useful incremental metadata beyond the bulk index.
