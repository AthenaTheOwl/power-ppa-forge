# Tasks — Foundation

## PR 0002 — mechanism doc, scenario schema, paper skeleton

- [ ] Author `mechanism/MECHANISM-v0.md` matching R-PPF-001 through
      R-PPF-003.
- [ ] Author `mechanism/leakage_bounds.yaml`.
- [ ] Write `schemas/scenario.schema.json` matching R-PPF-004.
- [ ] Author `scenarios/v0_1gw_3offtakers.json` matching R-PPF-005.
- [ ] Add `paper/power-ppa-forge.tex` skeleton with section
      headings.
- [ ] Add `paper/refs.bib` seeded with Vickrey 1961,
      Ausubel-Milgrom 2002, the ScienceDirect Jan 2026 PSI paper.
- [ ] Add `scripts/voice_lint.py`, `scripts/validate_schemas.py`,
      `scripts/validate_leakage_bound.py`, and
      `scripts/check_notional_disclosure.py`.
- [ ] Add `pyproject.toml` with `sealed-bid-sourcing` dep.

## PR 0003 — reference simulator

- [ ] Implement `src/power_ppa_forge/mechanism/scoring.py` for the
      load-profile-complementarity-weighted scoring rule.
- [ ] Implement `src/power_ppa_forge/mechanism/allocation.py`.
- [ ] Implement `src/power_ppa_forge/mechanism/payments.py` for the
      Vickrey-extension counterfactual computation.
- [ ] Implement `src/power_ppa_forge/simulator.py`.
- [ ] Write `tests/test_strategyproofness_regression.py` (each
      bidder cannot improve by deviating on the v0 benchmark).
- [ ] Write `tests/test_leakage_audit.py` (only bounded info
      leaks).

## PR 0004 — paper draft v0

- [ ] Fill paper sections 1-5 (intro, mechanism, threat model,
      simulator, notional benchmark).
- [ ] Run simulator on `v0_1gw_3offtakers.json`; produce the
      numerical table for section 5.
- [ ] Fill section 6 (capital-structure consequence) — compute
      delta in required equity tranche under v0 mechanism vs.
      bilateral-NDA baseline.
- [ ] Fill sections 7-8 (limitations, future work).
- [ ] Add `decisions/DEC-PPF-001-multi-tranche-not-combinatorial.md`.
- [ ] Add `decisions/DEC-PPF-002-notional-not-empirical-v0.md`.
- [ ] Tag `v0.1`.
