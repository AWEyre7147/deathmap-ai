# biostudies-arrayexpress

Entity level: repository native record; experimental granularity not assumed. Field status: observed on saved responses; detailed semantics are not guaranteed by the API help. Search/detail variability is retained. No external source was visited.

Coverage: 139 response objects. Presence is across both endpoint shapes; types count occurrences, not unique records. Container examples are represented by their child rows. Full examples and source paths are in field_inventory.json. Native values are neither terminology-normalized nor interpreted scientifically.

| Native path | Types | Present / absent objects | Example | Meaning | Mapping / caution |
|---|---|---|---|---|---|
| `accession` | str | 17 / 122 | E-MTAB-14519 | Native detail identifier | accession_reported after identity validation |
| `additional` | dict | 17 / 122 | (container or null) | Repository-dependent additional metadata object | native evidence; recognized child mappings below |
| `additional.additional_accession` | list | 17 / 122 | (container or null) | Source-reported additional.additional_accession; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.additional_accession[]` | str | 4 / 135 | E-MTAB-15056 | Source-reported additional.additional_accession; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.data_protocol` | list | 11 / 128 | (container or null) | Reported data protocol | datasets._native_protocols and evidence; no NLP extraction |
| `additional.data_protocol[]` | str | 11 / 128 | Data Transformation - Processed data file is a raw counts table as described in the \\\\"high throug | Reported data protocol | datasets._native_protocols and evidence; no NLP extraction |
| `additional.description` | list | 17 / 122 | (container or null) | Source-reported additional.description; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.description[]` | str | 17 / 122 | This project explores the effects of Cdc42 gene-knock in effector cytotoxic T lymphocytes (CTLs). Ef | Source-reported additional.description; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.figure_sub` | list | 17 / 122 | (container or null) | Source-reported additional.figure_sub; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.figure_sub[]` | str | 17 / 122 | Organization | Source-reported additional.figure_sub; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.full_dataset_link` | list | 17 / 122 | (container or null) | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.full_dataset_link[]` | str | 17 / 122 | https://www.ebi.ac.uk/biostudies/studies/E-MTAB-14519 | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.instrument_platform` | list | 12 / 127 | (container or null) | Source-reported additional.instrument_platform; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.instrument_platform[]` | str | 12 / 127 | Illumina NovaSeq 6000 | Source-reported additional.instrument_platform; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.omics_type` | list | 17 / 122 | (container or null) | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.omics_type[]` | str | 17 / 122 | Metabolomics | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.organism` | list | 17 / 122 | (container or null) | Reported organism label | datasets.organism_reported |
| `additional.organism[]` | str | 17 / 122 | Mus musculus | Reported organism label | datasets.organism_reported |
| `additional.pubmed_abstract` | list | 5 / 134 | (container or null) | Publication abstract, distinct from dataset description | native evidence only; never dataset description |
| `additional.pubmed_abstract[]` | str | 5 / 134 | <h4>SUMMARY</h4>  Natural killer (NK) cells are emerging as a promising therapeutic option in cancer | Publication abstract, distinct from dataset description | native evidence only; never dataset description |
| `additional.pubmed_authors` | list | 17 / 122 | (container or null) | Reported associated publication authors | publications.author_list_reported only when unambiguous |
| `additional.pubmed_authors[]` | str | 17 / 122 | Claire Ma | Reported associated publication authors | publications.author_list_reported only when unambiguous |
| `additional.pubmed_title` | list | 6 / 133 | (container or null) | Reported associated publication title | publications.title_original only when association unambiguous |
| `additional.pubmed_title[]` | str | 6 / 133 | Single-cell functional genomics of natural killer cell evasion in blood cancers | Reported associated publication title | publications.title_original only when association unambiguous |
| `additional.repository` | list | 17 / 122 | (container or null) | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.repository[]` | str | 17 / 122 | biostudies-arrayexpress | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.sample_protocol` | list | 17 / 122 | (container or null) | Reported sample protocol; narrative may cover multiple entities | datasets._native_protocols and evidence; no NLP extraction |
| `additional.sample_protocol[]` | str | 17 / 122 | Sample Collection - Cells were harvested by centrifugation into a cell pellet, and lysed with 350 μL | Reported sample protocol; narrative may cover multiple entities | datasets._native_protocols and evidence; no NLP extraction |
| `additional.software` | list | 1 / 138 | (container or null) | Source-reported additional.software; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.software[]` | str | 1 / 138 | Salmon | Source-reported additional.software; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.species` | list | 17 / 122 | (container or null) | Reported species label | datasets.organism_reported |
| `additional.species[]` | str | 17 / 122 | Mus musculus | Reported species label | datasets.organism_reported |
| `additional.study_type` | list | 17 / 122 | (container or null) | Source study-type label | datasets.experiment_type_reported |
| `additional.study_type[]` | str | 17 / 122 | RNA-seq of coding RNA | Source study-type label | datasets.experiment_type_reported |
| `additional.submitter` | list | 17 / 122 | (container or null) | Source-reported additional.submitter; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter[]` | NoneType, str | 17 / 122 | Claire Ma | Source-reported additional.submitter; detailed semantics not independently established | native evidence only; no structured target assignment |
| `citationsCount` | int | 122 / 17 | 0 | Source-reported citationsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `citationsCountScaled` | float | 122 / 17 | 0.0 | Source-reported citationsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `claimable` | bool | 122 / 17 | False | Source-reported claimable; detailed semantics not independently established | native evidence only; no structured target assignment |
| `connectionsCount` | int | 122 / 17 | 0 | Source-reported connectionsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `connectionsCountScaled` | float | 122 / 17 | 0.0 | Source-reported connectionsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references` | dict | 17 / 122 | (container or null) | Source-reported external associations; not verified externally | native evidence; named publication IDs only mapped |
| `cross_references.Biostudies` | list | 5 / 134 | (container or null) | Source-reported cross_references.Biostudies; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.Biostudies[]` | str | 5 / 134 | E-MTAB-15064 | Source-reported cross_references.Biostudies; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.EFO` | list | 17 / 122 | (container or null) | Source-reported cross_references.EFO; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.EFO[]` | str | 17 / 122 | EFO_0002944 | Source-reported cross_references.EFO; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.ENA` | list | 13 / 126 | (container or null) | Source-reported cross_references.ENA; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.ENA[]` | str | 13 / 126 | ERP164850 | Source-reported cross_references.ENA; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.doi` | list | 5 / 134 | (container or null) | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.doi[]` | str | 5 / 134 | 10.1101/2022.08.22.504722 | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.pubmed` | list | 3 / 136 | (container or null) | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.pubmed[]` | str | 3 / 136 | 26491539 | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `database` | str | 17 / 122 | biostudies-arrayexpress | Native detail repository label | identity validation; conflicts retained |
| `dates` | dict | 17 / 122 | (container or null) | Source dates; not our retrieval timestamp | native evidence only |
| `dates.creation` | str | 17 / 122 | 2024-10-07T20:11:12.943Z | Source-reported dates.creation; detailed semantics not independently established | native evidence only; no structured target assignment |
| `dates.modification` | str | 17 / 122 | 2025-07-30T00:00:58.848Z | Source-reported dates.modification; detailed semantics not independently established | native evidence only; no structured target assignment |
| `dates.release` | str | 17 / 122 | 2025-07-29T00:00:00Z | Source-reported dates.release; detailed semantics not independently established | native evidence only; no structured target assignment |
| `description` | str | 139 / 0 | To profile the cell states of interacting natural killer (NK) cells and blood cancer cells, we cultu | Resource record description; not an adjudicated experiment | datasets.description_reported |
| `downloadCount` | int | 122 / 17 | 0 | Source-reported downloadCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `downloadCountScaled` | float | 122 / 17 | 0.0 | Source-reported downloadCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions` | list | 17 / 122 | (container or null) | Source file/version metadata; no files retrieved | native evidence only |
| `id` | str | 122 / 17 | E-MTAB-13204 | Native search identifier | accession_reported; dataset_id identity |
| `is_claimable` | bool | 17 / 122 | False | Source claimability flag; not accessibility | native evidence only |
| `keywords` | NoneType | 122 / 17 | (container or null) | Source-reported keywords; detailed semantics not independently established | native evidence only; no structured target assignment |
| `name` | str | 17 / 122 | RNA-seq of Cdc42 knockout murine cytotoxic T lymphocytes | Resource record name | datasets.title_original |
| `omicsType` | list | 122 / 17 | (container or null) | Source-reported omicsType; detailed semantics not independently established | native evidence only; no structured target assignment |
| `omicsType[]` | str | 122 / 17 | Transcriptomics | Source-reported omicsType; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms` | list | 122 / 17 | (container or null) | Source-reported organisms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms[]` | dict | 122 / 17 | (container or null) | Source-reported organisms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms[].acc` | str | 122 / 17 |  | Source-reported organisms.acc; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms[].name` | str | 122 / 17 | Homo sapiens | Source-reported organisms.name; detailed semantics not independently established | native evidence only; no structured target assignment |
| `publicationDate` | str | 122 / 17 | 20230724 | Source-reported publicationDate; detailed semantics not independently established | native evidence only; no structured target assignment |
| `reanalysisCount` | int | 122 / 17 | 0 | Source-reported reanalysisCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `reanalysisCountScaled` | float | 122 / 17 | 0.0 | Source-reported reanalysisCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `score` | NoneType | 122 / 17 | (container or null) | Source-reported score; detailed semantics not independently established | native evidence only; no structured target assignment |
| `scores` | NoneType | 17 / 122 | (container or null) | Source index scores; not scientific qualification | native evidence only |
| `source` | str | 122 / 17 | biostudies-arrayexpress | Native search repository label | repository_normalized, unchanged |
| `title` | str | 122 / 17 | Single-cell RNA sequencing and single-cell CRISPR screens of interacting natural killer and blood ca | Resource record title | datasets.title_original |
| `viewsCount` | int | 122 / 17 | 0 | Source-reported viewsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `viewsCountScaled` | float | 122 / 17 | 0.0 | Source-reported viewsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
