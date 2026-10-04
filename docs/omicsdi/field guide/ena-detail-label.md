# ENA

Entity level: repository native record; experimental granularity not assumed. Field status: observed on saved responses; detailed semantics are not guaranteed by the API help. Search/detail variability is retained. No external source was visited.

Coverage: 33 response objects. Presence is across both endpoint shapes; types count occurrences, not unique records. Container examples are represented by their child rows. Full examples and source paths are in field_inventory.json. Native values are neither terminology-normalized nor interpreted scientifically.

| Native path | Types | Present / absent objects | Example | Meaning | Mapping / caution |
|---|---|---|---|---|---|
| `accession` | str | 33 / 0 | PRJNA967172 | Native detail identifier | accession_reported after identity validation |
| `additional` | dict | 33 / 0 | (container or null) | Repository-dependent additional metadata object | native evidence; recognized child mappings below |
| `additional.additional_accession` | list | 33 / 0 | (container or null) | Source-reported additional.additional_accession; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.center_name` | list | 33 / 0 | (container or null) | Source-reported additional.center_name; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.center_name[]` | str | 33 / 0 | UCLA | Source-reported additional.center_name; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.description_synonyms` | list | 13 / 20 | (container or null) | Source-reported additional.description_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.description_synonyms[]` | str | 13 / 20 | Coculture, ribonucleic acid, Acid, RNA, Ribonucleic, Cocultures, Coculture Technique, Co-cultures, r | Source-reported additional.description_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.full_dataset_link` | list | 33 / 0 | (container or null) | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.full_dataset_link[]` | str | 33 / 0 | https://www.ebi.ac.uk/ena/browser/view/PRJNA967172 | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.long_description` | list | 33 / 0 | (container or null) | Source-reported additional.long_description; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.long_description[]` | str | 33 / 0 | We performed deep RNA-sequencing (RNA-seq) analysis of PA/OA-stimulatedhepatocytes after co-culture  | Source-reported additional.long_description; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.name_synonyms` | list | 12 / 21 | (container or null) | Source-reported additional.name_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.name_synonyms[]` | str | 12 / 21 | NK Cell, 1500016L11Rik, Natural Killer Cells, NK Cells, Malignant Neoplasm, VPS2A, Natural Killer Ce | Source-reported additional.name_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.omics_type` | list | 33 / 0 | (container or null) | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.omics_type[]` | str | 33 / 0 | Genomics | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.repository` | list | 33 / 0 | (container or null) | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.repository[]` | str | 33 / 0 | ENA | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.scientific_name` | list | 28 / 5 | (container or null) | Reported organism name | datasets.organism_reported |
| `additional.scientific_name[]` | str | 28 / 5 | Mus musculus | Reported organism name | datasets.organism_reported |
| `additional.tag` | list | 27 / 6 | (container or null) | Source-reported additional.tag; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.tag[]` | str | 27 / 6 | xref:PubMed:37450593 | Source-reported additional.tag; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references` | dict | 33 / 0 | (container or null) | Source-reported external associations; not verified externally | native evidence; named publication IDs only mapped |
| `cross_references.GEO` | list | 30 / 3 | (container or null) | Source-reported cross_references.GEO; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.GEO[]` | str | 30 / 3 | GSE215803 | Source-reported cross_references.GEO; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.PubMed` | list | 25 / 8 | (container or null) | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.PubMed[]` | str | 25 / 8 | 37450593 | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.taxon` | list | 28 / 5 | (container or null) | Source-reported cross_references.taxon; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.taxon[]` | str | 28 / 5 | 10090 | Source-reported cross_references.taxon; detailed semantics not independently established | native evidence only; no structured target assignment |
| `database` | str | 33 / 0 | ENA | Native detail repository label | identity validation; conflicts retained |
| `dates` | dict | 33 / 0 | (container or null) | Source dates; not our retrieval timestamp | native evidence only |
| `dates.first_public` | str | 33 / 0 | 2024-08-02 | Source-reported dates.first_public; detailed semantics not independently established | native evidence only; no structured target assignment |
| `dates.last_updated` | str | 33 / 0 | 2024-08-02 | Source-reported dates.last_updated; detailed semantics not independently established | native evidence only; no structured target assignment |
| `description` | str | 33 / 0 | RNA Seq of co-culture system | Resource record description; not an adjudicated experiment | datasets.description_reported |
| `file_versions` | list | 33 / 0 | (container or null) | Source file/version metadata; no files retrieved | native evidence only |
| `file_versions[]` | dict | 26 / 7 | (container or null) | Source file/version metadata; no files retrieved | native evidence only |
| `file_versions[].body` | dict | 26 / 7 | (container or null) | Source-reported file_versions.body; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].body.files` | dict | 26 / 7 | (container or null) | Source-reported file_versions.body.files; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].body.files.Fastqsanger.gz` | list | 26 / 7 | (container or null) | Source-reported file_versions.body.files.Fastqsanger.gz; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].body.files.Fastqsanger.gz[]` | str | 26 / 7 | ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR244/046/SRR24435946/SRR24435946.fastq.gz | Source-reported file_versions.body.files.Fastqsanger.gz; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].body.type` | str | 26 / 7 | primary | Source-reported file_versions.body.type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].headers` | dict | 26 / 7 | (container or null) | Source-reported file_versions.headers; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].headers.Content-Type` | list | 26 / 7 | (container or null) | Source-reported file_versions.headers.Content-Type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].headers.Content-Type[]` | str | 26 / 7 | application/json | Source-reported file_versions.headers.Content-Type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].statusCode` | str | 26 / 7 | OK | Source-reported file_versions.statusCode; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].statusCodeValue` | int | 26 / 7 | 200 | Source-reported file_versions.statusCodeValue; detailed semantics not independently established | native evidence only; no structured target assignment |
| `is_claimable` | bool | 33 / 0 | False | Source claimability flag; not accessibility | native evidence only |
| `name` | str | 33 / 0 |  | Resource record name | datasets.title_original |
| `scores` | NoneType | 33 / 0 | (container or null) | Source index scores; not scientific qualification | native evidence only |
