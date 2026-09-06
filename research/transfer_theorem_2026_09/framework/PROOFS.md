# Transfer of query guarantees through nuisance removal and restricted sensing

This is a finite-dimensional transfer theorem with explicit approximation contracts. The source class and its bounded structured uncertainties may be infinite-dimensional or nonlinear. All infinite-to-finite claims must enter through proved inclusions. The theorem is supplied in full; it is not a claim of historical novelty. Optimal recovery and positive-operator elimination are classical subjects: see [Donoho, Statistical Estimation and Optimal Recovery (1994)](https://web.stanford.edu/dept/statistics/cgi-bin/donoho/wp-content/uploads/2018/08/SEOR.pdf) and [Anderson and Trapp, Shorted Operators II (1975)](https://epubs.siam.org/doi/10.1137/0128007). Their specialized results are context; no statistical distribution is assumed here.

## 1. Experiment contract

Let theta range over the actual joint set Theta of source and bounded/shared nuisance coordinates. Its requested answer is q(theta) in a set Z, or in a finite-dimensional normed space when an error radius is requested. Measurements in real or complex finite-dimensional Y have the form

    y = f(theta) + B z + e,     ||e||_W <= eta,             (1)

where W is real symmetric positive definite, or Hermitian positive definite for complex measurements, and z is unrestricted and independent of theta. Rank deficiency of B is allowed. Source-dependent error radii can be used by assigning eta(theta) to each explanation. The unrestricted nuisance hypothesis is indispensable: bounded or correlated coordinates stay in Theta instead of being silently freed.

The physical acquisition or an exact linear preprocessing retains w=R y. If this is a restriction of the original error ball, its noise set is R{e:||e||_W<=eta}. If a newly designed device has a different error set, its declared metric replaces that pushforward; measurement deletion does not authorize renormalizing the noise.

Write Y(theta) for the allowed observations in (1) and

    Q(y) = {q(theta): y in Y(theta)},  H = union_theta Y(theta).

Only H is the promised domain. A singleton answer set means exact discrete recovery. A verified ball containing the answer set gives the stated continuous-query error. An empty outer set means the observation is inconsistent with that certificate's contract; multiple outer answers mean abstention, not proved ambiguity.

## 2. Exact metric for restriction followed by elimination

Whiten the original error using W^(1/2). Put

    A = R W^(-1/2),     L = ran A*,     N = ran(W^(1/2)B),
    M = L intersect N-perp.

Orthogonality in these definitions is Euclidean/Hermitian. For a retained residual r in ran R, the least squared original noise cost of explaining it by unrestricted nuisance is

    min_{z,e: R B z + R e = r} ||e||_W^2.                  (2)

**Theorem A (exact profiled restriction).** For every full residual v with r=Rv, (2) equals

    ||P_M W^(1/2)v||^2.                                  (3)

The minimum is attained. Hence theta is compatible with w at radius eta exactly when this cost for w-R f(theta) is at most eta². This gives equality of the original restricted and profiled answer sets, with no source linearity requirement.

**Proof.** Let a=W^(1/2)v and h=W^(1/2)e. The constraint says A(a-n-h)=0 for some n in N. Since ker A=L-perp, admissible h are precisely

    a - (N + L-perp).

This is an affine translate of a finite-dimensional closed subspace. Its unique minimum-norm vector is the orthogonal projection of a onto (N+L-perp)-perp = N-perp intersect L = M. Thus the minimum is (3), and decomposing a-P_M a in N+L-perp constructs a legal nuisance and retained-noise explanation. Changing the full lift v by ker R changes a by L-perp and leaves the result unchanged. Taking the union over actual theta proves the answer-set assertion. QED.

The retained-noise metric has an equivalent explicit form. Let Q_R=R W^(-1)R*. On ran R,

    min_{e:Re=r} ||e||_W^2 = r* Q_R^dagger r.             (4)

Indeed h=A*Q_R^dagger r is feasible and orthogonal to ker A, so is the minimum-norm lift. Then minimize (r-RBz)*Q_R^dagger(r-RBz) over z. Redundant retained coordinates must satisfy ran R consistency; assigning them independent noise is a different experiment.

For full row rank R, put H_R=Q_R^(-1) and let C contain any independent columns spanning ran(RB). Then the exact rational matrix formula is

    J_R = H_R - H_R C(C*H_R C)^(-1)C*H_R,
    (2) = r*J_R r.                                      (5)

For C with zero columns use J_R=H_R. Completing the square proves (5), including its attained nuisance minimizer. The consumer implements (5) for rational real data; its full-row-rank contract is explicit. The mathematical theorem also covers redundant rows through (4).

### Which operations can be interchanged?

In whitened coordinates let P=P_(N-perp). The operation A P a can be computed as D A a from the retained observations for every a if and only if

    P ker A subset ker A,

equivalently L is invariant under P. Necessity follows by applying a putative D to a in ker A. For sufficiency define D on ran A by D(Aa)=APa; the condition makes this well-defined. As P is self-adjoint, invariance of L-perp and L are equivalent. In that case the orthogonal projections P_L and P commute, and P_M=P_L P. Thus the restricted full quotient agrees with the correct quotient on retained coordinates with its transported metric.

This is weaker than reconstructing the entire full-data quotient P a, which is possible if and only if ker A subset N. Necessity again follows on ker A; sufficiency uses the same factorization argument. Equivalently, N-perp subset L and M=N-perp. These two implementation claims must not be conflated.

If M is a proper subspace of N-perp, choose nonzero h in N-perp intersect M-perp. Its full quotient is h but its restricted profiled residual is zero. The two source centers 0 and W^(-1/2)h therefore have a new noiseless ambiguity after restriction. At any fixed positive finite noise radius, scale h beyond twice that radius to keep the full-data response sets disjoint while the restricted sets overlap. Conversely M=N-perp preserves every source feasibility test. Consequently **restriction preserves all source families and all queries exactly if and only if ker A subset N**. A particular coarser query can need less information, as follows.

## 3. Exact preservation for one query, and sound approximate transfer

For answer a define the answer-class observation union U_a=union_{q(theta)=a}Y(theta). Under exact restriction R,

    Q_R(Ry) = {a: y in U_a + ker R}.

**Theorem B (query-specific exactness).** The equality Q_R(Ry)=Q(y) for every promised y in H holds if and only if

    (U_a + ker R) intersect H = U_a, for every answer a.   (6)

**Proof.** Membership in the left-hand set means Ry=Rv for some v in U_a, or y-v in ker R. Equality of the answer sets for every y is exactly the membership equivalence in (6). QED.

Saturation of each individual source's observations is sufficient, but is not necessary for a coarser query. Equality of noiseless kernels or equality of the uniform minimax risk is also insufficient for pointwise equality of answer sets. For example, y=(x+e1,e2), e1²+e2²<=eta², x unrestricted: retaining y1 preserves the worst-case error eta, but the full conditional interval radius is sqrt(eta²-y2²), while the retained interval radius is eta.

For approximation, suppose an implemented observation transform T and reduced sets C(theta) satisfy

    T(Y(theta)) subset C(theta)                          (7)

under their complete error contract. Then Q(y) subset {q(theta):Ty in C(theta)}. The proof is direct substitution of each legal explanation. Another verified containment composes with (7) by inclusion. This gives a sound decoder whenever the outer answers form a singleton or lie in an explicitly constructed ball. Reverse containment needs lifting as in Theorem A or saturation as in Theorem B; accurate calculations alone do not supply it.

For continuous queries, the exact conditional best worst-case error is rad Q(y)=inf_c sup_{a in Q(y)}||c-a||. In finite dimensions every bounded nonempty Q has a center: its maximal-distance function is continuous and coercive, so achieves its infimum on a sufficiently large compact ball. The uniform minimax radius over arbitrary decoders is sup_{y in H}rad Q(y), by this pointwise lower bound and selection of centers. This is an existence theorem, without a computational or measurability assertion. In general a diameter bound 2r does not imply radius r; an equilateral triangle is a counterexample. A supplied enclosing ball or proved inverse-error bound avoids that mistake.

## 4. Quantitative certificate through a complete processing pipeline

Let the actual final computed observation have the verified representation

    v = c(theta) + r(theta) + K e,
    r(theta) in C_theta,       ||e||_W <= eta(theta).      (8)

The set C_theta includes finite approximation, complete infinite tails, bounded/shared nuisance and numerical errors, with their true joint incidence or a proved outer enlargement. An exact nuisance quotient supplies no residual from unrestricted z. For successive known linear stages T_1,...,T_s with stage errors epsilon_j, the final error is exactly

    T_s...T_1 e + sum_j T_s...T_(j+1) epsilon_j.           (9)

Thus stage errors are propagated before evaluating norms or supports. Reused readings have the same e coordinate. If errors are coupled, retain that joint set; the support of a containing product set gives a conservative upper bound, never an independence assertion.

For a real linear functional ell on the final space, including real parts of complex functionals, define certified support bounds h_theta^+(ell), h_theta^-(ell) for ±ell(r), and a gain bound

    g(ell)^2 >= ell* K W^(-1)K* ell.                      (10)

Here the notation represents the real dual pairing when complex coordinates are used. Every compatible explanation obeys

    -h_theta^- - eta(theta)g <= ell(v-c(theta))
                                  <= h_theta^+ + eta(theta)g.   (11)

This follows from the support definitions and weighted Cauchy–Schwarz. Intersecting any certified slabs gives (7). For unequal answers theta,theta', orient ell so d=ell(c(theta)-c(theta'))>0. A sufficient separation condition is

    d > h_theta^- + h_theta'^+ + [eta(theta)+eta(theta')]g. (12)

