# Complete proofs for three adaptive arithmetic-noise cycles

## Shared acquisition and inherited premises

The source is an absolutely convergent Dirichlet series F(2+it)=sum a(k) k^(-2-it), with integer coefficients0<=a(k)<=d14(k). The retained vector consists of indices1,...,50. Acquire the same8900 complex readings at t_j=(2j+1-8900)/10. The outer midpoint cosine window has T=1780,m=8900. The inner window T=510,m=2550 occupies outer indices3175,...,5724. Its samples are reused, not acquired a second time. All window coefficients are the original binary64 values interpreted as exact rationals.

For alpha in[0,1], let W_alpha be the diagonal probability weights alpha wS+(1-alpha)wL, with wS extended by zero outside the inner grid. The cosine density is positive and each component has mass exactly one by discrete Fourier orthogonality. Write Phi_jn=exp(-it_j log n), D=diag(n²), G_alpha=Phi*W_alpha Phi. The original decoder is D G_alpha^-1 Phi*W_alpha y whenever the Gram is invertible. For iid mean-zero complex observation errors with covariance sigma²I, its coefficient covariance is exactly sigma² D G_alpha^-1 Phi*W_alpha² Phi G_alpha^-1 D. Gaussianity is unnecessary for a variance statement.

The complete finite tails to10^6 and MPFR remote bounds above10^6 were reconstructed in the previous five-path package. This chain explicitly inherits those mathematical premises, revalidates their formal projections and binding, and freshly reconstructs every new finite response, weight, and Gram bound it uses. The dependency hashes establish identity, not proof by themselves. The previous full reconstruction commands and records remain in `research/five_paths_2026_09/path3_noise/`; the shared bound framework is its PROOF.md. No unchanged expensive baseline is silently relabelled as a new research cycle.

## N1 — a complete-family certificate/variance Pareto obstruction

### The precise certification functional

Let R_S(k/n),R_L(k/n) denote the real, centered response of the two windows. The response is real because midpoint times and weights are symmetric. Put R_alpha=alpha R_S+(1-alpha)R_L. For each target n define the original complete normalized absolute-tail certificate

    T_n(alpha)=sum_(51<=k<=10^6) d14(k)/k² |R_alpha(k/n)|
               +alpha U_S,n +(1-alpha)U_L,n,                  (N1.1)

where U_S,n,U_L,n are the verified remote upper endpoints. The first sum is the exact finite functional, evaluated outward by producers. The last term is the full prescribed positive remote bound, not a claim that the actual remote tail attains that value. With exact Gram row bounds q_n(alpha) and q=max q_n<1, the original Neumann sufficient bias functional is

    B_n(alpha)=n²[T_n(alpha)+q_n(alpha) max_h T_h(alpha)/(1-q)]. (N1.2)

A certificate with all B_n<1/2 suffices for noiseless integer rounding. Failure is not actual recovery impossibility. The theorem below concerns this explicit certificate/design family and the decoder's actual iid variance, not an unknown sharp minimax bias.

### Theorem N1

If any alpha in[0,1] permits the original complete certificate (N1.1)–(N1.2) to have B_n(alpha)<1/2 for all targets, then

    0.0017613 < alpha < 0.0020428.                             (N1.3)

For every alpha in the entire closed interval between these rational endpoints, the actual iid variance of decoded coefficient50 is strictly greater than the outer-window variance. The certified uniform ratio is greater than1.00009090067766. The reference alpha0=125/65536 lies in this interval and its inherited complete bias upper bound is0.4980274167750795, so the rounding-capable part is nonempty.

Consequently varying the positive mixture alone cannot retain the original complete rounding certificate while avoiding all of the target50 iid variance penalty. This is the claimed method-specific Pareto obstruction.

### Complete proof of the necessary interval

Since all terms of (N1.2) are nonnegative, B50>=2500T50. Retain only the fourteen omitted indices

    51,52,54,55,56,72,80,90,96,128,144,160,216,240

