# Reproducing the fifteen-cycle continuation

Read the [findings report](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/REPORT.md), then the [cycle ledger](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/CYCLE_LEDGER.md). The [evidence index](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/EVIDENCE_INDEX.md) maps all fifteen developments to complete proofs, concrete witnesses, independent audits, and reconstruction commands. The prior five-path package and original research sources are preserved.

## One-command verification

Run from the Math repository root with the prepared numerical environment:

```sh
/private/tmp/math-five-paths-venv/bin/python research/next15_2026_09/verify_package.py --deep --output research/next15_2026_09/VALIDATION.json
```

This runs 13 checker commands covering all 15 cycles and five isolated test suites: 13 harmonic, 17 preparation, 14 quadratic, 11 noise, and 11 resolution tests, totaling **66**. It rebuilds all new harmonic and noise computations, the exact arithmetic witnesses and geometric bounds, all new resolution inequalities, and the nominal plus two finite preparation ODE enclosures. It writes only the requested validation JSON and its sibling log. Without `--deep`, the preparation verifier checks consequences from its supplied enclosures. Ordinary chain checkers do not modify their certificates. The recorded [final run](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/VALIDATION.json) passed all 18 jobs and all 66 tests; [completion audit](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/COMPLETION_AUDIT.md) records scope and preservation.

The recorded runtime is Python 3.12.14 with the versions in [requirements.txt](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/requirements.txt), including python-flint 0.9.0, FLINT 3.6.0, and MPFR 4.2.2. Installation into a separate Python environment uses `python -m pip install -r research/next15_2026_09/requirements.txt`. The prepared `/private/tmp` environment is convenient but temporary; the pinned requirements are the portable dependency record.

## What is reconstructed and what is inherited

| Path | New proof and reconstruction | Explicit retained premise |
|---|---|---|
| Harmonic | Exact label classification, complete continuous dual cover, actual nonlinear interval Jacobian and fixed-point witness; 256/384-bit controls | Original finite observation model and inspected mathematical argument |
| Preparation | Rational decoder/calibration consequences; deep mode rebuilds all three nonlinear ODE enclosures | Preserved mechanical protocol and trusted outward arithmetic primitives |
| Quadratic | Actual-field witnesses, exact finite and infinite coefficient geometry, nine-stratum sensor query; fresh full sensor-tail replay saved separately | Q3's complete Gram and remote-tail premises still require the full source replay below |
| Noise | Continuous-family bounds, every rational zeta-envelope correction, augmented drift channels and full new tail bound; 192/256-bit controls | Unchanged complete degree-14 finite/remote tail certificates, reconstructed in the prior package |
| Resolution | Analytic graph locality and moment bounds, exact rational checks, independent finite-model controls | Prior central finite/continuum floor enclosures and their documented model reconstruction |

The complete quadratic sensor premise was freshly regenerated during this continuation into [base_tail_replay.json](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/quadratic/base_tail_replay.json), reproducing the earlier certificate exactly. To repeat this independently without changing saved artifacts:

```sh
/private/tmp/math-five-paths-venv/bin/python research/five_paths_2026_09/path4_realizability/query_certificate.py --output /private/tmp/next15-quadratic-replay.json
/private/tmp/math-five-paths-venv/bin/python research/five_paths_2026_09/path4_realizability/check_certificate.py /private/tmp/next15-quadratic-replay.json
```

The unchanged, expensive degree-14 reconstructions were not rerun or counted as new cycles. Their earlier complete replay records and commands are in the [noise reproduction guide](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/noise/README.md). A nonmutating full multiscale reconstruction is:

```sh
/private/tmp/math-five-paths-venv/bin/python verify_multiscale_certificate.py --certificate certificates/arithmetic_sensing_v_multiscale_end_to_end.json --processes 4
```

The earlier single-window/remote rebuild script refreshes an old log; its guide identifies that write. The central resolution reconstruction is documented in the [preserved resolution guide](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path5_resolution/README.md). Source hashes establish premise identity, not mathematical validity. Floating large-state demonstrations are diagnostic controls, never substitutes for complete inequalities.

## Detailed proofs and audits

| Path | Complete argument | Independent review | Detailed reproduction |
|---|---|---|---|
| Harmonic | [Proofs](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/harmonic/PROOFS.md) | [Audit](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/harmonic/AUDIT.md) | [Guide](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/harmonic/README.md) |
| Preparation | [Proofs](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/preparation/PROOFS.md) | [Audit](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/preparation/AUDIT.md) | [Guide](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/preparation/README.md) |
| Quadratic | [Proofs](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/quadratic/PROOFS.md) | [Audit](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/quadratic/AUDIT.md) | [Guide](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/quadratic/README.md) |
| Noise | [Proofs](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/noise/PROOFS.md) | [Audit](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/noise/AUDIT.md) | [Guide](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/noise/README.md) |
| Resolution | [Proofs](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/resolution/PROOFS.md) | [Audit](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/resolution/AUDIT.md) | [Guide](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/resolution/README.md) |

Checkers validate finite consequences using exact integers/rationals and outward numerical contracts. Complete analytic proofs establish the infinite and continuous assertions. Independent audits are separate reasoning and controls, not formal proof-assistant verification. Exact mathematical decoders do not automatically provide a certified floating implementation or empirical apparatus validation.
