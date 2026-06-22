# Spec 0002 Design Ledger

Status: implemented in v0.1

## Scope

Spec 0002 turns the foundation scaffold into a runnable data-report
repository. It does not revise the 0001 foundation files.

## Decisions

- Use `scenarios/v0_1gw_3offtakers.json` as the canonical fixture for
  validation, simulation, and report generation.
- Use a root-level Python package so `python -m power_ppa_forge validate`
  works from a checkout before an editable install.
- Keep simulator dependencies in the Python standard library for v0.1.
- Publish run artifacts as JSON and the capital-impact artifact as
  Markdown.
- Treat all values in the scenario and report as notional.

## Requirements covered

- Product brief exists at `PRODUCT_BRIEF.md`.
- System map exists at `docs/SYSTEM_MAP.md`.
- Status file uses the required section headings.
- CLI validates the canonical scenario with no flags.
- Tests cover the default CLI action, allocation feasibility, and
  leakage-receipt minimization.

## Follow-up requirements

- Add calibrated empirical scenarios only after source review.
- Add a cryptographic receipt implementation after the disclosure
  surface stops changing.
- Add formal proof material for the leakage bound.
