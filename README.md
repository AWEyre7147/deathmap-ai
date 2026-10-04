# DeathMap-AI v0.1

A metadata discovery and curation pipeline for CRISPR screens. The completed ORCS pilot filters saved BioGRID ORCS metadata, joins saved Cellosaurus annotations, and produces evidence-preserving JSON and a v6 review workbook.

Start with the [completed pilot](searches/orcs/orcs-crispr-biological-classes-pilot-v01/README.md), [pilot completion record](docs/orcs/pilot-completion-v01.md), or [documentation index](docs/index.md).

## Pilot result

The run examined 2,217 cached screens and retained 1,830 direct-rule candidates plus 56 publication companions across 328 publications. After reviewing the output, the project owner reported representation of **33/33 CRISPR-related comparison publications present in ORCS**. This is publication-level representation in the defined comparison set; it does not establish the eligibility of every candidate, general retrieval recall, or experimental dataset availability.

The production search does not load ICRAFT references. Publication companions remain distinct from direct-rule candidates. Unresolved annotations and conflicting identifiers remain visible; dataset attribution and external enrichment are deferred.

## Local setup and search

Python 3.11 or later is required. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
python scripts/validate_orcs_pilot_profiles.py --profile searches/orcs/orcs-crispr-biological-classes-pilot-v01/profile.json
python -m deathmap_ai.orcs_crispr_pilot
```

The last command creates a new UTC-named directory under `outputs/orcs/orcs-crispr-biological-classes-pilot-v01/`. It reads the saved catalogs once without refreshing sources or retrieving experimental data. Canonical JSON and the complete evidence ledger are produced before workbook export.

The same offline suite can also be run with `python -m unittest discover -s tests -q`; this was the command used for release verification.

The workbook exporter additionally requires Node.js and the OpenAI artifact-tool runtime provided in the Codex spreadsheet environment. It is **not yet a standalone pip-installed Excel exporter**. In that environment, set `ARTIFACT_NODE_MODULES` to the runtime's `node_modules` directory and `BUNDLED_PYTHON` to its Python executable, then run:

```powershell
node scripts/export_evidence_workbook_v6.mjs <new-run-directory>
```

The v6 template's glossary/reference sheets are preserved. The Sources sheet currently retains template example counts; consult the run summary for actual counts.

## Repository layout

| Folder | Purpose |
|---|---|
| `searches/orcs/<search-name>/` | Versioned filter profile and instructions |
| `searches/omicsdi/` | Reserved OmicsDI configurations; not part of this pilot |
| `data/orcs/` | Saved screen/publication catalogs, associations and provenance |
| `data/cellosaurus/` | Saved reference annotations and supporting evidence |
| `data/templates/` | Preserved blank workbook models |
| `outputs/orcs/<search-name>/<run-id>/` | Local generated results, workbook and verification; excluded from Git |
| `docs/` | Specifications, guides, vocabularies and completion records |
| `logs/` | Decisions and preservation receipts; temporary workspaces excluded |
| `src/`, `scripts/`, `tests/` | Implementation, entry points and offline checks |

Saved public-resource metadata is included to reproduce the pilot's input conditions. Source records retain their identifiers, dates and provenance. Project code is [MIT licensed](LICENSE); third-party metadata retains its upstream terms as described in [third-party notices](THIRD_PARTY_NOTICES.md).

Historical runs and superseded experiments remain in the owner's external archive. The [relocation registry](logs/repository-relocations-20261004.json) preserves their paths and hashes; archived files and machine-specific paths are not portable dependencies for the completed pilot.

See [authoritative specifications](docs/specifications/README.md), [agent instructions](AGENTS.md), and [GitHub preparation notes](docs/github-preparation.md). Older modules remain available as historical development code; the command above is the entry point for the completed CRISPR pilot.
