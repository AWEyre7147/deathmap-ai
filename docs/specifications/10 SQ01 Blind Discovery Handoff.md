# 10 SQ01 Blind Discovery Handoff

## [S1-1] Status and authorization

The project owner authorized implementation and, after successful offline
verification, execution of this bounded live-discovery slice on 2026-09-28.

This handoff supersedes the v02 handoff only for the new v03 SQ01 work. V01 and
v02 remain immutable historical runs with their original limits, receipts,
outputs, and documentation.

The authorized question is:

> `pooled CRISPR knockout screens in cancer cells under immune selection`

SQ02 is not part of this run. The known-publication TSV is withheld until the
blind SQ01 outputs are frozen. Repository enrichment, OmicsDI detail requests,
scientific adjudication, entity projection, and Excel generation remain
unauthorized.

## [S1-2] Governing requirements

Implementation and execution must follow:

- `[M1-4]` for the standard discovery-record unit;
- `[M1-6]` for evidence and provenance;
- `[M1-11]` for resource-specific JSON outputs;
- `[M1-13]` for reproducibility and verification;
- `[M1-14]` for historical preservation;
- `[WS3-3]` for the scientific questions;
- `[WS3-4]` for TSV isolation;
- `[WS3-5]` for the resource roles;
- `[WS3-9]` for stage order and bounded network behavior;
- `[H3-8]` for evaluation-file isolation;
- `[H3-9]` for ORCS planning boundaries; and
- `[H3-10]` for proposed OmicsDI ledger behavior as revised below.

Where this handoff supplies a more specific accepted SQ01 decision, it controls
the v03 SQ01 run without changing the historical meaning of v01 or v02.

## [S1-3] Scientific and retrieval boundary

The purpose of this slice is to answer:

> What can the complete cached BioGRID ORCS index and OmicsDI discover and report
> for SQ01 using only their native index/search information?

Search matches are unreviewed discovery observations. They do not establish that
a publication, screen, or dataset qualifies scientifically.

Keeping enrichment outside this slice is useful because it exposes what ORCS and
OmicsDI contribute independently. For example, an OmicsDI GEO accession remains
an OmicsDI discovery result even if a later GEO pass supplies decisive sample or
file metadata.

## [S1-4] Query-variant design

Each OmicsDI query is an independent retrieval test with its own identifier,
pagination state, query hits, raw pages, counts, and contribution summary. Queries
must not be combined into one expression, treated as sequential scientific gates,
or collapsed after deduplication.

The broad proposed query `CRISPR AND screen AND cancer AND immune` is abandoned and
must not be submitted in this run.

The accepted query family begins with the strict and relaxed SQ01 searches and
adds spelling or biological variants as independently measurable tests.

| ID | Variant | Literal OmicsDI query | Comparison purpose |
|---|---|---|---|
| `OM3-SQ01-Q01` | strict reference | `pooled AND CRISPR AND knockout AND screens AND "cancer cells" AND immune AND selection` | Closest literal representation of SQ01. |
| `OM3-SQ01-Q02` | relaxed reference | `CRISPR AND knockout AND "cancer cells" AND immune` | Tests records that omit pooled, screen, or selection wording. |
| `OM3-SQ01-Q03` | singular screen | `pooled AND CRISPR AND knockout AND screen AND "cancer cells" AND immune AND selection` | Changes only `screens` to `screen` relative to the strict reference. |
| `OM3-SQ01-Q04` | singular cancer cell | `pooled AND CRISPR AND knockout AND screens AND "cancer cell" AND immune AND selection` | Changes only `cancer cells` to `cancer cell`. |
| `OM3-SQ01-Q05` | tumor-cell wording | `pooled AND CRISPR AND knockout AND screens AND "tumor cell" AND immune AND selection` | Tests a common biological alternative to cancer-cell wording. |
| `OM3-SQ01-Q06` | coculture | `pooled AND CRISPR AND knockout AND "cancer cells" AND coculture` | Tests unhyphenated interaction terminology without requiring selection. |
| `OM3-SQ01-Q07` | co-culture | `pooled AND CRISPR AND knockout AND "cancer cells" AND co-culture` | Measures the hyphenated spelling independently. |
| `OM3-SQ01-Q08` | co culture | `pooled AND CRISPR AND knockout AND "cancer cells" AND "co culture"` | Measures the spaced spelling independently; phrase semantics remain unresolved. |
| `OM3-SQ01-Q09` | immune killing | `pooled AND CRISPR AND knockout AND "cancer cells" AND "immune killing"` | Tests an outcome-oriented description of immune selection. |
| `OM3-SQ01-Q10` | immune pressure | `pooled AND CRISPR AND knockout AND "cancer cells" AND "immune pressure"` | Tests an alternative selection-pressure phrase. |
| `OM3-SQ01-Q11` | immune selection phrase | `pooled AND CRISPR AND knockout AND "cancer cells" AND "immune selection"` | Tests the explicit SQ01 selection phrase without requiring screen wording. |

