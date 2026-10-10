# Contributing

Contributions are welcome after maintainer review.

## Local validation

Use Python and run:

```bash
python -m src.fr0 validate
python -m src.fr0 lock
python -m unittest discover -s tests -v
```

The lock command requires V0–V8 validation to pass. Do not submit changes that weaken validation, alter generated digests without explanation, or introduce secrets or personal data.

## Change process

1. Open an issue describing the change and its motivation.
2. Develop changes in a separate branch.
3. Add or update tests and documentation.
4. Open a pull request explaining compatibility, security implications, and validation results.
5. Wait for maintainer review; do not assume approval or automatic merging.

By contributing, you agree your contributions may be distributed under the repository's MIT license, subject to the rights you hold in those contributions.
