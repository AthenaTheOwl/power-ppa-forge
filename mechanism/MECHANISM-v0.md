# Mechanism v0

## Purpose

The v0 mechanism coordinates multiple sealed bids for capacity on one
long-duration generation asset. It is a reference mechanism for the
checked-in notional scenario, not a settlement system.

## Inputs

- Asset capacity, capacity factor, commercial operation year, DSCR
  target, and notional project cost.
- A fixed tranche set published before bidding.
- One sealed bid per offtaker, containing maximum capacity, price per
  MWh, and a discretized hourly load-shape vector.

## Allocation rule

The simulator enumerates feasible tranche combinations whose total
capacity equals the asset capacity. Each candidate receives a score:

```text
score = allocated_capacity_price_score
      + complementarity_weight * asset_capacity * aggregate_flatness
```

`aggregate_flatness` is one minus the coefficient of variation of the
allocated hourly load shape, clipped to the range from zero to one. The
highest-scoring feasible allocation wins.

## Payment rule

For each winner, the simulator computes the best feasible allocation
without that bidder. The winner's payment is the positive externality
between that counterfactual score and the score available to the other
winners under the selected allocation. The implementation reports this
externality as a per-MWh payment and as an annual notional payment.

This is a Vickrey-style externality payment. The v0 mechanism relies on
the standard incentive argument for Vickrey and VCG mechanisms, with the
additional caveat that the scoring function is fixed and public before
bids are submitted.

## Leakage boundary

Each bidder receives only:

- scenario id;
- bidder id;
- win/loss state;
- allocated capacity;
- own payment when applicable;
- aggregate complementarity score for the selected allocation.

Receipts do not include another bidder's bid price, load-shape vector,
maximum capacity, or counterfactual table. The machine-readable ledger is
`mechanism/leakage_bounds.yaml`.

## v0 limits

- The simulator is reference-grade and uses in-process JSON.
- The leakage proof is stated as an implementation boundary, not a
  production cryptographic protocol.
- The tranche set is small enough for exhaustive enumeration.
