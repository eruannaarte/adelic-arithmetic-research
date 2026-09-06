# Complete polynomial-drift recovery theorem

## 1. Model, unchanged acquisition, and exact answer-set quotient

Let

\[
F_a(t)=\sum_{n\ge1}a(n)n^{-2-it},\qquad
a(n)\in\mathbb Z,\quad 0\le a(n)\le d_{14}(n),\quad a(1)=1.
\]

Here \(d_{14}(n)\) counts ordered factorizations into fourteen positive integers. The product formula \(d_{14}(\ell^e)=\binom{e+13}{13}\), together with absolute convergence, gives \(\sum d_{14}(n)n^{-s}=\zeta(s)^{14}\) for \(\Re s>1\). Thus every source series above converges absolutely.

The actual observations are

\[
y_j=F_a(t_j)+b(t_j)+\epsilon_j,\qquad
t_j=(2j+1-8900)/10,\quad 0\le j<8900,
\]

where \(b\) is an arbitrary complex polynomial of degree at most \(p\). Its coefficients have no magnitude restriction. The error obeys \(\|\epsilon\|_W\le\eta\), with \(\|z\|_W^2=z^*Wz\). We separately use the original positive outer weights and the original multiscale weights

\[
W=(125/65536)W_S+(1-125/65536)W_L.
\]

The inner 2,550 samples are the outer indices 3,175 through 5,724; their weights are extended by zero before addition. The original eight cosine coefficients are their exact binary64 rational values. Both weight vectors have mass one and are even in time. This is the same 8,900-reading physical acquisition; fitting additional nuisance columns requires additional computation. The two choices of \(W\) define different weighted error balls. A common pointwise bound \(\max_j|\epsilon_j|\le\eta\) implies either weighted bound.

**Exact nuisance quotient.** Let \(\mathcal B_p\) be the subspace of sampled polynomials of degree at most \(p\), and \(P_p\) its \(W\)-orthogonal complementary projector. For every actual source \(a\),

\[
\exists b\in\mathcal B_p,\ e:\ y=F_a+b+e,\ \|e\|_W\le\eta
\quad\Longleftrightarrow\quad
\|P_p(y-F_a)\|_W\le\eta. \tag{1}
\]

The forward direction uses \(P_pb=0\) and the contraction of an orthogonal projection. Conversely choose \(e=P_p(y-F_a)\), and take \(b=(I-P_p)(y-F_a)\in\mathcal B_p\). This proves (1), including the closed-ball endpoint. Hence projecting out the unrestricted polynomial nuisance preserves the exact set of possible answers to every query on the original source class. No approximation of that source class is needed for this equivalence.

The finite calculation below is a subsequent certified enclosure of those answers. Subtracting a known deterministic center is an invertible translation of the data and leaves the experiment's information unchanged. The gain it enables is a gain in the decoder's sufficient certificate, not in the information contained in a fixed observation.

## 2. Exact polynomial basis and complete new tail channels

Write \(x=t/890\). Gram–Schmidt in the actual \(W\) inner product defines real polynomials \(\psi_0=1,\psi_1,\ldots,\psi_p\), where each leading coefficient is positive and

\[
\psi_d=\frac{x^d-\sum_{k<d}\langle\psi_k,x^d\rangle_W\psi_k}
 {\left\|x^d-\sum_{k<d}\langle\psi_k,x^d\rangle_W\psi_k\right\|_W}.
\]

The denominator is positive whenever \(d<8900\): a degree-\(d\) nonzero polynomial cannot vanish on all 8,900 distinct points carrying positive weights. Taking inner products proves inductively that the new polynomial is orthogonal to every preceding one and has norm one. Symmetry makes \(\psi_d\) even or odd with parity \(d\), since opposite-parity moments vanish. These elementary identities justify exact orthogonality; the stored interval identity checks are additional diagnostics.

