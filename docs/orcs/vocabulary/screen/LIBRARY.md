---
field: "LIBRARY"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 177
description_basis: "Perplexity name-based family/scope assignment; verify scope against the source"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# LIBRARY

## Technical definition

Name of the guide RNA library used (free text curated by ORCS).

## Plain-language description

Which collection of guides (the set of genes to be changed) was used.

## Where it goes in DeathMap

Screens.library_name_reported; Screens.library_scope_normalized (candidate)


## Scope categories

| Scope candidate | Plain-language meaning |
|---|---|
| genome-wide | Covers nearly every gene in the genome. |
| targeted | Covers a chosen group of genes (for example, only kinases or only immune-related genes). |
| partial/custom | A library made for one study or a part of a bigger library. How many genes it covers needs checking. |
| unclear | Coverage is not clear from the name. |

Scope is assigned from the library name only. Per pilot-scope PS3, a targeted library must never be relabeled genome-wide, and the reviewer confirms scope against the paper or FULL_SIZE.

## Values

| Value | Screens | Family | Scope candidate | Modality (LIBRARY_TYPE) | Organism | Technical note |
|---|---:|---|---|---|---|---|
| `3Cs-gRNA DUB library` | 2 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library; verify scope in the source. |
| `African green monkey CRISPRn  (CP0070)` | 7 | Study-specific | partial/custom | CRISPRn | Chlorocebus sabaeus | Study-specific library named after the publication; verify scope in the source. |
| `African green monkey CRISPRn (Norris, 2022)` | 2 | Study-specific | partial/custom | CRISPRn | Chlorocebus sabaeus | Study-specific library named after the publication; verify scope in the source. |
| `Asagio (mouse)` | 7 | Asagio (Broad) | genome-wide | CRISPRn | Homo sapiens, Mus musculus | Compact mouse genome-wide CRISPRn library. |
| `Autophagy and vesicle trafficking targeted library (Elledge and Harper, 2019)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Avana` | 371 | Avana (Broad) | genome-wide | CRISPRn | Homo sapiens | Human genome-wide CRISPRn library (about 74,000 guides, 4 per gene) used by DepMap/Project Achilles. |
| `Avana-4` | 12 | Avana (Broad) | genome-wide | CRISPRn | Homo sapiens | Human genome-wide CRISPRn library (about 74,000 guides, 4 per gene) used by DepMap/Project Achilles. |
| `BARBEKO sgRNA library` | 6 | Study-specific | partial/custom | Cytosine Base Editing-Mediated Gene KnockOut | Homo sapiens | Study-specific library; verify scope in the source. |
| `Bassik Human CRISPR Knockout Library` | 41 | Bassik (Stanford) | genome-wide | CRISPRn | Homo sapiens | Bassik lab genome-wide CRISPRn library (10 guides per gene, delivered as sublibraries; Morgens et al. 2017). |
| `Bassik Mouse CRISPR Knockout Library` | 5 | Bassik (Stanford) | genome-wide | CRISPRn | Mus musculus | Bassik lab genome-wide CRISPRn library (10 guides per gene, delivered as sublibraries; Morgens et al. 2017). |
| `Bassik Mouse CRISPR Knockout Library:  Drug targets, kinases, phosphatases and Membrane Proteins sub-libraries` | 1 | Focused/targeted | targeted | CRISPRn | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `Brie (mouse)` | 31 | Brie (Broad) | genome-wide | CRISPRn | Mus musculus | Optimized mouse genome-wide CRISPRn library (about 78,000 guides; Doench et al. 2016). |
| `Brunello (human)` | 175 | Brunello (Broad) | genome-wide | CRISPRn | Homo sapiens | Optimized human genome-wide CRISPRn library (about 77,000 guides, 4 per gene; Doench et al. 2016). |
| `Brunello Kinase targeted library` | 1 | Brunello-derived | targeted | CRISPRn | Homo sapiens | Targeted subset built from Brunello guides. |
| `Brunello TF targeted library` | 3 | Brunello-derived | targeted | CRISPRn | Homo sapiens | Targeted subset built from Brunello guides. |
| `Caprano` | 2 | Caprano (Broad) | genome-wide | CRISPRa | Mus musculus | Mouse genome-wide CRISPRa library (Sanson et al. 2018). |
| `Cellecta CRISPR Human Genome Knockout Library` | 2 | Cellecta | genome-wide | CRISPRn | Homo sapiens | Commercial Cellecta human genome-wide CRISPRn library. |
| `CP1658 custom Cas9-CRISPR KO library (Rebendenne, 2022)` | 4 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CP1660 custom Cas12a-CRISPR KO library (Rebendenne, 2022)` | 1 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CP1663 custom dCas9-VP64-CRISPRa library (Rebendenne, 2022)` | 4 | Study-specific | partial/custom | CRISPRa | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRIPSRn targeted membrane protein library (Bassik, 2017)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPR SARS-CoV-2 interactor library (Gordon 2020)` | 1 | Unclassified | unclear | CRISPRn | Homo sapiens | Library not matched to a known family; verify in the source. |
| `CRISPR/Cas9-bEXOmiR (minus MMM sub-library)` | 1 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library; verify scope in the source. |
| `CRISPR/Cas9-bEXOmiR (MMM sub-library)` | 1 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library; verify scope in the source. |
| `CRISPRa (Heaton, 2017)` | 1 | Study-specific | partial/custom | CRISPRa | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRa (Metzakopian, 2019)` | 1 | Study-specific | partial/custom | CRISPRa | Mus musculus | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRa (Weissman, 2014)` | 3 | Weissman v1 (Gilbert 2014) | genome-wide | CRISPRa | Homo sapiens | Weissman lab first-generation genome-wide CRISPRi/a library (Gilbert et al. 2014). |
| `CRISPRa sgRNA-eBAR library (Zhu, 2021)` | 1 | Study-specific | partial/custom | CRISPRa | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRa targeted BC risk gene library (Rosenbluh, 2023)` | 20 | Focused/targeted | targeted | CRISPRa | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRa targeted library (Chen, 2025)` | 2 | Focused/targeted | targeted | CRISPRa | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRa Targeted Library (Weissman, 2017)` | 2 | Focused/targeted | targeted | CRISPRa | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRa targeted library based on Caprano sgRNAs (Zhao, 2024)` | 1 | Focused/targeted | targeted | CRISPRa | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRa-v2 (activation)` | 1 | Weissman v2 (Horlbeck 2016) | genome-wide | CRISPRa | Homo sapiens | Weissman lab genome-wide CRISPRi/CRISPRa v2 library (Horlbeck et al. 2016). |
| `CRISPRi (Weissman, 2014)` | 4 | Weissman v1 (Gilbert 2014) | genome-wide | CRISPRi | Homo sapiens | Weissman lab first-generation genome-wide CRISPRi/a library (Gilbert et al. 2014). |
| `CRISPRi targeted BC risk gene library (Rosenbluh, 2023)` | 17 | Focused/targeted | targeted | CRISPRi | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRi targeted library (Chen, 2025)` | 2 | Focused/targeted | targeted | CRISPRi | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRi Targeted Library (Weissman, 2017)` | 7 | Focused/targeted | targeted | CRISPRi | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRi Targeted Transcription Factor Library (Kampmann, 2022)` | 3 | Focused/targeted | targeted | CRISPRi | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRi-v2 (inhibition)` | 5 | Weissman v2 (Horlbeck 2016) | genome-wide | CRISPRi | Homo sapiens | Weissman lab genome-wide CRISPRi/CRISPRa v2 library (Horlbeck et al. 2016). |
| `CRISPRn  Targeted 1905 Interferon Stimulated Genes (ISGs) (Emerman, 2018)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn (Bassik, 2016)` | 2 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Cong, 2019)` | 2 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (CP1560) (Wilen, 2020)` | 1 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Hao, 2021)` | 1 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Helliwell, 2018)` | 6 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Hoffman and Nyfeler, 2016)` | 4 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Hundley, 2021)` | 36 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Kirkland, 2021)` | 4 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Liu and Brown, 2019)` | 2 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Liu, 2021)` | 2 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Martin, 2017)` | 3 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Perrimon, 2018)` | 1 | Study-specific | partial/custom | CRISPRn | Drosophila melanogaster | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Settleman, 2019)` | 2 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Spaan, 2018)` | 3 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Steinmetz, 2022)` | 1 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Zavolan, 2017)` | 6 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn (Zhong, 2021)` | 1 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn Druggable Genome Library (Metzakopian, 2023)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn focused 833 genes (Sherman, 2022)` | 5 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn library in CRISPR-StAR vector (Elling, 2024)` | 2 | Study-specific | partial/custom | CRISPRn | Mus musculus | Study-specific library named after the publication; verify scope in the source. |
| `CRISPRn Metabolically Focused Library (Wood, 2019)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn Minipool (Murphy, 2017)` | 8 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn NF-kB pathway (Steinmetz, 2022)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn Nuclear Factor Targeted Library based on Brie sgRNAs` | 1 | Brie-derived | targeted | CRISPRn | Mus musculus | Targeted subset built from Brie guides. |
| `CRISPRn phosphatase domain library (Vakoc, 2022)` | 12 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn Senescence Targeted Library (Wang, 2019)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn subpool library (CP1564) (Wilen, 2020)` | 7 | Focused/targeted | targeted | CRISPRn | Chlorocebus sabaeus | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn targeted BC risk gene library (Rosenbluh, 2023)` | 20 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn Targeted Chromatin Regulator Library (Bernstein, 2021)` | 2 | Focused/targeted | targeted | CRISPRn | Mus musculus, Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn targeted epigenetic regulator library (Wöhrle, 2019)` | 10 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn Targeted library (Berger, 2021)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn targeted library (Bonifacino, 2019)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn Targeted Library (Elledge, 2018)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn Targeted Library (Flynn, 2021)` | 14 | Focused/targeted | targeted | CRISPRn | Chlorocebus sabaeus | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn targeted library (Ginsburg, 2021)` | 9 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn targeted library (Hacohen, 2020)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn Targeted Library (Haining, 2017)` | 4 | Focused/targeted | targeted | CRISPRn | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn targeted library (Lehner, 2020)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn targeted library (Marson, 2019)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn targeted library (Wyss-Coray, 2020)` | 1 | Focused/targeted | targeted | CRISPRn | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn targeted library of gene enriched in cSCC tumor subpopulations (Khavari, 2020)` | 5 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn targeted mouse library (Liu, 2020)` | 36 | Focused/targeted | targeted | CRISPRn | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn Targeted Sub-libraries (Perrimon, 2018)` | 2 | Focused/targeted | targeted | CRISPRn | Drosophila melanogaster | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn Targeted Transcription Factor Domain Library (Vakoc, 2018)` | 19 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn Transcription Factor Targeted Library (Li, 2019)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn UPS targeted library` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn UPS targeted library (Bonifacino, 2019)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn UPS targeted library (Thoma, 2020)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn UPS targeted library (Weiss, 2022)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRISPRn ZRSR2 splicing target library (Abdel-Wahab, 2021)` | 3 | Focused/targeted | targeted | CRISPRn | Mus musculus, Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRL2 BC box adaptor CRISPRn library (Elledge, 2018)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRL2/5 adaptor targeted CRISPRn library (Elledge, 2018)` | 17 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `CRL4 DCAF adaptor CRISPRn library (Elledge, 2018)` | 5 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `DDR targeted library (Elledge, 2019)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Druggable Cancer Targets (DCT v1.0)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Edit-R crRNA Cell Cycle Regulation library` | 1 | Dharmacon Edit-R | targeted | CRISPRn | Homo sapiens | Arrayed synthetic crRNA targeted library. |
| `Edit-R Human Whole Genome crRNA Library` | 2 | Dharmacon Edit-R | genome-wide | CRISPRn | Homo sapiens | Arrayed synthetic crRNA genome-wide library (Dharmacon Edit-R). |
| `Epi-Drug Library` | 5 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library; verify scope in the source. |
| `EpiC library` | 1 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library; verify scope in the source. |
| `Epigenetic targeted CRISPRi library (Chen, 2023)` | 1 | Focused/targeted | targeted | CRISPRi | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Extended Knockout Library (EKO)` | 22 | EKO | genome-wide | CRISPRn | Homo sapiens | Extended Knockout library covering genes plus alternative exons and unannotated ORFs (Bertomeu et al. 2018). |
| `Focused Ras Synthetic Lethal Human CRISPR Knockout Library` | 15 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Gattinara (human)` | 1 | Gattinara (Broad) | genome-wide | CRISPRn | Homo sapiens | Compact human genome-wide CRISPRn library (2 guides per gene). |
| `GECKO` | 30 | GeCKO (Zhang lab) | genome-wide | CRISPRn | Homo sapiens | Human genome-wide CRISPRn library (GeCKO v1/v2; Shalem 2014, Sanjana 2014). |
| `GECKO v2` | 239 | GeCKO (Zhang lab) | genome-wide | CRISPRn | Homo sapiens, Chlorocebus sabaeus, Mus musculus | Human genome-wide CRISPRn library (GeCKO v1/v2; Shalem 2014, Sanjana 2014). |
| `GECKO v2 (mouse)` | 21 | GeCKO v2 (Zhang lab) | genome-wide | CRISPRn | Mus musculus, Homo sapiens | Mouse genome-wide CRISPRn library (GeCKO v2; Sanjana et al. 2014). |
| `H1 CRISPRi (Horlbeck, 2016)` | 5 | Weissman v2 (Horlbeck 2016) | genome-wide | CRISPRi | Homo sapiens | Weissman lab genome-wide CRISPRi/CRISPRa v2 library (Horlbeck et al. 2016). |
| `Heidelberg (HD) CRISPR library` | 2 | Heidelberg HD | genome-wide | CRISPRn | Homo sapiens | Heidelberg (HD) human genome-wide CRISPRn library (Henkel et al. 2020). |
| `HIVDEP` | 5 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library; verify scope in the source. |
| `Human Activity-optimized genome-wide library` | 21 | Sabatini/Lander activity-optimized | genome-wide | CRISPRn | Homo sapiens | Activity-optimized genome-wide CRISPRn library (Wang et al. 2015/2017). |
| `Human CRISPR Activation Pooled Library (Calabrese)` | 16 | Calabrese (Broad) | genome-wide | CRISPRa | Homo sapiens | Human genome-wide CRISPRa library (Sanson et al. 2018). |
| `Human CRISPR Deletion Library - Drug targets, kinases, phosphatases and Human CRISPR Deletion Library - Trafficking, mitochondrial, motility` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Human CRISPR Knockout Pooled Libraries (Enriched Sub-pools)` | 6 | Sabatini/Lander (Wang 2014) | partial/custom | CRISPRn | Homo sapiens | Sub-pools from the first Wang et al. 2014 human CRISPRn library. |
| `Human CRISPR Knockout Pooled Library (H3)` | 3 | Liu (H1/H2/H3) | genome-wide | CRISPRn | Homo sapiens | Human genome-wide CRISPRn library (H3) from the X. Shirley Liu lab. |
| `Human CRISPR Library v.1.1` | 325 | Yusa / Sanger | genome-wide | CRISPRn | Homo sapiens | Wellcome Sanger (Yusa lab) genome-wide CRISPRn library (Koike-Yusa 2014; Tzelepis 2016). |
| `Human CRISPR Metabolic Gene Knockout Library` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Human CRISPRi sgRNA library Dolcetto` | 3 | Dolcetto (Broad) | genome-wide | CRISPRi | Homo sapiens | Human genome-wide CRISPRi library (Sanson et al. 2018). |
| `Human genome-wide library v1` | 1 | Other genome-wide | genome-wide | CRISPRn | Homo sapiens | Genome-wide CRISPRn library (compact or first-generation design). |
| `Human Improved Genome-wide Knockout CRISPR Library` | 45 | Yusa / Sanger | genome-wide | CRISPRn | Homo sapiens | Wellcome Sanger (Yusa lab) genome-wide CRISPRn library (Koike-Yusa 2014; Tzelepis 2016). |
| `Human Kinase Domain-Focused CRISPR Knockout Library` | 27 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Human Lentiviral sgRNA Library - Kinases` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Human Metabolic Enzyme sgRNA library (Qiu, 2022)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Human SAM library in lenti-puro backbone` | 2 | SAM (Zhang lab) | genome-wide | CRISPRa | Homo sapiens | Genome-wide CRISPRa Synergistic Activation Mediator library (Konermann et al. 2015). |
| `Human SAM library in lentiSAMv2 backbone` | 3 | SAM (Zhang lab) | genome-wide | CRISPRa | Homo sapiens | Genome-wide CRISPRa Synergistic Activation Mediator library (Konermann et al. 2015). |
| `Human Two Plasmid Activity-Optimized CRISPR Knockout Library` | 1 | Sabatini/Lander activity-optimized | genome-wide | CRISPRn | Homo sapiens | Activity-optimized genome-wide CRISPRn library (Wang et al. 2015/2017). |
| `ICR (Immune Checkpoint Inhibitor) Targeted Library` | 8 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Kinase and Cell Cycle Subpools from Human CRISPR Knockout Pooled Libraries` | 1 | Sabatini/Lander (Wang 2014) | partial/custom | CRISPRn | Homo sapiens | Sub-pools from the first Wang et al. 2014 human CRISPRn library. |
| `Lipid metabolic targeted CRISPRn library (Jin,2021)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Liu Human CRISPR Knockout Library (CRISPRn H1 H2, H1/H2)` | 19 | Liu (H1/H2/H3) | genome-wide | CRISPRn | Homo sapiens | Human genome-wide CRISPRn library from the X. Shirley Liu lab. |
| `LX-miR gRNA library` | 1 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library; verify scope in the source. |
| `Mini-human` | 1 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library; verify scope in the source. |
| `MinLibCas9` | 1 | Other genome-wide | genome-wide | CRISPRn | Homo sapiens | Genome-wide CRISPRn library (compact or first-generation design). |
| `MitoCarta2.0` | 1 | Focused/targeted | targeted | CRISPRn | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `Modified Calabrese Library (414 interferon-stimulated genes) (Danziger, 2021)` | 4 | Calabrese-derived | targeted | CRISPRa | Homo sapiens | Targeted subset of the Calabrese CRISPRa library (gene set named in the title). |
| `mouse CRISPRn library (Yusa, 2013)` | 1 | Yusa / Sanger | genome-wide | CRISPRn | Mus musculus | Wellcome Sanger (Yusa lab) genome-wide CRISPRn library (Koike-Yusa 2014; Tzelepis 2016). |
| `Mouse druggable genome (Elledge, 2021)` | 12 | Focused/targeted | targeted | CRISPRn | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `Mouse improved genome-wide library v2` | 4 | Yusa / Sanger | genome-wide | CRISPRn | Mus musculus | Wellcome Sanger (Yusa lab) genome-wide CRISPRn library (Koike-Yusa 2014; Tzelepis 2016). |
| `Mouse Tumor Suppressor Gene (TSG) targeted library (Elledge, 2021)` | 17 | Focused/targeted | targeted | CRISPRn | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `Mouse Two Plasmid Activity-Optimized CRISPR Knockout Library` | 4 | Sabatini/Lander activity-optimized | genome-wide | CRISPRn | Mus musculus | Activity-optimized genome-wide CRISPRn library (Wang et al. 2015/2017). |
| `mTKO (mouseTKO)` | 32 | Toronto KnockOut (Moffat lab) | genome-wide | CRISPRn | Mus musculus | Mouse genome-wide TKO library. |
| `Murine lentiviral gRNA library (version 1)` | 3 | Yusa / Sanger | genome-wide | CRISPRn | Mus musculus | Wellcome Sanger (Yusa lab) genome-wide CRISPRn library (Koike-Yusa 2014; Tzelepis 2016). |
| `Murine Transcriptional Regulator Library (Pu, 2021)` | 1 | Focused/targeted | targeted | CRISPRn | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `MusCK` | 2 | MusCK | partial/custom | CRISPRn | Mus musculus | Mouse CRISPR knockout library; verify gene coverage in the source. |
| `MusCK 2.0` | 3 | MusCK | partial/custom | CRISPRn | Mus musculus | Mouse CRISPR knockout library; verify gene coverage in the source. |
| `Neurodevelopmental Disorder (NDD) candidate targeted library (Pasca, 2023)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `RAS Interactome (Adhikari, 2018)` | 3 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Resident mitochondrial targeted library (Elledge and Harper, 2019)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Root library (Gu, 2023)` | 2 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library; verify scope in the source. |
| `RxG library` | 6 | Study-specific | partial/custom | CRISPRn | Homo sapiens | Study-specific library; verify scope in the source. |
| `S. cerevisiae CRISPRi targeted library (Patil, 2021)` | 3 | Focused/targeted | targeted | CRISPRi | Saccharomyces cerevisiae | Targeted library covering a defined gene set (named in the library title). |
| `S. cerevisiae CRISPRn library (Liu, 2022)` | 10 | Study-specific | partial/custom | CRISPRn | Saccharomyces cerevisiae | Study-specific library named after the publication; verify scope in the source. |
| `SAM v1 (Puromycin)` | 2 | SAM (Zhang lab) | genome-wide | CRISPRa | Homo sapiens | Genome-wide CRISPRa Synergistic Activation Mediator library (Konermann et al. 2015). |
| `SAM v1 (Zeomycin)` | 12 | SAM (Zhang lab) | genome-wide | CRISPRa | Homo sapiens | Genome-wide CRISPRa Synergistic Activation Mediator library (Konermann et al. 2015). |
| `SARS-CoV-2 interactome targeted library` | 5 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Superti-Furga Lab Human SLC KO Library` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Surfaceome CRISPRa library (Song, 2022)` | 2 | Focused/targeted | targeted | CRISPRa | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Surfaceome Library` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Targeted cancer-relevant druggable genes (CP1080, M-AB34) (Kaelin, 2021)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Targeted CRISPRn library (Schwank, 2022)` | 1 | Focused/targeted | targeted | CRISPRn | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `Targeted CRISPRn library in CRISPR-StAR vector (Elling, 2024)` | 3 | Focused/targeted | targeted | CRISPRn | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `Targeted epigenetic regulator library  (Wong, 2019)` | 2 | Focused/targeted | targeted | CRISPRn | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `Targeted lipid-related genes library (Rohatgi, 2019)` | 2 | Focused/targeted | targeted | CRISPRn | Mus musculus | Targeted library covering a defined gene set (named in the library title). |
| `Targeted Posttranslational Regulator CRISPRn library (Li , 2023)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Targeted Resistant Cervical Cancer Cell Library (Hu, 2021)` | 3 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Targeted subset of TKOv3 (Myers, 2024)` | 19 | Toronto KnockOut-derived | targeted | CRISPRn | Homo sapiens | Targeted subset of TKOv3. |
| `Teichmann Retroviral Mouse Genome-wide CRISPR Knockout Library` | 1 | Teichmann | genome-wide | CRISPRn | Mus musculus | Retroviral mouse genome-wide CRISPRn library for primary immune cells (Henriksson et al. 2019). |
| `TKO (Toronto Knockout) v1` | 41 | Toronto KnockOut (Moffat lab) | genome-wide | CRISPRn | Homo sapiens | Human genome-wide CRISPRn library (TKO v1/v2/v3; Hart et al. 2015, 2017). |
| `TKOv2` | 12 | Toronto KnockOut (Moffat lab) | genome-wide | CRISPRn | Homo sapiens | Human genome-wide CRISPRn library (TKO v1/v2/v3; Hart et al. 2015, 2017). |
| `Toronto Knockout version 3 (TKOv3)` | 93 | Toronto KnockOut (Moffat lab) | genome-wide | CRISPRn | Homo sapiens, Chlorocebus sabaeus | Human genome-wide CRISPRn library (TKO v1/v2/v3; Hart et al. 2015, 2017). |
| `TSAG library` | 1 | Study-specific | partial/custom | CRISPRn | Mus musculus | Study-specific library; verify scope in the source. |
| `TSG targeted CRISPRn library (Elledge, 2017)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Tumor Suppressor Gene (TSG) targeted library (Elledge, 2022)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Tumor Suppressor Gene (TSG) targeted library (Schwank, 2020)` | 1 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Ub pathway targeted library (Harper and Elledge, 2019)` | 2 | Focused/targeted | targeted | CRISPRn | Homo sapiens | Targeted library covering a defined gene set (named in the library title). |
| `Weissman Human CRISPRi Titration Libraries` | 1 | Weissman | targeted | CRISPRi | Homo sapiens | CRISPRi titration library with mismatched guides for graded knockdown (Jost et al. 2020). |
| `Yeast Editing Library (Kruglyak, 2022)` | 11 | Non-mammalian or non-human/mouse | partial/custom | Cytosine Base Editing-Mediated Gene Perturbation | Saccharomyces cerevisiae | Library for yeast or green monkey cells. |
| `Yeast Inducible CRISPRi Library` | 1 | Study-specific | partial/custom | CRISPRi | Saccharomyces cerevisiae | Study-specific library named after the publication; verify scope in the source. |
