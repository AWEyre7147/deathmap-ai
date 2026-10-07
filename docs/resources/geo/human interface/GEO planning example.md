# GEO planning example: filters first

## [HG-1] Choose the interface
Worked example: **native GEO (Entrez gds)**. This is not an OmicsDI expression or an authorization to implement native discovery. Evidence: [saved Perplexity assessment](../progress/perplexity-01/Native%20GEO%20search%20design%20for%20the%20cancer%E2%80%93immune%20CRISPR%20pilot.md).

## [HG-2] Filter menu
| Property you choose | Available control | Example choice | Use for pilot? |
|---|---|---|---|
| Kind of record | Entry Type | GEO Series, gse[ETYP] | Yes for Series intake; Series is not one screen |
| Organism | Organism | Human OR mouse, [ORGN] | Matches pilot scope; missing annotations may be excluded |
| Assay/data type | DataSet Type | Expression profiling by high throughput sequencing, [GTYP] | Leave unrestricted: guide-count screen deposits can be Other |
| Has indexed publication link | PubMed-link filter | gds pubmed[FILT] | Leave unrestricted: missing citation is not ineligibility |
| Dates | Release/update date fields | No restriction | Pilot had no date gate |
| Cancer cell category | No equivalent verified curated field | Unavailable | Needs model evidence/reference lookup |
| Immune lineage / organoid | No equivalent verified curated field | Unavailable | Needs source descriptions/model review |
| CRISPR screening modality | No equivalent verified library-type field | Unavailable | Needs screening/library evidence |

The last three rows are the remaining scientific gaps. More general keywords do not automatically solve them. If their absence makes GEO unsuitable for a first automated pass, we can retain ORCS as the screen-discovery source and use GEO for identified-accession enrichment instead; that would not demonstrate independent GEO discovery.

## [HG-3] Text criteria, after filters
Candidate seed: CRISPR in All Fields. Do not add organism words here: organism already has its own filter. Do not require cancer AND immune: pilot branches combine with OR. The single CRISPR seed is verified as executable, but incomplete modality terminology and non-screen editing matches remain limitations.

This text criterion is a temporary candidate mechanism, not an approved equivalent to ORCS LIBRARY_TYPE. Decide whether it is acceptable before retrieval.

## [HG-4] What the readable request means
```text
FILTER: record type = GEO Series
FILTER: organism = human OR mouse
TEXT: indexed All Fields contains CRISPR
LATER: establish actual screen, modality and one pilot biological branch
```

Its already-observed native expression is:
```text
gse[ETYP] AND ("Homo sapiens"[ORGN] OR "Mus musculus"[ORGN]) AND CRISPR[ALL]
```

[ORGN] applies the organism filter. [ALL] searches indexed text. Both occur in the same API term parameter, but they do different jobs. Do not paste this into OmicsDI.

## [HG-5] Your blank planning sheet
```text
Source/interface:
Record type filter:
Organism filter:
Other scientifically justified structured filters:
Filters deliberately left unset, and why:
Remaining text requirement(s):
Screening evidence needed after retrieval:
Model evidence needed after retrieval:
Treatment of missing/ambiguous metadata:
Question for a small sample, if needed:
Maximum sample size and stopping point:
```

## [HG-6] What we can do without new research
Select the target interface and organism/record-type choices from existing evidence. Leave inappropriate assay/citation gates unset. Review a few supplied examples before deciding how to handle missing screening/model fields. The next approval should concern a concrete small sample or an enrichment route, not an exhaustive search.
