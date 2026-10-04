# project

Entity level: ENA/project record; may aggregate experiments. Field status: observed on saved responses; detailed semantics are not guaranteed by the API help. Search/detail variability is retained. No external source was visited.

Coverage: 914 response objects. Presence is across both endpoint shapes; types count occurrences, not unique records. Container examples are represented by their child rows. Full examples and source paths are in field_inventory.json. Native values are neither terminology-normalized nor interpreted scientifically.

| Native path | Types | Present / absent objects | Example | Meaning | Mapping / caution |
|---|---|---|---|---|---|
| `citationsCount` | int | 914 / 0 | 0 | Source-reported citationsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `citationsCountScaled` | float | 914 / 0 | 0.0 | Source-reported citationsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `claimable` | bool | 914 / 0 | False | Source-reported claimable; detailed semantics not independently established | native evidence only; no structured target assignment |
| `connectionsCount` | int | 914 / 0 | 0 | Source-reported connectionsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `connectionsCountScaled` | float | 914 / 0 | 0.0 | Source-reported connectionsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `description` | str | 914 / 0 | Genome-wide CRISPR/Cas9 screen reveals factors that influence the susceptibility of tumor cells to N | Resource record description; not an adjudicated experiment | datasets.description_reported |
| `downloadCount` | int | 914 / 0 | 0 | Source-reported downloadCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `downloadCountScaled` | float | 914 / 0 | 0.0 | Source-reported downloadCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `id` | str | 914 / 0 | PRJNA1163363 | Native search identifier | accession_reported; dataset_id identity |
| `keywords` | NoneType | 914 / 0 | (container or null) | Source-reported keywords; detailed semantics not independently established | native evidence only; no structured target assignment |
| `omicsType` | list | 914 / 0 | (container or null) | Source-reported omicsType; detailed semantics not independently established | native evidence only; no structured target assignment |
| `omicsType[]` | str | 914 / 0 | Genomics | Source-reported omicsType; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms` | NoneType | 914 / 0 | (container or null) | Source-reported organisms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `publicationDate` | NoneType | 914 / 0 | (container or null) | Source-reported publicationDate; detailed semantics not independently established | native evidence only; no structured target assignment |
| `reanalysisCount` | int | 914 / 0 | 0 | Source-reported reanalysisCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `reanalysisCountScaled` | float | 914 / 0 | 0.0 | Source-reported reanalysisCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `score` | NoneType | 914 / 0 | (container or null) | Source-reported score; detailed semantics not independently established | native evidence only; no structured target assignment |
| `source` | str | 914 / 0 | project | Native search repository label | repository_normalized, unchanged |
| `title` | NoneType, str | 914 / 0 | Genome-wide CRISPR/Cas9 screen reveals factors that influence the susceptibility of tumor cells to N | Resource record title | datasets.title_original |
| `viewsCount` | int | 914 / 0 | 0 | Source-reported viewsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `viewsCountScaled` | float | 914 / 0 | 0.0 | Source-reported viewsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
