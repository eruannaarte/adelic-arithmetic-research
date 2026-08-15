# Arithmetic Observability VI

## Sharp harmonic complexity of a normalized product-Segre patch and exact separation loss under model mismatch

### Status

Research manuscript with reproducible finite certificate, 2026-08-15.

The analytic theorems in Sections 2--4 and 6--8 are proved below.  For the
canonical rational schedule in Section 5, a companion 384-bit Arb verifier
reconstructs all eighteen reduced phases and formally proves the phase-box,
factor-floor, tensor-floor, quotient-floor, and recovery-amplification
inequalities used here.  The certificate checks the finite inputs and
inequalities; it does not mechanize the general analytic theorems.

---

## Abstract

Earlier Arithmetic Observability results showed that a one-parameter
geometric factor at each of `r` primes can be recovered globally from exactly
`r` well-designed complex harmonic readings.  The normalized nonnegative
Segre patch, equivalently the labelled product-simplex model, is much larger:
each factor is now an arbitrary probability vector on `s` exponent states.
Its parameter dimension is `r(s-1)`.

This paper determines its individual complex reading complexity exactly:

\[
 \boxed{m_{\mathrm{harm}}^{\mathrm{prod}}(r,s)
 =r\left\lfloor\frac{s}{2}\right\rfloor.}
 \tag{A.1}
\]

The upper bound is constructive.  A real DFT half-frame recovers one factor,
and prime-log Kronecker approximation produces harmonic times which isolate
each factor arbitrarily accurately.  A uniform derivative estimate turns
that approximation into a global inverse-Lipschitz inequality on the entire
product of simplices.  The lower bound is not merely dimensional.  Coordinate
reversal has an odd subspace of dimension `floor(s/2)` per factor.  On every
small sphere in the resulting `r floor(s/2)`-dimensional space, centered
harmonic readings obey an exact conjugation symmetry.  Borsuk--Ulam therefore
produces exact collisions for every smaller schedule, arbitrarily close to
the uniform product.  This also explains why the apparently spare imaginary
part of the even-`s` Nyquist coefficient cannot be used to lower the global
count.

For `(r,s,p)=(3,4,(2,3,5))`, six rational times with denominator `1000` are
given.  The companion interval certificate proves target-phase error below
`1/1000` and off-axis error below `17/1000`.  Those inequalities imply the
global factor-coordinate floor

\[
 \sqrt2-\frac{9\sqrt{1202}}{500}>0.7901
\]

and an ambient tensor secant floor above `0.4561`.

The second part asks what survives when the source is only *near* a product.
For a linear harmonic map `H`, latent product `p`, source mismatch radius
`rho`, and data-noise radius `epsilon`, the complete uncertainty response set
is

\[
 Hp+H B(\rho)+B(\varepsilon).
\]

Two latent products are pairwise confusable precisely when their response
sets overlap.  With no data noise,
the critical mismatch radius for a pair is exactly half the Hilbert distance
of its secant to `ker H`.  In the induced quotient norm, equal-radius
thickening reduces every pairwise minimum separation by exactly `2 rho`:

