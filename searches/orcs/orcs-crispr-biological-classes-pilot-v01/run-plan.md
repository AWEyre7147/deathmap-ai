# CRISPR biological classes: run preparation

## [PC-R1] Status and preserved scope

The owner authorized execution after choosing only this CRISPR pilot. The dedicated offline runner implements the profile's shared schema, and the first run is 20261004T215601947427Z. The legacy v01 command remains incompatible and unchanged. Preserve the profile criteria, expansion policy and inferred candidate classifications.

## [PC-R2] Runner requirements

1. Select this profile explicitly; record its ID, schema, version, file hash and input hashes. Examine each cached screen once, without a source refresh or an arbitrary candidate cap.
2. Interpret the common gates, token separator and trimming exactly as supplied. Evaluate regexes case-insensitively and preserve field names, original strings and matching spans. Record per-rule outcomes and missing evidence.
3. Join publication metadata by the exact native SOURCE_TYPE/SOURCE_ID pair. Retain ambiguous or missing mappings instead of selecting one silently. For a fields list, make per-field matches visible; document whether each field is searched independently before execution.
4. Retain every matching rule ID. For publication expansion, preserve seed anchors and distinguish companions that fail common filters. Avoid duplicate screens when multiple rules or seed publications overlap.
5. Keep source observations direct where appropriate, but scientific class labels inferred. Do not infer a dataset accession, accessibility, exact screen-dataset link, clinical trial, or perturbational single-cell assay from a mention alone.
6. Keep annotation joins separate from ORCS evidence. Use the v6 cell_line/accession/ledger model. Adjust the current evidence adapter's historical profile-version guard for these newly approved pilot families; do not bump their supplied profile_version simply to bypass that guard. Preserve historical v01 rejection behavior.
7. Produce a new versioned run package under the directory documented in README.md. Record direct-rule candidates, companions, distinct publications, missing/ambiguous joins, and reference review issues separately. Generate a v6 workbook only from the supported canonical projection.

## [PC-R3] Semantics to settle in the implementation

Implemented choices for this run: missing is absent/null/blank/trimmed dash; regexes search fields independently with IGNORECASE and no DOTALL; exact-value comparisons split `|` and trim; annotation joins use the complete original CELL_LINE value; reference review issues are retained without an extra exclusion gate; missing publication joins cannot seed expansion; ambiguous publication/annotation keys fail explicitly. No clinical ICB tag exists in this active profile. The checklist below is retained as preparation context.

- Define missing field/category behavior explicitly; missing text is not evidence of absence, and a missing-reference fallback must not overwrite an existing Cellosaurus category.
- Define regex search across fields and line breaks explicitly. The supplied patterns use IGNORECASE without DOTALL; do not silently concatenate fields or broaden those flags.
- Define non-excluding tag behavior and review issue propagation. The clinical ICB tag supplies a pattern without its own flags; make the chosen tag flags explicit before using it.
- Decide how unsupported or conflicting source observations are represented in the workbook and ledger. Keep companions distinct from candidates and preserve all matched rules.

These are implementation details to document, not additional exclusion gates. Do not reinterpret the supplied scope notes as permission for named-study retrieval.

## [PC-R4] Checks and boundary

Use inspectable fixtures for common-gate AND logic, rule OR/nested AND logic, exact multi-value matching, missing annotations, publication joins, simultaneous rule matches, companion expansion and original-source preservation. Validate workbook/ledger evidence IDs, shared accessions, source attribution, reviewer colors and fixed glossary preservation before release.

This pilot is ORCS-only and metadata-only. For example, a clinical publication mention can be retained for review without asserting that ORCS provides its cohort dataset. External repository enrichment is a separate stage.

Learning checkpoint: a validated profile proves the settings are internally compatible with the available inputs; it does not prove that the requested scientific class is present or that any candidates qualify.
