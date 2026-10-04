# ORCS searches

## Completed and supported

[CRISPR biological-classes pilot](orcs-crispr-biological-classes-pilot-v01/README.md) is the primary entry point. Its dedicated offline runner and v6 workbook support are implemented. The owner concluded the discovery pilot after reporting representation of 33/33 ORCS-present comparison publications; see the [completion record](../../docs/orcs/pilot-completion-v01.md).

Run `python -m deathmap_ai.orcs_crispr_pilot` after the root README's local setup. Use `scripts/validate_orcs_pilot_profiles.py` for a read-only preflight. Shared inputs live under `data/orcs/` and `data/cellosaurus/`; each new execution creates `outputs/orcs/<search-name>/<UTC-run-id>/`.

## Prior configurations

- [cancer-cell-crispr-knockout-v01](cancer-cell-crispr-knockout-v01/README.md): historical filtering implementation and outputs; preserved.
- [cancer-cell-crispr-knockout-v02](cancer-cell-crispr-knockout-v02/README.md): separate prepared configuration, not the completed biological-classes pilot.

Do not interchange runner commands between profile schemas. The removed single-cell and clinical-omics profiles are not production dependencies. Validation-reference inventories remain outside production discovery.
