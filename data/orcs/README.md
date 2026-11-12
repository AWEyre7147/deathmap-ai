# ORCS reference data and saved enrichment

ORCS is a reference database and saved enrichment cohort. Collection, filtered
search profiles and the former search-output workflow are retired. Existing
native metadata, accessions and persistent publication identities are preserved.

## Reference catalogs

| File | Purpose |
| --- | --- |
| `publication-index.json` | Saved ORCS publication metadata and supported publication identifiers. |
| `screen-index.json` | Native ORCS screen metadata; a native screen is not automatically a qualifying downstream screen. |
| `publication-screen-links.json` | Explicit reference publication/screen memberships. |
| `ORCS Database.xlsx` | Readable publication, screen and relationship views. |
| `enrichment-publication-registry.json` | Persistent Publication Index crosswalk; retain across cohorts/runs. |
| `publication-source/`, `raw/` | Original source metadata, receipts and CSV views. |

Native ORCS publication IDs identify ORCS pages, not repository datasets.
Equal-looking publication indices from different cohorts do not establish identity.
Original source fields and missing/conflicting assertions remain separate.

## Maintained enrichment outputs

| Resource | Shared canonical file / workbook |
| --- | --- |
| PubMed | `pubmed-enrichment.json.gz` / `PubMed-Enrichment.xlsx` |
| PMC | `pmc-enrichment.json.gz` / `PMC-Enrichment.xlsx` |
| GEO | `geo-enrichment.json.gz` / `GEO-Enrichment.xlsx` |
| ENA | `ena-enrichment.json.gz` / `ENA-Enrichment.xlsx` |
| BioStudies | `biostudies-enrichment.json.gz` / `BioStudies-Enrichment.xlsx` |
| Figshare | `figshare-enrichment.json.gz` / `Figshare-Enrichment.xlsx` |
| Mendeley Data | `mendeley-data-enrichment.json.gz` / `Mendeley-Data-Enrichment.xlsx`; saved source run in `mendeley-data-enrichment/run-20261107-title-complete/`. |
| Library | `library-enrichment.json.gz` / `Library-Enrichment.xlsx`; separate status/checkpoint in `library-enrichment/run-20261112/`. |

Resource source-run folders retain native evidence and provenance. Original
PubMed batches in `pubmed-enrichment-source/` remain eligible GEO cache inputs.
`enrichment-runs/` retains completed historical synthesis/source bundles;
`biostudies-migration/` preserves the compressed ArrayExpress replacement evidence.
These are saved evidence, not enabled ORCS collection/search commands.

The separate resource registry is
[../identifiers/supplemental-index-registry.json](../identifiers/supplemental-index-registry.json).
Retired ID allocations remain reserved so old references cannot be reassigned.

## Use and limits

See the [enrichment guides](<../../docs/development/v02 - ORCS Pilot Enrichment/README.md>).
JSON is the machine-readable source; Excel is a derived review view. Repository
associations, file links and counts do not establish qualifying screen content,
ownership or exhaustive coverage. Experimental files were not downloaded.

The completed eight-source synthesis is `Enrichment-Synthesis.xlsx`: 418
publications, one master and 27 source sheets. `enrichment-synthesis.json.gz`
preserves the canonical tables; `Enrichment-Synthesis.manifest.json` records
source hashes, unresolved retrieval issues and export verification.
The supplied 28-sheet template
is registered as `Enrichment-Synthesis-Template.xlsx`.

Standalone publisher API outputs are retired in favor of the library workflow.
Superseded synthesis previews and intermediate exports are removed. Retired code, search outputs,
logs and historical cleanup archives have been removed from this repository;
recovery material is external and is not a runtime dependency.

Shared enrichment JSON uses gzip. See the [compression options](../../docs/enrichment-synthesis.md#compressed-enrichment-json) for `--compress-json` and reader support.

## Local source workspaces

All subfolders except `raw/` are excluded from Git. They remain on disk as
source evidence, response caches and checkpoints for reproducing or diagnosing
enrichment runs. Top-level workbooks, compressed canonical JSON, manifests and
reference catalogs remain versioned. Normal reuse of those canonical outputs
does not require the source-run folders; an exact source-level rebuild may.
A fresh clone does not include the ignored evidence, and manifest paths into
those folders refer to locally retained material.
