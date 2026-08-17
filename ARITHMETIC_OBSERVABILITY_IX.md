# Arithmetic Observability IX

## Quotient zonoids and alias-circle support

### Removing nonquery prefixes before the tail dual, and resolving the post-million Mellin aliases

- **Research lead, theorem synthesis, computation design, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** research manuscript; formal fine-grid certificate complete;
  not peer reviewed
- **Date:** 15 August 2026
- **Parent manuscripts:** `ARITHMETIC_OBSERVABILITY_I.md`,
  `ARITHMETIC_OBSERVABILITY_VIII.md`, and
  `ARITHMETIC_SENSING_V_COMPLETE.md`

## Abstract

Arithmetic Observability VIII reduced the four-anchor closest-fibre problem
to integer nonquery prefixes followed by distance to a compact arithmetic
tail zonoid.  Its pair-specific lower bound was already within `0.71151%` of
an explicit integral obstruction, but more than `99.49%` of the support cost
came from the certified response beyond one million.  This paper identifies
and repairs the mathematical source of that loss.

There are two complementary reductions.  First, all remaining real nonquery
prefix directions can be profiled out *before* optimizing over the tail zonoid.  If
`W` is their response span and `Q=P_{W^\perp}`, then

\[
 \inf_{w\in W,\ z\in\mathcal Z}\|q+w-z\|
 =\operatorname{dist}(Qq,Q\mathcal Z)
 =\max_{\substack{u\in W^\perp\\\|u\|\le1}}
   \bigl((u,q)_{\mathbb R}-h_{\mathcal Z}(u)\bigr).
\]

This quotient-zonoid value is a single uniform lower bound for every integer
nonquery prefix.  It is a convex relaxation of the remaining lattice search,
not an exchange of a minimum and maximum.

Second, the pinned multiscale sample times are odd tenths.  Every real dual
response is therefore antiperiodic under a log-frequency shift of `10 pi`,
and its absolute value lives on an exact alias circle.  The Fourier moments
of the degree-fourteen post-million measure are

\[
 D_M\left(2-\frac{im}{5}\right)
 =\zeta\left(2-\frac{im}{5}\right)^{14}
  -\sum_{k\le M}\frac{d_{14}(k)}{k^{2-im/5}}.
\]

Every pointwise trigonometric majorant of the absolute dual response thus
gives a finite support upper bound.  A convergent one-sided-majorant hierarchy
recovers the exact support in the limit.  This is an exact analytic
formulation, although a useful high-order numerical realization still needs
many certified complex moments.

For the pinned cosine window, a more direct finite certificate is stronger.
Writing `m=5T`, `x=omega/10`, and
`delta_r=pi r/m`, the shifted cosecants have the exact symmetric expansion

\[
 \frac{\sin(mx)}m\left[
 \csc x+\sum_{r=1}^Hc_r
 (\csc(x+\delta_r)+\csc(x-\delta_r))\right].
\]

The designed zeroth moment

\[
 a_0=1+2\sum_{r=1}^8c_r
 =\frac{6781931884467}{576460752303423488}
 =1.17647764524605\ldots\times10^{-5}
\]

survives a symmetric second-order Taylor bound.  The remainder in the former
coarse-bin theorem differentiated every shifted term separately, so its
dominant interval-width term did not retain this small factor.  Away from a
sampling pole, the new bound is of order `10^-9`, not `10^-6`.  Near the
poles, exact fine log bins confine every alias fallback to an interval one hundred times
narrower than before.  The shifted Dirichlet-quotient form supplies an
independent pole-safe theorem rather than assigning value one to a broad
coarse bin.

At fine width `h=10^-4`, exact FLINT convolution and directed-MPFR kernel
ceilings certify post-million support uppers
`1.5898117981810922e-5` for target 5 and `4.737636732087896e-6` for target 50.
These improve the published remote endpoints by factors `17.6862` and
`41.2115`.  The resulting target-5 common-box radius is
`0.019991343023375665...`, while the inverse-free quotient certificate gives
the stronger structural conclusion

\[
 \rho_{4,\mathrm{global}}
 \ge0.019991343027394314\ldots
\]

uniformly over the full remaining real nonquery prefix span.  The certified
integral alias obstruction is below `0.01999999999778216`, leaving a relative
gap of about `0.04330%`.  The exact quotient minimizer remains open.

An apparently simpler quadratic-moment route is falsified quantitatively:
Cauchy--Schwarz gives about `0.0162283` at target 5, roughly 58 times *worse*
than the old bound.  The narrow alias geometry, not merely an `L^2` moment,
must be retained.

---

## 1. The remaining loss after common-nuisance centering

Let `H` be the finite realification of the pinned Arithmetic Sensing V data
space.  For the first fifty normalized Dirichlet columns write

\[
 Ae_n=\frac1{n^2}c_n,
 \qquad \|c_n\|=1,
 \tag{1.1}
\]

and let

\[
 \mathcal Z
 =\left\{
   \sum_{k>50}x_k\frac{c_k}{k^2}:
   |x_k|\le d_{14}(k)
  \right\}
 \tag{1.2}
\]

be the continuous common-tail difference body.  The series converges
absolutely in the finite data space.  Arithmetic Observability VIII proved
that `Z` is a compact centrally symmetric zonoid and that, for every prefix
difference `h`,

\[
 d(h)=\operatorname{dist}(Ah,\mathcal Z)
 =\max_{\|u\|\le1}
 \left((u,Ah)_{\mathbb R}
 -\sum_{k>50}\frac{d_{14}(k)}{k^2}
  |(u,c_k)_{\mathbb R}|
 \right).
 \tag{1.3}
\]

For the adjacent direction `e_5`, choosing `u=c_5` gave the direct support
bound

\[
 \sum_{k>50}\frac{d_{14}(k)}{k^2}
 |(c_5,c_k)_{\mathbb R}|
 \le
 1.4158209810239882\times10^{-6}
 +2.8117732435796035\times10^{-4}.
 \tag{1.4}
\]

The first term is the Arb finite sum for `51<=k<=10^6`.  The second is the
directed-MPFR remote majorant.  The remote term supplies more than `99.49%`
of (1.4).  This is inconsistent with the scale of the exact window away from
an alias and therefore signals a proof loss rather than a discovered large
tail response.

There were two unresolved questions.

1. Must the integer coordinates `15,...,50` be searched one branch at a time,
   or can their entire real span be removed by an exact quotient?
2. Can the remote support retain the window's designed cancellation and the
   narrow geometry of its sampling aliases simultaneously?

The next two sections answer the structural parts of both questions.

---

## 2. Profiling a subspace before a compact zonoid

The common-subspace theorem in Arithmetic Observability I and the compact-
zonoid theorem in Arithmetic Observability VIII compose exactly.

