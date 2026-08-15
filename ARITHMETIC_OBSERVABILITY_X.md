# Arithmetic Observability X

## Arithmetic defect, convexification gaps, and infinite-support fibres

### Exact quotient certificates and the boundary between continuous and integral nuisance models

- **Research lead, theorem synthesis, computation design, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** research manuscript; formal convexification-gap certificate
  complete; not peer reviewed
- **Date:** 15 August 2026
- **Parent manuscripts:** `ARITHMETIC_OBSERVABILITY_VIII.md`,
  `ARITHMETIC_OBSERVABILITY_IX.md`, and
  `ARITHMETIC_SENSING_V_COMPLETE.md`

## Abstract

Arithmetic Observability IX replaced the unresolved nonquery-prefix search by
the quotient distance between an affine subspace and a compact arithmetic
zonoid.  It certified the four-anchor critical radius to within `0.043304%`,
but it did not identify the quotient minimizer or determine whether the
continuous and coefficientwise integral nuisance models have the same closest
fibre.

This paper identifies the exact mathematical obstruction.  First, it gives a
finite quotient quadratic program, its attained dual, its KKT system, and a
primal--dual gap identity with a direction-specific remote-tail remainder.
For the pinned four-anchor model, every optimal real nonquery-prefix
coefficient is smaller than

\[
 0.04907896327096330.
\]

The unbounded quotient value is therefore exactly the distance to the convex
hull of the legal bounded **integral** nuisance responses, not merely a lower
relaxation obtained by discarding the prefix bounds.

Let `x_*` be the convex projection and let `eta` be its distance to the actual
nonconvex integral response set.  Projection geometry gives

\[
 \sqrt{d^2+\eta^2}
 \le d_{\mathbb Z}
 \le d+\eta.
\]

Thus `eta` is a precise arithmetic defect: continuous and integral distances
agree exactly when the convex projection is integrally realizable.  Any such
realization in the pinned model must use zero nonquery prefix.

The sampled exponential frame makes the remaining tail defect finite in a
different sense.  A positive-distance continuous optimizer saturates every
tail coefficient except possibly those for which its residual response
vanishes.  That response is an antiperiodic trigonometric polynomial of degree
at most `8899`; consequently at most `8899` integer tail coordinates can be
exceptional.  Nevertheless, neither a continuous nor an independent integral
positive-distance optimizer can have finite support.  Both model classes are
compact and attain their optima, but every exact optimizer uses infinitely
many tail coordinates.  Finite witnesses are dense and strictly improvable.

An eleventh legal mode gives an explicit improvement of the published
ten-mode integral alias witness.  The companion AO-X artifact formally
certifies that improvement, the resulting eleven-mode upper endpoint, a
one-coordinate real quotient descent, and the corresponding metric-projection
localization.  It does not identify an exact optimizer.  The exact quotient
value, integral equality, and number-field realizability remain open.

---

## 1. Model boundary and notation

Let `H` be the finite-dimensional realification of the pinned Arithmetic
Sensing V data space.  At logarithmic frequency `x`, let `c(x) in H` be the
normalized sampled exponential column.  For an integer `n>=1`, write

\[
 c_n=c(\log n),
 \qquad
 Ae_n=\frac{c_n}{n^2},
 \qquad
 \|c_n\|=1.
 \tag{1.1}
\]

The four-anchor query reduction from Arithmetic Observability VIII fixes the
query difference to `e_5`, up to overall sign.  Put

\[
 q=Ae_5=\frac1{25}c_5,
 \qquad
 J=\{4,6,7,\ldots,50\},
 \tag{1.2}
\]

and let

\[
 C:\mathbb R^J\longrightarrow H,
 \qquad
 C\alpha=\sum_{j\in J}\alpha_jc_j.
 \tag{1.3}
\]

Thus the real nonquery-prefix subspace is

\[
 W=\operatorname{ran}C.
 \tag{1.4}
\]

If `p_j` is an original prefix coefficient, its normalized coefficient in
(1.3) is

\[
 \alpha_j=\frac{p_j}{j^2},
 \qquad
 Ap=C\alpha.
 \tag{1.5}
\]

For `k>50`, set

\[
 d_k=d_{14}(k),
 \qquad
 a_k=\frac{d_k}{k^2}.
 \tag{1.6}
\]

Since

\[
 \sum_{k>50}a_k<\infty,
 \tag{1.7}
\]

all tail series below converge absolutely and uniformly over their declared
coefficient products.

### 1.1 Three tail models

The **continuous coefficient box** is

\[
 X_{\rm cont}
 =\prod_{k>50}[-d_k,d_k],
 \tag{1.8}
\]

with response body

\[
 \mathcal Z
 =\left\{
   \sum_{k>50}\xi_k\frac{c_k}{k^2}:
   \xi\in X_{\rm cont}
  \right\}.
 \tag{1.9}
\]

The **independent integral coefficient envelope** is

\[
 X_{\mathbb Z}
 =\prod_{k>50}
 \bigl([-d_k,d_k]\cap\mathbb Z\bigr),
 \tag{1.10}
\]

with response set

\[
 \mathcal Z_{\mathbb Z}
 =\left\{
   \sum_{k>50}\xi_k\frac{c_k}{k^2}:
   \xi\in X_{\mathbb Z}
  \right\}.
 \tag{1.11}
\]

This is the exact difference-coordinate set for two independent nonnegative
integer boxes: every signed `xi_k` is realized by assigning its positive and
negative parts to the two tails.  It is not an assertion that those
coordinate choices arise from one number field.

Finally, genuinely arithmetically realizable sequences may satisfy coupled
multiplicative or field-theoretic constraints.  They form a possibly much
smaller set.  Nothing in this paper identifies that set with either (1.9) or
(1.11).

Let

\[
 \mathcal P_{\mathbb Z}
 =\prod_{j\in J}
 \bigl([-d_{14}(j),d_{14}(j)]\cap\mathbb Z\bigr)
 \tag{1.12}
\]

be the legal nonquery-prefix difference box, and let

\[
 \mathcal P_{\rm cont}
 =\operatorname{conv}\mathcal P_{\mathbb Z}
 =\prod_{j\in J}[-d_{14}(j),d_{14}(j)].
 \tag{1.13}
\]

The integral nuisance response set and its continuous bounded relaxation are

\[
 \begin{aligned}
 \mathcal S_{\mathbb Z}
 &=\{z-Ap:z\in\mathcal Z_{\mathbb Z},\ p\in\mathcal P_{\mathbb Z}\},\\
 \mathcal C_{\rm box}
 &=\{z-Ap:z\in\mathcal Z,\ p\in\mathcal P_{\rm cont}\}.
 \end{aligned}
 \tag{1.14}
\]

The exact independent-integral separation after the query reduction is

\[
 \delta_{\mathbb Z}
 =\operatorname{dist}(q,\mathcal S_{\mathbb Z}),
 \tag{1.15}
\]

whereas the unbounded quotient value from Arithmetic Observability IX is

\[
 \delta_Q
 =\operatorname{dist}(q,\mathcal Z-W)
 =\inf_{w\in W,z\in\mathcal Z}\|q+w-z\|.
 \tag{1.16}
\]

The associated critical radii are one half of the corresponding distances.

---

## 2. Exact finite quotient optimization

The infinite zonoid has a finite-dimensional data image, but its coefficient
description is countable.  A finite tail set supplies a conventional convex
quadratic program whose residual is already in the correct quotient space.

Let `F` be any finite subset of `{51,52,...}`.  Define

\[
 G_F:\mathbb R^F\longrightarrow H,
 \qquad
 G_F\theta=\sum_{k\in F}a_k\theta_kc_k,
 \qquad |\theta_k|\le1.
 \tag{2.1}
\]

