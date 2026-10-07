# Supported ORCS searches

The biological-classes pilot is the current scientific baseline. All three supplied profiles remain supported by the offline runner:

- `orcs-crispr-biological-classes-pilot-v01/profile.json`
- `cancer-cell-crispr-knockout-v01/profile.json`
- `cancer-cell-crispr-knockout-v02/profile.json`

Run `deathmap-search-orcs --profile searches/orcs/<folder>/profile.json` from the repository root after installation. Saved ORCS/Cellosaurus metadata is read without source refresh. Each run creates a new output directory. The search command automatically exports a portable review workbook using the approved main template; a separate export command also remains available.

[Curated ORCS outputs](../../outputs/orcs/README.md) retain the latest generated workbooks and canonical metadata. Older reviewed workbooks are preserved in the external archive. Publication companions remain distinct from direct-rule candidates; external repository enrichment is deferred.
