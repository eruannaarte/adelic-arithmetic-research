# Arithmetic Observability I

## Nuisance quotients, integer-lattice trichotomy, and prime-valuation geometry

- **Research lead, theorem synthesis, computation, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** first complete theory kernel within this programme; not peer reviewed
- **Date:** 14 August 2026
- **Parent programmes:** Operational Information Geometry and Arithmetic Sensing

## Abstract

Arithmetic observability asks which local arithmetic distinctions are actually
determined, and stably determined, by incomplete global harmonic data.  The
answer depends on three structures that must not be conflated: the arithmetic
model class, the observation protocol, and the allowed nuisance or tail.

This paper gives the first unified framework within this research programme.
For a linear local query observed through a global response with an
unrestricted nuisance subspace, orthogonal projection away from the nuisance
produces the exact observational quotient.
The induced factor map has an optimal norm `kappa`, and the adversarial minimax
query error at noise radius `epsilon` is exactly `kappa epsilon`.  The matching
lower bound is realized by the least distinguishable direction; it is not only
an estimator upper bound.

Arithmetic integrality then creates a trichotomy absent from ordinary linear
observability.  A linear protocol on an integer lattice may have an exact
integer collision; it may be injective on every integer point while its
minimum observation separation is zero; or it may produce a genuinely
separated observation lattice.  In the middle regime exact identification at
infinite precision coexists with failure at every positive uniform noise
radius.  Applied to finite Dirichlet polynomials, this proves that for almost
every single sampling time one complex trace value identifies every
nonnegative integer coefficient vector at a fixed cutoff, yet for cutoffs
`N>=4` the protocol is uniformly unstable.  A bounded-height pigeonhole bound
quantifies the collapse.

A second arithmetic model gives a completely explicit geometry.  On the prime
box

\[
 n=\prod_{j=1}^r p_j^{\alpha_j},
 \qquad 0\leq\alpha_j<s,
\]

sampling at times `2 pi m/log p_j` recovers exactly the complementary marginal
obtained by summing out the `p_j`-valuation.  After declared inverse-Vandermonde
calibration, the pooled Gram has the exact ANOVA spectrum

\[
 \lambda_S=\sum_{j\notin S}w_j,
 \qquad \dim H_S=(s-1)^{|S|}.
\]

All pure monomials are separated when `r>=2`, but the full interaction space
has dimension `(s-1)^r` and is completely invisible.  The positive quotient
floor is `min_j w_j`, uniform weights are exactly E-optimal with floor `1/r`,
and the quotient reconstruction constant is sharp.  For
`(p_1,p_2,p_3)=(2,3,5)` and `s=4`, the exact certificate has ambient dimension
64, rank 37, a 27-dimensional kernel, and quotient floor `1/3`.

Finally, the formal degree-fourteen Arithmetic Sensing V artifact is converted
into a certified arithmetic-fibre distance bracket.  Under its declared
`d_14` tail model, different integer prefixes through 50 are separated in the
weighted observation geometry by at least

\[
 1.5774701544883733\times10^{-6},
\]

so adversarial noise below

\[
 7.8873507724418666\times10^{-7}
\]

is certified not to merge prefix fibres.  A constructive pair gives the upper
radius `2e-4`.  Closing this factor-254 gap is a concrete next problem.

The abstract linear ingredients are standard inverse theory, lattice geometry,
and Vandermonde algebra.  The contribution claimed here is their precise
synthesis into a falsifiable arithmetic-observability framework and the two
explicit arithmetic realizations.  No literature-priority claim is made.

---

## 1. The question and the separation of layers

The operational question is:

> Given a class of arithmetic alternatives, a declared global harmonic
> protocol, an allowed nuisance or tail, and a noise metric, which local query
> is determined, how stable is its recovery, and what geometry is induced on
> the distinctions that survive?

There are at least two maps before an observation is produced:

\[
 \text{arithmetic object}
 \longrightarrow
 \text{arithmetic features}
 \longrightarrow
 \text{harmonic data}.
 \tag{1.1}
\]

For a number field, the middle feature might be its sequence of ideal-count
coefficients.  The second map might sample the corresponding Dirichlet series.
A collision in the first map cannot be repaired by changing only the second.
Conversely, perfect object-level features can still be lost by a deficient
sampling protocol.

This gives three distinct obstructions.

1. **Representation obstruction.**  Different objects have the same chosen
   feature.  Arithmetically equivalent nonisomorphic number fields are an
   exact example.
2. **Acquisition obstruction.**  Different features lie in the same fibre of
   the observation map.  Harmonic aliases and rank loss are examples.
3. **Nuisance obstruction.**  A target distinction can be cancelled by an
   allowed tail or calibration direction.

Arithmetic Sensing I--VI developed recovery certificates and concrete
obstructions for a particular coefficient model.  Operational Information
Geometry I--XII developed quotient metrics, generalized observable spectra,
and continuum-to-finite transfer.  The missing bridge was a theorem stated
for a *local arithmetic query* rather than for recovery of an entire latent
vector.  That is the starting point here.

---

## 2. General arithmetic-observability framework

### 2.1 Object-first response fibres

Let `M` be any arithmetic model class, let `q:M->Z` be the desired local
query, and let

\[
 \mathcal F_m\subseteq Y
\]

be the set of every noiseless response allowed for object `m`, including its
declared tails and nuisances.  Two objects form a zero-noise indistinguishable
pair when