Let `H` be a finite-dimensional real Hilbert space, let `W subset H` be a
linear subspace, let `Q=P_{W^\perp}`, let `q in H`, and let `Z subset H` be
nonempty, compact, and convex.  Central symmetry is useful in the arithmetic
application but is not needed for the equality below.

### Theorem 2.1 - quotient-zonoid distance

The distance between the affine nuisance space `q+W` and `Z` is attained and
satisfies

\[
 \boxed{
 \begin{aligned}
 \inf_{w\in W,\ z\in\mathcal Z}\|q+w-z\|
 &=\min_{z\in\mathcal Z}\|Q(q-z)\|\\
 &=\operatorname{dist}(Qq,Q\mathcal Z).
 \end{aligned}}
 \tag{2.1}
\]

It also has the attained dual

\[
 \boxed{
 \operatorname{dist}(Qq,Q\mathcal Z)
 =\max_{\substack{u\in W^\perp\\\|u\|\le1}}
 \bigl((u,q)_{\mathbb R}-h_{\mathcal Z}(u)\bigr),}
 \tag{2.2}
\]

where

\[
 h_{\mathcal Z}(u)=\sup_{z\in\mathcal Z}(u,z)_{\mathbb R}.
 \tag{2.3}
\]

If

\[
 \mathcal Z
 =\left\{\sum_kx_kv_k:|x_k|\le d_k\right\},
 \qquad \sum_kd_k\|v_k\|<\infty,
 \tag{2.4}
\]

then (2.2) becomes

\[
 \operatorname{dist}(Qq,Q\mathcal Z)
 =\max_{\substack{u\in W^\perp\\\|u\|\le1}}
 \left((u,q)_{\mathbb R}-
 \sum_kd_k|(u,v_k)_{\mathbb R}|
 \right).
 \tag{2.5}
\]

#### Proof

For fixed `z`, orthogonal decomposition gives

\[
 \inf_{w\in W}\|q-z+w\|
 =\|Q(q-z)\|.
 \tag{2.6}
\]

Taking the infimum over `z` proves the first line of (2.1).  The image `QZ`
is compact, so the remaining minimum is attained.  If `z_*` minimizes it,
then choosing

\[
 w_*=-P_W(q-z_*)
 \tag{2.7}
\]

also attains the original two-variable infimum.

Apply the support-function distance theorem to the compact convex set `QZ`.
Every dual vector may be taken in `W^\perp`, and for such a vector

\[
 (u,Qq)_{\mathbb R}=(u,q)_{\mathbb R},
 \qquad
 h_{Q\mathcal Z}(u)=h_{\mathcal Z}(u).
 \tag{2.8}
\]

This proves (2.2).  Absolute convergence in (2.4) gives the support identity

\[
 h_{\mathcal Z}(u)=\sum_kd_k|(u,v_k)_{\mathbb R}|,
 \tag{2.9}
\]

and hence (2.5).  \(\square\)

### Corollary 2.2 - one lower bound for every remaining prefix

For the four-anchor problem, put

\[
 q=Ae_5,
 \qquad
 W=\operatorname{span}_{\mathbb R}
 \{Ae_n:n\in\{4,6,7,\ldots,50\}\}.
 \tag{2.10}
\]

Then every real or integer nonquery prefix `p` supported on those coordinates
obeys

\[
 \operatorname{dist}(A(e_5+p),\mathcal Z)
 \ge \operatorname{dist}(Qq,Q\mathcal Z).
 \tag{2.11}
\]

Therefore a single feasible dual vector

\[
 u\in W^\perp,
 \qquad \|u\|\le1,
 \tag{2.12}
\]

certifies the uniform branch-independent lower bound

\[
 (u,q)_{\mathbb R}
 -\sum_{k>50}\frac{d_{14}(k)}{k^2}
 |(u,c_k)_{\mathbb R}|.
 \tag{2.13}
\]

This corollary does not assert that the real relaxation is attained at an
integer prefix.  It moves in the safe direction: minimizing over the larger
real subspace can only lower the distance.  If the quotient value already
matches the best explicit upper witness, the 36-coordinate branch search is
unnecessary.  If it is smaller, its optimizer identifies the real direction
along which an integer search should concentrate.

### Proposition 2.3 - a finite Schur quotient certificate

The quotient dual need not begin with a large sample-space optimization.  Work
in the realified Hilbert space from Section 1, and let the **real** operator
`C_W` synthesize normalized nuisance columns `c_j`, `j in J_W`, from real
coefficients.  Put

\[
 G_W=C_W^{\mathsf T}C_W,
 \qquad
 g=C_W^{\mathsf T}c_5.
 \tag{2.14}
\]

Assume `G_W` is positive definite and define the real coefficient vector

\[
 \beta=G_W^{-1}g,
 \qquad
 r=c_5-C_W\beta,
 \qquad
 \gamma^2=1-g^{\mathsf T}G_W^{-1}g>0.
 \tag{2.15}
\]

Then `u=r/gamma` belongs to `W^perp`, has unit norm, and satisfies

\[
 (u,Ae_5)_{\mathbb R}=\frac\gamma{25}.
 \tag{2.16}
\]

For the centrally symmetric arithmetic zonoid, if certified numbers `tau_j`
obey

\[
 h_{\mathcal Z}(c_j)\le\tau_j,
 \tag{2.17}
\]

then

\[
 \boxed{
 \operatorname{dist}(Ae_5+W,\mathcal Z)
 \ge
 \frac\gamma{25}
 -\frac{\tau_5+\sum_{j\in J_W}|\beta_j|\tau_j}{\gamma}.}
 \tag{2.18}
\]

#### Proof

The normal equations give `C_W^T r=0`, while

\[
 \|r\|^2=1-g^{\mathsf T}G_W^{-1}g=\gamma^2.
 \tag{2.19}
\]

Thus `u` is a feasible vector in (2.5).  Orthogonality also gives
`(r,c_5)=||r||^2`, proving (2.16).  Finally, every `beta_j` is real, so
sublinearity, positive homogeneity, and symmetry of the support function imply

\[
 h_{\mathcal Z}(u)
 \le\frac1\gamma\left(
 \tau_5+\sum_{j\in J_W}|\beta_j|\tau_j
 \right).
 \tag{2.20}
\]

Insert (2.16) and (2.20) in the feasible dual lower bound.  \(\square\)

For the four-anchor nuisance set,

\[
 J_W=\{4,6,7,\ldots,50\}.
 \tag{2.21}
\]

The factors `j^-2` in `Ae_j` do not change their real span, so normalized
columns may be used in (2.14).  Proposition 2.3 converts the all-target remote
vector directly into a global closest-fibre lower bound; it does not require a
new remote theorem for a dense sample-space vector.

### Corollary 2.4 - inverse-free quotient bound

The exact Gram solve in Proposition 2.3 can be removed.  Let `G` be the full
real Gram matrix of the normalized realified columns `c_j`, `1<=j<=50`, and
write

