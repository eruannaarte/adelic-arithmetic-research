# Larger multiplicative blocks improve the complete clock guarantee

The complete affine-clock bound is now below **2.987008e-8** at the base
clock rectangle, for both physical windows. This is more than **53.45% smaller**
than the preceding all-integer pairing bound and more than **5.36 times tighter**
than the original uniform pointwise allowance. The source still contains every
integer coefficient in the full divisor envelope; no source tail is discarded.

The improvement has a demonstrated consequence. The predeclared **120-fold
clock rectangle** preserves exact recovery of all 49 unknown coefficients
at degree 12, amplitude 4000, frequency 3, sensor radius 4e-5 and separate
mismatch radius 1e-6. It doubles the preceding phase-pairing demonstration's
clock rectangle without changing any readings or relaxing the other budgets.

| Physical weighting | New base clock radius, upper bound | Error bound at h=120 | Previous pair formula at h=120 |
|---|---:|---:|---:|
| Multiscale | 2.986832e-8 | <0.447153367 | <0.457446227; passes |
| Outer window | 2.987008e-8 | <0.496198708 | >0.506493579; gate fails |

The outer-window comparison establishes an improvement of a sufficient
certificate at the same fixed contract. The failing preceding formula is
not an impossibility theorem about the experiment.

## What changed mathematically

Every integer is written uniquely as `2^k m`, with m odd. Instead of handling
only two coefficients at once, the new proof retains 32 successive valuations
in each odd-m orbit. It bounds their joint oscillatory Gram using the actual
31 phase gaps, at every one of the four shared affine-clock corners. The
resulting Gram factor is below 1.000000287 for both windows.

The finite block is not a source cutoff. Exact geometric sums charge every
valuation k>=32. Complete odd-integer generating series charge every odd m.
The proof substitutes coefficient envelopes only after a monotone squared
norm bound, so actual coefficients may independently vanish; they need not
satisfy the envelope's multiplicative ratios. The entire nonlinear clock
remainder remains separately charged.

The [proof](PROOFS.md) is self-contained apart from the explicitly inherited
model and complete recovery theorem. The bound transfers through the exact
polynomial nuisance projection because that projection is contractive. No
new numerical advantage from the projection itself is claimed.

## The threshold of the new sufficient formula

At degree 12, with all other fixed budgets unchanged and a verified normal
residual at most 1e-30, exact rational gates locate the largest *integer*
multiplier allowed by each formula:

| Weighting | New complete block formula | Previous complete pair formula |
|---|---:|---:|
| Multiscale | 827 | 385 |
| Outer window | 170 | 79 |

The new outer formula gives error below 0.499934396 at h=170; its own
sufficient gate fails at h=171. Monotonicity follows because all radius and
family coefficients are nonnegative. These are sharp integer thresholds of
the stated sufficient formulas, not claims of optimal clock tolerance across
all methods or all decoders. The direct physical demonstration uses the
separately fixed h=120 contract, preserving more margin.

## Verification and computation

The producer uses 256-bit outward arithmetic. A separate consumer rebuilds the
physical windows from their original exact binary coefficients and checks
**248 actual corner/phase-lag correlations at 384 bits**, all complete odd
masses and valuation tails, every rational square-root inequality, and the
linear-plus-quadratic clock formula. An independent zeta-series calculation
cross-checks the elementary positive-series enclosures.

Two actual degree-12 solves reconstruct the declared 8,900-reading synthetic
model with the h=120 clock error, unbounded polynomial nuisance, sinusoidal
drift, bounded mismatch and sensor noise. All 49 unknown integers are
returned correctly. A 384-bit replay reconstructs the same rational readings
and checks the saved proposals and dual residual identities. Their normal
residuals are below 3.37e-37. These finite-source fixtures verify instances;
the infinite-envelope guarantee comes from the proof and complete bounds.

The exact consequence checker replays 2,352 comparison gates, 392 integer
boundary gates and 98 returned-answer complex-disk checks. Ten tests also
reject missing phase lags, missing shared clock corners, discarded infinite
valuation tails, false positive phase bounds, an undercharged odd mass, a
missing nonlinear remainder and a falsely relabelled rounding result.

This run's producer and independent phase consumer each took about 1.71 s.
Each phase calculation sums 8,900 physical contributions, for 2,207,200
corner/lag contributions in total. Degree 12 retains a 62-column augmented
solve; the classical full Gram count is 34,211,600 complex multiply-adds.
Actual 320-bit matrix reconstructions took 2.95 and 3.28 s, and verified
solves about 0.37 s each. These are local wall-clock observations, not
machine-independent performance claims.

The compact [publication budget](publication_budget.json) bounds each error
component uniformly over n=2,...,50, rounds each upward to 12 decimal places,
and is independently replayed. Their sums are 0.447153366502 and
0.496198707854. A browser visualization may illustrate those sealed budgets;
it cannot certify membership in a physical clock, drift or noise family or
verify a new numerical inverse by itself.

## What this justifies next

A second multiplicative direction, for example joint powers of 2 and 3,
could exploit additional actual phase geometry while retaining complete
coprime starting classes and both infinite valuation tails. That is more
promising than merely increasing this 32-term block, whose omitted valuation
mass is already tiny. A complementary target is a verified bound after the
exact nuisance projection, where low-frequency clock directions may be
removed more effectively. Either target must keep the same declared source
class and retain independent clock choices for competing source explanations.
