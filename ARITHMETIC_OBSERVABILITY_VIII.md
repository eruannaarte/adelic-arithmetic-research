# Arithmetic Observability VIII

## Common-nuisance geometry and the exact tail-relaxation dual

### Centered coefficient boxes, sharper arithmetic radii, and a certified route to the closest fibres

- **Research lead, theorem synthesis, computation design, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** research manuscript with reproducible finite certificate; not peer reviewed
- **Date:** 15 August 2026
- **Parent manuscripts:** `ARITHMETIC_OBSERVABILITY_I.md`,
  `ARITHMETIC_OBSERVABILITY_VII.md`, and
  `ARITHMETIC_SENSING_V_MULTISCALE.md`

## Abstract

Arithmetic Observability VII bounded two arbitrary tail responses separately.
That is the correct general argument when nuisance sets may be unrelated, but
it leaves information unused when every source tail lies in one common
coefficient box.  The geometry of a common box is controlled by its width,
not twice its radius about the origin.  If

\[
 \mathcal T
 =\left\{\sum_{k>N}b_kv_k:0\le b_k\le d_k\right\},
\]

then

\[
 \mathcal T=t_0+\frac12\mathcal Z,
 \qquad
 \mathcal T-\mathcal T=\mathcal Z,
 \qquad
 \mathcal Z
 =\left\{\sum_{k>N}x_kv_k:|x_k|\le d_k\right\}.
\]

Consequently, a reconstruction row whose full signed width is at most `B_n`
has centered single-tail bias at most `B_n/2`, while a difference of two tails
has bias at most `B_n`, not `2B_n`.  This yields the constructive centered
decoding threshold

\[
 \varepsilon_n<\frac{1-B_n}{2\kappa_n}
\]

for unit-spaced labels.  The earlier uncentered rounding threshold
`(1/2-B_n)/kappa_n` remains correct if the common center is not modeled.

For the pinned degree-fourteen Arithmetic Sensing V experiment, the existing
finite and remote absolute-sum certificates already control the whole signed
difference box.  Combining this fact with the row-local Schur bound gives the
four-anchor sufficient radius

\[
 \boxed{0.0198587033410859808050\ldots}
\]

for `I={1,2,3,5}`.  This leaves only a `0.71151%` ratio to the elementary
`0.02` obstruction.  A ten-mode tail with integral generalized-divisor
endpoint coefficients gives the strict certified upper radius

\[
 0.0199999999977821582051\ldots<0.02.
\]

For all fifty prefix coefficients, an exact rational scan of the localized
bounds has the unique bottleneck `n=50` and improves the published sufficient
radius from about `7.887e-7` to

\[
 \boxed{0.0001003945163298032675\ldots}.
\]

The resulting all-coordinate bracket has ratio less than `1.993`, rather
than about `254`.

The common continuous relaxation also admits an exact convex formulation.
Its tail-difference body is a compact countably generated zonoid in the
finite realified data space.  For any prefix difference `h`, its exact fibre
distance is both the attained primal

\[
 \min_{|x_k|\le d_k}
 \left\|Ah-\sum_{k>N}x_kv_k\right\|
\]

and the attained support-function dual

\[
 \max_{\|u\|\le1}
 \left(
 (u,Ah)_{\mathbb R}
 -\sum_{k>N}d_k|(u,v_k)_{\mathbb R}|
 \right).
\]

An unconstrained squared-distance dual has an exact nonnegative
primal-dual gap identity.  It supplies falsifiable optimality certificates
and exposes the remaining difficulty: more than `99.49%` of the present
pair-specific support upper bound comes from the conservative post-million
remote estimate.  The manuscript proves a finite reduction of the global
four-anchor prefix search but does **not** claim that the adjacent `n=5`
pair is the exact global closest pair.  For integral tails, the same width
bounds remain valid, while the zonoid problem is explicitly only a convex
relaxation and its fractional upper witnesses need not be arithmetically
realizable.

---

## 1. Why a common nuisance box changes the answer

Suppose an observation has the form

\[
 y=Aa+t+\eta,
 \qquad t\in\mathcal T_a,
 \qquad \|\eta\|\le\varepsilon.
 \tag{1.1}
\]

A bound `|ell_n(t)|<=B_n` measured from the origin implies
`|ell_n(t-t')|<=2B_n` for unrelated nuisance sets.  That was the premise of
the general theorem in Arithmetic Observability VII.  It cannot be improved
without more structure.

Arithmetic coefficient envelopes do have more structure.  Every allowed
tail is coefficientwise contained in the same interval box.  The relevant
quantity for separating two fibres is then the diameter of that box in the
observation direction.  An interval `[0,d]` has radius `d/2` about its
midpoint and difference interval `[-d,d]`; it does not produce `[-2d,2d]`.
The infinite-dimensional coefficient statement is exactly the same.

This distinction separates two decoders.

1. **Uncentered coefficient rounding.**  Apply a reconstruction row directly
   to `y` and round about zero.  Its worst single-tail bias is measured from
   the origin.  The Arithmetic Sensing V condition `B_n<1/2` belongs here.
2. **Common-nuisance or centered decoding.**  Model the shared nuisance box,
   or subtract its known midpoint before rounding.  The single-tail bias is
   half the full width.  Pairwise fibre separation uses that width once.

The second procedure is not a post hoc change of norm.  It uses known model
information which the first procedure discards.

### 1.1 Continuous and integral tails are different models

This paper keeps two tail classes distinct.

- In the **continuous relaxation**, every coefficient varies independently
  in `[0,d_k]`.  Its centered difference body is convex, and the exact
  support-function dual below applies.
- In the **integral model**, every coefficient belongs to
  `{0,1,...,d_k}`.  The same common-width lower bounds apply because the
  difference coefficients still lie in `[-d_k,d_k]`, but the exact tail
  difference set is nonconvex.  The continuous zonoid is its closed convex
  hull (in the present finite-dimensional data space that hull is compact).

