# DeathMap-AI documentation

## Start here

The metadata pipeline supports cached ORCS discovery, publication identifier
resolution, PubMed enrichment, GEO Series/sample enrichment and BioStudies–
ArrayExpress study/IDF/SDRF enrichment. ENA enrichment, screen attribution and
evidence harmonization remain future work. The executable package remains v0.1.0.

- [Project vision](specifications/project-vision-v01.md): purpose and scope.
- [Module specification](specifications/module-01-evidence-discovery.md): entity
  boundaries, evidence rules and implemented behavior.
- [Repository enrichment outputs](../data/orcs/) and
  [owner templates](../data/templates/README.md).
- [Curated ORCS outputs](../outputs/orcs/README.md) and
  [search profiles](../searches/orcs/README.md).

## Resources and definitions

- [Repository-interface references](resources/README.md).
- [ORCS vocabulary](orcs/vocabulary/README.md): preserved source-field definitions.
- [OmicsDI status](resources/omicsdi/index.md): retired discovery route.
- [Third-party metadata notices](../THIRD_PARTY_NOTICES.md).

Current work uses descriptive metadata and identifiers. Publication association
does not establish qualifying screen content or exact screen–dataset attribution.
Experimental-file downloads, analysis and future reasoning are outside the
implemented enrichment stages.
