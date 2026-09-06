# Higher polynomial drift at the same 8,900 readings

The arithmetic acquisition now has a certified decoder for **arbitrary quintic instrument drift**, while retaining all 49 unknown coefficients through index 50. The multiscale design supports weighted sensor noise \(\eta\le1.6\times10^{-5}\). The outer window supports arbitrary quartic drift with \(\eta\le3.3\times10^{-5}\). Both statements require the known normalization \(a(1)=1\), the same declared integer coefficient envelope, and an exact augmented linear solve. The drift coefficients can be arbitrary complex numbers.

The earlier result removed affine drift. The advance here is a general multiple-channel Schur bound and a complete bound for every new polynomial tail channel. The polynomial basis is orthonormal in the actual physical sampling weights. Its weighted absolute norms sharpen the old unit-norm tail estimate. That refinement changes the multiscale quintic sufficient bias bound from above 0.5541 to below **0.459148827331**, crossing the one-half rounding threshold.

| Maximum drift degree | Certified multiscale noise radius | Certified outer noise radius |
|---|---:|---:|
| Affine | 0.000097 | 0.000077 |
| Quadratic | 0.000090 | 0.000070 |
| Cubic | 0.000077 | 0.000057 |
| Quartic | 0.000053 | 0.000033 |
| Quintic | 0.000016 | Sufficient gate fails |
| Degree six | Sufficient gate fails | Sufficient gate fails |

These are declared sufficient radii, not sharp statistical or minimax thresholds. Each column uses its respective positive weighted norm; the physical error balls differ. A common pointwise bound implies the corresponding weighted bounds. All 8,900 samples are reused exactly as before, including the inner/outer covariance cross term. The offline basis construction and augmented fit add computation, not observations.

This path also gives an exact instance of the unified answer-set principle. Let \(P\) project onto the weighted orthogonal complement of all allowed sampled drift polynomials. A source is consistent with the observation and an arbitrary allowed drift precisely when its projected discrepancy has norm at most the sensor radius. The reverse direction explicitly allocates the projected discrepancy to noise and the remaining discrepancy to drift. Nuisance elimination therefore preserves the exact answer set for this model; the finite centered-tail calculation then provides a rigorous enclosure small enough to round. Known deterministic centering improves the decoder's certificate while leaving the fixed experiment's information unchanged.

The complete infinite tail remains essential. Each new nuisance channel is bounded by the full centered envelope \([\zeta(2)^{14}-\sum_{n\le50}d_{14}(n)/n^2]/2\), multiplied by the actual weighted absolute polynomial norm. Reusing only the old arithmetic-channel tail bounds would leave a gap. The original finite arithmetic tails and remote certificates are explicitly inherited; every new basis, moment, cross sum and complete nuisance bound is reconstructed.

There are two genuine identifiability boundaries. Unknown \(a(1)\) aliases an arbitrary constant baseline exactly. Even when \(a(1)=1\) is known, polynomial degree 8,899 can interpolate every 8,900-point response difference, so the acquisition cannot support unrestricted nuisance complexity. In contrast, the low-degree failures in the table are failures of the present sufficient tail bound. They do not establish that a better decoder or certificate could not recover.

The new polynomial and full-correction certificates reproduce at both 192 and 256 bits. A separate standard-library checker verifies exact Schur and strict rounding consequences. Eight tests cover full-grid basis and cross products, all declared degrees, adversarial weighted noise, larger drift amplitudes, omitted source modes, projection consistency, reused covariance, normalization aliases, and tampering. The direct examples use baseline polynomial coefficients of order \(10^8\); the inherited affine-only fit fails on at least one such higher-degree example while the new fit rounds correctly. Those examples are diagnostics, not a proof of finite-precision performance for unlimited amplitudes.

The next focused objective is to replace the constant pointwise tail envelope in the degree-six nuisance channels with sharper complete oscillatory channel bounds. This could decide whether the present degree limit reflects only the enclosure. A practical implementation would separately certify solve error and allocate a budget for nonpolynomial drift residuals. No hardware noise distribution or drift law has been empirically validated here.

[Full proofs](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/noise/PROOFS.md) · [Reproduction guide](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/noise/README.md) · [Evidence](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/noise/evidence.json)
