# power-ppa-forge

Three hyperscalers want power off the same 1,000 MW reactor. None will tell the
others how much it needs or what it would pay — those are the two facts a lender
needs and the two facts a competitor must never see. power-ppa-forge runs the
auction that clears the megawatts while keeping both facts sealed.

## What it does

A single buyer can anchor the very biggest nuclear deals — Meta took 6.6 GW from
Constellation, AWS 1.92 GW from Talen. The tier below that needs several offtakers
on one asset, and there is no mechanism for it. Project finance wants offtake
certainty; hyperscalers will not hand rivals their load profiles to get it. That
standoff is where a lot of long-duration generation stalls.

power-ppa-forge is the mechanism that breaks it: a multi-buyer Vickrey-style
auction over one long-duration asset, with a bounded leak on what each buyer's bid
reveals. It ships as a runnable simulator, a mechanism spec, and a white paper
modeled on a notional 1 GW SMR with three notional offtakers. The receipt each
buyer gets back discloses its own id, win or loss, allocation, payment, and one
aggregate complementarity number — never anyone's price, never anyone's load shape.

## Try it

One command, no setup, no keys. It reads the committed run and prints the result:

```bash
python -m power_ppa_forge show
```

```
power-ppa-forge - multi-buyer PPA syndication, run v0-baseline-3eac2d52
scenario v0_1gw_3offtakers | mechanism multi-buyer-vickrey-bounded-leak

1000 MW allocated across 2 winning offtaker(s); 1 offtaker(s) cleared no capacity. portfolio complementarity 0.945 (1.0 = perfectly flat combined load).

offtaker              allocated   clearing price   annual payment
-----------------------------------------------------------------
mesa_ai                   500MW $      86.61/MWh $       349.0M/yr
northstar_compute         500MW $      86.59/MWh $       348.9M/yr
harbor_cloud                0MW       (no clear)                -

capital headline: bounded-leak Vickrey cuts required equity from 42% to 34% (8 pts) on a $7.4B project - $592M less equity to syndicate (notional v0.1).
receipts disclose only id, win/loss, allocation, payment, and aggregate complementarity - never bid prices or load shapes.
```

Two buyers split the 1,000 MW; the third walks away with a receipt that proves it
lost without proving anything else. The 8-point equity cut is the whole argument:
lenders can underwrite multi-counterparty offtake without bilateral NDA chains.

## Live demo

A Streamlit page (`streamlit_app.py`) renders the same result interactively:
allocation metrics, the ranked offtaker table, and the capital headline. It reads
the committed `runs/v0_baseline/` directly - no network, no secrets.

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud: New app -> repo `AthenaTheOwl/power-ppa-forge`,
branch `main`, main file `streamlit_app.py`.

<!-- live-url: -->

## How it connects

power-ppa-forge sits where four things the others already do meet:

- [sealed-bid-sourcing](https://github.com/AthenaTheOwl/sealed-bid-sourcing) — the
  PSI / MPC primitives that bound how much a bid leaks.
- [interconnect-alpha](https://github.com/AthenaTheOwl/interconnect-alpha) —
  capacity-price calibration data, so the clearing prices aren't invented.
- [grid-silicon](https://github.com/AthenaTheOwl/grid-silicon) — the asset side,
  scoring whether the generation behind the auction is real or a form.
- [agent-notary-layer](https://github.com/AthenaTheOwl/agent-notary-layer) — the
  receipt schema that makes the auction audit trail hold up.

## Run it in full

```bash
# validate the canonical scenario
python -m power_ppa_forge validate

# regenerate the run artifacts and capital-impact report
python -m power_ppa_forge simulate --out runs/v0_baseline
python -m power_ppa_forge capital-impact --out reports/capital_impact.md
```

The committed run produces `reports/capital_impact.md`: the allocation table, the
capital-structure delta, and the leakage-receipt check.

## Layout

```
power_ppa_forge/      package: cli, simulator, scoring, models
mechanism/            MECHANISM-v0.md + leakage_bounds.yaml
paper/                the white paper
scenarios/            v0_1gw_3offtakers.json — the benchmark instance
schemas/              scenario.schema.json
runs/v0_baseline/     allocation, payments, receipts
reports/              capital_impact.md + .jsonl
specs/  docs/  tests/
```

## License

MIT. See [LICENSE](LICENSE).
