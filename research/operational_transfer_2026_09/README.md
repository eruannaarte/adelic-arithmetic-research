# Reproduction and evidence guide

Start with [REPORT.md](REPORT.md). The complete new arguments are in
[resolution/PROOFS.md](resolution/PROOFS.md) and
[noise/PROOFS.md](noise/PROOFS.md). [PROTOCOL.md](PROTOCOL.md) records the
objectives set before the work. The predecessor's general theorem is unchanged.

## Evidence levels

| Evidence | What it establishes |
|---|---|
| Spatial rational certificates and consumer | Every target and pair covers every time, with explicit model, noise and accuracy budgets |
| Complete kernel reconstruction | The rational kernel enclosures come from the defining physical generator |
| Arithmetic physical residual verifier | An actual supplied augmented solution has a bounded exact-model normal residual |
| Arithmetic tail records and inherited complete-tail proof | The omitted infinite coefficient sequence is included in the recovery guarantee |
| 320-bit replay | Both exact datasets, all four saved proposals, both residual formulas and all integer answers are reverified |
| Specific seven-row witness | Two different targets are indistinguishable with allowed physical noise for that layout |
| Floating search / finite-grid diagnostics | Candidate selection / regression controls only; neither proves continuum separation |

The current [validation record](VALIDATION.json) lists the commands actually run,
and the [preservation manifest](PREVIOUS_ARTIFACTS_SHA256.json) covers 338 files
in the four preceding research packages. No claim of an independent external
or new agent review is made; checks use exact consumers, different evaluation
algorithms, higher precision, adverse cases and explicit proofs.

## Runtime

Use Python 3.12 with [requirements.txt](requirements.txt). The installed
interpreter used for this phase was
`/private/tmp/math-five-paths-venv/bin/python`; a temporary environment may need
to be recreated later. The pinned packages record the runtime used, not a claim
about the newest public releases. For repeatable floating proposals, set
`OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1` and `PYTHONDONTWRITEBYTECODE=1`.
Commands below assume the working directory is
`/Volumes/KINGSTON/Vibecoding/Math` and `python` selects that environment.

## Verify existing evidence without rewriting it

```sh
python research/operational_transfer_2026_09/resolution/check.py --bank 9
python research/operational_transfer_2026_09/resolution/check.py --bank 8
python research/operational_transfer_2026_09/resolution/obstruction.py
python research/operational_transfer_2026_09/resolution/test_resolution.py -v
python research/transfer_theorem_2026_09/resolution/kernel.py --precision 256
python research/operational_transfer_2026_09/noise/replay.py
python research/operational_transfer_2026_09/noise/test_operational.py -v
python research/operational_transfer_2026_09/applications.py
python research/operational_transfer_2026_09/integrity.py
```

The spatial consumers recompute all exact polynomial inequalities; they are
larger than ordinary unit tests. The arithmetic replay reconstructs the full
physical experiment at 320 bits and verifies saved exact proposals without
rerunning their proposal solver. It checks a saved residual instead of trusting
it. Complete arithmetic-tail and midpoint-correction reconstructions are
unchanged dependencies, with commands and prior run records in the
[preceding guide](../transfer_theorem_2026_09/README.md). They were not silently
replaced by a finite source example.

## Reconstruct new artifacts

These commands generate fresh proposals and check them before saving:

```sh
python research/operational_transfer_2026_09/resolution/produce.py --bank 9 --write
python research/operational_transfer_2026_09/resolution/produce.py --bank 8 --write
python research/operational_transfer_2026_09/resolution/obstruction.py --write
python research/operational_transfer_2026_09/noise/demo.py --write
python research/operational_transfer_2026_09/noise/replay.py --write
python research/operational_transfer_2026_09/applications.py --write
```

The first two use floating Cholesky proposals and exact acceptance, so valid
certificate files need not be byte-identical on another floating runtime.
`demo.py` also treats binary64 solutions as proposals. Saved exact proposals
can be replayed independently of the machine that proposed them. If artifacts
are deliberately regenerated, their new hashes and validation record must be
updated; `integrity.py` should otherwise reject changed evidence.

For extra diagnostics, run `resolution/discover.py` or
`resolution/forward_checks.py`. Without `--write` they leave saved artifacts
unchanged. The latter uses the actual million-state finite graph, with a
different algorithm from the certified periodic kernel. Its output remains
floating regression evidence.

## Use the arithmetic verifier on supplied readings

The data JSON must contain `readings`: exactly 8,900 pairs of exact rational
strings `[real, imaginary]`, in increasing physical time order. For example:

```sh
python research/operational_transfer_2026_09/noise/certify.py \
  research/operational_transfer_2026_09/noise/data_large.json \
  --design multi --degree 8 --eta 1/25000 --nu 3/100000 --bits 256
```

An optional `--proposal path.json` accepts 58 exact complex pairs at degree
eight and verifies them without invoking a solver. The actual residual is
always recomputed. A failed gate returns `not_certified`, without an integer
answer. Invalid input, unresolved interval arithmetic or inadequate precision
can raise an error; this is refusal, not a negative identifiability theorem.

The model requires known $a(1)=1$, the stated coefficient envelope, exact times,
the selected physical metric and valid sensor/remainder bounds. Digitization
belongs in the sensor/data budget. The tests certify synthetic sources; they
do not measure a device or establish arithmetic realization by number fields.

The spatial decoder accepts normalized rational data and rational time; its
proof covers all real known times. Approximate normalization or time needs a
separate verified budget. See its proof for the distinction between these
interface and mathematical claims.
