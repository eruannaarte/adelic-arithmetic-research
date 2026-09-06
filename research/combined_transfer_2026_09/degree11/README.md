# Reproduce the degree-eleven construction

Read [REPORT.md](REPORT.md) for the result and [PROOFS.md](PROOFS.md) for the
exact mathematical argument. Run commands from the repository root. The
recorded environment used Python 3.12.14, python-flint 0.9.0 and NumPy 2.5.2;
these were already available in the scientific virtual environment. Arb and
FLINT are supplied through python-flint. The reconstruction and tests need
those libraries; the rational consumer uses Python's standard library.

Fast consequence checks (read-only):

```sh
python research/combined_transfer_2026_09/degree11/check.py
python research/combined_transfer_2026_09/degree11/consequences.py
python research/combined_transfer_2026_09/degree11/orbit_comparison.py
```

Fresh physical model and complete new-channel reconstruction:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/combined_transfer_2026_09/degree11/verify_model.py --bits 384
```

This rebuilds both exact physical windows, all 8,900 sampling rows, the true
degree-eleven orthonormal basis and Gram, all 22 complete nuisance channels,
1,100 cross entries, 42 weighted approximation norms and four complete
remainder norms. The inherited original arithmetic-tail enumeration and the
full digital midpoint have the unchanged reconstruction route documented in
[the prior complete-tail guide](../../transfer_theorem_2026_09/noise/README.md).

Reconstruct both raw data sets and verify all four saved computed solutions:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/combined_transfer_2026_09/degree11/demonstrate.py --bits 384
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/combined_transfer_2026_09/degree11/test_degree11.py
```

The replay compares exact rational readings and checks that fresh residual
bounds lie within the saved 320-bit upper bounds. The nine controls include
changed complete-bias rejection, missing Taylor-channel rejection, forbidden
degree-twelve leakage, odd-degree parity, fixed and smaller-amplitude gates,
and an actual inaccurate proposal rejected by a fresh physical residual.
The synthetic data contain genuine degree-eleven polynomial terms, not just
a lower-degree example fitted using an eleven-degree decoder.

The above commands do not change recorded evidence. `construct.py --write`
deliberately regenerates evidence from the hash-bound complete channels;
`demonstrate.py --write --bits 320` deliberately regenerates both data sets
and proposals. The optional `--record` model flag and `--record-replay`
demonstration flag save new timing/replay records and therefore change
artifact hashes. They are unnecessary for verification.

`orbit_comparison.json` applies the separate complete orbit clock to exactly
the same physical residuals and degree-eleven inverse. Reproduce that clock
premise using [the orbit guide](../blocks/README.md). Its proof is independent
of the polynomial degree. No file in an earlier research package is edited.
