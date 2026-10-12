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

Each winner pays its critical value. The simulator sets the winner's
price bid to zero, holds every other input fixed, and finds the best
feasible score. The payment is that score less the selected
allocation's score without the winner's own bid revenue (allocated MW
times bid price). Over the tranches the winner holds, this is the
lowest price at which it would still win each one, so no winner pays
more than it bid. The implementation reports the payment per MWh,
capped at the bid against cent rounding, and as an annual notional
payment.

The score is bid revenue plus a term that depends only on the
allocation, so this is the VCG payment with a Clarke pivot (Clarke
1971). For the price dimension, with the bidder's load shape and
capacity held fixed, the allocation is monotone in the bid and the
payment is the critical value, so bidding the true price is a dominant
strategy (Myerson 1981). Load shapes and capacities also enter the
score; v0 makes no incentive claim about them. The scoring function is
fixed and public before bids are submitted. An earlier rule measured
flatness without the winner; `decisions/DEC-PPF-003-critical-value-payments.md`
records why it was replaced.

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
