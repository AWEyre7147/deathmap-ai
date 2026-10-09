# Completed PubMed enrichment milestone — 2026-10-08

The owner approved the semicolon text-date template and authorized the full
ORCS publication-index enrichment plus views for each retained ORCS search.
This is a completed metadata subgoal within v02, not completion of native
repository enrichment or screen-dataset attribution.

| Output | ORCS publications | Retrieved PMIDs | Unresolved |
|---|---:|---:|---:|
| Shared ORCS catalog | 418 | 415 | 3 |
| Cancer-cell knockout v01 | 93 | 93 | 0 |
| Cancer-cell knockout v02 | 231 | 230 | 1 |
| Biological-classes pilot v01 | 328 | 327 | 1 |

One shared pass made 90 successful requests. All 415 selected PMIDs were
returned. Distinct linked native records: GEO 272, BioProject 286, SRA 5,101.
The database has 572 publication-repository rows representing 558 distinct
repository records, 5,822 SRA accession rows, 2,781 MeSH descriptor/qualifier
pairs and 6,724 publication-specific MeSH links. Row counts exceed native
record counts when publications share a record or an experiment has multiple
runs. These counts describe returned direct associations, not adjudicated
repository coverage or qualifying-screen availability.

The three unresolved shared-index records are ORCS PUBLICATION_ID 657, 842 and
1054. No PMID was invented, and preprint identity was not inferred from titles.
Unresolved entries remain in the database mapping and output manifests.

The final template is at `data/templates/PubMed-Enrichment.xlsx`. The shared
JSON database, Excel view and manifest are in `data/orcs/`. Each current ORCS
run has a separate `pubmed-enrichment/` workbook and receipt. ORCS projections
and owner-authored ORCS workbooks remain unchanged. Source batch responses,
URLs, hashes and timestamps are retained under
`data/orcs/pubmed-enrichment-source/20261008/`.

Verification: four focused fixture checks passed; every exported row matched
its expected subset; template headers, widths, panes and unrelated package
parts were preserved; namespace checks passed; all four workbooks opened
normally in native Excel with Text-formatted dates; all five sheet previews of
the shared workbook were inspected. One full export pass generated the four
workbooks. No ORCS rebuild or experimental-file download occurred.

Superseded template-development and one-/ten-publication artifacts are preserved
in the external archive identified by [the cleanup receipt](pubmed-cleanup-receipt.json),
with unchanged bytes and per-file hashes. The archive is local recovery material
and is not a GitHub dependency. Active reproduction uses retained native batch
responses, the final template and production modules.

The next goals are GEO, BioStudies–ArrayExpress and ENA repository-specific
enrichment. The learning checkpoint is to inspect their hierarchy, matching
and attribution contracts using the PubMed associations before implementing
those passes. Direct PubMed links can miss a GEO SubSeries with no citation;
GSE72841 remains an example for later hierarchy review. No new native repository
pass is authorized by this completed milestone.

See [usage and retrieval details](../../pubmed-enrichment.md) and
[GitHub preparation status](../../github-preparation.md). No commit, push or
pull request was made.

The owner-requested biological-classes rerun replaced the edited run and
regenerated its PubMed view from saved metadata. All current ORCS workbooks and
projections match their export receipts. Resolved error details are archived;
the rerun and archive receipts retain provenance.
