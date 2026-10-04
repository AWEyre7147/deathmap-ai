# 09 V03 Query Planning and Initialization Handoff

## [H3-1] Status and authorization

The project owner authorized implementation of this limited handoff on 2026-09-27.

This handoff authorizes an offline v03 query-planning and run-initialization slice.
It does not authorize live network retrieval. The implementation must stop after
producing a reproducible proposed query-plan manifest for review.

The authoritative specifications are:

- `docs/specifications/project-vision-v01.md`;
- `docs/specifications/module-01-evidence-discovery.md`; and
- `docs/specifications/work-session-v03-discovery-enrichment.md`.

The detailed design under review is
`docs/proposed-discovery-enrichment-v03.md`. If this handoff conflicts with an
authoritative specification, stop and present the conflict to the project owner.

## [H3-2] Why this is the first implementation slice

The completed v02 implementation combines fixed OmicsDI queries, historical-state
reuse, retrieval scheduling, and entity export. V03 begins from new scientific
questions and must not inherit the old query family silently.

An offline planning layer creates a safe boundary between scientific intent and
network behavior. It makes the proposed literal queries, filters, limits, routing,
and exclusions reviewable before any request can consume service capacity or alter
the evidence pool.

Project-specific example: the question “pooled CRISPR knockout screens in immune
cells under cancer-cell-mediated selection” must not be reduced silently to the
v02 query `CRISPR AND "T cell"`. The planned queries must show how pooled screening,
immune-cell perturbation, and cancer-mediated selection are represented and which
concepts cannot be expressed reliably through OmicsDI search syntax.

## [H3-3] Scientific questions

The planner must preserve these questions verbatim and assign stable identifiers:

| Question ID | Scientific question |
|---|---|
| `SQ01` | `pooled CRISPR knockout screens in cancer cells under immune selection` |
| `SQ02` | `pooled CRISPR knockout screens in immune cells under cancer-cell-mediated selection` |

The scientific questions are not submitted queries and are not eligibility rules.

## [H3-4] Required implementation behavior

Implement a v03 planning component that can:

1. represent each scientific question independently;
2. represent a versioned family of proposed literal queries for each resource;
3. record the purpose of each query and the scientific concepts it attempts to
   retrieve;
4. record known gaps between the scientific question and the resource syntax;
5. record proposed filters, sorting, pagination, request limits, timeouts, retries,
   rate limits, stop conditions, and resumability rules;
6. record the ORCS routing rule and its use of the complete cached index;
7. record that OmicsDI and ORCS observations remain separate;
8. record forbidden discovery inputs, including the known-publication TSV and
   local ICRAFT materials;
9. generate deterministic JSON from the same configuration, excluding an optional
   generation timestamp from semantic comparison;
10. validate the plan before writing it; and
11. refuse any `run`, `retrieve`, or equivalent live action in this implementation
    slice.

The plan should be data-driven. Query definitions must not be scattered through
network scheduling code.

## [H3-5] Query research requirement

Before fixing literal OmicsDI queries, review the current official OmicsDI API
documentation and compare it with the behavior already observed in
`docs/omicsdi/search-information.md` and `docs/field guide/omicsdi/`.

Document, without assuming unsupported behavior:

- boolean operator behavior;
- quotation behavior;
- tokenization or stemming only when documented or directly observed;
- supported fielded filters;
- repository and omics-type filters;
- sorting options and the consequence of omitting a sort;
- maximum page size;
- pagination behavior;
- record identity fields; and
- any difference between documentation and observed responses.

Search-interface research may access documentation. It must not submit the v03
scientific searches or retrieve candidate records under this handoff.

The proposed query family remains subject to project-owner review. Do not describe
it as validated, exhaustive, or high-recall merely because the API accepts it.

## [H3-6] Query-plan structure

The generated plan must include at least:

```text
schema_version
plan_version
status
created_at or generated_at
scientific_questions[]
resources[]
  resource_name
  resource_role
  interface
  routing_rule
  query_strategy_id
  queries[]
    query_id
    scientific_question_ids[]
    intended_query
    submitted_query
    purpose
    concepts_represented[]
    known_semantic_gaps[]
    filters
    sort
  pagination
  limits
  retry_policy
  rate_limit_policy
  stop_conditions[]
  resume_policy
forbidden_discovery_inputs[]
preservation_rules[]
review_gates[]
source_documentation[]
```

Use explicit `null`, empty lists, or a documented not-applicable value where the
resource does not support a property. Do not invent a filter or default.

## [H3-7] Proposed interface

Provide an offline command through the existing package interface or a narrowly
scoped new module:

```powershell
$env:PYTHONPATH = "$PWD\src"
python -B -m deathmap_ai.discovery_v03 prepare
python -B -m deathmap_ai.discovery_v03 verify
```

`prepare` may create only the reviewed planning directory and plan artifacts.
`verify` must regenerate the semantic plan in memory and compare it with the saved
plan without network access.