\[
 G=I+E,
 \qquad
 q\ge\max_i\sum_{j\ne i}|E_{ij}|,
 \qquad
 q_5\ge\sum_{j\ne5}|E_{5j}|,
 \tag{2.22}
\]

where both sums range over `1<=j<=50`, the displayed `q,q_5` may be certified
rational upper bounds, and `q<1`.  Here the scalar Gram defect `q` is
unrelated to the vector `q` in Theorem 2.1.  Let

\[
 \tau_W=\max_{j\in J_W}\tau_j,
 \qquad
 s_5=1-\frac{q_5^2}{1-q},
 \qquad
 P_5=\tau_5+\frac{q_5\tau_W}{1-q}.
 \tag{2.23}
\]

For the 46-column nuisance set (2.21), if `s_5>0`, then

\[
 \boxed{
 \operatorname{dist}(Ae_5+W,\mathcal Z)
 \ge D_5
 :=\frac{\sqrt{s_5}}{25}-\frac{P_5}{\sqrt{s_5}}.}
 \tag{2.24}
\]

Equivalently, with `N_5:=s_5/25-P_5`, positivity of `N_5` gives
`D_5=N_5/sqrt(s_5)` and the exact rational identity
`D_5^2=N_5^2/s_5`.  Thus a certificate can store `D_5^2` exactly and only
needs outward square-root rounding for the displayed distance.

In particular, if `D_5>0`, every remaining real nonquery prefix supported on
(2.21), and hence every allowed integer prefix in that class, has fibre
distance at least `D_5`.  Combined with the earlier coordinate exclusions and
query-coordinate reduction of Arithmetic Observability VIII, the global
four-anchor critical radius is at least `D_5/2`.

#### Proof

Let `B=G_W`.  Because `B-I` is real symmetric and is a principal submatrix
of `E`,

\[
 \|B-I\|_1=\|B-I\|_\infty\le q,
 \qquad
 \|B-I\|_2\le q,
 \qquad
 \|B^{-1}\|_1\le\frac1{1-q},
 \qquad
 \|B^{-1}\|_2\le\frac1{1-q}.
 \tag{2.25}
\]

The vector `g` is a restriction of the off-diagonal fifth Gram row, so
`||g||_1<=q_5`.  Therefore

\[
 \|\beta\|_1
 =\|B^{-1}g\|_1
 \le\|B^{-1}\|_1\|g\|_1
 \le\frac{q_5}{1-q}.
 \tag{2.26}
\]

Likewise,

\[
 \gamma^2
 =1-g^{\mathsf T}B^{-1}g
 \ge1-\frac{q_5^2}{1-q}
 =s_5.
 \tag{2.27}
\]

The support numerator in (2.18) is at most `P_5`.  The function

\[
 x\longmapsto\frac{x}{25}-\frac{P_5}{x}
 \tag{2.28}
\]

is strictly increasing for `x>0`.  Substitute `gamma>=sqrt(s_5)` in (2.18).
\(\square\)

Every input in (2.23) is either an existing certified rational Gram-row upper
or a nuisance-target support upper from the fine-bin certificate.  Thus
Corollary 2.4 needs no stored inverse, no approximate quotient vector, and no
new sample-space remote response.

### 2.1 Exact equivalence after both nuisance layers

Equation (2.1) also characterizes a new impossibility condition:

\[
 \operatorname{dist}(q+W,\mathcal Z)=0
 \quad\Longleftrightarrow\quad
 Qq\in Q\mathcal Z.
 \tag{2.29}
\]

Because `QZ` is compact, zero distance here is an attained collision, not
merely an asymptotic instability.  Thus the quotient-zonoid model retains the
three distinctions required by arithmetic observability:

- exact equivalence, when (2.29) holds;
- positive but possibly small distinguishability, measured by (2.1);
- integer effects, which can only increase the continuous-relaxation value.

---

## 3. The exact alias circle

The pinned multiscale measure has two centered midpoint components,

\[
 (T,m,\lambda)
 =\left(510,2550,\frac{125}{65536}\right),
 \qquad
 \left(1780,8900,\frac{65411}{65536}\right).
 \tag{3.1}
\]

Both have sample spacing `T/m=1/5`.  Their centered midpoint times are

\[
 t_j=-\frac T2+\left(j+\frac12\right)\frac15
 =\frac{2j+1-m}{10}.
 \tag{3.2}
\]

Since both sample counts are even, every numerator in (3.2) is odd.

Let `c(x)` denote the normalized data column at logarithmic frequency `x`,
and for a realified dual vector `u` define

\[
 F_u(x)=(u,c(x))_{\mathbb R}.
 \tag{3.3}
\]

### Proposition 3.1 - antiperiodicity and absolute periodicity

For every `u`,

\[
 c(x+10\pi)=-c(x),
 \qquad
 F_u(x+10\pi)=-F_u(x),
 \tag{3.4}
\]

and hence

\[
 |F_u(x+10\pi)|=|F_u(x)|.
 \tag{3.5}
\]

#### Proof

At every sample time in (3.2),

\[
 e^{it_j(x+10\pi)}
 =e^{it_jx}e^{i(2j+1-m)\pi}
 =-e^{it_jx}.
 \tag{3.6}
\]

The same sign applies to all coordinates and both time components.  Taking a
real inner product proves (3.4), and absolute values give (3.5).  \(\square\)

This is not an approximate alias relation.  It follows from the exact sample
lattice.  The support integrand lives on the circle

\[
 \mathbb R/(10\pi\mathbb Z).
 \tag{3.7}
\]

### Theorem 3.2 - exact arithmetic Fourier moments

Let `M>=1`, let `d>=1`, and define the post-cutoff Dirichlet function

\[
 D_{M,d}(s)
 :=\zeta(s)^d-\sum_{k\le M}\frac{d_d(k)}{k^s},
 \qquad \operatorname{Re}s>1.
 \tag{3.8}
\]

Then for every integer `r`,

\[
 \boxed{
 \sum_{k>M}\frac{d_d(k)}{k^2}
 e^{ir\log k/5}
 =D_{M,d}\left(2-\frac{ir}{5}\right).}
 \tag{3.9}
\]

In particular, the complete Fourier moment sequence of the remote
degree-fourteen alias-circle measure is known through values of one classical
Dirichlet function.

#### Proof

Absolute convergence at real part two permits termwise subtraction and gives

\[
 D_{M,d}\left(2-\frac{ir}{5}\right)
 =\sum_{k>M}d_d(k)k^{-2+ir/5}.
 \tag{3.10}
\]

This is (3.9).  \(\square\)

The identity is exact.  A numerical certificate must still enclose both the
complex zeta value and the finite Dirichlet polynomial with enough precision
to survive their subtraction.

---

## 4. A convergent one-sided majorant hierarchy

Let

\[
 f_u(x)=|F_u(x)|.
 \tag{4.1}
\]

It is a continuous `10 pi`-periodic function.  Suppose a real trigonometric
polynomial

