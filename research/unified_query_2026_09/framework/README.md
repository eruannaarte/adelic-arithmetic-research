# Reproducing the common transfer layer

Read [PROOFS.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/framework/PROOFS.md) for the complete set, minimax, quotient, and support-function arguments. [REPORT.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/framework/REPORT.md) states their role and limitations. The independent [audit](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/framework/AUDIT.md) includes separate anisotropic-metric and asymmetric-support checks.

From the Math root:

```sh
/private/tmp/math-five-paths-venv/bin/python -S research/unified_query_2026_09/framework/check_applications.py
/private/tmp/math-five-paths-venv/bin/python -S -m unittest discover -s research/unified_query_2026_09/framework -p 'test_*.py' -v
```

Expected:687 exact scalar gates across three models pass; six focused tests pass. `check_applications.py --write` deliberately saves application_validation.json; ordinary checking does not mutate it. The six controls illustrate exact boundary, metric, correlation, and centering cases; the analytic theorems are established by the supplied proofs, not inferred from finite tests.

The application checker calls each model's strict consumer before reconstructing its scalar transfer. The nonlinear ODE, full arithmetic tails, and polynomial special-function bounds remain the model-specific proof/reconstruction obligations detailed in their guides. The common checker includes the digital correction error in the polynomial total radius and preserves the nonlinear diameter conclusion's non-strict endpoint.
