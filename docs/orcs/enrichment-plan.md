# ORCS enrichment plan

Current update, 2026-10-07: the three profiles have fresh corrected workbook packages and publication/screen seed lists under `outputs/orcs`. Their inputs remain the shared saved catalogs. [Handoff 17](../specifications/18%20Repository%20Native%20Discovery%20Release%20Preparation.md) governs this refresh and native discovery direction. External enrichment still requires its resource contract; no previous output is silently enriched.
## [EP1] Objective and boundary
Use the two complete shared ORCS metadata databases in future pipeline runs: 2,217 screen records and 418 publication records. This plan is independent of the previous filtered analysis. No historical workbook is enriched or changed by building these databases or this map.

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
