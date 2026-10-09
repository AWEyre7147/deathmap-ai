# ORCS v02 run preparation

Current update, 2026-10-07: [handoff 17](../../../docs/development/v02%20-%20ORCS%20Pilot%20Enrichment/specification-history/18%20Repository%20Native%20Discovery%20Release%20Preparation.md) authorizes and resolves the offline implementation below. The shared profile runner now supports this configuration; use `python -m deathmap_ai.orcs_crispr_pilot --profile searches/orcs/cancer-cell-crispr-knockout-v02/profile.json`. The supplied profile is unchanged. See `outputs/orcs/README.md` for the verified fresh package. The preparation sections below preserve the earlier planning stage.

## [V02-R0] Accepted output evidence model

Use [workbook v6 and its JSONL evidence ledger](../../../docs/development/v02%20-%20ORCS%20Pilot%20Enrichment/specification-history/18%20Repository%20Native%20Discovery%20Release%20Preparation.md) for this and subsequent outputs. The evidence adapter/exporter are implemented and fixture-verified; this does not implement or execute the v02 filtering runner below. Preserve v01 outputs without an ID map.
## [V02-R1] Purpose
Prepare the owner-defined profile.json for a separate next ORCS search. This document records implementation requirements, not a completed run or an instruction to execute the v01 command.

## [V02-R2] Required runner support
The current src/deathmap_ai/orcs_filters.py hardcodes the v01 identity, seven filters, accepted input schema, exact criteria and review handling. It cannot execute v02 as supplied.

A future implementation should:
1. Select the v02 profile explicitly, validate its supported operations, and route outputs to the requested v02 search directory while retaining the original internal profile ID.
2. Implement native multi-value comparison using the supplied separator, preserving native strings and field-level pass/fail/missing evidence.
3. Apply the four v02 filter categories. Keep enzyme and modality descriptive unless the optional knockout-only restriction is explicitly enabled.
4. Apply the supplied CELL_TYPE fallback only when the reference category is missing. Keep the fallback's evidence and result label distinct from a supported Cellosaurus category; preserve reference conflicts.
5. Implement non-excluding candidate tags with documented matching rules and retained source locators. Record unmapped modality as unresolved; keep multiple immune-pressure matches.
6. Preserve publication siblings as context, and maintain distinct direct/fallback/context/review statuses without reporting all workbook rows as direct hits.
7. Support local publication joins for a separately requested output workbook, using the field-source map and preserving missing/conflicting identifiers.
8. Preserve historical v01 behavior and artifacts; test supported v02 behavior with small fixtures before the first execution.

Do not relax the v01 validator and assume that it now interprets the extra v02 semantics. Unsupported operations must fail explicitly.

## [V02-R3] Interpretation details to make explicit before execution
Keep the supplied profile unchanged during preparation. Before implementation/execution, document these details in the accepted run specification:
- How to represent records with missing reference categories whose CELL_TYPE fallback does not match, including whether they remain in a separate unresolved review list.
- How each descriptive regex applies (case sensitivity and search versus whole-string match), and how rule precedence and multiple labels are recorded.
- The profile's experimental-setting else -> in_vitro rule is a derived candidate label, not direct evidence of an in vitro setting. Preserve the underlying values and do not promote the label to adjudicated scientific context.
- How to flag missing required native fields and preserve existing annotation review issues.
- Which result roles belong in a future workbook, and how overlaps are represented without duplicate screens.

These are not additional filters. Resolve semantics without silently changing the owner's intended search or inventing participant roles.

## [V02-R4] Verification and stop conditions
Verify input hashes and source schema, requested native vocabulary values, exact category joins, multi-value handling, fallback boundaries, optional knockout gating, non-excluding tags, missing-value behavior and context separation. Record the tool/profile version, input snapshots, metadata retrieval dates, hashes and examination counts.

Search only the existing saved metadata when execution is separately requested. No source refresh, external bibliography, gene-level results or supplementary-file contents are needed.

Create a new run directory, preserve the original native IDs and do not overwrite any old output. Report direct candidates, fallback candidates, unresolved records, publication context and distinct publications separately. Do not claim qualifying-study coverage.

## [V02-R5] Learning checkpoint
Filtering defines which candidates are retained; descriptive tags record hints for review. For example, an immune keyword tag may help locate co-culture evidence without making it a required filter or a confirmed biological classification.
