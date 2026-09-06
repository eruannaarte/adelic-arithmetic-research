# Path 5 proof appendix: a wider finite-resolution certificate

## 1. Declared model and claim status

All spaces below are real. Fix K=2, g=4/5, odd n=1001 and midpoint nodes x_j=(j+1/2)/n, 0≤j<n. Let L_n be the path Laplacian with diagonal (1,2,…,2,1) and adjacent entries −1, and V_n=diag(1+gx_j). For target mode 1≤ell<n set

\[
\omega_{n,\ell}=4\sin^2(\ell\pi/(2n)),\qquad A_{n,\ell}=L_n+\omega_{n,\ell}V_n.
\]

Write e=n^(-1/2)(1,…,1)^T and (u_k)_j=sqrt(2/n) cos(k pi x_j), k=1,2. Define b_{n,k}(tau,ell)=e^T exp(−tau A_{n,ell})u_k and

\[
G_n(\tau)=\sqrt{1+\tau}\frac2n
 \sum_{\substack{2\le\ell<n\\\ell\text{ even}}}
 b_n(\tau,\ell)b_n(\tau,\ell)^T. \tag{1}
\]

This is the exactly central one-cell target: its positive even modal coefficients have square 2/n, and odd coefficients vanish. The zero mode response vanishes because u_k has zero mean and e is invariant under exp(−tau L_n). No target-placement change is permitted.

The continuum comparison uses phi_k(x)=sqrt2 cos(k pi x), V(x)=1+gx and

\[
F_k(s)=\int_0^1e^{-sV(x)}\phi_k(x)\,dx
=\sqrt2e^{-s}\frac{gs[1-(-1)^ke^{-gs}]}{(gs)^2+(k\pi)^2},
\]
\[
G(\tau)=\sqrt{1+\tau}\int_0^1
F(\tau\omega(\xi))F(\tau\omega(\xi))^T d\xi,
\quad \omega(\xi)=4\sin^2(\pi\xi/2). \tag{2}
\]

The closed form follows by integrating exp(−gsx)cos(k pi x) and evaluating its endpoints. Both Grams carry the same sqrt(1+tau) output normalization and Euclidean modal-energy norm. No physical stochastic noise covariance is inferred from this norm.

The source metrics are I (L2), S=diag(1+pi²,1+4pi²) (declared continuum H1), and S_n=diag(1+4n²sin²(pi/(2n)),1+4n²sin²(pi/n)) (natural discrete H1). Define the three symmetric error matrices

\[
\Delta_{L2}=G_n-G,\quad
\Delta_{H1}=S^{-1/2}(G_n-G)S^{-1/2},\quad
\Delta_{dH1}=S_n^{-1/2}G_nS_n^{-1/2}-S^{-1/2}GS^{-1/2}. \tag{3}
\]

The new claim is a fixed-band, fixed-grid, **computationally certified continuous** extension from tau∈[1,6/5] to tau∈[1,2], using the analytic remainder theorem below. Exact final bounds are in certificate.json; decimal summaries are not proof inputs. This does not assert monotonicity, optimal grid size, unbounded-time transfer, growing-K transfer, or hardware-local sensing.

## 2. New remainder theorem, with complete proof

**Theorem 1 (normalized Gram remainder independent of generator norm).** Let a>0, b≥a, c=(a+b)/2, r=(b−a)/2>0, integer d≥1, and C>0 with C²≥1+b. Suppose an unnormalized Gram entry R_ij(t) is either a nonnegative weighted sum, of total weight at most one, of products

\[
\langle e,e^{-tA}u_i\rangle\langle e,e^{-tA}u_j\rangle,
\]

where A is a real symmetric positive semidefinite matrix and ||e||,||u_i||,||u_j||≤1, or the corresponding integral of multiplication responses with unit L2 source/observation vectors and nonnegative bounded multiplication generators. Let H_ij(t)=sqrt(1+t)R_ij(t). Then, uniformly on [a,b], its degree-(d−1) Taylor polynomial at c satisfies

\[
\left|H_{ij}(t)-\sum_{k=0}^{d-1}\frac{H_{ij}^{(k)}(c)}{k!}(t-c)^k\right|
\le \mathcal R_d(a,b,r,C),
\]
\[
\boxed{\mathcal R_d=C r^d\sum_{j=0}^d
\frac{|\binom{1/2}{j}|}{(1+a)^j a^{d-j}}.} \tag{4}
\]

All terms of (4) are rational for rational a,b,r,C. For a finite-minus-continuum difference add the two remainder bounds. With diagonal metrics multiply each entry remainder by its own inverse square-root metric product before adding.

