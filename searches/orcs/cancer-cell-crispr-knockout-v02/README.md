# cancer-cell-crispr-knockout-v02
## [V02-1] Configuration and status
[profile.json](profile.json) is the owner's v02 search definition. The directory keeps the requested name; the profile's internal ID remains **orcs-cancer-cell-crispr-v02**, reflecting its broader CRISPR scope. It supersedes the v01 profile for the proposed next search; v01 configuration and historical results remain unchanged.

Status: configuration prepared; not executed. The existing runner is restricted to v01 and must be extended before this profile can run. See [run-plan.md](run-plan.md).

## [V02-2] Filters and changes
| Category | v02 rule |
|---|---|
| Organism | Homo sapiens or Mus musculus |
| Screen format | Pool or in vivo |
| Phenotype | The nine exact values in profile.json, including proliferation/viability, tumorigenicity and chemical/toxin/radiation response |
| Cell-line reference | Exact CELL_LINE join to saved Cellosaurus category Cancer cell line |
| Missing reference category fallback | When the annotation/category is unavailable, the supplied CELL_TYPE regex may retain a candidate with the separate cancer_by_orcs_cell_type label |
| CRISPR modality | ENZYME, LIBRARY_TYPE and METHODOLOGY are not exclusion gates; optional knockout-only restriction remains disabled |

Fields combine with AND; alternatives within a field combine with OR. The profile specifies splitting native values on the exact separator ' | ' before comparison. Preserve original unsplit strings as evidence.

Modality, experimental setting, immune-pressure hints and host-contrast labels are descriptive candidate tags. Tags do not exclude screens or establish scientific eligibility. Cellosaurus-supported and fallback candidates remain distinguishable. Reference category describes cell-line origin, not which experimental population was perturbed.

All requested organism, format and phenotype values were found in the saved screen metadata during directory preparation, including 47 records with SCREEN_FORMAT=in vivo. These are source vocabulary checks, not search-hit counts.

## [V02-3] Shared inputs and planned outputs
Filter inputs remain:
- [Native screen database](../../../data/orcs/screen-index.json)
- [Saved reference annotations](../../../data/cellosaurus/orcs-annotations/annotations.json)

Future local workbook enrichment can reuse [publication metadata](../../../data/orcs/publication-index.json) and [explicit screen-publication associations](../../../data/orcs/publication-screen-links.json). These do not add publication-based filter gates.

Keep future run artifacts under outputs/orcs/cancer-cell-crispr-knockout-v02/<UTC-run-id>/. Record both that search-directory name and the internal profile ID in the manifest; do not derive the directory blindly from the differing internal ID.

Keep profiles/configuration here, shared inputs in data, and execution results in outputs. No output directory or populated workbook was generated during this preparation.

## [V02-4] Related guidance
- [Run preparation plan](run-plan.md)
- [Previous search](../cancer-cell-crispr-knockout-v01/README.md)
- [Shared database guide](../../../data/orcs/README.md)
- [Workbook field-source map](../../../docs/orcs/workbook-field-source-map.md)
- [Local enrichment plan](../../../docs/orcs/enrichment-plan.md)

Handoff 14 names a fixed v01 run. It must not be silently retargeted to v02; any v02 workbook task should name its own accepted filtered run after that run exists.
