# Operational Information Geometry II

## Protocol invariance, common blind subspaces, and stable mixture recovery

- **Research lead, mathematics, software, and manuscript:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Date:** 13 August 2026
- **Status:** second theorem-and-falsification layer; not peer reviewed

## Abstract

Operational Information Geometry I associated a metric to observable histories
of a finite dynamics. That construction was intentionally relative to a sensor
matrix and a time schedule. This paper asks the necessary next question: when
do different protocols recover approximately the same geometry, and what can
remain hidden even when they agree on every pure state?

We define a scale-free bi-Lipschitz dilation between finite operational
metrics. A finite random-projection theorem shows that normalized sign sensors
preserve all pure-state history distances with
\(q=O(\varepsilon^{-2}\log(mn^2/\delta))\) channels, for \(n\) states and
\(m\) observation times. An exact common-kernel theorem shows that pooling
protocols adds their Gramians and intersects their indistinguishability
kernels. Complete observation at different time schedules nevertheless need
not agree: its Gram is the spectral filter
\(g_{\mathcal T}(L)=\sum_{t\in\mathcal T}e^{-2tL}\), so changing the schedule
changes the relative weight of dynamical scales.

Experiments on the 216-state \(2^a3^b5^c\) universe confirm conditional, not
universal, protocol invariance. With a fixed early schedule and 32 independently
refreshed sign channels per time, the median dilation from complete observation
is \(1.292\); 64 channels reduce it to \(1.189\). Between paired 32-channel
protocols the median dilation is \(1.454\). In contrast, even complete early
and late observers differ by dilation \(8.861\). There is no single geometry
across arbitrary time windows.

Adversarial protocols expose a stronger obstruction. A sensor constant along
one prime-exponent axis erases that axis exactly and sees only two of the three
slow directions. Combining one observer blind to each axis separates all 216
pure states with minimum signature margin \(1.404\), yet the combined history
map has rank only 91 and a 125-dimensional kernel on mixture differences. This
number is exact:

\[
 125=(6-1)^3.
\]

We construct two distinct nonnegative mixtures in that kernel with identical
histories. Therefore agreement and injectivity on every pure alternative do
not imply identifiability of mixtures.

This obstruction motivates the adjacent recovery target. The Stage I repeated
late protocol has simplex-tangent condition number \(2.65\times10^9\).
Moving measurements early but reusing the same sensor still gives
\(7.42\times10^7\). Refreshing 32 channels independently at every early time
reduces the condition number to \(12.75\). At Gaussian noise standard deviation
\(0.01\), the predicted affine least-squares RMSE is \(0.13648\), the simulated
value is \(0.13647\), and projection onto the probability simplex reduces it
to \(0.08792\). The result is a finite stable regime for arbitrary mixtures,
not merely sparse or pure alternatives.

## 1. What “protocol invariance” can mean

Let \(\mathcal O_A\) and \(\mathcal O_B\) be two observable-history operators
on the same latent vector space. Absolute distance scale is conventional: one
observer may measure in units that differ by a global gain. The meaningful
comparison is therefore up to one positive scalar.

For a declared set of nonzero differences \(D\), define

\[
 r(v)=\frac{\|\mathcal O_Av\|_2}{\|\mathcal O_Bv\|_2},
 \qquad v\in D,
\]

provided the denominator and numerator are nonzero. The **scale-free
bi-Lipschitz dilation** is

\[
 K_D(A,B)=\frac{\max_{v\in D}r(v)}{\min_{v\in D}r(v)}\geq1.
\]

For pure states,

\[
 D_{\rm pure}=\{e_i-e_j:1\leq i<j\leq n\}.
\]

For arbitrary mixture differences, the relevant set fills the simplex tangent
space

\[
 T=\left\{v\in\mathbb R^n:\sum_i v_i=0\right\}.
\]

### Proposition 1.1 — optimal symmetric scaling

Let \(r_{\min}\) and \(r_{\max}\) be the extreme ratios on \(D\). The global
scale

\[
 a_*=(r_{\min}r_{\max})^{-1/2}
\]

minimizes the largest multiplicative deviation from one, and

