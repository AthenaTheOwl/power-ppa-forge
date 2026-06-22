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
