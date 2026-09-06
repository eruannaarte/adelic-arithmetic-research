# Certified answers from imperfect experiments

**The Transfer Theorem Lab — a public guide to certified query recovery under structured uncertainty.**

A useful experiment does not have to reconstruct everything. It has to answer
the question we asked, with a guarantee that survives the uncertainty we allow.
This research develops a way to carry such a guarantee through nuisance
removal, finite approximation, restricted sensing, clock error and model
uncertainty. Two detailed applications now recover a spatial source and a
finite set of arithmetic integers.

Open the [standalone interactive lab](website/transfer-theorem-lab/index.html),
read the [current mathematical report](research/combined_transfer_2026_09/REPORT.md),
or use the [portable reproduction guide](publication/transfer-theorem-v1/PORTABLE_GUIDE.md).
The public release includes an offline lab ZIP: extract it and open `index.html`.

## Begin with the answers still possible

Imagine an unknown source value x and an unknown instrument offset u. Two
readings have the form x + u and 2x + u, each with a bounded sensor error.
Subtracting them removes the shared offset. It does not remove sensor error.
If the offsets are independent, the same subtraction does not remove them.

The lab makes this small example exact. It retains every source value compatible
with the displayed observation. In the integer version, one integer may remain
even while a continuous interval would still contain many values. These are
different source assumptions, made explicit in the controls.

The general object is the **answer set**:

\[
\mathcal Q_D(y)=\{q(x):y=F_D(x,u)+e,\quad x,u,e\text{ admissible}\}.
\]

Here D is the experiment and q is the question. A singleton certifies a discrete
answer. A continuous question needs an enclosure narrow enough for the desired
accuracy. A processing step is sound when it retains the true explanation;
silently dropping an allowed uncertainty can create false certainty.

## What the transfer theorem does

The theorem turns model-specific estimates into a query guarantee. First state
the source class, the shared nuisance, the allowed uncertainty, and the norm in
which measurement error is bounded. Then perform a valid nuisance operation and
include its effect on that norm. Finite approximations and numerical processing
need their own error bounds. Finally, test whether different answers remain
separated and how much inverse error the remaining uncertainty can cause.

For a spatial label j, the processed model has the form

\[
y=A_j u+D_j(z)u+e,\qquad \|e\|\le r_j\|u\|.
\]

The parameter z retains the joint clock/model uncertainty across all readings.
The matrix D describes its leading directions; the complete nonlinear remainder
is included in r. Two estimates serve different purposes:

\[
F_j\ge\sup_z\|D_j(z)\|,\qquad
V_j\ge\sup_z\|A_j^\dagger D_j(z)\|.
\]

F helps enclose feasible observations and separate different labels. V measures
how these particular disturbances affect the reconstructed source. If
A_j* A_j ≥ μ_j I > 0, then, after the correct label is identified,

\[
\frac{\|\widehat u-u\|}{\|u\|}
\le V_j+\frac{r_j}{\sqrt{\mu_j}}.
\]

This follows directly from applying the nominal inverse to the model. It can
be substantially sharper than charging every disturbance at the weakest inverse
direction. A separate weighted Gram inequality proves that two different label
tubes cannot overlap, using Cauchy–Schwarz. The
[complete proof](research/combined_transfer_2026_09/framework/PROOFS.md) states
the positive constants, strict inequalities, transported norms and query version.

Shared uncertainty must stay shared within one explanation. Different competing
explanations may choose different unknown clock or model values. The theorem
does not gain information by forcing them to agree.

## A six-reading spatial experiment with declared physical uncertainty

The spatial model evolves a two-mode source on a reflecting 1001 × 1001 grid.
Its starting target is one of 21 neighboring rows. Six selected spatial averages
must identify that row and recover both source coefficients.

Earlier work established six-channel recovery with known time and potential,
and a separate seven-channel experiment with uncertain time and potential. The
new result establishes the combination directly: it recomputes the six-channel
directional bounds and enlarges the complete pair certificate.

| Quantity | New six-channel contract |
|---|---:|
| Selected rows | 485, 493, 499, 501, 507, 515 |
| Possible target rows | Every row from 490 through 510 |
| Nominal and actual time | Both in [1,2] |
| Sensor radius, relative to source norm | 3 × 10⁻⁸ |
| Shared clock displacement | At most 10⁻⁸ |
| Potential uncertainty around g = 4/5 | At most 10⁻⁸ |
| Guaranteed relative source error | Less than 0.000852831068 |

The clock and potential tolerances were fixed before testing. The proof covers
every nonzero source in the specified two-mode space and every admitted time,
not only saved examples. Independent consumers verify 1,280 polynomial source
and pair records and 2,688 directional cells. Twenty-four raw examples were
also reconstructed from the actual finite generator and decoded successfully.

