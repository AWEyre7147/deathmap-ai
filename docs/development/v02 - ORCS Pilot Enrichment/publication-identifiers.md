# Publication identifier resolution

## [PI-1] Authorization and scope
Owner instructions [A139–A142] authorize exact DOI, PMID and PMCID resolution, updating the shared ORCS publication catalog, and regenerating the same three profiles. This is an exception to AG7's live-enrichment restriction. No dataset discovery, article contents, title matching or preprint-to-publication equivalence is added.

## [PI-2] Reusable function and command
`deathmap_ai.publication_identifiers.Resolver.resolve(records)` accepts dictionaries containing one or more of `doi`, `pmid`, `pmcid`. Each dictionary represents one publication. It returns supported identifiers, status, alternatives and retrieval evidence.

```powershell
deathmap-resolve-publication 12345678 PMC123456 --output identifier-results.json
deathmap-resolve-publication --input publications.json --output identifier-results.json
```

JSON input is a list, for example `[{"pmid":"12345678","doi":"10.1234/example"}]`. An input containing multiple identifiers constrains one publication; positional IDs are separate requests. Existing output paths are refused. Install the project again to register the new command, or use `python -m deathmap_ai.publication_identifiers`.

## [PI-3] Sources and failure behavior
PubMed ESearch uses exact article-identifier terms for DOI seeds; EFetch supplies article identifiers for PMIDs. PMC ID Converter supplies related IDs for articles represented in PMC. Returned DOI values must exactly match DOI seeds. Conflicting mappings do not fill missing fields. Missing mappings do not imply absence of a publication or dataset.

Responses and retrieval dates are cached in `data/publication-identifiers/cache`. Requests are paced, with 30-second timeouts and three attempts per invocation. Successful requests survive interruption; failed requests raise an error and may be retried in a later invocation. Historical responses are reused unless a separate refresh is requested.

## [PI-4] ORCS maintenance
`scripts/enrich_orcs_identifiers.py --archive <archive-directory>` backs up catalog JSON, CSV and manifest, then fills missing identifier fields and stores lookup provenance. `scripts/refresh_orcs_identifier_outputs.py --archive <archive-directory>` generates the three profiles, verifies workbook values, then archives previous runs and retains one active run per condition.

Existing ORCS identifiers remain source-reported; added identifiers receive separate NCBI evidence in the generated ledger. DOI/PMID/PMCID links are derived URLs, not additional identifier retrievals. Do not interpret identifier resolution as scientific eligibility or dataset attribution.

Official interfaces: [PMC converter](https://pmc.ncbi.nlm.nih.gov/tools/id-converter-api/), [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25499/).
