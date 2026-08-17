# Independent audit of the compact Arb lattice-time cover

## Verdict

**The certificate is mathematically valid for its declared scope.**  I found
no theorem-breaking defect in the Taylor construction, the two remainder
arguments, the finite/continuum normalizations, the metric transfers, or the
directed comparison with the imported Stage X floors.

More precisely, subject to the already proved Stage X continuum floors and
the documented semantics of Arb/python-flint, the implementation certifies
that the exactly centred odd `n=1001`, `K=2` full Neumann Gram has a positive
generalized spectral floor for every

\[
  1\leq \tau\leq 6/5
\]

in the three declared comparisons: raw \(L^2\), declared continuum \(H^1\),
and natural discrete \(H^1\).

This verdict does **not** extend the result past \(6/5\), to fixed \(n\) on an
unbounded time interval, to an off-centre target, or to a source band wider
than two.

## Independent reproduction

I reran the complete cover at 192-bit Arb precision.  All eight focused tests
passed in 56.9 seconds.  I also evaluated the full noncommuting finite model
and the continuum integral through the independent binary64 diagnostic at
five points.  Those point values do not participate in the proof, but they
are a useful normalization and parity check:

| \(\tau\) | \(L^2\) error | declared \(H^1\) error | natural discrete \(H^1\) error |
|---:|---:|---:|---:|
| 1.00 | \(1.69009\times10^{-8}\) | \(1.49115\times10^{-9}\) | \(1.39036\times10^{-9}\) |
| 1.05 | \(1.72737\times10^{-8}\) | \(1.52479\times10^{-9}\) | \(1.42621\times10^{-9}\) |
| 1.10 | \(1.76588\times10^{-8}\) | \(1.55946\times10^{-9}\) | \(1.46285\times10^{-9}\) |
| 1.15 | \(1.80544\times10^{-8}\) | \(1.59502\times10^{-9}\) | \(1.50016\times10^{-9}\) |
| 1.20 | \(1.84592\times10^{-8}\) | \(1.63134\times10^{-9}\) | \(1.53806\times10^{-9}\) |

Each lies below its whole-cell Arb upper bound.  The agreement is particularly
useful because the natural discrete comparison has different finite and
continuum whitening matrices.

## Audit of the proof chain

### 1. Finite Taylor coefficients

For a target eigenvalue \(\omega\), the code uses

\[
 A=L_n+\omega V_n,\qquad
 c=2+\frac75\omega,\qquad B=A-cI,
\]

with

\[
 \|B\|\leq \rho=2+\frac25\omega,
 \qquad c-\rho=\omega.
\]

The path Laplacian spectrum lies in \([0,4]\), while
\(V_n\in[1,9/5]\).  Thus these bounds hold for every retained mode.  The
degree-48 centred exponential polynomial consequently has operator error

\[
 e^{-\tau_c c}e^{\tau_c\rho}
 \frac{(\tau_c\rho)^{49}}{49!}
 =e^{-\tau_c\omega}
 \frac{(\tau_c\rho)^{49}}{49!}.
\]

The implementation takes a directed upper endpoint of this expression.  It
then applies \((-A)^q/q!\) recursively, multiplying the base error by
\(\|A\|^q/q!\), with the safe global bound
\(\|A\|\leq4+(9/5)\omega\leq56/5\).  This correctly encloses every finite
response Taylor coefficient through degree 18.

The DCT normalization is also consistent.  The stored source vector is
\(n^{-1/2}\phi_{k,h}\); summing the evolved state and dividing by
\(\sqrt n\) gives \(n^{-1}\sum_j(e^{-\tau A}\phi_{k,h})_j\), exactly the
declared discrete inner product.  Multiplication by \(2/n\) in the target-mode
sum is the exact squared coefficient of each positive even mode.  Odd modes
vanish at the central cell, and the zero target mode has zero response to the
two zero-mass ports.

### 2. Continuum Taylor coefficients

The elementary series recurrences for product, reciprocal, exponential, and
square root are the standard coefficient recurrences.  Substitution into

\[
 F_k(s)=\sqrt2e^{-s}
 \frac{gs[1-(-1)^ke^{-gs}]}{(gs)^2+(k\pi)^2}
\]

with \(s=(\tau_c+\delta)\omega(\xi)\) therefore gives the Taylor
coefficients of the correct continuum response.  Arb's validated complex
integrator encloses each coefficient on \([0,1]\).  The discarded imaginary
component is justified by the independent mathematical fact that the
integrand and integral are real on the real path; the code also requires its
imaginary enclosure to contain zero.

The normalization series is the Taylor series of
\(\sqrt{1+\tau_c+\delta}\), so both finite and continuum Grams use exactly the
same declared \(\sqrt{1+\tau}\) normalization before metric whitening.

### 3. Order-19 remainder

For either unit source port,

\[
 |b^{(q)}(\tau)|\leq M^q
\]

