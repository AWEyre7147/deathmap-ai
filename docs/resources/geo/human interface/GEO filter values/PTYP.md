# GEO Platform Technology Type: values (PTYP)

Filter kind: Fixed choice. Interface: native GEO Entrez gds, not OmicsDI. Reviewed 2026-10-06 using saved schema, supplied observations and official search documentation.

## Values currently supported by evidence
| What you can pass | Meaning | Evidence status |
|---|---|---|
| `high throughput sequencing` | Platform technology | Documented example; not freshly tested |

This is **not a complete current value list**. The saved schema reports 17 indexed terms. Do not assume these are mutually exclusive or all apply to Series.

## How to obtain the remaining values
In [GEO DataSets Advanced Search](https://www.ncbi.nlm.nih.gov/gds/advanced), select the field and use **Show Index**, where available, to inspect indexed terms. This route is described by official guidance but was not operated in this session. Supply the displayed/exported terms to extend this note. EInfo supplies field definitions and term counts, not value lists.

## Example choice
`"high throughput sequencing"[PTYP]`

A value observed in a summary is not automatically a verified server filter. Empty results do not prove biological absence. Do not add restrictions simply because a value menu exists.

Sources: [saved EInfo schema](../../progress/perplexity-01/evidence/native-geo-einfo.body), [saved documentation extraction](../../progress/perplexity-01/evidence/official-geo-query-documentation.json), [official GEO search guide](https://www.ncbi.nlm.nih.gov/geo/info/qqtutorial.html). Documentation examples are distinct from saved executed probes; no new filter requests performed here.
