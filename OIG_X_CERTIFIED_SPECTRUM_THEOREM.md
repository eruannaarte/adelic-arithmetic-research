# Operational Information Geometry X

## A certified observable-spectrum theorem

**Status:** analytic theorem memo; not peer reviewed

**Model:** the Stage IX source-response Gramians on the declared parabolic
path model

**Purpose:** turn fixed-band positivity into reproducible, coordinate-invariant
lower and upper spectral certificates, while separating finite-\(K\)
certification from asymptotic claims

---

## 1. Result in one paragraph

Stage IX proved that every fixed finite source quotient has a positive
calibrated Gram floor on the compactified three-chart atlas, but compactness
forces that floor to zero as the source dimension grows.  This memo identifies
the exact object that can be certified and proves a finite algorithmic
theorem for it.  On each compact stratum, let \(G_\theta\) be the response
Gram and \(S_\theta\succ0\) the declared source-cost Gram.  The observable
spectrum is the generalized spectrum

\[
 G_\theta z=\lambda S_\theta z.
\]

It is invariant under every nonsingular change of source coordinates.  For a
fixed quotient dimension \(K\), outward-rounded entry and tail enclosures,
combined with interval \(LDL^*\) inertia, produce rigorous numbers

\[
 \boxed{0<L_K\le\gamma_K\le U_K,}
\qquad
 \gamma_K=\inf_{\theta\in\mathfrak A}
 \lambda_{\min}(G_\theta,S_\theta).
\]

The bounds converge to \(\gamma_K\) as the parameter cover, quadrature
remainders, and matrix intervals are refined.  This is a theorem of
certifiability, not a claim that ordinary high-precision eigenvalues are
certificates.

Two structural lower tools make the result more than point sampling.
First, an Andréief sampling-frame bound turns separated output intervals into
a positive determinant lower bound; determinant and trace then give an
explicit, if conservative, generalized eigenvalue lower bound.  Second, for
the standard Gaussian early endpoint and the first \(K\) ramp/cosine ports,
the calibrated endpoint determinant is exactly

\[
 \boxed{
 \det H_K=
 \frac{(\det M_K)^2}{\prod_{i=1}^K(i!)^2}
 \frac1{(2\pi)^K}
 \prod_{j=0}^{K-1}j!\,\Gamma\!\left(j+\frac52\right),}
\]

where \(M_K=(\langle V^m,\phi_k\rangle)_{m,k=1}^K\).  Strict monotonicity
makes \(\det M_K\ne0\), and for an affine ramp its entries are elementary
finite integrals that admit direct interval enclosure.

The asymptotic boundary remains sharp.  Analytic Hankel kernels give
\(\gamma_K\le C\rho^{-K}\) in every fixed source metric uniformly equivalent
to \(L^2\), but neither total positivity nor finitely many certified values
provides a matching lower law.  A calibrated early endpoint can flatten the
\(q,q^2,\ldots,q^K\) causal flag only by changing source cost; the norm of
that calibration must appear in every information budget.

---

## 2. Coordinate-invariant observable spectra

Let \(E^\sharp\) be a \(K\)-dimensional complement of the exact Stage IX null
space

\[
 \mathcal Z_V=H_0\cap
 \{f:\mathbb E[f\mid\sigma(V)]=0\}.
\]

The quotient dimension and null space must be constant on each parameter
stratum.  If a symmetry is opened or closed as a parameter varies, split the
family into separate strata before taking a smallest nonzero eigenvalue.
Numerically deleting an eigenvalue whose exact status changes is not a
coordinate-invariant operation.

Choose arbitrary coordinates \(z\in\mathbb C^K\) on \(E^\sharp\).  For chart
parameter \(\theta\), let

\[
 G_\theta=R_\theta^*W_\theta R_\theta
\]

be the chart-normalized output Gram, where \(W_\theta\) is the declared output
metric, and let

\[
 S_\theta\succ0
\]

be the declared source-cost Gram.  Define the ordered generalized
eigenvalues

\[
 0<\lambda_1(\theta)\le\cdots\le\lambda_K(\theta),
\qquad
 G_\theta z=\lambda S_\theta z.
 \tag{2.1}
\]

The response singular values in these metrics are

\[
 \sigma_j(\theta)=\sqrt{\lambda_j(\theta)}.
\]

Under a nonsingular coordinate change \(z=P\widetilde z\),

\[
 (G_\theta,S_\theta)
 \longmapsto
 (P^*G_\theta P,P^*S_\theta P),
\]

and (2.1) is unchanged.  This congruence invariance is why the pair
\((G,S)\), rather than an unlabelled matrix eigenvalue, is the primary
certification object.

### 2.1 The atlas floor and its strata

For a compact stratum \(\mathfrak A_a\), put

\[
 \gamma_{K,a}
 =\inf_{\theta\in\mathfrak A_a}\lambda_1(\theta),
\]

and define the full declared atlas floor by

\[
 \boxed{\gamma_K=\min_a\gamma_{K,a}.}
 \tag{2.2}
\]

Equation (2.2) is used only when the strata share the same quotient dimension
and the same declared source-space interpretation.  If an exact null opens
and the quotient dimension changes, certify and report
\(\gamma_{d_a,a}\) and the effective rank separately on each stratum; taking
a numerical “smallest nonzero” value across the transition would hide a rank
change.

The declared atlas has the following strata.

1. **Early resolved.**  In an \(L^2\)-orthonormal moment-adapted basis with
   pivot orders \(r_i\), use

   \[
   \widehat G_q=D(q)^{-1}\Gamma_q^{\mathrm R}D(q)^{-1},
   \qquad
   D(q)=\operatorname{diag}(q^{r_1},\ldots,q^{r_K}),
   \]

   and \(S=I\).  The matrix extends to \(q=0\).  Equivalently, for \(q>0\)
   one may use the raw pair
   \((\Gamma_q^{\mathrm R},D(q)^2)\).  The endpoint must be represented in
   the rescaled coordinates because \(D(0)^2\) is singular.
2. **Resolved-to-atomic.**  Use
   \(\sqrt q\,\Gamma_q^{\mathrm R}\) for \(q\ge q_0>0\), compactified at
   \(q=\infty\).
