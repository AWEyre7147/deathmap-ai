# cancer-cell-crispr-knockout-v01
[profile.json](profile.json) defines seven exact filters: Cellosaurus category Cancer cell line; Cas9; CRISPRn; Knockout; Pool; human or mouse; and one of four proliferation, viability, cell-cycle or migration phenotypes. Fields combine with AND; alternatives within a field combine with OR.

No immune-population or experimental-setup gate is applied. This broad candidate subset supports later review of possible co-cultures; a hit does not establish co-culture eligibility.

Inputs are shared [ORCS screen metadata](../../../data/orcs/README.md) and [saved reference annotations](../../../data/cellosaurus/README.md). Missing/conflicting categories remain unresolved.

## Existing completed run

- [Summary](../../../outputs/orcs/cancer-cell-crispr-knockout-v01/20261003T173643920687Z/summary.md)
- [Workbook](../../../outputs/orcs/cancer-cell-crispr-knockout-v01/20261003T173643920687Z/DeathMap-AI-v1-reference-output.xlsx)
- [Verification](../../../outputs/orcs/cancer-cell-crispr-knockout-v01/20261003T173643920687Z/verification.json)

1,020 direct hits across 76 publications; workbook 1,176 screens across 92 publications including unresolved and context rows. Keep run snapshots immutable.

## Repeatable local workflow

With the project Python dependencies installed, run from the repository root:

    python -m deathmap_ai.orcs_filters

Make src available on PYTHONPATH. The command creates a new timestamped run, filters all saved screens, copies the blank template and prepares projection.json; it performs no network retrieval. To create Excel, invoke scripts/export_orcs_filter_workbook.mjs with that run directory, using the bundled artifact-tool dependencies and ARTIFACT_NODE_MODULES. Verify with:

    python -m deathmap_ai.orcs_filter_verify outputs/orcs/cancer-cell-crispr-knockout-v01/<run-id>

Results stay in the run directory. Do not replace the blank template. [Field-source plan](../../../docs/orcs/workbook-field-source-map.md) and [enrichment plan](../../../docs/orcs/enrichment-plan.md) govern the next review discussion. No enrichment run is authorized by these instructions.