**Proof.** Orthogonal diagonalization of real symmetric A is justified by the real spectral theorem, Axler, *Linear Algebra Done Right*, fourth edition, Theorem 7.29. Positive semidefiniteness makes every eigenvalue nonnegative. In finite dimensions,

\[
 b_i(t)b_j(t)=\langle e\otimes e,
 e^{-tB}(u_i\otimes u_j)\rangle,
\qquad B=A\otimes I+I\otimes A.
\]

Indeed, the two summands commute because they act on different tensor factors; their exponential is exp(−tA)⊗exp(−tA). This commutation uses different tensor factors and never assumes L_n commutes with V_n. The tensor generator is symmetric PSD, has eigenvalues lambda_p+lambda_q≥0, and tensor vector norms are at most one.

For k≥0 and lambda≥0, the exponential series has nonnegative terms, giving exp(a lambda)≥(a lambda)^k/k! (including k=0). Thus

\[
\lambda^k e^{-t\lambda}\le\lambda^k e^{-a\lambda}\le k!a^{-k}
\quad(t\ge a).
\]

The spectral theorem and Cauchy–Schwarz yield |(b_i b_j)^(k)(t)|≤k!a^(-k). Summing against nonnegative weights of total mass≤1 preserves the bound.

For the continuum multiplication case the product is explicitly a double integral over x,y, with generator value lambda=m(x)+m(y)≥0, and source phi_i(x)phi_j(y) when the observation function is1. For a general unit observation e, the density is e(x)phi_i(x)e(y)phi_j(y), whose L1 norm is at most ||e||2²||phi_i||2||phi_j||2≤1 by Cauchy–Schwarz in each factor. The same scalar inequality proves the derivative bound directly; differentiation under integration is justified because the multiplication generators are bounded and the source product is integrable. Any additional nonnegative outer integral of total mass≤1 preserves it.

For h(t)=sqrt(1+t),

\[
|h^{(j)}(t)|/j!=|\binom{1/2}{j}|(1+t)^{1/2-j}
\le C|\binom{1/2}{j}|/(1+a)^j.
\]

Leibniz and the raw derivative bound imply

\[
|H_{ij}^{(d)}(t)|/d!\le
C\sum_{j=0}^d|\binom{1/2}{j}|(1+a)^{-j}a^{-(d-j)}.
\]

Taylor’s integral remainder has absolute value at most r^d sup|H^(d)|/d!. This proves (4). For metric whitening, the metrics in (3) are constant in tau, so their positive entry factors simply multiply the remainder. ∎

**Verification of hypotheses for (1)–(2).** L_n is symmetric and v^T L_n v=Σ(v_{j+1}−v_j)²≥0. V_n is positive diagonal and omega≥0, so A is symmetric PSD even though L_n and V_n do not commute. The geometric-series identity for cosines on midpoint nodes gives e^T u_k=0, ||e||=||u_k||=1 for 1≤k<n. There are (n−1)/2 retained modes, each with weight 2/n, giving total (n−1)/n<1. In (2), the multiplication generator omega(xi)V is nonnegative bounded by 36/5; phi_1 and phi_2 have L2 norm1, the observation function 1 has norm1, and xi∈[0,1] has total mass1. Therefore both finite and continuum raw Grams satisfy the theorem. The three metrics are SPD because every diagonal is at least1. No uncontrolled projection or noise factor occurs.

**Improvement over the baseline.** The earlier remainder replaced each raw k-th derivative by (2M)^k, with M_f=56/5 and M_c=36/5. That is valid but expensive when widening a cell. Formula (4) uses semigroup decay before discarding the spectrum. For [1,3/2], r=1/4, d=19, C=2, the sum of the two raw entry remainders is <1.88141×10^-11. Consequently two degree-18 Taylor cells can be tried on [1,2], rather than increasing the polynomial order roughly to45 for a single cell under the old bound. This is a new application/corollary of elementary spectral estimates, not a claimed new spectral theorem.

## 3. Rigorous construction of coefficient intervals

The generator retains the audited finite_gram_series and continuum_gram_series algorithms, recording their source hashes. The following facts connect those algorithms to the declared model.

For each ell, 0≤L_n≤4I (use Σ(v_{j+1}−v_j)²≤4Σv_j²), I≤V_n≤(9/5)I, and omega∈[0,4]. Set

\[
c_\ell=2+(7/5)\omega,\quad B_\ell=A-c_\ell I,
\quad \rho_\ell=2+(2/5)\omega.
\]

Then ||B_ell||≤rho_ell and c_ell−rho_ell=omega. For exponential degree D, the scalar Taylor series and sum bound Σ_{j>D}z^j/j!≤exp(z)z^(D+1)/(D+1)! give

