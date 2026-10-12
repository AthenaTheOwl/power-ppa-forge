# Spec 0003 acceptance

The curtailment term is accepted when:

- `python -m power_ppa_forge simulate --scenario scenarios/v0_1gw_3offtakers.json --out <tmp>`
  matches `runs/v0_baseline` with `diff -r` printing nothing.
- `python -m power_ppa_forge simulate --scenario scenarios/v0_1gw_3offtakers_curtail.json --out runs/v0_curtail`
  exits 0.
- `python -m pytest tests/test_curtailment.py -q` passes.
- `python scripts/check_notional_disclosure.py` exits 0.
