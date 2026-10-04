---
field: "ANALYSIS"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 46
description_basis: "hand-authored by Perplexity"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# ANALYSIS

## Technical definition

Statistical method or software used to score genes and call hits.

## Plain-language description

The computer method the authors used to decide which genes were important.

## Where it goes in DeathMap

Screens.statistical_analysis_reported


## Values

| Value | Screens | Technical description | Plain-language description | Method family |
|---|---:|---|---|---|
| `MaGeCK` | 645 | Model-based Analysis of Genome-wide CRISPR-Cas9 Knockout; negative-binomial guide model with robust rank aggregation (RRA) to gene level. | A widely used program that decides which genes are hits by comparing guide counts between conditions. | mageck |
| `BAGEL` | 388 | Bayesian Analysis of Gene Essentiality; Bayes factor vs. reference essential/non-essential gene sets. | A program that estimates how likely each gene is to be essential. | essentiality |
| `CERES` | 378 | Copy-number-corrected essentiality score (DepMap/Avana). | An essentiality score that corrects for extra copies of DNA in cancer cells. | essentiality |
| `Log2 Fold Change (L2FC)` | 221 | log2 ratio of guide (or gene) abundance between conditions. | How much a guide went up or down, on a doubling scale. | fold_change |
| `DrugZ` | 83 | Z-score-based differential analysis for drug-gene interaction screens. | Finds genes whose loss changes drug response, compared to untreated cells. | differential |
| `STARS` | 69 | Gene-ranking algorithm (Broad GPP) based on guide rank distribution. | A program that ranks genes by how consistently their guides behave. | rank_based |
| `Delta Z scores` | 47 | Difference in Z scores between conditions. | The change in standardized scores between conditions. | differential |
| `CasTLE` | 42 | Cas9 high-Throughput maximum Likelihood Estimator; effect size and confidence from guides and controls. | A program that estimates how strong each gene's effect is. | effect_size |
| `MAGeCK-MLE` | 39 | MAGeCK maximum-likelihood module; fits gene 'beta scores' across multiple conditions. | A version of MAGeCK that compares several conditions at once. | mageck |
| `RSA` | 32 | Redundant siRNA Activity analysis, applied to guides. | A ranking method borrowed from RNAi screens. | rank_based |
| `EdgeR` | 27 | edgeR negative-binomial differential count analysis. | A program borrowed from RNA-seq to compare counts. | count_model |
| `RIGER` | 25 | RNAi Gene Enrichment Ranking, applied to CRISPR guides. | An older ranking method borrowed from RNAi screens. | rank_based |
| `RANKS` | 23 | Robust Analytics and Normalization for Knockout Screens. | A program that ranks genes compared to control guides. | rank_based |
| `Differential LFC` | 19 | Difference in log2 fold change between conditions. | The change in guide enrichment between two conditions. | differential |
| `Kolmogorov-Smirnov` | 15 | Two-sample distribution test. | A statistical test comparing two distributions. | statistic |
| `Robust-rank aggregation (RRA)` | 14 | Gene ranking by aggregating guide ranks (core of MAGeCK). | Ranks genes by combining all their guides. | mageck |
| `Differential CRISPR score` | 13 | Difference in CRISPR score between conditions. | The change in a gene's score between two conditions. | differential |
| `DESeq2` | 12 | DESeq2 negative-binomial differential count analysis. | A program borrowed from RNA-seq to compare counts. | count_model |
| `CRISPRBetaBinomial` | 11 | Beta-binomial model of guide counts (CB2). | A statistical model for guide counts. | count_model |
| `Mann-Whitney U test` | 11 | Rank-based nonparametric test. | A statistical test comparing two groups by rank. | statistic |
| `Phenotype scores based on log2 fold enrichments` | 11 | Phenotype score (e.g., gamma/rho) from log2 enrichment, typical of CRISPRi/a screens. | A score for how strongly a gene affects the trait. | fold_change |
| `MaGeckFlute` | 10 | MAGeCKFlute downstream pipeline (normalization, beta-score comparison, pathway analysis). | A follow-up tool for MAGeCK results. | mageck |
| `None` | 10 | No analysis method reported. | The source does not say how hits were picked. | unresolved |
| `Z-score based on MAGECK score` | 9 | Z-transformed MAGeCK gene scores. | MAGeCK scores rescaled for comparison. | mageck |
| `MAGeCK-iNC` | 8 | MAGeCK with internal negative controls. | MAGeCK using built-in control guides as a baseline. | mageck |
| `Quantitative genetic interaction (qGI) method (Chan, 2022)` | 8 | qGI score for genetic interactions between a query mutation and library genes. | Measures whether two gene changes together have a bigger or smaller effect than expected. | differential |
| `Z-score` | 8 | Standardized score (value minus mean, divided by SD). | A score that shows how unusual a result is. | statistic |
| `ZFCiBAR` | 6 | Z-scored fold change with internal barcodes (iBAR). | A scoring method that uses built-in barcodes to reduce noise. | barcode_based |
| `CRISPR-StAR–MAGeCK analysis pipeline` | 5 | CRISPR-StAR internal-control barcoding analyzed with MAGeCK; designed for noisy in vivo screens. | A method for cleaner results in animal screens. | mageck |
| `MEMcrispR` | 4 | Mixed-effects model for essentiality across cell lines. | A statistical model for essential genes across many cell lines. | essentiality |
| `FDR` | 3 | False discovery rate thresholding. | A cutoff that controls how many hits are likely false. | statistic |
| `DESeq` | 2 | DESeq negative-binomial differential count analysis. | A program borrowed from RNA-seq to compare counts. | count_model |
| `Log2 (TS)` | 2 | log2 of a gene-level three-score (TS) metric. | A study-specific score on a doubling scale. | fold_change |
| `MA-plot` | 2 | Intensity vs. fold-change (MA) analysis. | A visual way to spot genes that change a lot. | fold_change |
| `MAGeCK-MLE/EdgeR` | 2 | MAGeCK-MLE combined with edgeR. | Two hit-finding programs used together. | mageck |
| `MAUDE` | 2 | Mean Alterations Using Discrete Expression; for sorting-based (bin) screens. | A method for screens where cells are sorted into groups. | sorting_model |
| `sgRSEA` | 2 | sgRNA rank-sum enrichment analysis. | A rank-based hit-picking method. | rank_based |
| `CRISPRanalyzer` | 1 | CRISPRAnalyzeR web suite. | An online analysis tool. | rank_based |
| `Differential MAGeCK Beta-scores` | 1 | Difference in MAGeCK-MLE beta scores between conditions. | The change in MAGeCK scores between two conditions. | mageck |
| `eBAR-analyzer (Zhu, 2021)` | 1 | Analysis for external-barcode (eBAR) guide libraries. | A scoring method using barcodes. | barcode_based |
| `Etest` | 1 | E-test statistic (study-specific). | A statistical test. | statistic |
| `HiTSelect` | 1 | High-throughput screen hit selection by multi-objective optimization. | A hit-picking program. | rank_based |
| `MoPAC` | 1 | Modeling of Proliferation and Copy number (MoPAC). | A model that accounts for growth rate and DNA copy number. | essentiality |
| `Reduced Chi Squared` | 1 | Reduced chi-squared goodness of fit. | A statistical fit measure. | statistic |
| `RNAither` | 1 | RNAither pipeline (from RNAi screening). | An analysis tool borrowed from RNAi screens. | statistic |
| `Ss=log10(10,000/Ranked position based on abundance)` | 1 | Study-specific rank-transformed abundance score. | A study-specific ranking score. | rank_based |
