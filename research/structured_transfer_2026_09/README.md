# Reproducing structured query transfer

Start with the [report](REPORT.md), [scope fixed before discovery](PROTOCOL.md),
and [shared proofs](framework/PROOFS.md). All seven predecessor packages are
preserved by [553 historical hashes](PREVIOUS_ARTIFACTS_SHA256.json).

Use Python 3.12 with [requirements.txt](requirements.txt). The existing runtime
is `/private/tmp/math-five-paths-venv/bin/python`. Run from the Math root:

```sh
export PY=/private/tmp/math-five-paths-venv/bin/python
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
```

## Fast verification and exact consequences

```sh
$PY research/structured_transfer_2026_09/integrity.py
$PY research/structured_transfer_2026_09/framework/test_transfer.py
$PY research/structured_transfer_2026_09/framework/applications.py
$PY research/structured_transfer_2026_09/arithmetic/consequences.py
```

Integrity checks historical and new hashes, component manifests, local links,
syntax and report claims. It does not rerun every physical reconstruction.
The adapter re-evaluates the exact transfer inequalities using the separately
established physical premises. It deliberately includes failed older
sufficient gates; their failure is part of the comparison, not a failed
validation. The adapter writes a fresh deterministic applications receipt.

## Complete time and actual-model reconstruction

| Objective | Reproduction route |
|---|---|
| Six rows | [six_rows/README.md](six_rows/README.md): exact polynomial producer and independent Bareiss/Sylvester consumer; all 231 time covers; seven physical ambiguity witnesses; 320-bit raw fixture replay and decoder |
| Structured potential | [resolution/README.md](resolution/README.md): full finite-x potential derivative; complete nonlinear, image and boundary bounds; independent 2,688-cell consumer; direct perturbed-model raw data and decoder |
| Weighted clock and degree cost | [arithmetic/README.md](arithmetic/README.md): complete valuation masses, all affine corners and second remainder; fixed-degree matrix/residual/cost study; new 60-fold-clock data and exact proposals at 384 bits |

The physical spatial kernel, weighted polynomial approximants and complete
arithmetic-tail/centering premises are unchanged. Their original full
reconstruction paths and hashes remain in the
[preceding package](../uncertain_transfer_2026_09/README.md). New spatial
potential derivatives and complete arithmetic clock envelopes are reconstructed
in this phase; no finite simulation substitutes for an infinite-tail premise.

## Focused behavior and adverse checks

```sh
$PY -m unittest discover -s research/structured_transfer_2026_09/resolution -p test_resolution.py
$PY -m unittest discover -s research/structured_transfer_2026_09/six_rows -p test_six.py
$PY -m unittest discover -s research/structured_transfer_2026_09/arithmetic -p test_clock.py
```

Together with the shared suite these are 32 tests: ten potential, eight
six-row, eight arithmetic and six common. Tests reject weakened or corrupted
records, omitted clock corners/remainders, excessive error budgets, malformed
inputs and false degree or separation claims. The spatial suites include
complete certificate initialization and take longer than the scalar tests.

## Independent review

- [Clock review](review/clock_review.py) independently rebuilds all physical
  phase sums and complete valuation masses using analytic zeta derivatives
  and the odd Euler factor at 384 bits. It imports no current producer or
  consumer. [Result](review/clock_review.json)
- [Six-row review](arithmetic/six_review.md) by the arithmetic agent checks the
  full weighted polynomial consumer, exact two-source inequality, endpoint
  raw examples and rejection behavior.
- [Potential review](six_rows/REVIEW_POTENTIAL.md) by the six-row agent checks
  the inverse directions, all derivative/remainder assumptions and a fresh
  full-time replay at 384 bits.
- [Shared and arithmetic proof review](resolution/CROSS_REVIEW.md) by the
  potential agent checks the directional/weighted-pair theorems and complete
  arithmetic pairing, including the distinction between actual coefficients
  and their envelopes.

These are independent internal reviews, not external peer review. Their
scopes are explicit: point checks supplement full-time consumers; the recorded
normal residuals come from outward actual-matrix reconstruction.

Artifact regeneration may change timings and hashes. Use a new versioned
package for changed claims. Replaying a saved certificate at another precision
can change the numerical enclosure receipt even when it proves the same bound.
The [validation manifest](VALIDATION.json) records what actually ran here.
See also the [completion audit](COMPLETION_AUDIT.md).
