# First GitHub publication preparation

## [GH1] Release scope

The completed CRISPR pilot is the primary entry point. Include implementation, offline tests, search profiles, authoritative specifications, curated vocabularies, preserved workbook templates and saved public-resource metadata/provenance. Keep generated runs, local validation material, installed dependencies, editor state, duplicate backups and temporary inspection/authoring files local via `.gitignore`. No files are deleted by this policy.

This boundary keeps the source repository reproducible without uploading machine-specific runtime installations. For example, `scripts/node_modules/` is excluded while the workbook exporter and its runtime requirements are documented.

## [GH2] Remaining owner choices

- GitHub repository name: `deathmap-ai`; destination account and visibility remain to be selected.
- Owner-selected code license: MIT. Third-party metadata is governed separately by upstream terms.
- Whether to distribute the completed workbook/run as a separate release asset. Generated runs currently remain excluded from Git.

Historical specifications and provenance receipts intentionally contain local Windows paths. The active runner uses repository-relative inputs, but archive locations and prior session receipts remain machine-specific. Review these before making the repository public.

The Excel exporter requires the Codex artifact-tool runtime. Python discovery and JSON generation can run from the documented local Python setup; fully independent Excel export remains a portability task.

## [GH3] Publication sequence

Review the release-readiness report and owner choices, make the first commit, create/select the GitHub repository, configure its remote, then push. This preparation step does not create a commit, remote or GitHub repository. It also does not alter frozen search outputs or add enrichment.

Automated secret scanning is a check, not a guarantee. Preserve source acknowledgments and review upstream metadata terms before broader redistribution. The root MIT license records the owner's code-license decision; it does not relicense source metadata.

## [GH4] Verification result

All 177 offline tests passed both in the working repository and in a temporary copy containing only Git-included release files. No oversized file or credential-pattern match was found in the scanned source candidate set. Dependency installations remain excluded. See [release readiness report](../logs/github-release-readiness-20261004.json) for counts, machine-specific path inventory and pending decisions.
