# DeathMap-AI finding-card agent instructions

## Scope and purpose

These instructions govern research finding cards in the directory containing this file and its subdirectories. Use any more-specific local instructions where applicable; surface material conflicts rather than silently changing scientific rules.

A finding card is one small, traceable research note answering one specific question with one substantive finding. Cards communicate evidence to the project owner and ChatGPT. They are not pipeline configurations, implementation specifications, or automatic authorization to change code.

Use the supplied task and materials as the working context. Do not depend on memory of earlier sessions to establish implementation status, approval, or access to evidence.

## Responsibilities

- **Perplexity:** investigate resource interfaces, search/filter behavior, repository hierarchy, metadata availability, and concrete source examples. Prefer official documentation and original records.
- **ChatGPT:** compare findings with existing specifications and implementation; propose entity boundaries, evidence rules, stage order, review criteria, and necessary implementation changes.
- **Project owner:** decide scientific eligibility, meaningful grouping, acceptable attribution evidence, and material scope changes.

Do not modify pipeline code, filters, the evidence model, historical outputs, or reviewer work unless a separate current instruction explicitly authorizes that action.

## Start-of-task procedure

1. Read this file, applicable local instructions, and the supplied task.
2. Inspect existing relevant cards and supplied source materials before repeating research.
3. Establish the actual accessible baseline. Do not assume that a repository link, remembered artifact, or another assistant's local output is available.
4. Identify the question, permitted actions, limits, expected output, and stopping condition.
5. Ask one concise clarification if missing context or conflicting instructions would materially affect the work.

If no research task is supplied, request one. Reading this file alone does not authorize a discovery run, enrichment run, or repository-wide investigation.

For OmicsDI tasks, establish implementation status and the approved filtering strategy from the current supplied baseline. If discovery is not confirmed operational, report that limitation before treating repository enrichment as the next executable step. Capability research may proceed to establish the missing strategy; it does not require an operational discovery pipeline. Preserve the ORCS pilot unless the current task explicitly authorizes a change.

## Required task context

Use the owner's task description. Request missing material details rather than creating a new task-management schema.

```text
Task and specific questions:
Current state / relevant baseline:
Supplied materials:
Allowed sources and actions:
Excluded work:
Limits: queries / pages / records / source calls / link depth / downloads
Expected deliverable:
Done when:
Stop and ask if:
```

An unspecified limit does not authorize an exhaustive search. Do not start a substantial live retrieval when its scope or stopping condition is unresolved.

## Evidence categories

Assign one category per card:

- **Resource documentation:** what an inspected source explicitly documents.
- **Observed source metadata:** what an inspected record or response contains, or what a particular request demonstrably returned.
- **Proposed interpretation/rule:** reasoning or a suggested rule supported by identified evidence.
- **Owner-approved decision:** an explicit owner decision supported by a dated approval record.

Keep documentation, observations, interpretations, and decisions separate even when they concern the same field. Link separate cards instead of combining different evidence categories into one finding.

Approval of a research note does not change its evidence category. A documented filter does not become observed API behavior merely because the documentation was accepted.

## Research and evidence rules

- Prefer official documentation and original records. Use existing cards and preserved responses before making new requests; check freshness when current behavior matters.
- Cite inspected evidence. Do not invent URLs, quotations, native identifiers, dates, field values, or locators.
- Keep excerpts short and verbatim. Identify omissions or truncation.
- Scope an observation to the inspected sample, request, endpoint, version where known, and date. Report sample size when relevant.
- Do not infer universal field availability from one example, source-wide absence from missing sample fields, or absence of relevant research from a zero-result query.
- Distinguish absent, null, empty, unavailable, and not inspected.
- Separate a scientific question from the literal source query. Do not assume natural-language wording is a valid or effective retrieval strategy.
- Distinguish publication association, dataset identity, and exact screen–dataset attribution. Shared publication identifiers do not establish exact experimental correspondence.
- Do not assume an omics classification establishes scientific eligibility.
- Separate observation/retrieval dates from publication, repository-release, and source-indexing dates. If a date is unknown, say so.
- For proposed rules, reference supporting cards and identify the reasoning as a proposal.
- For owner decisions, use the actual approval instruction or decision record. A public URL or dataset example is not required.

### Observed API behavior

Include the literal request method, endpoint, and query/parameters, relevant response field paths and values, and a preserved-response reference when available.

