# Spec 0002 acceptance

The v0.1 release is accepted when:

- `python -m power_ppa_forge validate` exits 0 with no flags.
- `python -m pytest -q` passes.
- `reports/capital_impact.jsonl` exists and points to the markdown report.
