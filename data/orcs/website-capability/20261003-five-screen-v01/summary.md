# ORCS screen-page capability test — 2026-10-03 owner review

## Findings

ORCS's homepage currently reports **2,217 screens and 418 publications**, version
2.0.18, agreeing with the saved unique-screen count. Relevant scopes are 1,020
filter-hit screens, 1,176 distinct screens in the review workbook, or all 2,217
ORCS screens. Publications can be enriched once each rather than per screen.
The workbook contains 92 publications, of which 76 have direct filter hits.

The screen pages add publication titles, descriptive link destinations,
Cellosaurus/ontology identifiers, and ORCS-hosted source-supplement links.
Most design descriptions, notes and significance metadata already exist in the
saved screen-list response. No GEO/SRA/ENA/BioProject-style accession was found
in the four successfully captured metadata excerpts. This small sample cannot
establish their absence elsewhere. Addgene links identify libraries/materials,
not sequencing datasets. Source supplements are possible supporting assets;
their URLs alone do not prove what they contain or an exact screen-dataset link.

One linked ORCS publication page was also inspected through the web reader:
[Dataset/2](https://orcs.thebiogrid.org/Dataset/2) reports title, author list,
abstract, journal, publication date, PMID and a supplementary-file link. Thus
publication enrichment can obtain useful bibliographic fields from ORCS itself;
PMID-based external enrichment is an alternative, not yet performed. This page
was inspected separately; it is not counted as one of the timed script captures.
ORCS's `/Dataset/` URL denotes a publication summary here, not a GEO/SRA identity.

## Fixed sample and capture outcome

Three direct hits (16, 18, 65), one unresolved screen (572), and one publication
context screen (1) were selected from saved order across distinct publications.
The sample is deliberately small and not representative of all page layouts.

| ORCS screen ID | Final programmatic outcome | Saved excerpt bytes | Final-attempt seconds |
|---|---|---:|---:|
| 16 | failed | — | 0.219 |
| 18 | success | 6141 | 0.187 |
| 65 | success | 6207 | 0.188 |
| 572 | success | 5621 | 0.343 |
| 1 | success | 6458 | 0.172 |

There were ten HTTP requests across five fixed screens; all returned HTTP 200.
Initial parsing stopped at the words “Score Distribution” inside embedded JSON-LD,
before the displayed metadata. A corrective pass was bounded to one further
attempt per screen. Screen 16's second attempt failed before the boundary bug was
fully diagnosed; it was not requested again. The remaining four pages succeeded
after switching to the actual HTML heading. Failed attempts remain in receipts.
Screen 16 was independently viewable through the web reader, so its parser failure
is not evidence of a missing ORCS record. Initial failed bodies were not retained;
that is a limitation of this prototype. The final parser saves the metadata excerpt
before its identity check. No score table or supplementary file was downloaded.

Successful capture latency was 0.172–0.343 seconds
per page, excluding the intentional one-second inter-request delay. The metadata
excerpts averaged 6,107 bytes. Scaling only that measured excerpt size gives
**13.5 MB for all 2,217 screens** (about 7.2 MB for the workbook's 1,176).
The existing complete metadata index is **3.51 MB**. JSON records, indexes,
receipts and publication metadata add overhead; retaining multiple versions
multiplies storage. A companion metadata database would plausibly be tens of MB
per snapshot, but its precise size was not benchmarked. Full HTML mirrors were
not measured. The script read only 16,384 bytes per successful response before
closing at the metadata boundary.

At the measured latency plus the script's one-second delay, a serial 2,217-page
pass extrapolates to **45 minutes**, excluding failures, backoff and publication pages.
This is an estimate, not a throughput guarantee or permission to crawl routinely.

## Existing bulk resources

ORCS already provides a structured metadata route:

- [REST documentation](https://wiki.thebiogrid.org/doku.php/orcs:webservice):
  `/screens/` returns screen metadata in JSON/tab form and requires a free key.
  Its documented maximum is 10,000 rows per request, enough for today's count.
  Our saved index already uses this metadata approach. The singular `/screen/ID`
  endpoint returns score results and is outside this metadata-only test.
- [Index-file documentation](https://wiki.thebiogrid.org/doku.php/orcs:downloads:screen_index):
  `.index.tab.txt` contains screen annotations. Its documented columns largely
  match the saved index and do not include full publication bibliographies or
  an explicit repository-accession column.
- [Current release listing](https://downloads.thebiogrid.org/BioGRID-ORCS/Current-Release/)
  resolves to release 2.0.18, compiled September 9, 2025. It lists human and mouse
  archives at 717.79 MB and 54.73 MB respectively. These include screen results
  plus annotations, so they are not equivalent to a small metadata-only resource.
  No archive was downloaded.
- [Latest release](https://downloads.thebiogrid.org/BioGRID-ORCS/Latest-Release/)
  provides stable LATEST filenames for scripting. A standalone enriched metadata
  database covering everything on the website was not established by this check.

Recommendation: use the native bulk metadata index as the base and retain a
small supplemental collection keyed by SCREEN_ID and reported publication ID.
Check the ORCS release/version first and refresh only as needed; changed existing
records also need revalidation, not just new IDs. Establish publisher pacing and
update policy before a full recurring collection. Storage is manageable; the
tradeoff is parser maintenance and deciding which new evidence merits review.

## Verification and preserved outputs

Metadata identity checks compare native screen name and publication association;
links are retained without fetching them. Four offline parser tests include
script-embedded boundary text and mismatched identities. Existing workbook bytes
are unchanged. All 409 historical SQ01 preservation checks pass through the
existing authorized workbook-transition rule. No current IDs were changed,
no routine job was created, and no workbook enrichment was performed.

Artifacts: [metrics](metrics.json), [manifest/receipts](manifest.json), and
`screen-*.metadata.html` / `screen-*.json` for the preserved excerpts and fields.
The failed screen 16 excerpt is incomplete and must not be treated as a successful
capture. Source retrieval timestamps are UTC and remain in the individual receipts.

Learning checkpoint: a bulk metadata index, screen-page evidence and publication
metadata are complementary layers. Keeping them separate prevents ORCS's use of
“dataset” for a publication or result set from becoming a false repository link.
