# Path 5 claim-to-evidence index

| Claim | Status | Evidence / exact scope |
|---|---|---|
| The previous certificate covered n=1001,K=2,tau∈[1,6/5] | Historical baseline | Root `oig_uniform_lattice_arb_cover.md`; current wider result includes that interval |
| The inherited continuum L2 and H1 floor premises are positive and apply for all tau≥1 | Fresh computational certificate + analytic density-domination derivation | `baseline.json`; `revalidate_baseline.py`; Appendix§4; exact2×2 principal-minor validation |
| A normalized PSD-semigroup Gram has the generator-norm-independent remainder(4) | Proved analytically | Appendix§2, including unit source/observation norms, tensor product, total positive weight and continuum multiplication hypotheses |
| New remainder is over10^8 times smaller than the old majorant on[1,1.5],d=19 | Computationally certified comparison of explicit bounds | `test_remainder_improvement_is_rigorous`; no empirical convergence inference |
| Full n=1001,K=2 Neumann error is below the small inherited information floor for every tau∈[1,2] in all3 metrics | Computationally certified continuous theorem | `certificate.json`, model-to-Arb generation, Appendix§§3–5, independent rational `check_certificate.py` |
| Uniform error bounds are respectively2.550715019124e-8,2.259489034e-9,2.17948059475e-9 | Exact rational upper bounds | `certificate.json.uniform_bounds`; decimals printed here are terminating representations of the rational chosen upper witnesses |
| Uniform finite floors exceed1.1764481493014326e-7,1.2928209881039934e-9,1.3728294273539934e-9 | Exact rational difference certificates; displayed decimals approximate | Use exact `floor_lower` fields, or conservatively rounded Chapter table; do not treat display rounding as outward |
| Small-grid finite Taylor coefficients and derivatives agree with a distinct dense Arb exp path | Independent algorithmic control | `test_small_grid_dense_exponential_independent_derivatives`; n=7, centre5/4, orders0–3 |
| Refinement is consistent with canonical coefficient intervals and tightens the bounds | Independent precision/order/degree repetition, same underlying Arb library | `refinement_validation.json`; source regeneration at256 bits,order20,degree72 compared to192 bits,order18,degree64 |
| Negative/nonnormal generators, unnormalized sources, a=0, growingK or displaced targets are not covered | Proved boundaries / explicit counterexamples | Appendix§6 and focused controls |
| Fixed n cannot satisfy a positive continuum-to-finite floor on the entire late half-line | Analytic obstruction | Appendix§6.4: every retained finite mode exponentially decays; continuum floor remains positive |
| A failed sufficient transfer test implies finite singularity or minimal required n | Not claimed; false in general | Appendix§6.6 provides a positive finite-matrix counterexample |

## Before / after

Before: one degree-18 Arb time cell of radius1/10 certified[1,1.2], with a derivative majorant involving the generator norm. A wider interval was explicitly an unclosed next target.

After: a complete norm-independent normalized-Gram remainder corollary, two degree-18 cells of radius1/4, freshly revalidated continuum premises, a coefficient-bearing certificate for[1,2], and a separate stdlib rational consequence checker. This is a fivefold increase in certified interval length at unchanged n and K. Both metrics, target symmetry, all 500 active modal outputs and the full noncommuting generator remain declared exactly.

## Remaining obligations outside the claim

No literature-priority claim, minimal-grid theorem, growing-band theorem, target-placement robustness, or actual noise/hardware model is established. Arb ball implementation and quadrature are trusted numerical components. The small checker accepts coefficient enclosures as premises; full model verification requires regenerating them, not simply trusting JSON hashes. Primary sources and their checked hypotheses are in Appendix§7.
