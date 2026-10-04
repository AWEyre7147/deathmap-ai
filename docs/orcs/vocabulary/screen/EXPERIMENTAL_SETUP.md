---
field: "EXPERIMENTAL_SETUP"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 18
description_basis: "hand-authored by Perplexity; review recommended"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# EXPERIMENTAL_SETUP

## Technical definition

ORCS controlled term for the selective pressure applied during the screen. Multi-valued entries are joined by ' | '.

## Plain-language description

What challenge the cells were put through during the screen (a drug, a virus, immune cells, growth in a mouse, or just time).

## Where it goes in DeathMap

Screens.immune_interaction_mode_normalized; Screens.experimental_setting_normalized; Screens.screen_category_normalized


## Values

| Value | Screens | Technical description | Plain-language description | Normalized candidate |
|---|---:|---|---|---|
| `Timecourse` | 1271 | Selection by growth over time without an added agent; compares late vs. early (or plasmid) guide abundance to find fitness genes. | The cells were simply allowed to grow. Genes whose loss slows growth show up as hits. | baseline_fitness |
| `Drug Exposure` | 538 | Selection in the presence of a drug or chemical (see CONDITION_NAME, CONDITION_DOSAGE). | A drug was added to see which genes change how cells respond to it. | drug_selection |
| `Virus Exposure` | 193 | Selection by viral infection; usually identifies host factors required for infection. | The cells were infected with a virus to find genes the virus needs. | virus_selection |
| `Implantation to Mouse Model` | 46 | Perturbed cells are transplanted into mice and grown as tumors; selection is the in vivo environment, including host immunity when the host is immunocompetent. | The changed cells were put into mice to grow as tumors. If the mice have a working immune system, the immune system is part of the pressure. | in_vivo_tumor_growth |
| `Cytokine exposure` | 32 | Selection in the presence of a cytokine (e.g., IFN-gamma, TNF, IL-2) without effector cells. | A signaling protein that immune cells release (a cytokine) was added. This copies part of an immune attack without the immune cells themselves. | cytokine_selection |
| `T cell exposure` | 32 | Co-culture of perturbed target cells with T cells (CTLs, TILs, antigen-specific, or CAR T cells) as the selective pressure. | Cancer cells were mixed with T cells, an immune cell type that kills infected or cancer cells. Survivors show genes that help cancer cells resist T cells. | coculture_T_cell |
| `Other` | 24 | Setup not covered by the ORCS vocabulary. Inspect CONDITION_NAME and NOTES; several immune co-culture screens (e.g., macrophage phagocytosis, bispecific antibodies) use this label. | The setup did not fit ORCS's standard labels. The details are in other fields. | unresolved_check_condition |
| `Toxin Exposure` | 22 | Selection by a biological toxin; identifies receptors and uptake factors. | A natural poison was added to find genes the poison needs. | toxin_selection |
| `Ligand Exposure` | 19 | Selection by exposure to a purified ligand or protein that binds a cell-surface receptor. | A molecule that binds to a receptor on the cell surface was added. | ligand_selection |
| `Bacteria Exposure` | 11 | Selection by infection with bacteria. | The cells were exposed to bacteria. | bacteria_selection |
| `NK cell exposure` | 10 | Co-culture of perturbed target cells with natural killer (NK) cells as the selective pressure. | Cancer cells were mixed with natural killer (NK) cells, immune cells that kill abnormal cells without needing prior training. | coculture_NK_cell |
| `Radiation Exposure` | 8 | Selection by ionizing or UV radiation. | The cells were exposed to radiation, which damages DNA. | radiation_selection |
| `Cytokine depletion` | 3 | Selection after removal of a cytokine or growth factor the cells depend on. | A growth signal the cells normally need was taken away. | cytokine_withdrawal |
| `SARS-CoV-2 Spike-RBD exposure` | 3 | Exposure to the receptor-binding domain of the SARS-CoV-2 spike protein; usually a phenotype (binding) screen. | Cells were exposed to the part of the COVID-19 virus that grabs onto cells. | ligand_selection |
| `Oxygen Exposure` | 2 | Selection under altered oxygen levels (hypoxia or hyperoxia). | The cells were grown with more or less oxygen than usual. | oxygen_selection |
| `Cytokine exposure \| Drug exposure` | 1 | Combined cytokine and drug selection in a single screen; split on ' \| ' for filtering. | Both a cytokine and a drug were added. | cytokine_selection; drug_selection |
| `SARS-CoV-2 Spike exposure (293T-spike-GFP11-P2A-mCherry cells)` | 1 | Co-culture with spike-expressing cells to select for cell-cell fusion or binding. | Cells were mixed with other cells carrying the COVID-19 spike protein. | ligand_selection |
| `Transferrin receptor (TFRC/CD71) exposure` | 1 | Exposure to transferrin receptor ligand; study-specific setup. | Cells were exposed to a molecule that binds the iron-uptake receptor. | ligand_selection |
