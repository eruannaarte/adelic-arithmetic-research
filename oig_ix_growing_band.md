# Operational Information Geometry IX

## Growing-band response Gramians: numerical laboratory

- **Status:** exact finite identities, exact phase-limit Gram kernels, and
  reproducible high-precision numerical evidence
- **Model scope:** the declared one-way parabolic toy model only
- **Not claimed:** this is not the growing-band theorem, an all-$K$
  singular-value asymptotic, or a physical law
- **Executable:** oig_ix_growing_band.py
- **Tests:** test_oig_ix_growing_band.py

## 1. Outcome

The growing-band problem separates into two questions.

1. **Chart accuracy.** The experiments identify the source-diffusion number

   $$
   \delta_{K,h}(t)=t\mu_{K,h}=\tau\omega_{K,h}
   $$

   as the first cutoff parameter. Fixed $K$ drives $\delta_{K,h}$ to zero.
   A band $K\asymp\sqrt n$ on the $t\asymp n^{-1}$ resolved/atomic clock,
   or $K\asymp n$ on the lattice clock, keeps it nonzero and leaves a
   persistent last-port error.

2. **Inverse stability.** Even when chart convergence is excellent, the
   response is severely compact. In 100-digit calculations, the smallest
   balanced and atomic singular values fall approximately by factors
   $0.0446$ and $0.0607$ for every additional cosine port over the tested
   range. Finite-$K$ positivity and stable growing-$K$ inversion are not the
   same statement.

The early resolved chart has a further structure. For

$$
E_K=\operatorname{span}\{\sqrt2\cos(k\pi x):1\leq k\leq K\},
$$

the observed response singulars satisfy

$$
\sigma_j(q)\sim q^j,\qquad 1\leq j\leq K,
$$

and hence

$$
\det\Gamma_K(q)\sim q^{K(K+1)}.
$$

This produces the physical critical fan

$$
\boxed{\alpha_j=\frac{4j}{4j+1}}
$$

along $\varepsilon=h^\alpha,\ t=h^2$. It is a dimension staircase: at
$\alpha=0.9$, the first two directions persist or grow while the third and
higher directions vanish.

The analytic companion proves the exact common quotient, fixed-band atlas,
causal singular flag, and relative transfer rule
$\delta_K/\gamma_K\to0$. The remaining quantitative target is to bound the
necessarily $K$-dependent floor $\gamma_K$ sharply enough to turn that rule
into an explicit bandwidth schedule, not a false $K$-uniform frame constant.

## 2. Finite response and metric calibration

For source modes $1\leq k\leq K$, target modes $0\leq\ell<n$, and a target
mass preparation with coefficient $\beta_{\ell,h}$, the laboratory assembles

$$
R_h(t)_{\ell k}
=\beta_{\ell,h}
\langle1,e^{-t(A_h+\mu_{\ell,h}V_h)}\phi_{k,h}\rangle_h.
$$

Target-mode separation reduces this exactly to $n$ symmetric tridiagonal
source problems. A small $n^2$-state Kronecker calculation independently
checks the reduction.

For a stacked protocol operator $\mathsf A$,

$$
\Gamma=\mathsf A^*\mathsf A,
\qquad
\lambda_j(\Gamma)=\sigma_j(\mathsf A)^2.
$$

The tested metrics are:

- $L^2$ source to full target-density $L^2$;
- $H^1$ source to target $L^2$, represented by dividing source column $k$ by
  $(1+\mu_{k,h})^{1/2}$; and
- $L^2$ source to target $H^{-1/2}$, represented by multiplying target row
  $\ell$ by $(1+\mu_{\ell,h})^{-1/4}$.

Chart scalars are $n^{-1/2}$ in the lattice chart,
$\sqrt\varepsilon$ in the resolved chart, and $t^{1/4}$ in atomic and
boundary charts. They compare amplitudes but do not alter condition numbers.

## 3. Exact phase-limit Gram kernels

This section concerns **phase-limit Grams**, not arbitrary pre-collapse
finite-time Grams.

For $V(x)=1+gx$, put

$$
F_k(s)=\int_0^1e^{-sV(x)}\phi_k(x)\,dx.
$$

After interchanging source and target integrals, every limiting Gram has form

$$
\Gamma_{jk}=\int_0^1\!\int_0^1
\phi_j(x)\Phi(V(x)+V(y))\phi_k(y)\,dx\,dy.
$$

Writing $A=V(x)+V(y)$, the four kernels are

$$
\begin{aligned}
\Phi_q^{\mathrm{res}}(A)
  &=\frac{1}{2\sqrt\pi\sqrt{1+qA}},\\
\Phi^{\mathrm{atom}}(A)
  &=\frac{1}{2\sqrt{\pi A}},\\
