# Quadratic realizability and constrained queries

Read CHAPTER.md for the concise result and PROOF.md for complete statements and proofs. AUDIT.md records the independent mathematical review. P4.1 exactly characterizes finite quadratic prefixes; P4.3 certifies a(5) for all real quadratic fields at weighted noise radius0.02001, exceeding an independent-envelope collision radius0.02.

Run from the repository root with the package's pinned environment:

```sh
python research/five_paths_2026_09/path4_realizability/quadratic.py
python research/five_paths_2026_09/path4_realizability/check_certificate.py
python research/five_paths_2026_09/path4_realizability/check_certificate.py research/five_paths_2026_09/path4_realizability/refinement.json
python -m unittest discover -s research/five_paths_2026_09/path4_realizability -p 'test_*.py' -v
```

Expect27 exact witnesses, two `verified:true` results, and 17 passing controls. The checker independently proves positive weights, logarithmic mass bounds, sine denominator bounds, complete remote composition, and every rational query inequality. The finite and Gram vectors must additionally be regenerated for full model verification:

```sh
python research/five_paths_2026_09/path4_realizability/query_certificate.py
python research/five_paths_2026_09/path4_realizability/query_certificate.py --precision 256 --output research/five_paths_2026_09/path4_realizability/refinement.json
```

Each full replay sums 497,500 finite response terms with outward Arb arithmetic and reconstructs all Gram rows. Expected output includes `complete quadratic query guarantee: True`, radius `2001/100000`, and worst-case sufficient boundary approximately 0.02003156766635. Both 192- and 256-bit replays were run. Source artifacts remain separate from optional experiments; `PREREGISTRATION.md` records the fixed comparison.

The arithmetic infinitude proof relies on Dirichlet's theorem under explicitly checked coprimality hypotheses. Finite examples and passing tests alone do not prove that theorem. The certificate's numerical trust is Python-FLINT/Arb plus the inspected response kernel and exact divisor sieve; the independent checker uses standard-library integers/Fractions and the existing exact Sturm implementation.