\[
 P(x)=p_0+2\operatorname{Re}
 \sum_{r=1}^Jp_re^{irx/5}
 \tag{4.2}
\]

satisfies

\[
 P(x)\ge f_u(x)
 \qquad(x\in\mathbb R).
 \tag{4.3}
\]

### Theorem 4.1 - finite moment support upper

For degree `d` and cutoff `M`,

\[
 \boxed{
 \begin{aligned}
 &\sum_{k>M}\frac{d_d(k)}{k^2}|F_u(\log k)|\\
 &\quad\le
 p_0D_{M,d}(2)
 +2\operatorname{Re}\sum_{r=1}^J
 p_rD_{M,d}\left(2-\frac{ir}{5}\right).
 \end{aligned}}
 \tag{4.4}
\]

#### Proof

Multiply (4.3) at `x=log k` by the nonnegative weight
`d_d(k)k^-2`, sum over `k>M`, and apply (3.9) term by term.  \(\square\)

### Theorem 4.2 - completeness of the hierarchy

There is a sequence of trigonometric polynomials `P_J` satisfying

\[
 P_J\ge f_u,
 \qquad
 \|P_J-f_u\|_\infty\longrightarrow0.
 \tag{4.5}
\]

Consequently the right side of (4.4) consists of valid upper bounds converging
to the exact remote support; the particular Fejer construction need not be
monotone in `J`.  More quantitatively, if

\[
 0\le P_J-f_u\le\epsilon_J,
 \tag{4.6}
\]

then the support gap is at most

\[
 \epsilon_JD_{M,d}(2).
 \tag{4.7}
\]

#### Proof

Fejer means of the continuous periodic function `f_u` converge uniformly.
Add their uniform approximation error as a constant.  This produces a
one-sided polynomial satisfying (4.5).  Equation (4.7) follows by summing the
pointwise error against the positive remote arithmetic measure.  \(\square\)

### 4.1 Exact positivity certificates

Put `phi=x/10`.  The response `F_u(10phi)` is a trigonometric polynomial on
the `2 pi` circle and is antiperiodic under `phi -> phi+pi`.  A majorant may
be restricted to even harmonics.  Then

\[
 P(10\phi)\ge|F_u(10\phi)|
 \tag{4.8}
\]

is equivalent to the two nonnegativity conditions

\[
 P(10\phi)+F_u(10\phi)\ge0,
 \qquad
 P(10\phi)-F_u(10\phi)\ge0.
 \tag{4.9}
\]

For exact rational or dyadic response coefficients, each condition can be
certified by an exact Fejer--Riesz factor, by a rational trigonometric
sum-of-squares identity, or after conversion to an algebraic polynomial by a
Sturm certificate.  Thus (4.4) is not dependent on visual sampling of a
majorant.

This hierarchy is analytically exact and applies to arbitrary certified dual
directions, including quotient-space optimizers not lying in the prefix span.
Its computational cost is different from the positive fine-bin method below:
it requires many sharply enclosed complex Dirichlet tails rather than one
large nonnegative convolution.

---

## 5. A useful negative result: the quadratic level is far too weak

The first tempting moment relaxation keeps only a quadratic response.  Let

\[
 A_M=\sum_{k>M}\frac{d_{14}(k)}{k^2},
 \qquad
 Q_M(u)=\sum_{k>M}\frac{d_{14}(k)}{k^2}F_u(\log k)^2.
 \tag{5.1}
\]

Cauchy--Schwarz gives

\[
 \sum_{k>M}\frac{d_{14}(k)}{k^2}|F_u(\log k)|
 \le\sqrt{A_MQ_M(u)}.
 \tag{5.2}
\]

Equivalently, the elementary polynomial majorant

\[
 |x|\le\frac{x^2+\delta^2}{2\delta}
 \tag{5.3}
\]

gives

\[
 \frac{Q_M(u)+\delta^2A_M}{2\delta},
 \tag{5.4}
\]

whose optimum over `delta>0` is exactly (5.2).

For `u=c_5`, the current independent numerical audit gives

\[
 A_M\approx66.2708,
 \qquad
 Q_M(c_5)\approx3.97396\times10^{-6},
 \tag{5.5}
\]

and therefore

\[
 \sqrt{A_MQ_M(c_5)}\approx0.0162283.
 \tag{5.6}
\]

This is about `57.7` times *larger* than the already certified remote upper
`2.81177e-4`.  The quadratic relaxation is therefore rejected as a practical
certificate at the pinned cutoff.

The failure is informative.  The unfiltered degree-fourteen tail mass is
large, while the response is tiny on most of the alias circle and large only
in narrow neighborhoods.  A global second moment forgets where those
neighborhoods lie.  A successful theorem must preserve phase localization.
The numbers in (5.5)--(5.6) are diagnostic computations, not part of the
formal fine-grid certificate.

---

## 6. Preserving the designed cancellation away from poles

For one centered cosine-window component, put

\[
 m=5T,
 \qquad
 x=\frac\omega{10},
 \qquad
 \delta_r=\frac{\pi r}{m}.
 \tag{6.1}
\]

The exact common-numerator identity from Arithmetic Sensing V is

\[
 R_T(\omega)
 =\frac{\sin(mx)}m\left[
 \csc x+\sum_{r=1}^Hc_r
 \bigl(\csc(x+\delta_r)+\csc(x-\delta_r)\bigr)
 \right],
 \tag{6.2}
\]

with removable values supplied by the original finite quadrature.

Define

\[
 a_0=1+2\sum_{r=1}^Hc_r,
 \qquad
 S_2=\sum_{r=1}^H|c_r|r^2.
 \tag{6.3}
\]

For the pinned exact binary64 coefficients,

\[
 \begin{aligned}
 a_0
 &=\frac{6781931884467}{576460752303423488}
 =1.1764776452460532\ldots\times10^{-5},\\
 S_2
 &=\frac{24283045757518484661}{18446744073709551616}
 =1.3163865482433226\ldots.
 \end{aligned}
 \tag{6.4}
\]

The global cap used below is itself exact.  For the cosine density

\[
 W(\theta)=1+2\sum_{r=1}^8c_r\cos(r\theta),
\]

a Sturm certificate proves
`9/10^6<W(theta)<5/2` for every real `theta`.  Each midpoint grid has
`m>8`, so its exact average annihilates every nonconstant window harmonic;
the positive quadrature weights therefore sum to one.  Finally
`125+65411=65536`, so the two ensemble weights are nonnegative and sum to
one.  Each component response and their mixture `K` are consequently Fourier
transforms of probability measures and obey the certified global cap
`|R_T|<=1`, `|K|<=1`.

### Lemma 6.1 - symmetric cosecant remainder

If the interval `[x-delta,x+delta]` contains no multiple of `pi`, then

