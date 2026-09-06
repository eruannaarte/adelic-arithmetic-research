# Seven rows, verified raw normalization, and weighted drift recovery

Completed 2026-09-05. All three selected objectives are achieved. The shared
transfer theorem remains unchanged; this phase supplies stronger approximation
bounds, a smaller certified experiment, and a verified step from raw readings
to the existing decoder.

## Seven spatial channels meet the requirement fixed before the search

The bank **488, 490, 497, 500, 504, 508, 510** identifies every allowed target
490 through 510 and recovers every nonzero two-mode source, for every known
time in [1,2]. It permits L2 sensor error at most **$10^{-7}$ times source norm**
and guarantees relative source error **below 0.000998507**.

The [protocol](PROTOCOL.md) fixed the noise requirement and accuracy target
before searching. The result meets them without relaxing the requirement.
Its proof checks all 21 individual maps and all 210 target-pair maps over
complete time intervals: **1,051 nonempty cells and 3,391 exact records**.
[Spatial result and proof](resolution/REPORT.md)

The acquisition tradeoff is now explicit:

| Certified bank | L2 sensor radius, relative to source norm | Source relative error |
|---|---:|---:|
| Previous nine rows | $3\cdot10^{-7}$ | $<0.001$ |
| Previous eight rows | $2.3\cdot10^{-7}$ | $<0.001$ |
| New seven rows | $10^{-7}$ | $<0.001$ |

These are different layouts and sufficient guarantees. Seven is not proved
minimal; the four-row necessary benchmark remains unchanged. The new
seven-row result is L2 only; the earlier H1 contracts remain attached to
their eight- and nine-row banks.

A second seven-row layout that looked strongest on coarse time samples has a
proved physical ambiguity at an interior time. This rules out that layout at
the chosen noise level and demonstrates why full-time certification matters.
It is not an obstruction to all seven-row layouts.

## Raw readings now enter through a verified normalization wrapper

Previously, the exact spatial decoder assumed already-normalized data and
allowed a conditional numerical error of $10^{-9}$ times source norm. The new
wrapper accepts **unnormalized rational readings and known rational time**
and verifies the normalization error it actually introduces.

It uses a rational multiplier $r$ in place of $(1+t)^{-1/4}$. An exact
fourth-power inequality bounds the multiplier error. The physical operator
bound $\|A_j\|\le4/3$ then converts that bound to a source-relative error
charge **without knowing the source amplitude or target**. The wrapper sends
that verified charge to the existing decoder.
[Normalization theorem and interface](normalization/PROOFS.md)

All **72 exact raw-data cases** passed across seven, eight and nine rows,
all eight available profiles, and source scales $10^{-40}$, $1$ and $10^{40}$.
Independent review reconstructed the raw readings, verified that they meet the
actual finite-model sensor promise, and checked every source-error enclosure.

This discharges the former numerical normalization allowance for the stated
exact-input interface. Sensor error, acquisition digitization and clock
accuracy remain physical assumptions; an approximate clock is not certified
by treating its displayed time as exact.

## Weighted approximation admits much larger specified smooth drift

For the arithmetic experiment, retain degree eight and all **8,900 complex
readings**. Consider the explicitly bounded family

\[
g(t)=A\sin(\omega t/890+\phi),\qquad |A|\le B,\quad |\omega|\le1,
\quad\phi\in\mathbb R.
\]

The new proof covers every phase and the whole frequency interval. It gives
a degree-eight polynomial $p$ whose remaining physical weighted norm obeys
$\|g-p\|_W\le B K_W$, with $K_W<1.364\cdot10^{-9}$ for either design.
The existing augmented inverse absorbs $p$; only the bounded remainder
consumes the uncertainty budget. [Weighted-family proof](noise/PROOFS.md)

This is **over 2,021 times tighter** than the previous pointwise Taylor bound
for this family. At the same remainder radius $0.00003$:

| Sufficient approximation bound | Permitted family amplitude |
|---|---:|
| Previous pointwise Taylor bound | 10.8864 |
| New multiscale weighted bound | 22,023 |
| New outer weighted bound | 22,008 |

The gain comes from measuring the remainder in the actual sensing norm and
improving the polynomial approximation. It introduces no extra measurements
and does not increase polynomial degree. These are sufficient bounds, not
optimal thresholds or measured instrument tolerances.

The actual recovery demonstration uses drift amplitude **20,000**, arbitrary
polynomial nuisance of scale $10^{20}$, and sensor radius **0.00004**. Both
weighting designs recover **all 49 unknown integer coefficients**, while
retaining the complete infinite arithmetic tail and verifying the actual
normal residual. All data digits and accepted proposals replay at 320 bits.
[Arithmetic results and evidence](noise/REPORT.md)

The family is slow: its phase changes by at most approximately two radians
across the observation window. A valid frequency/amplitude bound is still a
model or calibration input; a small solver residual cannot establish it.

## What the shared theorem now delivers

The common adapter checks **3,509 transfer gates** plus all **72 normalization
packets**. They include full-time spatial transfer, target separation, source
accuracy, integer rounding under weighted drift, and the newly verified
normalization charges. These are two different physical models governed by
the same error-propagation rules, not measurements with interchangeable units.
[Common theorem specialization](framework/README.md)

Validation passed **23 focused tests**, full spatial-kernel reconstruction at
256 bits, weighted approximation reconstruction at 192/256/320 bits, and
arithmetic data/proposal replay at 320 bits. A separate agent independently
checked the normalization logic and raw fixtures, all weighted approximants,
and selected spatial floors. Its point checks supplement the full-time proof.
[Independent review](review/REVIEW.md)

All **388 historical artifacts** in the preservation manifest remain unchanged.
The [reproduction guide](README.md) distinguishes exact proofs, outward model
reconstructions, inherited complete-tail premises and floating diagnostics.
No empirical apparatus calibration or public release was performed.

## The next focused objectives

For spatial sensing, determine the cost–noise–accuracy tradeoff more sharply:
either increase the seven-row noise margin or test six-row layouts under a
noise requirement fixed in advance. The narrow current source margin means
that improving pair separation alone need not improve source recovery.

For arithmetic sensing, declare a frequency/amplitude uncertainty set with a
separate mismatch allowance, then optimize approximation and polynomial degree
against the complete recovery budget. The proved dependence
$K_W(\Omega)\le\Omega^9K_W(1)$ for $0\le\Omega\le1$ now makes that tradeoff
quantitative. Family membership must continue to come from a justified model
or calibration.

A useful next shared transfer objective is to charge **uncertain timing and
model mismatch** explicitly. The normalization wrapper resolves arithmetic
rounding of a known time; it does not yet resolve uncertainty in the time or
the forward model itself.
