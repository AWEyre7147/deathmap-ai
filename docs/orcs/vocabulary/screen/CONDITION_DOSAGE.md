---
field: "CONDITION_DOSAGE"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 248
description_basis: "format profile generated from data"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# CONDITION_DOSAGE

## Technical definition

Dose or ratio of the condition, free text (e.g. '130.0 nM', '1:1', '10 ng/ml'); '-' if not applicable.

## Plain-language description

How much of the drug or condition was used. For immune cells it may be a ratio of immune cells to cancer cells.

## Where it goes in DeathMap

Screens.condition_dosage_reported; Screens.effector_target_ratio_reported (when the condition is an immune population)


## Value formats

Numbers are replaced by `N` to show the patterns used.

| Pattern | Screens |
|---|---:|
| `-` | 1414 |
| `N µM` | 269 |
| `N nM` | 197 |
| `N MOI` | 179 |
| `N ng/mL` | 26 |
| `N IC` | 22 |
| `N Ratio of effector cells/target cells` | 20 |
| `N µg/mL` | 19 |
| `N μmol/L` | 13 |
| `N IU/ml` | 9 |
| `N mM` | 8 |
| `N LD (%Lethal Dose)` | 6 |
| `N %` | 5 |
| `N units/mL` | 4 |
| `N nmol/L` | 4 |
| `N Gy` | 4 |
| `N pM` | 3 |
| `N M` | 3 |
| `N ng/µL` | 2 |
| `N mg/kg` | 2 |

## Most common values

| Value | Screens |
|---|---:|
| `-` | 1414 |
| `5.0 µM` | 33 |
| `0.1 MOI` | 25 |
| `1.0 µM` | 22 |
| `20.0 IC` | 22 |
| `0.3 MOI` | 20 |
| `10.0 nM` | 17 |
| `100.0 nM` | 16 |
| `2.5 µM` | 16 |
| `50.0 nM` | 14 |
| `0.01 MOI` | 14 |
| `10.0 µM` | 13 |
| `0.5 µM` | 13 |
| `0.005 MOI` | 13 |
| `1 µM` | 12 |
