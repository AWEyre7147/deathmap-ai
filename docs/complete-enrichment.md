# Complete ORCS metadata enrichment

The maintained Python commands run independently from a checked-out repository.
They require Python 3.11+ and the normal project dependency, openpyxl. No ChatGPT,
Codex, Node.js, spreadsheet authoring service or ignored pilot script is needed.

Install with `python -m pip install -e .`. Every example below can also use
`python -m deathmap_ai.enrichment_commands` instead of `deathmap-enrichment-stage`.
Each command creates a new stage directory and refuses an existing one. The
publication index is the complete input selection, never a validation inventory.

## Commands

Run from the repository root in PowerShell. Choose a new output directory; do not
reuse the example run ID if it already exists.

```powershell
$repo = (Get-Location).Path
$index = Join-Path $repo 'data/orcs/publication-index.json'
$runRoot = Join-Path $repo 'data/orcs/enrichment-runs/NEW-RUN-ID'

deathmap-enrichment-stage --stage registry --root $repo --publication-index $index --output-dir "$runRoot/registry" --registry "$repo/data/orcs/enrichment-publication-registry.json"

deathmap-enrichment-stage --stage pubmed --root $repo --publication-index $index --output-dir "$runRoot/pubmed" --cache-root "$repo/data/orcs/pubmed-enrichment-source/20261008"

deathmap-enrichment-stage --stage geo --root $repo --publication-index $index --output-dir "$runRoot/geo" --cache-root "$runRoot/pubmed" --cache-root "$repo/data/orcs/geo-enrichment-source/20261011"

deathmap-enrichment-stage --stage arrayexpress --root $repo --publication-index $index --output-dir "$runRoot/arrayexpress" --cache-root "$repo/data/orcs/arrayexpress-enrichment-source/20261011"

deathmap-enrichment-stage --stage ena --root $repo --publication-index $index --output-dir "$runRoot/ena" --pubmed "$runRoot/pubmed/database.json" --geo "$runRoot/geo/geo-enrichment.json" --cache-root "$repo/data/orcs/ena-enrichment-source/20261014" --metadata-only-project PRJEB40771 --metadata-only-project PRJEB40772 --metadata-only-project PRJNA63443

deathmap-enrichment-stage --stage synthesize --root $repo --publication-index $index --output-dir "$runRoot/synthesis" --registry "$runRoot/registry/publication-registry.json" --pubmed "$runRoot/pubmed/database.json" --geo "$runRoot/geo/geo-enrichment.json" --arrayexpress "$runRoot/arrayexpress/database.json" --ena "$runRoot/ena/database.json"
```

The cache directories are optional examples, not discovery dependencies. Omit
`--cache-root` for fresh requests. GEO can also reuse the curated native sources
under this repository's data/orcs automatically. Native cache reuse requires
verified bytes and the appropriate request identity; original retrieval dates
remain distinct from reuse/execution dates. This is not a silent freshness claim.

PubMed, GEO and ArrayExpress start from publication identifiers/titles in the
index. ENA additionally receives the explicitly selected PubMed and GEO metadata
for their source-backed accession links. PubMed records with no PMID are listed
as unresolved for that resource; they still receive publication indices and can
participate in title/accession-led repository enrichment.

The three `--metadata-only-project` exceptions are the accepted broad-collection
boundary: retain project records and native hierarchy but do not expand their
collection-wide run reports. They are not benchmark discovery inputs. If changing
this policy, treat it as a separate resource/scientific scope decision.

## Outputs and reruns

Each resource writes its canonical JSON, native response receipts, registered
repository workbook and a stage receipt. The repository workbooks use the revised
templates directly under data/templates. `--template` explicitly selects another
registered revision. Missing or conflicting source metadata stays canonical
evidence even where the owner excluded it from the workbook.

Synthesis reads the four explicit saved databases and persistent publication
registry. It cannot issue network requests or launch another stage. It uses
data/templates/Enrichment-Synthesis.xlsx and its manifest, preserves native
repository identities, and writes the final 21-sheet Enrichment-Synthesis.xlsx.
It performs no scientific dataset merging or qualifying-screen adjudication.
The canonical output is `synthesis.json.gz`: native tables and original value
combinations are compressed losslessly, and the display layout is derived during
export, avoiding another large duplicate of every display table.

