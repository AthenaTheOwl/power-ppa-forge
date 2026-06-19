# Acceptance — v0 Foundation

"v0 done" means the mechanism doc is published, the notional
benchmark runs end-to-end through the reference simulator, the
paper draft compiles, and the notional-disclosure gate refuses
prose that smuggles unsupported numbers.

## Commands a reviewer must be able to run

```bash
python -m pip install -e .[dev]

python -m power_ppa_forge validate scenarios/v0_1gw_3offtakers.json

python -m power_ppa_forge simulate \
  --scenario scenarios/v0_1gw_3offtakers.json \
  --mechanism multi-buyer-vickrey-bounded-leak \
  --out runs/v0_baseline/

python -m power_ppa_forge capital-impact \
  --run runs/v0_baseline/ \
  --baseline bilateral-nda \
  --out reports/capital_impact.md

cd paper && pdflatex power-ppa-forge.tex
```

## Gates that must pass

- `python -m pytest` exits 0, including the strategyproofness
  regression test.
- `python scripts/voice_lint.py paper/ mechanism/ README.md` exits 0.
- `python scripts/validate_schemas.py scenarios/ runs/` exits 0.
- `python scripts/validate_leakage_bound.py
  mechanism/leakage_bounds.yaml` exits 0.
- `python scripts/check_notional_disclosure.py paper/` exits 0 —
  every number in the paper is either cited or flagged
  `(notional)`.

## Artifacts that must exist

- `mechanism/MECHANISM-v0.md` and `mechanism/leakage_bounds.yaml`.
- `scenarios/v0_1gw_3offtakers.json` — the notional benchmark.
- `runs/v0_baseline/{allocation,payments,receipts}.json` —
  simulator output on the benchmark.
- `reports/capital_impact.md` — the headline equity-tranche delta.
- `paper/power-ppa-forge.pdf` — compiled draft.
- `decisions/DEC-PPF-001` and `DEC-PPF-002`.

## Out of scope for v0

- Real hyperscaler load profiles.
- Real project-finance numbers.
- Combinatorial-auction extensions.
- Production cryptography.
- Customer deployment.

## What "done" feels like

A mechanism-design academic reads `mechanism/MECHANISM-v0.md` and
agrees the construction is well-defined and the bounded-leakage
claim is provable. A project-finance reader reads the paper's
section 6 and recognizes the language — required equity tranche,
DSCR underwriting confidence. Both can re-run the simulator on the
published benchmark and reproduce the table. That is the bar.
