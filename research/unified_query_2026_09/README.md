# Reproduce the unified query-recovery research

Start with [REPORT.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/REPORT.md), the [evidence index](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/EVIDENCE_INDEX.md), and the project-wide [current-state index](/Volumes/KINGSTON/Vibecoding/Math/MATH_CURRENT_STATE.md). The [completion record](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/COMPLETION_AUDIT.md) connects the requested objectives to the delivered evidence and remaining limits. Earlier research packages and original tasks remain historical records. This package has not been published.

## Consolidated check

From the Math repository root:

```sh
/private/tmp/math-five-paths-venv/bin/python research/unified_query_2026_09/verify_package.py --deep --output research/unified_query_2026_09/VALIDATION.json
```

The full run performs 21 jobs: 13 application/reconstruction commands, six isolated suites containing 49 focused tests, complete preparation ODE replay, and the 192-case full finite-graph diagnostic. The [validation JSON](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/VALIDATION.json) and sibling log record the exact commands and results. Without `--deep`, the last two jobs are omitted; new harmonic and polynomial source reconstructions still run. The wrapper writes only the requested output and its sibling log; individual ordinary verification commands preserve their evidence files.

The numerical runtime is Python 3.12.14 with [pinned requirements](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/requirements.txt): NumPy 2.5.2, SciPy 1.18.1, mpmath 1.4.1, gmpy2 2.3.1, and python-flint 0.9.0 (FLINT 3.6.0, MPFR 4.2.2 in the recorded environment). To recreate an isolated environment, install the requirements with `python -m pip install -r research/unified_query_2026_09/requirements.txt`. The prepared `/private/tmp` runtime is convenient but temporary.

## Proofs, audits, and reproduction boundaries

| Track | Complete proof | Independent audit | Detailed commands |
|---|---|---|---|
| Common framework | [Proof](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/framework/PROOFS.md) | [Audit](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/framework/AUDIT.md) | [Guide](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/framework/README.md) |
| Harmonic | [Proof](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/PROOFS.md) | [Audit](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/AUDIT.md) | [Guide](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/README.md) |
| Preparation | [Proof](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/PROOFS.md) | [Audit](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/AUDIT.md) | [Guide](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/README.md) |
| Quadratic | [Proof](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/quadratic/PROOFS.md) | [Audit](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/quadratic/AUDIT.md) | [Guide](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/quadratic/README.md) |
| Polynomial drift | [Proof](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/noise/PROOFS.md) | [Audit](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/noise/AUDIT.md) | [Guide](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/noise/README.md) |
| Sensing bank | [Proof](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/PROOFS.md) | [Audit](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/AUDIT.md) | [Guide](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/README.md) |

Harmonic reconstructions independently use factored and 64-label formulas, each at 256/384 bits. Polynomial drift rebuilds all new actual-grid basis, cross-moment, absolute-norm, and complete nuisance-tail quantities, plus the full 8,900-entry correction at 192/256 bits. Preparation rechecks exact interval consequences and, with `--deep`, rebuilds all three inherited nonlinear ODE enclosures. Quadratic checking covers all 243 pairs and supplies 81 explicit actual-field witnesses. Resolution's new weighted-energy bound uses exact rational exponential remainders; the large-state examples remain floating controls.

The common checker reconstructs 687 exact scalar gates after invoking each relevant model consumer. Those gates are applications of one theorem, not 687 research results or tests of the infinite theorem by sampling. The six suites contain 6 framework, 10 harmonic, 10 preparation, 7 quadratic, 8 noise, and 8 resolution tests.

The complete d₂ finite/remote tail and Gram source, complete d₁₄ arithmetic finite/remote tails, and central finite/continuum resolution floors retain their documented earlier model reconstructions. Their identities and required consequences are checked here. Full replay commands are in the [prior reproduction guide](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/README.md). Hashes establish identity, not correctness. The unchanged expensive d₁₄ and central-resolution producers are not rerun by this wrapper and are not presented as newly reconstructed premises.

## Preparation records

The [calibration protocol](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/CALIBRATION_PROTOCOL.md), [record schema](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/record.schema.json), and [synthetic example](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/synthetic_calibration.json) specify the required data. Another record can be assessed with:

```sh
/private/tmp/math-five-paths-venv/bin/python -S research/unified_query_2026_09/preparation/calibration_bridge.py --record /absolute/path/to/record.json
```

The example's physical status is NOT_RUN. A record labelled physical still requires external provenance and model validation. The inspected Atlas and chamber provide internal numerical evidence, not measured apparatus calibration. No remote computation or Windows access was necessary, and no existing browser interface was changed.

Mathematical decoders retain explicit numerical-error contracts. Independent audits are separate reasoning and implementations, not formal proof-assistant verification or empirical validation. Discovery searches and diagnostic controls remain distinct from complete proofs and outward certificates.
