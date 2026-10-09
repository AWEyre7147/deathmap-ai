---
title: Codex Handoff Rules
type: primary-workflow
---

# Codex Handoff Rules

Apply these instructions whenever this note is supplied as context to a ChatGPT project. They govern how ChatGPT scopes and writes work for Codex, and must be carried into each handoff. Creating this note does not itself configure automatic loading into other projects.

## Purpose

Produce useful, bounded Codex tasks without turning a small request into an open-ended implementation, audit or validation project. Respect the user's available resources. Preserve accepted decisions and completed work. Prefer the smallest deliverable that satisfies the current request.

## 1. Estimate resources before drafting

Present a brief estimate of low, moderate or high effort, with the factors driving that estimate and its main uncertainty. Assess both model work (reasoning, reading and editing) and execution work (downloads, builds, rendering and tests). Long command runtime is not itself a measure of model-token usage.

- Low: a focused note, a small edit or a bounded inspection using known files.
- Moderate: changes across several related files with focused validation.
- High: broad codebase documentation, cross-source investigation, full data rebuilds, repeated rendering, environment migration or publication/legal review.

These are planning categories, not promises of elapsed time, tokens or account usage. Do not invent exact costs or claim to know remaining account capacity without checking it. Give ranges only when there is a defensible basis. If the scope is uncertain, propose a small read-only inventory first. Split high-effort work into useful milestones instead of issuing one exhaustive handoff.

## 2. Give each handoff one bounded deliverable

State the outcome, exact files or modules in scope, and observable acceptance criteria. Distinguish implementation from a proposal or review. Describe how Codex should interpret completion, rather than relying on phrases such as fully ready, exhaustive or production-ready.

Documentation, code commenting, cleanup, portability work and publication readiness are separate deliverables by default. Do not bundle them just because they concern the same project. Reuse existing schemas, reports and verified results instead of repeating completed research.

## 3. Include explicit exclusions

State which adjacent activities are outside the task. For documentation-only work, default exclusions are data rebuilding, dependency changes, architecture refactoring, new automated checks, licensing investigation, historical audits and publication. Read existing outputs and code only as needed to document the requested scope.

For comments-only work, preserve behavior and public interfaces. For cleanup, identify specific disposable artifacts; preserve source data, authoritative outputs, provenance, active recovery files and unrelated user changes. Repository preparation does not imply permission to commit, push, publish or rewrite history.

Record useful out-of-scope discoveries in a short backlog. Do not implement them automatically.

## 4. Define checkpoints before expensive work

Name foreseeable expensive operations in advance: full rebuilds, whole-repository test suites, repeated exports/renders, bulk downloads, new environments and substantial dependency changes. If such work is already explicitly included and accepted, do not ask for the same approval again.

When an unplanned expensive operation or scope expansion becomes necessary, preserve completed work and report:

- What is complete.
- What triggered the additional work and why it matters.
- The smallest next step, estimated effort and cheaper alternative if available.

Stop at that checkpoint until the user chooses the expansion. A progress update is not approval. Continue only independent work already within the agreed boundary. In particular, do not automatically launch a full rebuild merely because comment/docstring edits changed implementation hashes: report that consequence and offer a separately scoped validation task. Never falsify or bypass provenance checks to avoid the rebuild.

If the user specifies a time or resource budget, include it verbatim. Describe it as an operational checkpoint unless a genuine enforceable limit is configured; do not pretend prose guarantees a hard cap. Do not silently raise a budget or continue beyond a stop instruction.

## 5. Set a stopping condition

Specify the minimum sufficient verification and the exact point at which Codex should return control. Stop when the named deliverable and checks pass. Do not add optional polishing, broaden test coverage, rerun unchanged checks or begin the next milestone without a new reason or request.

For documentation, verify the scoped field/command descriptions and links against existing files. Do not require biological data regeneration. For code, run focused tests appropriate to the change; run broader checks only when required by the repository or an identified risk. Report conflicting requirements instead of silently expanding the task.

At completion, summarize changed files, checks performed, limitations and deferred work. If interrupted or budget-limited, report a checkpoint honestly; do not mark unfinished work complete. If asked only for status, answer from current evidence without launching new audits.

## 6. Bound repeated validation and freeze edits

For every accepted expensive workflow, state the maximum number of full rebuild/export passes. Documentation-only work defaults to zero. If one full pass is explicitly accepted, finish all intended implementation edits before starting it; do not edit hash-tracked implementation files while it runs. A second expensive pass is a checkpoint, not an automatic consequence of optional polishing or a documentation/report correction.

When another pass seems necessary, identify the actual defect, distinguish scientific/output correctness from presentation or provenance-only changes, explain the smallest sufficient check and preserve the previous valid release. Do not falsify hashes, weaken checks or redesign provenance as a shortcut. Record the limitation and defer further expensive work unless the user accepts it. Reuse already valid results.

Track model effort separately from execution work. Do not infer tokens, account capacity or monetary cost from command duration. Report exact resource usage only when available from reliable measurements; otherwise state the uncertainty.