The preferred planning output is:

```text
outputs/immune-crispr-coculture-v03/query_plan.json
```

If resource-specific planning files are useful, place them under the corresponding
v03 package directory without creating candidate, hit, detail, or raw-response
artifacts.

Do not add a live `run` action in this slice. If a shared command parser requires
the name to exist, it must fail clearly with an authorization message before any
network code is reachable.

## [H3-8] TSV and evaluation isolation

The implementation must not read
`data/brainstorming/week3_papers_metadata.tsv`. It may record the repository-relative
path as a forbidden discovery input or later evaluation reference, but it must not
read its contents, hash its identifiers into the query plan, or import a component
that uses it.

The same isolation applies to local ICRAFT titles, identifiers, accessions, and
metadata.

Tests must use synthetic strings that are not copied from either evaluation set.

## [H3-9] ORCS planning boundary

The v03 plan must state that:

- a case-insensitive CRISPR trigger includes ORCS;
- ORCS uses the complete existing cached index;
- no index refresh is authorized;
- no fixed candidate cap applies to the cached-index search;
- native screen metadata and publication siblings retain their existing evidence
  roles; and
- proposed v03 matching rules require review before execution.

Do not modify the v01 or v02 ORCS outputs.

## [H3-10] OmicsDI planning boundary

The v03 plan must define proposed limits without borrowing or resetting v01 or v02
attempt accounting. V03 will use a new versioned ledger if live retrieval is later
authorized.

The plan must preserve:

- bounded per-request timeouts;
- service rate limits;
- cumulative retry limits;
- reservation-before-request behavior for future detail requests;
- resumable progress;
- native repository and identifier pairs;
- raw response preservation; and
- explicit uncertain and conflicting states.

The exact v03 candidate and detail limits are review decisions. The planner may
represent them as `proposed` values, but implementation must not present them as
authorized retrieval allowances.

## [H3-11] Required tests

Add small, inspectable offline tests covering:

1. preservation of the two scientific questions verbatim;
2. stable question and query identifiers;
3. each query referencing at least one scientific question;
4. unique query identifiers within a resource;
5. explicit scientific purpose and semantic gaps for every submitted query;
6. ORCS routing for case-insensitive `CRISPR`;
7. no ORCS routing when the trigger is absent;
8. explicit TSV and ICRAFT exclusions;
9. rejection of unversioned or incomplete plan structures;
10. deterministic semantic regeneration;
11. offline `prepare` and `verify` behavior;
12. refusal of live retrieval actions;
13. no modification of v01 or v02 outputs; and
14. no import or read dependency on the TSV or ICRAFT files.

Tests must not require credentials or network access.

## [H3-12] Preservation verification

Before implementation, record hashes for the existing v01 and v02 manifests,
resume states, entity tables, and reference workbooks already covered by the
preservation baseline. After implementation and tests, verify those files remain
unchanged.

New files belong only to source, tests, documentation, and the v03 planning output.
Do not regenerate existing discovery outputs as a side effect of testing.

## [H3-13] Non-goals

This handoff does not authorize:

- live ORCS or OmicsDI discovery;
- candidate retrieval;
- OmicsDI detail requests;
- publication-seeded lookup;
- reading or comparing the known-publication TSV;
- repository enrichment;
- GEO, SRA, ENA, or BioProject requests;
- dataset classification;
- scientific eligibility decisions;
- screen-group creation;
- screen–dataset links;
- Excel generation; or
- experimental-data download.

Do not add placeholder implementations for these stages.

## [H3-14] Deliverables

1. A small v03 planning/configuration module.
2. An offline `prepare` command.
3. An offline `verify` command.
4. A proposed `query_plan.json` for project-owner review.
5. Unit tests for `[H3-11]`.
6. Documentation of the proposed literal query family and known semantic gaps.
7. A preservation report confirming historical outputs were unchanged.

## [H3-15] Acceptance criteria

The slice is complete when:

- all required offline tests pass;
- the plan validates and regenerates deterministically;
- the two scientific questions remain verbatim;
- every proposed submitted query has a purpose and recorded semantic limitations;
- the TSV and ICRAFT materials did not influence the plan;
- no network request is possible through the v03 interface;
- historical outputs remain unchanged;
- the proposed plan is easy for a scientific reviewer to read; and
- the project owner receives the plan for review before any retrieval work begins.

## [H3-16] Required completion report

Report:

- files changed;
- tests run and results;
- proposed query family;
- documentation sources consulted;
- assumptions made;
- unresolved query-semantics questions;
- proposed but unauthorized retrieval limits;
- preservation verification results;
- open project-owner decisions; and
- the learning checkpoint introduced by implementation.

Do not commit, push, create a remote, or open a pull request unless the project
owner separately requests it.

## [H3-17] Learning checkpoint

The first executable v03 artifact is a query plan rather than a retrieval result.
This makes the information loss between a scientific question and a resource's
literal search syntax visible before that loss shapes the candidate pool.
