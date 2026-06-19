# Design — Foundation

## Shape

Mechanism on top, simulator underneath, paper to the side.

```
        mechanism/MECHANISM-v0.md          (formal statement)
        mechanism/leakage_bounds.yaml      (threat model)
                       |
            scenarios/v0_1gw_3offtakers.json
                       |
                  simulator
                       |
              runs/<run_id>/{allocation,payments,receipts}.json
                       |
              paper/power-ppa-forge.tex    (capital-structure framing)
```

## Mechanism sketch

The v0 mechanism is a sealed-bid multi-buyer Vickrey-like allocation
on a single asset with multiple capacity tranches:

1. Asset is described by total capacity C, COD year, generation
   technology, and project-finance debt-service-coverage-ratio
   (DSCR) targets.
2. Each offtaker submits a sealed bid vector: for each tranche size
   t in {25%, 50%, 75%, 100%} of C, willingness-to-pay per MWh and
   load-profile commitment (a discretized hourly shape).
3. Allocation maximizes a scoring function combining total
   willingness-to-pay weighted by load-profile complementarity
   (because complementary loads improve the asset's capacity-factor
   underwriting).
4. Payment rule is Vickrey-extension: each winning offtaker pays
   the marginal externality their bid imposes, computed via the
   counterfactual without their bid.
5. Bounded leakage: each offtaker learns only their allocation,
   their payment, and aggregate complementarity score. Losing
   bidders learn only that they lost.

The mechanism doc names the construction's debt to single-good
Vickrey (Vickrey 1961) and to the multi-unit combinatorial
extensions (Ausubel-Milgrom 2002) and acknowledges what is
deliberately novel: the load-profile-complementarity term in the
scoring rule.

## Why load-profile complementarity matters

Project-finance underwriting of a 1-GW SMR requires confident
24/7/365 dispatch. If three hyperscaler offtakers each have
correlated demand profiles, the asset's effective utilization is
worse than if their demands are complementary. The mechanism
internalizes this by rewarding complementarity in the score,
giving lenders a reason to accept lower required equity tranche.

This is the load-bearing claim the paper makes.

## Simulator

The simulator reuses primitives from `sealed-bid-sourcing` for the
single-buyer-side sealed-bid execution and adds a multi-buyer
scoring layer plus a counterfactual-computation layer for the
Vickrey payments.

## Paper structure

```
1. Introduction (the 2026 nuclear bottleneck framing)
2. Mechanism (formal statement)
3. Threat model and leakage bounds
4. Reference simulator
5. Notional benchmark (1-GW SMR, 3 offtakers)
6. Capital-structure consequence (required equity tranche delta)
7. Limitations (what v0 doesn't model)
8. Future work (real-deployment requirements)
```

## Dependencies

- `pyca/cryptography` for sealed-bid primitives.
- `numpy` and `scipy` for scoring and counterfactual computation.
- `pydantic` for typed scenarios.
- `jsonschema` for validation.
- `sealed-bid-sourcing` as a library dependency.
- LaTeX for the paper.

## What is deliberately NOT in v0

- Real project-finance numbers. v0 is notional.
- Real hyperscaler load profiles. v0 uses synthetic shapes.
- Combinatorial-auction (Ausubel-Milgrom full) extensions. v0 uses
  a simpler multi-tranche allocation.
- Settlement / payment rails.
- Real-asset case study. The paper uses a notional SMR.
