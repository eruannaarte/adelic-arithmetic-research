# Structured transfer after nuisance removal

This is a proved extension of the [uncertain-acquisition theorem](../../uncertain_transfer_2026_09/framework/PROOFS.md).
Its purpose is to retain known directions through the inverse or query, instead
of charging every disturbance at the weakest singular value. All physical
approximation and nonlinear remainder bounds remain separate premises with
reconstruction paths. No historical novelty claim is made.

## 1. Forward separation and inverse accuracy need different bounds

Work after a valid nuisance operation L, with its transported physical norm.
In particular, L must annihilate the nuisance images of every admitted clock
and model, or their leakage must already have a finite declared bound. For a
label j and a nonzero Euclidean source u, suppose the actual processed reading
has the representation

\[
y=A_j u+D_j(z)u+e_j,\qquad
D_j(z)=\sum_{r=1}^s z_rD_{jr},\quad z\in Z_j,
\quad\|e_j\|\le r_j\|u\|. \tag{1}
\]

The last radius includes sensor error, finite approximation, verified
processing, and the **complete** nonlinear Taylor remainder. The set Z_j
retains joint uncertainty; one parameter is not replaced by an independent
copy at each reading. Let B_j=A_j^dagger, assume A_j* A_j>=mu_j I>0,
and establish

\[
F_j\ge\sup_{z\in Z_j}\|D_j(z)\|,
\qquad V_j\ge\sup_{z\in Z_j}\|B_jD_j(z)\|. \tag{2}
\]

**Theorem 1 (directional inverse transfer).** The usual outer tube with
radius delta_j=F_j+r_j is valid for label feasibility and separation. After
the correct label is known, the ordinary nominal least-squares estimate
satisfies

\[
\frac{\|\widehat u-u\|}{\|u\|}
\le V_j+\frac{r_j}{\sqrt{\mu_j}}. \tag{3}
\]

For a linear query Q_j u, replace V_j by sup_z||Q_jB_jD_j(z)|| and the
last gain by ||Q_jB_j||. The declared source normalization still determines
the right-hand relative radius.

**Proof.** The triangle inequality gives the outer forward tube. Since
B_j A_j=I, the reconstruction error is B_jD_j(z)u+B_j e_j. Apply (2)
and ||B_j||<=1/sqrt(mu_j), or the corresponding query bounds. QED.

Equation (3) can be much stronger than (F_j+r_j)/sqrt(mu_j): it does not
force a known physical direction into the inverse's worst direction. No new
information is asserted to arise from the deterministic inverse itself.

For a box Z=product_r[-h_r,h_r], each norm in (2) is a convex function of
z. Every box point is a convex combination of its vertices, and D is linear,
so the supremum is attained at a vertex. Thus a complete bound on all corner
matrices, before taking norms, covers the whole joint parameter box. Frobenius
norm bounds are sufficient upper bounds on operator norms. For another compact
convex polytope the same argument uses its vertices. A nonlinear uncertainty
map requires a separately proved remainder or direct enclosure; the vertex
rule alone does not apply to arbitrary nonlinear maps.

Different candidate explanations of the same observation may assign
**different** unknown clock/model parameters. Their feasible tubes must allow
those choices independently. Sharing a parameter across readings within one
explanation never licenses forcing the same unknown value on two competing
explanations.

## 2. Preserve the two source norms in a pair comparison

Write G_jk=[A_j,-A_k]*[A_j,-A_k]. Suppose delta_j and delta_k are the
separate relative tube radii. A general sufficient separation condition is

\[
G_{jk}\succ\operatorname{diag}(c_j I,c_k I),
\qquad c_j,c_k>0,
\qquad \frac{\delta_j^2}{c_j}+\frac{\delta_k^2}{c_k}\le1. \tag{4}
\]

**Theorem 2 (weighted pair transfer).** Condition (4) makes the two tubes
disjoint for all nonzero source choices.

