# Common response fields

All per-field statements below are observed, not a complete documented schema.
The API help documents the search envelope `count`, `datasets`, and `facets`;
these are pagination/result-container metadata, not dataset attributes. `count`
may change between cached and live pages. Native result order is retained.

| Native path | Observed meaning | Target mapping |
|---|---|---|
| `id` | Native search identifier | accession_reported; dataset_id identity |
| `accession` | Native detail identifier | accession_reported after identity validation |
| `source` | Native search repository label | repository_normalized, unchanged |
| `database` | Native detail repository label | identity validation; conflicts retained |
| `title` | Resource record title | datasets.title_original |
| `name` | Resource record name | datasets.title_original |
| `description` | Resource record description; not an adjudicated experiment | datasets.description_reported |
| `additional.organism` | Reported organism label | datasets.organism_reported |
| `additional.species` | Reported species label | datasets.organism_reported |
| `additional.scientific_name` | Reported organism name | datasets.organism_reported |
| `additional.study_type` | Source study-type label | datasets.experiment_type_reported |
| `additional.gds_type` | Source study-type label | datasets.experiment_type_reported |
| `additional.full_dataset_link` | Source-reported record link; not visited | datasets.dataset_url; no availability inference |
| `additional.pubmed_title` | Reported associated publication title | publications.title_original only when association unambiguous |
| `additional.pubmed_authors` | Reported associated publication authors | publications.author_list_reported only when unambiguous |
| `additional.journal` | Reported publication journal | publications.journal_reported only when unambiguous |
| `additional.pubmed_abstract` | Publication abstract, distinct from dataset description | native evidence only; never dataset description |
| `additional.sample_protocol` | Reported sample protocol; narrative may cover multiple entities | datasets._native_protocols and evidence; no NLP extraction |
| `additional.data_protocol` | Reported data protocol | datasets._native_protocols and evidence; no NLP extraction |
| `additional` | Repository-dependent additional metadata object | native evidence; recognized child mappings below |
| `cross_references` | Source-reported external associations; not verified externally | native evidence; named publication IDs only mapped |
| `dates` | Source dates; not our retrieval timestamp | native evidence only |
| `scores` | Source index scores; not scientific qualification | native evidence only |
| `file_versions` | Source file/version metadata; no files retrieved | native evidence only |
| `is_claimable` | Source claimability flag; not accessibility | native evidence only |

See source tables for exact types, presence counts, variability and source-grounded examples. Unrecognized dates, links and cross-references remain native evidence. Neither a URL nor a repository name establishes data or screen availability.
