from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_ALLOWED = {
    "scenario_id",
    "offtaker_id",
    "won",
    "allocation_mw",
    "own_payment_per_mwh_usd",
    "aggregate_complementarity_score",
}

REQUIRED_FORBIDDEN = {
    "bid_price_per_mwh",
    "load_shape",
    "max_capacity_mw",
    "counterfactual_allocations",
}


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    path = Path(args[0]) if args else Path("mechanism/leakage_bounds.yaml")
    text = path.read_text(encoding="utf-8")
    allowed = _read_list(text, "allowed_disclosures")
    forbidden = _read_list(text, "forbidden_fields")

    missing_allowed = REQUIRED_ALLOWED - allowed
    missing_forbidden = REQUIRED_FORBIDDEN - forbidden
    if missing_allowed or missing_forbidden:
        if missing_allowed:
            print(f"missing allowed disclosures: {sorted(missing_allowed)}", file=sys.stderr)
        if missing_forbidden:
            print(f"missing forbidden fields: {sorted(missing_forbidden)}", file=sys.stderr)
        return 1

    print("leakage bound OK")
    return 0


def _read_list(text: str, section: str) -> set[str]:
    values: set[str] = set()
    active = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith(f"{section}:"):
            active = True
            continue
        if active and line and not line.startswith("  - "):
            break
        if active and line.startswith("  - "):
            values.add(line[4:].strip())
    return values


if __name__ == "__main__":
    raise SystemExit(main())
