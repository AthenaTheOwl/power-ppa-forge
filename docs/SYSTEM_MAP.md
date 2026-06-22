# System Map

## Artifact flow

```text
scenarios/v0_1gw_3offtakers.json
        |
        v
python -m power_ppa_forge validate
        |
        v
python -m power_ppa_forge simulate --out runs/v0_baseline
        |
        +--> runs/v0_baseline/allocation.json
        +--> runs/v0_baseline/payments.json
        +--> runs/v0_baseline/receipts.json
        |
        v
python -m power_ppa_forge capital-impact --run runs/v0_baseline
        |
        v
reports/capital_impact.md
```

## Boundaries

- `scenarios/` contains typed notional inputs.
- `power_ppa_forge/models.py` validates scenario shape and feasibility.
- `power_ppa_forge/simulator.py` computes allocation, payments, leakage receipts, and report text.
- `scripts/` contains repository gates that can run without network access.
- `mechanism/` describes the mechanism and the leakage disclosure surface.
- `paper/` is the customer-facing prose surface for the mechanism claim.

## Data contract

The simulator reads one scenario JSON file and writes three run
artifacts:

- `allocation.json` records the selected capacity allocation and score.
- `payments.json` records bidder-level Vickrey-style externality payments.
- `receipts.json` records the intentionally small disclosure each bidder receives.

Receipts must not contain bid prices, load-shape vectors, or
counterfactual allocation tables.