The tolerances are small and expressed in the model's coordinates. Practical
adequacy requires units and calibration. The coarse inverse estimate also
passes this small region, so the new achievement is the combined six-channel
contract; structured inversion is sharper here but is not necessary for success.
No optimal bank or maximal tolerance is claimed.

## Arithmetic recovery with the whole infinite tail

The arithmetic model observes an infinite Dirichlet series at 8,900 complex
sample times. It recovers the 49 unknown integers a(2), …, a(50), with a(1) known.
All coefficients obey the declared envelope 0 ≤ a(n) ≤ d₁₄(n). This is a
mathematical source class; not every admissible sequence is asserted to come
from a number field.

Higher coefficients remain in a complete infinite-tail bound. Polynomial drift
is removed through an augmented model. An affine clock preserves that polynomial
nuisance space. Bounded oscillatory drift, separate model mismatch, sensor noise,
digital centering and an actual-matrix residual all consume the recovery budget.
If every complex coefficient error is strictly below ½, rounding the real part
recovers the integer.

The new clock estimate groups 32 successive powers of two for **every odd
starting integer**. It uses the actual weighted phase geometry and charges every
omitted power. This reduces the complete base-clock radius from about
6.416861 × 10⁻⁸ to below 2.987008 × 10⁻⁸, more than 53.45% smaller. The bound
is established before nuisance projection; contraction transfers it afterward.
The construction does not assume that a projected norm retains every phase
symmetry of the unprojected measurements.

With polynomial degree twelve, oscillatory amplitude at most 4,000, frequency
at most 3, sensor radius 4 × 10⁻⁵ and separate mismatch radius 10⁻⁶, both
weightings certify **120 times the base clock radii**: fractional scale error
at most 1.2 × 10⁻¹² and additive offset at most 1.2 × 10⁻⁹.

| Weighting of the same 8,900 readings | New complete coefficient error | Prior pair bound at the same clock |
|---|---:|---:|
| Multiscale | < 0.447153367 | Passes |
| Single outer window | < 0.496198708 | > 0.506493579; misses the sufficient gate |

Both new actual-data reconstructions recover all 49 unknown integers, with
384-bit replay of the readings and inverse proposals. The previous demonstrated
clock multiplier was 60. This doubles that demonstrated rectangle, while
remaining a model-conditional sufficient guarantee.

## Why the degree-eleven result matters

Degree eleven closes a gap in the acquisition-cost comparison. Its complete
61-column augmented model, all tail channels, weighted approximation norms and
actual inverse have now been verified at higher precision.

At amplitude 4,000 and frequency 3, its sufficient bounds exceed 1.09 and 1.14
for the two weightings: 32 of 49 gates pass. Twelve therefore remains the least
passing degree **among the tested degrees 6, 8, 10, 11 and 12**. This does not
prove every degree-eleven recovery method impossible.

The same verified degree-eleven construction does recover every integer at
amplitude 500 and the base clock radii. Its errors are below 0.445865330 and
0.494913819. That gives a useful operating region for a smaller augmented solve,
with computation dimensions, operation counts and measured runtimes recorded.

## How the five research paths meet

| Original path | What it contributes |
|---|---|
| Experimental preparation | A defensible uncertainty region and joint calibration conditions; apparatus calibration remains unperformed. |
| Harmonic readings | Sharp reading counts and interior collision obstructions; full-source separation cannot be replaced by vertex checks. |
| Arithmetic query structure | Multiplicative constraints and actual quadratic-field witnesses; a query can be determined while intermediate labels remain uncertain. |
| Multiscale arithmetic sensing | Complete infinite-tail, drift, clock and residual budgets for integer recovery. |
| Finite-resolution sensing | Transfer at the scale of the weakest information direction, restricted banks and continuous source accuracy. |

The lab includes evidence links and a nine-package progression through these
paths. Older reports remain records of their original, narrower guarantees.
The common theorem is useful because it produces checked consequences while
preserving those differences, rather than declaring every model equivalent.

## Explore and verify

In the lab, the toy example is exact elementary mathematics. Spatial controls
test containment in saved certified uncertainty boxes. Arithmetic bars show
rounded component estimates; badges inherit only explicitly verified contracts.
Crossing a displayed boundary can mean that this certificate stops applying.
It does not by itself prove impossibility.

The release includes proofs, complete certificates, separate consumers, actual
model reconstructions, adverse tests and independent internal reviews. These
establish the stated mathematical guarantees. They do not supply measured
pendulum calibration, a physical noise distribution, external peer review, or
a historical priority claim. A solver residual verifies a computation within
its model; it cannot establish that a physical system belongs to that model.

The next questions are specific: enlarge the six-channel joint uncertainty
region under the same noise and accuracy requirement; exploit projected phase
geometry while proving the necessary operator bounds; and sharpen the
degree-eleven amplitude/frequency frontier or its query-specific drift bound.
