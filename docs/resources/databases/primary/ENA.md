> Research status: owner-curated interface reference for v02 ORCS enrichment. Examples and described capabilities require confirmation for the specific programmatic retrieval contract; this note does not authorize live retrieval or define pipeline filters.


# European Nucleotide Archive

## EBI Search
- Searches across all ENA data
- All biological data resouces hosted at teh European Bioinformatics Institute (EMBL-EBI)
- Nucleotide and protein sequences; structures ranging from chemicals to macro-molecular complexes; gene-expression experiments; binary level molecular interactions; reaction maps and pathway models; functional classifications; biological ontologies; diseases; comprehensive literature libraries
### Specification
- A WADL for the EBI Search RESTful service is defined to build a generic client.
- The EBI Search RESTful API is presented here via our OpenAPI Specification(formerly Swagger Specification) definition
#### Search - Entry Retrieval
- General Information

| Summary         | Description                                                             | Method | URL                                                       |     |
| --------------- | ----------------------------------------------------------------------- | ------ | --------------------------------------------------------- | --- |
| Entry retrieval | It returns entry information associated with entry identifiers provided | GET    | www.ebi.ac.uk/ebisearch/ws/rest/{domain}/entry/{entryids} |     |

- Response content type
	- application/xml
	- application/json
	- text/csv
	- text/tab-separated-values
	- text/plain
- Parameters

| Parameter name | Parameter value | Description                                                                                                                             | Data type |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| domain         | required        | A single domain identifier e.g. uniprot                                                                                                 | string    |
| entryids       | required        | Comma separated values of entry identifiers (max 100) e.g. P53_HUMAN                                                                    | string    |
| fields         |                 | Comma separated values of field identifiers to retrieve e.g. descRecName                                                                | string    |
| fieldurl       |                 | Whether field links are included. The returned links mean direct URLs to the data entries in original portals. Valid with XML/JSON only | string    |
| viewurl        |                 | Whether other view links on an entry are included. Valid with XML/JSON only                                                             | string    |
| format         |                 | Response format                                                                                                                         | string    |

#### Search - All EBI search
- General Information

|Summary|Description|Method|URL|
|---|---|---|---|
|All EBI search|If a query parameter is specified, it will return the numbers of hits in a domain hierarchy. Otherwise, return meta-data of all domains available in EBI Search|GET|//www.ebi.ac.uk/ebisearch/ws/rest/|
- Response content type
	- application/xml
	- application/json
	- text/csv
	- text/tab-separated-values
	- text/plain
- Parameters

|Parameter name|Parameter value|Description|Data type|
|---|---|---|---|
|query||Query string e.g. tp53|string|
|filter||Filter queries (non-scoring queries that do not affect relevance) e.g. TAXONOMY:9606|array|
|format||Response format|string|

#### Search - Domain search
- General Information

|Summary|Description|Method|URL|
|---|---|---|---|
|Domain search|If a query parameter is specified, it will return search results. Otherwise, return meta-data of the specified domain|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}|
- Response content type
	- application/xml
	- application/json
	- text/xml
	- text/csv
	- text/tab-separated-values
	- text/plain
- Parameters

| Parameter name   | Parameter value | Description                                                                                                                                                                                                                                                                                                                                                     | Data type |
| ---------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| domain           | required        | A single domain identifier e.g. uniprot                                                                                                                                                                                                                                                                                                                         | string    |
| query            |                 | Query string e.g. tp53                                                                                                                                                                                                                                                                                                                                          | string    |
| filter           |                 | Filter queries (non-scoring queries that do not affect relevance) e.g. TAXONOMY:9606                                                                                                                                                                                                                                                                            | array     |
| size             |                 | The number of entries to retrieve. limit 10,000 for list type and 100 for other types                                                                                                                                                                                                                                                                           | string    |
| start            |                 | The index of the first entry in the results. Limit 100,000                                                                                                                                                                                                                                                                                                      | string    |
| sortfield        |                 | A single field identifier to sort on. Not allowed to use with 'sort' parameter                                                                                                                                                                                                                                                                                  | string    |
| order            |                 | Whether to sort in ascending/descending order. Should come along with 'sortfield' parameter and not allowed to use with 'sort' parameter                                                                                                                                                                                                                        | string    |
| sort             |                 | Comma separated values of sorting criteria. (field_id:order, e.g. boost:descending,length:descending). Should not be used in conjunction with any of 'sortfield' and 'order' parameters                                                                                                                                                                         | string    |
| sortignorenull   |                 | Ignore null values at sort time. If true, null values will always appear on the end                                                                                                                                                                                                                                                                             | string    |
| fields           |                 | Comma separated values of field identifiers to retrieve                                                                                                                                                                                                                                                                                                         | string    |
| fieldurl         |                 | Whether field links are included. The returned links mean direct URLs to the data entries in the original portals. Valid with XML/JSON only                                                                                                                                                                                                                     | string    |
| viewurl          |                 | Whether other view links on an entry are included. Valid with XML/JSON only                                                                                                                                                                                                                                                                                     | string    |
| facetfields      |                 | Comma separated values of field identifiers associated with facets to retrieve. In case of hierarchical facet, the value for the field can be a path where the nodes are separated by a '/'. i.e.: taxonomy_lineage/1/10239/35268 (taxonomy_lineage is the name of the hierarchical facet and nodes are possible values of the facet). Valid with XML/JSON only | string    |
| facetcount       |                 | The number of facet values to retrieve. In case of hierarchical facet, the facet count limit the number of children retrieved in a single level. Valid with XML/JSON only.                                                                                                                                                                                      | string    |
| facets           |                 | A comma separated list of selected facet values                                                                                                                                                                                                                                                                                                                 | string    |
| feedtitle        |                 | RSS feed title and required when a selected format parameter is 'rss'                                                                                                                                                                                                                                                                                           | string    |
| feedmaxdays      |                 | The number of days for time window. always used with 'feedmasdaysfield' parameter. valid when format is 'rss'                                                                                                                                                                                                                                                   | string    |
| feedmaxdaysfield |                 | A date type field to set time window. always used with 'feedmaxdays' parameter. valid when format is 'rss'                                                                                                                                                                                                                                                      | string    |
| entryattrs       |                 | Comma separated values of additional entry attributes. Valid with XML/JSON only.                                                                                                                                                                                                                                                                                | string    |
| hlfields         |                 | Comma separated values of field identifiers to apply highlighting. Valid with XML/JSON only                                                                                                                                                                                                                                                                     | string    |
| hlpretag         |                 | A string appearing before a highlighted term. Valid with XML/JSON only.                                                                                                                                                                                                                                                                                         | string    |
| hlposttag        |                 | A string appearing after a highlighted term. Valid with XML/JSON only.                                                                                                                                                                                                                                                                                          | string    |
| format           |                 | Response format                                                                                                                                                                                                                                                                                                                                                 | string    |
| searchposition   |                 | The search position from which to start the next request. Set to 0 to start a new bulk search.                                                                                                                                                                                                                                                                  | string    |

