# Arithmetic Sensing I: Stable Recovery from Noisy Global Dirichlet Traces

## Stage 9 of the order–factorization and adelic-geometry program

**Status:** completed first theorem layer, 2026-08-12. This document proves a
deterministic perturbation theorem, a coefficientwise probabilistic rounding
certificate, field-uniform quadratic Dedekind-tail bounds, and a random-time
conditioning guarantee. Numerical experiments audit the constants and expose
where the first certificates are useful or conservative. No claim about zeta
zeros, a physical law, or literature priority is made.

## Abstract

Arithmetic sensing asks how much local arithmetic information can be recovered
from noisy aggregate global responses. The first model is

`y_j=sum_(n<=N) a_n n^(-sigma-it_j)+h(t_j)+eta_j`,

where `h` is the omitted Dirichlet tail and `eta` is measurement noise.

Four separate quantities control recovery:

1. the Gram matrix of the sampled log-integer Fourier dictionary;
2. measurement-noise energy;
3. the population projection of the omitted tail onto the target modes;
4. the finite-sample fluctuation of that tail projection.

An exact least-squares identity yields global and coefficientwise deterministic
bounds. For independent uniform sample times, the population Gram matrix has an
explicit sinc kernel, matrix Chernoff gives a finite-sample conditioning
theorem, and complex Bernstein concentration controls the sampled tail
correlations. In quadratic fields, `a_K(n)<=tau(n)` gives explicit analytic
tail envelopes through `zeta(s)^2`, while the identity

`sum tau(n)^2 n^(-s)=zeta(s)^4/zeta(2s)`

and the Montgomery–Vaughan Hilbert inequality give a mean-square tail budget.

These ingredients produce a computable certificate for exact integer rounding.
At target cutoff `N=50`, `sigma=2`, window `T=10,000`, and 500,000 random
samples, all 20 held-out designs received a field-uniform quadratic-tail bound
between `0.3947` and `0.3990`, below the required `1/2`. With circular complex
Gaussian noise standard deviation `0.01`, the largest additional conditional
rounding-failure bound was `5.70*10^-4`, on top of a 5% tail-correlation failure
budget. The bounds are sufficient, not necessary: direct held-out
`Q(sqrt(-5))` experiments succeeded with far smaller actual errors.

## 1. Measurement model and normalization

Let `a_n` be real coefficients and fix a cutoff `N`, an abscissa `sigma>1`,
and sample times `t_1,...,t_m`. Write

`x_n=a_n n^(-sigma)`, for `1<=n<=N`,

and define the normalized sensing matrix

`A_(j,n)=m^(-1/2) exp(-i t_j log n)`.                    (1)

The normalized observation vector is

`y=A x+r+e`,                                             (2)

where

`r_j=m^(-1/2) h(t_j)`,

`h(t)=sum_(k>N) a_k k^(-sigma-it)`,                      (3)

and `e_j=m^(-1/2) eta_j`. Let

`G=A^*A`                                                 (4)

be the empirical Gram matrix. When `G` is invertible, least squares gives

`x_hat=G^(-1)A^*y`.

The normalization in (1) keeps the diagonal of `G` equal to one. It also makes
the roles of sample count and observation window distinct: adding samples
concentrates the empirical Gram matrix, while increasing the time window
separates nearby log frequencies in its population mean.

## 2. Exact deterministic stability

### Theorem A (noise–conditioning–tail decomposition)

Let `D_sigma=diag(1^sigma,...,N^sigma)`. For arbitrary deterministic tail and
noise vectors, the coefficient error is exactly

`a_hat-a=D_sigma G^(-1) A^*(r+e)`.                       (5)

Consequently,

`||a_hat-a||_2`

` <= N^sigma / sqrt(lambda_min(G)) * (||r||_2+||e||_2)`. (6)

For every coefficient `n`, the sharper leverage bound is

`|a_hat_n-a_n|`

` <= n^sigma sqrt((G^(-1))_(n,n)) (||r||_2+||e||_2)`.   (7)

If the right side of (7) is less than `1/2` for every `n` and the true
coefficients are integers, rounding every recovered real part returns the
complete coefficient vector exactly.

