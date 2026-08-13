# Inverse Adelic Spectral Geometry

## Stage 7 of the order–factorization program

**Status:** completed first inverse layer, 2026-08-12. Exact identifiability
statements are proved for quadratic splitting templates, an Archimedean unit
channel, robust rational rigidity certificates, and interacting-mode
factorization defects. Numerical experiments quantify their stability. The
results reconstruct supplied arithmetic models; they do not derive a spectral
operator for zeta zeros or a physical theory.

## Abstract

Stages 2–6 constructed local coordinates, adelic conservation, finite
calibration, and prime-mode spectra in the forward direction. Stage 7 reverses
the arrows:

> Given incomplete or noisy responses, which pieces of the place decomposition
> can actually be recovered, and which are not identifiable?

Five answers are obtained.

1. The first two local Euler coefficients distinguish split, ramified, and
   inert quadratic primes exactly.
2. Labelled noisy local heat responses retain high splitting-classification
   accuracy in both quadratic laboratories.
3. The regulator of `Q(sqrt(5))` is recovered directly and optimally from a
   noisy Archimedean unit channel; ideal labels alone cannot perform that
   geometric recovery.
4. Every exact Stage 5 rigidity backbone has a rigorous noisy counterpart. Its
   multiplier mass is exactly the error-amplification constant.
5. Cross-mode interactions break Euler factorization and create mixed
   occupation covariance, but one aggregate trace value cannot identify the
   interaction.

The repeated lesson is that identifiability depends on what is observed.
Locally labelled responses, Archimedean embeddings, and mixed statistics carry
information that a single global partition value does not.

## 1. Inverse data hierarchy

The phrase “recover the adelic geometry from a trace” hides several distinct
experiments. Ordered from strongest to weakest data, they are:

1. **place-labelled response:** the contribution of each rational prime or
   place is measured separately;
2. **frequency-resolved response:** modes are separated by their logarithmic
   time frequencies, but their arithmetic labels may be unknown;
3. **global response curve:** only the product or total trace is measured at
   several temperatures;
4. **one aggregate scalar:** the partition function is known at one
   temperature.

An inference valid at level 1 need not be possible at level 4. Stage 7 records
the data level for every result instead of treating all spectral information as
equivalent.

## 2. Exact inverse recovery of quadratic splitting

Fix a rational prime `p` and put `T=p^(-s)`. For an unramified or ramified
quadratic prime, the local Dedekind factor has one of three forms:

`Z_split(T)=(1-T)^(-2)`,

`Z_ramified(T)=(1-T)^(-1)`,

`Z_inert(T)=(1-T^2)^(-1)`.

The ramification index does not duplicate the Euler factor: there is one factor
for each prime ideal. Inertia changes the prime-ideal norm from `p` to `p^2`.

### Theorem A (two coefficients determine quadratic behavior)

Write the labelled local factor as

`Z_p(T)=1+a_p T+a_(p^2)T^2+O(T^3)`.

Then

| behavior | `(a_p,a_(p^2))` |
|---|---:|
| split | `(2,3)` |
| ramified | `(1,1)` |
| inert | `(0,1)` |

Consequently the first two coefficients determine the quadratic splitting
behavior exactly.

#### Proof

Expand the three rational functions:

`(1-T)^(-2)=sum_(k>=0)(k+1)T^k`,

`(1-T)^(-1)=sum_(k>=0)T^k`,

`(1-T^2)^(-1)=sum_(k>=0)T^(2k)`.

Their first two coefficient pairs are distinct. QED.

In fact, if `p` and one exact positive real `s` are known, even one local
factor value distinguishes the templates because

`Z_split>Z_ramified>Z_inert>1`.

The coefficient theorem is preferable because it remains purely algebraic and
shows exactly which ideal-counting information separates the cases.

### Noisy labelled-response experiment

For every rational prime through `97`, sample the logarithm of its local factor
at

`s in {0.25,0.4,0.7,1.1,1.6}`,