The lower endpoint for theta then exceeds the upper endpoint for theta'. With common radius eta, symmetric support sum h, and g²>0, this is the exact scalar gate

    eta² < (d-h)²/(4g²),    d>h.                         (13)

At g=0 only d>h is required. For closed scalar intervals the strict inequality is necessary and sufficient for their disjointness. A failed single directional bound need not imply overlap of the vector sets. If every unequal-query pair is separated by some certified direction, all promised observations have one query label in the outer model. No intermediate nuisance label needs to be decoded.

For nonempty compact convex response sets K_i,K_j in the final real Euclidean space (realifying complex coordinates when needed), optimizing the exact directional supports is complete:

    dist(K_i,K_j)
      = max_{||ell||<=1} [inf_{a in K_i} ell(a) - sup_{b in K_j} ell(b)].  (14)

To prove this, let v be a minimum-norm point of the compact convex difference set K_i-K_j. If v=0 both sides are zero, using ell=0 and the common point. Otherwise minimality along the segment from v to any d in the difference set gives <v,d-v>>=0 by differentiating its squared norm at zero. Thus ell(d)=<v,d>/||v|| is at least ||v|| for all d, with equality at v. The reverse inequality follows from the dual-norm bound at a minimizing pair. QED.

Adding Euclidean closed noise balls with radii eta_i,eta_j gives disjoint sets exactly when this attained distance is greater than eta_i+eta_j. Necessity and sufficiency follow from the triangle inequality and allocating a shortest connecting segment between the two radii. Thus an optimized support certificate is exact for these compact convex templates. For an outer approximation it is exact only for that outer model.

