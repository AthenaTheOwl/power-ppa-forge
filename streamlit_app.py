"""power-ppa-forge - live demo (Streamlit Community Cloud).

Reads the committed run under runs/v0_baseline/ (allocation, payments, receipts)
and shows the multi-buyer PPA syndication result: which offtakers cleared
capacity on a notional 1 GW asset, what they pay under the bounded-leak Vickrey
mechanism, and how much project equity that mechanism frees up versus bilateral
NDA chains. No network, no secrets - runs entirely off the committed fixture.

Deploy: Streamlit Community Cloud -> New app -> repo AthenaTheOwl/power-ppa-forge,
branch main, main file streamlit_app.py.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import streamlit as st

from power_ppa_forge.models import (
    ScenarioValidationError,
    canonical_scenario_path,
    validate_scenario,
)
from power_ppa_forge.simulator import run_simulation

REPO = Path(__file__).resolve().parent
RUN = REPO / "runs" / "v0_baseline"


def load_run() -> tuple[dict, list[dict], list[dict]] | None:
    allocation_path = RUN / "allocation.json"
    payments_path = RUN / "payments.json"
    receipts_path = RUN / "receipts.json"
    if not allocation_path.is_file() or not payments_path.is_file():
        return None
    allocation = json.loads(allocation_path.read_text(encoding="utf-8"))
    payments = json.loads(payments_path.read_text(encoding="utf-8"))["payments"]
    receipts = (
        json.loads(receipts_path.read_text(encoding="utf-8"))["receipts"]
        if receipts_path.is_file()
        else []
    )
    return allocation, payments, receipts


st.set_page_config(page_title="power-ppa-forge - PPA syndication", layout="wide")
st.title("power-ppa-forge")
st.caption(
    "multi-buyer PPA syndication on a long-duration generation asset: who clears "
    "capacity, what they pay under a bounded-leak Vickrey auction, and how much "
    "project equity the mechanism frees up versus bilateral NDA chains."
)

loaded = load_run()
if loaded is None:
    st.warning("no committed run found under runs/v0_baseline/ - run `python -m power_ppa_forge simulate` first")
    st.stop()

allocation, payments, receipts = loaded
alloc = allocation["allocation"]
capital = allocation["capital_impact"]

st.subheader(
    f"{allocation['scenario_id']} - {allocation['mechanism']} (run {allocation['run_id']})"
)

allocated_mw = sum(p["allocated_mw"] for p in payments)
equity_freed = capital["equity_reduction_musd"]
delta_pts = capital["equity_share_delta_percentage_points"]

c1, c2, c3 = st.columns(3)
c1.metric("allocated", f"{allocated_mw:,.0f} MW", help="capacity cleared across winning offtakers")
c2.metric(
    "portfolio complementarity",
    f"{alloc['complementarity_score']:.3f}",
    help="1.0 = perfectly flat combined load; rewards offtakers whose load shapes offset",
)
c3.metric(
    "equity freed",
    f"${equity_freed:,.0f}M",
    delta=f"-{delta_pts:.0f} pts equity share",
    delta_color="inverse",
    help="less equity to syndicate vs bilateral-NDA baseline",
)

# winners ranked, plus non-clearing offtakers from receipts
won_by_id = {p["offtaker_id"]: p for p in payments}
won_rows = sorted(payments, key=lambda p: p["allocated_mw"], reverse=True)
lost_rows = [r for r in receipts if not r["won"]]

only_winners = st.checkbox("show only offtakers that cleared capacity", value=False)

table = [
    {
        "offtaker": p["offtaker_id"],
        "allocated MW": p["allocated_mw"],
        "clearing price $/MWh": p["payment_per_mwh_usd"],
        "annual payment $M/yr": p["annual_payment_musd"],
        "cleared": True,
    }
    for p in won_rows
]
if not only_winners:
    table += [
        {
            "offtaker": r["offtaker_id"],
            "allocated MW": 0.0,
            "clearing price $/MWh": None,
            "annual payment $M/yr": None,
            "cleared": False,
        }
        for r in lost_rows
    ]

st.dataframe(table, use_container_width=True, hide_index=True)

if won_rows:
    top = won_rows[0]
    st.info(
        f"**capital headline:** bounded-leak Vickrey cuts required equity from "
        f"{capital['bilateral_nda_required_equity_share'] * 100:.0f}% to "
        f"{capital['bounded_leak_required_equity_share'] * 100:.0f}% "
        f"({delta_pts:.0f} pts) on a ${capital['project_cost_musd'] / 1000:.1f}B project - "
        f"${equity_freed:,.0f}M less equity to syndicate (notional v0.1). "
        f"top clearer: {top['offtaker_id']} at {top['allocated_mw']:.0f} MW, "
        f"${top['payment_per_mwh_usd']:.2f}/MWh."
    )

st.caption(
    "receipts disclose only id, win/loss, allocation, payment, and aggregate "
    "complementarity - never bid prices or load shapes. the mechanism + simulator live "
    "in `power_ppa_forge/`; this page reads the committed `runs/v0_baseline/`. "
    "repo: github.com/AthenaTheOwl/power-ppa-forge"
)

# ---------------------------------------------------------------------------
# interactive: run the real auction yourself
#
# everything below drives the actual engine. it builds a scenario from your
# inputs, runs it through power_ppa_forge.models.validate_scenario (the real
# v0.1 data contract) and power_ppa_forge.simulator.run_simulation (the real
# vickrey allocation + payment solver) — no lookup, no hardcoded result.
# ---------------------------------------------------------------------------

st.divider()
st.header("run the auction yourself")
st.caption(
    "edit each offtaker's bid and the size they can take, plus how much the asset "
    "owner values a flat combined load. the page rebuilds a scenario and runs it "
    "through the real solver (`power_ppa_forge.simulator.run_simulation`) — the "
    "allocation, the bounded-leak Vickrey clearing prices, and the complementarity "
    "score below are all recomputed live, never looked up."
)


@st.cache_data
def base_scenario() -> dict:
    """the canonical v0.1 fixture — the same one the CLI defaults to."""
    return json.loads(canonical_scenario_path().read_text(encoding="utf-8"))


_base = base_scenario()
scenario = copy.deepcopy(_base)

st.markdown("**asset / auction**")
ac1, ac2 = st.columns(2)
scenario["auction"]["complementarity_weight"] = ac1.slider(
    "complementarity weight",
    min_value=0.0,
    max_value=12.0,
    value=float(_base["auction"]["complementarity_weight"]),
    step=0.5,
    help=(
        "how much the asset owner pays, per MW of capacity, for a perfectly flat "
        "combined load shape. higher weight favours offtakers whose loads offset, "
        "even at a lower bid."
    ),
)
ac2.metric(
    "asset capacity",
    f"{_base['asset']['capacity_mw']:,.0f} MW",
    help="fixed at the notional 1 GW asset; tranches must sum to exactly this.",
)

st.markdown("**offtakers** — set each bidder's price and the largest tranche they will take")
for offtaker in scenario["offtakers"]:
    base_off = next(o for o in _base["offtakers"] if o["id"] == offtaker["id"])
    oc1, oc2 = st.columns([1, 1])
    offtaker["bid_price_per_mwh"] = oc1.slider(
        f"{offtaker['display_name']} — bid $/MWh",
        min_value=40.0,
        max_value=200.0,
        value=float(base_off["bid_price_per_mwh"]),
        step=1.0,
        key=f"bid_{offtaker['id']}",
    )
    offtaker["max_capacity_mw"] = oc2.select_slider(
        f"{offtaker['display_name']} — max tranche MW",
        options=[250.0, 500.0, 750.0, 1000.0],
        value=float(base_off["max_capacity_mw"]),
        key=f"cap_{offtaker['id']}",
    )

try:
    validate_scenario(scenario)
    run = run_simulation(scenario)
except ScenarioValidationError as exc:
    st.error(f"scenario does not satisfy the v0.1 data contract: {exc}")
    st.stop()
except ValueError as exc:
    st.error(f"no feasible allocation for these inputs: {exc}")
    st.stop()

live_alloc = run["allocation"]
live_payments = run["payments"]
won_ids = {p["offtaker_id"] for p in live_payments}

lc1, lc2, lc3 = st.columns(3)
lc1.metric("allocated", f"{sum(p['allocated_mw'] for p in live_payments):,.0f} MW")
lc2.metric(
    "portfolio complementarity",
    f"{live_alloc['complementarity_score']:.3f}",
    delta=f"{live_alloc['complementarity_score'] - alloc['complementarity_score']:+.3f} vs baseline",
)
lc3.metric(
    "winning offtakers",
    f"{len(won_ids)} of {len(scenario['offtakers'])}",
)

display_by_id = {o["id"]: o["display_name"] for o in scenario["offtakers"]}
pay_by_id = {p["offtaker_id"]: p for p in live_payments}
live_table = []
for off in scenario["offtakers"]:
    p = pay_by_id.get(off["id"])
    live_table.append(
        {
            "offtaker": display_by_id[off["id"]],
            "bid $/MWh": off["bid_price_per_mwh"],
            "allocated MW": p["allocated_mw"] if p else 0.0,
            "clearing price $/MWh": p["payment_per_mwh_usd"] if p else None,
            "annual payment $M/yr": p["annual_payment_musd"] if p else None,
            "cleared": off["id"] in won_ids,
        }
    )
st.dataframe(live_table, use_container_width=True, hide_index=True)

st.caption(
    "note the Vickrey twist: a winner's clearing price is the externality it imposes "
    "on the others, not its own bid — so the offtaker who bids highest does not "
    "necessarily pay the most. push one bidder's price up or shrink another's tranche "
    "and watch who clears flip live. computed by `run_simulation`, run "
    f"`{run['run_id']}`."
)
