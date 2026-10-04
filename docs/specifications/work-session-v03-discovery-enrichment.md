# Current work-session specification: v03 discovery and enrichment

## [WS3-1] Status

This is the current work-session specification. The offline planning slice was
completed under `09 V03 Query Planning and Initialization Handoff.md`. On
2026-09-28, the project owner authorized implementation and, after successful
preflight, execution of the SQ01-only blind discovery slice defined in
`10 SQ01 Blind Discovery Handoff.md`.

The historical detailed design, originally docs/proposed-discovery-enrichment-v03.md, is now in the approved external archive. The relocation registry records its original path. This work-session specification preserves its scope and acceptance gates.

On 2026-10-03, the owner authorized a separate ORCS-only profile-filtering run
and population of the blank reference Excel workbook under
[11 ORCS Filter Run and Excel Handoff](11%20ORCS%20Filter%20Run%20and%20Excel%20Handoff.md).
That handoff controls the new ORCS filtering/Excel task and explicitly identifies
its exceptions to the earlier JSON-only stopping point. The historical SQ01 run
and its native-only boundaries remain unchanged. Enrichment follows Excel review.

## [WS3-2] Objective

Design and, after approval, implement a new versioned discovery iteration that:

1. searches BioGRID ORCS and OmicsDI for two cancer–immune pooled CRISPR questions;
2. measures blind publication discovery against a known qualifying list only after
   discovery output is frozen;
3. performs separately labeled diagnostic recovery for missed publications;
4. enriches discovered repository accessions, beginning with GEO-related records;
5. classifies dataset roles and hierarchy using evidence-preserving vocabulary;
6. projects supported entities into the seven JSON tables; and
7. stops for JSON review before generating a new Excel workbook.

## [WS3-3] Scientific questions

1. `pooled CRISPR knockout screens in cancer cells under immune selection`
2. `pooled CRISPR knockout screens in immune cells under cancer-cell-mediated selection`

The questions define scientific intent. Resource-specific literal queries require
separate review and approval.

## [WS3-4] Known-publication evaluation boundary

`data/brainstorming/week3_papers_metadata.tsv` is a list of publications already
known by the project owner to qualify and expected to be retrieved by the searches.

Before blind discovery is frozen, no value from that file may be used as a search
input, query expansion, filter, ranking feature, inclusion rule, enrichment seed,
or production dependency.

After the frozen run:

- compare normalized PMID and DOI values to measure retrieval;
- report misses without changing the blind output; and
- use the identifiers only in a separately labeled diagnostic recovery stage.

## [WS3-5] Current resources

- BioGRID ORCS: search the complete cached index without refreshing it.
- OmicsDI: conduct a new versioned search using an approved query family and
  bounded, resumable retrieval rules.
- Repository enrichment: begin with GEO-related records after discovery freezes;
  retain linked hierarchy identifiers when supported.

Do not use ICRAFT data in production discovery. Do not download experimental data.

## [WS3-6] Dataset terminology

Do not treat a pooled CRISPR screen as automatically equivalent to bulk RNA-seq.
Guide-abundance sequencing, bulk RNA-seq, single-cell RNA-seq, Perturb-seq,
targeted sequencing, and other modalities remain distinguishable.

Use the proposed multidimensional vocabulary in `[V3-6]` of
`docs/proposed-discovery-enrichment-v03.md`. Preserve both controlled values and
plain-language meanings in review documentation.

## [WS3-7] Anchor and supporting records

The intended future output distinguishes:

- primary records that directly represent a qualifying screen;
- related companion, follow-up, validation, control, or contextual records; and
- unresolved candidates retained for review.

A related dataset may accompany a qualifying screen without becoming the evidence
that made the publication qualify.

The minimum evidence required for an anchor dataset remains undecided.

## [WS3-8] Attribution boundary

Discovery of a publication-associated dataset does not establish that it contains
a qualifying screen. Exact screen–dataset links require evidence that distinguishes
the screen from the publication's other screens and related study components.

Repository study, sample, run, and file metadata may support attribution. When it
does not resolve attribution, retain publication-only, screen-group,
multiple-possible-screen, or unresolved status.

## [WS3-9] Stage order

1. Research resource interfaces and propose literal query families.
2. Review and freeze the v03 query plan.
3. Run blind ORCS and OmicsDI discovery.
4. Freeze native and projected discovery outputs.
5. Compare the frozen output with the known-publication TSV.
6. Run separately labeled publication-seeded diagnostic recovery.
7. Build a repository-enrichment queue.
8. Retrieve GEO-related metadata with preserved provenance.
9. Classify dataset modality, role, hierarchy, attribution, and availability.
10. Regenerate the seven projected JSON tables.
11. Stop for scientific and structural review.
12. Propose Excel export separately.

Stages 1–3 are authorized only to the extent defined in the SQ01 handoff: SQ01
resource discovery, frozen native outputs, and no evaluation comparison. The
accepted plan must define bounded requests, service rate limits, cumulative
retries, resumable progress, and output paths before live execution.

## [WS3-10] Required first review output

Produce a compact JSON review table with one row per native repository record and:

- run, resource, and query provenance;
- scientific-question direction;
- native repository and accession;
- parent or child accessions when reported;
- source title and description;
- directly supported publication identifiers;
- discovery relationship;
- publication association;
- data modality;
- experimental role;
- repository level;
- screen attribution;
- evidence strength;
- inclusion role;
- availability;
- enrichment status;
- supporting evidence identifiers and locations;
- unresolved issues; and
- reviewer fields.

Complete native records and raw-response evidence remain separate canonical
artifacts.

## [WS3-11] Explicitly deferred work

- Excel workbook generation;
- automatic screen-group creation;
- automatic exact screen–dataset attribution without decisive evidence;
- downloading or analyzing experimental data;
- reasoning-layer behavior;
- patient context; and
- generalized biomedical search.

## [WS3-12] Project-owner decisions required

1. Accept or revise the two scientific questions.
2. Accept the blind-discovery and TSV-separation boundary.
3. Accept or revise the proposed controlled vocabulary and plain-language meanings.
4. Define the minimum evidence required for an anchor dataset.
5. Decide when single-cell RNA-seq without linked perturbation identities is
   qualifying screen data versus related evidence.
6. Approve GEO as the first enrichment target and choose the repository hierarchy
   depth for the initial pass.
7. Accept or revise the required JSON review output.
8. Approve this replacement specification set as authoritative and authorize the
   corresponding updates to `AGENTS.md` and repository documentation.

## [WS3-13] Completion criteria for this work session

The design session is complete when:

- the specification set is accepted;
- all `[WS3-12]` decisions needed for query implementation are resolved;
- the literal query plan and retrieval limits are reviewed;
- output paths and preservation rules are fixed; and
- the project owner explicitly authorizes implementation.

No retrieval-coverage claim is made merely because candidates were returned.

## [WS3-14] Learning checkpoint

This work session treats scientific search intent, publication eligibility,
dataset modality, experimental role, repository hierarchy, and screen attribution
as separate decisions. That separation is required before the pipeline can decide
which record is primary evidence and which records are supporting context.

## [WS3-15] Owner-approved organization update — 2026-10-04

[Handoff 12](12%20Repository%20Organization%20and%20Workbook%20Planning.md) records the current structure and the authorized external relocation of historical artifacts. The blank workbook is now a shared data/templates input; populated results remain in per-run output directories. Original run evidence is preserved unchanged. This update authorizes planning only, not enrichment.

## [WS3-16] Shared ORCS publication metadata — 2026-10-04

The owner separately authorized [handoff 13](13%20ORCS%20Shared%20Publication%20Metadata%20Database.md): build the complete ORCS publication database beside the shared screen database, then plan field mappings from both. This resource-level catalog task is independent of the previous analysis. The authorized retrieval is limited to publication headers and metadata associations; output workbooks and screen inputs remain unchanged.

## [WS3-17] Owner-selected output model v5 — 2026-10-04

[The v5 template contract](15%20Output%20Workbook%20v5%20Template.md) supersedes the historical output-template choice for future workbooks. Glossary/reference content remains fixed. This registration does not execute a search or enrichment run; exporter adaptation remains a separate implementation step.

## [WS3-18] Owner-approved evidence model v6 — 2026-10-04

[The v6 evidence model](16%20Evidence%20Model%20and%20Workbook%20v6.md) records accepted A118–A122. Use grouped reviewer evidence with a complete JSONL ledger, independent Cellosaurus cell_line entries, screen accession references, and marked display truncation from v02 onward. Create v6 and revise only affected glossary entries; preserve v5 and all v01 outputs. This output-stage implementation does not execute the configuration-only v02 search.

## [WS3-19] Owner-authorized CRISPR pilot execution

The owner selected only orcs-crispr-biological-classes-pilot-v01 and requested execution after editing the search documents. Implement and run that profile against the complete saved ORCS screen/publication catalogs and saved Cellosaurus annotations. Generate a new v6 workbook and evidence ledger. No ICRAFT inputs, other pilot searches, source refreshes, external enrichment or experimental-file contents are authorized by this run.

Interpret exact-value lists by splitting `|` and trimming; compare case-sensitively. Search regex fields independently using IGNORECASE without DOTALL. Missing is null, absent, blank or a trimmed dash. Retain every matching rule, keep companions—including common-gate failures—separate, and preserve unresolved joins. The new pilot family's v01 profile numbering is eligible for v6; historical knockout-v01 remains protected.

## [WS3-20] Pilot conclusion and first GitHub preparation

After reviewing the frozen CRISPR pilot output, the owner reported representation of 33/33 CRISPR-related comparison publications present in ORCS and concluded this portion of the project. This is an owner-reviewed publication-level comparison, not a claim of precision across the complete candidate pool or experimental dataset attribution. See the pilot completion record in docs/orcs.

The owner requested preparation for the first GitHub publication, selected the repository name `deathmap-ai` and the MIT code license, and requested documentation resolution/organization. Prepare source inclusion rules and current navigation without changing frozen outputs, deleting historical evidence, adding enrichment or rewriting original provenance. No commit, remote creation or push is performed by this preparation step.
