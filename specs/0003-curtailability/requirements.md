# Spec 0003 requirements

## R-PPF-003-001 - curtailment term

An offtaker may declare `curtailable_fraction` (0 to 1) and the asset may
declare `stress_hours` (hours 0-23). The score adds `curtailment_weight`
times the sum of each winner's allocated MW times its curtailable
fraction, and flatness is measured after each winner's curtailable share
is shed in the stress hours.

## R-PPF-003-002 - defaults leave earlier runs unchanged

With the fields absent, every committed run under `runs/` that predates
the term must reproduce byte for byte.

## R-PPF-003-003 - no new disclosure

Receipts and payments keep their keys. A receipt must not disclose any
bidder's curtailable fraction.

## R-PPF-003-004 - individual rationality

At every curtailment weight, no winner pays more per MWh than it bid.

## R-PPF-003-005 - publish the weight

The weight is notional and can decide the auction alone, so the mechanism
spec publishes the allocation across a range of weights.