Let

\[
 B=C^{\mathsf T}C,
 \quad b=C^{\mathsf T}q,
 \quad D=C^{\mathsf T}G_F,
 \quad K=G_F^{\mathsf T}G_F.
 \tag{2.2}
\]

The matrix `B` is positive definite by the certified Gram bound.

### Theorem 2.1 - exact Schur-complement box program

The finite quotient distance

\[
 \delta_F
 =\min_{\alpha\in\mathbb R^J,\ |\theta_k|\le1}
 \|q+C\alpha-G_F\theta\|
 \tag{2.3}
\]

is attained.  Its squared value is

\[
 \boxed{
 \frac{\delta_F^2}{2}
 =\frac12\min_{|\theta_k|\le1}
 \left(\gamma-2\ell^{\mathsf T}\theta
       +\theta^{\mathsf T}\Gamma\theta\right),}
 \tag{2.4}
\]

where

\[
 \begin{aligned}
 \gamma
 &=\langle q,q\rangle-b^{\mathsf T}B^{-1}b,\\
 \ell
 &=G_F^{\mathsf T}q-D^{\mathsf T}B^{-1}b,\\
 \Gamma
 &=K-D^{\mathsf T}B^{-1}D\succeq0.
 \end{aligned}
 \tag{2.5}
\]

For a minimizing `theta`, the unique minimizing nuisance coefficient is

\[
 \alpha=B^{-1}(D\theta-b).
 \tag{2.6}
\]

#### Proof

For fixed `theta`, differentiating the squared norm in (2.3) with respect to
`alpha` gives

\[
 B\alpha+b-D\theta=0,
 \tag{2.7}
\]

which proves (2.6).  Substitute (2.6) into the expanded squared norm.  The
result is (2.4)--(2.5).  Equivalently, if

\[
 Q=I-CB^{-1}C^{\mathsf T}=P_{W^\perp},
 \tag{2.8}
\]

then

\[
 \gamma=\|Qq\|^2,
 \quad
 \ell=G_F^{\mathsf T}Qq,
 \quad
 \Gamma=G_F^{\mathsf T}QG_F.
 \tag{2.9}
\]

This also proves `Gamma` is positive semidefinite.  The coefficient box is
compact, so the reduced minimum is attained.  \(\square\)

Every entry in (2.2) is a positive rational scale times the sampled kernel

\[
 \kappa(\log(i/j))=(c_i,c_j)_{\mathbb R}.
 \tag{2.10}
\]

No sample-space vector with thousands of coordinates is required to state or
verify the finite program.

### Theorem 2.2 - finite squared dual and KKT system

The finite quotient program has the attained dual

\[
 \boxed{
 \frac{\delta_F^2}{2}
 =\max_{\substack{u\in H\\C^{\mathsf T}u=0}}
 \left(
 (u,q)_{\mathbb R}
 -\sum_{k\in F}a_k|(u,c_k)_{\mathbb R}|
 -\frac12\|u\|^2
 \right).}
 \tag{2.11}
\]

A primal triple `(alpha,theta,r)` is optimal if and only if

\[
 \begin{aligned}
 r&=q+C\alpha-G_F\theta,\\
 C^{\mathsf T}r&=0,\\
 \theta_k&\in\operatorname{Sign}\bigl((r,c_k)_{\mathbb R}\bigr)
 \qquad(k\in F),
 \end{aligned}
 \tag{2.12}
\]

where

\[
 \operatorname{Sign}(t)
 =\begin{cases}
 \{1\},&t>0,\\
 [-1,1],&t=0,\\
 \{-1\},&t<0.
 \end{cases}
 \tag{2.13}
\]

The unique dual optimizer is the primal residual `r`.

#### Proof

Apply Fenchel duality to the squared distance from `Qq` to the finite
zonotope `QG_F[-1,1]^F`.  Its support function at a vector in `W^perp` is

\[
 \sum_{k\in F}a_k|(u,c_k)_{\mathbb R}|.
 \tag{2.14}
\]

This gives (2.11).  Strict concavity of the negative norm square gives dual
uniqueness.  The normal equation in `alpha` is `C^T r=0`.  The coordinatewise
normal-cone condition for the box is precisely the sign rule in (2.12).
These conditions are necessary and sufficient because the primal objective
is convex and differentiable and its feasible box has nonempty relative
interior.  \(\square\)

If no pairing in (2.12) vanishes, a proposed sign vector `s in {+1,-1}^F`
reduces the KKT problem to the linear calculation

\[
 \alpha_s=B^{-1}(Ds-b),
 \qquad
 r_s=q+C\alpha_s-G_Fs,
 \tag{2.15}
\]

followed by the finite strict tests

\[
 s_k(r_s,c_k)_{\mathbb R}>0.
 \tag{2.16}
\]

This is a useful certificate form, but the infinite optimizer cannot be
certified by a finite sign vector; Section 6 proves why.

### Theorem 2.3 - remote-aware primal--dual gap

Let `R` be the complement of `F` in `{51,52,...}`.  Suppose

\[
 U_R(u)
 \ge\sum_{k\in R}a_k|(u,c_k)_{\mathbb R}|
 \tag{2.17}
\]

is a certified support upper bound.  Let `(alpha,theta)` be finite-primal
feasible, put

\[
 r=q+C\alpha-G_F\theta,
 \tag{2.18}
\]

and take any exact quotient-dual vector `u` satisfying `C^T u=0`.  Define

\[
 \begin{aligned}
 P(\alpha,\theta)
 &=\frac12\|r\|^2,\\
 D_U(u)
 &=(u,q)_{\mathbb R}
 -\sum_{k\in F}a_k|(u,c_k)_{\mathbb R}|
 -U_R(u)-\frac12\|u\|^2.
 \end{aligned}
 \tag{2.19}
\]

Then

\[
 \boxed{
 \begin{aligned}
 P(\alpha,\theta)-D_U(u)
 &=\frac12\|r-u\|^2\\
 &\quad+
 \sum_{k\in F}a_k
 \left(
 |(u,c_k)_{\mathbb R}|
 -\theta_k(u,c_k)_{\mathbb R}
 \right)
 +U_R(u)\ge0.
 \end{aligned}}
 \tag{2.20}
\]

Here `D_U` is a conservative dual value obtained by replacing the exact
remote support with its certified upper bound.  Equation (2.20) is an exact
identity for that conservative value; it is not an assertion that `U_R`
equals the remote support.
The exact full squared-dual objective used below is

\[
 D(u)=(u,q)_{\mathbb R}
 -\sum_{k>50}a_k|(u,c_k)_{\mathbb R}|
 -\frac12\|u\|^2,
 \qquad C^{\mathsf T}u=0,
\]

and the compact-zonoid projection theorem gives
`delta_Q^2/2=max D(u)`.

Consequently,

\[
 \sqrt{\max\{0,2D_U(u)\}}
 \le\delta_Q
 \le\sqrt{2P(\alpha,\theta)}.
 \tag{2.21}
\]

#### Proof

Expand `||r-u||^2/2`.  Since `C^T u=0`, the `C alpha` term drops out.  The
remaining finite support terms give the sum in (2.20).  Every summand is
nonnegative because `|theta_k|<=1`, and `U_R(u)` is nonnegative.  The lower
bound in (2.21) is weak duality for the full tail; the upper bound uses the
finite tail with all omitted coefficients set to zero.  \(\square\)

If a primal certificate uses an explicit finite set outside a contiguous
cutoff, that set may simply be included in `F`.  Alternatively, one may leave
it inside `R`; then `U_R(u)-(u,z_R)` replaces the final term in (2.20) and is
still nonnegative.

### Corollary 2.4 - directional truncation bracket

Let

