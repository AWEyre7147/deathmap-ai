# Offline publication-enriched workbook

## [PE1] Scope

Handoff 14 authorizes a new workbook using the completed filtered run and shared
ORCS catalogs. The entry point loads saved results; it does not rerun the filter,
collector or external retrieval. Native SCREEN_ID associations determine the
publication join. The historical 92 publication IDs remain intact; native screen
2469 gains its supported publication 1165 link with a new deterministic ID.

## [PE2] Repeatable commands

Run from the repository root with the bundled Python and Node executables.
Choose an exclusively new UTC output directory ending in
`-publication-enriched-v01`. Set `ARTIFACT_NODE_MODULES` to the bundled packages.

```powershell
& $python scripts/enrich_orcs_publications.py $sourceRun $newRun
& $node scripts/export_orcs_filter_workbook.mjs $newRun
& $python scripts/enrich_orcs_publications.py $sourceRun $newRun --verify
```

The first command also accepts `--screens`, `--publications` and `--links` for
local copies of the accepted catalogs; manifest fingerprints must still agree.
Missing, corrupt or ambiguous joins fail explicitly. Existing output directories
are rejected. The starting workbook backup and immutable input hash references
are saved before export. Historical files are never edited.

After inspecting the publication, screen, evidence and reviewer previews, save
`visual-verification.json` containing `status: passed`, `reviewed_ranges` with
`publications`, `screens`, `evidence`, `reviewers`, a `preview_hashes` mapping of
relative preview paths to SHA-256 values, and the actual `offline_tests_passed`
count. Then run the same entry point with `--complete`; it repeats acceptance
checks before marking the stage complete. Rendering alone does not pass review.

Run the offline regression suite with `src` on `PYTHONPATH`:
`python -m unittest discover -s tests -q`.

## [PE4] Owner revision

[Workbook revision 15](../specifications/15%20ORCS%20Workbook%20ID%20and%20Field%20Revision.md)
authorizes sequential IDs, evidence_id_link and FULL_SIZE output mapping.
These are now the default for new preparations; `--legacy-schema` retains
handoff 14 behavior. Use `--starting-workbook` to preserve entries from the
previous enriched workbook while loading the original frozen filter results.
The new stage includes `id-migration.json` and explicit changed-cell receipts.

## [PE3] Preservation and review

Empty supported cells are filled. Nonempty owner values and formulas win;
differing source proposals retain their source locators in the field audit.
Authorized provenance/note appends keep the exact old prefix and are explicitly
listed in `approved_appends`. New publication evidence and direct association
evidence retain their original header and browse receipt dates, separately from
the offline projection time. JSON keeps full receipt precision; Excel dates have
millisecond precision.

The 128 field mappings classify support without representing unresolved cells as
completed. Publications have rightmost yellow reviewer fields; identifier-conflict
rows request attention in orange. Existing screen review entries and roles remain.
Supplementary URLs are publication asset mentions. No group, dataset or exact
screen-dataset relationship is inferred, and absent journals stay blank.

Learning checkpoint: explicit native associations repair an omitted publication
link without changing the screen's unresolved cancer category or biological
eligibility. The tradeoff is that a richer bibliography still leaves scientific
participant roles and dataset attribution for a separately authorized review.
