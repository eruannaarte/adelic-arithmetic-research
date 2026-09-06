# Independent audit: complete polynomial drift removal

Auditor: the resolution/sensing-bank agent, independently of the polynomial producer. I read the final proof, source and numerical contracts, producer, independent checker, and tests; rederived the core bounds; ran the complete test suite and rational consumer; and performed separate complete-envelope and physical-map calculations. **Verdict: the stated quintic multiscale and quartic outer guarantees are supported under their declared assumptions. No unresolved mathematical or implementation defect was found.**

## Mathematical review

1. **The nuisance quotient preserves the actual answer set.** For an unrestricted sampled polynomial subspace and a weighted Euclidean closed noise ball, complementary orthogonal projection is an exact equivalence. The reverse direction explicitly uses the projected residual as noise and the remaining residual as nuisance. It needs the full subspace to be allowed independently of the source; that is the declared model. The fixed normalization $a(1)=1$ remains a source constraint, while the nuisance constant is unrestricted. Deterministic centering is a known invertible translation and does not add information to a fixed experiment.

2. **The polynomial columns represent the actual acquisition.** The 8,900 timestamp formula and the nested 2,550 inner samples match the previous physical model. Rescaling time to $x=t/890$ changes only the basis of each polynomial space. The Gram–Schmidt recurrence projects the monomial onto the preceding exactly orthonormal polynomials; the positive weighted residual norm is justified because the degree is below the number of distinct positive-weight points. Its parity identities and the real/imaginary cross-channel signs agree with $\Phi_{jn}=\exp(-it_j\log n)$. Both choices of weights are positive and have mass one.

3. **Every added tail channel is complete.** For the centered omitted coefficient sequence, $|a(n)-d_{14}(n)/2|\le d_{14}(n)/2$. Absolute convergence therefore bounds the full signal by
   \[
   h_0=\frac12\left[\zeta(2)^{14}-\sum_{n\le50}d_{14}(n)/n^2\right].
   \]
   Multiplying by the actual weighted absolute polynomial norm gives $h_0\ell_k$ for every new channel. This is a bound on the entire omitted sequence, with no sampled-frequency cutoff. The inherited arithmetic response bound $B_n$ contributes $B_n/(2n^2)$ before the final source scaling. The factor one half, the source coefficient normalization $n^{-2}$, and the eventual multiplication by $n^2$ are charged consistently.

4. **Schur elimination includes the coupling to the old arithmetic fit.** With $G=\Phi^*W\Phi$, $C=\Phi^*W\Psi$, and $S=I-C^*G^{-1}C$, the arithmetic tail term is
   \[
   G^{-1}\Phi^*Wh-G^{-1}CS^{-1}\bigl(\Psi^*Wh-C^*G^{-1}\Phi^*Wh\bigr).
   \]
   The proposed $v_{nk}$ bounds $|(G^{-1}C)_{nk}|$ by separating the first row of the Gram Neumann series. The matrix $M$ bounds the absolute Schur defect entrywise. Its row-sum bound below one gives the second Neumann series and the componentwise residual bound. The proof correctly includes both the direct new nuisance channel and its coupling to the inherited arithmetic bias. No independence of polynomial channels is assumed.

5. **The weighted noise gain is the actual augmented gain.** The augmented Gram is Hermitian with diagonal one. Its absolute off-diagonal row bound $Q_p$ gives a lower spectral floor $1-Q_p$ by the elementary quadratic-form inequality. The fitted map applied to weighted noise has squared norm bounded by $(1-Q_p)^{-1}$ because its product with its adjoint is the inverse Gram. The digital correction error is a pointwise complex bound, so weight mass one makes its weighted norm at most $10^{-20}$ without an extra coordinate factor. The checker requires positive bias margin before squaring the rounding inequality and tests all 49 unknown indices.

6. **The constant alias and high-degree obstruction are genuine.** The constant arithmetic column is also the nuisance constant column. The augmented matrix includes it only once; its fitted coefficient is discarded, and the externally declared $a(1)=1$ is supplied. Without that normalization the stated constant-source counterexample is exact. At polynomial degree 8,899, Lagrange interpolation on the 8,900 distinct times can absorb the response difference of two legal normalized sources. In contrast, the degree-five outer and degree-six failures are explicitly failures of a sufficient tail estimate, not impossibility claims. These distinctions are correct.

7. **Acquisition, covariance, and implementation limits remain explicit.** Inner and outer weights are added before the reused-reading covariance is squared, preserving the cross term. The two designs use different weighted noise balls; the proof does not equate them. The exact fit removes arbitrarily large polynomial coefficients, while deployed finite-precision error needs its separately stated allowance. The report properly labels the large-amplitude floating examples as diagnostics.

## Executed checks

- The independent standard-library consumer passed. It certified nine design/degree combinations: multiscale degrees one through five and outer degrees one through four. It retained the negative-margin failures rather than squaring them into positive thresholds.
- All **eight tests passed** in a fresh process. Their full producer calls reconstructed the complete correction vector, physical arithmetic Gram, polynomial moments, basis, absolute norms, cross products, and complete new nuisance envelope at 192 and 256 bits with identical exported certificates. The tests also covered physical-grid projection, reused covariance, omitted source terms, adversarial noise directions, normalization aliases, and altered certificate contracts.
- I independently reconstructed $d_{14}(n)$ through 50 by **fourteen Dirichlet convolutions of the constant-one sequence**, rather than the producer's prime-factor/binomial formula. At 256-bit Arb precision, the distinct identity $\zeta(2)=\pi^2/6$ then gave
  \[
  h_0=469.812014357583184485562292870350772465184681546250766940409177678441585082
  \]
  within an enclosure of radius below $7.1\times10^{-73}$. That full enclosure lies inside the stored outward interval. This independently checks both the omitted-envelope subtraction and the complete infinite series value.
- For both actual 8,900-row weight designs and all six degrees, I built the polynomial columns by direct weighted vector orthogonalization, formed $G$ and $C$, solved for the actual $G^{-1}C$, and formed the actual Schur matrix. All twelve comparisons respected the exported componentwise inverse-cross and Schur-defect bounds, up to the separately declared floating diagnostic tolerance. The smallest observed Schur eigenvalue was about 0.9999999999938772. This supports the proof's distinction between an accurately invertible finite fit and a conservative complete-tail gate that can still fail.
- The same twelve independent physical maps were used to project deterministic complex vectors. The projected residuals were orthogonal to the complete polynomial nuisance space, and their complementary components reconstructed the original vectors. This checks the constructive answer-set equivalence in the actual weighted coordinates.

## Trust and scope of this audit

The new model-to-enclosure reconstruction was rerun, including both working precisions. The unchanged million-term arithmetic tail bounds and their analytic remote certificates remain inherited from the previous audited package; I did not regenerate those expensive unchanged baseline tails in this audit. Their identities and parameter contracts are checked, but a digest is not mathematical evidence for an interval enclosure.

The conclusion is a deterministic recovery guarantee for the declared integer envelope, exact timing, known normalization, respective weighted noise norm, and exact augmented linear map. It establishes neither empirical apparatus performance nor a sharp maximum feasible drift degree. Within that scope, the complete nuisance-channel refinement is a substantial result: it moves the quintic multiscale sufficient bias from above one half to below 0.459148827331 and supports the declared positive sensor radius.