in the finite sum of (N1.1), keeping its entire remote term. Dropping the other nonnegative finite terms gives a lower bound on the complete **certificate functional**. For any fixed signs s_k in{-1,1}, |z|>=s_k z yields a globally valid affine minorant

    T50(alpha)>=L_s(alpha)
      =alpha U_S,50+(1-alpha)U_L,50
       +sum_selected s_k d14(k)/k² [R_L+alpha(R_S-R_L)].        (N1.4)

The exact rational arithmetic weights use d14(p^e)=binomial(e+13,13), multiplied across prime factors. At alpha=17613/10^7, the checker chooses the signs of the fourteen actual mixed responses and reconstructs each response with outward Arb arithmetic. It proves2500L_s(alpha)>1/2 and the affine slope is strictly negative. Therefore the same inequality holds for every smaller alpha. At alpha=5107/2500000, a second fixed-sign affine minorant has endpoint value>1/2 and strictly positive slope, excluding every larger alpha. These two half-line arguments establish (N1.3) over the whole family[0,1], rather than testing a finite list of alpha values. The remote term has not been truncated or omitted. QED for the interval.

### Complete proof of the actual variance penalty

Let A=||wS||², B=||wL||², C=<wS,wL>, where wS is the actual zero-extended reused vector. Then

    S2(alpha)=||w_alpha||²
             =B+2alpha(C-B)+alpha²(A+B-2C).                  (N1.5)

The cross term is mandatory because one physical error receives the sum of its two weights. Exact Fourier orthogonality gives A=K/2550 and B=K/8900, where K=1+2sum c_h². Direct outward summation certifies C>B and A+B-2C>0. Hence S2 is strictly increasing on[0,1], and its minimum on (N1.3) is bounded below by its value at the left endpoint.

Gram affinity gives G_alpha=G_alpha0+(alpha-alpha0)(G_S-G_L). All component diagonals equal one exactly. The absolute row sums therefore obey

    q_n(alpha)<=q_n(alpha0)+d(q_n(S)+q_n(L)),                 (N1.6)

where d is the larger endpoint distance from alpha0. Each component/reference Gram row is freshly reconstructed outward. Set Q_n to (N1.6) and Q=max Q_n<1. By the rowwise Neumann argument, the l1 norm of row n of G_alpha^-1-I is <=delta_n=Q_n/(1-Q). Each uncorrected Fourier-weight row has l2 norm sqrt(S2). Triangle and reverse-triangle inequalities thus give

    n^4 S2(alpha)(1-delta_n)^2
      <= Var(a_hat_n)/sigma²
      <= n^4 S2(alpha)(1+delta_n)^2,                          (N1.7)

with the lower bound used only when delta_n<1. This is a bound on the actual covariance of the full decoder, not a replacement noise model. The uniform multiscale lower in (N1.7), divided by the separately certified outer-window upper, exceeds1.00009090067766 by exact rational arithmetic. This proves the variance statement for every allowed alpha simultaneously. QED.

### Scope and verification

The restriction is on the original complete absolute-tail certificate. A better bias argument or a different decoder may escape it; it is not a universal impossibility result for every use of these observations. The variance increase is proved for coefficient50 and the stated iid physical noise covariance; it does not claim that every coefficient or every correlation law worsens. cycle1.py reconstructs the two affine minorants, all new Gram bounds, the complete reused-weight statistic, final exact inequality, and binding to the previously verified full-tail premises. Independent raw-grid and covariance controls accompany it.

## N2 — complete envelope centering changes the robustness regime

### Theorem N2 and worked acquisition

At exactly the original8900 readings define the known complex correction

    u(t)=[zeta(2+it)^14-sum_(n<=50) d14(n)n^(-2-it)]/2.       (N2.1)

