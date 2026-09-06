# Quadratic realizability and a constrained arithmetic query

Evidence status: the realizability and separation statements below are analytic consequences of stated standard theorems; the explicit sensing radius also uses outward finite computations. They are new developments of this project's envelope analysis. No priority claim for the general quadratic-field facts or constrained least-squares principle is made.

## P4.1 — Exact finite-prefix realizability

Let N≥2. A vector of integers (a(1),…,a(N)) is the Dedekind-zeta coefficient prefix of a real quadratic field if and only if all the following conditions hold:

1. a(1)=1, and a(mn)=a(m)a(n) whenever gcd(m,n)=1 and mn≤N.
2. At each prime p≤N, a(p) belongs to {0,1,2}.
3. Writing x_p=a(p)−1, one has a(p^k)=Σ_{j=0}^k x_p^j for each p^k≤N.

Every prefix satisfying these conditions occurs for infinitely many distinct real quadratic fields. There is no discriminant ceiling in this statement. Thus exactly 3^π(N) prefixes occur, while no one such prefix identifies the field. For N=1 the sole prefix (1) also occurs infinitely often.

**Proof of necessity.** Write K=Q(√d), with d>1 squarefree, and D=d if d≡1 mod4 and D=4d otherwise. A rational prime splits, ramifies, or stays inert according to χ_D(p)=1,0,−1. Unique ideal factorization gives local generating functions (1−z)⁻², (1−z)⁻¹, or (1−z²)⁻¹, respectively. Their degree-k coefficients are k+1, 1, or 1 for even k and 0 for odd k. These are exactly Σ_{j=0}^k χ_D(p)^j. Coprime multiplicativity gives all remaining coefficients and 0≤a(n)≤d₂(n), where d₂ is the ordinary divisor function. In particular a(n)=Σ_{e|n}χ_D(e).