\[
 F_M=\{51,52,\ldots,M\},
 \tag{2.22}
\]

and suppose the finite optimum has `delta_M>0`, residual `r_M`, and unit
normal

\[
 \nu_M=\frac{r_M}{\delta_M}.
 \tag{2.23}
\]

Then

\[
 \boxed{
 \max\{0,\delta_M-U_{>M}(\nu_M)\}
 \le\delta_Q\le\delta_M.}
 \tag{2.24}
\]

#### Proof

Finite KKT gives

\[
 \delta_M
 = (\nu_M,q)_{\mathbb R}
 -\sum_{51\le k\le M}a_k
 |(\nu_M,c_k)_{\mathbb R}|.
 \tag{2.25}
\]

For \(t\ge0\), insert \(u=t\nu_M\) into the full squared dual, and let
`D` denote its exact objective.  Positive homogeneity of the support and
(2.25) give

\[
 D(t\nu_M)
 \ge t\bigl(\delta_M-U_{>M}(\nu_M)\bigr)-\frac12t^2.
 \tag{2.26}
\]

Maximizing the right side over \(t\ge0\) gives one half the square of the
positive part in (2.24).  Taking square roots proves the lower bound.  The
upper bound follows because the finite zonotope is contained in the full
zonoid.  \(\square\)

The direction-free Hausdorff remainder

\[
 R_M=\sum_{k>M}a_k
 \tag{2.27}
\]

also gives `delta_M-R_M<=delta_Q<=delta_M`, but it is far too large at the
pinned cutoff.  Arithmetic Observability IX supplies the useful
direction-specific alternative through exact alias-circle support bounds.

---

## 3. The bounded quotient is an exact convex hull

The quotient in (1.16) permits every real vector in `W`.  In the pinned
problem this does not change the convex value: its optimizer lies far inside
the legal bounded prefix box.

The Arithmetic Observability IX certificate supplies exact upper bounds

\[
 \begin{aligned}
 q_G
 &=\frac{257168756981514768514508306559006707}{2^{128}},\\
 q_5
 &=\frac{108343607646993126701039729904793}{2^{128}},\\
 \tau_W
 &=\frac{6670899940450463606943553795810303}{2^{128}},
 \end{aligned}
 \tag{3.1}
\]

where `q_G` bounds every off-diagonal Gram row sum, `q_5` bounds the fifth
row sum, and

\[
 h_{\mathcal Z}(c_j)\le\tau_W
 \qquad(j\in J).
 \tag{3.2}
\]

The symbol `q_G` is used here to avoid confusing the scalar Gram defect with
the vector `q=c_5/25`.

### Lemma 3.1 - every fixed-tail prefix projection is small

For each `z in Z`, the unique minimizer of

\[
 \alpha\longmapsto\|q+C\alpha-z\|
 \tag{3.3}
\]

is

\[
 \alpha(z)=-B^{-1}C^{\mathsf T}(q-z),
 \tag{3.4}
\]

and obeys

\[
 \|\alpha(z)\|_\infty
 \le L_W
 :=\frac{q_5/25+\tau_W}{1-q_G}.
 \tag{3.5}
\]

For the exact inputs (3.1),

\[
 L_W
 =\frac{
 166880842118908583300289884625162368
 }{
 8500629954098923717371502478130230118725
 }
 =0.00001963158530838531709878\ldots.
 \tag{3.6}
\]

Hence every original prefix coefficient satisfies

\[
 \boxed{
 \|p(z)\|_\infty
 \le2500L_W
 =\frac{
 16688084211890858330028988462516236800
 }{
 340025198163956948694860099125209204749
 }
 =0.04907896327096329274695\ldots<1.}
 \tag{3.7}
\]

#### Proof

The normal equations give (3.4).  If

\[
 b(z)=C^{\mathsf T}(q-z),
 \tag{3.8}
\]

then, for every `j in J`,

\[
 \begin{aligned}
 |b_j(z)|
 &\le\frac1{25}|(c_j,c_5)_{\mathbb R}|
      +|(c_j,z)_{\mathbb R}|\\
 &\le\frac{q_5}{25}+\tau_W.
 \end{aligned}
 \tag{3.9}
\]

The real symmetric principal Gram block satisfies

\[
 \|B-I\|_\infty\le q_G<1,
 \qquad
 \|B^{-1}\|_\infty\le\frac1{1-q_G}.
 \tag{3.10}
\]

Equations (3.4), (3.9), and (3.10) prove (3.5).  Finally `p_j=j^2
alpha_j` and `j^2<=2500`, which proves (3.7).  The argument is realified; a
complex coefficient solve would require additional support bounds in the
directions `i c_j`.  \(\square\)

### Lemma 3.2 - continuous tails are the convex hull of integral tails

In the finite-dimensional space `H`,

\[
 \boxed{
 \operatorname{conv}\mathcal Z_{\mathbb Z}=\mathcal Z.}
 \tag{3.11}
\]

#### Proof

The inclusion from left to right is immediate because `Z` is convex and
contains `Z_Z`.  For the converse, fix `xi in X_cont`.  At each coordinate
choose a random integer `Xi_k` supported on

\[
 \{\lfloor\xi_k\rfloor,\lceil\xi_k\rceil\}
 \tag{3.12}
\]

with expectation `xi_k`; at an integer coordinate choose that value with
probability one.  Take the product probability measure.  Absolute uniform
convergence gives

\[
 \mathbb E\left[
  \sum_{k>50}\Xi_k\frac{c_k}{k^2}
 \right]
 =\sum_{k>50}\xi_k\frac{c_k}{k^2}.
 \tag{3.13}
\]

Thus every point of `Z` is a barycenter of a probability measure supported
on `Z_Z`, and hence belongs to its closed convex hull.  In a finite-
dimensional space the convex hull of a compact set is compact: by
Caratheodory, every point uses at most `dim(H)+1` support points.  Section 6
proves directly that `Z_Z` is compact.  Therefore its convex hull is already
closed, proving (3.11).  \(\square\)

### Theorem 3.3 - quotient equals the exact integral convex hull

For the pinned four-anchor problem,

\[
 \boxed{
 \begin{aligned}
 \delta_Q
 &=\operatorname{dist}(q,\mathcal Z-W)\\
 &=\operatorname{dist}(q,\mathcal C_{\rm box})\\
 &=\operatorname{dist}
   \bigl(q,\operatorname{conv}\mathcal S_{\mathbb Z}\bigr).
 \end{aligned}}
 \tag{3.14}
\]

#### Proof

The finite prefix identity

\[
 \operatorname{conv}\mathcal P_{\mathbb Z}
 =\mathcal P_{\rm cont}
 \tag{3.15}
\]

and Lemma 3.2 give

\[
 \operatorname{conv}\mathcal S_{\mathbb Z}
 =\mathcal C_{\rm box}.
 \tag{3.16}
\]

Since the bounded real prefix box is contained in `W`, the first distance in
(3.14) is no larger than the second.  Conversely, quotienting by `W` gives
the compact projected body `QZ`, so a quotient minimizer exists.  Choose a
tail `z` above its projected point and then use the unique fixed-tail
coefficient `alpha(z)` from Lemma 3.1.  Equation (3.7) places every
corresponding original coefficient strictly inside `[-1,1]`, which is
contained in the legal real prefix box because `d_14(j)>=1`.  The quotient
minimizer therefore belongs to `C_box`, so the two distances agree.  Equation
(3.16) finishes the proof.  \(\square\)

This theorem is stronger than saying that the quotient is a safe lower
relaxation.  It identifies the quotient exactly as the convexified
independent-integral problem.

### Corollary 3.4 - integral attainment forces zero prefix

If some point of `S_Z` attains the quotient distance `delta_Q`, every
integral prefix in such a representation is zero.

