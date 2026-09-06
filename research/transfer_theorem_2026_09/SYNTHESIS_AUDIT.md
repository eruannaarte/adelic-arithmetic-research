# Final cross-synthesis review

Status: **PASS.** The final framework and application claims, shared adapter, independent audits, root reproduction guide and current-state index agree on their mathematical scopes. No unresolved substantive defect was found. The root's consolidated verification record separately reports actual execution of the full package; this review does not anticipate an unfinished run's outcome.

This review checks the final claims against their mathematical scope, source/noise normalization, executable interfaces and evidence. The reviewer developed the arithmetic application, so its independent physical validation is attributed to the separate [noise audit](noise/AUDIT.md). The general theorem received the separate [framework review](framework_review/REVIEW.md). The synthesis review does not relabel an author's own code checks as independent scientific validation.

## 1. The common theorem and the claimed contribution

Theorem A gives the attained minimum squared physical-noise cost after restriction and elimination. In whitened coordinates it is the squared norm of the projection onto the intersection of the retained row space and the orthogonal complement of the unrestricted nuisance range. The lifting construction supplies reverse compatibility, so the result is equality of answer sets under the declared unrestricted-nuisance contract. Bounded or state-correlated coordinates remain in the actual joint source/uncertainty set.

The operation-order condition is distinguished from reconstructing the full quotient. The query-specific theorem uses saturation only on the promised observation domain. Approximation supplies containment unless a separate reverse lifting or equality condition is proved. This matches the root report's distinction between a singleton certified answer and an inconclusive outer answer set.

The complete directional-error formula propagates a shared primitive through the actual stage operators before taking supports. It does not invent independent copies of reused measurements. The compact-convex directional result has its required convexity and compactness assumptions; the report does not transfer this completeness claim to a convexified nonlinear query union. The nonzero-source block-map theorem treats all source directions and uses strict pair margins. The supplied lower-channel bound is a necessary benchmark for unrestricted joint source/label recovery, not a sufficiency result at four channels.

The general linear algebra and optimal-recovery ideas are explicitly identified as classical. The project's local contribution is the integrated exactness and error-transfer contract together with model-derived certified consequences. Neither the number of example witnesses nor the number of checked scalar inequalities is presented as a count of novel theorems.

## 2. Arithmetic claims and their transfer interface

The detailed [application audit](framework/APPLICATION_AUDIT.md) verifies the common map for the new coefficient bounds. In the n-th integer coordinate the native bias is A_n, the augmented Gram floor is f, and the physical noise gain is n^2/sqrt(f). The common scalar gate uses spacing one, support sum 2*A_n, gain squared n^4/f, and the combined sensor-plus-digital radius eta+Xi. Its minimum exact rational boundary equals the native certificate.

An exact-model normal residual of Euclidean norm at most rho contributes n^2*rho/f to that integer coordinate. The adapter adds it to the bias before doubling the support sum. This correctly distinguishes inverse-Gram solve error from the inverse-singular-value observation error. All eight cases allow rho=10^-8 jointly with their declared sensor allowance and Xi=10^-20. This is an implementation acceptance contract; an arbitrary floating residual is not its own verification.

The degree table matches the evidence. Multiscale degrees six and eight retain eta=10^-4, and ten and twelve retain 9.9*10^-5. Outer degrees six, eight and ten retain 8*10^-5, and twelve retains 7.9*10^-5. The earlier centered no-drift allowance comparison was checked directly against its saved exact evidence. The polynomial theorem's known-a(1) hypothesis remains explicit. Each weight vector retains its own physical noise ball; the table is not an uncalibrated stochastic comparison.

The full zero-extended second differences retain both endpoints and nested-window transitions. The finite phase range concerns log(n) with 51<=n<=10^12, and every higher coefficient is included through the complete zeta moment bound. The failed earlier degree-six sufficient bound is accurately described as a limitation of that enclosure. Sharper bounds and known centering are not described as an increase in true experimental information. No maximal degree or optimal noise threshold is asserted.

The separate noise auditor rebuilt the physical channels at 320 bits and proved a coarser independent rational zeta upper bound. All 392 coefficient gates, including the residual allowance, remain valid under those independently rounded premises. The producer's 192/256-bit reconstruction and ten adverse tests support, rather than replace, the uniform proof. The unchanged million-term arithmetic-tail enumeration remains explicitly inherited and hash-bound.

## 3. Spatial adapter: normalized operator error and source metrics

The native spatial consumer checks 21 individual maps and 210 pairs, with a separate complete time cover for each case. The saved bank contains the eleven indices

    485, 488, 491, 494, 497, 500, 503, 506, 509, 512, 516.

The 895 whole-cell records occur in 46 time-cell entries. These counts were independently read from the certificate; the union of different cases' time cells is not used as a substitute for each case's own cover.

The approximate physical map is alpha times the unnormalized polynomial map. Its Gram floors are therefore

    mu = (19/16)^2 * 7*10^-8,
    lambda = (19/16)^2 * 10^-11.

The model error rho=10^-9 already includes the upper normalization factor, the Frobenius conversion over the eleven rows and two source columns, and the four stated approximation sources. The common adapter correctly does not multiply rho by alpha a second time.

