# GitHub preparation — PubMed milestone, 2026-10-08

The PubMed milestone is complete and curated files are prepared for owner
review before committing and pushing. The owner authorized commit and push
after resolved-error cleanup on October 8. The checkout contained broader ORCS/documentation
changes before this work; those changes have been preserved.

## Included milestone deliverables

- Final `data/templates/PubMed-Enrichment.xlsx` and its manifest.
- Shared `data/orcs/pubmed-enrichment.json`, Excel view and manifests.
- Native NCBI batches and URL/date/hash receipts under
  `data/orcs/pubmed-enrichment-source/20261008/`.
- An enrichment workbook and manifest inside each retained ORCS run.
- Reusable modules, focused tests, milestone report and usage documentation.

The batches contain publication metadata and repository summaries, not
full-text articles or experimental data. Third-party content retains upstream
terms; see [third-party notices](../THIRD_PARTY_NOTICES.md).

## Verification and cleanup

Four focused fixture tests passed. Every workbook row matched its expected
projection; namespace and template preservation checks passed. All four
workbooks opened normally in Excel, and five sheet previews of the shared
workbook were inspected. One enrichment pass and one four-workbook export pass
completed; no ORCS rebuild occurred.

Final code-commenting updates changed docstrings only. Executed source snapshots
are retained with their original hashes, and current executable ASTs were
verified equal without another retrieval/export. Current documentation hashes
are recorded separately; original run provenance was not rewritten.

Superseded experiments and template versions were removed from the active tree
after a verified byte-preserving archive. The [cleanup receipt](development/v02%20-%20ORCS%20Pilot%20Enrichment/pubmed-cleanup-receipt.json)
records paths and hashes. The external archive is recovery material; active
reproduction does not depend on it. Temporary authoring support is excluded
from Git. Public response batches are retained for offline reproducibility.

## Remaining boundaries

Three ORCS publications have no verified PMID and remain unresolved. Direct
PubMed links do not establish complete repository coverage or qualifying
screen-dataset attribution. GEO, BioStudies–ArrayExpress and ENA enrichment are
the next separately scoped goals. See [the PubMed milestone](development/v02%20-%20ORCS%20Pilot%20Enrichment/pubmed-milestone.md).

Resolved error details have been archived, and current readiness records show
no remaining workbook-hash mismatch. Archive and rerun receipts are retained.

The earlier biological-classes ORCS workbook mismatch was resolved by an
owner-requested offline rerun. The edited run is preserved in a verified archive,
and its active copy was replaced by `20261009T000854143096Z` (UTC run identifier;
generated October 8 locally). Its PubMed view was regenerated from the existing
database without retrieval. All three active ORCS workbook/projection pairs now
match their export receipts. Both replacement workbooks opened normally in
Excel. See [the rerun receipt](development/v02%20-%20ORCS%20Pilot%20Enrichment/biological-classes-rerun-20261008.json).
