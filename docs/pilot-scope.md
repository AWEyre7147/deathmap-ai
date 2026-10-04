> Navigation status (2026-10-04): historical scope record. The [current work-session specification](specifications/work-session-v03-discovery-enrichment.md), especially WS3-19, governs the completed CRISPR pilot. Earlier limits below do not apply to that run.

> Current scope (2026-09-19): [OD1–OD10 v02 search](C:/Users/aweyr/Documents/Archives/deathmap-ai-v01-archive/superseded-documentation/docs/omicsdi/search-information.md) supersedes the historical limits below. Version 01 remains unchanged; v02 has separate 5,000-native-record/50-new-detail-attempt accounting.

> Current shared-search override (2026-09-08): see [shared-resource-search.md](C:/Users/aweyr/Documents/Archives/deathmap-ai-v01-archive/superseded-documentation/docs/shared-resource-search.md). Earlier five-minute limits, data/raw paths and Excel instructions below are historical. Active JSON outputs and cache/archive mappings are under outputs/<package>/.

# Co-culture Discovery Pilot Scope

This implementation-facing note records accepted pilot decisions. The curated
specifications remain authoritative and should incorporate these decisions when
their next revision is made.

## [PS1] Discovery objective

Discover as many cancer-immune CRISPR co-culture screen publications as possible
and connect them to their experiments, datasets, and accessions when evidence
supports those relationships.

The search may be narrowed later if breadth makes iteration impractical.

## [PS2] Iteration runtime budget

During development, an ordinary search run should take no longer than three to
five minutes of wall-clock time. This is an iteration budget, not a claim about
the eventual exhaustive search.

When the budget would be exceeded, prefer a bounded query, cached raw response,
pagination limit, date slice, or staged resource run. Record which limit was used
so a fast pilot result is not mistaken for complete retrieval.

## [PS3] Primary qualifying screen

A primary anchor is a pooled CRISPR knockout screen performed in a cancer-immune
co-culture context. Genome-wide, near-genome-wide, partial, custom, and targeted
libraries are eligible. Library breadth is a descriptive scientific field, not
an inclusion gate. A targeted screen must never be relabeled as genome-wide.

Either the cancer or immune cell population may be perturbed. Human and mouse
studies are eligible, and indirect co-culture configurations remain eligible
during the pilot.

Record the source library name, library type, reported or derived target count,
and an explicitly reviewed library-scope category when evidence permits. Keep
the source wording separate from the reviewed category. Initial reviewed
categories are `genome-wide`, `near-genome-wide`, `partial/custom`, `targeted`,
and `unclear`.

## [PS4] Anchor terminology

- A screen anchor is a direct qualifying co-culture screen. During discovery,
  an exact co-culture metadata match is only a candidate screen anchor until it
  is reviewed.
- A publication anchor is a publication containing at least one screen anchor.
- A publication sibling is another ORCS screen assigned to that publication. It
  may be a control, comparator, or another experiment and is not automatically a
  co-culture screen.

The screen anchor establishes the qualifying experimental evidence. The
publication anchor permits retention of sibling screens. Both relationships
remain explicit for later curation and reasoning.

## [PS5] Secondary evidence

CRISPRi, CRISPRa, arrayed screens, Perturb-seq, other single-cell readouts,
conditioned-media experiments, cytokine experiments, organoid or ex vivo
experiments, in vivo follow-up, and validation assays may be retained only when
linked to a primary qualifying anchor.

Focused, partial, custom, or targeted pooled knockout libraries are primary
evidence when the screen itself meets the co-culture criterion. They do not need
a parent genome-wide screen.

## [PS6] Phenotype representation

Retain the source's original phenotype wording. Store a separate normalized
phenotype category so categorization never overwrites the source description.

The appropriate terminology is controlled-vocabulary normalization or phenotype
harmonization. Initial categories may include:

- cancer-cell survival or death;
- immune-mediated killing;
- immune activation;
- immune exhaustion or dysfunction;
- resistance or sensitization;
- cell recognition or interaction;
- cytokine production;
- competitive fitness;
- other or unclear.

## [PS7] Accessibility representation

Record discovery separately from usability. Preserve at least:

- accession reported;
- repository;
- landing page reachable;
- metadata publicly accessible;
- processed data accessible;
- raw data accessible;
- controlled access required;
- download tested;
- access status;
- access checked date;
- restriction or failure reason;
- supporting evidence source.

## [PS8] ICRAFT validation boundary

The local ICRAFT publication list is an external validation reference. Its
publication titles, identifiers, accessions, and curated metadata must not be used
to construct or expand discovery queries.

The primary ICRAFT comparison is publication recall because inclusion in the
relevant list already indicates a validated co-culture screen. Dataset and
accession recovery may be reported separately.

The historical comparison is approximately 30 percent publication recall for the
ICRAFT authors' automated retrieval. This value is project-owner context and must
be verified against its original definition before formal reporting.

Novel candidates absent from ICRAFT require manual adjudication; absence from
ICRAFT does not establish irrelevance.

The first released version of module 1 must not contain ICRAFT data or code that
tests ICRAFT publications or accessions. Validation should occur in a separate
evaluation step outside the production discovery path.

