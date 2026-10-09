# DeathMap-AI documentation

## Start here

**Current iteration: v02 — ORCS Pilot Enrichment.** We are defining repository enrichment of the existing ORCS publications/screens. Identifier enrichment, portable Excel outputs and the [PubMed enrichment milestone](pubmed-enrichment.md) are implemented. GEO, BioStudies–ArrayExpress and ENA enrichment are the next goals; repository hierarchy expansion and screen-group assignment remain pending. The executable package remains v0.1.0.

The long-term direction is comprehensive identification of publications and datasets from CRISPR perturbation studies of cancer and immune cells, followed by normalized, analyzed and thoroughly annotated datasets for future use. A priority future annotation source is the ligand–receptor database, previously XDeathDB. Current work remains metadata-only.

1. [Project vision](specifications/project-vision-v01.md): purpose, target and long-term direction.
2. [Module specification](specifications/module-01-evidence-discovery.md): implemented behavior, evidence rules, current boundaries and pending capabilities.
3. [Current iteration](development/v02%20-%20ORCS%20Pilot%20Enrichment/README.md): immediate work and next decisions.
4. [User and AI-agent responsibilities](workflow/project/AI-agent-workflow/responsibilities.md).

## Current iteration notes

- [Next-session repository enrichment handoff](development/v02%20-%20ORCS%20Pilot%20Enrichment/chatgpt-handoff-repository-enrichment.md)
- [Accepted decisions](development/v02%20-%20ORCS%20Pilot%20Enrichment/decision-log.md)
- [Ideas and open questions](development/v02%20-%20ORCS%20Pilot%20Enrichment/ideas-questions.md)
- [Publication identifier resolver](development/v02%20-%20ORCS%20Pilot%20Enrichment/publication-identifiers.md)
- [Development iterations](development/README.md)
- [Curated ORCS outputs](../outputs/orcs/README.md) and [the three search profiles](../searches/orcs/README.md)

## Resource research and definitions

- [Repository-interface research](resources/README.md): native filters, hierarchy and programmatic-contract questions.
- [ORCS vocabulary](orcs/vocabulary/README.md): preserved source-field definitions; these do not automatically translate to other repositories.
- Entity and evidence definitions are in the module specification. Research notes and query examples do not authorize implementation.
- [OmicsDI status](resources/omicsdi/index.md): retired discovery route.

## Conversation and implementation instructions

- [Workflow overview](workflow/README.md)
- [Accession labels](workflow/global/AI-agent-workflow/accession-labels.md)
- [Codex handoff rules](workflow/global/AI-agent-workflow/codex-handoff-rules.md) and [historical rebuild incident](workflow/global/AI-agent-workflow/incident-repeated-rebuilds.md)
- [Proposed user notation](workflow/global/AI-agent-workflow/user-notation.md) — not adopted yet.
- [Project-note recording](workflow/project/AI-agent-workflow/project-notes.md)
- [Code-commenting standard](workflow/global/coding/code-commenting-standard.md)
- [Specification structure](workflow/global/specifications/specification-structure.md), [vision template](workflow/global/specifications/project-vision-template.md), [module template](workflow/global/specifications/module-specification-template.md)
- [Specification lifecycle questions](workflow/global/AI-agent-workflow/specification-lifecycle.md) — rules remain pending.
- [Optional finding-card format](workflow/finding-cards/Finding%20Card%20Instructions.md)

## History and authority

The v01 development folder contains historical ORCS pilot and validation notes. Preserve their original scientific meaning; they do not supply current query inputs or new retrieval authorization. Active specifications describe current requirements; iteration logs record decisions and work. The repository's [AGENTS.md](../AGENTS.md) connects applicable agent instructions. Reusable global notes are local to this repository until explicitly installed elsewhere.
