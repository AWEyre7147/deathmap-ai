---
field: "publication-screen links"
entity: link
entity_source: BioGRID ORCS cached metadata
unique_values: 1
description_basis: "hand-authored by Perplexity"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, link]
---

# ORCS publication-screen links

Source: `data/orcs/publication-screen-links.json` (2,217 links, one per screen).

## Fields

| Field | Technical definition | Plain-language note |
|---|---|---|
| `SCREEN_ID` | ORCS screen identifier. | The screen. |
| `PUBLICATION_ID` | ORCS publication (dataset) identifier. | The paper it belongs to. |
| `SOURCE_TYPE` / `SOURCE_ID` | Identifier type and value of the publication (PMID or preprint). | |
| `PUBLICATION_URL` | ORCS publication page. | |
| `EVIDENCE_STATUS` | How the link was established. | How we know the screen belongs to the paper. |

## EVIDENCE_STATUS values

| Value | Links | Technical | Plain-language | Evidence status (workbook) |
|---|---:|---|---|---|
| `direct website browse association; cached source identity` | 2217 | The screen is listed on the ORCS publication page, and its SOURCE_ID matches the cached screen index. | ORCS itself lists this screen under this paper. | `direct` |

## Note on scope

An ORCS publication-screen link says only that ORCS assigns the screen to the paper. It does not establish a repository dataset or a screen-dataset relationship. Those links come from repository enrichment (GEO, ENA, Europe PMC text-mining) and belong in the Screen-Dataset Links sheet with their own evidence.

