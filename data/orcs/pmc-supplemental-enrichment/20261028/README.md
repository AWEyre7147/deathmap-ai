# PMC supplemental source evidence

The completed 2026-10-28 ORCS run processed 418 publications (364 with PMCIDs)
with no retrieval issues. Current outputs are the [workbook](../../PMC-Supplemental-Enrichment.xlsx)
and [canonical metadata](../../pmc-supplemental-enrichment.json).

`source-material.zip` preserves exact native XML/cloud metadata responses and
request receipts, selected publications, the summary, and snapshots of the input,
registry, template and exporter code. The adjacent manifest records every member
hash and the archive hash. Each receipt/body pair was hash-verified after packaging.
Native receipts retain retrieval dates across interrupted and resumed executions.

Extract the archive to a local directory and supply that directory as `--cache-root`
to the [collector](../../../../src/deathmap_ai/pmc_supplemental_collection.py) for response reuse.
Raw article XML is retained as source evidence; prose was not searched. No media or
supplemental contents were downloaded. Article XML and author-supplied descriptions
retain upstream terms and article-specific licenses; see the project notices.

Local checkpoints, duplicate exports and superseded partial results are excluded
from Git. The external ICRAFT validation cohort remains local as before.