**Convexification is not harmless for a query union.** If q=0 has exact responses {-1,+1} and q=1 has {0}, noiseless observations determine the query. Convexifying the q=0 class creates a false ambiguity at zero. The appropriate implementation keeps templates or structured alternatives until after feasibility and only then collects their query labels. Compact convex completeness does not justify taking a convex hull of a nonlinear answer-class union.

This reconstructs the previous arithmetic template and polynomial-rounding gates with their actual source-specific supports and sensor gains. The previous framework's exact scalar implementation is recovered algebraically; the new content includes the profiled metric, implementation criteria, and operator transfer below.

## 5. Restricted source-image transfer with certified model error

For a finite label j and nonzero source u in R^r, let S_j be positive definite and a=S_j^(1/2)u. After exact restriction/elimination and noise calibration, suppose the exact map is M_j a and the computable approximation is A_j a, with

    ||M_j-A_j|| <= rho_j,
    ||noise|| <= eta_j ||a||,
    ||additional computed-data error|| <= xi_j ||a||.

Set delta_j=rho_j+eta_j+xi_j. The source-image outer tube is

    C_j = {A_j a + v : a != 0, ||v|| <= delta_j||a||}.    (15)

If an absolute additional error chi is given instead, a declared amplitude lower bound a_min,j>0 permits xi_j=chi/a_min,j. Without an amplitude lower bound, a fixed positive absolute budget cannot be relabelled as a uniform relative budget.

**Theorem C (pair and inverse transfer).** Suppose, for every pair j!=k,

    [A_j,-A_k]*[A_j,-A_k] >= lambda_jk I,
    lambda_jk > delta_j² + delta_k².                     (16)