Thus a lower bound proved for the continuous relaxation automatically holds
for the smaller integral model.  A fractional continuous-tail collision or
upper witness does not automatically transfer in the other direction.

---

## 2. Compact centered boxes and their difference zonoids

Let `H` be a finite-dimensional real Hilbert space.  A complex data space is
always read as its realification, with

\[
 (u,v)_{\mathbb R}=\operatorname{Re}\langle u,v\rangle
 \tag{2.1}
\]

and unchanged norm.  Let `v_k in H`, let `d_k>=0`, and assume

\[
 \sum_{k>N}d_k\|v_k\|<\infty.
 \tag{2.2}
\]

Define

\[
 \begin{aligned}
 \mathcal T
 &=\left\{\sum_{k>N}b_kv_k:0\le b_k\le d_k\right\},\\
 t_0&=\frac12\sum_{k>N}d_kv_k,\\
 \mathcal Z
 &=\left\{\sum_{k>N}x_kv_k:|x_k|\le d_k\right\}.
 \end{aligned}
 \tag{2.3}
\]

The sums converge uniformly over their coefficient products by (2.2).

### Theorem 2.1 — common-box centering

The sets `T` and `Z` are compact and convex, `Z` is centrally symmetric, and

\[
 \boxed{
 \mathcal T=t_0+\frac12\mathcal Z,
 \qquad
 \mathcal T-\mathcal T=\mathcal Z.}
 \tag{2.4}
\]

Moreover, the finite partial sums

\[
 \mathcal Z_M
 =\sum_{N<k\le M}[-d_kv_k,d_kv_k]
 \tag{2.5}
\]

are zonotopes and converge to `Z` in Hausdorff distance.  Accordingly, `Z`
is a compact zonoid, or equivalently here a countably generated convergent
infinite Minkowski sum.  We reserve the word *zonotope* for the finite
partials (2.5).

#### Proof

The product `prod_[k>N] [-d_k,d_k]` is compact in its countable product
topology.  Its finite synthesis maps are continuous, and (2.2) makes them
converge uniformly.  Their limit is therefore continuous, so its image `Z`
is compact.  Convexity and central symmetry follow coordinatewise.  The same
argument applies to `T`.

For `|x_k|<=d_k`, the coordinate assignments

\[
 b_k=\frac{d_k+x_k}{2},
 \qquad
 b'_k=\frac{d_k-x_k}{2}
 \tag{2.6}
\]

belong to `[0,d_k]` and satisfy `b_k-b'_k=x_k`.  Conversely, every difference
of two coefficients in `[0,d_k]` lies in `[-d_k,d_k]`.  This proves both
identities in (2.4).  Finally,

\[
 d_H(\mathcal Z_M,\mathcal Z)
 \le\sum_{k>M}d_k\|v_k\|\longrightarrow0,
 \tag{2.7}
\]

which proves the zonoid statement.  \(\square\)

If every `d_k` is an integer, let `Z_Z` denote the same synthesis with
integer coefficients `x_k in {-d_k,...,d_k}`.  Then

\[
 \mathcal Z=\overline{\operatorname{conv}}(\mathcal Z_{\mathbb Z}).
 \tag{2.8a}
\]

Indeed, every finite interval box is the convex hull of its integer lattice
points, so every truncation of a point of `Z` lies in
`conv(Z_Z)` after setting all later coefficients to zero.  Uniform
convergence passes to the limit.  The reverse containment follows from
convexity of `Z`.  Moreover `Z_Z` is compact by the same product argument,
and in finite-dimensional `H` its convex hull is compact, so the closure bar
in (2.8a) is in fact redundant.  We retain it when describing the relation
because it is the topology-safe formulation.

### Theorem 2.2 — exact support function

For every `u in H`,

\[
 \boxed{
 h_{\mathcal Z}(u)
 :=\sup_{z\in\mathcal Z}(u,z)_{\mathbb R}
 =\sum_{k>N}d_k|(u,v_k)_{\mathbb R}|.}
 \tag{2.8}
\]

The supremum is attained by taking

\[
 x_k=d_k\operatorname{sign}(u,v_k)_{\mathbb R}
 \tag{2.9}
\]

whenever the displayed inner product is nonzero, with arbitrary admissible
`x_k` at a zero.

#### Proof

The scalar series is absolutely convergent because

\[
 \sum_{k>N}d_k|(u,v_k)_{\mathbb R}|
 \le\|u\|\sum_{k>N}d_k\|v_k\|.
 \tag{2.10}
\]

Every admissible coefficient sequence is bounded above termwise by the
right-hand side of (2.8), and the sign choice (2.9) attains every term
simultaneously.  \(\square\)

For real coefficient intervals, the real pairing in (2.8) is exact.  Replacing
it by the complex modulus is a valid upper bound but can be strictly
conservative.

---

## 3. Width-aware reconstruction and centered decoding

Let `A:X->H` be a linear prefix observation on a coordinate model and suppose
bounded linear functionals `ell_n:H->R` satisfy

\[
 \ell_n(Aa)=a_n.
 \tag{3.1}
\]

Write

\[
 \kappa_n=\|\ell_n\|,
 \qquad
 S_n=\sup_{z\in\mathcal Z}|\ell_n(z)|.
 \tag{3.2}
\]

Because `Z` is symmetric, `S_n` is its support in either Riesz direction.
Allow prefix-dependent tail sets `T_a`, but assume every one lies in the same
ambient box `T` of Section 2.  Define fibres

\[
 \mathcal F_a=Aa+\mathcal T_a.
 \tag{3.3}
\]

### Theorem 3.1 — common-width fibre separation

For every two prefixes `a,b`,

\[
 \boxed{
 \operatorname{dist}(\mathcal F_a,\mathcal F_b)
 \ge
 \max_n\frac{(|a_n-b_n|-S_n)_+}{\kappa_n}.}
 \tag{3.4}
\]

#### Proof

For `t in T_a` and `t' in T_b`, Theorem 2.1 gives `t-t' in Z`.  Hence

