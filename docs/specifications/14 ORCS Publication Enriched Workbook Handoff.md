# ORCS publication-enriched workbook implementation handoff

## [PEH1] Objective and authorization

Prepared on 2026-10-04 at the owner's request for a handoff. Implement repository
support for an offline workbook projection combining the most recent completed
ORCS filtered run with the new shared publication database, following
[the field-source map](../orcs/workbook-field-source-map.md).

The receiving implementation task should complete the code, verification and new
workbook, rather than stop at another plan. This preparation task creates the
handoff only; it does not execute workbook enrichment or dispatch another chat.

For this new stage, the owner's request supersedes handoff 13's prohibition on
workbook projection. Preserve its shared sources and the original filtered run.
No external retrieval, source refresh or new filtering is needed or authorized.
Follow AGENTS.md, the project vision, module 1 specification, current work-session
specification and code-commenting standard.

## [PEH2] Fixed inputs and scope

Repository root: `C:\Users\aweyr\Documents\Repositories\deathmap-ai-v01`.
Paths below are relative to that root.

| Input | Path / use |
|---|---|
| Most recent completed filtered run | `outputs/orcs/cancer-cell-crispr-knockout-v01/20261003T173643920687Z/` |
| Accepted results and roles | That run's `matched_screens.json`, `unresolved_screens.json`, `publication_siblings.json`, `projection.json`, `summary.json` and `run_manifest.json` |
| Starting workbook | That run's `DeathMap-AI-v1-reference-output.xlsx`; copy it to the new output directory, preserving existing IDs, nonempty values, formulas and reviewer entries |
| Blank schema reference | `data/templates/DeathMap-AI-v1-reference-output.xlsx`; preserve its seven sheet names, order and exact headers, including historical spelling |
| Screen database | `data/orcs/screen-index.json`, with its manifest and original retrieval provenance |
| Publication database | `data/orcs/publication-index.json`, `publication-index.manifest.json` and `publication-verification.json` |
| Explicit association table | `data/orcs/publication-screen-links.json` |
| Publication source evidence | `data/orcs/publication-source/20261004-v01/`: saved headers and per-page receipts |
| Original reference evidence | The filtered run's `reference_annotations.json`; preserve its accepted Cellosaurus joins and review issues |
| Field mapping and stage plan | `docs/orcs/workbook-field-source-map.md` and `docs/orcs/enrichment-plan.md` |

Use exactly the original projected screen set and roles: 1,020 direct hits,
59 unresolved-category records and 108 publication-context records, with
11 unresolved/context overlaps counted once, yielding 1,176 distinct screens.
Preserve both observations for overlapping roles and the original direct-hit
publication count of 76. Do not add excluded screens, apply a new immune gate,
change category decisions, or reinterpret candidates as qualifying co-cultures.

The shared catalogs contain 2,217 screens and 418 publications; those are input
inventory counts, not the output row counts or qualifying discovery counts.

## [PEH3] Confirmed local join finding

Read-only preparation verified that all 1,176 selected native SCREEN_ID values
have explicit association-table entries. They connect to **93** ORCS publication
pages, whereas the original workbook contains 92 publication rows.

The additional association is native screen `2469`, an unresolved-category row,
to ORCS publication page `1165`. Its original internal screen ID is
`DM-SCR-a1bb18c00220f2d55d9cdea2`. The source index reports:

- `SOURCE_TYPE = prepub`;
- `SOURCE_ID = 10.1101/2025.08.26.672429`;
- a DOI-shaped source identifier retained in publication `DOI`;
- page-reported `PAGE_SOURCE_TYPE = pubmed` and `PAGE_SOURCE_ID = 28`, which
  conflict with the cached source identity.

The original projection left this screen's publication_id empty. Create the
supported publication row and link in the new projection, preserving the
prepublication identity and conflict. **Do not populate PMID with 28.** This adds
a source-backed association; it does not resolve the screen's cancer category,
change its filter role or establish scientific eligibility.

Two of the 93 linked publication records have no JOURNAL value. Leave those
cells blank; do not search externally or infer a journal from identifiers.

## [PEH4] Identity, joining and preservation rules

1. Join native screen `SCREEN_ID` to association `SCREEN_ID`, then association
   `PUBLICATION_ID` to publication `PUBLICATION_ID`. Keep these native IDs
   distinct from internal workbook publication_id and screen_id.
2. Validate uniqueness, foreign keys and exact SOURCE_TYPE/SOURCE_ID agreement
   between association records and the screen/publication catalogs. A missing,
   duplicate or ambiguous required association is an explicit error, not a
   title-based match or silently dropped screen.