add independent Gaussian noise, and choose the nearest of the three template
vectors. There are 25 primes and 100 trials, hence 2,500 classifications per
field and noise level.

| log-factor noise sd | `Q(i)` accuracy | `Q(sqrt(5))` accuracy |
|---:|---:|---:|
| 0 | 100% | 100% |
| 0.002 | 100% | 100% |
| 0.01 | 100% | 100% |
| 0.03 | 100% | 100% |
| 0.10 | 98.52% | 98.48% |

This is finite Monte Carlo evidence about a labelled three-template model. It
does not show that an unlabelled global zeta trace uniquely reveals its Euler
factorization.

## 3. Direct inverse recovery of the unit regulator

Let

`phi=(1+sqrt(5))/2`, `R=log(phi)`.

The two real logarithmic embeddings of `phi^k` are

`(kR,-kR)`.

Suppose both components are observed with independent mean-zero Gaussian noise
of standard deviation `sigma`:

`X_k=kR+epsilon_(k,1)`,

`Y_k=-kR+epsilon_(k,2)`.

### Theorem B (unbiased regulator estimator and exact variance)

For positive measured powers `k in K`, define

`R_hat=sum_k k(X_k-Y_k)/(2 sum_k k^2)`.                   (1)

Then

`E[R_hat]=R`

and

`Var(R_hat)=sigma^2/(2 sum_k k^2)`.                       (2)

Among unbiased linear estimators in the Gaussian linear model, this is the
least-squares estimator and has minimum variance.

#### Proof

The difference satisfies

`X_k-Y_k=2kR+(epsilon_(k,1)-epsilon_(k,2))`.

Substitution into (1) proves unbiasedness. The differences are independent and
have variance `2 sigma^2`, so

`Var(R_hat)`

`=(sum_k k^2 2sigma^2)/(4(sum_k k^2)^2)`

`=sigma^2/(2sum_k k^2)`.

The minimum-variance statement is ordinary one-parameter Gaussian least
squares. QED.

With `sigma=0.1` and powers `1,...,K`, 2,000 trials give:

| `K` | empirical RMSE | predicted sd | empirical/predicted sd |
|---:|---:|---:|---:|
| 1 | 0.07082 | 0.07071 | 1.0017 |
| 2 | 0.03139 | 0.03162 | 0.9928 |
| 4 | 0.01280 | 0.01291 | 0.9915 |
| 8 | 0.005025 | 0.004951 | 1.0152 |
| 16 | 0.001824 | 0.001828 | 0.9958 |
| 32 | 0.0006628 | 0.0006611 | 1.0027 |

Since `sum_(k<=K)k^2` is of order `K^3`, the standard deviation decays as
`K^(-3/2)` in this increasing-power protocol.

### Exact nonidentifiability without the Archimedean channel

For every unit `u`,

`(u)=O_K`, `|N(u)|=1`.

Thus every power `phi^k` produces the same principal-ideal label and absolute
norm. No estimator using only those direct observations can distinguish two
possible regulator values: the observation map is constant on the unit group.

This does not contradict the analytic class-number formula, in which a
Dedekind-zeta residue contains the regulator together with other global
invariants. It says specifically that the local prime-ideal occupation labels
do not display the unit lattice geometrically.

## 4. Robust rigidity backbones

Stage 5 used adjacent exponent rows

`a_n=v(n)-v(n+1)`

and exact nonnegative dual certificates. Replace exact monotonicity by bounded
one-sided defects:

`a_n dot w=E(n)-E(n+1)<=delta_n`, `delta_n>=0`.            (3)

### Theorem C (certificate error propagation)

Suppose `y_n>=0` and

`sum_n y_n a_n=L e_2-e_3`.

Under (3), with `E(2)=1`,

`E(3)>=L-sum_n y_n delta_n`.                              (4)

If instead

`sum_n y_n a_n=e_3-Ue_2`,

then

`E(3)<=U+sum_n y_n delta_n`.                              (5)

#### Proof

Multiply each inequality (3) by its nonnegative certificate multiplier and
sum. Insert the exact certificate identity. QED.