#### Cross-reference search - cross-reference search
- General Information

|Summary|Description|Method|URL|
|---|---|---|---|
|Cross-reference search|It returns a list of cross references in a target domain associated with an entry|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}/entry/{entryids}/xref/{targetdomainid}|

- Response content type
	- application/xml
	- application/json
	- text/csv
	- text/tab-separated-values
	- text/plain
- Parameters

| Parameter name | Parameter value | Description                                                                                                                                                                                                                                                                                                                                                     | Data type |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| domain         | required        | A single domain identifier e.g. uniprot                                                                                                                                                                                                                                                                                                                         | string    |
| entryids       | required        | Comma separated values of entry identifiers e.g. P53_HUMAN                                                                                                                                                                                                                                                                                                      | string    |
| targetdomainid | required        | A single domain identifier to search on e.g. europepmc                                                                                                                                                                                                                                                                                                          | string    |
| size           |                 | The number of entries to retrieve. limit 100                                                                                                                                                                                                                                                                                                                    | string    |
| start          |                 | The index of the first entry in the results. limit 1,000,000                                                                                                                                                                                                                                                                                                    | string    |
| fields         |                 | Comma separated values of field identifiers to retrieve                                                                                                                                                                                                                                                                                                         | string    |
| fieldurl       |                 | Whether field links are included. The returned links mean direct URLs to the data entries in the original portals. Valid with XML/JSON only                                                                                                                                                                                                                     | string    |
| viewurl        |                 | Whether other view links on an entry are included. Valid with XML/JSON only                                                                                                                                                                                                                                                                                     | string    |
| facetfields    |                 | Comma separated values of field identifiers associated with facets to retrieve. In case of hierarchical facet, the value for the field can be a path where the nodes are separated by a '/'. i.e.: taxonomy_lineage/1/10239/35268 (taxonomy_lineage is the name of the hierarchical facet and nodes are possible values of the facet). Valid with XML/JSON only | string    |
| facetcount     |                 | The number of facet values to retrieve. In case of hierarchical facet, the facet count limit the number of children retrieved in a single level. Valid with XML/JSON only.                                                                                                                                                                                      | string    |
| facets         |                 | A comma separated list of selected facet values                                                                                                                                                                                                                                                                                                                 | string    |
| query          |                 | Query string e.g. tp53                                                                                                                                                                                                                                                                                                                                          | string    |
| via            |                 | Comma seperated values of domain identifiers associated with finding cross-references                                                                                                                                                                                                                                                                           | string    |
| format         |                 | Response format                                                                                                                                                                                                                                                                                                                                                 | string    |

#### Cross-reference search - finding domains referred by an entry
- General Information

|Summary|Description|Method|URL|
|---|---|---|---|
|Finding domains referred by an entry|It returns a list of domains referred by an entry|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}/entry/{entryid}/xref|

- Response content type
	- application/xml
	- application/json
	- text/csv
	- text/tab-separated-values
	- text/plain
- Parameters

| Parameter name | Parameter value | Description                              | Data type |
| -------------- | --------------- | ---------------------------------------- | --------- |
| domain         | required        | A single domain identifier e.g. uniprot  | string    |
| entryid        | required        | A single entry identifier e.g. P53_HUMAN | string    |
| format         |                 | Response format                          | string    |

#### Cross-reference search - finding domains referred by a domain
- General information

| Summary                              | Description                                       | Method | URL                                             |
| ------------------------------------ | ------------------------------------------------- | ------ | ----------------------------------------------- |
| Finding domains referred by a domain | It returns a list of domains referred by a domain | GET    | //www.ebi.ac.uk/ebisearch/ws/rest/{domain}/xref |
- Response content type
	- application/xml
	- application/json
	- text/csv
	- text/tab-separated-values
	- text/plain
- Parameters

| Parameter name | Parameter value | Description                             | Data type |
| -------------- | --------------- | --------------------------------------- | --------- |
| domain         | required        | A single domain identifier e.g. uniprot | string    |
| format         |                 | Response format                         | string    |

#### Auto complete
- General Information

|Summary|Description|Method|URL|
|---|---|---|---|
|Auto complete|It returns a list of suggested queries based on a given term|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}/autocomplete|

- Response content type
	- application/xml
	- application/json
	- text/csv
	- text/tab-separated-values
	- text/plain
- Parameters

| Parameter name | Parameter value | Description                                                                      | Data type |
| -------------- | --------------- | -------------------------------------------------------------------------------- | --------- |
| domain         | required        | A single domain identifier e.g. uniprot                                          | string    |
| term           | required        | A term to get suggestions, whose length should be at least 3 characters e.g. tpi | string    |
| formatted      |                 | Whether to include suggestions in a highlighted form                             | string    |
| format         |                 | Response format                                                                  | string    |

