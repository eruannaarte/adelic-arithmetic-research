# Complete multiplicative blocks for affine-clock uncertainty

This is a refinement of the complete affine-clock theorem in the preceding
[structured transfer package](../../structured_transfer_2026_09/arithmetic/PROOFS.md).
The source, physical weights, exact polynomial nuisance, drift family and
recovery norm are unchanged. This proof uses elementary absolute convergence,
the triangle inequality, a finite Gram estimate, and explicit geometric tails.

## 1. Shared clock and complete nonlinear remainder

There are 8,900 samples at `t_j=(2j+1-8900)/10`, with either of the two
strictly positive, exactly even, mass-one weight vectors W. The source is

`s(t)=sum_(n>=1) a(n)n^-2 exp(-it log n)`,

where `a(1)=1` and every coefficient is an integer in `[0,d_14(n)]`.
No finite-support or number-field realizability assumption is made.
For `|delta_a|<=h/10^14`, `|delta_b|<=h/10^11`, write
`delta_j=delta_a*t_j+delta_b`. The exact exponential remainder gives

`s(t_j+delta_j)-s(t_j) = -i delta_j sum_n b_n exp(-it_j log n) + R_j`,

`b_n=a(n)log(n)/n^2`, `|R_j|<=D2 delta_j^2/2`.

Put `Z=sum n^-2`, `L=sum log(n)n^-2`, `L2=sum log(n)^2/n^2`. Counting
ordered fourteen-tuples proves the complete identity

`D2=sum d_14(n)log(n)^2/n^2 = 14 Z^13 L2 + 182 Z^12 L^2`.

The finite sums through N=1000 plus their decreasing-function integral tails
bound these complete positive series. The producer's elementary bounds are
independently checked by an outward zeta power series as well.

For each fixed source, the linear term is linear in the *same two clock
parameters at every reading*. Convexity therefore reduces its maximum to the
four rectangle corners. At a corner `delta_j=(h/10^11)d_j`, where
`d_j=epsilon_b+epsilon_a*t_j/1000`. Define

`S2=max_corners sum_j W_j d_j^2`,

`S4=max_corners sum_j W_j d_j^4`.

All four physical sums are enclosed independently; exact evenness makes their
values equal. Convexity of the fourth power covers the nonlinear remainder
throughout the clock rectangle, giving `||R||_W<=h^2 D2 sqrt(S4)/(2*10^22)`.

## 2. Finite phase block and a bound valid for every allowed coefficient

Write every positive integer uniquely as `n=2^k m`, with m odd. Set

`u_k=binom(k+13,13)/4^k`, `v=log 2`, `L_m=log m`.

Multiplicativity of the divisor envelope gives

`0<=b_(2^k m)<=[d_14(m)/m^2] u_k (L_m+k v)`.

Take K=32. For each clock corner and lag `ell=1,...,31`, the *actual* sampled
phase correlation is

`gamma_ell >= |sum_j W_j d_j^2 exp(i ell t_j log 2)| / sum_j W_j d_j^2`.

The certificate takes a maximum across all four corners and puts
`Lambda=1+2 sum_(ell=1)^31 gamma_ell`. For arbitrary complex numbers c_k,
expanding the weighted squared norm, bounding each cross term absolutely,
and using `2|c_k c_l|<=|c_k|^2+|c_l|^2` proves

`||d sum_(k=0)^31 c_k exp(-ik t log 2)||_W^2
 <= S2 Lambda sum_(k=0)^31 |c_k|^2`.

This is a Gram operator bound; no equidistribution or independence is
assumed. The common phase `exp(-it log m)` has modulus one and does not
change the norm. Substituting the coefficient envelope only *after* this
bound is valid because the sum of coefficient squares is monotone. Then the
ordinary Euclidean triangle inequality gives

`|| (u_k(L_m+k v))_(k<K) ||_2 <= L_m U + v V`,

