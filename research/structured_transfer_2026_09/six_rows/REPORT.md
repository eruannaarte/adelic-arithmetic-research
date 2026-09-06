# Six channels meet the fixed spatial contract

The redesigned bank **(485, 493, 499, 501, 507, 515)** certifies the target and
both source coefficients for every target 490–510, every nonzero real two-mode
source and every exactly known time in `[1,2]`. At the predeclared relative
sensor radius **3·10^-8**, with model and numerical radii **10^-9 each**, its
relative source error is **below 0.000852151**, against the required 0.001.
The rows have minimum separation two and lie in the allowed offset range.
A channel still means a global average in x at one y location.

At the same known-time and nominal-generator assumptions, the proved choices
are:

| Channels | Relative sensor radius | Relative source error |
|---|---:|---:|
| New six-row bank | 3·10^-8 | <0.000852151 |
| Prior seven-row bank | 1.4·10^-7 | <0.000976359 |

Both charge model and arithmetic radii of 10^-9 each. The seven-row profile
is recorded in `uncertain_transfer_2026_09/REPORT.md`; the lower acquisition
count therefore comes with a stricter noise requirement.

The mathematical gain is retaining the separate source blocks in a candidate
pair. Instead of charging an indiscriminate factor of two to their combined
squared norm, a rational weight certifies the joint inequality

\[
[P_j,-P_k]^T[P_j,-P_k]
\succ b^2\operatorname{diag}(a^{-1},a^{-1},(1-a)^{-1},(1-a)^{-1}).
\]

Weighted Cauchy then excludes intersecting explanation tubes. The weight is
fixed per target pair and time cell and works for **all** source vectors.
This directly instantiates the shared objective of preserving joint incidence.

An exact rational witness proves that the previous uniform pair-floor gate
cannot certify this bank: at time 1 its polynomial pair Gram floor is at most **97.551%
of that gate's requirement**. The new proof succeeds with unchanged budgets.
It uses **1,278 complete-time records**, proving positivity of all leading
principal minors as rational polynomials. A separate consumer reconstructs
those polynomials with fraction-free elimination. Thus the guarantee depends
on complete time covers and full model remainders, not on the discovery grid.

All **seven one-row deletions of the preceding seven-channel bank** fail the
same noise contract. Each has an explicit rational time/source ambiguity;
all seven are already ambiguous at some radius below **1.080·10^-9**. Redesign
was necessary within that deletion family. This is not a lower bound on every
six-row layout, and six channels have not been proved optimal.

The raw wrapper verifies fourth-root normalization without knowing source
amplitude or label. **60 synthetic exact-rational datasets** cover five target
labels, three times, four source directions and amplitudes from `10^-12` to
`10^12`. Every target and source is recovered; the largest observed relative
source error is below `3.372·10^-5`. A 320-bit replay reproduces all stored raw
digits and reproves their full finite-model sensor promises. These examples
illustrate the theorem and do not replace its all-source/time proof.

The bounded discovery scan examined 1,730 separated layouts and refined 50
candidates. It did not prove a six-row impossibility. A subsequent symmetric
layout check exposed the successful candidate and the loss in the old gate.
The exact producer completed in approximately 23 seconds on the recorded local
Python/FLINT runtime; this is an algebraic certificate cost, not an apparatus
acquisition-time measurement.

See [the proofs](PROOFS.md) and [reproduction guide](README.md). The six-row
profile assumes known time and the nominal potential. Transferring the new
bank to the separate structured potential/clock profile, with tolerances fixed
before testing, is a concrete next step. Globally excluding five rows would
require a new obstruction; no such lower bound is asserted here.
