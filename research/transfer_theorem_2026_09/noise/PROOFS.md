# Complete oscillatory tails with polynomial drift

This result improves a sufficient recovery certificate for the same physical experiment. It proves recovery of all 49 unknown integer coefficients through degree twelve of unrestricted polynomial drift. Its new ingredient is a uniform discrete oscillatory bound for every omitted frequency through a large cutoff, combined with a complete analytic bound above that cutoff. No finite frequency scan or truncated tail is used as a proof.

## 1. Physical experiment and inherited premises

There are exactly 8,900 complex observations at

\[
t_j=(2j+1-8900)/10,\qquad 0\le j<8900.
\]

For one declared design let \(W=\operatorname{diag}(w_j)>0\), \(\sum_jw_j=1\). The two weight vectors are precisely those in the [predecessor proof](../../unified_query_2026_09/noise/PROOFS.md): the outer window, and its mixture with the nested 2,550-point window with coefficient \(125/65536\). Inner and outer windows reuse the same readings. They do not have independent errors. The measurement model is

\[
y_j=\sum_{n\ge1}a(n)n^{-2-it_j}+\sum_{k=0}^p\beta_k(t_j/890)^k+e_j,
\quad \|e\|_W\le\eta,
\]

where every \(a(n)\) is an integer with \(0\le a(n)\le d_{14}(n)\), \(a(1)=1\) is known, and all complex \(\beta_k\) are unrestricted. The theorem is for this envelope source class, without additional multiplicativity assumptions. The target is \((a(2),\ldots,a(50))\). Complex absolute error less than \(1/2\) suffices for rounding the real part.

Absolute convergence follows from the elementary product identity

\[
\sum_{n\ge1}d_{14}(n)n^{-s}=\zeta(s)^{14}\quad(s>1).
\]

Indeed multiplying fourteen absolutely convergent positive Dirichlet series counts the ordered fourteen-factor decompositions of each integer. Thus regrouping and all tail estimates below are legitimate.

Subtract the known complete midpoint vector

\[
u(t)=\tfrac12\left(\zeta(2+it)^{14}-\sum_{n\le50}d_{14}(n)n^{-2-it}\right).
\]

Its stored digital realization \(\widetilde u\) has the inherited, fully reconstructed physical error \(\|u-\widetilde u\|_W\le\Xi=10^{-20}\). The remaining complete tail is

\[
h(t)=\sum_{n>50}\bigl(a(n)-d_{14}(n)/2\bigr)n^{-2-it},\qquad
|h(t)|\le H_0=\tfrac12\left(\zeta(2)^{14}-\sum_{n\le50}d_{14}(n)n^{-2}\right).
\]

The code uses an outward upper bound for \(H_0\), approximately 469.812014357584.

Let \(\Phi_{jn}=e^{-it_j\log n}\), \(1\le n\le50\), and \(G=\Phi^*W\Phi\). The inherited physical certificates supply row bounds

\[
\sum_{m\ne n}|G_{nm}|\le q_n,\quad q=\max_nq_n<1,
\quad |(G^{-1}\Phi^*Wh)_n|\le B_n/(2n^2).
\tag{1}
\]

Here \(B_n\) is the previous complete uncentered arithmetic bias bound; linearity halves it after centering. Its finite arithmetic sum through \(10^6\), complete remote tail, and exact prescribed window form are unchanged premises, bound to the previous certificate by hashes and strict consequence checks. Their expensive original tail enumerations were replayed in the earlier package, not rerun in this extension. Every new producer run does freshly reconstruct the actual arithmetic Gram matrix, all 8,900 digital corrections, \(H_0\), and every new polynomial quantity. The numerical premises are outward interval enclosures, not claims inferred from saved Gram matrices alone.

## 2. Complete summation by parts, including endpoints

Let \(r_0,\ldots,r_{m-1}\) be real or complex and extend it by zero to every integer. Put

\[
V_2(r)=\sum_{j\in\mathbb Z}|r_j-2r_{j-1}+r_{j-2}|.
\]

For \(|z|=1\), \(z\ne1\), finite reindexing gives

