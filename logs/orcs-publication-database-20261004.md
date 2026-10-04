# Shared ORCS publication database — 2026-10-04
## [PC1] Outcome
Created publication-index.json and publication-metadata.csv in data/orcs with all 418 website-indexed publication records. Created explicit publication-screen association JSON/CSV covering every one of the 2,217 existing native screens. Captured 607 supplementary-link mentions without fetching their contents.

Each publication has title, authors, abstract and date; seven journal values are absent. Six prepub page identifier assertions conflict with the cached source identifiers. Both observations remain visible; their displayed numbers are not promoted to verified PMIDs. No external authority was queried to resolve them.

The original screen database, template and populated output workbook retain their prior hashes. No gene-level screen contents, supplements or external publication records were downloaded. No search filter was run and no Git commit was made.

## [PC2] Verification
All 138 offline tests pass. Every publication row re-parses from its saved header, all source hashes and request receipts match, unique publication IDs/counts agree with the website inventory, every screen association is accounted for, JSON/CSV round trips match, and the screen/template/workbook hashes are unchanged. Details are in data/orcs/publication-verification.json.

## [PC3] Planning correction
Rebuilt docs/orcs/workbook-field-source-map.md and enrichment-plan.md around the complete publication and screen catalogs. All 128 template/reviewer headers are documented. They are independent of the prior filtered search and contain no previous workbook population counts or 76-versus-92-publication scope choice. Earlier drafts are preserved in logs/orcs-planning-before-publication-database-20261004.

## [PC4] Assumptions and open decisions
ORCS publication page IDs identify publication summary records despite the /Dataset/ route name. Exact browse links establish screen-publication associations, not screen-repository dataset attribution. The index covers the resource version observed today; completeness does not imply qualifying-study coverage.

Future normalization rules, screen grouping, prepub identifier resolution, exact dataset attribution and workbook projection remain separate reviewed steps. No new participant-role or scientific eligibility assumptions were introduced.

Learning checkpoint: separate entity tables and an explicit association table allow pandas joins while preserving native identities, conflicts and field-level provenance. The tradeoff is maintaining the ID mappings and source versions together.
