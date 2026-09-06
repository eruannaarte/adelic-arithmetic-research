# Adaptive resolution proofs

## R1. Interior target placement preserves the calibrated information floor

**Model and inherited premise.** Use the declared model in `research/five_paths_2026_09/path5_resolution/APPENDIX.md`: n=1001, K=2, g=4/5, midpoint x-grid, path Laplacians L_x=L_y=L_n, V=diag(1+g x), unit mean vector e and orthonormal source columns u_1,u_2. For a target cell j, replace the central target by δ_j. Write

H = I_y⊗L_x + L_y⊗V,
T_j(τ)u = (1+τ)^(1/4)(I_y⊗e^T) exp(-τH)(δ_j⊗Uu).

The y-DCT is orthogonal; its ℓth output is `(1+τ)^(1/4) v_ℓ(j) e^T exp[-τ(L_x+ω_ℓV)]Uu`. Hence G_j=T_j^T T_j is exactly the target-dependent Gram, with weights |v_ℓ(j)|². The zero mode vanishes because Uu has zero mean. At the central cell j=500 the even-mode formula is precisely the inherited certificate. The observation norm remains normalized Euclidean energy, not a proposed physical noise covariance.

The inherited certificate provides central finite lower floors c_m>0 and finite-to-continuum error bounds ε_m on τ∈[1,2] in the three metrics m=L2, declared H1, natural discrete H1. Its exact contents and model are bound in the new certificate; its full producer and proofs remain premises, not something proved by a hash. All three source metrics are diagonal and at least I, so whitening cannot increase an operator norm.

**Theorem R1.** If d≤j≤n−1−d and d≤500, put μ=(56/5)·2, r=2d+1 and assume r+1>μ. For all τ∈[1,2],

||G_j(τ)−G_500(τ)||₂ ≤ E_d := 8 μ^r/[r!(1−μ/(r+1))].

The same E_d bounds the difference after either source whitening. Therefore every metric has finite floor at least c_m−E_d and continuum error at most ε_m+E_d.

**Proof.** Each raw Gram entry is the target-diagonal block matrix element of

K = I_y⊗(L_x⊗I+I⊗L_x) + L_y⊗(V⊗I+I⊗V),

between δ_j⊗e⊗e and δ_j⊗u_a⊗u_b. To see this, diagonalize L_y orthogonally, tensorize the two x-responses for each eigenvalue, and sum |v_ℓ(j)|². This does not assume L_x and V commute. K is a symmetric weighted graph Laplacian: each x-direction edge has weight1 and each y-edge has weight V_aa+V_bb≤18/5. Its row sums are zero and its maximum diagonal is at most 4+36/5=56/5. Thus P=I−K/(56/5) has nonnegative entries, is symmetric, and has row sums1. Every eigenvalue has magnitude at most1 by the maximal-component row-sum argument; hence ||P^k||₂≤1.

Translated target-diagonal blocks of P^k agree for k≤2d. Indeed, expand a matrix entry as a sum over length-k walks, allowing diagonal steps. Away from the y-boundaries the weights are invariant under y-translation. A closed walk from j must make at least d steps to reach the nearest endpoint and d to return. The earliest boundary-specific diagonal step needs one additional step, so it first occurs at length2d+1. A walk that crosses the translated endpoint needs length at least2d+2. Both the target j and center have boundary distance at least d. The x-boundaries are identical under this translation and cause no discrepancy. This proves block agreement including arbitrary x endpoints.

Since I and P commute, the convergent exponential series gives `exp(-τK)=exp(-qτ) Σ (qτ)^k P^k/k!`, q=56/5. All differences through k=2d vanish. Every remaining matrix-element difference has magnitude at most2 because all four tensor vectors have norm1. Dropping exp(-qτ)≤1 and using qτ≤μ gives a raw entry bound `2 Σ_(k≥r) μ^k/k!`. For k≥r the ratio of consecutive terms is at most μ/(r+1)<1, yielding the displayed geometric remainder. The Gram normalization √(1+τ) is at most2. A real two-by-two matrix with entries bounded by e has operator norm at most2e. These two factors give E_d. Subtracting E_d from a minimum eigenvalue follows directly from the Rayleigh quotient. Whitening norms are at most1, so the same argument applies to all three metrics. ∎

