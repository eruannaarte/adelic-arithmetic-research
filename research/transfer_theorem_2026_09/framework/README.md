# Reproduce the transfer theorem's executable consequences

The [complete proof](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework/PROOFS.md) supplies the theorem. The real-rational [consumer](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework/transfer.py) implements exact profiled noise forms, attained lifting witnesses, directional gates, source-image pair gates, inverse-error gates, continuous-cell inequalities, and numerical residual allowances. It does not prove a physical premise merely because the supplied numbers satisfy an inequality.

From the Math repository root:

```sh
/private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/transfer_theorem_2026_09/framework -p 'test_*.py' -v
/private/tmp/math-five-paths-venv/bin/python -S research/transfer_theorem_2026_09/framework/applications.py
/private/tmp/math-five-paths-venv/bin/python -S research/transfer_theorem_2026_09/framework/applications.py --new-noise
/private/tmp/math-five-paths-venv/bin/python -S research/transfer_theorem_2026_09/framework/applications.py --all
```

The first command runs 12 focused tests. They include correlated retained noise, attained weighted nuisance lifts, loss of a shared reference, commuting restriction without full reconstruction, dependent nuisance columns, invalid metrics, strict endpoints, an actual pair-tube collision at the boundary, sign checks before squaring, weak-direction solve error, query-class saturation, and unbounded nuisance leakage.

The second command invokes the previous model consumers and reconstructs all **687** prior scalar gates through the new function: 243 quadratic pairs, 441 polynomial-coordinate gates and three nonlinear preparation rows. The third adds the **98** core degree-six gates. `--extended-noise` checks all **392** gates in the bounded extension's eight design/degree pairs and the same 392 with an additional conditional normal-residual allowance of 10^-8.

`--all` includes the complete spatial consumer and verifies three global source-metric contracts through the pair and inverse gates, covering all 21 targets and 210 pairs over their checked continuous-time cover. It includes a conditional computed-data allowance of 10^-9 times the source norm and proves source error below 0.000962 for an exact final inverse. These global metric contracts are not counted as hundreds of additional identical scalar tests. `--write` saves the selected [application result](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework/applications.json) without editing earlier packages.

The [independent review](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/framework_review/REVIEW.md) includes ten exact assumption witnesses, a separate equality-constrained minimum-noise reconstruction for 205 residuals, and 180 exact continuous-cell comparisons. General arguments are not validated by sampling: these examples exercise delicate assumptions and the code, while the complete proofs establish the quantified claims.

The theorem covers real and complex finite data spaces. The matrix consumer deliberately supports exact real rational input and full-row-rank retained maps; redundant rows require a separate independent row basis with range-consistency checks, or the theorem's pseudoinverse formula. Binary floating inputs and Boolean scalars are rejected rather than silently interpreted as exact certificates.

Inherited arithmetic-tail, nonlinear ODE and calibration premises retain their recorded provenance. The new application adapter checks their consequences; the consolidated reproduction guide distinguishes unchanged inherited producers from new model reconstructions. Physical preparation remains unverified.
