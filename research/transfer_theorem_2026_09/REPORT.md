# A transfer theorem with two further certified consequences

The research now has a developed transfer theorem, a common exact consequence checker, and two substantive application advances: recovery under higher polynomial drift on the same arithmetic acquisition, and an eleven-channel spatial bank. The theorem explains exactly when a reduction preserves the answers, when it only gives a safe enclosure, and which quantitative margins make that enclosure useful.

The [complete proofs](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework/PROOFS.md) and [independent framework review](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework_review/REVIEW.md) are the mathematical starting point. General projection, convex separation and optimal-recovery ideas are classical; this package's claimed contribution is their explicit integration and the checked consequences for the project's models.

## What is now proved about transfer

Begin with the answers consistent with a specified experiment and its actual joint uncertainty:

\[
\mathcal Q(y)=\{q(\theta): y=f(\theta)+Bz+e,\;\theta\text{ admissible},\;\|e\|_W\le\eta\}.
\]

Here z is unrestricted nuisance; bounded, shared or source-dependent coordinates stay inside the joint admissible theta. A reduction must establish exact equality of answer sets or a proved containment in a computable outer set. A singleton outer answer is safe; several outer answers mean the certificate abstains.

**The exact geometry is now explicit.** Whiten the physical noise, let L be the retained measurement row space, and let N be the unrestricted nuisance range. Restriction followed by correct nuisance removal leaves the space

\[
M=L\cap N^\perp.
\]

The squared norm of the whitened residual's projection onto M gives the *minimum possible squared noise cost* of explaining the retained data. The proof constructs the required nuisance and noise, so this is an exact equivalence, not merely an error estimate. It also identifies when restriction and nuisance removal can be interchanged. For a specific coarser query, a separate necessary-and-sufficient condition tests whether discarded fibers add any new answers on the promised domain.

**Approximation has a quantitative contract.** Complete tails, model error and numerical error are propagated through the actual operators before their directional supports are bounded. Reused readings and shared errors retain their common coordinates. Optimizing these supports exactly recovers separation for compact convex response templates; convexifying a nonlinear union of answers can instead create false ambiguity.

**Restricted sensing has an all-source test.** If A_j and A_k are approximate source maps for two different labels, a certified block Gram floor lambda for [A_j,-A_k] separates their complete nonzero-source response sets whenever

\[
\lambda>\delta_j^2+\delta_k^2,
\]

where each delta includes model, sensor and computation error in its declared source norm. A separate individual-map floor gives the continuous-source error. A finite cover by closed time cells, each with a proved remainder, makes these guarantees uniform in continuous time.

The exact consumer reproduces the previous **687 scalar gates across three models**, **392 new polynomial rounding gates**, and **392 additional gates with a jointly budgeted normal residual**. These checks demonstrate a shared mathematical mechanism; they are not hundreds of separate theorems.

## Arithmetic sensing: the degree-six limit came from the enclosure

The previous complete bound supported multiscale quintic drift at noise radius 0.000016, while its degree-six sufficient gate failed. The new bound retains the same **8,900 readings**, the same two physical weightings, the integer envelope 0<=a(n)<=d14(n), and known a(1)=1. It recovers the other **49 integers through index 50** under the following arbitrary complex polynomial drifts:

| Maximum drift degree | Multiscale weighted noise radius | Outer-window weighted noise radius |
|---|---:|---:|
| Six | 0.000100 | 0.000080 |
| Eight | 0.000100 | 0.000080 |
| Ten | 0.000099 | 0.000080 |
| Twelve | 0.000099 | 0.000079 |

Thus the multiscale design tolerates degree eight, and the outer design degree ten, at their earlier centered no-drift noise allowances. Each column refers to its own weighted deterministic error ball. This is not a comparison under an unspecified common sensor-noise distribution.

The improvement uses two discrete summation-by-parts steps on the actual weighted polynomial columns, including both zero-extension boundaries and the nested-window transitions. Frequencies log(n) for coefficient indices 51 through 10^12 are uniformly separated from sampling aliases. The entire remaining infinite tail receives a separate zeta(3/2)^14/(2*10^6) bound. No finite tail cutoff is substituted for the infinite source. At degree six the complete coefficient-bias bounds fall below **0.249284107184** and **0.298235974205** for the two designs.

