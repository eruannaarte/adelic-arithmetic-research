# Completion against the declared objectives

| Initial objective | Completed result | Evidence and limits |
|---|---|---|
| Improve the seven-row margin or test six rows under a fixed noise contract | Seven rows meet 1.4e-7 sensor radius at source accuracy below 0.001, exceeding the primary predeclared 1.1e-7 requirement | All 231 cases over complete time intervals; 861 cells / 3,743 records. Six rows were not searched; no minimality claim. [Spatial report](resolution/REPORT.md) |
| Declare amplitude/frequency and separate mismatch, then compare polynomial degree against the full budget | Continuous phase/frequency family, mismatch 1e-6, degrees 6/8/10/12, four frequency limits; 32 capacity and 40 error-planning rows | Complete-tail and Gram costs included. Future rows require new residual verification at most 1e-30. All eight actual inverses reconstructed. [Arithmetic report](noise/REPORT.md) |
| Explicit transfer for uncertain timing and model mismatch | Complete set-inclusion theorem; necessary/sufficient nuisance-annihilation condition; finite-grid affine-clock characterization; quantitative two-model specializations | Common logic preserves physical units and joint incidence. No independence or inferred calibration. [Proofs](framework/PROOFS.md) |
| Demonstrate useful consequences beyond terminology | A spatial profile with positive clock and generator error recovers twelve actual raw examples; degree-twelve arithmetic with positive clock and mismatch recovers 49 integers in both designs | Outward model/data reconstructions and independent consequence checks. Synthetic observations, not measured apparatus data. |
| Validate and preserve the research record | 24 focused tests, five independent audits, exact common gates, complete approximation/timing replays and higher-precision actual data/residual verification | 467 prior artifacts preserved; the index advances while all six preceding packages remain records. [Validation](VALIDATION.json) |

The key mathematical limitation is constructive: one arbitrarily small timing
spike can produce unbounded polynomial-nuisance leakage. The positive affine
result states exactly why this application's chosen clock family avoids it.
A failed sufficient coefficient gate, a failed search, and proved physical
ambiguity remain different claims.

No required objective is deferred. Tighter directional uncertainty bounds and
the optional six-row branch are subsequent research questions, not conditions
silently omitted from the completed claims.
