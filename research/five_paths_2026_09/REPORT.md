# Five mathematical research paths: supported developments

Research synthesis · 4 September 2026

The most useful development is a sharper account of **which question an experiment can answer, under which uncertainty, and at what cost**. All five paths now contribute a proved extension or a computational certificate beyond the earlier review. The new results are local to their declared models; they do not establish the project's broader philosophical interpretations.

Two findings deserve particular attention. Actual quadratic-field identities improve a discrete-query guarantee beyond an impossibility threshold for a larger coefficient envelope. Harmonic acquisition admits much shorter six-reading schedules with explicit global stability and clock bounds, while a separate five-reading example exposes the difference between local and global recovery. These make focused mathematical presentations with clear hypotheses and comparisons.

The applications also become more concrete. The pendulum guarantee now includes finite preparation error and a shared clock perturbation. Multiscale arithmetic sensing retains a positive noise allowance, although its coefficient-50 noise variance increases. A sharper semigroup remainder extends the finite-resolution certificate to a time interval five times as long at unchanged grid size.

The work starts from the [public research ledger](https://thegodnet.work/number-geometry/) and the local manuscripts and certificates assessed in the earlier review. Classical theorems are cited and their hypotheses checked in the proofs; the work claims new developments of this research package, without asserting historical priority. Exact arithmetic and outward interval computations decide numerical inequalities. Simulations supply additional controls. Noise tolerances in different chapters answer different questions and should not be compared without their source classes and norms.

The five chapters below give the results and limitations. The [proof appendix](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/PROOF_APPENDIX.md) and [claim-to-evidence index](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/CLAIM_EVIDENCE_INDEX.md) provide the full verification route.

## 1. A nonlinear experiment with bounded preparation and clock error

The original double-pendulum result certified that five observations recover two infinitesimal mass/length directions after removing one shared clock direction. It assumed exact preparation. The new result permits **finite, unknown preparation error**, a finite shared clock change, and adversarial sensor noise, and returns an explicit recovery error.

Write u=log(m2/m1), v=log(l2/l1), and let the globally shared clock multiply observation time by exp(e). Throughout |u|,|v|,|e|<=10^-4, each launch may have independent errors of at most rho=10^-7 in both initial angles and both dimensionless angular velocities. Preparation is unknown but remains common to that launch's observations. Its effect is propagated through the nonlinear equations; it is neither measured nor fitted away.

For the selected A+B experiment, outward integration encloses all relevant derivatives over this entire finite box. A fixed, exactly computed weighted left inverse B has uniform Jacobian-deviation norm k<0.077461. Separately certified preparation-output bounds E and the weighted sensor-noise bound ||W^(1/2)n||_2<=eta yield

\[
\|s-s'\|_\infty\le
\frac{2\max_i\{\sum_j|B_{ij}|E_j+
\eta\sqrt{\sum_j B_{ij}^2/w_j}\}}{1-k},
\qquad s=(u,v,e).
\]

This holds for any two parameter vectors consistent with the same observations and allowed uncertainties. Thus any feasible estimate lies within the stated error of the true parameters. The clock remains one shared nuisance; its nonlinear change is included in the derivative bounds rather than removed using an unavailable true-state projector.

At eta=10^-7, the worked comparison is:

| Budget allocation | Certified maximum parameter error |
|---|---:|
| Selected A+B, shares (2/3,1/3,0) | <2.011628e-5 |
| Uniform A+B+C, shares (1/3,1/3,1/3) | <2.489142e-5 |
| Uniform A+B, shares (1/2,1/2,0) | <1.979238e-5 |

All designs have the same seven available local sensors, additive group costs, total budget, and noise rule. The selected design improves the sufficient bound relative to uniform use of all groups, but uniform A+B slightly improves the preparation-dominated bound. Earlier optimality for a different local-information objective therefore supplies no blanket ranking under uncertainty. Conversely, for a required error of 10^-4, the selected design certifies a larger noise allowance than either uniform comparison: approximately 5.68e-6 versus 4.40e-6 and 5.08e-6. Exact half-plane inequalities describe the preparation/noise tradeoff.

The proof uses outward Picard–Taylor tubes and a separate rational checker; alternate time partitions, independent mechanical evaluations, and finite nonlinear controls pass. This is a finite neighbourhood certificate, extending the earlier point-derivative result. The preparation tolerance is small and unvalidated experimentally. The comparison concerns proved sufficient bounds, not actual minimax errors, global parameter recovery, or apparatus performance. A larger region requires sharper enclosures or additional preparation measurements.

Proof and evidence: [complete derivation](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path1_preparation/PROOF.md); [independent audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path1_preparation/AUDIT.md).

## 2. Harmonic acquisition: six readings at much shorter times

How expensive is a mathematically minimal experiment? For three known prime axes `(2,3,5)`, each carrying an arbitrary probability distribution on four exponent states, the existing theory gives an exact answer in reading count: six complex harmonic values suffice globally, and every smaller schedule has exact collisions. But its certified six-reading example reaches time `220023.423`. Reading count alone conceals a substantial acquisition cost.

We reconstructed both sides of that theorem. A factor DFT supplies the upper construction; reversal symmetry and Borsuk's antipodal theorem supply the matching obstruction, including collisions arbitrarily close to the uniform product. Local recovery is different: five readings can have an injective differential at an interior point, as a new Arb-certified example demonstrates, while still failing globally.

The main extension is a quantitative time–clock–stability tradeoff. Centering each exponent alphabet and retaining the individual phase errors yields a tighter derivative bound than the original common phase box. Because that bound holds over the entire product of closed simplices, integration along every factor-coordinate chord proves global separation; sampled Jacobian ranks are unnecessary.

At six readings and absolute time errors bounded by `0.001`, the same improved theorem gives:

| Design | Maximum time | Certified global factor floor |
|---|---:|---:|
| Existing schedule | 220023.423 | greater than 1.2391 |
| New short schedule | 1463.985949 | greater than 0.5039 |
| New balanced schedule | 2773.804407 | greater than 0.8150 |
| New higher-floor schedule | 8081.202441 | greater than 1.0907 |

Here the factor norm is the Euclidean norm of the concatenated changes in all factor probabilities. The floor `c` means every pair of factor tuples satisfies `||data-data'||_2 >= c||q-q'||_fac`. The balanced design reduces maximum time by a factor of **79.3**. The old schedule retains the strongest floor when evaluated with the same new bound: this is a measured tradeoff, not an across-the-board improvement.

The timing theorem covers independent bounded offsets and therefore also a single shared offset. A pure shared clock-rate error `beta` is covered when `|beta|T_max<=0.001`; the balanced schedule consequently permits `|beta|<=3.6051e-7`, compared with `4.5449e-9` for the old schedule.

Unknown timing requires a separate finite nuisance bound. For the balanced schedule, adversarial raw-data noise of Euclidean radius `0.001` plus an unknown shared time offset of `0.001` gives factor-recovery error at most **0.063781** for every global nominal least-squares minimizer. If the realized timing is known, the same sensor noise gives error at most **0.002454**. Neither claim assumes independent noise samples.

The proof appendix and small checker reconstruct prime logarithms and acquisition phases with outward Arb intervals, then derive the decisive bounds using exact rational arithmetic. The original baseline verifier, a 512-bit refinement, and 15 focused controls pass. These results apply to the finite normalized product model and its declared metrics. They do not establish the shortest possible acquisition time, an efficient global optimizer, or a theorem for infinite arithmetic tails.

Proof and evidence: [complete derivation](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path2_harmonic/PROOFS.md); [independent audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path2_harmonic/AUDIT.md).

## 3. Arithmetic sensing: bias improvement survives some noise, while variance rises

The multiscale arithmetic sensor previously recovered 50 integer coefficients from 8,900 complex observations with certified noiseless error below 0.498028. That narrow margin below one half left an essential question: does any useful guarantee survive actual measurement error?

The new calculation follows noise through the implemented weighted decoder, retaining the complete arithmetic tail and Gram bounds. The 2,550 short-window samples are already among the 8,900 long-window observations. Their weights are added before computing covariance; they do not provide independent copies of the sensor noise.

For coefficient n, let b_n be the complete deterministic bias bound, and let q<1 bound the Gram defect. If the sensor error satisfies

\[
\sum_j w_j|\epsilon_j|^2\le\eta^2,
\]

then its decoded contribution has magnitude at most n²η/√(1−q). Provided every b_n<1/2, all 50 integers are recovered by rounding whenever

\[
\eta^2<\min_{1\le n\le50}
\frac{(1/2-b_n)^2(1-q)}{n^4}.
\]

The multiscale certificate permits η<7.88735×10⁻⁷; the declared rational radius **7×10⁻⁷** passes strictly. For identical assumptions across designs, a common bound |ε_j|≤7×10⁻⁷ on every physical reading implies both designs' weighted bounds because both weight vectors have total mass one. The single-window control's existing bias bound is approximately 0.595929, so this calculation cannot certify its rounding even without noise. That is an insufficient certificate, not an impossibility result.

Under the separate assumption of independent circular complex Gaussian errors with E|ε_j|²=10⁻¹⁰, exact covariance propagation and a union bound give probability of any rounding failure below **5.466×10⁻¹⁴** for multiscale sensing. This probability includes the deterministic tail bias. It depends on the stated distribution; it is not an adversarial-noise guarantee or a measured hardware error rate.

The comparison also disproves a tempting blanket advantage. For coefficient 50, outward variance bounds prove

\[
\frac{\operatorname{Var}_{\rm multiscale}}
{\operatorname{Var}_{\rm single}}>1.000265975.
\]

Multiscale weighting improves the bias certificate while increasing this coefficient's iid noise variance. Treating the nested readings as independent would incorrectly remove a covariance term; a direct numerical check shows that omission understates the squared-weight sum by roughly 0.51%.

The extension consists of explicit noise tolerances, a distribution-specific probability guarantee, and a certified bias–variance tradeoff at equal acquisition budget. A separate rational checker verifies the decisive inequalities; complete finite and infinite arithmetic-tail reconstructions establish their inputs. The results apply to the degree-14 coefficient envelope and its verified arithmetic subclasses. Physical noise calibration, extra decoder-rounding error, and broader claims of statistical superiority remain separate questions.

Proof and evidence: [complete derivation](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path3_noise/PROOF.md); [independent audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path3_noise/AUDIT.md).

## 4. Arithmetic constraints improve a discrete query beyond its envelope limit

The earlier observability work distinguished recoverable integer questions from unstable continuous reconstruction. Its unresolved arithmetic issue was whether coefficient patterns used to prove impossibility correspond to actual number fields. We now settle a tractable part of that issue for **all real quadratic fields**, without a discriminant ceiling, and use it to improve a query guarantee. Here a(n) counts integral ideals of norm n, and readings are values of the field's Dedekind zeta function on Re(s)=2.

There is an exact finite-prefix criterion. For any integer N≥2, the coefficients a(1),…,a(N) are realizable precisely when a(1)=1, coprime multiplicativity holds, each prime coefficient belongs to {0,1,2}, and

\[
a(p^k)=\sum_{j=0}^{k}(a(p)-1)^j\qquad(p^k\le N).
\]

Every compatible prefix occurs in infinitely many distinct real quadratic fields. The proof prescribes splitting, inertia, or ramification at each relevant prime using the Chinese remainder theorem, then applies Dirichlet's theorem to a coprime progression. Thus a finite prefix can determine local arithmetic information while leaving field identity unresolved. This is a consequence of classical arithmetic, newly applied to the project's source-class question; no priority claim is made for the underlying realization principle.

For a concrete example, discriminants 453, 3165, and 381 all give a(2)=0,a(3)=1, but their a(5) values are 0,1,2. Their arithmetic also forces a(20)=a(45)=a(5). In general, a(20)=a(4)a(5) and a(45)=a(9)a(5), with a(4),a(9) each 1 or 3. A coefficient-envelope collision changing only a(5) is therefore impossible for quadratic prefixes of length at least 20.

This constraint has a measurable consequence on the same 8,900-observation grid used in Path3. First recover a(2),a(3), which fixes a(4),a(9). Then estimate a(5) by combining the unrounded coefficient estimates at 5,20,45, with weights chosen to minimize a conservative noise-amplification bound. Complete divisor-function tails, including every integer beyond the finite sum, are retained.

For every real quadratic field, this two-stage decoder recovers a(5) under adversarial weighted observation error

\[
\|\epsilon\|_W\le\mathbf{0.02001}.
\]

The sufficient boundary is above 0.02003156 in the least favorable arithmetic case. By comparison, the larger independent coefficient envelope has two allowed sources differing only at5 whose responses are distance1/25 apart. Noise of radius **0.02** makes them indistinguishable. The new actual-field guarantee strictly exceeds that envelope limit, using the same readings, measure, query, and noise norm. The gain is small; its significance is a rigorously demonstrated difference between source classes.

The appendix also gives an exact compact-set criterion for robust label recovery and a simple example where convexifying integral uncertainty collapses a positive threshold to zero. These examples are kept distinct from number-field realizability. Exact field witnesses, a rational tail/consequence checker, and a higher-precision finite-tail replay support the arithmetic result. It does not recover the whole field, establish the optimal radius, or settle realizability for higher-degree envelope extremizers.

Proof and evidence: [complete derivation](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path4_realizability/PROOF.md); [independent audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path4_realizability/AUDIT.md).

## 5. A wider time window for finite-resolution sensing

A continuum model can have a positive information floor while its discretization loses the weakest informative direction. The relevant test is therefore whether the full matrix error is smaller than the smallest continuum information value, under the same source and output calibration.

For the existing two-port Neumann benchmark, the previous certificate covered only lattice times 1≤tau≤1.2 at n=1001. We now certify **every tau∈[1,2] at the same resolution**, retaining the full diffusion–modulation generator and exactly central target. The interval length increases fivefold. The source band remains the first two cosine modes, and the interaction is V(x)=1+4x/5.

| Source metric | Uniform matrix-error upper | Uniform finite information floor |
|---|---:|---:|
| L2 | 2.55072×10^-8 | >1.17644×10^-7 |
| Continuum H1 | 2.25949×10^-9 | >1.29282×10^-9 |
| Natural discrete H1 | 2.17949×10^-9 | >1.37282×10^-9 |

The numbers are conservative summaries of exact rational endpoints. The natural discrete calculation uses its own grid-dependent energy metric; substituting the continuum metric would answer a different question.

The enabling step is an improved analytic remainder. A raw Gram entry is a product of two semigroup responses. On a tensor product space this product has the positive symmetric generator A⊗I+I⊗A. At time t≥a>0, spectral decay gives the derivative bound k!/a^k, independently of the potentially large generator norm. Combining this with the derivatives of sqrt(1+t) gives an explicit rational Taylor remainder. On the cell [1,1.5], its two-family entry bound is below 1.882×10^-11; the earlier generator-norm bound exceeds 0.00259. The improvement is more than 10^8-fold for this remainder, allowing two degree-18 Taylor cells to close the wider interval.

The proof is computationally certified rather than inferred from sampled times. Arb encloses every finite and continuum Taylor coefficient. A separate rational checker reconstructs polynomial ranges, remainders, two-by-two spectral inequalities, the gap-free time cover, and the positive transferred floors. Fresh 256-bit quadrature revalidates the inherited continuum floors. An independently implemented dense Arb matrix exponential checks small-grid coefficients and derivatives.

For example, the natural discrete row guarantees that throughout [1,2], the squared normalized response to any two-port intervention is at least 1.37282×10^-9 times its discrete H1 source cost. Thus n=1001 is an explicit sufficient resolution for this time window. It is not claimed minimal.

This result is a useful application of classical spectral and validated-numerical methods, not a new general spectral theorem. It does not extend to arbitrary source bandwidth, displaced targets, or physical local detectors. Nor can any fixed grid work for all late times: its finite response eventually decays, while the normalized continuum information remains positive. The next justified extension is target-placement robustness or a larger source band, with its smaller spectral floor explicitly included.

Proof and evidence: [complete derivation](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path5_resolution/APPENDIX.md); [independent audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path5_resolution/AUDIT.md).

## What the results justify next

The quadratic query is the clearest bridge from an abstract uncertainty envelope to actual arithmetic. Its next question is whether more multiplicative relations produce a materially larger margin, or a sharp threshold, under the same measurement norm. The harmonic work is the strongest compact acquisition study: finding rigorous lower time bounds would complement its improved schedules.

For experimental design, the next useful step is increasing the certified preparation region and checking which tolerances an apparatus can achieve. For multiscale sensing, optimize bias and noise variance jointly; the present certificate establishes a tradeoff rather than universal statistical superiority. For resolution transfer, vary target position or add source modes while continuing to compare error with the weakest information direction.

All central numerical claims have a route back to their defining model, not only a saved matrix. The package records complete arithmetic-tail replays, nonlinear integration, phase reconstruction, continuum quadrature, precision controls, and independent consequence checkers. The [reproduction guide](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/README.md) distinguishes fast checks from expensive reconstructions. These verifications establish the stated mathematical guarantees; they do not supply empirical validation of a pendulum model or a physical noise distribution.
