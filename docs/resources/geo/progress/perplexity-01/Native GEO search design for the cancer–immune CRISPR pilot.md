# Native GEO search design for the cancer–immune CRISPR pilot

The recommendation is to follow the ORCS–ICRAFT pilot's method, not copy ORCS field names into GEO: use supported broad restrictions, retain extra candidates, avoid selected cell-line allowlists, and compare publication representation afterward. GEO retrieval should generate candidate series and publication leads, not claim that every match is an eligible screen.

## Recommended initial search

Use this literal, verified expression for a human/mouse-scoped pilot:

```text
gse[ETYP] AND CRISPR[ALL]
AND ("Homo sapiens"[ORGN] OR "Mus musculus"[ORGN])
```

The interface is native NCBI Entrez: GET `/entrez/eutils/esearch.fcgi`, with `db=gds`, the expression supplied as `term`, and identifiers subsequently resolved through ESummary ([programmatic-access documentation](https://www.ncbi.nlm.nih.gov/geo/info/geo_paccess.html), [executed example](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BALL%5D&retmax=0&retmode=json)). This is not an OmicsDI `query` expression, and the successful research requests do not establish that the current DeathMap-AI runner already implements a native GEO route.

The exact expression returned 11,355 GEO Series candidates with no query-error field and the intended query translation ([verified request](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BALL%5D+AND+%28%22Homo+sapiens%22%5BORGN%5D+OR+%22Mus+musculus%22%5BORGN%5D%29&retmax=0&retmode=json)). This was a count-only interface probe, not retrieval of 11,355 records or scientific review of that set.

Species is a scope choice, not evidence of a cancer–immune interaction. If unannotated/other-species studies should remain eligible, omit the species clause and retain the broader verified baseline.

The CRISPR term is deliberately broad. Its successful execution does not prove comprehensive matching of CRISPRa-only, CRISPRi-only, Perturb-seq-only or other terminology; any synonym expansion should be separately specified and checked, not assumed to be covered.

## Which native controls are actually verified?

NCBI documents Entry Type, Organism, DataSet Type, Filter, Title, Description, Sample Source and date fields, with explicit aliases and query syntax ([GEO query documentation](https://www.ncbi.nlm.nih.gov/geo/info/qqtutorial.html)). The following table separates executed expressions from fields that were only documented or exposed by the schema.

| Native field and value | Evidence and usefulness | What the restriction could exclude | Pilot recommendation |
|---|---|---|---|
| `gse[ETYP]` | Executed; returns Series rather than mixing record types. Documented values are `gse`, `gds`, `gpl` ([documentation](https://www.ncbi.nlm.nih.gov/geo/info/qqtutorial.html), [executed baseline](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BALL%5D&retmax=0&retmode=json)). | Standalone curated GDS or platform records. It also makes Series the retrieval unit, not a complete inventory of every GEO entity. | Use for Series-level discovery; retain returned sample/platform links for later work. |
| `"Homo sapiens"[ORGN] OR "Mus musculus"[ORGN]` | Executed as one OR group; Organism uses taxonomy terms rather than a curated experimental-role label ([documentation](https://www.ncbi.nlm.nih.gov/geo/info/qqtutorial.html), [species probe](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BALL%5D+AND+%28%22Homo+sapiens%22%5BORGN%5D+OR+%22Mus+musculus%22%5BORGN%5D%29&retmax=0&retmode=json)). | Other-species models and records lacking either indexed organism. Human-only would also exclude mouse immune and in-vivo models. Matching a species does not identify which compartment was edited. | Carry forward the earlier human/mouse scope provisionally; keep an unrestricted baseline count. |
| `CRISPR[ALL]` | Executed. All Fields searches indexed text, not a curated “CRISPR screen” category ([schema](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=gds), [baseline](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BALL%5D&retmax=0&retmode=json)). | Records without that indexed term, including potentially alternative modality names or related deposits whose descriptions omit the screen. Conversely, it admits editing-method and non-screen studies. | Use as the verified seed, with an explicit incomplete-terminology limitation. |
| `CRISPR[TITL]` | Executed; narrows retrieval substantially. Title searches are free text, not a scientific classification ([documentation](https://www.ncbi.nlm.nih.gov/geo/info/qqtutorial.html), [title probe](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BTITL%5D&retmax=0&retmode=json)). | Relevant series where CRISPR is described elsewhere, or companion assays with titles emphasizing the target or readout. | Do not replace All Fields with Title as a mandatory gate. |
| `"expression profiling by high throughput sequencing"[GTYP]` | Documented and executed; this is a native DataSet/Series Type value, not OmicsDI's Transcriptomics label ([documentation](https://www.ncbi.nlm.nih.gov/geo/info/qqtutorial.html), [assay probe](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BALL%5D+AND+%22expression+profiling+by+high+throughput+sequencing%22%5BGTYP%5D&retmax=0&retmode=json)). | Screen deposits classified only as Other or another assay type; guide-count sequencing is not necessarily expression profiling. A concrete excluded candidate is GSE199813, discussed below. | Use only for an optional expression-readout subset, not the main CRISPR pilot. |
| `"gds pubmed"[FILT]` | Documented and executed; restricts to records with indexed PubMed links ([documentation](https://www.ncbi.nlm.nih.gov/geo/info/qqtutorial.html), [link probe](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BALL%5D+AND+%22gds+pubmed%22%5BFILT%5D&retmax=0&retmode=json)). | New deposits, preprint-associated studies, and published studies whose citation is missing from GEO. Missing citation is not evidence of no publication. | Retrieve `pubmedids` where present; retain unresolved records rather than requiring this filter. |
| `[PDAT]` and `[UDAT]` | Verified as native fields and documented for ranges, but no date restriction was executed here. PDAT is record release date; UDAT is record update date ([schema](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=gds), [date semantics](https://www.ncbi.nlm.nih.gov/geo/info/qqtutorial.html)). | A release-date cutoff could lose an older deposit linked to a newer publication; an update-date cutoff can include old studies updated recently. | No date gate in the initial pilot. Later separate repository timing from publication timing. |
| `[SRC]`, `[DESC]`, `[TITL]`, `[ALL]` | Documented searchable text fields; Sample Source is explicitly submitter-supplied and not curated ([documentation](https://www.ncbi.nlm.nih.gov/geo/info/qqtutorial.html)). No cancer/immune class expression was executed in this check. | Requiring literal “cancer cell line,” “immune,” or “co-culture” can miss primary immune cells, named models, alternate spellings, in-vivo studies, and sparse descriptions. | Use a general biological vocabulary for candidate flags or a separately assessed narrower branch, not a selected model-name allowlist. |
| `[ATNM]`, `[ATTR]` | Attribute Name and Attribute appear in the current schema; specific cell-type values and their query behavior were not tested ([schema](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=gds)). | Treating heterogeneous sample labels as standardized cancer/immune categories can reject poorly annotated but relevant studies. | Preserve for metadata review; do not call them verified cancer/immune filters. |
| `[NSAM]`, `[SFIL]` | Number of Samples and Supplementary Files are documented fields, but no proposed threshold/file value was tested ([documentation](https://www.ncbi.nlm.nih.gov/geo/info/qqtutorial.html)). | Sample thresholds can lose small focused screens; file-type restrictions can lose deposits with different packaging or raw data stored elsewhere. | Descriptive metadata, not main inclusion gates. Sample count is not library size or an analogue of genome-wide coverage. |

## What the restriction probes actually returned

Each row below changes only the specified restriction relative to `gse[ETYP] AND CRISPR[ALL]`. Restrictions were tested independently, not cumulatively.

| Expression | Series count | Baseline candidates outside that restricted result |
|---|---:|---:|
| Broad baseline | 12,487 ([request](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BALL%5D&retmax=0&retmode=json)) | Not applicable |
| Add human OR mouse | 11,355 ([request](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BALL%5D+AND+%28%22Homo+sapiens%22%5BORGN%5D+OR+%22Mus+musculus%22%5BORGN%5D%29&retmax=0&retmode=json)) | 1,132 |
| Add expression-sequencing type | 6,796 ([request](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BALL%5D+AND+%22expression+profiling+by+high+throughput+sequencing%22%5BGTYP%5D&retmax=0&retmode=json)) | 5,691 |
| Add PubMed-link filter | 10,281 ([request](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BALL%5D+AND+%22gds+pubmed%22%5BFILT%5D&retmax=0&retmode=json)) | 2,206 |
| Replace All Fields with Title | 3,110 ([request](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse%5BETYP%5D+AND+CRISPR%5BTITL%5D&retmax=0&retmode=json)) | 9,377 |

The final column is arithmetic on API counts, not a count of eligible studies lost. These probes do not estimate precision, recall, unique publications, independent screens, or downloadable datasets.

Requests were made at approximately 20:04 EDT on 2026-10-06, corresponding to 2026-10-07 UTC in the preserved request metadata. The five count probes and two illustrative-record requests are preserved in the accompanying evidence archive.

## Requirements that need text or metadata review

The verified GEO schema does not provide a curated equivalent of the ORCS/Cellosaurus “Cancer cell line” category or structured fields for perturbed compartment, immune pressure, pooled-screen modality, and experimental eligibility ([current schema](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=gds)). Those requirements should not be silently converted into invented filters.

- **Cancer derivation versus experimental role:** cancer-derived origin, primary tumour status, and whether a cell acts as target or immune effector are separate questions. Use native descriptions and sample metadata, with reference annotation where already available; a named line or an organism alone is insufficient.
- **Immune lineage:** use broad class-level vocabulary such as T-cell, NK-cell, macrophage, dendritic-cell and related lineage descriptions. Treat missing text as unresolved rather than proof of a non-immune model.
- **Interaction setting:** distinguish direct co-culture, immune-conditioned exposure, in-vivo host immunity, and immune-intrinsic assays. Do not make a literal co-culture mention a universal gate.
- **Actual CRISPR screen:** establish library/perturbation design and screening readout, rather than counting a single-gene knockout, CRISPR method mention, or companion RNA-seq dataset as a screen.
- **Perturbation modality and readout:** preserve knockout, interference, activation and other modalities independently of fitness, cytokine, marker-sorting or molecular-profile readouts. Do not equate sequencing with transcriptomics.
- **Publication-to-dataset association:** retain native UIDs, GSE accessions, PMID links and BioProject accessions. An associated publication can contain several experiments, and one GSE is not necessarily one screen.

These are review questions, not instructions to add a validation engine or classification workstream to the discovery pipeline. Initial outputs can carry source text, metadata and unresolved status for later owner/Perplexity interpretation.

## Concrete exclusion risks from relevant studies

### Expression-sequencing or cancer-cell-only gates

GSE199813 is titled “CRISPR screens unveil signal hubs for nutrient licensing of T cell immunity [CRISPR screen],” reports mouse T cells, links PMID 34795452, and has native `gdstype="Other"` ([actual GEO summary](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id=200228188%2C200199813%2C200190604%2C200174284&retmode=json)). It would be excluded by the tested expression-profiling type restriction.

The publication describes nutrient/immune signaling to mTORC1 and T-cell/Treg functional and antitumour-immunity findings, making it pertinent to broad immune-functional candidate discovery rather than a cancer-cell-only screen model ([publication](https://pubmed.ncbi.nlm.nih.gov/34795452/)). A requirement that the edited cells themselves be cancer cells could exclude this kind of immune-intrinsic study.

This PMID is in the supplied ICRAFT CRISPR reference list but was not present in the supplied ORCS snapshot. That is a practical reason to compare GEO with the full ICRAFT CRISPR reference set, not just the 33 publications found in ORCS.

### Knockout-only, tumour-cell-only or co-culture-only gates

PMID 35113687 reports genome-wide CRISPRa and CRISPRi screens in primary human T cells, cytokine-production readouts, arrayed confirmation and single-cell characterization ([publication](https://pubmed.ncbi.nlm.nih.gov/35113687/)). Knockout-only and tumour-cell-only eligibility would exclude its stated screen modalities/models; co-culture-only eligibility would reject records without additional interaction-setting evidence.

GSE174284 and GSE190604 link that same PMID but describe Bulk RNA-seq and CRISPRa Perturb-seq respectively ([GEO summaries](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id=200228188%2C200199813%2C200190604%2C200174284&retmode=json)). Their common PMID does not make them two independent publications or establish that every associated deposit contains primary genome-wide screen counts.

This publication is also in the supplied ICRAFT/ORCS comparison. It illustrates why the reference's biological breadth should inform interpretation without turning particular cell models into search keys.

### Native assay labels can be multi-valued

GSE228188, an NK co-culture CRISPR screen linked to PMID 38619967, has native `gdstype="Other; Expression profiling by high throughput sequencing"` ([GEO summary](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id=200228188%2C200199813%2C200190604%2C200174284&retmode=json)). Unlike GSE199813, it is not an example of a series that necessarily fails the expression-type restriction.

Its earlier OmicsDI detail reported an Other omics label, while the native GEO summary contains both assay labels ([OmicsDI detail](https://www.omicsdi.org/ws/dataset/geo/GSE228188), [native summary](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id=200228188%2C200199813%2C200190604%2C200174284&retmode=json)). Do not transfer a restriction's expected behavior between the two interfaces.

### Citation or title requirements can hide companion datasets

The previously checked GSE349221 summary describes RNA sequencing of JMJD5-knockout and wild-type HepG2 cells, mentions CRISPR in the summary rather than the displayed series title, and has `pubmedids=[]` ([GEO summary](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id=200349270%2C200349221&retmode=json)). A mandatory PubMed-link restriction excludes it; title-only searching risks missing deposits whose CRISPR context is supplied elsewhere.

This example is not being labelled a pooled screen or an ICRAFT reference. It illustrates candidate/companion metadata that the publication-and-dataset pipeline should not reject merely for an absent citation.

## How to reproduce the ORCS–ICRAFT pilot method

- **Freeze the biological scope:** keep the broad cancer-model, immune-lineage and relevant model-context objective. Do not require both a cancer term and an immune term in every deposited record; interpret the compartments and setting afterward.
- **Use one supported discovery expression:** start with the verified Series + CRISPR + human/mouse expression. Do not add assay-type, PubMed-link, fitness-readout or co-culture gates solely to make the candidate list cleaner.
- **Keep reference identifiers out of discovery:** ICRAFT PMIDs/accessions, authors and selected cell lines are comparison inputs, never query clauses. The accession lookups in this note were illustrative metadata checks, not a proposed production allowlist.
- **Keep the pipeline simple:** ask ChatGPT to establish whether its existing retrieval route can execute native Entrez requests before applying this expression. Do not paste Entrez field syntax into the OmicsDI parser or claim an unsupported route works. Preserve UID, GSE, title, description, organism, reported assay type, dates, sample count, PMID links and BioProject identity where returned; no new runner, benchmark module or eligibility validator is proposed here.
- **Compare afterward:** use the full supplied ICRAFT CRISPR publication reference, and separately identify which reference publications have demonstrable GEO records. Report represented, not represented and unresolved associations separately from newly discovered candidates.
- **Describe rather than certify performance:** counts demonstrate a tangible pilot result. Extra candidates are welcome; matches are not formal recall estimates, validated scientific eligibility, or complete dataset recovery.
- **Handle later publications separately:** establish ICRAFT's actual literature-search stop date before making a post-cutoff claim, and use publication evidence for publication dates rather than substituting GEO record-release dates.

This adapts the pilot philosophy to GEO's actual metadata. It does not claim that native GEO offers the same curated biological class filters as ORCS, or that the tested CRISPR seed exhausts relevant records.