Subtract a rational vector u_tilde whose error at each reading has modulus strictly less than xi=10^-20. The file cycle2_correction.json supplies this entire vector, storing4450 positive-time entries and defining the negative-time entries by conjugate symmetry. Apply the unchanged original weighted Gram decoder to y-u_tilde and round each real coefficient to the nearest integer. All50 coefficients round correctly for either of these acquisitions:

* Reference multiscale weights and weighted sensor-error radius eta<=10^-4.
* Outer-only weights and weighted sensor-error radius eta<=8*10^-5.

The weighted norm uses the respective positive probability weights. In particular, the common coordinatewise error bound |epsilon_j|<=8*10^-5 suffices for both designs without changing the physical sensor-error set. The reference sufficient sensor radius has threshold greater than0.000100356572843797; the outer threshold exceeds0.000080772574233712. The reference threshold is over127.237364914 times its original uncentered threshold7.88735077244e-7. The complete bias bounds change from0.4980274167750795 to0.2490137083875398 for the reference and from0.5959293953409309 to0.2979646976704655 for the outer design. These are sufficient bounds, not sharp minimax thresholds.

### Proof of the full correction identity and half-tail bound

For Re(s)=2, the series sum n^-s converges absolutely. Its14-fold product therefore equals the sum over all positive ordered14-tuples of their product raised to -s. Grouping by product is justified by absolute convergence. The count for a prime power p^e is the number of distributions of e indistinguishable exponents among14 factors, binomial(e+13,13). Unique prime factorization multiplies these counts across primes. Thus zeta(s)^14=sum d14(k)k^-s, with sum d14(k)/k²=zeta(2)^14 finite. Equation(N2.1) is exactly the midpoint of the complete omitted source-coefficient envelope, including every k>10^6.

For every admissible source, a(k)-d14(k)/2 belongs to[-d14(k)/2,d14(k)/2]. After subtracting u, the normalized omitted response at every retained target consequently has modulus at most T_n/2, where T_n is the same complete finite-plus-remote upper bound used previously. The finite sum and entire remote envelope are both halved. The rowwise Neumann argument is linear in these nonnegative bounds, so its final coefficient bias is B_n/2. Nothing is inferred about attaining the remote bound. Because the source class contains every independent integer interval endpoint, the centering is also consistent with the integer model; the correction itself need not have integer coefficients.

### Proof of the digital and sensor-error allowance

Let A=W^(1/2)Phi. Its Gram is G=A*A. Since the weights have mass one, the pointwise correction bound implies ||W^(1/2)(u-u_tilde)||2<xi. The same norm of the sensor error is at most eta. Gershgorin's elementary quadratic-form bound gives lambda_min(G)>=1-q: expanding x*(G-I)x and bounding each off-diagonal product by(|x_i|²+|x_j|²)/2 proves the claimed inequality because G is Hermitian and its row sums are bounded by q. The inverse observation map is G^-1 A*, whose Euclidean operator norm is at most1/sqrt(1-q). One way to see this without assuming a singular-value theorem is to write its norm squared as the largest eigenvalue of G^-1 A*A G^-1=G^-1. Therefore the error at coefficient n is bounded by

    |a_hat_n-a_n| <= B_n/2+n²(eta+xi)/sqrt(1-q).             (N2.2)

Nearest-integer rounding is unique when this is strictly below1/2. The checker establishes positive margins and the equivalent exact rational inequalities

    (eta+xi)² n^4 < (1/2-B_n/2)²(1-q),   n=1,...,50.        (N2.3)

For the declared eta values, the smallest remaining rounding margins exceed0.000891769150922454 and0.001932429049846045 respectively. This proof covers adversarial physical errors, with no distribution or independence assumption.

### Proof of the correction certificate and covariance statement

