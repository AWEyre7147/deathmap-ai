# ChatGPT handoff: v02 ORCS repository enrichment

Prepared 2026-10-08. This is a conversation handoff and planning brief, not an approved implementation contract.

## 1. Objective and one deliverable

Continue DeathMap-AI v02 — ORCS Pilot Enrichment. Help the owner interpret their ongoing repository research and produce **one proposed first-resource enrichment contract** for the retained ORCS publications and screens. Resource selection is still open; GEO is a leading candidate, not a finalized choice.

Begin by establishing what research is available and what the owner wants to examine next. If their research is not ready, help clarify a small concrete question rather than inventing a complete strategy. Do not require a formal research submission or conversational notation.

## 2. Effort estimate and pre-dispatch assessment

- Deliverable and boundary: one proposed metadata-enrichment contract for one resource, based on relevant existing notes and owner-supplied findings.
- Effort: low for orientation; moderate for a first contract. Main uncertainty is whether native/programmatic capabilities and attribution evidence are sufficiently established. Cross-resource investigation could be high effort and must be separately scoped.
- Allowed expensive work: none in this opening task; zero full rebuilds, exports, bulk downloads or live retrieval runs.
- Verification boundary: check the relevant local notes and paths; distinguish verified behavior from examples, expectations and unanswered questions. Do not automatically audit all resources.
- Instruction conflicts: compare this brief with active specifications and applicable agent instructions. Report a material conflict before dependent work. Historical release/work-session notes are not current defaults.
- Checkpoint and stop: return an inspectable proposal and unresolved decisions. Implementation or substantial new research requires a separate bounded task.

## 3. Relevant inputs and accepted decisions

Repository: `C:/Users/aweyr/Documents/Repositories/deathmap-ai`.

Read these first when repository access is available:

- `AGENTS.md`
- `docs/index.md`
- `docs/specifications/project-vision-v01.md`
- `docs/specifications/module-01-evidence-discovery.md`
- `docs/development/v02 - ORCS Pilot Enrichment/README.md`
- The current iteration's `decision-log.md` and `ideas-questions.md`
- `docs/workflow/project/AI-agent-workflow/responsibilities.md`
- `docs/workflow/global/AI-agent-workflow/codex-handoff-rules.md`
- `docs/workflow/global/AI-agent-workflow/accession-labels.md`

Then read only the repository-interface notes relevant to the chosen discussion under `docs/resources/databases`, using `docs/resources/README.md` for navigation. Existing ORCS outputs and profiles are indexed by `outputs/orcs/README.md` and `searches/orcs/README.md`. Do not load whole output catalogs for orientation.

If this ChatGPT session cannot access local files, say so and ask the owner for the relevant notes or excerpts. Do not imply local documents were read. No mandatory current-work-session specification exists.

### Project state

- Current iteration is v02; the executable package remains v0.1.0. The vision's `v01` filename is retained for compatibility and does not mean enrichment is a v01 task.
- Implemented: three cached ORCS profiles, Cellosaurus interpretation, reusable DOI/PMID/PMCID resolution, canonical JSON and portable Excel export using the owner-approved template.
- Repository enrichment adapters and screen-group assignment are not yet implemented.
- The owner is manually examining which databases overlap ORCS, which identifiers connect entries and what metadata can be retrieved. Their interface notes are research references, not automatically approved queries or API guarantees.

### Accepted direction and boundaries

- Enrich the existing curated ORCS results first. Independent repository discovery is deferred from this immediate task.
- Use the ORCS biological-classes pilot as the scientific starting point: human/mouse, configured CRISPR modalities, and cancer-derived, immune-lineage or organoid contexts. Do not change eligibility or mechanically copy ORCS fields into unsupported repository filters.
- For later searches, prefer supported structured filters and avoid needlessly duplicating their constraints in free-text terms. Identifier-led enrichment may use different routes from discovery search.
- Preserve publication, screen group, screen, dataset and repository hierarchy distinctions. A shared publication establishes neither a qualifying experimental dataset nor an exact screen–dataset relationship.
- Missing fields, conflicting mappings and unresolved attribution are useful outcomes; preserve them with evidence rather than guessing.
- Develop the existing screen-group concept after sufficient enrichment. Whole-ORCS grouping remains an exploratory idea.
- OmicsDI is retired from primary discovery. Possible tertiary accession lookup is backlog work, not a dependency of this phase.
- No required ChatGPT–Perplexity collaboration exists. Optional external findings are evidence to assess, not authority.
- Long-term direction: comprehensive CRISPR publication/dataset identification for cancer and immune cells, then normalized, analyzed and thoroughly annotated datasets for future reuse, especially with the ligand–receptor database previously called XDeathDB. These downstream capabilities are not authorized in this phase.

