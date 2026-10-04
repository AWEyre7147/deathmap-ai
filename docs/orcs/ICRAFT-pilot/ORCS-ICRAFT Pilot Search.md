---
title: "ORCS–ICRAFT three-class pilot: availability comparison and search profiles"
created: 2026-10-04
status: pilot-development-results
tags: [deathmap-ai, orcs, icraft, pilot, search-profiles]
---

# ORCS–ICRAFT three-class pilot

Three class-level ORCS searches captured all PMID-resolved reference publications that were present in the supplied ORCS snapshot: 33 CRISPR publications, one scRNA-seq publication, and one clinical/genomics-cohort publication. These are publication-level discovery results, not evidence that ORCS supplies the corresponding count matrices, expression datasets, or patient data. The comparison separates supplemental reference rows, website-listed records, and files present in the supplied download inventory.

## Main comparison

“Publications” means distinct PubMed IDs, after splitting multi-PMID cells and performing the explicitly documented bibliographic resolution. “Rows linked to ORCS papers” means reference dataset/screen/cohort rows whose publication appears in ORCS; it does not mean experimentally equivalent ORCS screens.

| Classification | Reference condition | Reference units | Identified publications | Publications in ORCS | Reference units linked to those publications |
|---|---|---:|---:|---:|---:|
| CRISPR | Supplemental total, Table S1 | 558 screen rows | 90 | 33 | 194 screen rows |
| CRISPR | Website, all screen metadata | 544 screen rows | 89 | 33 | 193 screen rows |
| CRISPR | Supplied public-file inventory | 65 count-file bundles | 43 | 18 | 36 count-file bundles |
| scRNA-seq | Supplemental total, Table S2 | 83 dataset rows | 70 | 1 | 1 dataset row |
| scRNA-seq | Website, all scRNA records | 83 dataset rows | 70 | 1 | 1 dataset row |
| scRNA-seq | Supplied public-file inventory | 83 count/annotation pairs | 70 | 1 | 1 dataset pair |
| Clinical | Supplied Table S8, cBioPortal cohorts | 97 distinct study IDs | 71 linked PMIDs; 7 cohorts unresolved | 1 | 1 cohort |
| Clinical | Website, ICB RNA-seq cohorts | 18 cohorts | 15 | 0 | 0 |
| Clinical | Supplied public-file inventory, ICB RNA-seq | 18 expression/clinical-info pairs | 15 | 0 | 0 |

The CRISPR reference publications present in ORCS collectively have 152 ORCS screen records. The scRNA match has five ORCS screen records, and the clinical/genomics match has six. These counts must remain distinct from 194 ICRAFT screen rows, one scRNA dataset row, and one cohort.

All nine combinations and the underlying row-level joins are available in `evaluation/availability-and-coverage.csv`, `evaluation/reference-publications.csv`, and `evaluation/reference-datasets.csv`. Matching uses the native ORCS publication `SOURCE_ID` when `SOURCE_TYPE = pubmed`; unmatched identifiers are described as absent from this snapshot, not absent from all ORCS releases.

## Input interpretation and corrections

### Supplemental tables

- **Table S1, `mmc2`**: 558 actual CRISPR screen rows, `Table S1!A3:S560`; trailing formatted rows are not counted. Four in-house rows, `IH1`–`IH4`, have no PubMed ID, so no publication identity is invented for them.
- **Table S2, `mmc3`**: 83 dataset rows, `Sheet1!A3:E85`. The abbreviation glossary beginning below the dataset table is excluded.
- **Table S4, `mmc4`**: 54 selected integrative-analysis metadata records, `Table S6!A3:K56`. Despite the worksheet name, its title identifies it as Table S4; it is not an additional complete dataset denominator.
- **Table S8, `mmc8`**: a patient-level alteration table with cBioPortal `studyId` in `Table S13!C4`. Cohort counting groups populated study IDs; only cohort metadata is retained in the delivered package, not patient-level records.

The supplied `mmc8` is **not the ICB RNA-seq cohort list** shown on the website. It contains cBioPortal cancer cohorts and genotype information for an autoimmune-associated gene analysis. Consequently, the clinical supplemental, website, and inventory sets are not three nested availability tiers of one collection; treating them that way would give misleading counts.