#### Proof

Insert (2) into the least-squares formula and subtract `x`:

`x_hat-x=G^(-1)A^*(r+e)`.

Multiplication by `D_sigma` gives (5). The pseudoinverse
`G^(-1)A^*` has operator norm `1/sqrt(lambda_min(G))`; also
`||D_sigma||=N^sigma`, which proves (6).

The squared Euclidean norm of row `n` of `G^(-1)A^*` is

`(G^(-1) A^* A G^(-1))_(n,n)=(G^(-1))_(n,n)`.

Cauchy–Schwarz gives (7). A complex error of modulus below `1/2` has real part
below `1/2`, so nearest-integer rounding is correct. QED.

### Why the global bound is often pessimistic

The factor `N^sigma` in (6) treats every perturbation as if it were aligned
with the least observable direction and then amplified at the largest target
norm. Equation (7) retains the exact leverage of each coefficient. The
probabilistic theorem below is sharper again: instead of bounding the complete
tail by its raw energy, it bounds the actual tail correlations before applying
`G^(-1)`.

## 3. Population geometry of random-time sampling

Suppose now that the times are independent and uniform on `[0,T]`. Define

`K_T(omega)=E exp(i t omega)`

` = exp(i T omega/2) sinc(T omega/2)`,                    (8)

where `sinc(u)=sin(u)/u`. The population Gram matrix `Gamma=E G` is therefore

`Gamma_(n,l)=K_T(log(n/l))`.                              (9)

This is an exact log-integer Fourier kernel.

### Proposition B (elementary population conditioning)

Let `H_(N-1)=sum_(k=1)^(N-1) 1/k`. Then

`lambda_min(Gamma)>=1-4 N H_(N-1)/T`.                    (10)

The sharper computable Gershgorin bound is

`lambda_min(Gamma)>=1-rho_N(T)`,

`rho_N(T)=max_n sum_(l!=n)|K_T(log(n/l))|`.               (11)

#### Proof

Equation (8) gives

`|K_T(omega)|<=min(1,2/(T|omega|))`.

For `n!=l<=N`, the mean-value theorem gives

`|log(n/l)|>=|n-l|/N`.

Hence each off-diagonal row sum is at most

`(2N/T)(H_(n-1)+H_(N-n))<=4NH_(N-1)/T`.

Gershgorin's theorem proves both claims. QED.

The elementary result guarantees positive population conditioning once
`T>4NH_(N-1)`, an `N log N` scale. It is intentionally crude. Direct evaluation
of (11) is much sharper, while the exact eigenvalue of (9) is sharper still.

### Theorem C (finite-sample conditioning)

Let `lambda=lambda_min(Gamma)>0`. For `0<epsilon<1`,

`P(lambda_min(G)<=(1-epsilon)lambda)`

` <= N exp(-epsilon^2 m lambda/(2N))`.                   (12)

In particular, probability at least `1-delta` is guaranteed when

`m >= 2N log(N/delta)/(epsilon^2 lambda)`.                (13)

#### Proof

If `v(t)=(exp(-it log n))_(n<=N)`, then

`G=(1/m)sum_j v(t_j)v(t_j)^*`.

Every summand is positive semidefinite and has largest eigenvalue
`||v(t_j)||^2=N`. Its expected sum has minimum eigenvalue `m lambda`.
The lower-tail matrix Chernoff inequality gives (12), using the standard
quadratic simplification of its exponent. Rearrangement gives (13). QED.

This theorem is a preregistration guarantee: it selects a sample count before
data are seen. After sampling, the actual `G` and its eigenvalues are observable,
so Theorems A and F below can use them directly.

## 4. A necessary logarithmic resolution scale

Conditioning is not only a finite-sample issue. Consider two normalized
population modes with frequencies `log n` and `log k`. After choosing their
relative complex phase optimally, their squared `L^2([0,T],dt/T)` distance is

`2(1-|K_T(log(n/k))|)`.                                  (14)

If adversarial noise has radius at least half this distance, the two one-mode
signals can produce the same midpoint observation; no estimator can distinguish
both correctly.

For adjacent modes `k=N+1`,

