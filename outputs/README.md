# Search outputs
Use <resource>/<search-name>/<run-id>/ for each execution. A run directory keeps its result JSON, workbook, input snapshots, provenance and verification together.

The [curated ORCS runs](orcs/README.md) are preserved unchanged. New runs receive new IDs; they do not overwrite previous results. OmicsDI discovery is retired.

Historical output iterations are excluded from the curated release. Shared GEO
databases and native sources are under `data/orcs`; see the
[GEO collection guide](../docs/geo-orcs-enrichment.md). This folder holds new
working runs, rather than duplicate copies of finalized shared databases.
