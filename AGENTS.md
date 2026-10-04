# DeathMap-AI Agent Instructions

## [AG1] Source of truth

The authoritative v0.1 specifications are located in
[`docs/specifications`](docs/specifications/README.md).

Read `project-vision-v01.md`, `module-01-evidence-discovery.md`, and the current
work-session specification before making consequential changes. If chat
instructions and a written specification conflict, identify the conflict before
proceeding.

## [AG2] Scope control

- Implement only what the current module and work-session specifications require.
- Do not build the future reasoning layer, patient-context integration, graph
  interface, or generalized biomedical search engine during milestone 1.
- Put useful but nonessential ideas in the backlog instead of implementing them.
- Do not silently make consequential scientific or architectural assumptions.

## [AG3] Collaboration and review

- Use stable point labels such as `[A1]`, `[A2]`, or the letter series already
  active in the conversation so the project owner can reply precisely.
- Do not renumber an existing labeled point when revising a document.
- Prefer small, reviewable changes.
- In spreadsheet review outputs, place active reviewer-entry columns together at
  the far right and fill them yellow. Fill the reviewer cells for rows currently
  requesting project-owner attention orange. Keep the underlying review fields
  and notes as the scientific record; color is a visual navigation aid, not the
  only representation of review status. Remove review columns when they are no
  longer used and all requested review work has been resolved.
- Before finishing, report what changed, what was tested, assumptions made, open
  questions, and any learning checkpoint introduced.
- Do not commit, push, create a remote, or open a pull request unless the project
  owner requests that action.

## [AG4] Code readability

All generated or substantially modified code must follow
[`docs/code-commenting-standard.md`](docs/code-commenting-standard.md).

Comments should help a scientifically trained reader understand intent,
evidence-handling choices, non-obvious transformations, and failure behavior.
They must not merely translate each line of code into English.

## [AG5] Scientific traceability

- Preserve source identifiers and provenance through every transformation.
- Keep publication, experiment, screen, dataset, and sample-level entities
  distinct unless the specification explicitly defines a justified merge.
- Mark direct evidence separately from inferred relationships.
- Preserve unresolved and conflicting relationships rather than forcing them
  into a false single answer.
- Never treat publication-dataset association as proof that the dataset contains
  the qualifying CRISPR experiment.

## [AG6] Verification

- Add or update tests for implemented behavior.
- Prefer small fixtures that can be inspected manually.
- Never claim successful retrieval coverage from an unadjudicated candidate pool.
- Record tool version, query strategy, retrieval date, and raw identifiers needed
  to reproduce a benchmark run.

## [AG7] Pilot constraints

- The owner-authorized shared ORCS publication database follows [handoff 13](docs/specifications/13%20ORCS%20Shared%20Publication%20Metadata%20Database.md). Its publication-header retrieval exception is separate from historical filtered runs; no gene-level or linked experimental file contents may be retrieved.

- Owner-approved repository organization follows [handoff 12](docs/specifications/12%20Repository%20Organization%20and%20Workbook%20Planning.md). Historical outputs may be relocated to the approved external archive with unchanged bytes and a hash/path registry. This location exception supersedes older in-repository path constraints; it does not authorize new retrieval or enrichment.


- For the separate owner-authorized ORCS profile-filtering and Excel task, follow
  [`docs/specifications/11 ORCS Filter Run and Excel Handoff.md`](docs/specifications/11%20ORCS%20Filter%20Run%20and%20Excel%20Handoff.md).
  Its explicit exceptions apply only to that new task; preserve historical SQ01
  outputs and do not begin external enrichment before Excel review.

- Follow [`docs/pilot-scope.md`](docs/pilot-scope.md) during the iterative
  co-culture discovery phase.
- Follow
  [`docs/specifications/10 SQ01 Blind Discovery Handoff.md`](docs/specifications/10%20SQ01%20Blind%20Discovery%20Handoff.md)
  for the current v03 scope. The first live v03 run is SQ01-only. Do not execute
  SQ02 or the abandoned broad query `CRISPR AND screen AND cancer AND immune`.
- Preserve v01 and v02 as immutable historical iterations. The v02 5,000-native-
  record cap, 50-new-detail-attempt allowance, 89 historical receipts, and
  50-within/39-excess accounting retain their historical meaning and must not be
  reset, borrowed, or applied as v03 limits.
- The v03 SQ01 OmicsDI search has no unique-candidate cap, search-page cap, or
  total-runtime cap. Exhaust every approved query through pagination unless an
  explicit error blocks it. Keep bounded per-request timeouts, service pacing,
  cumulative retries, durable request reservations, and resumable progress.
- OmicsDI detail requests and repository enrichment are not authorized in the
  SQ01 blind-discovery slice.
- Search the complete existing cached ORCS index once for SQ01 with no candidate
  or runtime cap and no refresh. Stop successfully after every cached screen is
  examined once; stop with an explicit error on missing, corrupt, or unrecognized
  cache input. Preserve field-level match evidence and publication siblings as
  context rather than direct hits.
- Generate resource-specific JSON under
  `outputs/<package>/immune-crispr-coculture-v03/` and shared run-plan/summary
  artifacts under `outputs/immune-crispr-coculture-v03/`. Do not generate the
  seven entity tables or an Excel workbook in this slice.
- Treat local ICRAFT files as validation-only references. Do not use their titles,
  identifiers, accessions, or metadata as search inputs, query expansions,
  allowlists, or production dependencies.
- Do not add code for scoring against ICRAFT or testing ICRAFT accessions to the
  first released version of module 1.
- Metadata discovery is allowed within the current handoff. Do not download gene-level screen results,
  guide counts, FASTQ files, processed matrices, or other experimental datasets
  during the metadata-only pilot.

## [AG8] Boundary coaching

- When a proposed boundary helps isolate a resource, control scope, protect
  provenance, or keep iteration fast, state why it is useful and give one
  project-specific example.
- When a boundary would prevent the stated objective or make the result
  misleading, challenge it before proceeding and give one concrete example of
  what would remain missing.
- Do not cross an accepted boundary silently. Propose a separate stage or revised
  boundary and wait for project-owner authorization when the change is material.

Example of a useful boundary: an ORCS-only pass reveals exactly what ORCS
contributes; silently adding PubMed metadata would contaminate that evaluation.

Example of an unhelpful boundary: retaining ORCS-only restrictions during a
later dataset-attribution stage would leave accessions unresolved even when the
publication or repository supplies decisive evidence. At that stage, propose a
separate external-enrichment pass.
