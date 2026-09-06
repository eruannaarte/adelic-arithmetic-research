# Three adaptive harmonic cycles

Start with REPORT.md (chain interpretation), CYCLES.md (objectives frozen before confirmation, results, and justified successors), and PROOFS.md (complete proofs). This directory is an isolated extension of `research/five_paths_2026_09/path2_harmonic/`; no baseline file was changed.

1. Universal horizon lower bound20.56316841858... at six readings/floor.815, versus old1.64705031364, from exact arithmetic vertex gaps.
2. A complete continuum dual bound excludes horizon21.8; an actual six-time design below30 separates all64 vertices with floor>1.03.
3. That same short design has a proved exact interior collision, with all probabilities>.07 and source separation>.79. Its full-product floor is zero.

Run from the Math repository root with the prepared Python3.12 environment:

```sh
/private/tmp/math-five-paths-venv/bin/python research/next15_2026_09/harmonic/cycle1.py
/private/tmp/math-five-paths-venv/bin/python research/next15_2026_09/harmonic/cycle2.py
/private/tmp/math-five-paths-venv/bin/python research/next15_2026_09/harmonic/cycle3.py
/private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/next15_2026_09/harmonic -p test_cycles.py -v
```

Expected: all three complete proof reconstructions PASS;13 tests PASS. These ordinary checks rebuild all model-to-certificate quantities, including the continuous time cover and the nonlinear interval Jacobian. They do not just trust saved matrices. They are inexpensive. `--write` on a cycle script deliberately regenerates its canonical evidence; Cycle3 also freezes inputs from its retained floating proposal. The mathematical checks require only Python's standard library and python-flint0.9.0/FLINT3.6.0. Discovery used NumPy2.5.2 and SciPy1.18.1, but optimization success is not a certificate premise.

Each cycle has its own `cycleN_evidence.json`. Cycle3's exact input box is `cycle3_inputs.json`; `cycle3_discovery.json` is explicitly a floating proposal, not an equality witness by itself. The exact interval root existence theorem is what proves the collision. SOURCES.md gives the primary-source context and trust boundary. No fourth cycle, optimal schedule, empirical sensor claim, or extension to arithmetic tails/unknown gain/clocks is included.
