# ADR-001: Start with a dependency-free, transparent baseline

## Status

Accepted — 2026-08-14

## Context

The repository needs to be immediately runnable by clinical researchers on common systems and easy to inspect before it grows into a larger multi-language workflow. Full MR and single-cell analysis ecosystems are powerful but introduce substantial environment, version, and data-assumption complexity.

## Decision

Version 0.1.0 uses Python's standard library for two deliberately narrow workflows: an exploratory delta-method IVW MR calculation for pre-harmonised instruments, and a single-cell QC metadata summary. Synthetic CSV examples and JSON outputs make every input/output visible.

## Alternatives considered

### Begin with a full R pipeline

This would expose standard research tools earlier, but package versioning and installation barriers would make first-time use and CI less reliable. It remains a planned interoperability target.

### Begin with a notebook collection

Notebooks are convenient for exploration but can obscure execution order and make automated testing harder. The project instead starts with testable command-line modules; notebooks can later wrap stable functions.

## Consequences

- The first release is intentionally limited and must not be described as a complete MR or single-cell pipeline.
- New dependencies require documented scientific and reproducibility justification.
- Users receive a fast, testable scaffold that can serve as a basis for rigorous study-specific workflows.