\[
(1-z)^2\sum_jr_jz^j
=\sum_j(r_j-2r_{j-1}+r_{j-2})z^j,
\qquad
\left|\sum_jr_jz^j\right|\le\frac{V_2(r)}{|1-z|^2}.
\tag{2}
\]

There are \(m+2\) potentially nonzero differences, including both zero extensions. Omitting the boundary terms invalidates (2): for an odd length constant sequence and \(z=-1\), all internal second differences vanish but the oscillatory sum is one. The complete variation is four, giving the correct bound one.

Construct the real polynomials \(\psi_0=1,\psi_1,\ldots,\psi_p\) by exact weighted Gram–Schmidt on \(1,x,\ldots,x^p\), \(x=t/890\), with positive leading coefficients. They satisfy \(\Psi^*W\Psi=I\) for \(\Psi=[\psi_1,\ldots,\psi_p]\), and each positive-degree polynomial is orthogonal to the constant. The model reconstruction proves positive residual norms and encloses the defining polynomial identities. Symmetric weights give the exact degree parity. Define

\[
\ell_k=\sum_jw_j|\psi_k(t_j/890)|\le1,\quad
V_{2,k}=V_2\bigl((w_j\psi_k(t_j/890))_j\bigr).
\]

The bound \(\ell_k\le1\) is weighted Cauchy–Schwarz, but the sharper actual \(\ell_k\) is used. From the physical spacing \(1/5\), the response to frequency \(\log n\) has ratio \(z=e^{-i\log n/5}\). Its initial phase has modulus one. Therefore (2) applies directly to each physical nuisance-tail channel.

## 3. Uniform finite-frequency bound and every remote coefficient

Set \(N=10^{12}\). For every integer \(51\le n\le N\),

\[
0.39<\theta=\log(n)/10<2.8<\pi,
\quad |1-e^{-i\log(n)/5}|=2\sin\theta>2/3.
\tag{3}
\]

These constants have exact rational checks. An upper exponential series plus geometric remainder proves \(e^{3.9}<51\); a finite positive exponential sum proves \(e^{28}>10^{12}\). The alternating sine series gives

\[
\sin(0.39)\ge0.39-0.39^3/6>1/3,
\quad
\sin(2.8)\ge\sum_{k=0}^{7}\frac{(-1)^k(2.8)^{2k+1}}{(2k+1)!}>1/3.
\]

The omitted sine-series terms decrease in magnitude at these truncation points (at 2.8 they decrease from the cubic term onward). The alternating remainder therefore has the required nonnegative sign. Concavity on \([0,\pi]\) puts every intermediate sine above the smaller endpoint value. The elementary \(\pi>3\) puts the whole interval in this concavity range. Thus (3) holds uniformly; it is not a sampled estimate.

Writing \(L_k(n)=\sum_j w_j\psi_k(t_j/890)e^{-it_j\log n}\), equations (2)–(3) give \(|L_k(n)|\le(9/4)V_{2,k}\) throughout the finite band. Consequently the centered finite contribution to \(|(\Psi^*Wh)_k|\) is at most \((9/4)H_0V_{2,k}\). Using the complete \(H_0\) in this finite bound is conservative and avoids enumeration through \(N\).

For every \(n>N\), \(n^{-2}\le N^{-1/2}n^{-3/2}\), so the **entire infinite remote mass** is bounded by

\[
M_{\rm rem}=\frac{\zeta(3/2)^{14}}{2\sqrt N}
=\frac{\zeta(3/2)^{14}}{2\cdot10^6}<0.344721270427.
\tag{4}
\]

At these frequencies use the always-valid \(|L_k(n)|\le\ell_k\). This includes all frequencies arbitrarily close to later sampling aliases; extending (3) to infinity would be false. The complete new channel is therefore

\[
|(\Psi^*Wh)_k|\le C_k:=\tfrac94 H_0V_{2,k}+M_{\rm rem}\ell_k.
\tag{5}
\]