3. **Finite-cell lattice-to-atomic.**  Use
   \(\sqrt\tau\,\Gamma_{\tau,Q}^{\mathrm L}\) for
   \(\tau\ge\tau_0>0\), with \(Q\) in a declared compact preparation family.
4. **Atomic boundary.**  Use \(\Gamma_\kappa^{\mathrm A}\) for
   \(\kappa\in[0,\infty]\).

Finite transition subcharts can be inserted without changing the theorem.
Different strata may declare different source costs.  In that case
\(\gamma_K\) is a minimum of explicitly different operational questions; it
is not a hidden assertion that the costs are physically identical.

### 2.2 Calibration cost

The early rescaling is mathematically legitimate but not free.  A unit vector
\(z\) in the endpoint coordinate represents raw \(L^2\) coefficients

\[
 x=D(q)^{-1}z,
\]

so

\[
 \|x\|_2\le\|D(q)^{-1}\|\,\|z\|_2=q^{-r_K}\|z\|_2.
\]

If the experiment constrains raw \(L^2\) intervention cost, it must use
\(S=I\), and the weakest early Gram eigenvalue still vanishes like
\(q^{2r_K}\).  A certificate in the moment metric answers a different,
explicitly amplified source-cost question.

---

## 3. Chart formulas and endpoint enclosures

For \(f,g\in E^\sharp\), write

\[
 F_f(s)=\int_0^1e^{-sV(x)}f(x)\,dx.
\]

The resolved, lattice, and atomic forms are

\[
 \Gamma_q^{\mathrm R}(f,g)
 =\int_0^\infty|\widehat\eta(\pi u)|^2
 F_f(\pi^2qu^2)\overline{F_g(\pi^2qu^2)}\,du,
 \tag{3.1}
\]

\[
 \Gamma_{\tau,Q}^{\mathrm L}(f,g)
 =\frac1\pi\int_0^\pi|B_Q(\theta)|^2
 F_f(\tau\omega(\theta))
 \overline{F_g(\tau\omega(\theta))}\,d\theta,
 \tag{3.2}
\]

and

\[
 \Gamma_\kappa^{\mathrm A}(f,g)
 =\int_0^\infty[1+\cos(2\pi\kappa r)]
 F_f(\pi^2r^2)\overline{F_g(\pi^2r^2)}\,dr.
 \tag{3.3}
\]

Here \(q,\tau>0\), \(B_Q(0)=1\), and \(\kappa=\infty\) removes the cosine
term.

For the standard Gaussian,
\(|\widehat\eta(\xi)|^2=e^{-\xi^2}\), the limiting Gram kernel is
\(\Phi(V(x)+V(y))\), with

\[
 \Phi_q^{\mathrm R}(A)
 =\frac1{2\sqrt\pi\sqrt{1+qA}},
 \qquad
 \Phi_\infty^{\mathrm A}(A)
 =\frac1{2\sqrt{\pi A}},
 \tag{3.4}
\]

\[
 \Phi_{\tau,\delta_0}^{\mathrm L}(A)
 =e^{-2\tau A}I_0(2\tau A),
 \qquad
 \Phi_\kappa^{\mathrm A}(A)
 =\frac{1+e^{-\kappa^2/A}}{2\sqrt{\pi A}}.
 \tag{3.5}
\]

Assume \(v_-\le V\le v_+\), with \(v_->0\).  The following endpoint bounds
turn unbounded chart parameters into finite certification tasks.

### Lemma 3.1 — resolved and boundary tail bounds

On raw \(L^2(0,1)\),

\[
 \boxed{
 \left\|\sqrt q\,\Gamma_q^{\mathrm R}
 -\Gamma_\infty^{\mathrm A}\right\|_{\mathrm op}
 \le
 \frac{1}{4\sqrt\pi(2v_-)^{3/2}q}.}
 \tag{3.6}
\]

Also,

\[
 \boxed{
 \left\|\Gamma_\kappa^{\mathrm A}
 -\Gamma_\infty^{\mathrm A}\right\|_{\mathrm op}
 \le
 \frac{\exp[-\kappa^2/(2v_+)]}
 {2\sqrt{2\pi v_-}}.}
 \tag{3.7}
\]

After a source synthesis \(C:E^\sharp\to L^2\), multiply the right sides by
\(\|C\|^2\); after a source metric \(S\), use the corresponding certified
norm of \(CS^{-1/2}\).

#### Proof

For \(A\in[2v_-,2v_+]\),

\[
 0\le
 \frac1{2\sqrt{\pi A}}
 -\frac1{2\sqrt\pi\sqrt{A+q^{-1}}}
 \le\frac1{4\sqrt\pi A^{3/2}q}.
\]

The boundary-kernel difference is at most

\[
 \frac{e^{-\kappa^2/(2v_+)}}{2\sqrt{2\pi v_-}}.
\]

On a unit-measure square, the operator norm is bounded by the
Hilbert--Schmidt norm, which is at most the kernel supremum.  \(\square\)

### Lemma 3.2 — lattice tail reduction

For every fixed finite source quotient \(E^\sharp\), there is an explicitly
computable \(C_E\) such that

\[
 \boxed{
 \left\|\sqrt\tau\,\Gamma_{\tau,Q}^{\mathrm L}
 -\Gamma_\infty^{\mathrm A}\right\|_{\mathrm op}
 \le
 C_E\frac{1+\operatorname{Var}(Q)}{\tau},
 \qquad \tau\ge1,}
 \tag{3.8}
\]

for preparation families of uniformly bounded variance.  A first-moment
bound alone gives a weaker computable tail modulus.

#### Proof

Put \(z=\sqrt\tau\,\theta\).  Uniformly on bounded \(z\),

\[
 \tau\omega(z/\sqrt\tau)=z^2+O(z^4/\tau),
\qquad
 |B_Q(z/\sqrt\tau)|^2=1+O(\operatorname{Var}(Q)z^2/\tau).
\]

The source profile is bounded by \(Ce^{-v_-z^2}\) after rescaling.  Split at
\(z=\tau^{1/8}\); Taylor bounds control the first part and the Gaussian
envelope controls the second.  Every constant is a supremum of finitely many
source norms on \(E^\sharp\), and can therefore be enclosed.  For
\(Q=\delta_0\), the same estimate follows directly from a validated
large-argument remainder for \(e^{-2\tau A}I_0(2\tau A)\).  \(\square\)

