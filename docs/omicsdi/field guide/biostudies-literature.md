# biostudies-literature

Entity level: literature-associated native record; not an independent experimental deposit. Field status: observed on saved responses; detailed semantics are not guaranteed by the API help. Search/detail variability is retained. No external source was visited.

Coverage: 1378 response objects. Presence is across both endpoint shapes; types count occurrences, not unique records. Container examples are represented by their child rows. Full examples and source paths are in field_inventory.json. Native values are neither terminology-normalized nor interpreted scientifically.

| Native path | Types | Present / absent objects | Example | Meaning | Mapping / caution |
|---|---|---|---|---|---|
| `accession` | str | 63 / 1315 | S-EPMC11442982 | Native detail identifier | accession_reported after identity validation |
| `additional` | dict | 63 / 1315 | (container or null) | Repository-dependent additional metadata object | native evidence; recognized child mappings below |
| `additional.additional_accession` | list | 63 / 1315 | (container or null) | Source-reported additional.additional_accession; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.full_dataset_link` | list | 63 / 1315 | (container or null) | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.full_dataset_link[]` | str | 63 / 1315 | https://www.ebi.ac.uk/biostudies/studies/S-EPMC11442982 | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.funding` | list | 49 / 1329 | (container or null) | Source-reported additional.funding; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.funding[]` | str | 49 / 1329 | NIEHS NIH HHS | Source-reported additional.funding; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.funding_grant_id` | list | 46 / 1332 | (container or null) | Source-reported additional.funding_grant_id; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.funding_grant_id[]` | str | 46 / 1332 | K12 CA090354 | Source-reported additional.funding_grant_id; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.journal` | list | 63 / 1315 | (container or null) | Reported publication journal | publications.journal_reported only when unambiguous |
| `additional.journal[]` | str | 63 / 1315 | Nature communications | Reported publication journal | publications.journal_reported only when unambiguous |
| `additional.omics_type` | list | 63 / 1315 | (container or null) | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.omics_type[]` | str | 63 / 1315 | Unknown | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pagination` | list | 63 / 1315 | (container or null) | Source-reported additional.pagination; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pagination[]` | str | 63 / 1315 | 8439 | Source-reported additional.pagination; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pmcid` | list | 63 / 1315 | (container or null) | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `additional.pmcid[]` | str | 63 / 1315 | PMC11442982 | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `additional.pubmed_abstract` | list | 63 / 1315 | (container or null) | Publication abstract, distinct from dataset description | native evidence only; never dataset description |
| `additional.pubmed_abstract[]` | str | 63 / 1315 | Chimeric antigen receptor (CAR)-modified natural killer (NK) cells show antileukemic activity agains | Publication abstract, distinct from dataset description | native evidence only; never dataset description |
| `additional.pubmed_authors` | list | 63 / 1315 | (container or null) | Reported associated publication authors | publications.author_list_reported only when unambiguous |
| `additional.pubmed_authors[]` | str | 63 / 1315 | Wolf S | Reported associated publication authors | publications.author_list_reported only when unambiguous |
| `additional.pubmed_title` | list | 63 / 1315 | (container or null) | Reported associated publication title | publications.title_original only when association unambiguous |
| `additional.pubmed_title[]` | str | 63 / 1315 | CRISPR/Cas9 editing of NKG2A improves the efficacy of primary CD33-directed chimeric antigen recepto | Reported associated publication title | publications.title_original only when association unambiguous |
| `additional.repository` | list | 63 / 1315 | (container or null) | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.repository[]` | str | 63 / 1315 | biostudies-literature | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter` | list | 63 / 1315 | (container or null) | Source-reported additional.submitter; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter[]` | str | 63 / 1315 | Bexte T | Source-reported additional.submitter; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.volume` | list | 61 / 1317 | (container or null) | Source-reported additional.volume; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.volume[]` | str | 61 / 1317 | 15(1) | Source-reported additional.volume; detailed semantics not independently established | native evidence only; no structured target assignment |
| `citationsCount` | int | 1315 / 63 | 0 | Source-reported citationsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `citationsCountScaled` | float | 1315 / 63 | 0.0 | Source-reported citationsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `claimable` | bool | 1315 / 63 | False | Source-reported claimable; detailed semantics not independently established | native evidence only; no structured target assignment |
| `connectionsCount` | int | 1315 / 63 | 0 | Source-reported connectionsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `connectionsCountScaled` | float | 1315 / 63 | 0.0 | Source-reported connectionsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references` | dict | 63 / 1315 | (container or null) | Source-reported external associations; not verified externally | native evidence; named publication IDs only mapped |
| `cross_references.doi` | list | 63 / 1315 | (container or null) | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.doi[]` | str | 63 / 1315 | 10.1038/s41467-024-52388-1 | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.pubmed` | list | 63 / 1315 | (container or null) | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.pubmed[]` | str | 63 / 1315 | 39349459 | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `database` | str | 63 / 1315 | biostudies-literature | Native detail repository label | identity validation; conflicts retained |
| `dates` | dict | 63 / 1315 | (container or null) | Source dates; not our retrieval timestamp | native evidence only |
| `dates.creation` | str | 63 / 1315 | 2025-04-04T02:09:26.012Z | Source-reported dates.creation; detailed semantics not independently established | native evidence only; no structured target assignment |
| `dates.modification` | str | 63 / 1315 | 2025-04-04T02:09:26.012Z | Source-reported dates.modification; detailed semantics not independently established | native evidence only; no structured target assignment |
| `dates.publication` | str | 63 / 1315 | 2024 Sep | Source-reported dates.publication; detailed semantics not independently established | native evidence only; no structured target assignment |
| `dates.release` | str | 63 / 1315 | 2024-01-01T00:00:00Z | Source-reported dates.release; detailed semantics not independently established | native evidence only; no structured target assignment |
| `description` | NoneType, str | 1378 / 0 | Chimeric antigen receptor (CAR)-modified natural killer (NK) cells show antileukemic activity agains | Resource record description; not an adjudicated experiment | datasets.description_reported |
| `downloadCount` | int | 1315 / 63 | 0 | Source-reported downloadCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `downloadCountScaled` | float | 1315 / 63 | 0.0 | Source-reported downloadCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions` | list | 63 / 1315 | (container or null) | Source file/version metadata; no files retrieved | native evidence only |
| `id` | str | 1315 / 63 | S-EPMC7362346 | Native search identifier | accession_reported; dataset_id identity |
| `is_claimable` | bool | 63 / 1315 | False | Source claimability flag; not accessibility | native evidence only |
| `keywords` | NoneType | 1315 / 63 | (container or null) | Source-reported keywords; detailed semantics not independently established | native evidence only; no structured target assignment |
| `name` | str | 63 / 1315 | CRISPR/Cas9 editing of NKG2A improves the efficacy of primary CD33-directed chimeric antigen recepto | Resource record name | datasets.title_original |
| `omicsType` | list | 1315 / 63 | (container or null) | Source-reported omicsType; detailed semantics not independently established | native evidence only; no structured target assignment |
| `omicsType[]` | str | 1315 / 63 | Unknown | Source-reported omicsType; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms` | NoneType | 1315 / 63 | (container or null) | Source-reported organisms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `publicationDate` | NoneType | 1315 / 63 | (container or null) | Source-reported publicationDate; detailed semantics not independently established | native evidence only; no structured target assignment |
| `reanalysisCount` | int | 1315 / 63 | 0 | Source-reported reanalysisCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `reanalysisCountScaled` | float | 1315 / 63 | 0.0 | Source-reported reanalysisCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `score` | NoneType | 1315 / 63 | (container or null) | Source-reported score; detailed semantics not independently established | native evidence only; no structured target assignment |
| `scores` | NoneType | 63 / 1315 | (container or null) | Source index scores; not scientific qualification | native evidence only |
| `source` | str | 1315 / 63 | biostudies-literature | Native search repository label | repository_normalized, unchanged |
| `title` | str | 1315 / 63 | CRISPR-based screens uncover determinants of immunotherapy response in multiple myeloma. | Resource record title | datasets.title_original |
| `viewsCount` | int | 1315 / 63 | 0 | Source-reported viewsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `viewsCountScaled` | float | 1315 / 63 | 0.0 | Source-reported viewsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
