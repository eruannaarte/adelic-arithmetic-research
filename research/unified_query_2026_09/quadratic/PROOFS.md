# Joint recovery of a(5) with uncertain a(7)

## 1. Actual sensor, source, and finite templates

Keep the previous 8,900 complex observations y_j=ζ_K(2+it_j)+ε_j, t_j=(2j+1−8900)/10, for actual real quadratic fields K. The sensor errors obey ||ε||_W≤η in the same positive multiscale probability weights. The inner 2,550 readings are reused outer readings. The full coefficients obey 0≤a_K(n)≤d₂(n), coprime multiplicativity, and

    a(p^k)=sum_(j=0)^k (a(p)−1)^j,
    a(p)∈{0,1,2}.

These are coefficients of the full quadratic ring's Dedekind zeta function. The prior realizability proof checks the quadratic splitting conventions, the prime2 case, and unique ideal factorization; see [the accepted arithmetic inputs and hypotheses](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path4_realizability/PROOF.md). No arbitrary integer-envelope collision is called a field collision.

Write Φ_(j,n)=exp(−it_j log n), n≤50, G=Φ*WΦ, and D=diag(n²). The exact sensing inverse is â=D G⁻¹ Φ*W y. The previous complete source replay gives rational bounds q_n≥sum_(m≠n)|G_nm|, q=max q_n<1, and complete finite-plus-remote tail bounds τ_n. Thus the normalized estimate z_n=Re(â_n)/n² has

    z_n=a(n)/n²+b_n_actual+Re(Kε)_n,
    |b_n_actual|≤b_n:=τ_n+q_n max_m τ_m/(1−q),
    K=G⁻¹Φ*W.                                      (1)

No tail is discarded. The source checker validates the strict acquisition/positivity/remote/consequence contract. Its finite Gram/tail enclosures are explicitly inherited from the full Arb replay in the preceding package. All new template and support calculations here are exact rational arithmetic.

First certify a(2),a(3). Rounding is valid whenever, for n=2,3,

    b_n<1/(2n²),
    η² < [1/(2n²)−b_n]²(1−q).                       (2)

Fix the recovered anchors. Retain exactly the integers n≤50 with prime support in{2,3,5,7} and with a factor5 or7:

    I=(5,7,10,14,15,20,21,25,28,30,35,40,42,45,49,50).

For each template i=(a(5),a(7))∈{0,1,2}², multiplicativity gives every retained coefficient, and its center is c_i=(a_i(n)/n²)_(n∈I). In particular

    a(25)=1+(a(5)−1)+(a(5)−1)²,
    a(49)=1+(a(7)−1)+(a(7)−1)²,
    a(35)=a(5)a(7),  a(50)=a(2)a(25).                (3)

Thus (3) includes nonlinear query information and an uncertain nuisance label. The nine templates exhaust all legal retained responses for fixed anchors. The construction never assumes a(7) has been recovered.