Outward upper endpoints for \(H_0,V_{2,k},\ell_k,\zeta(3/2)\) preserve every inequality, and the subsequent powers and products are exact rational arithmetic. For degree six the multiscale channel is below 0.231366803825: its finite contribution is below 0.004739742999 and its remote contribution below 0.226627060826. The outer channel is below 0.231428433085. Each is more than 1,334 times smaller than its old \(H_0\ell_6\) bound. This is a gain in the certified enclosure; the true experiment and its information have not changed.

## 4. Transfer through the physical quotient and finite inverse

Set \(X=[\Phi,\Psi]\) and \(H=X^*WX\). The constant nuisance is already in \(\Phi_{\cdot1}=1\); the corresponding fitted coordinate is \(a(1)+\beta_0\) and is discarded. All other polynomial coefficients are represented exactly by \(\Psi\). Let \(C=\Phi^*W\Psi\) and let \(c_{nk}\) bound \(|C_{nk}|\). In this section \(C\) is a matrix; the scalar channel bounds are \(C_k\) from (5).

The following nonnegative bounds are computed separately at each degree:

\[
v_{nk}=c_{nk}+q_n\max_hc_{hk}/(1-q),\quad
M_{kl}=\sum_nc_{nk}v_{nl},\quad
m_k=\sum_lM_{kl},\quad \mu=\max_km_k,
\]
\[
Q_{\rm aug}=\max\left\{\max_n\left(q_n+\sum_kc_{nk}\right),\ \max_k\sum_nc_{nk}\right\}.
\tag{6}
\]

The Neumann series for \(G^{-1}\) and the row refinement in (1) imply \(|(G^{-1}C)_{nk}|\le v_{nk}\). Hence \(|(C^*G^{-1}C)_{kl}|\le M_{kl}\). The exact nuisance Schur complement is \(I-C^*G^{-1}C\), and \(\mu<1\) supplies its componentwise inverse bound. Gershgorin applied to the Hermitian augmented Gram gives

\[
H\succeq(1-Q_{\rm aug})I>0.
\tag{7}
\]

For the complete tail, put

\[
R_k=C_k+\sum_nc_{nk}B_n/(2n^2),\quad
s_k=R_k+m_k\max_lR_l/(1-\mu).
\]

The normal equations give the nuisance tail coefficients
\((I-C^*G^{-1}C)^{-1}(\Psi^*Wh-C^*G^{-1}\Phi^*Wh)\), bounded componentwise by \(s_k\). Substituting into the arithmetic block bounds the decoded coefficient tail by

\[
A_n=B_n/2+n^2\sum_kv_{nk}s_k.
\tag{8}
\]

