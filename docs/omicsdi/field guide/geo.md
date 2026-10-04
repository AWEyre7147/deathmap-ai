# geo

Entity level: repository native record; experimental granularity not assumed. Field status: observed on saved responses; detailed semantics are not guaranteed by the API help. Search/detail variability is retained. No external source was visited.

Coverage: 659 response objects. Presence is across both endpoint shapes; types count occurrences, not unique records. Container examples are represented by their child rows. Full examples and source paths are in field_inventory.json. Native values are neither terminology-normalized nor interpreted scientifically.

| Native path | Types | Present / absent objects | Example | Meaning | Mapping / caution |
|---|---|---|---|---|---|
| `citationsCount` | int | 659 / 0 | 0 | Source-reported citationsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `citationsCountScaled` | float | 659 / 0 | 0.0 | Source-reported citationsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `claimable` | bool | 659 / 0 | False | Source-reported claimable; detailed semantics not independently established | native evidence only; no structured target assignment |
| `connectionsCount` | int | 659 / 0 | 0 | Source-reported connectionsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `connectionsCountScaled` | float | 659 / 0 | 0.0 | Source-reported connectionsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `description` | str | 659 / 0 | This study investigates the role of cancer cell surface proteins in modulating the response of cance | Resource record description; not an adjudicated experiment | datasets.description_reported |
| `downloadCount` | int | 659 / 0 | 0 | Source-reported downloadCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `downloadCountScaled` | float | 659 / 0 | 0.0 | Source-reported downloadCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `id` | str | 659 / 0 | GSE266329 | Native search identifier | accession_reported; dataset_id identity |
| `keywords` | NoneType | 659 / 0 | (container or null) | Source-reported keywords; detailed semantics not independently established | native evidence only; no structured target assignment |
| `omicsType` | list | 659 / 0 | (container or null) | Source-reported omicsType; detailed semantics not independently established | native evidence only; no structured target assignment |
| `omicsType[]` | str | 659 / 0 | Transcriptomics | Source-reported omicsType; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms` | list | 659 / 0 | (container or null) | Source-reported organisms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms[]` | dict | 659 / 0 | (container or null) | Source-reported organisms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms[].acc` | str | 659 / 0 |  | Source-reported organisms.acc; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms[].name` | str | 659 / 0 | Homo sapiens | Source-reported organisms.name; detailed semantics not independently established | native evidence only; no structured target assignment |
| `publicationDate` | str | 659 / 0 | 20250430 | Source-reported publicationDate; detailed semantics not independently established | native evidence only; no structured target assignment |
| `reanalysisCount` | int | 659 / 0 | 0 | Source-reported reanalysisCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `reanalysisCountScaled` | float | 659 / 0 | 0.0 | Source-reported reanalysisCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `score` | NoneType | 659 / 0 | (container or null) | Source-reported score; detailed semantics not independently established | native evidence only; no structured target assignment |
| `source` | str | 659 / 0 | geo | Native search repository label | repository_normalized, unchanged |
| `title` | str | 659 / 0 | Co-culture CRISPR screens reveal ATG9A as a regulator to macrophage-mediated cytotoxicity in cancer | Resource record title | datasets.title_original |
| `viewsCount` | int | 659 / 0 | 0 | Source-reported viewsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `viewsCountScaled` | float | 659 / 0 | 0.0 | Source-reported viewsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
