**Final status: complete.** Full [1,2] proof, numerical replay, independent audit and all16 controls pass; see README.md and AUDIT.md. The initial-target notes below are retained as development history.

# Path 5 progress

Target fixed before certified computation: extend the n=1001, K=2, central-target full-Neumann transfer from [1,6/5] to [1,2] in L2, continuum H1, and natural discrete H1. Compare operator error to the exact inherited Stage X late-core floors; no optimizer/minimal-grid claim. Pilot asymptotic diagnostic predicts H1 error at tau=2 about 2.26e-9 below floor 3.55e-9 (descriptive only).

New analytic device: tensorize the raw Gram product. Its generator is positive self-adjoint, so |R^(k)(tau)| <= k! / a^k on tau>=a>0. This removes the old (2M)^k majorant. With normalization sqrt(1+tau), normalized order-d Taylor remainder has an explicit rational bound after bounding sqrt(1+b). Proposed two cells [1,3/2], [3/2,2], degree18. The finite and continuum coefficients are subtracted before evaluation. Their interval endpoints will be exact dyadic rationals; a small independent stdlib checker will reconstruct Taylor enclosure, all three 2x2 spectral bounds, cover topology, and transferred floors. Generating coefficient enclosures still trusts Arb and audited base semigroup coefficient code, and will be separately reproducible.

Baseline source: oig_uniform_lattice_arb_cover.md. Exact floor provenance: oig_xi_transfer_certificate.py:55 and oig_x_spectral_certificate.md:2.2. Full proofs and hypothesis mapping pending alongside computations.

## Completed validation

- Both full cells[1,1.5],[1.5,2] passed at192 bits,order18,exponential degree64, taking58.6s and60.5s.
- Exact assembled cover passed the separate stdlib checker in all3metrics. Uniform finite floors are conservative exact rational differences; readable approximations are1.176448e-7,1.292821e-9,1.372829e-9.
- The inherited continuum floor matrices were freshly reconstructed with256-bit quadrature and exact rational principal-minor checks.
-16 focused tests passed, including independent dense Arb exponential/derivative comparison at n=7 and counterexample/boundary/tamper controls.
- The first cell was recomputed at256 bits,order20,degree72(119.8s); all171 common coefficient intervals overlap and all3error uppers improve.
- Full proof, primary sources/hypothesis mapping, main-body chapter, claim index and exact reproduction commands saved. No existing source file was edited.