Quotation is preserved as submitted syntax, not treated as proof that OmicsDI
performs exact phrase matching. Hyphen handling, stemming, tokenization, and role
assignment remain unresolved and must be recorded as semantic gaps.

## [S1-5] OmicsDI scheduling and pagination

Run query variants independently in stable query-ID order. Exhaust one query's
pagination before advancing to the next so each variant can be run, resumed, and
reviewed separately. Record request dates and reported totals because a changing
live index may affect comparisons across query times.

For every approved query:

1. start at offset zero;
2. request pages of 50 records;
3. advance by the number of rows actually returned;
4. retain complete raw response bytes;
5. preserve duplicate observations;
6. buffer and admit every valid native repository–identifier pair;
7. continue until the returned page is empty or the offset reaches the service's
   reported total;
8. preserve count changes and pagination anomalies; and
9. stop or block the affected query rather than treating an uncertain request as
   exhaustion.

Pagination retrieves successive portions of one query. It does not create new
query variants or scientific subgroups.

## [S1-6] OmicsDI limits and safety controls

The project owner does not authorize a unique-candidate cap, search-page cap, or
total-runtime cap for the SQ01 OmicsDI search. Every approved query should be
exhausted unless an explicit error condition prevents completion.

The accepted request controls are:

- 20-second timeout per request;
- one request in flight at a time;
- at least one second between request starts;
- at most two cumulative attempts for one query/offset;
- two seconds before the one permitted search-page retry;
- no automatic repetition of an uncertain request;
- reservation and durable checkpoint before each request;
- stop an invocation after three consecutive failed network operations;
- bounded local checkpoint-replacement retries; and
- resumable progress without resetting cumulative attempts.

These controls bound failure behavior, not candidate retrieval. A successfully
advancing search may run as long as necessary to exhaust its pages.

OmicsDI detail requests are disabled. No detail ledger capacity is authorized in
this slice.

## [S1-7] ORCS execution

Search the complete existing cached ORCS index once for SQ01. There is:

- no candidate cap;
- no request cap because the pass is local;
- no detail-attempt cap;
- no runtime cap;
- no index refresh; and
- no experimental-data retrieval.

Successful completion means every cached native screen was examined once under
the accepted v03 rules. Stop with an explicit error if the cache is missing,
corrupt, cannot be parsed, or has an unrecognized required schema.

ORCS matching rules must cover the accepted SQ01 terms and variants without
turning a match into scientific qualification. Search the relevant native fields
deliberately rather than concatenating every value without identity.

## [S1-8] ORCS match-evidence output

For every direct ORCS match, preserve:

- query/rule identifier;
- native ORCS screen identifier;
- matched term;
- exact native field name;
- exact native field value;
- normalized comparison form, when used;
- match operation, such as word or phrase comparison;
- direct-match status;
- scientific-question identifier; and
- source-record reference.

Publication siblings remain contextual records with explicit parent-match
references. They are not direct hits or qualifying screens.

Match evidence is a primary JSON output. It is not intended to become a column-by-
column copy in the final workbook. A future `Sources & Evidence` row may reference
the versioned JSON file, run metadata, evidence identifier, and precise record or
field locator without reproducing the JSON contents.

Many evidence identifiers may point into one versioned JSON artifact. Do not make
a separate JSON file for every evidence identifier.

## [S1-9] Resource-specific outputs

Write new v03 artifacts under:

```text
outputs/omicsdi/immune-crispr-coculture-v03/
outputs/orcs/immune-crispr-coculture-v03/
outputs/immune-crispr-coculture-v03/
```

OmicsDI must produce at least:

- `search_manifest.json`;
- `resume_state.json`;
- `source_records.json`;
- `candidates.json`;
- `query_hits.json`;
- `candidate_summary.json`;
- `issues.json`; and
- complete raw search pages.

ORCS must produce at least:

- `search_manifest.json`;
- `source_records.json`;
- `candidates.json`;
- `query_hits.json` with field-level match evidence;
- `candidate_summary.json`; and
- `issues.json`.

The shared v03 directory may retain the frozen accepted query plan, preservation
baseline, run summary, and cross-resource counts. Do not generate the seven entity
tables during this slice.

## [S1-10] Independent execution and Codex-resource boundary

The live pipeline must run without continuous Codex involvement. Provide ordinary
command-line actions that:

- emit concise checkpoint summaries rather than individual records;
- persist progress before and after network operations;
- resume safely after interruption;
- avoid sending native records through a language model;
- produce a compact completion summary for later review; and
- return meaningful exit status on completion, partial completion, or failure.

Running the Python package and OmicsDI requests must not require a Codex session.
Codex may later inspect compact summaries or selected records, but it is not part
of the retrieval loop.

## [S1-11] Blind-evaluation isolation