`Delta_N=log((N+1)/N)~1/N`.

When `T Delta_N` is small, (14) has distance

`T Delta_N/sqrt(12)+O((T Delta_N)^3)`.                   (15)

Thus the controlling resolution parameter is `T/N`. More samples on the same
short interval estimate a poorly resolved population geometry more accurately;
they do not change that geometry.

The complex-phase ambiguity in (14) is a general sensing obstruction. Extra
arithmetic restrictions such as real, nonnegative, integral coefficients can
make a particular pair easier to distinguish, but they do not remove the
near-collinearity of the measurement modes.

## 5. Field-uniform Dedekind-tail bounds

Let `K` be a degree-`d` number field and

`zeta_K(s)=sum_(n>=1) a_K(n)n^(-s)`.

### Proposition D (coefficient domination)

For every `n>=1`,

`0<=a_K(n)<=d_d(n)`,                                     (16)

where `d_d(n)` is the coefficient of `zeta(s)^d`. Therefore, for `sigma>1`,

`R_(d,N)(sigma):=sum_(n>N)a_K(n)n^(-sigma)`

` <= zeta(sigma)^d-sum_(n<=N)d_d(n)n^(-sigma)`.          (17)

#### Proof

At a rational prime `p`, write the local Dedekind factor as

`prod_(j=1)^r (1-p^(-f_j s))^(-1)`.

Its `p^e` coefficient counts nonnegative tuples satisfying
`sum_j f_j k_j=e`. If `r=d`, the degree formula forces complete splitting and
the count is `binomial(e+d-1,d-1)`. Otherwise `r<=d-1`; append the slack
`e-sum_j k_j` to inject the solutions into weak compositions of `e` into
`r+1<=d` parts. This again gives at most
`binomial(e+d-1,d-1)`. Multiplicativity proves (16), and summing its Dirichlet
series proves (17). QED.

For quadratic fields, `d_2(n)=tau(n)`, the ordinary divisor function. The
bound is universal over every quadratic field; it does not use the field's
discriminant, splitting density, or residue of its zeta function.

### Theorem E (quadratic tail-energy bound)

For a quadratic field, let `h` be the tail (3). Put

`S_0=sum_(n>N) tau(n)^2 n^(-2sigma)`,

`S_1=sum_(n>N) (n+1)tau(n)^2 n^(-2sigma)`.               (18)

Then

`(1/T) integral_0^T |h(t)|^2 dt`

` <= S_0+(3 pi/T)S_1=:V_(N,sigma,T)`.                   (19)

Both series can be evaluated without truncating the infinite tail because

`sum_(n>=1) tau(n)^2 n^(-s)=zeta(s)^4/zeta(2s)`.         (20)

#### Proof

Apply the Montgomery–Vaughan weighted Hilbert inequality to the frequencies
`log n`. Their nearest-neighbor gaps satisfy

`delta_n>=1/(n+1)`.

After expanding the square in the mean integral, the two endpoint Hilbert sums
contribute at most `3 pi sum_(n>N)(n+1)|c_n|^2`, where
`c_n=a_K(n)n^(-sigma)`. Divide by `T`, use `a_K(n)<=tau(n)`, and obtain (19).
The Euler factor identity for `tau(n)^2` gives (20). QED.

The constant in (19) is inherited from a classical general Hilbert inequality;
it is not asserted to be optimal for log-integer frequencies.

## 6. Tail projection and exact integer recovery

The deterministic energy bound treats every tail direction as adversarial. A
random-time experiment permits a sharper decomposition.

Define the population target–tail correlations

`beta_n=E[exp(i t log n)h(t)]`

` =sum_(k>N)a_K(k)k^(-sigma)K_T(log(n/k))`.              (21)

Let `b_n` be any deterministic bound with `|beta_n|<=b_n`. Proposition D and
the inequality in the proof of Proposition B give the computable envelope

`b_n<=sum_(k>N)d_d(k)k^(-sigma)`

`       * min(1,2/(T log(k/n)))`.                         (22)

The implementation evaluates a finite prefix of (22) exactly and bounds the
remaining mass by (17) times the largest remaining correlation.

### Proposition F (simultaneous tail-correlation concentration)