#### Proof

Write the attaining point as `z-Ap`.  For this fixed `z`, its real prefix must
minimize (3.3); otherwise replacing it by the unique fixed-tail minimizer
would contradict global optimality.  Equation (3.7) bounds every integer
`p_j` strictly between `-1` and `1`, so `p=0`.  \(\square\)

The corollary does not prove integral attainment.  It says that if the convex
projection is an actual integral nuisance response, the prefix part cannot
hide the realization: the entire response must be supplied by an integral
tail.  The compact image `S_Z` is not a discrete subset of `H`; only its
coordinate alphabets are discrete.  Infinite integer selections can produce
a Cantor-like or otherwise nondiscrete compact image.

---

## 4. Arithmetic-defect geometry

The continuous-versus-integral question is a projection-realizability
problem.  The following statement is independent of the arithmetic model.

### Theorem 4.1 - Pythagorean relaxation gap

Let `C` be a nonempty compact convex subset of a finite-dimensional real
Hilbert space, let `S subset C` be nonempty and compact, and let

\[
 x_*=P_Cq,
 \qquad
 d=\|q-x_*\|,
 \qquad
 \eta=\operatorname{dist}(x_*,S).
 \tag{4.1}
\]

Then

\[
 \boxed{
 \sqrt{d^2+\eta^2}
 \le\operatorname{dist}(q,S)
 \le d+\eta.}
 \tag{4.2}
\]

In particular,

\[
 \boxed{
 \operatorname{dist}(q,S)=d
 \quad\Longleftrightarrow\quad
 x_*\in S.}
 \tag{4.3}
\]

#### Proof

Projection normality says

\[
 (q-x_*,s-x_*)_{\mathbb R}\le0
 \qquad(s\in C).
 \tag{4.4}
\]

Hence, for every `s in S`,

\[
 \begin{aligned}
 \|q-s\|^2
 &=\|q-x_*\|^2+\|x_*-s\|^2
   +2(q-x_*,x_*-s)_{\mathbb R}\\
 &\ge d^2+\|x_*-s\|^2.
 \end{aligned}
 \tag{4.5}
\]

Taking the infimum proves the lower bound.  If `s_*` minimizes the distance
from `x_*` to `S`, the triangle inequality gives

\[
 \operatorname{dist}(q,S)
 \le\|q-s_*\|
 \le d+\eta.
 \tag{4.6}
\]

Compactness makes both projections attained.  If `eta=0`, then `x_* in S`
and equality with `d` is immediate.  Conversely, equality with `d` and
(4.5) force `eta=0`.  \(\square\)

### Definition 4.2 - arithmetic defect

For the pinned model, define

\[
 x_*=P_{\operatorname{conv}\mathcal S_{\mathbb Z}}q,
 \qquad
 \eta_{\rm arith}
 =\operatorname{dist}(x_*,\mathcal S_{\mathbb Z}).
 \tag{4.7}
\]

Theorem 3.3 and Theorem 4.1 give

\[
 \boxed{
 \sqrt{\delta_Q^2+\eta_{\rm arith}^2}
 \le\delta_{\mathbb Z}
 \le\delta_Q+\eta_{\rm arith}.}
 \tag{4.8}
\]

Thus the convexification gap is not an unspecified integrality penalty.  It
is controlled by the distance from one explicit convex projection to the
actual arithmetic response set.

### 4.1 Exact equivalence and two counterexamples

The distinctions are now exact:

\[
 \begin{array}{rcl}
 \delta_Q=0
 &\Longleftrightarrow&
 q\in\operatorname{conv}\mathcal S_{\mathbb Z},\\[2mm]
 \delta_{\mathbb Z}=0
 &\Longleftrightarrow&
 q\in\mathcal S_{\mathbb Z},\\[2mm]
 \delta_{\mathbb Z}=\delta_Q
 &\Longleftrightarrow&
 x_*\in\mathcal S_{\mathbb Z}.
 \end{array}
 \tag{4.9}
\]

Convex observational equivalence need not be integral equivalence.  In
`H=R`, take

\[
 S=\{-1,1\},
 \qquad C=[-1,1],
 \qquad q=0.
 \tag{4.10}
\]

Then `d=0` but `eta=dist(q,S)=1`, so the relaxation collides while the
nonconvex model remains separated.

The lower bound in (4.2) can be exact at positive distance.  In `R^2`, take

\[
 S=\{(-\eta,0),(\eta,0)\},
 \quad
 C=[-\eta,\eta]\times\{0\},
 \quad
 q=(0,d).
 \tag{4.11}
\]

Then `x_*=(0,0)` and

\[
 \operatorname{dist}(q,S)=\sqrt{d^2+\eta^2}.
 \tag{4.12}
\]

These examples rule out any theorem that silently identifies a compact set
with its convex hull or replaces the arithmetic defect by a first-order
support calculation.

Two model-structured examples isolate the two possible sources of the gap.
First take

\[
 H=\mathbb R^2,
 \qquad
 W=\operatorname{span}\{(1,0)\},
 \qquad
 \mathcal Z=\{0\},
 \qquad
 q=(1/2,1).
\]

The real-prefix quotient removes the first coordinate and has distance `1`.
If the prefix coefficient must instead be integral, its first residual
coordinate has absolute value at least `1/2`, so the exact distance is

\[
 \frac{\sqrt5}{2}>1.
\]

Thus prefix integrality alone can make convexification strict.  In the pinned
model, bound (3.7) turns equality into the sharp zero-prefix test of
Corollary 3.4; it does not prove that the test passes.

For a tail-only example, take

\[
 H=\mathbb R^2,
 \qquad
 \mathcal Z=[-1,1]^2,
 \qquad
 \mathcal Z_{\mathbb Z}=\{-1,0,1\}^2,
 \qquad
 q=(2,1/2).
\]

The continuous distance is `1`, attained at `(1,1/2)`, whereas the nearest
integral tail points `(1,0)` and `(1,1)` are both at distance

\[
 \frac{\sqrt5}{2}>1.
\]

Thus tail integrality can independently create a strict gap.  Section 5
reduces equality in the pinned model to a finite exceptional-face test; it
does not assert that the test passes.

### 4.2 Current localization, not exact recovery

Let `L` be the certified quotient distance lower from Arithmetic
Observability IX and let `U` be any feasible nuisance-response upper.  For
that response `s in conv(S_Z)`, (4.5) gives

\[
 \|x_*-s\|
 \le\sqrt{U^2-L^2}.
 \tag{4.13}
\]

Write `s_11` for the negative of the eleven-mode tail response, with zero
prefix, so that `q-s_11=Delta_11`.  The companion AO-X artifact uses this
legal integral response and the inherited AO-IX quotient lower.  Their exact
squared localization radius is

\[
 U^2-L^2
 =\frac{
 584388052516222151488109484484924277339295849686303517890888341110967736305220437276569054716441929213615978243517397534360819695084923953246908384328937148395789146105509270584732805642994565582936070277639256833919218078871300109544914181581670415352307654744927953
 }{
 421997051664125209268406588769770717187705581821478415248263834084954427431214698985191233456985827456970234037406465691347923741048546908508277349709481407047272198869930624442664974582849507983248143483345206758289017586691230580408615490919729596741399521952555597824000
 }.
 \tag{4.14}
\]

Consequently the certified outward enclosure is

\[
 \|x_*-s_{11}\|
 \le 1.176781834823725611650897135\ldots\times10^{-3}.
 \tag{4.15}
\]

This is a rigorous localization of the convex projection around the explicit
eleven-mode response `s_11`.  It does not identify `x_*` or any coefficientwise
optimizer and is much wider than the scalar distance gap.

For completeness, let

