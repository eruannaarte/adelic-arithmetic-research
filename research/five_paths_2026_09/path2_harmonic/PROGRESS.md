# Development record

1. Reconstructed AO VI model, upper/lower proofs, old six-reading time/floor data. Froze metrics and targets before searching in `PREREGISTRATION.md`.
2. Derived centered phase constants `sqrt(5)` and `3` for four states, and a six-by-three row-specific derivative majorant. Small nonformal pilots found candidates in under a second; retained exact rational schedules in `inputs.json`.
3. Reproduced original AO VI artifact at 384 bits; independently reconstructed the old phase box and floor. Evaluated old and new schedules under the same improved majorant.
4. Certified three new schedules with nonzero absolute clock box .001. Derived separate finite shared-clock and affine-clock recovery bounds; no iid timing model introduced.
5. Proved the full-product local-stable count distinction and certified an actual five-reading interior differential minor. Included a truly blind six-reading resonant control and cubic small-time obstruction.
6. Full checker passes; 512-bit replay gives identical rational consequences; 15 focused tests pass. An independent audit found a missing nonnegative-noise input check, which was corrected with negative-noise/floor regressions. Canonical results were unaffected.

7. Independent audit completed with a pass for the declared model and no unresolved defect; see `AUDIT.md`. All 15 tests and full source-to-certificate reconstruction were independently rerun.

Remaining boundaries: no shortest-time theorem; no maximum clock tolerance; no efficient guaranteed global least-squares algorithm; no tail, unknown-prime, unknown-gain, or number-field extension. Those are outside the completed tractable target. Discovery figures are not mathematical proof. Package is ready for parent integration.
