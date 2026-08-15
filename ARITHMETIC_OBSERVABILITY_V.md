# Arithmetic Observability V

## Sharp global complexity and acquisition chambers

**Research manuscript — 15 August 2026**

### Status

The analytic results in Sections 2--5 are proved.  They turn the positive
global count left open in Arithmetic Observability IV into an exact theorem.
Section 6 gives a rational three-reading schedule for the canonical prime
box and explicit stability constants.  Section 7 separates an open chamber
of globally injective schedules from an open chamber carrying exact
reciprocal collisions.  Their finite phase and parameterized-Krawczyk inputs
are independently enclosed by the accompanying 384-bit Arb certificate,
strict machine-readable artifact, and adversarial tests.

The paper concerns a finite harmonic model.  It makes no assertion about an
infinite Euler product, the Riemann hypothesis, or a physical model of the
universe.

---

## Abstract

Let

\[
 Q_s(z)=1+z+\cdots+z^{s-1},
 \qquad
 f_{C,u}(t)=C\prod_{j=1}^rQ_s(u_jp_j^{-it}),
\]

where the primes are known, the shape parameters `u_j` and the free scale
`C` are positive, and one reading is one complex value of `f`.  Arithmetic
Observability IV proved that fewer than `r` readings always admit exact
positive collisions, but left a large gap between that lower bound and full
coefficient interpolation.

This paper closes the gap:

\[
 \boxed{m_{\mathrm{glob},+}=r.}
\]

The proof compactifies each positive coordinate by
`y_j=u_j/(1+u_j)` and uses the continuously lifted phase of a homogenized
geometric polynomial.  Inside a root-free phase sector, its derivative has
an exact positive pair-sum formula.  Kronecker approximation then constructs
`r` readings whose prime-phase matrix is nearly diagonal.  The resulting
phase Jacobian is uniformly strictly diagonally dominant on the entire
closed cube `[0,1]^r`.  Integrating the Jacobian along line segments proves
global injectivity of the compactified phase shape, including its boundary
limits.  The unhomogenized raw amplitudes need not remain finite at the
`u_j=infinity` faces.  A phase-oscillation bound removes the possible
ambiguity modulo `2 pi`, after which any nonzero interior reading recovers
the positive scale.

The argument is quantitative.  It induces a distinguishability geometry on
the compact `y`-cube with a global inverse-Lipschitz modulus in the torus of
reading phases.  For `r=3`, `s=4`, and primes `(2,3,5)`, the rational schedule

\[
 T_*=(245.943,281.062,960.832)
\]

lies in an explicitly described globally injective chamber.  Its torus
phase map separates two shapes by more than `6/25` of their `l_infinity`
distance in `y`; unit phasors separate them by more than `3/20`, and the raw
readings obey a scale-aware lower bound greater than `2/15`.

The same acquisition space also contains a robust collision chamber near
`(1,2,3)`, obtained from a parameterized interval Krawczyk argument around a
reciprocal collision.  Thus the sharp reading *count* is universal while
global success remains a property of the schedule.  Finally, exact recovery
does not provide a uniform inverse in the uncompactified variables
`x_j=log u_j`: fixed log-distance pairs can approach the same boundary data.

---

## 1. Model, complexity, and observation geometry

Fix integers

\[
 r\ge1,
 \qquad
 s\ge2,
 \qquad
 d=s-1,
 \tag{1.1}
\]

and distinct primes `p_1,...,p_r`.  Write

\[
 \lambda_j=\log p_j,
 \qquad
 Q_s(z)=\sum_{a=0}^d z^a.
 \tag{1.2}
\]

For `u in R_{>0}^r` and `C>0`, define

\[
 A_u(t)=\prod_{j=1}^rQ_s(u_je^{-i\lambda_jt}),
 \qquad
 f_{C,u}(t)=C A_u(t).
 \tag{1.3}
\]

A schedule `T=(t_1,...,t_m)` gives the observation map

\[
 \mathcal F_T(C,u)
 =\bigl(f_{C,u}(t_1),\ldots,f_{C,u}(t_m)\bigr)
 \in\mathbb C^m.
 \tag{1.4}
\]

All primes and the integer `s` are known and labelled.  The unknowns are the
positive scale and positive shape parameters.  The coefficient tensor

\[
 c_\alpha=C\prod_{j=1}^ru_j^{\alpha_j},
 \qquad
 \alpha\in\{0,\ldots,d\}^r,
 \tag{1.5}
\]

determines `(C,u)` uniquely because `C=c_0` and
`u_j=c_{e_j}/c_0`.  Hence every collision discussed below represents two
different coefficient tensors.

### Definition 1.1 — positive global reading complexity

Let `m_glob,+` be the least integer `m` for which there exists a real
schedule of `m` individual readings such that `F_T` is globally injective on

\[
 \Theta_+=\mathbb R_{>0}\times\mathbb R_{>0}^r.
 \tag{1.6}
\]

The schedule is part of the design.  Thus the statement
`m_glob,+=r` means that some `r`-reading schedules work and no schedule with
fewer readings can work.  It does not say that every `r`-reading schedule is
injective.

### Definition 1.2 — compactified shape and phase observations

Use the coordinatewise compactification

\[
 y_j=\frac{u_j}{1+u_j}\in(0,1),
 \qquad
 u_j=\frac{y_j}{1-y_j}.
 \tag{1.7}
\]

For a nonzero complex number `z`, put `phase(z)=z/|z|`.  Whenever every
scheduled factor is nonzero, the scale-free phase observation is

\[
 \mathcal U_T(u)
 =\left(\frac{A_u(t_1)}{|A_u(t_1)|},\ldots,
        \frac{A_u(t_m)}{|A_u(t_m)|}\right)
 \in\mathbb T^m.
 \tag{1.8}
\]

For angles modulo `2 pi`, let

