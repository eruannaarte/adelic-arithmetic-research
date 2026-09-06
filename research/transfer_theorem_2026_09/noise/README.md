# Reproducing the oscillatory polynomial-tail certificate

Read [REPORT.md](REPORT.md) for the findings and [PROOFS.md](PROOFS.md) for the complete theorem. [OBJECTIVE.md](OBJECTIVE.md) records the core goal and the bounded successor. All commands below are run from the Math project root and leave prior research files unchanged.

## Fast exact checks and independent controls

The consumers use only Python's standard library. The tests additionally use the existing NumPy, mpmath and python-flint environment.

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/noise/check_certificate.py
PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/noise/check_certificate.py --extended
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/noise/test_oscillatory.py
```

The first command checks the frozen degree-six core. The second checks degrees 6, 8, 10 and 12 in both weight designs. Both also check the conditional exact normal-residual allowance of \(10^{-8}\). The ten tests independently reconstruct physical arrays and polynomial bases, exercise complete endpoints and a remote alias, reject changed contracts, and decode eight full-reading examples. Floating examples are diagnostics; they are not uniform or outward proofs.

## Separate independent audit

The [independent audit](AUDIT.md) reconstructs both complete physical designs at 320 bits, using full-vector Gram–Schmidt and two first-difference passes instead of the producer's moment/parity construction. It also proves the coarser bound \(\zeta(3/2)<2.613\) by a positive finite sum and integral remainder. With independently rounded inputs and that separate remote bound, all 392 coefficient gates still pass, including the conditional normal-residual allowance. Reproduce the saved audit with:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/noise/independent_audit.py
```

This job is more expensive than the fast consumers and was authored and executed by a separate reviewer. Its [evidence](independent_audit.json) distinguishes the independent new-channel reconstruction from inherited arithmetic-tail premises.

## Full reconstruction from the defining physical model

These jobs use outward Arb arithmetic and are more expensive than the consumers:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/noise/oscillatory_channels.py --precision 192
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/noise/oscillatory_channels.py --extended --precision 192
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/noise/oscillatory_channels.py --extended --precision 256
```

Each command freshly reconstructs the positive physical weights, arithmetic Gram matrix, inherited complete midpoint correction at all 8,900 readings, \(H_0\), and the new weighted polynomial basis, full second differences, cross moments and \(\zeta(3/2)\). It then compares every canonical outward enclosure and exact consequence with the saved evidence. The 256-bit job must reproduce the same enclosing rational endpoints, not merely close decimals.

`core_evidence.json` was frozen before the bounded extension. `evidence.json` contains the degree-twelve basis and the four selected degrees. The producer's `--write` switch is for deliberate regeneration of the corresponding new evidence only; it is not needed for verification. `check_certificate.py` imports neither this producer nor Arb. It checks predecessor bindings and reconstructs the proof's rational implications independently; its numerical intervals become model certificates only in conjunction with the full outward replay.

## Exact deployment interface

For a selected record, let `A[n-1]` be `complete_coefficient_bias_upper[n-1]`, `f = 1 - augmented_gram_defect`, `eta = declared_sensor_radius`, and `Xi = 1/10^20`. The scalar query is the integer \(a(n)\), \(2\le n\le50\). The sensor-plus-digital gain is \(n^2/\sqrt f\). Check

```text
margin = 1/2 - A[n-1]
margin > 0
n^4 * (eta + Xi)^2 < margin^2 * f
```

For a **verified exact physical normal residual** of Euclidean norm at most `rho`, replace `margin` by `1/2 - A[n-1] - n^2*rho/f`. `normal_residual_budget(record)` proves all 49 such gates at `rho = 1/10^8`. It does not compute or certify a residual from a user dataset. Any error in residual evaluation must be included in the asserted bound. A generic floating solve without this extra verification has only diagnostic status.

## Inherited premise boundary

The unchanged arithmetic-channel bounds include the original finite coefficient enumeration through \(10^6\) and the complete remote-tail proof. This package checks their exact consequence contracts and SHA-256 bindings and rebuilds their finite measurement Gram, but does not repeat the unchanged expensive coefficient enumeration. Its earlier reconstruction history is documented in [the predecessor reproduction guide](../../unified_query_2026_09/noise/README.md) and the linked earlier packages. The new cutoff \(10^{12}\) does not introduce an enumeration: the finite band has a uniform analytic oscillatory bound, and every coefficient above it is included by the zeta moment bound.

All arithmetic coefficients obey the full envelope \(0\le a(n)\le d_{14}(n)\), with known \(a(1)=1\). Drift coefficients may be complex and unrestricted in the mathematical theorem. The two physical weighted norms and reused-reading covariance remain explicit. No empirical calibration or physical noise-law validation is part of this package.
