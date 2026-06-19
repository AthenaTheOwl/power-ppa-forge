# First PR (after scaffold)

The literal first PR after this v0 scaffold is PR 0002: the
mechanism doc, the scenario schema, the notional benchmark, and the
paper skeleton.

## Scope

One PR. No simulator code yet. The mechanism and the scenario shape
are load-bearing; PR 0003 implements against them.

## Files added

```
mechanism/MECHANISM-v0.md
mechanism/leakage_bounds.yaml
schemas/scenario.schema.json
schemas/run_report.schema.json
scenarios/v0_1gw_3offtakers.json
paper/power-ppa-forge.tex
paper/refs.bib
src/power_ppa_forge/__init__.py
src/power_ppa_forge/__main__.py
src/power_ppa_forge/cli.py
scripts/voice_lint.py
scripts/validate_schemas.py
scripts/validate_leakage_bound.py
scripts/check_notional_disclosure.py
tests/test_scenario_validates.py
tests/test_notional_disclosure.py
pyproject.toml
```

## Files changed

```
README.md         # "How to run" gets the validate command
AGENTS.md         # uncomment the gate block
```

## Why this scope

`mechanism/MECHANISM-v0.md` is the document the whole repo exists
to ship. It must read clearly enough that a mechanism-design
academic agrees the construction is well-defined and a project-
finance reader recognizes the consequences. Get it right first.

The notional benchmark `v0_1gw_3offtakers.json` is hand-authored to
exercise: three offtakers with deliberately different load profiles
(one baseload, one peaking, one shoulder), a 1-GW asset with four
tranche sizes (25/50/75/100%), and one COD year. Small enough to
reason about by hand; large enough to expose the
load-profile-complementarity scoring rule.

The paper skeleton and refs.bib pin the citation graph now so PR
0004's draft cannot quietly drift from the published primitives.

## Verification

```bash
python -m pip install -e .[dev]
python -m pytest
python scripts/voice_lint.py README.md AGENTS.md paper/ mechanism/
python scripts/validate_schemas.py scenarios/v0_1gw_3offtakers.json
python scripts/check_notional_disclosure.py paper/
cd paper && pdflatex -interaction=nonstopmode power-ppa-forge.tex
```

All five exit 0. The paper PDF renders the abstract and section
headings cleanly.

## Out of scope (deferred to PR 0003)

- The reference simulator.
- Strategyproofness regression tests against the benchmark.
- The capital-impact calculator.
- Paper sections 4-8.

## Decision record

PR 0002 lands `decisions/DEC-PPF-000-mechanism-doc-before-code.md`
naming why the mechanism is fully specified in prose before any
simulator code lands — the construction's correctness depends on
the formal statement, not on what a simulator happens to do.
