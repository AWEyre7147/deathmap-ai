# ORCS Figshare enrichment

Completed November 2, 2026 using the registered Figshare template and linked-publication DOI search only. All 418 ORCS publications are accounted for: 47 with linked items, 370 without linked hits, and one without a DOI. No retrieval issues remain.

The workbook contains Publications (47 rows), Items (553 rows), and Files (584 rows). No-hit inputs remain only in canonical metadata. Metadata comes from public Figshare API search responses and item details; no experimental files were downloaded or inspected. A linked item does not establish qualifying CRISPR screen content.

`database.json` retains publication outcomes, original item metadata and response receipts. `native/` retains exact response bodies and hash receipts. The run resumed from checkpoints after environment interruptions; `requests.json` and the request count in `summary.json` describe the final execution, not cumulative requests across restarts. Original retrieval times remain in the native receipts.

`verification.json` records the checks of native response hashes, exact linked DOI associations, full-cohort coverage, canonical-to-workbook projection, parent relationships and workbook hash. The workbook writer also verified exported cells against the projected values. Stable FGI and FGF indices use the shared supplemental index registry.

The shared workbook, canonical metadata and manifest are in `data/orcs`. Their metadata identifies this run as the native evidence source.
