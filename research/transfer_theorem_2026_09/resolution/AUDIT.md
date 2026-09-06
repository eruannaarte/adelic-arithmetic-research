# Independent audit of the spatial model transfer

**Accepted within the stated finite diffusion model.** Independent proof review and a separate model calculation support the bridge from the full finite experiment to the rational polynomial maps. No central mathematical defect was found. The published physical operator allowance remains \(\rho=10^{-9}\), and the stated three source/noise calibrations remain unchanged.

The separate audit implementation is [independent_audit.py](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/resolution/independent_audit.py), with exact bounds and source hashes in [independent_audit.json](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/resolution/independent_audit.json). It imports neither the spatial producer nor its consumer. The complete 895-record case/cell verification belongs to the separate [check.py](/Volumes/KINGSTON/Vibecoding/Math/research/transfer_theorem_2026_09/resolution/check.py) job; this bounded audit does not duplicate those translations.

## Model and complete approximation bounds

The Fourier surrogate retains the exact 1,001-vertex \(x\) path, including endpoint degree one and the varying diagonal potential. Its mode generator is the full matrix \(L_x+\omega V\). The code does not interchange \(L_x\) and \(V\), which do not commute. Their spectral lower and upper bounds justify the shifted exponential center/radius and all derivative-coefficient remainder multipliers. Projection onto the unit constant output vector and each unit cosine source column has the required norm one.

The transverse zero Fourier mode vanishes by an exact identity: the finite path preserves constants, and each of the two midpoint cosine sources has zero mean. Its omission is valid for these source columns; it would be false for a constant source. Opposite nonzero modes and the Nyquist mode have the correct finite-Fourier weights.

The complex Laurent argument bounds the entire image sum, including both directions and every multiple of the period. The Hermitian-part estimate is valid despite the non-Hermitian complex matrix on the displaced contour. It needs only the positive semidefinite path Laplacian and the upper potential bound \(9/5\). Summing the geometric image tails at maximum displacement 26 gives exactly the exponents 38 and 90 used in the certificate. A separate rational exponential remainder check confirms the image bound below \(10^{-24}\).

Uniformization at rate \(28/5\) is valid for the full finite and infinite transverse generators: their transition operators are nonnegative, symmetric and contractive. At distance 490, a walk first reaches a boundary in 490 steps; its next step encounters the changed diagonal or crosses the edge. Thus agreement through degree 490 and the tail beginning at 491 are correct. The separate exact factorial/geometric calculation confirms the complete finite-boundary bound below \(10^{-500}\). No physical periodicity is assumed.

The degree-32 time expansion covers every real known time in \([1,2]\). The positive semidefinite spectral estimate for the 33rd derivative and Taylor's integral remainder justify \(2^{-33}\) uniformly, including expansion to the left of the center. Coefficient interval radii and outward rational midpoint rounding are charged separately. The conversion from entry bounds to the two-column, eleven-row operator uses the correct Frobenius factor \(\sqrt{22}\) and the physical normalization upper bound \(4/3\). Consequently \(\rho\) is already a bound on the normalized physical map.

## Independent numerical and exact controls

The audit recomputes 16 selected coefficients of the full 1,001-vertex \(x\) model, covering displacements 0 and 26, both source columns, and Taylor orders 0, 1, 16 and 32. All 32 nonzero Fourier representatives are included. Instead of the producer's degree-80 shifted expansion, it uses degree-160 positive uniformization:

\[
e^{-cA}=e^{-cq}\sum_{h\ge0}\frac{(cq)^h}{h!}(I-A/q)^h,
\qquad q=4+(9/5)\omega.
\]

The spectral bounds give \(0\le I-A/q\le I\). A complete first-omitted-term/geometric bound controls the positive-series tail, and each subsequent derivative receives its own propagated error allowance. At 256-bit outward precision, every independently reconstructed coefficient enclosure lies inside its saved interval. This is a bounded independent reconstruction, not a claim that all 1,782 stored coefficients were reconstructed by a second algorithm; the producer's complete replay is a separate job.

A rational small-graph control compares embedded finite and extended walk powers for all three source coordinates. All 15 equalities through distance four hold exactly, and the first discrepancy occurs at step five. A separate dense finite-cycle calculation checks 48 response entries over three times against the complete Fourier construction, with discrepancy below \(10^{-12}\). It also checks the exact-zero-mode formula numerically, verifies a nonzero constant-source control, and rejects commuting the two generator terms. These floating checks are diagnostics alongside the analytic proof.

## Independent margin and calibration checks

An additional analytic bound confirms that the published operator budget has margin. For \(s\ge1\), the maximum of \(\lambda^{33}e^{-s\lambda}\) is attained at \(\lambda=33/s\). Since the positive exponential series proves \(e>8/3\), the time remainder is at most

\[
\frac{(99/16)^{33}}{33!}<1.51816\cdot10^{-11}.
\]

Combining this with the same complete image, boundary and rounding allowances gives an exact physical squared operator bound below \(10^{-20}\). Thus an audit-only \(10^{-10}\) radius is also justified. The published \(10^{-9}\) radius and every downstream guarantee are deliberately kept unchanged; no new optimization or row search uses this sharper estimate.

Both H1 source metrics satisfy \(I\le S\le41I\). Whitening therefore divides individual and pair floors by at most 41, while the model allowance is unchanged. The audit independently checks all three pair-separation and source-inverse inequalities, including the optional \(10^{-9}\) computed-data allowance. It also verifies that the enlarged Euclidean tubes used by the rational H1 interface remain pairwise disjoint. Known normalization is handled consistently in that interface. No extra final-solve error may be silently added: the provided rational decoder solves exactly, while a different numerical implementation needs its own valid error accounting.

## Reproduction and limits

This command rebuilds and verifies the independent audit record:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/resolution/independent_audit.py
```

It was run successfully with Python 3.12.14, python-flint 0.9.0 / FLINT 3.6.0, NumPy 2.5.2 and SciPy 1.18.1. The source hashes bind the reviewed model, proof, coefficient and case certificates. Interval arithmetic is a trusted numerical component; a matching hash alone is not a model proof.

The theorem concerns eleven directly acquired global \(x\)-averages in the declared finite spatial model, with exact known time and nonzero source. It does not establish eleven fully local detectors, unknown-time robustness, spatial-continuum convergence, an optimal row count, apparatus feasibility, or that an arbitrary floating implementation meets the conditional error allowance. Continuous-time and all-source guarantees come from the complete analytic and cell proofs, not the forward examples.
