# Structured uncertainty: six channels and stronger query guarantees

Completed 2026-09-05. All objectives selected from the preceding report are
handled. The shared mathematical advance is to retain the directions and
joint structure of uncertainty through the relevant comparison or inverse.
This produces three concrete improvements under complete error contracts.

## Six channels meet the noise requirement fixed in advance

The new rows **485, 493, 499, 501, 507, 515** identify every target from
490 through 510 and recover every nonzero two-mode source, for every known
time in [1,2]. They tolerate sensor error **3e-8 times source norm**, plus
the declared model and numerical radii **1e-9 each**, with relative source
error **below 0.000852151**. The required target was 0.001.

| Known-time, nominal-potential experiment | Relative sensor radius | Relative source error |
|---|---:|---:|
| Previously certified seven rows | 1.4e-7 | <0.000976359 |
| New six rows | 3e-8 | <0.000852151 |

The smaller bank trades noise allowance for fewer channels. It does not
dominate the seven-row experiment. Each channel is the specified spatial
average at one row; this is an acquisition saving when those averages are
directly available. Six has not been proved minimal, and five is not excluded.

The decisive change is a **weighted comparison of the two candidate source
norms**. A rational split chosen for each target pair and time cell proves
their response tubes disjoint for all source vectors. The previous uniform
pair-floor test provably falls short on this bank: a rational witness bounds
its polynomial pair floor by less than 97.551% of that test's requirement.
The weighted proof succeeds without reducing noise or loosening accuracy.

The certificate has **1,278 complete-time records** covering all 231 individual
and pair cases. Polynomial principal minors are strictly positive over full
intervals, checked by a separate exact consumer. All 60 exact synthetic raw
datasets recover correctly and replay at 320 bits.
[Six-row proof and evidence](six_rows/REPORT.md)

All seven ways of deleting one row from the preceding seven-row bank also
have proved physical ambiguity witnesses at noise below 1.080e-9. Thus
redesign was necessary within that deletion family. Those obstructions do
not apply to all six-row layouts; the successful redesigned bank illustrates
the distinction.

## The specified spatial potential tolerates much larger uncertainty

For the stronger seven-row bank, retain sensor radius **1.1e-7**, shared time
error **5e-7**, and the source accuracy target **0.001**. Specify the physical
potential as

\[
H(g)=I_y\otimes L_x+L_y\otimes\operatorname{diag}(1+g x_i),
\qquad g_0=4/5.
\]

The new certificate permits **|g-g0|<=2.5e-6** and gives relative source
error **below 0.000801020**, for all allowed targets, sources and times.
The channels remain **490, 492, 496, 500, 504, 508, 510**. This uncertainty
profile is attached to these seven rows; it has not been transferred to the
new six-row bank.

The potential allowance is 10,000 times the earlier chosen generic-generator
profile's implied bound of 2.5e-10. That earlier profile had unused margin.
A more conservative comparison also holds: the preceding scalar formula,
with its original constants and the same sensor/time allowances, cannot
certify potential radius 1.401e-9. The new certified radius exceeds that upper
limit by more than **1,784 times**. Neither comparison claims a globally
optimal tolerance. [Exact comparison gates](framework/applications.json)

This improvement comes from bounding how the perturbation affects the
**reconstructed source**, rather than charging its whole output norm at the
inverse's weakest direction. If F bounds the structured forward disturbance,
V bounds its influence through the nominal inverse, and r contains all other
errors and complete nonlinear remainders, the two relevant tests are

\[
2(F+r)^2<\lambda\quad\text{for target separation},
\qquad V+r/\sqrt\mu<0.001\quad\text{for source accuracy}.
\]

They use different bounds for different questions. Here the directional
source test passes, whereas the corresponding global-gain bound is about
0.001227 and fails. The joint clock/potential corner calculation also reduces
the separate-direction forward and inverse allowances by **8.33%** and
**3.45%**, respectively. The parameters stay shared across the readings of
one explanation; competing explanations may choose different unknown values.

The calculation reconstructs the actual potential derivative from the full
finite transverse model, with complete exponential, time, image and boundary
remainders. It verifies **2,688 target/time cells**. All twelve raw synthetic
examples are generated from the model at the actual perturbed potential and
time, then successfully decoded at nominal time. Their data replay at 320
bits; the 1,782 derivative coefficient enclosures replay at 384 bits.
[Spatial potential proof and reconstruction](resolution/REPORT.md)

## Arithmetic clock bounds now exploit the actual oscillatory measurements

The complete clock bound for the original affine-clock rectangle falls from
**1.601465e-7** to **below 6.416861e-8**, about a **2.50-fold reduction**.
This covers every allowed integer coefficient in the infinite divisor
envelope, using the same 8,900 readings. It does not substitute the small
distortion of a finite synthetic source for the uniform bound.

