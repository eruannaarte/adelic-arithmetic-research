# Operational Information Geometry X

## Reproducible finite-band spectral certificate laboratory

**Status:** outward-rounded finite-$K$ certificate; not peer reviewed

**Certified scope:** the standard-Gaussian late resolved continuum
$q\geq1$, the one-cell late lattice continuum $\tau\geq1$, and the interior
atomic endpoint, for the first $K\leq8$ affine-ramp cosine ports in the
declared $L^2$ and continuum $H^1$ source metrics

**Not certified as continuous families here:** the calibrated early endpoint,
general lattice preparations, and the full reflecting-boundary parameter
family

---

## 1. What is new

Stage IX identified the continuum quotient-Gram floor $\gamma_K$ as the
quantity that must dominate a finite-model remainder before a growing source
band is operationally recoverable. Ordinary eigensolvers estimated that floor
but did not certify it. This laboratory supplies a rigorous moderate-band
core:

\[
 0<L_{K,S}\leq
 \gamma^{\mathrm{late},\delta_0}_{K,S}
 \leq U_{K,S},
 \qquad 1\leq K\leq8,
\]

where $S=I$ for $L^2$, $S_{kk}=1+(k\pi)^2$ for continuum $H^1$, and

\[
 \gamma^{\mathrm{late},\delta_0}_{K,S}
 =\inf\left\{
 \lambda_{\min}(\widehat\Gamma_q^{\mathrm R},S):q\geq1,\quad
 \lambda_{\min}(\widehat\Gamma_\tau^{\mathrm L},S):\tau\geq1,\quad
 \lambda_{\min}(\Gamma_\infty^{\mathrm A},S)
 \right\}.
\]

The Stage IX normalizations are

\[
 \widehat\Gamma_q^{\mathrm R}
 =\sqrt{1+q}\,\Gamma_q^{\mathrm R},
 \qquad
 \widehat\Gamma_\tau^{\mathrm L}
 =\sqrt{1+\tau}\,\Gamma_{\tau,\delta_0}^{\mathrm L}.
\]

The lower bound is genuinely uniform over the two unbounded continuous
parameters. It is not a finite parameter sample. Every proof decision is
made with Arb ball arithmetic on the generalized pair $(G,S)$, directly by
proving $G-LS\succ0$. NumPy and mpmath are only descriptive cross-checks and
witness-discovery tools.

---

## 2. The continuous common core

For

\[
 V(x)=1+\frac45x,
 \qquad
 \phi_k(x)=\sqrt2\cos(k\pi x),
\]

The Stage IX structural null is trivial: the affine ramp is strictly
monotone, so conditioning on $V$ is equivalent to conditioning on $x$.
Consequently the displayed cosine band is already the exact quotient on
which the certificate is made. The output norm is the Stage IX phase-output
$L^2$ norm; the statistical example in Section 6 separately declares its
white Gaussian variance.

The corresponding phase profile is

\[
 F_k(s)=\sqrt2e^{-s}
 \frac{(4/5)s\,[1-(-1)^ke^{-(4/5)s}]}
 {((4/5)s)^2+(k\pi)^2}.
\]

Define

\[
 H_b=\frac1{2\pi}\int_0^b
 s^{-1/2}F(s)^*F(s)\,ds.
 \tag{2.1}
\]

Its equivalent Hankel kernel is

\[
 K_b(A)=\frac{\operatorname{erf}(\sqrt{Ab})}
 {2\sqrt{\pi A}}.
 \tag{2.2}
\]

The implementation removes the endpoint square root with $s=br^2$:

\[
 (H_b)_{jk}=\frac{\sqrt b}{\pi}
 \int_0^1F_j(br^2)F_k(br^2)\,dr.
 \tag{2.3}
\]

This analytic one-dimensional integral is evaluated by Arb's validated
complex quadrature.

### 2.1 Uniform resolved domination

Changing variables in the standard-Gaussian resolved integral gives

\[
 \widehat\Gamma_q^{\mathrm R}
 =\frac1{2\pi}\int_0^\infty s^{-1/2}
 w_{\mathrm R}(q,s)F(s)^*F(s)\,ds,
\]

where

\[
 w_{\mathrm R}(q,s)
 =\sqrt{\frac{1+q}{q}}e^{-s/q}.
\]

