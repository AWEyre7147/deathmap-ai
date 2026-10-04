---
field: "SCREEN_TYPE"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 5
description_basis: "hand-authored by Perplexity; review recommended"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# SCREEN_TYPE

## Technical definition

Direction of selection: negative (dropout), positive (enrichment), both, or phenotype (sorting-based).

## Plain-language description

Whether the screen looks for genes cells need, genes whose loss helps cells survive, or genes that change a measurable feature.

## Where it goes in DeathMap

Screens.screen_category_normalized (selection direction component)


## Values

| Value | Screens | Technical description | Plain-language description | Normalized candidate |
|---|---:|---|---|---|
| `Negative Selection` | 1089 | Hits are guides depleted from the final population: their target genes are required for survival or growth under the condition (dropout screen). | The screen looks for genes the cells cannot live (or grow) without. Cells missing those genes disappear over time. | negative_selection |
| `Positive and Negative Selection` | 504 | Both enriched and depleted guides are scored from the same selection, identifying both resistance and sensitivity genes. | The screen looks both ways: genes whose loss helps cells survive and genes whose loss makes them die. | positive_and_negative_selection |
| `Positive Selection` | 364 | Hits are guides enriched in the final population: loss of the target gene confers a survival or growth advantage under the selective condition (e.g., resistance). | The screen looks for genes whose loss helps cells survive a challenge, such as a drug or immune attack. Cells missing those genes take over. | positive_selection |
| `Phenotype Screen` | 259 | Cells are separated by a measured trait (e.g., FACS sorting on a reporter or surface protein) rather than by survival; hits are guides that differ between sorted bins. | Instead of counting which cells survive, the cells were sorted by a feature (like how much of a protein they show on their surface). The screen finds genes that control that feature. | phenotype_sorting |
| `Unknown` | 1 | Selection direction not reported or not determinable from the source. | The source does not say how the screen picked out its hits. | unresolved |
