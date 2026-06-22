from __future__ import annotations

import json
from itertools import product
from pathlib import Path
from typing import Any


CANONICAL_SCENARIO = Path("scenarios/v0_1gw_3offtakers.json")


class ScenarioValidationError(ValueError):
    """Raised when a scenario does not match the v0.1 data contract."""


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def canonical_scenario_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / CANONICAL_SCENARIO


def load_scenario(path: str | Path | None = None) -> dict[str, Any]:
    scenario_path = Path(path) if path is not None else canonical_scenario_path()
    try:
        data = json.loads(scenario_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ScenarioValidationError(f"scenario not found: {scenario_path}") from exc
    except json.JSONDecodeError as exc:
        raise ScenarioValidationError(f"scenario is not valid JSON: {scenario_path}: {exc}") from exc

    validate_scenario(data)
    return data


def validate_scenario(data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ScenarioValidationError("scenario root must be an object")

    for key in ("scenario_id", "schema_version", "asset", "auction", "offtakers", "capital_case"):
        if key not in data:
            raise ScenarioValidationError(f"missing required field: {key}")

    asset = _object(data["asset"], "asset")
    auction = _object(data["auction"], "auction")
    offtakers = data["offtakers"]
    capital_case = _object(data["capital_case"], "capital_case")

    capacity_mw = _positive_number(asset.get("capacity_mw"), "asset.capacity_mw")
    _positive_number(asset.get("capacity_factor"), "asset.capacity_factor")
    _positive_number(asset.get("target_dscr"), "asset.target_dscr")
    _positive_number(asset.get("project_cost_usd_billion"), "asset.project_cost_usd_billion")

    tranche_options = auction.get("tranche_options_mw")
    if not isinstance(tranche_options, list) or not tranche_options:
        raise ScenarioValidationError("auction.tranche_options_mw must be a non-empty list")
    tranche_values = [_positive_number(value, "auction.tranche_options_mw[]") for value in tranche_options]
    if any(value > capacity_mw for value in tranche_values):
        raise ScenarioValidationError("auction tranche cannot exceed asset capacity")

    _positive_number(auction.get("complementarity_weight"), "auction.complementarity_weight")

    if not isinstance(offtakers, list) or not offtakers:
        raise ScenarioValidationError("offtakers must be a non-empty list")

    seen_ids: set[str] = set()
    max_capacities: list[float] = []
    for index, offtaker in enumerate(offtakers):
        bidder = _object(offtaker, f"offtakers[{index}]")
        bidder_id = _text(bidder.get("id"), f"offtakers[{index}].id")
        if bidder_id in seen_ids:
            raise ScenarioValidationError(f"duplicate offtaker id: {bidder_id}")
        seen_ids.add(bidder_id)

        max_capacity = _positive_number(bidder.get("max_capacity_mw"), f"{bidder_id}.max_capacity_mw")
        _positive_number(bidder.get("bid_price_per_mwh"), f"{bidder_id}.bid_price_per_mwh")
        shape = bidder.get("load_shape")
        if not isinstance(shape, list) or len(shape) != 24:
            raise ScenarioValidationError(f"{bidder_id}.load_shape must contain 24 hourly values")
        for hour, value in enumerate(shape):
            _positive_number(value, f"{bidder_id}.load_shape[{hour}]")
        max_capacities.append(max_capacity)

    if sum(max_capacities) < capacity_mw:
        raise ScenarioValidationError("offtaker max capacities cannot cover asset capacity")
    if not _has_exact_capacity(capacity_mw, max_capacities, tranche_values):
        raise ScenarioValidationError("tranche options cannot exactly allocate asset capacity")

    baseline = _positive_number(
        capital_case.get("bilateral_nda_required_equity_share"),
        "capital_case.bilateral_nda_required_equity_share",
    )
    mechanism = _positive_number(
        capital_case.get("bounded_leak_required_equity_share"),
        "capital_case.bounded_leak_required_equity_share",
    )
    if mechanism > baseline:
        raise ScenarioValidationError("bounded-leak equity share cannot exceed baseline equity share")


def _has_exact_capacity(capacity_mw: float, max_capacities: list[float], tranches: list[float]) -> bool:
    options_by_bidder = []
    for max_capacity in max_capacities:
        options_by_bidder.append([0.0] + [value for value in tranches if value <= max_capacity])
    return any(abs(sum(candidate) - capacity_mw) < 0.0001 for candidate in product(*options_by_bidder))


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ScenarioValidationError(f"{field} must be an object")
    return value


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ScenarioValidationError(f"{field} must be a non-empty string")
    return value


def _positive_number(value: Any, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise ScenarioValidationError(f"{field} must be a positive number")
    return float(value)