### 3.3 Preparation families

For a finite-support family, parameterize \(Q\) by a compact probability
polytope.  For an infinite-support \(\ell^1\)-compact family, certification
also needs a uniform tail envelope.  If \(Q^{(R)}\) is the truncation and

\[
 \sup_Q\|Q-Q^{(R)}\|_1\le\epsilon_R,
\]

then

\[
 \bigl||B_Q(\theta)|^2-|B_{Q^{(R)}}(\theta)|^2\bigr|
 \le2\epsilon_R+\epsilon_R^2.
 \tag{3.9}
\]

This converts the infinite preparation family into a finite parameter box
plus a rigorous operator error.  Mere assertion of compactness, without a
finite descriptor or tail oracle, is not yet a machine-checkable
certificate.

---

## 4. The finite-\(K\) interval certification theorem

Let \(\mathfrak A_a\) be one compact parameter stratum with constant quotient
dimension \(K\).  Assume:

1. \(G_\theta=G_\theta^*\) and \(S_\theta=S_\theta^*\succ0\) are continuous;
2. a known \(s_a>0\) satisfies \(S_\theta\succeq s_aI\);
3. every rational parameter box \(B\subset\mathfrak A_a\) has outward-rounded
   Hermitian interval enclosures
   \(\mathbb G_B\ni G_\theta\) and
   \(\mathbb S_B\ni S_\theta\) for all \(\theta\in B\);
4. the enclosure radii converge uniformly to zero with box diameter,
   quadrature precision, and tail cutoff; and
5. unbounded physical parameters have been replaced by the endpoint
   enclosures in Section 3, rather than by a finite sample at a large value.
6. after removal of the exact null, \(G_\theta\succ0\) throughout the
   stratum.

### Theorem 4.1 — convergent certified atlas enclosure

For every fixed \(K\) and every tolerance \(\varepsilon>0\), a finite
parameter cover and finite interval computation produce

\[
 \boxed{
 0\le L_K\le\gamma_K\le U_K,
 \qquad U_K-L_K<\varepsilon.}
 \tag{4.1}
\]

If Stage IX positivity is used only qualitatively, the first coarse lower
bound may be zero.  Refinement eventually makes \(L_K>0\).

#### Certification rule

For each parameter box \(B\), certify a number \(\ell_B\) by proving with
interval \(LDL^*\) arithmetic that

\[
 \boxed{
 \mathbb G_B-\ell_B\mathbb S_B\succ0.}
 \tag{4.2}
\]

Replace a negative coarse \(\ell_B\) by zero using hypothesis 6.  Then

\[
 L_K=\min_{a,B\subset\mathfrak A_a}\ell_B
\]

is a global lower bound.  At any certified point
\(\theta_*\), an outward-rounded generalized eigensolve or any test vector
\(z\ne0\) gives

\[
 \gamma_K\le\lambda_1(\theta_*)
 \le\frac{z^*G_{\theta_*}z}{z^*S_{\theta_*}z}.
 \tag{4.3}
\]

The minimum of finitely many such upper enclosures is \(U_K\).  An arbitrary
test vector gives a valid upper bound, but convergence in (4.1) uses
pointwise generalized-eigenvalue enclosure or certified approximate
minimizing vectors as the cover is refined.

#### Proof

Positive definiteness in (4.2) implies

\[
 z^*G_\theta z>\ell_Bz^*S_\theta z
\]

for every nonzero \(z\) and every \(\theta\in B\).  Thus
\(\lambda_1(\theta)\ge\ell_B\).  Taking minima proves the lower inequality.
Equation (4.3) is the Rayleigh principle and proves the upper inequality.

The generalized eigenvalues are uniformly continuous because the parameter
set is compact and \(S_\theta\succeq s_aI\).  Uniformly convergent interval
oracles and a refining finite cover therefore make both the local lower
tests and sampled upper tests converge to the same infimum.  Fixed-\(K\)
positivity on the compact stratum supplies a positive gap, so sufficiently
fine refinement certifies \(L_K>0\).  \(\square\)

### 4.2 Full-spectrum enclosures

Verified symmetric-indefinite \(LDL^*\) with pivoting (including certified
\(2\times2\) pivot blocks when they occur) gives inertia as well as
positivity.  Failure of one proposed interval pivot pattern is inconclusive;
one must change the verified factorization or refine the parameter box.
Bisection in
\(\lambda\) for

\[
 G_\theta-\lambda S_\theta
\]

therefore encloses every generalized eigenvalue on every parameter box.
The resulting ordered intervals certify the robust effective rank, not only
the smallest eigenvalue.

### 4.3 What counts as a certificate

A finite-\(K\) certificate consists of:

1. the exact quotient basis and source/output metrics;
2. rational or outward-rounded parameter boxes;
3. quadrature, series, and infinite-tail remainders;
4. interval matrix enclosures;
5. an \(LDL^*\), Cholesky-residual, or exact-rational inertia proof; and
6. a reproducible proof trace identifying the weakest parameter box.

More decimal digits without items 2--5 are evidence, not certification.
Pointwise positivity on a dense-looking grid does not lower-bound a compact
atlas minimum.

---

## 5. Structural lower bounds

Interval inertia is sharp but computational.  The next results provide
analytic lower certificates and independent controls.

### Lemma 5.1 — determinant-and-trace generalized bound

Let \(G\succ0\), \(S\succ0\), and \(K\ge2\).  Put

\[
 D=\frac{\det G}{\det S},
 \qquad
 T=\operatorname{tr}(S^{-1}G).
\]

Then

\[
 \boxed{
 \lambda_{\min}(G,S)
 \ge
 \frac{D}{(T/(K-1))^{K-1}}.}
 \tag{5.1}
\]

For \(K=1\), the generalized eigenvalue is \(G/S\).

#### Proof

The eigenvalues of \(S^{-1/2}GS^{-1/2}\) have product \(D\) and sum \(T\).
The product of the largest \(K-1\) is at most
\((T/(K-1))^{K-1}\) by arithmetic--geometric mean.  Divide \(D\) by this
upper bound.  \(\square\)

