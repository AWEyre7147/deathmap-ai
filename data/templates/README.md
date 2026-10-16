# Excel template

`DeathMap-AI-output.xlsx` is the owner-finalized, repaired main template. `DeathMap-AI-output-backup.xlsx` is a byte-identical backup. The active manifest records its hash; changes require registration before export.

The ORCS search command exports `workbook-authored.xlsx` automatically into each new run directory using Python/openpyxl. Existing outputs are refused. Column styles preserve owner coloring when body rows are blank. `owner-change-catalog.json` records the original-to-final comparison. Superseded models and proposal materials are archived externally with hashes.

Sources-sheet example counts are illustrative; use run summaries for measured counts. Template opening was confirmed by the owner; generated exports need their own Excel opening check.

## Repository enrichment templates

`GEO-Enrichment.xlsx` is the owner-approved four-sheet template: Series Records,
Series Hierarchy, Repository Identifiers and Sample Metadata. Discovery Evidence
is excluded from this workbook; native responses and evidence remain in saved
metadata pending the v02 evidence-compilation design. Its byte-for-byte hash,
ordered headers and projected-record mappings are registered in
`GEO-Enrichment.manifest.json`.

`PubMed-Enrichment.xlsx` retains its five sheets and existing columns, with the
same plain formatting as GEO: bold headers, uniform widths and no decorative
fills or Excel table objects. Its regenerated manifest records the current hash,
ordered headers and canonical row positions. Publication dates retain literal
text `MM;DD;YYYY`, partial `MM;YYYY` or `YYYY`.

`deathmap_ai.geo_workbook.export_workbook` validates the registered template and
field mappings, then populates a fresh workbook from projected metadata tables.
It reuses the XML-preserving writer in `pubmed_workbook`; body cells follow the
template default style. Missing values stay blank; existing output paths are
refused. Owner template changes need registration before GEO export.

Active templates and registration manifests remain here. Their recorded hashes
and field mappings define the inputs accepted by the workbook exporters.

`BioStudies-ArrayExpress-Enrichment.xlsx` is the owner-approved blank eight-sheet
template registered in `BioStudies-ArrayExpress-Enrichment.manifest.json`.
It retains the selected Studies fields and repository metadata sheets, excludes
Publication links, External links and Other metadata, and removes the specified
display columns. SDRF retains individual sample/assay fields through Part; IDF
retains fields through Original value. Formatting matches the plain PubMed
template, with no tables or filters. The manifest
records the unchanged workbook hash, ordered headers and projected-record keys.
Canonical source evidence remains separate. Registration does not itself run
whole-ORCS enrichment or implement the ArrayExpress exporter.

`ENA-Enrichment.xlsx` is the owner-selected seven-sheet template, registered in
`ENA-Enrichment.manifest.json`: Studies, Publications, Study hierarchy, Samples,
Experiments, Runs and File listings. Search PMID and ENA PMID remain distinct.
Experiments and Runs retain ENA's native terminology and do not imply qualifying
CRISPR screens. The template is unchanged by population; omitted broad-project
child counts stay blank and their scope decisions remain in canonical evidence.