Writing $x=1/q\in[0,1]$,

\[
 \log w_{\mathrm R}=\frac12\log(1+x)-sx
\]

is concave in $x$, so its minimum is at an endpoint. On
$0\leq s\leq b$,

\[
 w_{\mathrm R}(q,s)\geq
 c_{\mathrm R}(b):=\min(1,\sqrt2e^{-b}).
 \tag{2.4}
\]

### 2.2 Uniform lattice and atomic domination

For $Q=\delta_0$, set $s=\tau\omega(\theta)$. The normalized lattice
density relative to (2.1) is

\[
 w_{\mathrm L}(\tau,s)
 =\frac{2\sqrt{1+\tau}}{\sqrt{4\tau-s}}.
\]

If $\tau\geq1$ and $0\leq s\leq b\leq4$, then

\[
 w_{\mathrm L}(\tau,s)\geq
 \sqrt{\frac{1+\tau}{\tau}}>1.
 \tag{2.5}
\]

The interior atomic integral contains $[0,b]$. Therefore

\[
 \boxed{
 \widehat\Gamma_q^{\mathrm R}\succeq c_{\mathrm R}(b)H_b,\quad
 \widehat\Gamma_\tau^{\mathrm L}\succeq H_b
 \succeq c_{\mathrm R}(b)H_b,\quad
 \Gamma_\infty^{\mathrm A}\succeq H_b
 \succeq c_{\mathrm R}(b)H_b.}
 \tag{2.6}
\]

This turns one validated matrix into a certificate for an entire continuum
atlas. The frozen rational cutoffs are

\[
 b_K=1,\frac74,\frac{21}8,\frac72,4,4,4,4
 \quad(K=1,\ldots,8).
\]

They were selected in a finite exploratory scan. The scan was not certified
and no optimality is claimed; validity depends only on $b_K\leq4$.

---

## 3. How the certificate works

Let

\[
 C_K=c_{\mathrm R}(b_K)H_{b_K}.
\]

For an exact rational proposal $L>0$, the script forms $C_K-LS$ without
numerical whitening. It evaluates all leading principal determinants in Arb.
If every determinant ball is strictly positive, Sylvester's criterion proves

\[
 C_K-LS\succ0.
\]

Equation (2.6) then proves the same generalized lower floor for every covered
chart parameter. This remains a generalized-metric proof for
$S_{kk}=1+(k\pi)^2$; the metric is never silently replaced by Euclidean
coordinates.

For an upper bound, a high-precision eigensolver proposes a weak direction.
It is rounded to an integer vector $v$, after which Arb checks

\[
 \lambda_{\min}(G,S)
 \leq\frac{v^TGv}{v^TSv}<U.
\]

The atlas upper bound uses an actual point in the covered family. Therefore
both sides have proof witnesses, although the gap is conservative.

---

## 4. Certified bounds

These are decimal approximations to the exact rational bounds in the JSON
proof record.