The producer encloses zeta(2+it)^14 and the entire retained polynomial in Arb complex balls at192 bits. The50 head coefficients are exact rationals obtained from the prime-power formula just proved. Each real and imaginary center is rounded to the nearest multiple of10^-20. The producer then re-subtracts those exact rationals from the original enclosure and verifies the squared complex error is strictly below10^-40 at all4450 positive times. Real source coefficients imply u(-t)=conjugate(u(t)), covering all8900 physical readings. This includes errors from zeta evaluation, finite arithmetic, and final rounding. Rebuilding at256 bits reproduces every rational entry and all published bounds. Independent75-decimal mpmath evaluations check three widely separated times; these controls corroborate, but do not replace, the outward proof.

For any deterministic correction c, L(y-c)=L(y_signal-c)+L epsilon with L=D G^-1 Phi*W. Its error covariance is therefore exactly L Cov(epsilon)L*. The centering changes its deterministic bias but leaves the full physical-noise response unchanged, including the shared-reading cross term. This completes the theorem.

### Scope and trusted numerical components

The known d14 upper envelope and exact sampling times are required. The correction costs offline evaluation and storage, not extra source observations. The complete tail premises remain the previously reconstructed certificates; a finite-only correction would not justify this theorem. Arb's complex zeta enclosure is a new trusted numerical component. Its documented automatic implementation supplies rigorous ball enclosures; the relevant mathematical evaluation methods are analyzed by Johansson in *Rigorous high-precision computation of the Hurwitz zeta function and its derivatives*, arXiv:1309.2877. Re(s)=2 avoids the pole. The proof of the Dirichlet-series identity and its use here is given above rather than imported from that algorithm paper. The theorem concerns the exact linear decoder with the supplied rational preprocessing. A deployed finite-precision linear solve needs its own separately charged rounding allowance. No property of multiplicative sources beyond the stated envelope, and no hardware-noise validation, is claimed.

## N3 — arbitrary affine instrument drift and its exact identifiability boundary

### Theorem N3

In addition to the shared envelope, assume a(1)=1 is known. Suppose the same8900 observations are

    y_j=F(2+it_j)+beta0+beta1*t_j+epsilon_j,                  (N3.1)

where beta0 and beta1 are arbitrary complex constants, with no magnitude restriction. Subtract the rational midpoint vector from N2. Jointly fit the50 arithmetic columns and the normalized linear-time column defined below. Discard the fitted first arithmetic coefficient, supply the known value a(1)=1, and scale/round the other49 coefficients. All50 reported values are correct for weighted sensor radius eta<=9*10^-5 with the reference multiscale weights, or eta<=7*10^-5 with the outer-only weights. The correction error xi=10^-20 remains charged separately.

Without the normalization, a(1) cannot be recovered under arbitrary constant baseline even from noiseless, unlimited observations. The two legal envelope sources a(1)=0 and a(1)=1, all other coefficients zero, give identical observations when beta0 is respectively1 and0. Both obey0<=a(1)<=d14(1)=1. Hence the known-normalization hypothesis is necessary for the stated whole-prefix problem, rather than a numerical convenience.

### Complete block-inverse and tail proof

Fix either weight vector and write

    s_t²=sum_j w_j t_j²,  psi_j=t_j/s_t,
    g=Phi*W psi,   H=[[G,g],[g*,1]].                         (N3.2)

The weights are symmetric about t=0; their mass is one. Consequently s_t²>0, psi has weighted norm one, and g1=0 exactly. Every other g_n is purely imaginary, with

    Im(g_n)=2/s_t sum_(t_j>0) w_j t_j sin(t_j log n).         (N3.3)

The producer encloses these actual physical sums outward, not a surrogate matrix. Let c_n be their absolute rational upper endpoints, q_n the original Gram row bounds and q=max q_n<1. The Neumann row bound gives

    |(G^-1 g)_n|<=v_n:=c_n+q_n max_h(c_h)/(1-q).             (N3.4)

Set gamma0=1-sum c_n v_n. The Schur complement gamma=1-g*G^-1g is real and at least gamma0>0. Positivity follows because G is Hermitian positive definite and the computed lower bound is positive. In particular H is invertible. This also follows directly by completing the square in x*Gx+2Re(z*x*g)+|z|², whose residual z term is gamma|z|².

