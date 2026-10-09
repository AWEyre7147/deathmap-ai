# Module Specification

## Module Name

Module 1 — Evidence discovery and dataset attribution

## Status

Current iteration: v02 — ORCS Pilot Enrichment. Partially implemented. Cached ORCS discovery, saved Cellosaurus interpretation, publication identifier enrichment and portable Excel output are implemented. PubMed-led metadata enrichment of the ORCS publication index and saved searches is implemented under the owner's 2026-10-08 authorization. Native GEO, BioStudies–ArrayExpress and ENA enrichment and screen grouping remain pending approved contracts. OmicsDI discovery is retired.

## Objective

### [M1-1] Module purpose

Module 1 discovers candidate publications, screens, and repository records;
retrieves permitted descriptive metadata; preserves native evidence; and projects
supported entities for scientific review.

The module does not decide biological importance or make therapeutic conclusions.

## Why This Module Exists

Produce inspectable metadata and evidence that connects publications, screens and repository records without forcing uncertain scientific relationships into a single answer.

## Inputs

### [M1-2] Inputs

An authorized discovery run receives:

- one or more scientific questions;
- a versioned resource-specific query strategy;
- defined resources and repository-enrichment adapters;
- per-request limits, retry rules, and stop conditions;
- a versioned output location; and
- optional evaluation references that remain isolated from production discovery.

Scientific questions and submitted queries are distinct. The system records both.

## Outputs

### [M1-11] Outputs

Each resource receives versioned, native JSON outputs including:

- search manifest;
- source records;
- candidates;
- query hits;
- candidate summary;
- issues;
- attempt or resume state when applicable; and
- preserved raw responses or references to them.

The cross-resource projection produces:

- Publications;
- Screen Groups;
- Screens;
- Datasets;
- Screen-Dataset Links;
- Evidence.

The workbook also preserves the owner-approved reference and glossary sheets.

JSON is the canonical machine-readable output. Excel is a derived review format,
not a required retrieval dependency.

### [M1-12] Review outputs

Compact reviewer tables may summarize the canonical records, but they must not
replace raw evidence. Reviewer-entry fields remain distinct from source-reported,
pipeline-normalized, and pipeline-inferred fields.

When an Excel workbook is authorized:

- generate a new version rather than overwriting the reviewed model;
- populate it from projected entity JSON, not directly from raw responses;
- keep reviewer-entry columns together at the far right;
- retain review status in data fields as well as color;
- use the approved review colors; and
- preserve glossary definitions and provenance.

## In Scope

Cached ORCS filtering under the three existing profiles; exact publication-identifier resolution; evidence-preserving projections and review workbooks. The next planned work is metadata-only enrichment of the retained ORCS collection, then evidence-supported screen-group design. Implementation of future retrieval requires explicit owner authorization.

## Explicitly Out of Scope / Non-Goals

### [M1-15] Deferred capabilities

Module 1 does not implement:

- the future reasoning layer;
- patient-context integration;
- therapeutic prioritization;
- automated scientific adjudication;
- generalized biomedical search;
- graph visualization; or
- experimental-data analysis.

No experimental-file downloads, benchmark identifiers in production queries, automatic whole-ORCS grouping, or unauthorized publication. Independent native discovery is deferred from the immediate priority.

## Data Sources / Dependencies

### [M1-3] Resource layers

### Discovery resources

Discovery resources identify candidate publications, screens, or repository
records. BioGRID ORCS and repository-native interfaces are the current discovery
direction. OmicsDI is tertiary accession-led relationship research, subject to a
separately approved lookup contract. Any such lookup requires separately approved scope.

### Repository-enrichment resources

Repository-specific resources retrieve additional metadata for an accession
already discovered or separately authorized as an enrichment seed. Enrichment may
clarify repository hierarchy, data modality, samples, runs, files, availability,
and experimental descriptions.

