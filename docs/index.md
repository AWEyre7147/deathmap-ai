# DeathMap-AI documentation

## Start here

- [Project vision](specifications/project-vision-v01.md): purpose and scope.
- [Module specification](specifications/module-01-evidence-discovery.md): evidence rules, boundaries and acceptance criteria.
- [Implemented enrichment guides](<development/v02 - ORCS Pilot Enrichment/README.md>): resource descriptions, processes, commands, options, outputs and key findings.
- [ORCS enrichment outputs](../data/orcs/) and [registered templates](../data/templates/README.md).

The enrichment guides cover accession resolution, PubMed, PMC, GEO, ENA, BioStudies, Figshare, Mendeley Data and institutional library collection. Offline synthesis currently integrates PubMed, GEO, BioStudies and ENA only. Publication association does not establish qualifying screen content or exact screen-dataset attribution. Experimental-file downloads, analysis and the future scientific reasoning layer remain outside these stages.

## Resources and definitions

- [Repository-interface references](resources/README.md).
- [ORCS vocabulary](orcs/vocabulary/README.md).
- [Third-party metadata notices](../THIRD_PARTY_NOTICES.md).

## Proposed support workflow

[Guided support workflow](<development/v00 - Additional Features/guided-support-workflow.md>) describes portable diagnostic packages and assistant instructions for troubleshooting. It remains a design proposal.

## Reference and evaluation scope

ORCS is a saved reference database and enrichment cohort; its former collection
and filtered-search commands are retired. Native field definitions remain in the
ORCS vocabulary. Standalone publisher API enrichments and obsolete institutional
probes are retired; the library collector retains its necessary publisher and
OSU access adapters. Historical recovery material is external to the repository.

ICRAFT comparison, screen-selection rules and post-2022 discovery/evaluation are
planned work. They are not executed or scientifically validated by cleanup.