All 97 supplemental cohort IDs were resolved to current cBioPortal study metadata. Ninety cohorts had linked PMIDs, yielding 71 distinct PMIDs after deduplication; seven had no linked PMID. Some studies, especially TCGA PanCancer Atlas cohorts, link to multiple papers, so the count is of cBioPortal-linked publications rather than one original publication per cohort.

The seven unresolved study-to-publication links are `all_phase2_target_2018_pub`, `aml_target_2018_pub`, `biliary_tract_summit_2022`, `mds_iwg_2022`, `nbl_target_2018_pub`, `rt_target_2018_pub`, and `wt_target_2018_pub`. They are retained as unresolved, not counted as confirmed ORCS absences. Current cBioPortal bibliography is used only for evaluation, never as a discovery input.

### Website-listed is not downloaded

The [ICRAFT website](https://icraft.pku-genomics.org/) provides separate CRISPR, single-cell, and immunotherapy-cohort resources. This comparison snapshots metadata through its read-only listing endpoints, rather than downloading or testing the experimental files.

The CRISPR screen list returned 544 records, while the separate count-file listing returned 80 bundles associated with 57 split/deduplicated PMIDs. That count-file listing labels 66 bundles as `PubliclyAvailable` and 14 as `Received`; the 66 public labels span 44 PMIDs. The main “website all” comparison uses the **complete screen-metadata list**, not the smaller count-file listing, because it is the closest counterpart to supplemental Table S1.

The supplied inventory contains 65 genuine CRISPR count bundles, not 66: `New Text Document.txt` is excluded. `CNT65`, associated with PMID `32984844`, is website-labelled public but missing from the inventory. The report therefore measures inventory-confirmed possession, not an exhaustive claim about everything publicly downloadable.

The scRNA inventory contains 83 count archives plus 83 annotation files, representing 83 dataset pairs, not 166 datasets. The clinical inventory contains 18 expression matrices plus 18 clinical-information files, representing 18 cohort pairs, not 36 cohorts. Presence in the filename inventory does not establish file integrity, complete archive contents, raw-data availability, license permission, or current download success.

### Bibliographic enrichment of scRNA references

The supplied scRNA table initially gives 65 distinct PMIDs and eight rows without a PMID. Five additional publication identities resolve those eight rows, producing 70 distinct PMID-linked publications; the mappings are retained separately from the source-reported reference values.

| Dataset/reference | Resolved PMID | Evidence |
|---|---|---|
| E-MTAB-8107, three cancer-specific rows | 32561858 | The [original Cell Research paper](https://www.nature.com/articles/s41422-020-0355-0) explicitly deposits E-MTAB-8107; its DOI matches the [PubMed record](https://pubmed.ncbi.nlm.nih.gov/32561858/). |
| GSE142744 | 32788668 | Its parent [GSE142745 SuperSeries](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE142745&targ=self&form=text&view=quick) links PMID 32788668; this is a parent-series bibliographic association, not a direct child-record citation. |
| GSE143423, two disease rows | 39311908 | Current [GEO metadata](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE143423&targ=self&form=text&view=quick) links this PMID, replacing the supplemental table's preprint-only citation for evaluation. |
| GSE141299 | 34655292 | The [GEO record](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE141299) explicitly links this PMID. |
| GSE154600 | 32747365 | Current [GEO text metadata](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE154600&targ=self&form=text&view=quick) links this PMID. |

Some cached GEO HTML pages lacked newer citations that were present in current text metadata. The package keeps the enrichment URLs and original reference fields, so this update can be audited rather than silently rewriting the supplemental table.

### Selected CRISPR metadata crosswalk

Forty-seven of the 54 Table S4 IDs match Table S1 exactly. Seven do not: `ICR201`, `ICR203`, `ICR204`, `ICR206`, `ICR209`, `ICR210`, and `ICR212`. Their names describe Moffat 2020 co-culture entries, but no automatic publication or screen equivalence is assigned from cell-line names; the unresolved ID crosswalk is delivered as `evaluation/s4-crosswalk.csv`.

## Three search profiles

Each profile is independently runnable against the ORCS snapshot. Discovery never loads an ICRAFT PMID list, accession list, selected cell-line list, author list, or selected library list; the supplementary references are used only afterward to compare outputs.

### CRISPR biological-class search

**Profile:** `orcs-crispr-biological-classes-pilot-v01`.

Common gates retain human/mouse records with an ORCS CRISPR knockout, interference, activation, or supported cytosine-base-editing library label. A screen is a candidate if any of these biological branches matches:

- **Cancer derivation**: its saved Cellosaurus category is `Cancer cell line`.
- **Unannotated cancer-model fallback**: only when the Cellosaurus category is missing, its ORCS `CELL_TYPE` names a cancer class.
- **Immune lineage**: its ORCS `CELL_TYPE` names an immune class, such as T cells, macrophages, or microglia.
- **Organoid/assembloid**: its ORCS `CELL_TYPE` indicates a three-dimensional organoid or assembloid model, including normal organoids for this broad pilot.

Phenotype, enzyme spelling, pooled/arrayed/in-vivo format, library name, and immune pressure do not exclude candidates. This deliberate broadening retains baseline growth, infection-related, marker-sorting, immune-edited, and normal-organoid entries that occur in the full ICRAFT reference set. It is therefore broader than the earlier tumor-cell fitness v02 profile and the six-rule immune-related screen proposal.

`FULL_SIZE` is retained as descriptive source metadata. It is not used to assert genome-wide library coverage automatically: library scope needs its own annotation, and a source's number of scored entries is not inherently its number of guides or complete targeted genes.

The biological rules avoid memorizing particular model names but still produce a broad set: 1,830 direct candidates across 328 publications, increasing to 1,886 screen records after adding 56 companion screens. This is not a selective immune-oncology classifier and does not establish the relevance of all 328 papers.

### Single-cell publication-candidate search

**Profile:** `orcs-single-cell-publication-candidates-pilot-v01`.

The same common CRISPR/species gates apply. The profile searches ORCS publication titles/abstracts and screen notes/rationales for general single-cell transcriptomic terms, including `scRNA-seq`, single-cell RNA/transcriptomic descriptions, Perturb-seq, Perturb-CITE-seq, and CROP-seq.

It returns 16 publication candidates linked to 60 ORCS screen records. All 60 were selected through a publication-field mention in this snapshot; they are **not 60 verified single-cell perturbation experiments**. A paper may combine conventional CRISPR screens with separate observational single-cell data.

The sole scRNA reference publication in ORCS is Ji et al., PMID `32579974`, which combines single-cell RNA sequencing, spatial transcriptomics, imaging, and in-vivo CRISPR screens ([PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/32579974/)). The search captures this paper and its five ORCS screen records; the reference table's one linked scRNA dataset remains a separate entity.

### Clinical-omics publication-candidate search

**Profile:** `orcs-clinical-omics-publication-candidates-pilot-v01`.

The same common gates apply. Publication title/abstract text must mention patients or a cohort **and** a general molecular-profiling assay, such as RNA-seq, transcriptome sequencing/profiling, whole-exome sequencing, whole-genome sequencing, genomic profiling, molecular profiling, or genotyping.

ICB/immunotherapy mentions are tags, not necessary inclusion criteria, because the supplied clinical supplemental table is broader than ICB RNA-seq. The profile returns 17 candidate publications linked to 57 ORCS screen records; it does not infer trial participation, pretreatment sampling, or patient response metadata from a method mention.

The one cBioPortal supplemental publication in ORCS is Reddy et al., PMID `28985567`, linked by [cBioPortal study `dlbcl_duke_2017`](https://www.cbioportal.org/api/studies/dlbcl_duke_2017). Its paper combines whole-exome/transcriptome analysis of a 1,001-patient DLBCL cohort with a CRISPR cell-line screen ([PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/28985567/)). The search captures its six ORCS screens; those are cell-line experiments, not six clinical cohorts.

No PMID from the website/inventory's 15-publication ICB cohort set appears in the supplied ORCS snapshot. The valid result for that particular clinical set is zero, even though the broader clinical-omics search produces other candidates.

## Execution results

| Profile | Total candidate publications | Directly selected ORCS screen rows | Companion rows | Expanded ORCS screen rows | Supplemental-reference publications captured |
|---|---:|---:|---:|---:|---:|
| CRISPR biological classes | 328 | 1,830 | 56 | 1,886 | 33 of the 33 PMID-linked publications found in ORCS |
| Single-cell publication candidates | 16 | 60 | 0 | 60 | 1 of the 1 PMID-linked publication found in ORCS |
| Clinical-omics publication candidates | 17 | 57 | 0 | 57 | 1 of the 1 PMID-linked publication found in ORCS |

For the CRISPR inventory subset, the first profile captures all 18 reference publications present in ORCS, associated with 36 inventory count bundles. For scRNA, the one reference publication is captured in all three conditions because the dataset set is the same after reconciliation. For ICB clinical website/inventory conditions, there is no ORCS reference publication to capture.

Results across the three searches overlap and must not be added together as independent publications or screens. Within each run, screen IDs are deduplicated and publication identity uses `SOURCE_TYPE` plus `SOURCE_ID`.

## Implementation and evidence contract

The JSON profiles use the explicit contract `deathmap-orcs-pilot-profile/1.0`; they are not asserted to work unchanged in the current v02 parser. `run_orcs_profile.py` is a working standard-library reference implementation, and `README.md` gives the commands and adaptation requirements.

- **Rule combination**: common gates are AND; candidate branches are OR.
- **Reference join**: Cellosaurus annotations join on exact native `CELL_LINE`; publication metadata joins on `SOURCE_TYPE` plus `SOURCE_ID`.
- **Null handling**: missing fields are empty, never positive evidence; a missing abstract produces no publication-text match.
- **Comparison handling**: exact multivalue fields split on `|` and trim whitespace; regex rules are case-insensitive.
- **Companion expansion**: publication companions are explicitly labelled and have no direct matched-rule IDs. Companion inclusion does not assert that all experiments have the selected assay or immune context.
- **Provenance**: native source values and matched rule IDs are retained. Derived biological/assay labels are candidates; dataset accession, availability, and experimental equivalence remain unverified.

The saved annotation projection permits reproducing the reported category branch. Using an updated annotation file can change CRISPR counts; retaining source annotations is normal reference enrichment, whereas embedding a hand-picked list of positive model names in the profile would violate the intended filter strategy.

Nine automated acceptance tests passed, covering cancer fallback, non-knockout inclusion, non-cancer reference handling, immune/organoid branches, companion labelling, source-type join collisions, assay conditions, multivalues/nulls, and forbidden identifier fields in selection. Re-execution using the packaged annotation projection reproduced the reported run counts.

## Interpretation and limitations

This is a **development pilot**, not a held-out validation or a recall estimate. The reference tables were visible while the search strategy was chosen; category-based rules prevent an explicit cell-line allowlist but do not eliminate development-set bias. The earlier PS8 wording prohibiting use of ICRAFT in query construction needs an explicit pilot exception in a future spec revision; it was not silently edited here.

The maximum established publication overlap is constrained by the cached ORCS snapshot. Most supplied scRNA and ICB cohort papers are not present as ORCS records, so no filter over this snapshot can retrieve them. The [ORCS resource](https://orcs.thebiogrid.org/) catalogs CRISPR screens; the [ICRAFT resource](https://icraft.pku-genomics.org/) also includes expression and clinical resources, so the three source categories are not interchangeable.

Seven clinical cohorts and four in-house CRISPR rows remain without a resolved publication identity. The snapshot-presence result does not rule out matches under alternative publication versions, DOI-only preprints, or unresolved identifiers; those would require a separate bibliographic equivalence step.

No experimental matrices or patient-level records were downloaded or tested in this task. The downloaded-file report is availability evidence at the inventory level only, and the public/received labels are preserved as source metadata rather than promoted into access guarantees.

An appropriate repository summary is: “In an ORCS-only development pilot, general biological-class filters located all 33 PMID-linked ICRAFT CRISPR publications represented in the cached ORCS snapshot, associated with 194 supplemental screen rows. Separate publication-method searches located the one represented scRNA reference paper and one represented cBioPortal cohort paper; no website ICB cohort paper was represented. These are publication-discovery and scope-demonstration results, not independent recall or dataset-access claims.”
