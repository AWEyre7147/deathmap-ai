# EGA

Entity level: repository native record; experimental granularity not assumed. Field status: observed on saved responses; detailed semantics are not guaranteed by the API help. Search/detail variability is retained. No external source was visited.

Coverage: 2 response objects. Presence is across both endpoint shapes; types count occurrences, not unique records. Container examples are represented by their child rows. Full examples and source paths are in field_inventory.json. Native values are neither terminology-normalized nor interpreted scientifically.

| Native path | Types | Present / absent objects | Example | Meaning | Mapping / caution |
|---|---|---|---|---|---|
| `accession` | str | 2 / 0 | EGAS00001005528 | Native detail identifier | accession_reported after identity validation |
| `additional` | dict | 2 / 0 | (container or null) | Repository-dependent additional metadata object | native evidence; recognized child mappings below |
| `additional.additional_accession` | list | 2 / 0 | (container or null) | Source-reported additional.additional_accession; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.category` | list | 2 / 0 | (container or null) | Source-reported additional.category; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.category[]` | str | 2 / 0 | restricted | Source-reported additional.category; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.dataset_title` | list | 2 / 0 | (container or null) | Source-reported additional.dataset_title; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.dataset_title[]` | str | 2 / 0 | iPSC and iNeuron RNAseq, chip-seq and single cell CRISPR activation | Source-reported additional.dataset_title; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.description` | list | 2 / 0 | (container or null) | Source-reported additional.description; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.description[]` | str | 2 / 0 | EGA study EGAS00001005528 | Source-reported additional.description; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.description_synonyms` | list | 2 / 0 | (container or null) | Source-reported additional.description_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.description_synonyms[]` | str | 2 / 0 | d230, Materials, PhrB photolyase activity, determination, HSN1E, Gene, dTAFII250, photoreactivating  | Source-reported additional.description_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.full_dataset_link` | list | 2 / 0 | (container or null) | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.full_dataset_link[]` | str | 2 / 0 | https://ega-archive.org/studies/EGAS00001005528 | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.host` | list | 2 / 0 | (container or null) | Source-reported additional.host; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.host[]` | str | 2 / 0 | EGA | Source-reported additional.host; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.name_synonyms` | list | 1 / 1 | (container or null) | Source-reported additional.name_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.name_synonyms[]` | str | 1 / 1 | lod, Colorectal Tumors, Carcinomas, Colorectal Neoplasm, Carcinoma, DmelCG2684, Colorectal Cancer, G | Source-reported additional.name_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.omics_type` | list | 2 / 0 | (container or null) | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.omics_type[]` | str | 2 / 0 | Genomics | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pubmed_abstract` | list | 1 / 1 | (container or null) | Publication abstract, distinct from dataset description | native evidence only; never dataset description |
| `additional.pubmed_abstract[]` | str | 1 / 1 | <h4>Objective</h4>Sporadic early-onset colorectal cancer (EOCRC) has bad prognosis, yet is poorly re | Publication abstract, distinct from dataset description | native evidence only; never dataset description |
| `additional.pubmed_abstract_synonyms` | list | 1 / 1 | (container or null) | Source-reported additional.pubmed_abstract_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pubmed_abstract_synonyms[]` | str | 1 / 1 | Dm DWnt3/5, CRISPR Locus, Colorectal Neoplasm, Similarity, SMAD family member 4, DWnt-5, rasGAP, DWn | Source-reported additional.pubmed_abstract_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pubmed_authors` | list | 1 / 1 | (container or null) | Reported associated publication authors | publications.author_list_reported only when unambiguous |
| `additional.pubmed_authors[]` | str | 1 / 1 | Yan Helen H N HHN, Siu Hoi Cheong HC, Ho Siu Lun SL, Yue Sarah S K SSK, Gao Yang Y, Tsui Wai Yin WY, | Reported associated publication authors | publications.author_list_reported only when unambiguous |
| `additional.pubmed_title` | list | 1 / 1 | (container or null) | Reported associated publication title | publications.title_original only when association unambiguous |
| `additional.pubmed_title[]` | str | 1 / 1 | Organoid cultures of early-onset colorectal cancers reveal distinct and rare genetic profiles. | Reported associated publication title | publications.title_original only when association unambiguous |
| `additional.pubmed_title_synonyms` | list | 1 / 1 | (container or null) | Source-reported additional.pubmed_title_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pubmed_title_synonyms[]` | str | 1 / 1 | lod, Colorectal Tumors, Carcinomas, Colorectal Neoplasm, Carcinoma, DmelCG2684, Colorectal Cancer, G | Source-reported additional.pubmed_title_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.repository` | list | 2 / 0 | (container or null) | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.repository[]` | str | 2 / 0 | EGA | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.study_type` | list | 2 / 0 | (container or null) | Source study-type label | datasets.experiment_type_reported |
| `additional.study_type[]` | str | 2 / 0 | Transcriptome Analysis | Source study-type label | datasets.experiment_type_reported |
| `cross_references` | dict | 2 / 0 | (container or null) | Source-reported external associations; not verified externally | native evidence; named publication IDs only mapped |
| `cross_references.EGA` | list | 2 / 0 | (container or null) | Source-reported cross_references.EGA; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.EGA[]` | str | 2 / 0 | EGAD00001010050 | Source-reported cross_references.EGA; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.TAXONOMY` | list | 2 / 0 | (container or null) | Source-reported cross_references.TAXONOMY; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.TAXONOMY[]` | str | 2 / 0 | 9606 | Source-reported cross_references.TAXONOMY; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.pubmed` | list | 1 / 1 | (container or null) | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.pubmed[]` | str | 1 / 1 | 32217638 | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `database` | str | 2 / 0 | EGA | Native detail repository label | identity validation; conflicts retained |
| `dates` | dict | 2 / 0 | (container or null) | Source dates; not our retrieval timestamp | native evidence only |
| `dates.updated` | str | 2 / 0 | 2023-03-03 08:34:16 | Source-reported dates.updated; detailed semantics not independently established | native evidence only; no structured target assignment |
| `description` | str | 2 / 0 | Single cell CRISPR activitaion analysis with 96 genes with the aim to build a quantative CRISPR acti | Resource record description; not an adjudicated experiment | datasets.description_reported |
| `file_versions` | list | 2 / 0 | (container or null) | Source file/version metadata; no files retrieved | native evidence only |
| `is_claimable` | bool | 2 / 0 | False | Source claimability flag; not accessibility | native evidence only |
| `name` | str | 2 / 0 | CRISPR single cell activation | Resource record name | datasets.title_original |
| `scores` | NoneType | 2 / 0 | (container or null) | Source index scores; not scientific qualification | native evidence only |
