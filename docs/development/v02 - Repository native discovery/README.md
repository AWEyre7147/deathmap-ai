# DeathMap-AI v0.2: repository-native discovery

## [V02-1] Version and status
Planning version: **v0.2 — Repository-native discovery and ORCS enrichment**. The executable package remains v0.1.0 until v0.2 implementation is ready. This brief initializes planning; the final project document will follow owner review.

## [V02-2] Goal
Identify datasets and their publications in CRISPR perturbation contexts using repository-specific filters and search tools. The ORCS biological-classes pilot is the scientific starting point; translate its intent rather than copying unsupported fields into other resources.

## [V02-3] Two tracks
1. Enrich curated ORCS publications/screens with associated repository metadata and dataset candidates.
2. Discover studies independently through native repository interfaces, using publication-first or dataset-first routes as appropriate.

Keep discovery and enrichment contributions separately traceable. Prefer supported structured filters; use text only for properties without suitable fields. The owner first inspects each native interface; AI checks programmatic equivalents and small examples.

## [V02-4] Planned coverage
GEO first, then approved priorities among ENA, ArrayExpress within BioStudies, PRIDE, MassIVE, jPOST and iProX. OmicsDI is retired from primary discovery; any future accession lookup is optional backlog work.

## [V02-5] Boundaries and acceptance
Metadata only. Preserve native identities, hierarchy, evidence and unresolved links. Publication association alone does not prove that a dataset contains a qualifying screen. Assign screen groups after sufficient enrichment evidence. Validation references remain outside production queries.

For each resource, approve literal filters/queries, endpoints, hierarchy depth, pagination, pacing, retry/resume rules, evidence mapping and inspectable test cases before implementation. Success requires reviewed dataset identification and attributable evidence, not candidate counts alone.

## [V02-6] Next document
Use the owner's forthcoming repository research to choose the first retrieval contract, dataset attribution rules and acceptance examples. No live retrieval or new adapter is authorized by this brief.
