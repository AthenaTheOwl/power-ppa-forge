# AGENTS.md — power-ppa-forge

Operating contract for AI agents working in this repo. Conventions
match the rest of the AthenaTheOwl portfolio.

## What this repo is

A mechanism spec, a reference simulator, and a white paper for
multi-hyperscaler PPA coordination on long-duration generation. The
mechanism is the load-bearing artifact; the simulator exists to
prove the mechanism is implementable; the paper translates the
strategyproofness bound into capital-structure language a
project-finance reader recognizes.

This is research-shape work. The numbers in v0 are notional. The
mechanism, the bound, and the simulation framework are the real
deliverables.

## Roles you may see in tasks

| Role | What they do |
|---|---|
| `mechanism-author` | Maintains mechanism/MECHANISM-v0.md and the formal statement |
| `simulator-engineer` | Builds the reference simulator |
| `leakage-prover` | Writes and maintains the bounded-leakage proof |
| `project-finance-translator` | Writes the capital-structure-impact section of the paper |
| `scenario-author` | Authors typed notional scenarios |

These roles exist in spec ledger; not all are implemented in v0.

## Voice constraints

- The paper is the customer surface. Read it through voice_lint
  before each commit.
- No marketing words. The mechanism speaks for itself.
- No antithetical-reversal phrasing.
- Numbers in v0 are notional; the paper says so explicitly. Never
  let a notional number drift into prose framed as empirical.
- Cryptographic claims cite. Project-finance claims cite.

## Gates (will land in spec 0002)

```bash
python -m pytest
python scripts/voice_lint.py paper/ mechanism/ README.md
python scripts/validate_schemas.py scenarios/
python scripts/validate_leakage_bound.py mechanism/leakage_bounds.yaml
python scripts/check_notional_disclosure.py paper/
```

The `check_notional_disclosure.py` gate is the load-bearing
discipline check. Any number in the paper that lacks an "(notional)"
or empirical-source citation fails.

## Out of scope

- Production-deployment cryptography. v0 is reference-grade.
- Real customer engagement. The first artifact is the paper plus
  simulator; engagement is downstream.
- Forward-auction (English / Dutch) variants. Sealed-bid multi-buyer
  Vickrey-like only in v0.
- Settlement / payment rails. The mechanism produces an allocation;
  settlement is out-of-band.
- Cryptocurrency / on-chain anything.
