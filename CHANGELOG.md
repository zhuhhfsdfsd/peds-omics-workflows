# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Validate that MR variant identifiers and single-cell identifiers are non-empty and unique.
- Add issue templates for reproducibility reports and workflow proposals that require safe, shareable examples.
- Add optional machine-readable manifests with input hashes, workflow parameters, and software versions.
- Add an R helper and guide for exporting already harmonised `TwoSampleMR`-style data to the narrow MR CSV schema.
- Add a dependency-free pseudobulk aggregation command with synthetic immune-cell count data and documentation.

### Changed

- Normalise blank single-cell annotations to `unassigned`.

## [0.1.0] - 2026-08-14

### Added

- Dependency-free command-line workflows for an educational IVW MR summary and single-cell QC summary.
- Synthetic example data, unit tests, GitHub Actions CI, contribution guidance, and an architecture decision record.