\[
 \mathcal F_m\cap\mathcal F_{m'}\ne\varnothing.
\]

The query is exactly identifiable on this model if every such intersection
implies `q(m)=q(m')`.  Quantitative robustness is controlled by the pairwise
fibre separation

\[
 \Delta(m,m')
 =\operatorname{dist}(\mathcal F_m,\mathcal F_{m'}).
 \tag{2.0}
\]

At noise radius `epsilon`, the observed datum has the form

\[
 y=f+\eta,
 \qquad f\in\mathcal F_m,
 \qquad \|\eta\|_Y\leq\varepsilon.
\]

Disjoint noncompact fibres can have zero separation.  Moreover, set distance
between arbitrary fibres need not satisfy the triangle inequality.  Therefore
`Delta` is not called a pseudometric in this generality.  A useful query
modulus is

\[
 \omega_q(\varepsilon)
 =\frac12\sup\left\{
 \|q(m)-q(m')\|:
 \Delta(m,m')\leq2\varepsilon
 \right\}.
\]

The supremum of the empty set is taken to be zero.

Whenever the relevant closest points are attained, their midpoint proves
that no decoder can have uniform error smaller than this pairwise lower
modulus.  An equally sharp upper theorem requires additional structure.  The
common-subspace model below has exactly that structure; the constrained
arithmetic fibres of Section 8 give another special case.

### 2.2 Linear common-subspace model

Let `X`, `Y`, and `Z` be finite-dimensional real or complex Hilbert spaces.
The local target is `x in X`; the desired arithmetic query is

\[
 Lx\in Z.
\]

The declared experiment is

\[
 y=Hx+Bz+\eta,
 \qquad \|\eta\|_Y\leq\varepsilon,
 \tag{2.1}
\]

where `H:X->Y` is the global observation, `B:U->Y` maps an unrestricted
nuisance parameter from a finite-dimensional Hilbert space `U` into the data
space, and `eta` is bounded adversarial noise.  Put

\[
 \mathcal N=\operatorname{ran}B,
 \qquad P=P_{\mathcal N^\perp},
 \qquad A=PH.
 \tag{2.2}
\]

The component in `N` can be changed arbitrarily by nuisance and therefore
contains no uniform target information.  Projection gives the effective datum

\[
 Py=Ax+P\eta.
\]

### Definition 2.1 — exact equivalence and distinguishability

Two targets are observationally equivalent after profiling the nuisance when

\[
 x\sim_A x'
 \quad\Longleftrightarrow\quad
 A(x-x')=0.
 \tag{2.3}
\]

Equivalently, `H(x-x')` lies in `N`.  The experiment induces the pseudometric

\[
 d_A(x,x')=\|A(x-x')\|_Y.
 \tag{2.4}
\]

It is a genuine metric on `X/ker A`.  This is the Operational Information
Geometry quotient, now with the nuisance explicitly profiled.

### Definition 2.2 — local identifiability

The query `Lx` is exactly identifiable if observational equivalence always
implies query equivalence:

\[
 Ax=Ax'\Longrightarrow Lx=Lx'.
 \tag{2.5}
\]

For linear maps this is the kernel condition

\[
 \ker A\subseteq\ker L.
 \tag{2.6}
\]

The distinction matters: the complete target `x` can be unidentifiable while
a lower-dimensional local query remains exactly determined.

### Theorem 2.3 — local-query factorization and exact minimax radius

The following are equivalent:

1. `Lx` is exactly identifiable from `Ax`;
2. `ker A` is contained in `ker L`;
3. there is a unique linear map `R:ran A -> Z` satisfying

   \[
   L=RA.
   \tag{2.7}
   \]

When these conditions hold, define

\[
 \kappa(A,L)
 =\|R\|
 =\sup_{Ax\ne0}\frac{\|Lx\|_Z}{\|Ax\|_Y}.
 \tag{2.8}
\]

Use the convention `kappa=0` when `L=0` (including the trivial `A=L=0`
case).

For the observation model (2.1), the optimal worst-case error for estimating
`Lx`, uniformly over every target and nuisance, is exactly

\[
 \boxed{
 \inf_{\widehat q}
 \sup_{x,z,\|\eta\|\leq\varepsilon}
 \|\widehat q(Hx+Bz+\eta)-Lx\|_Z
 =\kappa(A,L)\varepsilon.}
 \tag{2.9}
\]

If (2.6) fails and the target space is unbounded, the minimax error is already
infinite at zero noise.

#### Proof

Condition (2.6) makes `R(Ax)=Lx` well-defined.  It is plainly linear and
unique on `ran A`; conversely (2.7) implies (2.6).

For the upper bound, let `P_A` be orthogonal projection onto `ran A` and use

\[
 \widehat q(y)=R P_A P y.
\]

Because `PBz=0` and orthogonal projections do not increase norm,

\[
 \|\widehat q(y)-Lx\|
 =\|R P_A P\eta\|
 \leq\kappa\varepsilon.
\]

If `epsilon=0`, the lower bound is trivial.  If `kappa=0`, the zero estimator
proves (2.9).  Otherwise, for positive `epsilon`, finite dimensionality makes
the supremum in (2.8) attainable after normalizing `||Ah||=1`.  Scale an
extremizer so that
`||Ah||=epsilon`.  The two targets `h` and `-h`, with nuisance choices that
cancel the `N`-components of `Hh` and `-Hh`, and noises `-Ah` and `Ah`, produce
the same datum.  Their queries are `Lh` and `-Lh`.  For every proposed answer
`q`, the triangle inequality gives

\[
 \max(\|q-Lh\|,\|q+Lh\|)\geq\|Lh\|=\kappa\varepsilon.
\]

Thus the upper constant is minimax sharp.  If `h in ker A` but `Lh` is
nonzero, arbitrary multiples of `h` have identical effective data and
unboundedly separated queries.  \(\square\)

### 2.3 Profiled Gram and quotient recovery

The profiled information form is

\[
 G_{\rm eff}=H^*PH.
 \tag{2.10}
\]

Since

\[
 P=I-B(B^*B)^\dagger B^*,
\]

this can be written as the Schur-complement form

\[
 G_{\rm eff}
 =H^*H-H^*B(B^*B)^\dagger B^*H.
 \tag{2.11}
\]

Give `X` a positive source metric `S`, with
`||h||_S^2=h^* S h`.  The minimum-cost quotient norm is

\[
 \|[h]\|_{S,q}
 =\min_{n\in\ker A}\|h+n\|_S.
 \tag{2.12}
\]

Define the positive quotient floor

\[
 \gamma
 =\inf_{[h]\ne0}
 \frac{\|Ah\|_Y^2}{\|[h]\|_{S,q}^2}.
 \tag{2.13}
\]

If the quotient is zero-dimensional, use the convention `gamma=+infinity` and
`epsilon/sqrt(gamma)=0`.  Otherwise the finite-dimensional quotient makes
`gamma` positive.

Taking `L` to be the canonical quotient map in Theorem 2.3 gives

\[
 \boxed{R_\varepsilon^*=\frac{\varepsilon}{\sqrt\gamma}.}
 \tag{2.14}
\]

Thus a generalized Gram floor is not merely a conditioning diagnostic.  It is
the reciprocal square of the exact adversarial minimax constant.

### 2.4 Object-level equivalence

For a nonlinear arithmetic object class `M` with feature map `Phi:M->X`, the
induced equivalence is

\[
 m\sim m'
 \quad\Longleftrightarrow\quad
 A(\Phi(m)-\Phi(m'))=0.
 \tag{2.15}
\]

The linear theorem controls feature recovery.  It cannot separate two objects
already identified by `Phi`.  This limitation will matter again in Section 9.

---

## 3. Integer lattices: identifiability is not stability

Let `Lambda` be a full lattice of rank `ell` in its real span `V`, and let
`A:V->Y` be real linear.  A complex observation is treated by realifying its
real and imaginary parts.  Define

\[
 \delta(A,\Lambda)
 =\inf_{\lambda\in\Lambda\setminus\{0\}}\|A\lambda\|.
 \tag{3.1}
\]

### Theorem 3.1 — arithmetic-observability trichotomy

Exactly one of the following regimes holds.

1. **Exact collision.**

   \[
   \ker A\cap\Lambda\ne\{0\}.
   \tag{3.2}
   \]

   Then distinct lattice targets give exactly identical data.

2. **Exact arithmetic identification without stable separation.**

   \[
   \ker A\cap\Lambda=\{0\},
   \qquad \operatorname{rank}(A|_V)<\ell.
   \tag{3.3}
   \]

   Every lattice target is identifiable at infinite precision, but

   \[
   \delta(A,\Lambda)=0.
   \tag{3.4}
   \]

   Hence every positive uniform adversarial noise radius fails.

3. **Stable lattice observability.**

   \[
   \operatorname{rank}(A|_V)=\ell.
   \tag{3.5}
   \]

   The image `A Lambda` is a discrete lattice,

   \[
   \delta(A,\Lambda)>0,
   \tag{3.6}
   \]

   and nearest-image decoding is uniformly correct for noise strictly below
   `delta/2`.  The radius `delta/2` is optimal: a shortest pair and its
   midpoint are ambiguous at equality.

#### Proof

The first equivalence follows because two lattice points collide exactly when
their nonzero lattice difference lies in `ker A`.

In regime 2, `A Lambda` is an abstract free abelian group of rank `ell` inside
a real space of dimension smaller than `ell`.  A discrete subgroup of a
finite-dimensional real vector space has rank no larger than the dimension of
its span.  Therefore `A Lambda` is not discrete.  Because it is a group,
nondiscreteness supplies nonzero elements arbitrarily close to zero, proving
(3.4).

In regime 3, `A` is bounded below on `V`: there is `c>0` with
`||Av||>=c||v||`.  A lattice has a positive shortest-vector length, so its
image does as well.  Bounded image balls have finite preimages, hence the
infimum in (3.1) is attained.  Noise below half the shortest distance leaves
a unique nearest codeword.  At half the distance, the midpoint of a shortest
pair lies in both closed noise balls.  \(\square\)

### Proposition 3.2 — quantitative crowding in the middle regime

Take `Lambda=Z^ell`, identify `ran A` orthonormally with `R^d`, and suppose
`1<=d<ell`.  There is a constant `C_A` such that for every sufficiently large
positive integer `Q` one can find a nonzero integer vector with

\[
 \|z\|_\infty\leq Q,
 \qquad
 \|Az\|_2\leq C_A Q^{1-\ell/d}.
 \tag{3.7}
\]

If there is no integer kernel, the constructed image `Az` is nonzero.

#### Proof

Consider the `(Q+1)^ell` points `Aq` with
`q in {0,...,Q}^ell`.  They lie in a `d`-dimensional box of side `O_A(Q)`.
Put

\[
 K_Q=\left\lceil(Q+1)^{\ell/d}\right\rceil-1.
\]

Partition each coordinate into `K_Q` intervals.  Since
`K_Q^d<(Q+1)^ell`, two images share a cell.  Their nonzero integer difference
has norm at most `Q`; because `K_Q` is comparable to `Q^(ell/d)`, its image
has diameter `O_A(Q^(1-ell/d))`.  \(\square\)

### 3.1 Geometry of the image lattice

The metric quotient
\(\Lambda/(\ker A\cap\Lambda)\) is isometric to `A Lambda`.  Its metric
completion is the closed subgroup

\[
 \overline{A\Lambda}\subseteq Y.
 \tag{3.8}
\]

In regime 2, a countable set of exactly distinct arithmetic states therefore
acquires nontrivial limit points in observation geometry.  This is a precise
sense in which incomplete observation can fold a discrete arithmetic space
into a continuum-like completion without producing an exact collision.

### 3.2 Restricted model classes

For a finite or otherwise restricted arithmetic model `C subset Lambda`, the
relevant difference set is `C-C`, not the whole lattice.  Define

\[
 \delta_C
 =\min_{x\ne x'\in C}\|A(x-x')\|.
 \tag{3.9}
\]

When `C` is finite and injectively observed, `delta_C>0` even in regime 2.
Nearest-signature decoding has the exact strict threshold `delta_C/2`.
Instability appears as the model class expands and these finite separations
collapse.

---

## 4. The one-trace paradox for Dirichlet coefficients

Fix real `sigma`, a cutoff `N`, and normalized finite Dirichlet polynomials

\[
 F_a(\sigma+it)
 =1+\sum_{n=2}^N a_n n^{-\sigma-it},
 \qquad a_n\in\mathbb Z_{\geq0}.
 \tag{4.1}
\]

One complex value is a real two-dimensional observation of the
`N-1`-dimensional coefficient vector.

### Theorem 4.1 — generic one-trace identification and zero uniform radius

Outside a countable measure-zero set of times `t`, the map

\[
 a\longmapsto F_a(\sigma+it)
 \tag{4.2}
\]

is injective on every nonnegative integer coefficient vector at the declared
cutoff.  If `N>=4`, then at every such generic time

\[
 \inf_{a\ne b}|F_a(\sigma+it)-F_b(\sigma+it)|=0.
 \tag{4.3}
\]

Thus one global trace value can identify all finite-cutoff integer vectors at
infinite precision while tolerating no positive uniform noise radius.

#### Proof

For each nonzero `v in Z^(N-1)`, put

\[
 f_v(t)=\sum_{n=2}^N v_n n^{-\sigma}e^{-it\log n}.
 \tag{4.4}
\]

Distinct real frequencies `log n` make the finite exponentials linearly
independent, so `f_v` is not identically zero.  It is entire as a function of
complex `t`, hence its real zero set is discrete.  There are countably many
integer vectors `v`, so the union of all exceptional zero sets is countable.
Outside it, no integer difference collides.

For `N>=4`, the real coefficient dimension `N-1` is larger than the real rank
of one complex observation, which is at most two.  Theorem 3.1 puts the map in
regime 2 and proves (4.3).  \(\square\)

### 4.1 An explicit exceptional collision

At `sigma=2`, take

\[
 a_2=4,\ a_3=0,
 \qquad
 b_2=0,\ b_3=9,
\]

with every other coefficient equal.  Since

\[
 4\,2^{-2-it}=e^{-it\log2},
 \qquad
 9\,3^{-2-it}=e^{-it\log3},
\]

the two polynomials collide whenever

\[
 t\log(3/2)\in2\pi\mathbb Z.
 \tag{4.5}
\]

The exceptional set is therefore a genuine alias set, not only a proof
artifact.

### Theorem 4.2 — bounded-height threshold and crowding ceiling

Let `H>=1` be an integer and let

\[
 \mathcal C_H
 =\{a:0\leq a_n\leq H,\ 2\leq n\leq N\},
\]

and define

\[
 \delta_H(t)
 =\min_{a\ne b\in\mathcal C_H}
 |F_a(\sigma+it)-F_b(\sigma+it)|.
 \tag{4.6}
\]

At every generic time, `delta_H(t)>0` and the exact strict adversarial
threshold is `delta_H(t)/2`.

Put

\[
 r=N-1,
 \qquad S_{N,\sigma}=\sum_{n=2}^N n^{-\sigma},
 \qquad
 Q_H=\left\lceil(H+1)^{r/2}\right\rceil-1.
\]

For every time, generic or exceptional,

\[
 \boxed{
 \delta_H(t)
 \leq \frac{2\sqrt2\,H S_{N,\sigma}}{Q_H}.}
 \tag{4.7}
\]

For `N>=4`, the right side is

\[
 O_{N,\sigma}(H^{1-r/2})\longrightarrow0.
 \tag{4.8}
\]

#### Proof

The finite-threshold statement is Section 3.2.  For (4.7), all
`(H+1)^r` signatures lie in the translated square

\[
 (1,0)+[-HS_{N,\sigma},HS_{N,\sigma}]^2.
\]

Partition each coordinate into `Q_H` intervals.  Since
`Q_H^2<(H+1)^r`, two signatures occupy one cell.  The cell diagonal is the
right side of (4.7).  \(\square\)

The ceiling does not give a matching lower law.  Determining the typical
Diophantine size of `delta_H(t)` is one of the first open quantitative
questions created by this theory.

### Theorem 4.3 — an unrestricted-tail no-go theorem

Keep one complex sample and allow arbitrary finitely supported real tail
perturbations above `N`.  Then the effective target operator in (2.2) is zero:
every finite prefix is observationally equivalent to every other one.

#### Proof

At `t=0`, both target and real tail occupy the same real line, which the tail
spans.  Let `t` be nonzero.  Among three distinct primes above `N`, at least
two phasors `p^{-sigma-it}` are noncollinear over `R`.  Otherwise all three
phase differences would be integer multiples of `pi`, forcing a rational
relation between two logarithmic prime ratios.  Exponentiation would give a
nontrivial multiplicative relation among distinct primes, contradicting
unique factorization.  Two noncollinear tail modes span `C` over `R`, so the
nuisance range is the entire one-sample data space.  Hence `P=0`.  \(\square\)

This theorem does **not** apply to the nonnegative, integral, growth-bounded
tails used by Arithmetic Sensing.  It shows that those arithmetic constraints
are logically essential rather than cosmetic regularization.

---

## 5. Prime-resonant global traces recover valuation marginals

Let `r>=2` and `s>=2` be integers, let `p_1,...,p_r` be distinct primes, and
let

\[
 E=\{0,1,\ldots,s-1\}^r.
\]

For `alpha in E`, put

\[
 n_\alpha=\prod_{k=1}^r p_k^{\alpha_k}.
\]

Consider the finite harmonic trace on the imaginary axis

\[
 F_c(t)=\sum_{\alpha\in E}c_\alpha n_\alpha^{-it}.
 \tag{5.1}
\]

On a line `Re z=sigma`, absorb `n_alpha^{-sigma}` into `c_alpha`; the recovered
quantity is then a weighted coefficient marginal and the source metric must be
changed accordingly.

For axis `j`, use

\[
 t_{j,m}=\frac{2\pi m}{\log p_j},
 \qquad 0\leq m<s^{r-1}.
 \tag{5.2}
\]

Let `M_j c` be the complementary marginal formed by summing out
`alpha_j`:

\[
 (M_jc)_\beta
 =\sum_{a=0}^{s-1}c_{\operatorname{insert}_j(a,\beta)}.
 \tag{5.3}
\]

### Theorem 5.1 — exact valuation-marginal recovery

The samples (5.2) satisfy

\[
 D_jc=V_jM_jc,
 \tag{5.4}
\]

where `V_j` is the square Vandermonde matrix on nodes

\[
 z_{j,\beta}
 =\exp\!\left(
 -\frac{2\pi i}{\log p_j}
 \sum_{k\ne j}\beta_k\log p_k
 \right).
 \tag{5.5}
\]

All nodes are distinct.  Therefore `V_j` is invertible and the global
harmonic samples determine exactly the complementary `p_j`-valuation
marginal (5.3).

#### Proof

At time (5.2), the factor contributed by `alpha_j` is

\[
 \exp(-2\pi i m\alpha_j)=1,
\]

so terms differing only in that exponent add, giving (5.4).  If two nodes
were equal, then for some integer `ell`,

\[
 \prod_{k\ne j}p_k^{\beta_k-\gamma_k}=p_j^\ell.
\]

Unique factorization forces every exponent difference and `ell` to be zero.
Thus the nodes are distinct and the Vandermonde determinant is nonzero.
\(\square\)

This result uses a known finite prime box, complex samples, exact timing, and
zero contribution outside the box.  It is an exact algebraic theorem, not yet
a claim about noisy physical clocks.  It is best viewed as a nontrivial
arithmetic harmonic toy model.  The arithmetic content is the resonant
sampling identity and its unique-factorization proof; after calibration, the
spectrum in Section 6 is the generic ANOVA geometry of marginals and does not
depend on the numerical values of the primes.

---

## 6. Exact distinguishability geometry of valuation marginals

Put

\[
 H=(\mathbb C^s)^{\otimes r},
 \qquad
 R_j=s^{-1/2}M_j.
\]

Then `P_j=R_j^*R_j` is the orthogonal projection onto arrays constant in
axis `j`.  For positive weights with `sum_j w_j=1`, define

\[
 O_wc=(\sqrt{w_j}R_jc)_{j=1}^r,
 \qquad
 G_w=O_w^*O_w=\sum_{j=1}^r w_jP_j.
 \tag{6.1}
\]

This is the geometry after the declared calibration

\[
 \widetilde D_j=s^{-1/2}V_j^{-1}D_j=R_j.
 \tag{6.2}
\]

It is not the raw iid-sample-noise geometry.

Let `U` be the constant line in `C^s` and `W=U^perp`.  For every subset
`S subset {1,...,r}`, define the ANOVA subspace

\[
 H_S
 =\bigotimes_{k\in S}W_k
  \otimes
  \bigotimes_{k\notin S}U_k.
 \tag{6.3}
\]

### Theorem 6.1 — complete spectrum, quotient, and optimal design

The spaces `H_S` form an orthogonal decomposition of `H`, and

\[
 G_w|_{H_S}=\lambda_S I,
 \qquad
 \boxed{\lambda_S=\sum_{j\notin S}w_j},
 \qquad
 \dim H_S=(s-1)^{|S|}.
 \tag{6.4}
\]

Consequently,

\[
 \ker O_w=H_{\{1,\ldots,r\}}=W_1\otimes\cdots\otimes W_r,
 \tag{6.5}
\]

with dimension `(s-1)^r`, and

\[
 c\sim c'
 \quad\Longleftrightarrow\quad
 c-c'\in W_1\otimes\cdots\otimes W_r.
 \tag{6.6}
\]

On the observable quotient,

\[
 \gamma(w)=\min_jw_j.
 \tag{6.7}
\]

The exact minimax quotient error at calibrated noise radius `epsilon` is

\[
 \boxed{
 R_\varepsilon^*=\frac{\varepsilon}{\sqrt{\min_jw_j}}.}
 \tag{6.8}
\]

Under the unit budget, the unique E-optimal allocation is

\[
 w_1=\cdots=w_r=\frac1r,
 \qquad \gamma_*=\frac1r.
 \tag{6.9}
\]

#### Proof

On `H_S`, `P_j` acts as zero if `j in S` and as the identity otherwise.
Summing the weighted projections proves (6.4).  The only zero eigenvalue has
`S` equal to the full axis set, proving (6.5)--(6.6).  The smallest positive
eigenvalue is obtained by omitting all but one axis from the complement, so it
is `min_j w_j`.  Equation (6.8) is Corollary (2.14).  Finally,
`min_j w_j<=1/r`, with equality only for uniform weights.  \(\square\)

### 6.1 Pure-monomial geometry

Let `e_alpha` be a pure prime monomial.  For distinct `alpha,beta`,

\[
 d_w(e_\alpha,e_\beta)^2
 =\frac2s
 \sum_{\{j:\alpha_{-j}\ne\beta_{-j}\}}w_j.
 \tag{6.10}
\]

If the exponent vectors differ only in coordinate `k`, this is

\[
 \frac2s(1-w_k).
 \tag{6.11}
\]

If they differ in two or more coordinates, it is exactly

\[
 \frac2s.
 \tag{6.12}
\]

Thus every pair of pure monomials is separated when `r>=2`, but the metric is
not Hamming distance: all differences involving at least two axes saturate at
the same value.

### 6.2 A matching mixture obstruction

Let

\[
 h=(e_0-e_1)^{\otimes r}.
 \tag{6.13}
\]

Every complementary marginal of `h` is zero.  If `u` is uniform on the
`s^r` exponent states, then

\[
 p_\pm=u\pm\frac{1}{2s^r}h
 \tag{6.14}
\]

are distinct nonnegative probability distributions with identical data under
every resonant protocol.  Their intrinsic separations are

\[
 \|p_+-p_-\|_2^2=\frac{2^r}{s^{2r}},
 \qquad
 \operatorname{TV}(p_+,p_-)=\frac{2^{r-1}}{s^r},
 \tag{6.15}
\]

while their observational distance is zero.

This is not in tension with pure-state injectivity.  Identifying every point
of a generating set does not imply injectivity on its convex hull.

### 6.3 Raw trace noise is a different geometry

Equation (5.4) gives

\[
 D_j=\sqrt s\,V_jR_j.
\]

Invertible preprocessing preserves exact kernels but not noise geometry.  For
raw homoscedastic samples, stability depends on `sigma_min(V_j)`, and no
prime-uniform positive lower bound exists.  As two prime logarithms approach
one another in ratio, Vandermonde nodes can approach collision.

Indeed, take `s=r=2`, let the resonant prime `p` tend to infinity, and choose
a prime `q` with `p<q<2p`, as supplied by Bertrand's theorem.  Then

\[
 \frac{\log q}{\log p}
 =1+\frac{\log(q/p)}{\log p}\longrightarrow1.
\]

The two nodes `1` and
`exp(-2 pi i log(q)/log(p))` coalesce.  The determinant, and hence the smallest
singular value, of the resulting two-by-two Vandermonde tends to zero.

For each fixed instance, the elementary determinant certificate

\[
 \sigma_{\min}(V_j)
 \geq
 \frac{|\det V_j|}{q^{q-1}},
 \qquad
 q=s^{r-1},
 \tag{6.16}
\]

is valid, though often pessimistic.  A future raw-noise protocol theorem must
carry this calibration cost rather than silently assigning the marginal
metric to the physical samples.

---

## 7. Certified `2^a 3^b 5^c` geometry

Take

\[
 (p_1,p_2,p_3)=(2,3,5),
 \qquad s=4,
 \qquad w_j=1/3.
\]

The exponent box contains 64 monomials.  The exact calibrated spectrum is

| eigenvalue | multiplicity | interaction order |
|---:|---:|---:|
| `1` | 1 | 0 |
| `2/3` | 9 | 1 |
| `1/3` | 27 | 2 |
| `0` | 27 | 3 |

Therefore:

- the pooled rank is 37;
- the common blind space has dimension 27;
- the observable simplex-tangent quotient has dimension 36;
- the exact positive floor is `1/3`;
- the exact squared minimax amplification is `3`;
- one-coordinate pure distances have square `1/3`;
- distances involving two or three coordinates have square `1/2`;
- the collision (6.14) has squared Euclidean separation `1/512` and total
  variation `1/16`.

The exact artifact payload digest is

```text
3fe7461250815719b4e80c9ad73dc04325f7fb13e8fa0dd83f0906c9505dcc56
```

For orientation only, binary64 singular-value diagnostics of the
sample-normalized raw 16-by-16 Vandermonde blocks `V_j/sqrt(16)` are:

| resonant prime | smallest singular value | condition number |
|---:|---:|---:|
| 2 | `0.2258542515` | `5.9637142251` |
| 3 | `0.2925664448` | `4.8338086890` |
| 5 | `0.1378129726` | `9.8580958306` |

These three descriptive values are not interval certificates and are not used
by the exact artifact.

---

## 8. From Arithmetic Sensing V recovery to fibre distance

The subspace nuisance theorem does not directly describe a positive integral
tail cone.  For that setting the correct objects are observation fibres.

Let `A a` be the observed response of an integer prefix and let `T_a` be its
allowed tail-response set.  Define

\[
 \mathcal F_a=Aa+\mathcal T_a.
 \tag{8.1}
\]

Suppose a linear reconstruction map `R` satisfies

\[
 RA=I,
 \qquad
 \sup_{t\in\mathcal T_a}\|Rt\|_\infty\leq B<\frac12
 \tag{8.2}
\]

for every admissible prefix, and let

\[
 \kappa=\|R\|_{Y\to\ell^\infty}.
\]

### Theorem 8.1 — arithmetic-fibre separation

Distinct integer-prefix fibres satisfy

\[
 \boxed{
 \operatorname{dist}(\mathcal F_a,\mathcal F_b)
 \geq\frac{1-2B}{\kappa}.}
 \tag{8.3}
\]

If the fibres are compact, nearest-fibre decoding is therefore uniformly
correct for noise below

\[
 \frac{1/2-B}{\kappa}.
 \tag{8.4}
\]

If the infimum defining the exact closest-fibre distance `delta_fib` is
attained, the midpoint of a closest pair proves that `delta_fib/2` is the
matching impossibility threshold.

#### Proof

For `y=Aa+t` and `y'=Ab+t'`, integrality gives
`||a-b||_infty>=1`.  Hence

\[
 \kappa\|y-y'\|_Y
 \geq\|R(y-y')\|_\infty
 \geq1-\|Rt\|_\infty-\|Rt'\|_\infty
 \geq1-2B.
\]

Take the infimum.  The decoding and midpoint statements follow from metric
balls.  \(\square\)

### 8.1 Exact degree-fourteen bridge certificate

The formal Arithmetic Sensing V multiscale artifact has

\[
 B=
 \frac{
 7203006588741627759985152795444110550802077110215782157377355393577524691875
 }{
 14463072405499051244996447951833472306623699230360514791222607147412978925568
 }
 =0.4980274167750795\ldots
 \tag{8.5}
\]

and the certified exact-rational upper bound

\[
 q=
 \frac{257168756981514768514508306559006707}
 {340282366920938463463374607431768211456}
 =0.0007557510525994\ldots
 \tag{8.6}
\]

on the maximum Gram row defect.

Here `Y` is the weighted observation Hilbert space declared by the AS-V
measure.  Let `C:C^50->Y` be its normalized phase-synthesis map, so

\[
 G=C^*C,
 \qquad D=\operatorname{diag}(1^2,2^2,\ldots,50^2),
 \qquad A=CD^{-1}.
\]

The prefix reconstruction map is

\[
 R=DG^{-1}C^*,
\]

and therefore `RA=I`.  The source artifact's coefficient endpoint (8.5) is
precisely the uniform statement `sup_t ||Rt||_infinity<=B` over its admissible
tails.  The squared norm of row `n` of `R` is

\[
 n^4(G^{-1})_{nn}.
\]

Hermitian Gershgorin gives `lambda_min(G)>=1-q`, so

\[
 \|R\|_{Y\to\ell^\infty}
 =\max_n n^2\sqrt{(G^{-1})_{nn}}
 \leq\frac{2500}{\sqrt{1-q}}.
 \tag{8.6a}
\]

Combining this with (8.3) gives the exact squared lower bound

\[
 \delta_{\rm fib}^2
 \geq\frac{(1-2B)^2(1-q)}{2500^2},
 \tag{8.7}
\]

whose decimal square root is

\[
 \delta_{\rm fib}\geq
 1.5774701544883733\times10^{-6}.
 \tag{8.8}
\]

The certified robust radius is therefore

\[
 \boxed{
 \rho_{\rm robust}\geq
 7.8873507724418666\times10^{-7}.}
\tag{8.9}
\]

The declared `d_14` tail set is common and compact: each coefficient lies in a
finite set, their product is compact, and absolute uniform convergence at
`sigma=2` maps that product continuously into the finite observation space.
The prefixes are also coefficientwise bounded by `d_14` through 50, so only
finitely many prefix fibres occur.  Consequently the global closest-fibre
distance is attained and the midpoint obstruction in Theorem 8.1 applies.

Two zero-tail prefixes differing by one unit at `n=50` have observation
distance `1/2500`, because the normalized 50th column of `C` has norm one and
the corresponding column of `A=CD^{-1}` is scaled by `50^-2`.  Thus

\[
 \delta_{\rm fib}\leq4\times10^{-4},
 \qquad
 \rho_{\rm robust}\leq2\times10^{-4}.
 \tag{8.10}
\]

The current certified radius bracket spans a factor of about 254.  This is not
a defect hidden by the theorem: it is an explicit closest-fibre problem for
future computation and analysis.

The bridge artifact pins both the source file digest

```text
ad03df9d6325512074e6940602c1c888c81abd057a5856d6212f93dc8e780517
```

and the original formal certificate digest

```text
89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b
```

Its own payload digest is

```text
bf2e02334d9e2f68942d7ffba394d213c514ddf30c4db0ca277a3263adc8cd58
```

---

## 9. The object-level boundary

Perfect coefficient observability is not perfect arithmetic-object
observability.  The Perlis examples already used in Arithmetic Sensing II and
IV give nonisomorphic number fields with identical Dedekind zeta functions.
Their complete coefficient streams and all zeta-only harmonic data coincide.
They therefore have distance zero under every protocol that factors only
through Dedekind zeta.

Arithmetic Sensing IV also gives the complementary positive fact: for the
fields generated by `x^8-33` and `x^8-528`, the local `Q_2` component-degree
features

\[
 (1,1,2,4)
 \qquad\text{and}\qquad
 (2,2,2,2)
\]

separate the zeta collision.  This is an example of protocol enrichment
shrinking the object-level equivalence relation.  It remains an oracle-level
local channel until an acquisition and noise model is supplied.

The correct conclusion is layered:

- harmonic design can remove acquisition aliases;
- arithmetic constraints can turn continuous rank loss into exact lattice
  identifiability;
- neither can separate objects collapsed by the chosen arithmetic feature;
- a new local channel can refine that earlier quotient.

---

## 10. Validity ledger

### Proved in this manuscript

1. Nuisance-projected exact equivalence and local-query factorization.
2. The exact adversarial minimax identity `kappa epsilon`.
3. The three-way lattice observability theorem.
4. Quantitative bounded-height crowding under rank deficiency.
5. Almost-everywhere one-trace integer identification and its zero uniform
   radius for `N>=4`.
6. The explicit exceptional `2/3` coefficient collision.
7. Total one-sample blindness under an unrestricted real tail.
8. Exact recovery of prime-valuation complementary marginals from resonant
   harmonic grids.
9. The complete ANOVA spectrum, kernel, sharp quotient floor, and E-optimal
   weights for calibrated marginal protocols.
10. Pure-monomial distances and an exact nonnegative mixture collision.
11. The arithmetic-fibre separation theorem.
12. The exact-rational Arithmetic Sensing V radius bracket derived from its
    existing formal artifact.

### Machine-verified here

- the 64-dimensional rational prime-box Gram and its declared digest;
- projector identities, spectrum multiplicities, rank and kernel dimensions;
- the exact nonnegative probability collision and its intrinsic distances;
- the two exact bridge-artifact digests;
- reconstruction of the AS-V radius bracket from pinned exact fractions;
- rejection of altered payloads even when an attacker recomputes the outer
  JSON digest.

The bridge checker verifies provenance and the new rational consequence.  It
does not independently replay the source artifact's expensive Arb theorem.

### Descriptive computation only

- the three binary64 raw-Vandermonde condition numbers in Section 7.

### Not established

- a literature-priority claim for the abstract ingredients;
- a prime-uniform raw-sample stability constant;
- clock-jitter robustness for resonant time grids;
- a matching Diophantine lower law for `delta_H(t)`;
- the exact closest-fibre distance in the degree-fourteen model;
- a positive coefficient-recovery lower bound restricted to an actual family
  of Dedekind zeta functions;
- identification of arbitrary number fields from zeta data;
- any consequence for zeta zeros, the Riemann hypothesis, or fundamental
  physics.

---

## 11. Relation to prior work and novelty boundary

The abstract quotient pseudometric and Gaussian discrimination interpretation
were established in `OPERATIONAL_INFORMATION_GEOMETRY_I.md`.  Pooled kernels,
axis-blind interaction obstructions, and finite mixture stability were
developed in `OPERATIONAL_INFORMATION_GEOMETRY_II.md`.  The later OIG work
supplies generalized source-metric spectra, compactness obstructions,
proof-producing interval floors, and continuum-to-finite transfer.  Those
results are prerequisites and are not renamed as new theorems here.

The exact least-squares identity, leverage constants, tail/noise decomposition,
and harmonic `T/N` resolution obstruction originate in
`ARITHMETIC_SENSING.md`.  The deterministic two-ball lower bound and Perlis
collision are in `ARITHMETIC_SENSING_II.md`; the local feature separating a
zeta collision is in `ARITHMETIC_SENSING_IV.md`; and the formal
degree-fourteen endpoint consumed in Section 8 is in the Arithmetic Sensing V
manuscripts and certificates.

Operator factorization through a quotient, Moore--Penrose recovery, discrete
subgroups of Euclidean space, pigeonhole/geometry-of-numbers arguments,
Vandermonde inversion, and tensor ANOVA decompositions are standard
mathematics.  Perlis arithmetic equivalence and the local-algebra facts are
classical ingredients inherited through the cited Arithmetic Sensing work.

The contribution asserted within this programme is the synthesis:

1. a local-query and nuisance formulation whose constant is stated as an
   exact minimax identity;
2. the lattice trichotomy applied to show generic exact but uniformly unstable
   one-trace Dirichlet identification;
3. the prime-resonant realization of complementary valuation marginals and
   its complete calibrated quotient geometry; and
4. the exact-rational conversion of the AS-V recovery margin into a certified
   arithmetic-fibre distance bracket.

No external priority claim is made for this combination before literature
review and independent mathematical scrutiny.

---

## 12. Reproduction

The exact prime-box certificate uses only the Python standard library:

```bash
python arithmetic_observability_prime_box.py \
  --verify arithmetic_observability_prime_box_certificate.json
```

Optional descriptive raw-Vandermonde diagnostics require NumPy:

```bash
python arithmetic_observability_prime_box.py --raw-diagnostics
```

The AS-V bridge checker consumes the existing formal artifact:

```bash
python arithmetic_observability_asv_bridge.py \
  --verify arithmetic_observability_asv_bridge_certificate.json
```

Run all new adversarial tests with:

```bash
python -m unittest -v \
  test_arithmetic_observability_prime_box.py \
  test_arithmetic_observability_asv_bridge.py
```

The bridge checker is intentionally cheap.  It does not replace the expensive
Arb verification of the source Arithmetic Sensing V artifact; it pins that
artifact and independently verifies the new exact-rational consequence.

---

## 13. Research questions now exposed

The work will proceed by whichever of these questions yields the strongest
theorem or counterexample, rather than by a fixed stage order.

1. **Closest arithmetic fibres.**  Reduce the factor-254 gap in (8.9)--(8.10)
   through a certified shortest-vector or convex-fibre search.
2. **Metric Diophantine observability.**  Determine almost-everywhere lower
   laws for `delta_H(t)` and whether the pigeonhole exponent is sharp.
3. **Constrained tails.**  Replace unrestricted nuisance subspaces by positive
   integral divisor-bounded cones and characterize exactly when they restore
   a positive separation.
4. **Breaking the top interaction.**  Determine the minimum additional
   harmonic protocols needed to observe
   `W_1 tensor ... tensor W_r`, with a sharp raw-noise cost.
5. **Raw resonant design.**  Optimize protocol weights after including the
   actual Vandermonde covariance rather than the calibrated marginal metric.
6. **Actual arithmetic families.**  Compute distinguishability geometry for
   quadratic and higher number-field coefficient families, not only the full
   integer coefficient lattice.
7. **Object-level local queries.**  Give acquisition and stability theorems
   for ramification-aware channels that split known zeta collisions.
8. **Infinite-dimensional boundary.**  Combine the OIG compactness obstruction
   with arithmetic integrality to decide when an infinite coefficient lattice
   remains discrete in an incomplete harmonic topology.

The central lesson is already firm: arithmetic observability is not a binary
property.  Exact equality, stable recovery, and object identity live on
different quotients.  The geometry becomes informative precisely when those
quotients and their noise scales are declared rather than silently merged.
