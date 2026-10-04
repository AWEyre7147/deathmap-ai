---
field: "SCREEN_FORMAT"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 3
description_basis: "hand-authored by Perplexity; review recommended"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# SCREEN_FORMAT

## Technical definition

Physical format of the screen: pooled in vitro ('Pool'), pooled in vivo ('in vivo'), or arrayed ('Array').

## Plain-language description

How the experiment was set up: all gene changes mixed in one dish, grown in an animal, or each in its own well.

## Where it goes in DeathMap

Screens.screen_format_normalized; Screens.experimental_setting_normalized


## Values

| Value | Screens | Technical description | Plain-language description | Normalized candidate |
|---|---:|---|---|---|
| `Pool` | 2167 | Pooled format: all guides are delivered to one population of cells, and guide abundance is read out by sequencing. | All the gene changes are mixed together in one dish of cells. Afterward, sequencing counts which changes are still there. | pooled_in_vitro |
| `in vivo` | 47 | Pooled screen in which the perturbed cells are grown in a living animal (usually transplanted tumors in mice); guide abundance is measured from the recovered tissue. | The mixed pool of changed cells was put into a living animal (usually a mouse) and grown as a tumor. Researchers then counted which changes survived. | pooled_in_vivo |
| `Array` | 3 | Arrayed format: each gene is perturbed in a separate well, and the phenotype is measured well by well (no pooled sequencing readout). | Each gene was changed in its own separate well, so every result can be measured on its own. | arrayed |
