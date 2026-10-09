# DeathMap-AI Agent Instructions

## [AG1] Source of truth

The active project specifications are located in
[`docs/specifications`](docs/specifications/README.md).

Read `project-vision-v01.md` and `module-01-evidence-discovery.md` before making
consequential changes. If chat
instructions and a written specification conflict, identify the conflict before
proceeding.

## [AG2] Scope control

- Implement only what the current project vision and module specification require.
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
[`code-commenting standard`](docs/workflow/global/coding/code-commenting-standard.md).

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

## [AG7] Current constraints

- Follow the active project vision and module specification. Historical task notes and retired SQ01 contracts do not authorize new work.
- Preserve ORCS vocabulary and saved source metadata. The owner-authorized PubMed milestone is complete; release preparation alone does not authorize additional live enrichment. GEO, BioStudies–ArrayExpress and ENA passes require their own accepted contracts. Experimental-file downloads remain out of scope.
- Preserve the owner's edited workbooks byte-for-byte. Export only into new run directories. Promote the repaired template only after owner approval.
- Keep validation references outside production discovery; no benchmark identifiers as query inputs or production dependencies.
- Historical artifacts may be archived with unchanged bytes and hash/path receipts. No commit, push or PR without an explicit owner request.

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

## [AG9] Conversation workflow

- Read [user and AI-agent responsibilities](docs/workflow/project/AI-agent-workflow/responsibilities.md).
- Read [point accessions](docs/workflow/global/AI-agent-workflow/accession-labels.md),
  [notation status](docs/workflow/global/AI-agent-workflow/user-notation.md), and
  [project notes](docs/workflow/project/AI-agent-workflow/project-notes.md).
- Follow the adopted accession-label note: bold A1/A2 items in the first reply,
  B1/B2 in the second, and subsequent letter series per reply. Commentary and
  final text share the reply letter and consume distinct point numbers. Preserve
  historical quoted IDs; never retrospectively renumber them.
- The Explore/Remember/Decide/Do notation is proposed and not yet adopted.
  Use clear ordinary language to distinguish authorization from speculation.
- Record accepted decisions and unapproved ideas separately in the current
  iteration under `docs/development/v02 - ORCS Pilot Enrichment/`.
- Files under workflow/global are reusable local drafts, not instructions
  installed across other projects. Project-note recording is a DeathMap-AI trial.
- The former ChatGPT–Perplexity collaborative workflow is retired; do not require
  Perplexity handoffs or treat its suggestions as authoritative.
- Apply [Codex handoff rules](docs/workflow/global/AI-agent-workflow/codex-handoff-rules.md)
  when scoping or writing Codex tasks. Include bounded deliverables, effort,
  exclusions, verification, expensive-pass limits, checkpoints and stopping rules.
  Previously accepted authorization and explicit owner instructions take precedence.
- [Repeated rebuild incident](docs/workflow/global/AI-agent-workflow/incident-repeated-rebuilds.md)
  is historical supporting context, not a new audit or execution instruction.
  Documentation-only tasks authorize zero full rebuild/export passes by default.

## [AG10] Specification templates and lifecycle

- Reusable templates are in `docs/workflow/global/specifications/`: project vision,
  module specification and their structure. Templates are standalone and omit
  cross-document dependencies.
- A current-work-session specification is not required by the new template
  structure. Existing accepted specifications retain their authority until an
  explicitly authorized revision or migration; do not silently delete them.
- Session logs may record work without becoming specifications or granting
  implementation authorization.
- [Specification lifecycle](docs/workflow/global/AI-agent-workflow/specification-lifecycle.md)
  is pending. Rules for new versions, updates and additional specifications must
  be agreed before automatic lifecycle behavior is introduced.
