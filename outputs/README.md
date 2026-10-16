# Search outputs
Use <resource>/<search-name>/<run-id>/ for each execution. A run directory keeps its result JSON, workbook, input snapshots, provenance and verification together.

The [curated ORCS runs](orcs/README.md) are preserved unchanged. New runs receive new IDs; they do not overwrite previous results. OmicsDI discovery is retired.

Historical output iterations are excluded from the curated release. Shared GEO
databases and native sources are under `data/orcs`; see the
[GEO collection guide](../docs/geo-orcs-enrichment.md). This folder holds new
working runs, rather than duplicate copies of finalized shared databases.

ENA development pilots and the GEO template-test workspace were archived on 2026-10-16 outside the repository. Final shared enrichment outputs and native evidence remain under data/orcs. Curated ORCS runs remain unchanged. The local cleanup receipt is logs/ena-cleanup-receipt-20261016.json.