This is an exact nuisance quotient followed by a sharper approximation bound and the same scalar rounding transfer. It establishes that the previous degree-six failure was a limitation of that enclosure. It does not locate a sharp maximum drift degree; the bounded extension stops at twelve.

Arbitrary drift amplitude is a mathematical-model guarantee. An approximate projector with nonzero nuisance leakage has no uniform amplitude-independent error bound. A deployed calculation therefore needs exact annihilation or a certified residual, not merely a small floating matrix error. All eight degree/design cases permit an exact physical normal-residual bound of **10^-8** jointly with their sensor and digital-correction allowances. The arithmetic proof distinguishes the observation-error gain from this conditional solve allowance; a deployed residual certifier has not yet been implemented.

## Spatial sensing: eleven separated channels

The new directly acquired spatial-average indices are

\[
\{485,488,491,494,497,500,503,506,509,512,516\}.
\]

This is **11 channels instead of 48**, a reduction of **77.08%** from the previous smallest bank and **88.89%** from the earlier 99-channel bank. The model remains n=1001, an arbitrary nonzero source in the two real source modes, known time in [1,2], and unknown integer target among 490 through 510. Each channel still averages globally in the other spatial coordinate.

The new decoder keeps target labels whose full two-dimensional source map can explain the observation within the declared relative error. It then applies the selected map's inverse. It receives the known time and retained readings, not the true target. The certificate covers all **21 individual maps and 210 target pairs**, using **895 whole-cell records in 46 time-cell entries**. Every case separately covers [1,2].

The map is reconstructed from the full finite dynamics in the globally averaged coordinate and a periodic transverse representation. Complete periodic-image, finite-boundary, Taylor and coefficient-enclosure errors are charged. The resulting normalized physical operator error is at most **10^-9**. The physical approximate-map floors are

\[
\mu=(19/16)^2\,7\times10^{-8},\qquad
\lambda=(19/16)^2\,10^{-11}.
\]

They preserve the previous noise allowances: **3*10^-7 times the L2 source norm**, or **3*10^-8 times the relevant H1 source norm**, with the two H1 calibrations kept distinct. Target identification remains exact and relative source error remains below **10^-3**.

The common transfer also leaves room for a further *conditional* computed-data error of 10^-9 times the corresponding source norm. Including that allowance and the model error, the exact inequalities bound source error below **0.000962 with an exact final inverse**. This is an available numerical budget, not a claim that a floating implementation already verifies that budget. Any certified error from computing the final inverse must be added to the source-error bound.

Four real channels remain a necessary lower benchmark for joint recovery of an unrestricted two-dimensional source and multiple labels. Eleven are sufficient under the current robust contract; minimality remains open. Forming these eleven averages after acquiring a full measurement vector does not save acquisition. The channel reduction applies when the specified readouts are directly available.

## What this changes in the research direction

The two advances use different parts of the same theorem. [Arithmetic drift](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/noise/PROOFS.md) uses exact nuisance elimination and complete oscillatory error supports. [Spatial sensing](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/resolution/PROOFS.md) uses restriction, finite-model approximation and separation of complete source-image sets. Both retain explicit physical error norms and numerical obligations. The common framework now does more than organize terminology: it reproduces earlier certificates and supplies the quantitative tests behind new guarantees.

The next focused target is to reduce the separated bank toward the four-channel lower benchmark while preserving an explicit noise/accuracy tradeoff. For arithmetic sensing, the next useful improvement is a verified augmented solve with data-dependent residuals and a bounded nonpolynomial drift budget. Further increasing polynomial degree is a secondary question until its practical value is specified.

The full [verification](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/VALIDATION.json) passed all **15 jobs and 31 focused tests**, including independent reconstructions and 27 full finite-graph diagnostic cases. The [synthesis audit](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/SYNTHESIS_AUDIT.md) checks the conclusions against their proofs and contracts. All 279 recorded historical artifacts are preserved.

These are mathematical guarantees for declared models; physical calibration and hardware noise distributions remain unverified. The [reproduction guide](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/README.md) records which new computations were rebuilt and which unchanged expensive premises are inherited.
