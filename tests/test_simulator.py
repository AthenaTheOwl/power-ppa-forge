from __future__ import annotations

import json

from power_ppa_forge.models import load_scenario
from power_ppa_forge.simulator import render_report, run_simulation


def test_simulation_allocates_full_asset_capacity() -> None:
    scenario = load_scenario()
    run = run_simulation(scenario)

    allocated = sum(run["allocation"]["allocation_mw"].values())
    assert allocated == scenario["asset"]["capacity_mw"]
    assert run["allocation"]["complementarity_score"] > 0
    assert run["capital_impact"]["equity_share_delta_percentage_points"] == 8.0


def test_receipts_do_not_leak_bid_or_profile_fields() -> None:
    run = run_simulation(load_scenario())
    receipt_text = json.dumps(run["receipts"])

    assert "bid_price_per_mwh" not in receipt_text
    assert "load_shape" not in receipt_text
    assert "max_capacity_mw" not in receipt_text
    assert "counterfactual" not in receipt_text


def test_report_marks_notional_values() -> None:
    report = render_report(run_simulation(load_scenario()))

    assert "MW (notional)" in report
    assert "% (notional)" in report
    assert "million (notional)" in report
