# Reproduce the Transfer Theorem release

The release tag is `transfer-theorem-v1-2026-09-05`. Use its complete source
archive or a checkout of that tag, not a single research subdirectory: the new
proofs inherit complete kernel, arithmetic-tail and approximation premises from
eight preserved predecessor packages.

```sh
git clone https://github.com/eruannaarte/adelic-arithmetic-research.git
cd adelic-arithmetic-research
git checkout transfer-theorem-v1-2026-09-05
python3.12 -m venv .venv-transfer
. .venv-transfer/bin/activate
python -m pip install -r research/structured_transfer_2026_09/requirements.txt
```

On Windows use `.venv-transfer\Scripts\Activate.ps1` to activate. The scientific
runtime used Python 3.12.14, python-flint 0.9.0, gmpy2 2.3.1, mpmath 1.4.1,
NumPy 2.5.2 and SciPy 1.18.1. The new release was reconstructed on macOS;
this phase does not claim a fresh Windows certificate. Historical Markdown
contains original machine paths for provenance. Substitute this checkout root
for `/Volumes/KINGSTON/Vibecoding/Math` and your activated `python` for the old
temporary virtualenv path. Executable research paths resolve from their files.

Run from the repository root. For reproducible CPU allocation set
`OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1` and `PYTHONDONTWRITEBYTECODE=1`.
In POSIX shells use `export`; in PowerShell set `$env:NAME='value'`.

## Quick identity and exact consequence checks

```sh
python research/combined_transfer_2026_09/integrity.py
python research/combined_transfer_2026_09/framework/test_transfer.py
python research/combined_transfer_2026_09/blocks/consequences.py
python research/combined_transfer_2026_09/degree11/validate.py
python research/combined_transfer_2026_09/degree11/consequences.py
node --test website/transfer-theorem-lab/test-core.js
```

Node.js 22 runs the lab tests; it is unnecessary for scientific Python checks
or for opening the lab. These commands check identity and exact consequences.
Hashes prove that evidence is unchanged; they do not replace the derivations.

## Recompute the complete new model bounds

```sh
python research/combined_transfer_2026_09/spatial/check.py
python research/combined_transfer_2026_09/blocks/check_orbit.py --bits 384
python research/combined_transfer_2026_09/degree11/verify_model.py --bits 384
```

The spatial consumer covers all times and target pairs. The orbit consumer
reconstructs every stored actual-grid corner/lag correlation and complete
valuation remainder. The degree-eleven replay reconstructs the augmented
matrix, weighted approximation norms and complete channel checks.

## Rebuild observations and actual inverse consequences

```sh
python research/combined_transfer_2026_09/spatial/fixtures.py --replay --bits 320
python research/combined_transfer_2026_09/spatial/decoder.py
python research/combined_transfer_2026_09/review/block_review.py
python research/combined_transfer_2026_09/degree11/demonstrate.py --bits 384
```

These are model reconstructions with outward arithmetic, not laboratory data.
Use the [current research reproduction guide](../../research/combined_transfer_2026_09/README.md)
for the full command map, runtime distinctions and focused tests. In particular,
some producers intentionally rewrite runtime-bearing outputs; use a disposable
checkout when passing `--write`. Ordinary consumers are designed to check saved
evidence without modifying it.

## Inherited infinite and continuum premises

The new arithmetic proof retains the complete d₁₄ tail, all remote channels and
the digital centering certificate. The spatial proof retains the full finite-x
kernel and its derivative. Their potentially expensive reconstruction routes are
in the [transfer package](../../research/transfer_theorem_2026_09/README.md),
[uncertain-transfer package](../../research/uncertain_transfer_2026_09/README.md),
and [structured-transfer package](../../research/structured_transfer_2026_09/README.md).
The original local archive preserves all 660 predecessor files byte for byte.
The public release retains 657 files and the hashes/citations of three omitted
third-party Borsuk reference scans. These scans are not numerical inputs. The
new integrity checker permits only these explicitly named archival omissions;
all authored proofs, source code and numerical evidence are included. See
[the archive note](../../research/combined_transfer_2026_09/PUBLIC_ARCHIVE_NOTE.md).

## Read the proof or use the lab

- [Public guide](../../TRANSFER_THEOREM_PUBLIC_COMPANION.md)
- [Current theorem and hypotheses](../../research/combined_transfer_2026_09/framework/PROOFS.md)
- [Current report](../../research/combined_transfer_2026_09/REPORT.md)
- [Internal reviews](../../research/combined_transfer_2026_09/review)
- [Standalone lab](../../website/transfer-theorem-lab/index.html)

Extract `Transfer-Theorem-Lab-v1.zip` and open `index.html`. It contains everything
needed for the interactive guide. Downloaded scenario JSON can be imported
offline. Research links require internet access when followed.
