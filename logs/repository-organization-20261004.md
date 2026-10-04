# Repository organization — 2026-10-04
## [OC1] Changes
Implemented the owner-confirmed layout. Named ORCS search configuration is in searches/orcs/cancer-cell-crispr-knockout-v01; results remain in the corresponding outputs/orcs search/run directory. Shared native metadata, saved reference annotations and blank templates now have separate data directories. ORCS vocabularies are grouped under docs/vocabularies/orcs.

Historical SQ01 runs, superseded documentation, output-structure experiments and temporary artifacts were moved to the approved external archive. Original versions of moved active files were preserved before editing. The path/hash registry records 1,055 files and three dependency junctions, whose targets were not moved or copied.

Updated active code paths, navigation and ignore rules. Added archive resolution with byte-hash checks and registered dependency-link handling for old preservation baselines. Original frozen run manifests, profiles, result JSON and workbooks were not rewritten.

Created the complete workbook field-source map and proposed ORCS enrichment plan. Preserved the full ORCS reference spreadsheet as the owner's visual of the database. Copied the original service-vocabulary snapshot into shared data with its original hash and source path.

## [OC2] Verification
132 offline tests passed, including exact filters, namespace/foreign-key behavior, existing reviewer value preservation, archive boundary checks and corruption detection.

All 1,055 preserved originals match their recorded hashes. The full existing workbook projection was reconciled on a disposable copy; its original preservation baseline, including software dependencies, also passed. Re-evaluating the saved native cache reproduced the original filter summary without creating a new run. The native index, blank template and populated workbook retain their expected hashes. All active local Markdown links were checked; before-full-annotation evidence snapshots retain their original historical links.

Detailed receipts: repository-organization-navigation-20261004.json and repository-organization-verification-20261004.json. No network requests, experimental-data downloads, workbook cell edits or Git commits occurred.

## [OC3] Assumptions and open decisions
This was organization and planning only, with no new scientific eligibility assumptions. Hits remain candidates; unresolved categories and publication siblings retain their distinct roles. Existing accepted display-ID preference remains pending rather than being implemented as an unrelated migration.

Before enrichment, agree whether to cover the 76 direct-hit publications or all 92 workbook publications, and the analogous screen scope. Exact dataset attribution may need a later publication/repository stage. OmicsDI remains planned, with next search rules pending.

## [OC4] Learning checkpoint
Shared inputs, filter configuration, per-run evidence and workbook projection serve different purposes. Keeping them separate makes it possible to see which fields ORCS supplies directly, which the pipeline derives transparently, and which still require evidence.
