# GEO

Entity level: repository native record; experimental granularity not assumed. Field status: observed on saved responses; detailed semantics are not guaranteed by the API help. Search/detail variability is retained. No external source was visited.

Coverage: 11 response objects. Presence is across both endpoint shapes; types count occurrences, not unique records. Container examples are represented by their child rows. Full examples and source paths are in field_inventory.json. Native values are neither terminology-normalized nor interpreted scientifically.

| Native path | Types | Present / absent objects | Example | Meaning | Mapping / caution |
|---|---|---|---|---|---|
| `accession` | str | 11 / 0 | GSE228188 | Native detail identifier | accession_reported after identity validation |
| `additional` | dict | 11 / 0 | (container or null) | Repository-dependent additional metadata object | native evidence; recognized child mappings below |
| `additional.additional_accession` | list | 11 / 0 | (container or null) | Source-reported additional.additional_accession; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.entry_type` | list | 11 / 0 | (container or null) | Source-reported additional.entry_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.entry_type[]` | str | 11 / 0 | GSE | Source-reported additional.entry_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.full_dataset_link` | list | 11 / 0 | (container or null) | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.full_dataset_link[]` | str | 11 / 0 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE228188 | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.gds_type` | list | 11 / 0 | (container or null) | Source study-type label | datasets.experiment_type_reported |
| `additional.gds_type[]` | str | 11 / 0 |  Expression profiling by high throughput sequencing | Source study-type label | datasets.experiment_type_reported |
| `additional.omics_type` | list | 11 / 0 | (container or null) | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.omics_type[]` | str | 11 / 0 | Other | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.repository` | list | 11 / 0 | (container or null) | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.repository[]` | str | 11 / 0 | GEO | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.species` | list | 11 / 0 | (container or null) | Reported species label | datasets.organism_reported |
| `additional.species[]` | str | 11 / 0 | Homo sapiens | Reported species label | datasets.organism_reported |
| `cross_references` | dict | 11 / 0 | (container or null) | Source-reported external associations; not verified externally | native evidence; named publication IDs only mapped |
| `cross_references.GPL` | list | 11 / 0 | (container or null) | Source-reported cross_references.GPL; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.GPL[]` | str | 11 / 0 | 21697 | Source-reported cross_references.GPL; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.GSE` | list | 11 / 0 | (container or null) | Source-reported cross_references.GSE; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.GSE[]` | str | 11 / 0 | 228188 | Source-reported cross_references.GSE; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.GSM` | list | 11 / 0 | (container or null) | Source-reported cross_references.GSM; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.GSM[]` | str | 11 / 0 | GSM7116270 | Source-reported cross_references.GSM; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.PMID` | list | 7 / 4 | (container or null) | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.PMID[]` | str | 7 / 4 | [38619967] | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.SRA` | list | 2 / 9 | (container or null) | Source-reported cross_references.SRA; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.SRA[]` | str | 2 / 9 | SRP322075 | Source-reported cross_references.SRA; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.taxon` | list | 11 / 0 | (container or null) | Source-reported cross_references.taxon; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.taxon[]` | str | 11 / 0 | Homo sapiens | Source-reported cross_references.taxon; detailed semantics not independently established | native evidence only; no structured target assignment |
| `database` | str | 11 / 0 | GEO | Native detail repository label | identity validation; conflicts retained |
| `dates` | dict | 11 / 0 | (container or null) | Source dates; not our retrieval timestamp | native evidence only |
| `dates.publication` | str | 11 / 0 | 2023/03/29 | Source-reported dates.publication; detailed semantics not independently established | native evidence only; no structured target assignment |
| `description` | str | 11 / 0 | Therefore, to gain a deeper understanding of the interaction between NK cells and B-cell malignancie | Resource record description; not an adjudicated experiment | datasets.description_reported |
| `file_versions` | list | 11 / 0 | (container or null) | Source file/version metadata; no files retrieved | native evidence only |
| `file_versions[]` | dict | 11 / 0 | (container or null) | Source file/version metadata; no files retrieved | native evidence only |
| `file_versions[].body` | dict | 11 / 0 | (container or null) | Source-reported file_versions.body; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].body.files` | dict | 11 / 0 | (container or null) | Source-reported file_versions.body.files; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].body.files.Other` | list | 11 / 0 | (container or null) | Source-reported file_versions.body.files.Other; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].body.files.Other[]` | str | 11 / 0 | ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE228nnn/GSE228188/ | Source-reported file_versions.body.files.Other; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].body.type` | str | 11 / 0 | primary | Source-reported file_versions.body.type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].headers` | dict | 11 / 0 | (container or null) | Source-reported file_versions.headers; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].headers.Content-Type` | list | 11 / 0 | (container or null) | Source-reported file_versions.headers.Content-Type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].headers.Content-Type[]` | str | 11 / 0 | application/json | Source-reported file_versions.headers.Content-Type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].statusCode` | str | 11 / 0 | OK | Source-reported file_versions.statusCode; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].statusCodeValue` | int | 11 / 0 | 200 | Source-reported file_versions.statusCodeValue; detailed semantics not independently established | native evidence only; no structured target assignment |
| `is_claimable` | bool | 11 / 0 | False | Source claimability flag; not accessibility | native evidence only |
| `name` | str | 11 / 0 | NK co-culture CRISPR screen in the 721.221 B-cell lymphoblast | Resource record name | datasets.title_original |
| `scores` | NoneType | 11 / 0 | (container or null) | Source index scores; not scientific qualification | native evidence only |