\[
 \rho_{\mathrm{cont}}^*=\frac12\delta_Q,
 \qquad
 \rho_{\mathrm{int}}^*=\frac12\delta_{\mathbb Z}.
 \tag{4.16}
\]

The exact certified endpoints are

\[
 \begin{aligned}
 \rho_-&>0,\\
 \rho_-^2
 &=\frac{
 522498539110428232051459448205413793406130172262694566199655461204496602604045250436934053894588758576546341875255041253645236604172776941139523097969
 }{
 1307377896291793069080052219103517151139796265284360653520230531080727409669497180507688124376509215585344987824569223506558746956505175752733561454592000
 },\\
 \rho_+
 &=\frac{
 8580997074204765306731431976326904868585364962800439605261031394743733548586069164381065333367657644425871979220887974785942792533416422831139179387594863
 }{
 429049853758163107186368799942587076079339706258956588087153966199096448962353503257659977541340909686081019461967553627320124249982290238285876768194691072
 }.
 \end{aligned}
 \tag{4.17}
\]

The AO-IX lower certificate and the eleven-mode feasible response therefore
give the common formal bracket

\[
 \boxed{
 \rho_{\mathrm{cont}}^*,\rho_{\mathrm{int}}^*
 \in[\rho_-,\rho_+]}
 \subset
 [
 0.0199913430273943145214458406485\ldots,
 0.0199999999977660012499708079641
 ].
 \tag{4.18}
\]

The lower endpoint is inherited from the quotient relaxation.  The upper
endpoint is supplied by an outward enclosure of an explicit legal integral
witness.  The bracket is valid for both radii but does not assert that they
are equal.

---

## 5. Endpoint KKT and the finite exceptional face

The common midpoint lattice sharply limits the coordinates at which a
continuous optimizer can be fractional.

For the component with `m` samples, the centered times are

\[
 t_j=\frac{2j+1-m}{10}.
 \tag{5.1}
\]

The largest component has `m=8900`, so every sample-time numerator is odd
and has absolute value at most `8899`.  For `r in H`, put

\[
 F_r(x)=(r,c(x))_{\mathbb R}.
 \tag{5.2}
\]

Then `F_r(10 theta)` is a real trigonometric polynomial in `theta` of degree
at most `8899`, containing only odd harmonics.  In particular,

\[
 F_r(x+10\pi)=-F_r(x).
 \tag{5.3}
\]

### Lemma 5.1 - a nonzero residual has a nonzero response polynomial

If `r` belongs to the linear span of the sampled exponential curve and
`r ne 0`, then `F_r` is not identically zero.

#### Proof

If `F_r(x)=0` for every `x`, then `r` is orthogonal to every `c(x)`, hence to
their linear span.  Since `r` lies in that span, `||r||^2=0`, a
contradiction.  \(\square\)

Every residual considered here lies in that span: `q`, the prefix columns,
and every absolutely convergent tail response do.

### Lemma 5.2 - one integer logarithm per zero phase

For a fixed phase modulo `10 pi`, at most one positive integer `k` has
`log k` in that phase.

#### Proof

If two distinct integers did, then

\[
 \frac{k_1}{k_2}=e^{10\pi m}
 \tag{5.4}
\]

for some nonzero integer `m`.  The left side is rational.  The right side is
a nonzero integer power of `e^pi` and is transcendental by the classical
Gelfond--Schneider theorem: if a nonzero integer power of `e^pi` were
algebraic, then `e^pi` would be algebraic over the algebraic numbers and hence
algebraic, a contradiction.  \(\square\)

### Theorem 5.3 - at most 8899 exceptional tail coordinates

Let `(alpha_*,xi_*)` solve the full continuous quotient problem, and let

\[
 r_*=q+C\alpha_*
 -\sum_{k>50}\xi_{*,k}\frac{c_k}{k^2}.
 \tag{5.5}
\]

Assume `delta_Q=||r_*||>0`.  Define

\[
 E(r_*)
 =\{k>50:F_{r_*}(\log k)=0\}.
 \tag{5.6}
\]

Then

\[
 \boxed{|E(r_*)|\le8899.}
 \tag{5.7}
\]

At every other coordinate,

\[
 \boxed{
 \xi_{*,k}
 =d_k\operatorname{sign}F_{r_*}(\log k).}
 \tag{5.8}
\]

Consequently the exposed tail face is the finite zonotope

\[
 \boxed{
 z_{\rm sat}(r_*)
 +\left\{
   \sum_{k\in E(r_*)}\xi_k\frac{c_k}{k^2}:
   |\xi_k|\le d_k
  \right\},}
 \tag{5.9}
\]

where

\[
 z_{\rm sat}(r_*)
 =\sum_{\substack{k>50\\k\notin E(r_*)}}
 d_k\operatorname{sign}F_{r_*}(\log k)\frac{c_k}{k^2}.
 \tag{5.10}
\]

#### Proof

The infinite-series KKT equality from Arithmetic Observability VIII applies
because of absolute convergence.  It gives (5.8) whenever the pairing is
nonzero, and permits the full interval only at a zero pairing.

By Lemma 5.1, `F_{r_*}` is a nonzero trigonometric polynomial.  A nonzero real
trigonometric polynomial of degree `8899` has at most `17798` zeros modulo
its full `20 pi` period, counting multiplicity.  Antiperiodicity pairs every
zero phase with its translate by `10 pi`, with no fixed phase.  There are
therefore at most `8899` distinct zero phases modulo `10 pi`.  Lemma 5.2
places at most one integer logarithm in each phase.  This proves (5.7), and
(5.9) is the standard exposed-face description obtained from the KKT signs.
\(\square\)

### Corollary 5.4 - exact finite integrality test at the projection

All continuous tail coefficients outside `E(r_*)` are already legal
integers.  Thus equality between the continuous quotient and the model with
real prefix but integral tails reduces to an integer feasibility problem in
at most `8899` exceptional coordinates.

For the original integral prefix-and-tail problem, Theorem 4.1 and Corollary
3.4 give the sharper exact condition

\[
 \delta_{\mathbb Z}=\delta_Q
 \quad\Longleftrightarrow\quad
 x_*\in\mathcal Z_{\mathbb Z},
 \tag{5.11}
\]

where `x_*` must be represented with zero nonquery prefix.  Equation (5.9)
turns this into a finite exceptional-face feasibility question once `r_*`
and `x_*` are known.

This corollary does **not** say that the exceptional feasibility problem has
a solution.  It identifies exactly where a continuous--integral gap can
remain.  Nor does it say that a nearest integral point lies in the exposed
face (5.9) when the arithmetic defect is positive.  That nearest point then
has, in general, a different residual normal.  The finite face is an exact
test for equality at the convex projection, not a search-space reduction for
an unknown positive-gap integral minimizer.

### 5.1 Classical facial lineage and the arithmetic specialization

Bang--bang endpoint descriptions, finite-dimensional facial reductions, and
extreme-lift sparsification belong to the classical lineage of Dubins,
Bolker, Starr, Cassels, and Artstein.  In particular, Artstein explicitly
relates discrete and continuous bang--bang problems, facial spaces, moment
constraints, and minimum-norm questions.  No general novelty is claimed for
those principles.

The programme-specific synthesis in Theorem 5.3 is narrower: the exact
odd-tenth sample lattice makes the residual response antiperiodic; its degree
bounds the zero phases; and Gelfond--Schneider makes the map from integer
logarithms to those phases injective.  Together they turn a general exposed
face into a finite arithmetic exceptional set of size at most `8899`.  This
paper makes no priority claim beyond that pinned synthesis.

---

## 6. Compact attainment and infinite-support fibres

Finite-support witnesses are reproducible and useful, but they cannot be
exact optimizers at positive distance.

### Lemma 6.1 - logarithms of integers are dense modulo every period