| $K$ | metric | $b_K$ | certified $L_{K,S}$ | certified $U_{K,S}$ | upper witness |
|---:|:---:|---:|---:|---:|:---|
| 1 | $L^2$ | 1 | $1.31065\times10^{-4}$ | $5.69203\times10^{-4}$ | resolved $q=1$ |
| 1 | $H^1$ | 1 | $1.20579\times10^{-5}$ | $5.23665\times10^{-5}$ | resolved $q=1$ |
| 2 | $L^2$ | $7/4$ | $1.43152\times10^{-7}$ | $9.94471\times10^{-7}$ | resolved $q=1$ |
| 2 | $H^1$ | $7/4$ | $3.55231\times10^{-9}$ | $2.46473\times10^{-8}$ | resolved $q=1$ |
| 3 | $L^2$ | $21/8$ | $1.77650\times10^{-10}$ | $1.96271\times10^{-9}$ | resolved $q=1$ |
| 3 | $H^1$ | $21/8$ | $2.01796\times10^{-12}$ | $2.22383\times10^{-11}$ | resolved $q=1$ |
| 4 | $L^2$ | $7/2$ | $2.23908\times10^{-13}$ | $3.95391\times10^{-12}$ | resolved $q=1$ |
| 4 | $H^1$ | $7/2$ | $1.48943\times10^{-15}$ | $2.62281\times10^{-14}$ | resolved $q=1$ |
| 5 | $L^2$ | 4 | $2.72483\times10^{-16}$ | $7.96784\times10^{-15}$ | resolved $q=1$ |
| 5 | $H^1$ | 4 | $1.21070\times10^{-18}$ | $3.53520\times10^{-17}$ | resolved $q=1$ |
| 6 | $L^2$ | 4 | $2.41218\times10^{-19}$ | $1.60003\times10^{-17}$ | resolved $q=1$ |
| 6 | $H^1$ | 4 | $7.73921\times10^{-22}$ | $5.13632\times10^{-20}$ | resolved $q=1$ |
| 7 | $L^2$ | 4 | $1.53496\times10^{-22}$ | $3.20199\times10^{-20}$ | resolved $q=1$ |
| 7 | $H^1$ | 4 | $3.74302\times10^{-25}$ | $7.82025\times10^{-23}$ | resolved $q=1$ |
| 8 | $L^2$ | 4 | $7.36997\times10^{-26}$ | $1.82508\times10^{-23}$ | lattice $\tau=1$ |
| 8 | $H^1$ | 4 | $1.41495\times10^{-28}$ | $3.50451\times10^{-26}$ | lattice $\tau=1$ |

The rapid decay is a measured finite-band fact, not a fitted asymptotic law.
These eight cases do not establish a lower decay exponent as $K\to\infty$.

### 4.1 Fixed representatives at $K=8$

The same direct proof was run on four full phase Grams. Infinite $s$
integrals use a proved analytic tail after $B=40$.

| chart | metric | certified lower | certified upper |
|:---|:---:|---:|---:|
| normalized resolved $q=1$ | $L^2$ | $2.87599\times10^{-23}$ | $6.39109\times10^{-23}$ |
| normalized resolved $q=1$ | $H^1$ | $5.53308\times10^{-26}$ | $1.22957\times10^{-25}$ |
| normalized lattice $\tau=1,Q=\delta_0$ | $L^2$ | $8.21287\times10^{-24}$ | $1.82508\times10^{-23}$ |
| normalized lattice $\tau=1,Q=\delta_0$ | $H^1$ | $1.57703\times10^{-26}$ | $3.50451\times10^{-26}$ |
| interior atomic | $L^2$ | $3.29333\times10^{-21}$ | $7.31850\times10^{-21}$ |
| interior atomic | $H^1$ | $6.35990\times10^{-24}$ | $1.41331\times10^{-23}$ |
| boundary $\kappa=1$ | $L^2$ | $2.87485\times10^{-21}$ | $6.38856\times10^{-21}$ |
| boundary $\kappa=1$ | $H^1$ | $5.55928\times10^{-24}$ | $1.23540\times10^{-23}$ |

The boundary row is a point-chart certificate only. It is not uniform over
$\kappa\in[0,\infty]$.

---

## 5. Rigorous tails and enclosure audit

For every normalized port,

\[
 |F_k(s)|\leq e^{-s},
\]

by Cauchy--Schwarz and $V\geq1$. With $B=40$, the per-entry omitted-tail
bounds are

\[
 \begin{array}{c|c}
 \text{chart}&\text{absolute tail per Gram entry}\\ \hline
 \text{resolved }q=1&
 \displaystyle\frac{\sqrt2e^{-3B}}{6\pi\sqrt B}\\[2mm]
 \text{interior atomic}&
 \displaystyle\frac{e^{-2B}}{4\pi\sqrt B}\\[2mm]
 \text{boundary }\kappa=1&
 \displaystyle\frac{e^{-2B}}{2\pi\sqrt B}.
 \end{array}
\]

The lattice integral is compact and has no tail. At 320 bits the largest
total entry radius, including analytic tails, was
$4.542\times10^{-37}$, below the exact audit cap $10^{-34}$.

---

## 6. Effective rank and a declared noise budget

At an exact information threshold $\eta$, the script forms $G-\eta S$.
When all leading minors have certified nonzero signs, sign changes in

\[
 1,\Delta_1,\ldots,\Delta_K
\]

