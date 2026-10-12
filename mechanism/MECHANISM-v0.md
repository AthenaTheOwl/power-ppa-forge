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
- Optional, for the curtailment term: the asset's `stress_hours` (hours
  0-23, published before bidding), a public `curtailment_weight`, and a
  per-bid `curtailable_fraction` (0 to 1), the share of its load the
  bidder agrees to shed during those hours.

## Allocation rule

The simulator enumerates feasible tranche combinations whose total
capacity equals the asset capacity. Each candidate receives a score:

```text
score = allocated_capacity_price_score
      + complementarity_weight * asset_capacity * aggregate_flatness
      + curtailment_weight * curtailable_capacity
```

`aggregate_flatness` is one minus the coefficient of variation of the
allocated hourly load shape, clipped to the range from zero to one. The
highest-scoring feasible allocation wins.

`curtailable_capacity` is the sum over winners of allocated MW times
`curtailable_fraction`. Before flatness is measured, each winner's
curtailable share is shed in every stress hour, so flatness describes
the load the asset serves on a stress day. The shed can move flatness
either way: harbor_cloud's flat load served alone gets lumpier, while
paired with mesa_ai, whose load peaks in the evening, it gets flatter.

The defaults are a weight of zero, a fraction of zero and no stress
hours. Under them the term vanishes, nothing is shed, and the two-,
three- and four-offtaker runs reproduce byte for byte. A scenario that
declares `curtailment_weight` also gets `curtailable_mw` and
`weighted_curtailment` in its allocation artifact.

### Curtailment weight sweep (notional)

`scenarios/v0_1gw_3offtakers_curtail.json` is the three-offtaker
baseline with harbor_cloud 0.3 curtailable over stress hours 17-20
(17:00-21:00) at a weight of 10 (notional). The weight is a notional
number and decides the auction on its own, so the sweep is part of the
result. Payments are $/MWh (notional).

| Weight | Allocation (MW) | Payments |
|---:|---|---|
| 0 | northstar 500, mesa 500 | northstar 86.05, mesa 85.56 |
| 6 | northstar 500, mesa 500 | northstar 87.85, mesa 87.36 |
| 8 | northstar 500, mesa 250, harbor 250 | northstar 88.30, mesa 87.61, harbor 85.69 |
| 10 | northstar 500, harbor 500 | northstar 88.49, harbor 85.44 |
| 20 | northstar 500, harbor 500 | northstar 88.49, harbor 82.44 |

Against mesa_ai's $2/MWh (notional) price lead and the flatness its
shed costs, harbor_cloud needs a weight near 7 (notional) to win a
250 MW tranche and near 9.4 (notional) to take all 500 MW. Even at
weight 0 the payments move off the baseline, because a curtailable
loser is a different counterfactual. No winner pays above its bid at
any weight: mesa_ai bids 88 and pays 87.36 at weight 6, and
harbor_cloud bids 86 and pays 85.44 at weight 10 (notional).
`tests/test_curtailment.py` pins the allocation column and
`tests/test_payments.py` checks every payment against its bid from
weight 0 to 50.

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

The curtailment credit is part of the score, so it enters the critical
value like any other term: a curtailable winner's own credit lowers the
bid it needs to win, and with it the payment.

## Leakage boundary

Each bidder receives only:

- scenario id;
- bidder id;
- win/loss state;
- allocated capacity;
- own payment when applicable;
- aggregate complementarity score for the selected allocation.

Receipts do not include another bidder's bid price, load-shape vector,
maximum capacity, curtailable fraction, or counterfactual table. The
curtailment term adds no receipt field; the aggregate complementarity
score is still one number, now measured after the stress-hour shed. The
machine-readable ledger is `mechanism/leakage_bounds.yaml`.

## v0 limits

- The simulator is reference-grade and uses in-process JSON.
- The leakage proof is stated as an implementation boundary, not a
  production cryptographic protocol.
- The tranche set is small enough for exhaustive enumeration.
- The curtailment term prices a promise to shed load. Nothing in v0
  dispatches, meters or penalizes the shed, so a bidder can claim
  flexibility it never delivers.