\[
 \csc(x+\delta)+\csc(x-\delta)-2\csc x
 =\int_{-\delta}^{\delta}
 (\delta-|t|)\csc''(x+t)\,dt.
 \tag{6.5}
\]

Moreover,

\[
 |\csc''y|
 =\frac{2-\sin^2y}{|\sin y|^3}
 \le\frac2{|\sin y|^3}.
 \tag{6.6}
\]

#### Proof

Equation (6.5) is the integral second-difference identity, obtained by
integrating the second derivative against the triangular kernel.  Direct
differentiation gives (6.6).  \(\square\)

### Theorem 6.2 - cancellation-aware away bound

Assume the quadrature weights underlying `R_T` are nonnegative and sum to
one, as certified for both pinned components.  Let `I` be a closed interval
of `x` values.  Put

\[
 s_0(I)=\inf_{x\in I}|\sin x|,
 \qquad
 s_H(I)=\inf_{\substack{x\in I\\|t|\le\delta_H}}
 |\sin(x+t)|.
 \tag{6.7}
\]

If `s_H(I)>0`, then

\[
 \boxed{
 \sup_{x\in I}|R_T(10x)|
 \le\min\left\{1,
 \frac{|a_0|}{m s_0(I)}
 +\frac{2\pi^2S_2}{m^3s_H(I)^3}
 \right\}.}
 \tag{6.8}
\]

#### Proof

Add and subtract `2c_r csc x` in every symmetric pair in (6.2).  The
coefficient of `csc x` becomes exactly `a_0`.  Lemma 6.1 and

\[
 \int_{-\delta_r}^{\delta_r}(\delta_r-|t|)\,dt
 =\delta_r^2
 \tag{6.9}
\]

give

\[
 \left|\csc(x+\delta_r)+\csc(x-\delta_r)-2\csc x\right|
 \le\frac{2\delta_r^2}{s_H(I)^3}.
 \tag{6.10}
\]

Use `|sin(mx)|<=1`, sum the absolute remainders, substitute
`delta_r=pi r/m`, and finally use the global positive-quadrature bound
`|R_T|<=1`.  \(\square\)

For a point whose distance from `pi Z` is `rho>delta_H`, (6.8) has the simpler
form

\[
 |R_T(10x)|
 \le\min\left\{1,
 \frac{|a_0|}{m\sin\rho}
 +\frac{2\pi^2S_2}{m^3\sin^3(\rho-\delta_H)}
 \right\},
 \tag{6.11}
\]

whenever the distances lie in the monotone half of a sine period.  The
interval formulation (6.8), not an implicit monotonicity assumption, is used
by the formal checker.

The numerical constants before the sine factors are

| `T` | `m` | `|a_0|/m` | `2 pi^2 S_2/m^3` | `delta_8` |
|---:|---:|---:|---:|---:|
| 510 | 2550 | `4.61363782449e-9` | `1.56708529541e-9` | `0.00985597695244` |
| 1780 | 8900 | `1.32188499466e-9` | `3.68589667633e-11` | `0.00282390350884` |

On the old `h=0.01` product bins, (6.8) reduces the non-pole part of the
remote majorant to approximately

\[
 1.391\times10^{-7}\quad(n=5),
 \qquad
 1.138\times10^{-7}\quad(n=50).
 \tag{6.12}
\]

These diagnostic values use the exact old convolution masses but exploratory
floating evaluation of (6.8).  They isolate the remaining problem: coarse
bins that touch one of the removable alias poles.

### 6.1 A pole-safe companion representation

Define the continuous normalized Dirichlet quotient

\[
 D_m(y)=\frac{\sin(my)}{m\sin y},
 \qquad
 D_m(\ell\pi)=(-1)^{(m-1)\ell}.
 \tag{6.13}
\]

Since `m delta_r=pi r`, (6.2) is equivalently

\[
 R_T(10x)
 =D_m(x)+\sum_{r=1}^H(-1)^rc_r
 \bigl(D_m(x+\delta_r)+D_m(x-\delta_r)\bigr).
 \tag{6.14}
\]

For an interval `J`, a safe elementary upper is

\[
 \mathcal D_m(J)
 =\begin{cases}
 1,&J\cap\pi\mathbb Z\ne\varnothing,\\
 \min\{1,[m\inf_{y\in J}|\sin y|]^{-1}\},&\text{otherwise}.
 \end{cases}
 \tag{6.15}
\]

Therefore

\[
 \sup_{x\in I}|R_T(10x)|
 \le\min\left\{1,
 \mathcal D_m(I)+\sum_{r=1}^H|c_r|
 \bigl(\mathcal D_m(I+\delta_r)
      +\mathcal D_m(I-\delta_r)\bigr)
 \right\}.
 \tag{6.16}
\]

The bound (6.16) is weaker far from a pole because it separates the shifted
terms, but it is regular at every removable singularity.  The frozen
fine-grid realization takes the rigorous minimum of (6.16) and the previously
audited directed midpoint enclosure of the exact common-numerator bracket,
whose interval remainder uses first derivatives.  A global cap handles any
remaining pole case.  At width `0.0015`, the midpoint branch preserves the
center cancellation and the shifted-Dirichlet branch confines removable-pole
fallbacks narrowly.  The symmetric second-order theorem (6.8) remains an
analytic cross-check and possible future sharpening; it is not silently
substituted for the two kernel rules named by the artifact.

For a positive time ensemble `K=sum_s lambda_s R_{T_s}`, the safe composition
is

\[
 \sup_I|K|
 \le\sum_s\lambda_s\sup_I|R_{T_s}|.
 \tag{6.17}
\]

Signed interval evaluation of the ensemble can only improve (6.17), but is
not required by the theorem.

---

## 7. Fine positive convolution with an exact target shift

The alias-circle hierarchy is exact but complex-valued.  The following
positive theorem gives a direct finite certificate using the established
log-Mellin machinery.

Fix a rational bin width `h>0` and an integer `J`.  For `0<=j<J`, let

\[
 \beta_j\ge
 \sum_{r:\,jh\le\log r<(j+1)h}r^{-\sigma}
 \tag{7.1}
\]

be certified nonnegative one-factor masses.  Let

\[
 C=\beta^{*d}
 \tag{7.2}
\]

be their exact ordinary convolution, retaining coefficients `C_q` for
`0<=q<J`.  A tuple contributing to `C_q` has product logarithm in

\[
 [qh,(q+d)h).
 \tag{7.3}
\]

Let `K` be any continuous response kernel.  For each integer `p`, define

\[
 U_p
 =\sup_{\omega\in[(p-1)h,(p+d)h]}|K(\omega)|.
 \tag{7.4}
\]

Finally choose a certified target shift `a_n` such that

\[
 a_nh\le\log n<(a_n+1)h.
 \tag{7.5}
\]

### Theorem 7.1 - fine-bin cross-correlation bound

Put `R=Jh`.  For every integer `1<=n<=M`,