\[
 \frac1{\sqrt K}
 \leq a_*\frac{\|\mathcal O_Av\|_2}{\|\mathcal O_Bv\|_2}
 \leq\sqrt K
 \qquad(v\in D).
\]

#### Proof

After multiplication by \(a\), the two extreme ratios are
\(ar_{\min}\) and \(ar_{\max}\). A minimax symmetric choice makes them
reciprocals, so \(a^2r_{\min}r_{\max}=1\). Substitution gives the displayed
bounds. \(\square\)

Thus \(K=1\) means exact equality up to scale. At \(K=1.292\), the optimal
rescaled distances all lie between \(0.880\) and \(1.137\) times the reference
distances. This worst-case finite diagnostic is stricter than correlation.

## 2. Conditional invariance from random projection

Fix times \(t_1,\ldots,t_m\), diffusion operators
\(P_\ell=e^{-t_\ell L}\), and complete-observation distance

\[
 d_{\rm full}(e_i,e_j)^2
 =\sum_{\ell=1}^{m}\|P_\ell(e_i-e_j)\|_2^2.
\]

Let \(C\in\mathbb R^{q\times n}\) have independent entries
\(\pm1/\sqrt q\). It may be reused at every time, or an independent
\(C_\ell\) may be drawn at each time.

### Theorem 2.1 — finite pure-history preservation

There is a universal constant \(c>0\) such that, for
\(0<\varepsilon<1\) and \(0<\delta<1\),

\[
 q\geq c\varepsilon^{-2}
 \log\!\left(\frac{2m{n\choose2}}{\delta}\right)
\]

is sufficient for the following event with probability at least
\(1-\delta\): simultaneously for every pure pair,

\[
 (1-\varepsilon)d_{\rm full}(e_i,e_j)^2
 \leq d_C(e_i,e_j)^2
 \leq(1+\varepsilon)d_{\rm full}(e_i,e_j)^2.
\]

The statement holds both for one reused sign matrix and for independently
refreshed sign matrices.

#### Proof

Apply the standard Rademacher Johnson–Lindenstrauss concentration inequality to
the finite collection

\[
 \mathcal V=
 \{P_\ell(e_i-e_j):1\leq\ell\leq m,\ i<j\}.
\]

It contains at most \(m{n\choose2}\) vectors. A union bound makes every
individual squared norm lie between \((1-\varepsilon)\|v\|_2^2\) and
\((1+\varepsilon)\|v\|_2^2\). Sum those inequalities over \(\ell\) for each
pair. Independence between times is not needed for the reused-matrix version;
for refreshed matrices the same union bound applies to all matrix–vector
pairs. \(\square\)

### Corollary 2.2 — protocol agreement on pure states

On the event of Theorem 2.1,

\[
 K_{D_{\rm pure}}(C,\mathrm{full})
 \leq\sqrt{\frac{1+\varepsilon}{1-\varepsilon}}.
\]

If two protocols both satisfy the same \(\varepsilon\) bound against complete
observation, then

\[
 K_{D_{\rm pure}}(A,B)
 \leq\frac{1+\varepsilon}{1-\varepsilon}.
\]

This supplies an actual conditional invariance theorem. Its domain is finite
pure-state differences. It does not imply a lower bound on every vector in the
\((n-1)\)-dimensional mixture tangent space. Preserving a finite cloud requires
only logarithmically many random coordinates; embedding an entire
high-dimensional subspace is a different problem.

## 3. Why time schedules legitimately disagree

Even perfect sensors do not remove protocol dependence if observers watch at
different times.

### Proposition 3.1 — schedule as spectral filter

For complete observation \(C=I\) at a multiset of times \(\mathcal T\),

\[
 G_{\mathcal T}
 =\sum_{t\in\mathcal T}P_t^{\mathsf T}P_t
 =\sum_{t\in\mathcal T}e^{-2tL}
 =g_{\mathcal T}(L),
\]

where

\[
 g_{\mathcal T}(\lambda)=\sum_{t\in\mathcal T}e^{-2t\lambda}.
\]

Two complete schedules induce the same metric up to scale on an
\(L\)-invariant subspace if their filters are proportional on every eigenvalue
present in that subspace.

#### Proof

