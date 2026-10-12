# DEC-PPF-003 — pay each winner its critical value

## Status

Accepted (2026-10-12).

## Context

The v0.1 payment rule charged each winner the score of the best allocation
without it, less the score of the other winners' MW scored on their own. That
second score measured load flatness on the other winners' load alone, while the
allocation rule measures it on the full load, winner included. Whenever adding
the winner changes flatness the two disagree, so the payment was not the price
at which the winner would stop winning. In two of the three committed runs it
was higher than the winner's own bid, which breaks individual rationality: the
winner would rather have lost.

Bisecting the allocation rule (lowering one winner's bid, everything else fixed,
until it loses a tranche) gives each winner's critical value. All values $/MWh
(notional):

| Run | Winner | Bid | Old payment | Critical value |
|---|---|---:|---:|---:|
| v0_2offtakers | atlas_inference | 88.80 | 89.00 | 88.22 |
| v0_2offtakers | solstice_compute | 89.00 | 88.80 | 88.21 |
| v0_4offtakers | harbor_vector | 89.01 | 89.39 | 88.53 |
| v0_4offtakers | summit_inference | 89.00 | 89.26 | 88.54 |
| v0_4offtakers | copperline_compute | 89.03 | 88.80 | 87.97 |
| v0_4offtakers | keystone_ai | 89.02 | 88.67 | 87.93 |
| v0_baseline | mesa_ai | 88.00 | 86.61 | 85.83 |
| v0_baseline | northstar_compute | 92.00 | 86.59 | 85.99 |

The baseline payments stayed under the bids and were still off. The lowest bids
that keep mesa_ai's two 250 MW tranches are 85.67 and 85.99 (notional), an
average of 85.83, against the 86.61 it was charged.

## Decision

Each winner pays the best score reachable with its price bid set to zero, less
the selected allocation's score without its own bid revenue, divided by its MW.
The score is bid revenue plus a term that depends only on the allocation, so
this is the Clarke-pivot VCG payment for that score (Clarke 1971) and equals the
MW-weighted sum of the winner's per-tranche critical values (Myerson 1981). It
cannot exceed the bid; a cap at the bid covers cent rounding.

Allocations do not change. Payments change, and so does everything derived from
them: the payment fields in `payments.json` and `receipts.json` of all three
committed runs, the payment column of `reports/capital_impact.md`, and the
README sample output.

## Alternatives considered

- Keep the old rule and cap each payment at the bid. That restores individual
  rationality, yet a bidder valued between its critical value and the old
  payment still does better by losing, so truthful bidding stops being dominant.
- Pivot on the best allocation with the winner removed. That matches this rule
  whenever a zero bid would lose all the winner's MW, which holds in every
  committed run, and undercharges when flatness alone would win it MW at a zero
  bid.

## Evidence

`tests/test_payments.py` bisects the allocation rule without calling the payment
code and asserts that every payment equals the winner's per-tranche critical
values, that no winner pays above its bid, and that a four-offtaker winner
bidding 0.001 below its critical value loses its tranche while one at it wins.
Under the old rule six of its seven cases fail.

## Rollback

Revert the commit. The earlier runs and report stay in git history; any payment
quoted from them was computed under the old rule.
