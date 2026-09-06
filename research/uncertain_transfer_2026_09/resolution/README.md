# Reproducing the spatial uncertainty result

Use `/private/tmp/math-five-paths-venv/bin/python` with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`.
Run commands from the Math project root.

```sh
python research/uncertain_transfer_2026_09/resolution/check.py --bank 7
python research/uncertain_transfer_2026_09/resolution/timing.py
python research/uncertain_transfer_2026_09/resolution/fixtures.py --replay
python -m unittest discover -s research/uncertain_transfer_2026_09/resolution -p test_resolution.py
python research/uncertain_transfer_2026_09/resolution/forward_checks.py
```

The first command is the full independent rational polynomial-floor consumer;
it takes substantially longer than the remaining focused checks. The fixed
receipt records 861 nonempty cells and 3,743 case records.

To regenerate the proposed spatial certificate and its exact acceptance:

```sh
python research/uncertain_transfer_2026_09/resolution/produce.py --bank 7 --write
```

`discovery.py` only re-screens one previously discovered candidate using floating
arithmetic. Its scores are not certificate premises. `produce.py` chooses
rational preconditioners using numerical proposals; the independent consumer
accepts only the exact resulting inequalities.

The underlying physical kernel can be reconstructed separately using
`research/transfer_theorem_2026_09/resolution/kernel.py --precision 256`.
Its complete model error is also checked by `check.py`. No prior package needs
to be edited. The new package's `review/spatial_review.py` independently checks
outward point floors, time derivative bounds, strict profiles and raw fixture
promises at higher precision. The shared `framework/raw_clock.py` provides
operational normalization and decoding of the uncertainty fixtures.
