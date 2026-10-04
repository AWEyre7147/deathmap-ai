# Owner review decisions

## [RD1] Entity identifier display — 2026-10-03

Owner-requested formats, recorded for later implementation:

| Entity | Format |
|---|---|
| Publications | PUB-0001, PUB-0002, … |
| Screens | SCR-0001, SCR-0002, … |
| Datasets | DATA-0001, DATA-0002, … |
| Screen groups | SG-0001, SG-0002, … |
| Screen–dataset links | SDL-0001, SDL-0002, … |
| Sources & Evidence | EVI-0001, EVI-0002, … |

Status: accepted owner preference; not implemented. Current workbook and IDs
remain unchanged. Future implementation must preserve native identifiers and
existing foreign-key relationships, persist the assigned numbers across reruns,
and avoid renumbering after sorts or filtering. Numbering scope and migration
mapping should be made explicit when implemented; no current IDs are reassigned.

## [RD2] Small ORCS website capability test — 2026-10-03

The owner authorized A16's small fixed sample now, plus investigation of the
number of screen pages and existing bulk resources. This advances beyond handoff
11's stop-before-enrichment boundary only for this capability test. It does not
authorize routine crawling, a full mirror, workbook enrichment or external
repository retrieval. Five screen pages are selected from saved results in order
across distinct publications. ORCS documentation and one linked ORCS publication
page are inspected to assess available metadata. No result/supplement files are
downloaded and no existing outputs are changed.

## [RD3] ORCS searchable-data location and scope — 2026-10-03

The owner designates `data/orcs/` as the home for ORCS-related databases searched
by the project. Screen annotation metadata are wanted; single-screen score
results and cross-screen score matrices are not needed. The initial index copy
retains its original 2026-09-04 retrieval date. A fresh API download remains pending
the local access-key path. Historical outputs/configurations are preserved.

### [RD3a] Relocation implemented

The owner subsequently requested moving both JSON and CSV and updating repository
consumers. They now reside at `data/orcs/screen-index.json` and
`data/orcs/screen-metadata.csv`. Active paths and source links have been updated.
The two original files were removed from their former location only after matching
hashes. Frozen run outputs and prior provenance strings remain unchanged and are
resolved through the two-file hash-verified relocation map. No download or new
search was performed for this move.

### [RD3b] Fresh metadata verification completed

The supplied local ORCS key was used for one metadata-only API request on
2026-10-03 (America/New_York). All 2,217 screens matched the existing index;
JSON and CSV bytes were identical after serialization. data/orcs/download-receipt.json
records the verification without the key. No score data or new discovery run
was requested, and the existing annotation mappings remain valid.
