---
tags: [deathmap-ai, orcs, vocabulary, screen]
generated: 2026-10-04
---

# ORCS screen vocabulary

One page per native field of `data/orcs/screen-index.json` (2,217 screens). Identifier fields (SCREEN_ID, SOURCE_ID, SCREEN_NAME, AUTHOR, SOURCE) are not described.

## Experimental design

| Field | Unique values | Page type | Plain-language summary |
|---|---:|---|---|
| [[EXPERIMENTAL_SETUP]] | 18 | values | What challenge the cells were put through during the screen (a drug, a virus, immune cells, growth in a mouse, or just time). |
| [[CONDITION_NAME]] | 439 | values | The specific thing the cells were exposed to, such as the name of the drug, virus, or immune cell type. |
| [[CONDITION_DOSAGE]] | 248 | format | How much of the drug or condition was used. For immune cells it may be a ratio of immune cells to cancer cells. |
| [[DURATION]] | 92 | format | How long the cells were under the challenge. |
| [[SCREEN_TYPE]] | 5 | values | Whether the screen looks for genes cells need, genes whose loss helps cells survive, or genes that change a measurable feature. |
| [[SCREEN_FORMAT]] | 3 | values | How the experiment was set up: all gene changes mixed in one dish, grown in an animal, or each in its own well. |
| [[THROUGHPUT]] | 2 | values | Whether many genes or only a few were tested. |
| [[PHENOTYPE]] | 29 | values | What the researchers measured to judge each gene change, such as cell growth or the amount of a protein. |

## Perturbation and library

| Field | Unique values | Page type | Plain-language summary |
|---|---:|---|---|
| [[LIBRARY]] | 177 | values | Which collection of guides (the set of genes to be changed) was used. |
| [[LIBRARY_TYPE]] | 5 | values | Whether the guides break genes, turn them down, turn them up, or make single-letter changes. |
| [[METHODOLOGY]] | 4 | values | What the gene change does: break, dim, boost, or slightly alter the gene. |
| [[ENZYME]] | 20 | values | Which CRISPR protein tool was used. |
| [[MOI]] | 37 | format | How many guide-carrying viruses were used per cell. A low number means most cells got only one gene change, which keeps results clean. |

## Biological model

| Field | Unique values | Page type | Plain-language summary |
|---|---:|---|---|
| [[CELL_LINE]] | 825 | values | Which cells received the gene changes. Most are 'cell lines': cells first taken from a patient or animal and then grown in labs for many years. |
| [[CELL_TYPE]] | 145 | values | A short description of what kind of cell was used, such as 'Melanoma Cell Line' (skin cancer cells). |
| [[ORGANISM_OFFICIAL]] | 5 | values | Which species the cells came from. |
| [[ORGANISM_ID]] | 5 | field_only | A number code for the species. |

## Analysis and scores

| Field | Unique values | Page type | Plain-language summary |
|---|---:|---|---|
| [[ANALYSIS]] | 46 | values | The computer method the authors used to decide which genes were important. |
| [[SIGNIFICANCE_INDICATOR]] | 3 | values | How ORCS decides which genes count as hits. |
| [[SIGNIFICANCE_CRITERIA]] | 266 | format | The exact cutoff used to call a gene a hit. |
| [[SCORE_TYPE|SCORE.#_TYPE]] | 59 | values | What each number in the results file means (for example, a p-value or a fold change). |
| [[SCORE_COL_COUNT]] | 5 | field_only | How many different scores ORCS stores per gene. |
| [[SCORES_SIZE]] | 657 | format | How many genes ORCS has results for in this screen. |
| [[FULL_SIZE]] | 507 | format | How many genes the screen tested in total. |
| [[FULL_SIZE_AVAILABLE]] | 2 | values | Whether ORCS has results for every gene tested, or only the highlighted ones. |
| [[NUMBER_OF_HITS]] | 1146 | format | How many genes the screen called as hits. |

## Source and free text

| Field | Unique values | Page type | Plain-language summary |
|---|---:|---|---|
| [[SOURCE_TYPE]] | 2 | values | Tells you whether the screen comes from a published paper or a preprint. |
| [[NOTES]] | 953 | field_only | Extra notes from the ORCS team about the screen. |
| [[SCREEN_RATIONALE]] | 344 | field_only | One sentence on what the screen was trying to find. |

