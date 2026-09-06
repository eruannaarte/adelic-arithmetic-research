# Independent review of the structured potential result

A separate agent reviewed the finite-generator, derivative, transfer and
normalization arguments in `../resolution/PROOFS.md` and the implementing
consumer. The current theorem and its fixed budgets pass this review.

The new script `review_potential.py` independently evaluates rational
polynomials by direct powers, forms each two-column inverse directly, and
checks the physical and query-specific norms of both uncertainty corners.
All 63 target/time cases (21 targets at 1, 3/2 and 2) pass. These point checks
are only consistency tests. The separate complete-time consumer also passes a
fresh 384-bit replay of all 2,688 target/time cells.

The review independently derives all three Cauchy tail sums as exact geometric
series, the pure time Hessian bound 15/16, the pure potential remainder and the
mixed bound. Across the entire uncertain potential rectangle,
`||H(g)||≤56/5+4DG<45/4`; this gives a mixed bound `380/3<128`.
The owner clarified the sequential expansion and added the stronger uniform
inequalities to the consumer. Thus no assumption that the nominal generator
norm remains unchanged at a larger potential is needed.

The initial consumer independently proved the declared theorem limits but did
not compare reconstructed cell norms with every smaller stored producer bound.
The owner added those comparisons and an adverse reduced-bound test. The final
384-bit review passes the hardened consumer as well. This strengthens the
stored numerical certificates; it does not change the budgets or theorem.

The independent rational label and inverse gates pass. The global inverse
comparison fails at the same uncertainty rectangle, confirming that retaining
the structured directions through inversion is material. Two different target
explanations retain independent possible values of the clock and potential;
the proof correctly charges both forward tubes.

The review result binds the inspected source and certificate files by SHA-256
and rejects a change during the audit. The finite-x and differentiated-kernel
reconstructions remain explicit physical premises, independently replayed by
the main package. Neither these proofs nor the synthetic examples establish
apparatus calibration.
