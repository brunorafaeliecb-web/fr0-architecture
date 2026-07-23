# FR0 Implementation Pack — Bootstrap V0–V8

Executable bootstrap for `AB-FR0-001`.

## Scope

- Normative JSON schemas for the baseline and 12 registries.
- Materialized FR-0 registry data.
- RFC 8785-compatible canonicalization for this baseline profile (integers only; floats rejected).
- SHA-256 digests and deterministic `AB-FR0-001.lock.json`.
- Architecture validation stages V0–V8.
- Automated tests and machine-readable validation report.

## Run

```bash
python -m src.fr0 validate
python -m src.fr0 lock
python -m unittest discover -s tests -v
```

The lock command runs validation first and refuses to generate a lock when V0–V8 fails.
