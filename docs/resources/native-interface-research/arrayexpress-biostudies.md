# ArrayExpress within BioStudies: native-interface research

Historical observations from 2026-10-06. Capabilities and literal searches require verification before a new adapter is implemented.

## Native interface and translation limits

The [native study page](https://www.ebi.ac.uk/biostudies/studies/E-MTAB-1898) supplied a nine-sample count and experiment-design metadata. Retrieval of its directly linked descriptive JSON was blocked, and SDRF/sample/file traversal was not performed.

The successful index restriction does not justify replacing GEO as the priority or applying the same omics restriction to ENA. Native BioStudies/ArrayExpress search filters and query grammar remain untested.

Evidence: native receipts in `examples/`; generic OmicsDI comparisons are archived.
