# orcs-crispr-biological-classes-pilot-v01

This profile is supported by the offline ORCS runner. The biological-classes profile is the current scientific baseline; categorical profiles retain their own explicit rules. Inspect `profile.json` for the exact filter contract.

After installing the project, run from the repository root:

```powershell
deathmap-search-orcs --profile searches/orcs/orcs-crispr-biological-classes-pilot-v01/profile.json
```

The command searches saved ORCS metadata, applies saved Cellosaurus interpretation, preserves canonical JSON/evidence, and exports `workbook-authored.xlsx` using the main template. It performs no live source refresh or experimental download. Existing run directories and reviewed workbooks are refused.

See [curated outputs](../../../outputs/orcs/README.md) and [current scope](../../../docs/specifications/work-session-next-stage.md). Publication companions remain distinct from direct candidates; repository attribution is deferred.
