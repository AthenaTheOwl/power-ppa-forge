from __future__ import annotations

import hashlib
import json
import math
from itertools import product
from pathlib import Path
from typing import Any


def run_simulation(scenario: dict[str, Any]) -> dict[str, Any]:
    allocation = best_allocation(scenario)
    payments = compute_payments(scenario, allocation["allocation_mw"])
    receipts = build_receipts(scenario, allocation, payments)
    capital = compute_capital_impact(scenario)

    return {
        "run_id": _run_id(scenario),
        "scenario_id": scenario["scenario_id"],
        "mechanism": scenario["auction"]["mechanism"],
        "allocation": allocation,
        "payments": payments,
        "receipts": receipts,
        "capital_impact": capital,
    }


def best_allocation(scenario: dict[str, Any], exclude_bidder: str | None = None) -> dict[str, Any]:
    candidates = list(_candidate_allocations(scenario, exclude_bidder=exclude_bidder))
    if not candidates:
        raise ValueError("no feasible allocation for scenario")
    return max(
        candidates,
        key=lambda item: (
            item["score"],
            item["revenue_score"],
            tuple(item["allocation_mw"].values()),
        ),
    )


def score_allocation(scenario: dict[str, Any], allocation_mw: dict[str, float]) -> dict[str, Any]:
    bidders = {bidder["id"]: bidder for bidder in scenario["offtakers"]}
    revenue_score = sum(
        allocation_mw.get(bidder_id, 0.0) * bidders[bidder_id]["bid_price_per_mwh"]
        for bidder_id in allocation_mw
    )
    complementarity_score = compute_complementarity(scenario, allocation_mw)
    weighted_complementarity = (
        scenario["auction"]["complementarity_weight"]
        * scenario["asset"]["capacity_mw"]
        * complementarity_score
    )
    score = revenue_score + weighted_complementarity
    return {
        "allocation_mw": {key: round(value, 3) for key, value in allocation_mw.items() if value > 0},
        "score": round(score, 6),
        "revenue_score": round(revenue_score, 6),
        "complementarity_score": round(complementarity_score, 6),
        "weighted_complementarity": round(weighted_complementarity, 6),
    }


def compute_complementarity(scenario: dict[str, Any], allocation_mw: dict[str, float]) -> float:
    bidders = {bidder["id"]: bidder for bidder in scenario["offtakers"]}
    hourly = []
    for hour in range(24):
        total = 0.0
        for bidder_id, capacity in allocation_mw.items():
            total += capacity * bidders[bidder_id]["load_shape"][hour]
        hourly.append(total)

    mean_load = sum(hourly) / len(hourly)
    if mean_load <= 0:
        return 0.0
    variance = sum((value - mean_load) ** 2 for value in hourly) / len(hourly)
    coefficient_of_variation = math.sqrt(variance) / mean_load
    return max(0.0, min(1.0, 1.0 - coefficient_of_variation))


def compute_payments(scenario: dict[str, Any], allocation_mw: dict[str, float]) -> list[dict[str, Any]]:
    payments: list[dict[str, Any]] = []
    capacity_factor = scenario["asset"]["capacity_factor"]

    for bidder_id, capacity in allocation_mw.items():
        without_bidder = best_allocation(scenario, exclude_bidder=bidder_id)
        others_allocation = {
            other_id: other_capacity
            for other_id, other_capacity in allocation_mw.items()
            if other_id != bidder_id
        }
        others_score = score_allocation(scenario, others_allocation)
        externality = max(0.0, without_bidder["score"] - others_score["score"])
        payment_per_mwh = round(externality / capacity, 2)
        annual_payment_musd = round(payment_per_mwh * capacity * 8760 * capacity_factor / 1_000_000, 3)
        payments.append(
            {
                "offtaker_id": bidder_id,
                "allocated_mw": round(capacity, 3),
                "payment_per_mwh_usd": payment_per_mwh,
                "annual_payment_musd": annual_payment_musd,
                "externality_score": round(externality, 6),
            }
        )

    return sorted(payments, key=lambda item: item["offtaker_id"])


