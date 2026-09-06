# Adaptive preparation research ledger

Baseline: `research/five_paths_2026_09/path1_preparation/` is preserved. All computations use the same dimensionless double-pendulum model, seven available scalar readings, launch costs 7/2, 9/4, 5/2, unit total budget, and one global finite clock parameter. Preparation is a bounded unknown launch error, shared by every reading of that launch. It is not an observed input or an additional fitted source coordinate.

## Cycle 1 — preregistered objective

**Question.** Can retaining the signed preparation-to-reading map enlarge the useful certified preparation region, rather than merely reducing the earlier scalar Gronwall constant?

**New construction.** Integrate all four launch-coordinate variational equations together with the two physical-source derivatives, over finite source and preparation boxes. For a fixed source decoder B, form the interval matrix B P before taking absolute values; use its induced box support function in a finite nonlinear feasible-set diameter theorem.

**Fixed primary experiment, recorded before computation.** Source box `|u|,|v|,|epsilon| <= 1/10000`; four-coordinate preparation box `rho = 1/1000000`; weighted adversarial observation noise radius `eta = 1/10000000`; useful source diameter threshold `1/10000`. Compare the existing selected A+B shares `(2/3,1/3,0)`, uniform A+B `(1/2,1/2,0)`, and uniform A+B+C `(1/3,1/3,1/3)` without changing sensor access, group charges, or noise semantics. The baseline preparation radius is `1/10000000`.

**Validation plan.** Outward Arb Picard–Taylor tubes for the 31-coordinate augmented ODE; standard-library rational consequence checker; derivative checks against independently integrated mechanical equations; exact artifact replay; negative tests for omitted launch-sharing, source/clock incidence, malformed intervals, and contraction failure. Compare the signed shared-preparation bound with the conservative absolute-before-projection bound using the same new sensitivity enclosures. A failed target is an evidence-backed limitation, not an impossibility result. Later objectives will be chosen only after this cycle has a certified result.

### Cycle 1 outcome and successor decision

The source replay and six independent/control tests passed (`cycle1_validation.log`). The signed shared-preparation theorem certifies rho=10^-6 at the original eta=10^-7: diameters are 1.640686e-5 (selected A+B), 1.600212e-5 (uniform A+B), and 2.112889e-5 (uniform A+B+C), rounded upward. These are smaller than the baseline bounds at rho=10^-7. With the same new sensitivity enclosures, discarding signs before projection gives 2.962140e-5, 3.021550e-5, and 3.556746e-5. The improvement is therefore supported by a changed treatment of the shared nuisance, not a smaller declared error. Unknown preparation remains nonzero and unobserved. The finite source box, not a point derivative, is certified.

The uniform A+B result beats the historically selected decoder in this preparation-dominated setting. That makes the next question whether a decoder designed directly for finite bounded preparation can materially beat weighted least squares, whose original motivation was a different local information criterion.

## Cycle 2 — preregistered objective (after Cycle 1 validation)

**Question.** Can a single fixed preparation-aware decoder, synthesized by a convex certificate objective, certify the larger four-coordinate box rho=1/100000 at eta=1/10000000 and diameter target delta=1/10000, when the source box and sensor/budget contracts stay unchanged?

**New construction.** Derive a convex sufficient feasibility objective in each row of a rational left inverse B. It includes the full finite-source derivative deviation, the signed shared-preparation sensitivity, and a conservative upper bound on weighted noise amplification. Search by a linear epigraph program, then project the candidate to BA=I in exact rational arithmetic and independently certify it with the tighter quadratic noise gain. Compare the synthesized and original least-squares decoders for all three fixed budget designs. Numerical optimization supplies candidates only; no optimizer success flag has proof authority and no global minimax claim will be made.

**Decision rule.** The preregistered 100-times-baseline preparation box is the primary test. A failure will be recorded; any revised box will be separately declared and justified. Checks include source replay, BA=I, budget conservation, exact finite sufficient inequalities, a deliberately invalid rounded decoder, and a control in which nominal preparation cancellation alone fails because finite Jacobian uncertainty is omitted. The successor will be chosen only after this result is proved and checked.

### Cycle 2 primary result and declared revision

