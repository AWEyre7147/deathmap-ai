# ORCS filter run and Excel handoff

## [OFH1] Authorization and scope

The project owner authorized this handoff on 2026-10-03: implement and run the
accepted ORCS filter profile, summarize the results, and, if there are matched
screens, populate the owner's Excel output using available evidence. This is an
ORCS-only pipeline test. Complete implementation, tests, local execution and Excel
population autonomously within this scope; do not stop after writing another plan.

This handoff supersedes the JSON-only stop and entity/Excel deferral in
`searches/orcs/cancer-cell-crispr-knockout-v01-run-plan.md` and the corresponding
work-session restrictions **only for this new ORCS filtering stage**. It does not
change the historical SQ01 blind-discovery run, its native-only interpretation,
or historical outputs. Do not run SQ02, OmicsDI, benchmark comparisons, or external
enrichment. Do not commit or push. Network enrichment is a subsequent stage to
discuss after the Excel output is delivered.

## [OFH2] Inputs and destination

- Profile: `searches/orcs/cancer-cell-crispr-knockout-v01.json`.
- Cached ORCS index and its completeness summary:
  `outputs/orcs/cache/legacy/20260904T213941Z/`.
- Saved annotations: `docs/references/orcs-vocabulary-annotations/annotations.json`.
- Run plan: `searches/orcs/cancer-cell-crispr-knockout-v01-run-plan.md`.
- Excel destination: `data/output-example/DeathMap-AI-v1-reference-output.xlsx`,
  the blank, header-bearing workbook selected by the owner. Do not use
  `data/brainstorming/DeathMap-AI-output-v4.xlsx` as the output template. The old
  filled `DeathMap-AI-output-brainstorm-examples.xlsx` is no longer relevant and
  must not supply search inputs, example results or retrieval ground truth.

All paths are relative to the repository root. The expected cache contains 2,217
unique screens. Confirm counts, cache/reference hash agreement, schema and unique
annotation keys before execution. Save exact profile and annotation snapshots,
input hashes, original retrieval dates, current execution time and code version.
Use a new run directory under
`outputs/orcs/filter-runs/orcs-cancer-cell-crispr-knockout-v01/<UTC-run-id>/`.

Inspect the selected workbook's actual headers, glossary and layout before export.
Preserve its sheet names, exact headers, formulas, formatting, existing data and
reviewer edits. Back up the original byte-for-byte in the run directory before
updating it; also save the populated result there. Append or update by stable
identity rather than replacing unrelated rows. Template examples are not evidence.

## [OFH3] Implement and execute the filter

There is no existing runner for this JSON profile. Add the small local runner and
fixture tests proposed in the run plan, reusing existing validation/provenance
ideas without modifying historical SQ01 matching semantics. Support and validate
only the operations used by the accepted profile.

All seven criteria must pass, using exact source spelling/case:

| Field | Accepted values |
| --- | --- |
| CELL_LINE joined category | Cancer cell line |
| ENZYME | Cas9 |
| LIBRARY_TYPE | CRISPRn |
| METHODOLOGY | Knockout |
| SCREEN_FORMAT | Pool |
| ORGANISM_OFFICIAL | Homo sapiens OR Mus musculus |
| PHENOTYPE | cell proliferation OR cell viability OR cell cycle progression OR cell migration |

Join `CELL_LINE` exactly to annotation `cell_lines[].value`, reading `category`.
Preserve reference accessions, match method, evidence location and review issues.
Evaluate each native screen once; save the matched, unresolved-category and
excluded outcomes and all criterion results. Missing cancer categories go into
the unresolved list only when the other six criteria pass. Conflicts are flagged
without an additional unrequested exclusion rule.

Immune cell type and experimental setup are intentionally unrestricted. The owner
expects varied immune partners and incomplete/multiple-population descriptions;
requiring a particular label could remove relevant co-culture candidates. Do not
add an immune, exposure, co-culture keyword, or partner-cell gate.

Preserve all cached publication siblings of matched screens as a **separate
context collection**, keyed by valid exact `(SOURCE_TYPE, SOURCE_ID)` pairs.
Exclude direct matches from this extra collection, deduplicate by `SCREEN_ID`,
and record which matching screen(s) supplied the publication association. Keep
their original filter outcomes and mark their role `publication_sibling_context`.
For example, a sibling screen performed in primary T cells may fail the cancer
criterion yet provide useful context for the cancer-cell screen in the same paper.
Publication siblings are neither filter hits nor confirmed co-culture evidence.
This cannot recover studies that have no matching anchor screen in the cache.

## [OFH4] JSON and human-readable summary

Produce the manifest, profile/reference snapshots, `matched_screens.json`,
`unresolved_screens.json`, `screen_audit.json` and `summary.json` defined in the
run plan, plus `publication_siblings.json` and a compact `summary.md`.
Reconcile the three filter outcomes to all examined screens; context membership
is an additional relationship, not a fourth outcome or extra discovery hit.

Report matched screens, distinct reported publications, unresolved categories,
context-only siblings, annotation conflicts, and independent/cumulative filter
counts. Include links to artifacts and state whether there were hits. A hit means
the filter passed, not that immune interaction or scientific eligibility is proven.
If there are no hits, still deliver the audit and summary without silently relaxing
filters; do not insert fabricated results into Excel.

