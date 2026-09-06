# Harmonic acquisition: complete proofs for three adaptive cycles

## Shared model and interpretation

The source is a labelled tuple q=(q1,q2,q3), with each qj a probability vector on exponents 0,1,2,3. At a fixed nonadaptive real time t the observed complex scalar is F_t(q)=product over j of sum over a of qj,a exp(-it a log pj), with primes (2,3,5). There are m=6 readings unless stated otherwise. Factor distance is the square root of the sum of the three squared Euclidean factor distances; data distance is raw complex Euclidean norm, with no normalization by m. A global factor floor c means that every pair of sources satisfies data distance >=c times factor distance. Source normalization and exact prime labels are known. The closed product of simplices is included.

All new proofs below are elementary finite arguments; computational statements use exact integer/rational enumeration and outward Arb elementary functions. Nearby frequency-separation and superresolution literature is discussed in SOURCES.md. The package makes no historical-priority claim.

## Cycle 1 — the strongest single product-vertex obstruction

### Theorem H1

For general r known distinct primes and s exponent states, consider any two product vertices with exponent vectors a,b in {0,...,s-1}^r. Let k be the number of their unequal coordinates, X=product pj^aj, Y=product pj^bj, and delta=abs(log(X/Y))>0. Every schedule of m times satisfying abs(t_l)<=T has global factor floor at most

    U_pair(T)=sqrt(2m/k) sin(min(T delta,pi)/2).                 (H1)

For each k, let R_k>1 be the smallest of max(X,Y)/min(X,Y) over such pairs with k unequal coordinates. Then the strongest upper bound of form (H1) supplied by a single pair is the minimum over k of its right side with delta=log R_k. For a requested c with 0<=c<=sqrt(2m/k), the k-th bound requires

    T >= 2 asin(c sqrt(k/(2m))) / log R_k.                     (H2)

If c>sqrt(2m/k), that pair rules out c at any horizon. The zero target gives only T>=0.

**Complete proof.** A product vertex has response exp(-it log X). The two responses differ in modulus by exactly 2 abs(sin(t delta/2)). Its factor distance is sqrt(2k), since different coordinate unit vectors are orthogonal. If T delta<=pi, sine is increasing on [0,T delta/2]; otherwise its modulus is bounded by one. Sum the squares of m such bounds and divide by sqrt(2k) to obtain (H1). Every exponent difference belongs to {-(s-1),...,s-1}^r and every such difference is realized by its positive and negative parts. Unique prime factorization excludes ratio one for a nonzero difference. There are finitely many pairs, and the right side of (H1) is nondecreasing in positive delta, so the minimum ratio in each k class gives exactly the strongest member of that class. Inverting its increasing sine branch gives (H2); the saturated branch cannot strengthen it. This also proves the impossible-target and zero cases. QED.

The theorem is sharp only as a **single-pair, horizon-only upper-bound method**: maximizing that one pair's response is achieved by putting every reading at a maximizer, or approached with distinct times. It does not assert that such a schedule separates other vertices or general product distributions.

### Exact finite classification and worked result

For (2,3,5), s=4, orient each nonzero difference so that X>Y. Exact enumeration has 9,54,108 vectors in the k=1,2,3 classes, respectively. The minimum ratios are

    R1=2, R2=27/25, R3=25/24.

The checker exhausts the 171 oriented differences with integer prime powers and exact Fraction comparisons. An independent control instead enumerates every unordered pair among the 64 actual vertices. These methods agree. Because every possible difference is enumerated and every difference is realizable, the finite classification is a proof by exhaustive exact arithmetic, not a sample of nearby ratios.

For m=6 and c=163/200, the strongest bound is supplied by X=25 and Y=24, i.e. a=(0,0,2), b=(3,1,0), whose factor distance is sqrt(6). Outward evaluation of (H2) gives

    T >= 20.56316841858... .                                  (H3)

The previous single-factor cubic necessary bound was only 1.64705031364... under precisely the same target and norms. The new necessary horizon is over twelve times larger. In particular any six-reading schedule with all abs(t_l)<=20 has floor strictly below .815. Exact outward intervals are in cycle1_evidence.json; displayed decimals are descriptive.

### Boundaries and negative control

The minimum-ratio argument concerns vertices, which are legitimate sources in the full model; interior positivity cannot be silently imposed. Larger horizons make this particular obstruction saturate; they do not prove injectivity. For example the six distinct times t_l=2pi l/log2, l=1,...,6, lie below 55 and make every first-factor response equal to one. Two first-factor vertices are exactly indistinguishable, although the horizon-only H1 bound at T=55 permits .815. This separates a necessary acquisition condition from a sufficient design. Exact or adversarial clock uncertainty is not included in H1; it will require separately stated quantifiers if investigated.

