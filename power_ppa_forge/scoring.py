"""Compatibility report surface for the active-MVP factory contract."""

from __future__ import annotations

import json
from pathlib import Path

from power_ppa_forge.model import FactorScore


def write_report(scores: list[FactorScore], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(score.__dict__, sort_keys=True) for score in scores) + "\n",
        encoding="utf-8",
    )
    return path
