# DeathMap-AI documentation

## Start here

The metadata pipeline supports cached ORCS discovery, publication identifier
resolution, PubMed enrichment and GEO Series/sample enrichment. BioStudies–
ArrayExpress and ENA enrichment, screen attribution and evidence harmonization
remain future work. The executable package remains v0.1.0.

- [Project vision](specifications/project-vision-v01.md): purpose and scope.
- [Module specification](specifications/module-01-evidence-discovery.md): entity
  boundaries, evidence rules and implemented behavior.
- [Publication identifier resolution](publication-identifiers.md): DOI, PMID and
  PMCID input formats, commands and failure behavior.
- [PubMed enrichment](pubmed-enrichment.md): publication and repository metadata.
- [GEO enrichment](geo-orcs-enrichment.md): Series hierarchy, sample metadata,
  collection commands and interpretation limits.
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
