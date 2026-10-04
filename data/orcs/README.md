# Shared ORCS metadata databases
## [DB1] Resource inventory
These shared catalogs cover the ORCS 2.0.18 index observed on 2026-10-04. They are independent of filtered search runs.

| Entity | JSON database | CSV view | Records |
|---|---|---|---:|
| Screens | [screen-index.json](screen-index.json) | [screen-metadata.csv](screen-metadata.csv) | 2,217 |
| Publications | [publication-index.json](publication-index.json) | [publication-metadata.csv](publication-metadata.csv) | 418 |
| Screen-publication associations | [publication-screen-links.json](publication-screen-links.json) | [publication-screen-links.csv](publication-screen-links.csv) | 2,217 |

JSON files contain arrays of records; CSV files contain the same uppercase fields. Publication lists/dictionaries are JSON-encoded inside CSV cells; empty values remain empty. IDs remain strings. pandas can read either format without SQL.

## [DB2] Publication data dictionary
The publication database is extracted ORCS website metadata, not a native REST publication response. Each row corresponds to one ORCS /Dataset/ publication summary page.

| Field | Meaning |
|---|---|
| PUBLICATION_ID | Native ORCS publication-page ID from /Dataset/<ID>; not a repository dataset accession or internal DeathMap ID |
| SOURCE_TYPE, SOURCE_ID | Exact source namespace/identifier from the associated native screen records; includes pubmed and prepub |
| TITLE, AUTHORS, ABSTRACT, JOURNAL, PUBLICATION_DATE | Reported publication-header text; whitespace collapsed; missing values null; authors retained as one full reported string |
| PAGE_SOURCE_TYPE, PAGE_SOURCE_ID | Identifier assertion displayed in the page citation, preserved independently of cache identity |
| PMID | Cached pubmed identifier promoted only when the page citation agrees |
| DOI | Exact cached SOURCE_ID when DOI-shaped; no canonical DOI guessed from a prepub URL |
| SUPPLEMENTARY_FILES | Reported asset labels and URLs; contents not retrieved and dataset attribution not assumed |
| LINKS | Header link labels/URLs, including source and supplementary links; targets not followed |
| SCREEN_IDS, SCREEN_COUNT | Native screen IDs explicitly associated by the website browse listing |
| PUBLICATION_URL | Source ORCS publication-page URL |
| FIELD_LOCATORS | Header locations supporting the extracted fields |
| REVIEW_ISSUES | Source discrepancies retained for review |
| RETRIEVED_AT | UTC timestamp for the successful page metadata retrieval |
| SOURCE_METADATA_FILE, SOURCE_METADATA_SHA256 | Saved header excerpt and its SHA-256 hash |

Titles, authors, abstracts and dates are present for all 418 records. Journals are present for 411. There are 412 agreed PMIDs and six prepub records; five have DOI-shaped cached identifiers and one retains a URL as SOURCE_ID. Six prepub pages display conflicting PUBMED-labelled numbers; preserve these page assertions without promoting them to verified PMIDs.

607 supplementary-link mentions are stored across the publications. They are asset metadata, not 607 established experimental datasets.

## [DB3] Joins and provenance
Join screen-index SCREEN_ID to publication-screen-links SCREEN_ID, then links PUBLICATION_ID to publication-index PUBLICATION_ID. SOURCE_TYPE/SOURCE_ID remains an independent identifier/provenance pair. A publication association is not proof of any screen-repository dataset relationship.

- [Publication manifest](publication-index.manifest.json): schema, counts, source version, input/file hashes and collection policy.
- [Publication verification](publication-verification.json): complete screen coverage, unique IDs, source re-parsing and JSON/CSV agreement.
- [Publication source snapshots](publication-source/README.md): saved metadata headers, browse response, homepage observation and durable request receipts.
- screen-index.manifest.json, download-receipt.json, relocation.json and cache-summary.json: original screen source provenance and verification.
- metadata-service-vocabularies.json and its manifest: byte-exact saved service vocabulary snapshot.
- website-capability/: previous small screen-page metadata feasibility sample.

The existing screen index and CSV were not changed by this task. No gene-level results, screen score endpoints, publication-screen downloads, supplementary contents or external bibliographic pages were retrieved.

## [DB4] Repeatable collection and planning
The local collector is python -m deathmap_ai.orcs_publications with src on PYTHONPATH. It resumes data/orcs/publication-source/20261004-v01, uses bounded reads and per-request timeouts, waits one second between page attempts, and permits at most three cumulative attempts per page. Successful receipt/header pairs are reused with hash checks; incomplete capture does not publish a complete database.

For a later resource refresh, create a new dated collection and retain the original snapshot. The current collector implements this dated collection, not a generalized refresh scheduler.

[Field-source map](../../docs/orcs/workbook-field-source-map.md) and [enrichment plan](../../docs/orcs/enrichment-plan.md) consider both complete catalogs. They plan future local joins; they do not enrich the previous search workbook.
