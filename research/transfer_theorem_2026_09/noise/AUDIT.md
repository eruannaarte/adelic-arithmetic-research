# Independent audit of the polynomial-drift extension

**Accepted within the declared mathematical model.** The proof, outward producer, exact consumer and independent reconstruction support all eight degree/design guarantees, for polynomial degrees 6, 8, 10 and 12. No substantive defect was found. One sentence about decreasing sine-series terms was corrected during review: at argument 2.8 the first two magnitudes increase, but the omitted alternating tail at the stated truncation decreases and has the required positive first term. The certified numerical bound was already valid.

This audit was written separately from the producer. Its additional reconstruction is [independent_audit.py](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/noise/independent_audit.py), with exact output and source hashes in [independent_audit.json](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/noise/independent_audit.json). It imports neither the producer nor its consequence checker.

## Mathematical checks

The frequency estimate covers every integer from 51 through \(10^{12}\), using rational exponential bounds, the alternating sine remainder, and concavity on the whole phase interval. The phase estimate is not extended beyond its valid interval. Every remaining coefficient is covered by the absolutely convergent \(\zeta(3/2)^{14}/(2\cdot10^6)\) mass bound. Using the full centered mass in the finite part overcounts some remote mass conservatively; it does not omit any contribution.

Both physical endpoints and the discontinuities introduced by the embedded inner window are included in the full zero-extended second difference. The identity has 8,902 potentially nonzero terms per 8,900-entry column. Its factor \(|1-z|^{-2}\) and physical phase step agree. The constant-sequence adverse control demonstrates that an internal-difference-only version would be false.

The finite inverse retains all 50 arithmetic columns and every arithmetic/polynomial cross term. In particular the constant polynomial is represented by the first arithmetic column; its fitted coefficient is discarded, while the 49 requested coefficients remain well defined. The Neumann row refinement, nuisance Schur bound and augmented Hermitian Gershgorin floor have the stated directions. Positivity is checked before squaring the final rounding condition.

The digital midpoint error, sensor error and exact-normal-residual allowance are charged with their appropriate gains. The first two use the reciprocal square root of the Gram floor; the normal residual uses the reciprocal floor. An approximately annihilating projector cannot give an amplitude-independent error allowance for unrestricted polynomial drift. The proof correctly requires a certified, data-dependent residual for a numerical implementation.

## Separate model reconstruction

At 320-bit outward precision the audit reconstructs both complete weight vectors directly from the original binary64 coefficient literals and their midpoint cosine formula. Finite Fourier cancellation supplies exact normalization; positivity and interval enclosure of that normalization are checked on all physical entries.

It then applies weighted modified Gram–Schmidt to full vectors on all 8,900 physical times, through degree twelve. This is a different calculation from the producer's monomial/moment construction. Uniqueness of the orthonormal polynomial with positive leading coefficient identifies the same exact basis. Norm and orthogonality identities are enclosed. Two successive zero-extended first differences supply the complete second variation. Direct cosine and sine sums rebuild both phase components of all 1,176 nonconstant arithmetic/polynomial cross entries across the two designs. Each reconstructed active cross component, weighted absolute norm and variation lies inside the corresponding saved enclosure; the opposite-parity component encloses zero.

The new audit also proves a looser remote bound without evaluating a zeta special function. For decreasing \(t^{-3/2}\),

\[
\zeta(3/2)\le\sum_{n=1}^{100}n^{-3/2}+\int_{100}^{\infty}t^{-3/2}\,dt
<2.612874098754<2.613.
\]

Each of the 100 finite terms receives an exact rational upper bound from an integer square root. Thus the remote mass can safely be increased to \((2613/1000)^{14}/(2\cdot10^6)<0.345877046\). The audit uses this larger mass, independently reconstructed channel inputs rounded outward to multiples of \(10^{-15}\), and a separate exact rational derivation of the Schur and rounding consequences.

**All 392 coordinate gates still pass** at the declared sensor radii, with digital error \(10^{-20}\) and conditional exact normal residual at most \(10^{-8}\). The smallest resulting certified rounding slack is greater than 0.000202192701008, attained in the degree-eight multiscale case. This slack concerns the audit's deliberately looser constants, not an optimal threshold.

## Executed verification

The following commands were independently run successfully with Python 3.12.14 and python-flint 0.9.0 / FLINT 3.6.0:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/noise/test_oscillatory.py
/private/tmp/math-five-paths-venv/bin/python -S research/transfer_theorem_2026_09/noise/check_certificate.py --extended
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/noise/oscillatory_channels.py --extended --precision 192
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/noise/oscillatory_channels.py --extended --precision 256
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/noise/independent_audit.py
```

The ten focused tests pass. Both complete producer replays agree exactly with the frozen evidence. The separate audit reconstructs its own saved evidence deterministically; its 392 checks are an additional audit job, not 392 unit tests.

The original complete arithmetic bias bounds, arithmetic Gram row bounds, centered mass and midpoint-correction contract remain explicit inherited premises. Their identities and existing strict consumer are checked, and the full producer freshly replays its prescribed physical Gram and midpoint-correction calculations. This audit does not claim a new enumeration of the unchanged million-term arithmetic tail. It supplies no physical noise measurements, apparatus validation, proof that every envelope source is a number field, or certification that a deployed solver has actually met the conditional residual allowance.
