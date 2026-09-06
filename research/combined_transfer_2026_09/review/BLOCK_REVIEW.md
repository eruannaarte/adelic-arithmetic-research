# Independent review of the complete multiplicative-block clock bound

**Outcome: the reviewed proof and demonstrated h=120 consequences pass.**
No mathematical defect was found in the complete-orbit construction, the
actual coefficient-envelope substitution, or the joint recovery budget.
This review did not modify the block package or any predecessor artifact.

## What was checked mathematically

Every positive integer has exactly one representation `n=2^k m` with `m`
odd. The finite block retains `k=0,...,31` inside each such orbit; the argument
then sums over **all** odd `m`. The `m=1` orbit is included and its `n=1`
derivative term vanishes because `log(1)=0`.

The Gram bound is applied to the actual coefficients before envelope
replacement. Its bound by `Lambda sum |c_k|^2` is valid for arbitrary complex
coefficient vectors: every off-diagonal product is bounded in absolute value,
and `2|c_k c_l| <= |c_k|^2+|c_l|^2` charges each row by at most twice the sum
of the lag bounds. Replacing each squared magnitude by its envelope is then
monotone. Independently vanishing admissible coefficients therefore cause no
problem. The proof does not impose envelope multiplicative ratios on the
actual unknown coefficients.

The omitted-valuation bounds can be checked against exact full sums, using
the negative-binomial generating function and its derivative:

\[
\sum_{k\ge0}{\binom{k+13}{13}\over4^k}=(4/3)^{14},\qquad
\sum_{k\ge0}{k\binom{k+13}{13}\over4^k}
={14\over3}(4/3)^{14}.
\]

Subtracting the 32 retained terms gives exact rational omitted masses. Both
are positive and below the claimed geometric bounds. This independently
confirms that the finite block length does not restrict the source class.

The complete odd-integer sums are also correct. Differentiating
`sum_(m odd) m^-s=(1-2^-s) zeta(s)` gives at `s=2` the factor
`3L/4-(log 2)Z/4`; the fourteen-factor product produces the stated `O1`.
The producer's use of a lower `Z` bound in the subtractive term preserves its
outward direction. The elementary series and the consumer's separate outward
zeta-derivative route cover every odd starting integer.

The exact exponential Taylor remainder gives
`|exp(-iz)-1+iz| <=z^2/2` for real `z`. Absolute convergence of the complete
divisor-envelope second derivative justifies summing it. Maximizing the fourth
moment at the same four clock corners covers the full nonlinear clock
rectangle. There is one shared slope and offset within each explanation;
different possible explanations need not share their clock parameters.

Affine-clock substitution preserves the unbounded polynomial nuisance space.
The sinusoidal frequency enlargement and arbitrary phase, sensor radius,
separate mismatch radius, digital correction, complete arithmetic tail and
actual normal residual are charged in the same budget. A residual certifies
the numerical solve, not membership in those physical uncertainty families.

## Fresh computational checks

The [review script](block_review.py) performs the following independent audit:

- Replays all **248** corner/lag correlations at **448 bits**, rebuilding the
  original physical windows and actual sampled phases through the independent
  consumer.
- Checks both infinite valuation tails against the exact generating-function
  totals above.
- Reconstructs the full physical augmented experiments at **384 bits** and
  regenerates all **8,900** actual h=120 raw readings from their defining model.
- Recomputes both normal-space and reading-space residuals from the saved
  rational proposals. Their componentwise enclosures agree, and the fresh
  residuals satisfy the recorded bounds.
- Independently evaluates the exact squared rounding inequalities. Both new
  windows pass **49/49** gates and recover all 49 unknown integers. At the same
  clock and other budgets, the prior pair formula passes **49/49** multi-window
  gates and **48/49** outer-window gates.
- Verifies all seven publication-budget components over every `n=2,...,50`,
  **686 exact component inequalities** in total, including the displayed
  upward rounding and the separate future residual premise `rho<=1e-30`.

The outer-window comparison is therefore supported: the new coefficient
bound is below `0.496198708`, while the previous pair-based sufficient bound
exceeds `0.506493579`. Failure of that previous gate is an inconclusive
certificate, not an impossibility of recovery.

Run from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
python research/combined_transfer_2026_09/review/block_review.py
```

Add `--write` only to replace the review's own JSON output. The
[recorded result](block_review.json) binds reviewed artifact hashes and reports
the complete replay outcome. Rebuilding reviewed files can legitimately change
runtime-bearing hashes; it does not remove the need to rerun the checks.

## Scope relevant to further work

This improvement is established **before** the exact nuisance projection;
contractivity transfers it afterward. It does not claim additional reduction
from projected phase correlations. In a future projection-specific argument,
the common orbit phase `exp(-it log m)` generally cannot be removed as a norm
invariance after projection, because the projection need not commute with
that diagonal phase multiplier. Such an extension must retain the projected
geometry's dependence on `m` or prove a suitable replacement bound.

The finite-source datasets are mathematical examples. They do not establish
number-field realizability, empirical noise distributions, apparatus
calibration or an optimal achievable clock tolerance.