def build_receipts(
    scenario: dict[str, Any],
    allocation: dict[str, Any],
    payments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    payment_by_bidder = {payment["offtaker_id"]: payment for payment in payments}
    receipts = []
    for bidder in scenario["offtakers"]:
        bidder_id = bidder["id"]
        payment = payment_by_bidder.get(bidder_id)
        allocated_mw = allocation["allocation_mw"].get(bidder_id, 0.0)
        receipts.append(
            {
                "scenario_id": scenario["scenario_id"],
                "offtaker_id": bidder_id,
                "won": allocated_mw > 0,
                "allocation_mw": allocated_mw,
                "payment_per_mwh_usd": None if payment is None else payment["payment_per_mwh_usd"],
                "aggregate_complementarity_score": allocation["complementarity_score"],
            }
        )
    return receipts


def compute_capital_impact(scenario: dict[str, Any]) -> dict[str, Any]:
    capital_case = scenario["capital_case"]
    asset = scenario["asset"]
    baseline = capital_case["bilateral_nda_required_equity_share"]
    mechanism = capital_case["bounded_leak_required_equity_share"]
    delta = baseline - mechanism
    project_cost_musd = asset["project_cost_usd_billion"] * 1000
    return {
        "bilateral_nda_required_equity_share": round(baseline, 4),
        "bounded_leak_required_equity_share": round(mechanism, 4),
        "equity_share_delta_percentage_points": round(delta * 100, 2),
        "equity_reduction_musd": round(delta * project_cost_musd, 2),
        "project_cost_musd": round(project_cost_musd, 2),
    }


def write_run_artifacts(run: dict[str, Any], out_dir: str | Path) -> None:
    path = Path(out_dir)
    path.mkdir(parents=True, exist_ok=True)
    _write_json(path / "allocation.json", _allocation_artifact(run))
    _write_json(path / "payments.json", _payments_artifact(run))
    _write_json(path / "receipts.json", _receipts_artifact(run))


def write_report(run: dict[str, Any], out_path: str | Path) -> None:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_report(run), encoding="utf-8")


def render_report(run: dict[str, Any]) -> str:
    allocation = run["allocation"]
    payments = run["payments"]
    capital = run["capital_impact"]
    lines = [
        "# Capital Impact Report",
        "",
        f"Scenario: `{run['scenario_id']}`",
        "",
        "All numeric values in this artifact are notional v0.1 fixture values.",
        "",
        "## Allocation",
        "",
        "| Offtaker | Capacity | Payment |",
        "|---|---:|---:|",
    ]

    payment_by_bidder = {payment["offtaker_id"]: payment for payment in payments}
    for bidder_id, capacity in allocation["allocation_mw"].items():
        payment = payment_by_bidder[bidder_id]
        lines.append(
            f"| `{bidder_id}` | {capacity:g} MW (notional) | "
            f"${payment['payment_per_mwh_usd']:.2f}/MWh (notional) |"
        )

    lines.extend(
        [
            "",
            "## Capital Structure",
            "",
            "- Bilateral NDA required equity: "
            f"{capital['bilateral_nda_required_equity_share'] * 100:.1f}% (notional).",
            "- Bounded-leak mechanism required equity: "
            f"{capital['bounded_leak_required_equity_share'] * 100:.1f}% (notional).",
            "- Equity-share delta: "
            f"{capital['equity_share_delta_percentage_points']:.1f} percentage points (notional).",
            "- Equity reduction on project cost: "
            f"${capital['equity_reduction_musd']:.1f} million (notional).",
            "",
            "## Leakage Receipt Check",
            "",
            "The checked-in receipts disclose only bidder id, win/loss state, allocation, payment, "
            "and aggregate complementarity score. They do not disclose bid prices or load-shape vectors.",
            "",
        ]
    )
    return "\n".join(lines)


def _candidate_allocations(scenario: dict[str, Any], exclude_bidder: str | None) -> list[dict[str, Any]]:
    capacity_mw = scenario["asset"]["capacity_mw"]
    tranches = scenario["auction"]["tranche_options_mw"]
    active_bidders = [bidder for bidder in scenario["offtakers"] if bidder["id"] != exclude_bidder]
    options_by_bidder = []
    for bidder in active_bidders:
        bidder_options = [0.0] + [float(value) for value in tranches if value <= bidder["max_capacity_mw"]]
        options_by_bidder.append(bidder_options)

    candidates = []
    for candidate in product(*options_by_bidder):
        if abs(sum(candidate) - capacity_mw) > 0.0001:
            continue
        allocation = {
            bidder["id"]: capacity
            for bidder, capacity in zip(active_bidders, candidate, strict=True)
            if capacity > 0
        }
        candidates.append(score_allocation(scenario, allocation))
    return candidates


def _run_id(scenario: dict[str, Any]) -> str:
    payload = json.dumps(scenario, sort_keys=True).encode("utf-8")
    return f"v0-baseline-{hashlib.sha256(payload).hexdigest()[:8]}"


def _allocation_artifact(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": run["run_id"],
        "scenario_id": run["scenario_id"],
        "mechanism": run["mechanism"],
        "allocation": run["allocation"],
        "capital_impact": run["capital_impact"],
    }


def _payments_artifact(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": run["run_id"],
        "scenario_id": run["scenario_id"],
        "payments": run["payments"],
    }


def _receipts_artifact(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": run["run_id"],
        "scenario_id": run["scenario_id"],
        "receipts": run["receipts"],
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