#### Top Terms
- General information

|Summary|Description|Method|URL|
|---|---|---|---|
|Top terms|It returns a list of top terms of a field|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}/topterms/{fieldid}|

- Response content type
	- application/xml
	- application/json
	- text/csv
	- text/tab-separated-values
	- text/plain
- Parameters

| Parameter name | Parameter value | Description                                                                  | Data type |
| -------------- | --------------- | ---------------------------------------------------------------------------- | --------- |
| domain         | required        | A single domain identifier e.g. pride                                        | string    |
| fieldid        | required        | A single field identifier e.g. data_protocol                                 | string    |
| size           |                 | The number of entries to retrieve. limit 100                                 | string    |
| excludes       |                 | Comma separated values of terms to be excluded (e.g. stop-words) e.g. to,the | string    |
| excludesets    |                 | Comma separated values of stop-word sets to be excluded                      | string    |
| format         |                 | Response format                                                              | string    |

#### Sequence analysis tool results search
|Summary|Description|Method|URL|
|---|---|---|---|
|Sequencing tool results search|Get the results from a Sequencing tool search and map them to a domain, permitting to execute further text and facets filtering|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}/seqtoolresults|

- Response content type
	- application/xml
	- application/json
	- text/csv
	- text/tab-separated-values
	- text/plain
- Parameters

| Parameter name     | Parameter value | Description                                                                                                                                                                                                                                                                                                                                                     | Data type |
| ------------------ | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| domain             | required        | A single domain identifier e.g. uniprot                                                                                                                                                                                                                                                                                                                         | string    |
| toolid             | required        | Identifier of sequencing tool configured in the system. Please check the 'seqtoolresults/help' endpoint for more information                                                                                                                                                                                                                                    | string    |
| jobid              | required        | Identifier of sequencing tool job                                                                                                                                                                                                                                                                                                                               | string    |
| query              |                 | Query string e.g. tp53                                                                                                                                                                                                                                                                                                                                          | string    |
| filter             |                 | Filter queries (non-scoring queries that do not affect relevance) e.g. TAXONOMY:9606                                                                                                                                                                                                                                                                            | array     |
| size               |                 | The number of entries to retrieve. limit 10,000 for list type and 100 for other types                                                                                                                                                                                                                                                                           | string    |
| start              |                 | The index of the first entry in the results. Limit 100,000                                                                                                                                                                                                                                                                                                      | string    |
| sortfield          |                 | A single field identifier to sort on. Not allowed to use with 'sort' parameter                                                                                                                                                                                                                                                                                  | string    |
| order              |                 | Whether to sort in ascending/descending order. Should come along with 'sortfield' parameter and not allowed to use with 'sort' parameter                                                                                                                                                                                                                        | string    |
| sort               |                 | Comma separated values of sorting criteria. (field_id:order, e.g. boost:descending,length:descending). Should not be used in conjunction with any of 'sortfield' and 'order' parameters                                                                                                                                                                         | string    |
| sortignorenull     |                 | Ignore null values at sort time. If true, null values will always appear on the end                                                                                                                                                                                                                                                                             | string    |
| fields             |                 | Comma separated values of field identifiers to retrieve                                                                                                                                                                                                                                                                                                         | string    |
| fieldurl           |                 | Whether field links are included. The returned links mean direct URLs to the data entries in the original portals. Valid with XML/JSON only                                                                                                                                                                                                                     | string    |
| viewurl            |                 | Whether other view links on an entry are included. Valid with XML/JSON only                                                                                                                                                                                                                                                                                     | string    |
| facetfields        |                 | Comma separated values of field identifiers associated with facets to retrieve. In case of hierarchical facet, the value for the field can be a path where the nodes are separated by a '/'. i.e.: taxonomy_lineage/1/10239/35268 (taxonomy_lineage is the name of the hierarchical facet and nodes are possible values of the facet). Valid with XML/JSON only | string    |
| facetcount         |                 | The number of facet values to retrieve. In case of hierarchical facet, the facet count limit the number of children retrieved in a single level. Valid with XML/JSON only.                                                                                                                                                                                      | string    |
| facets             |                 | A comma separated list of selected facet values                                                                                                                                                                                                                                                                                                                 | string    |
| feedtitle          |                 | RSS feed title and required when a selected format parameter is 'rss'                                                                                                                                                                                                                                                                                           | string    |
| feedmaxdays        |                 | The number of days for time window. always used with 'feedmasdaysfield' parameter. valid when format is 'rss'                                                                                                                                                                                                                                                   | string    |
| feedmaxdaysfield   |                 | A date type field to set time window. always used with 'feedmaxdays' parameter. valid when format is 'rss'                                                                                                                                                                                                                                                      | string    |
| entryattrs         |                 | Comma separated values of additional entry attributes. Valid with XML/JSON only.                                                                                                                                                                                                                                                                                | string    |
| hlfields           |                 | Comma separated values of field identifiers to apply highlighting. Valid with XML/JSON only                                                                                                                                                                                                                                                                     | string    |
| hlpretag           |                 | A string appearing before a highlighted term. Valid with XML/JSON only.                                                                                                                                                                                                                                                                                         | string    |
| hlposttag          |                 | A string appearing after a highlighted term. Valid with XML/JSON only.                                                                                                                                                                                                                                                                                          | string    |
| format             |                 | Response format                                                                                                                                                                                                                                                                                                                                                 | string    |
| searchposition     |                 | The search position from which to start the next request. Set to 0 to start a new bulk search.                                                                                                                                                                                                                                                                  | string    |
| tooloutputformat   |                 | Sequence Tool output format configured in the system (i.e.: ids) if missing a default will be used                                                                                                                                                                                                                                                              | string    |
| jobresultsstart    |                 | Sequence Tool results reading start index                                                                                                                                                                                                                                                                                                                       | integer   |
| jobresultssize     |                 | Sequence Tool results reading size                                                                                                                                                                                                                                                                                                                              | integer   |
| jobresultsmapfield |                 | Sequence Tool results domain field to map on, default is 'id'                                                                                                                                                                                                                                                                                                   | string    |
| valuemappers       |                 | Comma separated list of 'value mappers' to use on the sequence tool results. Value mappers help in translating the values from the Sequence Search tool results to values in the EBI Search domain. A list of possible values are available in the system configuration                                                                                         | string    |

