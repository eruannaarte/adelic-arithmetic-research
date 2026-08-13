# Arithmetic Sensing II

## Deterministic tapered quadrature, alias-safe certificates, and exact limits

**Status:** proved computational theorem layer with explicit scope boundaries  
**Date:** 12 August 2026  
**Companion to:** `ARITHMETIC_SENSING.md`

## Abstract

The first arithmetic-sensing theorem used independent uniform sample times.
That made the finite Gram matrix random and forced a simultaneous Bernstein
budget for the omitted Dirichlet tail. At `N=50`, `sigma=2`, it produced a
complete quadratic-field certificate at `T=10,000` with 500,000 samples and a
5% design-failure budget.

This continuation replaces random sampling by a weighted midpoint quadrature.
For a Hann taper, the target Gram matrix and every target-tail correlation are
then exact finite sums. The sampling-failure event disappears. A new
alias-aware divisor-tail estimate controls the part beyond a finite
truncation, including all remote grid aliases. The result is a deterministic
complete-tail certificate at

```text
N=50, sigma=2, T=1,000, m=5,000:
worst coefficient bias <= 0.02718449 < 1/2.
```

At 100,000 sensor readings and circular complex Gaussian noise of standard
deviation `0.01`, the same design gives a rounding-failure bound

```text
8.84 * 10^-11.
```

Thus the new construction uses one tenth of the observation window and one
fifth of the samples used by the earlier random certificate, while replacing
its 5% random-design budget by a deterministic design. This is a theorem about
the stated sensing model, not a claim of optimality.

The negative side is developed in parallel. Nearby normalized integer
Dirichlet polynomials give an explicit positive noise radius at which uniform
recovery is impossible. At the arithmetic-object level, Perlis' classical
degree-eight examples give nonisomorphic number fields with exactly identical
Dedekind zeta functions, proving that complete aggregate zeta data cannot
identify a field up to isomorphism.

## 1. Model

Let

\[
F_K(\sigma+it)=\sum_{k\geq 1}a_K(k)k^{-\sigma}e^{-it\log k},
\qquad \sigma>1,
\]

where `a_K(k)` counts ideals of norm `k`. Fix a recovery cutoff `N`, sample
times `t_j`, and nonnegative weights `w_j` with

\[
\sum_{j=0}^{m-1}w_j=1.
\]

Define

\[
\Phi_{j,n}=e^{-it_j\log n},\qquad
W=\operatorname{diag}(w_0,\ldots,w_{m-1}),\qquad
G=\Phi^*W\Phi.
\]

Writing

\[
x_n=a_K(n)n^{-\sigma},\qquad 1\leq n\leq N,
\]

the observations decompose as

\[
y=\Phi x+r+\eta,
\]

where `r` is the complete omitted tail and `eta` is sensor noise. Weighted
least squares is

\[
\widehat x=G^{-1}\Phi^*Wy.
\]

The recovered integer coefficients are

\[
\widehat a=D_\sigma\widehat x,
\qquad
D_\sigma=\operatorname{diag}(1^\sigma,\ldots,N^\sigma).
\]

## 2. Why the direct random-concentration idea did not close

The natural proposed improvement to Arithmetic Sensing I was to concentrate
the recovered tail error

\[
D_\sigma G^{-1}A^*r
\]

directly, rather than first bounding every coordinate of `A^*r` and then
applying `|G^{-1}|`. For ordinary empirical least squares, however, both
`G^{-1}` and `A^*r` are functions of the same random times. Treating
`G^{-1}` as fixed inside a vector Bernstein inequality is invalid. A correct
proof would require a self-normalized, leave-one-out, or sample-splitting
argument. None of the immediate substitutions rigorously improved the bound.

This is not an impossibility theorem for sharper random concentration. It is a
dependency obstruction to the simple proof that had been proposed. The
deterministic quadrature below removes the dependent random objects entirely.

## 3. Exact weighted-quadrature identity

### Theorem A — deterministic recovered-error formula

If `G` is invertible, then

