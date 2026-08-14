# Contributing

Thank you for helping make pediatric omics workflows more reproducible.

## Before contributing

1. Open an issue to discuss non-trivial features or workflow changes.
2. Never upload identifiable patient data, restricted summary statistics, access tokens, or institutional credentials.
3. Keep research assumptions visible: document input requirements, defaults, and limitations.

## Development

```bash
python -m venv .venv
# Activate it, then:
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Pull requests

- Add or update tests for changed behavior.
- Use synthetic or openly licensed data in examples.
- Keep modules dependency-light unless a clear reproducibility benefit is documented in an ADR.
- Describe validation performed and any study-specific assumptions in the pull request.

## Code of conduct

Be respectful, constructive, and mindful that contributors may work across clinical, wet-lab, and computational disciplines.