Let \(\Phi_{jn}=e^{-it_j\log n}\), \(1\le n\le50\), and let \(\Psi\) contain \(\psi_1,\ldots,\psi_p\) evaluated on the grid. Set

\[
G=\Phi^*W\Phi,\quad C=\Phi^*W\Psi,\quad
H=\begin{pmatrix}G&C\\C^*&I_p\end{pmatrix}. \tag{2}
\]

In particular \(C_{1k}=0\). Other cross products are real for even \(k\) and purely imaginary for odd \(k\). Their nonzero coordinate is the actual sum

\[
2\sum_{t_j>0}w_j\psi_k(t_j/890)
\begin{cases}\cos(t_j\log n),&k\text{ even},\\
\sin(t_j\log n),&k\text{ odd}.
\end{cases} \tag{3}
\]

This physical-grid sum is freshly evaluated outward; it is not inferred from an approximate saved matrix.

As before, subtract the known full envelope midpoint

\[
u(t)=\tfrac12\left[\zeta(2+it)^{14}-\sum_{n\le50}d_{14}(n)n^{-2-it}\right]. \tag{4}
\]

Its supplied rational approximation \(\widetilde u\) has pointwise complex error strictly below \(\xi=10^{-20}\) at every observation. That bound is replayed for the entire vector. The centered omitted signal is

\[
h(t)=\sum_{n>50}(a(n)-d_{14}(n)/2)n^{-2-it},\quad
|h(t)|\le h_0:=\tfrac12\left[\zeta(2)^{14}-\sum_{n\le50}d_{14}(n)/n^2\right]. \tag{5}
\]

This includes every omitted index, with no cutoff. Numerically \(469<h_0<470\). Define

\[
\ell_k=\sum_jw_j|\psi_k(t_j/890)|\le1.
\]

The inequality follows from Cauchy–Schwarz and weight mass one. The **complete new nuisance channel** obeys

\[
|\psi_k^*Wh|\le h_0\ell_k. \tag{6}
\]

The actual \(\ell_k\) is substantially smaller than one. Its outward finite sum makes (6) sharper than the former unit-norm bound \(h_0\). Crucially, (6) is a bound on the entire infinite omitted source; adding a polynomial column while retaining only the old arithmetic-channel tail bounds would not prove the result.

## 3. Componentwise Schur elimination with a complete bias bound

The inherited complete arithmetic certificates provide nonnegative rational bounds \(B_n\), and absolute off-diagonal row bounds \(q_n\) for \(G\), with \(q=\max q_n<1\). They include finite sums to \(10^6\) and verified remote tails beyond \(10^6\). Their consequence after exact centering is

\[
z=G^{-1}\Phi^*Wh,\qquad |z_n|\le b_n:=B_n/(2n^2). \tag{7}
\]

Let \(c_{nk}\) bound \(|C_{nk}|\), and define

\[
v_{nk}=c_{nk}+\frac{q_n\max_h c_{hk}}{1-q},\qquad
M_{k\ell}=\sum_n c_{nk}v_{n\ell},\qquad
m_k=\sum_\ell M_{k\ell},\qquad\mu=\max_km_k. \tag{8}
\]

The Neumann expansion of \(G^{-1}=(I+(G-I))^{-1}\) gives \(|(G^{-1}C)_{nk}|\le v_{nk}\): the first nonidentity row has sum at most \(q_n\), and subsequent powers cost successive factors at most \(q\). It follows that for the exact Schur complement \(S=I-C^*G^{-1}C\),

\[
|I-S|\le M\quad\hbox{entrywise},\qquad\|I-S\|_\infty\le\mu.
\]

All explored cases satisfy \(\mu<1\). Since \(S\) is Hermitian, the same row-sum bound implies positivity and hence invertibility of \(S\) and \(H\). Set

\[
r_k=h_0\ell_k+\sum_nc_{nk}b_n,\qquad
s_k=r_k+\frac{m_k\max_\ell r_\ell}{1-\mu}. \tag{9}
\]

