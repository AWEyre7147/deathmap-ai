# Saved PubMed enrichment responses — 2026-10-08

`selection.json` binds 415 selected PMIDs to the ORCS index hash and preserves
three unresolved publications. `requests.json` records 90 successful requests
with literal URLs, retrieval timestamps, status, attempt and SHA-256.

`pubmed-N.xml`, `links-RESOURCE-N.json`, and `summary-RESOURCE-N.xml` are native
response bytes. `pubmed.xml` and unsuffixed `links-RESOURCE.json` are derived
merges used by the parser. Native responses are verified against receipts.
`link-counts.json` records 272 GEO, 286 BioProject and 5,101 SRA linked native
IDs. `retrieval-issues.json` records no final retrieval failures.

`code-used/` preserves the exact source bytes used for the completed run, bound
to its manifest hashes. The active modules subsequently received docstring-only
cleanup under the project commenting standard; executable AST equality and
syntax were checked without repeating retrieval or export. The manifest keeps
original execution hashes and separately records current documentation hashes.

No experimental files or article full text were downloaded. Raw PubMed metadata
includes abstracts, references and returned source fields; repository summaries
include descriptive metadata. Source content retains upstream terms. See
[PubMed enrichment](../../../../docs/pubmed-enrichment.md) for limits and scope.