For interval use, it is enough to certify

\[
 \det G\ge d_G>0,\quad
 \det S\le d_S,\quad
 S\succeq sI,\quad
 \operatorname{tr}G\le t_G,
\]

because \(D\ge d_G/d_S\) and
\(T\le t_G/s\).

### Lemma 5.2 — verified \(LDL^*\) bound

If an interval factorization proves

\[
 G-\ell S=LDL^*+E,
\]

with

\[
 \lambda_{\min}(LDL^*)>\|E\|_{\mathrm op},
\]

then \(\lambda_{\min}(G,S)>\ell\).  Equivalently, interval pivots that stay
strictly positive certify the same statement.  This is normally much sharper
than (5.1), while (5.1) is a valuable independent proof route.

### Theorem 5.3 — separated-output sampling-frame bound

Let

\[
 G_{ij}=\int_\Omega f_i(s)\overline{f_j(s)}\,d\nu(s)
\]

for \(K\) continuous functions.  Suppose there are pairwise disjoint
measurable sets \(I_1,\ldots,I_K\) such that

\[
 \nu(I_a)\ge\mu_a>0
\]

and

\[
 \left|\det[f_i(s_a)]_{i,a=1}^K\right|
 \ge d>0
 \quad
 \text{whenever }s_a\in I_a.
 \tag{5.2}
\]

Then

\[
 \boxed{\det G\ge d^2\prod_{a=1}^K\mu_a.}
 \tag{5.3}
\]

Together with Lemma 5.1, this gives an explicit lower eigenvalue certificate.

#### Proof

Andréief's identity gives

\[
 \det G=\frac1{K!}\int_{\Omega^K}
 \left|\det[f_i(s_a)]\right|^2
 \prod_{a=1}^Kd\nu(s_a).
\]

Restrict to the \(K!\) permutations of
\(I_1\times\cdots\times I_K\).  The integrand is symmetric, so the
factor \(K!\) cancels.  Apply (5.2).  \(\square\)

For Stage IX, take \(f_i(s)=F_{e_i}(s)\) and put the nonnegative chart
weight into \(d\nu(s)\) (equivalently, multiply every profile by the square
root of the weight relative to Lebesgue measure).  Since
\(F_{e_i}(s)=c_is^i+O(s^{i+1})\), the desingularized profiles
\(F_{e_i}(s)/s\) have orders \(0,\ldots,K-1\) and a nonzero Wronskian at
\(s=0\).  Equivalently, the evaluation determinant of the original profiles
is nonzero for sufficiently small distinct positive samples after its
explicit \(\prod_as_a\) factor is removed.  Therefore sufficiently small
separated intervals satisfy (5.2).  A certificate must still enclose the
determinant and the weight masses there; the words “Chebyshev system” or
“total positivity” alone do not provide a numerical lower bound.

### Theorem 5.4 — one truncated Laplace Gram controls three late charts

Define the common truncated Gram

\[
 \boxed{
 H_b(f,g)=\frac1{2\pi}\int_0^b
 s^{-1/2}F_f(s)\overline{F_g(s)}\,ds,
 \qquad b>0.}
 \tag{5.4}
\]

For every \(b>0\), \(H_b\) has the same null space
\(\mathcal Z_V\): vanishing on an \(s\)-interval forces the analytic Laplace
profile \(F_f\) to vanish identically.  It is therefore positive definite on
every fixed exact-null quotient.

For the standard Gaussian resolved preparation, a one-cell lattice atom, and
the interior atomic chart,

\[
 \boxed{
 \begin{aligned}
 \sqrt q\,\Gamma_q^{\mathrm R}&\succeq e^{-b}H_b,
 &&q\ge1,\\
 \sqrt\tau\,\Gamma_{\tau,\delta_0}^{\mathrm L}&\succeq H_b,
 &&\tau\ge1,\quad0<b\le4,\\
 \Gamma_\infty^{\mathrm A}&\succeq H_b.
 \end{aligned}}
 \tag{5.5}
\]

If the atlas uses \(\sqrt{1+q}\) and \(\sqrt{1+\tau}\) instead, the first
constant improves to

\[
 c_{\mathrm R}(b)=\min\{1,\sqrt2e^{-b}\},
\]

and the lattice constant remains at least one.

For a general lattice preparation, suppose

\[
 |B_Q(\theta)|\ge\beta>0
\]

whenever

\[
 0\le\theta\le
 2\arcsin(\sqrt b/2).
\]

Then the lattice lower bound in (5.5) becomes
\(\beta^2H_b\), uniformly in \(Q\).

#### Proof

In (3.1), set \(s=\pi^2qu^2\).  Then

\[
 \sqrt q\,\Gamma_q^{\mathrm R}(f,f)
 =\frac1{2\pi}\int_0^\infty
 s^{-1/2}e^{-s/q}|F_f(s)|^2\,ds.
\]

On \(0\le s\le b\) and \(q\ge1\), \(e^{-s/q}\ge e^{-b}\).  With the
\(\sqrt{1+q}\) normalization, the ratio to the \(H_b\) weight is

\[
 \sqrt{\frac{1+q}{q}}e^{-s/q}.
\]

Writing \(x=1/q\in[0,1]\), its logarithm
\(\tfrac12\log(1+x)-sx\) is concave in \(x\), so its minimum occurs at an
endpoint and gives \(c_{\mathrm R}(b)\).

For the lattice atom, set
\(s=4\tau\sin^2(\theta/2)\).  Since

\[
 d\theta=\frac{ds}{\sqrt{s(4\tau-s)}},
\]

the ratio between the \(\sqrt\tau\Gamma^{\mathrm L}\) weight and the
\(H_b\) weight is

\[
 \frac{2\sqrt\tau}{\sqrt{4\tau-s}}\ge1.
\]

The restriction \(b\le4\) keeps \([0,b]\) inside the transformed domain for
all \(\tau\ge1\).  The factor \(|B_Q|^2\) gives the general-preparation
claim.  Finally, the substitution \(s=\pi^2r^2\) shows

\[
 \Gamma_\infty^{\mathrm A}=H_\infty.
\]