follows from self-adjoint positivity, contraction of \(e^{-\tau A}\), and
the operator-norm bounds.  Here \(M_f=56/5\) and \(M_c=36/5\).  Leibniz then
gives \(|(b_i b_j)^{(q)}|\leq(2M)^q\).  The finite target weights sum to
\((n-1)/n<1\), and the continuum integral has total weight one, so the same
entry bound survives aggregation.

The helper for \(c(\tau)=\sqrt{1+\tau}\) uses the upper endpoint for
\(q=0\), and the lower endpoint for every \(q\geq1\), precisely where the
absolute derivative is largest.  Its binomial sum is therefore a valid
uniform bound on the nineteenth derivative of a normalized Gram entry.
Multiplication by \(r^{19}/19!\) is the correct Taylor remainder on
\(|\delta|\leq r=1/10\).  Adding the finite and continuum bounds gives a
valid symmetric remainder for their difference.

The exponential-polynomial uncertainty and the order-19-in-\(\tau\)
uncertainty are not conflated: the former is propagated inside every stored
finite coefficient; the latter is added after evaluating the degree-18
difference polynomial.

### 4. Metric transfer

The three comparisons are directionally sound:

- \(L^2\) whitens both families by the identity.
- Declared \(H^1\) whitens both by
  \(S=\operatorname{diag}(1+\pi^2,1+4\pi^2)\).
- Natural discrete \(H^1\) whitens the finite Gram by
  \(S_n=\operatorname{diag}(1+n^2\omega_{n,1},1+n^2\omega_{n,2})\) and the
  continuum Gram by \(S\).

Thus the last case directly bounds
\(\|S_n^{-1/2}G_nS_n^{-1/2}-S^{-1/2}GS^{-1/2}\|_2\).  Weyl's inequality
then subtracts that error from the continuum generalized floor and produces
a lower floor for the finite problem in its own natural metric.  No unsafe
replacement of \(S_n\) by \(S\) occurs.

### 5. Directed spectral decisions

For the symmetric two-by-two error matrix, interval evaluation of the closed
eigenvalue formula encloses both eigenvalues.  The code takes each Arb
absolute upper endpoint, converts it to an exact dyadic rational, and uses the
larger one.  The imported floor remains an exact rational.  The strict Arb
comparison is conservative, and the reported transferred floor is the exact
rational difference between the imported floor and the outward dyadic upper
bound.

The independently repeated decisions were:

| metric | outward error upper | exact-floor decimal | exact positive margin (decimal) |
|---|---:|---:|---:|
| \(L^2\) | \(1.8641777991478482\times10^{-8}\) | \(1.4315196512138325\times10^{-7}\) | \(1.2451018712990477\times10^{-7}\) |
| declared \(H^1\) | \(1.6408051800951587\times10^{-9}\) | \(3.5523100221039936\times10^{-9}\) | \(1.9115048420088350\times10^{-9}\) |
| natural discrete \(H^1\) | \(1.5475021286371954\times10^{-9}\) | \(3.5523100221039936\times10^{-9}\) | \(2.0048078934667980\times10^{-9}\) |

The word “exact” in the last column refers to the underlying rational
subtraction, not the displayed decimal rendering.

## Concrete issues and hardening recommendations

None of the following invalidates the theorem, but each matters for a durable
proof artifact.

1. **The focused tests trust the certificate's `passed` fields.**  They also
   compare binary64 renderings with loose decimal thresholds.  A stronger
   verifier should parse `stage_x_floor_exact` and
   `spectral_error_upper_exact`, recompute every strict rational inequality
   and margin, and reject inconsistent boolean or decimal fields.

2. **The Stage X dependency is imported, not replayed.**  This is legitimate
   theorem composition, but the JSON artifact should record the source file,
   schema/version, and preferably a digest of the exact floor table.  At
   present a later edit to `STAGE_X_LOWER_BOUNDS` changes the premise without
   an explicit provenance record in the cover output.

3. **The integrator trace is thin.**  The result records precision but not
   the requested relative/absolute tolerances, subdivision limits, or a
   coefficient-level trace.  Arb enclosures remain rigorous, yet recording
   those parameters would make independent reproduction and diagnosis more
   transparent.

4. **`binary64_decides_no_inequality` is declarative metadata.**  Source
   inspection confirms it for the current implementation: floats are used
   only for JSON display fields.  A future verifier should nevertheless
   derive this assurance by recomputing decisions from exact fields rather
   than trusting the boolean.

5. **Reality of the continuum integral is partly a mathematical premise.**
   Checking merely that the returned imaginary ball contains zero would not,
   by itself, prove that discarding the imaginary component is safe for an
   arbitrary integrand.  Here it is safe because the explicit integrand is
   real for real \(\xi\).  That premise should remain stated near the code so
   a later generalization does not inherit the check without its justification.

## Final assessment

The proof cell is a sound and useful milestone.  It closes a genuine compact
interval for the full finite noncommuting model, rather than for a phase
surrogate or a set of sampled times.  The remaining work is coverage, not
repair: extend the rational-cell construction over \((6/5,2]\), retain the
same exact verification discipline, and then connect the compact cover to a
joint \(n\)-versus-\(\tau\) tail schedule rather than attempting the false
fixed-grid half-line statement.
