# Completion audit against the initial protocol

All three objectives in [PROTOCOL.md](PROTOCOL.md) are achieved at their stated
scope. The spatial noise requirement was retained throughout; no failed search
was relabelled an impossibility theorem.

| Objective | Result | Required evidence |
|---|---|---|
| Seven rows at L2 sensor radius 1e-7 and source error below 0.001 | Certified rows 488,490,497,500,504,508,510; error below 0.000998507 | All 231 cases cover [1,2]; 3,391 exact records; complete model error; separate review controls |
| Verify normalization from raw data | Exact quartic multiplier certificate gives actual physical error charge without source amplitude or target | 72 raw cases, all old/new profiles, eight tests, independent raw-fixture and scalar audits |
| Weighted drift-family approximation | Uniform unknown-phase/frequency bound over 2,021 times tighter than the pointwise bound | 24 rational approximants, six complete moments, three-precision replay, independent moment audit |
| Demonstrate arithmetic recovery | All 49 unknown integers recovered in both designs at drift amplitude 20,000 | Complete arithmetic tails retained; actual normal residual and 320-bit data/proposal replay; 98 rounding gates |
| Keep the paths aligned | Unchanged general theorem accepts all new consequences | 3,509 common gates plus 72 normalization packets |
| Preserve history | All five completed packages unchanged | 388 historical hashes |

The result does not assert that seven is minimum, that every seven-row bank
works, or that the weighted approximants are optimal. Physical sensor and
drift-family bounds are model/calibration premises. Exact timing, the spatial
two-mode source class and the arithmetic coefficient envelope remain explicit.
The new normalization computation discharges an
arithmetic error allowance; it does not validate an approximate clock.

There are 23 focused tests, alongside larger exact checks and outward model
reconstructions. Independent review found no mathematical blocker. The two
minor implementation review notes were addressed and rechecked. The root
[validation record](VALIDATION.json) is authoritative about the work performed.

The next objectives in [REPORT.md](REPORT.md) are further research, not missing
steps in the guarantees delivered by this phase. No empirical calibration,
external peer review, formal proof-assistant verification or public release is
claimed.
