# PowerPPAforge

An open mechanism specification, reference simulator, and white paper
for multi-hyperscaler power-purchase-agreement coordination on long-
duration generation (nuclear, SMR, gas-with-CCS), letting multiple
hyperscalers co-fund and co-offtake projects whose financeability
requires multi-counterparty offtake — without any hyperscaler
revealing its load profile or willingness-to-pay.

## What this is

Single-hyperscaler-anchored nuclear deals (Meta 6.6 GW Constellation,
AWS 1.92 GW Talen) work for the very biggest sites. The next tier of
projects requires multi-offtaker syndication, and there is no
primitive for it. Project finance demands offtake certainty;
hyperscalers will not reveal load profiles to competitors. The 2026
nuclear renaissance is bottlenecked here.

This repo is the mechanism — a multi-buyer Vickrey-like auction on
a long-duration generation asset with bounded leakage on each
buyer's load profile — plus a reference simulator, plus a white
paper modeled on a notional 1-GW SMR with three notional hyperscaler
offtakers.

## Status


v0.1 shipped — runnable, minimal. The first real deliverable is in place; the next passes deepen it (more scenarios, real-data backfill). The entry command `python -m power_ppa_forge validate` runs. See `specs/0002-design/` for the v0.1 scope and `STATUS.md` (where present) for the current state and next-feature queue.

## How to run

Placeholder. Will land in spec 0003. The intended invocation:

```bash
python -m power_ppa_forge scenario create \
  --asset notional-1gw-smr \
  --offtakers 3 \
  --out scenarios/v0_1gw_3offtakers.json
python -m power_ppa_forge simulate \
  --scenario scenarios/v0_1gw_3offtakers.json \
  --mechanism multi-buyer-vickrey-bounded-leak \
  --out runs/v0/
python -m power_ppa_forge capital-impact \
  --run runs/v0/ \
  --out reports/capital_impact.md
```

## Layout

```
power-ppa-forge/
  README.md
  LICENSE
  AGENTS.md
  .gitignore
  specs/
    0001-foundation/
      requirements.md
      design.md
      tasks.md
      acceptance.md
  docs/
    first-pr.md
  paper/                 # arrives in PR 0002
  mechanism/             # mechanism spec doc; PR 0002
  scenarios/             # benchmark instance JSON
  src/                   # arrives in PR 0003
```

## Why this exists

`procurement-negotiation-lab` is a working multi-attribute auction
simulator. `sealed-bid-sourcing` brings PSI / MPC primitives to
procurement. `grid-silicon` and `interconnect-alpha` provide the
power-market data layer. MIT SDM systems framing covers the
project-finance side. No portfolio combines all four. This repo
sits at that intersection.

The mechanism is the moat. Legal opinion and project-finance
compatibility are the hard part. Capacity-price calibration data
from `interconnect-alpha` closes the loop.

## First artifact

Open-source mechanism spec plus reference simulator plus white paper
modeled on a notional 1-GW SMR with three notional hyperscaler
offtakers. Show how the strategyproofness bound translates to
capital-structure consequence: lower required equity tranche when
the auction is bounded-leak Vickrey, because lenders can underwrite
multi-counterparty offtake without bilateral NDA chains.

## Plausibility

This is the most ambitious single repo in the portfolio. The
mechanism could become the standard if it lands; it could also
remain a paper. v0 deliberately produces an artifact (paper +
simulator) rather than chasing customer deployment.

## Compounds with

- `sealed-bid-sourcing` (shares MPC / bounded-leakage primitives)
- `interconnect-alpha` (capacity-price calibration data)
- `grid-silicon` (asset-side phantom-vs-real scoring)
- `agent-notary-layer` (receipt schema for auction audit trail)

## License

MIT. See [LICENSE](LICENSE).
