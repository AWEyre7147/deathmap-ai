# Saved ORCS reference annotations
[orcs-annotations](orcs-annotations/README.md) contains the full saved ORCS vocabulary annotation bundle: Cellosaurus cell-line categories/accessions, BTO/CL/EFO cell-type references, raw provider references, receipts and screen-page metadata excerpts.

The directory name identifies the principal cell-line reference; ontology facts retain their own provider identities. Never relabel BTO, CL or EFO definitions as Cellosaurus facts. No reference was refreshed during organization.

Human-facing annotation guides live in docs/orcs/vocabulary/screen; the saved JSON remains the filtering input. Filtering uses the saved annotations.json and an exact CELL_LINE-to-value join. Missing categories are unresolved, not automatically non-cancer.