\Phi_\tau^{\mathrm{lat}}(A)
  &=e^{-2\tau A}I_0(2\tau A),\\
\Phi_\kappa^{\partial}(A)
  &=\frac{1+e^{-\kappa^2/A}}{2\sqrt{\pi A}}.
\end{aligned}
$$

The first two follow from Gaussian target-frequency integration. The lattice
formula follows from
$4\sin^2(\pi\xi/2)=2(1-\cos\pi\xi)$ and the integral representation of
$I_0$. The boundary multiplier follows by integrating
$1+\cos(2\pi\kappa u)$.

An independent control compares these two-dimensional kernel Grams with
direct one-dimensional integrals of $F_jF_k$. At 100 decimal digits, maximum
relative discrepancies across the four charts were between
$1.6\times10^{-98}$ and $7.1\times10^{-99}$.

These identities do not provide a finite-$h$, growing-$K$ remainder estimate.

## 4. High-precision early singular fan

The phase Grams were assembled using 64-point, 100-digit Gauss--Legendre
quadrature and diagonalized at the same precision. For
$K=4$ and $q=0.02,0.01,0.005,0.0025$:

| singular direction | predicted power | fitted power | last dyadic power |
|---:|---:|---:|---:|
| 1 | 1 | 0.97185 | 0.98751 |
| 2 | 2 | 1.94933 | 1.97752 |
| 3 | 3 | 2.92680 | 2.96753 |
| 4 | 4 | 3.90424 | 3.95753 |

The Gram determinant has predicted power $K(K+1)=20$. Its four-point fit was
$19.5044$ and its last dyadic power was $19.7802$.

The numerical mechanism is the multiplication-moment flag

$$
E_{rk}=\frac{(-1)^r}{r!}\int_0^1V(x)^r\phi_k(x)\,dx,
\qquad 1\leq r,k\leq K.
$$

Successive source combinations cancel the first $0,1,\ldots,K-1$ moments.
The companion theorem proves the flag for every fixed $K$. A useful diagonal
$K=K(h)$ result still needs quantitative lower bounds on its constants and
uniform control of higher and mixed terms.

### Double precision creates false nulls

For $K=10$, every high-precision phase Gram was positive definite:

| chart | high-precision positive rank | double numerical rank |
|---|---:|---:|
| balanced resolved, $q=1$ | 10 | 6 |
| atomic | 10 | 7 |
| one-cell lattice, $\tau=1$ | 10 | 6 |
| boundary atomic, $\kappa=1$ | 10 | 7 |

The smallest double Gram eigenvalues were slightly negative, around
$10^{-24}$, not genuine negative or zero directions.

## 5. Critical fan and dimension staircase

Along

$$
\varepsilon=h^\alpha,\qquad t=h^2,\qquad q=h^{2-2\alpha},
$$

the physical singulars have early prediction

$$
\varepsilon^{-1/2}\sigma_j(q)
\asymp h^{2j-\alpha(2j+1/2)}.
$$

The exponent vanishes at $\alpha_j=4j/(4j+1)$:

| $j$ | $\alpha_j$ | predicted $h$-power | fitted $h$-power |
|---:|---:|---:|---:|
| 1 | 0.800000 | 0 | -0.011260 |
| 2 | 0.888889 | 0 | -0.011260 |
| 3 | 0.923077 | 0 | -0.011262 |
| 4 | 0.941176 | 0 | -0.011266 |

The small common bias is consistent with finite-$q$ pre-asymptotics.

At $\alpha=0.9$, predicted powers for $j=1,2,3,4$ are
$-0.25,-0.05,0.15,0.35$; fits were
$-0.2556,-0.0601,0.1354,0.3308$. The operational dimension rises one
singular direction at a time.

## 6. Balanced and atomic compactness

| $K$ | balanced $\sigma_{\min}$ | ratio | atomic $\sigma_{\min}$ | ratio |
|---:|---:|---:|---:|---:|
| 7 | $1.5047\times10^{-10}$ | 0.044735 | $1.4077\times10^{-9}$ | 0.060846 |
| 8 | $6.7225\times10^{-12}$ | 0.044676 | $8.5548\times10^{-11}$ | 0.060771 |
| 9 | $3.0006\times10^{-13}$ | 0.044635 | $5.1942\times10^{-12}$ | 0.060717 |
| 10 | $1.3385\times10^{-14}$ | 0.044607 | $3.1518\times10^{-13}$ | 0.060679 |

This is evidence over $K\leq10$, not an all-$K$ asymptotic.

For $K=10$, effective ranks at declared relative noise floors were:

