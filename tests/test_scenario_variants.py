from __future__ import annotations

import json
from pathlib import Path

import pytest

from power_ppa_forge.models import load_scenario
from power_ppa_forge.simulator import run_simulation


REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIO_PATHS = [
    REPO_ROOT / "scenarios" / "v0_1gw_2offtakers.json",
    REPO_ROOT / "scenarios" / "v0_1gw_4offtakers.json",
]
RECEIPT_FIELDS = {
    "scenario_id",
    "offtaker_id",
    "won",
    "allocation_mw",
    "payment_per_mwh_usd",
    "aggregate_complementarity_score",
}


@pytest.mark.parametrize("scenario_path", SCENARIO_PATHS)
def test_scenario_variant_simulation_is_deterministic(scenario_path: Path) -> None:
    scenario = load_scenario(scenario_path)

    first = run_simulation(scenario)
    second = run_simulation(scenario)

    assert first == second


@pytest.mark.parametrize("scenario_path", SCENARIO_PATHS)
def test_scenario_variant_allocates_full_asset_capacity(scenario_path: Path) -> None:
    scenario = load_scenario(scenario_path)
    run = run_simulation(scenario)

    allocated = sum(run["allocation"]["allocation_mw"].values())

    assert allocated == scenario["asset"]["capacity_mw"]


@pytest.mark.parametrize("scenario_path", SCENARIO_PATHS)
def test_scenario_variant_receipts_keep_bids_and_profiles_private(scenario_path: Path) -> None:
    scenario = load_scenario(scenario_path)
    run = run_simulation(scenario)
    receipt_text = json.dumps(run["receipts"])

    assert all(set(receipt) == RECEIPT_FIELDS for receipt in run["receipts"])
    assert "bid_price_per_mwh" not in receipt_text
    assert "load_shape" not in receipt_text
    assert "max_capacity_mw" not in receipt_text
    assert "counterfactual" not in receipt_text
