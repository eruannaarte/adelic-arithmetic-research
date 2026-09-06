# Path 5: finite-resolution transfer and spectral stability

**New supported extension:** fixed n=1001, first two cosine ports, affine interaction g=4/5, exact central target, and the full noncommuting Neumann model are certified throughout **1≤tau≤2**, replacing the previous 1≤tau≤6/5 interval. No source bandwidth, target position, output metric, or resolution changed.

- `CHAPTER.md`: concise result for the main five-path presentation.
- `APPENDIX.md`: definitions, complete new remainder proof, coefficient-model connection, fresh continuum-floor derivation, counterexamples, and primary sources.
- `certificate.json`: canonical continuous-cover certificate, including both cells and all coefficient intervals.
- `baseline.json`: fresh 256-bit common-core quadrature plus rational principal-minor witnesses for inherited continuum floors.
- `check_certificate.py`: independent Python-standard-library reconstruction of interval polynomial, remainder, spectral, cover and floor consequences.
- `generate_certificate.py`: model-to-Arb coefficient generation and assembly.
- `revalidate_baseline.py`: rebuild the inherited floor premise from the defining integral.
- `test_resolution.py`: 16 tests, including a separate dense Arb matrix-exponential implementation on a small grid.
- `refinement_cell_1_1p5.json`, `validate_refinement.py`, `refinement_validation.json`: higher-precision/order/degree consistency control.
- `CLAIM_INDEX.md`: claim-to-evidence mapping and before/after.

## Quick independent check

From the repository root, with any Python≥3.9:

```sh
python3 research/five_paths_2026_09/path5_resolution/check_certificate.py
```

Expected: `PASS`, followed by three positive finite floors (nearest-decimal displays):

- L2 ≈ 1.1764481493014326e-7;
- declared H1 ≈ 1.2928209881039934e-9;
- natural discrete H1 ≈ 1.3728294273539934e-9.

This checker does not require NumPy, SciPy, or Arb. It proves consequences of the supplied outward coefficient/metric intervals. It does not authenticate those numerical premises: regenerate them for the complete model-to-certificate proof chain. A hash establishes identity, not mathematical correctness.

## Reproduce the numerical proof

Use Python 3.12 and the versions in `requirements.txt`. The session's prepared environment was `/private/tmp/math-five-paths-venv/bin/python`; a fresh machine may install the requirements in its own virtual environment. Commands below use `python` for that prepared interpreter and assume the repository root as working directory.

```sh
python research/five_paths_2026_09/path5_resolution/revalidate_baseline.py
python research/five_paths_2026_09/path5_resolution/generate_certificate.py --interval 1 3/2 --output research/five_paths_2026_09/path5_resolution/cell_1_1p5.json
python research/five_paths_2026_09/path5_resolution/generate_certificate.py --interval 3/2 2 --output research/five_paths_2026_09/path5_resolution/cell_1p5_2.json
python research/five_paths_2026_09/path5_resolution/generate_certificate.py --assemble research/five_paths_2026_09/path5_resolution/cell_1_1p5.json research/five_paths_2026_09/path5_resolution/cell_1p5_2.json --output research/five_paths_2026_09/path5_resolution/certificate.json
python -m unittest discover -s research/five_paths_2026_09/path5_resolution -p test_resolution.py -v
```

The two full n=1001 runs are the expensive checks: each visits all 500 retained modes with n-vector tridiagonal actions, then validates 57 continuum coefficient integrals. Session runs used 192 bits, exponential degree64, time Taylor order18, and took about one minute per cell. Time and widths may vary by environment; exact serialized inequality acceptance is authoritative. Baseline quadrature and 16 focused tests are much cheaper. The code imports existing audited coefficient helpers from the repository root. Their SHA256 identities are recorded in the artifact; revalidation is required if these sources change.

Optional refinement control (more expensive than one standard cell):

```sh
python research/five_paths_2026_09/path5_resolution/generate_certificate.py --interval 1 3/2 --precision 256 --order 20 --degree 72 --output research/five_paths_2026_09/path5_resolution/refinement_cell_1_1p5.json
python research/five_paths_2026_09/path5_resolution/validate_refinement.py
```

Expected: all 171 shared coefficient intervals overlap and all three spectral upper bounds improve. This repeats the coefficient algorithm at a different precision, order and exponential degree; it is not a different implementation of Arb. The separate n=7 dense-matrix exponential control is the differential implementation check.

## Numerical settings and trusted components

Fresh session: Python 3.12.14, python-flint 0.9.0 with FLINT 3.6.0, NumPy 2.5.2, SciPy 1.18.1, mpmath 1.4.1, gmpy2 2.3.1. Only Arb and exact rational arithmetic decide these new proof inequalities. Numerical imports used by the pre-existing source modules do not become independent scientific premises.

Coefficient integration uses the existing `acb.integral` callback with relative tolerance 2^(-(precision−40)), absolute tolerance 2^(-(precision−16)), evaluation limit 40,000 and depth limit 32. These settings request accuracy; the actual outward balls decide the result. Nonfinite coefficient balls are rejected. Every floating decimal in the JSON or console is descriptive. The original finite-exponential remainder and the new time remainder are both retained, as separate error contributions.

There is no physical validation here: Euclidean modal energy is the declared output norm. No claim of local hardware sensing, actual noise covariance, optimal n, target-placement robustness, K>2, or all-time finite resolution is made.