For a uniform defect `delta`, the amplification constant is therefore the
certificate mass `||y||_1`. This is rigorous and needs no stochastic noise
model.

For the selected exact lower and upper certificates:

| cutoff `N` | exact width | total certificate mass | uniform defect doubling the width | union support |
|---:|---:|---:|---:|---:|
| 100 | `1/35` | `39/35` | `1/39` | 7 |
| 1,000 | `65/38808` | `30823/38808` | `5/2371` | 21 |
| 10,000 | `5387/45735336` | `1279718/1905639` | `5387/30713232` | 37 |

At `N=10000`, a uniform defect `10^-4` enlarges the certified width from

`0.0001177864` to `0.0001849407`.

The certificate remains stable in amplitude because its total mass is below
one, but missing comparisons are a different problem. If each needed adjacent
comparison is independently observed with probability `q`, the probability
that the displayed `N=10000` certificate pair survives intact is `q^37`:

| `q` | intact-pair probability |
|---:|---:|
| 0.90 | 0.0203 |
| 0.95 | 0.1499 |
| 0.99 | 0.6894 |

This exposes an important distinction: a sparse certificate can have excellent
noise amplification but still be fragile to missing a single support edge.
Designing redundant or minimum-mass certificates is therefore a genuine
optimization target for robust arithmetic reconstruction.

## 5. Sparse prime support: a deterministic certificate

Stage 6 recovered active log-prime modes with Orthogonal Matching Pursuit from
random-time samples. Let `A` be the column-normalized measurement dictionary
and

`mu=max_(p!=q)|<A_p,A_q>|`

its mutual coherence.

A standard uniform sufficient condition for noiseless OMP recovery of every
`K`-sparse vector is

`mu<1/(2K-1)`.                                             (6)

Unlike the earlier Monte Carlo percentages, (6) can be evaluated as a
deterministic certificate for the realized matrix.

For the 25 candidate primes through `97`, 512 randomized samples on
`[0,1000]`, and seed `20260812`, the measured coherence is

`mu=0.1039344946<1/7`.

Consequently the standard condition certifies uniform noiseless recovery for
every four-sparse coefficient vector in this realized log-prime dictionary.
The strict coherence threshold is approximately `5.31`, so it also certifies
five-sparse recovery.

This is the first rigorous recovery guarantee in the noisy/sparse branch, but
only for noiseless support recovery after the finite matrix has been formed.
It is not yet a probability theorem explaining how many random time samples
will achieve the needed coherence.

## 6. Interactions as exact countermodels to Euler factorization

Take two prime modes and add a repulsive cross-term

`H_J=(log p)N_p+(log q)N_q+J N_pN_q`, `J>0`.              (7)

### Theorem D (cross interaction breaks the Euler product)

For every real `beta>0`,

`Z_J(beta)<Z_p(beta)Z_q(beta)`.

Moreover, the mixed occupation covariance is strictly negative:

`Cov_J(N_p,N_q)<0`.

#### Proof of factorization failure

Every Boltzmann term with both occupations positive is multiplied relative to
the free model by

`exp(-beta J k l)<1`.

Terms on the coordinate axes are unchanged, and jointly occupied terms exist.
Termwise comparison proves the strict inequality.

The negative covariance is the expected anticorrelation caused by the
repulsive interaction. Indeed, conditional on `N_p=k`, the other occupation is
geometric with mean

`m(k)=1/(exp(beta(log q+Jk))-1)`,

which is strictly decreasing in `k`. Hence

`Cov(N_p,N_q)=Cov(N_p,m(N_p))<0`.

For completeness, if `K'` is an independent copy of `K=N_p`, then

`2Cov(K,m(K))=E[(K-K')(m(K)-m(K'))]`.

The integrand is nonpositive everywhere and negative with positive probability
because `K` is nondegenerate and `m` is strictly decreasing. This proves the
covariance claim.

For `p=2`, `q=3`, `J=log 2`, and `beta=2`, an exact rational sum through
occupation 12 proves a factorization deficit larger than

