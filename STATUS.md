# Status

## Current state

- v0.1 ships a canonical notional scenario, a deterministic reference simulator, and a checked-in capital-impact report.
- The first user action is `python -m power_ppa_forge validate`; it validates the canonical scenario with no flags.
- The CLI can validate, simulate, and regenerate the capital-impact report from the checked-in scenario.
- The repo includes a product brief, system map, mechanism note, leakage-bound ledger, and specs/0002 design ledger.

## Known limits

- All scenario, allocation, payment, and capital-structure values are notional.
- The simulator is reference-grade and uses plain JSON artifacts rather than production cryptography.
- The v0.1 allocation search is exhaustive over the published tranche set; it is not a full combinatorial-auction solver.
- Settlement, payment rails, real load profiles, and customer-specific underwriting are out of scope.

## Next feature queue

- Add a formal proof appendix for the bounded-leakage claim.
- Add scenario variants for two-offtaker and four-offtaker syndication.
- Replace placeholder project-finance references with a reviewed bibliography.
- Add receipt signing once the simulator artifact format stabilizes.
