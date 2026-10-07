# Repository-native discovery: milestone release preparation

## [R18-1] Owner decisions

The owner authorizes GitHub preparation, obsolete-artifact archival and documentation updates. In [A107] the `orcs-crispr-biological-classes-pilot-v01` profile is the current scientific reference. In [A108] retired OmicsDI/SQ01 discovery code, obsolete exporters and their dependent tests are to be archived. In [A109] retain metadata, templates, search profiles and generated ORCS milestone results. Native resource implementation begins after publication, once the owner supplies resource research. Preparation does not authorize a commit, push, remote change or PR.

This supersedes the active-stage portions of handoff 17 and the prior current work session for release preparation. Prior contracts remain historical records. The owner's edited `workbook-authored.xlsx` files must not be edited, regenerated, recalculated or overwritten.

## [R18-2] New discovery direction

Find studies relevant to CRISPR perturbation contexts using each repository's own programmatic interface and search structure. The ORCS biological-classes profile establishes the present target: human/mouse, the configured CRISPR modalities, and cancer-derived, immune-lineage or organoid model contexts, including normal organoids and non-immune readouts. Do not copy ORCS's literal fields or labels into unrelated interfaces.

Some resources may begin with publications and then locate associated datasets; others may begin with repository studies or datasets and then identify their publications. Preserve the actual route, native record type, identifiers, field-level evidence and query/filter contribution. Prefer usable structured filters and reserve text criteria for properties without supported fields. Missing metadata is a useful limitation, not permission to infer a qualifying screen. Dataset identification and justified screen attribution remain the intended outcomes.

GEO, ENA, ArrayExpress within BioStudies, PRIDE, MassIVE, jPOST and iProX are the primary planned families. Resource priority and concrete retrieval contracts remain to be approved from the owner's forthcoming research. No native discovery/enrichment adapter is implemented during release cleanup.

## [R18-3] OmicsDI and evidence boundaries

OmicsDI is deprecated as a discovery implementation and no longer drives current searches or development. Keep only useful independent evidence/identity utilities; archive its query engines, executors, historical limits and dependent tests. A possible future tertiary accession-led lookup remains backlog work, not an implemented or mandatory pipeline layer.

Keep independent discovery distinct from publication/accession-seeded enrichment. Assign screen groups after sufficient enrichment evidence. Publication-dataset association alone does not establish that a deposit contains the qualifying perturbation experiment. No experimental-file contents, reasoning layer or automated scientific adjudication are added.

## [R18-4] Milestone source package and workbooks

Retain saved public ORCS/Cellosaurus metadata and workbook models needed for offline reproducibility. Keep all three supplied search profiles and current ORCS execution. Include a curated snapshot of the three milestone results under `examples/orcs`, including byte-identical copies of the owner's reviewed authored workbooks and canonical generation-time JSON/provenance. Keep original working outputs local. Exclude temporary authoring files, installed runtimes, caches and external archives.

Reviewer edits in XLSX are subsequent to JSON generation; they have not been imported into canonical JSON. State that difference explicitly. The reviewed workbooks are milestone evidence, not blank templates or refresh targets. Generate future results in new directories and refuse an existing authored workbook before initializing the authoring runtime.

`workbook-authored.xlsx` becomes the sole exported workbook. Archive the redundant `DeathMap-AI-output-v6.xlsx` derivatives and remove the template-transplant step from future exports. Earlier XML/value checks did not prove Excel compatibility; the owner reports that authored workbooks open successfully and the derivative workbooks do not. Do not claim that the derivative compatibility defect was fixed.

## [R18-5] Verification and remaining release choice

Hash-check owner workbooks before and after cleanup; preserve backups and byte/hash receipts. Test only supported active behavior after retiring dependent tests. Test the authored-workbook overwrite guard without authoring or opening reviewed files. Validate the Git-included package in an isolated copy without access to local output directories or archives. Review broken active documentation links, omitted dependencies, oversized files and credential-like artifacts without printing secret values.

In [A111] the owner requires the pipeline's Excel functionality to run without Codex. Implement a Python/openpyxl writer and prepare a repaired v6-style template with its important coloring preserved. The separate repaired-template proposal requires owner review before promotion. The edited authored outputs remain protected. Retire the artifact-tool production exporter; an optional developer preview utility is not a production dependency. Publication remains pending template approval and final isolated-package verification.

Learning checkpoint: a milestone result snapshot documents what worked, while the supported pipeline and roadmap tell a new contributor what can be run now and what awaits repository-specific implementation.

## [R18-6] Template promotion and integrated export

Owner instructions [A118] authorize archiving superseded template workbooks, promoting the owner-finalized repaired template as `data/templates/DeathMap-AI-output.xlsx`, keeping a byte-identical backup alongside it, and integrating portable Excel export with the ORCS search command. Search runs write JSON first and retain explicit failure status if workbook export fails. Existing reviewed outputs remain unchanged. No live retrieval or publication is added.

## [R18-7] Final output curation and next-version planning

Owner clarification [A122] supersedes R18-4's examples packaging: retain the latest run for each ORCS search directly in `outputs/orcs` and include those outputs in Git. Remove duplicate examples and older working runs after preserving reviewed files in the external archive. Initialize v0.2 repository-native discovery planning; keep the executable package at v0.1.0. No commit or push is authorized.
