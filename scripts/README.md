# Maintained library and verification scripts

- `library_enrichment.mjs`: publication-driven automatic/assisted collection.
- `library_browser.mjs`: browser access and observed response extraction.
- `library_routes.mjs`: native-service selection and bounded route fallbacks.
- `library_run_state.mjs`: durable attempt selection, cooldowns and content merge.
- `library_access.mjs`: browser loading, privacy, timing and atomic checkpoints.
- `library_delivery.mjs`: publisher host/file boundaries and institutional DOI entry.
- `verify_enrichment_template.py`: read-only ENA template/cell verification.

Python metadata collectors live in `src/deathmap_ai`. The library's native Nature
listing adapter is `library_nature.py` within that package; it is not a separate
publisher enrichment CLI. ORCS search/collection, standalone publisher APIs and
old OSU probes/batch controllers are retired. Their shared library functionality
was preserved in the modules above, without a hidden pilot execution path.

The current institutional adapter still requires OSU authentication and proxy
routes. This cleanup does not add support for another institution. Existing
completed outputs and historical checkpoint bindings are preserved, not migrated;
changed parsing rules require a new retrieval run. No live retrieval is needed
for verification. See the enrichment guides for supported commands.