### Numerical proof contract

cycle1.py reconstructs the integer labels and exact ratios, then evaluates log, asin, sine, and the cube root using Arb at 256 bits. Every result is enclosed again on a rational 1e-12 grid; the checker compares a fresh reconstruction with the complete record. A 384-bit control gives identical exported inequalities. Independent raw product-response checks exercise the factor norm and trigonometric identity; they are regression controls, while H1 and the outward endpoint calculations carry the universal statement.

## Cycle 2 — simultaneous source-pair constraints

### Theorem H2: a continuum dual obstruction

For an oriented nonzero exponent difference v, let k_v count its nonzero coordinates and delta_v=log(product pj^vj)>0. Put

    f_v(t)=(1-cos(delta_v t))/k_v.

For any finite collection of such differences and any nonnegative rational weights lambda_v summing to one, every schedule with m readings in [-T,T] satisfies

    c_full^2 <= c_vertices^2
              <= m sup over 0<=t<=T of sum_v lambda_v f_v(t).  (H4)

Here c_vertices is the exact minimum response/factor-distance ratio over the finite product vertices, while c_full is the corresponding infimum over all factor distributions.

**Complete proof.** Cycle1's exact response identity gives a squared normalized distance sum_l f_v(t_l) for that pair. The minimum over all source pairs cannot exceed the minimum over vertices, which cannot exceed a convex combination of finitely many vertex-pair squared ratios. Rearranging the finite sums yields sum_l sum_v lambda_v f_v(t_l). Each term is at most the indicated supremum, using cosine's evenness for negative times. This proves (H4). It does not require statistical noise assumptions, an LP duality theorem, or a limiting exchange. Nonnegative weights summing to one are essential; signed or unnormalized combinations need not bound a minimum. QED.

Thus H4 is a rigorous design obstruction even if a numerical optimization used to propose its weights was approximate. Fractional acquisition measures can suggest such witnesses but do not prove that a six-atom experiment exists.

### Complete dual certificate and worked design

Take T=109/5=21.8 and the two actual vertex differences with ratios25/24 and27/20, both changing three factors. Use weights1761/2000 and239/2000. The checker partitions [0,T] into4096 exact adjoining intervals and evaluates their complete cosine boxes with outward Arb arithmetic. The maximum exported cell upper bound is strictly below (163/200)^2/6. Therefore **every** six-reading full-model schedule with abs(t_l)<=21.8 fails the target global floor .815. This improves Cycle1 by accounting for simultaneous pair requirements; no sampled time grid has proof authority.

A separate six-reading schedule, with exact decimal times

    (15.790052,25.962780,28.039208,28.695603,29.332467,29.966619),

has **vertex** factor floor >1.03. The producer evaluates sum_l f_v(t_l) outward for all171 oriented exponent differences. Every lower endpoint is larger than1.03^2. Each of the64 vertices is an actual legal source, and the finite difference classification exhausts every possible vertex-pair response and denominator. Hence this is a complete finite-source separation certificate, not a sample. The minimum is approximately1.033454, and a distinct raw-product computation checks all2016 unordered vertex pairs.

This concrete design establishes a limitation of any argument that uses only product vertices: such an argument cannot universally rule out horizon29.966619 at target .815, or even1.03. The remaining factor distributions could still destroy separation. Passing the finite vertex test is explicitly not a proof of full product-simplex injectivity or stability. The difference between that finite certificate and the earlier full-model schedules is a newly isolated research question, not an assumed bridge.

### Verification and boundaries

The continuum dual cover is rebuilt from rational times, weights, integer ratios, and Arb logarithms/cosines; its reported upper is rounded outward. A distinct center-value plus global Lipschitz numerical control checks that the slack is not a grid artifact, but the interval cover remains the proof. Full256/384-bit replays agree on the rational exported certificate. Tests reject negative/unnormalized dual weights, invalid ratios, repeated times, and a short schedule that fails vertex separation. Only the declared deterministic finite source geometry is certified; neither a dual optimum nor optimal acquisition time is asserted.

## Cycle 3 — a certified interior collision in the short vertex design

### Theorem H3: the finite vertex certificate does not extend to mixtures

For exactly the six rational times in Cycle2, there exist two distinct product sources q,r with every one of their24 factor probabilities greater than7/100, with factor distance greater than79/100, and with

    F_tl(q)=F_tl(r) for l=1,...,6.                            (H5)

Therefore this schedule's full-model global factor floor is zero, despite its vertex factor floor being greater than1.03. The noninjectivity occurs strictly inside the product of simplices; it is not caused by a boundary vertex, negative coefficient, floating near-collision, or change of the measurement model.

### A complete interval-existence lemma

