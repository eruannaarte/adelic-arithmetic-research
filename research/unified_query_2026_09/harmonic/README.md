# Uniform harmonic collision family

Read [REPORT.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/REPORT.md) for the result and limitations, and [PROOFS.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/PROOFS.md) for the complete proof. This package preserves all earlier harmonic files and has no runtime dependency on their code or saved matrices.

Run from the Math repository root:

```sh
/private/tmp/math-five-paths-venv/bin/python research/unified_query_2026_09/harmonic/uniform_collision.py
/private/tmp/math-five-paths-venv/bin/python research/unified_query_2026_09/harmonic/uniform_collision.py --precision 384
/private/tmp/math-five-paths-venv/bin/python research/unified_query_2026_09/harmonic/uniform_collision.py --independent
/private/tmp/math-five-paths-venv/bin/python research/unified_query_2026_09/harmonic/uniform_collision.py --independent --precision 384
/private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/unified_query_2026_09/harmonic -p test_uniform_collision.py -v
```

Expected: four complete model-to-certificate replays pass, and ten tests pass. No discovery optimization is needed. Each ordinary replay rebuilds phases, source/time derivative intervals, uniform existence bounds, all source-domain gates, all 171 vertex-difference bounds, and the fixed query obstruction. `--independent` uses a separately implemented 64-term integer-label expansion instead of factored products. Both use Arb inclusion arithmetic. The requirements are Python's standard library and python-flint 0.9.0 with FLINT 3.6.0. The prepared runtime uses Python 3.12.14.

[inputs.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/inputs.json) contains the exact rational center, active coordinates, preconditioner, affine predictor, radii, and claims. [certificate.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/certificate.json) and [independent_certificate.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/independent_certificate.json) are outward rational consequences. Passing `--write` deliberately regenerates the selected certificate from the frozen inputs; ordinary checks never write.

`check_consequences` checks exact exported inequalities and the frozen query arithmetic. It alone does not authenticate numerical premises. The command-line entry point first rebuilds the entire model certificate and matches its saved record, then runs the consequence checks.

The source coordinates and preconditioner originate in the earlier isolated collision, but neither its near-zero residual nor any earlier saved Jacobian is trusted. The moving predictor was proposed from the exact-input point model. All validation is repeated here over the full new time/source box. [VALIDATION.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/VALIDATION.json) records the performed checks and rejected controls.
