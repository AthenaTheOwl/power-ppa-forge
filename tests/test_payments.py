from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from power_ppa_forge.models import load_scenario
from power_ppa_forge.simulator import best_allocation, run_simulation


REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = REPO_ROOT / "scenarios"
COMMITTED_SCENARIOS = [
    "v0_1gw_3offtakers.json",
    "v0_1gw_2offtakers.json",
    "v0_1gw_4offtakers.json",
    "v0_1gw_3offtakers_curtail.json",
]
# From no credit to far past where harbor_cloud takes all 500 MW (about 9.4).
CURTAILMENT_WEIGHTS = [step / 2 for step in range(0, 101)]


def _bid(scenario: dict[str, Any], bidder_id: str) -> float:
    return next(b["bid_price_per_mwh"] for b in scenario["offtakers"] if b["id"] == bidder_id)


def _allocated_at(scenario: dict[str, Any], bidder_id: str, price: float) -> float:
    """MW the bidder wins if it bids `price` and every other input stays fixed."""
    offtakers = [
        {**b, "bid_price_per_mwh": price} if b["id"] == bidder_id else b for b in scenario["offtakers"]
    ]
    allocation = best_allocation({**scenario, "offtakers": offtakers})["allocation_mw"]
    return allocation.get(bidder_id, 0.0)


def _threshold(scenario: dict[str, Any], bidder_id: str, level_mw: float) -> float:
    """Lowest price at which the bidder still wins at least `level_mw`, by bisection."""
    lo, hi = 0.0, _bid(scenario, bidder_id)
    if _allocated_at(scenario, bidder_id, lo) >= level_mw:
        return 0.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if _allocated_at(scenario, bidder_id, mid) >= level_mw:
            hi = mid
        else:
            lo = mid
    return hi


@pytest.mark.parametrize("scenario_name", COMMITTED_SCENARIOS)
def test_no_winner_pays_above_its_bid(scenario_name: str) -> None:
    scenario = load_scenario(SCENARIOS / scenario_name)
    payments = run_simulation(scenario)["payments"]

    assert payments
    for payment in payments:
        assert payment["payment_per_mwh_usd"] <= _bid(scenario, payment["offtaker_id"]), payment


@pytest.mark.parametrize("scenario_name", COMMITTED_SCENARIOS)
def test_no_winner_pays_above_its_bid_across_the_curtailment_sweep(scenario_name: str) -> None:
    scenario = load_scenario(SCENARIOS / scenario_name)
    violations = []
    for weight in CURTAILMENT_WEIGHTS:
        swept = {**scenario, "auction": {**scenario["auction"], "curtailment_weight": weight}}
        for payment in run_simulation(swept)["payments"]:
            if payment["payment_per_mwh_usd"] > _bid(scenario, payment["offtaker_id"]):
                violations.append((weight, payment["offtaker_id"], payment["payment_per_mwh_usd"]))

    assert violations == []


@pytest.mark.parametrize("scenario_name", COMMITTED_SCENARIOS)
def test_payment_is_the_winners_critical_value(scenario_name: str) -> None:
    # Bisect the real allocation rule, independently of the payment code: for
    # each MW level the winner reaches, find the lowest bid that still wins it.
    # The payment must be those per-tranche critical values, MW-weighted.
    scenario = load_scenario(SCENARIOS / scenario_name)
    tranches = sorted(float(value) for value in scenario["auction"]["tranche_options_mw"])

    for payment in run_simulation(scenario)["payments"]:
        bidder_id, held = payment["offtaker_id"], payment["allocated_mw"]
        levels = [level for level in tranches if level <= held]
        thresholds = [_threshold(scenario, bidder_id, level) for level in levels]
        steps = [level - previous for previous, level in zip([0.0] + levels, levels)]
        critical_per_mwh = sum(t * step for t, step in zip(thresholds, steps)) / held

        assert payment["payment_per_mwh_usd"] == pytest.approx(critical_per_mwh, abs=0.006), bidder_id


def test_bid_just_below_the_critical_value_loses_and_at_it_wins() -> None:
    # In the four-offtaker run each winner holds one 250 MW tranche, so its
    # critical value is one number: externality_score / allocated MW.
    scenario = load_scenario(SCENARIOS / "v0_1gw_4offtakers.json")
    payments = run_simulation(scenario)["payments"]

    assert len(payments) == 4
    for payment in payments:
        bidder_id, held = payment["offtaker_id"], payment["allocated_mw"]
        critical = payment["externality_score"] / held

        assert _allocated_at(scenario, bidder_id, critical - 0.001) < held, bidder_id
        assert _allocated_at(scenario, bidder_id, critical + 0.0001) == held, bidder_id
