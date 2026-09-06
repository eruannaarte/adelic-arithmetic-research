# Reproduce the combined six-channel certificate

Run from the repository root with Python 3.12 and `python-flint`, NumPy and
SciPy installed. The recorded environment used Python 3.12.14, python-flint
0.9.0, NumPy 2.5.2 and SciPy 1.18.1. The physical and interval proofs use Arb
and FLINT; NumPy's floating SVD only proposes rational pair split weights.

```sh
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
python research/combined_transfer_2026_09/spatial/check.py
python -m unittest discover -s research/combined_transfer_2026_09/spatial -p test_spatial.py
```

The main consumer independently recomputes all 2,688 direction-cell bounds
and all 1,280 exact-polynomial single-target/pair records. Its 320-bit run took
about 28 seconds in the recorded environment; the 13-test suite took about
29 seconds. Runtime depends on hardware and other simultaneous work.

To replay the actual-model route, without writing any predecessor file:

```sh
python research/transfer_theorem_2026_09/resolution/kernel.py --precision 320
python research/structured_transfer_2026_09/resolution/kernel_derivative.py --bits 384
python research/combined_transfer_2026_09/spatial/fixtures.py --replay --bits 320
python research/combined_transfer_2026_09/spatial/decoder.py
```

The first two commands reconstruct the entire finite-x value and derivative
coefficient enclosures. The fixture command reconstructs all 24 actual-time,
actual-potential raw packets, including complete periodic-image and finite
boundary charges. The decoder verifies every raw normalization receipt before
recovering the target and source. A 256-bit fixture generation took about
52 seconds. These replays are distinct from verifying saved matrices alone.

To rebuild the new certificate proposals and outputs:

```sh
python research/combined_transfer_2026_09/spatial/directions.py --write
python research/combined_transfer_2026_09/spatial/polynomial_producer.py
python research/combined_transfer_2026_09/spatial/check.py --write
python research/combined_transfer_2026_09/spatial/fixtures.py --write
python research/combined_transfer_2026_09/spatial/fixtures.py --replay --write
python research/combined_transfer_2026_09/spatial/decoder.py --write
```

Only this new `spatial` directory is written by those commands. Polynomial
proposal construction took about 23 seconds. A different run may produce
different runtime fields while preserving the exact scientific data.

The public Python entry point is `decoder.StructuredBank`. Its `decode`
method takes six exact rational raw readings, an exact nominal time, a
declared actual-time interval, and a declared potential interval. It rejects
intervals exceeding the fixed `1e-8` clock/potential radii. A scalar, list or
interval supplied by the user is a premise, not a calibration established by
the decoder. Data digitization must be included in the sensor error budget.

All required prior artifacts are linked through repository-relative paths.
The complete argument is in [PROOFS.md](PROOFS.md); [REPORT.md](REPORT.md)
explains the result and limitations. `VALIDATION.json` records artifact hashes
and successful checks. Its recorded snapshot is expected to change when
regeneration overwrites runtime-bearing outputs.
