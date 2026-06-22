from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from power_ppa_forge.models import ScenarioValidationError, load_scenario  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    targets = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])]
    if not targets:
        targets = [Path("scenarios")]

    failures: list[str] = []
    checked = 0
    for file_path in _json_files(targets):
        checked += 1
        try:
            json.loads(file_path.read_text(encoding="utf-8"))
            if "scenarios" in file_path.parts:
                load_scenario(file_path)
        except (json.JSONDecodeError, ScenarioValidationError) as exc:
            failures.append(f"{file_path}: {exc}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"schema validation OK: {checked} JSON file(s)")
    return 0


def _json_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if not path.exists():
            continue
        if path.is_dir():
            files.extend(sorted(child for child in path.rglob("*.json") if child.is_file()))
        elif path.suffix.lower() == ".json":
            files.append(path)
    return files


if __name__ == "__main__":
    raise SystemExit(main())
