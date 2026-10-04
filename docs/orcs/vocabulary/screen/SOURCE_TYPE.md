---
field: "SOURCE_TYPE"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 2
description_basis: "hand-authored by Perplexity; review recommended"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# SOURCE_TYPE

## Technical definition

Type of identifier in SOURCE_ID: 'pubmed' (PMID) or 'prepub' (preprint record).

## Plain-language description

Tells you whether the screen comes from a published paper or a preprint.

## Where it goes in DeathMap

Publications.publication_type_reported (candidate); evidence basis for pmid


## Values

| Value | Screens | Technical description | Plain-language description | Normalized candidate |
|---|---:|---|---|---|
| `pubmed` | 2204 | SOURCE_ID is a PubMed identifier (PMID) for a peer-reviewed or indexed publication. | The screen comes from a published paper listed in PubMed, the main index of biomedical papers. | peer_reviewed_publication |
| `prepub` | 13 | SOURCE_ID refers to a preprint or pre-publication record not yet indexed with a PMID. | The screen comes from a paper that was shared before formal peer review (a preprint). | preprint |
