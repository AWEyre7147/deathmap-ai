# Enrichment synthesis

Consolidates the eight saved enrichment sources into the owner's registered
28-sheet workbook. The first sheet gives a publication-level view; the other
27 sheets retain resource-specific records. It performs no retrieval or
scientific dataset merging.

## Enrichment process

Load PubMed, PMC, GEO, ENA, BioStudies, Figshare, Mendeley Data and Library
canonical JSON files. Join the publication registry, retain source identifiers
and count distinct resource identifiers per publication. Export through the
registered template and verify every written cell. All source files and the
persistent identifier registry remain unchanged.

## Script and usage

Module: `deathmap_ai.enrichment_consolidation` (installed command:
`deathmap-synthesize-enrichment`). Example for the saved reference cohort:

```powershell
python -m deathmap_ai.enrichment_consolidation `
  --publication-index data/orcs/publication-index.json `
  --registry data/orcs/enrichment-publication-registry.json `
  --index-registry data/identifiers/supplemental-index-registry.json `
  --source PubMed=data/orcs/pubmed-enrichment.json.gz `
  --source PMC=data/orcs/pmc-enrichment.json.gz `
  --source GEO=data/orcs/geo-enrichment.json.gz `
  --source ENA=data/orcs/ena-enrichment.json.gz `
  --source BioStudies=data/orcs/biostudies-enrichment.json.gz `
  --source Figshare=data/orcs/figshare-enrichment.json.gz `
  --source Mendeley=data/orcs/mendeley-data-enrichment.json.gz `
  --source Library=data/orcs/library-enrichment.json.gz `
  --template data/templates/Enrichment-Synthesis-Template.xlsx `
  --output-dir data/orcs/enrichment-synthesis/NEW-RUN
```

All eight sources and a nonexisting output directory are required. Inputs must
belong to the selected cohort and have compatible saved schemas. GEO indices
reproduce the source export's accession-sorted projection. Sources containing
unresolved retrieval issues are included as saved observations; their issues
and status accompany the canonical output and receipt.

## Additional information

The final reference-cohort deliverables are `data/orcs/Enrichment-Synthesis.xlsx`,
`data/orcs/enrichment-synthesis.json.gz` and
`data/orcs/Enrichment-Synthesis.manifest.json`. The manifest records source
paths/hashes, unresolved issues and verification results. CLI runs produce
`synthesis.json.gz` and a stage receipt in a new output directory; these are
promoted into the final filenames after verification.
Values exceeding Excel's cell limit are retained in an explicit overflow
sidecar. Re-export the saved canonical JSON with `deathmap_ai.enrichment_export`
and the same registered template.

The workbook is a review deliverable. Downstream software can consume the
versioned canonical tables and source references; registering a workbook alone
does not implement a downstream screen-curation contract.

## Key findings

- PubMed Records is a retrieved-publication indicator (0 or 1). Other master
  counts use distinct source resource IDs, not duplicate association rows.
- Zero means no saved record; it does not establish absence. Source retrieval
  gaps remain unresolved by consolidation.
- Cross-resource observations are kept separate. Matching publication
  membership does not establish dataset equivalence or screen attribution.
- Publication dates retain PubMed precision. Master journal names use the
  reference catalog. Mendeley's Page Size means the returned page size.
- The supplied header spellings and spacing are preserved through manifest
  aliases. The legacy four-source template remains separately reproducible.

The workbook preserves template header colors, column widths, body fonts,
alignment and wrapping. Superseded synthesis previews and run copies are
removed after promotion; all eight authoritative enrichment sources remain.

## Compressed enrichment JSON

The eight shared resource databases directly in `data/orcs` now use `.json.gz`.
Plain copies were removed after exact-byte round-trip checks. Source-run
snapshots, manifests, registries and reference catalogs retain their formats.
The synthesis is also compressed. Native source evidence remains available. Redundant Mendeley source-run
exports are replaced by the shared outputs, with a pointer in the run folder.

Readers accept plain or gzip JSON. A missing `.json` path also resolves its
`.json.gz` replacement. Manifests preserve the original uncompressed hash and
record the compressed storage hash.

Add `--compress-json` to `python -m deathmap_ai.enrichment_commands` to compress
the completed canonical output, update its manifest and remove the plain copy.
The option leaves source responses and checkpoints intact. Without the option,
existing output behavior is unchanged; synthesis already writes gzip.

For a standalone collector, run:

```powershell
python -m deathmap_ai.json_storage path/to/database.json --remove-original
```

This utility verifies the bytes and reports both hashes. Update separately
maintained manifests when promoting its output; the shared pipeline option
updates its own export manifests automatically.
