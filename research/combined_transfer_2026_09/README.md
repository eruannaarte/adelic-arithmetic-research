# Reproduce the combined transfer results

Start with [REPORT.md](REPORT.md), the predeclared [PROTOCOL.md](PROTOCOL.md),
and the self-contained [joint-budget corollary](framework/PROOFS.md). Detailed
models and commands are in the [spatial](spatial/README.md),
[complete clock-block](blocks/README.md), and
[degree-eleven](degree11/README.md) guides.

Run commands below from the repository root. Use Python 3.12; the exercised
environment was Python 3.12.14 with python-flint 0.9.0, NumPy 2.5.2, SciPy
1.18.1, mpmath 1.4.1 and gmpy2 2.3.1. Arb and FLINT are supplied by
python-flint. A portable local environment can be created with:

```sh
python3.12 -m venv .venv-transfer
. .venv-transfer/bin/activate
python -m pip install -r research/five_paths_2026_09/requirements.txt
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
```

These shell examples use POSIX syntax; on Windows use the corresponding
virtual-environment activation and environment-variable commands. Numerical
code does not depend on a particular user's filesystem path.

## Fast complete consequence checks

```sh
python research/combined_transfer_2026_09/spatial/check.py
python research/combined_transfer_2026_09/blocks/check_orbit.py
python research/combined_transfer_2026_09/blocks/consequences.py
python research/combined_transfer_2026_09/degree11/check.py
python research/combined_transfer_2026_09/degree11/consequences.py
python research/combined_transfer_2026_09/degree11/orbit_comparison.py
```

The spatial command independently checks all 2,688 direction cells and
1,280 exact-polynomial single-target/pair records. The block consumer
rebuilds all 248 actual phase/corner sums and complete series bounds. Its
consequence checker verifies the joint budgets, strict integer boundaries,
returned answer disks and compact publication components. The degree-eleven
consumers recompute its own Schur/complete-tail consequences, odd-degree
approximation budget and orbit-clock comparison.

Expected outcomes: the fixed six-row joint contract passes; both h=120
degree-twelve arithmetic profiles pass; degree eleven is uncertified at
amplitude 4000 and certified at amplitude 500. An uncertified profile is an
expected scientific result, not a failed test run.

Run the 32 positive and adverse tests:

```sh
python -m unittest discover -s research/combined_transfer_2026_09/spatial -p test_spatial.py
python research/combined_transfer_2026_09/blocks/test_orbit.py
python research/combined_transfer_2026_09/degree11/test_degree11.py
```

Recorded spatial consumers and tests took roughly half a minute each; the
arithmetic phase and scalar consequence checks took seconds. These are local
wall-clock observations and not promises about other machines.

## Fresh model and computed-data reconstruction

The following spatial commands rebuild the defining finite-x kernels and
their derivative, reconstruct true-clock/true-potential raw observations,
then verify the normalization and exact decoder:

```sh
python research/transfer_theorem_2026_09/resolution/kernel.py --precision 320
python research/structured_transfer_2026_09/resolution/kernel_derivative.py --bits 384
python research/combined_transfer_2026_09/spatial/fixtures.py --replay --bits 320
python research/combined_transfer_2026_09/spatial/decoder.py
```

These commands preserve the saved kernel, fixture and answer artifacts. The
new spatial consumers separately charge every periodic image, finite-boundary
walk tail, time-series remainder and mixed clock/potential term.

For arithmetic, reconstruct the actual degree-eleven forward matrix and all
new complete channels, then reconstruct its raw data and four inverses:

```sh
python research/combined_transfer_2026_09/degree11/verify_model.py --bits 384
python research/combined_transfer_2026_09/degree11/demonstrate.py --bits 384
```

This includes both actual 8,900-row weight designs, their eleven-column
physical polynomial bases, 22 complete nuisance-tail channels, 1,100 cross
entries, 42 approximation norms and four complete Taylor remainder norms.
The raw data contain actual degree-eleven nuisance of scale `1e20`; both
normal-space and reading-space residual identities are recomputed.

The independent block review is a nonmutating route through the h=120 model:

```sh
python research/combined_transfer_2026_09/review/block_review.py
```

It performs a 448-bit actual-phase replay, checks the omitted valuation tails
against exact full generating-function totals, regenerates all 8,900 actual
h=120 readings at 384 bits, reconstructs both physical augmented inverses,
rechecks both residual identities, and independently verifies the integer
and presentation budgets. It changes no block or predecessor file.

The block author's additional reconstruction command is:

```sh
python research/combined_transfer_2026_09/blocks/demonstrate.py --bits 384
```

This verifies the saved raw readings and proposals and writes a fresh
`blocks/precision_replay.json` summary, including runtime fields. Use a
working copy when preserving the publication snapshot byte-for-byte.

## Independent reviews and inherited complete tails

Read the [spatial review](review/SPATIAL_REVIEW.md),
[block review](review/BLOCK_REVIEW.md), and
[degree-eleven review](review/DEGREE11_REVIEW.md) for the independently checked
claims and limits. These are internal independent proof/computation reviews;
they are not external peer review. Their scripts and JSON results are linked
from the respective documents.

The original arithmetic finite/remote tail enumeration remains an inherited
premise. It is not replaced by the finite synthetic fixture or by a saved
matrix. Its full reconstruction route is described in the
[complete-tail guide](../transfer_theorem_2026_09/noise/README.md),
[preceding polynomial guide](../unified_query_2026_09/noise/README.md), and
[earlier tail guide](../next15_2026_09/noise/README.md). Portable commands for
two important nonmutating deeper replays are:

```sh
python research/transfer_theorem_2026_09/noise/oscillatory_channels.py --extended --precision 256
python verify_multiscale_certificate.py --certificate certificates/arithmetic_sensing_v_multiscale_end_to_end.json --processes 4
```

The first rebuilds the full extended physical channels and complete midpoint
correction. The second reconstructs the complete original multiscale
certificate, including the large arithmetic enumeration and remote tail.
The predecessor guide also identifies the separate single-window rebuild;
that historical script refreshes an old reconstruction record, so execute it
in a disposable copy when preserving the archive. Historical deep replays
took several minutes. They are not counted as new reconstructions merely
because their hashes are checked in this round.

## Evidence identity and deliberate regeneration

`PREVIOUS_ARTIFACTS_SHA256.json` identifies the 660 preserved predecessor
files. Package validation manifests and review records bind the exact new
artifacts they checked. Hash equality proves identity with those recorded
files; it does not establish the truth of their mathematical or numerical
premises. That requires the proofs and appropriate model replays above.

Producer `--write`, `--record` or `--record-replay` options deliberately
regenerate evidence or replay summaries. They can alter runtime-bearing
hashes even when all scientific enclosures remain valid. The three local
guides document which commands write files. Avoid treating a changed hash
as either automatic mathematical failure or automatic permission to discard
the model reconstruction.

All mathematical guarantees are conditional on their stated acquisition and
source classes. The spatial and arithmetic error units differ. Shared
uncertainties remain shared within a measurement explanation, physical
family membership is a declared premise, and each newly computed inverse
needs its own verified residual before its query guarantee is used.

## Public reference archive

The public source omits three third-party Borsuk reference scans, retaining
their original hashes and publisher citation. All authored proofs, code and
numerical evidence remain present. The local 660-file archive is unchanged.
See [PUBLIC_ARCHIVE_NOTE.md](PUBLIC_ARCHIVE_NOTE.md). The new integrity checker
accepts only these exact documented omissions.