## [OFH5] Excel propagation and entity identities

If there are hits, populate the selected workbook's existing entity sheets using
matched screens and clearly identified context siblings. Keep unresolved-category
records available for review with an explicit role. Do not combine their counts
with direct hits. Preserve these roles in existing notes/status fields and JSON;
add a minimal review view only if necessary to keep the distinction readable.

Generate deterministic internal publication, screen, dataset (where supported),
link and evidence IDs from native identities. IDs must remain stable across reruns,
not depend on row positions, and not collide with existing workbook identities.
Use reported publication type/identifier for publication identity and ORCS
`SCREEN_ID` for screen identity. Preserve the native identifiers alongside generated
IDs. Resolve foreign keys to the existing workbook before appending duplicates.

| Sheet | Supported propagation and limits |
| --- | --- |
| Publications | Generate/reuse publication ID; map `SOURCE_TYPE` and `SOURCE_ID` to PMID or DOI as reported; generate corresponding URLs; record ORCS provenance. `AUTHOR` is an abbreviated reported attribution, not a full author list. Leave absent titles, journals, PMCID and full authors blank, preserving attribution in notes. Do not extract a publication year from an author label without marking it as derived. |
| Screens | Generate/reuse screen ID and supported publication link. Map `SCREEN_NAME`, `METHODOLOGY`, `ENZYME`, `LIBRARY`, `LIBRARY_TYPE`, `CELL_LINE`, `ORGANISM_OFFICIAL`, `CONDITION_NAME`, `CONDITION_DOSAGE`, `DURATION`, `PHENOTYPE`, `ANALYSIS` and `NOTES` to their corresponding reported fields. Preserve `SCREEN_FORMAT`, `EXPERIMENTAL_SETUP`, `SCREEN_TYPE`, MOI, rationale and significance metadata with evidence, using explicit documented crosswalks for normalized fields. |
| Screen Groups | Populate only if available source evidence establishes an actual shared design. A publication or a common filter match alone is not a screen group; otherwise leave group relationships unresolved. |
| Datasets | Create rows only for dataset identities actually reported in available metadata or already supported in the selected workbook's evidence. Keep repository accession and level distinct from an internal ID and native ORCS screen ID. Do not invent GEO/SRA accessions or duplicate every screen as a repository dataset merely to fill this tab. Leave unsupported fields empty. |
| Screen-Dataset Links | Resolve explicit source-supported relationships with evidence and attribution status. Publication association alone is not an exact screen-dataset link. Retain publication-only or ambiguous associations without upgrading them to confirmed screen links. |
| Sources & Evidence | Create evidence rows for native cached ORCS records and saved reference facts, with original retrieval time, source identity, field/JSON location, reference accession, tool version and supported entity. Keep derived mappings distinguishable from reported facts. |
| Discovery Resources (or corresponding existing sheet) | Record the actual ORCS contribution and use of saved Cellosaurus reference annotations. Do not report OmicsDI or enrichment retrieval as performed. |

Do not infer immune partners, interacting populations, co-culture configuration,
effector:target ratios, disease eligibility, guide counts or dataset availability
from an uninformative label. `FULL_SIZE` and `FULL_SIZE_AVAILABLE` concern ORCS's
screen result set; they do not establish sequencing sample counts, library design
size, FASTQ availability or downloadable repository data. Keep unsupported fields
blank and record their missing evidence in notes/audit.

Use the source glossary where available, and document the field mapping before
writing cells. Honor the selected template's exact spelling, including existing
header typos, rather than renaming unrelated columns. Keep reviewer-entry columns
together at the far right, yellow, with currently requested reviewer cells orange,
as required by AGENTS.md; preserve textual review status as the scientific record.
Follow the spreadsheet skill's authoring and visual verification workflow.

## [OFH6] Tests, verification and delivery

Test the run-plan cases plus sibling-context separation, deterministic entity IDs,
publication deduplication, foreign-key integrity, absent dataset evidence, and
preservation of workbook content/reviewer edits. Check that no network retrieval
is invoked during this run and that all source/historical hashes remain unchanged.

Reopen the exported workbook, reconcile its populated rows with the JSON records,
verify references/URLs and inspect representative populated ranges visually.
Check formulas and relevant formatting after export. Keep a machine-readable
projection and mapping alongside Excel so the workbook is not the only evidence.

Deliver the hit summary and populated workbook link (if hits), explain populated
and unavailable fields, review issues and source limitations, and list remaining
enrichment questions. The next stage should examine whether ORCS individual
screen/publication pages supply additional metadata, accession links, experimental
notes and co-culture details. Do not retrieve those pages or other repositories
in this handoff; the owner will decide the enrichment scope after reviewing Excel.

Learning checkpoint: generated indices organize evidence; they do not create
biological relationships. Populate what the available source supports, preserve
unresolved links, and let the first workbook reveal which enrichment is needed.

## [OFH7] Owner-approved organization update — 2026-10-04

[Handoff 12](12%20Repository%20Organization%20and%20Workbook%20Planning.md) records the current structure and the authorized external relocation of historical artifacts. The blank workbook is now a shared data/templates input; populated results remain in per-run output directories. Original run evidence is preserved unchanged. This update authorizes planning only, not enrichment.