Symmetry of \(L\) gives \(P_t^{\mathsf T}P_t=e^{-2tL}\). Functional calculus
diagonalizes both Gramians in the eigenbasis of \(L\). Proportional filter
values therefore give proportional quadratic forms. Conversely, proportional
quadratic forms on each represented eigenspace require proportional filter
values there. \(\square\)

Late observations suppress high-frequency modes much more strongly than early
ones. Their disagreement is not sensor failure; the observers ask different
dynamical questions.

## 4. Pooling observers and the common kernel

Let \(\{\mathcal O_a\}_{a\in A}\) be any finite protocol family.

### Theorem 4.1 — pooled geometry

Define the pooled history operator by vertical concatenation and its Gram by

\[
 \mathcal O_{\rm pool}
 =\begin{bmatrix}\mathcal O_1\\\vdots\\\mathcal O_k\end{bmatrix},
 \qquad
 G_{\rm pool}=\sum_{a=1}^kG_a.
\]

Then

\[
 d_{\rm pool}(x,y)^2=\sum_{a=1}^kd_a(x,y)^2
\]

and

\[
 \ker\mathcal O_{\rm pool}
 =\bigcap_{a=1}^k\ker\mathcal O_a.
\]

#### Proof

Both statements follow from

\[
 \|\mathcal O_{\rm pool}v\|_2^2
 =\sum_a\|\mathcal O_av\|_2^2.
\]

The sum is zero exactly when every nonnegative summand is zero. \(\square\)

Protocol diversity can therefore remove blind directions, but only directions
that at least one observer sees. The next construction shows that apparently
complementary observers can still share a large interaction kernel.

## 5. Exact axis-blind obstruction

Identify the factorization state space with

\[
 V=(\mathbb R^s)^{\otimes r}.
\]

Let \(\mathbf1\in\mathbb R^s\) be the constant vector. A sensor blind to axis
\(j\) has rows in

\[
 W_j=(\mathbb R^s)^{\otimes(j-1)}
 \otimes\operatorname{span}\{\mathbf1\}
 \otimes(\mathbb R^s)^{\otimes(r-j)}.
\]

Such a row is constant while the \(j\)-th exponent varies. Because the heat
operator is a tensor product of path heat operators and preserves constants,
every later history row remains in \(W_j\).

### Theorem 5.1 — shared interaction kernel

The pooled row space of one axis-blind protocol for every axis is contained in
\(W_1+\cdots+W_r\). Its kernel contains

\[
 H=(\mathbf1^\perp)^{\otimes r},
\]

whose dimension is

\[
 \dim H=(s-1)^r.
\]

If the history rows span each \(W_j\), then the common kernel equals \(H\) and
the pooled history rank is

\[
 s^r-(s-1)^r.
\]

#### Proof

The orthogonal complement of \(W_j\) consists of tensors mean-zero in the
\(j\)-th factor. Intersecting these complements over every \(j\) gives tensors
mean-zero in every factor, namely \((\mathbf1^\perp)^{\otimes r}\). Its
dimension is the product of the factor dimensions, \((s-1)^r\). If every
\(W_j\) is spanned, no additional orthogonal direction remains. Apply
Theorem 4.1. \(\square\)

### Proposition 5.2 — pure states can still all be separated

For \(r\geq2\), the complete collection of axis-blind marginal projections is
injective on pure tensor-basis states.

#### Proof

The projection blind to axis \(j\) retains the tuple of all coordinates except
the \(j\)-th. Given these reduced tuples for at least two distinct axes, every
coordinate of the original pure state is determined. \(\square\)

Thus pure injectivity and mixture injectivity are mathematically different.

### Proposition 5.3 — explicit nonnegative collision

Let \(w=(1,-1,0,\ldots,0)\in\mathbf1^\perp\),
\(h=w^{\otimes r}\), and \(u\) be the uniform distribution on \(s^r\) states.
Then

\[
 p_\pm=u\pm\frac1{2s^r}h
\]

are distinct nonnegative probability distributions and every axis-blind
protocol gives them identical histories.

#### Proof

Every coordinate of \(h\) is \(-1,0\), or \(1\), so each coordinate of
\(p_\pm\) is nonnegative. Since every factor \(w\) has sum zero, \(h\) has sum
zero, hence both distributions have total mass one. Theorem 5.1 puts \(h\) in
every axis-blind kernel. \(\square\)