#### More like this - more like this in a same domain
|Summary|Description|Method|URL|
|---|---|---|---|
|More like this in a same domain|It returns similar entries to an entry. In order to get better results it is necessary to tune parameters|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}/entry/{entryid}/morelikethis|


| Parameter name | Parameter value | Description                                                                                                                                 | Data type |
| -------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| domain         | required        | A single domain identifier e.g. pride                                                                                                       | string    |
| entryid        | required        | A single entry identifier of a base entry e.g. PXD001673                                                                                    | string    |
| size           |                 | The number of entries to retrieve. limit 100                                                                                                | string    |
| start          |                 | The index of the first entry in the results. limit 1,000,000                                                                                | string    |
| fields         |                 | Comma separated values of field identifiers to retrieve e.g. name                                                                           | string    |
| fieldurl       |                 | Whether field links are included. The returned links mean direct URLs to the data entries in the original portals. Valid with XML/JSON only | string    |
| viewurl        |                 | Whether other view links on an entry are included. Valid with XML/JSON only                                                                 | string    |
| mltfields      |                 | Comma separated values of field identifiers to be used for generating a query                                                               | string    |
| mintermfreq    |                 | The minimum term frequency. Any terms whose frequency is below this value will be ignored from forming a final query                        | string    |
| mindocfreq     |                 | The minimum document frequency. Any terms which do not occur in at least this number of entries will be ignored                             | string    |
| maxqueryterm   |                 | The maximum number of query terms that will be included in any generated query (max. 25)                                                    | string    |
| excludes       |                 | Comma separated values of terms to be excluded (e.g. stop-words) e.g. to,the                                                                | string    |
| excludesets    |                 | Comma separated values of stop-word sets to be excluded                                                                                     | string    |
| format         |                 | Response format                                                                                                                             | string    |
| entryattrs     |                 | Comma separated values of additional entry attributes. Valid with XML/JSON only.                                                            | string    |

#### More like this - more like this

|Summary|Description|Method|URL|
|---|---|---|---|
|More like this|It returns similar entries in a target domain to an entry. In order to get better results it is necessary to tune parameters|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}/entry/{entryid}/morelikethis/{targetdomaini|

| Parameter name | Parameter value | Description                                                                                                                                 | Data type |
| -------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| domain         | required        | A single domain identifier e.g. pride                                                                                                       | string    |
| entryid        | required        | A single entry identifier of a base entry e.g. PXD001673                                                                                    | string    |
| targetdomainid | required        | A single domain identifier to search on                                                                                                     | string    |
| size           |                 | The number of entries to retrieve. limit 100                                                                                                | string    |
| start          |                 | The index of the first entry in the results. limit 1,000,000                                                                                | string    |
| fields         |                 | Comma separated values of field identifiers to retrieve e.g. name                                                                           | string    |
| fieldurl       |                 | Whether field links are included. The returned links mean direct URLs to the data entries in the original portals. Valid with XML/JSON only | string    |
| viewurl        |                 | Whether other view links on an entry are included. Valid with XML/JSON only                                                                 | string    |
| mltfields      |                 | Comma separated values of field identifiers to be used for generating a query                                                               | string    |
| mintermfreq    |                 | The minimum term frequency. Any terms whose frequency is below this value will be ignored from forming a final query                        | string    |
| mindocfreq     |                 | The minimum document frequency. Any terms which do not occur in at least this number of entries will be ignored                             | string    |
| maxqueryterm   |                 | The maximum number of query terms that will be included in any generated query (max. 25)                                                    | string    |
| excludes       |                 | Comma separated values of terms to be excluded (e.g. stop-words) e.g. to,the                                                                | string    |
| excludesets    |                 | Comma separated values of stop-word sets to be excluded                                                                                     | string    |
| format         |                 | Response format                                                                                                                             | string    |
| entryattrs     |                 | Comma separated values of additional entry attributes. Valid with XML/JSON only.                                                            | string    |
#### Raw data retrieval

|Summary|Description|Method|URL|
|---|---|---|---|
|Retrieving raw data for supported domains|It returns a raw data content for given domain and identifier|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}/rawdata/{entryid}|

| Parameter name | Parameter value | Description                             | Data type |
| -------------- | --------------- | --------------------------------------- | --------- |
| domain         | required        | A single domain identifier e.g. epo     | string    |
| entryid        | required        | A single entry identifier e.g. CQ852354 | string    |

### S4/Summary Specification

#### Suggestion - Suggested terms

|Summary|Description|Method|URL|
|---|---|---|---|
|Suggested terms|Retrieve a list of suggestions for a term|GET|//www.ebi.ac.uk/ebisearch/summary/api/suggestion|

| Parameter name | Parameter value | Description                                                                 | Data type |
| -------------- | --------------- | --------------------------------------------------------------------------- | --------- |
| term           | required        | term for which suggestions should be generated - e.g. VAV_HUMAN, tpi1, 1n0w | string    |

#### Identification - Identify a set of summary terms

|Summary|Description|Method|URL|
|---|---|---|---|
|Identify a set of summary terms|Retrieve a set of term identifiers for a given term, within a pre-selected spine and/or term|GET|//www.ebi.ac.uk/ebisearch/summary/api/identification|

| Parameter name | Parameter value | Description                                                                                              | Data type |
| -------------- | --------------- | -------------------------------------------------------------------------------------------------------- | --------- |
| term           | requried        | term for which correlated entries will be pulled from protein and gene DB's - e.g. VAV_HUMAN, tpi1, 1n0w | string    |
| spine          |                 | the chosen spine (optional) - e.g. molecular                                                             | string    |
| tid            |                 | term identifier (optional) - e.g. protOrthVAV2HUMAN                                                      | string    |