| relative noise | balanced rank | atomic rank |
|---:|---:|---:|
| $10^{-2}$ | 2 | 2 |
| $10^{-4}$ | 3 | 4 |
| $10^{-6}$ | 5 | 6 |
| $10^{-8}$ | 6 | 7 |
| $10^{-10}$ | 8 | 9 |
| $10^{-12}$ | 9 | 10 |

Effective rank is metric-, protocol-, and noise-dependent.

### Conditional logarithmic band scale

If $\sigma_{\min}(K)\asymp\rho^K$ continues and finite approximation error is
$h^p$, resolving the smallest direction requires roughly

$$
K < \frac{p}{|\log\rho|}\log n.
$$

Against an $h^2$ floor, the observed $K=10$ thresholds are about
$n=8.64\times10^6$ balanced and $n=1.78\times10^6$ atomic. This supports
$K=o(\log n)$ as a conservative target, conditional on a singular lower
bound and uniform finite error estimate.

## 7. Finite source-diffusion cutoff

The multiplication-only reference retains the finite target symbol,
preparation, ramp samples, and source cosines, but replaces

$$
e^{-\tau(L_n+\omega_{\ell,h}V_h)}
\quad\text{by}\quad
e^{-\tau\omega_{\ell,h}V_h}.
$$

It isolates source diffusion from target quadrature and symbol error.

For fixed $K=2$:

| $n$ | physical $\delta_{2,h}$ | resolved | atomic | boundary | lattice error |
|---:|---:|---:|---:|---:|---:|
| 63 | 0.62612 | 0.25007 | 0.25172 | 0.25012 | $1.483\times10^{-3}$ |
| 127 | 0.31079 | 0.13771 | 0.13841 | 0.13776 | $3.665\times10^{-4}$ |
| 255 | 0.15481 | 0.07261 | 0.07307 | 0.07257 | $9.109\times10^{-5}$ |

The lattice column uses $\tau=0.3$ and therefore much smaller
$\delta_{2,h}$. At small $\delta$, last-port error is approximately
$\delta/2$.

Hostile growing bands retain nonzero error:

- $K\approx0.25\sqrt n$, $t=1/n$: $\delta_K$ stays near $0.65$ and
  resolved, atomic, and boundary last-port errors stay between $0.250$ and
  $0.280$.
- $K\approx0.30n$, $\tau=0.3$: $\delta_K$ stays near $0.245$ and lattice
  last-port error stays near $0.113$.

Whole-band operator error can still be small because the inaccurate high port
has weak output. Absolute operator error, column-relative error, and inverse
stability are inequivalent.

### Mixed causal words

For the $K$th early direction, source diffusion produces an adversarial
relative scale

$$
\boxed{\frac{tK^2}{q^{K-1}}}.
$$

Preparation moments or $K\varepsilon$ alone do not control it. At the
critical fan it falls quickly with nominal $n$, but
$\varepsilon/h=n^{1/(4K+1)}$ grows extremely slowly. For $K=8$, even
$n=10^{12}$ gives only $\varepsilon/h=2.31$ and $q=0.187$. These are scale
diagnostics, not simulations of trillion-cell grids or a proved remainder.

A future theorem must control:

1. $t\mu_{K,h}$;
2. $tK^2/q^{K-1}$ in the smallest early direction;
3. preparation moment leakage at the same $q^K$ scale; and
4. the singular gap against discretization error.

## 8. Column obstruction and weighted metrics

For every $K$-column operator,

$$
\sigma_{\min}(\mathsf A_K)\leq\|\mathsf A_Ke_K\|.
$$

The ramp profile has a $k^{-2}$ column envelope. In $H^s$ unit-source
coordinates, source weighting adds $k^{-s}$. Fits over
$16\leq k\leq64$ at $n=511$ were:

| chart | $L^2$ odd/even powers | $H^1$ odd/even powers |
|---|---:|---:|
| lattice | -2.00443 / -2.00434 | -2.99994 / -2.99990 |
| resolved | -2.00436 / -2.00413 | -2.99986 / -2.99969 |
| atomic | -2.00424 / -2.00386 | -2.99975 / -2.99942 |
| boundary endpoint | -2.00424 / -2.00386 | -2.99975 / -2.99942 |

Thus a $K$-uniform lower frame bound already fails at the column level.
Column correlation makes the actual smallest singular decay much faster.

A five-time finite protocol at $n=127$ illustrates this:

| chart | $K=2$, $L^2\to L^2$ | $K=10$, $L^2\to L^2$ |
|---|---:|---:|
| lattice | $5.232\times10^{-4}$ | $6.892\times10^{-11}$ |
| resolved | $5.750\times10^{-4}$ | $1.400\times10^{-8}$ |
| atomic | $1.361\times10^{-3}$ | $3.979\times10^{-8}$ |
| boundary endpoint | $2.016\times10^{-3}$ | $9.548\times10^{-8}$ |

