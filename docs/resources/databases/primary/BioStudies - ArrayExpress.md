> Research status: owner-curated interface reference for v02 ORCS enrichment. Examples and described capabilities require confirmation for the specific programmatic retrieval contract; this note does not authorize live retrieval or define pipeline filters.


# BioStudies - ArrayExpress: Functional Genomics Data

## Notes
- Raw sequence reads from high-throughput sequencing studies are brokered to the ENA

## Native 'Browse' Categories
### Released (top 10)
- 2026 (n = 1102)
- 2025 (n = 1228)
- 2024 (n = 958)
- 2023 (n = 1256)
- 2022 (n = 1334)
- 2021 (n = 1300)
- 2020 (n = 1174)
- 2019 (n = 1034)
- 2018 (n = 990)
- 2017 (n = 1022)
### Link Type (all)
- Array Design (n = 56748)
- DOI (n = 23392)
- ENA (n = 20777)
- Expression Atlas (Single Cell) (n = 129)
- Biostudies (n = 2807)
- EGA (n = 40)
- Expression Atlas (n = 4006)
- GEO (n = 48110)
### File Type (top 10)
- CEL (n = 23982)
- bed (n = 2228)
- cel (n = 943)
- CSV(n = 898)
- gpr (n = 4324)
- idat (n = 737)
- pair (n = 1934)
- r (n = 6869)
- txt (n = 80954)
- wig (n = 1555)
### Study Type (top 10)
- ChIP-chip by tiling array (n = 1541)
- ChIP-seq (n = 5821)
- RNA-seq of coding RNA (n = 12552)
- RNA-seq of coding RNA from single cells (n = 1265)
- RNA-seq of non coding RNA (1913)
- comparative genomic hybridization by array (n = 2309)
- methylation profiling by array (n = 1673)
- other (n = 1417)
- transcription profiling by array (n = 48641)
- unknown experiment type (n = 1533)
### Experimental Design (top 10)
- N/A (n = 51397)
- cell type comparison design (n = 1524)
- co-expression_design (n = 5337)
- compound treatment design (n = 1800)
- compound_treatment_design (n = 1566)
- genetic modification design (n = 1782)
- genotype design (n = 1643)
- stimulus or stress design (n = 1427)
- transcription profiling by array (n = 12782)
- unknown_experiment_design_type (n = 3962)
### Organism (top 10)
- Arabidopsis thaliana (n = 3543)
- Caenorhabiditis elegans (n = 1223)
- Danio rerio (n = 833)
- Drosophila melanogaster (n = 2489)
- Eschicherichia coli (n = 493)
- Homo sapiens (n = 30893)
- Mus musculus (n = 21784)
- Rattus norvegicus (n = 2567)
- Saccharomyces cerevisiae (n = 2074)
- Sus scrofa (n = 553)
### Technology (all)
- Array assay (n = 57749)
- N/A (n = 247)
- Sequencing assay (n = 23795)
### Assay by Molecule (all)
- DNA assay (n = 14237)
- N/A (n = 3376)
- RNA assay (n = 65394)
- assay by molecule (n = 1)
- protein assay (n = 197)

### Raw Data Available (n = 65231)
### Processed Data Available (n = 61290)

## FAQs
### How do I access BioStudies?

