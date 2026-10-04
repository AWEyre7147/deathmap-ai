# Data directory

- `raw/` is for immutable source downloads and is ignored by Git.
- `interim/` is for reproducible intermediate transformations and is ignored by Git.
- `curated/` is for small, manually reviewed benchmark artifacts suitable for
  version control when they contain no restricted data.

Every curated artifact should document its source identifiers, retrieval date,
adjudication status, and schema version. Do not place credentials, controlled
data, or large sequencing files in this repository.

An ORCS run writes both the immutable native JSON response and a flat
`orcs-screen-metadata.csv` in its ignored run directory. The CSV is an
inspection view of descriptive screen metadata, not a download of screen result
rows. It may include counts and analysis descriptions but must not include gene
scores, guide counts, matrices, or molecular measurements.