## [PS9] Minimum future-facing evidence envelope

The pilot should preserve source records and retrieval provenance; distinct
publication, experiment, screen, dataset, accession, and sample/group entities;
explicit evidence links; original supporting text; normalized metadata;
accessibility; direct versus inferred status; confidence; and review status.

The final reasoning-layer schema is intentionally deferred. The pilot must avoid
discarding provenance or relationships that would be difficult to reconstruct.

## [PS10] Tool-evaluation architecture

Evaluate existing retrieval and metadata tools inside this repository, but keep
evaluation adapters and outputs isolated from the eventual production pipeline.
An independent repository is not currently necessary because the evaluations
directly determine which capabilities DeathMap-AI should integrate and which gaps
it may need to implement.

Tool evaluation code should be disposable or promotable:

- a thin adapter records a tool's native query and raw response;
- common inspection output makes results comparable without forcing identical
  query syntax;
- no adapter becomes a production dependency until its value, accessibility,
  reproducibility, and maintenance burden are reviewed;
- exploratory code is not imported by stable production modules.

Reconsider a separate repository only if the evaluation harness becomes a
general-purpose resource intended for reuse beyond DeathMap-AI.

## [PS11] Standard discovery-record unit

Accepted decision: one discovery record represents one candidate returned by one
resource during one search run.

Separate records must be retained when multiple resources find the same candidate
or when the same resource finds it in different versioned runs. Deduplication may
group those records into a combined candidate, but it must not erase their
individual retrieval provenance.

The discovery record is an intake object, not a curated scientific assertion.
Fields extracted before manual review are hints or source claims. Eligibility,
experimental identity, and dataset attribution remain undetermined until they are
supported by reviewed evidence.

See [`standard-discovery-record.md`](standard-discovery-record.md) for the pilot
contract.

## [PS12] Metadata-only retrieval boundary

The ORCS pilot may download publication metadata, screen metadata, controlled
vocabularies, identifiers, and other descriptive records needed for discovery.

"Do not download datasets" means that the pilot must not download experimental
screen results or molecular data, including gene-level scores, guide counts,
FASTQ files, processed count matrices, or similar result files. Metadata records
describing a screen are allowed even when ORCS refers to a collection of screens
as a dataset.

## [PS13] ORCS terminology normalization

During tool evaluation, spelling variants such as `co-culture`, `coculture`, and
`co culture` remain separate so their contributions can be measured.

In a future user-facing search interface, common variants may be normalized to
the canonical terminology supported by ORCS. For example, `coculture` and
`co culture` may be interpreted as `co-culture`. The original user query and the
normalized query must both be recorded so normalization remains transparent.

Normalization changes search syntax, not scientific eligibility. It must not
cause a result to be labeled as a qualifying co-culture screen automatically.

## [PS14] Screen-family context

When one ORCS screen is a candidate co-culture screen anchor, retain the
publication anchor's sibling screens as linked context. Label each record's
inclusion basis so baseline, cytokine-only, or other comparator screens are not
misrepresented as direct co-culture evidence.

For example, ORCS screens 1912-1917 directly describe TIL co-culture conditions,
while screens 1910-1911 are the associated baseline and IFN-gamma context. All
eight should remain reviewable, but their evidentiary roles differ.

## [PS15] ORCS-only enrichment boundary

During the current ORCS iteration, additional metadata and supporting-asset
links may be retained when ORCS exposes them. Do not search PubMed, GEO, journal
sites, or other resources to fill missing fields during this iteration. Missing
publication details, accessions, and evidence relationships remain explicitly
unresolved until a later resource evaluation authorizes those sources.

An ORCS-hosted supplementary link may be recorded as an available supporting
asset without ingesting its experimental contents into the metadata pipeline.

## [PS16] Temporary Excel reporting

Keep CSV and JSON outputs as the canonical machine-readable records. A derived
Excel workbook may be generated for project-owner and PI review. The pilot
workbook contains all candidate records, all native screen-metadata records,
run context, source links, and field descriptions.

Excel generation is a temporary reporting convenience and must not become a
required production dependency.

## [PS17] ORCS pilot completion

The project owner marked the metadata-only ORCS pilot complete on 2026-09-07.
Preserve the existing ORCS retrieval outputs as the resource-specific baseline
while allowing manual review fields to be completed or corrected.

Continuing adjudication does not reopen the retrieval pilot. A materially changed
ORCS query strategy, newly downloaded ORCS index, or new candidate-generation
rule must be recorded as a separate versioned run. ORCS results may later be
compared or integrated with other resources, but they must not be used to seed a
comparison resource's independent discovery queries.

## [PS18] Co-culture evidence may be hidden in details

Return to the ORCS observation that some qualifying screens were not formally
classified as co-culture even though their conditions or screen details clearly
described interacting cancer and immune populations. Future discovery and
adjudication must examine the perturbed population, interacting population,
selection pressure, condition details, and publication context rather than
requiring a literal co-culture label.

This is a retrieval lesson, not authorization to label candidates automatically.
Direct, indirect, and inferred co-culture evidence must remain distinguishable
and reviewable.

## [PS19] Retired resource boundary

Retired 2026-09-19; see the dated decision in the repository README.
