# Arithmetic Sensing V

> **Later milestone:** the cancellation-aware common-numerator theorem in
> `ARITHMETIC_SENSING_V_ALL_ALIAS_OPTIMIZATION.md` shows that the degree-nine
> obstruction reported here was caused by a triangle-inequality proof loss.
> At the same resources, the updated sufficient certificate reaches degree
> thirteen. `ARITHMETIC_SENSING_V_END_TO_END.md` later certifies that frontier
> with Arb finite sums and an inverse-free Gram theorem. The results below
> remain the historical first log-Mellin layer.

## Exact continuum positivity, log-Mellin alias certificates, and the fixed-degree recovery boundary

- **Research lead and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** first exact-and-fixed-degree continuation complete
- **Date:** 13 August 2026
- **Companions:** `ARITHMETIC_SENSING_III.md`, `ARITHMETIC_SENSING_IV.md`

## Abstract

Arithmetic Sensing IV left two sharp technical boundaries. Its continuum
positivity certificate used floating-point Fejer--Riesz factors, and its
general fixed-degree tail theorem certified number fields only through degree
four; degree five produced a bound of `3.48969`, above the `1/2` integer-
rounding threshold.

This paper removes both boundaries. First, the displayed window coefficients
are interpreted exactly as rational numbers. After the substitution
`x=cos(theta)`, exact Sturm sequences prove

\[
10^{-5}<p(\theta)<2.499999995
\]

on the full circle. This is a symbolic rational certificate, independent of
the floating spectral factorization.

Second, the identity `d_d=1^{*d}` is used before estimating the remote tail.
The one-factor zeta mass is enclosed on logarithmic bins; ordinary convolution
then encloses the mass of ordered multiplicative `d`-tuples. Each product bin
is multiplied by a supremum of the exact periodic sampling kernel over the
entire interval where that product can lie. This log-Mellin certificate treats
every alias and avoids the coarse fixed-degree remote bound that dominated the
previous computation.

At `N=50`, `sigma=2`, `T=1000`, `m=5000`, and a million-term exact cutoff, the
same window now certifies every number field through degree eight. The worst
degree-five bound becomes `0.00775068`; degree eight gives `0.376281`; degree
nine gives `1.13679` and is not certified. At fixed `m/T=5`, degree nine first
crosses the threshold in the tested time grid between `T=2400` and `T=2450`,
where the bounds are `0.512317` and `0.498176`.

A degree-aware finite-band optimizer does not fix degree nine at `T=1000`:
larger harmonic models improve their training objective while slightly
worsening the complete certificate. A separate sensor-noise study brackets a
`10^-6` Gaussian rounding-failure target between 67,000 and 67,200 samples at
noise standard deviation `0.01`. Finally, the enriched `Q_2` channel from
Arithmetic Sensing IV is compressed to its first separating symmetric moment:
the second component-dimension moment is 22 versus 16, with adversarial
ambiguity radius 3.

The mathematical bin inequality and exact Sturm proof are distinct from the
reported floating computation. No result concerns zeta zeros, new axioms,
physics, or complete identification of a number field.

---

## 1. Why degree five appeared to fail

For a degree-`d` number field `K`, write

\[
\zeta_K(s)=\sum_{n\ge1}a_K(n)n^{-s}.
\]

The universal domination

\[
0\le a_K(n)\le d_d(n),
\qquad
\sum_{n\ge1}d_d(n)n^{-s}=\zeta(s)^d
\]

reduces the omitted-tail question to correlations weighted by `d_d(n)n^-s`.
Arithmetic Sensing IV enumerated these weights through one million, used
pre-alias kernel decay immediately afterward, and then paid an elementary
complete tail at half the first alias.

For degree five and target cutoff 50, an audit separates the terms:

| contribution | magnitude |
|---|---:|
| largest explicitly summed million-term kernel contribution | `1.107e-7` |
| unweighted `zeta(2)^5` remainder after one million | `4.103e-3` |
| old remote remainder at target 50 | `1.394e-3` |
| old final coefficient bound | `3.48969` |

The finite window was not the problem. The explicitly filtered mass was four
orders of magnitude smaller than the remote estimate. Re-optimizing the same
finite objective before repairing that theorem would therefore have attacked
the wrong term.

---

## 2. Exact rational positivity

The reference density is

\[
p(\theta)=1+2\sum_{r=1}^{8}c_r\cos(r\theta),
\]

