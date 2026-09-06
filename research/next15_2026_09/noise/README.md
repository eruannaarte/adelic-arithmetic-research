# Reproducing the three arithmetic-noise cycles

Start with REPORT.md, the chronological CYCLES.md, and the complete PROOFS.md. CLAIMS.json maps each cycle to its evidence. SOURCES.md distinguishes primary-method context from accepted numerical contracts. AUDIT.md, when present, is the separate independent review.

The fixed acquisition uses8,900 complex midpoint observations at spacing1/5, the original nested positive8-cosine windows, retained indices1,...,50, and the full envelope0<=a(k)<=d14(k). N3 additionally requires known a(1)=1 and exactly affine complex baseline. No baseline source files were changed.

Run these nonmutating checks from the Math repository root:

```sh
/private/tmp/math-five-paths-venv/bin/python research/next15_2026_09/noise/cycle1.py
/private/tmp/math-five-paths-venv/bin/python research/next15_2026_09/noise/cycle2.py
/private/tmp/math-five-paths-venv/bin/python research/next15_2026_09/noise/cycle3.py
OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/next15_2026_09/noise -p test_cycles.py -v
```

Expected: N1 complete-family Pareto obstruction PASS; N2 full8900-reading correction and bounded-noise rounding PASS; N3 affine baseline recovery PASS; all11 tests PASS. Typical runtime is under10 seconds total in the recorded environment. N3's standalone checker includes the complete N2 correction check and binds its verified digest. Each cycle freshly reconstructs every new finite computation required by its claim. The tests replay the new certificates at256 bits in addition to the canonical192 bits.

To regenerate only this chain's supplied outputs, add `--write` to each cycle command, in order1,2,3. This rewrites the corresponding evidence JSON and, for N2, the entire rational correction vector. N3's frozen inputs are cycle3_inputs.json. These regeneration commands preserve the earlier five-path package and original research artifacts.

The runtime is Python3.12.14 with python-flint0.9.0/FLINT3.6.0, NumPy2.5.2, and mpmath1.4.1. N1's direct covariance controls use NumPy; N2's independent evaluations use mpmath. The actual certificates use Arb outward arithmetic and exact rational endpoint inequalities.

The complete baseline finite/remote tails were fully reconstructed in the previous package and are explicitly inherited here. The new code validates their strict parameter contracts and formal bindings. Hashes establish premise identity; they do not replace the earlier full numerical verification. The recorded deep reconstruction commands are:

```sh
/private/tmp/math-five-paths-venv/bin/python research/five_paths_2026_09/path3_noise/rebuild_dependencies.py
/private/tmp/math-five-paths-venv/bin/python verify_multiscale_certificate.py --certificate certificates/arithmetic_sensing_v_multiscale_end_to_end.json --processes 4
```

The first command verifies both MPFR remote tails and the single-window finite/Gram source, and refreshes the old package's reconstruction record. Do not run it when preserving that record byte-for-byte is required. The second command nonmutatingly verifies the complete multiscale artifact. Previous recorded runtimes were394 and417 seconds. The inherited records are dependency_rebuild.json and multiscale_rebuild.json in the old path3_noise directory. These expensive unchanged premises were not relabelled as new cycles.

All bounds concern exact linear decoders with the supplied rational preprocessing. Actual hardware errors, uncertain timestamps, and finite-precision solve error are outside the certified implementation and need explicit budgets. N3's arbitrary baseline magnitude is a mathematical statement; a fixed-precision numerical implementation cannot silently inherit it.
