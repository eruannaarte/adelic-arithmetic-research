# Two further consequences of the transfer theorem

Completed 2026-09-05. The theorem remains the shared framework: arithmetic
sensing develops nuisance removal and controlled numerical inversion; spatial
sensing develops acquisition reduction and separation of different answers.
This phase advances both selected targets and adds a specific obstruction.
The previous theorem and research packages are preserved.

## Fewer spatial measurements, with an explicit tradeoff

The previous eleven-row result can now be reduced to **nine rows with its
original noise and accuracy allowances**, or **eight rows with a quantified
tradeoff**. All guarantees cover every permitted target, every nonzero
two-mode source, and every known real time in [1,2].

| Spatial-average channels | L2 sensor error, relative to source norm | Guaranteed source relative error |
|---|---:|---:|
| Previous 11 | $3\cdot10^{-7}$ | $<0.001$ |
| New 9 | $3\cdot10^{-7}$ | $<0.001$ |
| New 8 | $2.3\cdot10^{-7}$ | $<0.001$ |
| New 8, keeping the original noise allowance | $3\cdot10^{-7}$ | $<0.0013$ |

Both new banks also preserve the two previously declared H1 noise allowances
and relative error below 0.001. The eight-row bank is
$\{488,490,494,498,502,506,510,514\}$; the nine-row bank is
$\{485,488,492,496,500,504,508,512,516\}$. These save three or two channels
against eleven. Each channel retains the same global spatial average in the
other coordinate.

The proof checks **all 21 individual source maps and all 210 target-pair maps**
over complete time intervals, including model approximation and the existing
conditional numerical error allowance. It uses 2,457 exact case-specific
records. [Spatial theorem and decoder](resolution/PROOFS.md)

A particular seven-row proposal fails more decisively than a numerical lower
bound failing: at time $285/256$, two different targets have overlapping allowed
physical observations at L2 noise radius $3\cdot10^{-8}$. This is an actual
ambiguity for that layout. Other seven-row banks remain open, and four rows
remain the necessary lower benchmark. [Checked obstruction](resolution/obstruction_7_checked.json)

## A verified arithmetic solve with bounded nonpolynomial drift

The arithmetic path now **computes and certifies the normal residual from the
actual readings and proposed solution**. The earlier conditional allowance
has become an executable verifier. It reconstructs the physical weights,
phases, augmented Gram matrix and polynomial basis using outward arithmetic.

For coefficient $n$, the guarantee is

\[
\left|n^2\widehat\theta_n-a(n)\right|
\le A_n+n^2\left(\frac{\eta+\nu+\Xi}{\sqrt f}+\frac\rho f\right)<\frac12.
\]

Here $A_n$ includes the complete infinite arithmetic tail; $f$ is the verified
Gram floor; $\eta$ bounds sensor error; $\nu$ bounds the remainder after
polynomial removal; $\Xi$ bounds the digital correction error; and $\rho$ is
the newly evaluated solve residual. Sensor and remainder errors share one
budget. [Proof and operational contract](noise/PROOFS.md)

On the same 8,900 readings, degree-eight removal certifies all 49 unknown integer
coefficients in four synthetic tests: two datasets, each decoded with both
weighting designs. Both accept sensor radius **0.00004** and remainder radius
**0.00003** together. For the refined large-drift dataset, the sufficient
remainder limit is above 0.00006009 for the multiscale design and 0.00004050 for
the outer design at that sensor radius.

The remainder budget can handle a substantial smooth drift. For
$10\sin(t/890)$, its degree-eight Taylor polynomial is removed as nuisance and
the complete remainder is at most $10/9!<0.00003$. The large test also includes
polynomial coefficients of scale $10^{20}$. Its ordinary floating proposals
fail verification; refined proposals recover every unknown coefficient with
normal residuals below $3.21\cdot10^{-39}$. This tests numerical cancellation
with exact synthetic inputs that retain the small signal. It does not establish
that a physical instrument has that dynamic range. [Results and receipts](noise/demonstration.json)

A small solve residual cannot establish that the physical drift bound is true:
an unbounded remainder could itself contain an arithmetic measurement column
and imitate a changed integer coefficient. The proof includes an exact example.

## What the combined result establishes

The unchanged transfer theorem accepts **2,457 interval gates, seven spatial
noise/accuracy profiles, and 196 arithmetic coordinate gates** from this phase.
Its usefulness is now demonstrated through both reduced acquisition and a
working numerical certification step. [Common theorem adapter](applications.json)

Validation passed: **17 focused tests**, complete reconstruction of the spatial
kernel at 256 bits, and reconstruction of both arithmetic datasets and all four
saved proposals at 320 bits. A distinct full finite-grid algorithm also passed
63 floating spatial regressions; those are diagnostics, not proof premises.
All **338 historical artifacts** covered by the preservation manifest remain
unchanged. [Reproduction and validation](README.md)

## The next focused objectives

For spatial sensing, use the seven-row ambiguity as a design constraint:
search other seven-row layouts under a fixed minimum noise requirement, then
either certify a full-time bank or produce a stronger obstruction for a stated
class of layouts. Separately, a verified normalization wrapper would discharge
the decoder's remaining conditional computed-data budget.

For arithmetic sensing, replace the pointwise Taylor remainder bound by a
verified weighted approximation bound for a specified drift family. This can
increase the permissible drift while retaining the same readings. The physical
remainder bound still needs a declared model or calibration; a solver residual
cannot supply it. Adding more polynomial degrees remains secondary until the
new family makes their value explicit.