\[
 \boxed{
 \begin{aligned}
 &\sum_{M<k<e^R}\frac{d_d(k)}{k^\sigma}
 |K(\log(k/n))|\\
 &\quad\le
 \sum_{\substack{0\le q<J\\
 (q+d)h>\log(M+1)}}C_qU_{q-a_n}.
 \end{aligned}}
 \tag{7.6}
\]

If `E_d(R)` is any upper bound for

\[
 \sum_{k\ge e^R}\frac{d_d(k)}{k^\sigma},
 \tag{7.7}
\]

then adding `E_d(R) sup|K|` gives the complete post-`M` support upper.

#### Proof

Expand `d_d` as the number of ordered `d`-tuples with product `k`.  Assign
each factor to its bin in (7.1).  If the factor-bin indices sum to `q`, then
(7.3) holds.  Subtracting the target enclosure (7.5) gives

\[
 \log(k/n)\in[(q-a_n-1)h,(q-a_n+d)h],
 \tag{7.8}
\]

whose response is bounded by `U_(q-a_n)`.  Every product greater than `M`
has `(q+d)h>log(M+1)`.  Products below the cutoff in bins that cross it are
possibly included, which only enlarges the positive sum.  Products at or
beyond `e^R` are handled by (7.7).  \(\square\)

The right side of (7.6) is a discrete cross-correlation of the single mass
vector `C` with the single kernel-ceiling vector `U`, evaluated at the target
shifts `a_n`.  Thus the expensive degree-fourteen convolution is performed
once, not once per target.  All fifty targets differ only by certified integer
shifts.  The last retained tuple bins can extend slightly past `R`; adding the
terminal bound (7.7) deliberately double-counts that nonnegative overhang.

### 7.1 Certified realization

The pinned realization uses

\[
 d=14,
 \quad \sigma=2,
 \quad M=10^6,
 \quad h=10^{-4},
 \quad J=824600,
 \quad R=82.46.
 \tag{7.9}
\]

The hash-pinned artifact records:

1. directed-MPFR integer boundaries for all one-factor log bins;
2. dyadic upper masses `beta_j`;
3. an exact FLINT integer convolution for `C=beta^{*14}`;
4. directed enclosures of (7.5) for all `1<=n<=50`;
5. directed kernel ceilings from the minimum of the exact common-numerator
   midpoint/first-derivative theorem and (6.16), with the global `|K|<=1`
   cap for any remaining pole case;
6. exact dyadic dot products in (7.6); and
7. the existing elementary terminal bound beyond `R`.

The width in (7.4) is `(d+1)h=0.0015`, compared with `0.15` in the former
target-enclosed `h=0.01` calculation.  More importantly, the formal midpoint
branch retains cancellation in the exact common-numerator bracket.  Theorem
6.2 independently explains that mechanism and supplies a possible sharper
away-from-poles branch; it is not an unstated input to the frozen table.

The full canonical local reconstruction, including all `725578` directed
kernel intervals, exact convolution, cross-correlation, and consequences,
completed in about `342` seconds with `3.59 GB` maximum resident memory.  Those
resource observations are descriptive and are not mathematical premises.

---

## 8. The formal fine-grid certificate

The exact positive convolution, directed-MPFR kernel ceilings, and exact
cross-correlation certify

\[
 \begin{aligned}
 \tau_{5,>10^6}
 &\le
 \frac{5409849216438953933448898259612643}{2^{128}}
 =1.5898117981810922\ldots\times10^{-5},\\
 \tau_{50,>10^6}
 &\le
 \frac{1612134240806449149224291781115653}{2^{128}}
 =4.7376367320878956\ldots\times10^{-6}.
 \end{aligned}
 \tag{8.1}
\]

They are rigorous upper bounds, not sampled estimates, and replace the former
coarse-bin endpoints:

| target | published remote upper | formal fine-grid upper | improvement |
|---:|---:|---:|---:|
| 5 | `2.8117732435796035e-4` | `1.5898117981810922e-5` | `17.6862x` |
| 50 | `1.9524502867616994e-4` | `4.7376367320878956e-6` | `41.2115x` |

Adding the unchanged Arb sums over `51<=k<=10^6` gives the complete supports

\[
 \begin{aligned}
 \tau_5
 &\le
 \frac{184113379093691304767321860115219}{
 10633823966279326983230456482242756608}
 =1.7313938962834910\ldots\times10^{-5},\\
 \tau_{50}
 &\le
 \frac{1473535587533480688165653123330957}{
 170141183460469231731687303715884105728}
 =8.6606637944060345\ldots\times10^{-6}.
 \end{aligned}
 \tag{8.2}
\]

Exact-rational composition with the Arithmetic Observability VIII Gram data
proves that target 5 remains the unique four-anchor common-box bottleneck and
target 50 remains the unique all-fifty bottleneck.  Their certified radii are

\[
 \boxed{
 \rho_{4,\mathrm{box}}
 \ge0.019991343023375665\ldots,
 \qquad
 \rho_{50,\mathrm{box}}
 \ge0.000195667890740658595\ldots.}
 \tag{8.3}
\]

The remote vector has its unique maximum at target 1,
`4.3721111747776683e-5`; after the finite sums are added, the unique complete-
support maximum is still target 1, at `4.4828243814611756e-5`.  Of the
`725578` aligned kernel intervals, the global unit cap is used on only `618`
intervals for the `T=510` component and `247` for the `T=1780` component.
These counts are proof metadata, not sampled estimates.

The certified integral alias obstruction remains

\[
 \rho_{4,\mathrm{int}}^*
 <0.0199999999977821582051\ldots.
 \tag{8.4}
\]

Section 9 now combines the same formal support vector with the inverse-free
quotient theorem to make the four-anchor lower bound uniform over every
remaining real nonquery prefix.

---

## 9. How the two reductions meet

The quotient theorem changes which response needs a remote certificate.  The
old pair-specific direction `u=c_5` proves a bound only for the adjacent
prefix.  The quotient problem asks for

\[
 \max_{\substack{u\in W^\perp\\\|u\|\le1}}
 \left((u,Ae_5)_{\mathbb R}
 -\sum_{k>50}\frac{d_{14}(k)}{k^2}
 |(u,c_k)_{\mathbb R}|
 \right).
 \tag{9.1}
\]

For any fixed candidate `u`, the finite support through one million is an Arb
sum.  Its remote support can be bounded by either:

- the exact moment hierarchy (4.4), which applies to an arbitrary sample-
  space direction without changing the convolution; or
- the fine positive theorem (7.6), after constructing interval ceilings for
  the finite exponential response `F_u`.

This leads to a falsifiable optimizer-certificate loop.

1. Solve a finite fine-grid approximation of (9.1) for a candidate `u` in
   `W^\perp`.
2. Project and normalize it with certified linear algebra.
3. Enclose its complete finite and remote support.
4. Use the resulting feasible dual value as a global lower bound.
5. Compare it with an explicit integer-prefix and integral-tail primal
   witness.