For any physical perturbation \(e'\), the map \(H^{-1}X^*W\) has norm at most \((1-Q_{\rm aug})^{-1/2}\) from the physical \(W\)-norm to Euclidean coefficient norm: after whitening it is the full-column-rank least-squares inverse. Thus digital centering plus sensor error contribute at most \(n^2(\eta+\Xi)/\sqrt{1-Q_{\rm aug}}\). The total exact-solve bound is

\[
|\widehat a(n)-a(n)|\le A_n+\frac{n^2(\eta+\Xi)}{\sqrt{1-Q_{\rm aug}}}.
\tag{9}
\]

For each \(n=2,\ldots,50\) the consumer first checks \(A_n<1/2\), then the strict rational inequality

\[
n^4(\eta+\Xi)^2<(1/2-A_n)^2(1-Q_{\rm aug}).
\tag{10}
\]

The positivity check precedes squaring. Therefore all compatible sources give the same rounded 49-tuple.

This is an instance of [the common transfer theorem](../framework/PROOFS.md): the unrestricted nuisance space is the complete polynomial span through degree \(p\). Exact \(W\)-orthogonal elimination is an attained metric quotient and preserves the answer set with its correctly projected noise ball. The complete infinite tail enters the finite inverse through (1) and (5). The scalar output enclosure (9) contains every answer consistent with the actual observation; (10) isolates one integer. Fitting the augmented normal equations is a convenient equivalent implementation of the nuisance elimination for the requested coordinates. It does not require physically independent readings for the nested window.

## 5. Certified consequences and computation contract

The core evidence was frozen at degree six before the bounded successor at degrees eight, ten, and twelve. All entries below pass (10) for all 49 unknown coefficients. Displayed bias numbers are rounded **upward**; exact rational records govern acceptance.

| Polynomial degree | Multiscale maximum \(A_n\) | Multiscale \(\eta\) | Outer maximum \(A_n\) | Outer \(\eta\) |
|---:|---:|---:|---:|---:|
| 6 | 0.249284107184 | 0.000100 | 0.298235974205 | 0.000080 |
| 8 | 0.249675965042 | 0.000100 | 0.298629056012 | 0.000080 |
| 10 | 0.250385107704 | 0.000099 | 0.299340416429 | 0.000080 |
| 12 | 0.251520391985 | 0.000099 | 0.300479209164 | 0.000079 |

The earlier complete pointwise method gives maximum degree-six bounds above 0.611665785764 and 0.661793584785, reproduced exactly as controls. These were failed sufficient certificates, not impossibility theorems. The new degree-six sensor allowances equal the earlier centered no-drift allowances. A lower-degree polynomial is already a member of each higher-degree nuisance space; consequently the table also certifies every degree below each listed value at that row's allowance. It does not establish maximal possible degree or an optimal noise threshold.

**An implementation must account for the solve.** Let \(\widetilde\theta\) be a proposed computed augmented coefficient vector and suppose a certified evaluation of the *exact physical* normal residual proves

\[
\|r\|_2=\|H\widetilde\theta-X^*W(y-\widetilde u)\|_2\le\rho.
\]

Equation (7) then gives \(\|\widetilde\theta-\theta_{\rm exact}\|_2\le\rho/(1-Q_{\rm aug})\). The sufficient coefficient bound is (9) plus \(n^2\rho/(1-Q_{\rm aug})\). The independent consumer proves that **\(\rho\le10^{-8}\)** is allowed jointly with each displayed sensor radius and \(\Xi\), for every coordinate in all eight cases. It checks positive margins after subtracting this solve contribution, followed by (10) with those smaller margins.

This is a conditional acceptance contract, not a claim that a deployed floating decoder already certifies its residual. Errors in matrices, dot products and residual evaluation must themselves be enclosed when asserting \(\rho\). Any nonzero leakage of an approximate projector on the unrestricted polynomial space can be made arbitrarily large by scaling the drift. Thus closeness of an approximate projector alone cannot justify a uniform amplitude-independent budget. The exact theorem permits arbitrary drift amplitude; a floating implementation must meet the data-dependent residual contract or another valid error bound.

The two weight designs use different specified \(W\)-balls, even though physical coordinates and reading count coincide. Their radii compare guarantees in those stated norms. A pointwise bound \(|e_j|\le\eta\) implies either normalized \(W\)-bound. For independent equal-variance errors on the *physical* readings, covariance is

\[
\sigma^2H^{-1}X^*W^2XH^{-1},
\]

including the cross term in the squared mixed weights. The theorem assumes no random noise distribution and establishes no universal statistical superiority.

## 6. Boundaries and validation scope

Without known \(a(1)\), that coefficient is exactly aliased with the constant drift. At degree 8,899 arbitrary complex data on these distinct 8,900 times can be polynomial interpolation data, destroying all such source recovery. Neither boundary identifies the best degree between twelve and 8,899. The cutoff \(10^{12}\) is an analysis device, not an acquisition count, and frequencies above it remain explicitly included by (4).

The producer uses outward Arb arithmetic for the actual polynomial moments, finite sums, absolute variations, zeta values and inherited digital correction. All final inequalities are independently rederived with Python standard-library rational arithmetic. Independent direct-vector Gram–Schmidt, physical-map examples, endpoint and alias controls, tamper rejections and a second precision reconstruction exercise materially different failure modes. Numerical examples are diagnostics, not the uniform proof. The theorem is conditional on its mathematical source/noise/model assumptions and verified enclosures; it supplies no empirical apparatus validation.
