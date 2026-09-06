# Independent review of the strengthened query-transfer framework

Reviewer: `/root/harmonic_extension`, 2026-09-05. **Verdict: the new framework's Theorems A–C, compact-convex support completeness result, and real-rational consumer are sound under their stated contracts.** No unresolved central mathematical or canonical consumer defect was found.

Reviewed [the new complete proofs](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework/PROOFS.md), [transfer.py](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework/transfer.py), its twelve tests, the preceding [unified framework](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/framework/PROOFS.md), and the [original OIG integration](/Volumes/KINGSTON/Vibecoding/Math/OIG_ARITHMETIC_ATLAS_PROTOCOL_INTEGRATION.md). The new result supplies exact profiled geometry, factorization criteria, and source-image perturbation bounds that the earlier generic containment statement did not supply on its own.

Three precise wording clarifications were made during review: W is explicitly Hermitian positive definite for complex measurements; the universal loss witness can be scaled beyond a fixed positive noise radius; and the compact-convex support argument uses the real Euclidean space obtained by realifying complex coordinates. These do not change the mathematical claims or numerical evidence.

## 1. Exact restriction geometry and minimal noise cost

In whitened coordinates, let A=R W^(-1/2), L=ran A*, and N=ran(W^(1/2)B). The correct nuisance-free retained space is **M=L intersect N-perp**. This intersection, rather than an arbitrary restriction of a previously computed nuisance projector, determines the exact minimum noise cost.

Theorem A's proof is complete. For a full residual a=W^(1/2)v, all feasible whitened noise vectors form a-(N+ker A). This affine space is closed in finite dimensions. Its unique minimum-norm vector is P_M a. The decomposition of the complementary residual supplies an actual retained-noise and unrestricted-nuisance explanation, proving a reverse lifting implication as well as a bound. A different lift v with the same retained data changes a only in ker A and therefore leaves the cost unchanged. Nonlinear or infinite-dimensional sources are allowed because the lifting is pointwise in the exact finite observation.

There is an equivalent independent dual description. For a retained residual r in ran R, its minimum noise norm is

    sup Re(lambda* r),
    subject to (RB)*lambda=0 and
               ||W^(-1/2)R*lambda||<=1.

Every feasible lambda gives a lower bound by annihilating nuisance and applying Cauchy–Schwarz. For a nonzero minimizing projection p=P_M a, choose lambda with A*lambda=p/||p||, possible because p belongs to L. Its nuisance pairing is zero because p is orthogonal to N, and it attains ||p||. The zero case uses lambda=0 and the same lower-bound argument. Thus the profiled geometry is the smallest possible deterministic noise budget, not merely a conservative projection estimate.

For retained noise alone, the precision on ran R is `(R W^(-1)R*)^dagger`. A principal submatrix of W generally gives the wrong answer. Our exact witness uses W=[[2,1],[1,2]], retention of the first coordinate, and original error (4/5,-2/5). Its true minimum squared cost is 24/25, while using the principal precision 2 incorrectly gives 32/25. A separate exact Hermitian example with imaginary off-diagonal entries confirms the adjoint convention. Redundant retained rows must retain their range-consistency equations; treating duplicate readings as independently noisy changes the experiment.

## 2. Two factorization conditions and query-specific saturation

The proof correctly separates two claims:

- Restricted full-quotient values A P_(N-perp) a can be evaluated from Aa exactly iff ker A is invariant under P_(N-perp), equivalently L is invariant. This is the operation-order/implementability condition.
- The entire full-data quotient P_(N-perp)a can be reconstructed from Aa exactly iff ker A is contained in N, equivalently N-perp is contained in L. This is stronger.

Both follow by testing a proposed factorization on ker A and, conversely, defining the factor map on ran A. Self-adjointness proves the equivalence of invariant kernel and row spaces. Invariance also makes the two orthogonal projectors commute. A three-dimensional exact example satisfies the first condition while losing an additional nuisance-free coordinate, so it does not satisfy the second.

The universal preservation condition is also correct: if M is smaller than N-perp, a nonzero vector in N-perp intersect M-perp gives a full-data distinction that the retained profile cannot see. Scaling that vector supplies a counterexample at any fixed finite positive noise radius. Conversely, M=N-perp preserves every original source feasibility test.