### Stop word sets

These stop word sets can be used to exclude certain terms for 'excludesets' parameter in More like this & Top terms APIs

|Set id|List of stop words|
|---|---|
|lucene_stopwords|a, an, and, are, as, at, be, but, by, for, if, in, into, is, it, no, not, of, on, or, such, that, the, their, then, there, these, they, this, to, was, will, with|
|digits|0, 1, 2, 3, 4, 5, 6, 7, 8, 9|
|alphabets|a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z|
|omics_stopwords|1, 2, 3, 4, 5, 6, 7, 8, 9, a, able, about, across, after, all, almost, also, am, among, an, and, any, are, as, at, b, be, because, been, but, by, c, can, could, d, dear, did, do, does, e, either, else, ever, every, f, for, from, g, get, got, h, had, has, have, he, her, hers, him, how, however, i, if, in, into, is, it, its, j, just, k, \\l, least, let, like, likely, m, may, me, might, most, must, n, neither, no, nor, not, o, of, off, often, on, only, or, other, our, own, p, q, r, rather, s, should, since, so, some, such, \\t, than, that, the, their, them, then, then, there, these, they, this, to, too, u, us, v, w, was, we, were, what, when, where, which, while, who, whom, why, will, with, would, x, y, yet, you, your, z|

### Response formats

If a valid 'format' parameter is present, the parameter will be taken into account. If no parameter is specified, the response format is determined by 'Accept' HTTP request header.

|Response format|'format' parameter|HTTP 'Accept' header|Note|
|---|---|---|---|
|XML|xml|application/xml||
|JSON|json|application/json||
|RSS|rss|text/xml|available only Domain sarch API|
|CSV (Comma-separated values)|csv|text/csv||
|TSV (Tab-separated values)|tsv|text/tab-separated-values||
|ID list|idlist|text/plain|available only Domain search and Entry retrieval APIs  <br>example:<br><br>> TPIS_HUMAN  <br>> TPIS_MOUSE  <br>> ...|
|Accession number list|acclist|text/plain|available only Domain search and Entry retrieval APIs  <br>example:<br><br>> TPIS_HUMAN,TPIS_MOUSE,...|
|Comma separated ID list|cs_idlist|text/plain|available only Domain search and Entry retrieval APIs  <br>example:<br><br>> P60174  <br>> P17751  <br>> ...|
|Comma separated Accession number list|cs_acclist|text/plain|available only Domain search and Entry retrieval APIs  <br>example:<br><br>> P60174,P17751,...|
### HTTP status code

|HTTP status Code|Description|
|---|---|
|200 (Okay)|Successful operation|
|400 (Bad request)|Wrong user input parameters|
|404 (Not found)|Wrong URLs|
|500 (Internal server error)|Server internal error. If the problem persists please contact us at [EMBL-EBI Support](http://www.ebi.ac.uk/support/index.php?query=WebServices)|




## Searching with a query
### Introduction

You can find entries you're interested in by specifying the _query_ parameter e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53) 

  
By default, a response in XML format is returned. Depending on the _format_ parameter, a response in a different format can be returned. Here are some examples:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=xml](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=xml) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=json](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=json) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=tsv](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=tsv) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=csv](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=csv) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=idlist](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=idlist) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=acclist](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=acclist) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=cs_idlist](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=cs_acclist) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=cs_acclist](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&format=cs_acclist) 

More information about formats can be found [here](https://www.ebi.ac.uk/apidoc.ebi#response-formats).

  

The entry's identifier and the domain identifier it belongs to are returned, by default. It is possible to retrieve other fields' values using the _fields_ parameter, e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&fields=gene_primary_name,length](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&fields=gene_primary_name,length) 

Not all fields are retrievable. Which fields are retrievable in e.g. _UniProtKB_ are retrievable can be found [here](https://www.ebi.ac.uk/ebisearch/metadata.ebi?db=uniprot).

  

The link where the entry's detail can be found can be obtained using the _fieldurl_ parameter e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&fieldurl=true](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&fieldurl=true) 

  

There are additional links in some domains e.g. an UniProtKB entry in FASTA format:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&viewurl=true](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&viewdurl=true) 

### Pagination

By default a returned result has the first 15 entries if the number of hits is greater than 15. The both requests below return a same response.

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53) 

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&size=15](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&size=15) 

The _size_ parameter can't take a number greater than 100 for most response formats. However, greater numbers can be acceptable for certain formats. Please refer to [here](https://www.ebi.ac.uk/apidoc.ebi#response-formats).

  

It is possible to get the number of hits only by specifying the _size_ parameter is 0. The actual number can be obtained by parsing the response body or reading the value of the HTTP header: _x-ebi-search-total-results_.

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&size=0](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&size=0) 

  

To implement pagination, the number of entries per page is needed e.g. the following example gets the first 10 entries:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&size=10](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&size=10) 

  

The next 10 entries can be gained by the _start_ parameter, which indicates the index of the first entry in the results e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&size=10&start=10](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&size=10&start=10) 

More than 1,000,000 entries cannot be retrievable at the moment.

### Sorting

Lucene relevance score is the default sorting criterion. However some domains have specific sorting criteria (e.g. Literature data ordered by _publication_date_ field).

By reading the value of the HTTP header: _x-ebi-search-query-parameters_, it is possible to figure out the sorting criterion applied to a result. For example, a search result from _RNAcentral_ is ordered by the _boost_ field:

