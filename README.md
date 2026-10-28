# DeathMap-AI v0.1

A metadata discovery and curation pipeline for studies involving CRISPR perturbation. The completed ORCS milestone searches saved BioGRID ORCS metadata with structured filters and Cellosaurus interpretation. PubMed enrichment supplies a shared PMID-led metadata database and repository/publication associations. GEO enrichment supplies Series hierarchy, sample metadata and a shared ORCS database. BioStudies–ArrayExpress enrichment supplies study, protocol, sample and IDF/SDRF metadata. ENA enrichment adds native study and sequencing metadata with explicit broad-project omissions. OmicsDI discovery has been retired.

The biological-classes search has two current profiles: [v01, 2014–2022](searches/orcs/orcs-crispr-biological-classes-pilot-v01.json), retained 1,704 direct-rule candidates and 55 publication companions across 288 publications; [v02, without date bounds](searches/orcs/orcs-crispr-biological-classes-pilot-v02.json), retained 1,830 direct-rule candidates and 56 companions across 328 publications. Both use the same 2,217 cached screens. The owner reported representation of 33/33 ORCS-present comparison publications. This publication-level result does not establish dataset availability or eligibility of every candidate.

## Run locally

Python 3.11 or later, from the repository root:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
deathmap-search-orcs --profile searches/orcs/orcs-crispr-biological-classes-pilot-v01.json
```

Each execution writes canonical metadata to a new UTC-named folder under `outputs/orcs`. It does not refresh sources or download experimental files.

The search command exports Excel automatically. Excel export uses the project's Python/openpyxl dependency, without Codex or Node. The owner-finalized repaired template is selected by the active manifest. Export into a new run directory:

```powershell
deathmap-export-excel <new-run-directory>
```

Existing authored workbooks are refused. See the registered template manifests. Reference-sheet example counts are not measured run counts; consult each run summary.

## Milestone and roadmap

[Curated ORCS outputs](outputs/orcs/README.md) retain the latest generated workbook and canonical JSON for each search, with file hashes. The retained runs were generated with the finalized template; earlier reviewed versions are archived. Saved public metadata and templates are included for offline reproducibility. Curated outputs are included in Git; external archives remain local.

PubMed enrichment retrieves publication metadata and direct GEO, BioProject and SRA associations. See the [shared database](data/orcs/pubmed-enrichment.json), [Excel view](data/orcs/PubMed-Enrichment.xlsx) and [final template](data/templates/PubMed-Enrichment.xlsx).

GEO enrichment processed all 418 ORCS publications, identifying 503 candidate GSEs and preserving 22,139 distinct GSM metadata records. Its [shared database](data/orcs/geo-enrichment.json), [Excel view](data/orcs/GEO-Enrichment.xlsx) and [native source package](data/orcs/geo-enrichment-source/20261011/README.md) are retained for review and response reuse. Candidate associations do not establish dataset ownership or qualifying screen content. Screen attribution and evidence harmonization remain future work. PRIDE, MassIVE, jPOST and iProX remain later resource candidates. A future OmicsDI accession-led lookup remains optional backlog work.

BioStudies–ArrayExpress enrichment processed all 418 publications and found ten candidate studies associated with ten publications (eleven publication–study links). Its [shared database](data/orcs/arrayexpress-enrichment.json), [Excel view](data/orcs/BioStudies-ArrayExpress-Enrichment.xlsx), [source package](data/orcs/arrayexpress-enrichment-source/20261011/) and [final template](data/templates/BioStudies-ArrayExpress-Enrichment.xlsx) retain native evidence, including IDF/SDRF for all ten studies. The active adapter uses complete-title search and Europe PMC accession annotations; quoted DOI search was retired after adding no unique study. The completed run retains its original strategy and source-code snapshots. No experimental contents or publication bodies were retrieved.

ENA enrichment processed all 418 publications and retained 533 candidate project
records linked through discovery evidence to 191 publications. The
[workbook](data/orcs/ENA-Enrichment.xlsx), [canonical metadata](data/orcs/ena-enrichment.json),
[manifest](data/orcs/ena-enrichment.manifest.json) and
[source package](data/orcs/ena-enrichment-source/20261014/README.md) preserve native
study metadata and 530 complete run reports, including 16,253 distinct runs.
Three broad collections retain project metadata and hierarchy without expanding
collection-wide children; their child counts are blank. Complete-title search
added 20 candidate associations beyond PMID and saved accession routes. Citation
conflicts and missing identifiers remain explicit; screen attribution is unassessed.
The ENA exporter reuses the existing Python template-preserving writer.

Read the [current specifications](docs/specifications/README.md), [resource planning](docs/resources/README.md), and [documentation index](docs/index.md). Code is [MIT licensed](LICENSE); saved third-party metadata retains [upstream terms](THIRD_PARTY_NOTICES.md).

PMC supplemental enrichment processed all 418 ORCS publications, including 364
with PMCIDs, with no retrieval issues. It retained 2,353 supplementary entries
across 329 publications and 3,895 cloud file records, including 2,233 without an
exact supplementary-entry match. The [workbook](data/orcs/PMC-Supplemental-Enrichment.xlsx),
[canonical metadata](data/orcs/pmc-supplemental-enrichment.json) and
[source archive](data/orcs/pmc-supplemental-enrichment/20261028/README.md) preserve
file descriptions, identifiers, links and provenance. These are file inventories,
not confirmed qualifying datasets. See the [independent collector](src/deathmap_ai/pmc_supplemental_collection.py).
Supplemental contents were not downloaded; article prose was not searched.

Publication identifiers can be resolved independently of ORCS using `deathmap-resolve-publication`.

An [offline enrichment synthesis pilot](data/orcs/enrichment-runs/20261018/README.md) connects
saved repository records through persistent publication indices. It preserves
repository metadata separately and never launches enrichment automatically.

The [complete ORCS enrichment workflow](data/orcs/enrichment-runs/20261018/README.md) is available as independently runnable Python stages (deathmap-enrichment-stage). It produces PubMed, GEO, ArrayExpress and ENA workbooks, then fills the registered synthesis template from saved canonical results. The portable exporter requires no ChatGPT, Codex or Node runtime. See [the 2026-10-18 complete run](data/orcs/enrichment-runs/20261018/README.md).