\(\square\)

Theorem 5.4 is a genuine uniform lower reduction, not a pointwise sample.  If

\[
 \eta_{K,b}=\lambda_{\min}(H_b,S)>0
\]

is certified once, it supplies simultaneous late resolved, lattice, and
interior atomic lower bounds when those strata use the same source metric
\(S\).  With chart-dependent source metrics, certify the corresponding
numbers \(\lambda_{\min}(H_b,S_a)\) separately.  For a preparation family with
\(\sup_Q\sum_m|m|Q_m\le M_1\), the elementary inequality

\[
 |B_Q(\theta)-1|\le M_1|\theta|
\]

provides a positive \(\beta\) after choosing \(b\) small enough.

---

## 6. Exact Gaussian early-endpoint certificate

This section specializes to

\[
 |\widehat\eta(\xi)|^2=e^{-\xi^2}
\]

and an \(L^2\)-orthonormal moment-adapted basis
\(e_1,\ldots,e_K\) with pivot orders \(1,\ldots,K\).  Put

\[
 M_K=(m_i(\phi_k))_{i,k=1}^K,
 \qquad
 m_i(f)=\int_0^1V(x)^if(x)\,dx,
 \tag{6.1}
\]

where \(\phi_1,\ldots,\phi_K\) is any original \(L^2\)-orthonormal basis of
the same quotient.

### Theorem 6.1 — exact endpoint determinant

Let

\[
 H_K=\lim_{q\downarrow0}
 D(q)^{-1}\Gamma_q^{\mathrm R}D(q)^{-1},
 \qquad D(q)=\operatorname{diag}(q,\ldots,q^K).
\]

Then

\[
 (H_K)_{ij}
 =
 \frac{(-1)^{i+j}m_i(e_i)m_j(e_j)}
 {i!\,j!}
 \frac{\Gamma(i+j+1/2)}{2\pi},
 \tag{6.2}
\]

and

\[
 \boxed{
 \det H_K=
 \frac{(\det M_K)^2}{\prod_{i=1}^K(i!)^2}
 \frac1{(2\pi)^K}
 \prod_{j=0}^{K-1}
 j!\,\Gamma\!\left(j+\frac52\right).}
 \tag{6.3}
\]

Consequently, for \(K\ge2\),

\[
 \boxed{
 \lambda_{\min}(H_K)
 \ge
 \frac{\det H_K}
 {(\operatorname{tr}H_K/(K-1))^{K-1}}.}
 \tag{6.4}
\]

All quantities in (6.2)--(6.4) admit direct outward-rounded evaluation.

#### Proof

The Stage IX endpoint formula and

\[
 \int_0^\infty e^{-\pi^2u^2}u^{2N}\,du
 =\frac{\Gamma(N+1/2)}{2\pi^{2N+1}}
\]

give (6.2).  Let

\[
 C_{ij}=\frac{\Gamma(i+j+1/2)}{2\pi}.
\]

After shifting \(i=a+1\), \(j=b+1\), this is the Hankel moment matrix of
\(x^{3/2}e^{-x}dx\), multiplied by \(1/(2\pi)\).  The monic Laguerre norm
formula gives

\[
 \det C
 =\frac1{(2\pi)^K}
 \prod_{j=0}^{K-1}j!\,\Gamma\!\left(j+\frac52\right).
 \tag{6.5}
\]

Choose the adapted basis by an orthogonal triangularization of \(M_K\).
The matrix \((m_i(e_j))\) is triangular, and the product of its diagonal
entries has absolute value \(|\det M_K|\).  Since

\[
 H_K=
 \operatorname{diag}\!\left(
 \frac{(-1)^im_i(e_i)}{i!}\right)
 C
 \operatorname{diag}\!\left(
 \frac{(-1)^im_i(e_i)}{i!}\right),
\]

equation (6.3) follows.  Lemma 5.1 with \(S=I\) gives (6.4).
\(\square\)

### 6.2 A strict-monotonicity determinant bound

If \(V\) is continuous and strictly monotone, \(\det M_K\ne0\).  This fact
can itself be made quantitative.  Augment the moment matrix with
\(\phi_0=1\) and \(m=0\).  Andréief's identity expresses its determinant as
an integral over \(0<x_0<\cdots<x_K<1\) of

\[
 \prod_{a<b}[V(x_b)-V(x_a)]
 \det[\phi_k(x_a)]_{k,a=0}^K.
 \tag{6.6}
\]

For cosine ports, the second determinant is a nonzero constant times

\[
 \prod_{a<b}[\cos(\pi x_b)-\cos(\pi x_a)].
\]

Choose ordered disjoint intervals \(I_0,\ldots,I_K\).  Interval lower bounds
on every difference in (6.6), multiplied by
\(\prod_a|I_a|\), give an explicit positive lower bound for
\(|\det M_K|\).  The affine ramp admits a sharper exact factorization.  For
\(V_g(x)=1+gx\) and any zero-mean original ports \(\phi_k\), put

\[
 X_K=\left(\int_0^1x^m\phi_k(x)\,dx\right)_{m,k=1}^K.
\]

The constant term drops out and the binomial theorem gives
\(M_K(g)=L_K(g)X_K\), where

\[
 (L_K(g))_{mr}=\mathbf 1_{r\le m}\binom mr g^r.
\]

Thus \(L_K(g)\) is lower triangular with diagonal
\(g,g^2,\ldots,g^K\), and

\[
 \boxed{
 \det M_K(g)=g^{K(K+1)/2}\det X_K,\qquad
 \det H_K(g)=g^{K(K+1)}\mathcal C_K(\det X_K)^2,}
 \tag{6.6a}
\]

where

\[
 \mathcal C_K=
 \frac1{\prod_{i=1}^K(i!)^2}
 \frac1{(2\pi)^K}
 \prod_{j=0}^{K-1}j!\,\Gamma\!\left(j+\frac52\right).
\]

For cosine ports the entries of \(X_K\) are elementary finite integrals.
Equation (6.6a) quantifies the exact determinant collapse as the ramp contrast
\(g\) tends to zero; it does not by itself give the smallest-eigenvalue
exponent because the other eigenvalues also depend on \(g\).