Assume `|h(t)|<=R` and `E|h(t)|^2<=V`. For `0<delta<1`, set

`L=log(4N/delta)`

and

`q=R L/m+sqrt((R L/m)^2+4V L/m)`.                        (23)

Then, with probability at least `1-delta`, every empirical tail correlation

`u_n=(1/m)sum_j exp(i t_j log n)h(t_j)`

satisfies

`|u_n-beta_n|<=q`.                                       (24)

#### Proof

Apply scalar Bernstein separately to the real and imaginary parts of each
centered correlation variable. Its modulus is at most `2R`, and the sum of the
two component variances is at most `V`. If a complex deviation exceeds `q`,
one component exceeds `q/sqrt(2)`. A union bound over two components and `N`
coordinates gives failure probability at most

`4N exp(-m q^2/(4V+2Rq))`.

The definition (23) makes the exponent at least `L`. QED.

### Theorem G (arithmetic sensing certificate)

For the observed invertible Gram matrix `G`, define

`B_n=n^sigma sum_(l<=N)|(G^(-1))_(n,l)|(b_l+q)`.         (25)

With probability at least `1-delta` over the sampling times, the coefficient
error caused by the complete omitted tail satisfies

`|a_hat_n-a_n|<=B_n`                                     (26)

simultaneously for every `n`, before measurement noise is added.

Suppose in addition that `eta_j` are independent circular complex Gaussians
with `E|eta_j|^2=nu^2`, independent of the times. If every `B_n<1/2`, then
nearest-integer rounding fails with probability at most

`delta + 2 sum_(n<=N) exp(`

` -m(1/2-B_n)^2 / (nu^2 n^(2sigma)(G^(-1))_(n,n)) )`.   (27)

#### Proof

The tail contribution in weighted coefficient coordinates is `G^(-1)u`.
Equations (22)–(24), the triangle inequality, and multiplication by `n^sigma`
give (25)–(26).

Conditional on the sampled times, the weighted least-squares noise error is a
circular complex Gaussian vector with covariance

`(nu^2/m)G^(-1)`.

The real part of coefficient `n`, after rescaling by `n^sigma`, has variance

`nu^2 n^(2sigma)(G^(-1))_(n,n)/(2m)`.

Rounding can fail only if this real noise exceeds the remaining margin
`1/2-B_n`. Apply the two-sided Gaussian tail bound to every coordinate and use
a union bound, then add the tail-correlation failure probability `delta`. QED.

### Interpretation of the certificate

The terms have different remedies:

| term | meaning | improved by |
|---|---|---|
| `G^(-1)` | realized conditioning and leverage | longer windows and better designs |
| `b` | coherent population tail bias | longer windows, larger cutoff, larger `sigma`, or a tail model |
| `q` | finite-sample tail fluctuation | more independent samples and sharper tail priors |
| Gaussian term | measurement noise | more samples or less sensor noise |

This distinction is the first core principle of arithmetic sensing. “Noise” is
not one scalar phenomenon. Coherent model bias and stochastic measurement noise
behave differently and require different experimental interventions.

## 7. Computational audit

The experiments use `N=50`, `sigma=2`, independent uniform times, and 40 seeds
unless otherwise stated.

### Population and empirical conditioning

With 200 samples:

| `T` | population `lambda_min` | exact Gershgorin lower bound | mean empirical `lambda_min` | minimum over 40 |
|---:|---:|---:|---:|---:|
| 100 | numerically unresolved near zero | -3.036 | numerically zero | numerically zero |
| 300 | 0.5918 | -0.3089 | 0.1918 | 0.0983 |
| 1,000 | 0.8184 | 0.5938 | 0.2597 | 0.2097 |
| 3,000 | 0.9401 | 0.8634 | 0.2687 | 0.2266 |

At `T=1,000`, the elementary closed bound (10) is only `0.1042`. The exact
Gershgorin evaluation gives `0.5938`, and the exact population eigenvalue is
`0.8184`. This hierarchy is expected: transparent analytic bounds trade
sharpness for universality.

