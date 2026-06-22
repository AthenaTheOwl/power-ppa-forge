# Power PPA Forge Paper Draft

## Claim

Power PPA Forge tests whether a sealed-bid, multi-buyer mechanism can
produce a financeable offtake allocation without exposing bidder load
profiles to competing offtakers. The v0.1 paper draft uses one
canonical scenario with a 1 GW (notional) SMR, three (notional)
offtakers, and a 24 hour (notional) load-shape vector for each
offtaker.

## Mechanism

The allocation rule scores feasible tranche combinations by bid value
and aggregate load-shape flatness. The payment rule follows the
externality structure used by Vickrey and VCG mechanisms [Vickrey;
Clarke; Groves]. The v0.1 implementation is reference-grade and does
not claim production cryptographic privacy.

## Capital-Structure Translation

Project-finance underwriting usually treats contracted revenue, DSCR,
counterparty concentration, and disclosure quality as lender inputs
[ProjectFinancePrimer]. The checked-in scenario compares a 42.0%
(notional) equity requirement for bilateral NDA coordination with a
34.0% (notional) equity requirement for the bounded-leak mechanism.
That produces an 8.0 percentage point (notional) equity-share delta on
a 7.4 billion USD (notional) project-cost base.

## Limits

The scenario values are notional. They are included to test data flow,
report generation, and the leakage boundary. They are not empirical
claims about SMR cost, hyperscaler demand, lender appetite, or market
clearing prices.
