# Reproducing the uncertain-acquisition transfer package

Start with [REPORT.md](REPORT.md), the self-contained
[transfer proofs](framework/PROOFS.md), and the initial [protocol](PROTOCOL.md).
The report separates proved uniform guarantees, actual synthetic observations,
failed sufficient bounds and unmeasured calibration premises.

Use the existing interpreter, or a separate Python 3.12 environment with
[requirements.txt](requirements.txt). Commands run from the Math project root:

```sh
export PY=/private/tmp/math-five-paths-venv/bin/python
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
```

## Fast consequences and historical preservation

```sh
$PY research/uncertain_transfer_2026_09/integrity.py
$PY research/uncertain_transfer_2026_09/framework/applications.py
$PY research/uncertain_transfer_2026_09/noise/consequences.py
```

Integrity is read-only. It checks all 467 historical files, new evidence hashes,
component validation manifests, documentation links and central quantitative
claims. It does not rerun every mathematical reconstruction. The common adapter
recomputes all spatial cell-transfer gates, the new timing/mismatch budgets,
actual integer gates and raw packet consequences. Its physical and complete-tail
premises are established by the consumers below and recorded in validation.

## Focused tests and exact raw decoding

```sh
$PY research/uncertain_transfer_2026_09/framework/test_uncertainty.py
$PY -m unittest discover -s research/uncertain_transfer_2026_09/resolution -p test_resolution.py
$PY -m unittest discover -s research/uncertain_transfer_2026_09/noise -p test_uncertainty.py
```

There are eight tests in each component. The framework suite validates the
entire spatial certificate once, then exercises all twelve actual raw examples,
strict boundaries, incompatible data, expanded uncertainty, malformed inputs,
and scaling across 200 orders of magnitude. It writes a fresh deterministic
[raw-results receipt](framework/raw_results.json). That suite took about 67
seconds here; the two focused component suites are shorter.

[raw_clock.py](framework/raw_clock.py) is the operational interface for exact
real raw spatial readings. Its command line accepts a data JSON path, nominal
time, actual-time interval, relative sensor bound and generator bound. Its
constructor checks the full certificate. The generator and clock bounds are
acquisition assumptions, not quantities learned from the observations.

## Physical reconstruction

The [spatial reproduction guide](resolution/README.md) includes the independent
full-time consumer, complete derivative calculation, 320-bit perturbed-model
raw-data replay, and separate million-state floating diagnostics. The new raw
wrapper uses nominal time for its exact quartic normalization and charges the
actual-time interval separately.

The [arithmetic reproduction guide](noise/README.md) includes all 184 weighted
approximants and 16 complete moments, using actual physical weights at 384 bits.
It also reconstructs all 8,900 complex readings and all eight actual augmented
matrices and dual normal-residual identities, verifying saved exact proposals
at 384 bits. Future capacity tables use a residual ceiling that must be
verified anew for future readings.

Five [independent review scripts](review/REVIEW.md) reconstruct central inputs
and consequences with different formulas. They include a fresh positive-series
cutoff for the infinite timing envelope and an independent implementation of
raw spatial feasibility and least squares. The pointwise spatial review
supplements the full-time certificate rather than replacing it.

The unchanged physical spatial kernel and complete arithmetic-tail/correction
premises retain their prior reconstructions. Their files are hash-bound here;
see the [preceding reconstruction guide](../refined_transfer_2026_09/README.md)
and [full arithmetic-tail package](../transfer_theorem_2026_09/noise/README.md).
The new infinite timing envelope is independently reconstructed in this phase.

## Files and evidence

| Location | Role |
|---|---|
| [framework/PROOFS.md](framework/PROOFS.md) | Transfer with uncertain acquisition, exact nuisance obstruction, finite-grid affine-clock theorem, two applications |
| [resolution/](resolution/) | Stronger seven-row bank, full-time proof, derivative/model budgets, actual perturbed fixtures |
| [noise/](noise/) | Four-degree/four-frequency comparison, complete clock/family budgets, actual data and eight verified inverses |
| [review/](review/) | Independent mathematical and computational review |
| [COMPLETION_AUDIT.md](COMPLETION_AUDIT.md) | Initial requirements mapped to completed results and limits |
| [VALIDATION.json](VALIDATION.json) | Recorded checks and hashes of the completed new package |
| [PREVIOUS_ARTIFACTS_SHA256.json](PREVIOUS_ARTIFACTS_SHA256.json) | Preservation of all six predecessor packages |

Artifact regeneration is documented separately in each component. It can
intentionally change evidence hashes; do it in a new versioned package when
developing new results. No commit, historical conversation rewrite, public
publication or apparatus-calibration claim is part of this package.
