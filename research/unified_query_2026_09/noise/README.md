# Reproducing the polynomial-drift extension

Read [REPORT.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/noise/REPORT.md) for the result and limits, and [PROOFS.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/noise/PROOFS.md) for the complete answer-set, polynomial-channel, Schur, noise and alias arguments.

From the Math repository root, the following commands are nonmutating:

```sh
/private/tmp/math-five-paths-venv/bin/python -S research/unified_query_2026_09/noise/check_certificate.py
/private/tmp/math-five-paths-venv/bin/python research/unified_query_2026_09/noise/polynomial_drift.py
/private/tmp/math-five-paths-venv/bin/python research/unified_query_2026_09/noise/polynomial_drift.py --precision 256
OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/unified_query_2026_09/noise -p test_polynomial_drift.py -v
```

Expected: the exact consequence checker passes; both full physical reconstructions reproduce evidence.json; all eight tests pass. Nine degree/design pairs pass their declared strict all-coefficient gates. Three searched pairs retain failed sufficient margins. Typical combined runtime is under 15 seconds in the recorded environment.

The independent checker uses only Python's standard library and does not import the producer. It recomputes the exact rational consequences from supplied numerical enclosures and verifies inherited premise identities. Its evidence is conditional on those enclosures. The producer connects them to the actual physical model: it freshly rebuilds every polynomial moment, basis, absolute norm, arithmetic/nuisance cross sum, original arithmetic Gram, full real zeta envelope, and all 8,900 entries of the inherited complete correction. The second precision reconstructs the same exported rational evidence. The tests also build polynomial vectors independently by direct weighted Gram–Schmidt and evaluate the raw physical map.

The source and acquisition contract is frozen in `INPUTS` in polynomial_drift.py and separately in the independent checker. To deliberately regenerate only this new package's evidence, add `--write` to the producer. This preserves every prior package file. The runtime is Python 3.12.14, python-flint 0.9.0 with FLINT 3.6.0, NumPy 2.5.2 and mpmath 1.4.1. The latter is used by inherited numerical controls; the actual new certificate uses outward Arb arithmetic and exact rational consequences.

The original arithmetic finite sums through \(10^6\), plus complete remote bounds beyond \(10^6\), are inherited from the prior reconstructed package. They were not silently replaced by finite tests or counted as fresh reconstructions here. Their producer commands, recorded verification outputs and trust assumptions are in the [prior noise reproduction guide](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/noise/README.md). Its expensive `rebuild_dependencies.py` command writes to the older reconstruction record; do not use it when preserving that record byte-for-byte. The original multiscale verifier provides a separate nonmutating deep replay. Hash checks in this package bind the previously established premises; they do not themselves prove their numerical contents.

The exact-fit theorem supports arbitrary polynomial drift amplitude. A deployed solve needs a separately charged coefficient error bound; any nonpolynomial residual needs a weighted observation-error budget. The proof gives both adjustments. The finite floating examples test representative amplitudes and do not remove these implementation requirements.
