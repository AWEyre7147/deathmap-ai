# iprox

Entity level: repository native record; experimental granularity not assumed. Field status: observed on saved responses; detailed semantics are not guaranteed by the API help. Search/detail variability is retained. No external source was visited.

Coverage: 3 response objects. Presence is across both endpoint shapes; types count occurrences, not unique records. Container examples are represented by their child rows. Full examples and source paths are in field_inventory.json. Native values are neither terminology-normalized nor interpreted scientifically.

| Native path | Types | Present / absent objects | Example | Meaning | Mapping / caution |
|---|---|---|---|---|---|
| `citationsCount` | int | 3 / 0 | 0 | Source-reported citationsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `citationsCountScaled` | float | 3 / 0 | 0.0 | Source-reported citationsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `claimable` | bool | 3 / 0 | False | Source-reported claimable; detailed semantics not independently established | native evidence only; no structured target assignment |
| `connectionsCount` | int | 3 / 0 | 0 | Source-reported connectionsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `connectionsCountScaled` | float | 3 / 0 | 0.0 | Source-reported connectionsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `description` | str | 3 / 0 | Microsatellite stable/proficient mismatch repair (MSS/pMMR) colorectal cancer (CRC) is characterized | Resource record description; not an adjudicated experiment | datasets.description_reported |
| `downloadCount` | int | 3 / 0 | 0 | Source-reported downloadCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `downloadCountScaled` | float | 3 / 0 | 0.0 | Source-reported downloadCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `id` | str | 3 / 0 | PXD077233 | Native search identifier | accession_reported; dataset_id identity |
| `keywords` | NoneType | 3 / 0 | (container or null) | Source-reported keywords; detailed semantics not independently established | native evidence only; no structured target assignment |
| `omicsType` | list | 3 / 0 | (container or null) | Source-reported omicsType; detailed semantics not independently established | native evidence only; no structured target assignment |
| `omicsType[]` | str | 3 / 0 | Proteomics | Source-reported omicsType; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms` | list | 3 / 0 | (container or null) | Source-reported organisms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms[]` | dict | 3 / 0 | (container or null) | Source-reported organisms; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms[].acc` | str | 3 / 0 |  | Source-reported organisms.acc; detailed semantics not independently established | native evidence only; no structured target assignment |
| `organisms[].name` | str | 3 / 0 | Mus Musculus | Source-reported organisms.name; detailed semantics not independently established | native evidence only; no structured target assignment |
| `publicationDate` | NoneType, str | 3 / 0 | 20221026 | Source-reported publicationDate; detailed semantics not independently established | native evidence only; no structured target assignment |
| `reanalysisCount` | int | 3 / 0 | 0 | Source-reported reanalysisCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `reanalysisCountScaled` | float | 3 / 0 | 0.0 | Source-reported reanalysisCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
| `score` | NoneType | 3 / 0 | (container or null) | Source-reported score; detailed semantics not independently established | native evidence only; no structured target assignment |
| `source` | str | 3 / 0 | iprox | Native search repository label | repository_normalized, unchanged |
| `title` | str | 3 / 0 | Arid3b suppresses CD8+ T cell infiltration and function in Microsatellite-stable colorectal cancer v | Resource record title | datasets.title_original |
| `viewsCount` | int | 3 / 0 | 0 | Source-reported viewsCount; detailed semantics not independently established | native evidence only; no structured target assignment |
| `viewsCountScaled` | float | 3 / 0 | 0.0 | Source-reported viewsCountScaled; detailed semantics not independently established | native evidence only; no structured target assignment |