Strict monotonicity alone proves nonvanishing, not a uniform numerical
constant over a modulation family.  A family approaching a plateau or
\(g\downarrow0\) makes the determinant arbitrarily small.

### Lemma 6.3 — certified early neighborhood

For \(0\le q<1/(2v_+)\), the calibrated Gaussian early Gram is analytic at
\(q=0\), and

\[
 \boxed{
 \|\widehat G_q-H_K\|_{\mathrm op}
 \le C_{K,V}(q)\,q,}
 \tag{6.7}
\]

where one safe explicit choice is

\[
 C_{K,V}(q)
 =
 \frac{K\max\{1,(2v_+)^{2K+1}\}}
 {2\sqrt\pi(1-2v_+q)}.
 \tag{6.8}
\]

Thus

\[
 \lambda_{\min}(\widehat G_q)
 \ge\lambda_{\min}(H_K)-C_{K,V}(q)q.
 \tag{6.9}
\]

#### Proof

Expand

\[
 \Phi_q^{\mathrm R}(A)
 =\frac1{2\sqrt\pi}
 \sum_{n=0}^\infty
 \binom{-1/2}{n}q^nA^n.
\]

In the \(i,j\) entry, moment cancellation removes every term with
\(n<i+j\).  After division by \(q^{i+j}\), the leading term is (6.2).
For the remaining terms use

\[
 \left|\binom{-1/2}{n}\right|\le1,\qquad
 |m_a(e_i)|\le v_+^a\|e_i\|_1\le v_+^a,
\]

and sum the geometric tail.  Each entry is bounded by

\[
 \frac{(2v_+)^{i+j+1}q}
 {2\sqrt\pi(1-2v_+q)}.
\]

The operator norm is at most \(K\) times the largest entry.  Weyl's
inequality gives (6.9).  \(\square\)

The bound (6.8) is deliberately crude.  An interval Taylor model that keeps
the actual moments is usually far sharper, but (6.8) proves that the endpoint
can be enclosed by a neighborhood theorem rather than sampled at a tiny
positive \(q\).

---

## 7. Realizing the certificate on the complete atlas

For the canonical Gaussian/ramp/cosine model, Theorem 4.1 can be implemented
with the following finite proof decomposition.

### 7.1 Early resolved

1. Enclose \(M_K\) and its exact nonzero determinant.
2. Build an \(L^2\)-orthonormal adapted basis with a verified QR or
   congruence factorization.
3. Certify \(H_K\) by (6.2), (6.3), and interval \(LDL^*\).
4. Cover \(0\le q\le q_e\) using Lemma 6.3.
5. Cover \(q_e\le q\le q_0\) with interval Taylor models or
   Gauss--Legendre quadrature and interval inertia.

This retains the endpoint causal calibration.  Applying an ordinary
eigensolver to the raw Gram at very small \(q\) instead tests numerical
underflow, not the endpoint theorem.

### 7.2 Balanced and late resolved

The exact kernel

\[
 \frac1{2\sqrt\pi\sqrt{1+q(V(x)+V(y))}}
\]

is analytic on the compact integration square.  Validated tensor quadrature
or a one-dimensional phase integral encloses every entry.  Cover a finite
interval \(q_0\le q\le Q\); use (3.6) beyond \(Q\).  Alternatively,
Theorem 5.4 reduces all \(q\ge1\) to one certified \(H_b\).

### 7.3 Finite-cell lattice

For \(Q=\delta_0\), use the Bessel kernel in (3.5).  For finite-support \(Q\),
integrate (3.2) with its probability-polytope parameters.  Cover
\(\tau_0\le\tau\le T\), then use (3.8), or use the common lower in
Theorem 5.4 when a uniform \(\beta\) is available.  Infinite-support
preparations require (3.9).

### 7.4 Atomic boundary

The interior Gram is enclosed once.  For \(0\le\kappa\le K_0\), use the
exact kernel (3.5) and interval boxes.  Use (3.7) for
\(\kappa\ge K_0\).  Sampling a few large boundary coordinates does not
certify the \(\kappa=\infty\) tail.

### 7.5 A practical matrix certificate

For a box center \(\theta_B\), let a verified computation provide

\[
 \lambda_{\min}(G_{\theta_B},S_{\theta_B})\ge\widehat\lambda_B
\]

and

\[
 \|G_\theta-G_{\theta_B}\|\le e_G,\qquad
 \|S_\theta-S_{\theta_B}\|\le e_S.
\]

If \(S_{\theta_B}\succeq s_BI\) and \(e_S<s_B\), then

\[
 \boxed{
 \lambda_{\min}(G_\theta,S_\theta)
 \ge
 \frac{\widehat\lambda_Bs_B-e_G}{s_B+e_S}.}
 \tag{7.1}
\]

This follows directly from the Rayleigh quotient and is a convenient
independent check on interval \(LDL^*\).

---

## 8. Finite certification versus asymptotic bounds

### Theorem 8.1 — analytic-kernel upper ceiling

Suppose a fixed chart Gram has kernel

\[
 \Phi(V(x)+V(y)),
\]

where \(\Phi\) extends analytically to a common complex neighborhood of
\([2v_-,2v_+]\).  Let the injective map
\(C_K:\mathbb C^K\to L^2(0,1)\) synthesize the \(K\)-dimensional physical
source space, and
assume the declared source cost uniformly dominates \(L^2\):

\[
 \boxed{
 z^*S_Kz\ge s_*\|C_Kz\|_{L^2}^2,
 \qquad s_*>0.}
\]

If \(s_*\) is independent of \(K\), then there are \(C<\infty\) and
\(\rho>1\) such that

\[
 \boxed{
 \lambda_{\min}(G_K,S_K)
 \le\frac{C}{s_*}\rho^{-K}.}
 \tag{8.1}
\]

Equivalently, the coordinate-invariant hypothesis is the uniform synthesis
bound
\(\|C_KS_K^{-1/2}\|\le s_*^{-1/2}\).  A coordinate lower bound on the
matrix \(S_K\) by itself would not suffice in a poorly scaled basis.

#### Proof