`U=sqrt(sum_(k<K) u_k^2)`, `V=sqrt(sum_(k<K) k^2 u_k^2)`.

Actual coefficients may vanish independently. They need not have the
multiplicative ratios of their envelope. The result therefore applies to the
whole declared source class, rather than just its maximal coefficient vector.

## 3. Complete omitted valuations and all odd starting integers

For k>=K,

`u_(k+1)/u_k=(k+14)/(4(k+1)) <= r=(K+14)/(4(K+1))<1`.

Thus, with exact rational quantities,

`T0=sum_(k>=K) u_k <= u_K/(1-r)`,

`T1=sum_(k>=K) k u_k <= u_K[K/(1-r)+r/(1-r)^2]`.

The omitted terms in every odd-m orbit are charged by the weighted triangle
inequality, giving a bound

`sqrt(S2) [d_14(m)/m^2]
 {sqrt(Lambda)(L_m U+v V)+L_m T0+v T1}`.

Absolute convergence permits a triangle inequality over every odd m. Define

`O=sum_(m odd) d_14(m)/m^2 = (3Z/4)^14`,

`O1=sum_(m odd) d_14(m)log(m)/m^2
    =14(3Z/4)^13(3L/4-v Z/4)`.

These identities follow either by restricting the fourteen ordered factors
to odd integers or by differentiating the absolutely convergent generating
series. The producer uses a positive lower bound for Z in the subtractive
term and upper bounds elsewhere, so cancellation does not invalidate its
outward O1 bound. Every odd starting integer is included in O and O1.
Consequently

`B_orbit = sqrt(Lambda)(O1 U+v O V)+O1 T0+v O T1`

is a complete derivative norm bound. The resulting clock radius is

`tau_W(h) = h B_orbit sqrt(S2)/10^11
           + h^2 D2 sqrt(S4)/(2*10^22)`.

All constants used in this formula are saved as exact rational outward upper
bounds. The independent consumer checks the formula with rational arithmetic,
reconstructs all 248 corner/lag sums at 384 bits, checks the complete tails,
and cross-checks O, O1 and D2 by a separate zeta-series route. K=32 is a
computational block length, **not a cutoff in the admissible source class**.

## 4. Transfer to the same nuisance-removed integer query

Affine reparametrization preserves every polynomial of degree at most p, so
the unbounded polynomial nuisance is absorbed by the existing augmented
nominal solve. The W-orthogonal nuisance projection is contractive. Hence the
new complete clock bound remains valid after this exact nuisance operation.
We claim no additional improvement from the projection; the demonstrated
improvement comes from larger multiplicative phase blocks before projection.

The drift family remains a sinusoid with arbitrary phase, amplitude at most
4000 and frequency at most 3. Its effective frequency under the clock is at
most `Omega_eff=3(1+h/10^14)`. For the unchanged certified weighted
approximation K_(W,p), sensor radius eta=4e-5, separate model-mismatch radius
kappa=1e-6, and correction radius Xi=1e-20, define

`delta=eta+kappa+Xi+tau_W(h)+4000 K_(W,p)(Omega_eff)`.

Using the complete arithmetic-tail constants A_n, Gram floor f>0, and an
independently verified normal residual rho yields

`E_n=A_n+n^2(delta/sqrt(f)+rho/f)`.

For each n=2,...,50, put `m_n=1/2-A_n-n^2 rho/f`. The exact strict conditions

`m_n>0`, `n^4 delta^2 < m_n^2 f`

certify unique rounding. The normal residual must be verified from the actual
data and proposed solution; it cannot establish membership in the clock,
noise or drift family. All uncertainties are charged jointly without a
probabilistic independence assumption. Different hypothetical sources may
have different allowable clocks; the same bound applies to each explanation.

The full-budget consequence fixes h=120 and p=12 before certification. The
comparison uses the preceding pair formula at exactly the same h and the
same remaining budgets. If that preceding sufficient gate fails, this means
that particular certificate is inconclusive, not that recovery is impossible.
