# Path 2 preregistration

Frozen before the new numerical search, 2026-09-05.

## Model and comparison

Three labelled known prime axes `(2,3,5)`, four exponent states `0,1,2,3` per axis; each factor is an arbitrary point of the closed probability simplex. A source is the tensor product of the three factors. Every reading is the exact complex harmonic sum at one fixed, nonadaptive positive time; normalization is known. The source metric is the Euclidean direct sum of factor coordinates. The observation metric is the unnormalized Euclidean norm of six complex readings, isometrically realified.

Count six readings once each. Compare maximum positive observation time, certified global factor secant floor, and deterministic clock tolerance. Freeze additive data noise as an adversarial Euclidean radius; it is not per-reading variance. Common clock uncertainty is one unknown absolute offset shared across readings, `|delta t| <= 1/1000`. A robustness proof uniform over the larger independent-offset box is acceptable, but no covariance or independent-noise interpretation will be made. Distinguish a lower floor for each known perturbed schedule from inference with an unknown clock offset; the latter must include finite clock drift as nuisance.

The baseline is AO VI's six rational readings `(90540.692,220023.423,27819.627,94581.299,18084.130,75110.287)` with maximum 220023.423 and published factor floor greater than 0.7901. Reconstruct that floor before comparing. Evaluate both schedules using the same new sufficient bound too, to distinguish analytical gains from design gains.

## Tractable target

Seek a new six-reading schedule with maximum time at most 10,000, certified global factor floor at least 1/2, and the above nonzero clock box. Failing that, preserve the attempted certificate and report the strongest proven count/time/clock/floor tradeoff found. No claim of shortest possible time is planned without a separate lower bound.

## Candidate method and controls

Use a centered characteristic polynomial to reduce derivative error constants. Bound deviation from an ideal factor DFT by a row-specific nonnegative six-by-three block majorant; bound its spectral norm by an exact rational or interval Gram row-sum estimate. Search time rows near their assigned ideal phases, evaluate candidate floors in floating point, round chosen times to exact rationals, and reconstruct all phases and decisive bounds with Arb. Floating ranks or a sampled Jacobian do not certify a global inverse.

Run small pilots before broader scans. Freeze the selected rational witness before independent checks. Required controls: independently check the bound against the old AO VI bound; zero/duplicate/bad schedules must not obtain a positive certificate; derivative and secant samples are implementation regressions only; verify clock perturbation endpoints and simplex boundary examples. Include exact boundary cases of the analytic theorem and a separate review of local versus global identification.

## Validation standard

The analytic argument must include definitions, all quantifiers, and complete proof. The checker must reconstruct harmonic phases from prime logarithms and times, not accept supplied matrices. Arb outward enclosures prove only finite inequalities. Record runtime versions and trusted components. Literature sources establish classical tools, not historical priority for this application. No sources outside this path directory will be edited.