`0.03405776099`.

The entire omitted free tail is below

`2.23524*10^-8`,

so truncation cannot explain the defect. Numerically, the mixed covariance is
negative at every tested `beta` from `0.7` to `3`.

### Why one aggregate trace is insufficient

At one fixed `beta`, keep the first local factor and solve

`Z_J(beta)=Z_p(beta)(1-exp(-beta epsilon_eff))^(-1)`

for an effective second energy `epsilon_eff>0`. Thus the single interacting
partition value is reproduced exactly by a free model with a shifted apparent
energy.

Interaction becomes identifiable only after adding structure such as:

- locally calibrated mode energies;
- a response curve over multiple temperatures with fixed energies;
- mixed occupation measurements;
- direct tests of tensor-product factorization.

This is a concrete counterexample to treating a successful scalar zeta fit as
evidence for a unique underlying geometry.

## 7. What Stage 7 establishes

### Proved exactly

- two local coefficients classify quadratic split/ramified/inert behavior;
- the regulator estimator, its unbiasedness, and its variance;
- direct unit-lattice nonidentifiability from principal-ideal and absolute-norm
  labels;
- robust propagation formulas for every nonnegative rigidity certificate;
- the realized noiseless OMP coherence guarantee;
- strict failure of Euler factorization under a positive cross interaction;
- nonidentifiability of interaction from one aggregate partition scalar.

### Numerically verified

- noisy splitting recovery over all primes through `97` in both laboratories;
- Monte Carlo regulator errors matching the exact variance law;
- noisy and sparse log-prime recovery regimes from Stage 6;
- negative mixed covariance and multi-temperature factorization defects.

### Not established

- recovery of local factors from an unlabelled global trace without a model
  class;
- a sample-complexity probability theorem for random-time log-prime matrices;
- robust regulator recovery when unit powers or embedding labels are unknown;
- an optimal redundant certificate family under missing data;
- reconstruction for fields with nontrivial class group;
- any spectral realization of zeta zeros or physical law.

## 8. Reproduction

```text
python inverse_splitting_recovery.py \
  --prime-limit 97 --trials 100

python inverse_regulator_recovery.py \
  --trials 2000

python robust_rigidity_certificates.py \
  --limits 30 100 300 1000 3000 10000 --uniform-defect 1/10000

python interacting_prime_modes.py
python -m unittest discover -v
```

## 9. Recommended continuation

1. Derive high-probability coherence bounds for random-time log-prime
   Vandermonde matrices rather than certifying only realized matrices.
2. Optimize rigidity certificates for minimum multiplier mass and redundancy,
   not merely endpoint sharpness.
3. Recover unknown unit generators and regulators jointly, including the
   integer lattice ambiguity.
4. Move to quadratic fields of nontrivial class number, where principal data
   sees prime ideals only after class-order relations.
5. Formulate multi-temperature identifiability theorems for interacting mode
   graphs.
6. Connect local inverse data to the full idele-class quotient while preserving
   the distinction between arithmetic reconstruction and zeta-zero spectral
   realization.

## 10. Sources and novelty boundary

The place decomposition, local zeta integrals, unit lattice, and global
Fourier/Poisson framework remain those of [J. Tate, *Fourier Analysis in Number
Fields and Hecke's Zeta-Functions*
(1950)](https://sites.math.rutgers.edu/~alexk/2023S572/Tate1950.pdf).

The coherence-based OMP recovery framework follows [J. Tropp, *Greed is Good:
Algorithmic Results for Sparse Approximation*
(2004)](https://authors.library.caltech.edu/records/m0swv-ba672) and the random
measurement perspective of [J. Tropp and A. Gilbert, *Signal Recovery From
Random Measurements Via Orthogonal Matching Pursuit*
(2007)](https://authors.library.caltech.edu/records/hg25b-hf247).

The Stage 7 theorems are elementary deductions within the specified finite
models. The numerical inverse studies are exploratory. No literature-priority
claim is made.
