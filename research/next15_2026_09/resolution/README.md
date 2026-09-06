# Three adaptive resolution cycles

Read [CYCLES.md](CYCLES.md) for objectives and adaptive decisions, [CHAIN_REPORT.md](CHAIN_REPORT.md) for the synthesis, and [PROOFS.md](PROOFS.md) for full mathematical arguments. Exactly three developments are counted: interior-placement locality, unknown-target localization, and a restricted spatial sensing operator.

The declared model remains n=1001,K=2,g=4/5,tau∈[1,2]. The output is normalized full-field Euclidean energy; the three source calibrations remain L2, continuum H1 and natural discrete H1. Off-center targets generally activate odd modes. A99-row spatial operator does not mean99 fully local physical detectors: every row retains a global x-average, and acquisition savings require those spatial readouts to be available directly.

## Reproduction

Use Python3.12+ with numpy2.5.2 and python-flint0.9.0 for all controls. The three consequence checkers themselves use only the standard library, including the existing baseline rational checker:

```
python research/next15_2026_09/resolution/check_placement.py
python research/next15_2026_09/resolution/check_localization.py
python research/next15_2026_09/resolution/check_window.py
python -m unittest discover -s research/next15_2026_09/resolution -p 'test_*.py' -v
```

Regenerate new exact certificates in order with placement.py, localization.py, window.py. Simulate the full1002001-state finite model with simulate.py and window_example.py; these write explicitly labelled floating regression examples and are not proof inputs.

The inherited central certificate at `research/five_paths_2026_09/path5_resolution/certificate.json` is hash-bound and its complete rational consequences are rechecked automatically. Its model-to-Arb Taylor coefficients and continuum floor premises retain their prior proof/replay obligations; the original package documents their completed reconstruction. Nothing here alters that baseline or turns source hashes into mathematical proof. The new bounds after that premise are analytic graph-walk inequalities and exact integer/Fraction arithmetic.