Let f be a continuously differentiable map from a neighborhood of X=x0+[-rho,rho]^d to R^d, where rho>0 and x0 is fixed. Let R be any fixed rational d-by-d matrix. Suppose an interval derivative enclosure proves

    sup_x_in_X ||I-R Df(x)||_infinity <= L <1,
    ||R f(x0)||_infinity <= e,
    e+L rho <rho.                                             (H6)

Then f has exactly one zero in X.

**Complete proof.** Define S(x)=x-R f(x). Integrating DS along each chord of the convex box gives ||S(x)-S(y)||infinity<=L||x-y||infinity. In particular ||S(x)-x0||infinity<=e+Lrho<rho, so S maps the closed box into itself. Starting at x0 and iterating S, successive differences are bounded by a geometric series with ratio L. The iterates form a Cauchy sequence, converge in the complete finite-dimensional closed box, and continuity gives a fixed point x*. If two fixed points existed, their distance would be at most L times itself, so they would be equal.

To prove f(x*)=0 rather than merely Rf(x*)=0, note that ||I-RDf(x0)||<1 makes RDf(x0) invertible: the convergent geometric matrix series is an explicit inverse. In finite square dimensions this implies that R is invertible (a singular R would have a nonzero left null vector annihilating the product). Thus Rf(x*)=0 implies f(x*)=0. Any zero is a fixed point, proving uniqueness in X. QED. The lemma proves a local box root, not uniqueness among all global source pairs.

### Exact model-to-lemma construction

Use18 real complement coordinates: for each of q,r and each of its three factors, coordinates give the probabilities at exponents1,2,3; the exponent-zero probability is one minus their sum. Write E_lja=exp(-it_l a log pj), so each characteristic factor is affine in its three coordinates, and the raw response is their product. Take f to be the six real and six imaginary parts of F(q)-F(r).

The floating discovery proposes a well-separated interior source pair. Its only role is to choose rational center coordinates and twelve active coordinate indices. Both are frozen exactly in cycle3_inputs.json. The remaining six coordinates are held at their recorded rational values. Thus f is now a square12-dimensional real polynomial map of degree at most three, with exact transcendental constants E. It is smooth on all of R12. Every derivative column for a coordinate at exponent a of factor j is

    sign * (E_lja-E_lj0) * product over h!=j of chi_h(t_l),

where sign is positive for q and negative for r. The checker reconstructs these constants directly from the prime/time model and uses these explicit derivatives; it does not trust a supplied response matrix or sampled Jacobian.

The source box has rational radius1e-9 in the twelve active coordinates. The checker proposes R by rounding a point-Jacobian inverse to rational multiples of1e-12. The approximate inverse itself is not a proof premise: any such R is accepted only if the entire interval gate (H6) passes. Outward complex arithmetic encloses Df on the full box, evaluates f(x0), and then evaluates R Df and R f(x0). Absolute row sums yield L and e. The exported bound is

    L <= 0.000002922557,

and exact rational arithmetic verifies e+Lrho<rho. Consequently the lemma supplies an **exact** root within that box. Every factor's zero coordinate is reconstructed by normalization; all24 probability boxes have lower endpoints greater than .0770667338 and hence greater than7/100. The interval lower bound for the squared factor separation is greater than .639999996 and hence greater than(79/100)^2. The root therefore gives two distinct, strictly interior probability-product sources. H5 and the zero full-model floor follow. The exact endpoints and rational preconditioner are in cycle3_evidence.json.

This is an existence certificate for a nearby root, not an assertion that the recorded center coordinates themselves have exactly equal measurements. Their small floating residual is not used to infer equality. The interval contraction proves it.

### Independent and negative controls

The full proof is reconstructed at256 and384 bits. A distinct implementation expands the complete64-term tensor distribution and evaluates phases using log of the integer labels instead of multiplying three factor responses; its outward values agree with the factored calculation. Each derivative column is independently checked by a centered coordinate difference: the map is affine in that individual coordinate, so this identity is analytically exact rather than merely a small-step approximation. Exact rational tests separately check the final contraction, probability, and separation inequalities. Wrong times, invalid active coordinates, nonpositive radii, an excessively wide box, and inflated source/separation claims are rejected. These controls supplement, rather than replace, the full polynomial interval map and the proved existence lemma.

### Supported conclusion and next open question

Cycles1–2 constrain short acquisition through finite sources; Cycle3 proves that finite vertex success can coexist with a large interior exact collision. Merely improving the vertex-only schedule is therefore not a justified route to full recovery. A natural unexecuted successor is to impose a complete nonvertex secant or derivative-majorant certificate while optimizing acquisition time, or derive a family of interior obstructions that can be applied uniformly to all schedules in a short horizon. This three-cycle chain does not claim that every schedule below30 is noninjective: it proves that the explicitly certified vertex design is.
