# Transfer with uncertain acquisition and a perturbed model

This extends the [developed transfer theorem](../../transfer_theorem_2026_09/framework/PROOFS.md).
All statements below have proofs here; no historical novelty claim is made.
Clock tolerances and model membership are hypotheses about acquisition. An
accurate numerical solve does not establish those hypotheses.

## 1. The acquisition uncertainty must enter before the quotient

Let the actual observation be

\[
y=f_{c,m}(\theta)+B_{c,m}z+e,
\qquad (\theta,c,m)\in\mathcal A,
\]

where the admissible set retains any dependence between the source, clock
parameter c and model parameter m. The nuisance vector z is unrestricted and
independent of these coordinates. Let L be a fixed linear processing map,
including any permitted restriction and nuisance elimination, with the output
norm chosen using the transported physical noise metric. Suppose its computed
output v differs from Ly by a certified processing error. Let a(theta) be a
nominal center in this final space.

**Theorem 1 (uncertain-acquisition transfer).** Suppose, for every admissible
explanation,

\[
LB_{c,m}=0,
\quad\|L f_{c,m}(\theta)-a(\theta)\|
 \le \rho_\theta+\tau_\theta+\kappa_\theta,
\quad\|Le\|\le\eta_\theta,
\quad\|v-Ly\|\le\xi_\theta.
\]

Then every actual explanation belongs to the outer set

\[
\|v-a(\theta)\|\le
\delta_\theta:=\rho_\theta+\tau_\theta+\kappa_\theta+
\eta_\theta+\xi_\theta. \tag{1}
\]

Consequently its requested answer belongs to the answer set obtained from (1).
Any singleton or explicit enclosing ball for that outer answer set is a sound
query guarantee. The same statement holds with joint residual sets and their
directional supports in place of balls. Correlated clock/model/sensor errors
need not be independent: containing their sum by a sum of norm bounds is
sufficient, though potentially conservative.

**Proof.** Substitute the actual observation in v-a(theta). The nuisance term
vanishes, leaving the forward difference, sensor contribution and processing
error. Apply the asserted bounds and the triangle inequality. Every legal
explanation satisfies (1), proving the answer-set inclusion. For joint sets,
retain the actual tuple and add its components before taking a support bound.
This is the inclusion theorem of the predecessor with acquisition uncertainty
included among its original coordinates. QED.

The separation and inverse gates are unchanged. In the relative linear-source
case, with nominal physical matrices A_j and all errors bounded by
delta_j times source norm, sufficient conditions are

\[
\lambda_{jk}>\delta_j^2+\delta_k^2,
\qquad \delta_j^2<r^2\mu_j,
\tag{2}
\]

where lambda_jk lower-bounds the Gram matrix of [A_j,-A_k] and mu_j
lower-bounds A_j* A_j. The first identifies the label; the second bounds the
relative error of its exact least-squares source estimate by r. Their proof is
the predecessor's triangle/Cauchy--Schwarz argument. All budgets in (2) have
the same output units and the same source normalization.

## 2. An exact obstruction, and when a clock avoids it

**Theorem 2 (unbounded leakage).** For a fixed admissible (theta,c,m), a finite
bound on

\[
\sup_z\|L(f_{c,m}(\theta)+B_{c,m}z)-a(\theta)\|
\]

exists if and only if LB_c,m=0. Necessity follows by choosing a z0 with
LB_c,m z0 nonzero and scaling it: the reverse triangle inequality diverges.
Sufficiency follows because the expression becomes independent of z. This is
an obstruction to this uniform residual bound, not to every possible decoder.
Bounded nuisance amplitudes, a different common quotient, or explicit joint
clock/nuisance inference are different possible contracts. A small normal
residual of a nominal inverse cannot repair an unbounded physical leakage.

Here is a sharp clock-preservation criterion for the arithmetic application.
Let x_1,...,x_M be distinct real nominal nodes and V_p the vectors sampled from
polynomials of degree at most p, where p>=1 and M>p^2. A proposed clock assigns
real actual nodes s_i. Then