3. Reuse all existing internal screen/publication IDs. Match existing publication
   identities through their reported identifiers and original source evidence;
   preserve a native-to-internal ID mapping. Generate a deterministic ID only
   for the newly supported publication and additional evidence records.
4. Fill empty source-backed cells. Preserve existing nonempty values, formulas
   and reviewer entries; record differing source-backed proposals separately with
   retained value, proposed value, source locator and conflict status. Add new
   evidence and provenance without discarding the original scientific record.
5. The short sequential ID preference in owner decision RD1 remains pending.
   Do not bundle renumbering or an ID migration into this implementation.

Using the explicit association table is useful because it handles the prepub
screen whose old PMID/DOI-only projection omitted a publication link. It does
not justify treating the publication's assets as that screen's datasets.

## [PEH5] Workbook population rules

Apply all 128 template/reviewer mappings in the field-source map. Classify each
column as reported, explicitly derived, provenance, review-dependent or
unsupported; do not promise all columns will become populated.

### Publications

- Fill `title_original`, `author_list_ reported` and `journal_reported` from
  publication TITLE, AUTHORS and JOURNAL when nonempty.
- Derive `publication_year` from a valid PUBLICATION_DATE, preserving the full
  date in supporting evidence.
- Use the publication database's supported PMID/DOI fields. Construct links from
  those identifiers and label URLs as derived, not fetched. Preserve native
  SOURCE_TYPE/SOURCE_ID and PAGE_SOURCE_TYPE/PAGE_SOURCE_ID independently.
- Preserve ABSTRACT, publication URL, native publication ID, full date,
  supplementary-file labels/URLs and REVIEW_ISSUES in publication notes and
  structured evidence. Append provenance safely without overwriting notes.
  Append the saved publication-header source to retrival_sources while retaining
  its existing source attribution; do not replace one source with another.
- Preserve the exact workbook headers `author_list_ reported` and
  `retrival_sources`; do not silently repair their spelling.
- Leave PMCID/PMC links and unsupported publication types blank. SOURCE_TYPE is
  an identifier namespace, not an article/review classification.

### Screens

- Preserve the original selected native screen facts, internal IDs, role text,
  annotation conflicts and reviewer entries. Fill direct fields using the
  documented screen-column mappings, with source placeholders treated as missing.
- Reuse the accepted explicit crosswalks for SCREEN_FORMAT and Knockout
  methodology; leave unsupported normalization values unmapped.
- Add the supported publication association for screen 2469 and link publication
  evidence without attaching a paper's scientific claims to every screen.
- Preserve useful native design/notes/significance metadata as reported notes
  or evidence. FULL_SIZE/SCORES_SIZE are not library gene counts, guide counts,
  sample counts or proof of repository availability.
- Do not use abstracts, cell-type names or a cancer-cell-line category to invent
  participant roles, immune partners, disease context, ratios, shared design,
  co-culture eligibility or other review-dependent scientific fields.

### Screen Groups, Datasets and Screen-Dataset Links

Retain the sheets and their headers. Do not create rows without the evidence
required by the map; the current inputs do not establish these entities or exact
dataset relationships. A publication's `/Dataset/` page is a publication record.
Supplementary URLs remain publication-associated asset mentions, not fabricated
dataset rows or screen-dataset links. Preserve any existing owner-entered rows.

### Sources & Evidence and Discovery Resources

- Preserve prior evidence and create publication-level evidence records with
  `supports_entity_type = publication` and the correct internal publication ID.
  Record native publication IDs, original retrieval times, saved header hashes,
  URLs, field locators and transformation/conflict status.
- Preserve direct screen-publication association evidence and original screen
  and reference retrieval dates. Distinguish source retrieval from this offline
  projection timestamp.
- Document that publication metadata was reused locally, with zero new network
  requests. Resource summaries must keep 1,020 direct screen hits and 76
  direct-hit publications separate from 1,176 projected screens and the expected
  93 linked publication entities. Full catalog counts belong in provenance.
- For reviewer entry fields, keep them together at the far right and yellow;
  rows requesting owner attention have orange reviewer cells. Keep substantive
  review issues/status text as the record. Reuse existing screen review fields;
  add a rightmost publication reviewer pair where the identifier conflict needs
  owner attention, rather than silently adding review columns to every sheet.

## [PEH6] Implementation and output

Prefer a small extension of existing projection, export and verification code:

- `src/deathmap_ai/orcs_filter_projection.py`;
- `scripts/export_orcs_filter_workbook.mjs`;
- `src/deathmap_ai/orcs_filter_verify.py`;
- existing filter/run wrappers and regression tests where appropriate.

