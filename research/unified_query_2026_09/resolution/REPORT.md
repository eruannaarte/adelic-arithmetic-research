# About half as many spatial channels, with the same noise budget

The prior 99-row spatial sensing bank can be replaced by **50 asymmetric rows while retaining more than 99% of each certified information floor**. A second bank uses **48 rows and retains more than 97%**. Both identify the unknown target and recover its two source coefficients under the previous deterministic noise allowances, uniformly throughout the continuous time interval. This is a new certified acquisition reduction within the declared finite model.

| Result | Prior bank | New conservative bank | New smaller bank |
|---|---:|---:|---:|
| Spatial indices | 451–549 | 476–525 | 477–524 |
| Real rows acquired | 99 | 50 | 48 |
| Reduction from 99 rows | — | 49.49% | 51.51% |
| Retained fraction of all original central source-metric floors | >99% | >99% | >97% |
| Certified centroid error at relative output noise $10^{-3}$ | <0.198181 | <0.100347 | <0.130178 |
| Relative source error under the inherited source-relative noise allowances | <$10^{-3}$ | <$10^{-3}$ | <$10^{-3}$ |

All columns use the same $n=1001$, two source modes, $g=4/5$, known time $\tau\in[1,2]$, and unknown target prior $j\in\{490,\ldots,510\}$. Retained readings keep their original normalization. The source-relative noise allowances remain $3\cdot10^{-7}\|u\|_{L2}$ or $3\cdot10^{-8}\|u\|_{H1}$, where each H1 calibration is interpreted separately. Every vector within the declared Euclidean noise ball is allowed. The comparison does not assume a physical sensor noise distribution or rescale noise after removing rows.

The advance comes from using the transverse diffusion rate directly. The earlier proof bounded the total number of graph steps, including motion along the globally averaged coordinate. The new argument assigns an exponential weight to transverse distance and differentiates the weighted state energy. It proves a bound for the complete finite evolution operator without assuming that its spatial and variable-coefficient terms commute. Separate left and right tail bounds then charge both the missing information and the missing energy first moment.

This matters because unknown-target recovery needs more than a positive source Gram. Removing readings can bias the energy centroid, even if the remaining source map is invertible. Here the new proof controls that bias for all 21 possible targets and all signed combinations of source modes. The observed centroid first identifies the target by rounding; the decoder then uses that recovered target's least-squares inverse. It never receives the true target as an input.

The source calibration also improves the transfer. A missing-output bound in L2 becomes smaller when measured against either H1 source norm. Charging that factor explicitly is what supports the 50-row, 99% guarantee. The certificate retains both the inherited placement loss and the newly proved acquisition loss.

There is also a useful necessary bound. **At least four real rows are required for exact joint recovery of an arbitrary two-dimensional source and at least two target labels.** Each label's map must have a two-dimensional image. In three real dimensions, two such image spaces necessarily intersect in a nonzero response, producing distinct target/source pairs with identical noiseless data. This applies even when each label separately has an injective source map. Four is a lower bound, not a sufficient design, and the present work does not claim 48 rows are minimal.

The result contributes directly to the proposed unified line of certified query recovery. An explicit restriction of the experiment preserves one discrete answer and an enclosure for a continuous answer, provided the missing information and the statistic used to identify the discrete answer are both bounded. An information floor alone would not establish this joint guarantee.

The exact certificate checker passes, together with eight focused tests. The producer and checker evaluate the required exponentials with different rational Taylor remainder calculations. A separate full-model replay uses the 1,002,001-state finite graph at two extreme target positions and two times; all **192** source/noise controls identify the target correctly, with source error below 0.000151. These controls check the implementation. The analytic inequalities, exact rational consequences, and inherited continuous-time Gram premise establish the uniform guarantee.

Direct acquisition savings require the indicated spatial-average readouts to be available. Computing these rows from a previously acquired full modal vector would only reduce subsequent processing. Each row continues to average globally in the other spatial coordinate. The time is known, the source has two modes, and a positive absolute noise guarantee requires a source-amplitude lower bound. Numerical rounding in a deployed inverse would need its own error allowance.

The next justified objective is a bank of **separated, individually selected rows**, with a certified separation between the complete target-dependent source image spaces. The four-row obstruction provides a genuine lower benchmark. The centroid proof cannot simply be carried over to a bank with arbitrary gaps; the next decoder must certify the resulting joint answer set directly.

[Full proof](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/PROOFS.md) · [Exact evidence](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/evidence.json) · [Reproduction instructions](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/README.md)
