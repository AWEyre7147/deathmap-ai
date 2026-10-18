# Enrichment synthesis milestone preparation — 2026-10-18

The complete ORCS enrichment and 21-sheet synthesis are ready for owner review
before a commit and push. The [completed run](../data/orcs/enrichment-runs/20261018/README.md)
retains all 418 publications, 1,390 candidate publication–repository links, four
resource workbooks, final synthesis, canonical compressed evidence, stable registry
and historical execution receipts. [Independent commands](complete-enrichment.md)
cover the resource stages and offline synthesis without an AI authoring step.

## Cleanup

Superseded synthesis pilots, preview/authoring workspaces, the earlier generated
ICRAFT extraction and the October 9 biological-classes run were archived with
unchanged payload bytes and verified SHA-256/path receipts. The external recovery
archive is `deathmap-ai-v01-archive/enrichment-synthesis-cleanup-20261018` under the
owner's Archives directory. Current operation does not depend on that archive.
The two current biological-classes search configurations and outputs remain active:
v01 covers 2014–2022; v02 has no date bounds.

The owner's four curated ICRAFT workbooks remain byte-identical in their selected
folder. Original ICRAFT paper/supplements remain local. The existing Git exclusion
for that external validation material is unchanged; it is not a production input
or an included GitHub artifact.

The completed run's 9,233 supporting source files are preserved losslessly in
`source-material.zip` (53,925,094 bytes), with each original path, size and hash in
`source-material.manifest.json`. This replaces approximately 0.8 GB of loose
duplicate payloads, including two files above 100 MiB. Final workbooks and
compressed synthesis remain directly available. Standard Python ZIP extraction
restores the original source paths before source-based replay; see the
[restore instructions](complete-enrichment.md#restoring-the-packaged-completed-run).
Git ignores restored duplicates for this dated run only. Future runs retain their
normal output policy. No provenance manifest or protected workbook was rewritten.

## Verification and limits

- Every archived/bundled payload was read back and matched its original SHA-256.
- All 32 protected files, including the curated reviewer workbooks and registered
  templates, matched their preservation baseline after cleanup.
- 54 focused offline tests passed across enrichment, synthesis, date-bound ORCS
  filtering and evidence projection/template behavior.
- Scoped documentation links resolve; no Git candidate reaches 100 MiB.
- No retrieval, full enrichment rebuild, production workbook export, commit or push occurred.

The original complete-run workbook verification remains applicable; cleanup does
not add a native Excel application-opening check or adjudicate qualifying screen
content. Publication–repository associations remain candidates. Detailed local
receipts are retained under `logs/release-preparation/20261018/` and in the external
archive. Commit and push require the owner's explicit instruction.

## Follow-up cleanup

The three historical `searches/orcs/*/run-plan.md` notes were also archived with
verified bytes and hash/path receipts under the external
`retired-run-plans-20261018` recovery folder. They are not pipeline inputs; current
profiles, specifications and run receipts remain active. Removed the empty
`outputs/geo` test workspace and changed the GEO workbook fixture to use a
self-cleaning temporary directory directly under `outputs`. All four GEO workbook
tests passed and did not recreate the retired directory. Detailed receipt:
`logs/release-preparation/20261018/run-plan-cleanup.json`.

## Template consolidation

The approved repository revisions formerly under `data/templates/review-v2` are
now the four main enrichment templates directly in `data/templates`. Workbook
bytes and column mappings are unchanged; registrations and maintained command
paths now point to the consolidated locations. The older defaults and original
revision files are preserved byte-for-byte in
`data/templates/template-history-20261018.zip`, with paths and hashes in its
adjacent manifest. The ORCS main template, synthesis template, curated ICRAFT
workbooks and completed enrichment workbooks remain unchanged. Historical
execution receipts and source snapshots retain their original paths/hashes.
52 focused resource/synthesis tests passed after consolidation; no production
retrieval or workbook regeneration was performed.

## Flat search profiles and ORCS data cleanup

`searches/orcs` now contains exactly four standalone JSON profiles, named after
their search configurations. Their contents and SHA-256 values are unchanged.
Commands, maintenance scripts, tests and current links use the flat paths. New
runs continue under `outputs/orcs/<profile-filename-without-json>/<run-id>`; saved
per-run `profile.json` snapshots and historical execution manifests are unchanged.
The individual and directory READMEs are archived; usage remains in the main
README. No search was rerun for this migration.

Removed the superseded `data/orcs/website-capability` feasibility sample after
verified archival. The other six data directories remain because they hold source
publication evidence, reusable native repository responses, or completed enrichment
runs. For example, `publication-source` preserves the native header evidence for
the ORCS bibliography and the identifier cache; deleting it would remove provenance
needed to verify source metadata. Those folders are not temporary search runs.

All 34 focused profile/filter/export fixture tests passed, including regression
checks that all four flat profiles preserve their output namespaces and refuse
existing run directories. Detailed profile relocation and archive receipts are in
`logs/release-preparation/20261018/flat-profiles.json`; recovery material is under
`deathmap-ai-v01-archive/flat-orcs-profiles-20261018`. No retrieval, full search,
production export, commit or push was performed.

## Final preparation check

After template consolidation and profile flattening, the combined focused offline
suite passed all 85 tests. The four stale links in data/orcs/README.md now refer to
the maintained complete workflow. Current profile/template paths and scoped
release-document links resolve. Source bundles and protected review workbooks
retain their recorded hashes; no Git candidate reaches 100 MiB. ICRAFT validation
files remain ignored. These checks authorize no scientific coverage claim and
involve no live retrieval or production workbook regeneration. Changes are prepared
for Git staging; committing and pushing await the owner's explicit request.
