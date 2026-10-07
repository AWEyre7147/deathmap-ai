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

## [AG7] Current constraints

- Follow [release preparation](docs/specifications/18%20Repository%20Native%20Discovery%20Release%20Preparation.md) and the current work session. Retired SQ01 contracts are historical, not current defaults.
- Preserve ORCS vocabulary and saved source metadata. No live enrichment or experimental-file download is authorized in release preparation.
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
