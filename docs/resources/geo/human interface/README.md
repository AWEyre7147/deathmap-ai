# Designing searches: human interface examples

These are small planning examples, not approved searches or new retrieval results. They use the saved interface evidence. No external requests were made to create them.

## [HI-1] Start with the pilot target
Human or mouse AND an approved CRISPR screening modality AND (cancer-derived OR immune-lineage OR organoid model). Normal organoids and non-immune readouts remain within the final ORCS pilot target. See the [original profile](../../../../searches/orcs/orcs-crispr-biological-classes-pilot-v01/profile.json).

Do not turn this into a sentence to send to a search engine. Fill in three separate parts:

1. **Filters:** verified fields that restrict the returned records. Put organism here if supported; do not also add human/mouse words to general text. State each field's meaning and annotation limitations.
2. **Text criteria:** only requirements without an adequate structured field. Keep them explicit and justified. An unverified screen filter is not an alternative to text; it is an unresolved capability.
3. **Metadata decisions:** properties the retrieval interface cannot reliably establish. State what evidence is needed and what happens when it is absent.

## [HI-2] The three labels you need
| Label | Meaning | What to do |
|---|---|---|
| Available filter | Supported structured criterion at the selected interface | Set it before choosing text terms |
| Possible filter | A returned field/facet or documented feature without sufficient evidence for this source | Leave unset until verified; no expensive parser exploration by default |
| Later metadata decision | No adequate filter established | Decide whether to inspect a small sample, defer, or choose another resource |

Native GEO [ORGN] is a filter although it is written inside a term expression. OmicsDI repository/omics_type expressions also live inside a query parameter. Classify by the field being constrained, not by whether the API calls it a query.

## [HI-3] Small examples
- [GEO planning sheet](GEO%20planning%20example.md): one worked example with filters separated from text and review.
- [Small metadata comparison](Small%20metadata%20comparison.md): existing records showing why returned properties matter.

The interface must always be named: native GEO and OmicsDI GEO are different choices. Reading these examples does not select a native discovery adapter.

## [HI-4] You do not need the whole database
A whole-database document would be difficult to read and is unnecessary for designing the first search. It is not impossible technically, but we should not retrieve it for this planning task.

Start with the filter menu, a few existing metadata examples, and a blank planning sheet. If a specific decision remains unresolved, propose one small, capped sample to answer it. Inspect record type, model evidence, screening design and missing fields. This is a design aid, not a coverage estimate. Do not keep expanding samples without a stated question.

The owner can write desired filter values and circle missing criteria. ChatGPT can then translate supported choices into exact requests and identify only the gaps affecting the result. No Perplexity research is required just to fill this sheet.

Learning checkpoint: filters can narrow candidate intake, but only source fields that represent the intended scientific property can replace ORCS's rules.

- [Complete saved-schema GEO field menu](GEO%20filter%20menu.md), with separate value notes for categorical/controlled fields.