Every one of the 81 anchor/template combinations occurs in an actual real quadratic field. A general proof chooses R as the product of the requested ramified odd primes among3,5,7. For unramified2 choose d=Rr with d≡1 or5 mod8 according to the requested character at2. For ramified2 choose squarefree d=2Rr and fundamental discriminant D=4d. At each other unramified odd prime, prescribe the nonzero residue of the auxiliary prime r that makes the desired Legendre symbol of d; choose residue1 at ramified primes. These choices and the mod8 condition combine by CRT into a residue coprime to the full modulus. Dirichlet's theorem supplies a positive prime r outside2,3,5,7. In the unramified2 case D=d; in the ramified2 case D=8Rr. Each D is positive fundamental and realizes all prescribed symbols. The only infinitude input is [Dirichlet's progression theorem](https://arxiv.org/abs/0808.1408), under its stated coprimality hypothesis.

For this finite coverage claim the independent audit provides an additional elementary alternative: it explicitly verifies positive fundamental discriminants at most1,365 for all 81 patterns, with exact squarefree-radicand checks and independent Kronecker/divisor-sum coefficients. That finite table alone suffices to establish existence of every pattern used here; no infinite sign prescription is involved.

## 2. Directional noise with the actual covariance

For any real direction Δ supported on I,

    |Δ·Re(Kε)| ≤ η sqrt(Δ*G⁻¹Δ)
                 ≤ η sqrt(S/(1−q)), S=||Δ||².        (4)

Indeed K W⁻¹ K*=G⁻¹Φ*WΦG⁻¹=G⁻¹. The first inequality is weighted Cauchy–Schwarz, with passing to real parts only decreasing the absolute bound. Gershgorin or the elementary row-sum norm estimate gives G≥(1−q)I, proving the second. This is one vector sensor-noise bound, not independent errors on decoded coefficients or independent noise for different query stages.

For distinct-query templates i,j, choose Δ=c_i−c_j and define

    S=Δ·Δ,
    h=sum_(n∈I)|Δ_n|b_n,
    R_ij²=(1−q)(S/2−h)²/S, provided S>2h.           (5)

Every admitted observation from template i obeys

    |Δ·(z−c_i)| ≤ h+η sqrt(S/(1−q)).                 (6)

The analogous slab for j is centered S away in this direction. If η²<R_ij², then S>2h+2η sqrt(S/(1−q)), so the two slabs are disjoint. This is precisely the shared [directional transfer theorem](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/framework/PROOFS.md:101).

For each i there are six other templates with a different a(5). Across nine templates there are27 unordered distinct-query pairs. The actual-template sufficient radius is

    R_i²=min_(j:q_j≠q_i) R_ij².                    (7)

All 243 pair inequalities across nine anchor strata are reconstructed exactly. The field's tail may depend on its template and other prime symbols; a larger common coordinate support in(1) is a conservative enclosure, not an independence assumption.

## 3. The decoder and the conditional guarantee

The callable decoder validates the supplied certificate, checks the global anchor condition(2), and rounds only a(2),a(3). It then keeps every template satisfying(6) for all its distinct-query directions. It returns a label only when all retained templates agree on a(5). Multiple labels cause abstention. An empty set reports inconsistency/abstention, never a recovered answer.

**Theorem.** Under the declared full-field sensor contract, every returned label is correct. If the true template is i and η² is below both R_i² and the anchor boundary, a label is always returned and equals its a(5).

**Proof.** The true template satisfies every tested slab by(1),(4), so it is never discarded. Thus a single retained label must be correct. Under(7), every wrong-query template j is incompatible with the observed point: orient Δ from true i to j; the true observation gives Δ·(z−c_j)≥S−h−ηsqrt(S/(1−q)), strictly larger than j's positive support bound. Hence all wrong labels are rejected. Templates with the correct query but a different a(7) may survive, which is harmless. □

The algorithm does not look up a radius using the unknown true template. Formula(7) is a conditional performance theorem about that same fixed feasible-answer decoder. It is not a circular selection rule or an assumption that the conditional stratum is known. Even outside a uniform guarantee, the decoder can certify individual observations if their outer answer set is a singleton.

If the supplied coefficient estimates have an additional known absolute numerical-error bound ν_n, enlarge b_n by ν_n/n² in the anchor and slab tests. The implementation does so explicitly. Converting a floating value to an exact rational does not establish its error bound. The canonical performance table uses ν=0, corresponding to the exact mathematical inverse; a floating deployment must supply and charge ν.

## 4. Quantitative results and the limit of the improvement

Every one of the 81 sufficient squared radii is at least the previous Q3 radius in the same anchor stratum and sensor norm. The improvement is modest but provable: the largest relative boundary gain exceeds0.4%, at inert2,3 with split5,7. Its declared sensor radius is0.02011172. The largest absolute declared radius is0.02332810, when all four small primes split.

For split2,3, the following comparisons use the same complete tails, physical W, and Gram bound as Q3:

| a(5) | a(7) | Declared η | Gain in sufficient boundary over Q3 |
|---:|---:|---:|---:|
| 0 | 0 | 0.02324532 | Exactly zero |
| 0 | 2 | 0.02325960 | >0.0614% |
| 1 | 2 | 0.02325960 | >0.0614% |
| 2 | 0 | 0.02331387 | >0.2948% |
| 2 | 2 | 0.02332810 | >0.3560% |

The complete exact table is certificate.json. Displayed decimal η values round down with resolution10⁻⁸ and pass the strict inequalities. The percentage comparisons are computed from square roots of the exact squared-boundary ratios, rather than ratios of rounded display radii.

For each anchor stratum, the pair a(5)=0 versus1 with a(7)=0 has exactly the old Q3 boundary. On this pair the new7-dependent coordinates vanish or agree, and the25 and50 coefficients agree as well. Its normalized squared separation is exactly the old J; its directional tail support gives exactly the old bias-times-J expression. Hence this particular method's universal worst-case boundary is unchanged. The exact full-class coefficient geometry from the preceding package is consistent with this limitation, but is not imported as a sharp physical-sensor bound.

For η near0.02, the old direct single-coefficient rounding test for a(7) fails: its sufficient boundary is only about0.010197. Our decoder requires no such intermediate guarantee. That is a limitation of that rounding certificate, not a proof that every possible a(7) decoder fails.

The new knowledge is a complete, implementable finite answer-set construction that uses uncertain arithmetic information and nonlinear query relations without conditioning on an unproved intermediate label. Its numerical improvement is small, and the worst-case equality makes that limit visible. The next justified question is whether using the exact directional Gram inverse or a joint bias/noise design can improve these small margins under the same acquisition; a sharp minimax threshold remains open.

## 5. Verification

Seven focused tests check exact coverage, independently generated actual-field prefixes, all 81 guarantees, retained ambiguity, forged direct-decoder inputs, numerical-error accounting, and actual8,900-row noise propagation. The physical-grid controls use the real nested-window weights and worst directions for nine templates; they are finite-part interface diagnostics, while the full-field theorem uses the complete inherited tail.

The independent auditor reconstructs the arithmetic through a separate Kronecker/divisor-sum implementation and checks explicit field witnesses, all243 pair directions, all81 comparisons, and the anchors without calling build(). Analytic proofs, exact finite checks, and model-to-certificate numerical premises remain separate obligations. No claim of historical priority, physical sensor validation, or globally optimal query design is made.
