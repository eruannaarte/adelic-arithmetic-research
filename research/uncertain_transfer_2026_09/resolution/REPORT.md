# Seven-row sensing with stronger noise and uncertainty guarantees

The rows **490, 492, 496, 500, 504, 508, 510** identify every target from 490 to
510 and recover every nonzero two-mode source with relative Euclidean error
below **0.001**, for all nominal times in **[1,2]**. Their minimum spacing is
two. The new certificate improves the preceding seven-row noise allowance and
also supports a nonzero, explicitly charged clock/model uncertainty set.

| Certified profile | Relative sensor radius | Absolute shared clock error | Generator operator error | Relative source error bound |
| --- | ---: | ---: | ---: | ---: |
| Known clock and generator | \(1.4\,10^{-7}\) | 0 | 0 | < 0.000976359 |
| Uncertain clock and generator | \(1.1\,10^{-7}\) | \(5\,10^{-7}\) | \(10^{-9}\) | < 0.000915623 |

Both profiles additionally charge the complete finite-model approximation
\(10^{-9}\) and allow verified normalization error \(10^{-9}\). The first
sensor allowance is **40% greater** than the prior seven-row guarantee; the
second keeps a **10% increase** while adding positive uncertainty budgets.
These percentages compare sufficient certified allowances, not optimal noise
thresholds. Clock error uses the defining model's time units. The generator
allowance is an operator-norm assumption, not a claim of measured calibration.

The primary seven-row contract was fixed before work began. One promising
layout already present in the prior floating search was re-screened and then
proved. A new six-row search was unnecessary to meet that contract and was
not performed. Neither seven-row optimality nor six-row impossibility is claimed.

The proof uses 861 nonempty time cells and 3,743 rational case records covering
all 21 individual sources and all 210 pairs. An independent consumer verifies
each cell using a different polynomial-translation calculation. It establishes
unnormalized individual and pair Gram floors \(1.5\,10^{-8}\) and
\(5\,10^{-14}\). This improves the weakest source direction as well as
separating distinct labels. The preceding new bank's individual floor was
\(7.4\,10^{-9}\), which left little room for additional error.

The shared transfer consequence is explicit. For both nominal and true times
in \([1,2]\), a reconstructed polynomial forward-map derivative bound gives
\(L=0.037\). For a perturbed self-adjoint positive-semidefinite generator
\(H'\), Duhamel's identity gives forward error at most
\(8\|H'-H\|/3\). The sufficient recovery tradeoff is
\[
 \eta+\rho+\xi+0.037h+\tfrac83\varepsilon_H
 <\min\{0.001\sqrt\mu,\sqrt{\lambda/2}\},
 \qquad
 \mu=\frac{1083}{51200000000},\quad
 \lambda=\frac{361}{5120000000000000}.
\]
This bound transports an observation at its unknown true time to the nominal
map used by the decoder. It charges the inherited approximation radius once.
It does not assume that an approximation error also bounds its derivative.

Twelve raw rational observations were constructed for the actual finite model
with nonzero time shifts and \(H'=H+10^{-9}I\). Their sensor promises are
proved by outward evaluation and the complete model approximation, then
reconstructed at 320 bits. The operational wrapper recovers all twelve labels
and all sources, across scales \(10^{-8},1,10^8\); the largest observed
relative source error is below \(1.396\,10^{-5}\). These are synthetic
mathematical observations, not laboratory measurements.

A separate reconstruction evolves the actual 1,002,001-state finite model at
three perturbed times, applies the positive generator shift, and adds sensor
noise in each nominal map's weakest inverse direction. All labels are
recovered; the largest relative source error is below 0.000170145. These
floating diagnostics support the implementation; they are not premises of
the rational guarantees above.

Eight focused tests pass, including changed bank metadata, corrupted
preconditioners, excessive clock/noise budgets, non-rational inputs and
altered fixture contracts. An independent 384-bit review reconstructs the time
bound, both strict profiles, 693 pointwise Gram floor checks and all raw sensor
promises. The full-time result comes from the separate complete rational cell
consumer, not those point samples.

See [proofs](PROOFS.md), [reproduction instructions](README.md),
[time and mismatch receipt](timing.json), and the shared
[raw decoder](../framework/raw_clock.py). The next spatial improvement should
optimize the joint bound on source accuracy and label separation, or attempt
the already specified six-row contract. Tighter structured generator bounds
could increase useful clock tolerances without changing the bank.
