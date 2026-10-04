# ORCS workbook owner revision — 2026-10-04

## [WR1] Authority and scope

The owner explicitly requested implementation and an offline rerun with:
publication IDs `PUB-0001`, screen IDs `SCR-0001` and evidence IDs `EVI-00001`;
an `evidence_id_link` column immediately after the publication retrieval-source
column; and native `FULL_SIZE` copied to `library_gene_count_reported`.

This request supersedes handoff 14's pending RD1 decision, prohibition on ID
migration, exact-header-only requirement for this added column, and restriction
against mapping FULL_SIZE into this field. Preserve the historical header spelling
`retrival_sources`. Separate its embedded evidence IDs into the new column while
retaining source attribution. Keep reviewer columns together at the far right.

## [WR2] Traceability and scientific interpretation

Sequential IDs follow canonical entity-row order. Reuse existing sequential IDs
and reserve their numbers when adding entities. Preserve an old-to-new registry
and rewrite all entity foreign keys, evidence lists, role-map keys and structured
mapping references together. Native SCREEN_ID/PUBLICATION_ID remain unchanged.

Copy non-placeholder integer FULL_SIZE values, retaining native values and field
locators in notes/evidence. This is an owner-selected output convention: the
existing ORCS documentation describes screen result size, so the mapping does
not independently establish the number of genes in the experimental library.
Do not map SCORES_SIZE, fabricate counts for placeholders or infer guide counts.

## [WR3] Acceptance and preservation

Use new output directories, immutable catalog inputs and the same selected
screen set. Preserve source runs and review entries. Verify sequential identity
uniqueness, every rewritten reference, evidence-column placement and every
FULL_SIZE conversion. Run the full offline suite, reconcile exported cells and
inspect the changed workbook ranges. No external retrieval or filtering is
authorized. Retain legacy projection behavior for historical verification.
