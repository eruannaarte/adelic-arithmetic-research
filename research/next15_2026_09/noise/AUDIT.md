# Independent audit of the three arithmetic-noise cycles

Auditor: `/root/review_oig`, 2026-09-05. **Verdict: all three mathematical results and their numerical certificates are supported under the stated premises.** The review found and coordinated two hardening improvements: a positive uncentered-margin guard before the N2 gain calculation, and validation/binding of the complete N2 correction vector inside standalone N3 reconstruction. Both were repaired without changing scientific bounds. No unresolved certificate defect remains.

## N1: complete-family obstruction

The theorem in [PROOFS.md](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/noise/PROOFS.md:11) is correctly about the specified complete absolute-tail/Neumann **certificate functional**. Its prescribed positive remote upper bound is part of that functional; it is not being claimed as a lower bound on the actual tail. Dropping unselected nonnegative finite terms and applying fixed signs to the selected responses gives legitimate affine minorants. Strict endpoint exclusion with a negative left slope and positive right slope excludes whole half-lines. Thus the necessary interval covers every admissible mixture, rather than only sampled weights.

The variance proof uses the actual reused-reading covariance. The cross product between the inner window and its zero-extended outer-grid representation is included. Exact finite Fourier orthogonality gives each mass and squared norm. The positive derivative of squared weight mass and the affine Gram perturbation bound apply uniformly over the entire closed necessary interval. The rowwise Neumann estimate bounds actual decoder rows in Euclidean norm, with the lower bound properly requiring delta < 1. Dividing the mixture lower variance by the outer upper variance proves the stated strict comparison for coefficient 50. The covariance convention is complex variance under mean-zero physical errors with covariance sigma² I; Gaussianity is unnecessary here.

Independent controls, beyond running the supplied tests:

- Rational interval reconstruction from the exported response endpoints gives exclusion values greater than 0.50000149419 and 0.50000279582, with the required slope signs. Removing the remote term leaves only about 0.0120473 and 0.0117434, illustrating why the method-specific scope matters.
- Independent arithmetic on the rounded exported statistics proves a uniform variance ratio greater than 1.00009090067765. The native producer retains an unrounded Arb endpoint and proves the slightly sharper printed bound greater than 1.00009090067766.
- A separate 192-bit Arb implementation summed the physical midpoint grids directly, without the closed response kernel. All 28 selected responses and the reused cross product were enclosed; all 11,450 component weights were positive.

The already certified reference mixture lies strictly inside the necessary interval and has complete bias below one half, so nonemptiness is supported. The obstruction does not establish actual recovery impossibility or an optimum over different decoders.

## N2: full infinite-envelope centering

The [full correction construction](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/noise/cycle2.py:9) and proof correctly use absolute convergence to expand zeta(s)^14 into the d14 Dirichlet series. Subtracting the retained polynomial makes the correction exactly the midpoint of the entire omitted envelope. Both finite and remote bias bounds therefore halve. The 4,450 stored positive-time rational entries and reversed conjugates cover exactly the original 8,900 measurements.

Each squared complex-error gate includes the special-function enclosure, finite-head evaluation, and exact rational rounding. This proves the strict 10^-20 pointwise correction allowance. Probability-weight mass turns it into a weighted error allowance, which is added to the sensor radius before the exact all-coefficient rounding inequalities. The weighted metrics differ between designs; the common coordinatewise bound stated in the proof is correctly valid for both. Deterministic preprocessing leaves the physical-noise linear response and covariance unchanged.

I independently recomputed all 50 rational inequalities for each design. The limiting target is 50 in both cases. The declared radii 10^-4 and 8e-5 leave margins above 0.0008917691509 and 0.0019324290498. The full correction vector reproduces at 192 and 256 bits; the suite also checks three separated times with 75-decimal mpmath arithmetic.

An additional independent full-grid diagnostic used the allowed zero-envelope source and physical noise aligned to coefficient 50's actual weighted decoder row. All coefficients rounded correctly for both designs. The largest complex coefficient errors were approximately 0.2507130 and 0.2508663. This illustrates the actual acquisition and error metric; it is not a proof substitute.

The new numerical trust component is Arb's complex zeta enclosure. Its role matches the [primary algorithm paper](https://arxiv.org/abs/1309.2877) and [official FLINT documentation](https://flintlib.org/doc/acb_dirichlet.html). This audit does not independently reimplement that special-function algorithm.

## N3: affine baseline and normalization boundary

The [block-inverse proof](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/noise/PROOFS.md:118) correctly uses a unit-weighted-norm time column. Symmetry makes its constant cross term zero and its other arithmetic cross terms imaginary. The rowwise inverse-cross bounds imply the stated positive Schur complement. Crucially, the new nuisance channel uses the **complete unwindowed** centered-tail envelope, bounded by about 469.8120143576. Cauchy–Schwarz and the Schur formula then give the extra bias term; using only the old arithmetic-channel tail bounds would have been insufficient.

The first fitted coefficient is 1 + beta0, not a recovered arithmetic value. The algorithm supplies a1 = 1 from the explicit normalization and certifies the other 49 coefficients. The two legal sources with a1 = 0 and a1 = 1, paired with compensating constant baselines, prove the exact obstruction without that normalization. The arbitrary affine drift is removed in the exact linear model; finite-precision errors can depend on its amplitude, as the proof expressly states. The changed N3 decoder does not inherit N2's unchanged-covariance claim.

Independent verification reconstructed all 100 nuisance cross products as full 8,900-row complex Arb sums at 256 bits. An independent divisor convolution and the pi²/6 identity reproduced the complete real tail enclosure. Standard-library rational arithmetic reproduced both Schur bounds and every unknown-coefficient noise gate. Six additional full-grid augmented-decoder controls, using three affine-drift amplitudes per design and weighted adversarial noise, rounded correctly; the largest tested baseline magnitude was about 3.22e7. These numerical examples support the stated model while leaving unbounded-amplitude machine arithmetic outside the claim.

## Reproduction and residual trust

The complete 11-test suite passes after hardening, including all three 192/256-bit reconstructions, full correction replay, independent covariance/physical-grid controls, strict-boundary failures, normalization and nuisance-contract failures, and rejection when N2 correction validation fails. Standalone N3 now rebuilds N2's supplied correction, checks its error budget, and records its validated digest.

The unchanged finite sums through 10^6 and MPFR remote bounds are inherited explicitly from the previously reconstructed five-path package. This audit rechecked their formal projection/parameter bindings but did not repeat those expensive unchanged producers. Every new finite response, weight, Gram/cross bound, correction value, and derived consequence was freshly rebuilt. Hashes identify premises; they do not prove them. Trust remains in the analytic arguments, outward Arb/MPFR arithmetic, and exact rational consequences, not a proof assistant or hardware validation.

The three cycles contain distinct advances: a family-wide certificate obstruction, complete envelope centering, and recovery under an unbounded affine nuisance with an exact identifiability boundary. Their changed assumptions and retained limits are explicit, and no historical novelty claim is needed for these verified applications.