\[
 \operatorname{dist}_Q\bigl(Hp+HB(\rho),Hp'+HB(\rho)\bigr)
 =\bigl(\operatorname{dist}(p-p',\ker H)-2\rho\bigr)_+.
 \tag{A.2}
\]

Consequently, for the global class, every positive adversarial mismatch
radius admits collisions: neither the full ambient source nor a declared
latent product is uniformly exactly recoverable under incomplete
observations.  This negative result is quantitative rather than fatal:
restricted secant floors give linear finite-radius recovery, while the sine
of the smallest tangent--kernel principal angle is the exact linearized
minimax constant.  Exact model validity, approximate model validity, and
ambient completion are thereby separated cleanly.

---

## 1. Full normalized product sources

Fix integers

\[
 r\ge1,\qquad s\ge2,\qquad d=s-1,
 \tag{1.1}
\]

and distinct primes `p_1,...,p_r`.  Put

\[
 \lambda_j=\log p_j.
 \tag{1.2}
\]

For a probability vector `q in Delta_{s-1}`, define its finite
characteristic polynomial

\[
 \chi_q(\theta)=\sum_{a=0}^{d}q(a)e^{-ia\theta}.
 \tag{1.3}
\]

The normalized full product model is

\[
 \mathcal P_{r,s}
 =\left\{
   \Psi(q_1,\ldots,q_r)=\bigotimes_{j=1}^r q_j:
   q_j\in\Delta_{s-1}
  \right\}
 \subset\mathbb R^{s^r}.
 \tag{1.4}
\]

This is the nonnegative real part of a Segre variety with every factor
normalized.  The factorization is unique, including on the boundary, because
the one-axis marginals of `Psi(q)` are exactly the labelled factors `q_j`.

For a real time `t`, the arithmetic harmonic reading of a coefficient tensor
`x` is

\[
 H_t x
 =\sum_{\alpha\in\{0,\ldots,d\}^r}
 x_\alpha
 \exp\left(-it\sum_{j=1}^r\alpha_j\lambda_j\right).
 \tag{1.5}
\]

A schedule `T=(t_1,...,t_m)` gives `H_Tx=(H_{t_l}x)_l`.  On a product,

\[
 H_t\Psi(q_1,\ldots,q_r)
 =\prod_{j=1}^r\chi_{q_j}(\lambda_jt).
 \tag{1.6}
\]

### Definition 1.1 — product-harmonic reading complexity

Let `m_harm^prod(r,s)` be the least number of individual complex readings for
which some fixed, nonadaptive real schedule `T` makes `H_T` globally
injective on `P_{r,s}`.  One reading means one exact complex scalar, hence two
real coordinates.  This notation is specific to the present observation
family; it is not proposed as a standard invariant of the projective Segre
variety.

The normalization matters.  There is no unknown common amplitude in this
definition.  The unknown real dimension is `r(s-1)`, rather than the `r`
shape parameters of the geometric-factor model in Arithmetic Observability
V.

### 1.1 Three geometries that must not be conflated

For `p,p' in P_{r,s}`, three different quantities will occur:

1. the ambient tensor distance `||p-p'||`;
2. the raw observation distance `||H_T(p-p')||`; and
3. the quotient distance `dist(p-p',ker H_T)`.

The raw distance controls ordinary data noise.  The quotient distance
controls how efficiently an ambient source perturbation can cancel a product
secant.  They are comparable in finite dimension but they answer different
questions.

---

## 2. The real DFT half-frame

Put

\[
 k=\left\lfloor\frac{s}{2}\right\rfloor,
 \qquad
 \omega_l=\frac{2\pi l}{s},
 \quad 1\le l\le k.
 \tag{2.1}
\]

For a real zero-sum vector `h in R^s`, write

\[
 \widehat h_l=\sum_{a=0}^{s-1}h(a)e^{-ia\omega_l}.
 \tag{2.2}
\]

### Lemma 2.1 — half-DFT lower frame bound

For every real `h` with `sum_a h(a)=0`,

\[
 \boxed{
 \sum_{l=1}^{k}|\widehat h_l|^2
 \ge \frac{s}{2}\|h\|_2^2.}
 \tag{2.3}
\]

When `s` is odd, equality holds.  When `s` is even, the unpaired Nyquist
coefficient can only increase the left side relative to this lower bound.

#### Proof

The zero-frequency DFT coefficient vanishes.  Parseval gives

\[
 \sum_{l=0}^{s-1}|\widehat h_l|^2=s\|h\|_2^2.
 \tag{2.4}
\]

Because `h` is real, frequencies `l` and `s-l` have equal squared modulus.
If `s=2k+1`, every nonzero frequency occurs in one of `k` conjugate pairs,
so the selected half has exactly half the total energy.  If `s=2k`, the
frequency `k` is real and unpaired, hence

\[
 2\sum_{l=1}^{k-1}|\widehat h_l|^2+|\widehat h_k|^2
 =s\|h\|_2^2.
\]

Adding the Nyquist energy with coefficient one rather than one half proves
(2.3).  \(\square\)

### 2.1 The ideal factor-isolating experiment

Index `M=rk` ideal readings by `(j,l)` and define

\[
 G_{jl}(q_1,\ldots,q_r)=\chi_{q_j}(\omega_l).
 \tag{2.5}
\]

For `h=(h_1,...,h_r)` in the product of zero-sum factor spaces, Lemma 2.1
gives

\[
 \boxed{
 \|DG(h)\|_2
 \ge\sqrt{\frac{s}{2}}
 \left(\sum_{j=1}^r\|h_j\|_2^2\right)^{1/2}.}
 \tag{2.6}
\]

The ideal map is linear in the factor coordinates and globally injective.
It is not itself generally a finite-time arithmetic schedule: it asks for
one prime phase to equal `omega_l` while every other prime phase equals zero.
The next section shows that a sufficiently close genuine schedule inherits
the global lower bound.

---

## 3. Quantitative harmonic isolation

For every row `(j,l)`, choose integer windings and phase lifts

\[
 \theta_{jl,a}=\lambda_a t_{jl}-2\pi n_{jl,a}.
 \tag{3.1}
\]

### Definition 3.1 — asymmetric DFT-isolating schedule

A schedule is `(tau,delta)` DFT-isolating when

\[
 |\theta_{jl,j}-\omega_l|\le\tau,
 \qquad
 |\theta_{jl,a}|\le\delta\quad(a\ne j)
 \tag{3.2}
\]

for every row.  The distinction between target error `tau` and off-axis
error `delta` is useful for rational rounding.

Put

\[
 E_{r,s}(\tau,\delta)
 =d\sqrt{sM}
 \sqrt{\bigl(\tau+(r-1)\delta\bigr)^2
       +(r-1)\delta^2}.
 \tag{3.3}
\]

### Theorem 3.2 — global DFT perturbation theorem

If a `(tau,delta)` DFT-isolating schedule satisfies

\[
 E_{r,s}(\tau,\delta)<\sqrt{\frac{s}{2}},
 \tag{3.4}
\]

then for all factor tuples `q,q'`,

\[
 \boxed{
 \|H_T(\Psi(q)-\Psi(q'))\|_2
 \ge c_{\rm fac}\|q-q'\|_{\rm fac},}
 \tag{3.5}
\]

where

\[
 c_{\rm fac}
 =\sqrt{\frac{s}{2}}-E_{r,s}(\tau,\delta)>0,
 \qquad
 \|q-q'\|_{\rm fac}^2
 =\sum_j\|q_j-q'_j\|_2^2.
 \tag{3.6}
\]

Moreover,

\[
 \boxed{
 \|H_T(p-p')\|_2
 \ge \frac{c_{\rm fac}}{\sqrt r}\|p-p'\|_2
 \quad(p,p'\in\mathcal P_{r,s}).}
 \tag{3.7}
\]

In particular, the schedule is globally injective on the entire closed
product of simplices, including every boundary stratum.

#### Proof

For a probability vector `q`,

\[
 |\chi_q(\theta)|\le1,
 \qquad
 |\chi_q(\theta)-1|\le d|\theta|.
 \tag{3.8}
\]

For a real zero-sum vector `h`,

\[
 |\widehat h(\theta)|
 =\left|\sum_a h(a)(e^{-ia\theta}-1)\right|
 \le d\sqrt s\,|\theta|\|h\|_2,
 \tag{3.9}
\]

and

\[
 |\widehat h(\theta)-\widehat h(\omega)|
 \le d\sqrt s\,|\theta-\omega|\|h\|_2.
 \tag{3.10}
\]

At a row targeting axis `j`, differentiation of the product gives

\[
 DF_{jl}(q)h
 =\sum_{a=1}^r
 \widehat h_a(\theta_{jl,a})
 \prod_{b\ne a}\chi_{q_b}(\theta_{jl,b}).
 \tag{3.11}
\]

The target term differs from `widehat h_j(omega_l)` by at most

\[
 d\sqrt s\bigl(\tau+(r-1)\delta\bigr)\|h_j\|_2.
 \tag{3.12}
\]

Indeed, (3.10) handles target-phase displacement, while

\[
 \left|\prod_{b\ne j}\chi_{q_b}(\theta_{jl,b})-1\right|
 \le(r-1)d\delta
 \tag{3.13}
\]

handles the off-axis multiplier.  Each off-axis derivative term is at most

\[
 d\sqrt s\,\delta\|h_a\|_2.
 \tag{3.14}
\]

Cauchy--Schwarz in the factor blocks therefore yields the row bound

\[
 |(DF-DG)_{jl}h|
 \le d\sqrt s
 \sqrt{(\tau+(r-1)\delta)^2+(r-1)\delta^2}
 \|h\|_{\rm fac}.
 \tag{3.15}
\]

Stacking `M` rows gives

\[
 \|DF(q)-DG\|\le E_{r,s}(\tau,\delta)
 \tag{3.16}
\]

uniformly over the product of simplices.  Integrate along the straight
factor-coordinate segment from `q'` to `q`, use (2.6), and apply the reverse
triangle inequality.  This proves (3.5).

Finally, tensor telescoping and `||q_j||_2<=1` give

\[
 \|\Psi(q)-\Psi(q')\|_2
 \le\sum_j\|q_j-q'_j\|_2
 \le\sqrt r\|q-q'\|_{\rm fac},
 \tag{3.17}
\]

which proves (3.7).  \(\square\)

### Corollary 3.3 — exact-target prime-log schedules exist

For every `delta>0`, there is a DFT-isolating schedule with `tau=0` and
`M=r floor(s/2)` distinct times.

#### Proof

Fix a target pair `(j,l)` and impose the target phase exactly by setting

\[
 t_n=\frac{\omega_l+2\pi n}{\lambda_j},
 \qquad n\in\mathbb Z.
 \tag{3.18}
\]

The off-axis phases are the discrete orbit

\[
 \left(
 (n+\omega_l/(2\pi))\frac{\lambda_a}{\lambda_j}
 \right)_{a\ne j}pmod1.
 \tag{3.19}
\]

The numbers `1` and `lambda_a/lambda_j` for `a!=j` are rationally
independent: a rational relation would become a rational relation among the
prime logarithms after multiplication by `lambda_j`, contradicting unique
factorization.  Kronecker's theorem makes (3.19) dense in the off-axis torus.
Choose a sufficiently accurate and previously unused integer `n` for each
row.  \(\square\)

For `tau=0`, (3.3) simplifies to

\[
 E_{r,s}(0,\delta)
 =d\sqrt{sMr(r-1)}\,\delta,
 \tag{3.20}
\]

which can be made arbitrarily small.  Thus the upper construction is not
merely generic: it has a global quantitative margin.

---

## 4. Reflection symmetry gives the sharp lower bound

Let `R:R^s->R^s` reverse coordinates:

\[
 (Rq)(a)=q(d-a).
 \tag{4.1}
\]

Its antisymmetric subspace is

\[
 \mathcal A_-={b:Rb=-b\}.
 \tag{4.2}
\]

Every vector in `A_-` has zero sum, and

\[
 \dim\mathcal A_-=\left\lfloor\frac{s}{2}\right\rfloor=k.
 \tag{4.3}
\]

Put `u=s^{-1}1`.  For sufficiently small `b in A_-`, both `u+b` and
`u-b` are strictly positive probability vectors, and

\[
 u-b=R(u+b).
 \tag{4.4}
\]

Reversal has the exact Fourier identity

\[
 \chi_{Rq}(\theta)
 =e^{-id\theta}\overline{\chi_q(\theta)}.
 \tag{4.5}
\]

For `b=(b_1,...,b_r) in A_-^r`, define

\[
 q_j(b)=u+b_j,
 \qquad
 F_b(t)=H_t\Psi(q_1(b),\ldots,q_r(b)),
 \tag{4.6}
\]

and center the deterministic reversal phase by

\[
 B_b(t)
 =e^{id\Lambda t/2}F_b(t),
 \qquad
 \Lambda=\sum_{j=1}^r\lambda_j.
 \tag{4.7}
\]

Equation (4.5) gives

\[
 \boxed{B_{-b}(t)=\overline{B_b(t)}.}
 \tag{4.8}
\]

### Theorem 4.1 — every-radius reflection collision

For every schedule of

\[
 m\le rk-1
 \tag{4.9}
\]

complex readings and every sufficiently small radius `rho>0`, there is a
nonzero `b in A_-^r` with `||b||_2=rho` such that

\[
 H_T\Psi(u+b_1,\ldots,u+b_r)
 =H_T\Psi(u-b_1,\ldots,u-b_r).
 \tag{4.10}
\]

The two product tensors are distinct and converge to the uniform product as
`rho` tends to zero.

#### Proof

The sphere of radius `rho` in `A_-^r` is `S^{rk-1}`.  Define

\[
 \Gamma_T(b)
 =\bigl(\Im B_b(t_1),\ldots,\Im B_b(t_m)\bigr)
 \in\mathbb R^m.
 \tag{4.11}
\]

Equation (4.8) makes `Gamma_T` continuous and odd.  Borsuk--Ulam gives a
zero whenever `m<=rk-1`.  At such a nonzero `b`, every centered reading is
real, so (4.8) yields `B_b(t_l)=B_{-b}(t_l)` for all rows.  Undoing the same
known centering phase on both sides proves (4.10).  At least one factor
marginal differs because `b` is nonzero, so the product tensors are
distinct.  \(\square\)

### Theorem 4.2 — exact labelled product-simplex complexity

For all `r>=1` and `s>=2`,

\[
 \boxed{
 m_{\rm harm}^{\rm prod}(r,s)
 =r\left\lfloor\frac{s}{2}\right\rfloor.}
 \tag{4.12}
\]

#### Proof

Theorem 4.1 rules out every smaller count.  Corollary 3.3 and Theorem 3.2
give a globally injective schedule at the displayed count.  \(\square\)

### 4.1 Why dimension counting is not the whole lower bound

The interior factor space is an open subset of `R^{r(s-1)}`.  If a schedule
were globally injective, its restriction to that interior would be a
continuous injection into `C^m=R^{2m}`.  If `2m<r(s-1)`, pad the target by
zeros to `R^{r(s-1)}`; invariance of domain would force the image to be open,
although it lies in a proper linear subspace.  Hence

\[
 m\ge\left\lceil\frac{r(s-1)}2\right\rceil.
 \tag{4.13}
\]

For odd `s`, this agrees with (4.12).  For even `s`, it is weaker.  The
apparently unused imaginary coordinate of a Nyquist reading does not permit
pairwise packing of the remaining real parameters: the reversal-odd sphere
has dimension `rs/2`, and every reading supplies only one odd real equation
in the exact conjugation argument.  The obstruction is an exact collision,
not merely a rank defect.

---

## 5. Canonical six-reading certificate

Take

\[
 (r,s,p_1,p_2,p_3)=(3,4,2,3,5),
 \qquad
 (\omega_1,\omega_2)=\left(\frac\pi2,\pi\right).
 \tag{5.1}
\]

The sharp count is six.  Consider the exact rational schedule

\[
 \boxed{
 T=(90540.692,\ 220023.423,\ 27819.627,\
    94581.299,\ 18084.130,\ 75110.287).}
 \tag{5.2}
\]

Each decimal in (5.2) denotes the displayed integer divided by `1000`.
Use the target ordering

\[
 (1,\pi/2),(1,\pi),(2,\pi/2),(2,\pi),(3,\pi/2),(3,\pi)
 \tag{5.3}
\]

and the winding matrix

\[
 N=
 \begin{pmatrix}
  9988&15831&23192\\
 24272&38471&56359\\
  3069& 4864& 7126\\
 10434&16537&24227\\
  1995& 3162& 4632\\
  8286&13133&19239
 \end{pmatrix}.
 \tag{5.4}
\]

The reduced phases `t_l(log 2,log 3,log 5)-2pi N_l` evaluate numerically to

\[
 \begin{pmatrix}
 1.570537636686&0.010257754376&-0.011321290117\\
 3.141533735301&0.014350115734&-0.002127609288\\
 0.000311545179&1.570754241630&-0.016095386399\\
 0.005240435369&3.141934763973&-0.002019174376\\
 0.009034556249&0.015506569770&1.570092531043\\
 0.010209808259&0.011664399057&3.141386778083
 \end{pmatrix}.
 \tag{5.5}
\]

### Finite certificate 5.1

The companion verifier uses directed interval arithmetic to prove for all six
rows that

\[
 |\theta_{jl,j}-\omega_l|<\frac1{1000},
 \qquad
 |\theta_{jl,a}|<\frac{17}{1000}\quad(a\ne j).
 \tag{5.6}
\]

No rounded display in (5.5) is to be used as proof of (5.6).

### Corollary 5.2 — certified canonical global floor

The certified inequalities (5.6) imply that the schedule (5.2) is globally
injective on `P_{3,4}` and

\[
 \boxed{
 \|H_T(\Psi(q)-\Psi(q'))\|_2
 \ge
 \left(\sqrt2-\frac{9\sqrt{1202}}{500}\right)
 \|q-q'\|_{\rm fac}.}
 \tag{5.7}
\]

The factor floor is approximately `0.7901558727`.  In ambient tensor norm,

\[
 \boxed{
 \|H_T(p-p')\|_2
 \ge
 \frac{\sqrt2-9\sqrt{1202}/500}{\sqrt3}
 \|p-p'\|_2,}
 \tag{5.8}
\]

whose coefficient is approximately `0.4561967058`.

#### Proof

Insert `r=3`, `s=4`, `M=6`, `tau=1/1000`, and `delta=17/1000` in
(3.3).  Since

\[
 \left(\frac1{1000}+2\frac{17}{1000}\right)^2
 +2\left(\frac{17}{1000}\right)^2
 =\frac{1803}{10^6},
\]

one obtains

\[
 E_{3,4}=\frac{9\sqrt{1202}}{500}<\sqrt2.
 \tag{5.9}
\]

Theorem 3.2 gives both claims.  \(\square\)

### 5.1 A conservative quotient-secant consequence

Let `V` be the zero-mass subspace of `R^64` and realify `H_T|_V`.  Every
complex harmonic row has Euclidean norm `8`, so

\[
 \|H_T|_V\|\le8\sqrt6.
 \tag{5.10}
\]

The certified bounds (5.8) and (5.10) imply

\[
 \frac{\operatorname{dist}(p-p',\ker(H_T|_V))}{\|p-p'\|_2}
 \ge
 \frac{\sqrt2-9\sqrt{1202}/500}{24\sqrt2}
 >0.02328.
 \tag{5.11}
\]

This bound is deliberately conservative: it converts raw separation to
quotient separation using only the full operator norm.  Section 8 gives a
much stronger local angle bound at the uniform product.

---

## 6. Exact response sets for a near-product model

The rest of the paper is independent of the particular schedule in Section
5.  Let `X` and `Y` be finite-dimensional real Hilbert spaces, let
`V subseteq X` be the linear space of admissible source differences, and let

\[
 H:X\longrightarrow Y
 \tag{6.1}
\]

be linear.  A complex observation space is realified.  Let `M` be a declared
latent model contained in an affine translate `x_0+V`.  In the probability
application, `X` is the full coefficient space and `V` is its zero-mass
subspace.  From this point onward, `ker H`, `H^dagger`, and `||H||` in a
source-difference formula mean the kernel, pseudoinverse, and norm of the
restriction `H|_V`.  This convention removes an irrelevant known affine
offset while keeping expressions such as `Hp` well-defined.

For latent `p in M`, source mismatch `e`, and data noise `eta`, observe

\[
 y=H(p+e)+\eta,
 \qquad
 \|e\|_V\le\rho,
 \qquad
 \|\eta\|_Y\le\varepsilon.
 \tag{6.2}
\]

The declared uncertainty response set is

\[
 \mathcal F_p^{\rho,\varepsilon}
 =Hp+HB_V(\rho)+B_Y(\varepsilon).
 \tag{6.3}
\]

This symmetric affine tube is the exact local model whenever positivity is
inactive.  For probability sources it is always a valid outer model; at a
strictly positive tensor, all sufficiently small constructed perturbations
remain feasible.

### Theorem 6.1 — exact response-set overlap criterion

For two latent objects `p,p'`, the following are equivalent:

1. their uncertainty response sets intersect;
2. one has

   \[
   H(p-p')\in HB_V(2\rho)+B_Y(2\varepsilon);
   \tag{6.4}
   \]

3. one has

   \[
   \operatorname{dist}_Y
   \bigl(H(p-p'),HB_V(2\rho)\bigr)
   \le2\varepsilon.
   \tag{6.5}
   \]

When `epsilon=0`, these conditions reduce exactly to

\[
 \boxed{
 \operatorname{dist}_V(p-p',\ker H)\le2\rho.}
 \tag{6.6}
\]

Therefore the exact source-mismatch radius at which this particular pair can
first collide is

\[
 \boxed{
 \rho_{\rm crit}(p,p')
 =\frac12\operatorname{dist}_V(p-p',\ker H).}
 \tag{6.7}
\]

#### Proof

Two response-set elements agree exactly when

\[
 H(p-p')+H(e-e')+(\eta-\eta')=0.
\]

Because a difference of two radius-`rho` balls is the radius-`2rho` ball,
and similarly for `epsilon`, this is equivalent to (6.4).  Compactness of the
finite-dimensional balls makes (6.4) equivalent to (6.5).

At zero data noise, (6.4) says that there is a vector `v` of norm at most
`2rho` for which `H(p-p'-v)=0`.  Minimizing over such representatives is
exactly the distance to `ker H`, proving (6.6)--(6.7).  \(\square\)

### Theorem 6.2 — exact quotient-norm separation loss

Put `K=ker(H|_V)`, let `P=P_{K^perp}` on `V`, and give `ran(H|_V)` the
quotient norm induced by the selected source Hilbert norm,

\[
 \|z\|_Q
 =\min_{\substack{v\in V\\Hv=z}}\|v\|_V
 =\|H^\dagger z\|_V.
 \tag{6.8}
\]

Give the affine data coset `Hx_0+ran(H|_V)` the corresponding
translation-invariant metric, so the distance of two points is the quotient
norm of their difference.

Define

\[
 d_Q(p,p')
 =\|P(p-p')\|_V
 =\operatorname{dist}_V(p-p',K).
 \tag{6.9}
\]

For subsets `A,B` of the affine data coset, write

\[
 \operatorname{dist}_Q(A,B)
 =\inf_{a\in A,\,b\in B}\|a-b\|_Q,
 \tag{6.9a}
\]

the infimal separation gap, not the Hausdorff distance.

Then

\[
 \boxed{
 \operatorname{dist}_Q
 \bigl(Hp+HB_V(\rho),Hp'+HB_V(\rho)\bigr)
 =\bigl(d_Q(p,p')-2\rho\bigr)_+.}
 \tag{6.10}
\]

If data noise lies in `ran(H|_V)` and is itself bounded by `epsilon_Q` in the
quotient norm, the right side becomes

\[
 \bigl(d_Q(p,p')-2\rho-2\varepsilon_Q\bigr)_+.
 \tag{6.11}
\]

#### Proof

The image `HB_V(rho)` is exactly the radius-`rho` ball in `ran(H|_V)` under
the quotient norm.  Translation-invariant distance between two equal balls
in a normed space is the positive part of the center distance minus twice
the radius.  The quotient distance between the centers is (6.9).  \(\square\)

Equation (6.10) is the precise linear loss of minimum separation under
equal-radius thickening.  It is not a first-order approximation.  The
positive-part expression is only a pairwise separation gap; it need not be a
metric or pseudometric on the latent model.

---

## 7. Robust secants, recovery, and immediate impossibility

Define the global quotient-secant floor

\[
 \alpha_Q(H,\mathcal M)
 =\inf_{p\ne p'\in\mathcal M}
 \frac{d_Q(p,p')}{\|p-p'\|_V}
 \tag{7.1}
\]

and the raw observation floor

\[
 c_Y(H,\mathcal M)
 =\inf_{p\ne p'\in\mathcal M}
 \frac{\|H(p-p')\|_Y}{\|p-p'\|_V}.
 \tag{7.2}
\]

Assume `H|_V` is nonzero.  Because `H(p-p')=HP(p-p')`,

\[
 \boxed{
 \alpha_Q(H,\mathcal M)
 \ge\frac{c_Y(H,\mathcal M)}{\|H\|}.}
 \tag{7.3}
\]

### Corollary 7.1 — finite-radius latent ambiguity bound

If `alpha_Q>0`, every zero-data-noise ambiguous latent pair at mismatch
radius `rho` satisfies

\[
 \boxed{
 \|p-p'\|_V\le\frac{2\rho}{\alpha_Q}.}
 \tag{7.4}
\]

For the certified canonical constants (5.6), the conservative consequence
of (5.11) is

\[
 \|p-p'\|_2<85.91\,\rho.
 \tag{7.5}
\]

The large coefficient records the use of a global operator-norm conversion;
it is not asserted to be close to optimal.

### Theorem 7.2 — explicit near-model decoder

Suppose

\[
 y=H(p+e)+\eta,
 \qquad
 p\in\mathcal M,
 \quad\|e\|\le\rho,
 \quad\|\eta\|\le\varepsilon,
 \tag{7.6}
\]

and choose any least-residual model fit

\[
 \widehat p\in\arg\min_{q\in\mathcal M}\|Hq-y\|_Y.
 \tag{7.7}
\]

If `M` is compact and `c_Y>0`, then

\[
 \boxed{
 \|\widehat p-p\|_V
 \le\frac{2(\|H\|\rho+\varepsilon)}{c_Y}.}
 \tag{7.8}
\]

#### Proof

The true product has residual at most `||H||rho+epsilon`, so the minimizer
does too.  The triangle inequality gives

\[
 \|H(\widehat p-p)\|
 \le2(\|H\|\rho+\varepsilon).
\]

Apply the restricted raw secant floor.  \(\square\)

For the certified canonical schedule, (7.8) becomes the explicit, though
conservative, bound

\[
 \|\widehat p-p\|_2
 <85.91\,\rho+4.385\,\varepsilon.
 \tag{7.9}
\]

### 7.1 Exact minimax obstruction set

Define

\[
 \Omega(\rho,\varepsilon)
 =\sup\left\{
 \|p-p'\|:
 p,p'\in\mathcal M,
 H(p-p')\in HB_V(2\rho)+B_Y(2\varepsilon)
 \right\}.
 \tag{7.10}
\]

Every decoder has worst-case latent error at least

\[
 \boxed{\frac12\Omega(\rho,\varepsilon).}
 \tag{7.11}
\]

Indeed, every pair in (7.10) has a common admissible datum, and any answer at
that datum is at least half the pair distance from one endpoint.  Conversely,
a decoder which selects any model point compatible with the datum has error
at most `Omega`.  Thus (7.10), rather than a condition number alone, is the
exact adversarial obstruction set.

### Theorem 7.3 — ambient near-product sources are never exact

Suppose `ker H` contains a nonzero zero-mass vector and `p_0` is a strictly
positive probability tensor.  Then for every `rho>0` there are two distinct
probability sources within distance `rho` of `p_0` which give exactly the
same noiseless observations.

#### Proof

Choose nonzero `v in ker H` in the zero-mass space.  For sufficiently small
positive `t`, the tensors `p_0+tv` and `p_0-tv` remain nonnegative, lie inside
the declared tube, and have the same image under `H`.  \(\square\)

For six complex readings on the canonical `64`-coefficient probability
space, the realified kernel in the `63`-dimensional zero-mass space has
dimension at least

\[
 63-12=51.
 \tag{7.12}
\]

Thus the obstruction is unavoidable even though the six readings are
globally injective on the product model.

### Theorem 7.4 — a declared latent product is never exact at positive radius

Let `M` contain a nonconstant smooth curve of strictly positive products.
For every `rho>0`, there are distinct nearby latent products `p,p' in M` and
admissible source perturbations `e,e'` of norm below `rho` such that

\[
 H(p+e)=H(p'+e').
 \tag{7.13}
\]

This remains true even if `H` is exactly injective on `M`.

#### Proof

Choose distinct products sufficiently close that

\[
 \|P(p-p')\|<2\rho,
\]

where `P` projects onto `(ker H)^perp`.  Put `w=P(p-p')` and choose

\[
 e=-\frac w2,
 \qquad
 e'=\frac w2.
 \tag{7.14}
\]

Then both perturbations have norm below `rho` and

\[
 (p+e)-(p'+e')=(p-p')-w\in\ker H.
\]

Because the products and perturbations can be chosen arbitrarily close to a
strictly positive point, both perturbed sources remain probability tensors.
\(\square\)

Theorems 7.3 and 7.4 are different.  The first says the *actual ambient
source* is hidden along a fixed kernel.  The second says the *declared latent
product* can be traded against admissible mismatch.  Neither contradicts the
linear recovery bounds: exact identity is lost immediately, while ambiguity
diameter still tends to zero linearly with `rho`.

---

## 8. Tangent--kernel angle and the sharp local mismatch constant

Let `p` be a smooth point of a model manifold `M`.  Define

\[
 \mu(p)
 =\inf_{\substack{v\in T_p\mathcal M\\\|v\|=1}}
 \|P v\|,
 \qquad P=P_{(\ker H)^\perp}.
 \tag{8.1}
\]

This is the sine of the smallest principal angle between the model tangent
and the observation kernel.

### Theorem 8.1 — exact linearized minimax radius

In the tangent experiment

\[
 y=H(v+e),
 \qquad v\in T_p\mathcal M,
 \qquad\|e\|\le\rho,
 \tag{8.2}
\]

the exact worst-case minimax error for recovering `v` is

\[
 \boxed{R^*_{\rm tan}(p,\rho)=\frac{\rho}{\mu(p)}}
 \tag{8.3}
\]

when `mu(p)>0`.  If `mu(p)=0` and the tangent parameter is unbounded, the
zero-noise minimax error is infinite.

#### Proof

Exact `H`-data determine `P(v+e)` and conversely, because `H=HP`.  Moreover,
`Pe` fills the entire radius-`rho` ball in `(ker H)^perp`.  The effective
linear map is therefore

\[
 P|_{T_p\mathcal M}:T_p\mathcal M\longrightarrow(\ker H)^\perp
\]

with adversarial observation noise of radius `rho`.  Its smallest singular
value is `mu(p)`.  The exact linear minimax factorization theorem from
Arithmetic Observability I gives (8.3), including the matching two-point
lower bound.  \(\square\)

### Proposition 8.2 — nonlinear small-tube asymptotics

Let `M` be a compact `C^2` embedded manifold without boundary.  Fix
`p_ref in x_0+V` and suppose the translated map `p -> P(p-p_ref)` is an
embedding.  Put

\[
 \mu_*=\min_{p\in\mathcal M}\mu(p)>0.
 \tag{8.4}
\]

For exact observations of `P(p-p_ref+e)` with `||e||<=rho`, let `R^*(rho)`
be the minimax error for recovering `p`.  Then

\[
 \boxed{
 \lim_{\rho\downarrow0}\frac{R^*(\rho)}{\rho}
 =\frac1{\mu_*}.}
 \tag{8.5}
\]

#### Proof

The translated image

\[
 \mathcal N=\{P(p-p_{\rm ref}):p\in\mathcal M\}
\]

is a compact embedded `C^2` manifold and has a uniform tubular neighborhood.
In that neighborhood, compose nearest-point projection onto `mathcal N` with the
smooth inverse of the translated restriction of `P`.  At the image of `p`,
the derivative of this decoder is the pseudoinverse of `P|_{T_pM}` after
tangent projection, whose norm is `1/mu(p)`.  Uniform differentiability on
the compact manifold gives worst-case error

\[
 \rho/\mu_*+o(\rho).
\]

For the lower bound, take a point and unit tangent direction attaining
`mu_*`, and a smooth curve `gamma` through that point with the selected
tangent.  Given `eta>0`, for every sufficiently small positive `t`,

\[
 \frac12\|\gamma(t)-\gamma(-t)\|\ge(1-\eta)t,
 \qquad
 \frac12\|P(\gamma(t)-\gamma(-t))\|
 \le(\mu_*+\eta)t.
\]

For every sufficiently small `rho`, set `t=rho/(mu_*+eta)`.  The midpoint of
the two quotient observations is then admissible for both curve points at
radius `rho`, so every decoder incurs error at least

\[
 \frac{1-\eta}{\mu_*+\eta}\rho.
\]

This proves the required lower limit for all small radii; let `eta` decrease
to zero.  \(\square\)

The full product of closed simplices has corners, so Proposition 8.2 is not
invoked globally for that set without an additional stratified-boundary
argument.  The exact tangent theorem applies at every strictly positive
product, including the uniform point.

### 8.1 A certified analytic angle bound at the canonical uniform product

At the uniform `4^3` tensor, the product tangent has dimension nine.  Let
`R_0` be the full twelve-row realification of the six ideal complex DFT rows,
orthogonally restricted to the zero-mass source space.  Its three imaginary
rows at `pi` vanish; the remaining nine rows span the product tangent.  Thus
`R_0` has rank nine and smallest positive singular value `4 sqrt(2)`.

Under the certified phase boxes (5.6), relative to its ideal row every harmonic
coefficient changes phase by at most

\[
 d\bigl(\tau+(r-1)\delta\bigr)
 =3\left(\frac1{1000}+2\frac{17}{1000}\right)
 =\frac{21}{200}.
 \tag{8.6}
\]

Let `R` be the corresponding full twelve-row realification of the six actual
complex rows, again restricted to the zero-mass space.  The Frobenius
perturbation is at most

\[
 \sqrt{6\cdot64}\,2\sin\frac{21}{400}.
 \tag{8.7}
\]

because the squared real and imaginary differences of one coefficient sum to
the squared complex chord, so each of the six complex rows is counted once.
Restriction to the zero-mass source space is an orthogonal projection and
cannot enlarge this estimate.  A unit tangent vector can be written as
`R_0^T c` with

\[
 \|c\|_2\le\frac1{4\sqrt2}.
 \tag{8.7a}
\]

The vector `R^T c` lies in the actual harmonic row space, and its distance
from the original tangent vector is at most the bound in (8.7) divided by
`4 sqrt(2)`.

Dividing by `4 sqrt(2)` gives the subspace-gap bound

\[
 \zeta=4\sqrt3\sin\frac{21}{400}<1.
 \tag{8.8}
\]

Indeed, `sin x<x` for positive `x` gives

\[
 48\sin^2(21/400)<\frac{1323}{10000}.
 \tag{8.8a}
\]

Every unit tangent vector lies within distance `zeta` of the actual harmonic
row space.  Orthogonal decomposition then yields

\[
 \boxed{
 \mu(p_{\rm unif})
 \ge\sqrt{1-48\sin^2(21/400)}
 >\frac{9315}{10000}.}
 \tag{8.9}
\]

Here `8677/10000>(9315/10000)^2`, so the last rational inequality follows
from (8.8a).  The exact linearized mismatch factor is consequently below
`10000/9315<1.074`, far better than the crude global quotient conversion
(5.11).

A direct floating evaluation of the actual quotient Gram gives a tentative
smallest eigenvalue near `0.999387`.  A suitable independent finite target is

\[
 \lambda_{\min}
 \bigl(J^TP_{\operatorname{row}(H_T|_V)}J\bigr)
 >\frac{999}{1000},
 \tag{8.10}
\]

where `J` is an orthonormal uniform-product tangent basis.  The numerical
value is not used in any proved theorem here.

---

## 9. What geometry has been exposed?

The exact-model theorem and the tube theorem answer different questions.

For `rho=0`, the relevant set is the normalized product secant set.  The
DFT-isolating harmonic map avoids every nonzero secant, and reflection shows
the reading count is sharp.  For `rho>0`, the response of each latent point
is no longer a point: it is a translated image ball.  Pairwise confusability
is therefore governed by the distance of a secant to the ambient kernel.

There are consequently three scales of geometry:

1. **global exact geometry:** whether a model secant lies in the kernel;
2. **finite-radius robust geometry:** the quotient secant floor and the full
   ambiguity modulus `Omega(rho,epsilon)`; and
3. **infinitesimal geometry:** the principal angle between the tangent and
   the kernel.

The first is binary, the second is nonlinear and pairwise, and the third is
the sharp small-mismatch limit.  A large ambient kernel is compatible with
all three facts: exact recovery on the model, stable approximate recovery
near the model, and complete impossibility of exact ambient completion.

---

## 10. Validity ledger

### Proved analytically in this manuscript

1. the half-DFT frame inequality;
2. the quantitative global DFT perturbation theorem;
3. existence of arbitrarily accurate exact-target prime-log schedules;
4. the every-radius reflection collision for every smaller schedule;
5. the exact count
   `m_harm^prod(r,s)=r floor(s/2)`;
6. the exact response-set overlap criterion and pairwise critical mismatch
   radius;
7. exact quotient-norm minimum-separation loss by `2 rho`;
8. finite-radius secant and least-residual recovery bounds;
9. ambient-source and declared-latent nonidentifiability for every positive
   adversarial mismatch radius;
10. the exact tangent linearized minimax constant; and
11. the nonlinear small-tube asymptotic under the stated compact smooth
    embedding hypotheses.

### Formally interval-certified finite claims

1. all eighteen reduced-phase inequalities in (5.6);
2. `E_{3,4}<5/8`, the factor floor `>0.7901`, and the tensor floor
   `>0.4561`; and
3. the raw operator-norm bound `<20`, the quotient floor `>0.02328`, the
   mismatch amplification `<85.91`, and the data-noise amplification
   `<4.385`.

The symbolic implications from (5.6), including the exact radical constants,
are proved.

### Numerical displays only

The rounded digits in (5.5), the decimal interpretation following (8.9), and
the tentative Gram eigenvalue in (8.10) are descriptive computations.  The
certificate contains formal enclosures for the phase values, but it does not
certify the optional tangent-Gram target (8.10).

### Not established

1. a time-minimal six-reading schedule for the canonical model;
2. an optimal global quotient-secant constant for that schedule;
3. exact finite-radius nonlinear minimax risk on the closed product of
   simplices;
4. recovery of an arbitrary ambient near-product tensor from six readings;
5. statistical risk under stochastic rather than adversarial mismatch; or
6. robustness to unknown prime frequencies or integer-valued tail models.

The last item belongs to a separate integer-tail paper and is not folded into
the present theorem.

---

## 11. Novelty boundary and relation to standard mathematics

All algebraic, Fourier, Diophantine, topological, and quotient-space
ingredients used here are classical.  The DFT calculation is elementary;
prime-log phase isolation uses Kronecker's approximation theorem
([Kronecker, 1884](https://www.deutsche-digitale-bibliothek.de/item/QAZGRAANXUIMS2J4M4VNB5PBMG6OJKP5));
conjugate reversal is a standard Fourier ambiguity
([Hayes, 1982](https://doi.org/10.1109/TASSP.1982.1163863)); and the odd-sphere
obstruction uses the original Borsuk--Ulam theorem
([Borsuk, 1933](https://doi.org/10.4064/fm-20-1-177-190)).  Topological
measurement lower bounds are an established proof pattern; for a nearby
phase-retrieval use, see
[Huang--Xu, 2021](https://doi.org/10.1016/j.aam.2021.102243).

Generic secant/difference-set criteria for algebraic compressed sensing
([Breiding et al., 2023](https://doi.org/10.1016/j.acha.2023.03.006)) and
injective maps of complex toric varieties
([Dufresne--Jeffries, 2018](https://doi.org/10.1090/tran/7026)) are important
adjacent results, but they do not supply the restricted prime-log character
curve, the compact labelled probability patch, or the exact count proved
here.  Likewise, the quotient-ball identity in Theorem 6.2 is elementary
set-membership geometry rather than a new general principle; bounded-noise
set-membership methods long predate this programme
([Fogel--Huang, 1982](https://doi.org/10.1016/0005-1098(82)90110-8);
[Milanese--Tempo--Vicino, 1986](https://doi.org/10.1016/0885-064X(86)90024-5)).

Within the specifically defined labelled product-simplex model and the
one-parameter prime-log harmonic observation family, the programme-specific
contribution is the synthesis:

1. the sharp complex-reading count `r floor(s/2)`;
2. a quantitative realization of near-factor-isolating DFT readings with a
   global secant lower bound; and
3. the anti-reversal/Borsuk--Ulam mechanism proving sharpness, including the
   even-`s` excess over ordinary dimension counting.

The mismatch part specializes standard quotient and set-membership geometry
to separate exact-model injectivity, latent pairwise confusability, and
ambient nonidentifiability.  A targeted review of primary sources located no
prior statement combining the three model-specific items above; this is not
an unconditional claim of historical priority.

The upper proof gives an explicit ideal design and an algorithmically
searchable Kronecker realization, but no useful bound on observation-time or
bit complexity is claimed.  Distinct primes are the canonical arithmetic
realization; the same argument works for any nonzero rationally independent
frequency vector.  Arithmetic Observability I, III, IV, and V supply the
programme-specific framework and the geometric one-parameter comparison.

---

## 12. Reproducibility package

The companion artifacts are

- `arithmetic_observability_full_segre.py`;
- `arithmetic_observability_full_segre_certificate.json`; and
- `test_arithmetic_observability_full_segre.py`.

The strict schema identifier is

```text
arithmetic-observability-full-segre-v1
```

The certificate contains:

1. exact rational times and integer windings;
2. directed Arb intervals for `pi`, `log 2`, `log 3`, and `log 5`;
3. all eighteen reduced-phase intervals;
4. exact target/off-axis rational windows;
5. interval enclosures for `E_{3,4}` and the factor, tensor, quotient, and
   recovery-amplification constants;
6. the raw harmonic operator-norm bound;
7. a canonical digest of its payload; and
8. hashes binding the verifier, manuscript, and focused tests.

The verifier follows the strict-JSON, duplicate-key rejection,
finite-number, resource-cap, deterministic-line-ending, and pinned-Arb
conventions of Arithmetic Observability V.  It pins `python-flint 0.9.0`,
`FLINT 3.6.0`, and 384-bit precision.  The reproduction commands are

```bash
python arithmetic_observability_full_segre.py \
  --verify arithmetic_observability_full_segre_certificate.json

python -m unittest -v test_arithmetic_observability_full_segre.py
```

The focused suite contains 32 tests, including rehashed semantic tampering,
numeric aliases, duplicate keys, malformed fractions, resource exhaustion,
line-ending changes, and deterministic byte regeneration.  The artifact
stores the manuscript hash, so this manuscript intentionally does not embed
the artifact digest and create a circular dependency; the verification
command reports that digest directly.

---

## 13. Next questions

The exact count closes the first normalized product-Segre question and opens
sharper ones:

1. minimize time magnitude while retaining a certified global DFT margin;
2. compute the true global quotient-secant floor rather than the
   operator-norm conversion;
3. map how the tangent principal-angle spectrum varies across boundary
   strata of the product of simplices;
4. replace symmetric ambient balls by structured low-order interaction
   mismatch and determine which latent queries remain exactly identifiable;
5. derive exact finite-radius minimax risk from the ambiguity modulus; and
6. test deterministic acquisition design when prime frequencies themselves
   are uncertain.

The next finite falsifier is the optional tangent-Gram target (8.10).  Its
failure would leave the analytic count theorem, the certified six-reading
global floor, and the certified analytic angle bound (8.9) intact.