\[
 \operatorname{dist}_{\mathbb T}(a,b)
 =\min_{k\in\mathbb Z}|a-b-2\pi k|,
 \tag{1.9}
\]

and use the maximum of the coordinate distances on `T^m`.

The compact coordinate `y` is not cosmetic.  It is the coordinate in which
the phase response has nondegenerate limits at both `u=0` and `u=infinity`.
Section 8 proves that the log coordinate `x=log u` cannot support a uniform
global inverse bound.

---

## 2. The one-axis phase kernel

The central object is the homogenized geometric polynomial

\[
 P_s(y,\theta)
 =(1-y)^dQ_s\!\left(\frac{y}{1-y}e^{-i\theta}\right)
 =\sum_{a=0}^d y^a(1-y)^{d-a}e^{-ia\theta}.
 \tag{2.1}
\]

For `0<=y<1`, the multiplier `(1-y)^d` is positive, so `P_s` and
`Q_s(u e^{-i theta})` have the same phase.  Formula (2.1) also extends to the
two compactification faces:

\[
 P_s(0,\theta)=1,
 \qquad
 P_s(1,\theta)=e^{-id\theta}.
 \tag{2.2}
\]

### Lemma 2.1 — root-free phase sector

If

\[
 |\theta|<\frac{\pi}{d},
 \tag{2.3}
\]

then `P_s(y,theta)` is nonzero for every `0<=y<=1`.

#### Proof

For positive `theta`, the monomials in (2.1) have arguments
`0,-theta,...,-d theta`, contained in a sector of width strictly less than
`pi`.  A positive combination of vectors in such a sector cannot vanish.
The negative case is its complex conjugate, and `theta=0` is positive real.
The endpoint values are nonzero by (2.2).  \(\square\)

On this sector choose the unique continuous phase lift

\[
 \phi_s(y,\theta)=\arg P_s(y,\theta),
 \qquad
 \phi_s(0,\theta)=0.
 \tag{2.4}
\]

### Theorem 2.2 — exact phase-derivative identity

For `0<theta<pi/d`,

\[
 -\partial_y\phi_s(y,\theta)
 =\frac{1}{|P_s(y,\theta)|^2}
 \sum_{0\le b<a\le d}
 (a-b)y^{a+b-1}(1-y)^{2d-a-b-1}
 \sin\bigl((a-b)\theta\bigr).
 \tag{2.5}
\]

Every exponent in (2.5) is a nonnegative integer.  The right-hand side is
strictly positive throughout the closed interval and extends at both
endpoints as

\[
 -\partial_y\phi_s(0,\theta)
 =-\partial_y\phi_s(1,\theta)
 =\sin\theta.
 \tag{2.6}
\]

For negative `theta`, conjugation reverses the sign of the derivative.

#### Proof

First work with `u=e^x`.  Since

\[
 u e^{-i\theta}Q_s'(u e^{-i\theta})
 =\sum_{a=0}^d a u^ae^{-ia\theta},
\]

differentiation of the phase gives

\[
 \partial_x\arg Q_s(u e^{-i\theta})
 =\frac{\Im\left[
    \left(\sum_a a u^ae^{-ia\theta}\right)
    \left(\sum_b u^be^{ib\theta}\right)
   \right]}{|Q_s(u e^{-i\theta})|^2}.
 \tag{2.7}
\]

Pair the summand indexed by `(a,b)` with `(b,a)`.  When `a>b`, their
combined imaginary part is

\[
 -(a-b)u^{a+b}\sin((a-b)\theta).
 \tag{2.8}
\]

Now `dx/dy=1/[y(1-y)]`, and

\[
 Q_s(u e^{-i\theta})=(1-y)^{-d}P_s(y,\theta).
\]

Substitution into (2.7) gives (2.5).  Because
`1<=a-b<=d`, condition (2.3) makes every sine in (2.5) positive.  At `y=0`
only `(a,b)=(1,0)` survives; at `y=1` only `(d,d-1)` survives.  This proves
(2.6) and continuity on the compact interval.  \(\square\)

### Corollary 2.3 — monotonicity and exact oscillation

For `0<|theta|<pi/d`, the map `y -> phi_s(y,theta)` is strictly monotone and

\[
 \phi_s(1,\theta)-\phi_s(0,\theta)=-d\theta.
 \tag{2.9}
\]

In particular its total oscillation is exactly `d|theta|`.

#### Proof

The derivative sign follows from Theorem 2.2.  The sector in Lemma 2.1
contains the whole curve and prevents an additional winding by `2 pi`.
Equation (2.2) then gives the endpoint lift `-d theta`.  \(\square\)

---

## 3. Phase-separated schedules

For a schedule `T=(t_1,...,t_r)`, choose integers `n_{ell j}` and reduced
phases

\[
 \theta_{\ell j}
 =\lambda_jt_\ell-2\pi n_{\ell j}.
 \tag{3.1}
\]

The lifted phase map on the compact cube is

\[
 \Phi_{T,\ell}(y)
 =\sum_{j=1}^r\phi_s(y_j,\theta_{\ell j}),
 \qquad 1\le\ell\le r.
 \tag{3.2}
\]

Modulo `2 pi`, this is precisely the phase of the `ell`-th reading.

### Definition 3.1 — a phase-separated box

Fix

\[
 0<\alpha\le\beta<\frac{\pi}{d}
 \tag{3.3}
\]

and a positive `delta` satisfying

\[
 0<\delta<\frac{\pi}{d}.
 \tag{3.4}
\]

A reduced phase matrix is `(alpha,beta,delta)`-separated if

\[
 \theta_{\ell\ell}\in[\alpha,\beta],
 \qquad
 |\theta_{\ell j}|\le\delta\quad(j\ne\ell).
 \tag{3.5}
\]

Define the compact derivative bounds

\[
 c(\alpha,\beta)
 =\min_{\substack{0\le y\le1\\
                    \alpha\le\theta\le\beta}}
   \bigl(-\partial_y\phi_s(y,\theta)\bigr)>0,
 \tag{3.6}
\]

