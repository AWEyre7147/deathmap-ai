# DeathMap-AI

Publication and repository metadata enrichment for scientific review of CRISPR
perturbation studies. ORCS is retained as a reference database and a saved
publication cohort, not a supported collection/search product.

## Run locally

Use Python 3.11+ and install with `python -m pip install -e ".[dev]"`.
The maintained enrichments are publication accession resolution, PubMed, PMC,
GEO, ENA, BioStudies, Figshare, Mendeley Data and institutional library collection.
The library controller additionally requires Node, Playwright and Chrome; its
current institutional adapter uses OSU access. Publisher article routing is part
of that collector, not an independent publisher API enrichment stage.

Read the [enrichment guides](<docs/development/v02 - ORCS Pilot Enrichment/README.md>)
for commands/options and the [documentation index](docs/index.md) for project
specifications. Commands use explicit saved inputs and new output directories.
No experimental-file contents are downloaded.

## Reference data and evidence

[data/orcs](data/orcs/README.md) preserves the publication/screen reference
catalogs, source metadata, enriched workbooks and canonical JSON. Publication and
resource-ID registries remain required for stable cross-resource identities.
[data/icraft](data/icraft/) remains isolated validation material, not a production
query dependency. Field definitions remain in the [ORCS vocabulary](docs/orcs/vocabulary/README.md).

The current library snapshot retains enrichment for 415 of 418 publications,
with three explicit exceptions. Publication association does not establish which
dataset contains a qualifying screen. Missing/conflicting links remain evidence.

## Synthesis and planned evaluation

Offline synthesis combines saved PubMed, PMC, GEO, ENA, BioStudies, Figshare,
Mendeley Data and Library metadata through the registered 28-sheet
template. The final workbook is `data/orcs/Enrichment-Synthesis.xlsx`, accompanied
by `enrichment-synthesis.json.gz` and `Enrichment-Synthesis.manifest.json`.
See the [synthesis guide](docs/enrichment-synthesis.md) for reproducible usage and
coverage limits. Superseded previews have been removed; the legacy four-source
template is archived for historical projections.

The owner's planned evaluation uses enriched ORCS reference evidence to develop
screen-selection rules, compare with ICRAFT, and investigate qualifying studies
after 2022. Rules, evaluation protocol and additional publication discovery are
future work. Enriching ORCS alone cannot establish coverage of papers absent from
that reference. No evaluation or new retrieval is started by repository cleanup.

[MIT license](LICENSE); third-party metadata retains [upstream terms](THIRD_PARTY_NOTICES.md).
