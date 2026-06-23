from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_default_validate_command_works_from_checkout() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "power_ppa_forge", "validate"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "v0_1gw_3offtakers validates" in result.stdout


def test_show_command_prints_ranked_readable_view() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "power_ppa_forge", "show"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr
    out = result.stdout
    # reads the committed run artifact
    assert "v0-baseline-3eac2d52" in out
    assert "v0_1gw_3offtakers" in out
    # ranked table of offtakers with allocation + clearing price
    assert "mesa_ai" in out
    assert "northstar_compute" in out
    assert "harbor_cloud" in out
    assert "MW" in out
    assert "/MWh" in out
    # the capital headline finding
    assert "capital headline" in out
    assert "42%" in out and "34%" in out
    # winning offtakers ranked above the non-clearing one
    assert out.index("mesa_ai") < out.index("harbor_cloud")
