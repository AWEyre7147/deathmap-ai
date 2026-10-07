# Code Commenting Standard

This is a living standard. The project owner may edit it as their preferred code
review style develops.

## [CC1] Purpose

Comments should make the code understandable to a researcher who knows the
scientific problem but may still be learning the software techniques involved.
The goal is to explain intent, assumptions, and consequences without obscuring
the executable code.

## [CC2] File-level context

Each nontrivial source file should begin with a short module docstring or header
that explains:

- what responsibility the file owns;
- what important inputs and outputs cross its boundary;
- which scientific or data-integrity assumptions matter;
- what the file intentionally does not do, when that boundary is easy to mistake.

## [CC3] Functions and classes

Public functions and classes should document:

- their purpose;
- parameters and returned values;
- expected identifier or record formats;
- important exceptions or failure states;
- side effects such as network access, caching, or file creation.

Private helpers need shorter documentation when their name and behavior are not
self-explanatory.

## [CC4] Inline comments

Use inline comments for reasoning that the code alone cannot express clearly,
especially:

- why a filtering or matching rule is scientifically justified;
- why one stable identifier takes precedence over another;
- why missing, ambiguous, or conflicting evidence is retained;
- why a workaround or non-obvious library behavior is necessary;
- why a performance optimization does not change scientific meaning.

Place the comment immediately before the relevant block. Avoid narrating obvious
syntax or repeating a descriptive variable name.

## [CC5] Evidence transformations

For normalization, deduplication, and entity-linking code, comments must identify:

- the source and destination representation;
- which fields are preserved, derived, normalized, or discarded;
- the rule used to resolve collisions;
- how uncertainty and one-to-many relationships are handled.

## [CC6] Learning checkpoints

When code introduces an architectural concept that may not be familiar to the
project owner, flag it in the implementation summary as:

`Learning checkpoint: <concept>`

Explain the problem it solves, why it was chosen, its main tradeoffs, likely
failure modes, and what will depend on it. Do not turn source comments into a
software tutorial when a separate explanation would be clearer.

## [CC7] Review markers

Temporary review markers must use one of these forms and must not remain silently
in completed work:

- `TODO(owner):` a defined follow-up with a clear owner or decision needed.
- `FIXME:` known incorrect behavior that prevents completion.
- `ASSUMPTION:` a consequential assumption awaiting confirmation.
- `PROVENANCE:` a note about evidence origin or attribution.

The end-of-session report must list any markers intentionally left in the code.

## [CC8] Examples

Helpful:

```python
# Preserve every accession associated with the paper. Publication-level linkage
# alone does not establish which accession contains the qualifying CRISPR screen.
candidate_accessions = collect_linked_accessions(publication)
```

Not helpful:

```python
# Loop through accessions.
for accession in accessions:
    ...
```

## [CC9] Owner customization checklist

The project owner may refine:

- preferred docstring format;
- desired detail for parameter and return-value documentation;
- whether examples are required for public functions;
- terminology that should be defined for non-programmers;
- maximum acceptable comment density;
- rules for notebooks, command-line tools, and configuration files.