For every `T>0`, the sequence

\[
 \{\log k\bmod T:k\in\mathbb N\}
 \tag{6.1}
\]

is dense in `R/(T Z)`.  Every nonempty open phase interval contains
arbitrarily large integer logarithms.

#### Proof

Fix a representative `x in [0,T)`.  For every integer `m>=1`, let

\[
 k_m=\left\lceil e^{mT+x}\right\rceil.
 \tag{6.2}
\]

Then

\[
 0\le\log k_m-(mT+x)
 \le\log\left(1+e^{-(mT+x)}\right)
 \longrightarrow0.
 \tag{6.3}
\]

Thus `log k_m mod T` tends to `x`, and `k_m` tends to infinity.  \(\square\)

### Theorem 6.2 - compactness, attainment, and dense truncations

The sets `Z` and `Z_Z` are compact.  The bounded combined nuisance sets
`C_box` and `S_Z` are compact.  Hence both the continuous and independent-
integral distance problems attain their minima.

Moreover, finite-support tail responses are dense in both tail sets,
uniformly with remainder

\[
 \left\|
  \sum_{k>M}\xi_k\frac{c_k}{k^2}
 \right\|
 \le\sum_{k>M}\frac{d_k}{k^2}
 \longrightarrow0.
 \tag{6.4}
\]

#### Proof

Both coefficient products are compact in the product topology: one is a
product of compact intervals and the other a product of finite sets.  The
response map is the uniform limit of its finite coordinate sums by (1.7), so
it is continuous.  Its two images are therefore compact.  The prefix sets
are finite-dimensional compact or finite, and continuous addition preserves
compactness.  Truncating every coefficient after `M` proves (6.4) and the
density statement.  \(\square\)

For the integral envelope, the union of all finite-support selections is
countable and dense in `Z_Z`.  It is not closed when the positive-distance
optimizer has infinite support.  This is another reason not to call the
compact integer-selection image itself discrete.

### Theorem 6.3 - no positive-distance optimizer has finite tail support

Consider either the continuous coefficient box or the independent integral
coefficient envelope, with either a fixed prefix or any legal bounded prefix.
If the attained minimum distance is positive, no minimizing tail coefficient
sequence has finite support.

#### Proof

Suppose a finite-support candidate has residual `r ne 0`.  It is in the span
of the sampled exponential curve, so Lemma 5.1 makes `F_r` a nonzero
continuous periodic function.  Choose an open phase interval `I` and `c>0`
such that

\[
 |F_r(x)|\ge c
 \qquad(x\in I).
 \tag{6.5}
\]

By Lemma 6.1, there are arbitrarily large unused integers `k` with `log k` in
`I` modulo `20 pi`.

For the continuous model, increase the tail response at such a coordinate by

\[
 t\operatorname{sign}F_r(\log k)\frac{c_k}{k^2},
 \tag{6.6}
\]

where `0<t<=d_k` is sufficiently small.  The new squared residual minus the
old one is

\[
 -\frac{2t|F_r(\log k)|}{k^2}+\frac{t^2}{k^4}<0.
 \tag{6.7}
\]

For the integral model, take `t=1`, which is legal because `d_k>=1`.  For
large enough `k`,

\[
 -\frac{2|F_r(\log k)|}{k^2}+\frac1{k^4}
 \le-\frac{2c}{k^2}+\frac1{k^4}<0.
 \tag{6.8}
\]

Either perturbation keeps the prefix fixed and strictly lowers the distance,
contradicting minimality.  \(\square\)

### Corollary 6.4 - exact integral optimizers exist but are infinite

The pinned quotient lower bound is positive.  Therefore every exact
continuous optimizer and every exact independent-integral optimizer uses
infinitely many nonzero tail coefficients.  At the same time, Theorem 6.2
provides finite-support witnesses converging to each optimum.

This is not a failure of compactness.  It is a precise distinction between
attainment and finite certification: an exact primal certificate must either
describe an infinite sequence with a verified remainder or close the value
through convergent finite primal--dual gaps.

---

## 7. Discrete optimality geometry

Continuous KKT uses exact signs.  The independent integral envelope replaces
those signs by quantized one-coordinate inequalities and a global Voronoi
condition.

Let

\[
 r=q+Ap-\sum_{k>50}\xi_k\frac{c_k}{k^2}
 \tag{7.1}
\]

be an integral-feasible residual, and put

\[
 F_k=(r,c_k)_{\mathbb R}.
 \tag{7.2}
\]

### Proposition 7.1 - necessary tail-coordinate inequalities

At an integral optimum,

\[
 \begin{aligned}
 \xi_k<d_k
 &\Longrightarrow
 F_k\le\frac1{2k^2},\\
 \xi_k>-d_k
 &\Longrightarrow
 F_k\ge-\frac1{2k^2}.
 \end{aligned}
 \tag{7.3}
\]

In particular,

\[
 \boxed{
 \begin{aligned}
 F_k>\frac1{2k^2}
 &\Longrightarrow \xi_k=d_k,\\
 F_k<-\frac1{2k^2}
 &\Longrightarrow \xi_k=-d_k.
 \end{aligned}}
 \tag{7.4}
\]

If `-d_k<xi_k<d_k`, then

\[
 |F_k|\le\frac1{2k^2}.
 \tag{7.5}
\]

#### Proof

If increasing `xi_k` by one is legal, the residual changes from `r` to
`r-c_k/k^2`, and the squared-norm change is

\[
 -\frac{2F_k}{k^2}+\frac1{k^4}.
 \tag{7.6}
\]

It must be nonnegative at an optimum, which gives the first implication in
(7.3).  Decreasing `xi_k` by one changes the squared norm by

\[
 \frac{2F_k}{k^2}+\frac1{k^4},
 \tag{7.7}
\]

giving the second.  Equations (7.4)--(7.5) follow.  \(\square\)

The prefix coordinates have the reversed sign because `Ap` enters the
residual positively.  Whenever both unit prefix moves are legal, an integral
optimum must obey

\[
 |(r,c_j)_{\mathbb R}|\le\frac1{2j^2}.
 \tag{7.8}
\]

### Proposition 7.2 - exact global Voronoi condition

An integral-feasible pair `(p,xi)` is globally optimal if and only if, for
every other feasible pair represented by the perturbation `(Delta p,Delta
xi)`, one has

\[
 \boxed{
 2(r,A\Delta p-T\Delta\xi)_{\mathbb R}
 +\|A\Delta p-T\Delta\xi\|^2\ge0,}
 \tag{7.9}
\]

where

\[
 T\Delta\xi
 =\sum_{k>50}\Delta\xi_k\frac{c_k}{k^2}.
 \tag{7.10}
\]

#### Proof

The left side of (7.9) is exactly

\[
 \|r+A\Delta p-T\Delta\xi\|^2-\|r\|^2.
 \tag{7.11}
\]

Nonnegativity for every feasible competitor is therefore equivalent to
global minimality.  \(\square\)

The one-coordinate conditions are necessary but not sufficient: several
individually unfavorable moves can have negative cross terms and improve
jointly.  Equation (7.9), rather than coordinatewise local optimality, is the
exact discrete certificate target.

### 7.1 Confinement to alias-zero neighborhoods

Let `r` be an integral optimizer.  Outside any fixed open neighborhood of the
finitely many zero phases of `F_r`, continuity gives a positive minimum
`m_0` for `|F_r|`.  For

\[
 k>(2m_0)^{-1/2},
 \tag{7.12}
\]

Proposition 7.1 forces the endpoint

\[
 \xi_k=d_k\operatorname{sign}F_r(\log k).
 \tag{7.13}
\]