\[
\{(b(s_i))_{i=1}^M:b\in\mathcal P_p\}\subseteq V_p
\quad\Longleftrightarrow\quad s_i=a x_i+b\ \hbox{for every }i.
\tag{3}
\]

**Proof.** The forward implication, applied to the polynomial identity
function, gives a polynomial r of degree at most p with r(x_i)=s_i. Applied
to the pth power, it gives q of degree at most p with q(x_i)=s_i^p. The
polynomial r^p-q has degree at most p^2 and more than p^2 distinct roots, so
is identically zero. If r is nonconstant of degree k, then kp<=p, hence k=1;
constant r is also affine. Conversely composition with an affine function
preserves degree at most p. For a nonzero slope the spaces are equal because
the affine change has an affine inverse. QED.

The same proof on an interval uses infinitely many distinct nodes. On smaller
finite grids (3) is not asserted; interpolation can create exceptions. Our
actual M=8,900 and p in {6,8,10,12} satisfy the stated strict size condition.

**Arbitrarily small jitter counterexample.** Keep M>=p+2 distinct nodes and
move exactly one node by a nonzero h. The sampled linear drift beta*x changes
by beta*h times a coordinate vector. That coordinate vector is outside V_p:
a degree-p polynomial zero at M-1>p distinct nodes cannot be nonzero at the
remaining node. The nominal orthogonal quotient therefore leaves a nonzero
multiple of beta*h, unbounded as beta grows. Positivity of the physical
weights preserves this argument. For equally spaced p+2 nodes, the (p+1)st
finite-difference functional gives an explicit rational witness. Thus small
per-reading clock errors need an amplitude bound or another nuisance model.

## 3. Spatial transfer with a clock interval and generator error

Use the finite reflecting-generator model of the previous spatial packages.
Let H and the actual H+E both be real symmetric positive semidefinite, with
operator norm ||E||<=epsilon_H. The preparation, source modes and spatial
readout maps are fixed contractions. The nominal and actual maps are

\[
A_j(t)=\alpha(t)R e^{-tH}C_j,
\quad A^E_j(t)=\alpha(t)R e^{-t(H+E)}C_j,
\quad \alpha(t)=(1+t)^{1/4}.
\]

All nominal and actual times lie in [1,2]. The saved kernel proves
||A_j(t)-alpha(t)P_j(t)||<=rho uniformly, with rho=10^-9, including
the complete finite-boundary, image, Taylor and coefficient errors.
Let L_P uniformly bound the derivative norm of alpha(t)P_j(t) for every
admissible j. If |t_actual-t_nominal|<=h, then

\[
\|A^E_j(t_{actual})-\alpha(t_{nominal})P_j(t_{nominal})\|
\le\rho+L_P h+\tfrac83\epsilon_H. \tag{4}
\]

**Proof.** Differentiate
exp(-(t-s)(H+E)) exp(-sH) with respect to s and integrate on [0,t].
The resulting Duhamel identity and contraction of both semigroups give
||exp(-t(H+E))-exp(-tH)||<=t||E||. Since alpha<4/3 and t<=2,
this contributes at most 8 epsilon_H/3. Insert the approximating polynomial
at the *actual* time (one charge rho), then integrate its derivative between
actual and nominal times. This proves (4) without differentiating an
uncertified approximation remainder or charging it twice. QED.

The bounds cover all matrices E with the declared norm and positivity; the
correlation of E with time or target is immaterial. They do not automatically
cover changes to preparation, readout, source normalization or channel
locations. Those would require further proved contributions.

For exact rational raw data y, normalize using a rational approximation r0
to 1/alpha(t_nominal). The exact quartic test

\[
(1-e_0)^4\le (1+t_{nominal})r_0^4\le(1+e_0)^4
\]

with 0<=e0<1 proves |alpha(t_nominal)r0-1|<=e0. Contractivity of the
*actual* model implies ||y||<=(4/3+eta)||u||, so the physical processing
charge is xi_actual=e0(4/3+eta), without knowing the target or amplitude.
Combining this with (4) gives

