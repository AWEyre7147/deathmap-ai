# Persistent enrichment identifiers

`supplemental-index-registry.json` is required for stable resource indices across
metadata and library enrichment runs. Its historical filename does not mean it
is a temporary supplemental-file inventory. Native accessions remain separate.

Keep the registry across cohorts and reruns: existing identities retain their
indices; new identities append without renumbering. Retired namespace allocations
remain reserved for traceability and must not be reassigned. They do not enable
a retired collector. Do not regenerate or prune this file during cleanup.

Publication identity has its separate crosswalk in
`data/orcs/enrichment-publication-registry.json`. Neither registry is a cache.
Collectors can use an isolated resource registry with `--index-registry` where
supported; do not substitute an empty registry for the shared production one.
