# Three adaptive cycles: from a noise tradeoff to baseline-resistant arithmetic sensing

The strongest finding in this chain is a change in how the known arithmetic envelope is used. At the same8,900 physical readings, subtracting the midpoint of the complete omitted envelope increases the reference design's certified adversarial-noise radius by more than127 times. It also makes the outer-only design certify integer rounding. That additional margin then supports an exact decoder which removes an arbitrary complex affine instrument baseline, provided the source's first coefficient is known to be one. These results concern the full infinite source class, with explicit numerical correction error, rather than a finite tail surrogate.

The chain began with a less favorable question. The original multiscale design had complete bias bound0.4980274167750795, just below the half-integer rounding threshold. It used8,900 distinct observations because the2,550 inner-window samples are a subset of the8,900 outer readings. The original sufficient adversarial-noise threshold was about7.88735e-7. Meanwhile its actual target50 iid variance exceeded the outer-only variance. The source class throughout is every integer sequence satisfying0<=a(k)<=d14(k); no multiplicativity assumption is added. All newly chosen objectives and their resulting successors appear chronologically in [CYCLES.md](CYCLES.md).

## N1: retuning the original mixture cannot remove its certified tradeoff

The first objective was to improve, or rigorously delimit, the joint bias/noise behavior over every positive inner/outer mixture. The result is an obstruction for the original complete absolute-tail/Neumann certification method. Any mixture that could certify all50 coefficients must have inner weight strictly between0.0017613 and0.0020428. Throughout that entire interval, actual decoded coefficient50 iid variance exceeds the outer-only variance by a factor greater than1.00009090067766.

This is a statement over a continuous family, established without scanning a finite alpha grid. Two affine minorants retain the complete remote-tail bound and selected finite modes; their strict endpoint values and opposite slopes exclude both outside half-lines. A uniform Gram perturbation bound then controls the actual decoder. Crucially, the squared weights include the cross term caused by reusing physical observations. Omitting it would change the noise model. Independent direct-grid covariance checks agree with the proof.

The obstruction does not mean that an excluded mixture cannot recover the source. It limits the declared sufficient certificate, whose remote upper endpoints need not be attained by any actual tail. Its substantive consequence is narrower and useful: mixture retuning alone cannot escape this certification/variance tradeoff. That outcome justified changing the preprocessing rather than continuing a one-parameter search.

## N2: using the complete envelope midpoint changes the robustness regime

The original source interval for every omitted coefficient is one-sided. Its known midpoint can be removed before inversion. Absolute convergence gives the entire correction at time t as

    [zeta(2+it)^14 - sum_(n<=50) d14(n)n^(-2-it)]/2.

Every remaining omitted coefficient then lies in a symmetric interval of half the original radius. Both the finite and remote tail bounds halve, so the complete decoded bias bound halves too. This is deterministic preprocessing; its response to physical sensor noise, including the reused-reading covariance, is exactly unchanged.

The implementation supplies the full rational correction vector. It encloses the complex zeta value and retained polynomial outward, rounds each component to a multiple of10^-20, and proves total complex error below10^-20 at every reading. Conjugate symmetry covers the negative times. Rebuilding the entire vector at192 and256 bits gives identical rationals. Selected75-decimal mpmath evaluations provide independent corroboration.

After charging that correction error separately, all50 integers certify at weighted sensor radius10^-4 for the reference mixture and8*10^-5 for the outer-only weights. The reference threshold exceeds0.000100356572843797, an improvement greater than127.237 over its original sufficient threshold. The common coordinatewise error bound8*10^-5 suffices for both acquisitions. These gains require no additional source readings. They require the known envelope and its computed correction; they do not assert a sharp minimax noise threshold.

## N3: the new margin supports arbitrary affine baseline removal

The second result left enough margin to investigate a different failure mode: instrument drift too large to fit any prescribed bounded-error budget. The third objective added an arbitrary complex beta0+beta1*t to the observations. A constant baseline exactly aliases coefficient1, so the theorem explicitly assumes the common source normalization a(1)=1. Without it, the legal sources a(1)=0 and a(1)=1 become exactly indistinguishable after shifting the constant baseline by one.

For normalized sources, an augmented fit uses the arithmetic columns and a normalized linear-time column. A certified Schur complement proves invertibility and bounds the added tail leakage. This new channel receives a complete pointwise tail bound from zeta(2)^14; reusing only the old arithmetic-channel bounds would be insufficient. The resulting maximum biases are below0.258210856292 for the mixture and0.307180300807 for the outer design.

The exact augmented decoder certifies49 unknown integers, supplies the known first coefficient, and tolerates sensor radii9*10^-5 and7*10^-5 respectively. There is no magnitude bound on the affine baseline in this exact-solve theorem. A direct8,900-row example with baseline(100+37i)+(10000+2000i)t defeats the original arithmetic-only fit but is recovered by the augmented fit. All11 chain tests pass, including higher-precision reconstruction, invalid-budget controls, the normalization collision, and correction-file binding.

The full proofs are in [PROOFS.md](PROOFS.md); [README.md](README.md) gives reconstruction commands. The previously verified complete tail certificates remain explicit inherited premises. New trusted components are Arb's zeta and elementary complex enclosures. Finite-precision decoder error, especially with very large drift, still needs a deployment-specific allowance. Centering and nuisance projection are standard methods; the contribution here is their complete certified arithmetic application. The justified next question is how many higher polynomial baseline modes can be removed at the same readings and a fixed common error radius, with complete new tail channels and explicit normalization boundaries.
