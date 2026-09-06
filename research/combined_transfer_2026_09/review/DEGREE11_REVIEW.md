# Independent review of the degree-eleven construction

**Outcome: the scoped mathematical conclusions are supported.** No remaining
mathematical gap was found in the degree-eleven tail transfer, parity-based
approximation, actual inverse reconstruction, or the distinction between a
failed sufficient gate and a proved recovery result. This is an internal
independent computational/proof review, not external peer review.

## Proof assessment

1. The first eleven orthonormal polynomial columns are unchanged when the
   twelfth column is removed. Recomputing the cross, Schur and query bounds
   with precisely those eleven channels is valid. The construction does
   this explicitly; it does not reuse a degree-twelve inverse or assume its
   coefficient-bias vector survives column removal.
2. Every inherited nuisance-tail channel includes its finite oscillatory
   contribution and complete remote arithmetic tail. Taking channels
   one through eleven changes the finite solve, not the infinite source
   class or its tail coverage. The independent inherited consumer derives
   the new Schur consequences from these channels.
3. The odd approximants from degree twelve contain no twelfth-power term by
   exact parity, so their degree is at most eleven. The even approximants
   from degree ten already have degree at most ten. Combining them is valid
   in the same degree-eleven polynomial space. The odd remainder begins at
   order thirteen and the even remainder at order twelve; complete orders
   thirty-three and thirty-four are still charged. Exact even weighting
   makes the two parity remainders orthogonal, validating the maximum of
   their bounds for every sinusoidal phase.
4. The physical inverse has **61 columns**, reconstructed from 8,900 actual
   phases and weights. Sequential Gram–Schmidt reconstructs the polynomial
   basis independently of the original moment/parity producer. Interval
   containment binds that basis to the complete-tail certificate, and the
   actual Gram defect is bounded by the declared floor. The Hermitian Gram
   row bound controls its spectral defect.
5. The synthetic fixtures really contain a complex polynomial
   of degree eleven with coefficients of order 1e20, at the actual affine
   clock times. Degree eleven is therefore exercised in the data, rather
   than only declared in metadata. The full inverse and the two normal
   residual identities support the accepted B=500 answers. A small normal
   residual at B=4000 does not remove the separately charged family error.

## Independent computations performed

The reviewing agent ran, without altering the degree-eleven package:

```sh
python research/combined_transfer_2026_09/degree11/verify_model.py --bits 384
python research/combined_transfer_2026_09/degree11/demonstrate.py --bits 384
python research/combined_transfer_2026_09/review/check_degree11.py
```

The first command reconstructed both actual forward models and checked all
**1,100 arithmetic/polynomial cross channels**, 22 complete nuisance channels,
42 full weighted approximation norms and four complete Taylor remainder
moments. The second reproduced both sets of 8,900 rational readings and
verified all four saved proposals at 384 bits, including upper bounds on the
saved normal residuals. The retained logs are
[model replay](degree11_model_384.log) and [query replay](degree11_query_384.log).

The separate [review checker](check_degree11.py) imports neither the
new degree-eleven budget nor its consequence producer. It recomputes the
odd/even family sum, the complete uncertainty total, **196 strict rational
rounding gates**, 98 accepted-answer complex disks, data/proposal digests,
and the four saved residual/replay bindings. Its result is
[degree11_review.json](degree11_review.json).

At B=4000 and Omega=3, only 32 of 49 sufficient gates pass in each window.
At B=500 with the other budgets unchanged, all 49 pass in both windows and
the returned integers match the fixture. This supports a useful smaller
amplitude consequence. The B=4000 result does **not** prove degree eleven is
impossible for that experiment, and the least-passing-degree statement must
remain limited to the declared constructions and tested degree set.

## Issues resolved before sealing

The review identified an exact-input API inconsistency and recommended an
explicit cross-window binding. The producer agent confirmed the first input
check was already being added, then tagged the degree-eleven inverse record
with its design and required inverse, approximation and clock records to
share that design. Tests now cover these cases. Numerical data and bounds
were unchanged. The independent review checker confirms the final tagged
record and current evidence digest.

The inherited original arithmetic-tail enumeration remains an explicit,
hash-bound premise with its own complete replay route. This review replays
the new degree-eleven physical channels and consequences; it does not claim
to have independently enumerated that historical tail again. Neither fixture
nor inverse residual establishes number-field realization, sensor statistics
or empirical clock/drift calibration.