Distinguish a fresh request from inspection of a saved response. Never include credentials, tokens, or sensitive headers. Do not claim evidence was preserved when it was not.

Reference evidence that the recipient can access through supplied files, shared artifacts, or the authorized project materials. Do not rely only on a temporary location visible to one assistant.

## Resource limits and stopping

Respect the supplied limits across the entire task, including retries. Track work in observable units; disclose any requested limit that cannot be reliably measured.

Do not estimate or guarantee a credit cost. Do not expand into all repositories, recursively traverse linked records, download experimental data, inspect the entire literature, run a benchmark, or delegate to additional agents without explicit authorization.

When a cap or blocker is reached, return partial findings and identify what was not inspected. Stop when the requested deliverable is complete; do not begin implementation or a larger research phase.

Do not investigate unrelated records simply to populate every card field. An unresolved but well-supported answer is a valid finding.

## Card files and identifiers

- Save one card per Markdown file in this directory, unless an existing owner-approved layout specifies otherwise.
- Use stable filenames such as `F001.md`, `F002.md`, and so on.
- Inspect existing identifiers before allocating the next unused ID. Do not renumber cards or reuse identifiers from known rejected or superseded cards.
- Preserve the ID and filename when revising the same substantive finding. Create a new linked card for a different substantive claim or evidence category.
- Do not create a new index, logging system, validator, script, or pipeline schema merely to manage cards.
- If the destination directory is unavailable, disclose that. Deliver the card files through the available file mechanism without claiming they were written to the intended destination.
- If this file was supplied only as an attachment, do not assume its temporary attachment location is the owner's intended card directory.

## Card template

Use the following Markdown structure. API and revision fields are conditional.

```markdown
# F001: [Short descriptive title]

- **Question:** [One specific question.]
- **Finding:** [One concise, evidence-bounded statement.]
- **Category:** [One category from these instructions.]
- **Source and citation:** [Descriptive Markdown citation to the inspected
  source URL, or a supplied evidence/approval record when no public URL exists.]
- **Evidence location:** [Section, response field path, table, page, or
  another precise locator.]
- **Identifiers:** [Relevant native identifiers, or Not applicable.]
- **Date and method:** [When and how checked; distinguish fresh retrieval
  from review of saved evidence. Record unknown dates explicitly.]
- **Supporting evidence:** [Short verbatim excerpt or exact field value.
  For a proposal, reference supporting cards and separate reasoning.]
- **Uncertainty:** [Missing information, conflicting evidence, sample
  limitations, and what this finding does not establish.]
- **Example:** [One supporting record if available, otherwise Not applicable
  or Not inspected with a short explanation.]
- **Workflow implication:** [Suggested action, approval needed, or a
  question that should remain unresolved. Do not imply implementation.]
- **Review status:** [Proposed / Awaiting owner review / Accepted /
  Revised / Rejected; include the owner/date/review record when applicable.]

## API observation

[Include only for observed API behavior.]

- **Literal request:** [Method, endpoint, and query/parameters; no secrets.]
- **Response field paths:** [Exact relevant paths and returned values.]
- **Preserved-response reference:** [Accessible evidence reference, or
  Not preserved / Not supplied.]

## Related cards and revisions

[Include only when applicable.]

- **Related cards:** [IDs and relationships: supports, conflicts with,
  derives from, or supersedes.]
- **Revision note:** [Date, what changed, and the prior finding if materially
  changed. Preserve meaningful earlier evidence and review history.]
```

## Review and revision rules

New cards default to **Proposed**. Use **Awaiting owner review** when requesting a decision.

Use **Accepted** or **Rejected** only with an explicit owner review record. Acceptance of a documentation or observation card means the note was reviewed; it does not authorize its suggested workflow change.

Use **Owner-approved decision** only when the owner explicitly made the decision. Do not infer approval from silence, a previous related approval, or another assistant's recommendation.

**Revised** records an edit, not renewed approval. A materially changed accepted rule must return for owner review. Do not silently remove prior contradictions, limitations, or meaningful review history.

## Completion handoff

Provide a brief summary containing:

- **Status:** complete, partial, or blocked.
- **Cards:** IDs created or revised and their delivery locations.
- **Coverage:** sources, records, or cases actually inspected.
- **Limits:** any cap reached or measurement limitation.
- **Open decisions:** only the decisions needed for the next step.

Do not return only “verified” or “validation passed.” State what was actually checked and which scientific or implementation questions remain unresolved.
