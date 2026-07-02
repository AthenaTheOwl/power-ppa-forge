from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .models import ScenarioValidationError, canonical_scenario_path, load_scenario, repo_root
from .simulator import run_simulation, write_report, write_run_artifacts


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "show":
            return run_show(args.run)

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


def run_show(run_dir: Path) -> int:
    """Print a readable, ranked view of the committed run — no args, read-only, offline."""
    allocation_path = run_dir / "allocation.json"
    payments_path = run_dir / "payments.json"
    receipts_path = run_dir / "receipts.json"
    if not allocation_path.is_file() or not payments_path.is_file():
        print(
            f"NO_RUN: no committed run under {run_dir} — "
            "run `python -m power_ppa_forge simulate` first",
            file=sys.stderr,
        )
        return 1

    # A run dir can exist with truncated or hand-edited artifacts; surface that
    # as an actionable message instead of a raw decoder/key traceback.
    try:
        allocation = json.loads(allocation_path.read_text(encoding="utf-8"))
        payments = json.loads(payments_path.read_text(encoding="utf-8"))["payments"]
        receipts = (
            json.loads(receipts_path.read_text(encoding="utf-8"))["receipts"]
            if receipts_path.is_file()
            else []
        )
        alloc = allocation["allocation"]
        capital = allocation["capital_impact"]
    except (json.JSONDecodeError, KeyError) as exc:
        print(
            f"BAD_RUN: {run_dir} has corrupt or incomplete artifacts ({exc}) — "
            "re-run `python -m power_ppa_forge simulate`",
            file=sys.stderr,
        )
        return 1

    won = sorted(payments, key=lambda p: p["allocated_mw"], reverse=True)
    allocated_mw = sum(p["allocated_mw"] for p in won)
    lost = [r for r in receipts if not r["won"]]

    print(f"power-ppa-forge - multi-buyer PPA syndication, run {allocation['run_id']}")
    print(f"scenario {allocation['scenario_id']} | mechanism {allocation['mechanism']}\n")
    print(
        f"{allocated_mw:.0f} MW allocated across {len(won)} winning offtaker(s); "
        f"{len(lost)} offtaker(s) cleared no capacity. "
        f"portfolio complementarity {alloc['complementarity_score']:.3f} "
        "(1.0 = perfectly flat combined load).\n"
    )

    header = f"{'offtaker':<20} {'allocated':>10} {'clearing price':>16} {'annual payment':>16}"
    print(header)
    print("-" * len(header))
    for p in won:
        print(
            f"{p['offtaker_id']:<20} "
            f"{p['allocated_mw']:>8.0f}MW "
            f"${p['payment_per_mwh_usd']:>11.2f}/MWh "
            f"${p['annual_payment_musd']:>12.1f}M/yr"
        )
    for r in lost:
        print(f"{r['offtaker_id']:<20} {'0MW':>10} {'(no clear)':>16} {'-':>16}")

    print(
        f"\ncapital headline: bounded-leak Vickrey cuts required equity from "
        f"{capital['bilateral_nda_required_equity_share'] * 100:.0f}% to "
        f"{capital['bounded_leak_required_equity_share'] * 100:.0f}% "
        f"({capital['equity_share_delta_percentage_points']:.0f} pts) on a "
        f"${capital['project_cost_musd'] / 1000:.1f}B project - "
        f"${capital['equity_reduction_musd']:.0f}M less equity to syndicate (notional v0.1)."
    )
    print(
        "receipts disclose only id, win/loss, allocation, payment, and aggregate "
        "complementarity - never bid prices or load shapes."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m power_ppa_forge")
    subcommands = parser.add_subparsers(dest="command", required=True)

    show = subcommands.add_parser(
        "show", help="print a readable ranked view of the committed run"
    )
    show.add_argument(
        "--run",
        default=repo_root() / "runs" / "v0_baseline",
        type=Path,
        help="run directory; defaults to the committed v0 baseline run",
    )

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