For \(r=3,s=6\), their separation is

\[
 \|p_+-p_-\|_2=\frac{2^{3/2}}{6^3}
 =0.01309457\ldots,
\]

while their theoretical signature separation is exactly zero.

## 6. Basis-invariant stable directions: a Stage I correction

The factorization Laplacian has an exactly threefold degenerate slow
eigenvalue. Stage I initially evaluated observation energy on the individual
eigenvectors returned by a numerical eigensolver. Inside a degenerate
eigenspace those vectors can rotate arbitrarily, so their individual energies
are not invariant.

Let \(V_\lambda\) be any orthonormal basis for an eigenspace. The correct
object is

\[
 (\mathcal OV_\lambda)^{\mathsf T}(\mathcal OV_\lambda).
\]

Its eigenvalues—equivalently the squared singular values of
\(\mathcal OV_\lambda\)—are unchanged when the basis is replaced by
\(V_\lambda R\) for an orthogonal matrix \(R\). We therefore define the
observable dimension of the stable eigenspace as the number of these energy
eigenvalues above the declared threshold.

The corrected Stage I random protocol still observes all three slow
directions, with invariant energies

\[
 3.75161,\qquad3.37553,\qquad2.73224.
\]

Each axis-blind protocol has observable slow dimension exactly two. This is a
substantive methodological correction but does not change any Stage I count,
distance, control contrast, or conclusion.

## 7. Stable recovery on the probability simplex

Let

\[
 T=\mathbf1^\perp
\]

be the \((n-1)\)-dimensional tangent space of unit-sum mixtures, and let
\(B\in\mathbb R^{n\times(n-1)}\) have orthonormal columns spanning \(T\).
Define the restricted history matrix

\[
 A=\mathcal OB.
\]

### Theorem 7.1 — affine mixture stability

Suppose \(A\) has full column rank. For observations

\[
 y=\mathcal Ox+\eta,
 \qquad \mathbf1^{\mathsf T}x=1,
\]

the unit-sum least-squares estimator satisfies

\[
 \|\widehat x-x\|_2
 \leq\frac{\|\eta\|_2}{\sigma_{\min}(A)}.
\]

If \(\eta\sim N(0,\nu^2I)\), then

\[
 \mathbb E\|\widehat x-x\|_2^2
 =\nu^2\sum_{k=1}^{n-1}\sigma_k(A)^{-2}.
\]

#### Proof

Choose any unit-sum center \(u\). Write \(x=u+Bz\). Least squares gives
\(\widehat z-z=A^\dagger\eta\), and orthonormality of \(B\) yields

\[
 \|\widehat x-x\|_2=\|A^\dagger\eta\|_2
 \leq\|A^\dagger\|_2\|\eta\|_2.
\]

The operator norm is \(1/\sigma_{\min}(A)\). Under isotropic Gaussian noise,
the coefficient covariance is
\(\nu^2(A^{\mathsf T}A)^{-1}\); taking its trace proves the expectation.
\(\square\)

### Corollary 7.2 — simplex projection cannot increase error

If the true \(x\) lies in the probability simplex \(\Delta\) and
\(\Pi_\Delta\) is Euclidean projection, then

\[
 \|\Pi_\Delta(\widehat x)-x\|_2
 \leq\|\widehat x-x\|_2.
\]

This follows from the projection inequality for a closed convex set. The
committed implementation uses the standard sorting-and-thresholding exact
simplex projection.

### Proposition 7.3 — expected Gram of random sensors

For normalized sign sensors, whether reused or refreshed,

\[
 \mathbb E[C_t^{\mathsf T}C_t]=I
\]

and therefore

\[
 \mathbb E[\mathcal O^{\mathsf T}\mathcal O]
 =\sum_t e^{-2tL}=G_{\rm full}.
\]

Independent refreshment does not change the expected Gram. It changes
concentration and prevents one sensor's blind or weak directions from being
repeated coherently at every time.

## 8. Experimental design

The latent universe is unchanged from Stage I:

- 216 states \(2^a3^b5^c\), \(0\leq a,b,c<6\);
- the Cartesian product of three six-vertex paths;
- 14 observations per protocol;
- normalized Rademacher channels with fixed reproducible seeds.

Four time schedules are compared:

| schedule | times |
|---|---|
| early | 14 geometric times from 0.02 to 1 |
| broad | 14 geometric times from 0.02 to 8 |
| Stage I | 14 geometric times from 1 to 8 |
| late | 14 geometric times from 2 to 16 |

At channel counts 8, 16, 32, and 64, 16 seeded protocols are tested in two
forms:

1. **repeated:** one sign matrix is reused at all 14 times;
2. **refreshed:** a new independent sign matrix is used at each time.

Each protocol is compared with complete observation at the same schedule.
Consecutive seed pairs are also compared directly. The principal metric is
worst-case scale-free dilation. Spearman correlation is reported but can be
unstable when the complete geometry has a narrow distance distribution.

## 9. Protocol-invariance results

### 9.1 Complete observers at different schedules

| schedules | Spearman | dilation \(K\) | optimal symmetric factors |
|---|---:|---:|---:|
| early vs broad | 0.99923 | 1.00774 | [0.9962, 1.0039] |
| early vs Stage I | 0.78222 | 6.26078 | [0.3997, 2.5022] |
| early vs late | 0.66367 | 8.86108 | [0.3359, 2.9768] |
| Stage I vs late | 0.97714 | 1.87400 | [0.7305, 1.3689] |

The broad logarithmic schedule is almost identical to the early schedule
because its early samples dominate high-frequency energy. Arbitrary schedule
invariance is decisively rejected: even complete early and late observers
differ by almost a factor of nine in scale-free dilation.

### 9.2 Stage I time window

Medians across 16 seeds:

| channels | repeated dilation | refreshed dilation | repeated mixture condition | refreshed mixture condition |
|---:|---:|---:|---:|---:|
| 8 | 5.252 | 1.977 | rank deficient | rank deficient |
| 16 | 2.940 | 1.633 | rank deficient | numerically rank deficient |
| 32 | 2.109 | 1.398 | \(2.55\times10^9\) | \(2.07\times10^8\) |
| 64 | 1.688 | 1.258 | \(6.60\times10^6\) | \(1.98\times10^6\) |

Refreshed sensors give substantially more invariant pure-state geometry, but
late diffusion has already erased high-frequency mixture directions. More
channels help without curing that spectral loss.

For 32 refreshed channels, Spearman correlation against complete observation
is \(0.9852\pm0.0027\), and the median dilation between paired independent
protocols is \(1.610\). At 64 channels the corresponding values are
\(0.9924\pm0.0015\) and \(1.385\).

### 9.3 Early time window

Medians across 16 seeds:

| channels | repeated dilation | refreshed dilation | repeated mixture condition | refreshed mixture condition |
|---:|---:|---:|---:|---:|
| 8 | 13.884 | 1.711 | rank deficient | rank deficient |
| 16 | 3.671 | 1.440 | rank deficient | 766.4 |
| 32 | 2.240 | 1.292 | \(5.49\times10^7\) | 12.62 |
| 64 | 1.669 | 1.189 | 5314 | 5.27 |

Early complete-observation distances are close to a common value because
\(P_t\) remains near the identity. Consequently their fine rank ordering is
fragile: at 32 refreshed channels, mean Spearman correlation is only 0.7809
despite a median worst-case dilation of 1.292 and log-RMS distortion of 0.0309.
This is precisely why correlation alone is not an invariance certificate.

Directly paired 32-channel refreshed protocols have median dilation 1.454,
corresponding after optimal scaling to worst-case factors approximately
\([0.829,1.206]\). At 64 channels, paired dilation falls to 1.304.

The empirical trend matches Theorem 2.1: more independent channels concentrate
the finite pure-state geometry around complete observation. The theorem gives
asymptotic order rather than a sharp constant for this experiment.

## 10. Adversarial observer results

Each 32-channel axis-blind observer is tested on the early schedule.

| erased exponent axis | history rank | maximum collapsed-fiber signature gap | observable slow dimension |
|---:|---:|---:|---:|
| 0 | 36 | \(4.05\times10^{-15}\) | 2 |
| 1 | 36 | \(4.45\times10^{-15}\) | 2 |
| 2 | 36 | \(3.91\times10^{-15}\) | 2 |