All publicly available data can be accessed through the [BioStudies studies page](https://www.ebi.ac.uk/biostudies/studies).

Data that is not yet public—for example, data with “hold until published” status—can be accessed using the correct login credentials or a link in this format:

text

`https://www.ebi.ac.uk/biostudies/studies/<accession_number>?key=<access_key>`

### Can I search by publication, accession, or keyword?

Yes. You can search by any metadata field.

Enclose multi-word phrases in double quotes. See [Search](#search) for search capabilities and syntax.

### How do I link to a dataset?

Use the study accession in this URL format:

text

`https://www.ebi.ac.uk/biostudies/studies/<accession_number>`

Example: [S-BSST1](https://www.ebi.ac.uk/biostudies/studies/S-BSST1).

### How can I retrieve all studies from a large search or collection?

Use the BioStudies API with cursor pagination rather than requesting increasingly deep result pages.

See [Retrieving large result sets with cursor pagination](#retrieving-large-result-sets-with-cursor-pagination).

### What is the easiest way to download large data volumes?

Aspera transfers are supported and are particularly useful for large data volumes.

See [Download](#download) for available download methods.

### Under what licenses are datasets available?

Some datasets include license information in the metadata `License` field.

Where no license is stated, data are available under the [EMBL-EBI Terms of Use](https://www.ebi.ac.uk/about/terms-of-use/), which the FAQ describes as placing no restrictions on use or redistribution.

See [Licensing](#licensing) for the policy statement concerning new datasets and older studies.

## Search

### Basic search

Use the search box in the top-right corner of any page. Enter words describing the studies you are interested in.

As you type, a drop-down list suggests matching terms.

For terms in the [Experimental Factor Ontology (EFO)](http://www.ebi.ac.uk/efo), a button enables expansion to more specific terms. EFO is an EMBL-EBI resource that provides systematic descriptions of biological samples and experimental variables.

Search terms remain in the search box and can be refined using [advanced search](#advanced-search).

### Search results

Results appear as a list of matching studies, sorted by relevance by default.

You can:

- Change the sorting using the “Sort by” selector.
    
- Change the number of studies displayed per page.
    
- Navigate between result pages.
    
- Click a study title to open its detailed page.
    

Matching terms are highlighted:

|Highlight color|Meaning|
|---|---|
|Yellow|Exact match|
|Green|Synonym|
|Peach|More specific term from EFO|

For example, “pancreatic ductal adenocarcinoma” may be highlighted as a more specific term for “adenocarcinoma.”

Terms with more than 1,000 child terms are not expanded.

### Advanced search

#### Terms and phrases

Each word is treated as a separate search term unless enclosed in double quotes.

By default, results can contain any of the queried terms.

Use double quotes for a multi-word phrase:

text

`"pancreatic ductal adenocarcinoma"`

#### Boolean operators

Use Boolean operators and parentheses to control how terms are combined:

text

`Leukemia AND (mouse OR human)`

text

`cancer AND NOT (human)`

#### Wildcards

|Wildcard|Meaning|Example|
|---|---|---|
|`*`|Matches zero or more characters|`leuk*mia` matches `leukemia`, `leukaemia`, and `leukqwertymia`|
|`?`|Matches a single character|`m?n` matches `man` and `men`|

Queries containing wildcards are not expanded.

#### Regular expressions

BioStudies supports regular-expression searches.

For example:

text

`/[dl]ouse/`

This matches both `louse` and `douse`.

#### Reserved characters

The following characters are part of the query syntax:

text

`+ - && || ! ( ) { } [ ] ^ " ~ * ? : \ /`

Escape or quote them when they are intended as literal parts of a query.

For example, search for `eeg/fmri` using either:

text

`eeg\/fmri`

or:

text

`"eeg/fmri"`

Similarly, enclose a DOI in double quotes:

text

`"10.1371/journal.pone.0127346"`

#### Field-specific queries

Queries can use [Lucene query syntax](https://lucene.apache.org/core/2_9_4/queryparsersyntax.html):

text

`attribute_name:attribute_value`

Example:

text

`author:smith AND title:bacteria`

This returns fewer hits than:

text

`smith AND bacteria`

See [Search parameters](#search-parameters) for the available attributes.

### Download

BioStudies supports website downloads, FTP, Aspera, and Globus.

For fewer than 1,000 files, select the files on the study detail page and click “Download” to obtain HTTP, FTP, or Aspera instructions.

For larger studies, you will need the file paths.

##### Study directory structure

Study paths follow this structure:

text

`/<collection>/<parent>/<accession>`

|Component|Description|
|---|---|
|`<collection>`|Accession prefix, such as `S-EPMC`, `S-BSST`, or `E-MTAB`|
|`<parent>`|Usually the last three digits of the accession, with exceptions for some older studies|
|`<accession>`|Full study accession, such as `S-EPMC3521001`|

Collection examples:

- `S-EPMC`: Data imported from Europe PMC.
    
- `S-BSST`: Data submitted through the BioStudies Submission Tool.
    
- `E-MTAB`: Data belonging to the ArrayExpress collection.
    

For `S-BIAD300`, the parent directory is `300`.

##### Exceptions for older studies

Some older studies use a masked accession as the parent directory. For example, older Europe PMC accessions ending in `001` may use:

text

`S-EPMCxxx001`

Some older studies with one- or two-digit numeric accession components use:

text

`S-BSST0-99`

For example, `S-BSST7` has this relative path:

text

`S-BSST/S-BSST0-99/S-BSST7`

##### Retrieve a study path through the API

Use the study’s `/info` endpoint and extract `relPath`:

bash

`curl -s 'https://www.ebi.ac.uk/biostudies/api/v1/studies/S-BSST7/info' \   | jq -r '.relPath'`

Example output:

text

`S-BSST/S-BSST0-99/S-BSST7`

Another example:

bash

`curl -s 'https://www.ebi.ac.uk/biostudies/api/v1/studies/S-EPMC3521001/info' \   | jq -r '.relPath'`

Example output:

text

`S-EPMC/001/S-EPMC3521001`

#### FTP downloads

The BioStudies FTP root is:

text

`ftp://ftp.ebi.ac.uk/biostudies`

Anonymous downloads are enabled.

Click the FTP button for a study, or use an FTP client such as FileZilla.

Study FTP URLs follow this structure:

text

`ftp://ftp.ebi.ac.uk/biostudies/<mode>/<path>`

|Component|Description|
|---|---|
|`<mode>`|Storage mode: `fire` or `nfs`|
|`<path>`|Study path described in [Study directory structure](#study-directory-structure)|

Study data files are located in the `Files` directory:

text

`ftp://ftp.ebi.ac.uk/biostudies/<mode>/<path>/Files`

##### Download a file with `wget`

bash

`wget 'ftp://ftp.ebi.ac.uk/biostudies/nfs/S-BSST/S-BSST0-99/S-BSST7/Files/1_TCGA_signature_A_top_10percent.txt'`

##### Interactive FTP example

text

`$ ftp ftp.ebi.ac.uk Name: anonymous ftp> cd biostudies/nfs/S-BSST/S-BSST0-99/S-BSST7/Files ftp> get 1_TCGA_signature_A_top_10percent.txt`

##### Retrieve a study’s FTP link through the API

bash

`curl -s 'https://www.ebi.ac.uk/biostudies/api/v1/studies/S-BSST7/info' \   | jq -r '.ftpLink'`

#### Aspera downloads

Install the [Aspera `ascp` command-line interface](https://www.ibm.com/support/fixcentral/swg/selectFixes?parent=ibm~Other%20software&product=ibm/Other%20software/IBM%20Aspera%20CLI&release=All&platform=All&function=all), selecting the correct operating system.

The `ascp` executable is in the installation directory’s `bin` folder.

##### General command

bash

`ascp -P33001 -i <key> \   bsaspera@fasp-beta.ebi.ac.uk:<files-to-download> \  <local-download-location>`

|Argument|Description|
|---|---|
|`-P33001`|Aspera connection port|
|`-i <key>`|Path to the Aspera connection key|
|`bsaspera@fasp-beta.ebi.ac.uk`|User and server shown in the supplied command|
|`<files-to-download>`|Remote file or study files to download|
|`<local-download-location>`|Destination on your machine|

Key paths:

text

`Linux/macOS: <aspera-cli-installation-directory>/etc/asperaweb_id_dsa.openssh Windows: <aspera-cli-installation-directory>\etc\asperaweb_id_dsa.openssh`

> Source discrepancy: The supplied command uses `fasp-beta.ebi.ac.uk`, while its explanatory text names `fasp.ebi.ac.uk`. Both hostnames are preserved here rather than silently reconciled.

##### Windows example

The supplied text describes downloading `aeipf_denoised_reads.fna` from `S-BSST12` to `C:\Temp`, but the executable, key, and destination paths in the pasted command are corrupted.

The recoverable remote file path is:

text

`/S-BSST/012/S-BSST12/Files/aeipf_denoised_reads.fna`

> Aspera downloads are available only for studies whose storage mode is `fire`.

#### Globus downloads

BioStudies also supports downloads through [Globus](https://www.globus.org/).

Click the Globus icon on the website to open the [EMBL-EBI Public Data collection](https://app.globus.org/file-manager?origin_id=47772002-3e5b-4fd3-b97c-18cee38d6df2&origin_path=%2Fbiostudies%2F) in the Globus File Manager.

You can install [Globus Connect Personal](https://www.globus.org/globus-connect-personal) to create a personal collection on your machine.

See the [Globus getting-started guide](https://docs.globus.org/how-to/get-started/) for transferring multiple files.

### API

#### Base URL

text

`https://www.ebi.ac.uk/biostudies`

#### Search studies

text

`GET /api/v1/search`

Returns studies matching the supplied search criteria.

Only minimal metadata is returned for each study. Retrieve the study detail file separately for a complete representation.

#### Search parameters

|Parameter|Description|
|---|---|
|`query`|Searches the supplied text across submissions using the search behavior described above|
|`accession`|Searches for a BioStudies accession; wildcards are allowed after the first character, for example `S-EPMC*`|
|`title`|Searches study titles|
|`author`|Searches author or submitter names|
|`release_date`|Searches the date a study became public; format: `yyyy-mm-dd`|
|`content`|Free-text search across study content, including filenames and links|
|`links`|Number of links in the study|
|`files`|Number of files in the study|
|`orcid`|Searches author [ORCID](https://orcid.org/) identifiers, where available|
|`type`|Supported types: `study`, `array`, and `collection`|
|`link_type`|Searches for a specific external-database link type; see [Supported link types](#supported-link-types)|
|`link_value`|Searches the value associated with a link type, usually an accession in the corresponding database|
|`page`|Result page to return; default: `1`. Intended for normal browsing|
|`pageSize`|Results per request; default: `20`. Maximum depends on the pagination mode|
|`pagination`|Set to `cursor` to start cursor-based pagination|
|`cursor`|Continues a cursor search using the previous response’s opaque `nextCursor` value|
|`sortBy`|Sorting key; works only for numeric fields|
|`sortOrder`|Ascending or descending; default: descending|

#### Link-type search example

Combine `link_type` and `link_value` to find a study associated with PMID `15307895`:

text

`/api/v1/search?link_type=pmid&link_value=15307895`

#### Supported link types

The URL templates below preserve the mappings in the supplied documentation.

|Link type|Website or URL template|
|---|---|
|`pmc`|`https://europepmc.org/articles/<link_value>`|
|`pmid`|`https://europepmc.org/abstract/MED/<link_value>`|
|`doi`|`https://dx.doi.org/<link_value>`|
|`chembl`|`https://www.ebi.ac.uk/chembldb/compound/inspect/<link_value>`|
|`ega`|`https://www.ebi.ac.uk/ega/studies/<link_value>`|
|`uniprot`|`http://www.uniprot.org/uniprot/<link_value>`|
|`ena`|`https://www.ebi.ac.uk/ena/browser/view/<link_value>`|
|`arrayexpress files`|`https://www.ebi.ac.uk/arrayexpress/experiments/<link_value>/files/`|
|`arrayexpress`|`https://www.ebi.ac.uk/arrayexpress/experiments/<link_value>`|
|`dbsnp`|`http://www.ncbi.nlm.nih.gov/SNP/snp_ref.cgi?rs=<link_value>`|
|`pdbe`|`https://www.ebi.ac.uk/pdbe-srv/view/entry/<link_value>/summary`|
|`pfam`|`http://pfam.xfam.org/family/<link_value>`|
|`omim`|`http://omim.org/entry/<link_value>`|
|`interpro`|`https://www.ebi.ac.uk/interpro/entry/<link_value>`|
|`nucleotide`|`http://www.ncbi.nlm.nih.gov/nuccore/<link_value>`|
|`geo`|`http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=<link_value>`|
|`intact`|`https://www.ebi.ac.uk/intact/interaction/<link_value>`|
|`biostudies`|`/studies/<link_value>`|
|`biostudies title`|`/studies?first&query=title%3A%22<link_value>%22`|
|`biostudies search`|`/studies?query=<link_value>`|
|`go`|`http://amigo.geneontology.org/amigo/term/<link_value>`|
|`chebi`|`https://www.ebi.ac.uk/chebi/searchId.do?chebiId=<link_value>`|
|`bioproject`|`https://www.ncbi.nlm.nih.gov/bioproject/<link_value>`|
|`biosamples`|`https://www.ebi.ac.uk/biosamples/samples/<link_value>`|
|`chemagora`|`http://chemagora.jrc.ec.europa.eu/chemagora/inchikey/<link_value>`|
|`compound`|`https://www.ebi.ac.uk/biostudies/studies/<link_value>`|
|`rfam`|`http://rfam.org/family/<link_value>`|
|`rnacentral`|`http://rnacentral.org/rna/<link_value>`|
|`nct`|`https://clinicaltrials.gov/ct2/show/<link_value>`|
|`gxa`|`https://www.ebi.ac.uk/gxa/experiments/<link_value>?ref=biostudies`|
|`gxa-sc`|`https://www.ebi.ac.uk/gxa/sc/experiments/<link_value>?ref=biostudies`|

#### Retrieving large result sets with cursor pagination

Page-based pagination is intended for normal browsing.

For large result sets, or all studies matching a search, use cursor pagination. It enables sequential traversal without the increasing cost of requesting very deep result pages.

##### 1. Start a cursor search

Add `pagination=cursor`:

bash

`curl 'https://www.ebi.ac.uk/biostudies/api/v1/search?pagination=cursor&pageSize=1000'`

The response uses the normal `hits` structure and includes `nextCursor`.

Illustrative response:

json

`{   "hits": [],  "nextCursor": "djE6Uy1FUE1DMTAwMDMzNjg" }`

> The empty `hits` array above is a formatting placeholder; actual responses contain the matching study records.

##### 2. Retrieve the next batch

Pass the returned `nextCursor` value as the `cursor` parameter:

bash

`curl --get 'https://www.ebi.ac.uk/biostudies/api/v1/search' \   --data-urlencode 'cursor=djE6Uy1FUE1DMTAwMDMzNjg' \  --data-urlencode 'pageSize=1000'`

##### 3. Continue until completion

Use each newly returned `nextCursor` until its value is `null`.

A `null` cursor indicates that traversal is complete.

##### Cursor behavior and limitations

- Cursor values are opaque. Pass them back exactly as returned.
    
- Do not decode, modify, or construct cursor values.
    
- Pagination operates on the live BioStudies index, not a fixed snapshot.
    
- Studies added during a long-running traversal may or may not be included.
    
- `totalHits` may be approximate during cursor pagination.
    
- Check `isTotalHitsExact` before treating `totalHits` as an exact count.
    
- Use `nextCursor`, not `totalHits`, to determine whether more results are available.
    

##### Combine cursor pagination with search criteria

bash

`curl --get 'https://www.ebi.ac.uk/biostudies/api/v1/search' \   --data-urlencode 'query=cancer' \  --data-urlencode 'pagination=cursor' \  --data-urlencode 'pageSize=1000'`

#### Search within a collection

text

`GET /api/v1/{collection}/search`

This endpoint behaves like `/api/v1/search` but limits results to the specified collection.

Retrieve the [list of available collections](https://www.ebi.ac.uk/biostudies/api/v1/search?type=collection) using:

text

`GET /api/v1/search?type=collection`

All applicable search parameters, including cursor pagination, can also be used with collection searches.

#### Europe PMC collection example

bash

`curl 'https://www.ebi.ac.uk/biostudies/api/v1/EuropePMC/search?pagination=cursor&pageSize=1000'`

Continue passing the returned `nextCursor` as described above until it is `null`.

##### Retrieve study details

text

`GET /api/v1/studies/{accession}`

Returns detailed study information in PageTab JSON format, if accessible.

##### Retrieve additional study information

text

`GET /api/v1/studies/{accession}/info`

Returns additional information, including the study’s FTP link and relative path.

Example:

bash

`curl -s 'https://www.ebi.ac.uk/biostudies/api/v1/studies/S-BSST7/info'`

### Policies

#### Data access

Datasets are either private or public.

#### Private datasets

- Accessible to the data owner when logged into BioStudies.
    
- Also accessible through a secret key obtained by the owner while logged in.
    
- Secret-key links can be shared, for example, with reviewers of an associated manuscript.
    
- Other access mechanisms, such as a read-only user for a group of datasets, exist for specific collaborations.
    

#### Public datasets

- Accessible to everyone.
    
- No login is required.
    

#### Dataset submission, updates, and persistence

##### Permanent accessibility

Public datasets remain permanently accessible as part of the scientific record, subject to the exceptional circumstances described below.

See the [EMBL-EBI data preservation policy](https://www.ebi.ac.uk/long-term-data-preservation).

Corrections and updates from authors are welcome. Erroneous submissions may be removed from keyword search results while remaining accessible by accession number.

##### Submitter responsibilities

Information displayed as part of publicly released datasets is fully disclosed to the public.

Submitters are responsible for:

- Ensuring they have the right to submit the data.
    
- The quality and accuracy of their submissions.
    

BioStudies provides limited editorial control and internal integrity checks and works with submitters and users to improve resource quality.

##### Release dates

A release date is set when a submission is made.

- The date may be up to two years after submission.
    
- It can be changed after the submission is completed.
    
- Changes may be used to coordinate data release with an associated publication.
    

#### Updates to public datasets

|Change|Policy|
|---|---|
|Add new data files|Allowed|
|Modify published data files|Not allowed|
|Delete published data files|Not allowed|
|Update metadata fields|Allowed|
|Change a public dataset back to private|By exception only|
|Delete a public dataset|Generally not possible; exceptional cases are described below|

For exceptional requests to return a public dataset to private status, contact [biostudies@ebi.ac.uk](mailto:biostudies@ebi.ac.uk).

#### Exceptional removal or obsolescence

Exceptions may arise when the integrity, correctness, ownership, or provenance of data is questioned.

In unusual circumstances, BioStudies may:

- Make an entry wholly or partly obsolete, moving it out of the active archive while keeping it publicly accessible.
    
- Remove an entry entirely from the public record.
    

For example, this may occur when a publication is retracted by its authors, their institution, or the journal, and the retracting parties also request removal of the corresponding BioStudies data from the scientific record.

#### Updates to private datasets

Any updates, including dataset deletion, are enabled while a dataset remains private.

#### Licensing

New BioStudies datasets are released into the public domain under a [Creative Commons Zero (CC0) waiver](https://creativecommons.org/publicdomain/zero/1.0/legalcode).

Some older studies have individual licenses, explicitly stated on their accession pages.

Where no license is stated, data are available under the [EMBL-EBI Terms of Use](https://www.ebi.ac.uk/about/terms-of-use/).

##### Use of data upload areas

BioStudies is a permanent repository for life sciences data, but users’ private upload areas are temporary staging locations.

#### Upload workflow

1. Files are uploaded to a user-specific private upload area while a submission is being prepared.
    
2. When included in a submission, the associated files are moved into BioStudies.
    
3. After loading into BioStudies, data can be released immediately or kept confidential until an event such as publication of the associated manuscript.
    

If you intend to reuse a significant set of files in multiple submissions, contact BioStudies before the first submission.

#### Storage limits

Upload areas are neither intended nor suitable for long-term data storage.

- A file is expected to remain in an upload area for no longer than three months before becoming part of a submission.
    
- BioStudies reserves the right to routinely delete files that remain there for more than three months.
    
- This also applies to unfinished submissions in the `Draft` state.