For a **fixed query**, Theorem B uses the right weaker condition. Each answer-class observation union U_a must be saturated along ker R relative to the promised domain H:

    (U_a+ker R) intersect H = U_a.

Individual source observation sets need not be saturated when multiple sources have the same answer. The independent finite example has two different sources per retained coordinate; restriction loses their identities but preserves their shared query label. Global saturation outside H would also impose an unnecessary requirement.

Equality of noiseless query kernels or uniform minimax error does not imply equality of conditional answer sets. For y=(x+e1,e2), e1²+e2²<=1, retaining y1 leaves minimax error 1. At y=(0,3/5), however, the full compatible x interval is [-4/5,4/5], whereas the restricted interval is [-1,1]. The candidate x=9/10 is admitted only after restriction. This tests the deterministic noise-budget coupling, not a stochastic correlation model.

## 3. Exact composition of shared errors and directional completeness

The stage-error expansion in Section 4 has the correct order: an error introduced after stage j is propagated only through the subsequent operators. A noise or error primitive that occurs in two stages must remain the same primitive when supports are evaluated.

More explicitly, if the stage errors have the shared representation E_j u with u in a declared joint set U, and K_j is the product of subsequent transforms, the final error is F u with F=sum_j K_j E_j. Its **exact directional support** is

    h_final(ell)=h_U(F*ell).

This is immediate from the supremum definition and is minimal for that direction. For a box |u_l|<=r_l it is sum_l r_l |(F*ell)_l|. For a full ellipsoid it is the corresponding dual quadratic norm. The latter is a deterministic shape statement, not a probability or independence assumption. Summing stagewise supports is valid as a product-set enlargement; it need not be sharp. Our scalar witness has stage coefficients +1 and -1 on the same unit-bounded u, so the exact final budget is zero while separate bounds sum to two. Conversely, two genuinely separate deterministic unit-box components can sum to two, making a quadrature budget sqrt(2) unsafe.

The framework's support orientation is correct: when ell(c_i-c_j)>0, separation uses the negative residual support at i and positive residual support at j. Each competing explanation has its own allowed sensor error, hence the sum of the two radii. Sharing a nuisance across acquisition events does not by itself force competing explanations to assign it the same unknown value.

The added compact-convex result is a substantive completeness statement. For two nonempty compact convex response sets, a minimum-norm point of their difference set exists. Its variational inequality supplies a unit supporting direction that attains the exact distance; the reverse inequality is the dual-norm bound. Closed noise balls therefore intersect exactly when the attained distance is no greater than the sum of their radii. This validates optimization over directions when the exact template sets are compact and convex. It is not a license to convexify query unions. The exact responses {-1,+1} for one answer and {0} for another are disjoint with open noise threshold 1/2, while convexifying the first answer class creates a false noiseless alias. The quadratic template architecture correctly keeps alternatives until after feasibility.

## 4. Source-image, continuous-parameter, and numerical transfer

Theorem C consistently calibrates each source by its own positive-definite metric before adding model error, source-relative sensor noise, and source-relative computed-data error. The pair inequality

    lambda_jk > delta_j²+delta_k²

controls every nonzero source direction, with no hidden upper-amplitude assumption. Its proof follows from a block Gram lower bound and Cauchy–Schwarz on the two source amplitudes. Fixed absolute error requires the separately stated amplitude lower bound. Source-dependent relative noise cannot be interchanged with a common absolute radius.

The strict pair inequality is necessary for this general sufficient theorem. For orthogonal one-dimensional source images with block Gram I, relative radii 3/5 and 4/5 attain equality. Nonzero amplitudes 5/4 and 5/3 produce the same legal noisy observation (4/5,3/5). Both error norms are checked exactly in the witness file. Thus replacing the strict inequality by equality would be false. This does not claim the general bound is sharp for every pair of image spaces.

The least-squares conclusion uses the smallest source singular value and explicitly assumes an exact solve or a separately bounded solve error. Pair preconditioning is charged through its operator norm; it is not mistaken for a change in the physical source norm. The 2r real-output lower bound requires unrestricted nonzero r-dimensional sources for at least two labels. It does not automatically apply to a source whose exact amplitude has been supplied as additional information.

