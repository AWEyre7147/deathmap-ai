# Module 1 specification: evidence discovery and dataset attribution

## [M1-1] Module purpose

Module 1 discovers candidate publications, screens, and repository records;
retrieves permitted descriptive metadata; preserves native evidence; and projects
supported entities for scientific review.

The module does not decide biological importance or make therapeutic conclusions.

## [M1-2] Inputs

An authorized discovery run receives:

- one or more scientific questions;
- a versioned resource-specific query strategy;
- defined resources and repository-enrichment adapters;
- per-request limits, retry rules, and stop conditions;
- a versioned output location; and
- optional evaluation references that remain isolated from production discovery.

Scientific questions and submitted queries are distinct. The system records both.

## [M1-3] Resource layers

### Discovery resources

Discovery resources identify candidate publications, screens, or repository
records. BioGRID ORCS and OmicsDI are the currently evaluated discovery resources.

### Repository-enrichment resources

Repository-specific resources retrieve additional metadata for an accession
already discovered or separately authorized as an enrichment seed. Enrichment may
clarify repository hierarchy, data modality, samples, runs, files, availability,
and experimental descriptions.

Discovery and enrichment evidence remain separately attributed. An enrichment
result must not be misreported as a direct discovery hit.

## [M1-4] Standard discovery record

One discovery record represents one candidate returned by one resource during one
versioned run. Repeated observations from different queries or resources remain
preserved even when they later point to the same entity.

The minimum record follows `docs/standard-discovery-record.md` and includes run,
resource, query, rank, native identity, original title and identifiers, raw-response
reference, retrieval time, and initial review status.

## [M1-5] Entity boundaries

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

## [M1-6] Evidence rules

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

## [M1-7] Dataset classification

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

The controlled values and plain-language meanings proposed for the current
iteration are defined in `docs/proposed-discovery-enrichment-v03.md`. They are not
production vocabulary until accepted through the current work-session review.

## [M1-8] Anchor and related datasets

An anchor dataset contains data directly representing a qualifying screen, subject
to scientific review. Related datasets may contain companion characterization,
targeted follow-up, validation, controls, or contextual data connected to the
anchor screen, screen group, or publication.

Related datasets may be retained without being presented as the evidence that made
the publication qualify. Candidate records with unresolved roles remain visible
for review.

## [M1-9] Screen–dataset relationships

The module creates an exact screen–dataset relationship only when evidence supports
the specific screen, dataset, and relationship type. Shared publication, cell line,
treatment, title, or repository project alone is insufficient.

When exact attribution is not supported, retain the strongest justified level:

- screen group;
- publication only;
- multiple possible screens; or
- unresolved.

## [M1-10] Metadata-only boundary

Module 1 may retrieve publication metadata, screen metadata, repository metadata,
accessions, sample descriptions, run descriptions, file listings, availability
statements, controlled vocabularies, and other descriptive records needed for
discovery and attribution.

It must not download gene-level results, guide-count tables, FASTQ files, processed
expression matrices, or other experimental datasets during the metadata-only
stage.

## [M1-11] Outputs

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
- Sources & Evidence; and
- Discovery Resources.

JSON is the canonical machine-readable output. Excel is a derived review format,
not a required retrieval dependency.

## [M1-12] Review outputs

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

## [M1-13] Verification

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

## [M1-14] Preservation

New iterations use new versioned output directories. Do not reset, overwrite, or
reinterpret historical runs in place. Preserve prior raw responses, manifests,
attempt accounting, hashes, review values, and documented limitations.

## [M1-15] Deferred capabilities

Module 1 does not implement:

- the future reasoning layer;
- patient-context integration;
- therapeutic prioritization;
- automated scientific adjudication;
- generalized biomedical search;
- graph visualization; or
- experimental-data analysis.