Provide a repeatable offline entry point accepting the source filtered-run
directory and shared metadata inputs. It must load the saved results, not rerun
filtering or call the publication collector. Keep historical projection
behavior testable; do not silently alter old result files or their manifests.
Follow the code-commenting standard. Use the spreadsheet skill and bundled
dependencies for workbook authoring and visual verification; adapt the exporter
to support publication reviewer fields when present.

Create an exclusively new directory:

`outputs/orcs/cancer-cell-crispr-knockout-v01/<UTC-run-id>-publication-enriched-v01/`

Keep the workbook basename `DeathMap-AI-v1-reference-output.xlsx` in this new
directory. Never replace the source workbook, blank template or catalog files.

The new directory must contain:

- populated workbook and its starting-workbook backup;
- canonical `projection.json`, with IDs, row roles and retained/proposed conflicts;
- native-to-internal ID and association mapping;
- manifest linking the exact source run, input hashes, mapping-document hash,
  tool/code version and zero-network policy;
- source snapshots or immutable hashed references to the accepted inputs;
- field-level population audit recording supported additions, derived values,
  retained conflicts and unresolved fields; do not expose blanks as completed;
- verification report, concise summary and representative workbook previews.

A pending status is acceptable while exporting/verifying; mark the new stage
complete only after the workbook and all required checks pass. Fail explicitly
on corrupt/missing inputs or verification failure.

## [PEH7] Verification and acceptance

Add small fixtures covering publication enrichment, shared-publication reuse,
prepub/page identifier conflict, absent journal, duplicate/missing associations,
existing ID/reviewer/formula preservation, publication evidence foreign keys,
supplementary-link non-attribution and zero-network behavior.

For the actual output, verify:

1. Exactly 1,176 distinct screens and preserved source-run roles and IDs; no
   change to original filter counts or biological eligibility claims.
2. The 93 supported publication entities reconcile to the selected screens;
   the original 92 publication IDs remain intact and screen 2469 receives its
   previously missing supported link. Unexpected differences require an explicit
   diagnostic, not forced counts.
3. Every source-backed new cell agrees with its evidence, including exact title
   and author text, valid date-derived years and blank absent journals. PMID 28
   is never promoted for publication 1165.
4. All publication, screen and evidence foreign keys resolve to the right entity
   type. No duplicated entities from many screens referencing one publication.
5. Existing cell values, formulas and reviewer entries remain intact or have
   explicitly recorded conflicts; required headers and sheet order are preserved.
6. Source catalogs, original run artifacts and template hashes remain unchanged;
   use relocation receipts for historical paths rather than rewriting manifests.
7. No spreadsheet formula errors or unsafe interpretation of source text as
   formulas; inspect publication, screen, evidence and reviewer ranges visually.
8. No experimental downloads, no external enrichment, no invented dataset/group
   rows, no omitted identifier conflicts and zero new network requests.

Run the full appropriate offline suite once after the implementation is stable.
The baseline prior to this task is 138 passing tests; report the actual updated
count, workbook row counts, fields added, unresolved categories, material
limitations and output paths. Do not claim qualifying-study retrieval coverage.

## [PEH8] Input fingerprints checked during handoff preparation

| Input | SHA-256 |
|---|---|
| publication-index.json | `0ebd60824abe9832d5eb45f3e65a8765c4a864af13c999476eb4deecb194e76d` |
| publication-screen-links.json | `cf6ad9bad3d657781969e77b4d9ff5b283a8da8bc05a4721477db7d5ce2aac2b` |
| workbook-field-source-map.md | `c18ba5b8b443c96327a4d4213bd414eb577ac50d708f499d8fba22c9c3406f08` |
| Blank reference workbook | `c8e40370121c8ac2a5d7d4480f2dc8ac31c6153a46d473ac8682939762f025ca` |

Recheck these and record all other input hashes before implementation execution.
If a referenced input has changed, diagnose and disclose it; do not silently use
a different source run or refresh to newer data.

## [PEH9] Stop condition and learning checkpoint

Stop after producing and verifying the new workbook and its supporting artifacts.
Do not commit, push, create a remote/PR, implement OmicsDI changes, retrieve
external records, download assets or extend the future reasoning layer.

Learning checkpoint: local publication enrichment adds bibliography and missing
explicit associations while retaining the original filter outcomes. It increases
supported metadata, not certainty about the biological role of a screen.

## [PEH10] Subsequent owner-selected template

The owner subsequently selected [workbook v5](15%20Output%20Workbook%20v5%20Template.md) for future outputs. Its template choice supersedes the earlier seven-sheet model in this handoff. Historical fingerprints above remain historical evidence; record the v5 fingerprint for a future implementation. Preserve all v5 glossary/reference and separator sheets, apply the documented header aliases, and resolve the Sources sheet policy before changing it. Registration does not itself execute this handoff.