with the decimal coefficient strings published in Arithmetic Sensing IV. This
section treats those strings as exact elements of `Q`, not binary floats.

Set `x=cos(theta)`. Since `cos(r theta)=T_r(x)`, where `T_r` is a Chebyshev
polynomial,

\[
P(x)=1+2\sum_{r=1}^{8}c_rT_r(x)\in\mathbb Q[x],
\qquad -1\le x\le1.
\]

Define

\[
F_-(x)=P(x)-10^{-5},
\qquad
F_+(x)=2.499999995-P(x).
\]

### Theorem A — exact reference-window bounds

Both `F_-` and `F_+` are strictly positive on `[-1,1]`. Consequently

\[
10^{-5}<p(\theta)<2.499999995
\]

for every real `theta`.

### Certificate

The executable proof constructs the exact rational Sturm sequence of each
polynomial. The sign-variation difference between `-1` and `1` is zero for
both sequences, so neither boundary polynomial has a root in the open
interval. Exact endpoint evaluation is nonzero, and exact evaluation at zero
is positive. Continuity then makes each polynomial positive on the entire
closed interval.

This certificate uses integer and rational arithmetic throughout. It is
logically independent of the Stage IV root-selected Fejer--Riesz factors and
does not require a numerical root tolerance. It certifies the displayed
rational vector; it does not assert that every floating optimizer output is
automatically exact.

The numerical experiments use the nearest binary64 representations of this
same decimal vector. Converting both vectors to exact rationals gives

\[
2\sum_{r=1}^8 |c_r^{\rm binary64}-c_r^{\rm decimal}|
<5.11\mathbin{\cdot}10^{-17}.
\]

This uniformly bounds the induced density perturbation, so the actual stored
binary64 window remains strictly positive with a lower bound greater than
`9.9999999999e-6`. Thus the exact positivity proof really does justify the
global kernel cap used by the floating reproduction.

---

## 3. Multiplicative mass as additive log geometry

The classical generalized divisor function satisfies

\[
d_d=\underbrace{1*\cdots*1}_{d\text{ Dirichlet convolutions}}.
\]

Equivalently, `d_d(k)` counts ordered tuples

\[
(n_1,\ldots,n_d)\in\mathbb N^d,
\qquad n_1\cdots n_d=k.
\]

Therefore

\[
\sum_k d_d(k)k^{-\sigma}f(\log k)
=\sum_{n_1,\ldots,n_d\ge1}
(n_1\cdots n_d)^{-\sigma}
f(\log n_1+\cdots+\log n_d).
\]

Multiplication has become addition in logarithmic coordinates. This permits a
finite positive convolution certificate without enumerating remote products.

### 3.1 One-factor bins

Fix a width `h>0` and define

\[
B_j=\{n\ge1:jh\le\log n<(j+1)h\},
\qquad
\beta_j=\sum_{n\in B_j}n^{-\sigma}.
\]

Let `hat(beta)_j >= beta_j` be any certified upper mass. The implementation
enumerates integers through one million exactly at the coefficient level.
Above that cutoff it uses monotonicity: for integer endpoints `A<=B`,

\[
\sum_{n=A}^{B}n^{-\sigma}
\le A^{-\sigma}+\int_A^B x^{-\sigma}\,dx.
\]

The chosen floor/ceiling endpoints intentionally overlap possible boundary
integers; an integer is never lost to floating boundary placement.

### 3.2 Tuple convolution

Let

\[
C^{(d)}=\hat\beta^{*d}
\]

be ordinary additive convolution of the bin-index sequence. If the individual
factor-bin indices sum to `q`, then

\[
qh\le\log(n_1\cdots n_d)<(q+d)h.
\]

Thus `C_q^(d)` bounds all `d_d(k)k^-sigma` mass carried by tuples whose
product may occur in this expanded interval.

---

## 4. The all-alias log-Mellin certificate

Let `K(omega)` be the exact positive cosine-window midpoint kernel and let `M`
be the explicit coefficient cutoff. For target norm `n`, define

\[
\mathcal K_{q,n}
=\sup_{\omega\in[qh-\log n,(q+d)h-\log n]}|K(\omega)|.
\]

The interval supremum is bounded by the shifted sine-quotient theorem from
Arithmetic Sensing IV, with the positive-quadrature cap `|K|<=1`. It remains
valid at every exact grid alias.