For `T=1,000`, `epsilon=1/2`, and `delta=0.05`, the matrix Chernoff theorem
requests 3,377 samples to guarantee empirical minimum eigenvalue at least half
the population value. Two hundred samples often work for inversion, but they do
not meet this stronger preregistered threshold.

### The first omitted mode

The absolute population correlation between target mode 50 and omitted mode 51
is:

| `T` | `|K_T(log(51/50))|` |
|---:|---:|
| 100 | 0.8444 |
| 300 | 0.05735 |
| 1,000 | 0.04633 |
| 3,000 | 0.03333 |

The nonmonotonic sidelobes of `sinc` mean that correlation is not strictly
decreasing at every window. Its envelope is controlled by `T log(51/50)`,
confirming the `T/N` resolution parameter.

### Universal quadratic population-tail certificate

For every quadratic field, the uniform tail bound at `N=50`, `sigma=2` is

`R<=0.1199679536`.

The mean-square bounds and worst population coefficient-bias envelopes are:

| `T` | tail energy `V` | correlation-envelope `l2` norm | worst coefficient bias bound |
|---:|---:|---:|---:|
| 300 | `3.505*10^-4` | 0.003874 | 4.493 |
| 1,000 | `1.726*10^-4` | 0.001205 | 1.347 |
| 3,000 | `1.218*10^-4` | 0.000410 | 0.4948 |
| 10,000 | `1.040*10^-4` | 0.000130 | 0.1669 |

The population certificate first crosses the integer threshold near this range.
At `T=3,000` it is technically below `1/2` but has essentially no margin. At
`T=10,000` it leaves enough room for finite-sample fluctuation and measurement
noise.

### Finite-sample certificate at `T=10,000`

Using the 95% Bernstein tail-correlation budget:

| samples | worst tail coefficient bound | certifies integer rounding before sensor noise? |
|---:|---:|:---:|
| 200 | 161.4 | no |
| 1,000 | 21.45 | no |
| 5,000 | 4.450 | no |
| 20,000 | 1.741 | no |
| 100,000 | 0.7352 | no |
| 500,000 | 0.3963 | yes |

The large sample requirement comes mainly from a conservative simultaneous
Bernstein bound, subsequently amplified by `n^sigma`. It should not be confused
with an empirical claim that 500,000 samples are necessary.

Twenty held-out 500,000-sample designs all certified. Their worst tail bounds
ranged from `0.39465` to `0.39897`. At measurement-noise standard deviation
`nu=0.01`, the largest conditional Gaussian rounding-failure bound was
`5.70*10^-4`. Combining it with `delta=0.05` gives a success guarantee above
94.94% for the stated universal model and realized designs.

### Direct field-specific control

As a falsification check, five new designs used 200,000 samples at `T=10,000`
and the exact `Q(sqrt(-5))` tail through norm 2,000. All five rounded the first
50 coefficients correctly. Maximum complex coefficient errors were between
0.0262 and 0.0336; maximum real errors were between 0.0132 and 0.0302.

This does not replace the infinite field-uniform theorem. It shows that the
universal certificate is conservative by roughly an order of magnitude in this
laboratory, leaving room for substantial improvement through field-specific
splitting data or sharper concentration.

## 8. What has been proved

### Exact or rigorous conditional results

- the deterministic least-squares perturbation identity and global bound;
- coefficientwise leverage bounds and the integer-rounding criterion;
- the exact uniform-time population Gram kernel;
- elementary and exact-computable Gershgorin conditioning bounds;
- a finite-sample matrix Chernoff guarantee;
- degree-`d` Dedekind coefficient domination by `d_d(n)`;
- a field-uniform quadratic `l1` tail bound;
- a quadratic mean-square tail bound using Montgomery–Vaughan;
- simultaneous complex Bernstein control of empirical tail projections;
- a data-dependent exact-integer recovery probability certificate;
- a two-mode resolution obstruction for general complex coefficient sensing.

### Numerical evidence

- realized conditioning thresholds and the conservatism of the analytic bounds;
- the population tail-bias transition across the `1/2` rounding threshold;
- 20/20 held-out sampling designs satisfying the universal certificate;
- 5/5 direct `Q(sqrt(-5))` finite-tail recovery controls.