Thus any nonsaturated large integral coordinates are confined to shrinking
neighborhoods of at most `8899` alias phases.  Converting this qualitative
statement into an exact count would require Diophantine lower bounds for how
closely integer logarithms approach the unknown optimizer's zero phases.  No
such bound is claimed here.

---

## 8. The ten-mode alias is not optimal

Arithmetic Observability VIII supplied a legal ten-mode integral tail witness
for the `e_5` pair.  In its response convention, write

\[
 \Delta_{10}
 =\frac1{25}c_5
 +\sum_{k\in S_{10}}\frac{d_k}{k^2}c_k,
 \tag{8.1}
\]

where `S_10` is the exact factorized mode list frozen in
`arithmetic_observability_common_nuisance_certificate.json`.

Theorem 6.3 already proves, without numerical search, that this finite-support
witness cannot be an exact optimizer in either the continuous or the
independent integral envelope.  Two explicit descent directions make the
failure falsifiable.

### 8.1 Formally certified rank-11 integral improvement

The frozen candidate labelled rank 11 by the nonformal discovery search is

\[
 \begin{aligned}
 k_{11}
 &=220157529845760\\
 &=2^{12}\,3^3\,5\,13\,67\,331\,1381.
 \end{aligned}
 \tag{8.2}
\]

Its legal endpoint coefficient and normalized amplitude are

\[
 \begin{aligned}
 d_{14}(k_{11})
 &=1566233842432000,\\
 L_{11}
 :=\frac{d_{14}(k_{11})}{k_{11}^2}
 &=\frac{30590504735}{946666756792709085339648}\\
 &=3.231391037606529\ldots\times10^{-14}.
 \end{aligned}
 \tag{8.3}
\]

Appending this endpoint changes the squared response by the exact identity

\[
 \|\Delta_{10}+L_{11}c_{k_{11}}\|^2
 -\|\Delta_{10}\|^2
 =2L_{11}(\Delta_{10},c_{k_{11}})_{\mathbb R}
 +L_{11}^2.
 \tag{8.4}
\]

The companion artifact's 512-bit Arb reconstruction proves the directed
enclosures summarized by

\[
 \begin{aligned}
 \log(k_{11}/5)-10\pi
 &=2.4645982174299567411\ldots\times10^{-9},\\
 (\Delta_{10},c_{k_{11}})_{\mathbb R}
 &=-0.03999999999555552607730057060\ldots,\\
 2L_{11}(\Delta_{10},c_{k_{11}})_{\mathbb R}+L_{11}^2
 &=-2.58511282979694247677\ldots\times10^{-15}.
 \end{aligned}
 \tag{8.5}
\]

The resulting directed critical-radius enclosure has outward upper endpoint

\[
 0.0199999999977660012499708079640\ldots,
 \tag{8.6}
\]

an improvement of approximately

\[
 1.6156955188029095\times10^{-14}
 \tag{8.7}
\]

over the ten-mode radius.

**Formal status.**  Equations (8.2)--(8.4) are exact arithmetic identities.
The AO-X artifact certifies directed 512-bit intervals for every phase and
kernel entering (8.5), an interval for the full eleven-mode response computed
independently of the update identity, and strict overlap of the two routes.
It proves that the squared distance decreases by more than
`2.58511282979694247677e-15`, that the critical radius decreases by more than
`1.61569551880290951845e-14`, and that the outward upper endpoint in (8.6) is
valid.  Thus the formal global upper endpoint is now the eleven-mode value.
No claim of global optimality follows.

### 8.2 Formally certified one-coordinate quotient profiling

The ten-mode residual is not even stationary under the real nuisance
subspace.  The companion artifact certifies

\[
 h_7:=(\Delta_{10},c_7)_{\mathbb R}
 =-9.1622874804903325428\ldots\times10^{-10}.
 \tag{8.8}
\]

Since `||c_7||=1`, choosing the real nuisance response

\[
 w=-h_7c_7\in W
 \tag{8.9}
\]

gives the exact identity

\[
 \|\Delta_{10}+w\|^2
 =\|\Delta_{10}\|^2-h_7^2
 <\|\Delta_{10}\|^2.
 \tag{8.10}
\]

The corresponding directed profiled critical-radius enclosure is summarized by

\[
 0.0199999999977821529584393442805\ldots.
 \tag{8.11}
\]

This profiling statement concerns the real quotient; its prefix coefficient
is

\[
 p_7=-49h_7
 =4.48952086544026294598\ldots\times10^{-8},
 \tag{8.12}
\]

and is not integral.  The companion artifact formally certifies the directed
intervals in (8.8), (8.11), and (8.12), together with the exact norm identity
(8.10).  This establishes a legal continuous-prefix descent only; it does not
establish a legal integral-prefix improvement.  The qualitative
finite-support nonoptimality already follows from Theorem 6.3.

---

## 9. Alias-circle reconstruction of an endpoint tail

Arithmetic Observability IX used the alias circle to evaluate scalar support
moments.  The same moment lattice can reconstruct a polynomial approximation
to the endpoint tail vector required by KKT.

Choose the plus-exponent convention and write the sample-time harmonics as
odd integers `ell`.  A complex sample coordinate of `c(x)` is then, up to
its fixed positive square-root weight,

\[
 e^{i\ell x/10}.
 \tag{9.1}
\]

Using the conjugate column convention conjugates both sides of every formula
below and does not change the norm bounds.

Let

\[
 S(x)=\sum_{\substack{|r|\le R\\r\ \mathrm{odd}}}
 s_re^{irx/10}
 \tag{9.2}
\]

be an antiperiodic trigonometric polynomial intended to approximate
`sign F_u(x)`, with `sign(0)=0`; the zero-pair coordinates are handled
separately by `z_E`.  Recall

\[
 D_{M,14}(s)
 =\sum_{k>M}\frac{d_{14}(k)}{k^s}.
 \tag{9.3}
\]

### Theorem 9.1 - endpoint-vector moment transport

At the sample harmonic `ell`,

\[
 \boxed{
 \begin{aligned}
 &\sum_{k>M}\frac{d_{14}(k)}{k^2}
 S(\log k)e^{i\ell\log k/10}\\
 &\qquad=
 \sum_{\substack{|r|\le R\\r\ \mathrm{odd}}}
 s_rD_{M,14}
 \left(2-\frac{i(\ell+r)}{10}\right).
 \end{aligned}}
 \tag{9.4}
\]

Because `ell+r` is even, every Dirichlet value on the right lies on the
already established lattice

\[
 2-\frac{im}{5},
 \qquad m\in\mathbb Z.
 \tag{9.5}
\]

If a nonnegative trigonometric majorant `E` satisfies

\[
 E(x)\ge
 |\operatorname{sign}F_u(x)-S(x)|,
 \tag{9.6}
\]

then the norm error between the exact endpoint tail and the vector computed
from (9.4) is at most

\[
 \sum_{k>M}\frac{d_{14}(k)}{k^2}E(\log k).
 \tag{9.7}
\]

#### Proof

Insert (9.2), interchange the finite polynomial sum with the absolutely
convergent arithmetic sum, and combine exponents.  Since `ell` and `r` are
odd, `(ell+r)/2` is an integer, giving (9.4)--(9.5).  For the error, use
`||c(log k)||=1`, the triangle inequality, and (9.6).  \(\square\)

The discontinuity of `sign F_u` at its finitely many zeros prevents uniform
polynomial approximation on the whole circle.  A rigorous implementation can
instead:

1. isolate small cells around every certified zero crossing;
2. approximate the constant signs on the complementary arcs;
3. use positive fine-bin mass bounds on the exceptional cells; and
4. evaluate the polynomial part through (9.4).

This produces a falsifiable fixed-point route for

\[
 r=Q\left(q-z_{\rm sat}(r)-z_E\right),
 \tag{9.8}
\]

