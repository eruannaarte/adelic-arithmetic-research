# Five-path mathematics research package

Start with the [2,678-word report](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/REPORT.md). Its opening synthesis is 275 words. It develops all five paths from the [earlier review](/Volumes/KINGSTON/Vibecoding/Math/MATH_RESEARCH_REVIEW_2026-09-04.md), under the [goal prompt](/Volumes/KINGSTON/Vibecoding/Math/MATH_RESEARCH_DEVELOPMENT_GOAL_PROMPT.md).

- [Proof appendix and complete proof map](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/PROOF_APPENDIX.md): all model definitions, full proof files, accepted theorems and hypotheses, and trusted numerical components.
- [Claim-to-evidence index](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/CLAIM_EVIDENCE_INDEX.md): 27 central claims, distinguishing analytic results, finite certificates, historical premises, and implementation controls.
- [Completion audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/COMPLETION_AUDIT.md): requirement-by-requirement outcome and explicit research boundaries.
- [Final package validation](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/validation_tests.json) and [detailed output](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/validation_tests.log): all six main certificate checks and 62 focused controls passed.

This directory contains all newly authored proofs, code and certificates. It imports preserved source modules and historical certificate dependencies from the surrounding Math repository; it is not an independent installed Python package. The starting repository commit was `3d71fade83f57c6fcdb4b044145c44084af589ab`. Existing tracked research files were preserved. No publication or external communication was performed.

## Reproduce the checks

Use Python 3.12 and the exact versions in [requirements.txt](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/requirements.txt). For a fresh temporary environment:

```sh
cd /Volumes/KINGSTON/Vibecoding/Math
python3.12 -m venv /private/tmp/math-five-paths-check
/private/tmp/math-five-paths-check/bin/python -m pip install -r research/five_paths_2026_09/requirements.txt
/private/tmp/math-five-paths-check/bin/python research/five_paths_2026_09/verify_package.py --tests
```

The environment used for this research remains at `/private/tmp/math-five-paths-venv/bin/python`. It is session-local and can be replaced by any environment satisfying the pinned requirements. The tested underlying libraries were Python 3.12.14, FLINT 3.6.0 and MPFR 4.2.2.

The default command performs six quick checks (about 2 seconds here):

```sh
python research/five_paths_2026_09/verify_package.py
```

Adding `--tests` runs the six checks plus62 controls: 9 nonlinear-preparation tests, 15 harmonic tests, 5 noise/covariance tests, 17 quadratic-query/realizability tests, and 16 resolution tests. The final combined run took 16.34 seconds. It includes a complete nonlinear replay, harmonic phase reconstruction, independent decoder covariance, exact field witnesses, forged-certificate controls, and a small-grid independent matrix exponential. Expected result: 11 PASS lines, exit status 0, and `verified:true` in `validation_tests.json`.

These checks are mathematically meaningful but are not all equivalent. Some small checkers establish consequences of supplied outward intervals. The corresponding model-to-interval producer must also be replayed to reconstruct those premises; the independent analytic enclosure proof explains why the producer is valid.

## Complete numerical reconstruction

All required numerical premises were reconstructed during this research. Individual evidence records are retained:

| Path | Full reconstruction performed | Evidence |
|---|---|---|
| 1 | Nonlinear source, shared-clock and preparation tubes, plus alternate precision/order/step | [validation log](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path1_preparation/validation.log), [independent audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path1_preparation/AUDIT.md) |
| 2 | All phases and finite inequalities, original baseline, 512-bit refinement | [independent audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path2_harmonic/AUDIT.md), [package log](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/validation_tests.log) |
| 3 | Both MPFR remote tails plus complete single-window finite/Gram reconstruction 394s; complete multiscale finite/Gram reconstruction 417s | [remote/single replay](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path3_noise/dependency_rebuild.json), [multiscale replay](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path3_noise/multiscale_rebuild.json) |
| 4 | All 497,500 finite tail terms and Gram rows at 192 and 256 bits; independently proved infinite remote tail | [certificate](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path4_realizability/certificate.json), [refinement](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path4_realizability/refinement.json), [audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path4_realizability/AUDIT.md) |
| 5 | Both full n=1001 time cells, fresh continuum-core quadrature, higher-precision first cell, independent small-grid implementation | [validation](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path5_resolution/VALIDATION.json), [refinement](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path5_resolution/refinement_validation.json), [audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path5_resolution/AUDIT.md) |

To repeat the full standard numerical chain, including the slow arithmetic reconstructions and both resolution cells:

```sh
python research/five_paths_2026_09/verify_package.py --deep
```

Allow roughly 15–25 minutes, depending on hardware. This command regenerates named package certificates and validation records; it does not edit the historical source manuscripts. Its steps were run individually during development; the expensive combined wrapper itself was not rerun after those successful checks. Optional higher-order Path5 refinement and exact path-specific commands are in the [master appendix](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/PROOF_APPENDIX.md) and each path README. The standard full runner includes the Path4 refinement, while Path1 and Path2 refinements are already part of their tests.

The report can be rebuilt from the reviewed chapters with `python research/five_paths_2026_09/assemble_report.py`; it checks the requested word limits. Numerical displays are rounded summaries. Exact rationals and interval endpoints decide proof acceptance. The package is not a proof-assistant formalization, and its mathematical models and sensor-noise laws have not been empirically validated.