If the two values meet, the global closest continuous-relaxation fibre is
determined.  If the quotient lower remains substantially smaller, its primal
projection identifies a real nonquery prefix that can guide the residual
integer branch-and-bound.  Either outcome increases understanding; the
method does not presume that `e_5` is globally optimal.

The formal composition now bypasses that optimizer.  The stored certified
Gram-row uppers and nuisance support maximum are

\[
 \begin{aligned}
 q
 &=\frac{257168756981514768514508306559006707}{2^{128}}
 =7.5575105259940080\ldots\times10^{-4},\\
 q_5
 &=\frac{108343607646993126701039729904793}{2^{128}}
 =3.1839324684186703\ldots\times10^{-7},\\
 \tau_W
 &=\frac{6670899940450463606943553795810303}{2^{128}}
 =1.9604012987250635\ldots\times10^{-5}.
 \end{aligned}
 \tag{9.2}
\]

Target 4 is the unique maximizer defining `tau_W`.  The inverse-free estimate
also gives

\[
 \|\beta\|_1
 \le\frac{q_5}{1-q}
 =3.1863405486422468\ldots\times10^{-7}.
 \tag{9.3}
\]

Exact rational arithmetic then produces

\[
 \begin{aligned}
 s_5
 &=0.9999999999998985490687173899\ldots,\\
 P_5
 &=1.7313945209341060\ldots\times10^{-5},\\
 N_5:=\frac{s_5}{25}-P_5
 &=0.03998268605478660090252396198\ldots.
 \end{aligned}
 \tag{9.4}
\]

The displayed decimals are descriptive; the payload stores the reduced exact
rationals for all three quantities and for `N_5^2/(4s_5)`.  Corollary 2.4
therefore proves the uniform global result

\[
 \boxed{
 \rho_{4,\mathrm{global}}
 \ge\frac{N_5}{2\sqrt{s_5}}
 =0.019991343027394314\ldots.}
 \tag{9.5}
\]

The slight numerical excess of (9.5) over the lower bound (8.3) is not a
contradiction: they are two conservative dual lower bounds obtained from
different compositions, and neither is asserted to be exact.

Together with (8.4), both the continuous-box and coefficientwise integral
four-anchor critical radii lie in the certified bracket

\[
 \rho_{4,\mathrm{cont}}^*,\ \rho_{4,\mathrm{int}}^*
 \in[\,0.019991343027394314\ldots,
       0.019999999997782158\ldots\,),
 \tag{9.6}
\]

whose endpoint ratio is below `1.00043304`, a relative gap below `0.043304%`.
This one lower bound covers the entire real nuisance span (2.21), so the
remaining prefix branch search is unnecessary for the stated radius.  The
exact quotient minimizer, the exact vector `beta`, and the identity of an
exact closest integral prefix remain open.

### 9.1 Integral tails and arithmetic realizability

All lower bounds obtained from the continuous zonoid apply to the smaller
coefficientwise integral-tail class.  A primal optimizer of the continuous
problem may be fractional and therefore need not be an integral witness.
Even an integral endpoint sequence satisfying

\[
 0\le a_k\le d_{14}(k)
 \tag{9.7}
\]

need not be the ideal-count sequence of a number field.  The three model
classes remain distinct:

- the continuous coefficient box;
- the independent integral coefficient envelope; and
- coupled arithmetically realizable sequences.

No support computation in this paper collapses those distinctions.

---

## 10. What is proved, computed, and still open

### Proved in this manuscript

- the exact quotient-zonoid primal and support-function dual;
- its use as a uniform lower relaxation for every remaining integer prefix;
- the finite Schur-residual dual certificate (2.18), conditional only on
  certified Gram and per-column support inputs;
- the inverse-free real-Gram corollary (2.24), using only certified row-defect
  and per-column support uppers;
- exact antiperiodicity of every dual response on the pinned sample lattice;
- the exact complex Dirichlet moment identity for the alias-circle measure;
- existence and quantitative convergence of one-sided trigonometric
  support majorants;
- the symmetric second-order cosecant theorem preserving `a_0`;
- a pole-safe shifted-Dirichlet-quotient companion bound;
- the fine-bin target-shift and cross-correlation theorem; and
- the exact quadratic/Cauchy reduction (5.2)--(5.4), whose pinned numerical
  evaluation is separated below.

### Formally certified finite computation

- payload digest
  `f97fb3a484bb4e598558b47d8217be05f31b63fe1925a854b43aecf216a66c6f`;
- the `h=10^-4` degree-fourteen exact FLINT convolution and all `725578`
  directed kernel intervals;
- all fifty exact dyadic remote uppers and complete support uppers;
- the target-5 and target-50 endpoints (8.1)--(8.3), with target 5 and target
  50 remaining the unique four-anchor and all-fifty bottlenecks;
- the exact-rational inverse-free composition (9.2)--(9.5);
- direct projected exclusions exactly for coordinates
  `{4,6,7,...,24}`, leaving `{25,...,50}` to the old branch description; and
- the uniform quotient lower bound, which handles that entire real nuisance
  span without enumerating those remaining branches.

### Exploratory diagnostics, not theorem endpoints

- diagnostic old-grid away and pole decompositions;
- the exploratory quadratic values in (5.5)--(5.6); and
- dense floating kernel evaluations used only as independent audits, never as
  interval-supremum certificates.

### Not yet established

- the exact quotient-zonoid value for the full nonquery prefix span;
- an exact primal or dual optimizer attaining that quotient value;
- equality of the closest integral and continuous fibres;
- realization of an envelope witness by a number field;
- global optimality of the pinned time ensemble or window; or
- any statement about zeta zeros, the Riemann hypothesis, or new physical
  law.

---

## 11. Formal certificate boundary and adversarial checks

The companion package is

```text
arithmetic_observability_alias_circle.py
arithmetic_observability_alias_circle_certificate.json
test_arithmetic_observability_alias_circle.py
```

with schema

```text
arithmetic-observability-alias-circle-v1
```

and pinned payload digest

```text
f97fb3a484bb4e598558b47d8217be05f31b63fe1925a854b43aecf216a66c6f
```

The independent checker reconstructs or validates the following hash-pinned
payload.

1. Exact experiment parameters, component weights, and binary64 window
   coefficients in hexadecimal form.
2. Exact values of `a_0` and `S_2`, recomputed rather than trusted as decimal
   metadata.
3. Directed log-bin boundaries and one-factor dyadic upper masses.
4. The exact degree-fourteen convolution hash and scale.
5. Directed target-log shifts satisfying (7.5).
6. Hashes of both component kernel tables and their exact positive mixture,
   together with counts of intervals that used the global pole cap.
7. Exact dot-product numerators for all fifty targets.
8. The terminal tail and the complete remote vector.
9. Recomputed target-5 and target-50 consequences for the AO-VIII support
   theorem.