For the true Schur residual \(r^{\rm true}=\Psi^*Wh-C^*z\), equations (6)–(7) give \(|r^{\rm true}_k|\le r_k\). Summing the Neumann series for \(S^{-1}\), with the first defect row treated separately, gives

\[
|(S^{-1}r^{\rm true})_k|\le s_k. \tag{10}
\]

Solving the two block equations in (2) shows that the arithmetic part of the augmented fitted tail is

\[
z-G^{-1}C S^{-1}(\Psi^*Wh-C^*z).
\]

After multiplication by \(n^2\), its complete coefficient bias is therefore at most

\[
A_n=B_n/2+n^2\sum_kv_{nk}s_k. \tag{11}
\]

Equations (5)–(11) retain all complete arithmetic and nuisance tails. No assumption of independent polynomial channels is made.

## 4. Noise, rounding, and the proved numerical conclusion

The augmented Gram in (2) has diagonal one and absolute off-diagonal row sums bounded by

\[
Q_p=\max\left\{\max_n(q_n+\sum_kc_{nk}),\ \max_k\sum_nc_{nk}\right\}<1. \tag{12}
\]

For a Hermitian matrix, bounding every off-diagonal product using \(2|z_i||z_j|\le |z_i|^2+|z_j|^2\) proves \(H\succeq(1-Q_p)I\). For \(X=[\Phi,\Psi]\), the inverse observation map \(H^{-1}X^*W^{1/2}\) has squared Euclidean norm \(\lambda_{\max}(H^{-1})\le(1-Q_p)^{-1}\), because its product with its adjoint is \(H^{-1}\). Thus sensor and correction errors together contribute at most

\[
n^2(\eta+\xi)/\sqrt{1-Q_p}
\]

to coefficient \(n\). Rounding the real part is correct whenever

\[
A_n<\tfrac12,\qquad
n^4(\eta+\xi)^2<(\tfrac12-A_n)^2(1-Q_p),\quad2\le n\le50. \tag{13}
\]

The positive-margin condition is checked before squaring. The constant fitted coefficient includes the baseline constant; it is discarded, and the declared known value \(a(1)=1\) is supplied. Every polynomial of degree at most \(p\) is in the span of \(1,\psi_1,\ldots,\psi_p\), so the baseline is fitted exactly irrespective of amplitude. Eliminating its coefficients from the normal equations is exactly the residualized fit associated with (1).

**Theorem.** Under the stated source, timing, normalization and weighted error model, all 49 unknown retained coefficients are recovered correctly by the exact augmented fit and integer rounding for each listed radius:

| Maximum drift degree | Multiscale \(\eta\) | Outer-only \(\eta\) |
|---|---:|---:|
| 1 | \(9.7\times10^{-5}\) | \(7.7\times10^{-5}\) |
| 2 | \(9.0\times10^{-5}\) | \(7.0\times10^{-5}\) |
| 3 | \(7.7\times10^{-5}\) | \(5.7\times10^{-5}\) |
| 4 | \(5.3\times10^{-5}\) | \(3.3\times10^{-5}\) |
| 5 | \(1.6\times10^{-5}\) | Gate fails |
| 6 | Gate fails | Gate fails |

Proof: the producer reconstructs all new enclosures at 192 and 256 bits with identical exported rational endpoints. The independent standard-library checker substitutes those endpoints into (8)–(13) and proves all 49 strict inequalities for every declared radius. The largest quintic multiscale bias is below \(0.459148827331\), leaving a sufficient sensor threshold above \(1.63342920072\times10^{-5}\). The largest quartic outer bias is below \(0.415660679720\). This proves the declared table.

For comparison, replace each actual \(\ell_k\) by its valid coarser upper bound one in exactly the same complete Schur calculation. The resulting multiscale quintic bias upper bound exceeds \(0.5541\), so that coarse certificate does not support quintic rounding even at zero sensor noise. The actual weighted absolute norms bring it below one half. This is a concrete certified improvement obtained by the complete nuisance-channel refinement.