Degree-\((K-2)\) polynomial approximation of \(\Phi\) has uniform kernel
error \(C\rho^{-K}\).  The approximating integral operator has range in
\(\operatorname{span}\{1,V,\ldots,V^{K-2}\}\), so its compression to a
\(K\)-dimensional physical source space has a nonzero null vector
\(f=C_Kz\).  On that vector,

\[
 z^*G_Kz\le C\rho^{-K}\|C_Kz\|_{L^2}^2,\qquad
 z^*S_Kz\ge s_*\|C_Kz\|_{L^2}^2.
\]

Take the Rayleigh quotient.  \(\square\)

### 8.2 What this upper ceiling does and does not prove

The ceiling implies that a polynomially small modeling error can support at
most a logarithmic-order raw source band.  It does **not** prove

\[
 \gamma_K\asymp\rho^{-K},
\]

because:

1. the true floor may decay faster through column correlation;
2. the minimizing chart may change with \(K\);
3. moment-adapted coordinate gains may themselves be exponentially or
   superexponentially ill-conditioned; and
4. a \(K\)-dependent source metric can deliberately change the spectrum.

Strict total positivity proves exact positivity of finite minors.  It does
not provide a dimension-uniform lower frame constant.  Likewise, a sequence
of interval certificates for \(K\le K_0\) is not an asymptotic theorem.

### 8.3 What is genuinely two-sided

For each fixed \(K\), Theorem 4.1 gives a convergent two-sided enclosure of
the exact compact-atlas floor.  Theorems 5.3--6.1 give analytic finite-\(K\)
lower bounds, and a single certified Rayleigh quotient gives an upper bound.
As \(K\to\infty\), this memo proves the analytic upper ceiling (8.1) but no
matching lower rate.

This distinction is the main epistemic boundary of Stage X.

---

## 9. Certified effective rank

Let

\[
 0<\lambda_1(\theta)\le\cdots\le\lambda_K(\theta)
\]

be the generalized Gram spectrum and let \(\eta>0\) be a declared response
singular-value threshold.  Define

\[
 d_\eta(\theta)
 =\#\{j:\lambda_j(\theta)\ge\eta^2\}.
 \tag{9.1}
\]

Suppose interval inertia certifies, for every parameter box,

\[
 \underline\lambda_{j,B}
 \le\lambda_j(\theta)
 \le\overline\lambda_{j,B}.
\]

Then