The continuous-cell transfer correctly bounds the **operator** over an entire parameter cell and subtracts its error before squaring. In the consumer, the comparison sqrt(c)>=e+sqrt(p) becomes `r=c-e²-p>=0` followed by `r²>=4e²p`. The sign condition prevents a false positive from squaring a negative quantity. A positive proposed floor also ensures the required positive singular-value margin. A finite cover, including both endpoints, remains a model producer obligation; sampled matrices alone do not supply it.

Finally, any nonzero numerical nuisance leakage has unbounded amplitude-dependent error when the nuisance amplitude is unrestricted. Scaling a vector in the nonzero image proves this directly. Exact annihilation, a bounded nuisance amplitude, or a certified data-dependent computation residual is needed. A small matrix discrepancy alone is insufficient. The normal-equation residual bound `||r||/mu` correctly includes the inverse Gram floor; an unverified floating residual cannot serve as its own certificate.

## 5. Consumer audit and exact evidence

The real-rational consumer explicitly rejects inexact scalar inputs at its public certificate gates. `profile_form` verifies a symmetric positive-definite W and independent retained rows. Its independent column basis removes redundant or zero nuisance columns before the Schur formula. `lifting_witness` returns a feasible noise vector and retained nuisance component attaining the same quadratic cost. The mathematical theorem also covers redundant retained rows, but this consumer deliberately requires an independent row basis rather than silently ignoring consistency.

All twelve framework tests pass. Independently, [audit_consumer.py](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework_review/audit_consumer.py) solves the original equality-constrained minimum-noise KKT equations using separate exact elimination. It matches the consumer's noise vector, nuisance component, and minimum cost for **205 residuals** across five experiments, including correlated metrics, coupled retained rows, rank-deficient nuisance, and entirely discarded nuisance. It also checks **180 exact cell sign/endpoint cases** against perfect-square root comparisons. [consumer_audit.json](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework_review/consumer_audit.json) binds the reviewed consumer's file hash.

[examples.py](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework_review/examples.py) reproduces ten separate exact witnesses, including the Hermitian metric case, query saturation, conditional/minimax distinction, shared error budgets, nuisance leakage, convexification, and pair-tube endpoint. Their [saved evidence](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework_review/examples.json) is a replay target, not an unsupported source premise. These finite examples supplement the proofs and are not counted as additional applications or research cycles.

Reproduce from the Math root:

```sh
/private/tmp/math-five-paths-venv/bin/python -S research/transfer_theorem_2026_09/framework_review/examples.py
/private/tmp/math-five-paths-venv/bin/python -S research/transfer_theorem_2026_09/framework_review/audit_consumer.py
/private/tmp/math-five-paths-venv/bin/python -S -m unittest discover -s research/transfer_theorem_2026_09/framework -p test_transfer.py -v
```

The transfer theorem links the new polynomial-drift and separated-spatial-bank applications at the correct level: exact nuisance/noise profiling followed by model-derived residual supports or source-image separation. It does not replace either application's complete arithmetic tails, full graph evolution, or continuous-parameter enclosure with a generic positive matrix.

## Primary-source context and remaining scope

The author's [Donoho paper](https://web.stanford.edu/dept/statistics/cgi-bin/donoho/wp-content/uploads/2018/08/SEOR.pdf) and SIAM's [Anderson–Trapp article record](https://epubs.siam.org/doi/10.1137/0128007) were checked as primary sources. They establish the appropriate historical context of optimal recovery and shorted positive operators. Their specialized results are not used to bypass the complete finite-dimensional proofs supplied here, and no priority claim is made for the general ideas. The SIAM abstract and publication metadata were accessible; no paywalled theorem was assumed from an uninspected proof.

The new framework is mathematically useful because it gives necessary and sufficient exactness/factorization conditions, an attained minimal noise cost, an optimized-support completeness theorem under explicit convexity, and a computable uniform pair margin. Physical accuracy, computational feasibility on an unrestricted source class, and optimal acquisition counts remain application-specific obligations.
