# Contributing

Please submit small, testable changes with clear metric definitions and synthetic tests. Keep clinical data, private paths, patient identifiers, checkpoints and credentials out of issues and pull requests. Do not substitute illustrative outputs for experiment results.

Changes to published aggregates need provenance and an explanation of affected claims. Preserve adverse findings and explicit missing-data denominators. A new experiment should have a separate versioned result artifact rather than silently replacing the released snapshot.

Run `python -m unittest discover -s tests -v` and `python scripts/validate_public_results.py` before submitting code changes. Figures can be regenerated with `python scripts/render_results.py`.