Discovery and enrichment evidence remain separately attributed. An enrichment
result must not be misreported as a direct discovery hit.

Implemented sources: saved BioGRID ORCS metadata, saved Cellosaurus annotations, cached NCBI publication identifier responses, and the owner-authorized PubMed EFfetch/ELink/ESummary enrichment database. ORCS Excel export uses Python/openpyxl and the owner-approved template; PubMed workbooks preserve the approved template's XML envelopes and literal text dates. Next enrichment goals are GEO, BioStudies–ArrayExpress and ENA; native hierarchy and attribution contracts remain pending. PRIDE, MassIVE, jPOST and iProX remain later resource candidates.

## Workflow

1. Validate authorized profiles and saved source metadata.
2. Resolve publication identifiers when separately requested, preserving exact mappings and conflicts.
3. Audit cached screens, retaining direct candidates and publication companions distinctly.
4. Produce entity JSON and field-level evidence.
5. Export a fresh review workbook using the approved template.
6. Under an approved repository contract, retrieve descriptive records and assess dataset attribution.
7. Develop screen groups after sufficient enrichment evidence.

Steps 6–7 are planned, not authorized by this document update.

## Data Model / Interface

### [M1-4] Standard discovery record

One discovery record represents one candidate returned by one resource during one
versioned run. Repeated observations from different queries or resources remain
preserved even when they later point to the same entity.

The minimum record includes run,
resource, query, rank, native identity, original title and identifiers, raw-response
reference, retrieval time, and initial review status.

### [M1-5] Entity boundaries

Module 1 keeps the following entities distinct unless reviewed evidence justifies
a relationship:

- publication;
- screen group, which records the scientific objective and substantial design
  shared by related screens;
- screen, which records one independently interpretable perturbation-screen
  selection in a defined biological context;
- repository project;
- repository study or series;
- dataset;
- sample;
- sequencing or instrument run;
- file or supporting asset; and
- source-evidence assertion.

A repository's use of the word “dataset” does not determine the scientific entity
level. Publication association does not prove that a repository record contains a
qualifying screen, and it does not establish an exact screen–dataset link.

DeathMap-AI does not create a separate experiment entity. The screen group carries
the shared experimental design and context that might otherwise be assigned to an
experiment, while the screen preserves the distinct selection that must remain
independently interpretable. Repository-native records labeled “experiment” retain
that source hierarchy label without becoming a DeathMap-AI experiment entity.

### [M1-7] Dataset classification

Dataset records are classified along independent dimensions rather than one
combined type:

- discovery relationship;
- publication association;
- data modality;
- experimental role;
- repository hierarchy level;
- screen attribution;
- evidence strength;
- output inclusion role; and
- availability.

Controlled values require acceptance through a approved resource-specific retrieval contract. Archived proposals do not define current production vocabulary.

### [M1-8] Anchor and related datasets

An anchor dataset contains data directly representing a qualifying screen, subject
to scientific review. Related datasets may contain companion characterization,
targeted follow-up, validation, controls, or contextual data connected to the
anchor screen, screen group, or publication.

Related datasets may be retained without being presented as the evidence that made
the publication qualify. Candidate records with unresolved roles remain visible
for review.

### [M1-9] Screen–dataset relationships

The module creates an exact screen–dataset relationship only when evidence supports
the specific screen, dataset, and relationship type. Shared publication, cell line,
treatment, title, or repository project alone is insufficient.

When exact attribution is not supported, retain the strongest justified level:

- screen group;
- publication only;
- multiple possible screens; or
- unresolved.

## Requirements

### [M1-6] Evidence rules

Every populated scientific field or relationship must retain:

- its source resource;
- the native record identifier;
- a field path, page, section, figure, table, or other locator when available;
- whether the evidence is direct, inferred, conflicting, or unresolved;
- the transformation used to normalize it; and
- its review status.

Original reported text remains separate from normalized and curated values.
Conflicts remain visible. Missing evidence must not be replaced with a guessed
value.