\[
\widehat a-a
=D_\sigma G^{-1}\Phi^*W(r+\eta).
\]

For the noiseless tail, define the exact design kernel

\[
K_w(\omega)=\sum_{j=0}^{m-1}w_j e^{it_j\omega}.
\]

Then the `ell`th weighted target-tail correlation is

\[
u_\ell
=\sum_{k>N}a_K(k)k^{-\sigma}
K_w\!\left(\log\frac{\ell}{k}\right),
\]

and

\[
\widehat a-a=D_\sigma G^{-1}u
\]

before sensor noise.

**Proof.** Substitute `y=Phi x+r+eta` into the weighted normal equations.
Expanding `Phi^*Wr` gives the kernel formula. No probability is involved.

## 4. Midpoint and Hann kernels

Take midpoint times

\[
t_j=\left(j+\frac12\right)\frac{T}{m},
\qquad 0\leq j<m.
\]

For uniform weights `w_j=1/m`, put `u=T omega/2`. The kernel is exactly

\[
K_{U,m}(\omega)
=e^{iu}\frac{\operatorname{sinc}(u)}
{\operatorname{sinc}(u/m)},
\qquad \operatorname{sinc}(v)=\frac{\sin v}{v}.
\]

This formula exposes the discrete aliases at

\[
\omega=\frac{2\pi qm}{T},\qquad q\in\mathbb Z.
\]

The normalized midpoint Hann weights are

\[
w_j=\frac{1-\cos(2\pi t_j/T)}{m}.
\]

With `Omega=2pi/T`, their exact kernel is

\[
K_{H,m}(\omega)
=K_{U,m}(\omega)
-\frac12K_{U,m}(\omega+\Omega)
-\frac12K_{U,m}(\omega-\Omega).
\]

For `m>=3`, their effective sample count is

\[
m_{\mathrm{eff}}
=\frac{1}{\sum_jw_j^2}=\frac{2m}{3}.
\]

The taper therefore pays a factor `3/2` in independent sensor-noise variance,
but it strongly suppresses the boundary leakage that dominates uniform
sampling.

## 5. A complete alias-safe quadratic tail certificate

For every quadratic number field,

\[
0\leq a_K(k)\leq \tau(k),
\]

where `tau` is the ordinary divisor function. Let

\[
R_M(\sigma)
=\sum_{k>M}\tau(k)k^{-\sigma}
=\zeta(\sigma)^2-\sum_{k\leq M}\tau(k)k^{-\sigma}.
\]

### Lemma B — elementary remote divisor tail

For `X>=1` and `sigma>1`, write `L=log X`. Then

\[
\sum_{k>X}\tau(k)k^{-\sigma}\leq E_\sigma(X),
\]

where

\[
E_\sigma(X)
=X^{1-\sigma}\left(1+\frac{1+L}{\sigma-1}\right)
+\zeta(\sigma)
\left(X^{-\sigma}+\frac{X^{1-\sigma}}{\sigma-1}\right).
\]

**Proof.** Expand `tau(k)` as the number of factorizations `k=ab`. Split the
double sum at `a<=X` and `a>X`, then apply the integral bound to each decreasing
`b^{-sigma}` or `a^{-sigma}` tail. The harmonic sum is bounded by
`1+log X`.

### Lemma C — pre-alias kernel bounds

If

\[
0<|\omega|\leq \frac{\pi m}{T},
\]

then

\[
|K_{U,m}(\omega)|\leq \frac{\pi}{T|\omega|}.
\]

If additionally

\[
\Omega<|\omega|\leq\frac{\pi m}{T}-\Omega,
\]

then

\[
|K_{H,m}(\omega)|
\leq\frac{2\pi}{T(|\omega|-\Omega)}.
\]

**Proof.** In the half-alias region,
`|sinc(u/m)|>=2/pi`. Combine this with
`|sinc(u)|<=1/|u|`. The Hann estimate follows by applying the uniform bound to
its three shifted kernels and summing the coefficients `1+1/2+1/2=2`.

### Theorem D — deterministic complete-tail rounding certificate

