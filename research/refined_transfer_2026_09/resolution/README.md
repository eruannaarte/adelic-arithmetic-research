# Reproduce the seven-row result

Run commands from the project root. Use the existing environment:

    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
    /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/resolution/check.py --bank 7
    /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/resolution/obstruction.py
    /private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/refined_transfer_2026_09/resolution -p 'test_resolution.py' -v

The certificate consumer uses the standard library and exact rational
arithmetic. It verifies all 3,391 records, 231 individual case covers, complete
error inequalities, and fixed noise/accuracy gates. The eight tests exercise
coverage deletion, changed contract/model premises, incorrect preconditioners,
omitted whole-cell error, all 21 target labels at endpoint/interior times,
nonzero amplitudes from \(10^{-20}\) to \(10^{20}\), allowed noise, invalid
inputs, and the coarse-grid bank's genuine physical collision.

For model-derived diagnostics using the independent finite-million-state
uniformization algorithm:

    /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/resolution/forward_checks.py

These five floating cases include the weak source target 496 at time 1 and
noise along each tested map's weakest left singular vector. They are
regression checks, not proof inputs or a verified normalization procedure.

To reconstruct the complete inherited kernel from the defining generator,
use the unchanged producer's documented replay in
[the original reproduction guide](../../transfer_theorem_2026_09/resolution/README.md).
The root package validation performs one shared 256-bit replay. Hash binding
in the fast consumer does not replace that numerical physical premise.

The optional discovery and producer commands require NumPy/SciPy:

    /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/resolution/discover.py
    /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/resolution/produce.py --bank 7

Discovery writes its own local record and stdout; it does not prove a result.
The exact producer reconstructs proposals and checks the entire result before
returning. Add --write only to replace the new package's saved certificate
and checked summary deliberately. Prior packages are never modified.

The [report](REPORT.md) gives the outcome, [proof](PROOFS.md) states every
mathematical premise, and [checked_7.json](checked_7.json) stores exact final bounds.