\[
 \begin{aligned}
 \kappa_n\|A(a-b)+t-t'\|
 &\ge|\ell_n(A(a-b)+t-t')|\\
 &\ge|a_n-b_n|-S_n.
 \end{aligned}
 \tag{3.5}
\]

Take the positive part, maximize over the desired coordinates, and infimize
over both tails.  \(\square\)

This theorem uses only containment in one ambient coefficient box.  The
individual tail sets may still depend on the prefix and may encode additional
arithmetic coupling.

### Corollary 3.2 — centered separated-label decoder

Suppose coordinate `n` has label spacing `Delta_n>S_n`.  Subtract the common
center `t_0` and apply `ell_n`.  Nearest-label decoding is correct under data
noise `||eta||<=epsilon` whenever

\[
 \boxed{
 \varepsilon
 <\min_n\frac{\Delta_n-S_n}{2\kappa_n}.}
 \tag{3.6}
\]

For unit-spaced labels this is `(1-S_n)/(2 kappa_n)`.

#### Proof

By (2.4), every `t in T` can be written `t=t_0+z/2` with `z in Z`.  Thus

\[
 |\ell_n(t-t_0)|\le S_n/2.
 \tag{3.7}
\]

For an observation `y=Aa+t+eta`,

\[
 |\ell_n(y-t_0)-a_n|
 \le S_n/2+\kappa_n\varepsilon<\Delta_n/2.
 \tag{3.8}
\]

The true label is therefore uniquely nearest.  \(\square\)

The same radius follows from (3.4) and nearest-fibre decoding.  If a closest
pair is attained, its midpoint gives the matching impossibility obstruction
at half the exact separation.

Centered rounding assumes that the common midpoint is known in the data
coordinates.  In a numerical implementation, any enclosure error in
evaluating or subtracting `t_0` must be charged to the observation-noise
budget.  The pairwise fibre-separation theorem (3.4) does not require an
algorithmic evaluation of the midpoint.

### 3.1 Why the earlier theorem was not false

If all that is known is

\[
 \sup_{t\in\mathcal T_a}|\ell_n(t)|\le B_n
 \tag{3.9}
\]

for possibly unrelated sets, then their difference can have row magnitude
`2B_n`.  The Arithmetic Observability VII bound

\[
 \frac{(|a_n-b_n|-2B_n)_+}{\kappa_n}
 \tag{3.10}
\]

remains the correct generic conclusion.  The new result is stronger because
the declared arithmetic model supplies a common coefficientwise center and
width.  It is not obtained by algebraically replacing a valid generic
constant.

---

## 4. Exact continuous-tail primal and dual

From now on, take the full continuous box `T` rather than arbitrary subsets.
Its fibres are `F_a=Aa+T`.  The common translation `t_0` cancels between two
fibres, and Theorem 2.1 gives

\[
 \operatorname{dist}(\mathcal F_a,\mathcal F_b)
 =\operatorname{dist}(A(a-b),\mathcal Z).
 \tag{4.1}
\]

For a prefix difference `h`, write

\[
 d(h)=\operatorname{dist}(Ah,\mathcal Z).
 \tag{4.2}
\]

### Theorem 4.1 — exact fixed-prefix norm dual

The continuous-relaxation fibre distance has the attained primal-dual
identity

\[
 \boxed{
 \begin{aligned}
 d(h)
 &=\min_{|x_k|\le d_k}
 \left\|Ah-\sum_{k>N}x_kv_k\right\|\\
 &=\max_{\|u\|\le1}
 \left(
 (u,Ah)_{\mathbb R}
 -\sum_{k>N}d_k|(u,v_k)_{\mathbb R}|
 \right).
 \end{aligned}}
 \tag{4.3}
\]

In particular, exact zero-noise collision for this pair is equivalent to

\[
 Ah\in\mathcal Z,
 \tag{4.4}
\]

or, equivalently, to every dual inequality

\[
 (u,Ah)_{\mathbb R}\le h_{\mathcal Z}(u)
 \qquad(u\in H).
 \tag{4.5}
\]

#### Proof

Compactness of `Z` gives a unique metric projection `z*=P_Z(Ah)`.  Put
`r*=Ah-z*` and `d=||r*||`.  Projection normality says

\[
 (r^*,z-z^*)_{\mathbb R}\le0
 \qquad(z\in\mathcal Z),
 \tag{4.6}
\]

so `h_Z(r*)=(r*,z*)_R`.  For every `||u||<=1` and `z in Z`,

\[
 (u,Ah)_{\mathbb R}-h_{\mathcal Z}(u)
 \le(u,Ah-z)_{\mathbb R}
 \le\|Ah-z\|.
 \tag{4.7}
\]

This is weak duality.  If `d>0`, choose `u*=r*/d`; equations (4.6)--(4.7)
become equalities.  If `d=0`, choose `u=0`.  The unit ball is compact and the
dual objective is continuous, so the dual maximum is attained independently
as well.  The support theorem turns it into the displayed series.  The
collision equivalences follow from `d(h)=0` and the separating-hyperplane
description of a closed convex body.  \(\square\)

If `d(h)>0`, the norm-dual maximizer is unique: equality in Cauchy--Schwarz
forces `u` to be the unit residual `r*/d`.

### Theorem 4.2 — squared dual and exact gap identity

For `v=Ah`, define

\[
 \begin{aligned}
 P(z)&=\frac12\|v-z\|^2,\\
 D(u)&=(u,v)_{\mathbb R}-h_{\mathcal Z}(u)-\frac12\|u\|^2.
 \end{aligned}
 \tag{4.8}
\]

Then

\[
 \boxed{
 \frac12d(h)^2=\max_{u\in H}D(u),}
 \tag{4.9}
\]

and for every primal-feasible `z in Z` and every `u in H`,

\[
 \boxed{
 P(z)-D(u)
 =\frac12\|v-z-u\|^2
 +h_{\mathcal Z}(u)-(u,z)_{\mathbb R}\ge0.}
 \tag{4.10}
\]

The unique dual maximizer is

\[
 u^*=v-P_{\mathcal Z}v.
 \tag{4.11}
\]

#### Proof

Equation (4.10) follows by expanding the square.  Both terms on its right are
nonnegative: the second by the definition of a support function.  At
`z*=P_Zv` and `u*=v-z*`, the first term vanishes, while projection normality
gives `h_Z(u*)=(u*,z*)_R`.  Hence the gap is zero and (4.9) follows.  Strict
concavity of the negative norm-square term gives dual uniqueness.  \(\square\)

### Corollary 4.3 — infinite-series KKT signs

If

\[
 z^*=\sum_{k>N}x_k^*v_k
 \tag{4.12}
\]

is any coefficient representation of the projection and `u*=Ah-z*`, then

\[
 x_k^*=d_k\operatorname{sign}(u^*,v_k)_{\mathbb R}
 \tag{4.13}
\]

at every nonzero pairing.  At a zero pairing any coefficient in the interval
is permitted.

Indeed, support equality makes the convergent sum

\[
 \sum_{k>N}
 \left(d_k|(u^*,v_k)_{\mathbb R}|
 -x_k^*(u^*,v_k)_{\mathbb R}\right)
 \tag{4.14}
\]

equal zero.  Every term is nonnegative, so each term vanishes.  The projection
point and residual are unique; its coefficient representation need not be.

### 4.1 Certified finite reductions

Let `Z_M` be (2.5) and

\[
 R_M=\sum_{k>M}d_k\|v_k\|.
 \tag{4.15}
\]

Then

\[
 \boxed{
 \max(0,\operatorname{dist}(v,\mathcal Z_M)-R_M)
 \le\operatorname{dist}(v,\mathcal Z)
 \le\operatorname{dist}(v,\mathcal Z_M).}
 \tag{4.16}
\]

The norm remainder can be too coarse for arithmetic work, but a
direction-specific remote support certificate is sharper.  For any unit `u`
and certified bound

\[
 U_M(u)\ge\sum_{k>M}d_k|(u,v_k)_{\mathbb R}|,
 \tag{4.17}
\]

Theorem 4.1 gives

\[
 d(h)\ge
 (u,Ah)_{\mathbb R}
 -\sum_{N<k\le M}d_k|(u,v_k)_{\mathbb R}|
 -U_M(u).
 \tag{4.18}
\]

A finite feasible coefficient sequence gives the complementary upper bound.
Equations (4.10) and (4.18) specify exactly what a formal closest-fibre
certificate must check.

For integral tails, (4.3)--(4.14) compute the distance to the closed convex hull of
the true tail difference set.  They remain rigorous lower bounds on the
nonconvex integral-tail distance, but equality and fractional primal
witnesses belong only to the continuous model.

---

## 5. The pinned Arithmetic Sensing V specialization

Use exactly the positive multiscale measure certified in

```text
certificates/arithmetic_sensing_v_multiscale_end_to_end.json
```

with degree `14`, cutoff `N=50`, exponent `sigma=2`, and 8,900 distinct
centered readings.  Put

\[
 H=L^2(\mu;\mathbb C)_{\mathbb R},
 \qquad c_n(t)=n^{-it},
 \qquad \|c_n\|=1,
 \tag{5.1}
\]

where the subscript denotes realification.  Let `C` synthesize
`c_1,...,c_50`, and set

\[
 \begin{aligned}
 D&=\operatorname{diag}(1^2,2^2,\ldots,50^2),\\
 G&=C^*C=I+E,\\
 A&=CD^{-1},\\
 R&=DG^{-1}C^*.
 \end{aligned}
 \tag{5.2}
\]

Then `RA=I`.  Write

\[
 q_n\ge\sum_{j\ne n}|E_{nj}|,
 \qquad q=\max_nq_n<1.
 \tag{5.3}
\]

For `k>50`, take

\[
 v_k=k^{-2}c_k,
 \qquad d_k=d_{14}(k).
 \tag{5.4}
\]

The summability premise is exact:

\[
 \sum_{k\ge1}\frac{d_{14}(k)}{k^2}=\zeta(2)^{14}<\infty.
 \tag{5.5}
\]

The common center is therefore the explicit Dirichlet-series tail

\[
 \boxed{
 t_0(t)=\frac12\left(
 \zeta(2+it)^{14}
 -\sum_{k\le50}d_{14}(k)k^{-2-it}
 \right).}
 \tag{5.6}
\]

It is model data, not an unknown source-dependent quantity.

### 5.1 The existing tail certificate is already a width certificate

For a signed difference `z in Z`, let

\[
 e=C^*z.
 \tag{5.7}
\]

The finite Arithmetic Sensing V computation sums generalized-divisor weights
times absolute signed responses.  Its remote certificates are likewise
absolute majorants.  Thus the exact source values `tau_n` satisfy

\[
 |e_n|\le\tau_n
 \tag{5.8}
\]

for the whole signed interval `|x_k|<=d_14(k)`.  Nothing in this step requires
`x_k>=0`.  Put `tau=max tau_n`.  The same localized Neumann calculation as in
Arithmetic Observability VII gives

\[
 \boxed{
 S_n\le B_n
 :=n^2\left(\tau_n+q_n\frac{\tau}{1-q}\right).}
 \tag{5.9}
\]

There is no additional factor of two.  Equivalently, every centered
individual tail has reconstruction bias at most `B_n/2`.

The row-local Schur estimate remains

\[
 \kappa_n^2
 \le\bar\kappa_n^2
 :=n^4\frac{1-q}{1-q-q_n^2}.
 \tag{5.10}
\]

Combining (3.6), (5.9), and (5.10) gives the exact-rational sufficient square

\[
 \boxed{
 \rho_{n,\mathrm{box}}^2
 =(1-B_n)^2
 \frac{1-q-q_n^2}{4n^4(1-q)}.}
 \tag{5.11}
\]

Every quantity on the right is a rational reconstructed from the pinned
source certificate.

---

## 6. The refined four-anchor theorem

Take

\[
 I=\{1,2,3,5\}.
 \tag{6.1}
\]

The coordinate `a_1=1` is fixed in the normalized source class, but retaining
it records normalization and gives the same four-anchor interface as
Arithmetic Observability VII.  Exact substitution in (5.11) gives:

| `n` | certified width `B_n` | centered sufficient radius | certified unit fibre gap |
|---:|---:|---:|---:|
| 1 | `0.0005413328049489775` | `0.49972933359751925625` | `0.99945866719503851250` |
| 2 | `0.0015462579530286658` | `0.12480671775586836143` | `0.24961343551173672287` |
| 3 | `0.0030243219258030983` | `0.05538753767078675751` | `0.11077507534157351503` |
| 5 | `0.0070648329456505926` | **`0.01985870334108598081`** | **`0.03971740668217196161`** |

These are certified lower bounds, not asserted exact distances.  The `B_n`
are signed-width upper bounds and need not be attained.

### Theorem 6.1 — centered four-anchor observability

Under the common degree-fourteen coefficient envelope, unit-spaced labels at
`I={1,2,3,5}` are exactly identifiable.  Centered rounding, or nearest-fibre
decoding, is uniformly correct whenever

\[
 \boxed{
 \varepsilon
 <\rho_I
 :=\min_{n\in I}\rho_{n,\mathrm{box}}
 =\rho_{5,\mathrm{box}}
 =0.0198587033410859808050\ldots.}
 \tag{6.2}
\]

Consequently, the distance between every two query-distinct fibres is at
least

\[
 2\rho_I
 =0.0397174066821719616101\ldots.
 \tag{6.3}
\]

The companion artifact verifies by exact rational comparison that `n=5` is
the unique bottleneck among the four rows.

### 6.1 A stronger dual bound for the adjacent `n=5` pair

Let

\[
 v=Ae_5=\frac1{25}c_5.
 \tag{6.4}
\]

The unit dual direction `u=c_5` has

\[
 h_{\mathcal Z}(c_5)
 =\sum_{k>50}\frac{d_{14}(k)}{k^2}
 \left|\left(c_5,c_k\right)_{\mathbb R}\right|
 \le\tau_5.
 \tag{6.5}
\]

Therefore Theorem 4.1 gives the exact-rational certified pair bound

\[
 \begin{aligned}
 d(e_5)
 &\ge\frac1{25}-\tau_5\\
 &=
 \frac{
 168939165155824452248315566369552865403
 }{
 4253529586511730793292182592897102643200
 }\\
 &=0.0397174068546610156648\ldots.
 \end{aligned}
 \tag{6.6}
\]

Thus the adjacent-pair radius alone is at least

\[
 0.0198587034273305078324\ldots.
 \tag{6.7}
\]

This is slightly stronger than (6.2), but it is pair-specific.  The direction
`c_5` does not annihilate arbitrary nonquery prefix differences, so (6.7)
cannot replace the global four-anchor lower bound.

### 6.2 A strict integral-envelope upper witness

Arithmetic Observability VII used two zero-tail sources differing by `e_5` to
obtain the radius upper bound `1/50`.  The full fibres are in fact strictly
closer, even before relaxing tail coefficients from integers to intervals.

The companion certificate chooses the following ten modes near the first
half-grid alias:

```text
220157529292800  220157529264288  220157529863040
220157528661000  220157530205184  220157529984000
220157529055200  220157528520384  220157528834880
220157529177600
```

At each selected mode `k`, set the tail-difference coefficient to its legal
upper endpoint `d_14(k)`; set every other tail-difference coefficient to zero.
Every chosen coefficient is an integer.  It is nonnegative on one tail and
zero on the other, so the assignment belongs both to the independent integral
envelope and to its continuous relaxation.  Let

\[
 L_k=\frac{d_{14}(k)}{k^2},
 \qquad
 K(a,b)=(c_a,c_b)_{\mathbb R}.
 \tag{6.8}
\]

The resulting response difference is

\[
 \Delta=\frac1{25}c_5+\sum_{k\in S}L_kc_k,
 \tag{6.9}
\]

and its norm is evaluated without forming an 8,900-entry approximate vector:

\[
 \|\Delta\|^2
 =\frac1{625}
 +\frac2{25}\sum_{k\in S}L_kK(k,5)
 +\sum_{k,j\in S}L_kL_jK(k,j).
 \tag{6.10}
\]

A 512-bit Arb evaluation using the exact dyadic window coefficients and
ensemble weights proves

\[
 \begin{aligned}
 \|\Delta\|
 &=0.0399999999955643164103176741\ldots,\\
 \frac12\|\Delta\|
 &=0.0199999999977821582051588371\ldots,\\
 \frac1{50}-\frac12\|\Delta\|
 &>2.2\times10^{-12}.
 \end{aligned}
 \tag{6.11}
\]

The formal interval lies strictly below `1/50`.  Hence, for the declared
continuous coefficient-box class,

\[
 \boxed{
 0.0198587033410859808050\ldots
 \le\varepsilon_I^*
 \le0.0199999999977821582052\ldots.}
 \tag{6.12}
\]

The endpoint ratio is below `1.00711510`, a `0.71151%` multiplicative gap.
The witness is integral in the independent coefficient-envelope model, but
that observation does not assert realization by a number field or by a
coupled multiplicative family.

The same two numerical endpoints independently bracket the critical radius
of the coefficientwise integral-envelope class: the lower proof applies to
that smaller tail set, and the upper witness belongs to it.  The two exact
critical radii need not be equal.

The last qualification matters: endpoint integrality is weaker than
arithmetic realizability of the entire coefficient sequence.

---

## 7. What remains in the global prefix minimum

For the broad prefix class

\[
 \Lambda_{14}
 =\{a\in\mathbb Z_{\ge0}^{50}:
 a_1=1,\ 0\le a_n\le d_{14}(n)\},
 \tag{7.1}
\]

every difference vector is exactly an element of

\[
 \mathcal H_{14}
 =\{h\in\mathbb Z^{50}:
 h_1=0,\ |h_n|\le d_{14}(n)\}.
 \tag{7.2}
\]

Every such `h` is realized by taking its positive and negative parts in the
two prefix boxes.  Therefore the exact continuous-relaxation four-anchor
separation is

\[
 \delta_I
 =\min_{\substack{h\in\mathcal H_{14}\\
 (h_2,h_3,h_5)\ne0}}d(h),
 \qquad
 \varepsilon_I^*=\delta_I/2.
 \tag{7.3}
\]

The minimum is attained because the prefix set is finite and `Z` is compact.
This is a mixed-integer convex-distance problem: Theorem 4.1 solves each fixed
`h`, but a minimum over the nonconvex integer set cannot in general be
interchanged with its dual maximum.

### Theorem 7.1 — exact query-coordinate reduction

Every global minimizer in (7.3) has, up to the symmetry `h -> -h`,

\[
 h_2=h_3=0,
 \qquad h_5=1.
 \tag{7.4}
\]

Consequently,

\[
 \boxed{
 \delta_I
 =\min_{p\in\mathcal P}
 \operatorname{dist}(A(e_5+p),\mathcal Z),}
 \tag{7.5}
\]

where

\[
 \mathcal P
 =\{p\in\mathcal H_{14}:
 p_1=p_2=p_3=p_5=0\}.
 \tag{7.6}
\]

#### Proof

The explicit pair in Section 6 gives `delta_I<1/25`.  The common-width row
bounds give

\[
 \begin{aligned}
 h_2\ne0&\Longrightarrow d(h)
 \ge\frac{1-B_2}{\bar\kappa_2}
 =0.2496134355\ldots,\\
 h_3\ne0&\Longrightarrow d(h)
 \ge\frac{1-B_3}{\bar\kappa_3}
 =0.1107750753\ldots,\\
 |h_5|\ge2&\Longrightarrow d(h)
 \ge\frac{2-B_5}{\bar\kappa_5}
 =0.0797174066\ldots.
 \end{aligned}
 \tag{7.7}
\]

All three lower bounds exceed `1/25`.  Query distinctness and `h_1=0` leave
only `|h_5|=1`; central symmetry permits the positive sign.  \(\square\)

Theorem 7.1 is a genuine finite reduction, but it does not prove `p=0`.
Nonquery integer prefix differences are part of the declared nuisance and
must either be excluded by proof or included in a formal search.

### 7.1 A projected ellipsoid for the remaining integers

Let `P_C=C G^{-1}C^*=AR` be orthogonal projection onto `ran C`.  For any tail
difference `z in Z` and response residual `y=Ah-z`,

\[
 \begin{aligned}
 \|y\|^2
 &\ge\|P_Cy\|^2\\
 &=\|A(h-Rz)\|^2\\
 &\ge(1-q)\sum_{n=1}^{50}
 \frac{|h_n-(Rz)_n|^2}{n^4}.
 \end{aligned}
 \tag{7.8}
\]

Since `|(Rz)_n|<=B_n`, taking the infimum gives the separable exact-rational
lower bound

\[
 \boxed{
 d(h)^2
 \ge(1-q)\sum_{n=1}^{50}
 \frac{((|h_n|-B_n)_+)^2}{n^4}.}
 \tag{7.9}
\]

For `h_5=1` and a competitor no farther than `1/25`, every remaining
coordinate must satisfy

\[
 \sum_{n\ne5}
 \frac{((|h_n|-B_n)_+)^2}{n^4}
 \le\mathcal B,
 \tag{7.10}
\]

where

\[
 \mathcal B
 =\frac{1}{625(1-q)}-\frac{(1-B_5)^2}{5^4}
 =0.00002373772267357619294\ldots.
 \tag{7.11}
\]

Exact rational comparison proves that (7.10) forces

\[
 h_4=h_6=h_7=\cdots=h_{14}=0.
 \tag{7.12}
\]

It also gives the explicit coordinatewise consequence

\[
 |h_n|
 \le
 \left\lfloor B_n+n^2\sqrt{\mathcal B}\right\rfloor
 \qquad(15\le n\le50),
 \tag{7.13}
\]

intersected with `|h_n|\le d_{14}(n)`.  The unresolved global calculation is
therefore a finite lattice search over these last 36 nonquery coordinates,
with a convex zonoid distance oracle and dual certificates for every pruned
branch.

### Proposition 7.2 — the zero-tail prefix lattice alone chooses `e_5`

If the continuous tail is suppressed, `e_5` is the unique shortest query
difference, up to sign.  In the no-tail problem, the same Gershgorin case
split directly shows that a change at coordinate 2 or 3, or a change with
`|h_5|>=2`, is longer than `e_5`.  In the only remaining case write

\[
 D^{-1}h=\pm\frac1{25}e_5+u.
 \tag{7.14}
\]

If a nonquery integer changes, `||u||>=1/2500`.  Since `G=I+E`,

\[
 \begin{aligned}
 \|Ah\|^2-\|Ae_5\|^2
 &\ge(1-q)\|u\|^2-\frac{2q_5}{25}\|u\|\\
 &>0,
 \end{aligned}
 \tag{7.15}
\]

because the exact certificate has

\[
 \frac{2q_5}{25(1-q)}<\frac1{2500}.
 \tag{7.16}
\]

This proposition explains why the adjacent pair is the natural first
candidate.  It is not a proof for the full tail-assisted fibres: adding a
common continuous tail changes the optimization geometry.

---

## 8. The all-fifty common-box theorem

The width correction is even more consequential for simultaneous recovery.
The earlier global argument treated the all-fifty coefficient endpoint

\[
 B=
 \frac{
 7203006588741627759985152795444110550802077110215782157377355393577524691875
 }{
 14463072405499051244996447951833472306623699230360514791222607147412978925568
 }
 =0.4980274167750795\ldots
 \tag{8.1}
\]

as an uncentered bias.  Since it lies only slightly below `1/2`, that decoder
had very little margin.  As a signed common-box width, however, it lies far
below the unit label gap.

### Theorem 8.1 — centered recovery of all fifty coefficients

For each `1<=n<=50`, form `B_n` and `bar kappa_n` from (5.9)--(5.10).  Then
centered nearest-integer decoding of all fifty coordinates is uniformly
correct whenever

\[
 \varepsilon
 <\rho_{50}
 :=\min_{1\le n\le50}
 \frac{1-B_n}{2\bar\kappa_n}.
 \tag{8.2}
\]

An exact rational scan proves that `n=50` is the unique bottleneck and

\[
 \boxed{
 \rho_{50}
 =0.0001003945163298032675389996\ldots.}
 \tag{8.3}
\]

Its exact square is

\[
 \frac{
 15246553043322083550734153067832194128793817864218669034013748219875454372800728892379311138397247131424608986531979256721605438087956940520898973780482925056746576002038688156435386604280923619980883075098349967033889911059487
 }{
 1512696094033532083004064735049749510497261272800661201598862675839752738060687723569284691659234900501779411264476043363273867747301828859145020351671851605311443204317662990606704877933730569260355063356130976593069524140425216000000
 }.
 \tag{8.4}
\]

The published Arithmetic Observability I sufficient radius was

\[
 7.8873507724418666\times10^{-7}.
 \tag{8.5}
\]

Thus common centering plus the row-local scan improves the certified radius
by a factor of about `127.285`.  An independent ten-mode integral endpoint
witness, certified by the same Arb method as Section 6.2, gives the strict
upper radius `0.000199999999618975948869...`.  If
\(\rho_{50,\mathrm{cont}}^*\) and \(\rho_{50,\mathrm{int}}^*\) denote the
exact critical radii for the continuous and coefficientwise integral
envelopes, respectively, then

\[
 \rho_{50,\mathrm{cont}}^*,\ \rho_{50,\mathrm{int}}^*
 \in
 [\,0.0001003945163298032675\ldots,\,
 0.0001999999996189759489\ldots\,].
 \tag{8.6}
\]

The bracket ratio is below `1.993`.  As in the four-anchor case, the upper
endpoint is an obstruction for the broad envelope class, not a claim about a
number-field family.

For comparison, using only the global row norm instead of the localized
Schur scan gives the slightly weaker but simpler radius

\[
 \frac{(1-B)\sqrt{1-q}}{5000}
 =0.0001003565728437973388\ldots.
 \tag{8.7}
\]

This confirms that the large gain comes from common-box centering; the Schur
refinement supplies only the final local improvement.

---

## 9. Where the remaining `0.71151%` lives

For the pair-specific direction `c_5`, the complete signed support bound is

\[
 \tau_5
 =1.4158209810239882\times10^{-6}
 +2.8117732435796035\times10^{-4}.
 \tag{9.1}
\]

The first term is the formally evaluated finite sum through one million.  The
second is the cancellation-aware analytic bound beyond one million.  The
remote term accounts for more than `99.49%` of their total.  Hence the present
gap is not evidence of a large observed finite-tail cancellation.  It is
mostly uncertainty in a safe remote support majorant.

The most targeted next theorem is therefore not a larger brute-force prefix
search.  It is a direction-specific remote estimate for

\[
 \sum_{k>M}\frac{d_{14}(k)}{k^2}
 \left|
 \sum_{j\le50}\alpha_j
 R_\mu(\log(k/j))
 \right|,
 \tag{9.2}
\]

where `alpha` specifies a certified dual direction in `ran C`, initially
`c_5` and then a reconstruction-row or an optimized prefix-span direction.
Such a theorem would tighten (4.18) directly.  The exact squared-dual
optimizer need not lie in `ran C`; for a general sample-space direction
`u`, its required remote quantity is instead

\[
 \sum_{k>M}\frac{d_{14}(k)}{k^2}
 |(u,c_k)_{\mathbb R}|.
 \tag{9.3}
\]

A general optimizer certificate must bound (9.3) rather than silently
projecting `u` into the prefix span.  Either refinement would reveal whether
the current remote envelope is close to attained support or merely
conservative.

The complementary global task is a certified branch-and-bound over the
finite lattice left by Theorem 7.1 and (7.10).  Each branch can be pruned by
one of three falsifiable objects:

1. the exact rational projected ellipsoid (7.9);
2. a rigorously enclosed fixed-prefix dual value from (4.18); or
3. an interval lower bound for the convex box quadratic form in the
   reconstructed coordinates.

A primal feasible tail for the best surviving prefix and dual certificates
for all other branches would determine the global closest fibre to any
requested precision.  If a nonzero nonquery prefix wins, that negative result
would be mathematically informative: it would show that query geometry cannot
be inferred from the adjacent coordinate alone.

---

## 10. Relation to earlier observability work

The convex ingredients in Sections 2--4 are classical.  Projection,
support-function, conjugate-duality, and optimality principles belong to
standard convex analysis; see Rockafellar's *Conjugate Duality and
Optimization*
([DOI 10.1137/1.9781611970524](https://doi.org/10.1137/1.9781611970524)).
The zonoid terminology and finite-dimensional convex-body background are
classical as well; see Bolker's *A class of convex bodies*
([DOI 10.1090/S0002-9947-1969-0256265-X](https://doi.org/10.1090/S0002-9947-1969-0256265-X))
and Schneider's *Convex Bodies: The Brunn--Minkowski Theory*
([DOI 10.1017/CBO9781139003858](https://doi.org/10.1017/CBO9781139003858)).
Set-valued uncertainty also has a long control-theoretic history, including
Bertsekas and Rhodes's *Recursive state estimation for a set-membership
description of uncertainty*
([DOI 10.1109/TAC.1971.1099674](https://doi.org/10.1109/TAC.1971.1099674)).
We claim no novelty for those general tools.

Dirichlet series have appeared in observability theory before this project.
Gilliam and Martin's 1987 paper *Discrete observability and Dirichlet series*
linked recovery of heat-equation initial data from measurements discrete in
time and space to Dirichlet-series theory, solving a one-dimensional case
([DOI 10.1016/0167-6911(87)90061-2](https://doi.org/10.1016/0167-6911(87)90061-2)).
Komornik and Loreti's 2003 paper *Dirichlet series and simultaneous
observability: two problems solved by the same approach* used generalized
Ingham inequalities both for a Dirichlet-series singularity theorem and for a
simultaneous string-observability problem
([DOI 10.1016/S0167-6911(02)00267-0](https://doi.org/10.1016/S0167-6911(02)00267-0)).

The Hilbert-space treatment of square-summable Dirichlet series is also an
established subject; Hedenmalm, Lindqvist, and Seip's 1997 paper modeled that
space through an infinite-dimensional polydisk and vertical limit functions
([DOI 10.1215/S0012-7094-97-08601-4](https://doi.org/10.1215/S0012-7094-97-08601-4)).
Classical sampling theory, including Shannon's *Communication in the presence
of noise*
([DOI 10.1109/JRPROC.1949.232969](https://doi.org/10.1109/JRPROC.1949.232969)),
provides broader historical context for finite harmonic acquisition.  The
pinned AS-V measure here is not asserted to be a new sampling theorem.

The present result is adjacent but different.  It studies coefficientwise
bounded arithmetic tails at one pinned finite Mellin-harmonic acquisition,
uses common-nuisance centering and compact-zonoid distance rather than a
spectral gap inequality, and supplies finite exact-rational and interval
certificates for declared degree-fourteen source boxes.  We do not claim
priority for connecting Dirichlet series and observability, for Hilbert-space
projection duality, for support functions of zonoids, or for Schur-complement
row bounds.  The contribution is their model-specific synthesis, the
common-width correction, the exact fixed-fibre formulation, and the certified
arithmetic consequences above.

---

## 11. Formal certificate boundary

The companion package is

```text
arithmetic_observability_common_nuisance.py
arithmetic_observability_common_nuisance_certificate.json
test_arithmetic_observability_common_nuisance.py
```

with schema

```text
arithmetic-observability-common-nuisance-v1
```

Its pinned payload digest is

```text
96b874899b16e4502d815627c7b722b9ba0332266fb30c8cd4d0579b48ca0cfd
```

The pinned Arithmetic Sensing V source file and formal-payload digests are,
respectively,

```text
ad03df9d6325512074e6940602c1c888c81abd057a5856d6212f93dc8e780517
89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b
```

It is required to verify at least the following finite claims.

1. Pin the exact Arithmetic Sensing V source file and its formal payload
   digest.
2. Reconstruct all fifty `tau_n`, `q_n`, `B_n`, Schur row bounds, and centered
   squared radii from exact rationals.
3. Prove by rational comparison that `n=5` and `n=50` are the unique
   bottlenecks in their respective scans.
4. Verify the new four-anchor and all-fifty lower squares and the strict
   endpoint comparisons.
5. Verify the exact `c_5` dual fraction (6.6).
6. Reconstruct both selected ten-mode generalized-divisor endpoint witnesses
   and their factorizations, evaluate their Gram formulas in 512-bit Arb,
   prove integral coefficient admissibility, prove the `n=5` radius is below
   `1/50` by more than `2.2e-12`, and prove the `n=50` radius is below
   `1/5000` by more than `3.8e-13`.
7. Verify the exact query-coordinate reductions in (7.7), the projected
   ellipsoid budget, and the exclusions through coordinate `14`.
8. Record the finite-versus-remote split in (9.1) without treating its
   descriptive ratio as an exact support evaluation.
9. Enforce strict JSON shape, canonical fractions, bounded resources,
   dependency hashes, line endings, package digests, and adversarial mutation
   tests.

The companion executable does **not** mechanize the compactness proof,
Hilbert projection theorem, infinite support identity, or exact KKT theorem.
Those are manuscript mathematics.  It also does not prove that the adjacent
`e_5` pair is the global closest four-anchor fibre, that the continuous-box
optimum equals the integral-tail optimum, or that every envelope sequence is
realized by a number field.

---

## 12. Reproduction

From the repository root, using the pinned `python-flint` environment:

```bash
python arithmetic_observability_common_nuisance.py \
  --certificate arithmetic_observability_common_nuisance_certificate.json

python -m unittest -v \
  test_arithmetic_observability_common_nuisance.py
```

The verifier regenerates its payload from the pinned Arithmetic Sensing V
artifact and the declared exact inputs.  A certificate is evidence only for
the fields it reconstructs; passing it is not evidence for stronger claims
excluded in Section 11.

---

## 13. Conclusions

The common-nuisance correction changes both the quantitative result and the
conceptual picture.

1. Arithmetic tails inside one shared coefficient box are governed by the
   box width.  Centering converts the existing AS-V absolute-sum bounds into
   half-width single-tail biases.
2. The four-anchor sufficient radius rises to
   `0.01985870334108598...`, within `0.71151%` of a strict certified
   integral-envelope alias obstruction.
3. The all-fifty sufficient radius rises by a factor of about `127.285`, and
   its exact bracket contracts to less than a factor of `1.993`.
4. The continuous tail relaxation has an exact, attained primal-dual
   description with a checkable squared-gap identity.
5. The adjacent `n=5` pair is uniquely shortest before tails, but the full
   global fibre problem still includes nonquery integer prefixes.  The
   manuscript reduces, rather than hides, that remaining search.
6. The dominant uncertainty is now localized: a conservative remote support
   bound beyond one million, not the explicitly summed finite tail.

This is the intended behavior of a falsifiable theory of arithmetic
observability.  A stronger theorem, a counterexample prefix, or a sharper
remote certificate can each move a precisely defined boundary.  None
requires reinterpreting a sufficient bound as an exact answer.
