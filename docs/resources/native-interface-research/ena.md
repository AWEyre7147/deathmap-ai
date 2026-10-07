# ENA: native-interface research

Historical observations from 2026-10-06. Capabilities and literal searches require verification before a new adapter is implemented.

## Native interface and translation limits

The [native project page](https://www.ebi.ac.uk/ena/browser/view/PRJNA460738) and its [linked project XML](https://www.ebi.ac.uk/ena/browser/api/xml/PRJNA460738) supplied project-level metadata, including secondary accession `SRP230949` and parent project `PRJNA28259`. New checks added field schemas and one directly constrained run lookup, without recursive traversal.

ENA documents result-specific discovery through `/ena/portal/api/searchFields?result=...` and `/returnFields?result=...`, with `AND`/`OR` query components and explicitly requested return fields ([official advanced-search documentation](https://ena-docs.readthedocs.io/en/latest/retrieval/programmatic-access/advanced-search.html)). Its result types distinguish `study`, `read_study`, `read_experiment`, `read_run`, and `tsa_set`; do not assume fields apply identically across those entities.

Actual `result=read_run,format=json` requests returned 160 searchable fields and 195 returnable fields ([search schema](https://www.ebi.ac.uk/ena/portal/api/searchFields?result=read_run&format=json), [return schema](https://www.ebi.ac.uk/ena/portal/api/returnFields?result=read_run&format=json)). Relevant searchable fields include `library_strategy`, `library_source`, `library_selection`, `library_layout`, `cell_line`, `cell_type`, `study_title`, `experiment_title`, `tax_id`, `study_accession`, `sample_accession`, `first_public`, and `last_updated`; returnable fields additionally include file-link fields such as `fastq_ftp`.

The four library fields are described as controlled-value fields, while cell-line/type fields are text fields ([search schema](https://www.ebi.ac.uk/ena/portal/api/searchFields?result=read_run&format=json)). The complete controlled-value enumerations and biological grouping rules were not assessed.

```text
Executed native lookup:
GET https://www.ebi.ac.uk/ena/portal/api/search
result = read_run
query = study_accession="PRJNA460738"
fields = run_accession,study_accession,sample_accession,library_strategy
format = json
limit = 2
```

The actual JSON array contains one row: `run_accession="SRR10506495"`, `study_accession="PRJNA460738"`, `sample_accession="SAMN09071406"`, and `library_strategy="RNA-Seq"` ([native response](https://www.ebi.ac.uk/ena/portal/api/search?result=read_run&query=study_accession%3D%22PRJNA460738%22&fields=run_accession%2Cstudy_accession%2Csample_accession%2Clibrary_strategy&format=json&limit=2)). Library strategy was returned here; a separate query restricting on its value was not executed.

ENA documentation identifies TSA as transcriptome shotgun assembly records ([ENA data classes](https://ena-docs.readthedocs.io/en/latest/retrieval/general-guide/data-classes.html)). Do not treat TSA as a universal RNA-seq restriction or a tested OmicsDI filter.

Evidence: native receipts in `examples/`; generic OmicsDI comparisons are archived.

For translation, use the ENA schema for the requested native entity rather than forcing OmicsDI's omics label. Do not filter by individually hand-picked cell lines to maximize pilot recovery; any biological-class rule remains an owner decision.
