# Adaptive nonlinear preparation research — exactly three cycles

Read [CHAIN_REPORT.md](CHAIN_REPORT.md) for the chain, [CYCLES.md](CYCLES.md) for objectives recorded before calculations and adaptive decisions, and [PROOFS.md](PROOFS.md) for complete mathematical arguments, model hypotheses, worked examples, and limitations. Baseline research is unchanged.

## Claim/evidence index

| Claim | Proof / finite evidence | Scope |
|---|---|---|
| Shared launch-sensitivity projection certifies rho=10^-6, a tenfold increase over baseline with smaller sufficient source diameter | PROOFS Cycle 1; cycle1_region.json; cycle1_certificate.json | Entire finite source/preparation boxes; same scalar sensors and metric |
| Preparation-aware fixed rational decoders certify rho=7e-6 where least-squares controls fail the same gate | PROOFS Cycle 2; cycle2_region.json; cycle2_certificate.json; cycle2_calibration.json | Primary rho=10^-5 failure retained; no global decoder-optimality claim |
| Anisotropic calibration admits seven radii near 10^-5, with B.theta1 tighter; volume >5× isotropic and provably within 6e-10 relative of the certificate optimum | PROOFS Cycle 3; cycle3_certificate.json | Fixed synthesized decoder and finite constraint polytope, not true inverse-problem optimality |

The five fixed A+B readings have the same costs in the selected and uniform comparisons. C is available in the Cycle 1/2 ABC control and inactive in the equal-access Cycle 3 volume comparison. Preparation is a bounded unknown shared within each launch. Clock dilation is finite and shared globally. No actual preparation observations or empirical feasibility evidence are assumed.

## Reproduce

From this directory, using the prepared runtime:

```sh
/private/tmp/math-five-paths-venv/bin/python -S verify.py
/private/tmp/math-five-paths-venv/bin/python verify.py --deep
/private/tmp/math-five-paths-venv/bin/python -m unittest test_preparation test_cycle2 test_cycle3 -v
```

The first command uses only the Python standard library and verifies the exact consequences of the supplied finite enclosures. The deep command recomputes the nominal, Cycle 1, and Cycle 2 outward ODE boxes, including source hashes; all scientific fields must match exactly. Nominal takes about 4 seconds and each finite box about 4 seconds on the recorded host. Runtime seconds are descriptive and excluded from equality. `validation.log` contains the complete test run; individual cycle logs retain the checks used before selecting each successor.

To regenerate candidate outputs into new paths (existing artifacts are protected from accidental overwrite):

```sh
/private/tmp/math-five-paths-venv/bin/python full_sensitivity.py --radius 0 --preparation 0 --output /private/tmp/prep-nominal-rebuild.json
/private/tmp/math-five-paths-venv/bin/python full_sensitivity.py --preparation 1/1000000 --output /private/tmp/prep-cycle1-rebuild.json
/private/tmp/math-five-paths-venv/bin/python full_sensitivity.py --preparation 1/100000 --output /private/tmp/prep-cycle2-rebuild.json
/private/tmp/math-five-paths-venv/bin/python synthesize.py cycle2_region.json nominal.json --output /private/tmp/prep-decoders-rebuild.json
/private/tmp/math-five-paths-venv/bin/python anisotropic.py --output /private/tmp/prep-volume-rebuild.json
```

Candidate LP/SLSQP output need not be bit-identical across optimizer versions. The saved rational decoder and primal/dual witnesses are validated without rerunning optimization. Certificate decisions use exact fractions and integer square-root upper bounds; displayed decimal roots and optimizer diagnostics are not trusted.

`full_sensitivity.py` uses the preserved root modules `oig_double_pendulum_validated_transfer.py` (Arb interval/series primitives and step configuration) and `oig_double_pendulum_protocol.py` (literal protocol, independently cross-checked by the consequence verifier). The diagnostic tests additionally use `double_pendulum_dynamics.py` for its mechanical matrix-solve RHS. `requirements.txt` records the numerical runtime; the fast verifier has no third-party dependency.

Trust remains in the analytic variational/first-exit proofs, python-flint/Arb's outward elementary and power-series arithmetic, and Python integer arithmetic. This is not proof-assistant verification or experimental validation. A failed sufficient gate is never reported as mathematical impossibility.
