# Complete ORCS enrichment — 2026-10-18

Completed all 418 ORCS publications using independently runnable repository stages followed by offline synthesis. See [workflow](../../../../docs/complete-enrichment.md).

## Review workbooks

- [Final synthesis](synthesis/Enrichment-Synthesis.xlsx): 21 sheets, 418 publications, 1,390 publication–repository links.
- [PubMed](pubmed/PubMed-Enrichment.xlsx): 415 PMIDs; three publications without PMIDs retained in the publication registry and synthesis.
- [GEO](geo/GEO-Enrichment.xlsx): 503 distinct Series and 22,139 distinct samples.
- [ArrayExpress](arrayexpress/BioStudies-ArrayExpress-Enrichment.xlsx): 10 studies.
- [ENA](ena/ENA-Enrichment.xlsx): 533 study/project records and 16,253 distinct runs. Three accepted broad projects remain project-only.

## Verification and preservation

33 focused tests passed. All five workbooks were independently compared with their projected values: 3,891,845 body cells. Source and output hashes are recorded in manifests; verification.json records final checks. Native Excel application opening was not tested.

One GEO membership list exceeds Excel's cell limit. Its cell explicitly references record 1 in synthesis/Enrichment-Synthesis.overflow.json.gz, which preserves the full value. Canonical synthesis is also retained in synthesis/synthesis.json.gz. No value was silently truncated.

Cache reuse preserved original retrieval dates. Live requests comprised 214 GEO metadata requests and two ENA title-search requests. No unresolved retrieval failures remain. No experimental files were downloaded.

The initial synthesis export stopped at oversized-cell preflight; the completed canonical synthesis was then exported offline with overflow preservation. No resource stage or synthesis projection was repeated.

Raw intermediate ena/database.json (112,224,254 bytes) and geo/workbook-data.json (169,041,923 bytes) remain preserved. Future GitHub preparation should address these large files explicitly before staging. No commit or push was performed.

Publication indices are stable within the maintained enrichment registry. Legacy ORCS search workbooks have run-local indices; crosswalk those by native ORCS publication ID or PMID, not the identical-looking PUB string.

## Release storage — 2026-10-18

Resource source material is now preserved byte-for-byte in [source-material.zip](source-material.zip), with original relative paths and SHA-256 values in [its manifest](source-material.manifest.json). The four resource workbooks and their receipts remain directly available, as do the final synthesis workbook and compressed canonical evidence. Historical execution manifests retain their original hashes and source paths. Restore the ZIP into this folder before replaying source-database operations; see the [restore instructions](../../../../docs/complete-enrichment.md#restoring-the-packaged-completed-run). Offline export from synthesis/synthesis.json.gz requires no restore.

The previously noted 112 MB ENA database and 169 MB GEO projection are included losslessly in this bundle, together with the other source payloads. They are not discarded. No retrieval or scientific projection was repeated during release preparation. Superseded development pilots and the earlier generated ICRAFT package were externally archived; the owner's four curated ICRAFT reviewer workbooks remain local and unchanged.

The approved resource templates were subsequently consolidated into data/templates without changing their workbook bytes or mappings. Historical template paths in this run's execution receipts refer to the originals preserved in data/templates/template-history-20261018.zip. Current maintained commands select the consolidated paths; this organizational change did not rerun the completed enrichment or export.
