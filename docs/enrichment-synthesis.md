# Offline enrichment synthesis

The maintained synthesis stage accepts a publication registry, an ORCS publication
index and four explicit completed enrichment databases. It supports the full
collection, selected subsets, empty repository results and publications without
PMIDs. It never launches enrichment or downloads experimental files. Incomplete
source cohorts and failed source stages fail explicitly rather than appearing
as successful no-hit results. See the [complete runnable workflow](complete-enrichment.md).

## Publication identity and links

`PUB-0001` is a persistent review identity, not a replacement for a PMID, DOI,
PMCID or ORCS publication identifier. The registry retains its mappings. Existing
keys must not change when rows are sorted or new publications are added.
Publication–repository links contain one publication index, repository namespace
and accession per row. Discovery routes remain in the saved enrichment evidence.
Multiple discovery routes support one relationship rather than duplicating it.

Repository records remain distinct across repositories. Sharing a publication
does not establish dataset equivalence or an exact screen relationship. The
pilot omits a general cross-repository relationship sheet while retaining explicit
GEO/ENA hierarchy and the saved source cross-references for later review.

## Row boundaries

Each GEO Series/sample/identifier and each ENA study/sample/experiment/run has one
review row per native identifier. PubMed repository identity includes its resource
namespace. ArrayExpress protocol/section identity includes its study accession;
labels can repeat across unrelated studies. Repeated metadata values are collected
in newline-separated cells, and the companion `source_rows` retain their original
combinations. An index cell can contain several publication indices. Such context
does not assert that every child record contains a qualifying CRISPR screen.

Explicit inverse hierarchy claims collapse into parent-first edges. Only native
relationships are oriented; no hierarchy is guessed from shared titles or papers.
Unidentified source observations remain in evidence rather than being combined
into an artificial blank-ID record.

ArrayExpress protocol/sample/assay attributes are pivoted into exact native field
names. Case variants remain separate, and protocol Contact fields and Value state
are omitted from review only. IDF and SDRF retain their accepted long-form grain.
File listings remain in repository enrichment outputs for a later download stage.

Complete publication dates are literal `YYYY-MM-DD` strings. Partial dates retain
`YYYY-MM`, `YYYY` or native seasonal text; no missing date components are invented.
Original completed workbooks remain unchanged.

## Owner-facing layout revision (2026-10-18)

The synthesis exporter applies `synthesis_layout.py` after projecting native
source keys. It uses Title Case column labels, the owner's repository-specific
accession labels, the requested sheet names and column orders. The five-publication
review copy is saved in a new run directory; its predecessor is preserved.
GEO Repository Links retains all seven owner-confirmed columns. Publication Count,
ArrayExpress study association/URL display fields and SDRF Part are omitted only
from this review view. Native fields and evidence remain saved separately.

Display capitalization can collide for native ArrayExpress fields such as Age
and age. These remain separate columns, labeled Age and Age (2), with exact
source headers recorded in `column-mapping.json`. No metadata values are merged
as a consequence of this naming change. Source `_ch1` suffixes are removed from
GEO display labels only. The exporter preserves native source keys internally.

## Use and evidence

Use `deathmap-enrichment-stage --stage synthesize` with the explicit source flags
documented in the complete workflow. It refuses an existing output directory.
The registry retains Publication index, native ORCS Publication ID and optional
PMID. Compressed `synthesis.json.gz` records source hashes, source-value combinations,
native tables and the registry. The registered layout derives the Excel display
without duplicating those tables on disk. `deathmap-export-enrichment` can export
that compressed canonical file into a fresh workbook without repeating retrieval.
No pilot-specific spreadsheet builder or ChatGPT operation is required. Export
compares every saved cell and header independently; this does not establish native
Excel application behavior or scientific attribution accuracy.

Repository exports use the approved registrations directly under
[`data/templates`](../data/templates/README.md). These preserve the owner's field
removals, column ordering, ArrayExpress pivots and literal date convention. The
four template workbooks are byte-identical to the former review-v2 copies;
maintained defaults now use their consolidated main paths. Earlier templates and
original registrations remain recoverable from the template-history ZIP. Older
saved projections require their matching historical template or an explicitly
reprojected current schema, rather than blindly filling incompatible columns.

The accepted output has 21 sheets. Three accepted ENA broad projects remain
at project level without child expansion; native hierarchy links are retained.
Their child counts remain blank. The owner authorized complete ORCS enrichment
and synthesis on 2026-10-18; that execution does not introduce automatic retrieval
into the standalone synthesis command.

The final 2026-10-18 naming revision uses NCBI BioProject/NCBI BioSample display labels, PubMed-specific SRA link labels, GEO Study for series IDs, GEO Field/GEO Level in repository links and ENA Run in experiment rows. Duplicate Series ID and Accession columns are removed from GEO Sample Records. Native values and source keys remain in companion evidence.
