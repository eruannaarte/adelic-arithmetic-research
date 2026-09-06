# Reproducing the arithmetic extension

Run from the Math project root. The existing scientific environment is
`/private/tmp/math-five-paths-venv/bin/python`; it supplies python-flint,
NumPy and SciPy. Set `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1` and
`PYTHONDONTWRITEBYTECODE=1` to avoid uncontrolled parallelism and historical
bytecode changes. Commands below use `$PY` as that interpreter.

```sh
export PY=/private/tmp/math-five-paths-venv/bin/python
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
```

The quick exact consequence and behavior checks are:

```sh
$PY research/uncertain_transfer_2026_09/noise/consequences.py
$PY -m unittest discover -s research/uncertain_transfer_2026_09/noise -p test_uncertainty.py -v
```

The first command binds saved data and proposals, verifies the inherited
complete-tail consequence certificate, and recomputes every budget. Its
saved residual inputs were produced by the physical reconstruction below;
the quick command does not independently remeasure those residuals.

Reconstruct all physical weighted residual norms independently of the
producer's moment/projection calculation:

```sh
$PY research/uncertain_transfer_2026_09/noise/check_approximation.py --bits 384
```

Reconstruct the actual clocked and mismatched data, all eight nominal
arithmetic/polynomial matrices and both identities of each saved exact
proposal's normal residual:

```sh
$PY research/uncertain_transfer_2026_09/noise/demonstrate.py --bits 384
```

This verifies the same 8,900 rational readings and replays all proposals.
It writes `precision_replay.json` as the replay receipt; it does not
overwrite the original data or result certificates. The stored 384-bit
run succeeded. Exact numerical residual endpoints may differ when run
with a different precision, while the claims must still pass.

For deliberate artifact regeneration, rather than checking saved artifacts:

```sh
$PY research/uncertain_transfer_2026_09/noise/approximation.py --bits 320 --write
$PY research/uncertain_transfer_2026_09/noise/check_approximation.py --bits 384 --write
$PY research/uncertain_transfer_2026_09/noise/demonstrate.py --bits 320 --write
$PY research/uncertain_transfer_2026_09/noise/consequences.py --write
```

`approximation.json` holds fixed rational polynomials and their complete
weighted norms. `data.json` contains the actual rational observations and
source metadata used only for demonstration. `result_DESIGN_DEGREE.json`
contains the independently residual-checked proposal and physical budget.
`consequences.json` separates actual fixture budgets from future family
capacity tables, which require a newly verified residual ceiling 1e-30.

The inherited degree-specific complete arithmetic tails, correction, and
physical polynomial premises are bound to the preceding packages. Their
expensive full-tail replays were completed and documented there; this phase
preserves their artifacts rather than silently replacing complete tails
with finite test data. The new complete timing bound is reconstructed here
from finite sums plus explicit infinite integral tails. The independent
audit additionally checks it at a different cutoff.
