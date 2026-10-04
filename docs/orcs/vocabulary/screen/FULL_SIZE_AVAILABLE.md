---
field: "FULL_SIZE_AVAILABLE"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 2
description_basis: "hand-authored by Perplexity; review recommended"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# FULL_SIZE_AVAILABLE

## Technical definition

Whether ORCS holds scores for the full library ('Yes') or only a subset ('No').

## Plain-language description

Whether ORCS has results for every gene tested, or only the highlighted ones.

## Where it goes in DeathMap

Datasets.processed_data_available (ORCS-hosted gene scores; not a repository dataset)


## Values

| Value | Screens | Technical description | Plain-language description | Normalized candidate |
|---|---:|---|---|---|
| `Yes` | 1978 | ORCS holds scores for every gene in the screened library (SCORES_SIZE equals FULL_SIZE). | ORCS has results for all genes tested, not just the top hits. | complete_gene_scores |
| `No` | 239 | ORCS holds scores only for a subset of genes (usually the reported hits); SCORES_SIZE is smaller than FULL_SIZE. | ORCS only has results for some genes, usually the ones the authors highlighted. | partial_gene_scores |
