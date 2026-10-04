# ORCS profile filtering and Excel projection

Handoff 11 authorizes this separate local stage. Historical SQ01 semantics and
outputs remain unchanged. No network client is used, and no enrichment is run.

## Repeatable execution

Use the bundled Python with `src` on PYTHONPATH. Run
`python -B scripts/run_orcs_filters.py` from the repository. It validates the exact
accepted profile, 2,217 unique screens, cache-summary count, annotation/cache hash,
unique annotation keys and requested vocabulary values. Every invocation creates
a new directory and refuses to overwrite an existing run.

The runner emits native audit/outcome JSON, exact input snapshots, provenance,
a byte-exact workbook backup and a canonical `projection.json`. To populate the
archived workbook, set ARTIFACT_NODE_MODULES to the bundled node_modules directory
and run `node scripts/export_orcs_filter_workbook.mjs <run-directory>` using the
bundled Node executable. Run `python -B -m deathmap_ai.orcs_filter_verify
<run-directory>` with PYTHONPATH=src to verify the run workbook. Results remain in that run directory; the blank template is never replaced.

The workbook is derived from projection JSON. Existing publication identifiers
are reused; ORCS screen identities are retained explicitly in screen_notes.
Nonempty workbook cells and reviewer text are retained, and differing proposed
values appear in existing_value_conflicts. Ambiguous identities cause an error.
IDs use a namespaced SHA-256 digest of native identity, independent of row order.

## Mapping and limitations

The selected workbook has seven header-only entity sheets and no glossary sheet.
Its exact column names are preserved, including `author_list_ reported` and
`retrival_sources`. The authoritative machine-readable mapping is saved in
`projection.json` before spreadsheet authoring.

- SOURCE_TYPE/SOURCE_ID produce publication identities and PMID/DOI URLs.
  AUTHOR is retained as abbreviated attribution in publication_notes; title,
  journal, full authors, PMCID and year remain empty.
- SCREEN_NAME, METHODOLOGY, ENZYME, LIBRARY, LIBRARY_TYPE, CELL_LINE,
  ORGANISM_OFFICIAL, CONDITION_NAME, CONDITION_DOSAGE, DURATION, PHENOTYPE and
  ANALYSIS map to corresponding reported columns.
- Pool becomes pooled, Array becomes arrayed, and Knockout becomes CRISPR
  knockout only through the documented technology crosswalk. Other normalized
  fields remain blank. The native values remain in evidence and notes.
- SCREEN_TYPE, EXPERIMENTAL_SETUP, MOI, rationale, significance fields and NOTES
  remain reported evidence in screen_notes. FULL_SIZE and FULL_SIZE_AVAILABLE
  remain ORCS result-set metadata, never guide/sample counts or repository claims.
- Saved Cellosaurus facts retain accession, locator, exact join, reference date
  and review issues. They do not overwrite native ORCS facts.
- No source-supported shared design or explicit repository dataset identity was
  established. Screen Groups, Datasets and Screen-Dataset Links remain empty.
- Screens retain direct_filter_hit, unresolved_category or
  publication_sibling_context roles in textual status/notes and projection JSON.
  Siblings preserve their original filter outcome and anchor SCREEN_ID values.
- Reviewer decision/notes are grouped at the far right. Yellow marks reviewer
  fields; orange cells request owner review. Status text is authoritative.

A literal '-' is an absent-value marker only in the derived workbook; raw native
values remain intact. No immune partner, co-culture design, disease eligibility,
guide count or dataset availability is inferred. Conflicting annotations are
flagged, not used as an extra exclusion criterion.

## Verification and result

The full offline suite passed 120 tests before execution and 121 after final changes. Tests include exact
AND/OR criteria, negative boundaries, missing category handling, conflict
preservation, sibling separation, cache/schema errors, stable IDs, publication
and evidence foreign keys, reviewer-value preservation and network isolation.
The run also blocks Python socket creation. The saved verification report records
row reconciliation, workbook backup/output hashes and historical preservation.

Run: `outputs/orcs/cancer-cell-crispr-knockout-v01/20261003T173643920687Z/`.
See its summary.md for counts, independent/cumulative filtering and limitations.

Learning checkpoint: generated indices organize evidence; they do not establish
biological relationships. Publication siblings remain context, and empty dataset
links identify the evidence needed from a separately authorized enrichment stage.

The owner workbook replacement is recorded in logs/orcs-workbook-transition.json.
Historical SQ01 preservation accepts only this exact replacement when both the
archived original and replacement hashes match; other changes remain errors.

## Current input location

The owner relocated the complete index to `data/orcs/screen-index.json` and its
CSV export to `data/orcs/screen-metadata.csv`. The active profile now references
that JSON. Its bytes and annotation/cache hash agreement are unchanged. Historical
profile snapshots retain their original location; the relocation resolver supports
verification without rewriting those snapshots. The original completeness summary
is copied unchanged to data/orcs/cache-summary.json; the legacy cache is externally archived.
