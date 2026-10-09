# v0.2 decision log

- **2026-10-08 — PubMed-first staged enrichment.** Source: repository-enrichment
  conversation, owner request following F1. Inspect PMID 28611215 first and
  provide a readable programmatic output. A subsequent 10-publication stage
  will inform output-column selection; the intended later collection is all
  publications represented in ORCS. This direction expands the earlier
  retained-pilot priority, but the current execution is limited to one entry.
  Review the one-entry result before dispatching the 10-entry stage and settle
  columns, limits and preservation rules before a full-collection run. Keep
  reviewer-facing PubMed website links. No full text or experimental-file
  retrieval is included.

- **2026-10-08 — Handoff boundaries adopted.** Source: DeathMap-AI conversation
  request reviewed in reply C. Add the owner's Codex Handoff Rules and repeated
  rebuild incident to workflow/global/AI-agent-workflow. The rules govern bounded
  handoffs; the incident is historical context. Preserve the supplied notes
  unchanged and apply them locally, without installing global configuration or
  launching audits, pipeline rebuilds or another task.

Accepted decisions only. Entries record the scope of the owner's instruction;
they do not grant broader retrieval or implementation permission.

- **2026-10-08 — Fixed publication-date display adopted.** Source: owner
  request following Q2/Q4, reply R. Use `yyyy-mm-dd` for complete publication
  dates and retain partial dates as source-precision text. Save a new template
  version and a separate date-format-only ten-publication output; preserve
  owner-edited sources. The run-local exporter must inherit the template's
  number format rather than impose Excel's built-in short-date format. No
  retrieval or full-collection run is authorized by this formatting change.

- **2026-10-08 — Revised template and ten-publication review authorized.**
  Source: owner request following O2, reply P. Use the owner-edited five-sheet
  PubMed template. Repository Records begins with PMID; omit Links and retain
  MeSH Links for now. Execute a ten-publication metadata review, not a full ORCS
  run. Snapshot the revised template without rewriting the edited source.
  Preserve full relationships and field provenance outside the workbook in
  canonical JSON. PMID is the workbook's common publication index and does not
  establish exact screen attribution. Sample: first nine PMID-bearing rows in
  the biological-classes pilot projection plus previously inspected 28611215;
  this is an exploratory output-review sample, not a coverage benchmark.

- **2026-10-08 — Owner-formatted PubMed template preserved.** Source: owner
  request following L3, reply M. Preserve the formatted header workbook as the
  repository-local PubMed Enrichment template and populate a separate example
  for PMID 28611215 from existing cached responses. Template receipt:
  data/templates/pubmed-enrichment/current-template.json. Keep the original
  workbook and saved template byte-for-byte unchanged; no new retrieval,
  10-entry run, full-ORCS run or production adapter is included.

- **2026-10-08 — MeSH qualifiers and header-only review.** Source: owner
  response to K4/K5, reply L. Include qualifiers in the descriptor-centered
  MeSH view and preserve publication-specific associations and major-topic
  flags. Generate a separate header-only example for approval before the next
  retrieval stage. The proposed grouping by descriptor/qualifier pair and six
  worksheet headers in outputs/pubmed/header-review-20261008 remain pending
  owner approval; the example is not promoted to the production template.

- **2026-10-08 — Proposed output views narrowed.** Source:
  repository-enrichment conversation, owner response to J4, reply K. For the
  next output design, omit Overview; Publication contains PMID, DOI, PMCID,
  Title and Publication Date. Add Repository Record with Resource, accession,
  native entity level, title, description and reported data type. Name the
  relationship sheet Links for consistency. These are output-view decisions;
  preserve raw source evidence and previously accepted reviewer URL availability.
  MeSH organization remains under discussion. The existing inspection workbook
  is preserved; no new retrieval, template promotion or production export is
  authorized by this design note.

- **2026-10-08 — Review fields before the 10-entry stage.** Source:
  repository-enrichment conversation, owner observations following I2 and
  reply J. Assess the PubMed-first approach and select key field groups before
  retrieving 10 publications. Keep SRA experiment, study, sample, BioProject,
  BioSample and run accessions as available; defer deeper sample-level metadata
  inspection and gene-level enrichment. No experimental-file retrieval is
  authorized. This records review direction, not approval of a final schema or
  a new retrieval run.

- **2026-10-08 — Enrichment first.** Source: owner clarification following
  [A144] and response to [A146]. Prioritize enrichment of the ORCS collection.
  Screen grouping follows sufficient repository enrichment. “Study-group” meant
  the existing screen-group concept. Independent discovery is deferred from the
  immediate priority; concrete repository contracts remain unresolved.
