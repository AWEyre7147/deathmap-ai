---
tags: [deathmap-ai, orcs, vocabulary]
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
---

# ORCS annotated vocabulary

Annotated descriptions of the values that appear in the cached BioGRID ORCS metadata. This directory is separate from `vocabularies/orcs/local/` (exact value lists) and `vocabularies/orcs/metadata-service/` (the service's own term IDs). It adds meaning to those values and does not replace them.

Current repository location: `docs/orcs/vocabulary/`. Earlier local/service vocabulary directories are not present in this source release; exact native values and service terms remain in the saved data catalogs.

## Structure

| Folder | Source file | Contents |
|---|---|---|
| [[screen/index\|screen/]] | `data/orcs/screen-index.json` (2,217 screens) | One page per native screen field |
| [[publication/index\|publication/]] | `data/orcs/publication-index.json` (418 publications) | Publication field definitions and small value tables |
| [[links/index\|links/]] | `data/orcs/publication-screen-links.json` (2,217 links) | Link fields and EVIDENCE_STATUS |

## What each page contains

- **Technical definition**: what the ORCS field records, in documentation language.
- **Plain-language description**: written for an undergraduate reviewer with no CRISPR background.
- **Where it goes in DeathMap**: the workbook column(s) the field feeds.
- **Values table**, with one of three page types:
  - `values`: every distinct value with a description and screen count.
  - `format`: free-text or numeric fields. Shows value patterns and the most common values, not individual descriptions.
  - `field_only`: identifiers and free text. Shows the field definition only.

Self-explanatory fields such as titles, author lists, PMIDs and URLs are not described.

## How descriptions were produced

| Field | Technical description | Plain-language description |
|---|---|---|
| Small controlled fields (SCREEN_TYPE, EXPERIMENTAL_SETUP, PHENOTYPE, ENZYME, ANALYSIS, SCORE types, and others) | Hand-authored by Perplexity | Hand-authored by Perplexity |
| CELL_LINE | Saved Cellosaurus annotation (accession, category, disease, origin), unchanged from `vocabularies/orcs/local/CELL_LINE.md` | Generated from the Cellosaurus fields using a disease glossary |
| CELL_TYPE | ORCS value | Rule-based, with hand-authored text for non-cancer types |
| LIBRARY | Family and scope assigned from the library name | Scope category explanation |
| CONDITION_NAME | Category assigned by rules; drug mechanism class hand-assigned; immune values hand-described | Category or class explanation |

Each page's front matter records its `description_basis`.

## Flags and cautions

- **Normalized candidate** columns are proposals for the DeathMap controlled vocabularies. They are not final values.
- **CELL_LINE `immune-role` flag**: cancer-derived lines that commonly act as immune cells (Jurkat, RAW 264.7, J774, THP-1, NK-92, and others). Cellosaurus "Cancer cell line" describes where a line came from, not its role in a screen.
- **CELL_LINE `TNBC model` flag**: a hand-curated list of common triple-negative breast cancer models (human and mouse). Confirm against Cellosaurus and the paper.
- **LIBRARY scope** is assigned from the name only. A targeted library is never labeled genome-wide on purpose, but the reviewer confirms scope (pilot-scope PS3).
- **CONDITION_NAME PubChem CIDs** come from automated name lookup and can occasionally match the wrong compound. Verify before using them as identifiers.
- **CONDITION_NAME vs. EXPERIMENTAL_SETUP**: the condition page shows which EXPERIMENTAL_SETUP ORCS gave each condition. This exposes immune screens filed under other setups, such as macrophage phagocytosis screens under "Other" (pilot-scope PS18).

## Regenerating

The generator scripts are in `_generator/`. They read the three ORCS JSON files and the parsed Cellosaurus table (`cell_lines_parsed.json`) and rewrite this directory. Hand-authored text lives in `small_vocabs.py`, `fields.py`, `bio_rules.py`, `condition_rules.py` and `drug_classes.py`. Edit those files rather than the generated Markdown.
