# Reproduce the transfer theorem and its consequences

Start with the [research report](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/REPORT.md). The [goal protocol](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/PROTOCOL.md) states the acceptance criteria, and the [completion record](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/COMPLETION_AUDIT.md) maps them to delivered results. The [current-state index](/Volumes/KINGSTON/Vibecoding/Math/MATH_CURRENT_STATE.md) places this extension after the preserved earlier research.

## Consolidated verification

From the Math repository root:

```sh
/private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/verify_package.py --output research/transfer_theorem_2026_09/VALIDATION.json
```

The full run includes **15 jobs and 31 focused tests**: 12 framework, 10 polynomial and nine spatial tests. It also runs all common applications, exact assumption witnesses, independent constrained-minimum calculations, degree-six and extended physical polynomial reconstructions, a separate 320-bit polynomial audit, 192/256-bit spatial kernel reconstructions, the independent spatial model audit, and 27 floating controls using the million-state finite graph. The [validation record](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/VALIDATION.json) and its sibling log are authoritative for actual commands and outcomes.

The wrapper verifies all 279 prior research artifact identities against [the initial manifest](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/PREVIOUS_ARTIFACTS_SHA256.json). It writes only the requested report and log. Add `--quick` to omit full new model and independent numerical reconstructions; that mode checks consequences conditional on their saved enclosures and is not a substitute for the full run.

The recorded runtime is Python 3.12.14 with the [pinned requirements](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/requirements.txt). The prepared `/private/tmp` environment is temporary. An isolated Python 3.12 environment can install the same requirements with:

```sh
python -m pip install -r research/transfer_theorem_2026_09/requirements.txt
```

The numerical dependency versions are NumPy 2.5.2, SciPy 1.18.1, mpmath 1.4.1, gmpy2 2.3.1 and python-flint 0.9.0. The recorded native libraries are FLINT 3.6.0 and MPFR 4.2.2. Outward interval arithmetic is a trusted component; independent reconstruction and precision checks reduce implementation risk but are not formal proof-assistant verification.

## Evidence map

| Component | Complete argument | Independent review | Reproduction detail |
|---|---|---|---|
| Transfer geometry and quantitative theorem | [Framework proofs](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework/PROOFS.md) | [Theorem and consumer review](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework_review/REVIEW.md) | [Framework guide](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework/README.md) |
| Complete oscillatory drift channels | [Polynomial proofs](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/noise/PROOFS.md) | [Independent physical reconstruction](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/noise/AUDIT.md) | [Polynomial guide](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/noise/README.md) |
| Eleven separated spatial averages | [Spatial proofs](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/resolution/PROOFS.md) | [Independent model audit](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/resolution/AUDIT.md) | [Spatial guide](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/resolution/README.md) |
| Binding the models to one theorem | [Application adapter](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework/applications.py) | [Adapter audit](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework/APPLICATION_AUDIT.md) | [Application results](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework/applications.json) |

The [synthesis review](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/SYNTHESIS_AUDIT.md) checks the final cross-model presentation. Each application retains its actual source class, noise metric and acquisition cost.

## What is reconstructed and what is inherited

The common adapter first invokes the applicable strict model consumers. It then reconstructs 687 earlier scalar gates, 392 new polynomial gates, and the same 392 with a conditional exact-model normal residual allowance. Its three spatial metric contracts use the complete cover for 21 individual maps and 210 pairs, with 895 whole-cell records. These counts describe consequences and coverage, not independent theorems or unit tests.

The new polynomial producers reconstruct both actual 8,900-entry weight designs, all relevant weighted polynomial moments and cross terms, the complete zero-extended differences, the uniform finite-frequency argument, the infinite remote bound, and the full digital centering correction. The separate audit rebuilds the basis by full-vector orthogonalization and replaces the remote zeta constant by a looser independently proved rational bound. All eight design/degree cases still pass.

The expensive unchanged d14 arithmetic-channel tail enumeration and remote source bounds are inherited from the earlier packages. The new code checks their identity and required consequences, and rebuilds the actual Gram and new nuisance channels. The [previous reproduction guide](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/README.md) gives the original full replay commands. A hash establishes identity, not mathematical correctness.

Spatial recovery uses a newly reconstructed full finite-x model, complete transverse-image and finite-boundary estimates, a complete Taylor remainder, and exact per-case continuous-time coverage. It does not inherit the former central information-floor certificate as a new unexplained numerical input. Rational polynomial evaluation and relative-feasibility decoding are implemented; known rational time and exact or budgeted normalization are part of that interface. The mathematical theorem covers every real known time in [1,2].

## Numerical and physical contracts

The arithmetic table permits a **verified exact-model normal residual at most 10^-8** in addition to the sensor noise and digital correction. This is a conditional solve acceptance criterion. It does not assert that an arbitrary floating solver already verifies its residual or handles unlimited drift amplitude accurately.

The spatial table includes a **conditional computed-data error at most 10^-9 times the relevant source norm**. The common adapter then proves source error below 0.000962 for an exact final inverse. Any separate inverse-computation error must be added. Its exact rational decoder consumes unnormalized data, so input normalization must itself be exact or covered by the declared budget. Timing, sensor calibration and source-mode mismatch require additional proved allowances before deployment.

Neither application assumes an empirical noise distribution. The eleven spatial averages save acquisition only if they are directly available. The pendulum calibration status remains unverified; this goal adds mathematical results, not hardware data. Earlier conversations and packages are preserved, and no public release is made here.