- **2026-10-08 — Iteration notes.** Source: owner documentation-reorganization
  message following [A151]. Current iteration is `v02 - ORCS Pilot Enrichment`.
  Record accepted decisions here and unapproved ideas in `ideas-questions.md`.
- **2026-10-08 — Instruction scope.** Same source. Trial project-note recording
  in DeathMap-AI; keep reusable drafts in workflow/global without installing them
  across other projects. Proposed conversational notation is not yet adopted.
- **2026-10-08 — Collaboration status.** Same source. Retire the former
  ChatGPT–Perplexity workflow. Owner researches interfaces manually; occasional
  external clarification is optional and supplies no implementation authority.
- **2026-10-08 — Next session.** Same source. Establish the instructions and
  specifications before preparing the enrichment handoff to a new session.

- **2026-10-08 — Accession labels adopted.** Source: owner accession-label adoption message; DeathMap-AI conversation adoption reply B. Use one letter per assistant reply, resetting point numbers within each reply. Retain the supplied note's reference, artifact and traceability rules; the explicit chat instruction supersedes its continuous A01/A77 numbering. Other proposed conversational terminology remains inactive.

- **2026-10-08 — Current phase and long-term destination clarified.** Source: DeathMap-AI documentation-consistency request, reply H. Current work is v02 repository enrichment of retained ORCS results. The long-term destination is comprehensive cancer/immune CRISPR publication and dataset identification, normalized/analyzed datasets and thorough annotations, especially using the ligand–receptor database previously XDeathDB. This documentation decision does not authorize future experimental-data retrieval, analysis or integration.
# 2026-10-08 — Text dates and repository column order (T3)

Owner authorized a separate PubMed template and ten-publication workbook with
literal Text dates in `MM;DD;YYYY` order, superseding the prior `yyyy-mm-dd`
numeric-date display. Month/year precision uses `MM;YYYY`; year-only stays
`YYYY`. No missing date component is inferred. Canonical source JSON remains
unchanged. Repository Records places Reported Data Type between Native Entity
Level and Title. Prior template/workbook bytes are preserved. Focused checks
compare all values, unchanged package parts, native Excel opening and previews;
no new retrieval or full-collection run is authorized by this formatting change.

## 2026-10-08 — Completed PubMed milestone (U/V)

Owner approved the text-date template as final and authorized whole-index PubMed enrichment, saved-search views, documentation, cleanup and GitHub preparation. One shared PMID-led pass retrieved all 415 verified PMIDs from 418 index records. Three no-PMID records remain unresolved. Save the approved template at `data/templates/PubMed-Enrichment.xlsx`, database and Excel view at `data/orcs`, and separate enrichment workbooks inside the three current ORCS runs. Retain raw responses and receipts. Archive superseded development workbooks byte-for-byte before removing active copies. No ORCS rebuild, experimental download, commit, push or PR is authorized. Next goals: GEO, BioStudies–ArrayExpress and ENA repository-specific enrichment; future contracts remain pending.

## 2026-10-08 — Archive non-recent logs (W2)

Owner authorized archiving non-recent logs. Seventeen top-level logs modified before October 7 were archived with verified hashes and removed from active logs. October 7–8 logs and release-preparation remain active. Keep repository-relocations-20261004.json because production path resolution depends on it. The archive receipt is logs/archive-receipt-20261008.json. No rebuild, retrieval, commit or push occurred.

## 2026-10-08 — Owner-requested biological-classes rerun (Z1)

Archive the edited 20261008T013933234708Z run with verified hashes, remove its active copy, and replace it using the unchanged profile and cached sources. The replacement 20261009T000854143096Z retains 1,830 direct candidates, 56 companions and 328 publications. Regenerate its 327-PMID PubMed view from the shared database with zero retrieval. Both workbooks opened normally in Excel; all three active ORCS workbook/projection manifest hashes now match. One offline search/export pass and one PubMed subset export completed; no commit or push.

## 2026-10-08 — GitHub publication authorized (AA1)

Owner authorized resolved-error cleanup followed by commit and push of the prepared repository. Archived the previous readiness record, removed resolved mismatch details from active status, preserved unresolved scientific records and archive receipts. Eight focused publication tests passed; the remote main branch matched the starting local commit. No live metadata retrieval or workbook regeneration is part of this publication step.