with the finite exceptional zonotope `z_E` from Theorem 5.3.  No solution of
(9.8) is claimed in this paper.

---

## 10. Formal certificate boundary

The companion package is

```text
arithmetic_observability_convexification_gap.py
arithmetic_observability_convexification_gap_certificate.json
test_arithmetic_observability_convexification_gap.py
```

with schema

```text
arithmetic-observability-convexification-gap-v1
```

Its canonical theorem payload has SHA-256 binding

```text
fec0b1e43893794839afb4503975ba4f51b0c9c9980e1e43b38710a690e7348c
```

The immutable file hashes are

```text
verifier  b98336ed3ff5ea9e9a15e876893a62ff5ba00a0b3ba9268202676535cadd8379
artifact  19e0d5fd20674e7191c6de75ced760cc663e3b1cafdc57ad8cd193b2465f11eb
tests     297e6de872100fe07c1d3184bdceb460684799a8664f45a7ee48d8152815fb0e
```

The checker binds the AO-VIII and AO-IX source artifacts and verifies:

1. the exact inputs `q_G`, `q_5`, and `tau_W`;
2. the reduced fractions in (3.6)--(3.7) and the strict comparison
   `2500 L_W<1`;
3. the inherited exact quotient lower and ten-mode witness;
4. the eleven-mode upper endpoint and the exact localization bounds
   (4.13)--(4.15);
5. the rank-11 factorization, primality of its displayed factors, and
   `d_14(k_11)`;
6. the exact amplitude in (8.3);
7. directed Arb intervals for the phase, kernels, inner product, squared
   decrement, and improved radius in (8.5)--(8.7);
8. the `c_7` inner-product interval and profiled norm identity; and
9. canonical serialization, dependency hashes, verifier hash, and adversarial
   rejection tests.

The frozen payload passes reconstruction, including a byte-identical external
artifact rebuild, and all `29` focused hostile tests.  The broader
arithmetic-observability discovery run passes `281` tests with one explicitly
opt-in AO-IX full-rebuild test skipped.  These checks formalize the stated
outward bounds, not an exact quotient optimizer or a zero convexification gap.

The exact local reproduction commands are

```text
python arithmetic_observability_convexification_gap.py \
  --certificate arithmetic_observability_convexification_gap_certificate.json
python -m unittest -q test_arithmetic_observability_convexification_gap.py
python -m unittest discover -s . -p 'test_arithmetic_observability*.py'
```

### 10.1 Suggested primal--dual optimizer certificate

A later exact quotient computation need not store an exact transcendental
orthogonal vector.  Given a candidate sample vector `s`, define the exact
projection

\[
 u=Qs=s-CB^{-1}C^{\mathsf T}s.
 \tag{10.1}
\]

An interval linear-solve certificate can enclose `B^{-1}C^T s`; the support
correction is bounded with the already formal per-column `tau_j`.  The
squared dual avoids exact normalization.  A complete optimizer certificate
should contain:

- the candidate primal coefficient rule or finite witness;
- an exact definition of its projected residual;
- interval Gram solves and norm bounds;
- finite support sums and an alias-circle remote support bound;
- every complementarity slack in (2.20); and
- exact outward lower, upper, and gap endpoints.

Equality should be claimed only when the gap is proved zero.  A small positive
gap is a quantitative approximation, not an exact optimizer theorem.

---

## 11. Proved, formally computed, and open

### Proved in this manuscript

- the exact finite Schur-complement quotient QP, squared dual, KKT system,
  and remote-aware gap identity;
- the direction-specific truncation bracket;
- the uniform fixed-tail prefix bound `||p||_infinity<0.049079`;
- equality of the unbounded quotient, the bounded continuous-prefix value,
  and the distance to `conv(S_Z)`;
- the Pythagorean arithmetic-defect inequalities and their exact equality
  condition;
- the endpoint KKT description with at most `8899` exceptional integral-log
  phases;
- compact attainment and density of finite truncations in both envelope
  models;
- nonattainment by every finite-support tail at positive distance;
- the discrete one-coordinate inequalities and exact global Voronoi
  condition; and
- the endpoint-vector Dirichlet-moment identity.

### Formally certified in the companion package

- the rank-11 strict integral improvement and its eleven-mode radius endpoint;
- the explicit `c_7` real quotient profiling improvement;
- the updated exact global bracket for both the continuous box and independent
  integral envelope radii; and
- the exact observation-space localization (4.14) and its directed square-root
  enclosure (4.15).

### Not established

- the exact quotient-zonoid value;
- an exact primal or dual quotient optimizer;
- the arithmetic defect `eta_arith`;
- equality of the closest continuous and independent-integral fibres;
- the exact closest integral prefix and tail sequence;
- realization of any envelope optimizer by a number field;
- global optimality of the pinned time ensemble or window; or
- any statement about zeta zeros, the Riemann hypothesis, or physical law.

---

## 12. Classical foundations and priority boundary

The general tools used here are classical.  Metric projection and proximity
maps for convex sets go back at least to Cheney and Goldstein.  The relevant
extreme-point, zonoid, nonconvex-sum, and bang--bang lineage includes:

1. E. W. Cheney and A. A. Goldstein, *Proximity maps for convex sets*,
   Proceedings of the American Mathematical Society 10 (1959),
   DOI `10.1090/S0002-9939-1959-0105008-8`.
2. L. E. Dubins, *On extreme points of convex sets*, Journal of Mathematical
   Analysis and Applications 5 (1962),
   DOI `10.1016/S0022-247X(62)80007-9`.
3. E. D. Bolker, *A class of convex bodies*, Transactions of the American
   Mathematical Society 145 (1969),
   DOI `10.1090/S0002-9947-1969-0256265-X`.
4. R. M. Starr, *Quasi-equilibria in markets with non-convex preferences*,
   Econometrica 37 (1969), DOI `10.2307/1909201`.
5. J. W. S. Cassels, *Measures of the non-convexity of sets and the
   Shapley--Folkman--Starr theorem*, Mathematical Proceedings of the
   Cambridge Philosophical Society (1975),
   DOI `10.1017/S0305004100051884`.
6. Z. Artstein, *Discrete and continuous bang-bang and facial spaces, or:
   Look for the extreme points*, SIAM Review 22 (1980),
   DOI `10.1137/1022026`.

The phase-injectivity step uses the Gelfond--Schneider transcendence theorem;
the original 1934 work of Gelfond is indexed by MathNet as `im4924`, and
Schneider's 1935 paper has DOI `10.1515/crll.1935.172.65`.

No novelty is claimed for metric projection, exposed faces or zonoids,
compact product boxes, Caratheodory's theorem, product-measure barycenters,
or finite-dimensional extreme-lift sparsification.  The arithmetic
contribution is their exact composition with the odd-tenth alias circle,
dense integer-log phases, the trigonometric zero bound, the
Gelfond--Schneider injection, the common coefficient box, and independently
reproducible Mellin-tail certificates.  No broad priority claim is made for
that synthesis.

---

## 13. Conclusion

The quotient distance is now understood as an exact convexification, not an
unstructured relaxation.  Its failure to determine the integral answer is
measured by one geometric number: the distance from the convex projection to
the integral nuisance response set.  The sampled exponential frame then
confines every continuous fractional ambiguity to at most `8899` tail
coordinates, while a complementary theorem shows that every positive-
distance optimizer nevertheless has infinite support.

These facts change the reconstruction target.  Searching for a finite exact
alias is provably futile.  A successful next certificate must instead combine
an infinite endpoint rule, a finite exceptional face, and a vanishing
primal--dual remainder.  The theory specifies exactly what would prove
continuous--integral equality, exactly what would refute it, and exactly which
claims remain outside the independent coefficient-envelope model.
