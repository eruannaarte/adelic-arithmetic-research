# Complete 32-term multiplicative clock blocks

Read [REPORT.md](REPORT.md) for the result and [PROOFS.md](PROOFS.md) for the
complete theorem. This directory preserves all predecessor artifacts. Run
commands from the repository root with the scientific Python environment
specified by the parent reproduction guide. The exercised versions were
Python 3.12.14 and python-flint 0.9.0; actual-model reconstruction additionally
uses the repository's NumPy, SciPy and mpmath dependencies.

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python research/combined_transfer_2026_09/blocks/check_orbit.py
python research/combined_transfer_2026_09/blocks/consequences.py
python research/combined_transfer_2026_09/blocks/test_orbit.py
```

These checks reconstruct all actual phase sums, consume inherited complete
arithmetic-tail certificates, replay the exact full recovery budgets and
integer threshold boundaries, check answer disks and bindings to saved
384-bit physical replays, and replay the compact publication budget. They
finish in seconds in the recorded environment.

For a fresh high-precision reconstruction of the defining physical model,
including the actual uncertain-clock data and both saved numerical inverses:

```sh
python research/combined_transfer_2026_09/blocks/demonstrate.py --bits 384
```

This reconstructs the two actual 8,900-by-62 forward matrices, physical
polynomial basis and Gram terms, the same rational synthetic readings, and
the two independent normal residual identities. It verifies the saved
proposals; it does not trust a saved Gram matrix. It writes a replay summary
and leaves the original readings and proposed inverses unchanged.

The deterministic producer is available separately:

```sh
python research/combined_transfer_2026_09/blocks/orbit_bound.py --bits 256
```

Use `--write` only in a working copy when deliberately regenerating artifacts.
Running `demonstrate.py --write` generates new saved data and proposals;
`consequences.py --write` regenerates exact consequence and presentation
artifacts. The SHA256 seal identifies this publication's fixed files, so a
fresh replay log is expected to have different timing fields. Full historical
arithmetic-tail reconstruction is described in the inherited transfer and
uncertain-transfer reproduction guides; the present result does not replace
those prerequisites with a finite source cutoff.

Files:

- `orbit_bound.py/json`: outward producer, all 248 corner/lag correlations,
  complete positive-series masses, exact valuation tails and clock formula.
- `check_orbit.py`, `checked_orbit.json`: independent actual-grid and
  zeta-series replay at 384 bits.
- `demonstrate.py`, `data_h120.json`, `result_*_h120.json`: defining-model
  reconstruction and two actual degree-12 inverse certificates.
- `precision_replay.json`: 384-bit replay of readings and saved proposals.
- `consequences.py/json`: exact fixed-budget, integer-boundary and returned
  query checks, plus generation/checking of `publication_budget.json`.
- `test_orbit.py`: ten positive and adverse certificate tests.
- `VALIDATION.json`: SHA256 manifest and completion record.

The theorem assumes the declared source, clock, mismatch and drift families.
Synthetic examples and a small solve residual do not supply empirical
calibration for those assumptions. The normal-residual premise used by the
future budget must still be verified for each newly acquired data set.
