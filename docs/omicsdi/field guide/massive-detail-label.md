# MassIVE

Entity level: repository native record; experimental granularity not assumed. Field status: observed on saved responses; detailed semantics are not guaranteed by the API help. Search/detail variability is retained. No external source was visited.

Coverage: 2 response objects. Presence is across both endpoint shapes; types count occurrences, not unique records. Container examples are represented by their child rows. Full examples and source paths are in field_inventory.json. Native values are neither terminology-normalized nor interpreted scientifically.

| Native path | Types | Present / absent objects | Example | Meaning | Mapping / caution |
|---|---|---|---|---|---|
| `accession` | str | 2 / 0 | MSV000093718 | Native detail identifier | accession_reported after identity validation |
| `additional` | dict | 2 / 0 | (container or null) | Repository-dependent additional metadata object | native evidence; recognized child mappings below |
| `additional.additional_accession` | list | 2 / 0 | (container or null) | Source-reported additional.additional_accession; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.additional_accession[]` | str | 1 / 1 | PXD048064 | Source-reported additional.additional_accession; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.citation_count` | list | 1 / 1 | (container or null) | Source-reported additional.citation_count; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.citation_count[]` | str | 1 / 1 | 0 | Source-reported additional.citation_count; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.data_protocol` | list | 2 / 0 | (container or null) | Reported data protocol | datasets._native_protocols and evidence; no NLP extraction |
| `additional.data_protocol[]` | str | 2 / 0 |  | Reported data protocol | datasets._native_protocols and evidence; no NLP extraction |
| `additional.description_synonyms` | list | 2 / 0 | (container or null) | Source-reported additional.description_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.description_synonyms[]` | str | 2 / 0 | 70zpep, DYRK1, LYP2, T-lymphocyte receptor complex, LYP1, epsin, Dmel_CG7826, l(3)S011027, Cell, CG7 | Source-reported additional.description_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.file_size` | list | 2 / 0 | (container or null) | Source-reported additional.file_size; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.file_size[]` | str | 2 / 0 | 25 | Source-reported additional.file_size; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.full_dataset_link` | list | 2 / 0 | (container or null) | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.full_dataset_link[]` | str | 2 / 0 | https://massive.ucsd.edu/ProteoSAFe/dataset.jsp?task=15146bf0ee54420aa8f1b51ef170ee19 | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.instrument_platform` | list | 2 / 0 | (container or null) | Source-reported additional.instrument_platform; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.instrument_platform[]` | str | 2 / 0 | Orbitrap Fusion | Source-reported additional.instrument_platform; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.name_synonyms` | list | 2 / 0 | (container or null) | Source-reported additional.name_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.name_synonyms[]` | str | 2 / 0 | CRISPR Locus, 70zpep, CRISPR Loci, CRISPR Spacer Sequences, CRISPR Clusters, CRISPR-Cas Loci, CRISPR | Source-reported additional.name_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.omics_type` | list | 2 / 0 | (container or null) | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.omics_type[]` | str | 2 / 0 | Proteomics | Source-reported additional.omics_type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.ptm_modification` | list | 2 / 0 | (container or null) | Source-reported additional.ptm_modification; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.ptm_modification[]` | str | 2 / 0 | UNIMOD:21 - "Phosphorylation." | Source-reported additional.ptm_modification; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pubmed_abstract` | list | 1 / 1 | (container or null) | Publication abstract, distinct from dataset description | native evidence only; never dataset description |
| `additional.pubmed_abstract[]` | str | 1 / 1 | Protein tyrosine phosphatase nonreceptor type 22 (PTPN22) is encoded by a major autoimmunity gene an | Publication abstract, distinct from dataset description | native evidence only; never dataset description |
| `additional.pubmed_abstract_synonyms` | list | 1 / 1 | (container or null) | Source-reported additional.pubmed_abstract_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pubmed_abstract_synonyms[]` | str | 1 / 1 | 70zpep, CRISPR Locus, Ghrfr, T cell activation, Materials, Clustered Regularly Interspaced Short Pal | Source-reported additional.pubmed_abstract_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pubmed_authors` | list | 1 / 1 | (container or null) | Reported associated publication authors | publications.author_list_reported only when unambiguous |
| `additional.pubmed_authors[]` | str | 1 / 1 | Zhuang Chuling C, Yang Shen S, Gonzalez Carlos G CG, Ainsworth Richard I RI, Li Sheng S, Kobayashi M | Reported associated publication authors | publications.author_list_reported only when unambiguous |
| `additional.pubmed_title` | list | 1 / 1 | (container or null) | Reported associated publication title | publications.title_original only when association unambiguous |
| `additional.pubmed_title[]` | str | 1 / 1 | A novel gain-of-function phosphorylation site modulates PTPN22 inhibition of TCR signaling. | Reported associated publication title | publications.title_original only when association unambiguous |
| `additional.pubmed_title_synonyms` | list | 1 / 1 | (container or null) | Source-reported additional.pubmed_title_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.pubmed_title_synonyms[]` | str | 1 / 1 | LYP, 70zpep, TCR, Responder protein Smok-Tcr, Tcr, 2.7.11.1, TCR complex, signalling process, Ptpn8, | Source-reported additional.pubmed_title_synonyms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.repository` | list | 2 / 0 | (container or null) | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.repository[]` | str | 2 / 0 | MassIVE | Source-reported additional.repository; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.sample_protocol` | list | 2 / 0 | (container or null) | Reported sample protocol; narrative may cover multiple entities | datasets._native_protocols and evidence; no NLP extraction |
| `additional.sample_protocol[]` | str | 2 / 0 |  | Reported sample protocol; narrative may cover multiple entities | datasets._native_protocols and evidence; no NLP extraction |
| `additional.species` | list | 2 / 0 | (container or null) | Reported species label | datasets.organism_reported |
| `additional.species[]` | str | 2 / 0 | Homo Sapiens (ncbitaxon:9606) | Reported species label | datasets.organism_reported |
| `additional.submitter` | list | 2 / 0 | (container or null) | Source-reported additional.submitter; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter[]` | str | 2 / 0 | Nunzio Bottini | Source-reported additional.submitter; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter_affiliation` | list | 2 / 0 | (container or null) | Source-reported additional.submitter_affiliation; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter_affiliation[]` | str | 2 / 0 | UCSD | Source-reported additional.submitter_affiliation; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter_email` | list | 2 / 0 | (container or null) | Source-reported additional.submitter_email; detailed semantics not independently established | native evidence only; no structured target assignment |
| `additional.submitter_email[]` | str | 2 / 0 | [contact value retained in native response] | Source-reported additional.submitter_email; detailed semantics not independently established | native evidence only; no structured target assignment |
| `cross_references` | dict | 2 / 0 | (container or null) | Source-reported external associations; not verified externally | native evidence; named publication IDs only mapped |
| `cross_references.pubmed` | list | 1 / 1 | (container or null) | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `cross_references.pubmed[]` | str | 1 / 1 | 38777143 | Named publication identifier association | publications identifier and association; exact syntax normalization, no screen link |
| `database` | str | 2 / 0 | MassIVE | Native detail repository label | identity validation; conflicts retained |
| `dates` | dict | 2 / 0 | (container or null) | Source dates; not our retrieval timestamp | native evidence only |
| `dates.publication` | str | 2 / 0 | Thu Dec 21 18:41:00 GMT 2023 | Source-reported dates.publication; detailed semantics not independently established | native evidence only; no structured target assignment |
| `description` | str | 2 / 0 | LQF of 3x FLAG PTPN22 WT Jurkat cells compared to S325A and S325E KI mutant Jurkat cells. WT or KI l | Resource record description; not an adjudicated experiment | datasets.description_reported |
| `file_versions` | list | 2 / 0 | (container or null) | Source file/version metadata; no files retrieved | native evidence only |
| `file_versions[]` | dict | 2 / 0 | (container or null) | Source file/version metadata; no files retrieved | native evidence only |
| `file_versions[].body` | dict | 2 / 0 | (container or null) | Source-reported file_versions.body; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].body.files` | dict | 2 / 0 | (container or null) | Source-reported file_versions.body.files; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].body.files.Other` | list | 2 / 0 | (container or null) | Source-reported file_versions.body.files.Other; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].body.files.Other[]` | str | 2 / 0 | ftp://massive-ftp.ucsd.edu/v06/MSV000093718/ | Source-reported file_versions.body.files.Other; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].body.type` | str | 2 / 0 | primary | Source-reported file_versions.body.type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].headers` | dict | 2 / 0 | (container or null) | Source-reported file_versions.headers; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].headers.Content-Type` | list | 2 / 0 | (container or null) | Source-reported file_versions.headers.Content-Type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].headers.Content-Type[]` | str | 2 / 0 | application/json | Source-reported file_versions.headers.Content-Type; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].statusCode` | str | 2 / 0 | OK | Source-reported file_versions.statusCode; detailed semantics not independently established | native evidence only; no structured target assignment |
| `file_versions[].statusCodeValue` | int | 2 / 0 | 200 | Source-reported file_versions.statusCodeValue; detailed semantics not independently established | native evidence only; no structured target assignment |
| `is_claimable` | bool | 2 / 0 | False | Source claimability flag; not accessibility | native evidence only |
| `name` | str | 2 / 0 | Global phosphoproteomics for CRISPR/Cas9 mediated PTPN22 Ser325 mutagenesis on Jurkat cells | Resource record name | datasets.title_original |
| `scores` | NoneType, dict | 2 / 0 | (container or null) | Source index scores; not scientific qualification | native evidence only |
| `scores.citationCount` | int | 1 / 1 | 0 | Source-reported scores.citationCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `scores.reanalysisCount` | int | 1 / 1 | 0 | Source-reported scores.reanalysisCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `scores.searchCount` | int | 1 / 1 | 0 | Source-reported scores.searchCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `scores.viewCount` | int | 1 / 1 | 0 | Source-reported scores.viewCount; detailed semantics not independently established | native evidence only; no structured target assignment |
