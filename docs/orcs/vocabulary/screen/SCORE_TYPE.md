---
field: "SCORE.#_TYPE"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 59
description_basis: "hand-authored by Perplexity"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# SCORE.#_TYPE

## Technical definition

Type of the Nth score column (SCORE.1_TYPE ... SCORE.5_TYPE) in the ORCS gene-score file; '-' means the column is unused.

## Plain-language description

What each number in the results file means (for example, a p-value or a fold change).

## Where it goes in DeathMap

Not mapped (gene-score metadata; future hit-level table)


Counts are column occurrences across SCORE.1_TYPE to SCORE.5_TYPE.

## Values

| Value | Occurrences | Technical description | Plain-language description |
|---|---:|---|---|
| `-` | 6038 | No score in this column. |  |
| `FDR` | 1377 | False discovery rate (adjusted p-value) for the gene. | The chance the hit is a false alarm, after correcting for testing many genes. |
| `p-Value` | 816 | Unadjusted p-value. | How likely the result is due to chance. |
| `Log2FC` | 648 | log2 fold change of abundance. | How much the gene's guides went up or down, on a doubling scale. |
| `Bayes Factor` | 388 | BAGEL Bayes factor (higher = more likely essential). | How strongly the evidence says the gene is essential. |
| `CERES score` | 375 | CERES essentiality score (more negative = more essential; about -1 is typical of common essentials). | How much cells need this gene; more negative means more needed. |
| `MaGeCK Score` | 265 | MAGeCK gene score. | MAGeCK's gene score. |
| `Z-score` | 169 | Standardized score. | How unusual the result is compared to all genes. |
| `MAGeCK pos score` | 151 | MAGeCK RRA enrichment score. | MAGeCK score for genes whose loss helps cells. |
| `MAGeCK neg score` | 135 | MAGeCK RRA depletion score. | MAGeCK score for genes whose loss hurts cells. |
| `CRISPR Score (CS)` | 102 | CRISPR score (average log2 fold change of guides). | Average change for a gene's guides. |
| `STARS Score` | 69 | STARS gene score. | STARS ranking score. |
| `q-Value` | 48 | FDR-adjusted p-value (q-value). | A p-value corrected for testing many genes. |
| `Beta Score` | 45 | MAGeCK-MLE beta score (positive = enriched, negative = depleted). | Gene effect size from MAGeCK: positive helps, negative hurts. |
| `Rank` | 45 | Gene rank. | The gene's position in the list. |
| `CasTLE Score` | 39 | CasTLE confidence score. | How confident the result is. |
| `Log10 (p-value)` | 36 | log10-transformed p-value. | A p-value on a log scale. |
| `Log2` | 34 | log2-transformed score. | A score on a doubling scale. |
| `CasTLE Effect` | 31 | CasTLE estimated effect size. | How big the gene's effect is. |
| `RANKS score` | 23 | RANKS gene score. | RANKS ranking score. |
| `sgRNA number` | 22 | Number of guides supporting the gene. | How many guides agreed. |
| `CGI` | 19 | Chemical-genetic interaction score. | How a gene change and a drug interact. |
| `RSA` | 19 | RSA score. | RSA ranking score. |
| `NES (Normalized enrichment score)` | 18 | Normalized enrichment score. | A standardized enrichment score. |
| `RRA score` | 18 | Robust rank aggregation score. | A rank-combining score. |
| `Rho (Log2e Treated vs. Untreated)` | 13 | Treatment phenotype (rho) for CRISPRi/a screens. | Effect on response to treatment. |
| `T-score` | 12 | t-statistic-like score. | A score comparing change to variability. |
| `ZLFC` | 12 | Z-scored log fold change. | A standardized change score. |
| `mean fold change` | 9 | Mean fold change across guides. | Average change across a gene's guides. |
| `-log (p-value)` | 8 | Negative log10 p-value (larger is more significant). | A significance score where bigger means stronger. |
| `Differential score` | 8 | Difference between conditions. | Change between conditions. |
| `Read counts` | 8 | Raw sequencing read counts. | How many times the guide was read by the sequencer. |
| `FS (Fitness Score)` | 6 | Fitness score. | How much the gene affects growth. |
| `Gene Score` | 6 | Study-specific gene score. | The study's own gene score. |
| `neg Z-score` | 6 | Z-score for depletion. | How strongly the gene's guides dropped. |
| `pos Z-score` | 6 | Z-score for enrichment. | How strongly the gene's guides increased. |
| `RRA_depletion` | 6 | RRA depletion score. | Rank score for dropping. |
| `RRA_enrichment` | 6 | RRA enrichment score. | Rank score for increasing. |
| `RIGER score` | 5 | RIGER gene score. | RIGER ranking score. |
| `Dependency score` | 4 | Gene dependency score. | How much cells depend on the gene. |
| `Log10` | 4 | log10-transformed study score. | A score on a log scale. |
| `Log10 (Corrected p-Value)` | 4 | log10-transformed adjusted p-value. | A corrected p-value on a log scale. |
| `RRA rank` | 4 | RRA rank. | The gene's rank. |
| `Essentiality Score` | 3 | Essentiality score. | How essential the gene is. |
| `Mean Depletion` | 3 | Mean guide depletion. | Average drop for a gene's guides. |
| `Nscore` | 3 | Normalized score. | A normalized score. |
| `Gamma (normalized log2e/t)` | 2 | Growth phenotype (gamma) for CRISPRi/a screens. | Effect on growth. |
| `Gene-level Three Score (TS)` | 2 | Study-specific gene-level score. | The study's own gene score. |
| `neg score p-value` | 2 | p-value for depletion. | Significance for guides that disappeared. |
| `pos score p-value` | 2 | p-value for enrichment. | Significance for guides that increased. |
| `Second best guide score x RSA` | 2 | Combined second-best-guide and RSA score. | A combined robustness score. |
| `UMI` | 2 | Unique molecular identifier counts. | Counts of unique tagged molecules. |
| `Delta` | 1 | Difference between conditions. | Change between conditions. |
| `Depletion-Enrichment (DE) score` | 1 | Combined depletion/enrichment score. | Combined up/down score. |
| `DESeq2` | 1 | DESeq2 statistic. | A count-comparison statistic. |
| `Enrichment` | 1 | Enrichment value. | How much it increased. |
| `Percent sorted cells` | 1 | Percent of cells in the sorted gate. | Share of cells in the sorted group. |
| `Reduced Chi Squared` | 1 | Reduced chi-squared statistic. | A fit statistic. |
| `Second best guide score` | 1 | Score of the second-best guide (robustness metric). | Score of the second-best guide, a check that more than one guide agrees. |
