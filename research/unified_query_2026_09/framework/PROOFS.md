# Answer sets, exact elimination, and certified transfer

These results organize and extend the existing OIG/Arithmetic Observability certificate architecture. The general set and norm arguments are supplied in full; they are not claimed as historically new optimal-recovery theory. Useful contributions of this package are the concrete model connections and the quantified extensions in the five applications. Classical context includes [Donoho, Statistical Estimation and Optimal Recovery (1994)](https://web.stanford.edu/dept/statistics/cgi-bin/donoho/wp-content/uploads/2018/08/SEOR.pdf); its convex linear/Gaussian results are context, not assumed applicable to our nonlinear arithmetic and deterministic-noise models.

## 1. The exact object and the meaning of recovery

For a fixed design D, let A_D be the joint admissible set of source/nuisance pairs (x,u), let F_D:A_D→Y_D be the exact observation map, and let E_D(x,u)⊆Y_D be the allowed sensor errors. Source and nuisance need not be independent, convex, finite, or linear. The requested answer is q(x) in a query space Z. Define

    Y_D(x) = union_(u:(x,u)∈A_D) [F_D(x,u)+E_D(x,u)],
    Q_D(y) = {q(x): y∈Y_D(x)}.                         (1)

Only y in the union of the Y_D(x) are promised observations. An empty Q_D(y) is inconsistency with the declared model/budgets, not a successful recovery. Shared uncertainties are shared coordinates of A_D; making independent copies changes the experiment.

**Theorem 1 (exact discrete query).** There exists an arbitrary exact query decoder on all promised observations if and only if Q_D(y) is a singleton for every such y. Equivalently, Y_D(x) and Y_D(x') are disjoint whenever q(x)≠q(x').

**Proof.** A common observation with two different answers cannot be assigned both by one function. Conversely, assigning the unique element of each nonempty Q_D(y) defines a decoder. This is existence of a function; it does not prove measurability, computational feasibility, access to infinite data, or numerical implementability. □

For continuous answers in a finite-dimensional normed space Z, write

    rad Q = inf_(z∈Z) sup_(v∈Q) ||z-v||.

**Theorem 2 (deterministic minimax radius).** Over arbitrary decoders,

    inf_d sup_(promised y) sup_(v∈Q_D(y)) ||d(y)-v||
      = sup_(promised y) rad Q_D(y).                  (2)

Every bounded nonempty Q has a minimizing center. Thus an error tolerance r is achievable exactly when all these radii are at most r.

**Proof.** Every decoder's error at y is at least the radius there. For a bounded nonempty Q, its maximal-distance function f(z) is finite and 1-Lipschitz. Fix v0∈Q. Since f(z)≥||z-v0||, minimizing f can be restricted to a sufficiently large closed ball. Finite-dimensional compactness and continuity give a center. Selecting one center at each promised y proves the matching upper bound when the right side is finite. If a Q is unbounded its radius is infinite; if the radii have infinite supremum the lower bound already gives equality. The selection remains an existence statement. □

Diameter is not generally twice this radius. In Euclidean R² an equilateral triangle of side2 has radius2/√3>1. Consequently a generic diameter bound2r is not by itself an r-error certificate. Our continuous application bounds use an explicitly justified inverse or center, not this invalid inference.

## 2. Sound transfer through an observation transformation

Let T:Y_D→V be any known map, including a linear restriction or nuisance quotient. Suppose a verified reduced model gives outer observation sets C(x) satisfying

    T(Y_D(x)) ⊆ C(x) for every admissible source x.   (3)

Define Qhat(z)={q(x):z∈C(x)}.

**Theorem 3 (query-preserving containment).** For every promised y,

    Q_D(y) ⊆ Qhat(Ty).                               (4)

A singleton outer answer set therefore certifies the exact answer. An explicit ball containing Qhat(Ty) certifies the corresponding error. Empty outer sets reject the contract. Multiple outer answers mean this certificate abstains; they need not prove ambiguity of the original experiment.

**Proof.** If q(x)∈Q_D(y), then y∈Y_D(x). Applying (3) gives Ty∈C(x), hence q(x)∈Qhat(Ty). Every stated consequence follows from set inclusion. □

This composes by induction. If S(C(x))⊆C2(x), then ST(Y_D(x))⊆C2(x). The reverse inclusion requires a separate lifting theorem. A projection can lose distinctions even if its calculations are exact.

For a linear T, a useful verified instance is

    T F_D(x,u) ∈ f(x,v)+R(x,v),
    T E_D(x,u) ⊆ N(x,v),

with a valid admissible reduced v for each (x,u). The outer sets are unions of f+R+N. If implemented preprocessing has an additional error in C_num, add C_num as well. Every inclusion must preserve the actual source/nuisance incidence; enlarging to a product of bounds is allowed as a conservative relaxation, while replacing the joint set by a smaller product is not.

Under further linear processing S, use S(R+N+C_num)=SR+SN+SC_num. This explicitly propagates discretization, analytic-tail, model, and numerical errors. Different contributions cannot be added as scalar radii until they are expressed in the same output norm or mapped by valid operator bounds. Repeated readings cannot be assigned independent sensor noise merely because they appear in two windows.

## 3. When nuisance elimination is an exact equivalence

Suppose Y is a finite-dimensional real or complex inner-product space with metric W positive definite, and

    y = f(x,v)+Bz+e,   ||e||_W≤eta,

where v ranges over a declared bounded/structured admissible set and z is unrestricted, independently of x,v. Let P be the W-orthogonal projection onto the complement of ran B. Then

    exists z,e: y=f(x,v)+Bz+e, ||e||_W≤eta
    iff ||P(y-f(x,v))||_W≤eta.                       (5)

**Proof.** Forward, PB=0 and P is contractive in W. Reverse, set e=P(y-f(x,v)). The remaining residual (I-P)(y-f(x,v)) lies in ran B and can be written Bz. Its amplitude is unrestricted. This gives a legal explanation with the stated error bound. □

Union over the actual v proves equality of the original and projected answer sets, not merely containment. The argument applies to nonlinear f and nonlinear or discrete q. Full column rank of B is unnecessary; one may replace it by any basis of its range. If B depends on x, a source-specific projector may test feasibility, but a single global preprocessing P is not justified without further structure.

Bounded nuisance must not be removed as if unrestricted: in y=x+z with z=0, quotienting by the ambient nuisance column would discard all data although x is exactly observed. Likewise, two readings y1=x+z, y2=z with one shared z determine x by subtraction. Treating the two z values as independent destroys that answer. If sensing rows are restricted, form the quotient from the restricted B and the actual restricted noise metric. A full-data projector cannot simply be reused after a row deletion.

## 4. What deterministic centering can and cannot improve

Let c be a known vector independent of the unknown source and set T(y)=y-c. This is a bijection, and

    Q'_D(y-c)=Q_D(y).                                (6)

Indeed y∈Y_D(x) iff y-c∈Y_D(x)-c. Every decoder can be transported in either direction by adding/subtracting c. Thus the exact minimax risk and exact identifiability of the acquisition are unchanged.

For a source envelope a_k∈[0,d_k], subtracting the complete response of d_k/2 changes the residual interval to [-d_k/2,d_k/2]. A *fixed zero-centered absolute-tail certificate* may improve substantially, and the decoder using it may improve, while (6) still holds. In the inherited arithmetic result the >127× increase is a certified decoder/noise threshold, not an increase of intrinsic information by 127×. The computed correction's approximation error is an additional C_num and must be charged. Multiplicity of components and covariance of reused readings are unaffected by a known deterministic translation.

## 5. A common finite directional certificate

Suppose a finite template i with answer q_i has reduced observations

    z = c_i+r_i+K e+xi,  r_i∈R_i, ||e||≤eta, xi∈C_i.

Let ell be a real linear functional (real parts of complex linear forms are allowed). Assume verified upper bounds

    h_i^+ ≥ sup_(r_i,xi) ell(r_i+xi),
    h_i^- ≥ sup_(r_i,xi) -ell(r_i+xi),
    g² ≥ ||K*ell||_*².

Then every legal observation satisfies the slab

    -h_i^- - eta g ≤ ell(z-c_i) ≤ h_i^+ + eta g.      (7)

**Proof.** Apply the support bounds and the defining dual-norm inequality |ell(K e)|≤||K*ell||_*||e||. No independence between directions or measurement stages is used. □

Intersecting any finite collection of these slabs gives outer template sets. Keep all compatible templates and return an answer only when their query labels agree. This is Theorem 3 and does not require nuisance labels to be uniquely identified.

For two different-answer templates choose ell oriented with d=ell(c_i-c_j)>0. Their relevant slabs are disjoint whenever

    d > h_i^- + h_j^+ + 2 eta g.                    (8)

The proof compares the smallest possible ell(z) for i with the largest for j. If g²>0 and d>h_i^-+h_j^+, an exact sufficient squared noise boundary is

    eta² < (d-h_i^--h_j^+)²/(4g²).                  (9)

If g=0, only the strict support gap is needed. Failure of (8) does not establish overlap of the full vector sets: the other directions may still separate them. A computational checker instantiates these inequalities from *model-derived* supports and gains; accepting arbitrary supports is only a conditional algebraic statement.

### Three concrete instantiations

**Actual quadratic fields.** After certifying a(2),a(3), templates are (a(5),a(7)) in {0,1,2}². The normalized retained coefficients include a(25), a(49), and a(50), with their actual prime-power relations. Let ell have vector Delta=c_i-c_j, d=S=||Delta||², tail support h=sum_n |Delta_n|b_n, and g²=S/(1-q_G), where q_G<1 is the complete Gram-row bound. Formula (9) is exactly

    eta² < (1-q_G)(S/2-h)²/S.

The 243 pair inequalities and 81 template guarantees in quadratic/ are instances of this same theorem. The actual sensor covariance enters through K, and no independent decoded-coordinate noise is assumed. All candidate patterns are realizable finite quadratic prefixes; the complete infinite tails remain controlled remainders. The resulting callable decoder handles uncertain a(7) without assuming it has been separately recovered.

**Polynomial-drift arithmetic sensing.** First use the exact quotient (5) for the actual W and polynomial drift subspace. The centered tail and the augmented finite inverse then enclose each retained integer coordinate by c_i plus symmetric bias b_n and sensor gain g_n. Adjacent integer queries have d=1 and h_i^-=h_j^+=b_n. The rational midpoint correction has an additional weighted error at most xi, so use the total observation-error radius eta_total=eta+xi. Formula (9) becomes the certified rounding gate

    eta_total² < (1/2-b_n)²/g_n².

The extended Schur estimates in noise/ produce b_n,g_n from all new polynomial cross moments and complete tail channels. Any separately bounded nonpolynomial residual is added in the same weighted norm before applying this gate; a coefficient-space solve error can instead be charged to its directional support. This is the same scalar transfer inequality as the quadratic template certificate, after an exact nuisance quotient. The source normalization a(1)=1 is necessary for eliminating a constant baseline while retaining the intended query.

These are distinct reductions of different infinite arithmetic classes, not a claim that their coefficient norms, sensor metrics, or tail envelopes coincide. The framework also covers the preparation and resolution paths through their explicit nonlinear/finite operator inclusions, while the harmonic collision gives exact overlapping answer sets rather than failure of an outer certificate.

**Nonlinear preparation, a third model.** In the validated pendulum box, the fixed decoder yields for two explanations of the same calibration and output records

    x_i≤sum_j R_ij x_j+2h_i+2eta c_i,
    x_i=|s_i−s'_i|, k_i=sum_j R_ij<1.

For M=max_i x_i and any index attaining it, (1−k_i)M≤2h_i+2eta c_i. Consequently the source diameter is at most Delta if all rows obey Delta(1−k_i)≥2h_i+2eta c_i. The shared scalar gate uses d=Delta(1−k_i), symmetric supports h_i, and gain²=c_i². Formula(9) gives a sufficient strict interior; equality is also admitted for this non-strict diameter conclusion. Its derivation uses the separate nonlinear variational theorem, so an arbitrary supplied R is not a physical certificate. Known measured preparation centers affect outer-domain containment, while their remaining widths and shared systematic corrections determine h_i. Calibration measurements and reference characterization add acquisition resources beyond the five dynamical outputs.

The common application checker recomputes all243 quadratic pair gates, 441 integer-coordinate gates across nine certified polynomial design/degree pairs, and three pendulum diameter gates through one exact function. It first invokes each model's strict checker and binds its actual certificate. These are applications of one inequality to three declared models, not 687 new theorems or independent reconstructions of inherited physical premises.

## 6. Global separation, attained endpoints, and resource costs

For exact centers f(x) in a normed data space with additive radius-eta closed-ball noise, two actual source explanations have overlapping observations iff ||f(x)-f(x')||≤2eta: the forward direction is the triangle inequality, and the reverse uses their midpoint. Consequently exact query recovery requires the strict inequality for *every actual unequal-query pair*.

An infimum delta>2eta suffices. An infimum delta<2eta supplies a failing pair by the definition of infimum. At equality, recovery fails precisely if some actual pair attains a distance at most2eta. This is why the infinite quadratic threshold includes its nonattained endpoint and the finite prefix threshold excludes its attained endpoint. Replacing a source class by its closure can change the theorem.

Uniform approximation ||F(x)-f(x)||≤rho gives the safe sufficient condition ||f(x)-f(x')||>2eta+2rho for every unequal-query pair. Query-dependent rho values replace 2rho by their sum. This follows by two triangle inequalities and is only a sufficient transfer. Structured support bounds (7) can be sharper than using one common rho because they retain direction and correlation.

For a declared cost c(D), the exact resource problem is to minimize c(D) subject to the answer-set criterion in Theorem 1 or 2. Computable outer certificates give feasible designs and upper resource bounds. Exact collisions give lower bounds. A failed outer certificate gives neither. Known invertible processing has zero information gain by (6), row restriction can reduce acquisition cost but loses data, and nuisance elimination is information-preserving for the query only under a lifting result such as (5). These distinctions are part of the common contract.
