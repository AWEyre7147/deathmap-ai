# Repository organization and workbook planning
## [RO1] Owner authorization
On 2026-10-04 the owner confirmed the proposed structure [A89], specified C:/Users/aweyr/Documents/Archives/deathmap-ai-v01-archive, and accepted the workbook planning task [A88]. This is a repository-organization stage, not a new scientific search or enrichment pass.

## [RO2] Superseded location constraints
Historical SQ01 outputs remain scientifically immutable but may now be relocated into that archive. This owner-approved exception supersedes the earlier requirement to retain those outputs at their original repository paths. Original manifests, raw identifiers and bytes are preserved; logs/repository-relocations-20261004.json records original, active and preserved-original locations with hashes.

For the active ORCS pass, search configuration is searches/orcs/cancer-cell-crispr-knockout-v01/profile.json. Shared index and annotations are data/orcs/screen-index.json and data/cellosaurus/orcs-annotations/annotations.json. The original blank workbook is data/templates/DeathMap-AI-v1-reference-output.xlsx. Results and populated workbooks belong in outputs/orcs/cancer-cell-crispr-knockout-v01/<run-id>/, superseding handoff 11's original output-example destination.

Active paths in guides/code may change; original versions of moved active files are also archived. Frozen result artifacts and historical run snapshots are not rewritten.

## [RO3] Scope and deliverables
Archive superseded runs, output-structure experiments and temporary artifacts; retain active code, specifications, vocabularies, shared inputs and one named ORCS search directory. OmicsDI remains in the project with directories for future searches, inputs, results and documentation.

Provide navigation, a field-source map covering every workbook header, and a proposed ORCS enrichment plan. Do not retrieve new metadata, download experimental datasets, edit workbook values, implement enrichment or commit.

## [RO4] Verification and learning checkpoint
Check moved files against their recorded hashes, test active path resolution and filter behavior, and verify the native index, blank template and populated workbook remain unchanged. Distinguish candidate-hit counts from context/workbook row counts.

The checkpoint is understanding the separate roles of shared inputs, search configuration, per-run results, reference annotations and field-level enrichment. A publication link is not a screen-dataset attribution.
