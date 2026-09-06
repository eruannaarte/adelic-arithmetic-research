# Reproducing weighted drift recovery

Run from `/Volumes/KINGSTON/Vibecoding/Math` with the established Python runtime.
No command below rewrites a completed research package. Default invocations
also leave this package's evidence unchanged.

The short independent approximation and consequence checks are:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/noise/check_approximation.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/noise/consequences.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/refined_transfer_2026_09/noise -p 'test_*.py' -v
```

Reconstruct all approximation proposals at two precisions and recheck every
physical residual:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/noise/precision_replay.py
```

Reconstruct the actual source, slow drift, sensor perturbation and digitized
readings; rerun the augmented inverse; then independently verify both saved
exact proposals against all readings at 320 bits:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/noise/demonstrate.py --bits 320
```

The separate review agent's independent moment-based norm proof is:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/review/weighted_moment_review.py
```

`approximation.py --write`, `check_approximation.py --write`,
`demonstrate.py --write`, `consequences.py --write` and
`precision_replay.py --write` are the explicit generation commands for this
package's saved evidence. The generator proposes fixed rational polynomials;
the consumer verifies their physical weighted errors without invoking that
proposal code. The moment review uses a third evaluation formula.

Files and their logical roles:

- `PROOFS.md`: uniform phase/frequency theorem and complete inverse-error gate.
- `approximation.json`: 24 fixed rational approximants and physical norm bounds.
- `checked_approximation.json`: independently verified norm and amplitude bounds.
- `data.json`: all 8,900 exact complex readings and independently constructed
  synthetic truth; truth is withheld from the inverse.
- `result_multi.json`, `result_outer.json`: exact augmented proposals, actual
  residual certificates, recovered answers and failed adverse controls.
- `consequences.json`: all 98 exact integer gates and error bounds.
- `precision_replay.json`, `replay_320.log`, `tests.log`: reconstruction and test
  evidence. The replay log includes the check of saved exact proposals.

The unchanged operational verifier rebuilds the complete augmented physical
matrix, validates its Gram floor and basis correspondence, and evaluates the
normal residual from the actual data. It consumes the previous complete
arithmetic-tail bounds. For the separate expensive reconstruction of those
inherited tail premises, use the reproduction commands in
`research/transfer_theorem_2026_09/README.md`; a new drift bound does not replace
that inherited theorem.

A successful computation is conditional on the physical model. The normal
residual certifies the solve; it cannot supply an empirical drift or sensor
bound. The family theorem supplies the remainder radius only after its
amplitude/frequency assumptions have been justified.
