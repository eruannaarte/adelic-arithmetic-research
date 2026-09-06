# Reproduce the six-row result

Use `/private/tmp/math-five-paths-venv/bin/python` with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`.
The environment has Python 3.12.14, python-flint 0.9.0, NumPy 2.5.2 and SciPy
1.18.1. Rational polynomial arithmetic uses FLINT; no floating computation is
accepted as a proof.

From the Math workspace:

```sh
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/six_rows/certify.py
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/six_rows/obstruction_check.py
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/six_rows/comparison.py
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/six_rows/fixtures.py --replay
/private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/structured_transfer_2026_09/six_rows -p 'test_six.py'
```

The first command independently reconstructs every polynomial Gram inequality
and checks all 1,278 complete-time records. The second proves physical noise
ball intersections for every one-row deletion of the prior seven-row bank.
The third disproves only the older uniform sufficient gate on the successful
new bank. The fourth reconstructs all 60 raw synthetic datasets at 320 bits.
The tests include altered budgets, invalid weights, false minor bounds,
incomplete time covers, inexact time input, excessive normalization charge,
changed raw digits, and a dataset outside the model promises.

The preserved actual-model kernel can be replayed without changing history:

```sh
/private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/resolution/kernel.py --precision 256
```

This re-establishes the exported finite-x coefficient enclosures. The current
consumer additionally checks all periodic, Taylor and finite-boundary transfer
remainders. Do not substitute the saved Gram polynomial for this physical
premise.

To reconstruct the new proposals and data, adding `--write` only where shown:

```sh
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/six_rows/polynomial_producer.py
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/six_rows/certify.py --write
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/six_rows/obstruction_producer.py
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/six_rows/comparison.py --write
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/six_rows/fixtures.py --write
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/six_rows/fixtures.py --decode --write
```

Only files within this new `six_rows` directory are written. The raw decoder
accepts a JSON list of six exact rational real readings in bank order:

```sh
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/six_rows/raw.py readings.json --time 3/2
```

Its output includes the normalization receipt and a unique target/source
answer when compatible with the promised noise model. Accuracy is omitted for
an incompatible observation. Exact-input digitization error must already be
included in the sensor radius. Neither timing error nor potential uncertainty
is covered by this specific six-row profile.

A separate review of the seven-row potential/clock extension is recorded in
[REVIEW_POTENTIAL.md](REVIEW_POTENTIAL.md). Re-run its exact algebra and fresh
384-bit complete-time consumer audit, without changing stored files:

```sh
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/six_rows/review_potential.py
```