### Theorem B — fixed-degree log-Mellin alias bound

Choose a remote product-log cutoff `R`. Then

\[
\begin{aligned}
&\sum_{k>M}d_d(k)k^{-\sigma}
|K(\log(k/n))|\\
&\quad\le
\sum_{q:(q+d)h>\log(M+1)}
C_q^{(d)}\mathcal K_{q,n}
+\mathcal R_d(e^R),
\end{aligned}
\]

where only bins with `qh<R` are retained in the finite sum and

\[
\mathcal R_d(e^R)
\le\sigma\int_{e^R}^{\infty}
t^{-\sigma}(1+\log t)^{d-1}\,dt.
\]

### Proof

Expand `d_d` as its ordered factor tuples and assign every factor to a log bin.
For a fixed index sum `q`, the product logarithm lies in the stated expanded
interval, so replace the kernel by its interval supremum and the exact tuple
mass by `C_q^(d)`. Include every bin whose upper edge crosses the finite cutoff.
Products beyond `e^R` are bounded by the complete fixed-degree tail. Bins
crossing either boundary are counted on both sides, which is harmless for an
upper bound. Summing the nonnegative terms proves the claim. QED.

### Numerical realization

The direct convolutions use only positive terms. At each dot product the code
inflates by the standard `gamma_(2m+1)` round-to-nearest bound and also applies
a declared `10^-10` one-factor safety multiplier. This gives a deliberately
conservative IEEE floating certificate. The theorem itself is exact; a future
outward-rounded interval implementation would strengthen the computational
realization to a formal numerical proof.

---

## 5. Resolution continuation

The reference degree-five calculation was repeated while halving the log-bin
width. Every row includes the same million-term exact finite sum.

| bin width `h` | bins | worst coefficient bound |
|---:|---:|---:|
| 0.1000 | 825 | `9.29811e-3` |
| 0.0500 | 1650 | `8.43212e-3` |
| 0.0200 | 4123 | `7.97826e-3` |
| 0.0100 | 8246 | `7.75068e-3` |
| 0.0050 | 16491 | `7.63160e-3` |
| 0.0025 | 32981 | `7.59371e-3` |

The bound improves monotonically under this continuation and is below `0.01`
even at the coarsest resolution. The published cross-degree comparison uses
`h=0.01`, not an extrapolated zero-width limit.

---

## 6. The new fixed-degree boundary

Using the unchanged continuum-certified Stage IV window at

```text
N=50, sigma=2, T=1000, m=5000, M=1000000, h=0.01
```

gives:

| degree | unweighted remainder after `10^6` | complete bound | integer rounding? |
|---:|---:|---:|:---:|
| 2 | `1.59699e-5` | `4.53793e-5` | yes |
| 3 | `1.37121e-4` | `2.95596e-4` | yes |
| 4 | `8.39449e-4` | `1.64447e-3` | yes |
| 5 | `4.10333e-3` | `7.75068e-3` | yes |
| 6 | `1.70159e-2` | `3.16410e-2` | yes |
| 7 | `6.21442e-2` | `1.14647e-1` | yes |
| 8 | `2.04982e-1` | `3.76281e-1` | yes |
| 9 | `6.21746e-1` | `1.13679` | no |
| 10 | `1.75759` | `3.20149` | no |

The fixed-degree envelope therefore certifies recovery of the first 50 ideal-
counting coefficients for every number field of degree at most eight under the
stated noiseless model. It does not identify the field up to isomorphism.

For degree two, the general log-Mellin value is slightly sharper than the
quadratic-specific Stage IV value `4.56318e-5`. More importantly, the degree-
five result changes from a failed `3.48969` to a successful `0.00775068`, and
the success frontier advances through degree eight.

Degree nine is a certificate failure, not an impossibility theorem.

---

## 7. Degree-aware optimization: a falsification result

The finite LP was generalized to accept any nonnegative coefficient envelope,
so `d_9` rather than `d_2` can weight its objective. At `T=1000`, `m=5000`,
and design cutoff 150:

| window | finite objective | complete degree-nine bound |
|---|---:|---:|
| reused Stage IV `H=8` | — | `1.13679` |
| degree-nine `H=8` | `1.60730e-3` | `1.13675` |
| degree-nine `H=10` | `4.21420e-4` | `1.13964` |
| degree-nine `H=12` | `2.47406e-4` | `1.14254` |

