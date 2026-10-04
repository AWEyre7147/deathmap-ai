# iProX

Entity level: repository native record; experimental granularity not assumed. Field status: observed on saved responses; detailed semantics are not guaranteed by the API help. Search/detail variability is retained. No external source was visited.

Coverage: 2 response objects. Presence is across both endpoint shapes; types count occurrences, not unique records. Container examples are represented by their child rows. Full examples and source paths are in field_inventory.json. Native values are neither terminology-normalized nor interpreted scientifically.

| Native path | Types | Present / absent objects | Example | Meaning | Mapping / caution |
|---|---|---|---|---|---|
| `accession` | str | 2 / 0 | PXD077233 | Native detail identifier | accession_reported after identity validation |
| `additional` | dict | 2 / 0 | (container or null) | Repository-dependent additional metadata object | native evidence; recognized child mappings below |
| `additional.additional_accession` | list | 2 / 0 | (container or null) | Source-reported additional.additional_accession; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.data_protocol` | list | 2 / 0 | (container or null) | Reported data protocol | datasets._native_protocols and evidence; no NLP extraction |
| `additional.data_protocol[]` | str | 2 / 0 |  | Reported data protocol | datasets._native_protocols and evidence; no NLP extraction |
| `additional.description_synonyms` | list | 1 / 1 | (container or null) | Source-reported additional.description_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.description_synonyms[]` | str | 1 / 1 | Class 3 Semaphorins, glicoproteinas, Networks, Class 2 Semaphorins, Class 4 Semaphorins, Class 5 Sem | Source-reported additional.description_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.full_dataset_link` | list | 2 / 0 | (container or null) | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.full_dataset_link[]` | str | 2 / 0 | http://www.iprox.org/page/project.html?id=IPX0016693000 | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.name_synonyms` | list | 1 / 1 | (container or null) | Source-reported additional.name_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.name_synonyms[]` | str | 1 / 1 | Mass Spectrum Analysis, BPBS, Therapy, treatment, Mass Spectrum, absence of, Painful Bladder Syndrom | Source-reported additional.name_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.omics_type` | list | 2 / 0 | (container or null) | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.omics_type[]` | str | 2 / 0 | Proteomics | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pubmed_abstract` | list | 2 / 0 | (container or null) | Publication abstract, distinct from dataset description | native evidence only; never dataset description |
| `additional.pubmed_abstract[]` | str | 2 / 0 | Microsatellite-stable/proficient mismatch repair (MSS/pMMR) colorectal cancer (CRC) is characterized | Publication abstract, distinct from dataset description | native evidence only; never dataset description |
| `additional.pubmed_abstract_synonyms` | list | 1 / 1 | (container or null) | Source-reported additional.pubmed_abstract_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pubmed_abstract_synonyms[]` | str | 1 / 1 | Class 3 Semaphorins, l(1)d norm-12, Class 2 Semaphorins, Class 4 Semaphorins, CRISPR Locus, CRISPR L | Source-reported additional.pubmed_abstract_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pubmed_authors` | list | 2 / 0 | (container or null) | Reported associated publication authors | publications.author_list_reported only when unambiguous |
| `additional.pubmed_authors[]` | str | 2 / 0 | Wang Shuo S, Hou Sen S, Luo Ce C, Zhang Haorui H, Jin Yiteng Y, Zhang Rui R, Zhao Yanping Y, Xiong X | Reported associated publication authors | publications.author_list_reported only when unambiguous |
| `additional.pubmed_title` | list | 2 / 0 | (container or null) | Reported associated publication title | publications.title_original only when association unambiguous |
| `additional.pubmed_title[]` | str | 2 / 0 | Arid3b suppresses CD8 + T cell infiltration and function in microsatellite-stable colorectal cancer  | Reported associated publication title | publications.title_original only when association unambiguous |
| `additional.pubmed_title_synonyms` | list | 1 / 1 | (container or null) | Source-reported additional.pubmed_title_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pubmed_title_synonyms[]` | str | 1 / 1 | l(1)d norm-12, NPN-1, Thymus-Dependent Lymphocytes, EG:17A9.1, C530029I03, BR_C, Nrp, NRP, l(1)G0018 | Source-reported additional.pubmed_title_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.repository` | list | 2 / 0 | (container or null) | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.repository[]` | str | 2 / 0 | iProX | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.sample_protocol` | list | 2 / 0 | (container or null) | Reported sample protocol; narrative may cover multiple entities | datasets._native_protocols and evidence; no NLP extraction |
| `additional.sample_protocol[]` | str | 2 / 0 |  | Reported sample protocol; narrative may cover multiple entities | datasets._native_protocols and evidence; no NLP extraction |
| `additional.species` | list | 2 / 0 | (container or null) | Reported species label | datasets.organism_reported |
| `additional.species[]` | str | 2 / 0 | Mus Musculus | Reported species label | datasets.organism_reported |
| `additional.submitter` | list | 2 / 0 | (container or null) | Source-reported additional.submitter; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter[]` | str | 2 / 0 | Zhidong Gao | Source-reported additional.submitter; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter_affiliation` | list | 2 / 0 | (container or null) | Source-reported additional.submitter_affiliation; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter_affiliation[]` | str | 2 / 0 | Peking University People’s Hospital | Source-reported additional.submitter_affiliation; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter_email` | list | 2 / 0 | (container or null) | Source-reported additional.submitter_email; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter_email[]` | str | 2 / 0 | [contact value retained in native response] | Source-reported additional.submitter_email; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references` | dict | 2 / 0 | (container or null) | Source-reported external associations; not verified externally | native evidence; named publication IDs only mapped |
| `cross_references.TAXONOMY` | list | 2 / 0 | (container or null) | Source-reported cross_references.TAXONOMY; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.TAXONOMY[]` | str | 2 / 0 | 10090 | Source-reported cross_references.TAXONOMY; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references.pubmed` | list | 2 / 0 | (container or null) | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.pubmed[]` | str | 2 / 0 | 42140952 | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `database` | str | 2 / 0 | iProX | Native detail repository label | identity validation; conflicts retained |
| `dates` | dict | 2 / 0 | (container or null) | Source dates; not our retrieval timestamp | native evidence only |
| `dates.publication` | str | 2 / 0 | Thu Apr 16 00:00:00 GMT+01:00 2026 | Source-reported dates.publication; detailed semantics not independently established | native evidence only; no structured target assignment |
| `description` | str | 2 / 0 | Microsatellite stable/proficient mismatch repair (MSS/pMMR) colorectal cancer (CRC) is characterized | Resource record description; not an adjudicated experiment | datasets.description_reported |
| `file_versions` | list | 2 / 0 | (container or null) | Source file/version metadata; no files retrieved | native evidence only |
| `is_claimable` | bool | 2 / 0 | False | Source claimability flag; not accessibility | native evidence only |
| `name` | str | 2 / 0 | Arid3b suppresses CD8+ T cell infiltration and function in Microsatellite-stable colorectal cancer v | Resource record name | datasets.title_original |
| `scores` | NoneType | 2 / 0 | (container or null) | Source index scores; not scientific qualification | native evidence only |