For a standalone offline re-export:

```powershell
deathmap-export-enrichment --root $repo --database "$runRoot/synthesis/synthesis.json.gz" --template "$repo/data/templates/Enrichment-Synthesis.xlsx" --output "$runRoot/ANOTHER-OUTPUT.xlsx"
```

To change the publication selection, supply a different saved ORCS publication
index and a fresh run directory. Reuse the registry to preserve assigned PUB
indices. Existing identities never renumber; new records append. Existing input
PMIDs/native ORCS IDs must be unique, and publications without PMIDs are supported.
The persistent enrichment registry defines this namespace. Legacy ORCS search
workbooks have run-local PUB indices; join those using native ORCS publication ID
or PMID, never by assuming equal PUB strings mean equal publications.

To rerun synthesis, invoke only the final command with the saved source paths and
a new synthesis directory. It does not repeat enrichment. To rerun a repository,
invoke only its stage into a new directory, optionally supplying prior native
caches. If a stage fails, retain its partial output and inspect the explicit
failure; do not delete evidence or relabel errors as successful empty results.
The native GEO/ArrayExpress/ENA adapters retain their separately documented resume
interfaces. The shared offline export command can export a completed canonical
projection into a fresh workbook without repeating retrieval.

## Limits and verification

Native adapters retain their request/time/size limits. The stage stops on unresolved
retrieval issues rather than continuing to a complete-looking final output. ENA
full-title syntax recovery uses the same complete title via Portal TSV or the
accepted EBI phrase interface, never a shorter phrase. HTTP 200 run-report errors
are retained as incomplete evidence; only the failed report is retried once, with
a ten-failure checkpoint. The accepted project-only omissions remain explicit.

The portable Excel writer streams body rows into the registered template's XML
envelope, keeps literal strings and native numeric/Boolean types, and reopens every
sheet for exact header and cell verification. It refuses existing workbooks,
changed template hashes, missing tables and unexpected output rows. Repository
exports stop on oversized cells. Synthesis preserves any value exceeding Excel's
32,767-character limit in `Enrichment-Synthesis.overflow.json.gz`, placing an
explicit file/record reference in the cell. Nothing is silently truncated; native
values also remain in the canonical synthesis. This handles large many-to-many
membership lists without changing the accepted row grain or adding sheets.
Native Excel application opening is a separate check, not implied by XML/cell
verification.

Run the inspectable offline verification fixtures with:

```text
python -m unittest discover -s tests -p test_enrichment_end_to_end.py
```

The fixtures include persistent publication keys, no-PMID publications, empty
repository results, literal formula-like metadata/date text, exact native cache
reuse, and a complete synthesis-to-registered-workbook path with networking disabled.

## Restoring the packaged completed run

The published `data/orcs/enrichment-runs/20261018/source-material.zip` contains the
exact original resource databases, projections, native response bodies and
receipts. Its manifest records the ZIP hash and each original path, size and
SHA-256. Final workbooks, stage receipts, registry and compressed synthesis remain
available directly in the run folder. Historical execution manifests are unchanged.

To replay synthesis from that completed run, restore its source files first:

```powershell
$savedRun = Join-Path (Get-Location).Path 'data/orcs/enrichment-runs/20261018'
python -m zipfile -e "$savedRun/source-material.zip" $savedRun
```

Run this only in a clean source-material area: ZIP extraction replaces existing
payload paths. It does not touch the final workbooks because they are not ZIP
members. The restored source files require approximately 0.8 GB of disk space;
Git ignores them to avoid recommitting duplicate metadata. Then use the saved
source paths in the synthesis command with a **new** output directory. No
retrieval is required. Standalone export from `synthesis/synthesis.json.gz` does
not need restoration. Future freshly executed stages still write their ordinary
JSON and native response files; bundling is a release-storage step, not an
additional discovery or enrichment strategy.
