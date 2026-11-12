# Mendeley Data source evidence

This completed title-search run covers 418 publications and records 18 candidate
dataset associations across 16 publications, with 1,817 file records.

Final deliverables are maintained in `data/orcs`:

- [Compressed canonical JSON](../../mendeley-data-enrichment.json.gz)
- [Enrichment workbook](../../Mendeley-Data-Enrichment.xlsx)
- [Verification and provenance manifest](../../Mendeley-Data-Enrichment.manifest.json)

The compressed JSON preserves the original database bytes exactly; its
uncompressed hash is recorded in the shared manifest. The duplicate plain
`database.json` and superseded workbook/manifest have been removed.
`native/`, `requests.json` and `summary.json` retain original source evidence
and retrieval history. The summary's workbook hash describes the original
export; use the shared manifest for the current workbook hash.
