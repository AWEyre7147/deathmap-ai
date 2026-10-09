---
title: Code Commenting Standard
type: primary-workflow
status: adopted
---

# Code Commenting Standard

This is a living standard. The project owner may edit it as their preferred code
review style develops. This note consolidates the existing standard with the
owner's Repository Commenting Structure. Apply it to generated or substantially
modified code within the authorized task scope; it does not authorize a
repository-wide commenting pass. Use language-appropriate equivalents outside
Python. Prefer clear names and focused functions over compensating comments.

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

Identify whether the module is a command-line entry point or an imported helper,
and describe important side effects. Keep long usage guides and field dictionaries
in linked project documentation rather than duplicating them throughout code.

## [CC3] Functions and classes

Public functions and classes should document:

- their purpose;
- parameters and returned values;
- expected identifier or record formats;
- important exceptions or failure states;
- side effects such as network access, caching, or file creation.

Private helpers need shorter documentation when their name and behavior are not
self-explanatory.

For public Python functions, use NumPy-style docstrings: a one-sentence purpose,
then Parameters, Returns and Raises where applicable. Public class documentation
should describe construction and important state using the same conventions.
Add Notes for scientific assumptions or subtle behavior; use Examples only when
they clarify usage. Do not add empty sections, invent exceptions, or claim
guarantees that the implementation does not provide. Trivial private helpers do
not need boilerplate.

Use type hints where practical and compatible with the supported Python version.
Describe units, identifier namespaces, accepted values, missing-value behavior,
mutation and return semantics where relevant. Types do not replace scientific
definitions.

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

Cite a stable policy or source when a scientific rule depends on it. Explain
determinism, aggregation, transaction/recovery choices and format constraints
when they are nonobvious. Format validation is not experimental validation.
Correct stale comments within the changed scope. Keep credentials, personal
paths and conversational history out of source comments.

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

NumPy-style public-function docstrings are now adopted; further customization
should be explicit rather than leaving the docstring format undecided.

## [CC10] Major sections

For genuine major sections in longer Python scripts, use this exact form:

```python
# =============================================================================
# Source validation
# =============================================================================
```

Use short descriptive titles. Do not surround every function or divide short
functions with decorative headers.

## [CC11] Scope and verification boundaries

Follow [Codex Handoff Rules](../AI-agent-workflow/codex-handoff-rules.md).
Comments-only work preserves behavior, public interfaces, dependencies and
accepted scientific policies. It does not authorize unrelated refactoring,
new functionality or new test infrastructure.

Before editing code, check the scoped modules for tracked source-file hashes and
any regeneration requirement. Report that consequence in the handoff assessment.
Comments-only work defaults to zero full rebuild/export passes. A conflicting
requirement triggers a scoped checkpoint; never bypass checks, silently launch a
rebuild or hand-edit provenance hashes to make stale validation appear current.

Review documentation against implementation and use existing lightweight syntax
or documentation checks where applicable. Full suites and rebuilds must be part
of the accepted scope or separately authorized. Finish the named modules, report
remaining documentation gaps and review markers, then stop.

## [CC12] Public-function example

```python
def same_publication_pmid(left_pmid: str, right_pmid: str) -> bool:
    
    """
    Check equality of two supplied PubMed identifiers.

    Parameters
    ----------
    left_pmid : str
        First PMID, already validated and normalized by the caller.
    right_pmid : str
        Second PMID, already validated and normalized by the caller.

    Returns
    -------
    bool
        Whether the supplied identifiers are equal.

    Notes
    -----
    This compares identifiers only. It does not retrieve publication metadata
    or establish that associated datasets contain the same CRISPR screen.
    """
    
    return left_pmid == right_pmid
```

This illustrates documentation style, not a required pipeline function.
