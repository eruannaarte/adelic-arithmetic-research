# Actual arithmetic: exact geometry and adaptive recovery

These are developments of the project's arithmetic observability questions, without a claim of historical priority. The baseline is the previous five-path package. Every measurement norm below is stated explicitly: a normalized coefficient-space result is not silently applied to a full zeta-series sensor.

## Q1 — sharp retained-prefix geometry

Let A be the set of coefficient prefixes (a(1),…,a(50)) of real quadratic fields, with no discriminant bound. Use the normalized metric

    d(a,b)² = Σ_(n=1)^50 (a(n)−b(n))²/n⁴.

The query is q=a(5)∈{0,1,2}. Put J=5⁻⁴+20⁻⁴+45⁻⁴=1686433/1049760000. Then the exact minimum squared distances between query classes are

    δ01²=J,
    δ12²=J+4/25⁴,
    δ02²=4J+4/25⁴.                                  (Q1.1)

Consequently, observation of this normalized prefix with arbitrary Euclidean error permits uniform query recovery precisely for radii η<√J/2=0.02004054555934…; at equality it fails. This is a sharp theorem in the stated coefficient metric, not a claimed sharp threshold for8900 zeta readings.

**Arithmetic premises.** The existing realizability theorem supplies exactly the following input: a(1)=1, coprime multiplicativity, a(p)∈{0,1,2}, and a(p^k)=Σ_{j=0}^k(a(p)−1)^j characterize the possible finite quadratic prefixes. Every such prefix is realized infinitely often. Its complete proof appears in `research/five_paths_2026_09/path4_realizability/PROOF.md`. It follows from the quadratic splitting rules and unique ideal factorization in [Milne, Algebraic Number Theory, Theorems3.7,3.41 and Example3.44](https://www.jmilne.org/math/CourseNotes/ANTc.pdf), CRT for pairwise coprime moduli, and [Dirichlet's prime-progression theorem](https://arxiv.org/abs/0808.1408) applied only to a residue coprime to its modulus. We use the correct full quadratic ring of integers and treat prime2 separately. No arbitrary envelope witness is assumed to be a field.

**Lower bound proof.** If two prefixes differ at2 or3, their squared distance is at least min(2⁻⁴,3⁻⁴)=1/81, which is larger than every number in(Q1.1), by exact rational comparison. It remains to consider prefixes with equal a(2),a(3). They therefore have equal a(4),a(9), each in{1,3}. Multiplicativity forces

    Δa(20)=a(4)Δq,    Δa(45)=a(9)Δq.

Also a(25)=1 for q=0 or1 and a(25)=3 for q=2. Summing the four nonnegative contributions at5,20,25,45 gives exactly the applicable lower bound in(Q1.1), since a(4),a(9)≥1. All omitted squared coordinates are nonnegative; no cancellation is possible in this particular metric.

**Attainment proof.** Prescribe χ(p)=−1 at every prime p≤50 except5, and set χ(5)=q−1. At an inert prime, a(p^k)=0 for odd k and1 for even k. At5, the three possibilities give the local coefficients just described. Every integer≤50 divisible by5 is 5m with1≤m≤10; except m=1,4,5,9, its other inert prime factors force the coefficient to zero. Thus the three resulting prefixes differ only at5,20,25,45 and attain(Q1.1). The finite realizability theorem makes each prefix an actual field prefix. Other-prime coefficients are identical, rather than treated as free continuous variables.

For a finite collection of response points, distinct label neighborhoods of radiusη are disjoint if2η<δ. At2η≥δ, a minimizing pair's midpoint belongs to both closed noise balls. This proves the sharp recovery threshold and equality-case failure. Although infinitely many fields realize a prefix, there are finitely many distinct prefixes, so the distance minimum is attained.

**Explicit independent field witnesses.** `geometry.json` contains fundamental discriminants

    35473497127622875037, 12470811778107064205, 9894082171941632381,

for q=0,1,2 respectively. Each is R times an auxiliary prime, where R is1 or5, and is5 mod8. Consequently it is positive and squarefree and is itself the fundamental discriminant. The checker verifies every local symbol and the entire prefix. Auxiliary primes are certified using recursive integer Lucas certificates; FLINT is only a candidate/factorization producer.

For completeness, that primality criterion needs no probabilistic assumption. Suppose n>2, the complete factorization n−1=∏q_i^e_i has already certified prime factors, and a satisfies a^(n−1)≡1 modn and gcd(a^((n−1)/q_i)−1,n)=1 for every q_i. For any prime divisor r of n, a is a unit modulo r. Its multiplicative order divides both n−1 and r−1. The gcd conditions force every q_i^e_i to divide that order, hence n−1≤r−1. Since r divides n this implies r=n, so n is prime. The base n=2 is explicit. The finite checker verifies every product, modular power, gcd and recursion, not a probable-prime flag.

**Interpretation.** The preceding complete sensor guarantee had a sufficient boundary0.02003156. It already lies within roughly0.045% of the ideal worst-case coefficient radius in this diagnostic. Adding within-prefix multiplicative relations cannot change the worst-case coefficient-metric threshold. This neither proves optimality of the sensor decoder nor precludes larger conditional margins when some primes split, additional information beyond50, or a different observation norm.

## Q2 — infinite arithmetic information, nonattainment, and the critical radius

Let S_q consist of the full sequences (a_K(n)/n²)_(n≥1) for actual real quadratic fields with a_K(5)=q. They belong to l2. In this full coefficient metric,

    inf_(q≠r) dist(S_q,S_r) = δ = sqrt(ζ(8))/25.        (Q2.1)

No unequal-label actual field pair attains this infimum. Exact label recovery on all promised full-sequence observations with arbitrary l2 noise of norm≤η is possible if and only if

    η ≤ δ/2 = sqrt(ζ(8))/50 = 0.02004073208441… .      (Q2.2)

The endpoint is included, unlike Q1's finite-prefix theorem. “Possible” here means that the query label is uniquely defined on the union of the declared closed noise neighborhoods; it does not assert an efficiently computable decoder, access to an infinite physical sensor, or uniform separation above the critical radius.

**Universal separation.** At every prime, a(p^(2k)) is odd: it equals1 for ramification or inertia, and2k+1 for splitting. Consequently a(m²) is a positive odd integer for every m. Consider the set

    E = {5^(2h+1)m² : h≥0, m≥1, 5 does not divide m}.

Each n∈E has a unique such representation. If q=0, a(n)=0. If q=1, a(n)=a(m²) is odd and at least1. If q=2, a(n)=(2h+2)a(m²) is even and at least2. Thus an unequal-label difference has absolute value≥1 at every n∈E. Summing the nonnegative squared coordinates proves

    ||a_K/n²−a_L/n²||² ≥ Σ_(n∈E)n⁻⁴
       = [5⁻⁴/(1−5⁻⁸)] [(1−5⁻⁸)ζ(8)] = ζ(8)/625.

All series are positive and absolutely convergent, so the product decomposition is justified. For labels0 and2 the contributions are at least4 times this bound. For labels1 and2 the same bound applies, with the extra forced difference2 at n=25, which is outside E. Both pairs therefore have strictly larger distance thanδ.

For labels0 and1, let Q(√d), d>1 squarefree, be the field with q=1. There is an odd split prime p≠5 not dividing d: choose any prime divisor p of100d−1. This integer exceeds1 and is coprime to10d. Modulo p, (10d)²≡d, so d is a nonzero square and the quadratic splitting rule gives a(p²)=3. Hence at n=5p²∈E the q=1 coefficient is3, whereas the q=0 coefficient is0. This contributes9/n⁴ instead of the universal minimum1/n⁴, proving strict distance>δ. This elementary argument avoids assuming that an all-inert pattern is an actual field.

**Actual fields approach the infimum.** Define two formal coefficient sequences A₀,A₁ by prescribing every prime other than5 inert and prescribing5 inert or ramified. Then A₀(n)=1 exactly on perfect squares, while A₁(n)=1 when the exponents of every prime other than5 are even. Their difference is the indicator of E, so their squared distance is δ². Neither sequence is an actual quadratic field sequence, since every real quadratic field has a split prime by the argument just given (with a multiplier including5 if desired).

For each N≥5, prescribe those signs only at primes≤N. The finite CRT/Dirichlet realizability theorem gives actual fields K_N,L_N whose prefixes agree with A₀,A₁ throughN. This construction is existential for each finite N and does not postulate a single field realizing infinitely many chosen signs.

The approximation has a uniform complete tail bound. Both actual coefficient sequences lie between0 and d₂(n), so their difference has modulus≤d₂(n). For a prime exponent e,

    d₄(p^e)−d₂(p^e)²
      = (e+1)(e+2)(e+3)/6−(e+1)²
      = (e+1)e(e−1)/6 ≥0.

Multiplicativity gives d₂(n)²≤d₄(n). For n>N, n⁻⁴<N⁻²n⁻². Absolute Dirichlet convolution and ζ(2)<1+∫₁^∞x⁻²dx=2 therefore give

    Σ_(n>N) d₂(n)²/n⁴ ≤ N⁻²Σ_n d₄(n)/n²
                       = ζ(2)^4/N² <16/N².          (Q2.3)

It follows that the actual approximants have

    δ² < ||a_(K_N)/n²−a_(L_N)/n²||² < δ²+16/N².

Letting N grow proves the infimum and nonattainment. It also proves that the actual response sets are not closed in this coefficient Hilbert space: A₀,A₁ lie in their closures, with analogous tail convergence for each individual sequence.

**Critical recovery proof.** For η≤δ/2, every unequal-label pair has distance strictly greater than2η, so no point can belong to two unequal-label closed noise balls. The query is therefore uniquely determined for every promised observation. For η>δ/2, choose N so large that 16/N²<(2η)²−δ², equivalently δ²+16/N²<(2η)². This is possible because the right-hand gap is positive. A corresponding actual field pair has midpoint noise at mostη in both explanations, so recovery is impossible. The compact finite-prefix midpoint argument must not be applied at equality here: no minimizing field pair exists.

**Finite numerical content.** `infinite_geometry.py` encloses ζ(8) using the first100 terms and integral bounds 1/[7·101⁷]≤Σ_(n>100)n⁻⁸≤1/[7·100⁷]. Rational square-root brackets use integer square roots; no numerical zeta evaluation is trusted. The checker reconstructs the radius interval and the approximation bounds for N=50,500,5000,50000. These computations instantiate an analytic infinite theorem; finite checking alone would not prove the limiting statement.

Relative to Q1, access to the entire ideal coefficient sequence improves the universal half-distance by only about0.000931%. It changes the endpoint topology more than the practical numerical margin. This motivates investigating conditional arithmetic structure and actual finite decoding, rather than expecting a large uniform gain from simply extending the coefficient prefix.

## Q3 — conditional margins for the actual finite zeta sensor

Return to the exact8900-reading midpoint experiment and positive probability weight matrix W from the previous Path4. The physical observations are y_j=ζ_K(2+it_j)+ε_j, with t_j=(2j+1−8900)/10 and ||ε||_W≤η. The centered short grid is reused inside the long grid. The complete field coefficients obey0≤a(n)≤d₂(n); none of the infinite tail is set to zero.

Let Φ_(j,n)=exp(−it_j logn), n≤50, D=diag(n²), G=Φ*WΦ and â=DG⁻¹Φ*Wy. The baseline finite and infinite tail proof, independently checked and freshly replayed for this cycle, gives q_n≥Σ_(m≠n)|G_nm|, q=max q_n<1 and complete normalized tail bounds τ_n. Neumann's series and the exact Gram diagonal1 give

    |bias_n| ≤ B_n=n²[τ_n+q_n max_m τ_m/(1−q)].       (Q3.1)

The same weighted dual-norm calculation yields coefficient noise≤ηn²/√(1−q). For n=2,3 all nine declared noise radii below satisfy B_n+ηn²/√(1−q)<1/2. Thus rounding Re â₂,Re â₃ recovers a(2),a(3) exactly before selecting the query weights. No independence between stages is assumed.

Write x=a(2)−1,y=a(3)−1. For the index set I=(5,10,15,20,30,40,45), put

    c=(1,a(2),a(3),1+x+x²,a(2)a(3),1+x+x²+x³,1+y+y²).

Every index is5m where m is2,3-smooth and coprime to5. These are all such indices≤50. Multiplicativity gives a(n)=c_n a(5) at every n∈I. Set

    J=Σ_(n∈I)c_n²/n⁴,    α_n=c_n/(n⁴J),    z=Σ_(n∈I)α_n â_n.

Then Σα_n c_n=1, so the exact finite-prefix query is a(5). All α_n are nonnegative and the complete query bias is at most B_I=Σα_nB_n.

For v_n=α_nn², weighted operator multiplication gives

    ||v*G⁻¹Φ*W^(1/2)||²=v*G⁻¹v
       ≤||v||²/(1−q)=1/[(1−q)J].                   (Q3.2)

Therefore rounding Re z returns a(5) whenever

    B_I<1/2 and η²<(1/2−B_I)²(1−q)J.              (Q3.3)

The chosen weights minimize this particular Euclidean/Neumann noise upper bound among all linear unbiased combinations on I: Cauchy–Schwarz gives1=(Σα_nc_n)²≤(Σn⁴|α_n|²)J, with equality precisely at the chosen proportional vector. This does not prove optimality for the exact G metric, for bias plus noise jointly, or among nonlinear query decoders.

`conditional_query.json` supplies exact rational inequalities for all nine strata. The following declared radii are conservative decimal rationals; their endpoints pass the strict tests in(Q3.3):

| a(2) | a(3) | Declared weighted noise radius |
|---:|---:|---:|
| 0 | 0 | 0.02003 |
| 0 | 1 | 0.02015 |
| 0 | 2 | 0.02052 |
| 1 | 0 | 0.02064 |
| 1 | 1 | 0.02077 |
| 1 | 2 | 0.02116 |
| 2 | 0 | 0.02269 |
| 2 | 1 | 0.02283 |
| 2 | 2 | 0.02324 |

When both2 and3 split, the sufficient boundary exceeds0.02324532962, compared with0.02035273405 for the original5,20,45 combination evaluated in that same stratum, with identical tails, sensor, noise norm and Gram bound. The squared-radius comparison is exact and the radius gain exceeds14.21%. If both primes are inert, the extra usable multipliers vanish, and the theoretical boundary remains0.02003156766. The small difference between the new declared0.02003 and the older declared0.02001 is merely a choice of conservative reporting radius; no structural uniform gain is claimed.

**Finite decision and verification.** The implemented final decision takes the real coefficient estimates, certifies the two anchors using the declared radius, selects one of nine fixed rational weight vectors, and rounds its exact rational combination. It abstains if the supplied noise budget exceeds the certified stratum radius. The guard uses a global anchor budget that every stratum satisfies, so choosing the stratum is not circular. The theorem assumes the declared exact sensing decoder; any upstream numerical decoder error must be included in the observation/coefficient error contract. The final rational combination itself adds no floating-point error.

The new checker independently reconstructs B from the raw complete tail/Gram vectors, derives the2,3-smooth incidence from integer factorizations, checks the unbiased normalization and optimal upper-bound gain, verifies both anchors, and compares all nine cases against the original three-coordinate query under the same premises. A fresh source-to-certificate replay recomputes497500 finite tail terms, all Gram rows and the complete analytic remote contribution; it equals the prior bound source exactly. Independent full-grid tests apply the actual reused-weight decoder and worst-direction sensor noise to finite-part source controls. Those controls are interface tests, not a substitution of truncated series for the full-field theorem. Deliberately forged weights, budgets, strata and comparison bounds are rejected.

**Next question justified by Q3.** Conditional arithmetic information is useful even though uniform ideal information is nearly saturated. The next investigation is a joint classifier that also handles uncertain a(7) and the nonlinear a(25) relation, with a sharp query separation bound in the actual weighted observation norm and with full tails. That investigation is not counted among the three completed cycles.
