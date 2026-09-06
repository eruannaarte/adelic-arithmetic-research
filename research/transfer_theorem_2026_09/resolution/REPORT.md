# Eleven separated spatial rows suffice for joint target/source recovery

The next spatial objective is complete: **11 individually selected rows replace the previous 48-row sufficient design**, while retaining all 21 target positions, the full two-dimensional source, every known real time in [1,2], and the previous sensor-noise allowances and 0.1% source-error target.

The retained spatial indices are

**485, 488, 491, 494, 497, 500, 503, 506, 509, 512, 516.**

This is a 77.08% reduction in directly acquired spatial-average channels. Every row still averages globally over the finite 1,001-cell x direction. The diffusion coefficient, normalization, finite transverse path, and source calibrations are unchanged. The unknown target can be any integer from 490 to 510; the source can be any nonzero real combination of the two prescribed cosine modes.

## The new result

Gaps between retained rows prevent simply inheriting the earlier centroid argument. The new decoder instead compares the complete two-dimensional response image for each target. The certificate separates all **210 pairs of target images**, then certifies the inverse for each of the 21 individual images.

For the physically normalized polynomial approximation, the uniform individual Gram floor is greater than

\[
\mu_0=(19/16)^2(7\cdot10^{-8})=9.87109375\cdot10^{-8},
\]

and every four-column pair map has Gram floor greater than

\[
\lambda_0=(19/16)^2\,10^{-11}=1.41015625\cdot10^{-11}.
\]

These hold throughout [1,2], over every source direction. The complete operator approximation error is below **\(10^{-9}\)** in the original physical output norm. This error already includes periodic images, the finite boundary, the omitted time series, and outward coefficient rounding.

Both H1 source metrics are bounded above by \(41I\). Dividing the individual and pair floors by 41, while preserving the original output norm, gives the corresponding calibrated guarantees.

| Source metric | Retained sensor allowance | Certified relative source error |
|---|---:|---:|
| L2 | \(3\cdot10^{-7}\|u\|_2\) | \(<0.000962\) |
| Declared H1 | \(3\cdot10^{-8}\|u\|_{S_1}\) | \(<0.000653\) |
| Natural discrete H1 | \(3\cdot10^{-8}\|u\|_{S_2}\) | \(<0.000653\) |

The table includes the full model allowance and a further **conditional** computed-data allowance of \(10^{-9}\|u\|_S\). It does not assert that arbitrary floating normalization or arithmetic satisfies that additional allowance. Setting it to zero gives the pure sensor/model guarantee. The exact rational decoder introduces no inverse-solve rounding; a different floating solver needs its own verified error contract.

The source/noise metrics in the three rows are separate assumptions. Their numerical noise constants are not interchangeable.

## Why this is a transfer result

The proof connects the actual finite dynamics to a small rational polynomial map without discarding the difficult directions.

The x generator remains the full finite matrix, including its noncommuting variable coefficient. A periodic transverse surrogate permits Fourier reconstruction; a Laurent/Cauchy bound sums every periodic image. A walk expansion separately charges the physical finite boundary, including every omitted term starting at step 491. A positive-semidefinite derivative bound controls the complete order-32 time remainder on the whole interval.

Rational preconditioners make the pair floors practical to certify despite their small scale. Floating Cholesky factors only propose those preconditioners. The independent consumer checks their exact Gram defects, translated polynomial variation, and unpreconditioned floors. Each of the 231 cases must separately cover [1,2]. The completed evidence has **46 nonempty time cells and 895 whole-cell records**.

For each candidate label the decoder minimizes an explicit relative-feasibility quadratic. It retains only compatible labels and applies ordinary least squares once a unique label remains. Pair separation proves that valid data retain exactly the correct label. Empty compatible sets mean inconsistent data or budgets; zero data are rejected under the nonzero-source model. The executable interface accepts exact rational times and exactly normalized rational data. The mathematical time theorem covers all real known times in the interval.

## Verification and meaning

The standalone exact consumer passes. All nine tests pass, including a deliberately removed individual pair's time coverage, changed noise/kernel premises, boolean-as-integer rejection, every target label at the time endpoints and center, multiple source directions, noisy data under every calibration, and invalid or incompatible decoder inputs.

Full finite-x coefficient reconstruction at 192 and 256 bits gives the same exported outward intervals. Additional direct finite-grid diagnostics use 1,002,001 states and test nine forward experiments across all three calibrations: 27 decoded cases pass, with maximum observed model discrepancy \(3.36\cdot10^{-17}\) and source-relative error about \(0.000237\). Those floating experiments are regression evidence; the uniform guarantees come from the complete proof and exact certificate.

The [independent audit](AUDIT.md) separately verifies the analytic bridge, exact boundary-walk controls, and dense finite-model controls. A different positive uniformization expansion at 256 bits reconstructs 16 selected coefficients of the full 1,001-cell x model inside the saved outward intervals. It found no defect.

This establishes that target-dependent image separation can reduce acquisition far beyond a consecutive-window retention argument. It does not prove that eleven rows are minimal, or that the old 97% information-retention ratio survives. The retained performance claim is the same noise allowance and source-error target. Acquisition savings require these eleven averages to be directly available; forming them from an already acquired complete modal vector is post-processing.

The next focused objective is to certify fewer rows or more source modes using the same full-model pair certificate. Either extension must recheck all label pairs and continuous time; a failed sufficient bound would not by itself prove an obstruction.
