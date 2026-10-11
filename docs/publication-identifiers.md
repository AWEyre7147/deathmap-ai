# Publication identifier resolution

`deathmap_ai.publication_identifiers.Resolver.resolve(records)` accepts dictionaries
containing one or more of `doi`, `pmid` and `pmcid`. Each dictionary represents one
publication. Results preserve supported identifiers, status, alternatives and
retrieval evidence. This utility does not discover datasets or retrieve articles.

## Command and input

```powershell
deathmap-resolve-publication 12345678 PMC123456 --output identifier-results.json
deathmap-resolve-publication --input publications.json --output identifier-results.json
```

JSON input is a list, for example
`[{"pmid":"12345678","doi":"10.1234/example"}]`. Multiple identifiers within one
record constrain one publication; positional identifiers represent separate
requests. Existing output paths are refused. The command is also available as
`python -m deathmap_ai.publication_identifiers`.

## Sources, caching and failures

PubMed ESearch uses exact article-identifier terms for DOI seeds. EFetch supplies
article identifiers for PMIDs; PMC ID Converter supplies related identifiers for
articles represented in PMC. Returned DOIs must exactly match DOI seeds.
Conflicting mappings do not fill missing fields. Missing mappings do not imply
absence of a publication or dataset.

Responses and retrieval dates are cached in `data/publication-identifiers/cache`.
Requests are paced, with 30-second timeouts and three attempts per invocation.
Successful requests survive interruption; failed requests raise an error and may
be retried later. Historical responses are reused unless a refresh is requested.

## ORCS catalog maintenance

`scripts/enrich_orcs_identifiers.py --archive <archive-directory>` backs up catalog
JSON, CSV and manifest files before filling missing identifiers with provenance.
`scripts/refresh_orcs_identifier_outputs.py --archive <archive-directory>` generates
the three profiles, verifies workbook values, archives previous runs and retains
one active run per condition. These maintenance scripts change catalog/run files;
they are separate from an ordinary saved-metadata search.

Existing ORCS identifiers remain source-reported. Added identifiers receive
separate NCBI evidence. DOI/PMID/PMCID links are derived URLs, rather than additional
retrievals. Identifier resolution does not establish scientific eligibility or
dataset attribution.