Fix a finite truncation `M>N`. Define

\[
b_\ell^{(M)}
=\sum_{N<k\leq M}\tau(k)k^{-\sigma}
\left|K_w\!\left(\log\frac{\ell}{k}\right)\right|
+\rho_\ell(M).
\]

The universally valid choice is `rho_ell=R_M`. For the Hann grid, let

\[
L_\ell=\frac{\pi m}{T}-\Omega,
\qquad X_\ell=\ell e^{L_\ell}.
\]

If

\[
\log\frac{M+1}{\ell}<L_\ell
\quad\text{and}\quad
\log\frac{M+1}{\ell}>\Omega,
\]

the sharper alias-safe choice is

\[
\rho_\ell(M)=
\min\left\{
R_M,
\frac{2\pi R_M}
{T(\log((M+1)/\ell)-\Omega)}
+E_\sigma(X_\ell)
\right\},
\]

with the displayed kernel factor capped at one when necessary.

Let

\[
B_n=n^\sigma\sum_{\ell=1}^N
|(G^{-1})_{n\ell}|b_\ell^{(M)}.
\]

Then every quadratic field satisfies

\[
|\widehat a_n-a_K(n)|\leq B_n
\]

in the absence of sensor noise. In particular, if

\[
\max_{n\leq N}B_n<\frac12,
\]

rounding the real parts recovers all first `N` integer coefficients exactly.

**Proof.** The finite sum follows from `a_K(k)<=tau(k)` and the triangle
inequality. Before the half-alias frequency, Lemma C controls the unenumerated
kernel by its value at `M+1`; beyond that point Lemma B controls all mass even
at remote aliases. Applying the exact error identity and `|G^{-1}|` gives
`B_n`.

The remote term is essential. A discrete grid has infinitely many aliases, so
blindly replacing its kernel by the continuous Hann transform would not prove
an infinite-tail result.

## 6. Independent Gaussian sensor noise

Assume independent circular complex noise with

\[
\mathbb E\eta\eta^*=\nu^2I.
\]

### Theorem E — exact weighted-noise covariance and rounding bound

Set

\[
C=D_\sigma G^{-1}\Phi^*W^2\Phi G^{-1}D_\sigma.
\]

The coefficient-noise covariance is exactly `nu^2 C`. If every `B_n<1/2`,
then

\[
\Pr(\text{any real-part rounding error})
\leq
2\sum_{n=1}^N
\exp\left(
-\frac{(1/2-B_n)^2}{\nu^2 C_{nn}}
\right).
\]

This is the only probability in the deterministic design theorem. It concerns
physical measurement noise, not whether the chosen sampling matrix happened
to be well conditioned.

## 7. Certified experiments

All complete-tail bounds below use `M=1,000,000`; the remaining tail and every
remote alias are covered analytically.

### Uniform versus Hann at the same resources

Parameters: `N=50`, `sigma=2`, `T=1,000`, `m=5,000`.

| window | minimum Gram eigenvalue | worst complete-tail coefficient bound | exact rounding certified? |
|---|---:|---:|:---:|
| uniform | 0.818354 | 1.347945 | no |
| Hann | 0.984390 | 0.0271845 | yes |

The Hann taper improves both quantities in this regime: it suppresses
target-target leakage enough to raise the smallest eigenvalue, and suppresses
target-tail leakage by nearly two orders of magnitude.

### Time-window sweep for a fixed 5,000-point Hann grid

| `T` | minimum Gram eigenvalue | rigorous worst tail bound | certified? |
|---:|---:|---:|:---:|
| 300 | 0.06698 | 4.82883 | no |
| 500 | 0.83471 | 0.560884 | no |
| 750 | 0.95715 | 0.122516 | yes |
| 1,000 | 0.98439 | 0.0271845 | yes |

At fixed `m`, increasing `T` indefinitely is not free: the grid frequency
`m/T` falls and the first alias moves inward. Observation length and sampling
density must therefore be designed jointly.

### Noise scaling at `T=1,000`

For circular complex sensor noise `nu=0.01`:

