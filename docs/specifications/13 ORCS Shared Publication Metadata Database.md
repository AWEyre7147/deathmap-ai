# ORCS shared publication metadata database
## [PD1] Owner authorization — 2026-10-04
The owner requested all ORCS publications as a shared metadata database alongside the existing complete screen database, followed by a field map and enrichment plan considering both files. This is independent of the previous filtered analysis.

## [PD2] Boundary exception and scope
This authorization supersedes handoffs 11/12's stop-before-retrieval boundary for this shared ORCS publication-metadata task only. Retrieve the complete public ORCS publication index and each publication header. Preserve explicit screen-publication associations and supplementary link metadata. Do not retrieve gene-level results, linked supplement contents, score endpoints or external publication/repository records. Existing screens and output workbooks remain unchanged.

## [PD3] Deliverables and evidence
Place publication-index.json, publication-metadata.csv, publication-index.manifest.json, source headers and durable request receipts in data/orcs, matching the screen database's JSON/CSV/provenance design. Preserve ORCS page IDs separately from SOURCE_TYPE/SOURCE_ID; preserve source conflicts and missing values. Association files connect native SCREEN_ID to native publication page ID; an ORCS /Dataset/ page is a publication record, not a repository dataset.

Use bounded metadata reads, one-second pacing, cumulative attempt limits and resumable receipts. Verify the website publication count, complete screen association coverage, unique IDs, JSON/CSV agreement and unchanged screen input hash. Update the field map and enrichment plan only after both shared databases are available. No workbook projection or Git commit is authorized in this task.