**Worked certificate.** At d=41, E_d<3.252891×10^-12. Every j=41,…,959—919 of the1001 cells, coordinates from41.5/1001 to959.5/1001—retains more than99% of each inherited finite floor. Conservative new floors are >1.1764156×10^-7 (L2), >1.2895680×10^-9 (declared H1), and >1.3695765×10^-9 (natural discrete H1). The same simple bound fails the99% requirement at d=40; this is not a proof that such targets fail physically, nor an optimal boundary distance.

**Independent controls and limitations.** `test_placement.py` constructs the weighted graph by individual edges, independently of the proof's tensor expression. Exact rational matrix powers at x-size2,y-size11 agree through order4 for a depth2 target and center, and disagree at order5. A boundary target already disagrees at order1. A separate dense Arb exponential validates the finite-time inequality. Four focused tests and the rational checker pass. The result is uniform over fixed realized targets; it does not itself compare responses generated at different unknown targets. The full y-modal output (equivalently its orthogonal real-space transform) and the existing global x-average remain part of the protocol.

The spectral tools used here are finite-dimensional orthogonal diagonalization and the power-series definition of the matrix exponential, with hypotheses proved above; the real spectral theorem is [Axler, Linear Algebra Done Right, fourth edition, Theorem7.29](https://linear.axler.net/LADR4e.pdf). The inherited normalized model and continuum floors have their separate primary-source and Arb audit in the prior appendix. This is a new model-specific locality application and certificate, without a literature-priority claim.

## R2. An unknown target can be localized before source inversion

R1 gives a floor for each realized target separately. It does not by itself distinguish different target locations. The following explicit two-stage decoder closes that gap for nonzero sources, without assuming the target is known to a projector.

**Theorem R2.** Keep the R1 model and τ∈[1,2]. Suppose the unknown target is any integer j=47,…,953 and u≠0. Let y=T_j u in real-space output coordinates and observe z=y+ε, with `||ε||₂≤ν||y||₂`, ν=1/10000. Form `C(z)=Σ_(k=0)^(1000) k |z_k|² / ||z||₂²`. Rounding C(z) to the nearest integer returns exactly j. Then the least-squares (Moore–Penrose) inverse `(T_j^T T_j)^(-1)T_j^T` of the realized T_j returns a source estimate satisfying `||u_hat−u||_S≤||ε||₂/sqrt(c_S)` in each of the three source metrics, where c_S is the R1 floor.

In particular a common source-relative bound `||ε||₂≤3e-8||u||₂` suffices for location recovery and gives relative L2 source error <8.747e-5. In either H1 metric, `||ε||₂≤3e-9||u||_S` gives relative source error <1e-4. These are different calibrated assumptions, not interchangeable numerical noise radii. With a known minimum source norm a>0 they become ordinary absolute noise allowances by replacing the source norm on the right with a. No uniform positive absolute tolerance is asserted for arbitrarily small sources.

**Proof of boundary asymmetry bound.** Extend the y-axis to all integers and use the same finite x-axis. The infinite graph operator is `H_∞=I⊗L_x+L_Z⊗V`. Both finite and infinite single-response graphs have diagonal at most q=28/5. Their uniformized operators `P=I−H/q` are symmetric, nonnegative and stochastic. In the infinite case Jensen's inequality and column sums1 show directly that P contracts ℓ²; thus its exponential series is a bounded operator series. Put α=(1+τ)^(1/4) and X=diag(k−j) on the y-axis.

Embed the finite output into ℓ²(Z) by zero extension. If the target's boundary distance is d, the finite and infinite state powers applied to δ_j⊗Uu agree through k=d: a walk needs d steps to reach an endpoint and one more step to see its modified diagonal or cross it. Each k-step state is supported in |y−j|≤k and has norm at most||u||₂. Their difference therefore has X-weighted norm at most2k||u||₂. Projection on e commutes with X and contracts the norm. With μ=q·2=56/5, the exponential series gives

`||X(y−y_∞)||₂ ≤ 2α μ T_d(μ)||u||₂`,
`T_r(μ)= μ^r/[r!(1−μ/(r+1))]` when r+1>μ.

Also `||y+y_∞||₂≤2α||u||₂`. The infinite response is reflection-symmetric about j: reflection commutes with H_∞ and fixes the initial vector. Its energy first moment is therefore zero. All moments used are absolutely convergent because the weighted series is bounded by a convergent sum of kμ^k/k!. Cauchy–Schwarz applied to `Σ(k−j)(|y_k|²−|y_∞,k|²)` yields

`|C(y)−j| ≤ 4α² μ T_d(μ)/c_L2 ≤ 8μ T_d(μ)/c_L2`. (R2.1)

Here the denominator is at least c_L2||u||₂² by R1. This proof does not assume a response of one sign or a particular source direction; cancellation between the two source ports is included.

**Noise and source recovery.** Since C(y) lies between0 and1000, subtracting it inside the centroid numerator gives

`|C(y+ε)−C(y)| ≤ 1000(2ν+ν²)/(1−ν)²`. (R2.2)

Indeed the numerator difference is bounded by1000 times `2||y||||ε||+||ε||²`, and the noisy denominator is at least `(1−ν)²||y||²`. For d=47, (R2.1) is <0.079017 and (R2.2) is <0.200051; their exact sum is <0.279067<1/2. Hence rounding recovers the true target for every allowed source and noise. The least-squares inverse has norm at most1/sqrt(c_S) into the calibrated source norm: the pseudoinverse of `T_j S^(-1/2)` equals `S^(1/2)(T_j^T T_j)^(-1)T_j^T`, so its Euclidean gain follows from the whitened singular-value floor. An arbitrary left inverse need not obey this bound. The exact squared inequalities in `localization_certificate.json` prove that the declared source-relative noise implies the required output-relative bound and the stated source-error bounds. ∎

**Worked model and controls.** The certificate covers907 unknown locations for every τ∈[1,2]. For n=1001, j=47, τ=2, and u=(3/5,4/5), `simulate.py` directly propagates the two-dimensional weighted graph on1002001 states using its sparse stencil. The saved floating regression has normalized output energy about0.0005243413, centroid47.0000000016 under the recorded3e-8 far-channel noise, and correctly recovered location. This is a model-connected regression, not an interval premise; the guarantee is (R2.1)–(R2.2). Four independent controls check the first-moment series identity, reflection and centroid symmetry, noise perturbations at several coordinates, and exact zero-source nonidentifiability. If u=0 all locations yield the same zero response, so excluding that case is necessary. A positive absolute noise allowance without a source-amplitude lower bound is likewise impossible: sufficiently small distinct-location signals can both be hidden by noise at a common zero observation.

The real-space transformation is orthogonal, so it preserves the existing output metric; it is not an extra information source. The decoder still needs all1001 spatial output coordinates in this theorem and retains the existing global x-average. Target uncertainty is discrete cell placement; subcell shifts, target shape uncertainty, and timing uncertainty are outside this result.

## R3. A restricted spatial observation operator retains recovery

R2 uses a full spatial-output representation. Its noise-centroid bound also uses the full1000-cell coordinate range. Now assume the target prior is j∈{490,…,510}. This is additional information, not a consequence of R2. We change the observation operator to the99 rows indexed by I={451,…,549}, each still taking the same global x-average. Let P_I restrict the normalized output, and write T_j^I=P_I T_j.

**Theorem R3.** For every j in that prior and τ∈[1,2], the restricted Gram has, in all three source metrics, minimum eigenvalue greater than99% of the original central floor. Under `||ε_I||₂≤10^-3||T_j^I u||₂`, u≠0, rounding the restricted energy centroid identifies j exactly. Applying the least-squares inverse `[(T_j^I)^T T_j^I]^(-1)(T_j^I)^T` then has source error at most `||ε_I||₂/sqrt(c_S^I)`. The absolute source-relative allowances `3e-7||u||₂` or `3e-8||u||_S` for either H1 metric give relative source error <10^-3 and suffice for localization.

**Information loss.** Put w=39, the minimum distance from any allowed target to an endpoint of I, and retain μ=56/5. A k-step walk from the target stays inside I when k≤w. The contraction and finite-propagation properties proved for R2 give

`||(I−P_I^*P_I)T_j u||₂ ≤ α T_(w+1)(μ)||u||₂`.

Here and below a restriction is identified with its diagonal orthogonal projection when appearing inside an n-by-n expression. Consequently

`G_j−(T_j^I)^T T_j^I = T_j^T(I−P_I^*P_I)T_j`

is positive semidefinite with operator norm at most `L_w=2 T_(w+1)(μ)^2`, since α²=√(1+τ)≤2. This is an operator bound for every source combination, not an entrywise test at chosen source vectors. Source whitening contracts it. Thus `c_S^I=c_S−L_w` is a valid retained floor. At w=39, L_w<4.923987e-12. The exact checker proves c_S^I exceeds99% of each original central floor, including the earlier R1 placement loss. No output renormalization is performed after restriction; increasing the normalization would change the declared noise metric and is not used.

**Discarded first moment.** With X centered at the true target, support within k steps also gives

`||X(I−P_I^*P_I)T_j u||₂ ≤ α μ T_w(μ)||u||₂`.

Multiplying this by the discarded-output norm bounds its absolute energy first moment by `2μ T_w T_(w+1)||u||₂²`. The full finite response has first-moment error at most `8μ T_490||u||₂²` by R2, since every allowed target has global boundary distance≥490. Removing the discarded moment and dividing by the retained energy therefore yields

`|C(P_I y)−j| ≤ [8μT_490+2μT_w T_(w+1)]/(c_L2−L_w) <0.001690185`.

The restricted coordinate range is98, so the same deterministic noise proof as R2 gives centroid shift at most `98(2ν+ν²)/(1−ν)² <0.196491` at ν=1/1000. The exact total is <0.198181<1/2. Localization and the calibrated source inverse follow. The source-relative noise implications and error bounds are checked by squaring exact rational inequalities. ∎

**Worked example and a genuine boundary.** For n=1001, j=510, τ=2, u=(3/5,4/5), `window_example.py` forms the99-row observation matrix from direct finite graph propagation. Noise of norm3e-7 aligned with its least singular output direction leaves the rounded centroid at510 and gives source error about0.000150794, below the proved0.001 relative bound. The computed discarded information is about1.24e-59, which illustrates conservatism but has no authority to replace L_w. Three controls check the PSD Gram-loss identity, corrupted certificates, and a sharp geometry warning: two distinct readouts placed symmetrically about a central target have identical rows. Reflection about the center commutes with H and fixes δ_500⊗Uu; hence y_(500-r)=y_(500+r) for every source and every time. A two-row matrix of this form has rank at most1 and cannot recover the two source coordinates. This is an exact obstruction, not merely failure of our99-row sufficient bound.

**Acquisition and normalization limits.** At a central target only500 even modes are active. R1/R2 use the full-field Euclidean output, whose off-center realization generally activates all1000 nonzero modes; adding the known zero mode and applying the orthogonal DCT gives1001 spatial coordinates. They do not keep an old even-mode-only sensor unchanged. R3 defines99 transverse spatial-average channels with the same normalization. If only modal data are physically available, forming those spatial rows is post-processing and does not itself reduce acquisition. Direct99-channel acquisition requires those spatial-average readouts to be available. Each channel retains a global x-average; this is not a proof of fully local hardware observability. The narrower target prior, retained source band, known time, and explicit noise norm are essential.

**Next justified question, not a fourth executed cycle.** The symmetric-pair obstruction and the conservative99-row sufficiency leave a meaningful sensor-placement problem: certify a smaller asymmetric spatial bank for the same21-target prior while preserving an explicit source floor and target decoder margin. Any such comparison must retain the direct-versus-virtual acquisition distinction and the same normalization.