## 7. Stop means cancel owned active and queued work

A stop instruction revokes permission to continue the task's execution, including previously queued work. Before returning:

- Cancel owned waiting launchers and scheduled follow-on commands so they cannot start another job.
- Identify and stop only the task's own active processes. Prefer graceful cancellation with a short bounded shutdown period; preserve staging/backup recovery material rather than completing a long build merely for neatness.
- Do not launch builds, tests, audits or cleanup unless the user separately authorizes them. A minimal ownership/process check needed to stop work is part of cancellation, not permission for a new audit.
- Never terminate unrelated user processes. If ownership or cancellation is uncertain or blocked, immediately report the precise unresolved state instead of implying everything has stopped.
- State which work is complete, what is partial, and whether any owned work remains active. Returning a final message is not itself cancellation.

Do not create a background launcher simply to keep expensive work going after control returns to the user. When background execution is necessary and authorized, retain its process/job identity and cancellation method, including any child or queued jobs.

## Incident example

[Repeated rebuilds during documentation](incident-repeated-rebuilds.md) records a real failure: whole-file provenance hashes triggered regeneration, unfinished commenting/report edits triggered repeated expensive passes, and queued work was not cancelled on an explicit stop. Use it when reviewing handoffs for accidental rebuild loops and missing cancellation boundaries.

## Required handoff structure

Use these fields in every handoff, keeping detail proportional to the task:

1. Objective and one deliverable.
2. Effort estimate, cost drivers and uncertainty.
3. Relevant inputs and authoritative accepted decisions.
4. Files/actions in scope.
5. Explicit exclusions and files to preserve.
6. Minimum acceptance criteria and verification.
7. Checkpoint triggers, accepted full-pass limit, cancellation boundary and any user-specified budget.
8. Stopping condition and completion summary.

For a larger request, present the milestone sequence but dispatch only the current bounded milestone. Before presenting the handoff, review it as Codex would: could its wording authorize an unexpected rebuild, exhaustive audit, dependency migration or endless verification? Remove those unintended obligations.

Provide a short copyable dispatch message that points to the saved handoff and repeats its most important scope and stopping boundaries. Creating the handoff does not execute it or create another task automatically.

## Example: bounded field-guide task

**Objective:** Document columns in the primary interaction table using the existing schema and build report.
**Effort:** Low to moderate; depends on how many fields lack established descriptions.
**Scope:** Update the existing dictionary's primary-table section only.
**Exclude:** Supporting-table expansion, code changes, data rebuilds, new tests, dependency work and publication review.
**Verify:** Every primary-table column is documented, examples match existing data, and edited links resolve.
**Checkpoint:** If a field's meaning cannot be established from existing code/data, flag it rather than performing open-ended research.
**Stop:** Return the updated note, verification summary and unresolved fields. Do not begin script documentation or cleanup.

## Mandatory pre-dispatch assessment

Include this short assessment with every proposed handoff. It belongs in the user-visible proposal and the saved handoff, not only in internal reasoning:

- **Deliverable and boundary:** one named result; exact files/modules or an explicitly bounded inventory.
- **Effort:** low/moderate/high; main drivers and uncertainty.
- **Allowed expensive work:** named operations and maximum full-pass count; zero full rebuilds for documentation/comment-only tasks unless explicitly accepted.
- **Verification boundary:** named checks, with no automatic escalation to broader suites or repeated passes.
- **Instruction conflicts:** local instructions, provenance hashing or dependencies that could require work outside the boundary; resolve before dispatch when known.
- **Checkpoint and stop:** what unexpected condition returns control to the user, and what observable result ends the task.

Codex should make a brief preflight comparison between this scope and the actual repository before editing. A discovered conflict or high-effort prerequisite triggers a checkpoint rather than silent expansion. This is a bounded check of relevant instructions and inputs, not a new repository-wide audit. Explicit user instructions override generic defaults; preserve previously accepted authorization rather than repeatedly requesting it.

## Troubleshooting boundary and estimates

A failed planned check does not authorize an unlimited repair loop. Fix a clear in-scope defect and rerun the affected lightweight check once. If that rerun fails, the cause remains uncertain, or the remedy requires broader edits, new dependencies or expensive validation, return a checkpoint with the failure and next-step estimate. Handoffs may specify a different bounded retry allowance when the user accepts it. Full rebuilds remain governed by the accepted pass limit, not by the lightweight retry allowance.

Do not spawn subagents or dispatch parallel coding tasks unless explicitly authorized; when proposed, include their scope and combined resource implications in the estimate. Do not repeatedly poll unchanged long-running work or read large logs without a specific diagnostic question. Existing authorized background work remains subject to the cancellation rules above.

Effort labels and written stop rules reduce risk but are not hard usage enforcement. If the user needs a firm cap, use a supported enforceable control when available and verify what it limits; otherwise say clearly that only operational checkpoints are being set. Never promise these notes will prevent all resource exhaustion.
