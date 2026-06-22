# Product Brief

## Product

Power PPA Forge is a small data-report repository for testing a
sealed-bid, multi-buyer PPA coordination mechanism on a notional
long-duration generation asset.

## User

The first user is a reviewer who wants to inspect the mechanism,
validate the canonical scenario, rerun the simulator, and compare the
checked-in report with regenerated artifacts.

## First user action

`python -m power_ppa_forge validate`

The command uses `scenarios/v0_1gw_3offtakers.json` by default and exits
with a typed validation error when the fixture is malformed.

## v0.1 artifact

- Product brief: `PRODUCT_BRIEF.md`
- System map: `docs/SYSTEM_MAP.md`
- Design ledger: `specs/0002-design/ledger.md`
- Canonical scenario: `scenarios/v0_1gw_3offtakers.json`
- Mechanism note: `mechanism/MECHANISM-v0.md`
- CLI package: `power_ppa_forge/`
- Tests: `tests/`
- Checked-in report: `reports/capital_impact.md`

## Non-goals

- Production-deployment cryptography.
- Real hyperscaler load-profile data.
- Real project-finance terms.
- Settlement or payment rails.
