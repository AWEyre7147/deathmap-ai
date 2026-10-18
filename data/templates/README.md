# Excel templates

`DeathMap-AI-output.xlsx` is the owner-finalized main ORCS search template.
`DeathMap-AI-output-backup.xlsx` is its byte-identical backup. The active
`current-template.json` and `owner-change-catalog.json` register that workbook;
this template and its reference sheets are unchanged by enrichment consolidation.
ORCS search exports use Python/openpyxl and refuse existing output workbooks.
Sources-sheet example counts are illustrative, not measured run counts.

## Repository enrichment templates

The four current, owner-approved enrichment templates and registration manifests
are directly in this folder. They are the same workbook bytes previously used
from the review-v2 folder; the maintained commands now select these main paths.

- `PubMed-Enrichment.xlsx`: five metadata/link/MeSH sheets; complete publication
  dates use literal YYYY-MM-DD and partial dates retain reported precision.
- `GEO-Enrichment.xlsx`: four sheets; excludes citation and places Identifier and
  GSM immediately after PMID in their respective tables.
- `ENA-Enrichment.xlsx`: seven sheets, including File listings. The study table
  excludes Search PMID, ENA PMID, Native record type and Source URL. Experiments
  and Runs retain ENA's native terminology.
- `BioStudies-ArrayExpress-Enrichment.xlsx`: eight sheets. Protocol, sample and
  assay fields are pivoted to columns at native record level; contact attributes
  and Value state are excluded from those review tables. IDF/SDRF remain retained.

Each adjacent `.manifest.json` registers the workbook SHA-256, exact sheet/header
order and source-field mappings. The portable exporters validate that registration
and compare saved values against their projected tables. Missing values remain
blank, native numeric/Boolean values retain their types, and metadata text is not
executed as formulas. Existing outputs are refused. Omitted workbook fields remain
in canonical evidence; publication association is not qualifying screen attribution.

## Final combined enrichment output

[Enrichment-Synthesis.xlsx](Enrichment-Synthesis.xlsx) is the approved header-only
21-sheet combined review template. Its [manifest](Enrichment-Synthesis.manifest.json)
registers 209 columns, source mappings, Publication Index links, display aliases,
date convention and hash. The ORCS search, resource-specific and combined templates
retain distinct purposes. See [the complete workflow](../../docs/complete-enrichment.md).

## Historical template preservation

[Template history](template-history-20261018.zip) preserves the earlier default
workbooks/registrations and the original review-v2 files byte-for-byte. The
[history receipt](template-history-20261018.manifest.json) records original paths,
ZIP members, hashes and approved-template relocations. Extract it into a separate
working directory when a historical export requires its original schema; current
commands do not depend on the ZIP or the retired review-v2 directory.

Existing populated workbooks, historical execution manifests and source-code
snapshots retain their original bytes and paths as scientific provenance. Changing
a template's location does not require a new enrichment run or production export.