The rho=10^-5 primary target fails the exact target inequalities for all three synthesized decoders. Their scalar diameter bounds are approximately 1.344731e-4, 1.342199e-4, and 1.344709e-4, while the original least-squares decoders give 1.529772e-4, 1.509572e-4, and 1.980949e-4. This is a limitation of these certified candidates, not proof that the original target is impossible.

**Revision recorded before its check:** keep the full rho=10^-5 derivative enclosures and the already synthesized decoders, but test the smaller admissible subbox rho=7*10^-6. Derive each decoder's exact preparation/noise half-plane boundary using its individual row-contraction bounds rather than replacing them all by their maximum. Compare that boundary with least squares under identical large-box enclosures. The revision is part of Cycle 2's synthesis investigation, not an additional cycle.

### Cycle 2 verified outcome and successor decision

`cycle2_validation.log` records six passing checks, including fresh nonlinear replay, exact decoder/source binding, both sides of each calibration boundary, and a finite-preparation counterexample to nominal cancellation. The revised rho=7*10^-6 target passes for all synthesized decoders and fails the same sufficient row criterion for every least-squares control. The exact sufficient preparation limits range from 7.6644e-6 to 7.6835e-6. The primary rho=10^-5 failure remains visible.

The remaining gap to rho=10^-5 and the explicit unequal coordinate gains suggest that equal accuracy in all four launch coordinates is wasteful. The successor will therefore investigate which preparation coordinates actually require tighter calibration, without changing sensors, charges, or observation-noise assumptions.

## Cycle 3 — preregistered objective (after Cycle 2 validation)

**Question.** What is the largest-volume anisotropic preparation box supported by the new finite certificate at target delta=10^-4 and eta=10^-7, and does it materially relax calibration requirements compared with one isotropic radius?

**Fixed scope.** Use the already synthesized fixed decoders for selected A+B and uniform A+B, with exactly the same five local readings and charges. Optimize the eight per-launch coordinate radii, each capped by the already validated outer radius 10^-5; preparation remains one bounded unknown vector per launch. Do not add observation of preparation. The full source box stays [-10^-4,10^-4]^3. C is inactive in both comparisons and is not included as a spurious volume dimension.

**New theorem/construction.** The finite inverse theorem defines a polytope of admissible calibration radii. Maximize the product of its eight radii, using numerical convex optimization only to obtain candidates. Certify the resulting rational box directly; independently upper-bound the volume of *every* feasible box using a rational nonnegative dual combination and weighted AM–GM. This can prove closeness to the best box supported by this fixed finite certificate, although it cannot establish optimality for the true inverse problem or over all decoders/designs.

**Success targets and controls.** Aim for geometric mean radius at least 8*10^-6 and achieved volume at least 99.9% of the rigorous global upper bound. Record failures if either target is unmet. Check all calibration half-planes, outer-box caps, dual positivity, the AM–GM algebra, and constructed violations beyond a tight face; retain the isotropic calibration boundary as a control. No hardware measurements exist, so the result will be labeled a mathematical calibration requirement. A fourth research cycle will not be started in this owned chain.

### Cycle 3 verified outcome and stopping point

Both preregistered targets pass. The selected A+B box permits seven radii at 10^-5 and B.theta1 at 6.270072214e-6; uniform A+B permits B.theta1 at 6.300536639e-6 with the other seven at 10^-5 up to downward rounding. Geometric means are approximately 9.4332e-6 and 9.4389e-6. The volumes are 5.2655 and 5.1869 times the corresponding best isotropic box volumes admitted by these fixed finite certificates. Exact rational primal/dual comparisons certify volume ratios above 0.99999999998 and 0.99999999946 to their global upper bounds.

All five Cycle 3 tests pass (`cycle3_validation.log`), including the binding face, outer cap, dual/coordinate tampering, and a sharp AM–GM unit-cube control. The unit-cube control initially exposed a zero-row division in the isotropic diagnostic; the checker now treats a zero constraint row as inactive and checks the general matrix/cap hypotheses. Canonical certificate values were unaffected. This repair and verification are part of Cycle 3, not counted as research cycles.

**Next question, recorded but not executed or counted:** can actual preparation instrumentation demonstrate the needed joint calibration bounds, especially for B.theta1, and can independently established preparation correlations enlarge the admissible region? No such measurements are available. A mathematical successor could derive outer-enclosure/domain improvements or new equal-cost launch candidates, but that would require a new objective and certificate; this owned chain stops after exactly three substantive adaptive cycles.