The $H^1\to L^2$ and $L^2\to H^{-1/2}$ calibrations also collapse.

## 9. Moment preconditioning is not free

At $K=4,\ q=0.005$, the raw early response condition number was
$1.85\times10^9$. The inverse moment basis reduced it to
$6.06\times10^5$; formal $q^{-j}$ rescaling reduced it to
$5.20\times10^2$.

That apparent cure required source $L^2$ column norms

$$
1.31\times10^6,\quad
5.74\times10^8,\quad
1.66\times10^{11},\quad
2.37\times10^{13}.
$$

After unit-$L^2$ normalization, the condition returned to
$1.37\times10^6$. Moment coordinates expose the flag but do not remove its
operational cost.

## 10. Boundary and finite-sampling controls

For a four-port, three-time atomic protocol, endpoint/interior largest
singular-value ratios were

$$
1.36849\ (n=63),\qquad
1.38316\ (n=127),\qquad
1.41279\ (n=255).
$$

The last is within $0.00143$ of $\sqrt2$, as predicted by the doubled endpoint
squared constant.

If only $M$ scalar modal samples are kept, the response is $M\times K$, so

$$
\operatorname{rank}\Gamma\leq M,
\qquad
\operatorname{nullity}\Gamma\geq K-M.
$$

For $K=8$ and $M=1,2,4,6,8$, floating ranks were exactly
$1,2,4,6,8$. Forced Gram-null residuals stayed below
$2.2\times10^{-23}$. A finite-sensor theorem must respect this exact cap.

## 11. Exact and adversarial controls

| control | residual/result |
|---|---:|
| modal versus dense $n^2$ model | $2.70\times10^{-16}$ maximum |
| relative dense/modal Frobenius error | $1.13\times10^{-14}$ |
| Gram eigenvalues versus squared singulars | $2.17\times10^{-19}$ maximum |
| explicit $t=0$ nonconstant response | exactly 0 in code |
| constant-modulation null | $2.84\times10^{-15}$ maximum |
| symmetric-modulation odd-port null | $1.33\times10^{-15}$ maximum |
| minimum symmetric even-port column norm | $1.44\times10^{-3}$ |

The underlying exact statements are algebraic: target-mode separation,
$\Gamma=\mathsf A^*\mathsf A$, the time-zero null, the constant-modulation
null, and the reflection-odd/symmetric null.

## 12. Evidence and proof boundaries

- The four $\Phi$ formulas are exact **phase-limit** Gram identities.
- The finite modal reduction, Gram identity, finite-sampling cap, and declared
  nulls are exact finite statements.
- Early powers, determinant power, geometric tails, fan fits, and effective
  ranks are high-precision numerical evidence.
- No floating numerical rank is promoted to exact rank.
- No $K$-uniform lower bound is claimed; the ramp column envelope rules it
  out in the phase-limit $L^2$ metric.
- The geometric factors are observed only for the analytic ramp over
  $K\leq10$.
- The source-diffusion collapse suggests $\delta_{K,h}\to0$, but sufficiency
  at the $q^K$ smallest-direction scale remains unproved.
- The conditional $K=o(\log n)$ recommendation requires both a singular lower
  bound and a uniform finite rate.
- None of these results describes physical spacetime or a fundamental
  information substrate.

## 13. Reproduction

~~~text
python -m pip install -r oig_ix_growing_band_requirements.txt
python -m py_compile oig_ix_growing_band.py test_oig_ix_growing_band.py
python -m unittest -v test_oig_ix_growing_band.py
python oig_ix_growing_band.py --fast
python oig_ix_growing_band.py
~~~

The full run uses NumPy/SciPy for the finite model and 100-decimal mpmath
arithmetic for phase-limit Grams. On the reference machine, 23 of 23 focused
tests pass and the full report completes in about five seconds.

## 14. Immediate continuation targets

The companion analytic and adversarial lanes close finite-$K$ positivity,
the common structural null, the causal flag, and the conditional diagonal
transfer theorem. The next quantitative tasks are:

1. bound $\sigma_{\min}(K)$ above and below in balanced and atomic charts;
2. certify moderate-$K$ lower bounds with interval or outward-rounded
   arithmetic;
3. sharpen the finite error beyond the conservative Sobolev bookkeeping and
   control the mixed-word constants;
4. combine those estimates into an explicit $K(h)$ schedule;
5. optimize several times and target profiles for noise-thresholded effective
   rank; and
6. extend the continuum theorem to finite sampling with $M\geq K$ and a
   quantitative sensor-frame certificate.

The milestone is concrete: determine how many source directions survive at a
declared resolution, chart, metric, sampling budget, and noise floor.