and

\[
 \varepsilon(\delta)
 =\max_{\substack{0\le y\le1\\|\theta|\le\delta}}
   |\partial_y\phi_s(y,\theta)|.
 \tag{3.7}
\]

Joint continuity on the root-free compact set implies

\[
 \varepsilon(\delta)\longrightarrow0
 \quad\text{as}\quad\delta\longrightarrow0.
 \tag{3.8}
\]

### Theorem 3.2 — quantitative global phase separation

Suppose an `(alpha,beta,delta)`-separated schedule satisfies

\[
 \kappa
 :=c(\alpha,\beta)-(r-1)\varepsilon(\delta)>0
 \tag{3.9}
\]

and

\[
 W:=d\bigl(\beta+(r-1)\delta\bigr)<2\pi.
 \tag{3.10}
\]

Then `Phi_T` is globally injective on `[0,1]^r`, and

\[
 \|\Phi_T(y)-\Phi_T(y')\|_\infty
 \ge\kappa\|y-y'\|_\infty.
 \tag{3.11}
\]

Moreover, for the phase observations on the torus,

\[
 d_{\mathbb T,\infty}
 \bigl(\mathcal U_T(y),\mathcal U_T(y')\bigr)
 \ge\eta\|y-y'\|_\infty,
 \tag{3.12}
\]

where

\[
 \eta=\min\{\kappa,2\pi-W\}>0.
 \tag{3.13}
\]

Consequently the positive free-scale observation map `F_T` is globally
injective.

#### Proof

Let `h=y-y'`.  Along the segment `y'+tau h`, define

\[
 A=\int_0^1[-D\Phi_T(y'+\tau h)]\,d\tau.
 \tag{3.14}
\]

Every diagonal entry of `A` is at least `c(alpha,beta)`, while the sum of the
absolute values of the off-diagonal entries in each row is at most
`(r-1)epsilon(delta)`.  Thus `A` is strictly row diagonally dominant.
Choose an index `i` for which `|h_i|=||h||_infinity`.  Then

\[
 \begin{aligned}
 \|\Phi_T(y)-\Phi_T(y')\|_\infty
 &=\|Ah\|_\infty\\
 &\ge |(Ah)_i|\\
 &\ge\bigl(c(\alpha,\beta)-(r-1)\varepsilon(\delta)\bigr)
       \|h\|_\infty,
 \end{aligned}
 \tag{3.15}
\]

which proves (3.11) and injectivity of the lift.

By Corollary 2.3, the oscillation of row `ell` is at most

\[
 d\sum_{j=1}^r|\theta_{\ell j}|
 \le d\bigl(\beta+(r-1)\delta\bigr)=W.
 \tag{3.16}
\]

For a lifted difference `q` with `|q|<=W<2 pi`, its circular distance is at
least `min{|q|,2 pi-W}`.  Since `||h||_infinity<=1`, equations (3.11) and
(3.16) give (3.12)--(3.13).

If two positive models have the same raw observations, their positive
scales do not change the reading phases, so (3.12) forces `y=y'` and hence
`u=u'`.  Every scheduled factor is nonzero by Lemma 2.1.  Any one equality
`C A_u(t_l)=C' A_u(t_l)` now gives `C=C'`.  \(\square\)

### Remark 3.3 — elementary global univalence

No local-to-global continuation assumption is hidden in Theorem 3.2.  The
average of the Jacobians along the chord between two arbitrary points is
itself strictly diagonally dominant.  Its nonsingularity rules out that
entire secant directly.  One may view this as a particularly transparent
instance of the Gale--Nikaido global-univalence theorem: positive diagonal
and strict row diagonal dominance make every principal minor of
`-D Phi_T` positive, hence make it a P-matrix.  The direct chord proof is
retained because it also gives the quantitative constant `kappa`; its matrix
estimate is the same strict-diagonal-dominance mechanism underlying Varah's
classical inverse bound.

---

## 4. Kronecker design and the exact global count

The prime logarithms are rationally independent.  Indeed, if

\[
 \sum_{j=1}^r k_j\log p_j=0
 \qquad(k_j\in\mathbb Z),
 \tag{4.1}
\]

then exponentiation gives `product_j p_j^{k_j}=1`, so unique factorization
forces every `k_j=0`.

The continuous Kronecker theorem therefore says that

\[
 \bigl\{t(\lambda_1,\ldots,\lambda_r)\bmod2\pi:t\in\mathbb R\bigr\}
 \tag{4.2}
\]

is dense in `T^r`.  The positive half-orbit has the same closure, so every
open phase box is visited at arbitrarily large positive times.  This is the
finite-prime Bohr--Kronecker flow familiar from Dirichlet-series theory.

### Theorem 4.1 — existence of a globally injective `r`-reading schedule

For every `r>=1`, `s>=2`, and every set of distinct primes, there are
distinct positive nonzero times `t_1,...,t_r` for which `F_T` is globally
injective on `Theta_+`.

#### Proof

Choose any `a` with `0<a<pi/d`.  At `delta=0`, Theorem 2.2 and compactness
give

\[
 \min_{0\le y\le1}
 \bigl(-\partial_y\phi_s(y,a)\bigr)>0.
 \tag{4.3}
\]

For sufficiently small positive `delta`, with
`delta<min{a,pi/d-a}`, continuity gives both

\[
 c(a-\delta,a+\delta)>(r-1)\varepsilon(\delta)
 \tag{4.4}
\]

and `d(a+r delta)<2 pi`.  For row `ell`, ask the Kronecker orbit to enter the
open box centered at `a e_ell` whose coordinate radii are smaller than
`delta`.  Do this successively for `ell=1,...,r`, choosing each positive
visit later than every visit already selected; every box is revisited
arbitrarily late.  The resulting times are distinct and their phase matrix
satisfies Theorem 3.2 with
`alpha=a-delta` and `beta=a+delta`.
\(\square\)

The construction is existential but effective: simultaneous Diophantine
search finds candidate visits, and interval arithmetic certifies the finite
phase inequalities.  Section 6 carries this out with exact rational times.

Only the homogenized phase shape extends continuously to every point of the
closed `y`-cube.  The raw factor `Q_s(u e^{-i theta})` normally grows like
`u^d` at the `y=1` face.  The actual raw observation theorem is asserted on
the open positive parameter space; the closed cube is used to control its
phase and all possible escaping shape sequences.

### Theorem 4.2 — sharp positive global complexity

For every prime box and every `s>=2`,

\[
 \boxed{m_{\mathrm{glob},+}=r.}
 \tag{4.5}
\]

This includes `r=1`, where a single suitably phased complex reading recovers
the one shape coordinate from its strictly monotone phase and then recovers
the scale from its magnitude.

#### Proof

Theorem 4.1 proves the upper bound.  For completeness, the matching lower
bound is recalled next.

Write `u_j=e^{x_j}`, `S(x)=sum_j x_j`, and define

\[
 H_s(x,\theta)
 =e^{-d(x-i\theta)/2}Q_s(e^{x-i\theta}),
 \qquad
 B_x(t)=\prod_{j=1}^rH_s(x_j,\lambda_jt).
 \tag{4.6}
\]

Reversing the summation index in `Q_s` gives

\[
 B_{-x}(t)=\overline{B_x(t)}.
 \tag{4.7}
\]

For any schedule of `m<=r-1` readings, the map

\[
 x\longmapsto
 \bigl(\Im B_x(t_1),\ldots,\Im B_x(t_m)\bigr)
 \tag{4.8}
\]

is continuous and odd on every sphere `S^{r-1}` in `R^r`.  Borsuk--Ulam
produces a nonzero `x` for which all components vanish.  At that `x`, the
two distinct positive points

\[
 \left(Ae^{-dS(x)/2},e^x\right)
 \quad\text{and}\quad
 \left(Ae^{dS(x)/2},e^{-x}\right)
 \tag{4.9}
\]

give identical readings.  Hence no schedule with fewer than `r` readings is
globally injective.  For `r=1`, zero readings plainly cannot identify two
positive parameters, while Theorem 4.1 supplies one reading.  \(\square\)

### Corollary 4.3 — count versus design

The integer `r` is the optimal acquisition count, but it is not a guarantee
for a particular schedule.  For example, every `r`-reading schedule
containing `t=0` still has a reciprocal collision: the time-zero component
of (4.8) vanishes identically, leaving only `r-1` odd equations.  Sections 6
and 7 exhibit robust good and bad regions among nonzero schedules as well.

---

## 5. Distinguishability geometry

The proof supplies more than exact injectivity.  It equips the compactified
shape cube with an observation-induced metric.

### Theorem 5.1 — global phase inverse modulus

Under the hypotheses of Theorem 3.2,

\[
 d_{\mathbb T,\infty}
 \bigl(\mathcal U_T(u),\mathcal U_T(u')\bigr)
 \ge\eta
 \left\|
 \frac{u}{1+u}-\frac{u'}{1+u'}
 \right\|_\infty,
 \tag{5.1}
\]

with `eta` given by (3.13).  Thus the pullback of the torus metric dominates
the ordinary maximum metric on the closed `y`-cube.

The unit-circle chord and circular distance satisfy

\[
 |e^{ia}-e^{ib}|
 =2\sin\!\left(\frac{\operatorname{dist}_{\mathbb T}(a,b)}2\right)
 \ge\frac2\pi\operatorname{dist}_{\mathbb T}(a,b).
 \tag{5.2}
\]

Consequently,

\[
 \|\mathcal U_T(u)-\mathcal U_T(u')\|_\infty
 \ge\frac{2\eta}{\pi}
 \left\|
 \frac{u}{1+u}-\frac{u'}{1+u'}
 \right\|_\infty.
 \tag{5.3}
\]

This is a global, not merely differential, stability statement.

### Proposition 5.2 — a scale-aware raw-reading bound

Suppose additionally that

\[
 |A_u(t_\ell)|\ge q_*>0
 \quad\text{for every }u>0\text{ and every }\ell.
 \tag{5.4}
\]

Then for arbitrary `C,C'>0`,

\[
 \|\mathcal F_T(C,u)-\mathcal F_T(C',u')\|_\infty
 \ge \frac{2q_*\eta}{\pi}
       \min\{C,C'\}
 \left\|
 \frac{u}{1+u}-\frac{u'}{1+u'}
 \right\|_\infty.
 \tag{5.5}
\]

#### Proof

For nonzero complex numbers `z,w`,

\[
 |z-w|^2=(|z|-|w|)^2
 +|z||w|\left|\frac z{|z|}-\frac w{|w|}\right|^2,
 \tag{5.6}
\]

so

\[
 |z-w|\ge\min\{|z|,|w|\}
 \left|\frac z{|z|}-\frac w{|w|}\right|.
 \tag{5.7}
\]

Apply this in the coordinate selected by (5.3), noting that the two raw
magnitudes are at least `C q_*` and `C' q_*`.  \(\square\)

The factor `min(C,C')` cannot be removed from an absolute-noise statement:
the entire raw observation vector tends to zero with the free scale.  Unit
phasors or relative noise are the natural scale-free data.

### Definition 5.3 — the induced arithmetic observation metric

For a phase-separated schedule, define

\[
 d_T^{\mathrm{phase}}(u,u')
 =d_{\mathbb T,\infty}
   \bigl(\mathcal U_T(u),\mathcal U_T(u')\bigr).
 \tag{5.8}
\]

Equation (5.1) says this is a genuine metric on shapes, not a pseudometric,
and that its geometry dominates the compact arithmetic coordinate `y`.
Different valid schedules produce different but quantitatively comparable
embeddings of the same compactified shape cube into a reading torus.

---

## 6. A certified-design target for `(r,s,p)=(3,4,(2,3,5))`

For `s=4`, factorization gives

\[
 Q_4(z)=(1+z)(1+z^2).
 \tag{6.1}
\]

Let `phi=phi_4`.  Direct differentiation in `y=u/(1+u)` yields

\[
 -\partial_y\phi(y,\theta)
 =\frac{\sin\theta}{D_1(y,\theta)}
 +\frac{2y(1-y)\sin(2\theta)}{D_2(y,\theta)},
 \tag{6.2}
\]

where

\[
 D_1=(1-y)^2+2y(1-y)\cos\theta+y^2
 \tag{6.3}
\]

and

\[
 D_2=(1-y)^4+2y^2(1-y)^2\cos(2\theta)+y^4.
 \tag{6.4}
\]

### Lemma 6.1 — a rational sufficient phase box

Suppose the reduced `3 by 3` phase matrix satisfies

\[
 \frac7{10}<\theta_{\ell\ell}<1,
 \qquad
 |\theta_{\ell j}|<\frac1{25}\quad(j\ne\ell).
 \tag{6.5}
\]

Then the associated three-reading map is globally injective on `Theta_+`.
More quantitatively, put

\[
 M
 =2\tan\frac1{50}+4\tan\frac1{25}.
 \tag{6.6}
\]

The following strict inequalities hold:

\[
 M<\frac{21}{100},
 \qquad
 \kappa:=\sin\frac7{10}-2M>\frac6{25}.
 \tag{6.7}
\]

The lifted row oscillation obeys

\[
 W\le3\left(1+\frac2{25}\right)=\frac{81}{25}<2\pi,
 \tag{6.8}
\]

and `2 pi-W>kappa`.  Therefore

\[
 d_{\mathbb T,\infty}
 \bigl(\mathcal U_T(u),\mathcal U_T(u')\bigr)
 >\frac6{25}\|y-y'\|_\infty
 \tag{6.9}
\]

and

\[
 \|\mathcal U_T(u)-\mathcal U_T(u')\|_\infty
 >\frac3{20}\|y-y'\|_\infty.
 \tag{6.10}
\]

#### Proof

On the diagonal interval, both terms in (6.2) are positive and `D_1<=1`,
so

\[
 -\partial_y\phi(y,\theta)\ge\sin\frac7{10}.
 \tag{6.11}
\]

For `|theta|<=delta<pi/2`,

\[
 D_1\ge\cos^2(\theta/2).
 \tag{6.12}
\]

Writing `a=y^2`, `b=(1-y)^2`, one also has

\[
 D_2\ge(a+b)^2\cos^2\theta,
 \qquad
 y(1-y)\le(a+b)^2.
 \tag{6.13}
\]

It follows that

\[
 |\partial_y\phi(y,\theta)|
 \le2\tan\frac{|\theta|}{2}+4\tan|\theta|
 \le M
 \tag{6.14}
\]

on each off-diagonal window.  Equations (6.7)--(6.8) now verify Theorem 3.2.
Finally, (5.2), `2/pi>5/8`, and `(5/8)(6/25)=3/20` give (6.10).
\(\square\)

### Theorem 6.2 — an exact rational globally injective schedule

Let

\[
 T_*=\left(
 \frac{245943}{1000},
 \frac{140531}{500},
 \frac{120104}{125}
 \right)
 =(245.943,281.062,960.832).
 \tag{6.15}
\]

For the winding matrix

\[
 N=
 \begin{pmatrix}
 27&43&63\\
 31&49&72\\
 106&168&246
 \end{pmatrix},
 \tag{6.16}
\]

define

\[
 \theta_{\ell j}=t_\ell\log p_j-2\pi N_{\ell j}.
 \tag{6.17}
\]

At 384-bit Arb precision the outward-enclosed central values are

\[
 \begin{pmatrix}
 0.8286937346057943570 &
 0.0190339031786833230 &
 -0.0106858545339996159\\
 0.0385883399721677707 &
 0.9020870258365087136 &
 -0.0375035723771068526\\
 -0.0196507692627950161 &
 0.00671093938664287923 &
 0.7358627137032578048
 \end{pmatrix},
 \tag{6.18}
\]

with interval radii below `4e-101`.  Every diagonal entry lies strictly in
`(7/10,1)`, and every off-diagonal magnitude is strictly below `1/25`.
Consequently `T_*` is globally injective and satisfies (6.9)--(6.10).

The unrounded finite claim is the collection of inequalities

\[
 \frac7{10}<t_\ell\log p_\ell-2\pi N_{\ell\ell}<1
 \tag{6.19}
\]

and

\[
 |t_\ell\log p_j-2\pi N_{\ell j}|<\frac1{25}
 \quad(j\ne\ell),
 \tag{6.20}
\]

not the displayed decimal approximation.

The schedule was found by a deterministic enumeration of winding triples
and intersections of their admissible time intervals.  That discovery
procedure was not an exhaustive search over schedule space and gives no
optimality claim for the magnitudes in (6.15).  The theorem depends only on
the exact rational times, integer windings, and inequalities
(6.19)--(6.20), not on how the candidate was found.

### Corollary 6.3 — explicit raw-reading stability

For the phase box (6.5),

\[
 |A_u(t_\ell)|>\frac9{10}
 \qquad(u\in\mathbb R_{>0}^3).
 \tag{6.21}
\]

Therefore

\[
 \boxed{
 \|\mathcal F_{T_*}(C,u)-\mathcal F_{T_*}(C',u')\|_\infty
 >\frac2{15}\min\{C,C'\}\|y-y'\|_\infty.}
 \tag{6.22}
\]

#### Proof

For an off-diagonal phase `|theta|<1/25`, both `cos theta` and
`cos(2 theta)` are positive, so both factors in (6.1) have modulus at least
one.  For a diagonal phase `7/10<theta<1`, the first factor again has modulus
at least one.  With `v=u^2`, the minimum of
`|1+v e^{-2i theta}|` over `v>=0` is one when `cos(2 theta)>=0` and is
`sin(2 theta)` otherwise.  Throughout the declared interval this is greater
than `sin 2>9/10`.  Thus (6.21) holds.  Combining it with (6.10) and (5.7)
gives the coefficient `27/200`, which is greater than `2/15`.

The certificate records a substantially stronger finite constant.  Since
`eta=kappa` here and `||y-y'||_infinity<=1`, concavity of sine gives

\[
 \|\mathcal U_T(u)-\mathcal U_T(u')\|_\infty
 \ge2\sin(\kappa/2)\|y-y'\|_\infty.
 \tag{6.23}
\]

The certified values

\[
 2\sin(\kappa/2)>0.2434311410,
 \qquad
 \sin(2)\,2\sin(\kappa/2)>0.2213513102
 \tag{6.24}
\]

also imply (6.22), with ample margin.
\(\square\)

---

## 7. Acquisition chambers

The sharp count describes how many readings are needed when the schedule may
be designed.  At the threshold itself, schedule space contains qualitatively
different open regions.

### 7.1 A robust globally injective chamber

Let

\[
 \mathcal C_{\mathrm{good}}
 =\left\{T\in\mathbb R^3:
 |t_\ell-t_{*,\ell}|<\frac1{1000}
 \text{ for }\ell=1,2,3\right\}.
 \tag{7.1}
\]

Changing `t_l` by `Delta t_l` changes its `j`-th reduced phase by exactly
`lambda_j Delta t_l`, provided the same winding representative remains in
force.  Direct interval enlargement of all nine entries in (6.18) shows
that every schedule in `C_good` still satisfies (6.5).  The closest margins
are the off-diagonal entries in the second row; their coordinatewise changes
are bounded by `(log 2)/1000` and `(log 5)/1000`, respectively, and remain
strictly inside `(-1/25,1/25)`.

Hence every schedule in `C_good` is globally injective and retains the
uniform constants (6.9), (6.10), and (6.22).  This is an open acquisition
chamber, not an isolated Diophantine point.

The analytic implication is proved by Lemma 6.1.  The accompanying artifact
certifies the finite interval enlargement at radius `1/1000`: throughout
that cube the largest off-diagonal magnitude is below `0.039282`, the
smallest diagonal is above `0.734253`, and the largest diagonal is below
`0.903186`.

### 7.2 A robust reciprocal-collision chamber

Return to the centered trace (4.6) and define

\[
 G(T,x)
 =\bigl(\Im B_x(t_1),\Im B_x(t_2),\Im B_x(t_3)\bigr).
 \tag{7.2}
\]

Every nonzero zero of `G(T,x)` gives the exact reciprocal collision (4.9).
Arithmetic Observability IV reported a high-precision candidate at

\[
 T_0=(1,2,3),
 \tag{7.3}
\]

near

\[
 x_*=(-2.3116495000818833,
      -0.4996823392786412,
       0.2844776759098668).
 \tag{7.4}
\]

A parameterized interval Krawczyk test treats `T` as an interval parameter
and `x` as the solved variable.  Let the exact schedule cube be

\[
 \mathcal P=(1,2,3)+[-2^{-24},2^{-24}]^3
 \tag{7.5}
\]

and let the solution box be

\[
 \mathcal X=x_*+[-2^{-14},2^{-14}]^3,
 \tag{7.6}
\]

where `x_*` is stored as the exact rational represented by its full decimal
string in the payload and displayed approximately in (7.4).  Let `R` be the
exact rational `3 by 3` matrix recorded there; its exact determinant is
nonzero.  In centered coordinates the parameterized Krawczyk set is

\[
 \mathcal K
 =-R G(\mathcal P,x_*)
  +\bigl(I-RD_xG(\mathcal P,\mathcal X)\bigr)
    [-2^{-14},2^{-14}]^3.
 \tag{7.7}
\]

### Theorem 7.1 — a certified open collision chamber

The interval evaluation of (7.7) satisfies

\[
 \mathcal K\subset
 \operatorname{int}[-2^{-14},2^{-14}]^3.
 \tag{7.8}
\]

Consequently, for every \(T\in\mathcal P\), there is at least one
\(x(T)\in\mathcal X\) such that `G(T,x(T))=0`.  The box \(\mathcal X\)
excludes the origin—in fact each coordinate is bounded away from zero—so
every schedule in the interior of \(\mathcal P\) has a pair of distinct
reciprocal positive sources with identical three-reading data.

#### Proof

The parameterized Krawczyk existence theorem applied to the exact
nonsingular preconditioner `R` and the strict inclusion (7.8) produces at
least one root in \(\mathcal X\) for each fixed parameter
\(T\in\mathcal P\).  No uniqueness claim is needed or made.  The
certificate's outward intervals for the three centered Krawczyk coordinates
have absolute upper endpoints approximately

\[
 3.12\mathbin{\cdot}10^{-5},
 \qquad
 2.75\mathbin{\cdot}10^{-6},
 \qquad
 2.73\mathbin{\cdot}10^{-6},
 \tag{7.9}
\]

all strictly below
`2^{-14}=6.103515625...` \(\mathbin{\cdot}10^{-5}\); the artifact
stores exact dyadic endpoint comparisons.  It also checks directly that
every coordinate interval of \(\mathcal X\) avoids zero.  Finally,
`G(T,x(T))=0` says
that all three centered readings are real.  Equations (4.6)--(4.9) then give
the exact reciprocal collision.  \(\square\)

For the fixed schedule `(1,2,3)`, a second Krawczyk inclusion localizes a root
in the much smaller box of radius `2^{-280}` about `x_*`.  This validates the
formerly numerical collision from Arithmetic Observability IV; the robust
radius `2^{-24}` in schedule space is the new chamber statement.

### 7.3 What the two chambers mean

The good chamber and the collision chamber show that acquisition geometry
is nontrivial even when the optimal count is known:

\[
 \text{same model and same count}
 \quad\not\Longrightarrow\quad
 \text{same global observability}.
 \tag{7.10}
\]

They do not classify all of `R^3`.  Between them may lie further injective
components, collision components, singular walls, and schedules whose only
collisions escape toward a compactification face.  The phrase *acquisition
chamber* here means an explicitly controlled open set with a uniform
property, not a claim that the entire complement has been stratified.

---

## 8. Exact injectivity without uniform log-coordinate stability

The coordinate `y=u/(1+u)` compresses both arithmetic extremes into finite
boundary faces.  This is precisely why a global bound such as (5.1) can
hold.  The same statement is false in `x=log u`.

### Theorem 8.1 — obstruction at infinity

For any finite schedule `T`, any `s>=2`, and any `r>=1`, there is no constant
`L>0` such that

\[
 \|\mathcal F_T(C,e^x)-\mathcal F_T(C',e^{x'})\|
 \ge L\|(\log C,x)-(\log C',x')\|
 \tag{8.1}
\]

holds globally on `Theta_+`, for any fixed norm on the finite-dimensional
source and observation spaces.  This remains false even with `C=C'=1`.

#### Proof

Fix all coordinates except the first and take

\[
 x_1^{(n)}=-n,
 \qquad
 {x_1'}^{(n)}=-(n+1).
 \tag{8.2}
\]

Their log-coordinate distance is the fixed positive number given by the norm
of that coordinate vector (equal to one for the usual Euclidean or maximum
norm).  Uniformly over the finite schedule,

\[
 Q_s(e^{-n}e^{-i\lambda_1t_\ell})
 -Q_s(e^{-(n+1)}e^{-i\lambda_1t_\ell})
 =O(e^{-n}).
 \tag{8.3}
\]

All other factors are fixed, so the observation distance tends to zero.
No positive `L` can satisfy (8.1).  \(\square\)

The same phenomenon appears at `u=infinity` after compensating the leading
power by the free scale.  It is therefore a boundary property of the model,
not a defect of the phase-separated construction.

### Corollary 8.2 — geometry created by distinguishability

The observation geometry selects the compact coordinate `y`, rather than
the unbounded log coordinate `x`, as a natural globally stable shape
geometry.  Infinitesimal changes in `x` have derivative

\[
 \frac{dy}{dx}=y(1-y),
 \tag{8.4}
\]

which vanishes at both compactification faces.  Exact injectivity records
which interior point generated noiseless data; quantitative observability
records how boundary-near points become indistinguishable under noise.
These are different assertions and should not be conflated.

---

## 9. Validity ledger

### Proved analytically

1. The root-free compact phase sector for every `s>=2`.
2. The exact positive pair-sum identity (2.5), including its boundary
   extension.
3. Strict phase monotonicity and exact one-axis oscillation.
4. The phase-separated global-injectivity criterion with an explicit
   inverse modulus.
5. Existence, by Kronecker approximation, of suitable `r`-reading schedules
   for all prime boxes.
6. The sharp count `m_glob,+=r`, including `r=1`.
7. The torus distinguishability metric and scale-aware raw stability bound.
8. The canonical rational phase-box implication and its displayed analytic
   constants.
9. The impossibility of a uniform raw inverse-Lipschitz bound in global log
   coordinates.

### Certified finite claims

1. The nine reduced-phase enclosures for the rational schedule (6.15).
2. The strict bounds `M<21/100`, `kappa>6/25`, `W<2 pi`, and the auxiliary
   trigonometric inequalities used in the chord and raw-reading constants.
3. Preservation of every phase-box inequality throughout the time cube of
   radius `1/1000` in (7.1).
4. The parameterized Krawczyk inclusion establishing a nonzero reciprocal
   root throughout the declared bad chamber near `(1,2,3)`.

### Numerical displays that are not proof inputs

1. The shortened decimal center in (7.4); the artifact uses the exact
   rational represented by each full decimal string.
2. Rounded interval summaries such as (6.18), (6.24), and (7.9); every proof
   decision uses the exact rational bound or an outward Arb interval stored
   in the payload.

### Not established

1. A classification of all globally injective and colliding `r`-reading
   schedules.
2. Optimal bounds on the magnitudes of phase-separated times.
3. The largest good or bad acquisition chamber around either example.
4. The exact positive collision multiplicity outside the certified local
   Krawczyk box.
5. The optimal global count over the complex parameter space.
6. Robustness to unknown or mislabelled primes, clock error beyond the
   declared chamber, off-model coefficients, or an unknown value of `s`.
7. Any passage from the finite prime box to an infinite Euler product.

---

## 10. Reproduction

The finite artifact uses exact rational inputs and Arb interval
arithmetic.  It certifies finite transcendental inequalities and a
parameterized Krawczyk inclusion; it does not mechanize Kronecker's theorem,
Borsuk--Ulam, or the ordinary analytic proofs in Sections 2--5.

Verify the artifact with:

```bash
python arithmetic_observability_global_design.py \
  --verify arithmetic_observability_global_design_certificate.json
```

Run the adversarial suite with:

```bash
python -m unittest -v test_arithmetic_observability_global_design.py
```

Artifacts:

```text
arithmetic_observability_global_design.py
arithmetic_observability_global_design_certificate.json
test_arithmetic_observability_global_design.py
```

Frozen metadata:

```text
SCHEMA = arithmetic-observability-global-design-v1
PRECISION = 384 bits
PAYLOAD_SHA256 = ef58b99b5a1377878a7b9fd770c6a16fa5961bb46af40d74f0697e7f0454f2ab
IMPLEMENTATION_SHA256 = 9ecccaed11fb3114fb083a6efce1a97ea98fc7e2a5061c846c5430717b032521
CERTIFICATE_FILE_SHA256 = 09fdde5f630121329228b8fb57f8ce4cce3b99bf786b53843bf0aa8d793efe37
TEST_FILE_SHA256 = 5e55044c8a4532bf6c671246c8d9dc570053e9982cd396a0e9be7bda63439751
FOCUSED_TEST_COUNT = 29
COMBINED_REGRESSION_COUNT = 137
WINDOWS_REGENERATION = passed, byte-identical
WINDOWS_PYTHON = 3.13.14
WINDOWS_PYTHON_FLINT = 0.9.0
WINDOWS_FLINT = 3.6.0
```

The verifier and adversarial tests reject undeclared fields, duplicate JSON
keys, nonfinite numbers, noncanonical rational strings, booleans in integer
fields, insufficient precision, widened intervals, altered chamber boxes,
and digest mismatches.  Its formal scope explicitly excludes proofs of the
phase-separation theorem, Kronecker and Borsuk--Ulam, the Krawczyk theorem
itself, the reciprocal identity, schedule optimality, the complex-global
problem, and every infinite-product claim.

---

## 11. Relation to standard tools and novelty boundary

The mathematical ingredients are classical:

- phase differentiation of a polynomial on a radial ray;
- compactification of the positive half-line;
- strict diagonal dominance and integration along line segments;
- Kronecker approximation on a torus;
- Borsuk--Ulam for the matching lower bound; and
- interval Newton--Krawczyk methods for robust finite root certification.

No priority claim is made for any of these tools, nor is this manuscript a
survey of finite phase retrieval, exponential fitting, global univalence,
or interval nonlinear solving.

The contribution within this finite arithmetic model is the synthesis that
turns those tools into:

1. an exact global individual-reading count for every positive prime box;
2. a phase-separated design criterion that identifies the shape at that
   count, after which one nonzero magnitude identifies the scale;
3. a global distinguishability geometry that remains controlled at all
   compactified faces;
4. explicit robust good and bad regions in acquisition space; and
5. a precise separation between noiseless injectivity and stability in an
   unbounded parameterization.

These conclusions concern the declared model and should not be extrapolated
to unrelated phase-retrieval settings without checking their hypotheses.
In particular, the observations here are complex values, not magnitudes
alone.  General Dirichlet-polynomial and multivariate exponential
reconstruction results treat materially different arbitrary-coefficient or
unknown-frequency models; their sample counts neither imply nor contradict
the rank-one positive-model count proved here.

---

## 12. Next questions

The exact count changes the research target from *how many readings?* to
*which schedules, and with what geometry?*  Natural next problems are:

1. characterize the connected components and boundary walls of the good
   and bad acquisition regions;
2. minimize time magnitude subject to a certified global stability margin;
3. replace existence by a deterministic Diophantine design algorithm with
   explicit complexity bounds;
4. determine whether other factorizable arithmetic kernels admit larger
   monotonic phase sectors and better conditioning;
5. quantify perturbations of the frequencies themselves; and
6. compare the compact phase metric with statistical minimax risk under
   wrapped phase noise and raw complex noise.

The first question is already falsifiable on the canonical model.  One can
tile bounded schedule space, certify good boxes by derivative dominance,
certify bad boxes by parameterized Krawczyk inclusions, and leave every
unresolved tile explicitly undecided.  Such a computation would map a
genuine acquisition geometry rather than infer it from isolated examples.

---

## References and standard background

1. K. Borsuk, *Drei Sätze über die n-dimensionale euklidische Sphäre*,
   Fundamenta Mathematicae 20 (1933), 177--190.
2. J. W. S. Cassels, *An Introduction to Diophantine Approximation*,
   Cambridge University Press, 1957; standard background for simultaneous
   approximation and Kronecker's theorem.
3. R. E. Moore, R. B. Kearfott, and M. J. Cloud, *Introduction to Interval
   Analysis*, SIAM, 2009; interval Newton and Krawczyk methods.
4. D. Gale and H. Nikaido, *The Jacobian matrix and global univalence of
   mappings*, Mathematische Annalen 159 (1965), 81--93,
   [doi:10.1007/BF01360282](https://doi.org/10.1007/BF01360282); classical
   P-matrix global-univalence theorem.  The present integrated
   row-dominance proof is direct and quantitative.
5. H. Hedenmalm, P. Lindqvist, and K. Seip, *A Hilbert space of Dirichlet
   series and systems of dilated functions in L2(0,1)*, Duke Mathematical
   Journal 86 (1997), 1--37,
   [doi:10.1215/S0012-7094-97-08601-4](https://doi.org/10.1215/S0012-7094-97-08601-4);
   background for the finite-prime Bohr--Kronecker viewpoint.
6. Arithmetic Observability IV, *Local versus global complexity of
   individual harmonic readings*, companion manuscript, 2026.
7. J. M. Varah, *A lower bound for the smallest singular value of a matrix*,
   Linear Algebra and its Applications 11 (1975), 3--5,
   [doi:10.1016/0024-3795(75)90112-3](https://doi.org/10.1016/0024-3795(75)90112-3);
   classical strict-diagonal-dominance inverse estimate.
8. R. Krawczyk, *Newton-Algorithmen zur Bestimmung von Nullstellen mit
   Fehlerschranken*, Computing 4 (1969), 187--201,
   [doi:10.1007/BF02234767](https://doi.org/10.1007/BF02234767).
9. J. Miller and C. Martin, *Some properties of mappings induced by
   Dirichlet polynomials*, Applied Mathematics and Computation 64 (1994),
   1--11,
   [doi:10.1016/0096-3003(94)90136-8](https://doi.org/10.1016/0096-3003(94)90136-8).
10. A. Cuyt and W.-s. Lee, *Multivariate exponential analysis from the
    minimal number of samples*, Advances in Computational Mathematics 44
    (2018), 987--1002,
    [doi:10.1007/s10444-017-9570-8](https://doi.org/10.1007/s10444-017-9570-8).
