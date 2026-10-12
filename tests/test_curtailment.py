from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from power_ppa_forge.models import ScenarioValidationError, load_scenario, validate_scenario
from power_ppa_forge.simulator import (
    compute_complementarity,
    compute_curtailable_mw,
    run_simulation,
    score_allocation,
    write_run_artifacts,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = REPO_ROOT / "scenarios"
CURTAIL_SCENARIO = SCENARIOS / "v0_1gw_3offtakers_curtail.json"
RECEIPT_FIELDS = {
    "scenario_id",
    "offtaker_id",
    "won",
    "allocation_mw",
    "payment_per_mwh_usd",
    "aggregate_complementarity_score",
}
PAYMENT_FIELDS = {
    "offtaker_id",
    "allocated_mw",
    "payment_per_mwh_usd",
    "annual_payment_musd",
    "externality_score",
}


def _offtaker(scenario: dict, offtaker_id: str) -> dict:
    return next(bidder for bidder in scenario["offtakers"] if bidder["id"] == offtaker_id)


@pytest.mark.parametrize(
    ("scenario_name", "run_name"),
    [
        ("v0_1gw_3offtakers.json", "v0_baseline"),
        ("v0_1gw_2offtakers.json", "v0_2offtakers"),
        ("v0_1gw_4offtakers.json", "v0_4offtakers"),
        ("v0_1gw_3offtakers_curtail.json", "v0_curtail"),
    ],
)
def test_committed_runs_reproduce_byte_for_byte(scenario_name: str, run_name: str, tmp_path: Path) -> None:
    # The curtailment fields default to zero, so every scenario written before
    # them must still produce its committed artifacts unchanged.
    write_run_artifacts(run_simulation(load_scenario(SCENARIOS / scenario_name)), tmp_path)
    for artifact in ("allocation.json", "payments.json", "receipts.json"):
        fresh = (tmp_path / artifact).read_bytes().replace(b"\r\n", b"\n")
        committed = (REPO_ROOT / "runs" / run_name / artifact).read_bytes().replace(b"\r\n", b"\n")
        assert fresh == committed, f"{run_name}/{artifact} drifted"


@pytest.mark.parametrize(
    "allocation",
    [
        {"northstar_compute": 500.0, "harbor_cloud": 500.0},
        {"northstar_compute": 500.0, "mesa_ai": 250.0, "harbor_cloud": 250.0},
        {"northstar_compute": 500.0, "mesa_ai": 500.0},
    ],
)
def test_score_difference_equals_curtailment_term(allocation: dict[str, float]) -> None:
    scenario = load_scenario(CURTAIL_SCENARIO)
    unweighted = copy.deepcopy(scenario)
    unweighted["auction"]["curtailment_weight"] = 0.0

    weight = scenario["auction"]["curtailment_weight"]
    expected_term = weight * sum(
        capacity * _offtaker(scenario, bidder_id).get("curtailable_fraction", 0.0)
        for bidder_id, capacity in allocation.items()
    )

    weighted = score_allocation(scenario, allocation)
    plain = score_allocation(unweighted, allocation)

    assert weighted["score"] - plain["score"] == pytest.approx(expected_term, abs=1e-5)
    assert weighted["weighted_curtailment"] == pytest.approx(expected_term)
    assert weighted["curtailable_mw"] == pytest.approx(compute_curtailable_mw(scenario, allocation))
    # The weight moves only the curtailment term; shedding already shaped flatness.
    assert weighted["complementarity_score"] == plain["complementarity_score"]
    assert weighted["revenue_score"] == plain["revenue_score"]


def test_harbor_curtailment_term_is_150_curtailable_mw_at_weight_10() -> None:
    scored = score_allocation(
        load_scenario(CURTAIL_SCENARIO), {"northstar_compute": 500.0, "harbor_cloud": 500.0}
    )

    assert scored["curtailable_mw"] == 150.0
    assert scored["weighted_curtailment"] == 1500.0


def test_curtailment_leaves_receipt_and_payment_keys_unchanged() -> None:
    baseline = run_simulation(load_scenario())
    curtailed = run_simulation(load_scenario(CURTAIL_SCENARIO))

    assert all(set(receipt) == RECEIPT_FIELDS for receipt in baseline["receipts"])
    assert all(set(receipt) == RECEIPT_FIELDS for receipt in curtailed["receipts"])
    assert all(set(payment) == PAYMENT_FIELDS for payment in baseline["payments"])
    assert all(set(payment) == PAYMENT_FIELDS for payment in curtailed["payments"])

    receipt_text = json.dumps(curtailed["receipts"])
    assert "curtailable_fraction" not in receipt_text
    assert "curtailable_mw" not in receipt_text
    assert "stress_hours" not in receipt_text
    assert "bid_price_per_mwh" not in receipt_text
    assert "load_shape" not in receipt_text


def test_scenarios_without_the_term_report_no_curtailment_keys() -> None:
    allocation = run_simulation(load_scenario())["allocation"]

    assert "curtailable_mw" not in allocation
    assert "weighted_curtailment" not in allocation


def test_complementarity_sheds_curtailable_share_in_stress_hours() -> None:
    scenario = load_scenario(CURTAIL_SCENARIO)
    harbor = _offtaker(scenario, "harbor_cloud")
    stress_hours = set(scenario["asset"]["stress_hours"])

    hourly = [
        500.0 * value * (0.7 if hour in stress_hours else 1.0)
        for hour, value in enumerate(harbor["load_shape"])
    ]
    mean = sum(hourly) / 24
    cov = math.sqrt(sum((value - mean) ** 2 for value in hourly) / 24) / mean
    expected = max(0.0, min(1.0, 1.0 - cov))

    assert compute_complementarity(scenario, {"harbor_cloud": 500.0}) == pytest.approx(expected)
    # Shedding makes the served load lumpier than harbor's unshed shape.
    unshed = compute_complementarity(load_scenario(), {"harbor_cloud": 500.0})
    assert compute_complementarity(scenario, {"harbor_cloud": 500.0}) < unshed


def test_no_stress_window_means_nothing_is_shed() -> None:
    scenario = load_scenario(CURTAIL_SCENARIO)
    scenario["asset"]["stress_hours"] = []
    allocation = {"northstar_compute": 500.0, "harbor_cloud": 500.0}

    assert compute_complementarity(scenario, allocation) == compute_complementarity(
        load_scenario(), allocation
    )


@pytest.mark.parametrize(
    ("weight", "expected_allocation"),
    [
        (0.0, {"mesa_ai": 500.0, "northstar_compute": 500.0}),
        (6.0, {"mesa_ai": 500.0, "northstar_compute": 500.0}),
        (8.0, {"harbor_cloud": 250.0, "mesa_ai": 250.0, "northstar_compute": 500.0}),
        (10.0, {"harbor_cloud": 500.0, "northstar_compute": 500.0}),
        (20.0, {"harbor_cloud": 500.0, "northstar_compute": 500.0}),
    ],
)
def test_weight_sweep_matches_mechanism_doc(weight: float, expected_allocation: dict[str, float]) -> None:
    # The weight is notional and can decide the auction by itself; the sweep
    # in mechanism/MECHANISM-v0.md publishes where it flips.
    scenario = load_scenario(CURTAIL_SCENARIO)
    scenario["auction"]["curtailment_weight"] = weight

    assert run_simulation(scenario)["allocation"]["allocation_mw"] == expected_allocation


@pytest.mark.parametrize(
    ("section", "field", "value", "message"),
    [
        ("harbor_cloud", "curtailable_fraction", 1.2, "at most 1"),
        ("harbor_cloud", "curtailable_fraction", -0.1, "non-negative"),
        ("harbor_cloud", "curtailable_fraction", True, "non-negative"),
        ("asset", "stress_hours", [17, 24], "hours 0-23"),
        ("asset", "stress_hours", [17, 17], "repeat"),
        ("asset", "stress_hours", "17-21", "hours 0-23"),
        ("asset", "stress_hours", [], "stress_hours to shed into"),
        ("auction", "curtailment_weight", -1, "non-negative"),
    ],
)
def test_validation_rejects_bad_curtailment_fields(
    section: str, field: str, value: object, message: str
) -> None:
    scenario = json.loads(CURTAIL_SCENARIO.read_text(encoding="utf-8"))
    target = scenario[section] if section in scenario else _offtaker(scenario, section)
    target[field] = value

    with pytest.raises(ScenarioValidationError, match=message):
        validate_scenario(scenario)
