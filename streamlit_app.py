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

import json
from pathlib import Path

import streamlit as st

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