**Proof.** A common observation would give
||A_j u-A_k v||<=delta_j||u||+delta_k||v||. Weighted Cauchy--Schwarz
bounds the square of this right side by

\[
\left(\frac{\delta_j^2}{c_j}+\frac{\delta_k^2}{c_k}\right)
(c_j\|u\|^2+c_k\|v\|^2).
\]

The strict positive-definite inequality in (4) makes the left side's square
larger than c_j||u||^2+c_k||v||^2, a contradiction. QED.

For equal radius delta and any 0<a<1, use c_j=delta^2/a and
c_k=delta^2/(1-a). The reciprocal sum in (4) is exactly one. The usual
uniform pair-floor condition is the special choice a=1/2. Other choices
retain the unequal source-block norms in a weak pair direction. The split
is a proof parameter: it need not be measured or supplied to the decoder.
It may vary with the pair and nominal-time cell if complete coverage is proved.

For the six-row certificate the saved matrices are P=A/alpha and
alpha>=19/16. It therefore checks

\[
[P_j,-P_k]^*[P_j,-P_k]
\succ b^2\operatorname{diag}(a^{-1}I,(1-a)^{-1}I),
\quad b=(\eta+\rho+\xi)/(19/16). \tag{5}
\]

Its polynomial leading principal minors are strictly positive on each whole
time cell. Sylvester's criterion follows, for example, by successive exact
completion of squares: the positive pivots are ratios of consecutive positive
leading determinants. Thus the Gram difference is positive definite at every
time. Rational polynomial interval bounds, including all endpoints and all
231 source/pair covers, make (5) a continuous-time proof, not a sampled check.

## 3. Structured spatial potential: an actual inverse-direction consequence

The physical family is H(g)=I tensor Lx+Ly tensor diag(1+g*x), g0=4/5.
The seven rows and all source/target ranges stay as in the preceding package.
Both actual and nominal times lie in [1,2], |dt|<=h=5e-7 and
|dg|<=2.5e-6. This family stays positive semidefinite. Exact raw normalization
is at the nominal time; the true contraction bound remains 4/3 plus sensor
radius. It therefore needs no unknown source amplitude.

The [complete derivative reconstruction](../resolution/PROOFS.md) gives P(t),
its time derivative and a new potential derivative Q(t), with derivative
operator errors at most 1e-12. In normalized coordinates the linear direction
is