10. Exact-rational reconstruction of the certified uppers `q`, `q_5`,
    `tau_5`, and `tau_W`, followed by `s_5`, `P_5`, the positive numerator
    `s_5/25-P_5`, and `D_5^2`; the displayed `D_5` itself is an outward
    interval enclosing its square root.  No Gram inverse is stored.

The principal large-object digests inside that payload are

```text
one-factor bins       556e72133506a3aff44a0fced360b6027b137077c2983ef24770cf58581e442e
degree-14 convolution 634458ec1ff0d2caa8e208ccbcccca717bd435ad8cbb74fb1e458a268d98738d
component T=510      829911343c958db6231a5202c4f0bf12c65b98da53f88fd8860a41db4209856c
component T=1780     cf8daa986fd6556490b38dd0ba57a56b5078627a51a3cef7d75fb9e88d43e4cc
combined kernel       9293e59aee94a299a88003348240036b023df1c8389e944472bd0377920eef61
cross-correlations    871742037ea2a5c1e0e617e5b4ccc4d616be79a810e54a0fb0d5c5feedcfb3c8
```

The hash-pinned JSON is canonical LF data and its dependency hashes refer to raw
bytes.  Until the repository adds line-ending attributes, a byte-identical
Windows reproduction therefore requires a byte-preserving transfer or
checkout, as in the earlier milestones.  A native checkout with
`core.autocrlf=true` lies outside the byte-identical claim; it may reproduce
the mathematics, but it cannot be compared to the pinned raw-file digests.

The checker's rejection and audit surface covers:

- a downward-rounded one-factor mass;
- a missing `d h` tuple-width expansion;
- a target shift that omits the extra one-bin enclosure in (7.8);
- a target-cell index inferred only from binary64 `log(n)` rather than proved
  by directed endpoints, with near-boundary target `n=43` retained as an
  explicit cell regression;
- same-direction endpoint rounding in alias subtraction, with the `q=3`
  counterexample retained as an explicit directed-rounding regression;
- use of (6.8) across a pole;
- an incorrect removable limit in (6.13);
- coefficient sign changes hidden by decimal conversion;
- a nonpositive or nonnormalized ensemble weight;
- mismatched convolution scales or vector lengths;
- duplicate JSON keys, floats in formal integer fields, oversized integers,
  and resource-exhaustion payloads; and
- a certificate regenerated with different library or precision pins.

The moment hierarchy needs a separate checker because its proof objects are
different: pointwise positivity certificates for `P+F` and `P-F`, interval
complex zeta values, the finite complex Dirichlet polynomial, and the real
total in (4.4).

### 11.1 Reproduction

From the repository root, the producer environment is `python-flint 0.9.0`,
`FLINT 3.6.0` with one thread, `gmpy2 2.3.1`, and `MPFR 4.2.2`.  In that
environment, fast verification and the adversarial suite are

```bash
python arithmetic_observability_alias_circle.py \
  --certificate arithmetic_observability_alias_circle_certificate.json

python -m unittest -v test_arithmetic_observability_alias_circle.py
```

The full exact reconstruction of the fine bins, kernel tables, convolution,
cross-correlations, and consequences is

```bash
python arithmetic_observability_alias_circle.py \
  --certificate arithmetic_observability_alias_circle_certificate.json \
  --recompute
```

Normal verification checks the pinned payload and every stored exact
consequence; `--recompute` rebuilds the large proof objects byte for byte.
Passing the verifier certifies only the declared model and fields above, not
the open optimizer or arithmetic-realizability claims.

---

## 12. Sources and novelty boundary

Orthogonal projection, quotient norms, support functions, and separation of
compact convex sets are classical.  The relevant convex background is
described in Rockafellar's *Conjugate Duality and Optimization*
([DOI 10.1137/1.9781611970524](https://doi.org/10.1137/1.9781611970524))
and Schneider's *Convex Bodies: The Brunn--Minkowski Theory*
([DOI 10.1017/CBO9781139003858](https://doi.org/10.1017/CBO9781139003858)).
Fejer summation and Fejer--Riesz factorization are classical trigonometric
analysis.  Vaaler's *Some extremal functions in Fourier analysis* gives a
classical account of extremal Fourier majorants and their number-theoretic
uses
([DOI 10.1090/S0273-0979-1985-15349-2](https://doi.org/10.1090/S0273-0979-1985-15349-2)).
Carneiro and Vaaler's *Some extremal functions in Fourier analysis, II*
includes periodic one-sided approximation by bounded-degree trigonometric
polynomials
([DOI 10.1090/S0002-9947-2010-04886-X](https://doi.org/10.1090/S0002-9947-2010-04886-X)).
Dritschel and Rovnyak survey the classical Fejer--Riesz theorem and its
operator generalizations in *The operator Fejer--Riesz theorem*
([arXiv:0903.3639](https://arxiv.org/abs/0903.3639)).  The generalized divisor
identity `sum d_d(k)k^-s=zeta(s)^d` is classical as well.  In particular, no
novelty is claimed for the existence of one-sided periodic majorants, for the
majorant hierarchy in isolation, or for nonnegative trigonometric
factorization.

This manuscript does not claim those ingredients as new.  The programme-
specific contribution is their composition in the pinned arithmetic-
observability model:

- quotienting a finite prefix nuisance before a compact coefficient zonoid;
- recognizing the exact alias circle of the nested odd-tenth sample lattice;
- turning its Fourier moments into post-cutoff degree-fourteen Dirichlet
  values;
- preserving the designed zeroth window moment by a symmetric cosecant
  remainder; and
- converting the result into a one-convolution, all-target formal certificate
  architecture.

No literature-priority claim is made without independent peer review.

---

## 13. Next research target

The finite certification gate is closed.  The uniform bound (9.5) already
handles the entire remaining real nuisance span, so no branch enumeration is
needed to establish the stated global radius.

The highest-information next calculation is now the exact quotient problem
(9.1).  A certified primal--dual solve can test whether the conservative row-
defect corollary is essentially sharp, exhibit the geometry of the closest
projected zonoid face, and attempt to close the remaining `0.043304%` bracket.
If it meets the integral alias witness, it will identify the continuous
closest fibre and expose the remaining integrality question.  If it does not,
its optimizer will identify the direction in which the support theorem or the
integer witness must improve.

The exact alias-circle majorant hierarchy should be retained as an independent
route for arbitrary quotient dual directions and as a falsification check on
the positive fine-bin certificate.  A later arithmetic-realizability study
must remain separate from both continuous and coefficientwise integral
optimization.

The broader goal remains arithmetic observability: exact equivalence,
quantitative stability, obstruction, and distinguishability geometry under a
declared harmonic protocol.  The present milestone advances that goal by
replacing the dominant remote uncertainty with a formal all-target certificate
and by converting the remaining prefix search into an explicit quotient
geometry.