## 4. Files and actions in scope

Opening work is discussion and a proposed first-resource contract. Use the owner's available research to distinguish:

1. Available ORCS seeds: DOI, PMID, PMCID, reported repository accessions or other supported identifiers; identify what is actually present before choosing a route.
2. Connection route: exact accession lookup, identifier-linked publication search, repository links or another documented route. Distinguish exact matches from heuristic candidates, including identifier/version conflicts.
3. Returned information: native entity level, metadata fields, hierarchy and availability; distinguish native interface capabilities from programmatic output.
4. Proposed retrieval mechanics: endpoints, literal parameters/filters/queries, hierarchy depth, pagination, pacing, retries, caching/resume behavior and request/record limits. Mark undecided details explicitly.
5. Evidence and mapping: raw-response preservation, field provenance, cross-repository links, duplicate identity, direct/inferred/conflicting/unresolved status and review responsibilities. Related records must not be silently merged.
6. Acceptance examples: a small inspectable set showing a supported match, no match, ambiguity and incomplete metadata where applicable. Validation references must remain outside production queries.
7. Review output: which new fields/relationships are proposed and how the owner can review them without overwriting edited workbooks.

Choose a small pilot before any proposed full-collection enrichment. Do not assume all planned repositories are necessary. Current candidates include GEO, ENA, ArrayExpress within BioStudies, PRIDE, MassIVE, jPOST and iProX; additions require a reason tied to ORCS coverage or useful evidence.

The owner supplies scientific priorities, interface observations and adjudication. The AI helps translate them into bounded programmatic contracts, identifies uncertainty and implements only subsequently authorized work. Record accepted decisions separately from exploratory ideas when documentation updates are requested.

## 5. Exclusions and preservation

Do not implement adapters, run live enrichment, regenerate ORCS searches, export workbooks, change dependencies, reorganize the repository, conduct an exhaustive database audit, or commit/push/publish as part of this handoff.

Preserve existing source metadata, ORCS vocabulary, historical identifiers, provenance, owner-edited workbooks and unrelated changes. Future authorized enrichment must have its own output location and attribution; do not silently rewrite the historical ORCS evaluation.

Experimental-file downloads, matrix normalization, analysis, ligand–receptor integration and automatic screen grouping are outside this task.

## 6. Acceptance criteria and minimum verification

The proposal names one resource, concrete seed and connection routes, anticipated metadata, evidence rules, a bounded pilot and unresolved owner decisions. It distinguishes documented capabilities from unverified expectations. Relevant local links resolve when accessible. No execution or coverage claim is made from candidate counts.

No pipeline tests or rebuilds are required for this planning deliverable. External interface verification, if needed, should be proposed as a narrowly scoped next task rather than implied to have occurred.

## 7. Checkpoints and cancellation boundary

No numeric resource budget has been specified. Effort estimates are operational guidance, not hard usage guarantees. Maximum full rebuild/export passes for this task: zero.

Return a checkpoint if a contract requires broad new research, live API exploration, missing authoritative inputs or a scientific/architectural decision. Explain the smallest useful next step and its effort. Do not dispatch subagents or background work. A stop request cancels any owned active or queued work; preserve completed material and report unresolved cancellation honestly.

## 8. Stopping condition and completion summary

Stop after presenting the first-resource proposal and the specific questions preventing approval. Do not begin implementation merely because planning is complete. Summarize the proposed result, checks actually performed, assumptions, remaining decisions and the next bounded action.

## Conversation conventions

In a new session, use **A1 —**, **A2 —** for the first assistant reply; the next reply uses B and restarts at 1. Commentary and final text share that reply's letter and use distinct numbers. Preserve historical document labels.

Explore/Remember/Decide/Do terminology is proposed, not adopted. Ordinary-language instructions remain sufficient. Do not treat exploratory thoughts as implementation decisions or require the owner to use formal labels.

## Copyable opening message

Continue DeathMap-AI v02 ORCS repository-enrichment planning using this handoff and the active specifications. I am still investigating which databases can connect the retained ORCS entries and what information they provide. Begin with the research I have available and help me develop one proposed first-resource metadata-enrichment contract. Do not implement, perform live retrieval, rebuild searches or export workbooks. Return the proposal and unresolved decisions before moving to execution.

## Status update — 2026-10-08

The initial planning-only scope above is historical. The owner subsequently authorized and completed the PubMed enrichment milestone; see [the milestone report](pubmed-milestone.md). Next goals are GEO, BioStudies–ArrayExpress and ENA repository enrichment. This status update does not authorize those future native repository passes.
