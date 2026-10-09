# Project Vision

## Project Name

DeathMap-AI

## Purpose

### [PV-1] Purpose

DeathMap-AI will help researchers discover, organize, and evaluate evidence from
CRISPR perturbation studies involving cancer cells, immune cells, and cancer–immune
interactions. Cancer-only and immune-only studies can be relevant; co-culture is not a universal inclusion requirement. The completed v01 pilot and current v02 enrichment work establish the evidence foundation required before a
future reasoning system can compare screens, datasets, biological contexts, and
therapeutic hypotheses responsibly.

The immediate goal is not to produce biological recommendations. It is to learn
whether existing resources can discover relevant publications and connect them to
their screen groups, screens, datasets, and source evidence with sufficient coverage
and traceability.

## Problem Being Solved

Relevant CRISPR publications, screen metadata and repository datasets are distributed across resources with different identifiers and search structures. Publication association alone does not establish which dataset represents a qualifying screen. Missing and conflicting metadata require traceable review.

## Intended Users

Researchers reviewing CRISPR perturbation studies and maintainers developing reproducible metadata discovery and enrichment.

## High-Level Outcome

### [PV-7] Success criteria

The evidence-discovery and enrichment stages succeed when the project can make evidence-backed statements about:

- which resources retrieve qualifying publications and datasets;
- which query strategies contributed each result;
- what metadata each resource supplies or omits;
- where repository-specific enrichment is necessary;
- which publication, screen, and dataset relationships can be supported;
- what remains ambiguous or conflicting; and
- what level of human review is required.

Candidate counts alone do not establish successful retrieval coverage. Coverage
claims require a defined comparison set and adjudication appropriate to the claim.

## Major Modules

- Evidence discovery and dataset attribution: the current module.
- Screen-group organization after sufficient enrichment evidence: planned capability.
- Experimental dataset normalization, analysis and ligand–receptor annotation: deferred capabilities requiring their own specifications.
- Future reasoning: deferred long-term capability, not authorized implementation.

## System Boundaries

### In Scope

### [PV-2] Milestone-one objective

The completed milestone 1 established an evidence-discovery benchmark. Its broader evaluation framework covers existing retrieval
and metadata resources across four experimental classes:

1. conventional cancer-cell CRISPR screens;
2. co-culture or microenvironment CRISPR screens;
3. single-cell multimodal CRISPR screens; and
4. in vivo or spatial perturbation screens.

The completed ORCS milestone uses the biological-classes profile: human/mouse, configured CRISPR modalities and cancer-derived, immune-lineage or organoid contexts. Earlier pooled cancer–immune knockout work is historical. Current v02 planning translates this scientific intent into repository-specific metadata enrichment routes; independent repository discovery remains a later task.

Current priority is repository enrichment of the curated ORCS collection, followed by development of the existing screen-group concept. Whole-ORCS grouping remains exploratory.

### Out of Scope

### [PV-6] Milestone-one exclusions

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

## Guiding Principles

### [PV-3] Evidence-centered architecture

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

### [PV-4] Human review

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

### [PV-5] Development approach

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

## Long-Term Direction

The intended direction is comprehensive identification of datasets and publications from CRISPR perturbation studies of cancer cells and immune cells, followed by appropriately normalized and analyzed datasets with thorough annotations for future reuse. A priority future annotation source is the ligand–receptor database, previously known as XDeathDB. This is a long-term destination, not authorization to download experimental contents, normalize matrices, run analyses or integrate that database in the current metadata-enrichment phase.

### [PV-8] Long-term direction

A later DeathMap-AI reasoning layer may use the evidence graph produced by these
modules to compare biological contexts and generate testable hypotheses. That
future work depends on trustworthy entity boundaries and provenance established
here. Milestone 1 must not anticipate that layer by forcing uncertain evidence
into simplified conclusions.

## Current Version / Phase

Executable package: v0.1.0. Completed capabilities include the three cached ORCS profiles, Cellosaurus interpretation, reusable DOI/PMID/PMCID resolution, and portable Excel export. Current iteration: v02 — ORCS Pilot Enrichment. The PubMed enrichment subgoal is complete: shared publication metadata, direct repository associations and search-specific workbooks. Native GEO, BioStudies–ArrayExpress and ENA enrichment are the next goals; repository-specific hierarchy and attribution adapters are not yet implemented. Native repository retrieval contracts and screen-group rules await owner decisions. This restructuring does not authorize new retrieval, grouping, commits or publication.
