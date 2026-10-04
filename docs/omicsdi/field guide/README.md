# Observed OmicsDI field guide

API help checked 2026-09-19: [official documentation](https://www.omicsdi.org/help/api).
No server API version was reported. This guide covers the six unchanged v02
queries, 76 saved search pages and 137 saved detail responses.
Search observation dates span 2026-09-08T17:36:22.209111+00:00 through 2026-09-19T19:41:16.755608+00:00.
Original historical dates remain in source records; this is a cached/live mixture.
Counts include duplicate observations and whole pages, including any unadmitted entries.
Historical 89 receipts retain their 50-within/39-excess accounting. New reservations
are counted separately, including uncertain attempts without usable responses.

These are observed fields, not an exhaustive OmicsDI schema. Search and detail
shapes vary. For identity, search source/id and detail database/accession are
observed; conflicting alternatives are preserved, never silently merged.
Detail repository aliases differing from requested identity are withheld from
structured mapping; their complete native metadata remains in source_records.
Repository labels listed below are exactly those observed. Any repository absent
from this list was not observed; this guide makes no completeness claim about the
universe of repositories. No additional searches were used to fill this guide.

Per-source tables count presence across that source's search/detail objects. An
absent field is not evidence of scientific absence. Types and examples describe
native JSON; objects/arrays also have child rows. Examples are truncated, and
contact values are not repeated here. Every field and raw response remains saved.
Unknown fields have no invented semantic definition or target assignment.

Mapping applies only after identity/association checks. Structured publication
identifiers are syntax-normalized; multiple associations use arrays. Publication
sharing never creates a screen–dataset link. Narrative protocols and publication
abstracts remain separate evidence; no experiment extraction or scientific review
is performed. Source-native repository labels are preserved rather than aliased.

[Common fields](common-fields.md). Machine inventory: `outputs/immune-crispr-coculture-v02/field_inventory.json`.
Regenerate offline: `python -B -m deathmap_ai.discovery_v02 export` (after package installation).

| Source | Search objects | Detail objects | Notes |
|---|---:|---:|---|
| EGA | 0 | 2 | [EGA](ega-detail-label.md) |
| ENA | 0 | 33 | [ENA](ena-detail-label.md) |
| GEO | 0 | 11 | [GEO](geo-detail-label.md) |
| MassIVE | 0 | 2 | [MassIVE](massive-detail-label.md) |
| Pride | 0 | 7 | [Pride](pride-detail-label.md) |
| biostudies-arrayexpress | 122 | 17 | [biostudies-arrayexpress](biostudies-arrayexpress.md) |
| biostudies-literature | 1315 | 63 | [biostudies-literature](biostudies-literature.md) |
| biostudies-other | 7 | 0 | [biostudies-other](biostudies-other.md) |
| ega | 21 | 0 | [ega](ega.md) |
| geo | 659 | 0 | [geo](geo.md) |
| iProX | 0 | 2 | [iProX](iprox-detail-label.md) |
| iprox | 3 | 0 | [iprox](iprox.md) |
| jpost | 6 | 0 | [jpost](jpost.md) |
| massive | 20 | 0 | [massive](massive.md) |
| metabolights_dataset | 3 | 0 | [metabolights_dataset](metabolights_dataset.md) |
| pride | 53 | 0 | [pride](pride.md) |
| project | 914 | 0 | [project](project.md) |
