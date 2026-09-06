# Three actual-arithmetic research cycles

Read CHAIN_REPORT.md for interpretation, CYCLES.md for the objectives recorded before confirmation and their adaptive successors, and PROOFS.md for the complete arguments. Exactly three substantive cycles are counted.

- Q1: exact three-label geometry of all realizable quadratic prefixes through50; genuine field witnesses with integer Lucas prime certificates.
- Q2: exact full-sequence infimum, proof of nonattainment by field pairs, and the included critical closed-noise endpoint. This is an ideal coefficient-space theorem.
- Q3: nine conditional guarantees for the actual8,900-reading sensor, with complete tails and radii up to0.02324. The worst-case theoretical radius is unchanged.

Run from the Math repository root:

```sh
python -S research/next15_2026_09/quadratic/geometry.py
python -S research/next15_2026_09/quadratic/infinite_geometry.py
python -S research/next15_2026_09/quadratic/conditional_query.py
python -m unittest discover -s research/next15_2026_09/quadratic -p 'test_*.py' -v
```

The three mathematical consequence checkers use Python's standard library, including the preserved exact Sturm implementation used to check the old tail source. Numerical controls additionally need NumPy. The field-prime producer uses FLINT for candidate generation; every resulting primality claim is independently checked from integer modular identities.

The Q3 full source replay was performed with:

```sh
python research/five_paths_2026_09/path4_realizability/query_certificate.py --output research/next15_2026_09/quadratic/base_tail_replay.json
```

It rebuilds all497,500 finite response terms, the Gram rows, and the complete analytic remote tail using Arb at192 bits. The replay JSON equals the bound source exactly; the tests verify that equality. It writes only the new replay file and preserves the previous package.

To regenerate the three canonical new artifacts deliberately, add `--write` to the corresponding new script commands. Q1 re-creates the three actual discriminants and their recursive Lucas certificates. Q2's interval for ζ(8) uses rational partial sums and integral remainders; it does not trust a floating zeta routine. Q3 rebuilds the nine rational query cases from the verified complete tail/Gram source.

The baseline source's finite kernel evaluations are still numerical proof premises, distinct from a hash or a fast consequence check. AUDIT.md records independent field arithmetic, infinite-topology arguments, and finite query checks. None of the three claims is a hardware validation, a historical-priority claim, or a claim that full coefficient geometry equals the zeta observation metric.
