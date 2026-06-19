# Requirements — Foundation

Brand prefix: PPF (power-ppa-forge).

## Mechanism requirements

- **R-PPF-001** — The repo SHALL publish
  `mechanism/MECHANISM-v0.md` describing a multi-buyer Vickrey-like
  sealed-bid mechanism on a long-duration generation asset,
  including: bidder set, asset description, scoring rule,
  allocation rule, payment rule, and bounded-leakage profile.
- **R-PPF-002** — The mechanism SHALL be strategyproof under the
  honest-but-curious-other-bidders threat model. The proof or
  appeal-to-Vickrey SHALL appear in the mechanism doc.
- **R-PPF-003** — The mechanism SHALL bound the information any
  losing or winning bidder learns about another's load profile and
  willingness-to-pay. The bound SHALL be enumerated in
  `mechanism/leakage_bounds.yaml`.

## Scenario requirements

- **R-PPF-004** — The repo SHALL define a typed scenario schema
  `schemas/scenario.schema.json` covering: asset (capacity, COD,
  technology, project-finance structure), offtakers (n,
  load-profile shape, willingness-to-pay distribution), auction
  parameters.
- **R-PPF-005** — The repo SHALL ship one canonical notional
  scenario `scenarios/v0_1gw_3offtakers.json` (1-GW SMR, three
  notional hyperscaler offtakers) used as the reference workload
  in the paper.

## Simulator requirements

- **R-PPF-006** — The simulator SHALL run the mechanism against a
  scenario and produce a typed allocation + payment report.
- **R-PPF-007** — The simulator SHALL re-use sealed-bid runtime
  primitives from `sealed-bid-sourcing` where possible; this repo
  is the multi-buyer extension, not a fork.

## Paper requirements

- **R-PPF-008** — The paper SHALL include a project-finance
  capital-structure section translating the strategyproofness
  bound into language a project-finance reader recognizes
  (required equity tranche, lender-side underwriting confidence).
- **R-PPF-009** — Every numerical claim in the paper SHALL carry
  either an empirical citation or an explicit "(notional)"
  annotation.

## Voice and gate requirements

- **R-PPF-010** — The paper and mechanism doc SHALL pass voice_lint.
- **R-PPF-011** — `scripts/check_notional_disclosure.py` SHALL fail
  the build if any paper number lacks citation or notional flag.
- **R-PPF-012** — `scripts/validate_leakage_bound.py` SHALL fail the
  build if mechanism changes drift from `leakage_bounds.yaml`.