\[
D_{norm}(dt,dg)=dt\left(P'(t)+\frac{P(t)}{4(1+t)}\right)+dg\,Q(t).
\tag{6}
\]

The physical direction is alpha(t)D_norm, while its inverse effect is
P^dagger D_norm: the normalization cancels exactly. All four clock/potential
corners are enclosed on 128 cells for each of 21 labels. The certified limits
are F<=6.6e-8 and V<=2.8e-5. The complete nonlinear and derivative-error
radius is

\[
R=\tfrac12h^2+128h|dg|+\tfrac{128}{3}|dg|^2
+(h+|dg|)10^{-12}. \tag{7}
\]

The derivative proof supplies semigroup, finite boundary, Fourier image,
temporal and numerical bounds for every term. In particular, it does not
differentiate an unproved approximation remainder.

At eta=1.1e-7 and rho=xi=1e-9, set r=eta+rho+xi+R. The old seven-row
physical floors remain mu=1083/51200000000 and
lambda=361/5120000000000000. They prove

\[
2(F+r)^2<\lambda,\qquad
V+r/\sqrt\mu<0.001. \tag{8}
\]

The coarser accuracy gate (F+r)/sqrt(mu)<0.001 fails for the same
certified F. Equations (2)--(3) therefore supply a demonstrated sufficient
certificate improvement, not merely common terminology. The full geometric
error may be smaller than any of these bounds. The potential tolerance is
10,000 times the earlier *chosen* generic profile's implied |dg|<=2.5e-10;
this ratio does not claim optimality of either method.

## 4. Complete arithmetic phase pairing retains the shared clock direction

Let t'=t+s t+b with |s|<=m*1e-14 and |b|<=m*1e-11. The unrestricted
polynomial nuisance stays in the nominal polynomial space because this clock
is affine. For F(t)=sum a(n)n^(-2-it), the first clock variation is

\[
-i(st+b)\sum_{n\ge2}c_n e^{-it\log n},
\qquad 0\le c_n\le C_n=d_{14}(n)\log(n)/n^2. \tag{9}
\]

For each fixed admissible source, the W-norm of (9) is convex in (s,b).
Its maximum on the clock rectangle therefore occurs at a corner. At a base
corner write st+b=1e-11*(sign_s*t/1000+sign_b)=1e-11*p(t). Define

\[
\gamma_p=\frac{|\sum_j w_jp(t_j)^2e^{it_j\log2}|}
{\sum_j w_jp(t_j)^2}. \tag{10}
\]

Every positive integer belongs to exactly one pair (n,2n) with even v2(n).
For such a pair, expansion of the squared W-norm gives

\[
\|p(c_ne^{-it\log n}+c_{2n}e^{-it\log(2n)})\|_W
\le\|p\|_W\sqrt{C_n^2+C_{2n}^2+2\gamma_p C_nC_{2n}}. \tag{11}
\]

To justify replacing the actual coefficients by their envelopes, first bound
the cross inner product by its absolute value. The resulting quadratic has
nonnegative coefficients and increases in both nonnegative magnitudes. Thus
(11) does **not** assume that actual coefficients have a prescribed ratio.
Only the envelope ratio is used subsequently.

For n>1 with k=v2(n), the envelope ratio is

\[
\frac{C_{2n}}{C_n}=\frac{k+14}{4(k+1)}\frac{\log(2n)}{\log n}.
\]

For even k>=2 this lies between (k+14)/(4(k+1)) and (k+14)/(4k).
For k=0,n>=3 it lies between 7/2 and 35/6, since log2/log3<2/3
follows from 8<9. These ratios imply positive lower bounds q_k on
C_n C_2n/(C_n+C_2n)^2. Equation (11) is bounded by

\[
\|p\|_W(C_n+C_{2n})\sqrt{1-2(1-\gamma_p)q_k}. \tag{12}
\]

The pair (1,2), whose first derivative coefficient is zero, is charged
separately. Sum (12) by the triangle inequality over the entire partition.
The [arithmetic proof](../arithmetic/PROOFS.md) evaluates its complete mass by
odd-part Dirichlet products and explicit positive series tails. The refined
valuation classes stop at k=38, but every remaining class keeps a proved
global factor; no coefficient or infinite tail is dropped.

A complete second-derivative envelope D2 gives the actual exponential
remainder at each reading at most D2*|st+b|^2/2. Its W-norm is bounded
using the fourth weighted clock moment. Convexity of the linear norm and of
the fourth moment covers the entire clock rectangle, not just its four
corners. The resulting complete clock bound has the form

\[
\tau_W(m)\le m L_W+m^2 R_W. \tag{13}
\]

The weighted moment gain and the phase-pairing gain are recorded separately.
Any exact nuisance quotient is a contraction in the physical weighted norm,
so (13) remains valid after polynomial nuisance removal. The arithmetic
application uses this complete reading-space bound followed by the existing
query inverse gain; it does not claim that (13) is an optimal projected
query bound. The spatial application additionally exploits the explicit
inverse direction in (3).

Combining (13) with the complete arithmetic tail, weighted sinusoidal
approximation, mismatch, sensor, centering and newly verified solve residual
recovers the strict integer gates of the preceding theorem. At sixtyfold
clock radii these gates succeed for both windows, while the prior pointwise
clock enclosure fails for the outer window under the same requirements.
This is a proved improvement of sufficient certificates, not an intrinsic
noise threshold or measured clock calibration.
