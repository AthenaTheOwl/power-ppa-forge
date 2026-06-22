# Spec 0002 requirements

## R-PPF-002-001 - default validation

`python -m power_ppa_forge validate` must run with no flags and validate the
canonical notional scenario.

## R-PPF-002-002 - report artifact

The v0.1 run must publish one capital-impact markdown report and one JSONL
summary row under `reports/`.

## R-PPF-002-003 - bounded disclosure

Receipts must avoid bid prices, load-shape vectors, and counterfactual
allocation tables.
