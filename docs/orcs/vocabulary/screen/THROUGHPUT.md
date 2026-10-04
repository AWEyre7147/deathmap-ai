---
field: "THROUGHPUT"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 2
description_basis: "hand-authored by Perplexity; review recommended"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# THROUGHPUT

## Technical definition

High vs. low throughput as assigned by ORCS curators.

## Plain-language description

Whether many genes or only a few were tested.

## Where it goes in DeathMap

Screens.library_scope_normalized (supporting signal only)


## Values

| Value | Screens | Technical description | Plain-language description | Normalized candidate |
|---|---:|---|---|---|
| `High Throughput` | 2155 | Screen tested many genes at once (typically hundreds to genome-wide) in a single selection. | Many genes were tested at the same time. | high_throughput |
| `Low Throughput` | 62 | Screen tested a small number of genes or guides, often as a validation or focused experiment. | Only a small number of genes were tested. | low_throughput |
