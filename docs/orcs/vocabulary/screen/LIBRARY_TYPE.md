---
field: "LIBRARY_TYPE"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 5
description_basis: "hand-authored by Perplexity; review recommended"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# LIBRARY_TYPE

## Technical definition

CRISPR modality of the library: CRISPRn, CRISPRi, CRISPRa, or base editing.

## Plain-language description

Whether the guides break genes, turn them down, turn them up, or make single-letter changes.

## Where it goes in DeathMap

Screens.library_type_reported; Screens.perturbation_type_normalized


## Values

| Value | Screens | Technical description | Plain-language description | Normalized candidate |
|---|---:|---|---|---|
| `CRISPRn` | 2069 | CRISPR nuclease library: active Cas nuclease creates double-strand breaks, producing frameshift loss-of-function alleles (knockout). | Guides that make a cut in a gene, which usually breaks it so the cell can't use it (a knockout). | knockout |
| `CRISPRa` | 79 | CRISPR activation: dead Cas9 fused to activator domains (VP64, p65-HSF1, VPR, SunTag) is targeted to promoters to increase transcription. | Guides that turn a gene's activity up, making the cell produce more of it. | activation |
| `CRISPRi` | 52 | CRISPR interference: catalytically dead Cas9 fused to a repressor (e.g., KRAB) is targeted to promoters to reduce transcription without cutting DNA. | Guides that turn a gene's activity down, like a dimmer switch, without cutting the DNA. | interference |
| `Cytosine Base Editing-Mediated Gene Perturbation` | 11 | Cytosine base editor (C to T conversion) used to introduce specific point mutations rather than full knockouts. | A tool that changes a single DNA letter to test the effect of small, precise mutations. | base_editing |
| `Cytosine Base Editing-Mediated Gene KnockOut` | 6 | Cytosine base editor used to create premature stop codons (iSTOP), producing knockouts without double-strand breaks. | A tool that changes one DNA letter to create a 'stop' signal, breaking the gene without cutting the DNA. | base_editing_knockout |
