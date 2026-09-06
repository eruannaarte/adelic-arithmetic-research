# Reproduction

Use `/private/tmp/math-five-paths-venv/bin/python` from the project root with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`.
The environment uses Python 3.12.14, python-flint 0.9.0 and NumPy 2.5.2.

Fast outward reconstruction of every new complete clock premise:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/arithmetic/check_clock.py
```

Independent exact complete recovery consequences and adverse checks:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/arithmetic/consequences.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/structured_transfer_2026_09/arithmetic -p test_clock.py -v
```

Actual 8,900-reading and nominal forward-model reconstruction at higher
precision, with both residual forms and the saved exact returned proposals:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/arithmetic/demonstrate.py --bits 384
```

This last command refreshes `precision_replay.json`, including new timings;
the saved readings and proposals are only read and compared. It does not
modify historical packages. The original degree/cost study is in
`demonstration.json`, with all 8 degree/window comparisons. Repeating it
with `--benchmark --bits 384` adds freshly measured degree comparisons to
the replay record without replacing the original benchmark.

`clock_bound.py` reconstructs the new certificate. Its optional `--write`
replaces `clock_bound.json`; the default only prints a proposal. The
independent consumer imports no producer code, saved weights or phase
vectors. The prior exact weighted polynomial approximants are reused from
`research/uncertain_transfer_2026_09/noise/approximation.json`, whose hash
is bound by the new clock artifact and the old complete-vector audit.

`demonstrate.py --write --benchmark` is the full production command: it
rebuilds the 8 baseline matrices, makes new degree-12 proposals for the
60-fold clock example, and replaces this directory's generated data/results.
No such producer mutation is needed for normal verification. Whenever a
generated artifact is deliberately replaced, rerun its consumer and refresh
the current package's integrity manifest.

The complete infinite arithmetic-tail and digital-correction reconstructions
are unchanged and retain the reproduction routes documented in the
operational and uncertain-transfer packages. The new complete timing bound
has its own elementary positive-sum tail reconstruction and independent
zeta-series check. The finite synthetic source is used only for actual-data
validation, never as the uniform clock or arithmetic-tail premise.
