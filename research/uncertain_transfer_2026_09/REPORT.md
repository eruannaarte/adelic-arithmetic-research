# Certified query recovery with uncertain clocks and model mismatch

Completed 2026-09-05. Both focused objectives and the shared transfer objective
are achieved within explicit mathematical models. The main new knowledge is
a precise condition for tolerating uncertain acquisition, a stronger
seven-channel spatial experiment, and an arithmetic degree-selection rule
that includes the full recovery cost.

## The shared theorem now says when timing uncertainty is admissible

The [transfer extension](framework/PROOFS.md) places clock and model uncertainty
inside each possible explanation of an observation. After valid nuisance
removal, the source's nominal response must contain the actual response with
all five contributions charged:

\[
\delta=\text{sensor error}+\text{finite approximation}
+\text{processing error}+\text{timing error}+\text{model mismatch}.
\]

Existing query separation and source-error gates then apply to this enlarged
set. No probabilistic independence is assumed. The important restriction is
that the quotient must annihilate **every permitted nuisance image**, including
those changed by the uncertain clock. Otherwise scaling an unrestricted
nuisance coefficient makes its residual arbitrarily large.

For polynomial drift this yields a concise exact theorem. At M distinct
nominal nodes, with M>p^2, the actual sampled clock preserves every polynomial
of degree at most p **if and only if the actual sampled times are affine in
the nominal times**. The proof uses only polynomial composition and the bound
on the number of roots of a nonzero polynomial. All four arithmetic degrees
studied here satisfy this condition on the actual 8,900-node grid.

An arbitrarily small timing spike at one reading can therefore defeat a
uniform error budget when polynomial drift amplitude is unrestricted.
This is an obstruction to that nuisance-removal scheme, not to every possible
joint inference method. It explains why a general claim of jitter robustness
would be invalid and why the shared affine-clock model used below works.
[Independent derivation and exact witnesses](review/CLOCK_NUISANCE.md)

## Seven spatial channels have a substantially better noise allowance

The new rows are **490, 492, 496, 500, 504, 508, 510**. For every target
490 through 510, every nonzero two-mode source, and every allowed time in
[1,2], they meet these strict guarantees:

| Profile | Sensor radius, relative to source L2 norm | Absolute shared time error | Generator operator error | Relative source error |
|---|---:|---:|---:|---:|
| Known time and generator | 1.4e-7 | 0 | 0 | <0.000976359 |
| Uncertain time and generator | 1.1e-7 | 5e-7 | 1e-9 | <0.000915623 |

The known-time allowance is **40% greater** than the preceding seven-row
certificate at the same target accuracy of 0.001. The second profile retains
a 10% noise increase while accommodating nonzero clock and model errors.
Both also charge the complete approximation and normalization budgets,
1e-9 each. The higher accuracy in the second row reflects its smaller total
error allowance, not a benefit caused by uncertainty.

The fixed-before-search seven-row contract was exceeded. The proof covers
861 nonempty time cells with 3,743 exact records, covering all 21 individual
maps and all 210 target pairs. Both the weakest source direction and pair
separation improved. Six rows were not searched after this objective passed;
neither minimality nor six-row impossibility is claimed.
[Spatial proof and result](resolution/REPORT.md)

The model error allows any self-adjoint positive-semidefinite generator H'
with ||H'-H||<=epsilon_H, keeping preparation, readout and the time
normalization fixed. Nominal and true times both remain in [1,2]. A complete
polynomial derivative bound and a semigroup identity give the explicit rule

\[
\delta=\eta+\rho+\xi+0.037h+\tfrac83\epsilon_H.
\]

This charges the physical approximation once, at the true time, then transports
its polynomial map to nominal time. No derivative bound is inferred from a
mere approximation-error bound.

The [raw-data wrapper](framework/raw_clock.py) normalizes at the nominal
rational time, accepts an interval for the actual time, and verifies the
resulting total error budget without knowing the source amplitude or target.
All twelve exact synthetic raw examples with nonzero timing shifts and
H'=H+1e-9 I recover correctly. Their physical sensor promises replay at higher
precision. Three additional million-state evolutions are useful floating
diagnostics; the rational certificates do not depend on them.

## Arithmetic recovery now includes a declared clock and mismatch family

Retain all **8,900 complex readings**, known a(1), the complete infinite
arithmetic tail, and actual verified solve residuals. The declared family is