Before the SQ01 outputs are frozen, do not read or use:

- `data/brainstorming/week3_papers_metadata.tsv`;
- local ICRAFT files;
- identifiers, titles, or accessions copied from either evaluation source; or
- previous manual knowledge of expected publications as a query expansion,
  allowlist, ranking feature, or retrieval dependency.

Tests use synthetic identifiers and metadata. The later TSV comparison requires a
separate authorization after the blind outputs are frozen.

## [S1-12] Error and stop behavior

Successful stop conditions:

- ORCS examined the complete cached index once; and
- every OmicsDI SQ01 query reached documented pagination exhaustion.

Error or review stop conditions include:

- missing, corrupt, or unrecognized ORCS cache;
- an OmicsDI request reserved without a durable outcome;
- two failed attempts for one query/offset;
- three consecutive failed network operations in an invocation;
- persistent throttling;
- unrecognized search-response structure;
- invalid native identity;
- inability to preserve raw bytes or checkpoint state safely; or
- semantic plan mismatch between the frozen plan and executor.

A stopped query remains incomplete or blocked. Do not label it exhausted.

## [S1-13] Implementation requirements

1. Revise the v03 plan to SQ01-only and remove SQ02 queries from the executable
   plan while retaining SQ02 in the broader work-session specification.
2. Replace the proposed OmicsDI family with the accepted `[S1-4]` queries.
3. Implement a new v03 ledger; do not reuse v01/v02 offsets, buffers, candidates,
   raw pages, or attempt allowances.
4. Implement paginated OmicsDI search retrieval without detail requests.
5. Implement the complete local ORCS pass with field-level match evidence.
6. Generate the resource-specific outputs in `[S1-9]`.
7. Provide independent command-line prepare, run, resume, export, and verify
   behavior appropriate to each resource.
8. Preserve the accepted semantic plan digest in run state and reject mismatches.
9. Prevent simultaneous writers to the same v03 ledger.
10. Freeze completed outputs before any evaluation comparison.
11. Stop for project-owner review without enrichment or entity projection.

## [S1-14] Verification requirements

Add small, inspectable tests for:

- exact SQ01 question preservation;
- absence of SQ02 from the executable run plan;
- rejection of the abandoned broad query;
- stable and unique query IDs;
- independent per-query pagination;
- continuation without candidate or page caps;
- empty-page and reported-total exhaustion;
- changing reported totals;
- duplicate observations across queries;
- repository–identifier native identity;
- invalid identity handling;
- durable reservation before requests;
- cumulative retry accounting;
- uncertain-request blocking;
- three-failure invocation stop;
- checkpoint and resume behavior;
- live-plan digest validation;
- absence of detail requests;
- complete ORCS index traversal;
- ORCS field-level match evidence;
- publication-sibling labeling;
- TSV and ICRAFT isolation;
- refusal to create entity tables or Excel outputs; and
- preservation of every historical file covered by the baseline.

Network tests use fake transports. A separate preflight must verify the real plan,
paths, and preservation baseline before live execution.

## [S1-15] Preflight and execution gates

Live execution may begin only after:

1. all repository tests pass;
2. offline regeneration matches the frozen SQ01 plan;
3. the abandoned broad query is absent;
4. no cap fields can truncate successful pagination;
5. OmicsDI detail requests are unreachable;
6. output directories are new or contain only matching resumable v03 state;
7. the historical preservation baseline passes;
8. the command reports the exact query family and request policies before asking
   for network access; and
9. the executor can run without Codex supervision.

After execution, rerun offline verification and preservation checks. Report
complete, incomplete, blocked, and failed queries separately.

## [S1-16] Explicitly deferred work

- SQ02;
- the abandoned broad OmicsDI query;
- OmicsDI detail requests;
- repository enrichment;
- GEO, SRA, ENA, or BioProject retrieval;
- dataset-modality or scientific-role classification;
- publication-seeded lookup;
- TSV or ICRAFT comparison;
- cross-resource entity projection;
- screen-group creation;
- screen–dataset links;
- scientific adjudication;
- Excel generation; and
- experimental-data download.

## [S1-17] Required completion report

Report:

- implementation files changed;
- exact submitted query family;
- ORCS rules and searched fields;
- test commands and results;
- preservation results;
- request-policy values;
- per-query page, observation, duplicate, and unique-record counts;
- native repository counts;
- ORCS direct-match and sibling counts;
- all blocked, incomplete, and failed work;
- proof that no detail or enrichment request occurred;
- output paths and semantic plan digest;
- assumptions and open questions; and
- the learning checkpoint introduced.

Do not compare with the known-publication TSV in this report.

## [S1-18] Learning checkpoint

Query variation and pagination answer different questions. Variants measure how
wording changes discovery; pagination completes one variant's result set. Keeping
both explicit allows DeathMap-AI to improve search wording without confusing a
larger page count with broader scientific coverage.