At degree five the outer sufficient bias bound exceeds \(0.5087\); at degree six the multiscale and outer sufficient bounds exceed \(0.6116\) and \(0.6617\). These are failures of this explicit sufficient bound, not lower bounds on actual recovery error and not impossibility theorems. The explored finite-dimensional Grams remain well conditioned; the sufficient obstruction comes from the conservative tail enclosure after elimination.

## 5. Exact boundaries, covariance, and implementation scope

**Normalization is necessary.** Without known \(a(1)\), the legal sources \(a(1)=0\) and \(a(1)=1\), all other coefficients zero, yield identical observations after compensating constant baselines 1 and 0. No decoder can determine \(a(1)\) under arbitrary constant drift.

**A genuine high-degree boundary.** On any \(m\) distinct timestamps, every complex vector is the sampled value of a polynomial of degree at most \(m-1\), by the explicit Lagrange formula

\[
b(t)=\sum_{j=1}^m z_j\prod_{k\ne j}\frac{t-t_k}{t_j-t_k}.
\]

Each factor product equals the cardinal vector at the nodes. With 8,900 timestamps and degree 8,899, choose two legal sources both having \(a(1)=1\), with \(a(2)=0\) or 1 and every other coefficient zero. Interpolate their response difference \(e^{-it_j\log2}/4\) as the baseline of the first source; the second has zero baseline. Their data are identical. Thus even known normalization cannot support unrestricted growth of the nuisance degree. This is a true obstruction, unlike the low-degree failed sufficient gates.

**Physical covariance is preserved in the model.** Let \(J\) select the arithmetic rows and \(D=\operatorname{diag}(n^2)\). For iid mean-zero complex sensor noise with covariance \(\sigma^2I\), the exact augmented decoder covariance is

\[
\sigma^2 D JH^{-1}X^*W^2XH^{-1}J^*D.
\]

Its first reported row is instead deterministic because normalization supplies it. Deterministic centering does not change this covariance, but adding nuisance columns changes the decoder relative to the old fit. The reused inner/outer weights must be added before squaring; the \(2\alpha(1-\alpha)w_Sw_L\) term cannot be discarded. The theorem uses adversarial weighted noise and requires no statistical distribution.

**Implementation budget.** The arbitrary drift amplitude is a statement about the exact linear map. A finite-precision solve needs an independently bounded error. If its scaled coefficient error is at most \(\rho_n\), a sufficient deployed condition is \(A_n+n^2(\eta+\xi)/\sqrt{1-Q_p}+\rho_n<1/2\). A nonpolynomial baseline residual with \(W\)-norm at most \(\delta\) can be charged by replacing \(\eta+\xi\) with \(\eta+\xi+\delta\). Neither error is removed automatically. The supplied full-grid floating examples corroborate the model but do not certify machine arithmetic for unbounded amplitudes.

## 6. Verification and trust boundary

The polynomial basis, actual cross sums, full nuisance envelope, correction vector and arithmetic Gram are freshly replayed. The unchanged complete arithmetic finite/remote tails are inherited from the explicitly reconstructed prior package. Their identities and mathematical parameter contracts are checked; hashes establish identity rather than proof. The reproduction guide distinguishes these layers.

The new enclosure arithmetic uses Arb through python-flint, with exact rational endpoint consequences. The special-function evaluation is the same full correction already introduced in N2; its numerical algorithm is a trusted component. See [FLINT's official complex zeta documentation](https://flintlib.org/doc/acb_dirichlet.html) and [Johansson's primary algorithm paper](https://arxiv.org/abs/1309.2877). The linear algebra and answer-set equivalence are proved above. The contribution is this complete application and quantitative degree/noise certificate; no historical priority claim is made.