The training objective improves by 6.5 times from `H=8` to `H=12`, while the
complete certificate worsens. This rejects the hypothesis that more harmonics
or a degree-aware short tail automatically crosses the degree-nine boundary.
The missed mass lives in held-out log-product bands and aliases, not in the
finite design objective.

---

## 8. Crossing degree nine by observation time

The Stage IV coefficient vector was reused at fixed sampling ratio `m/T=5`.
No re-optimization was performed in this scan.

| `T` | `m` | `lambda_min` | degree-nine bound | certified? |
|---:|---:|---:|---:|:---:|
| 1000 | 5000 | 0.981821 | `1.13679` | no |
| 1250 | 6250 | 0.984514 | `1.82043` | no |
| 1500 | 7500 | 0.997785 | `0.973624` | no |
| 1750 | 8750 | 0.999117 | `0.694505` | no |
| 2000 | 10000 | 0.999098 | `0.568565` | no |
| 2300 | 11500 | 0.999172 | `0.533458` | no |
| 2400 | 12000 | 0.999387 | `0.512317` | no |
| 2450 | 12250 | 0.999520 | `0.498176` | yes |
| 2500 | 12500 | 0.999649 | `0.483062` | yes |
| 3000 | 15000 | 0.999996 | `0.378576` | yes |

The first certified point on this declared grid is `T=2450`. The initial rise
at `T=1250` is important: finite arithmetic frequencies move through window
sidelobes, so the bound is not a simple monotone power law at every time.

---

## 9. Tail budget versus noise budget

Arithmetic Sensing IV suggested choosing `m/T` close to the alias-safety
threshold when deterministic tail cost is the only objective. Sensor noise has
a different scaling: more weighted samples reduce the exact post-inversion
covariance even after the tail floor has stabilized.

At `T=1000`, quadratic fields, circular complex Gaussian sensor noise
`nu=0.01`, and the reference window:

| samples `m` | effective samples | complete tail | Gaussian failure bound |
|---:|---:|---:|---:|
| 50,000 | 27,596 | `4.52711e-5` | `5.13135e-5` |
| 60,000 | 33,115 | `4.53049e-5` | `5.13622e-6` |
| 67,000 | 36,979 | `4.53183e-5` | `1.03928e-6` |
| 67,200 | 37,089 | `4.53234e-5` | `9.93035e-7` |
| 70,000 | 38,635 | `4.53294e-5` | `5.25417e-7` |
| 80,000 | 44,154 | `4.53541e-5` | `5.45974e-8` |
| 100,000 | 55,192 | `4.54167e-5` | `6.08864e-10` |

Thus the tested `10^-6` target is bracketed between 67,000 and 67,200 raw
samples. This yields a two-budget design rule:

1. choose enough `m/T` to place aliases behind the certified arithmetic tail;
2. add samples, if needed, to meet the sensor-noise probability budget.

The small nonmonotonic changes in the deterministic tail are retained rather
than rounded into a false constant.

---

## 10. Compressing the enriched local channel

For the Perlis pair generated by `x^8-33` and `x^8-528`, Arithmetic Sensing IV
used the `Q_2` component-dimension multisets

\[
(1,1,2,4),\qquad(2,2,2,2).
\]

Define symmetric power moments

\[
M_r=\sum_v [K_v:\mathbb Q_2]^r.
\]

The first values are

| order `r` | first field | second field |
|---:|---:|---:|
| 0 | 4 | 4 |
| 1 | 8 | 8 |
| 2 | 22 | 16 |

The zeroth and first moments collide because both local algebras have four
components and total dimension eight. The second moment is the first symmetric
power-moment separator. As a scalar deterministic response it has distance 6,
so the midpoint/two-ball ambiguity radius is 3. Absolute adversarial error
strictly below 3 permits nearest-template separation of this pair.

This is an oracle-level local invariant. It is not yet a method for estimating
local component dimensions from raw measurements and should not be described
as a physical sensor.

---

## 11. What is proved, computed, and rejected

### Proved exactly

- rational power-basis conversion of the published cosine density;
- zero-root Sturm certificates for both declared continuum boundaries;
- the log-bin convolution theorem from the ordered-factorization identity;
- validity of multiplying each tuple bin by a whole-interval periodic-kernel
  supremum;
- the second local component-dimension moment is the first power-moment
  separator for the explicit Perlis pair.

