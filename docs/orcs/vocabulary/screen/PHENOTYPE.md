---
field: "PHENOTYPE"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 29
description_basis: "hand-authored by Perplexity; review recommended"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# PHENOTYPE

## Technical definition

Biological readout measured by the screen (ORCS controlled term).

## Plain-language description

What the researchers measured to judge each gene change, such as cell growth or the amount of a protein.

## Where it goes in DeathMap

Screens.phenotype_original; Screens.readout_reported (candidate)


## Values

| Value | Screens | Technical description | Plain-language description | Normalized candidate |
|---|---:|---|---|---|
| `cell proliferation` | 1180 | Readout is change in cell number over time (fitness), measured by guide abundance. | How fast the cells grow and divide. | fitness_proliferation |
| `response to chemicals` | 506 | Readout is survival or growth in the presence of a drug or chemical (resistance or sensitivity). | How the cells react to a drug: whether they resist it or become more sensitive. | drug_response |
| `response to virus` | 196 | Readout is survival after viral infection, or reporter-based infection status. | Whether the cells survive or get infected by a virus. | virus_response |
| `protein/peptide accumulation` | 159 | FACS-based readout on the level of a protein or reporter (e.g., surface PD-L1 or MHC-I); cells are sorted into high and low bins. | How much of a particular protein the cells make. Cells are sorted into 'high' and 'low' groups. | protein_level_sorting |
| `tumorigenicity` | 42 | Readout is the ability of perturbed cells to form or grow tumors in vivo. | How well the cells grow into a tumor inside an animal. | in_vivo_tumor_growth |
| `response to toxin` | 20 | Readout is survival after toxin exposure. | Whether the cells survive a natural poison. | toxin_response |
| `protein/peptide distribution` | 18 | FACS or imaging readout on where a protein is located in the cell. | Where in the cell a protein ends up. | protein_localization |
| `phagocytosis` | 17 | Readout is engulfment of target cells or particles by phagocytes (e.g., macrophages), or susceptibility of target cells to being engulfed. | Whether immune cells called macrophages 'eat' the target cells. | immune_phagocytosis |
| `regulation of signal transduction phenotype` | 14 | Reporter-based readout of a signaling pathway's activity. | How strongly a cell's internal messaging pathway is switched on. | signaling_reporter |
| `viability` | 12 | Same as 'cell viability' (ORCS spelling variant). | Whether the cells stay alive. | fitness_survival |
| `response to bacteria` | 10 | Readout is survival or infection status after bacterial exposure. | Whether the cells survive or get infected by bacteria. | bacteria_response |
| `cell viability` | 6 | Readout is cell survival under the condition. | Whether the cells stay alive. | fitness_survival |
| `protein transport` | 6 | Readout is trafficking of a protein between compartments. | How proteins are moved around inside the cell. | protein_localization |
| `cell cycle progression` | 4 | Readout is progression through the cell-division cycle, often by sorting on a cell-cycle reporter. | How cells move through the steps of dividing. | cell_cycle |
| `protein binding` | 4 | Readout is binding of a labeled ligand or protein to the cell surface. | Whether something sticks to the outside of the cell. | binding |
| `response to radiation` | 3 | Readout is survival after radiation. | Whether the cells survive radiation damage. | radiation_response |
| `autophagy` | 2 | Reporter readout of autophagic flux. | How cells break down and recycle their own parts. | autophagy |
| `cell migration` | 2 | Readout is directed movement or invasion (e.g., transwell). | How well the cells move or crawl through a barrier. | migration_invasion |
| `regulation of viral programmed -1 ribosomal frameshifting (-1 PRF)` | 2 | Reporter readout of -1 ribosomal frameshifting. | A virus trick for reading its genetic code in a shifted way. | virus_response |
| `RNA accumulation` | 2 | Reporter readout of RNA levels. | How much of a particular RNA message is in the cell. | rna_level |
| `senescence` | 2 | Readout of senescence (permanent growth arrest) markers. | Whether cells permanently stop dividing (an 'aging' state). | senescence |
| `vesicle distribution` | 2 | Readout of intracellular vesicle localization. | Where small bubbles that carry cargo inside the cell end up. | protein_localization |
| `Viral programmed ribosomal frameshifting (PRF)` | 2 | Reporter readout of viral ribosomal frameshifting. | A virus trick for reading its genetic code in a shifted way. | virus_response |
| `lysosome homeostasis` | 1 | Reporter readout of lysosome function. | How well the cell's 'recycling center' works. | organelle_function |
| `pyroptosis` | 1 | Readout of inflammatory, gasdermin-mediated cell death. | A type of cell death that sets off inflammation. | cell_death_mode |
| `regulation of lipid localization` | 1 | Readout of lipid uptake or distribution (e.g., LDL uptake). | How the cell takes in and moves fats. | metabolism |
| `regulation of Nonsense-mediated decay (NMD)` | 1 | Reporter readout of nonsense-mediated mRNA decay activity. | How well the cell destroys faulty RNA messages. | rna_level |
| `response to oxygen concentration` | 1 | Readout is fitness under altered oxygen. | How cells grow with more or less oxygen. | fitness_proliferation |
| `syncytium formation` | 1 | Readout of cell-cell fusion into multinucleated syncytia. | Whether cells fuse together into one big cell. | cell_fusion |