\[
\left\|e^{-cA}-e^{-cc_\ell}\sum_{j=0}^{D}(-cB_\ell)^j/j!\right\|
\le e^{-c\omega}(c\rho_\ell)^{D+1}/(D+1)!.
\]

Here c is the positive time-cell centre, not c_ell. Differentiating exp(−tau A) at c applies (−A)^k/k!. The base exponential remainder is therefore multiplied by ||A||^k/k!, with ||A||≤56/5. Source and observation norms are one, so this is also the amplitude coefficient remainder. Arb tridiagonal actions and outward tail additions produce enclosures of all finite coefficient entries; sums/products implement (1).

For (2), elementary coefficient recurrences for products, reciprocals and exponentials applied to the displayed closed form F_k compute its Taylor coefficients. Denominator zeros on a complex integration enclosure produce nonfinite enclosures and trigger quadrature subdivision; on the real xi path, (gs)²+(k pi)²>0. The xi dependence uses only meromorphic field operations, sine and exponential, so the Arb integration callback’s holomorphicity contract is satisfied wherever it returns a finite complex enclosure. Its argument-dependent operations contain no branch-cut function: the square roots of2 and sqrt(1+c+delta) are constant with respect to xi. The imaginary component of the integral is zero by the real integrand, and its enclosure is checked to contain zero.

Arb’s acb_calc_integrate returns a rigorous enclosure even if a requested tolerance is not achieved; nonfinite coefficients are rejected here. Requested tolerances and quadrature limits are inherited from the source algorithm, and working precision is recorded. Use the returned ball widths, never the requested tolerance, as numerical evidence. The main integration primary source is Johansson (2018), *Numerical integration in arbitrary-precision ball arithmetic*, especially its algorithm and implementation; the official FLINT acb_calc_integrate documentation spells out the finite-path and holomorphic-callback hypotheses checked above.

The normalization sqrt(1+tau) is applied by its elementary Taylor recurrence before subtracting finite and continuum coefficients. Whitening is applied to each coefficient in Arb; its result is exported as exact dyadic endpoints. Subtraction before interval polynomial evaluation preserves the finite/continuum cancellation. Exponential approximation radii remain inside coefficient intervals, while the time Taylor remainder (4) is added only after evaluation; neither replaces the other.

## 4. Continuum floor premise freshly revalidated

The old exact positive floor rationals ell_L2 and ell_H1 are embedded in the existing Stage X trace. We revalidate their matrix premise at256 bits, not merely their provenance hash. Let b0=7/4 and

\[
H_{b0}=\frac1{2\pi}\int_0^{b0}s^{-1/2}F(s)F(s)^Tds,
\quad c_R=\sqrt2e^{-b0}<1.
\]

The substitution s=b0 r² removes the endpoint singularity and gives H_b0=sqrt(b0)/pi ∫_0^1F(b0 r²)F(b0 r²)^Tdr, an analytic finite integral. baseline.json stores fresh outward Arb enclosures of c_R H_b0. Both c_R H_b0−ell_L2 I and c_R H_b0−ell_H1 S pass an independent rational2×2 principal-minor test using outward endpoints.

To connect that matrix to every tau≥1, substitute s=tau omega(xi) in (2). Its density relative to (1/(2pi))s^(-1/2)ds on0<s<4tau is

\[
w_L(\tau,s)=\frac{2\sqrt{1+\tau}}{\sqrt{4\tau-s}}\ge1.
\]

Since b0≤4≤4tau, restriction to[0,b0] proves G(tau)≥H_b0≥c_R H_b0. Every inequality is a Loewner inequality because the integrand outer product is PSD. Hence G≥ell_L2 I and G≥ell_H1 S uniformly on the late lattice half-line. This reconstructs the needed baseline theorem directly and does not rely on the irrelevant resolved-chart or full-atlas claims. Strict positivity c_R<1 follows, for example, from exp(7/4)>1+7/4>sqrt2.

## 5. Small exact checker and finite transfer theorem

Each cell stores the order-18 difference-coefficient intervals, inverse metric-product intervals, rational time endpoints, and exact remainder radii. The checker uses Fraction interval arithmetic for every Horner operation. It independently recomputes formula(4) and adds the finite and continuum metric remainder charges. The resulting box encloses every symmetric error matrix throughout that cell.

For an error box E=[[a,b],[b,d]], an exact rational U>0 is accepted only if **both** UI+E and UI−E are positive definite for every permitted entry. It checks positive lower diagonal endpoints and

\[
\underline{(U\pm a)}\ \underline{(U\pm d)}>
\max(|\underline b|,|\overline b|)^2.
\]