The tiny gaps are floating-point residue; the collapse is exact by
construction.

Pooling all three observers gives:

| diagnostic | result |
|---|---:|
| computed history rank | 91 |
| exact predicted rank \(216-5^3\) | 91 |
| minimum pure-state signature margin | 1.40440 |
| mixture-tangent rank | 90 of 215 |
| mixture-tangent kernel dimension | 125 |
| exact predicted common kernel | 125 |
| explicit mixture separation | 0.01309457 |
| explicit signature gap | \(2.94\times10^{-17}\) |

This is the central obstruction of Stage II:

> Multiple observers can jointly separate every pure state with a large
> margin while remaining exactly blind to a high-dimensional family of
> mixture differences.

No amount of noise reduction can recover the explicit collision from those
protocols. A new kind of sensor or intervention is required.

## 11. Adjacent target: stable arbitrary-mixture recovery

The obstruction made the adjacent target necessary. We compare three
32-channel, 14-time protocols using the same seed:

| protocol | tangent condition | smallest singular value | predicted affine RMSE | simulated affine RMSE | simplex-projected RMSE |
|---|---:|---:|---:|---:|---:|
| Stage I, late repeated | \(2.648\times10^9\) | \(7.51\times10^{-10}\) | \(1.9917\times10^7\) | \(1.9252\times10^7\) | 0.99998 |
| early repeated | \(7.422\times10^7\) | \(1.07\times10^{-7}\) | \(1.3265\times10^5\) | \(1.3297\times10^5\) | 0.99940 |
| early refreshed | 12.7487 | 0.34632 | 0.13648 | 0.13647 | 0.08792 |

The noise standard deviation is \(0.01\) independently in each of 448 history
coordinates. The simulation uses the same 200 dense Dirichlet mixtures and
noise arrays for all three protocols.

Three lessons follow.

1. **Early observation is necessary here.** Once diffusion has suppressed a
   high-frequency direction by many orders of magnitude, sensor diversity
   cannot restore its original amplitude.
2. **Early observation is not sufficient.** Reusing one sensor coherently
   repeats its weak directions, leaving condition number
   \(7.42\times10^7\).
3. **Early independent refreshment is sufficient in this finite experiment.**
   It makes all 215 mixture-tangent directions numerically visible with a
   moderate condition number and a Gaussian error matching Theorem 7.1.

Simplex projection converts the stable affine estimate into a feasible
probability distribution and reduces RMSE by roughly 36%. In the two unstable
protocols it merely projects a catastrophic affine estimate onto a nearly
arbitrary simplex boundary point, leaving error near one.

This is a computed finite stable regime. A sharp nonasymptotic lower bound on
the refreshed restricted Gram remains future theorem work.

## 12. What Stage II establishes

### Exact results

1. A scale-free minimax definition of protocol distortion and its optimal
   global rescaling.
2. A Johnson–Lindenstrauss pure-history preservation theorem for finite random
   protocols.
3. A spectral-filter characterization of time-schedule dependence.
4. Pooled protocol Gramians add and their kernels intersect.
5. Complete axis-blind families retain a
   \((s-1)^r\)-dimensional interaction kernel.
6. Distinct nonnegative mixtures can be constructed explicitly in that kernel.
7. Affine least-squares mixture error is controlled exactly by the restricted
   singular values, and simplex projection cannot worsen Euclidean error.
8. Observation dimension inside a degenerate eigenspace must be computed from
   invariant restricted singular values.

### Computed results for the reference universe

1. Random protocols concentrate toward complete pure-state geometry as channel
   count grows.
2. Independently refreshed sensors outperform one repeated sensor in both
   pure-state distortion and mixture conditioning.
3. Arbitrary complete time schedules do not induce one invariant geometry.
4. Three axis-blind protocols separate all pure states but have the exact
   predicted 125-dimensional mixture kernel.
5. Early refreshed sensing produces a stable arbitrary-mixture recovery regime
   with condition number 12.75 and projected RMSE 0.0879 at the declared noise.

### Rejected claims

