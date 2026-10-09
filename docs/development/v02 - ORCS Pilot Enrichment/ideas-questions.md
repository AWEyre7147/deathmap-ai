# v0.2 ideas and open questions

- **PubMed enrichment output selection.** Source: repository-enrichment
  conversation, owner request following F1. Use the one-entry inspection, then
  a separately scoped 10-entry sample, to assess which publication fields,
  MeSH descriptors/qualifiers and database links merit full-ORCS outputs.
  Linked Gene, GEO Profiles, literature and repository IDs have different
  meanings and scales. Native repository hierarchy recovery for citation-missing
  children remains unresolved; a publication link never establishes screen
  attribution. ICRAFT–ORCS MeSH comparison remains exploratory and requires an
  identified validation reference separate from production enrichment.

These entries are unapproved and do not change implementation scope.

- **Excel compatibility-prefix validation.** Source: owner Excel recovery log
  after PubMed template population, reply N. The run-local XML serializer
  dropped declarations used only by mc:Ignorable; ordinary XML parsing and
  workbook previews failed to detect the Excel defect. The repaired copy
  preserves original template envelopes, validates prefix scope and was opened
  in Excel 16.0. Future production export needs this compatibility check;
  do not reuse the original population helper without its repair step. No
  production adapter or broader export redesign is authorized by this repair.

- **Descriptor-centered MeSH review view.** Source: repository-enrichment
  conversation, owner question following J4, reply K. Consider one row per
  observed Descriptor UI, with descriptor name, unique publication count and
  associated PMIDs. Preserve PMID-specific qualifiers and major-topic flags in
  canonical association records; a descriptor-only aggregation cannot represent
  these without retaining their publication context. Do not populate the whole
  MeSH vocabulary or adopt a final grouped schema before review.

- **Deferred SRA-linked metadata inspection.** Source: repository-enrichment
  conversation, owner observations following I2 and reply J. Later examine
  which descriptive metadata is available for SRA Experiment (SRX), Study
  (SRP), Sample (SRS) and BioSample (SAMN) accessions. Retain accession
  relationships now without expanding to sample-level interpretation or raw
  experimental files. A separate bounded task must define depth and purpose.
- **Native hierarchy and publication-link gaps.** Same source. GSE72841 /
  200072841 is absent from the saved direct PubMed-to-GEO results. The readable
  GEO summary view does not expose SuperSeries/SubSeries relationships. Assess
  native metadata and hierarchy routes before claiming this hierarchy is
  unavailable or that direct PMID linkage recovers all associated series.
- **Repository data-type filters may exclude screen deposits.** Same source.
  Owner observed the CRISPR-screen BioProject classified as Other, with linked
  Transcriptome records describing related work. This example motivates
  identifier-led enrichment without a Transcriptome-only gate. It does not
  establish historical OmicsDI behavior, classification equivalence across
  resources, or the role of every linked dataset without further evidence.

- **Possible complete-ORCS grouping.** Source: owner response to [A146].
  Consider grouping all approximately 2,200 cached ORCS screens. Revisit after
  enrichment and a small varied grouping pilot reveal evidence needs and effort.
  No whole-catalog annotation is authorized.
- **Specification organization.** Source: owner reorganization message.
  Review the draft in `docs/workflow/global/specifications/specification-structure.md`
  before restructuring authority or moving completed handoffs out of active use.
- **User notation.** Explore/Remember/Decide/Do is liked but not adopted.
  Revisit once the conversation instructions and new-session handoff are settled.
- **Resource contracts.** Which repositories best enrich the ORCS results, what
  metadata depth is needed, and what evidence supports screen-dataset links?
  Resolve using the owner's repository documentation before implementing adapters.

- **Future ligand–receptor annotation contract.** Long-term direction accepted in reply H; concrete database version, schema, identifier mapping, normalization/analysis policies and annotation evidence remain unresolved. Do not invent these requirements during metadata enrichment.