The exact retained coefficients in this augmented representation are theta1=1+beta0, theta_n=a(n)/n² for2<=n<=50, and theta51=beta1*s_t. Thus the arbitrary drift is fitted exactly, independently of its amplitude. Let h be the source residual after the exact midpoint subtraction, excluding sensor/digital errors. The original arithmetic fit z=G^-1 Phi*Wh obeys |z_n|<=B_n/(2n²) by N2. Absolute convergence gives the complete pointwise envelope

    |h_j|<=H0=[zeta(2)^14-sum_(n<=50)d14(n)/n²]/2.           (N3.5)

This includes all omitted indices, not merely the earlier finite cutoff. Since psi has unit weighted norm and the weights have mass one, Cauchy–Schwarz yields |psi*Wh|<=H0. Solving the two block equations defining H^-1 gives the augmented arithmetic error

    z - G^-1g [psi*Wh-g*z]/gamma.                            (N3.6)

Therefore the new complete coefficient bias is bounded by

    Baug_n = B_n/2 + n² v_n/gamma0
                         [H0+sum_h c_h B_h/(2h²)].          (N3.7)

Every quantity on the right is explicitly enclosed or rational. This uses the entire unwindowed nuisance-tail channel, as required: the old arithmetic-channel tail bounds alone would not control a newly added time column.

### Complete error and numerical-certificate proof

The augmented Gram has diagonal one. Its off-diagonal absolute row sums are bounded by q_n+c_n for the first50 rows and sum c_n for the nuisance row. Put Qaug equal to the largest of these bounds. The same elementary Hermitian argument from N2 gives lambda_min(H)>=1-Qaug>0 and an augmented inverse observation norm at most1/sqrt(1-Qaug). Digital correction plus sensor error therefore contributes at most n²(eta+xi)/sqrt(1-Qaug) to coefficient n. For n=2,...,50 the checker verifies positive margins and the exact rational inequalities

    (eta+xi)² n^4 < (1/2-Baug_n)²(1-Qaug).                  (N3.8)

Coefficient1 is supplied by the known normalization and is deliberately excluded from this rounding test. Equations(N3.2)–(N3.8) prove the theorem.

The full pointwise centered-tail enclosure is about469.8120143576. Despite this conservative bound, the actual nuisance cross sums are small: sum c_n<4.997e-7 for both designs and gamma0>0.99999999999999. The certified new maximum biases are below0.258210856292 for the reference and0.307180300807 for the outer design. Their declared error radii leave rounding margins greater than0.0167040734347 and0.0177296850295. Full192/256-bit reconstructions agree, including every cross sum and rational endpoint.

### Worked example, controls, and scope

The worked finite source has a1=1,a2=7,a49=a50=1 and all other coefficients zero. Every coefficient respects the envelope. Add the baseline(100+37i)+(10000+2000i)t and a physical error eta*exp(-it log50), whose weighted norm is exactly eta. The independent direct8900-row augmented solve rounds every unknown retained coefficient correctly for both certified designs. The same arithmetic-only decoder fails for this baseline, while the augmented fitted first coefficient is visibly not the source's a1. This corroborates the exact theorem and catches treating the nuisance constant as a recovered arithmetic value.

The proof tolerates unbounded drift in an exact linear solve; finite-precision implementation error generally grows with baseline magnitude and must be separately bounded. The numerical worked example is not a claim of machine-precision robustness for arbitrarily large drift. A non-affine model residual can be included in the stated sensor-error budget but is not removed automatically. N2's unchanged covariance statement applies to its deterministic preprocessing; adding the nuisance column in N3 changes the decoder and its covariance. This theorem certifies the new bounded-error guarantee and does not assert unchanged or optimal iid variance for the augmented fit. Schur elimination, centering, and nuisance projection are standard methods; this complete arithmetic-tail application is the supported contribution, without a historical novelty claim.
