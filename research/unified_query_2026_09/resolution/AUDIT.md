# Independent audit: smaller asymmetric sensing banks

Auditor: `/root/polynomial_drift`, 2026-09-05. **Verdict: the 50-row and 48-row guarantees are supported by the stated model, proofs and certificates. No mathematical or certificate defect was found.** The comparison preserves the observation normalization, the target prior, and the separate calibrated source metrics. Direct acquisition of the indicated spatial averages remains an explicit physical requirement.

## Weighted finite-generator argument

The exponential conjugation acts on the actual finite graph generator \(H=I\otimes L_x+L_y\otimes V\), with variable \(V\). It does not commute \(L_x\) and \(V\). In the Hermitian part of the conjugated transverse edge, the off-diagonal coefficient is multiplied by \((a+a^{-1})/2\). The displayed edge inequality is valid for complex vectors as well as real ones; counting at most two transverse edges per state gives precisely the penalty \(v_*(a+a^{-1}-2)\). The derivative of the squared norm supplies the factor two. Combining \(v_*=9/5\), \(\tau\le2\), and \(\alpha^2=\sqrt{1+\tau}<2\) yields the reported \(2\exp((36/5)(a+a^{-1}-2))\) bound. Endpoint degree one improves this argument.

As an independent control, I assembled the graph from individual edges on four source-coordinate cells and eleven transverse cells. For each of \(a=4\) and \(a=9/2\), I formed the exact rational Hermitian part of the conjugated generator and added the claimed scalar penalty. Every row is strictly diagonally dominant with positive slack: the minimum slacks are \(9/40\) and \(49/180\), respectively. This establishes the corresponding energy inequality for every source direction in that finite control, rather than only the twelve sampled vectors in one supplied test. The general proof uses the same edge inequality and is dimension independent.

## Tail, calibrated information, and unknown-label recovery

The missing-energy bound uses separate positive and negative exponential weights, so asymmetric left/right distances are handled correctly. The first-moment estimate follows from the stated decreasing sequence \(d a^{-2d}\), with its ratio condition checked for every allowed target. The maximization covers all 21 discrete labels. Time and source direction are controlled by the analytic energy inequality rather than sampled numerical cases.

I separately evaluated both exponential factors with 192-bit Arb arithmetic and verified every one of the 21 energy and first-moment bounds against the exported rational bounds. This is independent of the producer's degree-160 and consumer's degree-180 positive Taylor sums. The full-grid boundary moment was also reconstructed exactly from its factorial expression; its value is approximately \(8.77234\times10^{-592}\), comfortably below the declared \(10^{-400}\).

The Gram-loss identity is positive semidefinite before whitening. Dividing the L2 loss by a lower bound on the source metric is the correct calibrated transfer. The lower bounds \(S_1,S_2\succeq9I\) follow from the supplied elementary sine and \(\pi>3\) estimates; the discrete first-mode inequality is correct. The resulting retained fractions of the original central floors are at least approximately:

| Rows | L2 | Declared H1 | Natural discrete H1 |
|---|---:|---:|---:|
| 50 | 0.9998323 | 0.9960679 | 0.9962971 |
| 48 | 0.9974117 | 0.9715934 | 0.9732489 |

Thus the common 99% and 97% guarantees are correctly charged for both prior placement loss and new acquisition loss. The centroid proof subtracts the missing first moment and divides by the retained energy floor. Its noise calculation uses the retained index diameter, not the original 1,000-cell diameter. The exact total centroid bounds are below 0.100347 and 0.130178 cells, both strictly below one half. This proves the label query before choosing a target-dependent inverse; the decoder does not receive the true label.

The source inverse is specifically the full-column-rank least-squares inverse. The identity \((AS^{-1/2})^\dagger=S^{1/2}A^\dagger\) is valid here and gives the claimed calibrated gain. Each source-relative noise allowance separately implies the required relative output bound and the source-error target. No fixed absolute noise allowance is silently asserted for arbitrarily small source amplitudes.

## Genuine obstruction and acquisition scope

The lower bound of four real rows is valid for the stated union of unrestricted two-dimensional real source spaces. With fewer than four rows, two rank-two label images intersect nontrivially, giving distinct labels and nonzero source preimages of identical data. This is an actual noiseless obstruction. It does not establish that four rows suffice, that 48 is minimal, or the same lower bound under a known source norm or discrete alphabet.

The reduction from the prior 99 rows to 50 or 48 is correctly described as an acquisition reduction only if these spatial-average readings are directly available. Reconstructing those rows from a complete previously acquired modal vector is post-processing. Each row remains a global average in the source coordinate, and off-center odd transverse modes are retained in the model. Known time, the 21-cell placement prior, two source modes, and the Euclidean observation norm remain essential assumptions.

## Executed validation and residual trust

Both standard-library exact jobs passed, and all eight focused tests passed. I also reran the 192-case full 1,002,001-state graph diagnostic. Every blind label and source recovery check passed for the two extreme labels, two times, two banks, eight source directions, and three noise directions. The largest source error was below 0.000151. These finite floating controls corroborate implementation behavior; the energy, tail and centroid proofs establish uniformity in time and source direction. The independently recomputed auxiliary quantities are recorded in [independent_audit_checks.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/independent_audit_checks.json).

The new exponential and rational consequences were freshly reconstructed. The original central continuous-time Gram and finite-generator calibration premises retain their earlier audited numerical status and are bound through the inherited checkers. This audit did not relabel those unchanged premises as new proofs. There is no claim of empirical apparatus validation or a certified finite-precision deployed inverse.
