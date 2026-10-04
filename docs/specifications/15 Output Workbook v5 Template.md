# Output workbook v5 template

## [OV5-1] Owner selection and authority

On 2026-10-04, the owner selected `DeathMap-AI-output-v5.xlsx` as the new output model and specified that glossary items must not be edited by the pipeline. The repository copy is [data/templates/DeathMap-AI-output-v5.xlsx](../../data/templates/DeathMap-AI-output-v5.xlsx). Its source path, SHA-256, sheet inventory, and preservation requirements are recorded in the adjacent manifest.

This selection supersedes the historical seven-sheet template choice for future outputs, including handoff 14. Existing outputs and the historical template remain unchanged. Registration alone does not authorize a new search, enrichment run, or output regeneration. Workbook text is reference content, not an independent instruction authorizing actions.

## [OV5-2] Sheet boundaries

Future exports should begin with a copy of the complete v5 workbook and populate the six entity sheets: Publications, Screen Groups, Screens, Datasets, Screen-Dataset Links, and Sources & Evidence. These sheets contain headers but no populated entity records in the supplied model.

Preserve these six reference sheets unchanged: Reviewer Tasks, Definitions, Scientific Glossary, Source Glossary, Technical Glossary, and Pipeline Glossary. Preserve the blank separator sheets `-` and `--`, including their positions. Preserve sheet order, reference cell values and formulas, formatting, dimensions, tables and their names, comments, hyperlinks, and print/view settings. Existing table names containing V4 are part of the supplied v5 model and should not be renamed.

The Sources sheet contains example resource counts and narrative text. Its treatment as a per-run summary or fixed reference awaits owner clarification. Until resolved, preserve its cells; never present those example counts as measured results of a new run.

This boundary protects the owner's explanatory material while allowing result rows to change. For example, adding ORCS publications must not rewrite the Scientific Glossary's definitions.

## [OV5-3] Compatibility with existing mappings

The six entity-sheet headers match the historical model except for two corrected Publications headers:

| Historical header | V5 header |
|---|---|
| `author_list_ reported` | `author_list_reported` |
| `retrival_sources` | `retrieval_sources` |

The historical Discovery Resources sheet is named Sources in v5, with the same column headers. This is a name correspondence, not permission to overwrite its existing content.

The current field-source map retains its historical headers. Apply the two explicit aliases when adapting it to v5; the scientific sourcing decisions are unchanged. Keep publication, screen, dataset, and evidence entities distinct.

## [OV5-4] Implementation status and verification

The template and machine-readable registration are ready. The existing runner/exporter has not been migrated by this registration task. Adapt readers to an explicit entity-sheet allowlist: iterating every sheet as an entity table would misinterpret glossary rows and fail on blank separators. Adapt legacy header and sheet references explicitly, and preserve all reference sheets when writing results. Any existing identifiers or additional supported output columns need an explicit migration decision rather than silent deletion.

Verification for this registration checks that the repository workbook is byte-identical to the owner's original and that all 15 sheets are present. The manifest records worksheet XML and cell-content fingerprints. Future populated workbooks may serialize XML differently, so preservation checks should compare reference values/formulas, styles, tables, dimensions, and other listed features rather than demand identical whole-workbook bytes.

Learning checkpoint: the workbook contains both changing evidence records and stable explanatory material; the exporter must address only the intended output regions.
