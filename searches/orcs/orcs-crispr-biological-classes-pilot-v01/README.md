# CRISPR biological classes

## [PC-1] Profile and readiness

[profile.json](profile.json) is the owner-supplied search definition, renamed from `orcs-crispr-biological-classes-pilot-v01.json` without changing its contents. Its internal ID and first-version pilot numbering remain unchanged.

**Dedicated runner implemented and owner-authorized run executed.** Use `python -m deathmap_ai.orcs_crispr_pilot`, then the v6 workbook exporter for the returned run directory. The historical knockout-v01 command is unchanged and must not be used for this pilot. See [run-plan.md](run-plan.md) for the recorded semantics.

## [PC-2] Search logic

Broad mammalian CRISPR discovery in cancer-derived, immune-lineage, or organoid models; includes controls and non-immune readouts.

Common gates combine with AND: organism is Homo sapiens or Mus musculus, and library type is one of the five values in profile.json. Split exact-value fields on `|`, trim tokens, and compare case-sensitively. Native unsplit values remain evidence. Candidate rules combine with OR; nested `all` tests combine with AND.

| Rule | Supplied test |
|---|---|
| `C1_cancer_reference` | annotation.category: Cancer cell line |
| `C2_cancer_native_fallback` | annotation.category: missing AND screen.CELL_TYPE: supplied regex (IGNORECASE) |
| `C3_immune_lineage` | screen.CELL_TYPE: supplied regex (IGNORECASE) |
| `C4_organoid_model` | screen.CELL_TYPE: supplied regex (IGNORECASE) |

The profile retains all screens from a seeded publication, including screens that fail the common gates. Label those `publication_companion`, separately from `direct_rule_candidate`. A direct rule match means the configured test matched; the scientific classification remains an inferred candidate.

Cancer-derived/reference-supported, immune-lineage, or organoid-model CRISPR candidates. Normal organoids and non-immune readouts remain eligible under the supplied rules.

## [PC-3] Inputs and outputs

Shared local inputs:

- [Screen metadata](../../../data/orcs/screen-index.json)
- [Publication metadata](../../../data/orcs/publication-index.json)
- [Saved Cellosaurus annotations](../../../data/cellosaurus/orcs-annotations/annotations.json)

Publication matching uses the supplied exact SOURCE_TYPE + SOURCE_ID pair. Preserve missing/ambiguous joins and reference review issues. No named study, accession, cell-line, or library allowlist is added. Scope notes mentioning validation references are narrative context, not executable dependencies or search seeds.

Future results belong under `outputs/orcs/orcs-crispr-biological-classes-pilot-v01/<UTC-run-id>/`. Keep the full directory name, without deriving a different name by stripping the internal ID prefix. Use [workbook v6 and its ledger](../../../docs/specifications/16%20Evidence%20Model%20and%20Workbook%20v6.md) for future outputs; first-version numbering in this new search family is not a request to recreate historical workbook v01.

## [PC-4] Validation performed

JSON structure, rule IDs, regex syntax, source fields, and requested common-filter vocabulary passed local preflight. The checked inputs contain 2,217 screens, 418 publications, and 825 saved cell-line annotation entries. These are input sizes, not search-hit counts. No duplicate publication join keys were detected in the checked snapshot.

Recheck without running a search:

```powershell
python scripts/validate_orcs_pilot_profiles.py --profile searches/orcs/orcs-crispr-biological-classes-pilot-v01/profile.json
```

Preparation performed no search or retrieval. The subsequent owner-authorized run is [20261004T215601947427Z](../../../outputs/orcs/orcs-crispr-biological-classes-pilot-v01/20261004T215601947427Z/summary.json): 2,217 screens examined, 1,830 direct-rule candidates plus 56 companions, across 328 publications. Rule counts overlap and candidate counts do not establish qualifying-study coverage. No source refresh, external enrichment, validation-inventory access or experimental data download occurred.