### Computed with declared numerical safeguards

- direct positive log-bin convolutions with roundoff inflation;
- million-term fixed-degree coefficient sieves and exact kernel evaluations;
- the degree 2--10 boundary table and bin-resolution continuation;
- the degree-nine time scan and degree-aware LP falsification;
- exact Gram spectra, noise covariance, and Gaussian union bounds.

### Rejected or not established

- the Stage IV conclusion that degree four was the practical boundary;
- the idea that more finite-band harmonics necessarily improve the global
  certificate;
- monotonic improvement at every observation time;
- impossibility of degree-nine recovery at `T=1000`;
- a raw-data acquisition procedure for the local moment;
- any claim about the Riemann hypothesis, zeta zeros, physical law, or new
  axioms of number.

---

## 12. Next targets

1. **Completed in the verified-Mellin milestone:** replace the declared
   floating safety inflation in the log-Mellin bins by outward-rounded MPFR
   arithmetic, exact dyadic convolution, and a compact checker artifact. See
   `ARITHMETIC_SENSING_V_VERIFIED_MELLIN.md`.
2. Optimize the actual all-alias log-Mellin objective, not a short integer-tail
   surrogate, and retest degree nine at `T=1000`.
3. Determine whether a non-midpoint schedule or a larger density cap crosses
   degree nine without lengthening `T`, while preserving noise cost explicitly.
4. Derive analytic degree/time/sample scaling rather than relying on a finite
   degree table.
5. Find trace or ramification measurements from which local component moments
   can be stably inferred; retain zeta-equivalent controls.
6. Bring arithmetic acceleration back as a decoding layer: multiplicative
   consistency may reduce the sensor precision needed once coefficientwise
   bounds approach, but do not individually cross, `1/2`.

The separate Operational Information Geometry project may later reuse these
distinguishability and stability tools. No conclusion should flow in the other
direction until its toy models survive matched random controls.

---

## 13. Reproduction

Exact rational positivity, the degree-five reference certificate, and the
quantitative local channel:

```text
python arithmetic_sensing_v.py
```

The larger studies are opt-in:

```text
python arithmetic_sensing_v.py --degree-study
python arithmetic_sensing_v.py --bin-study
python arithmetic_sensing_v.py --degree-aware-study
python arithmetic_sensing_v.py --degree-nine-time-study
python arithmetic_sensing_v.py --noise-study
python arithmetic_sensing_v.py --all
python -m unittest discover -v
```

All computations in this manuscript used the local machine. The Windows
computer was not required.

The post-manuscript formal remote-tail checker is:

```text
python verify_mellin_certificate.py
```

---

## 14. Sources and novelty boundary

- The generalized divisor identity `d_d=1^{*d}` and its interpretation as
  ordered factorization are classical. A recent explicit treatment is
  A. Fink, “Multifactorisations and divisor functions,” *Utilitas Mathematica*
  125 (2025), 43--60,
  [article](https://combinatorialpress.com/um-articles/vol-125/multifactorisations-and-divisor-functions/).
- Sturm's theorem, Chebyshev polynomials, Dirichlet convolution, and integral
  comparison for decreasing series are standard exact ingredients.
- Fejer--Riesz remains the spectral interpretation used in Arithmetic Sensing
  IV. For exact Hermitian-square methods over algebraic coefficient fields, see
  V. Magron et al., “Exact SOHS decompositions of trigonometric univariate
  polynomials with Gaussian coefficients,”
  [arXiv:2202.06544](https://arxiv.org/abs/2202.06544).
- R. Perlis, “On the equation `zeta_K(s)=zeta_K'(s)`,” *Journal of Number
  Theory* 9 (1977), 342--360,
  [doi:10.1016/0022-314X(77)90070-1](https://doi.org/10.1016/0022-314X(77)90070-1).
- A. Angelakis, *Universal Adelic Groups for Number Fields* (2015), Example
  1.4.1, supplies the stated `Q_2` decompositions,
  [PDF](https://www.math.u-bordeaux.fr/~ybilu/algant/documents/PhD_theses/Athanasios.pdf).

The classical ingredients are not claimed as new. The project-level
contribution is their combination into an exact continuum checker, a finite
all-alias log-Mellin sensing certificate, the resulting degree boundary and
resource studies, and the minimal symmetric local-moment formulation. No
literature-priority claim is made without independent peer review.
