# PubMed enrichment

## Scope and outputs

The owner-finalized [PubMed Enrichment template](../data/templates/PubMed-Enrichment.xlsx)
contains Publication, Repository Records, SRA Accessions, MeSH and MeSH Links.
The [template manifest](../data/templates/PubMed-Enrichment.manifest.json) records
its hash and date policy. Dates are literal text in `MM;DD;YYYY` order;
month/year precision uses `MM;YYYY` and year-only uses `YYYY`. Missing components
are never inferred. Canonical JSON keeps ISO notation and source precision.

The shared database is `data/orcs/pubmed-enrichment.json`, with an Excel view
`data/orcs/PubMed-Enrichment.xlsx` and manifest `pubmed-enrichment.manifest.json`.
Publication associations use PMID. The JSON also maps ORCS PUBLICATION_ID to
PMID and retains unresolved publications, source files and direct relationships.
Repository Records orders PMID, Resource, Accession, Native Entity Level,
Reported Data Type, Title and Description.

Each current ORCS run has a `pubmed-enrichment/` subdirectory with its own
workbook and receipt. These are subsets of the shared database; MeSH counts and
PMID lists are recalculated for each subset. No ORCS search is rebuilt. Records
without verified PMIDs remain in the shared database's unresolved mapping and
the relevant workbook manifest; they are not silently matched by title or DOI.

## Retrieval and reproducibility

The strategy is PMID-led PubMed EFfetch, followed by explicit ELink routes
`pubmed_gds`, `pubmed_bioproject`, and `pubmed_sra`; ESummary retrieves the
distinct linked GEO, BioProject and SRA records. EFfetch batches 100 PMIDs,
ELink batches 50 with repeated `id` parameters to preserve individual source
PMIDs, and ESummary batches 100 native IDs. Native bytes, exact request URLs,
timestamps and hashes are in `data/orcs/pubmed-enrichment-source/20261008/`.
Merged XML/JSON files are derived parsing inputs; original batch responses are
the byte-exact evidence. JournalIssue/PubDate is the publication date source.

Requests are serial, paced at least 0.4 seconds apart, with 30-second timeouts
and two attempts. Limits are 250 request attempts, 15 minutes per invocation
and 10,000 summary records per resource. Limits stop rather than truncate.
Successful byte-checked responses can be resumed; failed retrieval is never
classified as an empty relationship. No API key is required or saved.

Run the implemented milestone against an approved selection and a new output
destination; existing workbooks/database are refused:

```powershell
python -m deathmap_ai.pubmed_milestone --root . --source data/orcs/pubmed-enrichment-source/20261008 --saved-only
```

This exact command is a saved-response reproduction example. Because the
published outputs already exist, it refuses to overwrite them. To reproduce,
use a separate checkout/output copy with the existing enrichment outputs
removed; do not remove reviewed files in place. Without `--saved-only`, it
requests missing responses and reuses hash-verified cached responses.

Focused tests use small inspectable fixtures and the standard-library runner:

```powershell
python -m unittest discover -s tests -p test_pubmed_enrichment.py -v
```

Workbook validation compares every projected row, preserves template headers,
column widths and panes, and checks compatibility namespace declarations.
Native Excel opening is recorded separately in the milestone manifest.

## Interpretation and next goals

This stage captures direct PubMed associations, not comprehensive repository
coverage. An empty link is not evidence that no deposit exists. A publication
association is not proof that a dataset contains a qualifying CRISPR screen.
GEO GSE72841 illustrates why repository hierarchy traversal is needed: it may
be omitted from direct publication links while related series are returned.

The next goals are repository-specific enrichment of GEO, BioStudies–ArrayExpress
and ENA. Their contracts must address hierarchy, native descriptions,
publication matching, unresolved relationships and screen attribution. SRA
accessions are retained for later review; experimental files and detailed
sample-level expansion remain outside the current milestone.
