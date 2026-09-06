# Higher polynomial drift with complete oscillatory tails

**The degree-six objective is achieved, and a bounded extension certifies drift through degree twelve.** All 49 unknown integer coefficients remain recoverable from the same 8,900 complex readings, with the same arithmetic source envelope and physical weight vectors. The new proof substantially tightens the nuisance-tail enclosure while retaining every omitted coefficient.

The preceding pointwise-tail method produced degree-six bias bounds above 0.6116 for the multiscale design and 0.6617 for the outer window, exceeding the rounding threshold of one half. Those failures did not establish impossibility. The new complete bounds are below 0.249285 and 0.298236, respectively, restoring the earlier centered no-drift sensor allowances of 0.000100 and 0.000080 in their declared weighted norms.

The finite experiment samples a Dirichlet series with integer coefficients satisfying \(0\le a(n)\le d_{14}(n)\), with \(a(1)=1\) known. Its nuisance is an arbitrary complex polynomial in time. The source class is the full stated envelope; the theorem does not assume every such sequence arises from a number field.

## What changed mathematically

A weighted polynomial's response to an oscillating omitted mode is much smaller than its absolute norm alone suggests. Two exact summation-by-parts steps bound that response by the full second difference of its zero-extended physical weight column. The boundary terms are essential and are retained.

For every omitted coefficient from 51 through \(10^{12}\), an exact uniform phase bound puts the denominator above \(2/3\). Every coefficient beyond \(10^{12}\) is covered by the complete analytic mass bound

\[
\sum_{n>10^{12}}\frac{d_{14}(n)}{2n^2}
\le\frac{\zeta(3/2)^{14}}{2\cdot10^6}<0.344721270427.
\]

The remote bound remains valid at later sampling aliases, where the finite-band phase estimate would fail. It is not permissible to discard this remote channel.

The resulting degree-six nuisance channel is below 0.231367 for the multiscale weights and 0.231429 for the outer weights, improving the previous channel bounds by more than 1,334 times. This measures improvement of a proof bound. Known centering and sharper analysis do not create additional physical information.

## Bounded extension and useful tradeoff

After freezing the degree-six certificate, the same construction was tested at degrees eight, ten and twelve. Each row below has strict exact rational checks for all 49 unknown coefficients. Bias values are rounded upward.

| Maximum polynomial degree | Multiscale bias bound | Multiscale sensor radius | Outer bias bound | Outer sensor radius |
|---:|---:|---:|---:|---:|
| 6 | 0.249284107184 | 0.000100 | 0.298235974205 | 0.000080 |
| 8 | 0.249675965042 | 0.000100 | 0.298629056012 | 0.000080 |
| 10 | 0.250385107704 | 0.000099 | 0.299340416429 | 0.000080 |
| 12 | 0.251520391985 | 0.000099 | 0.300479209164 | 0.000079 |

Thus the multiscale design accommodates degree eight without reducing its earlier declared sensor allowance; the outer window reaches degree ten at its earlier allowance. Degree twelve costs 1% and 1.25%, respectively, relative to those allowances. These are certified budget comparisons, not optimal noise thresholds. Lower-degree polynomials belong to the listed nuisance spaces and inherit their guarantees. The search deliberately stops at twelve.

## Transfer and implementation meaning

The [proof](PROOFS.md) instantiates the [common transfer theorem](../framework/PROOFS.md) in the physical weighted metric. Exact elimination of unrestricted polynomial nuisance preserves the question's answer set. The complete infinite remainder passes through the actual finite Schur complement and inverse. Each scalar coefficient receives an enclosure narrower than half an integer step, so all compatible sources have the same rounded answer.

The digital midpoint error remains explicitly budgeted at \(10^{-20}\). A further exact consequence check permits a certified physical normal-equation residual of at most \(10^{-8}\), jointly with every displayed sensor allowance. This is a conditional contract for a deployed solver: matrix, dot-product and residual-evaluation errors must be rigorously enclosed. A floating residual or a merely close approximate projector is not that certificate. Any nonzero projector leakage can grow without bound under unrestricted drift amplitude.

The two weight vectors define different sensor-noise norms. The shared reading count does not make their noise balls equal; a uniform pointwise error bound implies either normalized weighted bound. Physical covariance retains the cross term from reused inner-window readings. No random noise law or universal statistical advantage is claimed.

## Validation and conclusions

The complete outward reconstruction agrees at 192 and 256 bits. The standard-library consumer independently rederives all eight degree/design consequences and the additional 392 residual-allowance gates. Ten independent and adverse controls pass, including direct physical polynomial reconstruction through degree twelve, actual omitted-mode responses, full-reading source-plus-drift examples, an alias beyond the finite band, missing-remote rejection, endpoint necessity, and reused covariance.

A [separate independent audit](AUDIT.md) reconstructs both full physical designs and every new channel at 320 bits. Even its coarser independently proved \(\zeta(3/2)<2.613\) bound and independently rounded inputs preserve all eight cases including the residual allowance, with minimum rounding slack at least 0.000202192701008.

The unchanged original arithmetic-tail enumeration through \(10^6\) and its complete remote certificate are inherited and hash-bound, with their earlier replay history recorded. This extension freshly reconstructs all new channels and all 8,900 digital midpoint values; it does not claim to rerun unchanged expensive enumerations. See the [reproduction guide](README.md) and [validation record](VALIDATION.json).

The main finding is that oscillatory nuisance channels remove the apparent degree-six barrier in the earlier proof. The improvement comes from following the true physical operator through complete tails and nuisance elimination. The result does not establish maximal drift degree or apparatus feasibility. The remaining concrete implementation task is a solver that certifies its exact-model normal residual on supplied data; that task can use the quantitative allowance proved here.
