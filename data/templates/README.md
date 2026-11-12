# Registered enrichment templates

Each active workbook has an adjacent manifest defining its exact hash, sheets,
column order and canonical source mappings. Existing owner-edited files are not
overwritten. Templates do not trigger retrieval.

- PubMed-Enrichment-Template.xlsx
- PMC-Enrichment-Template.xlsx
- GEO-Enrichment-Template.xlsx
- ENA-Enrichment-Template.xlsx
- BioStudies-Enrichment-Template.xlsx
- Figshare-Enrichment-Template.xlsx
- Mendeley-Data-Enrichment-Template.xlsx
- Library-Enrichment-Template.xlsx
- Enrichment-Synthesis-Template.xlsx

`Enrichment-Synthesis-Template.xlsx` is the registered 28-sheet, eight-source
synthesis template supplied by the owner. Use `enrichment_consolidation` with
this template. Its exact spelling, layout and workbook bytes are preserved;
the manifest maps renamed fields and header typos to the source keys.
The legacy four-source registration is archived under
`history/synthesis-four-source/` for historical projections.
The old ORCS search/evidence output templates and standalone publisher template
are retired, with their original bytes retained outside the repository.

The Library template preserves the supplied `Contex Index` header through its
manifest alias to `Context Index`, and plural `Supporting Materials Index` maps
to the canonical singular field. Provenance and operational status remain
separate from its four review sheets.

GEO/ENA resource indices identify native entities; repeated publication/study
memberships are not additional independent entities. Full mappings remain in the
registered manifests. See the [enrichment guides](<../../docs/development/v02 - ORCS Pilot Enrichment/README.md>)
for each collector's interpretation and limitations.

The [synthesis guide](../../docs/enrichment-synthesis.md) documents the final
28-sheet workbook and reproducible offline consolidation.
