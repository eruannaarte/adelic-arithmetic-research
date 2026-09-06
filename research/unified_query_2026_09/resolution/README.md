# Reproduce the smaller asymmetric sensing banks

Read [REPORT.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/REPORT.md) for the result and [PROOFS.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/PROOFS.md) for the complete weighted semigroup, acquisition transfer, joint decoder, and necessary-channel arguments.

From the Math project root, run:

```sh
python -S research/unified_query_2026_09/resolution/check.py
python -S research/unified_query_2026_09/resolution/certificate.py
python -m unittest discover -s research/unified_query_2026_09/resolution -p test_banks.py -v
python research/unified_query_2026_09/resolution/example.py
```

The first two commands require only the Python standard library. They recheck the inherited rational placement and original resolution certificates, then rebuild all new bounds with exact rational arithmetic. The producer and checker use different Taylor orders, 160 and 180. Neither trusts a saved floating matrix or a requested tolerance. `certificate.py --write` deliberately replaces the local evidence file; its default only reconstructs and checks.

Tests require NumPy, SciPy, and python-flint. The working environment is Python 3.12.14, NumPy 2.5.2, SciPy 1.18.1, python-flint 0.9.0 / FLINT 3.6.0. The existing environment at `/private/tmp/math-five-paths-venv/bin/python` contains these dependencies. Eight tests include certificate tampering, an independently assembled variable-coefficient graph, an Arb whole-source-subspace exponential enclosure, tail moment bounds, centroid noise controls, and exact ambiguity constructions.

The last command reconstructs the full finite graph responses at $n=1001$, at two endpoint times and two extreme target positions. It runs 192 noise/source controls through a decoder that first identifies the target. It is a floating regression, explicitly separate from the proof. `example.py --write` refreshes the local diagnostic JSON; the default leaves files unchanged.

The model, normalization, source metrics, and continuous-time baseline remain those in the [prior package](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/resolution/README.md). The expensive central Arb coefficient producer is an inherited, previously audited premise and is not rerun by these commands. Artifact hashes bind inputs but do not prove those underlying interval enclosures. The new tail calculation itself is self-contained and has no additional interval-integration premise.

[Evidence](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/evidence.json) records both row inventories, all 21-label tail maxima, metric-calibrated floor consequences, and decoder margins. [Validation](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/VALIDATION.json) records executed checks; [the model example](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/example.json) records diagnostic outcomes. The direct-readout, global-average, known-time, source-amplitude, and numerical-inverse limits are part of the theorem and must accompany any acquisition claim.