$ curl -I  [https://www.ebi.ac.uk/ebisearch/ws/rest/rnacentral?query=hotair](https://www.ebi.ac.uk/ebisearch/ws/rest/rnacentral?query=hotair) 
HTTP/1.1 200
Cache-Control: private,max-age=60
X-EBI-Search-Version: 47.3
X-EBI-Search-Total-Results: 23
Content-Type: application/xml;charset=UTF-8
Access-Control-Expose-Headers: X-EBI-Search-Version,X-EBI-Search-RetrievableHits,X-EBI-Search-RetrievableFacets,X-EBI-Search-Querystring,X-EBI-Search-Query-Parameters,X-EBI-Search-Total-Results,X-EBI-Search-Max-suggested-terms
Strict-Transport-Security: max-age=0
Date: Fri, 14 Aug 2020 13:30:18 GMT
X-EBI-Search-RetrievableHits: 1000000
X-EBI-Search-RetrievableFacets: 1000
X-EBI-Search-Querystring: hotair
Transfer-Encoding: chunked
ETag: "726e6163656e7472616c5f5475652c2037204a756c20323032302031303a31383a343820474d54"
X-Robots-Tag: noindex,nofollow
Last-Modified: Tue, 7 Jul 2020 10:18:48 GMT
X-EBI-Search-Max-suggested-terms: 15
**X-EBI-Search-Query-Parameters: domain:rnacentral; start:0; size:15; sort:boost; order:descending**
      

Which fields can be used for sorting results can be found [here](https://www.ebi.ac.uk/ebisearch/metadata.ebi?db=rnacentral) e.g for _RNAcentral_.

  

To apply a different sorting rule, there are two ways. One is using the _sortfield_ and _order_ parameters. This can be used to apply a single rule. e.g.

 [https://www.ebi.ac.uk/ebisearch/ws/rest/rnacentral?query=hotair&sortfield=length&order=descending ](https://www.ebi.ac.uk/ebisearch/ws/rest/rnacentral?query=hotair&sortfield=length&order=descending) 

  

If more than one sorting criterion needs to be applied, the _sort_ parameter can help e.g. applying two criteria:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/rnacentral?query=hotair&sort=length:descending,boost:descending ](https://www.ebi.ac.uk/ebisearch/ws/rest/rnacentral?query=hotair&sort=length:descending,boost:descending) 

Do not use the _sort_ parameter with the _sortfield_ and _order_ parameters.

### Highlighting

Highlighting a text matching with a given query string is a nice feature especially when displaying results on Web interface, for example. The _hlfields_ parameter can be used to get highlighting applied values of fields while the _field_ parameter is for original values.

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&hlfields=descRecName](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&hlfields=descRecName) 

The _hlfields_ works with retrievalbe fields only.

  

The highlighted terms are wrapped with _<em></em>_. Using the _hlpretag_ and _hlposttag_ parameters can change how to decorate highlighted terms e.g.

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&hlfields=descRecName&hlpretag=<i>&hlposttag=</i>](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&hlfields=descRecName&hlpretag=%3Ci%3E&hlposttag=%3C/i%3E) 

### Try example

Try your own example here:

General information

|Summary|Description|Method|URL|
|---|---|---|---|
|Domain search|If a query parameter is specified, it will return search results. Otherwise, return meta-data of the specified domain|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}|

Response content type

application/xmlapplication/jsontext/xmltext/csvtext/tab-separated-valuestext/plain

Parameters

|Parameter name|Parameter value|Description|Data type|
|---|---|---|---|
|domain||A single domain identifier e.g. uniprot|string|
|query||Query string e.g. tp53|string|
|filter||Filter queries (non-scoring queries that do not affect relevance) e.g. TAXONOMY:9606|array|
|size||The number of entries to retrieve. limit 10,000 for list type and 100 for other types|string|
|start||The index of the first entry in the results. Limit 100,000|string|
|sortfield||A single field identifier to sort on. Not allowed to use with 'sort' parameter|string|
|order||Whether to sort in ascending/descending order. Should come along with 'sortfield' parameter and not allowed to use with 'sort' parameter|string|
|sort||Comma separated values of sorting criteria. (field_id:order, e.g. boost:descending,length:descending). Should not be used in conjunction with any of 'sortfield' and 'order' parameters|string|
|sortignorenull||Ignore null values at sort time. If true, null values will always appear on the end|string|
|fields||Comma separated values of field identifiers to retrieve|string|
|fieldurl||Whether field links are included. The returned links mean direct URLs to the data entries in the original portals. Valid with XML/JSON only|string|
|viewurl||Whether other view links on an entry are included. Valid with XML/JSON only|string|
|facetfields||Comma separated values of field identifiers associated with facets to retrieve. In case of hierarchical facet, the value for the field can be a path where the nodes are separated by a '/'. i.e.: taxonomy_lineage/1/10239/35268 (taxonomy_lineage is the name of the hierarchical facet and nodes are possible values of the facet). Valid with XML/JSON only|string|
|facetcount||The number of facet values to retrieve. In case of hierarchical facet, the facet count limit the number of children retrieved in a single level. Valid with XML/JSON only.|string|
|facets||A comma separated list of selected facet values|string|
|feedtitle||RSS feed title and required when a selected format parameter is 'rss'|string|
|feedmaxdays||The number of days for time window. always used with 'feedmasdaysfield' parameter. valid when format is 'rss'|string|
|feedmaxdaysfield||A date type field to set time window. always used with 'feedmaxdays' parameter. valid when format is 'rss'|string|
|entryattrs||Comma separated values of additional entry attributes. Valid with XML/JSON only.|string|
|hlfields||Comma separated values of field identifiers to apply highlighting. Valid with XML/JSON only|string|
|hlpretag||A string appearing before a highlighted term. Valid with XML/JSON only.|string|
|hlposttag||A string appearing after a highlighted term. Valid with XML/JSON only.|string|
|format||Response format|string|
|searchposition||The search position from which to start the next request. Set to 0 to start a new bulk search.|string|

## Faceted searching

### Introduction

To get facets along with a search result, the _query_ and _facetcount_ parameters are needed e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&facetcount=5](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&facetcount=5) 

