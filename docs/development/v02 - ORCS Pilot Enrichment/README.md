# DeathMap-AI v02: ORCS Pilot Enrichment

## [V02-1] Version and status
Current iteration: **v02 — ORCS Pilot Enrichment**. The PubMed enrichment subgoal is complete: 415 verified PMIDs from the 418-publication ORCS index, a shared JSON database and Excel view, and enrichment workbooks for all three saved ORCS searches. Three publications remain explicitly unresolved. The executable package remains v0.1.0. Repository hierarchy expansion and screen grouping are not yet implemented. See the [milestone report](pubmed-milestone.md); the earlier opening handoff is historical and is superseded for PubMed by the owner's implementation authorization.

## [V02-2] Goal
Identify repository datasets associated with the retained ORCS publications and screens, and determine which relationships are supported. The long-term project seeks comprehensive publication/dataset identification for CRISPR perturbation studies of cancer and immune cells, then normalized and analyzed datasets annotated for future use, especially with the ligand–receptor database previously known as XDeathDB. Normalization, analysis and that integration are future stages, not current implementation. The ORCS biological-classes pilot is the scientific starting point; translate its intent rather than copying unsupported fields into other resources.

## [V02-3] Current priority
Enrich the curated ORCS publications/screens with associated repository metadata and dataset candidates. After sufficient enrichment, develop the existing screen-group concept using supported shared-design evidence. Independent repository discovery is deferred from the immediate priority. Whole-ORCS grouping is exploratory, not authorized.

Accepted decisions are in `decision-log.md`; possibilities and unresolved questions are in `ideas-questions.md`. Repository interfaces are being investigated by the owner. External clarification is optional; there is no required collaborative Perplexity workflow.

## [V02-4] Planned coverage
The next goals are GEO, BioStudies–ArrayExpress and ENA repository enrichment. Finalize each native hierarchy, matching and attribution contract before implementing it. PRIDE, MassIVE, jPOST and iProX remain later resource candidates. OmicsDI is retired from primary discovery; any future accession lookup is optional backlog work.

## [V02-5] Boundaries and acceptance
Metadata only. Preserve native identities, hierarchy, evidence and unresolved links. Publication association alone does not prove that a dataset contains a qualifying screen. Assign screen groups after sufficient enrichment evidence. Validation references remain outside production queries.

For each resource, approve literal filters/queries, endpoints, hierarchy depth, pagination, pacing, retry/resume rules, evidence mapping and inspectable test cases before implementation. Success requires reviewed dataset identification and attributable evidence, not candidate counts alone.

## [V02-6] Next document
Use the completed PubMed associations and the owner's repository research to define GEO, BioStudies–ArrayExpress and ENA contracts, dataset attribution rules and acceptance examples. The PubMed implementation authorization does not authorize those future repository passes.