| samples | worst complete-tail bound | Gaussian rounding-failure bound |
|---:|---:|---:|
| 10,000 | 0.0270066 | 0.6044 |
| 20,000 | 0.0270066 | 0.03278 |
| 50,000 | 0.0270066 | `1.53*10^-5` |
| 100,000 | 0.0270066 | `8.84*10^-11` |

The tail bias is controlled mainly by `T` and the taper. The sensor-noise term
shrinks with the effective sample count.

### Held-out arithmetic control

Using exact coefficients of `Q(sqrt(-5))` through norm 2,000, but fitting only
the first 50 coefficients with `T=1,000`, `m=5,000`, and the Hann grid, the
finite omitted tail produced

```text
maximum complex coefficient error: 0.00046314
maximum real coefficient error:    0.00028406
integer rounding:                   success
```

This is a falsification control, not part of the infinite universal proof. Its
actual error is roughly 59 times smaller than the universal complete-tail
certificate.

## 8. Why the proposed field-specific certificate was rejected

For a quadratic field with fundamental discriminant `D`,

\[
\zeta_K(s)=\zeta(s)L(s,\chi_D)
\]

and therefore

\[
a_K(n)=\sum_{d\mid n}\chi_D(d).
\]

Supplying the exact discriminant gives the complete character `chi_D`, hence
every target coefficient as well as every tail coefficient. Using that
information to certify recovery of the same coefficients would leak the
answer into the certificate. The earlier proposed “field-specific splitting
certificate” is therefore circular unless its side information is explicitly
independent of the recovery target.

The valid replacements are narrower:

1. a family-level or average-case theorem over discriminants;
2. a certificate using genuinely external local information that does not
   determine the target prefix;
3. recovery of a different unknown after the field itself is already known;
4. the universal `tau(n)` envelope used here.

The universal theorem is retained. No empirical field-specific improvement is
promoted to a theorem.

## 9. Quantitative and exact nonidentifiability

### Theorem F — deterministic two-ball lower bound

Consider the two normalized nonnegative integer Dirichlet polynomials

\[
F_n(s)=1+n^{-s},\qquad F_k(s)=1+k^{-s}.
\]

Their weighted response distance is

\[
d_{n,k}^2
=n^{-2\sigma}+k^{-2\sigma}
-2(nk)^{-\sigma}
\Re K_w\!\left(\log\frac{n}{k}\right).
\]

At adversarial weighted noise radius `d_(n,k)/2`, the midpoint of the two
responses lies in both closed noise balls. Consequently no decoder can
uniformly identify both coefficient vectors below assumptions that exclude
this pair.

For the certified Hann design with `n=50`, `k=51`, `sigma=2`, `T=1,000`, and
`m=5,000`,

```text
weighted response distance:      0.0005560869
adversarial ambiguity radius:    0.0002780435
```

These polynomials are valid normalized nonnegative integer Dirichlet
polynomials, but they are not asserted to be Dedekind zeta functions. This
lower bound applies to the broader coefficient-sensing model.

### Theorem G — exact number-field collision

Perlis proved that, when `+/-a` and `+/-2a` are nonsquares in `Q`, the fields
generated by roots of

\[
x^8-a\qquad\text{and}\qquad x^8-16a
\]

are arithmetically equivalent but nonisomorphic. Taking `a=3` gives

\[
K=\mathbb Q[x]/(x^8-3),
\qquad
K'=\mathbb Q[x]/(x^8-48),
\]

with

\[
K\not\cong K',\qquad \zeta_K(s)=\zeta_{K'}(s).
\]

Therefore their complete Dirichlet coefficients, all sampled vertical traces,
and every statistic derived only from the Dedekind zeta function coincide
exactly. No amount of noiseless aggregate-zeta data can identify a general
number field up to isomorphism.

This does not obstruct recovery of the shared ideal-count sequence. It draws
the correct boundary between coefficient recovery and arithmetic-object
recovery.

## 10. What is new in this continuation

### Proved here

