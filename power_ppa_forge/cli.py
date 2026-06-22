from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .models import ScenarioValidationError, canonical_scenario_path, load_scenario
from .simulator import run_simulation, write_report, write_run_artifacts


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "validate":
            scenario = load_scenario(args.scenario)
            print(f"OK: {scenario['scenario_id']} validates")
            return 0

        if args.command == "simulate":
            scenario = load_scenario(args.scenario)
            run = run_simulation(scenario)
            write_run_artifacts(run, args.out)
            print(json.dumps({"run_id": run["run_id"], "out": str(args.out)}, sort_keys=True))
            return 0

        if args.command == "capital-impact":
            scenario = load_scenario(args.scenario)
            run = run_simulation(scenario)
            write_run_artifacts(run, args.run)
            write_report(run, args.out)
            print(json.dumps({"run_id": run["run_id"], "report": str(args.out)}, sort_keys=True))
            return 0

    except ScenarioValidationError as exc:
        print(f"SCENARIO_ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"IO_ERROR: {exc}", file=sys.stderr)
        return 3

    parser.print_help(sys.stderr)
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m power_ppa_forge")
    subcommands = parser.add_subparsers(dest="command", required=True)

    validate = subcommands.add_parser("validate", help="validate a scenario")
    validate.add_argument(
        "scenario",
        nargs="?",
        default=canonical_scenario_path(),
        type=Path,
        help="scenario path; defaults to the canonical v0.1 fixture",
    )

    simulate = subcommands.add_parser("simulate", help="run the reference simulator")
    simulate.add_argument(
        "--scenario",
        default=canonical_scenario_path(),
        type=Path,
        help="scenario path; defaults to the canonical v0.1 fixture",
    )
    simulate.add_argument(
        "--mechanism",
        default="multi-buyer-vickrey-bounded-leak",
        help="accepted for compatibility; v0.1 has one mechanism",
    )
    simulate.add_argument(
        "--out",
        default=Path("runs/v0_baseline"),
        type=Path,
        help="directory for allocation, payments, and receipts JSON",
    )

    capital = subcommands.add_parser("capital-impact", help="write the capital-impact report")
    capital.add_argument(
        "--scenario",
        default=canonical_scenario_path(),
        type=Path,
        help="scenario path; defaults to the canonical v0.1 fixture",
    )
    capital.add_argument(
        "--run",
        default=Path("runs/v0_baseline"),
        type=Path,
        help="directory for regenerated run artifacts",
    )
    capital.add_argument(
        "--baseline",
        default="bilateral-nda",
        help="accepted for compatibility; v0.1 reports against bilateral-nda",
    )
    capital.add_argument(
        "--out",
        default=Path("reports/capital_impact.md"),
        type=Path,
        help="report path",
    )

    return parser