## Constraints

### [M1-10] Metadata-only boundary

Module 1 may retrieve publication metadata, screen metadata, repository metadata,
accessions, sample descriptions, run descriptions, file listings, availability
statements, controlled vocabularies, and other descriptive records needed for
discovery and attribution.

It must not download gene-level results, guide-count tables, FASTQ files, processed
expression matrices, or other experimental datasets during the metadata-only
stage.

### [M1-14] Preservation

New iterations use new versioned output directories. Do not reset, overwrite, or
reinterpret historical runs in place. Preserve prior raw responses, manifests,
attempt accounting, hashes, review values, and documented limitations.

Preserve ORCS vocabulary and source provenance. Keep validation references isolated from production discovery. Preserve reviewer-edited workbooks; replace active runs only through owner-authorized archival and new generation. Retain one current output per condition. Do not commit or push without a new request.

## Assumptions

Scientific eligibility is not established by candidate retention. A repository-native “experiment” label does not create a new DeathMap-AI experiment entity. Exact identifiers constrain publication matching; preprint and published-article identities are not automatically equivalent.

## Edge Cases / Failure Modes

- Missing identifiers or no external mapping: preserve known values and leave unavailable fields blank.
- Conflicting identifier mappings: preserve source values and alternatives for review.
- Missing or corrupt source catalogs: fail explicitly rather than silently evaluating a partial catalog.
- Incomplete metadata or ambiguous dataset attribution: retain unresolved relationships.
- Workbook export failure: preserve canonical JSON and record the failure.
- Existing authored workbook or run directory: refuse overwrite.
- Structurally valid XLSX: native Excel opening still requires a separate check.

## Acceptance Criteria / Definition of Complete

- Authorized source records and identifiers survive transformations with provenance.
- Direct, inferred, conflicting and unresolved evidence remain distinguishable.
- Each profile produces reproducible canonical metadata and a new review workbook.
- Reviewer fields and source claims remain distinct.
- Unsupported entities remain empty or unresolved.
- Coverage claims use a defined, appropriately adjudicated comparison set.
- Future repository adapters require accepted retrieval and attribution criteria; the complete enrichment module is not yet declared finished.

## Verification Plan

### [M1-13] Verification

Every implemented behavior requires tests appropriate to its risk. Use small,
inspectable fixtures. A reproducible run records:

- tool or interface version when available;
- scientific question and literal queries;
- query strategy version;
- retrieval date;
- pagination and filtering behavior;
- timeouts, rate limits, retries, and stop conditions;
- raw identifiers and response references;
- transformation version; and
- known failures or uncertainties.

Do not claim coverage from an unadjudicated candidate pool.

Use focused existing checks appropriate to the authorized change. Documentation-only updates require scoped content and link checks, with zero pipeline rebuild/export passes. Further expensive validation requires an accepted scope or checkpoint.

## Open Questions

- Which repositories best enrich the ORCS collection?
- What record hierarchy depth and metadata are needed?
- Which evidence supports publication-only, screen-group or exact screen-dataset attribution?
- What rules define screen-group membership after enrichment?
- Is whole-ORCS grouping justified? This remains exploratory.
- When should specification versions or additional modules be created? Lifecycle rules remain pending.

## Future Integration Points

The long-term project includes normalized and analyzed CRISPR datasets with thorough annotations, particularly with the ligand–receptor database previously known as XDeathDB. Those capabilities require future approved scope; module 1 currently prepares the metadata, identifiers and justified relationships they would need.

Repository-native metadata adapters may consume publication identifiers and accession seeds. Independent discovery may later feed the same evidence-preserving interfaces. Reasoning and patient-context functionality remain deferred.

## Change Log

- 2026-10-08 — Restructured existing requirements into the adopted template, preserved M1 point identifiers, clarified implemented versus planned behavior, and removed dependence on work-session specifications. No pipeline behavior or scientific filters changed.