The _facetcount_ parameter denotes the number of facet values per facet

  

By default, a response in XML format is returned. Only JSON and XML formats are supported to retrieve facets e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&facetcount=5&format=xml](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&facetcount=5&format=xml) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&facetcount=5&format=json](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&facetcount=5&format=json) 

  

If the _facetcount_ parameter is specified with a number greater than 0, a response is returned with all available facets. Each domain has its own list of facets. The _facetfields_ parameter can be used to get only a list of facets that you are interested in e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&facetcount=5&facetfields=status,TAXONOMY](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&facetcount=5&facetfields=status,TAXONOMY) 

  

To filter out by a list of selected facet values, the _facets_ parameter can help. The value format for the parameter is a comma separated list of _facet id_:_facet value_ e.g.

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&facetcount=5&facets=status:Reviewed](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&facetcount=5&facets=status:Reviewed)   
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&facetcount=5&facets=status:Reviewed,TAXONOMY:9606](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot?query=tp53&facetcount=5&facets=status:Reviewed,TAXONOMY:9606) 

### Hierarchical facets

Some facets are built in hierarchy. For example, date type facets (e.g. _EuropePMC_ - _publication_date_ facet) are built in three different levels, year/month/day. This means that it is feasible to filter out results by different levels of facet values and retrieve facet values in a full hierarchy or a partial.

This is to get values in full hierarchy:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/europepmc?query=tp53&facetcount=5&facetfields=publication_date](https://www.ebi.ac.uk/ebisearch/ws/rest/europepmc?query=tp53&facetcount=5&facetfields=publication_date) 

  

This request returns a result of searching for tp53 with values of the _publication_date_ facet in the partial hierarchy associated with 2020 year only:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/europepmc?query=tp53&facetcount=5&facetfields=publication_date/2020](https://www.ebi.ac.uk/ebisearch/ws/rest/europepmc?query=tp53&facetcount=5&facetfields=publication_date/2020) 

  

Search results can be narrowed down by different levels of hierarchical facet values e.g. this is to get entries published in 2020 only, e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/europepmc?query=tp53&facetcount=5&facetcount=5&facets=publication_date:2020](https://www.ebi.ac.uk/ebisearch/ws/rest/europepmc?query=tp53&facetcount=5&facetcount=5&facets=publication_date:2020) 

  

It is possible to apply more sophisticated filter e.g. finding publications published in July 2020:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/europepmc?query=tp53&facetcount=5&facetcount=5&facets=publication_date:2020/07](https://www.ebi.ac.uk/ebisearch/ws/rest/europepmc?query=tp53&facetcount=5&facetcount=5&facets=publication_date:2020/07) 

### Try example

Try your own example here:

General information

|Summary|Description|Method|URL|
|---|---|---|---|
|Domain search|If a query parameter is specified, it will return search results. Otherwise, return meta-data of the specified domain|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}|

Response content type

application/xmlapplication/jsontext/xmltext/csvtext/tab-separated-valuestext/plain

Parameters

|Parameter name|Parameter value|Description|Data type|
|---|---|---|---|
|domain||A single domain identifier e.g. uniprot|string|
|query||Query string e.g. tp53|string|
|filter||Filter queries (non-scoring queries that do not affect relevance) e.g. TAXONOMY:9606|array|
|size||The number of entries to retrieve. limit 10,000 for list type and 100 for other types|string|
|start||The index of the first entry in the results. Limit 100,000|string|
|sortfield||A single field identifier to sort on. Not allowed to use with 'sort' parameter|string|
|order||Whether to sort in ascending/descending order. Should come along with 'sortfield' parameter and not allowed to use with 'sort' parameter|string|
|sort||Comma separated values of sorting criteria. (field_id:order, e.g. boost:descending,length:descending). Should not be used in conjunction with any of 'sortfield' and 'order' parameters|string|
|sortignorenull||Ignore null values at sort time. If true, null values will always appear on the end|string|
|fields||Comma separated values of field identifiers to retrieve|string|
|fieldurl||Whether field links are included. The returned links mean direct URLs to the data entries in the original portals. Valid with XML/JSON only|string|
|viewurl||Whether other view links on an entry are included. Valid with XML/JSON only|string|
|facetfields||Comma separated values of field identifiers associated with facets to retrieve. In case of hierarchical facet, the value for the field can be a path where the nodes are separated by a '/'. i.e.: taxonomy_lineage/1/10239/35268 (taxonomy_lineage is the name of the hierarchical facet and nodes are possible values of the facet). Valid with XML/JSON only|string|
|facetcount||The number of facet values to retrieve. In case of hierarchical facet, the facet count limit the number of children retrieved in a single level. Valid with XML/JSON only.|string|
|facets||A comma separated list of selected facet values|string|
|feedtitle||RSS feed title and required when a selected format parameter is 'rss'|string|
|feedmaxdays||The number of days for time window. always used with 'feedmasdaysfield' parameter. valid when format is 'rss'|string|
|feedmaxdaysfield||A date type field to set time window. always used with 'feedmaxdays' parameter. valid when format is 'rss'|string|
|entryattrs||Comma separated values of additional entry attributes. Valid with XML/JSON only.|string|
|hlfields||Comma separated values of field identifiers to apply highlighting. Valid with XML/JSON only|string|
|hlpretag||A string appearing before a highlighted term. Valid with XML/JSON only.|string|
|hlposttag||A string appearing after a highlighted term. Valid with XML/JSON only.|string|
|format||Response format|string|
|searchposition||The search position from which to start the next request. Set to 0 to start a new bulk search.|string|

## Retrieving individual entries

### Introduction

This request for an entry consists of a domain identifier (e.g. _uniprot_ ) and the entry's identifier or accession number, e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN) 

  

By default, a response in XML format is returned. Depending on the _format_ parameter, a response in a different format can be returned. Here are some examples:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?format=xml](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?format=xml) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?format=json](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?format=json) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?format=tsv](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?format=tsv) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?format=csv](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?format=csv) 

  

