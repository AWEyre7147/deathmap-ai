# Curated ORCS outputs

One identifier-enriched run per condition. Older workbooks are preserved in the verified external archive; no reviewed workbook was rewritten.

| Search | Publications | PMID | DOI | PMCID |
|---|---:|---:|---:|---:|
| [cancer-cell-crispr-knockout-v01](cancer-cell-crispr-knockout-v01/20261008T013854733762Z/workbook-authored.xlsx) | 93 | 93 | 93 | 79 |
| [cancer-cell-crispr-knockout-v02](cancer-cell-crispr-knockout-v02/20261008T013918054722Z/workbook-authored.xlsx) | 231 | 230 | 230 | 198 |
| [orcs-crispr-biological-classes-pilot-v01](orcs-crispr-biological-classes-pilot-v01/20261009T000854143096Z/workbook-authored.xlsx) | 328 | 327 | 327 | 287 |

Exact NCBI publication identifier lookups enrich the shared catalog before searches. Missing identifiers remain blank. Sources-sheet example counts are illustrative; use summary.json for actual screen counts. Publication associations are not screen-dataset attribution.

## PubMed enrichment milestone

Each retained run now has a `pubmed-enrichment/PubMed-Enrichment.xlsx` workbook and manifest. They use the shared `data/orcs/pubmed-enrichment.json` database and do not rerun the ORCS searches. The three workbooks contain 93, 230 and 327 retrieved publications respectively; the latter two each retain one unresolved no-PMID publication in their manifests. MeSH counts and associated PMID lists are recalculated for each subset. See [PubMed enrichment](../../docs/pubmed-enrichment.md).