Then the tubes C_j,C_k are disjoint. Thus the observation determines its label among all admissible nonzero sources. If also A_j*A_j>=mu_j I with mu_j>0, the least-squares estimate after the correct label is known satisfies

    ||a_hat-a|| <= delta_j ||a|| / sqrt(mu_j),             (17)

provided that the final solve is exact. A certified solve error is added to the right side. These statements are uniform over any time or design parameter where the assumptions hold uniformly.

**Proof.** A common tube observation would give

    sqrt(lambda_jk) sqrt(||a||²+||b||²)
      <= ||A_j a-A_k b||
      <= delta_j||a||+delta_k||b||
      <= sqrt(delta_j²+delta_k²) sqrt(||a||²+||b||²),

contradicting (16). The least-squares inverse has norm at most 1/sqrt(mu_j): write its residual as A_j^dagger[(M_j-A_j)a+noise+computed error] and apply its singular-value bound. Returning u_hat=S_j^(-1/2)a_hat gives the same relative error in the declared S_j source norm. QED.

Pair preconditioning is permitted but must be charged. If a certificate instead proves C*G C>=lambda I for G=[A_j,-A_k]*[A_j,-A_k] and an invertible C with ||C||²<=b, then G>=lambda/b I, by substituting C^(-1)v and using ||C^(-1)v||>=||v||/||C||. Alternatively a full anisotropic lower form may be checked directly against (delta_j||a||+delta_k||b||)². A convenient discovery preconditioner is not a change of physical noise or source normalization.

This lower bound need not be sharp. It certifies every source direction and every pair of allowed labels, unlike a finite set of source-vector tests. With fewer than 2r real retained outputs, two injective r-dimensional label images intersect nontrivially by the dimension formula; rank deficiency already prevents within-label source recovery. Hence exact recovery of unrestricted source and label requires at least 2r rows. Sufficiency at 2r, and robustness there, require separate arguments.

### Certifying a continuous parameter interval

Suppose the actual block map B(t)=[M_j(t),-M_k(t)] has a computed center A(t_0), and verified bounds ||B(t)-A(t_0)||<=epsilon throughout a closed cell. If A(t_0)*A(t_0)>=lambda_0 I, then

    ||B(t)v|| >= (sqrt(lambda_0)-epsilon)||v||.

A proposed positive floor lambda is justified by sqrt(lambda_0)>epsilon and sqrt(lambda_0)>=epsilon+sqrt(lambda). These comparisons can be performed by exact rational squared inequalities with sign checks, or by outward intervals. A finite cover of closed cells including both endpoints yields a uniform theorem. Grid evaluations without a cell remainder do not.

## 6. Computational residuals and sharp failure controls

**Unrestricted nuisance leakage.** If an implemented linear transform L_tilde has L_tilde B!=0, then sup_z ||L_tilde B z||=infinity. Choose z_0 with nonzero image and scale it. Consequently a small matrix approximation alone supplies no amplitude-independent output error bound for arbitrary drift. Valid options are exact annihilation, an explicit amplitude bound, or a certified data-dependent computation residual. This is an obstruction to the proposed uniform error budget, not an impossibility theorem for every decoder.

For a floating least-squares solve, let A have full column rank and let v_tilde be a proposed source estimate. Its normal residual r=A*(y-A v_tilde) obeys

    ||v_tilde-A^dagger y|| <= ||r||/mu,

when A*A>=mu I. Indeed (A*A)(A^dagger y-v_tilde)=r. A verified residual bound must itself include arithmetic and model errors. This gives an explicit consequence checker for implementation error; a small unverified floating residual is only a diagnostic.

For exact centers in a normed space and closed equal-radius noise balls, two unequal-query explanations overlap exactly when their distance is at most 2eta: one implication is the triangle inequality and the other is the midpoint construction. If a global pair-distance infimum equals 2eta, overlap requires an actual pair attaining that endpoint. Replacing a class by its closure can change the answer. The strict certificates above deliberately avoid this unresolved endpoint unless an attained witness or lifting argument is supplied.

Known exact centering is a bijection and preserves answer sets and minimax risk. It can improve a particular finite-tail enclosure. Restricted sensing can save acquisition while losing answers. An exact nuisance quotient can preserve them. Theorems A–C assign these operations separate, testable roles in one transfer statement: **use the exact profiled geometry, contain every approximation error, and verify separation or an explicit enclosure in the resulting query space.**
