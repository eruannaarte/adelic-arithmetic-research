# Path 3 — arithmetic sensing with sensor noise

CHAPTER.md is the concise presentation; PROOF.md defines the acquisition, decoder, complete tail/Gram hypotheses, exact deterministic and Gaussian guarantees, and variance comparison. PREREGISTRATION.md froze the metrics before computation. AUDIT.md records the independently found and repaired remote-source binding gap and the scientific boundaries.

New result at 8,900 distinct readings: multiscale recovery of all 50 envelope coefficients is certified for weighted adversarial radius 7e-7 (also for the common coordinatewise bound |epsilon_j|<=7e-7). Under iid proper circular complex noise with E|epsilon_j|^2=1e-10, any rounding failure has probability <5.466e-14. The multiscale target-50 iid variance is nevertheless >1.000265975 times the single-window variance. The single-window's sufficient bias bound is above1/2; no impossibility conclusion follows.

Run from the Math repository root. Session runtime: /private/tmp/math-five-paths-venv/bin/python (Python3.12, python-flint0.9.0, NumPy2.5.2, SciPy1.18.1, gmpy2 2.3.1/MPFR4.2.2).

Fast independent exact consequence checker (standard library only):

```sh
python3 research/five_paths_2026_09/path3_noise/check_consequences.py
```

Expected: PASS for bias-margin, Neumann variance, bounded noise, rational Gaussian tail and variance inflation. This treats the saved tail/Gram/weight enclosures as premises.

Fast Arb/Gram/weight producer and independent controls (about one second):

```sh
/private/tmp/math-five-paths-venv/bin/python research/five_paths_2026_09/path3_noise/audit_checks.py
```

Expected: 5 tests PASS, including full direct covariance and source tamper controls. The actual certificate is certificate.json. To write a fresh derived copy outside this package:

```sh
/private/tmp/math-five-paths-venv/bin/python research/five_paths_2026_09/path3_noise/noise_certificate.py --write /private/tmp/path3-noise-fresh.json
```

Complete dependency checks are more expensive:

```sh
/private/tmp/math-five-paths-venv/bin/python research/five_paths_2026_09/path3_noise/rebuild_dependencies.py
```

Expected: both MPFR remote tails and the entire single-window finite/Gram source verify; dependency_rebuild.json records PASS and runtime. The initial fresh run took394s. The separate existing multiscale verification, recorded in multiscale_rebuild.json, took417s. Its exact nonmutating command is:

```sh
/private/tmp/math-five-paths-venv/bin/python verify_multiscale_certificate.py --certificate certificates/arithmetic_sensing_v_multiscale_end_to_end.json --processes 4
```

The distinction is deliberate: consequence checking is fast; complete finite/infinite arithmetic-tail reconstruction is not. Both layers have completed for this package. No full hardware-noise validation or numerical-roundoff allowance for an actual deployed decoder is claimed.
