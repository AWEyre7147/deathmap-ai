# Excel templates

The active main output template is `DeathMap-AI-output.xlsx`; its recovery copy
is `DeathMap-AI-output-backup.xlsx`. `current-template.json` points to the main
workbook and its column manifest.

Enrichment templates and their adjacent manifests are in this folder:

- `PubMed-Enrichment.xlsx`
- `GEO-Enrichment.xlsx`
- `ENA-Enrichment.xlsx`
- `BioStudies-ArrayExpress-Enrichment.xlsx`
- `PMC-Supplemental-Enrichment.xlsx`
- `Enrichment-Synthesis.xlsx`

Column headings use readable Title Case with standard acronyms. Manifests retain
canonical source keys separately from display labels, plus sheet/column order
and workbook hashes. Duplicate capitalization variants share one column; source mappings retain the
original keys and distinct reported values. Blank values remain blank.

Templates do not trigger retrieval. PMC supplemental projection and the final
ICRAFT pilot run are separate work. Existing populated outputs are unchanged.

`template-history-20261018.zip` contains historical templates;
`template-history-20261018.manifest.json` records their original paths and hashes.
The active manifests describe the current template mappings.
