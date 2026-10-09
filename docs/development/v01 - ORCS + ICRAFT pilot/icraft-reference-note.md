# ICRAFT CRISPR reference presence in the ORCS snapshot

This note preserves the reference comparison already made from the uploaded ICRAFT materials and the supplied ORCS snapshot. It is not an execution report for the next pipeline run, and the reference sets must not be loaded by the discovery pipeline.

## Reference presence

| Reference condition            |       Reference units | Identified PMID publications | Publications present in ORCS | Reference units associated with those publications |
| ------------------------------ | --------------------: | ---------------------------: | ---------------------------: | -------------------------------------------------: |
| Supplemental Table S1 (`mmc2`) |       558 screen rows |                           90 |                           33 |                                    194 screen rows |
| Website screen metadata        |       544 screen rows |                           89 |                           33 |                                    193 screen rows |
| Supplied public-file inventory | 65 count-file bundles |                           43 |                           18 |                              36 count-file bundles |

The 33 reference publications present in ORCS have 152 ORCS screen records between them. ORCS screen records, ICRAFT supplemental screen rows, and count-file bundles are different units; a publication match does not establish screen-to-dataset equivalence.

## Reporting boundaries

- **Publication representation**: a tangible demonstration of what the output contains.
- **No formal recall score**: this is an ORCS pilot, not a held-out validation.
- **Extra candidates**: welcome; absence from ICRAFT does not imply irrelevance.
- **No access claims**: filenames in the inventory do not verify downloads, archive contents, or repository accessibility.
- **No pipeline benchmark**: reference matching and the scientific summary remain follow-up work.
