# Data directory

`orcs/` contains the saved reference publication/screen catalogs and completed
metadata enrichment evidence. It is not an enabled ORCS collection/search
workflow. `identifiers/` preserves shared resource-ID allocations; publication
identities have a separate registry within `orcs/`.

`icraft/` is isolated external validation material, not a production query input.
`cellosaurus/` retains reference annotations useful for interpreting saved native
metadata. Future rule generation and evaluation require their own defined scope.

`raw/` and `interim/`, where used, are local workspaces ignored by Git. Preserve
native identities and provenance; keep unknown or conflicting values explicit.
Saved file listings describe experimental assets but do not download their
contents or establish qualifying-screen attribution.