\[
t'=a t+b,\quad |a-1|\le10^{-14},\quad |b|\le10^{-11},
\]
\[
\beta(t'/890)+A\sin(\omega t'/890+\phi)+h,
\quad |A|\le B,\quad |\omega|\le\Omega,
\quad \phi\in\mathbb R,\quad\|h\|_W\le10^{-6}.
\]

Here beta is an unrestricted complex polynomial of the selected degree.
Sensor plus digitization error is bounded separately by 4e-5 in the actual
weighted norm. The affine clock preserves beta's degree exactly. It enlarges
the effective sinusoidal frequency bound by the factor 1+1e-14.

A complete positive-series argument bounds the derivative of every signal
in the divisor-envelope source class. Its uniform clock charge is below
**1.601465e-7**. This includes the entire infinite signal; it does not substitute
the finite synthetic source for the full source class.

For **B=4,000 and Omega=3**, degree twelve recovers all **49 unknown integer
coefficients** in both weighting designs:

| Design | Maximum complete coefficient error bound | Integer rounding threshold |
|---|---:|---:|
| Multiscale | <0.438590 | 0.5 |
| Outer window | <0.487634 | 0.5 |

The actual readings contain nonzero affine clock errors, a polynomial of
scale 1e20, the declared sinusoid, separate mismatch and sensor perturbations.
The same readings were solved at degrees six, eight, ten and twelve.
The lower three degrees fail these sufficient full-family certificates;
that failure is not a proof of non-identifiability.
[Arithmetic proof, full tables and data](noise/REPORT.md)

The degree comparison now has practical content. Degree twelve admits the
largest sufficient amplitude among the four tested degrees across all four
frequency bounds. But minimizing the complete coefficient-error bound for
Omega<=1 gives different choices:

| Amplitude bound | Degree with the smallest certified error among those tested |
|---:|---:|
| 0 or 0.1 | 6 |
| 1 or 100 | 8 |
| 4,000 | 10 |

These future-family comparisons require a **freshly verified normal residual
at most 1e-30**. They do not reuse one observed residual as a guarantee for
new data. All actual reconstructed residuals meet that ceiling. Increasing
degree can reduce drift approximation while worsening arithmetic-tail and
Gram contributions; the complete budget decides which effect wins.

## Verification and limits

All **24 focused tests** passed. The evidence includes complete-time spatial
certification, 184 weighted approximant norms, 16 complete remainder moments,
all eight arithmetic matrix/dual-residual reconstructions, 384-bit replay of
every arithmetic reading and exact solve proposal, and twelve raw spatial
decodes. A separate agent independently checked the central proofs, raw data,
normalization, uncertainty bounds and degree comparisons. This is independent
internal review, not external peer review.

The [common adapter](framework/applications.json) checks all 3,743 spatial
cell transfers, both spatial uncertainty profiles, all 392 actual arithmetic
coordinate gates including the expected failures, and the twelve raw packets.
All **467 historical artifacts** in the preservation manifest remain unchanged.
See the [reproduction guide](README.md) and [validation record](VALIDATION.json).

Clock, mismatch and drift-family membership remain model or calibration
premises. The spatial channels are the specified spatial-average readouts;
the arithmetic sources satisfy the integer divisor envelope without a general
number-field realization claim. Spatial error is source-relative, while
arithmetic error is absolute in a weighted complex-reading norm. The timing
tolerances use the respective models' units. No apparatus calibration or new
public release was performed.

## The next focused objectives

The strongest shared target is to exploit **structured timing and model
directions after nuisance removal**, while retaining their joint incidence.
The current norm-sum theorem is valid but deliberately conservative.

For spatial sensing, bound the generator perturbation in a specified physical
parameter family, such as uncertainty in the spatial potential, and optimize
its effect on the weakest source direction. This could increase usable clock
or model tolerances without adding channels. The fixed six-row contract remains
a separate acquisition-cost objective.

For arithmetic sensing, replace the global derivative envelope by a complete
weighted bound on affine-clock distortion using the actual oscillatory
acquisition geometry. For the synthetic example, actual timing distortion is
below 2.791e-10 while the uniform allowance is 1.601465e-7; this gap motivates
the question without proving that the uniform source-class bound can achieve
the example's smaller value. Then select the least degree meeting a fixed
amplitude/frequency/error requirement, with computation cost stated explicitly.