These conditions give positive leading minors for every matrix in the box. Completing the square proves2×2 positive definiteness; no floating eigenvalue is trusted. Therefore −UI<E<UI and ||E||2<U by orthogonal diagonalization. The chosen U is rounded conservatively and then accepted by this exact test.

For any unit vector v, v^T Gwhite_n v≥v^T Gwhite v−U≥ell−U. Thus the finite generalized information floor is at least ell−U>0 under its declared metric. This direct Rayleigh argument supplies the perturbation step without invoking an unverified general Weyl theorem.

The checker then requires adjacent cells to meet exactly, without a gap or overlap, and their endpoints to equal the claimed interval. The maximum of their spectral uppers and the minimum resulting floor yield the uniform conclusion. Comparing natural discrete H1 uses S_n for the finite Gram and S for the continuum Gram, as explicitly defined in(3).

**Trust boundary.** The small checker proves exact consequences of supplied coefficient and metric enclosures. It does not itself recompute Arb tridiagonal actions or validated integration, and a new forged coefficient premise cannot be authenticated by an artifact hash. Regeneration from model definitions is the separate numerical proof step. The full trust chain is: explicit model/formula proofs, Arb numerical enclosure implementation and audited coefficient algorithm, exact exported endpoints, independent rational arithmetic. Tests that mutate derived fields are useful implementation controls but do not prove the analytic theorem. A separate small-grid direct Arb matrix-exponential comparison and refinement run test the coefficient implementation.

## 6. Boundary and counterexample review

1. **Positivity and self-adjointness are necessary for this proof.** A scalar negative generator A=−1 gives exponential growth, contradicting a norm-independent t^(-k) estimate. A stable nonnormal generator can have arbitrarily large transient amplification: A=[[1,−M],[0,1]] has positive eigenvalues but exp(−tA)=exp(−t)[[1,Mt],[0,1]]. Eigenvalues alone therefore cannot replace symmetric PSD hypotheses.
2. **Normalize source and output vectors.** Multiplying a source by alpha multiplies a diagonal Gram derivative by alpha². Formula(4) without that factor is then unjustified. In this model exact DCT/L2 norms and total weights were checked above.
3. **No a=0 extension.** The proof divides by a; it asserts only a>0. Initial-layer and growing-band cancellations require a different analysis.
4. **Fixed n cannot cover tau→infinity.** Every retained ell is positive and A≥omega I>0, so(1) decays exponentially despite sqrt(1+tau). The normalized continuum Gram has a positive floor by Section4. Thus no finite grid satisfies any positive inherited-floor transfer for all late times.
5. **Two ports do not establish growing-K stability.** The three metrics and all coefficient boxes are exactly2×2. Continuum smallest eigenvalues deteriorate with K; no exchange of K,n,tau limits occurs.
6. **A failed bound is not singularity.** For G=I and G_n=(1/10)I, an overly conservative error upper2 fails the unit-floor test although G_n is SPD. Failure is an inconclusive sufficient inequality, not an impossibility claim.
7. **Natural and continuum H1 differ.** Even G_n=G does not make the last error in(3) zero. The metrics must be whitened separately.
8. **Point checks do not cover an interval.** A polynomial vanishing at tested times can be positive between them. The cell theorem uses remainder bounds on the entire time interval and exact cover topology.
9. **Central target only.** Shifting the target changes parity weights and may introduce odd modes. No current certificate is reused for that model.

## 7. Primary sources and originality boundary

- Sheldon Axler, *Linear Algebra Done Right*, fourth edition, Theorem7.29 (real spectral theorem), https://linear.axler.net/LADR4e.pdf . Its hypotheses are met by the symmetric finite A and tensor B; the continuum derivative bound is proved directly by multiplication and scalar integration, so no unbounded spectral theorem is required.
- Fredrik Johansson, *Arb: Efficient Arbitrary-Precision Midpoint-Radius Interval Arithmetic*, IEEE Transactions on Computers66(8),1281–1292(2017), https://arxiv.org/abs/1611.02831 . Describes the numerical interval representation and arithmetic trusted by the generator.
- Fredrik Johansson, *Numerical integration in arbitrary-precision ball arithmetic*, ICMS2018,255–263, https://arxiv.org/abs/1802.07942 ; official numerical contract at https://flintlib.org/doc/acb_calc.html#acb-calc-integrate . Hypotheses and callback behavior are checked in Section3.

The tensor-product identity, spectral decay estimates, Taylor remainder, and positive-definiteness criteria are classical. The contribution claimed here is the explicit norm-independent normalized-Gram remainder applied to this finite-transfer problem, the resulting wider continuous certificate, and an independent rational consequence checker. No literature-priority claim is made for the general technique. The available primary literature establishes it as validated numerical analysis rather than empirical discovery.
