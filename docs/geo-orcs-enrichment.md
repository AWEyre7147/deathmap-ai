# ORCS GEO enrichment

## Implemented collection command

`deathmap-enrich-geo-collection` (or `python -m deathmap_ai.geo_collection`)
applies the accepted GEO routes to an ORCS publication index, follows explicit
SuperSeries/SubSeries relations, retrieves brief GSM metadata and fills the
registered GEO template. Prior PubMed enrichment is optional: verified native
responses can be reused, while absent caches fall back to the adapter's requests.

Both curated native source packages under `data/orcs` and active GEO working
runs are eligible caches. Archived exploratory runs are not required for reuse
of the completed ORCS source package. Original response dates and hashes remain
preserved; reuse does not imply a new retrieval.

```powershell
python -m deathmap_ai.geo_collection `
  --publication-index data/orcs/publication-index.json `
  --output-dir outputs/geo/my-new-collection
```

Use a new directory for a new collection. `--phase discover`, `samples`,
`project` and `export` support resumption. Successful responses are hash-checked;
changed publication inputs require a new directory. Existing workbooks are
reused only when their template, database and workbook hashes match their receipt.
The default runs all stages and exports one workbook. The single-publication
command remains `deathmap-enrich-geo`.

## Retrieval and interpretation

Routes are PubMed–GEO links, PubMed GEO accession-list fields, complete article-title
phrase searches, Europe PMC accession annotations and GEO-category data links,
PubMed–BioProject–GEO links, and explicit Series hierarchy. Missing PMIDs skip
identifier routes while retaining title discovery. Broad title-word searches,
SRA discovery, article bodies and experimental-file downloads are excluded.

Europe PMC data links now use `category=GEO&sectionLimit=1000`. The documented
section limit controls truncation; the earlier `pageSize` parameter did not.
Initial consolidated responses remain preserved with their actual queries.
Unrelated protein-interaction links are not workbook fields or sample metadata.
See the [Europe PMC reference](https://europepmc.org/docs/EBI_Europe_PMC_Web_Service_Reference.pdf).

GEO requests use `form=text&view=brief`, with `targ=self` for Series and `targ=gsm`
for sample batches. Returned GSM identities must exactly match the Series sample
list; experimental table markers are rejected. Shared samples are retrieved once
while each publication–Series–sample membership remains distinct. Operational
checkpoints are 120 minutes per retrieval phase, 50,000 unique GSMs, 600 sample
batches and 20 MB per sample response. Per-publication adapter limits also apply.

An accession mention or repository path is a candidate association, not proof
of author ownership or a qualifying CRISPR screen. Native citations, absent
citations, citation differences, query warnings and route evidence remain available
for later review. Zero results do not establish that a publication has no GEO data.

## Shared database and workbook

The 2026-10-11 pass completed all 418 publication records: 171 had GEO candidates,
with 519 publication–GSE associations and 503 distinct Series. All 22,139 distinct
GSMs were retrieved. Three records without PMIDs used title-only discovery; ORCS
842 yielded GSE223690 without changing its unresolved publication identifier.

- [Canonical database](../data/orcs/geo-enrichment.json): native Series and GSM
  records stored once, publication candidates/routes/evidence, and source locators.
- [Run manifest](../data/orcs/geo-enrichment.manifest.json): counts, hashes,
  verification and retrieval/reuse statistics.
- [Workbook](../data/orcs/GEO-Enrichment.xlsx): the unchanged owner template's four
  sheets. Series Records has 519 rows; Series Hierarchy 438; Repository Identifiers
  115,718; Sample Metadata 36,303 membership rows.
- [Native source package](../data/orcs/geo-enrichment-source/20261011/README.md):
  exact responses, batch-selection parents, receipts and executed-code snapshots.

Database publication keys are PMIDs when available and `orcs-{PUBLICATION_ID}`
otherwise. These fallback keys are not PMIDs; their workbook PMID cells stay blank.
Series `publication_keys` references this index. Series/sample `source_file` paths
are relative to the source package; publication evidence files are relative to the
publication's `_run_directory`. Native fields retain their repository names and
repeated values. No Discovery Evidence, File Inventory or Contacts sheet is added.

Coverage has not been adjudicated against a complete positive-control set. Dataset
ownership, screen classification and evidence harmonization remain later work.
BioStudies–ArrayExpress and ENA require their own accepted retrieval contracts.