1. Operational geometry is not observer independent across arbitrary protocol
   classes.
2. Pure-state injectivity does not imply mixture injectivity.
3. Full numerical rank does not imply stable inversion.
4. Early sampling by itself does not cure coherent sensor weakness.
5. High correlation alone is not a bi-Lipschitz invariance certificate.

## 13. Literature and novelty boundary

The main established ingredients are:

- the original finite-dimensional random-projection lemma of
  [Johnson and Lindenstrauss (1984)](https://web.stanford.edu/class/cs114/readings/JL-Johnson.pdf);
- observability Gramians and their conditioning, originating in classical
  control theory and used in modern randomized sensor-selection guarantees,
  for example [Bopardikar (2021)](https://doi.org/10.1016/j.automatica.2020.109340);
- exact Euclidean simplex projection by sorting and thresholding, as presented
  by [Duchi, Shalev-Shwartz, Singer, and Chandra (2008)](https://stanford.edu/~jduchi/projects/DuchiShSiCh08.pdf);
- elementary tensor-product linear algebra and path heat semigroups.

The project contribution is the particular synthesis and falsification chain:

1. distinguish pure-cloud protocol invariance from full mixture-subspace
   invariance;
2. derive and test exact axis-blind common kernels in the prime-factor product
   universe;
3. exhibit the paradoxical but rigorous regime in which all pure states are
   separated while a 125-dimensional mixture kernel remains;
4. connect this obstruction to an early refreshed-sensor remedy and verify the
   Gaussian least-squares error prediction numerically;
5. identify and correct basis dependence in the Stage I slow-mode diagnostic.

The random-projection, Gramian, projection, and tensor facts are classical.
No claim of literature priority is made for the combined construction without
independent specialist review and a broader literature search.

## 14. Scope and nonclaims

This work does **not** establish:

- an observer-independent geometry across all possible measurements;
- that the universe uses a factorization lattice;
- a physical theory of matter, fields, spacetime, or quantum measurement;
- continuum, causal, or Lorentzian geometry;
- a sharp finite-sample random-matrix theorem for the refreshed protocol;
- successful recovery outside the declared finite dynamics, noise, and sensor
  family;
- a connection to zeta zeros or the Riemann hypothesis.

It does establish something useful for future physical models: claims of
emergent geometry must specify their protocol class, prove invariance within
that class, and test common kernels on mixtures or interactions—not only on a
catalogue of pure states.

## 15. Reproduction

Run the Stage II tests:

```sh
python -m unittest -v test_operational_information_geometry_ii.py
```

Recompute all 16-protocol ensembles, schedule comparisons, adversarial
observers, explicit collision, and mixture-recovery study:

```sh
python operational_information_geometry_ii.py --protocols 16
```

Run both Operational Information Geometry layers:

```sh
python -m unittest -v \
  test_operational_information_geometry.py \
  test_operational_information_geometry_ii.py
```

Validate the complete repository:

```sh
python -m unittest discover -v
```

## 16. Next research order

### Immediate target — Stage III: compositional operational geometry

Study two independent factorization universes, then add controlled
interactions. For independent systems, derive exact tensor/Kronecker laws for
history Gramians and quotient kernels. For coupled systems, define and measure
the defect from product geometry. The central falsification question is
whether an interaction creates operational structure that cannot be explained
by either subsystem or by sensor choice alone.

Primary tests:

1. prove composition laws for complete and factorized protocols;
2. separate classical mixture correlations from dynamical interactions;
3. construct interaction-blind sensors analogous to the Stage II axis-blind
   controls;
4. seek a curvature-like product defect only after its sensor dependence is
   quantified;
5. test whether pooled local observers can recover global interaction modes.

### Adjacent theorem target — refreshed mixture concentration

The empirical condition number 12.75 deserves a theorem. Apply matrix
concentration to the independent rank-one history contributions and derive a
finite lower bound on the smallest simplex-tangent eigenvalue in terms of the
complete Gram, channel count, time schedule, and leverage. This target should
be revisited before any claim that stable mixture recovery scales beyond the
216-state laboratory.

Stage III is the next conceptual step. The concentration theorem remains an
adjacent dependency and should be pulled forward if composition experiments
require quantitative mixture stability.
