# Resource research

These notes describe interfaces, filters and repository hierarchies for evaluation during v02 ORCS enrichment. They are research references, not accepted query configurations, guarantees of current API behavior or implementation authorization. Examples do not define scientific eligibility.

The owner curates native-interface documentation and evaluates ORCS publication overlap. AI agents compare the relevant programmatic interface and propose a bounded metadata-retrieval contract. Record missing, uncertain or unverified capabilities rather than assuming browser filters have API equivalents.

## Repository notes

- [GEO](databases/primary/NCBI%20GEO.md)
- [ENA](databases/primary/ENA.md)
- [ArrayExpress within BioStudies](databases/primary/BioStudies%20-%20ArrayExpress.md)
- [PRIDE](databases/proteomics/PRIDE.md), [MassIVE](databases/proteomics/MassIVE.md), [jPOST](databases/proteomics/jPOST.md), [iProX](databases/proteomics/iProX.md)
- Secondary: [ExpressionAtlas](databases/secondary/ExpressionAtlas.md), [BioStudies literature](databases/secondary/BioStudies%20Literature.md)

The primary/proteomics/secondary folders organize notes; their presence is not an approved implementation order. A literature or reanalysis record is not automatically an original experimental deposit. Follow native accession hierarchies and preserve source identity.

Before implementation, agree the identifiers/seeds, endpoints, allowed metadata depth, pagination, pacing, retry/resume behavior, evidence mapping, resource limits and completion criteria. No experimental-file retrieval is authorized by these notes. OmicsDI's discovery route is retired.
