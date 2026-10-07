# DeathMap-AI v0.1 project vision

## [PV-1] Purpose

DeathMap-AI will help researchers discover, organize, and evaluate evidence from
functional genomic studies relevant to cancer biology and cancer–immune
interactions. Version 0.1 establishes the evidence foundation required before a
future reasoning system can compare screens, datasets, biological contexts, and
therapeutic hypotheses responsibly.

The immediate goal is not to produce biological recommendations. It is to learn
whether existing resources can discover relevant publications and connect them to
their screen groups, screens, datasets, and source evidence with sufficient coverage
and traceability.

## [PV-2] Milestone-one objective

Milestone 1 is an evidence-discovery benchmark. It evaluates existing retrieval
and metadata resources across four experimental classes:

1. conventional cancer-cell CRISPR screens;
2. co-culture or microenvironment CRISPR screens;
3. single-cell multimodal CRISPR screens; and
4. in vivo or spatial perturbation screens.

The completed ORCS milestone uses the biological-classes profile: human/mouse, configured CRISPR modalities and cancer-derived, immune-lineage or organoid contexts. Earlier pooled cancer–immune knockout work is historical. Next-version planning translates this scientific intent into repository-specific filters and metadata routes.

## [PV-3] Evidence-centered architecture

DeathMap-AI separates:

- discovery observations returned by a resource;
- publications;
- screen groups that capture shared experimental design and context;
- individual screens that capture independently interpretable selections;
- repository datasets and their hierarchy;
- samples, runs, and files when needed;
- relationships among those entities; and
- the evidence supporting each field and relationship.

Source identifiers and provenance must survive every transformation. Direct
evidence, inference, conflict, and unresolved status remain distinguishable.

## [PV-4] Human review

Automated retrieval and normalization prepare evidence for review; they do not
replace scientific judgment. Reviewers must be able to see:

- what the source reported;
- what the pipeline normalized;
- what relationship was inferred;
- what remains unresolved;
- where the supporting evidence can be checked; and
- which action requires human attention.

The pipeline should minimize repetitive review while never hiding uncertainty
behind a complete-looking output.

## [PV-5] Development approach

Development proceeds through small, versioned resource evaluations:

1. preserve native responses;
2. produce common discovery records;
3. evaluate retrieval behavior and metadata coverage;
4. enrich repository-specific records when authorized;
5. project supported entities and relationships;
6. review JSON outputs;
7. generate review workbooks when the scientific projection is sufficiently
   stable; and
8. promote only demonstrated capabilities into the production pipeline.

Retrieval runs must be reproducible, resumable when appropriate, and explicit
about limits, failures, dates, tool versions, queries, and preserved raw evidence.

## [PV-6] Milestone-one exclusions

Milestone 1 does not implement:

- patient-context integration;
- therapeutic recommendation or ranking;
- a generalized biomedical search engine;
- a graph user interface;
- the future reasoning layer;
- automatic resolution of ambiguous scientific relationships; or
- bulk download or analysis of experimental molecular datasets.

Metadata retrieval may identify and describe experimental data. Gene-level
results, guide counts, FASTQ files, processed matrices, and similar experimental
contents are outside the metadata-only discovery stage.

## [PV-7] Success criteria

Version 0.1 succeeds when the project can make evidence-backed statements about:

- which resources retrieve qualifying publications and datasets;
- which query strategies contributed each result;
- what metadata each resource supplies or omits;
- where repository-specific enrichment is necessary;
- which publication, screen, and dataset relationships can be supported;
- what remains ambiguous or conflicting; and
- what level of human review is required.

Candidate counts alone do not establish successful retrieval coverage. Coverage
claims require a defined comparison set and adjudication appropriate to the claim.

## [PV-8] Long-term direction

A later DeathMap-AI reasoning layer may use the evidence graph produced by these
modules to compare biological contexts and generate testable hypotheses. That
future work depends on trustworthy entity boundaries and provenance established
here. Milestone 1 must not anticipate that layer by forcing uncertain evidence
into simplified conclusions.
