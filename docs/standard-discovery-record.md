> Current shared-search override (2026-09-08): see [shared-resource-search.md](C:/Users/aweyr/Documents/Archives/deathmap-ai-v01-archive/superseded-documentation/docs/shared-resource-search.md). Earlier five-minute limits, data/raw paths and Excel instructions below are historical. Active JSON outputs and cache/archive mappings are under outputs/<package>/.

# Standard Discovery Record

## [DR1] Purpose

The standard discovery record provides a common, inspectable output for tools
that expose different query mechanisms and metadata. It allows DeathMap-AI to
compare, combine, and review tool results without pretending their native outputs
are equivalent.

## [DR2] Unit of record

One record represents:

> One candidate returned by one resource during one versioned search run.

The record documents a retrieval observation. It does not establish that the
candidate is relevant, that it contains a qualifying screen, or that a reported
dataset belongs to that screen.

## [DR3] Provenance rule

Never overwrite or discard an original discovery record during deduplication.
Several discovery records may later point to one combined candidate. This is how
the project can determine which resources found the candidate and what each
resource contributed.

## [DR4] Minimal pilot fields

The first tool evaluations should populate these fields when available:

| Field | Meaning |
|---|---|
| `record_id` | Stable identifier for this retrieval observation |
| `run_id` | Identifier for the search execution |
| `resource_name` | Tool or database that returned the candidate |
| `resource_version` | Tool, API, database, or release version when available |
| `retrieved_at` | Retrieval date and time |
| `query_strategy_id` | Versioned description of how this resource was searched |
| `result_rank` | Native result position when the resource provides one |
| `native_record_id` | Identifier assigned by the source resource |
| `native_url` | Source landing page or result URL |
| `candidate_type` | Publication, screen, dataset, mixed record, or unknown |
| `title_original` | Title exactly as supplied by the source |
| `pmid_reported` | PMID supplied by the source, without treating it as verified |
| `doi_reported` | DOI supplied by the source, without treating it as verified |
| `accessions_reported` | Dataset accessions supplied by the source |
| `evidence_text_original` | Source text or metadata explaining the candidate result |
| `raw_response_ref` | Location or identifier for the preserved native response |
| `review_status` | Initially `unreviewed` |

Use explicit null values for information the source did not provide. Do not use
empty strings, `NA`, or guessed values to make incomplete records appear full.

## [DR5] Optional source-supplied hints

The adapter may record additional source claims without asserting that they are
correct:

- proposed co-culture status;
- proposed perturbed and interacting cell types;
- proposed CRISPR modality;
- source library name and type;
- source-reported or derived library size;
- proposed library scope, kept separate from source wording;
- nuclease or enzyme, such as Cas9 or Cas12a;
- phenotype wording;
- species and model;
- repository and dataset type;
- availability claims;
- authors, journal, and publication year.

These fields should use names or documentation that clearly identify them as
reported, extracted, or inferred rather than reviewed.

## [DR6] Review fields

Manual review may later add:

- eligibility decision;
- exclusion reason;
- verified publication identifiers;
- verified anchor type;
- verified screen and experiment relationships;
- verified dataset attribution;
- accessibility findings;
- evidence source;
- reviewer notes;
- confidence or unresolved status.

Review must append evidence and decisions without changing the preserved native
result.

## [DR7] Record lifecycle

```text
Native tool result
    -> discovery record
    -> combined candidate
    -> manual adjudication
    -> accepted, rejected, or unresolved evidence
```

Combining candidates and curating scientific entities are separate operations.

## [DR8] Pilot implementation boundary

The first adapter should implement only the minimal fields needed to inspect one
resource's output. Optional fields should be added in response to observed native
data, not anticipated for every possible tool.

The initial iterative run should stay within the three-to-five-minute runtime
budget defined in `pilot-scope.md`.

## [DR9] Open implementation choices

The following remain undecided until the first native tool output is inspected:

- serialized file format;
- exact identifier syntax;
- whether one native result can contain several candidate subrecords;
- storage location for preserved raw responses;
- deduplication keys and precedence;
- schema validation technology.

These choices must not be made merely to complete the document.