For either H1 calibration, I<=S<=41I. Source whitening divides the individual and pair floors by 41. The same rho remains a valid operator bound from the S source norm because S>=I. Both H1 calibrations retain separate names and sensor contracts even though this conservative upper comparison gives the same displayed transfer margin.

The adapter adds the conditional computed-data allowance xi=10^-9 to rho and the appropriate sensor radius before applying the pair and inverse inequalities. Thus delta=3.02*10^-7 for L2 and 3.2*10^-8 for either H1 calibration. Independent exact rational calculations verify

    lambda/factor > 2*delta^2,
    delta^2 < (0.000962)^2 * mu/factor,

with factor one or 41. The corresponding source-error ratios lie in [0.000961223333,0.000961223334] for L2 and [0.000652167674,0.000652167675] for either H1 calibration. These are sufficient bounds, not sharp attainable errors.

The strengthened 0.000962 bound includes model and computed-data error and assumes an exact final inverse. Any separately certified inverse-computation error must be added to it. The root report was clarified to say this explicitly rather than suggesting an unallocated solve error is already included.

## 4. Acquisition, decoder and validation boundaries

The reduction from 48 to 11 direct channels is 925/12 percent, displayed as 77.08%; the reduction from 99 is 800/9 percent, displayed as 88.89%. Each channel remains a global average in the other spatial coordinate. Computing the eleven values from a full acquired vector is post-processing and does not reduce physical acquisition. The report preserves this distinction.

The exact rational decoder has no true-target argument. It tests candidate source-image feasibility and then uses ordinary least squares for the surviving target, rather than reporting the feasibility minimizer as the source estimate. Its conservative Euclidean enlargement for the H1 feasibility test is justified by the same factor-41 pair inequality. Zero data are excluded under the nonzero-source contract; incompatible and multiple-feasible cases are handled explicitly.

The executable time and normalized-data interface is rational. The uniform theorem covers every known real time in [1,2], but the implementation does not certify unprovided timing error or arbitrary normalization rounding. The conditional computed-data allowance is available for a separately verified implementation. No physical apparatus or empirical noise distribution has been validated.

## 5. Evidence counts and historical preservation

The common arithmetic adapter was run successfully in its extended mode. It reproduces 243 previous quadratic pair gates, 441 previous polynomial-coordinate gates and three previous preparation rows, totaling 687. It adds 392 new polynomial-coordinate gates and 392 additional conditional normal-residual gates. The spatial adapter checks three separate metric contracts, each with its pair and source-inverse consequence, after the native consumer supplies all 231 covered source-map cases. These distinct counts should not be conflated.

All **279** files listed in `PREVIOUS_ARTIFACTS_SHA256.json` independently match their recorded identities. This proves preservation of the listed historical artifacts, not their mathematical validity. The new work is isolated in this package; the current-state index may point to it without rewriting the earlier research record.

## 6. Final spatial audit and reproduction record

The final [spatial audit](resolution/AUDIT.md) independently accepts the full-model analytic bridge. It checks the noncommuting finite-x generator, exact zero Fourier mode, every periodic image, the first finite-boundary discrepancy at step 491, complete continuous-time remainder, physical normalization, and H1 source calibration. Its separate positive-uniformization algorithm reconstructs 16 selected full-model coefficients, covering both source modes, endpoint displacements and several derivative orders. This is accurately distinguished from a second reconstruction of every coefficient: the complete 1,782-coefficient replays remain separate producer jobs. Additional small-model and factorial controls check the analytic assumptions.

The audit derives a stronger auxiliary operator estimate but deliberately leaves the published rho=10^-9 and all downstream guarantees unchanged. The root report uses the published allowance. Neither the root nor spatial report transfers the earlier 97% information-floor retention claim to the new eleven-row bank; the retained claim is the original noise allowance and source-accuracy target.

The spatial producer records nine tests, complete 192/256-bit coefficient equality and 27 full finite-grid diagnostic cases. The latter use 1,002,001 states and are labeled floating regression evidence, not uniform proofs or certified implementation-error budgets. The exact rational decoder's inverse introduces no solve rounding; other solvers need their own error contract.

The final root reproduction guide correctly specifies **15 full jobs**, **7 quick jobs**, and **31 focused tests** divided 12/10/9 across the framework/arithmetic/spatial suites. The full job list includes both new physical reconstructions, the independent audits and the 27 finite-grid diagnostics. The quick mode omits those expensive reconstructions and is explicitly conditional on saved numerical premises. The wrapper checks subprocess outcomes and expected test counts, preserves previous artifacts, and writes only its requested report and log; the forward diagnostic's regeneration switch is explicit and is not used by the wrapper.

`MATH_CURRENT_STATE.md` points to the new version while retaining the earlier five-path, fifteen-cycle and unified records. It preserves the previous harmonic obstruction, conditional quadratic gains and unverified physical preparation status. Its current arithmetic and spatial headlines match the proved source restrictions, measurement counts and error budgets. The public ledger is allowed to lag; no publication or conversation rewrite is claimed.

The authoritative consolidated outcomes are [VALIDATION.json](VALIDATION.json) and its sibling log. The separately observed mathematical checks and audit results above pass; the consolidated run's completion is recorded there rather than inferred from this synthesis review.