### Not established

- optimal sample complexity for log-integer Fourier sensing;
- a matching lower bound for real nonnegative integer Dedekind coefficients;
- optimal concentration constants for the structured tail process;
- a sharp field-specific infinite-tail bound using splitting statistics;
- recovery on or inside the line `sigma=1`;
- recovery of principal ideal classes from aggregate ideal counts;
- any statement about the nontrivial zeros of a zeta function;
- novelty in the literature without independent specialist review.

## 9. New hypotheses opened by the theorem

### H1 — arithmetic tail cancellation beats divisor domination

For a fixed quadratic field and randomized long windows, field-specific
splitting should reduce the effective tail projection well below the universal
`tau(n)` envelope. Test this by replacing only the envelope—not the recovered
target—with independently derived Chebotarev or character information.

### H2 — the true finite-sample rate is leverage-local

The uniform coordinate deviation `q` treats all target modes equally before
`G^(-1)` amplification. A vector Bernstein bound or a direct concentration
bound for `G^(-1)u` should scale with realized leverage and reduce the current
500,000-sample certificate substantially.

### H3 — window design can suppress the boundary tail

Uniform windows inherit sinc sidelobes. A designed time density whose Fourier
transform has controlled zeros or tapering near `log((N+j)/N)` may reduce
coherent tail leakage without increasing the maximum observation time as much.
The tradeoff is a broader main lobe and potentially worse target conditioning.

### H4 — integer structure supports a sharper decoder

Least squares followed by independent rounding ignores nonnegativity,
multiplicativity, and local Euler constraints. A constrained integer decoder
should succeed beyond the coordinatewise `1/2` certificate, but must be tested
against explicit ambiguous coefficient sequences to avoid converting the prior
into the answer.

## 10. Recommended Stage 9 continuation

1. Replace coordinatewise Bernstein plus entrywise `|G^(-1)|` with a direct
   vector concentration theorem for the recovered tail error.
2. Optimize the time-sampling distribution jointly for target conditioning and
   boundary-tail suppression.
3. Derive a field-specific quadratic tail certificate from
   `zeta_K(s)=zeta(s)L(s,chi_D)` without using unknown target coefficients.
4. Construct two admissible arithmetic models inside the certified noise ball
   to obtain an information-theoretic lower bound.
5. Extend the coefficient envelope and tail energy theory from quadratic fields
   to fixed degree `d`.
6. Only after the one-dimensional theory is sharp, begin higher-rank unit
   lattices and noncyclic class-group laboratories.

## 11. Reproduction

```text
python arithmetic_sensing.py \
  --maximum-norm 50 --sample-count 200 --trials 40

python -m unittest \
  -v test_arithmetic_sensing.py

python -m unittest discover -v
```

The default analysis includes the 20-design, 500,000-sample certificate audit
and five exact finite-tail controls, so it can take noticeably longer than the
unit tests. The Windows computer is not required for these parameters.

## 12. Sources and novelty boundary

The adelic and Dedekind-zeta setting follows the classical framework initiated
by [J. Tate, *Fourier Analysis in Number Fields and Hecke's Zeta-Functions*
(AMS collected works)](https://bookstore.ams.org/cworks-24-1/).

The weighted Hilbert inequality used in Theorem E is due to [H. Montgomery and
R. Vaughan, *Hilbert's Inequality*, Journal of the London Mathematical Society
8 (1974), 73–82](https://doi.org/10.1112/jlms/s2-8.1.73).

The matrix Chernoff tool used in Theorem C follows [J. Tropp, *User-Friendly
Tail Bounds for Sums of Random Matrices*
(2012)](https://tropp.caltech.edu/papers/Tro11-User-Friendly-preprint.pdf).
The broader sparse-recovery viewpoint continues [J. Tropp, *Greed is Good:
Algorithmic Results for Sparse Approximation*
(2004)](https://authors.library.caltech.edu/records/m0swv-ba672).

The exact synthesis into a noise–conditioning–tail arithmetic certificate, its
software, and the experiments are constructions of this research program.
Classical ingredients are identified explicitly, and no priority claim is made
for the combined theorem without an independent literature review.