The entry's identifier and the domain identifier it belongs to are returned, by default. It is possible to retrieve other fields' values using the _fields_ parameter, e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?fields=gene_primary_name,length](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?fields=gene_primary_name,length) 

Not all fields are retrievable. Which fields are retrievable in e.g. _UniProtKB_ can be found [here](https://www.ebi.ac.uk/ebisearch/metadata.ebi?db=uniprot).

  

The link where the entry's detail can be found can be obtained using the _fieldurl_ parameter e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?fieldurl=true](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?fieldurl=true) 

  

There are additional links in some domains e.g. the uniprot entry in FASTA format:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?viewurl=true](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN?viewdurl=true) 

  

It is possible to retrieve multiple entries from a single request with a comma separated list of entry identifiers (or accession numbers):

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/WAP_RAT,WAP_MOUSE](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/WAP_RAT,WAP_MOUSE) 

### Try example

Try your own example here:

General information

|Summary|Description|Method|URL|
|---|---|---|---|
|Entry retrieval|It returns entry information associated with entry identifiers provided|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}/entry/{entryids}|

Response content type

application/xmlapplication/jsontext/csvtext/tab-separated-valuestext/plain

Parameters

|Parameter name|Parameter value|Description|Data type|
|---|---|---|---|
|domain||A single domain identifier e.g. uniprot|string|
|entryids||Comma separated values of entry identifiers (max 100) e.g. P53_HUMAN|string|
|fields||Comma separated values of field identifiers to retrieve e.g. descRecName|string|
|fieldurl||Whether field links are included. The returned links mean direct URLs to the data entries in original portals. Valid with XML/JSON only|string|
|viewurl||Whether other view links on an entry are included. Valid with XML/JSON only|string|
|format||Response format|string|

## Cross reference searching

### Finding domains referred by a domain

This request requires a domain identifier in order to return a list of other domains referred by or referring to a domain e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/xref](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/xref) 

  

By default, a response in XML format is returned. Depending on the _format_ parameter, a response in a different format can be returned. Here are some examples:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/xref?format=xml](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/xref?format=xml) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/xref?format=json](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/xref?format=json) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/xref?format=tsv](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/xref?format=tsv) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/xref?format=csv](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/xref?format=csv) 

More information about formats can be found [here](https://www.ebi.ac.uk/apidoc.ebi#response-formats).

### Finding domains referred by an entry

A list of domains referred by an entry can be obtained using the entry's identifier and the domain identifer where the entry belongs to e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref) 

  

By default, a response in XML format is returned. Depending on the _format_ parameter, a response in a different format can be returned. Here are some examples:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref?format=xml](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref?format=xml) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref?format=json](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref?format=json) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref?format=tsv](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref?format=tsv) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref?format=csv](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref?format=csv) 

### Cross reference searching

You can find entries referred by or referring to an entry e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc) 

  

By default, a response in XML format is returned. Depending on the _format_ parameter, a response in a different format can be returned. Here are some examples:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?format=xml](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?format=xml) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?format=json](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?format=json) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?format=tsv](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?format=tsv) 
 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?format=csv](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?format=csv) 

  

The entry's identifier and its domain identifier are returned, by default. It is possible to retrieve other fields' values using the _fields_ parameter, e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?fields=name](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?fields=name) 

  

The link where the entry's detail can be found can be obtained using the _fieldurl_ parameter e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?fieldurl=true](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?fieldurl=true) 

  

There are additional links in some domains e.g. the uniprot entry in FASTA format:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?viewurl=true](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?viewdurl=true) 

  

A single request can run with more than one entry e.g. :

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN,P53_RAT/xref/europepmc](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN,P53_RAT/xref/europepmc) 

  

##### Pagination

By default a returned result has the first 15 entries if the number of hits is greater than 15. The both requests below return a same response.

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc) 

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?size=15](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?size=15) 

The _size_ parameter can't take a number greater than 100 for most response formats. However, greater numbers can be acceptable for certain formats. Please refer to [here](https://www.ebi.ac.uk/apidoc.ebi#response-formats).

  

It is possible to get the number of hits only by specifying the _size_ parameter is 0. The actual number can be obtained by parsing the response body or reading the value of the HTTP header: _x-ebi-search-total-results_.

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?size=0](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?size=0) 

  

To implement pagination, the number of entries per page is needed e.g. the following example gets the first 10 entries:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?size=10](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?size=10) 

  

The next 10 entries can be gained by the _start_ parameter, which indicating the index of the first entry in the results e.g.:

 [https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?size=10&start=10](https://www.ebi.ac.uk/ebisearch/ws/rest/uniprot/entry/P53_HUMAN/xref/europepmc?size=10&start=10) 

More than 1,000,000 entries cannot be retrievable at the moment.

  

##### Facets

It is possible to get facets associated with cross reference searching result. [Here](https://www.ebi.ac.uk/ebisearch/documentation/rest-api/xref/api.doc/facet) is the documentation for that.

### Try example

Try your own example here:

- Cross-reference search   /{domain}/entry/{entryids}/xref/{targetdomainid}
- Finding domains referred by an entry   /{domain}/entry/{entryid}/xref
    
    General information
    
    |Summary|Description|Method|URL|
    |---|---|---|---|
    |Finding domains referred by an entry|It returns a list of domains referred by an entry|GET|//www.ebi.ac.uk/ebisearch/ws/rest/{domain}/entry/{entryid}/xref|
    
    Response content type
    
    application/xmlapplication/jsontext/csvtext/tab-separated-valuestext/plain
    
    Parameters
    
    |Parameter name|Parameter value|Description|Data type|
    |---|---|---|---|
    |domain||A single domain identifier e.g. uniprot|string|
    |entryid||A single entry identifier e.g. P53_HUMAN|string|
    |format||Response format|string|