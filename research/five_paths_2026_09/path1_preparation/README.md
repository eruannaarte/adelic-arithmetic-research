# Path 1 — Certified nonlinear inference with bounded preparation

Start with CHAPTER.md; PROOF.md contains all definitions, complete proofs, source/hypothesis checks, comparison semantics and limitations. PROTOCOL.md froze the primary comparison before its design-bound outcomes. Existing repository research was not changed.

New certificate: |u|,|v|,|shared log-clock|<=1e-4; independent unknown errors <=1e-7 in four initial coordinates per launch; finite nonlinear preparation/clock propagation. At weighted adversarial noise norm<=1e-7, any two feasible parameter triples differ by <2.011628e-5 under selected A+B, compared with <2.489142e-5 for uniform A+B+C. See comparison.json and noise_region.json. Uniform A+B has a slightly smaller preparation-dominated sufficient bound. No claim of empirical model adequacy or global optimality.

Run from the Math repository root. Tested runtime: Python 3.12.14; python-flint 0.9.0, NumPy 2.5.2, SciPy 1.18.1. The common session runtime is /private/tmp/math-five-paths-venv/bin/python. A fresh environment requires python-flint, numpy and scipy (all pinned in requirements.txt); the code also imports existing root modules.

Fast exact algebra checker (standard Python only; under one second):

```sh
python3 research/five_paths_2026_09/path1_preparation/checker.py research/five_paths_2026_09/path1_preparation/region.json research/five_paths_2026_09/path1_preparation/nominal.json
```

Expected: three certified designs, k approximately 0.0774604, 0.0832491, 0.0769582; diameters approximately 2.011627e-5, 2.489141e-5, 1.979238e-5. This checker proves consequences of supplied interval matrices; it does NOT establish their connection to the nonlinear ODE.

Complete source-to-certificate validation (about 14 seconds here, including numerical controls):

```sh
/private/tmp/math-five-paths-venv/bin/python research/five_paths_2026_09/path1_preparation/validate.py
```

Expected: 9 tests PASS. This reconstructs the nominal/primary/alternate interval integrations, all source/input/scientific fields, and provenance hashes. It independently tests the mechanical RHS, sensitivity directions, finite preparation and shared-clock effects; it rejects forged enclosures even with otherwise valid declarations. No expensive full-repository run is necessary for this isolated addition. validation.log records the final local run.

Generate a fresh primary certificate without overwriting existing files:

```sh
/private/tmp/math-five-paths-venv/bin/python research/five_paths_2026_09/path1_preparation/preparation.py --radius 1/10000 --preparation 1/10000000 --output /private/tmp/path1-region-fresh.json
```

For nominal: --radius 0 --preparation 0. For the alternate outward proof add --step 1/125 --bits 192 --order 9. Production refuses an existing output. The artifact runtime is descriptive and excluded from deep equality; all other fields are reconstructed. Proof decisions use exact rational inequalities or outward Arb comparisons, never decimal displays.

Files:

- preparation.py: 15-coordinate outward ODE/sensitivity/clock and preparation-bias producer; adapts the repository's previously audited Picard–Taylor method.
- checker.py: independent Fraction-only inverse-stability and noise certificate reconstruction, with explicit seven-sensor contract.
- validate.py: source replay, alternative partition, independent mechanical and finite-difference checks, finite nonlinear heldouts, and false/boundary controls.
- nominal.json, region.json, alternate.json: accepted outward proofs under declared configurations.
- pilot.json: earlier feasibility-only small-box calculation; it is not the primary comparison.
- comparison.json: exact fixed-left-inverse matrices and rigorous bounds.
- noise_region.json: exact preparation/noise half-planes at desired diameter 1e-4.
- evidence.json: claim/evidence and limitations map.

See PROOF.md for residual trust in Arb, Python integer arithmetic, and the analytic interval theorem. A hash establishes source identity; deep nonlinear replay and the mathematical proof establish the claimed model connection. The two outward runs share the same underlying field implementation and Arb library.
