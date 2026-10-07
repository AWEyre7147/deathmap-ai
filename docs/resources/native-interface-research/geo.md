# GEO: native-interface research

Historical observations from 2026-10-06. Capabilities and literal searches require verification before a new adapter is implemented.

## Native interface and translation limits

The linked [native GEO page](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE225574) returned a CAPTCHA page during the earlier attempted read. New checks independently established a working Entrez route, without solving or bypassing that CAPTCHA.

NCBI documents `gds` as the descriptive/accession database and distinguishes search UIDs from retrieved metadata ([programmatic-access documentation](https://www.ncbi.nlm.nih.gov/geo/info/geo_paccess.html)). The actual [eInfo response](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=gds) exposes these useful field codes:

| Native code | Meaning from field schema |
|---|---|
| `ALL` | All Fields |
| `TITL`, `DESC` | Title; Description |
| `ORGN`, `ACCN` | Organism; GEO Accession |
| `ETYP`, `GTYP`, `PTYP` | Entry Type; DataSet Type; Platform Technology Type |
| `NSAM`, `SRC` | Number of Samples; Sample Source |
| `PDAT`, `UDAT` | Publication Date; Update Date |
| `ATNM`, `ATTR` | Attribute Name; Attribute |

These are schema observations from [eInfo](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=gds), not tests of every code/value combination. `PDAT` must not be assumed to equal an associated article's publication date.

```text
Executed native search:
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
db = gds
term = CRISPR[All Fields] AND GSE[ETYP]
retmax = 2
retmode = json
```

This returned `esearchresult.count="12487"`, `idlist=["200349270","200349221"]`, and `querytranslation`, with no query-error field ([native search response](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=CRISPR%5BAll+Fields%5D+AND+GSE%5BETYP%5D&retmax=2&retmode=json)). The follow-up GET `esummary.fcgi`, `db=gds,id=200349270,200349221,retmode=json`, returned GSE349270 and GSE349221 with `result.<UID>.accession`, `.title`, `.summary`, `.taxon`, `.gdstype`, `.pdat`, `.n_samples`, `.samples`, `.pubmedids`, and `.bioproject` ([summary response](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id=200349270%2C200349221&retmode=json)).

For GSE349221, the summary reports RNA-sequencing of JMJD5 knockout and wild-type HepG2 cells, eight samples, BioProject PRJNA1537591, and `pubmedids=[]` ([same summary](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id=200349270%2C200349221&retmode=json)). This is a useful output example, not a confirmed pooled CRISPR screen or recovered publication.

GEO remains the priority source. The broad CRISPR examples demonstrate literal query execution, not scientific specificity, recall, or an owner-approved transcriptomics-only restriction.

Evidence: native receipts in `examples/`; generic OmicsDI comparisons are archived.

New evidence: `examples/new-search-geo-crispr*`, `examples/native-geo-einfo*`, `examples/native-geo-esearch-example*`, `examples/native-geo-esummary-example*`, and `examples/native-programmatic-documentation.json`. No data files were downloaded.
