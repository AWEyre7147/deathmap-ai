# ICRAFT CRISPR reference presence in the ORCS snapshot

This note preserves the reference comparison already made from the uploaded ICRAFT materials and the supplied ORCS snapshot. It is not an execution report for the next pipeline run, and the reference sets must not be loaded by the discovery pipeline.

## Reference presence

| Reference condition | Reference units | Identified PMID publications | Publications present in ORCS | Reference units associated with those publications |
|---|---:|---:|---:|---:|
| Supplemental Table S1 (`mmc2`) | 558 screen rows | 90 | 33 | 194 screen rows |
| Website screen metadata | 544 screen rows | 89 | 33 | 193 screen rows |
| Supplied public-file inventory | 65 count-file bundles | 43 | 18 | 36 count-file bundles |

The 33 reference publications present in ORCS have 152 ORCS screen records between them. ORCS screen records, ICRAFT supplemental screen rows, and count-file bundles are different units; a publication match does not establish screen-to-dataset equivalence.

Four in-house supplemental rows have no PMID and remain unresolved at the publication level. The inventory's `New Text Document.txt` is not a CRISPR dataset; excluding it leaves 65 count-file bundles.

## How this will be used

After the owner supplies the next pipeline output, Perplexity will compare its publication identifiers with these reference sets. It will report which publications are represented, which are missing from the filtered output, and which reference publications were not present in the ORCS snapshot in the first place.

The existing cancer-cell CRISPR search is narrower than the full ICRAFT collection, which also includes immune-edited and other experimental models. Missing references can therefore be explained as scope or metadata limitations without changing the search.

No capture count is specified for the next run. In particular, the earlier “all 33 captured” result belongs to the superseded broader biological-class evaluator and is not an expected outcome or acceptance criterion for this unchanged search.

## Reporting boundaries

- **Publication representation**: a tangible demonstration of what the output contains.
- **No formal recall score**: this is an ORCS pilot, not a held-out validation.
- **Extra candidates**: welcome; absence from ICRAFT does not imply irrelevance.
- **No access claims**: filenames in the inventory do not verify downloads, archive contents, or repository accessibility.
- **No pipeline benchmark**: reference matching and the scientific summary remain Perplexity's follow-up work.

The source comparison used `mmc2` Table S1 rows 3–560, ICRAFT website metadata saved on 2026-10-04, the supplied `ICRAFT-dataset-file-report.md`, and the supplied ORCS indexes. No fresh ORCS release or experimental data retrieval is required for the planned run.
