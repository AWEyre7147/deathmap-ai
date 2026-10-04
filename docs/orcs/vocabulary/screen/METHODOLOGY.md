---
field: "METHODOLOGY"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 4
description_basis: "hand-authored by Perplexity; review recommended"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# METHODOLOGY

## Technical definition

Perturbation outcome category: Knockout, Inhibition, Activation, or Perturbation.

## Plain-language description

What the gene change does: break, dim, boost, or slightly alter the gene.

## Where it goes in DeathMap

Screens.methodology_reported; Screens.perturbation_type_normalized


## Values

| Value | Screens | Technical description | Plain-language description | Normalized candidate |
|---|---:|---|---|---|
| `Knockout` | 2075 | Loss of function by gene disruption (nuclease or base-editor stop codon). | The gene is broken so it no longer works. | knockout |
| `Activation` | 79 | Increased transcription by CRISPRa. | The gene's activity is turned up. | activation |
| `Inhibition` | 52 | Reduced transcription by CRISPRi (no DNA cut). | The gene's activity is turned down. | interference |
| `Perturbation` | 11 | Targeted point mutation by base editing; effect may be loss, gain, or neutral. | A small, precise change is made in the gene. | base_editing |
