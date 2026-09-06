# Clock-aware arithmetic recovery with a separate mismatch budget

The same 8,900 readings now support a certified example with uncertain clock,
model mismatch, and a larger frequency family. At degree 12 both physical
windows recover all 49 unknown integers for amplitude bound 4,000 and
frequency bound 3. Their complete coefficient error bounds are below 0.438590
and 0.487634, respectively. The threshold remains 1/2.

## What changed mathematically

The clock is shared and affine: `t'=a*t+b`, with `|a-1|<=1e-14` and
`|b|<=1e-11`. Such a clock preserves the entire unrestricted polynomial
nuisance space. It changes a sinusoid's frequency bound to
`(1+1e-14)*Omega` and changes its already arbitrary phase.

A complete divisor-envelope calculation proves a uniform signal derivative
bound below 8,473.355258. It charges at most 1.601465e-7 to the weighted
arithmetic signal error from this clock uncertainty. The calculation sums
the full infinite envelope through an elementary series-product identity
and an integral tail bound; the finite synthetic source is not substituted
for it.

The declared model mismatch has its own weighted allowance 1e-6. Sensor and
digitization error retain allowance 4e-5. These errors add to the weighted
sinusoidal approximation, inherited complete arithmetic tail, verified solve
residual, and digital correction. A solver residual cannot certify the
clock or mismatch assumptions.

Arbitrary independent sample jitter is obstructed when polynomial nuisance
is unbounded: even an arbitrarily small timing spike can leak an arbitrarily
large linear nuisance into the quotient. Affine clock preservation is the
positive alternative used here. [Proofs](PROOFS.md) give the full argument.

## Degree selection uses the complete recovery budget

Rational weighted approximations were constructed for degrees 6, 8, 10, 12.
Taylor tails through orders 33 and 34 make their sinusoidal guarantees
uniform over every phase and every real frequency in the declared interval.
Both physical windows are retained.

The table gives approximate strict sufficient amplitude capacities. Every
row charges sensor, mismatch, clock, complete arithmetic tail, correction,
and a freshly verified future normal residual at most 1e-30. Exact rational
limits are in [consequences.json](consequences.json); the table values are
rounded displays. Family membership and this residual ceiling must both
hold for a future acquisition.

| Window | Degree | Omega<=1/2 | Omega<=1 | Omega<=2 | Omega<=3 |
|---|---:|---:|---:|---:|---:|
| Multi | 6 | 18,363.7 | 141.251 | 1.03706 | 0.0547535 |
| Multi | 8 | 22,449,882 | 43,262.8 | 80.0877 | 1.90586 |
| Multi | 10 | 4.05945e10 | 19,588,964 | 9,124.43 | 97.5392 |
| Multi | 12 | 1.02158e14 | 1.23398e10 | 1,444,274 | 6,919.76 |
| Outer | 6 | 12,268.4 | 94.3667 | 0.692837 | 0.0365792 |
| Outer | 8 | 14,978,584 | 28,864.9 | 53.4344 | 1.27158 |
| Outer | 10 | 2.70190e10 | 13,038,076 | 6,073.05 | 64.9200 |
| Outer | 12 | 6.77260e13 | 8.18074e9 | 957,487 | 4,587.47 |

Degree 12 has the largest sufficient capacity among the four tested degrees.
It need not minimize coefficient error for a smaller declared family. With
Omega<=1 and the same uncertainty/residual budget, the minimum-error choices
for both windows are:

| Amplitude bound | Best tested degree |
|---:|---:|
| 0 or 0.1 | 6 |
| 1 or 100 | 8 |
| 4,000 | 10 |

This is the practical reason to optimize the complete budget: a better
approximation can be outweighed by its larger arithmetic-tail or Gram cost.
Neither table claims an optimal polynomial approximation or an optimal
degree outside the four tested choices.

## Actual observations and adverse controls

The example uses both clock errors at their nonzero permitted endpoints,
the true-time sinusoid `4000*sin(3*t'/890+1/3)`, a degree-six polynomial of
size 10^20, mismatch `9e-7*cos(t'/17)`, and sensor perturbation
`3.9e-5*exp(i*t'/11)`. The same exact rationalized readings serve every
degree/window comparison. The source is an admissible integer
divisor-envelope source, without a number-field realization claim.

| Degree | Multi maximum coefficient error bound | Outer maximum coefficient error bound | Strict gates passing |
|---:|---:|---:|---:|
| 6 | 10,796.1202 | 10,805.5244 | 0/49 both |
| 8 | 309.682105 | 309.993073 | 1/49 both |
| 10 | 6.368366 | 6.422393 | 12/49 both |
| 12 | 0.438590 | 0.487634 | 49/49 both |

The first three rows fail this sufficient certificate; they do not prove
that those decoders or sources are impossible to identify. Degree 12 returns
all 49 integers correctly. Its uniform family remainders are below 3.363927e-5
and 3.366300e-5. The actual reconstructed remainders are smaller, below
2.471564e-5 and 2.473281e-5; recovery continues to charge the uniform bounds.

All eight actual normal residuals are below 3.362e-37 and meet the common
future residual ceiling 1e-30. The complete input signal's actual timing
distortion is below 2.791e-10, while the certificate charges the much larger
uniform bound 1.601465e-7. This conservatism identifies a useful next target.

## Verification and next target

The producer's 184 weighted polynomial residual bounds were checked from all
physical samples at 384-bit precision, together with 16 complete remainder
moment bounds. Every actual nominal matrix and both algebraic forms of all
eight solve residuals were reconstructed. At 384-bit precision the actual
readings reproduced identically and all saved exact proposals replayed.
Eight focused tests cover uncertainty rejection, exact affine closure,
nonaffine leakage, and adverse complete budgets. Independent reviews live
in the package's sibling `review/` directory.

The next arithmetic target is a sharper complete weighted timing bound
that uses the oscillatory acquisition geometry while preserving the affine
clock nuisance identity. A second useful question is choosing the least
polynomial degree that attains a specified amplitude/frequency and error
requirement, with a computational-cost charge. Empirical use still requires
justifying the clock and mismatch family through a model or calibration.