There are two separately quantified gains:

| Clock enclosure | Worst of the two weighted designs |
|---|---:|
| Previous maximum-time, pointwise derivative bound | <1.601465e-7 |
| Actual weighted affine-clock direction | <8.775077e-8 |
| Weighted direction plus complete phase pairing | <6.416861e-8 |

For the phase step, partition all integers into pairs (n,2n) whose first
member has even exponent of two. Every pair has the same phase difference,
log 2. The actual weighted correlation of these phases is tiny. Explicit
divisor-envelope ratios and complete odd-part generating series turn that
correlation into a bound for **every pair and the entire remaining tail**.
Twenty valuation classes receive sharper factors; the others retain a proved
global factor. A full second-order exponential remainder is also charged.

The phase calculation alone improves the weighted-only bound by about
**26.87%**. The ratio assumptions apply to coefficient envelopes, not to
the independently variable actual coefficients. The shared clock corners
cover the whole affine-clock rectangle by convexity. The bound remains valid
after the correct polynomial nuisance projection by contraction; a sharper
query-specific projected phase bound remains future work.
[Complete arithmetic proof](arithmetic/PROOFS.md)

An actual recovery example now uses **60 times the original clock radii**:
|a-1|<=6e-13 and |b|<=6e-10. Keep amplitude bound 4,000, frequency bound 3,
sensor radius 4e-5, separate mismatch radius 1e-6, and degree twelve.

| Design | New complete coefficient-error bound | Previous clock formula at the same requirements |
|---|---:|---:|
| Multiscale | <0.447818 | <0.462221 |
| Outer window | <0.496864 | >0.511267 |

Both new certificates recover all **49 unknown integers**; the required
rounding threshold is 0.5. The previous outer-window sufficient certificate
fails at these same requirements. The 60-fold figure compares clock rectangles,
not optimal clock capacities: the preceding example did not exhaust its
allowance. Both new sets of exact readings and solve proposals replay at
384 bits, including the complete tail and actual normal residual.

## Degree selection now includes a computation cost

Under the fixed original clock rectangle, B=4,000, Omega=3, the same sensor
and mismatch budgets, and a freshly verified future residual at most 1e-30,
degree **twelve is the least passing among 6, 8, 10 and 12**. The new maximum
coefficient-error bounds are below 0.438350 and 0.487394. Degree ten's bounds
remain above 6, so the tighter clock treatment alone does not lower the
degree required by this sufficient certificate. Untested degrees, including
eleven, have no minimum-degree claim.

The augmented dimension is 50+p. At degree twelve the forward matrix has
551,800 complex entries; classical full Gram formation costs 34,211,600
complex multiply-accumulates, followed by a dense solve of dimension 62.
All four degrees have explicit dimension and operation counts. Local matrix
reconstruction took about 2.47–3.44 seconds per degree/window at 320 bits;
fresh degree-twelve proposals took about 0.131 seconds each. These are recorded
single-run measurements on the stated runtime, not universal speed claims.
[Complete degree and cost table](arithmetic/REPORT.md)

## What is verified, and what remains a premise

The [shared proofs](framework/PROOFS.md) now cover directional inverse bounds,
weighted two-source separation and complete clock-phase transfer. Their
specializations give useful consequences in both physical models, including
a lower channel count and guarantees that the preceding sufficient gates
cannot provide.

All **32 focused tests** passed. Independent consumers and cross-reviews
reconstructed the complete time and series bounds, actual inputs, normalization
and inverse consequences. The new common adapter checks all six-row weighted
splits, structured spatial gates and 980 arithmetic rounding comparisons.
All **553 historical artifacts** remain unchanged. The [reproduction guide](README.md)
and [validation manifest](VALIDATION.json) distinguish complete proofs,
reconstructed numerical premises, inherited full tails and synthetic examples.

The source classes, readouts, clock and mismatch families remain explicit
model assumptions. These calculations supply no apparatus calibration,
physical noise distribution, general number-field realization or external
peer review. No public release or historical conversation rewrite was made.

## Next objectives supported by these results

The strongest shared next question is whether the **six-row experiment can
retain a useful structured clock/potential tolerance**, fixed before testing.
It would combine the acquisition reduction and directional inverse gain in
one contract; neither existing certificate alone establishes that combination.

For arithmetic, larger multiplicative blocks or phase correlations after
the exact nuisance projection could further tighten the complete clock
bound. The new all-integer pairing supplies a rigorous starting point for
that question. A verified degree-eleven construction would also close the
gap in the present least-tested-degree comparison. These are subsequent
objectives, not hidden assumptions in the completed guarantees.
