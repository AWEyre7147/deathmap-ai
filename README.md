# DeathMap-AI v0.1

A metadata discovery and curation pipeline for studies involving CRISPR perturbation. The completed ORCS milestone searches saved BioGRID ORCS metadata with structured filters and Cellosaurus interpretation. PubMed enrichment supplies a shared PMID-led metadata database and separate enrichment workbooks for all three saved ORCS searches. GEO enrichment supplies Series hierarchy, sample metadata and a shared ORCS database. BioStudies–ArrayExpress enrichment supplies study, protocol, sample and IDF/SDRF metadata. ENA is the next repository goal. OmicsDI discovery has been retired.

The [biological-classes profile](searches/orcs/orcs-crispr-biological-classes-pilot-v01/profile.json) is the current scientific baseline. It retained 1,830 direct-rule candidates and 56 publication companions across 328 publications from 2,217 cached screens. The owner reported representation of 33/33 ORCS-present comparison publications. This publication-level result does not establish dataset availability or eligibility of every candidate.

## Run locally

Python 3.11 or later, from the repository root:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
deathmap-search-orcs --profile searches/orcs/orcs-crispr-biological-classes-pilot-v01/profile.json
```

Each execution writes canonical metadata to a new UTC-named folder under `outputs/orcs`. It does not refresh sources or download experimental files.

The search command exports Excel automatically. Excel export uses the project's Python/openpyxl dependency, without Codex or Node. The owner-finalized repaired template is selected by the active manifest. Export into a new run directory:

```powershell
deathmap-export-excel <new-run-directory>
```

Existing authored workbooks are refused. See the [owner change catalog](data/templates/owner-change-catalog.json). Reference-sheet example counts are not measured run counts; consult each run summary.

## Milestone and roadmap

[Curated ORCS outputs](outputs/orcs/README.md) retain the latest generated workbook and canonical JSON for each search, with file hashes. The retained runs were generated with the finalized template; earlier reviewed versions are archived. Saved public metadata and templates are included for offline reproducibility. Curated outputs are included in Git; external archives remain local.

PubMed enrichment retrieves publication metadata and direct GEO, BioProject and SRA associations. See the [shared database](data/orcs/pubmed-enrichment.json), [Excel view](data/orcs/PubMed-Enrichment.xlsx) and [final template](data/templates/PubMed-Enrichment.xlsx).

GEO enrichment processed all 418 ORCS publications, identifying 503 candidate GSEs and preserving 22,139 distinct GSM metadata records. Its [shared database](data/orcs/geo-enrichment.json), [Excel view](data/orcs/GEO-Enrichment.xlsx) and [native source package](data/orcs/geo-enrichment-source/20261011/README.md) are retained for review and response reuse. Candidate associations do not establish dataset ownership or qualifying screen content. ENA, screen attribution and evidence harmonization remain future work. PRIDE, MassIVE, jPOST and iProX remain later resource candidates. A future OmicsDI accession-led lookup remains optional backlog work.

BioStudies–ArrayExpress enrichment processed all 418 publications and found ten candidate studies associated with ten publications (eleven publication–study links). Its [shared database](data/orcs/arrayexpress-enrichment.json), [Excel view](data/orcs/BioStudies-ArrayExpress-Enrichment.xlsx), [source package](data/orcs/arrayexpress-enrichment-source/20261011/) and [final template](data/templates/BioStudies-ArrayExpress-Enrichment.xlsx) retain native evidence, including IDF/SDRF for all ten studies. The active adapter uses complete-title search and Europe PMC accession annotations; quoted DOI search was retired after adding no unique study. The completed run retains its original strategy and source-code snapshots. No experimental contents or publication bodies were retrieved.

Read the [current specifications](docs/specifications/README.md), [resource planning](docs/resources/README.md), and [documentation index](docs/index.md). Code is [MIT licensed](LICENSE); saved third-party metadata retains [upstream terms](THIRD_PARTY_NOTICES.md).

Publication identifiers can be resolved independently of ORCS using `deathmap-resolve-publication`.
