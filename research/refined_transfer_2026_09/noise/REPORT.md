# Weighted drift approximation with actual integer recovery

The same degree-eight arithmetic experiment now certifies recovery in the
presence of a much larger **specified slow drift**. For the family

\[
g(x)=A\sin(\omega x+\phi),\qquad |A|\leq B,
\quad |\omega|\leq1,\quad \phi\in\mathbb R,\qquad x=t/890,
\]

a verified polynomial approximation reduces the complete physical W-norm
remainder to less than \(1.364\cdot10^{-9} B\) for either design. Every phase
and the whole frequency interval are covered. All 8,900 complex readings,
physical weights, degree-eight polynomial nuisance, and complete arithmetic
tail remain as before.

The certified bound is over **2,021 times smaller** than the earlier pointwise
Taylor bound \(B/9!\). This is an improvement in a sufficient approximation
bound for a declared drift family. It is not a measured increase in instrument
tolerance or a proof of optimal approximation.

## What produces the improvement

There are two steps. First, replace the largest pointwise Taylor remainder by
its norm under the actual positive sensing weights. Second, improve the
polynomial: approximate the Taylor powers of degree 9 through 20 by fixed
rational degree-eight polynomials, with complete higher-order Taylor remainders.
Every polynomial residual is verified at every reading. The proof uses exact
weight symmetry and polynomial parity to cover unknown phase without adding
odd and even errors unnecessarily.

The following are rounded values; the exact rational bounds and consequences
are recorded in `approximation.json` and `checked_approximation.json`.

| Design | Pointwise Taylor factor | Weighted Taylor factor | New uniform factor | Safe amplitude at remainder radius \(3\cdot10^{-5}\) |
|---|---:|---:|---:|---:|
| Multiscale | \(2.755732\cdot10^{-6}\) | \(3.602664\cdot10^{-8}\) | \(<1.362178\cdot10^{-9}\) | 22,023 |
| Outer | \(2.755732\cdot10^{-6}\) | \(3.606104\cdot10^{-8}\) | \(<1.363134\cdot10^{-9}\) | 22,008 |

At the same remainder radius, the pointwise bound supports amplitude 10.8864.
The intermediate weighted Taylor bound supports about 832.7 and 831.9,
respectively. The final polynomial improvement contributes another factor
exceeding 26.4 beyond using the physical norm alone.

The frequency dependence is explicit. If a smaller frequency bound
\(0\leq\Omega\leq1\) is known, the exact bound is a finite polynomial in
\(\Omega\) plus two complete remainder terms, and is at most
\(\Omega^9 K_W(1)\). At \(\Omega=1/2\), the multiscale factor is less than
\(2.625029\cdot10^{-12}\). These claims assume a frequency bound; the solver
residual does not estimate or validate it.

## Actual recovery under the new family bound

The supplied exact digital fixture contains a valid integer-envelope source,
nonzero omitted coefficients at 51, 60 and 72, a degree-eight complex polynomial
with coefficient scale \(10^{20}\), and
\(g(x)=20000\sin(x+1/3)\). The sensor perturbation has magnitude
\(3.9\cdot10^{-5}\), and verified digitization error is below \(10^{-35}\).
Together they satisfy the declared sensor budget \(\eta=4\cdot10^{-5}\).
The inverse receives no target answer and still uses its complete infinite-tail
certificate.

| Certified quantity | Multiscale | Outer |
|---|---:|---:|
| Uniform family remainder radius | \(<2.724355\cdot10^{-5}\) | \(<2.726268\cdot10^{-5}\) |
| Actual normal residual upper bound | \(<3.176\cdot10^{-39}\) | \(<3.207\cdot10^{-39}\) |
| Maximum unknown-coefficient error | \(<0.417849\) | \(<0.466873\) |
| Unknown integers recovered correctly | 49 of 49 | 49 of 49 |

The initial floating proposals fail their actual residual checks because of the
large polynomial component. Arb refinement produces the accepted proposals;
both the normal-equation and reading-space residual formulations are verified.
The old pointwise remainder, substituted into the same recovery calculation,
fails 47 of the 49 rounding gates in each design. Increasing the declared
family amplitude to one million also fails despite the very small solver
residual. These controls expose the separation between physical uncertainty
and numerical solve accuracy.

## How this advances the shared transfer theorem

The general theorem needs a justified error budget after nuisance reduction.
This extension supplies one for an infinite family, rather than treating the
nonpolynomial radius as an arbitrary input. For every admitted drift there is a
degree-eight polynomial \(p\) such that \(\|g-p\|_W\leq B K_W(\Omega)\).
The augmented inverse absorbs \(p\); its residual \(g-p\) is charged once with
the sensor and correction errors. The unchanged transfer gate then gives

\[
|n^2\widehat\theta_n-a(n)|\leq
 A_n+n^2\left(\frac{\eta+B K_W(\Omega)+\Xi}{\sqrt f}
                 +\frac{\rho}{f}\right)<\tfrac12.
\]

The proof, physical certificate and actual recovery verifier agree on that
same norm and shared set of readings.

## Validation and limits

The independent full-vector consumer checks 24 rational polynomial residual
bounds and six complete weighted-moment bounds. Reconstruction at 192, 256 and
320 bits yields identical rational polynomials, bounds and family factors.
A separate review verifies all residual norms using 320-bit moment quadratic
forms. Actual-data replay at 320 bits reproduces all 8,900 stored readings and
verifies the saved exact proposals. An independent exact consequence checker
passes all 98 integer gates, and seven focused adverse tests pass.

The family is deliberately slow: its phase changes by at most approximately
two radians over the full observation window. Faster drift, uncertain timing,
changed weights and calibration error require their own charged bounds.
The physical family and sensor promises still need a declared model or
calibration. The synthetic source is an integer-envelope example; no
number-field realization or measured noise distribution is claimed.

## The next focused objective

The next useful step is to specify a calibration-backed uncertainty set for
the drift's frequency and amplitude, including a separate mismatch radius.
Then optimize polynomial degree against the complete arithmetic bias and
remaining sensor budget over that set. The new explicit frequency dependence
makes the value of increasing degree measurable. A second mathematical target
is tightening the uniform approximation bound for that specified interval;
the current rational polynomials are certified but not asserted optimal.
