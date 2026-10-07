# ORCS first filter run plan

## [ORP1] Purpose and status

Prepared 2026-10-03 for owner review. This plan organizes implementation and a
subsequent local run of [the filter profile](profile.json).
No filter runner has been implemented or executed in this planning step.

Subsequent owner authorization is recorded in
[11 ORCS Filter Run and Excel Handoff](../../../docs/specifications/18%20Repository%20Native%20Discovery%20Release%20Preparation.md).
It adds publication-sibling context and Excel population using the selected blank
reference workbook, superseding this plan's JSON-only output boundary for the new run.

The objective is a reviewable subset of native ORCS screens satisfying the seven
specified criteria, using saved Cellosaurus annotations for the cancer category.
It does not establish qualifying publications or datasets. The profile contains
an owner-specified `SCREEN_FORMAT = Pool` condition and no immune-exposure
condition. Immune exposure must not be silently added from the historical SQ01 question.

The written SQ01 handoff governs a native-only historical discovery slice.
The owner's subsequent reference-annotation and filtering instructions establish
a separate reference-assisted stage. This plan does not revise, rerun, or relabel
that historical slice or its outputs.

## [ORP2] Existing code and proposed runner

| Existing component | Current behavior | Reuse decision |
| --- | --- | --- |
| `src/deathmap_ai/sq01_orcs.py` | Complete-cache validation; fixed SQ01 phrase rules; publication siblings; historical state/output paths | Reuse validation and evidence-handling ideas, leaving historical rules and orchestration unchanged |
| `src/deathmap_ai/orcs.py` and `scripts/run_orcs_probe.py` | Metadata retrieval and fixed co-culture matching | No retrieval or fixed-rule matching needed for this run |
| `scripts/annotate_orcs_vocabularies.py` | Builds reference annotations | Consume its saved JSON without rerunning annotation |
| `searches/orcs/cancer-cell-crispr-knockout-v01.json` | Declarative filter settings | Authoritative criteria for the new runner |

Proposed additions: `src/deathmap_ai/orcs_filters.py`, a small launcher
`scripts/run_orcs_filters.py`, and fixture tests. Standard Python dictionaries
and lists are adequate for 2,217 records; SQL is unnecessary. The runner should
implement only this profile's supported operations, rather than a general query
language. Unsupported settings must cause a clear error rather than be ignored.

## [ORP3] Preflight and input preservation

1. Load the profile, the complete cached ORCS metadata and its cache summary,
   and the saved reference-annotation JSON. Resolve profile paths relative to
   the repository root.
2. Validate JSON shapes, supported operations, required fields and field types,
   unique `SCREEN_ID` values, cache completeness, and unique annotation `value`
   keys. Reject corrupt or structurally incomplete inputs. Optional source
   description fields need not be present.
3. Check that requested values occur in the relevant source vocabularies and
   that annotations identify the same cache hash. Compute hashes of all inputs.
4. Save a run manifest with the profile snapshot, annotation snapshot, input
   paths/hashes, original metadata/reference dates, execution time and code
   version/hash. Use a new output directory and refuse to overwrite an existing
   run. An unchanged rerun creates a distinct invocation, not a new profile version.

This stage uses existing local inputs only: no ORCS refresh, external lookup,
OmicsDI run, experimental-data download, or known-publication evaluation input.
That boundary makes the contribution of the accepted profile inspectable. For
example, an unresolved primary-cell label remains unresolved rather than acquiring
an undocumented classification through a new publication lookup.

## [ORP4] Filtering and review handling

Evaluate every cached screen exactly once. Join its exact `CELL_LINE` string to
the annotation record's `value`. Preserve native screen fields separately from
the joined reference facts.

All seven filter fields must pass; values within each field are alternatives.
Comparisons are exact and case-sensitive. `EXPERIMENTAL_SETUP` is unrestricted.
Do not add synonyms, Cas9 variants, the separate phenotype `viability`, or any
other scientific criterion.

Each screen receives exactly one outcome:

- **Matched:** all seven criteria pass. Preserve annotation review issues and
  flag the row for review without imposing an additional exclusion rule.
- **Unresolved category:** the six native-field criteria pass, but the joined
  category is missing or no annotation is available. Retain separately for
  review; this is not a positive cancer match or a negative cancer classification.
- **Excluded:** at least one native criterion fails, or the known reference
  category fails the cancer criterion. Preserve the failed criteria in the audit.

Each outcome needs `SCREEN_ID`, source publication type/identifier, original
metadata location, individual criterion results and values, and reference
accession, match method, evidence locator and review issues where available.
An annotation's known category is used as configured, while species/identity
conflicts remain visible. Do not overwrite ORCS facts with reference facts.

## [ORP5] Outputs and run summary

Write to a new directory under
`outputs/orcs/cancer-cell-crispr-knockout-v01/<UTC-run-id>/`:

| Artifact | Purpose |
| --- | --- |
| `run_manifest.json` | Inputs, snapshots, hashes, version, dates, criteria and completion/error status |
| `profile.json` and `reference_annotations.json` | Exact configuration and annotation inputs used |
| `matched_screens.json` | One row per matching screen with native metadata and reference evidence |
| `unresolved_screens.json` | Otherwise matching screens whose cancer category cannot be evaluated |
| `screen_audit.json` | One row per examined screen with all criterion results and final outcome |
| `summary.json` | Total examined, each outcome count, annotation issues, per-field pass/fail/missing counts and cumulative filter counts |

Cumulative counts use the profile's field order and make reductions visible;
the final AND result must be independent of that order. Counts for independent
criteria are also needed so an early filter does not hide later metadata issues.
All outcome counts must reconcile with the complete cache count.

A summary may count distinct `(SOURCE_TYPE, SOURCE_ID)` pairs among matched
screens, but must not merge screen rows, infer qualifying publications, or bring
unmatched publication siblings into the matched subset. No Excel workbook or
seven-entity projection is part of this first run.

## [ORP6] Verification, execution and review

Before execution, add small inspectable fixtures for AND/OR semantics, exact
case-sensitive matching, each individual failed criterion, missing categories,
known nonmatching categories, review-issue preservation, and ambiguous/duplicate
annotation keys. Test corrupt inputs, cache/hash mismatches, outcome-count
reconciliation, existing-output protection and retention of native identifiers.
Include Cas9 variants, `viability`, and an unresolved primary population as
boundary examples. Check that no network path is invoked and original inputs
remain byte-identical.

After implementation and passing checks, execute the complete local pass and
verify output hashes and reconciliation. Then review matched and unresolved
screens before changing scientific criteria. Keep the profile version and run
outputs together; an intentional criterion change gets a new profile version.

Learning checkpoint: the filter profile states the scientific selection rule,
the runner applies it, and the run manifest records precisely what was used.
This separates evolving filter logic from preserved evidence and results.

## [ORP7] Organization update — 2026-10-04

The local filter and Excel run was subsequently completed. This note preserves the original planning context; see README.md for current execution and the existing results. Shared annotations and the blank template now live under data; populated workbooks stay in run directories.