\[
 \boxed{
 d_{\eta}^{\rm guaranteed}
 =
 \min_B\#\{j:\underline\lambda_{j,B}\ge\eta^2\}}
 \tag{9.2}
\]

is visible everywhere on the atlas, while

\[
 \boxed{
 d_{\eta}^{\rm possible}
 =
 \max_B\#\{j:\overline\lambda_{j,B}\ge\eta^2\}}
 \tag{9.3}
\]

is an upper bound on the number visible somewhere.  Eigenvalues whose
intervals straddle \(\eta^2\) are honestly unresolved.

If the finite-grid and continuum models use the same declared source metric,
define the metric-relative Gram error

\[
 \boxed{
 \delta_K=
 \left\|S^{-1/2}(G_h-G)S^{-1/2}\right\|_{\mathrm op}.}
 \tag{9.4}
\]

Weyl then shifts every generalized-eigenvalue enclosure to

\[
 [\max\{0,\underline\lambda-\delta_K\},
  \overline\lambda+\delta_K].
 \tag{9.5}
\]

Thus a direction is robustly transferred only when its continuum lower
certificate exceeds \(\eta^2+\delta_K\).

If the finite source metric also differs, certify the pair
\((G_h,S_h)\) directly by Theorem 4.1; an unwhitened bound
\(\|G_h-G\|\le\delta\) is not a generalized-eigenvalue perturbation bound.

### 9.1 Analytic effective-rank ceiling

Let

\[
 \mu_1\ge\mu_2\ge\cdots
\]

be the generalized Gram eigenvalues of the full compact chart operator in
descending order.  The polynomial approximation-number proof in Theorem 8.1
gives

\[
 \mu_j\le C\rho^{-j}
\]

up to a change of constants.  Equivalently, for a \(K\)-dimensional
compression whose eigenvalues are written in the ascending convention of
Section 2, only the floor has the universal statement
\(\lambda_1\le C\rho^{-K}\).  Hence, in a fixed analytic chart and a
uniformly equivalent source metric,

\[
 \boxed{
 d_\eta=O(\log(1/\eta)).}
 \tag{9.6}
\]

This is an upper information count.  A lower count requires certified
eigenvalue enclosures or a lower frame theorem such as Theorem 5.3.

---

## 10. Gaussian information budgets

Assume the declared output has been whitened and each repetition has
independent Gaussian noise \(N(0,\sigma^2I)\).  Source amplitude \(a\) is
measured in the declared source metric \(S\).  For a known \(S\)-unit
direction \(u\), equal-prior testing of zero against intervention \(au\) over
\(N\) repetitions has exact error

\[
 P_{\rm err}(u)
 =
 \Phi\!\left(
 -\frac{a\sqrt N\,\sqrt{u^*Gu}}{2\sigma}
 \right).
 \tag{10.1}
\]

Suppose the finite-model atlas floor obeys

\[
 \underline\gamma_h
 \le\gamma_{K,h}\le\overline\gamma_h,
\]

with

\[
 \underline\gamma_h=L_K-\delta_K>0,
 \qquad
 \overline\gamma_h=U_K+\delta_K.
 \tag{10.2}
\]

For a target error \(\alpha<1/2\), let
\[
 z_\alpha=\Phi^{-1}(1-\alpha).
\]

### Theorem 10.1 — certified repetition bracket

The repetitions sufficient for error at most \(\alpha\) in **every**
declared source direction satisfy

\[
 \boxed{
 N\ge
 \frac{4\sigma^2z_\alpha^2}
 {a^2\underline\gamma_h}.}
 \tag{10.3}
\]

Conversely, no uniform guarantee is possible when

\[
 \boxed{
 N<
 \frac{4\sigma^2z_\alpha^2}
 {a^2\overline\gamma_h}.}
 \tag{10.4}
\]

Thus the exact worst-direction repetition threshold lies in the certified
interval

\[
 \boxed{
 \frac{4\sigma^2z_\alpha^2}
 {a^2\overline\gamma_h}
 \le N_*
 \le
 \frac{4\sigma^2z_\alpha^2}
 {a^2\underline\gamma_h}.}
 \tag{10.5}
\]

#### Proof

The lower Gram certificate gives
\(u^*Gu\ge\underline\gamma_h\) for every \(S\)-unit \(u\), and (10.1)
gives (10.3).  The upper certificate means that some \(S\)-unit direction
has response energy at most \(\overline\gamma_h\).  Its testing error exceeds
\(\alpha\) under (10.4).  \(\square\)

The theorem assumes a known background, known direction, correct whitening,
and independent Gaussian repetitions.  It is not a composite-background,
unknown-support, or nonlinear recovery theorem.  Calibration gain and its
noise amplification must be included in \(S\), \(W\), and \(\sigma\);
whitening does not create information.

---

## 11. Exact hypotheses and no-go boundaries

### 11.1 Constant quotient dimension

Generalized eigenvalue certification requires \(S_\theta\succ0\) on a fixed
quotient.  If a symmetry parameter makes an exact null appear, stratify the
atlas and identify the null analytically.  An interval eigensolver cannot
decide whether an arbitrarily small channel is structurally zero.

### 11.2 Endpoint tails are part of the proof

No finite set of values \(q,\tau,\kappa<\infty\) certifies an infimum on a
compactified chart.  Use (3.6)--(3.8), Theorem 5.4, or another rigorous
endpoint enclosure.

### 11.3 Source metrics are part of the result

Congruence can make a finite Gram the identity by choosing its inverse square
root as source calibration.  The generalized pair records the associated
source cost.  Omitting that cost turns a true algebraic whitening statement
into a false information claim.

### 11.4 Total positivity is qualitative without constants

Andréief, Chebyshev systems, and strict total positivity prove that fixed
minors are nonzero.  A lower eigenvalue certificate additionally needs
quantitative separation, interval determinant bounds, or verified inertia.

### 11.5 High precision is not interval certification

Arbitrary precision reduces rounding error but does not bound quadrature
tails, parameter gaps, or the distance from an approximate eigenvalue to the
true one.  A reported 100-digit positive number may still be a non-certified
estimate.

### 11.6 Finite sensors require a frame certificate

The complete-density Gram may have rank \(K\), while \(M<K\) scalar
measurements have rank at most \(M\).  For \(M\ge K\), the sampled response
needs its own generalized Gram certificate; the continuum atlas floor does
not transfer without a sensor-frame error bound.

### 11.7 Finite-\(K\) certificates do not prove an asymptotic lower law

Even exact certificates for \(K=1,\ldots,K_0\) leave open the behavior as
\(K\to\infty\).  The analytic upper ceiling is rigorous; a matching lower
rate remains a separate theorem.

### 11.8 No physical-universe conclusion

Every result concerns the declared parabolic operational model.  Neither a
certified source spectrum nor a causal flag establishes a fundamental
geometry of spacetime or information.

---

## 12. What is proved and what remains open

### Proved in this memo

1. The coordinate-invariant certification object is the generalized pair
   \((G_\theta,S_\theta)\) on a fixed exact-null quotient.
2. Every fixed-\(K\) compact atlas with convergent interval oracles admits
   arbitrarily sharp, rigorous two-sided enclosure of \(\gamma_K\).
3. Interval \(LDL^*\), determinant--trace bounds, and separated-output
   Andréief bounds provide independent lower-certificate routes.
4. A single truncated Laplace Gram \(H_b\) uniformly lower-controls the late
   Gaussian resolved, one-cell lattice, and interior atomic charts.
5. The Gaussian early endpoint has the exact determinant (6.3).
6. The calibrated early Gram has an explicit \(O_K(q)\) endpoint enclosure.
7. Resolved, lattice, and boundary tails can be removed from the numerical
   parameter cover by rigorous analytic bounds.
8. Analytic Hankel kernels give an exponential generalized-eigenvalue upper
   ceiling in every uniformly \(L^2\)-equivalent source metric.
9. Certified spectral intervals give robust effective-rank and Gaussian
   repetition-budget intervals.

### Not proved here

1. Numerical values of the certified full-atlas intervals.  They require an
   outward-rounded implementation and proof trace.
2. A matching asymptotic lower bound for \(\gamma_K\).
3. A sharp \(K\)-dependence for moment-matrix conditioning or for the early
   endpoint remainder.
4. A universal lattice-tail constant over preparation families without a
   finite descriptor or moment/tail bound.
5. A finite-grid interval enclosure for the Stage IX transfer error
   \(\delta_K\); the information formulas accept such a certificate as an
   input.
6. Composite hypothesis testing, sparse support recovery, or minimax
   estimation.

---

## 13. Recommended next analytic and computational order

1. **Implement the proof trace for moderate \(K\).**  Use outward-rounded
   quadrature and interval \(LDL^*\) on every compact parameter box; report
   the weakest box, not only the smallest sampled point.
2. **Exploit the common \(H_b\) reduction.**  Optimize \(b\) jointly with its
   determinant/trace lower bound to obtain a useful three-chart certificate.
3. **Sharpen the early endpoint.**  Replace (6.8) by moment-aware interval
   Taylor models and verified QR/LDL factorizations.
4. **Locate the minimizing chart.**  Once a coarse global certificate exists,
   use derivative intervals to isolate the minimizer and tighten \(U_K-L_K\).
5. **Seek asymptotic lower structure.**  Combine truncated-Laplace spectral
   theory with the alignment of cosine bands and singular functions; do not
   extrapolate a law from moderate-\(K\) ratios.
6. **Certify finite transfer.**  Enclose \(\delta_K\), including moment
   leakage, mixed causal words, target preparation, boundary error, and
   sensor-frame error.
7. **Only then optimize experiment design.**  Choose times and preparations
   to maximize the certified effective rank at fixed source cost and noise.

The strongest completed result is finite but exact: for every declared
finite quotient, the entire compact-atlas observability floor is not merely
positive—it is, in principle, enclosable to arbitrary prescribed accuracy by
a finite reproducible proof.  The strongest unresolved obstacle is
asymptotic: no useful lower law in \(K\) follows from analyticity or total
positivity alone.
