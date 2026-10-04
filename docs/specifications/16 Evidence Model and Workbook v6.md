# Evidence model and workbook v6

## [EV6-1] Owner-approved scope

The owner accepted A118–A122 on 2026-10-04. Apply this model from ORCS v02 onward; preserve v01 outputs and template v5. No ID map is required unless v01 is separately converted. This supersedes the v5 evidence layout and authorizes changes only to affected glossary entries in a new v6 copy. It does not execute a search or authorize external enrichment.

## [EV6-2] Evidence rows and provenance

Group by source record + supported entity + evidence_basis + evidence_status. Namespace records by resource and native record type. Inferred claims remain separate and cannot be direct. Preserve each grouped observation, its full source record and transformations in the ledger.

Evidence columns, in order: evidence_id, supports_entity_type, supports_entity_id, claim, fields_supported, source_name, source_link, supporting_value, supporting_value_truncated, evidence_basis, evidence_status, reviewer_check, reviewer_note.

Basis values: structured_field, text_quote, text_mined_identifier, inferred, reviewer_assertion, reference_lookup. Status values: direct, indirect, inferred, conflicting, unresolved. Reviewer checks: blank, confirmed, corrected, rejected. Reviewer fields are rightmost and yellow; rows requesting unresolved/conflict review are orange, with status retained in text.

Claims attribute the source and do not upgrade its meaning. ORCS T cell exposure does not by itself establish co-culture eligibility. Grouped claims can refer to the listed fields; individual claims and exact values remain in the ledger.

Use 300 characters as the display target. Abbreviated supporting_value ends with `[…]` and has supporting_value_truncated=true. Preserve the complete value in supporting_value_full. Do not display full native-record JSON, file paths, hashes, precise timestamps or tool versions in Evidence.

Store evidence-ledger.jsonl beside the workbook within the existing per-search run directory. Every workbook evidence_id has exactly one ledger entry with the same entity, claim, basis and status. Retain raw records, URLs/IDs, source field paths, retrieval provenance, file paths, hashes, supported fields, transformations, tool metadata and target joins. IDs are deterministic hashes of the grouping key and do not depend on row order. Historical runs retain their version-specific content.

## [EV6-3] Shared cell-line references

Use entity type cell_line with the primary Cellosaurus accession as its ID. Generate one separate Cellosaurus reference_lookup Evidence entry per resolved accession. Screens carries cellosaurus_accession and can link to the shared evidence ID. Screen-to-annotation targets, reported join keys, match methods, secondary accessions and review issues live in the ledger. Do not nest reference observations in ORCS entries.

The cell_line entity is represented by its Evidence row and ledger entry; no additional Cell Lines sheet is introduced. Multiple ORCS aliases resolving to the same accession share one reference row. Preserve conflicting category observations with conflicting status. A missing accession remains blank and produces an explicit issue, not a guessed entity.

This boundary reduces repetitive reference review while showing that Cellosaurus, rather than ORCS, supplies the cancer-cell classification.

## [EV6-4] Template and preservation

Use data/templates/DeathMap-AI-output-v6.xlsx. It renames Sources & Evidence to Evidence, replaces that sheet's headers, adds Screens.cellosaurus_accession and Publications.evidence_id_link, revises evidence-related glossary rows, and adds definitions for the new fields and Cell line entity. Preserve all other entries, Reviewer Tasks, separators and Sources.

The Sources policy still awaits owner clarification. Its existing example counts are preserved and are not measured run results; the adapter records this limitation.

Artifact Tool authors edits and previews but changes unrelated formatting during export. The preservation pass transplants only authorized edits into the original XLSX package, retaining original styles, dimensions, table names and unaffected parts. Tests compare v6 against v5 and verify fixed-sheet bytes.

## [EV6-5] Implemented output stage

evidence_model.py implements grouping, display truncation, ledger writing and validation. orcs_evidence_v6.py adapts local v02+ projections; export_evidence_workbook_v6.mjs exports the workbook. Existing projections are snapshotted byte-for-byte as source-projection.json, preserving old diagnostics, evidence and reviewer fields. No existing run is overwritten.

Given a completed v02+ run with projection.json, run_manifest.json, profile.json and reference_annotations.json:

```powershell
python -m deathmap_ai.orcs_evidence_v6 --run outputs/orcs/cancer-cell-crispr-knockout-v02/<run-id> --output outputs/orcs/cancer-cell-crispr-knockout-v02/<run-id>/workbook-v6
node scripts/export_evidence_workbook_v6.mjs outputs/orcs/cancer-cell-crispr-knockout-v02/<run-id>/workbook-v6
```

Use bundled Python/Node with ARTIFACT_NODE_MODULES and BUNDLED_PYTHON set to their bundled paths. Use the new exporter, not the historical v01 exporter. The v02 filter profile remains configuration-only: its filtering runner must be implemented separately before a real v02 result exists. The fixture export is a software check, not scientific search results.

Learning checkpoint: a shared reference entity eliminates duplicate cell-line evidence while retaining every screen's independent reference join in the ledger.
