---
field: "SIGNIFICANCE_CRITERIA"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 266
description_basis: "format profile generated from data"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# SIGNIFICANCE_CRITERIA

## Technical definition

Free-text hit threshold, usually 'Score.N (<type>) <operator> <value>', e.g. 'Score.1 (FDR) < 0.05'.

## Plain-language description

The exact cutoff used to call a gene a hit.

## Where it goes in DeathMap

Not mapped (hit-level metadata)


## Value formats

Numbers are replaced by `N` to show the patterns used.

| Pattern | Screens |
|---|---:|
| `Score.N (FDR) < N` | 645 |
| `Score.N (Bayes Factor) > N` | 365 |
| `-` | 317 |
| `Score.N (p-Value) < N` | 120 |
| `Score.N (FDR) < N OR Score.N (FDR) < N` | 65 |
| `Score.N (CRISPR Score (CS)) < -N` | 64 |
| `Score.N (Z-score) < -N OR Score.N (Z-score) > N` | 45 |
| `Score.N (p-Value) < N AND Score.N (FDR) < N` | 39 |
| `Score.N (LogNFC) <= -N AND Score.N (p-Value) <= N OR Score.N (LogNFC) >= N AND Score.N (p-Value) <= N` | 36 |
| `Score.N (FDR) < N AND Score.N (LogNFC) > N` | 33 |
| `Score.N (Z-score) > N OR Score.N (Z-score) < -N` | 26 |
| `Score.N (p-Value) < N OR Score.N (p-Value) < N` | 19 |
| `Score.N (CGI) < -N AND Score.N (FDR) < N OR Score.N (CGI) > N AND Score.N (FDR) < N` | 18 |
| `Score.N (p-Value) < N AND Score.N (sgRNA number) > N` | 16 |
| `Score.N (Z-score) < N AND Score.N (FDR) <= N OR Score.N (Z-score) > N AND Score.N (FDR) <= N` | 14 |
| `Score.N (q-Value) < N` | 13 |
| `Score.N (LogN (p-value)) < -N` | 12 |
| `Score.N (LogNFC) < -N` | 12 |
| `Score.N (Rho (LogNe Treated vs. Untreated)) > N OR Score.N (Rho (LogNe Treated vs. Untreated)) < -N` | 11 |
| `Score.N (RRA score) < -N` | 10 |

## Most common values

| Value | Screens |
|---|---:|
| `Score.2 (FDR) < 0.05` | 412 |
| `Score.1 (Bayes Factor) > 0.0` | 328 |
| `-` | 317 |
| `Score.2 (p-Value) < 0.05` | 60 |
| `Score.3 (FDR) < 0.05` | 57 |
| `Score.1 (CRISPR Score (CS)) < -1.5` | 45 |
| `Score.2 (FDR) < 0.05 OR Score.4 (FDR) < 0.05` | 37 |
| `Score.1 (Log2FC) <= -0.3 AND Score.2 (p-Value) <= 0.01 OR Score.1 (Log2FC) >= 0.3 AND Score.2 (p-Value) <= 0.01` | 36 |
| `Score.1 (p-Value) < 0.05 AND Score.2 (FDR) < 0.05` | 36 |
| `Score.3 (FDR) < 0.1` | 34 |
| `Score.2 (p-Value) < 0.01` | 33 |
| `Score.1 (Z-score) < -3.0 OR Score.1 (Z-score) > 6.0` | 31 |
| `Score.1 (FDR) < 0.1` | 29 |
| `Score.3 (FDR) < 0.01` | 29 |
| `Score.1 (FDR) < 0.05 AND Score.2 (Log2FC) > 0.0` | 27 |