give the negative inertia. The number of generalized eigenvalues strictly
above $\eta$ is then certified without diagonalizing an interval matrix.
Applied to the common core, this is a uniform effective-rank lower bound for
every covered late chart. The JSON record includes the exact thresholds

\[
 10^{-4},10^{-8},10^{-12},10^{-16},10^{-20},10^{-24},10^{-28}.
\]

For one explicit statistical interpretation, take unit-amplitude simple
Gaussian discrimination with $\sigma=10^{-3}$ and one-sided error
$\alpha=0.05$. Put

\[
 z=\Phi^{-1}(0.95)=\sqrt2\,\operatorname{erf}^{-1}(0.9).
\]

The lower and upper certificates give

\[
 N_{\mathrm{suff}}
 =\left\lceil\frac{4\sigma^2z^2}{L_{K,S}}\right\rceil,
 \qquad
 N_{\mathrm{nec}}
 =\left\lceil\frac{4\sigma^2z^2}{U_{K,S}}\right\rceil.
\]

Arb encloses $z$, directs the integer roundings, and checks the sufficient
inequality. This is an example budget for the declared Gaussian experiment,
not a universal physical noise law.

---

## 7. Why binary64 is not the certificate

At $K=8$, the independent 106-digit mpmath check of the $L^2$ common-core
minimum was approximately

\[
 1.6377720494\times10^{-25},
\]

where binary64 returned $5.0570592356\times10^{-25}$. In the $H^1$ metric,
mpmath returned approximately

\[
 3.1443236557\times10^{-28},
\]

while binary64 returned the negative value
$-3.0034328610\times10^{-28}$ for a positive-definite Gram. This is why the
proof uses outward-rounded entries, exact rational thresholds, and
determinant signs. The mpmath values are also descriptive; only the Arb
inequalities carry proof status.

---

## 8. Honest boundary

This package does **not** certify the full Stage IX atlas floor.

1. The early interval $q\in[0,1]$ needs a rigorously constructed
   moment-adapted basis and a scaled analytic endpoint oracle. Evaluating
   small positive $q$ cannot replace the $q=0$ proof.
2. The full reflecting-boundary family could be covered by finite
   $\kappa$-boxes plus a certified large-$\kappa$ tail, but this file
   certifies only $\kappa=1$.
3. General lattice profiles $Q$ do not inherit the one-cell pointwise lower
   weight because $|B_Q|^2$ may vanish. They need a declared preparation
   family and a separate frame or parameter-cover argument.

Nor does this package certify finite-$h$ transfer. Its $L_{K,S}$ values are
continuum floors that a separate Stage IX remainder must beat.

---

## 9. Reproduction

Install the dedicated dependencies and run the focused tests:

~~~bash
python -m pip install -r oig_x_spectral_certificate_requirements.txt
python -m unittest -v test_oig_x_spectral_certificate.py
~~~

Generate the full $K\leq8$, 320-bit JSON proof record:

~~~bash
python oig_x_spectral_certificate.py \
  --max-band 8 \
  --precision-bits 320 \
  --output oig_x_spectral_certificate.json
~~~

The optional **--fast** flag reduces only the descriptive mpmath quadrature
order. It does not weaken Arb integration, tail enclosures, generalized
shifts, inertia, or Rayleigh checks.

The seven deterministic tests check the continuous scope, every generalized
lower and upper proof, fixed-chart coverage, effective-rank monotonicity, the
noise inequality, JSON portability, and a negative generalized-metric
control.

---

## 10. Reproducibility verdict

On the reference run:

- all 16 continuous late-atlas certificates passed;
- all 64 fixed-chart/metric/band certificates passed;
- every effective-rank inertia computation was decisive;
- every mpmath descriptive minimum lay inside its Arb spectral bracket;
- all analytic tails and radii passed the enclosure audit; and
- all seven focused tests passed.

The strongest sound conclusion is

\[
 \boxed{\begin{gathered}
 \text{For every }K\leq8,\text{ the declared late one-cell three-chart}\\
 \text{continuum has an explicit, reproducible positive generalized floor.}
 \end{gathered}}
\]

Compactness still predicts deterioration as $K$ grows. The certificate
quantifies that deterioration far enough to turn the Stage IX condition
“finite error $<\gamma_K$” into an executable moderate-band budget, without
claiming an unsupported infinite-dimensional stability law.