- the exact weighted-quadrature recovery identity;
- the exact uniform and Hann midpoint kernels;
- the pre-alias midpoint-kernel bounds;
- an elementary remote `tau(n)` tail estimate;
- a complete alias-safe deterministic quadratic-field tail certificate;
- the exact weighted least-squares sensor-noise covariance and rounding bound;
- the two-ball lower bound for normalized integer Dirichlet polynomials;
- the circularity diagnosis for exact-discriminant tail information.

### Computed and independently tested

- exact kernel formulas against materialized weighted sums;
- exact kernel Grams against materialized weighted dictionaries;
- the divisor sieve against the existing factorization implementation;
- the elementary remote-tail bound against the exact zeta-series remainder;
- the complete Hann certificate and a held-out number-field recovery;
- the closed two-mode distance against a direct response calculation.

### Classical ingredients, not new claims

- coefficient domination `a_K(n)<=tau(n)` for quadratic fields;
- the factorization `zeta_K=zeta L(chi_D)`;
- Perlis' arithmetically equivalent nonisomorphic fields;
- standard Gaussian tail and union bounds;
- Hann tapering as a signal-processing window.

### Still open

- optimal deterministic window design under conditioning, leakage, noise, and
  alias constraints;
- a sharper analytic treatment that sums all grid-alias bands rather than
  cutting at half the first alias;
- a self-normalized theorem that genuinely improves random empirical least
  squares;
- a coefficient-recovery lower bound inside an explicitly characterized
  family of Dedekind zeta functions;
- extensions to degree `d`, higher-rank unit lattices, and class-group-valued
  data;
- recovery on or inside `sigma=1`;
- any result concerning nontrivial zeta zeros or the Riemann hypothesis.

## 11. Next research order

1. Optimize positive trigonometric quadrature weights by a convex minimax
   program, with hard constraints on the target Gram eigenvalues and on the
   first alias.
2. Prove an all-alias tail theorem by partitioning the log-norm axis into
   alias bands and applying divisor-sum estimates in each band.
3. Extend the deterministic certificate from `tau=d_2` to `d_d`, preserving
   explicit remote-tail constants.
4. Construct quadratic-field families with deliberately matching finite Euler
   data, then quantify how much additional trace length separates them.
5. Move from scalar norm counts to enriched local probes capable of breaking
   Perlis/Gassmann zeta collisions.
6. Return to higher-rank unit lattices only after the scalar all-alias theorem
   is sharp.

Arithmetic acceleration remains an adjacent target: a constrained integer
decoder could use multiplicativity and finite factorization relations after
the unbiased analytic certificate is established. Such a decoder must be
tested against explicit collisions and must not encode the target answer in
its prior.

## 12. Reproduction

```text
python \
  deterministic_arithmetic_sensing.py \
  --maximum-norm 50 \
  --sigma 2 \
  --observation-time 1000 \
  --sample-count 100000 \
  --truncation 1000000 \
  --window hann \
  --noise-sigma 0.01

python \
  arithmetic_indistinguishability.py

python -m unittest \
  -v test_deterministic_arithmetic_sensing.py \
  test_arithmetic_indistinguishability.py

python -m unittest discover -v
```

The million-term divisor sieve and all reported certificates run comfortably
on the local machine. The Windows computer was not needed.

## 13. Sources and novelty boundary

The quadratic coefficient factorization and Dedekind-zeta framework are
classical. The exact collision is due to Robert Perlis,
[*On the equation zeta_K(s)=zeta_K'(s)*, Journal of Number Theory 9 (1977),
342-360](https://doi.org/10.1016/0022-314X(77)90070-1).

An accessible exposition of the degree-eight family and its local behavior is
given in Athanasios Angelakis,
[*Universal Adelic Groups for Number Fields* (PhD thesis), Example 1.4.1](https://www.math.u-bordeaux.fr/~ybilu/algant/documents/PhD_theses/Athanasios.pdf).

The deterministic synthesis, alias-safe bound, explicit certificate, and
software are constructions of this research program. No priority claim is
made without independent specialist review.
