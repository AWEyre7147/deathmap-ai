---
field: "SIGNIFICANCE_INDICATOR"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 3
description_basis: "hand-authored by Perplexity; review recommended"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# SIGNIFICANCE_INDICATOR

## Technical definition

How ORCS determines which genes are hits: by a score threshold, by an author-supplied significance column, or all listed genes.

## Plain-language description

How ORCS decides which genes count as hits.

## Where it goes in DeathMap

Not mapped (hit-level metadata)


## Values

| Value | Screens | Technical description | Plain-language description |
|---|---:|---|---|
| `Score Significance` | 1900 | Hits are defined by a threshold on a score column (given in SIGNIFICANCE_CRITERIA). | A gene counts as a hit if its score passes a cutoff. |
| `Column Significance` | 161 | Hits are flagged in a dedicated significance column supplied by the authors. | The authors marked which genes were hits. |
| `All Significant` | 156 | Every gene in the ORCS record is a reported hit (typical when only hits were deposited). | Every gene listed is a hit. |
