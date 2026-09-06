# Independent harmonic audit

Verdict: **all three adaptive-cycle claims pass for the fixed six-reading product-simplex model**, after one input-domain hardening change described below. In particular, the short schedule's interior collision is an exact existence result, not a floating near-collision. No unresolved mathematical or canonical certificate defect was found.

## Mathematical review

H1 uses the correct factor denominator: two vertices differing in k factors have squared factor distance2k. Their raw response difference gives `(1-cos(t log(X/Y)))/k` after squaring and normalizing. The saturation at Tδ=π, the inverse-arcsine necessary time, and the impossible/zero target cases are correct. Exact enumeration of the171 oriented differences is complete; independently enumerating2016 pairs of actual vertices gives the same closest ratios2,27/25,25/24. The statement is sharp only for its single-pair horizon bound, which is the scope claimed.

H2's nonnegative weighted-minimum inequality correctly preserves the direction of a universal obstruction. Both canonical dual terms are actual three-factor differences. The4096 closed time boxes cover the whole interval[0,21.8]; sampled optimization has no proof role. The vertex floor>1.03 exhausts all source pairs in the finite64-vertex class and is explicitly not transferred to mixtures. Its maximum time29.966619 and H1's stronger necessary horizon20.56316841858 are consistently distinguished from optimal-time claims.

H3's square map is exactly the twelve real/imaginary raw response differences after freezing six of eighteen complement coordinates. The selected derivative-column order matches the active variables, including normalization's negative exponent-zero term and the opposite sign for the second source. Each response is a degree-at-most-three polynomial in the active coordinates with fixed exact transcendental coefficients, so the smoothness hypothesis holds globally. The complete source box is enclosed, including rational-center rounding.

The contraction lemma is proved correctly: the fixed-point iteration is a self-map and contraction on a complete closed box; `||I-RDf||<1` also implies that the square rational preconditioner R is nonsingular. Hence its fixed point is a zero of f, not merely a point with Rf=0. The source-probability and separation gates apply throughout the box and therefore to that exact zero. They exclude both the diagonal pair and every simplex boundary. Only local uniqueness within the fixed-coordinate box is claimed.

## Independent numerical reconstruction

Freshly ran all13 focused tests and full256/384-bit certificate reconstructions; they pass. Independently recomputed the exact exported contraction consequences: L≤2.922557e-6, residual bound approximately6.528321e-15, and `(e+Lrho)/rho<9.451e-6`, comfortably below1. The probability lower bound exceeds.07706673382 and the factor distance exceeds.7999999975, so the stated.07/.79 claims are conservative.

An additional independent implementation expanded all64 integer-labelled tensor terms over the **entire active-coordinate box**, differentiating each coefficient product directly and evaluating phases with `log(integer label)`. It did not call the factored response or Jacobian implementation. With the recorded exact rational preconditioner at320-bit Arb precision it produced L<6.279467e-6 and `(e+Lrho)/rho<1.280779e-5`. Thus a different complete interval polynomial/Jacobian evaluation independently closes the exact-root gate; its wider interval arithmetic does not change the conclusion.

The cited [Rump review](https://www.tuhh.de/ti3/rump/intlab/ActaNumerica2010.pdf), Theorem13.3 on PDF page89, was checked against the primary source. It supports the stated preconditioned inclusion context. Here the explicit norm-contraction proof is self-contained; the numerical witness is the new model-specific contribution, not a claimed new general root theorem.

## Remedial change and limits

Initially `dual_upper` accepted any ratio>1 and changed-factor count≥1, although the dual theorem requires a realizable source difference. The canonical terms were valid, so this did not invalidate the printed result. Reported the gap; the author added exact membership validation against all171 differences and controls for impossible ratio7/6 and ratio25/24 with wrong count2. The latest13-test replay passes and canonical numerical certificates are unchanged.

The results prove one particular short schedule has zero full-model floor despite positive vertex floor. They do not prove that every schedule below30 is noninjective, optimal acquisition time, unknown-clock recovery, or an infinite arithmetic-tail statement. Python exact arithmetic and Arb inclusion semantics remain trusted components; the independent interval reconstruction uses the same Arb library. A test count or small residual alone is never used as a theorem proof.

Reviewed `PROOFS.md`, `SOURCES.md`, all three cycle producers and evidence files, frozen collision inputs, and `test_cycles.py` in `/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/harmonic/`.
