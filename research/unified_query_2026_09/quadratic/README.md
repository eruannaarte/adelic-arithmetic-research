# Reproducing the joint quadratic query

Read [PROOFS.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/quadratic/PROOFS.md) for full definitions and proofs and [REPORT.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/quadratic/REPORT.md) for interpretation. The independent audit provides a separate exact reconstruction and explicit actual-field witnesses.

From the Math repository root:

```sh
/private/tmp/math-five-paths-venv/bin/python -S research/unified_query_2026_09/quadratic/joint_query.py
OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/unified_query_2026_09/quadratic -p 'test_*.py' -v
/private/tmp/math-five-paths-venv/bin/python -S research/unified_query_2026_09/quadratic/audit_independent.py
```

The mathematical checker and independent arithmetic audit use exact Python integers and fractions. Seven focused tests additionally use NumPy for full8,900-reading operator controls. `--write` on joint_query.py deliberately regenerates certificate.json; ordinary verification does not change artifacts.

The prior complete d₂ sensor tail and Gram certificate is inherited, revalidated by its original strict standard-library checker, and bound by its immutable source content. Its recorded full Arb replay is in [the prior quadratic package](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/quadratic/README.md). No complete tail is replaced by a finite surrogate. No expensive unchanged premise is represented as a newly reconstructed calculation.

`answer_set` validates its certificate, certifies the two anchors, and returns an outer set of admissible a(5) labels. `None` means anchor certification is unavailable; an empty set means the model/budgets and supplied values are inconsistent. `decode` returns an answer only for a singleton and otherwise abstains. A numerical error vector can accompany approximate coefficients; its entries must bound absolute errors in the unnormalized coefficient estimates. The radius table assumes zero such error, corresponding to the exact inverse operator.

The [independent audit](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/quadratic/AUDIT.md) records the mathematical and implementation review. Its [exact evidence](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/quadratic/audit_independent.json) includes 81 explicit positive fundamental discriminants, squarefree-radicand factorizations, full coefficient prefixes, and all-pair verification summaries. The [separate audit implementation](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/quadratic/audit_independent.py) reconstructs these facts without calling the certificate producer.
