
# BioStudies - ArrayExpress: Functional Genomics Data

## Notes
- Data from high-throughput functional genomics experiments
- A study contains metadata such as detailed sample annotations, protocols, processed data, and raw data
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



## Links
### FAQs
- How do I access BioStudies?
	All publicly available data in BioStudies is available via [https://www.ebi.ac.uk/biostudies/studies](https://www.ebi.ac.uk/biostudies/studies). Data that is not yet public (e.g., with ‘hold until published’ status) can be accessed if you have the correct login credentials, or via a link of the form `https://www.ebi.ac.uk/biostudies/studies/<accession_number>?key=<access_key>`
- Can I search by publication / accession / keyword?
	Yes, search by any metadata field is possible. Include multi-word phrases in double quotes; see [the search tab](https://www.ebi.ac.uk/biostudies/help#how-to-search) for more information on search capabilities.
- How do I link to a dataset?
	Use `https://www.ebi.ac.uk/biostudies/studies/<accession_number>` to link to a particular dataset in BioStudies, e.g. [https://www.ebi.ac.uk/biostudies/studies/S-BSST1](https://www.ebi.ac.uk/biostudies/studies/S-BSST1).
- How can I retrieve all studies from a large search or collection?
	If you need to retrieve a large number of search results, or all studies matching a search or belonging to a collection, use the BioStudies API with cursor pagination rather than requesting increasingly deep result pages. See the **API** section below for cursor pagination and examples.
- What is the easiest way to download large data volumes from BioStudies?
	For general help with downloading see [here](https://www.ebi.ac.uk/biostudies/help#download). Aspera transfers are supported, and are particularly useful for large data volumes.
- Under what license(s) are datasets in BioStudies available?
	Some datasets will have license info included in the metadata “License” field. Where no license is stated, data are available under the [EBI Terms of Use](https://www.ebi.ac.uk/about/terms-of-use/) which place no restrictions on use or redistribution.

### Search
Use the Search box available in the top-right corner of every page. Enter any words that describe studies you are interested in. As you start typing, a drop-down list will appear suggesting terms that match. For terms that are in [EFO](http://www.ebi.ac.uk/efo) ([Experimental Factor Ontology](http://www.ebi.ac.uk/efo) - an EMBL-EBI resource providing systematic descriptions of biological samples and experimental variables), a button will be provided enabling expansion of more specific terms. Search terms are retained in the search box, where they can be refined (see the [Advanced search](https://www.ebi.ac.uk/biostudies/help#advancedsearch) section below).

The search results page is a list of matching biostudies sorted according to relevance. You can also change the sorting by using the _Sort by_ selector. If there are many results, they will be split over multiple pages. Links at the top of the results allow you to change the number of studies displayed per page as well as the current result page. Clicking on the title of a study takes you to a more detailed page about that study.

Within the results any matching terms are highlighted. Yellow highlighting indicates exact matches, green highlighting indicates synonyms, and peach highlighting indicates more specific matches (e.g. "pancreatic ductal adenocarcinoma" as a more specific term for "adenocarcinoma"). These more specific terms are from EFO. If a term has more than 1000 child terms, it is not expanded.

#### Advanced search

Each word in the query is treated as a separate term (unless surrounded by double quotes), and by default results can contain any of these queried terms. This behaviour can be modified by using boolean operators and brackets; e.g., Leukemia AND ( mouse OR human ), or cancer AND NOT ( human ).

Queries containing star or question mark characters are treated separately. A star character will match any combination of zero or more characters, e.g., leuk*mia will match to leukemia and leukaemia, as well as leukqwertymia. A question mark character will match any single characters, e.g., m?n will match both man and men. Queries that include wildcards are not expanded.

BioStudies search supports regular expression searched, e.g., searching for /[dl]ouse/ gives results for both louse and douse). As a results, the some characters (more specifically + - && || ! ( ) { } [ ] ^ " ~ * ? : \ /) are part of the query syntax and need to be either escaped or quoted if entered as a part of your query, e.g., query for eeg/fmri should be entered as either eeg\/fmri or "eeg/fmri". Similarly, queries for a DOI should be entered in double quotes as well, e.g., "10.1371/journal.pone.0127346".

Queries or parts of queries can also be in the [Lucene](https://lucene.apache.org/core/2_9_4/queryparsersyntax.html) query form like attribute_name:attribute_value. For example, author:smith AND title:bacteria will return fewer hits than smith AND bacteria. See below, in the /api/v1/search section, for a [full list of attributes](https://www.ebi.ac.uk/biostudies/help#rest-search).

### Download
- In addition to file download from the BioStudies website, we also support FTP and Aspera based downloads. For less than 1000 files, you can select the files from the study detail page and click on the "Download" button to get the HTTP/FTP/Aspera instructions. For larger studies, you will need to know the **path** of each of these files.
- This path is collection/parent/accession, where:
	- **collection** is the accession prefix e.g. S-EPMC for data imported from EuropePMC, S-BSST for data submitted via BioStudies Submission Tool, or E-MTAB for data belonging to the ArrayExpress collection.
	- **parent** is the last three digits in the accession, e.g. for S-BIAD300 it is 300. There are some exceptions to this though.
	    - For some older studies, parent is the masked path for the accession ending in the last 3 digits of the study accession number, e.g., older EuropePMC studies with accession numbers ending on 001 will be in the folder S-EPMCxxx001.
	    - For some older studies where the numeric part of the accession is one or two digit long, the parent folder is S-BSST0-99, e.g., for S-BSST7, the directory will be S-BSST/S-BSST0-99/S-BSST7.
	- **accession** is the study accession e.g. S-EPMC3521001
- Path for a study is available through the REST API, e.g.,


	$ curl https://www.ebi.ac.uk/biostudies/api/v1/studies/S-BSST7/info -s |
	jq -r .relPath S-BSST/S-BSST0-99/S-BSST7 $ curl
	https://www.ebi.ac.uk/biostudies/api/v1/studies/S-EPMC3521001/info -s |
	jq -r .relPath S-EPMC/001/S-EPMC3521001

#### FTP downloads
- The BioStudies FTP path is [ftp://ftp.ebi.ac.uk/biostudies](ftp://ftp.ebi.ac.uk/biostudies) . Anonymous downloads are enabled. For each study, you can click on the FTP button to access it. You can also use your favourite FTP client such as FileZilla to download a study from ftp://ftp.ebi.ac.uk/biostudies/**mode**/**path** , where,
	- **mode** is the storage mode and can be either fire or nfs
	- **path** is the path of the accession as [described above](https://www.ebi.ac.uk/biostudies/help#download)
- All data files for a study are in the ftp://ftp.ebi.ac.uk/biostudies/**mode**/**path**/Files directory, e.g., to download the file 1_TCGA_signature_A_top_10percent.txt from S-BSST7, you can use the command line wget ftp://ftp.ebi.ac.uk/biostudies/nfs/S-BSST/S-BSST0-99/S-BSST7/Files/1_TCGA_signature_A_top_10percent.txt or, for interactive access:
	$ ftp ftp.ebi.ac.uk Name: anonymous ftp> cd
	biostudies/nfs/S-BSST/S-BSST0-99/S-BSST7/Files ftp> get
	1_TCGA_signature_A_top_10percent.txt
- You can get the FTP link for a study from the /info REST API endpoint, e.g.,
	$ curl https://www.ebi.ac.uk/biostudies/api/v1/studies/S-BSST7/info -s | jq -r .ftpLink

#### Aspera downloads
- You will need to [download the Aspera ascp command line interface](https://www.ibm.com/support/fixcentral/swg/selectFixes?parent=ibm~Other%20software&product=ibm/Other%20software/IBM%20Aspera%20CLI&release=All&platform=All&function=all) . Please select the correct operating system. The ascp command line client is present in the bin folder in the installation directory. Your command for download should be like this:
- ascp -P33001 -i key bsaspera@fasp-beta.ebi.ac.uk:files to download download location on your machine
	- P33001 and bsaspera@fasp.ebi.ac.uk defines the port, user and server for the Aspera connection
	- key is the public key for the Aspera connection which has the value aspera cli installation directory/etc/asperaweb_id_dsa.openssh for Linux/MacOS and aspera cli installation directory\etc\asperaweb_id_dsa.openssh for Windows.
	- files to download might be all files for a certain study, as explained above.
- For instance, here's the command line to download the file aeipf_denoised_reads.fna from submission S-BSST12 to the directory C:\Temp on Windows.
	“C:.exe” -P33001 -i “C:_id_dsa.openssh”
	bsaspera@fasp-beta.ebi.ac.uk:/S-BSST/012/S-BSST12/Files/aeipf_denoised_reads.fna
	C:
- Aspera downloads are available only for studies where **mode** is fire.
#### Globus downloads
- BioStudies supports file downloads through [Globus](https://www.globus.org/) as well. You can click on the [![](https://www.ebi.ac.uk/biostudies/images/globus-logo.png)Globus](https://www.ebi.ac.uk/biostudies/help "Open Globus") icon to open up the [EMBL-EBI Public Data collection](https://app.globus.org/file-manager?origin_id=47772002-3e5b-4fd3-b97c-18cee38d6df2&origin_path=%2Fbiostudies%2F) in the Globus File Manager app. You may want to install [Globus Connect Personal](https://www.globus.org/globus-connect-personal) which creates a personal collection on your machine for [transferring multiple files](https://docs.globus.org/how-to/get-started/).

###