\[
\delta=\eta+\rho+L_P h+\tfrac83\epsilon_H+\xi_{actual}. \tag{5}
\]

The normalization uses the displayed nominal time only. It does not treat it
as the exact physical time; the separate L_P h term accounts for that gap.
The proposed source/label guarantees follow by (2), with all stated gates
checked strictly. Positive true semigroups are essential to this output-gain
argument; arbitrary operator mismatch with no contractivity assumption would
need an enlarged normalization gain.

## 4. Arithmetic transfer with an affine clock

Let t'_j=a t_j+b, |a-1|<=epsilon_a<1, |b|<=epsilon_b. Arbitrary complex
degree-p polynomial drift in t'/890 becomes degree-p polynomial drift in
t/890 and is exactly included in the augmented nominal inverse. For a real
sinusoidal component A sin(omega*t'/890+phi), the resulting phase is arbitrary
and its nominal frequency is at most Omega_eff=(1+epsilon_a)Omega when
|A|<=B and |omega|<=Omega. Let K_(W,p)(Omega_eff) be a proved uniform
weighted polynomial approximation error. Its residual consumes

\[
\nu=B K_{W,p}(\Omega_{eff}).
\]

For the full arithmetic signal F(t)=sum_(n>=1) a(n)n^(-2-it), assume the
same coefficient envelope 0<=a(n)<=d_14(n) as the complete-tail theorem.
There is a finite uniform derivative envelope

\[
D=\sum_{n\ge2}d_{14}(n)\log(n)n^{-2}
 =14\zeta(2)^{13}\sum_{n\ge2}\log(n)n^{-2}. \tag{6}
\]

**Proof.** Write d14 as the number of ordered 14-tuples with product n.
Expanding the nonnegative sum and log(product)=sum log(factors) separates
the 14 factors, giving (6). The sums converge: the latter scalar sum has
integral tail (log N+1)/N after N>=2, since log(x)/x^2 is decreasing there.
The coefficient-wise inequality |exp(-it' log n)-exp(-it log n)|
<=|t'-t| log n then bounds the absolutely convergent full signal difference
by D|t'-t|. No finite-tail truncation substitutes for this bound. QED.

The actual W has positive weights summing to one and |t_j|<890. Thus a valid
absolute weighted timing charge is

\[
\tau\le D\sqrt{\sum_j w_j(\epsilon_a|t_j|+\epsilon_b)^2}
\le D(890\epsilon_a+\epsilon_b). \tag{7}
\]

This bound is conservative; it covers all allowed integer coefficients and
clock parameters at once. Let kappa independently bound the physical weighted
norm of all mismatch outside the declared polynomial/sinusoidal family. This
is an additive model assumption, not a residual estimated by the inverse.
If eta bounds sensor error, Xi bounds digital centering, f>0 is the augmented
Gram floor, A_n is the complete centered tail bias, and rho_N is the verified
normal residual, the existing inverse gives

\[
E_n=A_n+n^2\left[
\frac{\eta+\nu+\tau+\kappa+\Xi}{\sqrt f}
+\frac{\rho_N}{f}\right]. \tag{8}
\]

Each strict E_n<1/2 certifies integer rounding. To avoid unchecked square
roots, verify m_n=1/2-A_n-n^2 rho_N/f>0 and
n^4(eta+nu+tau+kappa+Xi)^2<m_n^2 f. Optimizing the approximation factor
alone is insufficient: changing p also changes f, A_n and the actual solve
residual. The finite comparison in this package optimizes these *sufficient*
budgets over four declared degrees, not the information-theoretic optimum.

The actual affine clock keeps the polynomial nuisance representable while
(6)--(8) charge its effect on the arithmetic signal and sinusoidal frequency.
Equation (3) states the exact scope of this route when polynomial amplitude
is unrestricted. The spatial errors are source-relative; (8) uses absolute
weighted complex-reading error. Their transfer logic is common, their units
are not interchangeable.
