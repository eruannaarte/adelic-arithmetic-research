# Independent review of the shared theorem and arithmetic clock proof

Reviewed by the spatial-potential agent, separately from the framework and
arithmetic authors. This is a bounded mathematical/code review, not a claim
of external peer review or an additional whole-data numerical reconstruction.
Read `../framework/PROOFS.md`, `../arithmetic/PROOFS.md` and
`../arithmetic/clock_bound.py`. No blocking issue was found.

* **Directional inverse theorem.** With the stated processed-data
  representation and full-column-rank nominal map, A-dagger A=I gives the
  inverse-direction term plus the unstructured residual gain directly.
  Applying a linear query only changes these two gains. The quotient must
  remove every admitted nuisance image or its leakage must already be
  bounded; the theorem explicitly requires this. The box/polytope vertex
  argument follows from convexity of a matrix norm of an affine direction.
  Competing explanations correctly retain separate unknown parameters.

* **Weighted pair theorem.** Weighted Cauchy–Schwarz bounds the squared
  sum of the two relative error radii by the proposed positive block form.
  Strict domination of that form by the pair Gram matrix then contradicts
  a common observation. The equal-radius split delta²/a and
  delta²/(1−a) has reciprocal-radius sum exactly one. This remains valid
  if its split varies by pair and by independently covered time cell.

* **Envelope ratios do not constrain the actual source.** The arithmetic
  proof first takes the absolute cross-phase inner product. The resulting
  quadratic has nonnegative coefficients, hence is monotone in both actual
  nonnegative magnitudes. Replacing each magnitude by its own envelope is
  therefore valid even if one actual coefficient is zero. The later ratio
  bound applies only to the two strictly positive envelope magnitudes.

* **No integer or infinite tail is lost.** Each integer belongs uniquely
  to (n,2n) with even v2(n). The exceptional pair (1,2) has zero first
  derivative coefficient at 1 and is charged by C2. For valuation k, the
  factor binom(k+13,13)/4^k times the odd-part derivative and mass gives
  the complete class mass. The odd identities
  Zodd=3Z/4 and Lodd=3L1/4−(log 2)Z/4 are correct. Refinement subtracts
  nonnegative savings times **lower** class masses from a bound that
  already includes every coefficient through the complete D1 upper bound.
  Classes after k=38 remain charged with the global factor. The subtraction
  orientation is therefore conservative.

* **The global and refined factors are valid.** The envelope ratio lies
  in [1/4,35/6], whose minimum product fraction is 210/1681. On each
  smaller interval the function r/(1+r)² has its minimum at an endpoint.
  The code checks that each refined square-root upper bound is no larger
  than its global counterpart. Multiplication and subtraction use rational
  outward endpoints with the required signs.

* **Clock and nonlinear remainder.** For each fixed source, the first
  affine-clock variation is linear in its two shared errors. Its weighted
  norm is convex, so four corners cover the rectangle without introducing
  independent errors at each sample. Exact evenness of the declared weights
  and grid makes the second and fourth clock moments identical at all four
  corners; the phase correlations themselves are evaluated at all corners.
  The complete identity
  D2=14 Z^13 L2+182 Z^12 L1² is correct. The summands used in the tail
  integrals are decreasing beyond N=1000. The pointwise exponential remainder
  D2 delta_j²/2 gives the weighted fourth-moment remainder after taking the
  W norm. That fourth moment is a convex function of the affine-clock
  parameters, so the corners also bound the full nonlinear rectangle.

* **Scope of the arithmetic gain.** The new complete bound is in the
  physical reading norm. Its survival under an orthogonal nuisance quotient
  is valid by contraction. The presentation explicitly avoids claiming an
  optimized projected query bound. Actual solve residuals, model mismatch,
  and calibration remain separate premises.

The root package records its separate 384-bit numerical arithmetic review.
This review does not substitute for those computations or for replay of
historical full-tail certificates.
