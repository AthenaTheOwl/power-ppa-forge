from __future__ import annotations

import json
from pathlib import Path

from power_ppa_forge.models import load_scenario
from power_ppa_forge.simulator import render_report, run_simulation


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_simulation_allocates_full_asset_capacity() -> None:
    scenario = load_scenario()
    run = run_simulation(scenario)

    allocated = sum(run["allocation"]["allocation_mw"].values())
    assert allocated == scenario["asset"]["capacity_mw"]
    # Pin the exact baseline complementarity so a sign flip in the 1.0 - cov
    # formula (which clamps back to 1.0) cannot pass a bare > 0 check.
    assert run["allocation"]["complementarity_score"] == 0.945466
    assert run["capital_impact"]["equity_share_delta_percentage_points"] == 8.0


def test_baseline_allocation_and_score_are_pinned() -> None:
    # Golden-master lock on the winning allocation and objective score. Inverting
    # the score objective (revenue + weighted_complementarity) picks a different
    # maximizer, which the sum==capacity invariant would not catch.
    run = run_simulation(load_scenario())
    allocation = run["allocation"]

    assert allocation["allocation_mw"] == {"mesa_ai": 500.0, "northstar_compute": 500.0}
    assert allocation["score"] == 94254.596614
    assert allocation["revenue_score"] == 90000.0
    assert allocation["weighted_complementarity"] == 4254.596614


def test_baseline_payments_match_committed_golden() -> None:
    # Live payments must equal the committed golden run: this pins the Vickrey
    # externality (max clamp + externality/capacity per-MWh divide) and the
    # 8760-hour annual_payment constant against the run in runs/v0_baseline.
    run = run_simulation(load_scenario())
    committed = json.loads(
        (REPO_ROOT / "runs" / "v0_baseline" / "payments.json").read_text(encoding="utf-8")
    )["payments"]

    assert run["payments"] == committed
    # Spell out the pinned values so the intent survives even if the golden moves.
    mesa = next(p for p in run["payments"] if p["offtaker_id"] == "mesa_ai")
    assert mesa["payment_per_mwh_usd"] == 86.61
    assert mesa["externality_score"] == 43303.788472
    assert mesa["annual_payment_musd"] == 349.004


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