The arithmetic inputs are unique ideal factorization, [Milne, Algebraic Number Theory, v3.08, Theorem 3.7, p.49](https://www.jmilne.org/math/CourseNotes/ANTc.pdf), and the explicit quadratic splitting rule in Theorem 3.41 and Example 3.44, pp.62–64 of the same source. Their hypotheses hold: the ring of integers is a Dedekind domain, Q(√d)/Q is separable, d is squarefree, and the full ring of integers uses 1,√d or 1,(1+√d)/2 as appropriate. The special prime2 is handled by D mod8, rather than by applying the odd-prime rule to it.

**Proof of sufficiency.** More generally fix any finite set P of primes and any prescribed x_p∈{−1,0,1}. Put R=∏_{p∈P:x_p=0}p. Seek a prime q>max P and d=Rq. At an odd p∈P with x_p=0 impose q≡1 modp. At an odd p with x_p≠0, R is a unit modp; impose (q/p)=x_p(R/p), choosing any nonzero residue with this Legendre symbol. Such residues of either sign exist: squaring the p−1 nonzero elements has fibers of size2, so exactly half are squares.

If 2∈P and x₂=0, R is even; impose q≡1 mod8. Then d is even and2 ramifies. Otherwise R is odd. Impose q≡R⁻¹ mod8 for x₂=1 (also choose this when2∉P), or q≡5R⁻¹ mod8 for x₂=−1. Then d≡1 or5 mod8, respectively, and the desired splitting at2 follows.

All moduli8 and odd p are pairwise coprime; every chosen residue is a unit. The Chinese remainder theorem therefore gives q≡A modM, where M=8∏_{p∈P,p odd}p and gcd(A,M)=1. These are exactly the hypotheses of [Dirichlet's theorem on primes in arithmetic progressions, original paper in translation](https://arxiv.org/abs/0808.1408). It supplies infinitely many primes q in this class, and excluding finitely many q≤max P leaves infinitely many. Consequently d=Rq is positive, squarefree, and greater than1. For odd unramified p, (d/p)=(R/p)(q/p)=x_p; ramified primes and2 were already checked. Distinct q give distinct squarefree d and hence distinct quadratic fields. The CRT used here is also [Milne, Theorem1.14](https://www.jmilne.org/math/CourseNotes/ANTc.pdf); its pairwise coprimality hypothesis was explicitly verified.

Apply this construction to all p≤N and use the local identities to get exactly the requested prefix. Conversely every prefix determines all its x_p, proving the count. The proof uses an accepted infinitude theorem; enumerating field examples alone would not prove infinitude.

**Finite examples.** `quadratic.py` constructs all27 patterns at2,3,5 by exact CRT, trial-division primality, squarefreeness, and local-symbol checks. One set with a(2)=0,a(3)=1 is D=453,3165,381; their a(5) values are0,1,2. Their a(4)=a(9)=1, so each has a(20)=a(45)=a(5). The maximum D among the27 stored witnesses is28920. These illustrate, but do not replace, the proof.

## P4.2 — What convex relaxation can change

For a label q let S_q be its response set in a finite-dimensional Hilbert observation space. Assume finitely many labels and compact nonempty sets. Put δ=min_{q≠r}dist(S_q,S_r). An adversarial observation error of norm at most η permits uniform label recovery if 2η<δ. If 2η≥δ, two closest responses have a common midpoint observation with errors of norm at mostη, so recovery fails. This proves the exact threshold, including failure at equality when the minimum is attained. For noncompact sets the strict statements still follow from the infimum, but equality need not be decided this way.

Convexification replaces S_q by its compact convex hull C_q. Since S_q⊆C_q, δ_conv≤δ. A useful equality certificate is the following: for every pair of labels find a unit linear functional ℓ and orientation with inf_{S_r}ℓ−sup_{S_q}ℓ≥δ. Linear extrema are unchanged by convex hull, and Cauchy–Schwarz then gives dist(C_q,C_r)≥δ for every pair. Hence δ_conv=δ. In particular, equality holds if all S_q are already convex. This is a sufficient certificate, not a claim that every integral uncertainty set meets it.

A strict gap is possible even for one measurement: let q∈{0,1}, u∈{0,2}, and y=q+u. The integral response sets {0,2} and {1,3} have distance1 and threshold1/2; relaxing u to[0,2] produces overlapping intervals and threshold0. This elementary example is not advertised as a number-field witness. In actual quadratic data, multiplicativity imposes a different obstruction to an envelope witness: a prefix pair differing only at5 cannot occur for N≥20. Its equal a(4) is1 or3, while Δa(20)=a(4)Δa(5)≠0. An envelope impossibility based on an isolated unit change at5 therefore does not transfer to these fields.

## P4.3 — Observation model, complete tail, and explicit query

Use the same8900 physical readings as Path3: t_j=(2j+1−8900)/10, j=0,…,8899, of y_j=ζ_K(2+it_j)+ε_j. Let Φ_{jn}=exp(−it_j logn), n≤50, D₀=diag(n²), and W=diag(w_j), with the positive midpoint cosine weights from Path3. The inner2550 readings occupy indices3175:5725 and have mixture weight125/65536; the outer8900 component has weight65411/65536. Nested observations are reused, not acquired independently. Exact binary64 window coefficients are interpreted as rational numbers. Positivity and total weight1 are certified; consequently ||Φ_{·n}||_W=1 and every response R(ω)=Σ_jw_jexp(−it_jω) obeys |R(ω)|≤1. The noise assumption here is ||ε||_W≤η, with no distribution assumption.

The estimator is â=D₀G⁻¹Φ*Wy, G=Φ*WΦ. Let q_n≥Σ_{m≠n}|G_nm| and q=max q_n<1. A Neumann series and Hermitian symmetry give invertibility, λ_min(G)≥1−q, and the row bound ||(G⁻¹−I)_{n·}||₁≤q_n/(1−q). If the normalized arithmetic tail correlations are at most τ_n, then

    |bias_n| ≤ B_n = n²[τ_n + q_n max_m τ_m/(1−q)].                 (1)

This follows directly by applying I+(G⁻¹−I) to the tail vector. Absolute convergence at real part2 justifies regrouping all series, since a(n)≤d₂(n) and Σd₂(n)/n²<∞.

**All integers beyond50 are covered.** For51≤k≤M=10000, sum d₂(k)k⁻²|R(log(k/n))| with Arb outward arithmetic, for all50 targets. The signed mixture is formed before taking absolute values. Compute d₂ by exact divisor convolution. For M<k≤L=10⁹ and1≤n≤50, every sine denominator in the closed midpoint cosine-response formula has argument between

    log((M+1)/50)/10 − 8π/m   and   log(L)/10 + 8π/m,

for component size m∈{2550,8900}. Both endpoints lie in(0,π). Concavity of sine shows its minimum is at an endpoint, giving a positive rational lower bound s_m. The common numerator has modulus at most1; therefore each component response is at most C/(m s_m), where C=1+2Σ_{h=1}⁸|c_h|. Let H be the positively weighted sum of these two bounds.

For all x≥1, A(x)=Σ_{k≤x}d₂(k)=Σ_{a≤x}floor(x/a)≤x(1+logx). Partial summation gives

    Σ_{k>x} d₂(k)/k² = −A(x)/x² + 2∫_x^∞ A(t)t⁻³dt
                     ≤ 2(logx+2)/x.                            (2)

The discarded term is nonpositive. Thus a valid remote bound, uniform in n, is

    τ_remote ≤ H·2(logM+2)/M + 2(logL+2)/L < 1.308674×10⁻⁶.      (3)

The first term overcounts the middle interval, which is harmless; the second covers every higher alias and the entire infinite remainder using |R|≤1. No finite-support assumption or exchange of nonconvergent limits appears. Finite tails and Gram rows are rebuilt by `query_certificate.py`; a separate rational checker verifies the remote endpoints with convergent log/arctangent/sine series and all consequences. The complete τ_n are the finite endpoints plus(3).

**Two-stage decoder.** First round the real parts of â₂ and â₃. Their errors are bounded by B_n+ηn²/√(1−q), so the certificate verifies a strict1/2 margin for both. Then a(4),a(9) are known exactly from P4.1 and each belongs to{1,3}. Set c=(1,a(4),a(9)), supported at n=(5,20,45), and

    J=Σ c_n²/n⁴,    α_n=(c_n/n⁴)/J,    z=Σ α_n â_n.

Multiplicativity makes Σα_n a(n)=a(5), so this is an unbiased query on the finite prefix. Its tail bias is at most B_q=Σα_nB_n. For noise, put v_n=α_nn². The exact weighted operator identity gives

    ||v*G⁻¹Φ*W^(1/2)||² = v*G⁻¹v ≤ ||v||²/(1−q)
                         = 1/[(1−q)J].                         (4)

Hence rounding Re z returns a(5) whenever B_q+η/√((1−q)J)<1/2. The same observation is used at both stages; simultaneous deterministic inequalities require no independence and no union-probability argument. The rational certificate checks this for all four combinations of a(4),a(9), as well as the anchor inequalities.

At η=2001/100000=0.02001 every check passes, uniformly for every real quadratic field. The least sufficient boundary across cases exceeds0.02003156; the worst-case query bias is below0.000038664. These are sufficient bounds, not the optimal arithmetic minimax radius. This theorem recovers a(5), not all50 coefficients and not the field itself.

**Same-measure envelope comparison.** In the larger integer coefficient class 0≤a(n)≤d₂(n), hold every coefficient fixed except a(5), increasing it by1, and choose identical allowable tails (zero is allowed in that envelope). Both vectors satisfy the independent coordinate constraints, and their observation difference is Φ_{·5}/25 with W-norm1/25. Midpoint noise of radius1/50=0.02 makes them indistinguishable. Our actual-field guarantee0.02001 exceeds that envelope upper limit, with the same time grid, measure, noise norm, and a(5) query. No claim that these two envelope sources are quadratic fields is used; P4.1 proves why they cannot be. This is a strict certified separation between source classes, not a claim of large practical gain or an optimal new sensor design.

## Verification boundary and remaining questions

The finite checker does not prove its supplied 497,500 kernel evaluations: a full producer replay reconstructs those with Arb and reconstructs the Gram rows. A higher-precision replay supplies a separate enclosure check. Exact field-witness tests exercise local powers, multiplicativity, prime2, ramification, and deliberately invalid prefixes. Numerical tests support implementation fidelity; the infinitude and decoder arguments above remain the mathematical proofs.

The results do not determine sharp recovery limits under a discriminant bound, prove that higher-degree envelope extremizers are fields, or solve the full shared integral-tail problem. They establish an exact finite realizability rule for one genuine arithmetic family, an explicit invalid envelope collision, and a complete infinite-tail query certificate that crosses that collision threshold.
