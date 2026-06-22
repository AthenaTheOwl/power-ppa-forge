"""Compatibility model surface for the active-MVP factory contract."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapexPlan:
    scenario_id: str
    capacity_mw: int


@dataclass(frozen=True)
class FactorScore:
    name: str
    score: float


def rank_constraints(plan: CapexPlan) -> list[FactorScore]:
    return [
        FactorScore("contract-tenor", 0.7),
        FactorScore("buyer-surplus", min(1.0, plan.capacity_mw / 1000.0)),
    ]
