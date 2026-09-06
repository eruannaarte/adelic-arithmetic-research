# Reproduce the structured-potential result

From the project root, use the scientific runtime recorded below; set
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`.
The commands below only read existing artifacts unless `--write` is given.

```sh
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/resolution/check.py
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/resolution/decoder.py
/private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/structured_transfer_2026_09/resolution -p 'test_resolution.py'
```

`check.py` independently rebuilds all 2,688 whole-time direction cases and
checks complete analytic remainders and exact recovery gates. `decoder.py`
first rechecks all 3,743 nominal source/pair records from the previous package,
then the new direction cases, then decodes the twelve raw observations with
verified normalization. Tests include altered contracts, missing time
coverage, changed kernel binding, false smaller direction bounds, excessive
uncertainty, invalid exact inputs, and zero observations.

Rebuild the derivative from the actual finite-x modal generators:

```sh
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/resolution/kernel_derivative.py --bits 384
```

Reconstruct the twelve physical observations at the true perturbed potential
and clock, using direct exponentials and complete finite-boundary/image tails:

```sh
/private/tmp/math-five-paths-venv/bin/python research/structured_transfer_2026_09/resolution/fixtures.py --replay --bits 320
```

The derivative replay checks equality of every outward exported interval;
the physical-data replay checks equality of every raw rational reading and
reproves each saved sensor promise. Neither replay merely reloads the nominal
matrix or checks a solver residual. The fixed original nominal kernel can
also be reconstructed, without modifying its historical package:

```sh
/private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/resolution/kernel.py --precision 256
```

`directions.py --write` regenerates the discovery-independent producer's
whole-time bounds. `kernel_derivative.py --write`, `fixtures.py --write`,
`check.py --write` and `decoder.py --write` regenerate their respective new
artifacts. No command writes to any completed research package.

The runtime was Python 3.12.14 with python-flint 0.9.0 on this local machine.
The recorded producer took about 0.74 seconds for direction cells; independent
centered checking took about 9.21 seconds. Four direct physical response
reconstructions, reused for three sources each, took 26.47 seconds at 256 bits
and 27.48 seconds for the 320-bit replay. These are measured local runtimes,
not universal complexity claims. The previous nominal floor check dominates
raw-decoder initialization; its premise is validated once per bank instance.

`kernel_derivative.json` and the prior nominal kernel are interval premises
until reconstructed by their corresponding scripts. The complete proofs
explain the connection from these finite calculations to the full model.
Recorded SHA256 identities bind premises but do not prove them.
