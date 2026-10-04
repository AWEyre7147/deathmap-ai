# ORCS vocabulary reference annotations

## [VA1] Scope and table layout

The project owner authorized annotation of all existing `CELL_LINE` and
`CELL_TYPE` vocabulary values on 2026-10-01. This extends the reviewed pilot,
independently of the frozen SQ01 discovery outputs. No eligibility filter or
experimental-data retrieval was performed.

- [CELL_LINE](../../../docs/orcs/vocabulary/screen/CELL_LINE.md): ORCS value,
  Cellosaurus category, Reference Description, Accession, Secondary Accession,
  Review Issue.
- [CELL_TYPE](../../../docs/orcs/vocabulary/screen/CELL_TYPE.md): ORCS value,
  BTO Accession, BTO Definition, CL Accession, CL Definition, EFO Accession,
  EFO Definition, Review Issues.

Every native value was examined. Blank reference fields mean no supported
assignment or no reference-supplied value/definition, rather than an unprocessed
row. Unresolved assignments are identified in the review column. Previously
populated pilot evidence remains in its external archive (see [relocation registry](../../../logs/repository-relocations-20261004.json)).
The tables immediately before this expansion are preserved in
[CELL_LINE backup](CELL_LINE-before-full-annotation.md) and
[CELL_TYPE backup](CELL_TYPE-before-full-annotation.md).

## [VA2] Results and limits

| Field | Values checked | Values with reference accession(s) | Values without reference accession |
| --- | --- | --- | --- |
| CELL_LINE | 825 | 771 | 54 |
| CELL_TYPE | 145 | 124 | 21 |

Cell-line matches comprise 628 exact names/synonyms ignoring case, 137
ORCS-linked accessions, three explicit punctuation/Greek-letter variants,
one publication-supported derivative match retained from the pilot, and two
ORCS-linked accessions with species conflicts. These are annotation counts,
not measurements of reviewed retrieval coverage or qualifying-study eligibility.

Cellosaurus reports Cancer cell line for 730 vocabulary values. This is a
reference category attached to the matched identity, not an implemented cancer
filter or a resolution of every screen-specific assignment. Repeated ORCS labels
can share one accession; the count is not a count of distinct cell lines.

The unresolved cell-line values include generic primary populations, yeast
strains, organoid/model descriptions, ambiguous names, and named derivatives
without a supported unique identity. They were checked against the full
Cellosaurus snapshot and representative ORCS metadata links. The unresolved
values are not proof of absence from all other resources or literature.

B16-F10 and BV-2 have conflicting species across cached ORCS contexts. ORCS-linked
accessions are preserved alongside Cellosaurus species and explicit review issues;
neither source's reported species was overwritten. The 143B osteosarcoma versus
glioblastoma conflict remains visible. Obsolete ontology assignments are retained
with review notes instead of silently substituted.

## [VA3] Matching and descriptions

Cellosaurus matches use reference names/synonyms and cached species. Multiple
compatible matches are left unresolved unless ORCS supplies a unique accession.
Only spacing, hyphens, underscores, periods and explicit Greek-letter typography
are permitted as name variants. Biological qualifiers such as Cas9 or knockout
are retained. Parent identities are never substituted for unnamed derivatives.
The previously verified A549-AC candidate retains its publication-based evidence.

Reference descriptions are concise summaries of source-reported species, disease
and tissue/site of origin. Reported disease is the reference's donor-disease
annotation; it does not independently determine cancer classification. Full
selected native fields, parents, publications, entry histories and cautions are
retained in [annotations.json](annotations.json). Secondary accessions are alternate
identifiers for the same entry, not parent-line accessions.

For each cell type, ORCS-linked BTO/CL/EFO identifiers are used first. When an
ontology has no linked identifier, a unique exact label or EXACT synonym match,
ignoring case, can supply an assignment. Related/broad synonyms and fuzzy text
similarity are not used. The assignment method and representative source pages
are recorded individually. This does not verify every screen's biological subtype.

Definitions are copied from the corresponding ontology term's native `def` field.
No definition is synthesized from a label or hierarchy; a missing definition
stays blank. BTO, CL and EFO definitions remain separate. Native EFO identifiers
such as `efo:EFO_0002934` are displayed as `EFO:0002934`; both forms remain in evidence.

## [VA4] Sources and provenance

Reference metadata snapshots retrieved 2026-10-01:

| Reference | Version reported by snapshot | Provider |
| --- | --- | --- |
| Cellosaurus | 56.0; last update 25-June-2026 | [Provider flat file](https://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt) |
| BTO | releases/2021-10-26 | [BRENDA Tissue Ontology](https://github.com/BRENDA-Enzymes/BTO/blob/master/bto.obo) |
| CL | releases/2026-06-08 | [Cell Ontology](https://github.com/obophenotype/cell-ontology/blob/master/cl.obo) |
| EFO | v3.94.0 | [Experimental Factor Ontology](https://www.ebi.ac.uk/efo/efo.obo) |

Attribution: Cellosaurus, CALIPHO/SIB Swiss Institute of Bioinformatics, and BTO,
BRENDA Enzymes, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/);
Cell Ontology under [CC BY 4.0](https://github.com/obophenotype/cell-ontology/blob/master/LICENSE);
EFO, EMBL-EBI, under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).
Source-derived descriptions are summaries; ontology definitions are retained
as reported. Original ORCS source values are unmodified.

The [raw folder](raw/) preserves the locally retrieved metadata snapshots and
receipt files. Large public snapshots are excluded from Git tracking; receipts,
selected native Cellosaurus records and ontology stanzas remain in the curated
annotation artifacts. Each receipt records the source URL, time, size and hash.
ORCS files preserve only Cell Type and Cell Line HTML excerpts, excluding screen
results. Two hundred and five successful source receipts cover four reference
files and 201 representative ORCS pages. The first ORCS parsing attempt failed
because of HTML tags around labels; saved pages were reparsed before completion.

The original cache is
`outputs/orcs/cache/legacy/20260904T213941Z/orcs-screens.raw.json`.
Its hash, native screen/publication contexts, source versions, tool version,
matching methods and review issues are recorded in `annotations.json`.
Frozen discovery artifacts and known-publication evaluation inputs were not changed.

## [VA5] Verification and learning checkpoint

Checks confirm exact table column order, preservation of all 825 and 145 native
values in their existing order, the cached ORCS source hash, reference hashes,
and A-549's primary/secondary accession distinction. Small tests cover ambiguous
names, species disambiguation/conflicts, derivative qualifiers, missing ontology
definitions, EFO identifier forms, reference description provenance and table
preservation.

Learning checkpoint: a reference lookup can be complete while some annotations
remain unresolved. Cancer category, cell identity and a screen-specific assignment
are separate claims. Review issues identify where further evidence is needed;
blank fields do not become negative cancer classifications.

## [VA5] Organization note — 2026-10-04

This active guide now uses the current paths. The before-full-annotation Markdown tables retain their original bytes and original historical links; consult logs/repository-relocations-20261004.json at the repository root to locate those sources. They are evidence snapshots, not active navigation pages.
