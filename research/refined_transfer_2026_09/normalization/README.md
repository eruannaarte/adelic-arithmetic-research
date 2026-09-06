# Raw spatial normalization: reproduction

[PROOFS.md](PROOFS.md) derives the amplitude-independent physical error charge.
[normalize.py](normalize.py) implements exact normalization and the wrapper for
all three certified banks. It imports the historical eight/nine-row decoders
without changing them. The new seven-row decoder is in the sibling directory.

From the Math project root, using the environment pinned in the preceding
research package:

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/normalization/demo.py
PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/normalization/test_normalize.py -v
```

The first command checks all 72 exact raw cases, rebuilding each bank's full
certificate once. Use `--write` to deliberately replace `evidence.json`.
The seven-row full-time consumer is a substantial exact computation; this is
not an ordinary fast smoke test. The test suite also constructs the eight-row
wrapper to exercise its public refusal and budget checks.

To decode supplied raw data, create a JSON list of seven, eight or nine exact
rational real strings in the selected bank's row order, then run:

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/normalization/normalize.py readings.json --bank 7 --time 3/2
```

The default profile is L2, the seven-row theorem's only asserted calibration.
The eight/nine-row historical H1 profiles are also available through `--profile`.
`--xi` selects a nonnegative normalization allowance at most $10^{-9}$.

The output includes exact normalized data, the quartic certificate, the actual
physical error charge, content hashes and the query decision. The mathematical
guarantee still requires the declared model, known exact time and valid sensor
error bound including acquisition digitization. No floating parsing or clock
error is implicitly certified.
