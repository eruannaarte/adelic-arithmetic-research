# Refined transfer: reproduction and evidence guide

Start with [REPORT.md](REPORT.md). The initial [PROTOCOL.md](PROTOCOL.md) fixes
the seven-row requirement before discovery and records the three objectives.
The [completion audit](COMPLETION_AUDIT.md) maps their acceptance conditions.

| Component | Main proof | Executable verification |
|---|---|---|
| Seven-row sensing | [resolution/PROOFS.md](resolution/PROOFS.md) | Full-time rational consumer, case-coverage tests and physical ambiguity witness |
| Raw normalization | [normalization/PROOFS.md](normalization/PROOFS.md) | Exact quartic/data-scaling receipts, 72 raw cases and public-interface tests |
| Weighted drift | [noise/PROOFS.md](noise/PROOFS.md) | Actual W-norm bounds, complete family remainder, numerical solve residual and integer gates |
| Shared theorem | [framework/README.md](framework/README.md) | Unchanged general transfer predicates applied to all new consequences |
| Independent review | [review/REVIEW.md](review/REVIEW.md) | Different evaluation methods and adverse controls, including all raw fixtures |

The [validation record](VALIDATION.json) binds the delivered artifacts and lists
what actually ran. [PREVIOUS_ARTIFACTS_SHA256.json](PREVIOUS_ARTIFACTS_SHA256.json)
covers all 388 prior files. [integrity.py](integrity.py) checks their preservation,
new evidence hashes, basic artifact consistency, Python syntax and local links.

## Runtime and principal verification commands

The tested interpreter was `/private/tmp/math-five-paths-venv/bin/python`,
Python 3.12 with the packages in [requirements.txt](requirements.txt). That
temporary environment may later need recreation. The pins describe the
installed runtime used, not the newest public releases. Set
`OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1` and `PYTHONDONTWRITEBYTECODE=1` for
repeatable floating proposals. Commands below run from
`/Volumes/KINGSTON/Vibecoding/Math`, with `python` selecting that environment.

```sh
python research/refined_transfer_2026_09/resolution/check.py --bank 7
python research/refined_transfer_2026_09/resolution/test_resolution.py -v
python research/refined_transfer_2026_09/resolution/obstruction.py
python research/transfer_theorem_2026_09/resolution/kernel.py --precision 256
python research/refined_transfer_2026_09/normalization/demo.py
python research/refined_transfer_2026_09/normalization/test_normalize.py -v
python research/refined_transfer_2026_09/framework/applications.py
python research/refined_transfer_2026_09/integrity.py
```

The seven-row full-time consumer is a substantial exact calculation. Several
commands validate it as a prerequisite; it is not necessary to rerun all of
them after every documentation edit. See the model guides for fine-grained
reconstruction and mutation commands:
[spatial](resolution/README.md), [normalization](normalization/README.md), and
[weighted arithmetic](noise/README.md). The arithmetic guide includes
192/256/320-bit approximation replay and 320-bit actual-data replay.

All five independent review scripts are documented in [review/REVIEW.md](review/REVIEW.md).
The weighted reviewer uses moment quadratic forms instead of full-vector
residual evaluation. The spatial point reviewer uses outward LDL bounds and
direct polynomial powers. The normalization reviewer includes exact endpoint
counterexamples, source scaling and corruption checks. These are separate
agent reviews and computational checks, not external peer review or a
proof-assistant formalization.

## What is inherited and what is new

The new seven-row floors and their complete time cover are new proof evidence.
The physical kernel is unchanged and fully reconstructed again at 256 bits.
Its complete periodic-image, finite-boundary, time-series and coefficient
rounding bounds are retained explicitly.

The arithmetic experiment retains its known $a(1)=1$, integer envelope,
measurement times, physical weights, complete tail channels and digital
midpoint correction. Their expensive complete-tail reconstruction remains
documented in the [preceding theorem guide](../transfer_theorem_2026_09/README.md).
This phase does not replace that infinite source class by its finite synthetic
example. It adds a fully verified weighted drift-family remainder and replays
the actual data and solve proposals.

Raw normalization is now evaluated with exact rational arithmetic, including
the error's physical scale. Exact raw input and known rational time remain
requirements; acquisition uncertainty belongs in the sensor budget. The 72
raw fixtures are constructed with a proved bound against the actual finite
model, then independently reconstructed. They are not measured apparatus data.

Floating discovery and finite-grid diagnostics are useful controls, but they
are not substitutes for the interval covers or outward arithmetic proofs.
The seven-row count is sufficient, not minimum; the drift-family bound is
sufficient, not an optimal approximation or physical calibration claim.

## Rebuilding versus checking

Ordinary verification commands are read-only. `--write` options deliberately
replace the new package's own output files. Floating proposals may differ
across environments; all accepted proposals still need exact or outward
verification. Rebuilding artifacts requires updating validation hashes.
Preserve the preceding research packages and their records.
