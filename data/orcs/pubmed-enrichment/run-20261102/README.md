# ORCS PubMed refresh — November 2, 2026

Fresh EFetch/ELink/ESummary retrieval for the 415 verified PMIDs in the 418-publication
ORCS index. The other three publications remain explicit in canonical metadata.
All 90 requests succeeded without cache reuse. No experimental files were downloaded.

The owner-edited template was preserved byte-for-byte. Its manifest and maintained
pipeline now support Publication Index, PMR repository indices and PMS SRA
experiment/run indices. Repository Records includes parent SRA experiment summaries
so every SRA row has an explicit parent. Dates retain literal source precision.

| Sheet | Rows |
|---|---:|
| Publication | 415 |
| Repository Records | 5,681 |
| SRA Accessions | 5,822 |
| MeSH | 2,781 |
| MeSH Links | 6,724 |

Native batches and `requests.json` retain the exact query URLs, response hashes and
retrieval times. Merged XML/JSON files are derived parsing inputs. `database.json`
preserves native PMID-based rows plus the indexed `display_rows` used by the
workbook. `publication-registry.json` identifies the selected publication mappings.
`stage-receipt.json` binds the run to its input, template, command and workbook.
`verification.json` records response-hash, projection, parent-link and workbook
checks; the writer compared all 150,642 exported cells with the projected values.

The shared outputs are in `data/orcs`. Their previous versions and exact hash receipt
are preserved in `previous-shared-outputs/`. Original source responses from October
remain unchanged. Association with a publication does not establish qualifying
CRISPR screen content. See [field mappings](../../../../docs/pubmed-enrichment.md).
