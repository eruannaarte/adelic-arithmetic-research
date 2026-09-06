# Path 1: finite preparation, finite shared clock, and nonlinear inverse stability

## New result and historical baseline

The historical certificate proves a local derivative information floor >0.0180269 for exact preparation and one infinitesimal shared clock. This extension proves a uniform finite nonlinear inverse-stability bound with nonzero unknown preparation, a finite parameter neighbourhood, finite clock dilation, and bounded sensor error. It also certifies all seven existing scalar candidates, so a cost-matched uniform comparison is now physically connected to the declared nonlinear equations. This is a new application/certificate within this project, not a claim of literature novelty or empirical validation.

## Exact model and quantifiers

Let s=(u,v,e) belong to the convex box S=[-10^-4,10^-4]^3. Mass and length are m2=exp(u), l2=exp(v), with m1=l1=g=1. The source queries are u and v; e is a nuisance clock, shared globally. For launch g=A,B,C, start at z_g+p_g, where every coordinate of p_g lies in [-rho,rho], 0<=rho<=rho0=10^-7. Both angles and both dimensionless angular velocities are uncertain. Preparation p_g is fixed within that group's observations but otherwise unknown and independent across groups. It is not an additional measured or fitted parameter.

The nominal-time dynamics are z'=exp(e)F(z;u,v). Hence y_i(s,p) is the exact scalar flow output at declared nominal time tau_i, equivalently the physical flow at exp(e)tau_i. No linearization in e or p occurs in this definition. Readouts are unwrapped theta1, theta2, or dimensionless angular velocity. The seven rows and their launches/costs are frozen in PROTOCOL.md and checked literally in checker.py.

For shares a_g, use positive active-row weights w_i=a_g/c_g, with group costs c_A=7/2,c_B=9/4,c_C=5/2. The total budget shares sum to one. Noise is adversarial: ||W^(1/2)n||_2<=eta. This is a declared budget-normalized noise metric, not an inferred hardware law or a probability distribution. Zero-share rows are omitted. The global linear statistic below is post-processing the actual local sensor observations, never a free global sensor.

## The finite nonlinear inverse theorem

Let f:S x P -> R^m be C^1 in s. Suppose:

1. Every Jacobian D_s f(s,p) lies in an entrywise interval matrix J for all (s,p) in S x P.
2. For all s,p, |f_i(s,p)-f_i(s,0)|<=E_i.
3. A is a fixed rational m-by-3 matrix of rank 3 and B=(A^T W A)^(-1)A^T W, computed exactly. Thus BA=I.
4. With r_i=sum_j sup_{D in J}|(B(D-A))_ij|, define k=max_i r_i<1.

Put b_i=sum_j |B_ij|E_j and c_i=(sum_j B_ij^2/w_j)^(1/2). Let d_i=2(b_i+eta c_i) and D=max_i d_i/(1-k).

For every observation o and every two feasible sources s,s' in S for which

    o=f(s,p)+n=f(s',p')+n',
    p,p' in P, ||W^(1/2)n||_2,||W^(1/2)n'||_2 <= eta,

we have ||s-s'||_infinity <= D. More sharply, |s_i-s'_i|<=d_i+r_i D. In particular, the maximum of these two expressions for i=u,v bounds both physical parameter errors. If data come from the model, the true source is feasible, so choosing any feasible source has at most that error. This does not assert exact recovery under nonzero unknown errors.

### Complete proof

For fixed p, convexity of S and the fundamental theorem of calculus give

    f(s,p)-f(s',p) = A(s-s') + R,
    BR = integral_0^1 B(D_s f(s'+t(s-s'),p)-A)(s-s') dt.

Every integrand matrix lies in the computed interval product, so |(BR)_i|<=r_i ||s-s'||_infinity. Insert and subtract f(s',p) into the equality of observed data. Assumption 2 and the triangle inequality give |f_j(s',p)-f_j(s',p')|<=2E_j. Weighted Cauchy–Schwarz gives |(Bn)_i|<=eta c_i, and the same holds for n'. Applying B therefore yields

    |s_i-s'_i| <= r_i ||s-s'||_infinity + 2b_i+2eta c_i.

Taking a maximum and rearranging proves D because k<1; substituting D into the componentwise inequality proves the sharper bound. No varying or true-state-aware decoder is invoked: B is fixed once. The nonlinear change of clock direction is included in J and paid in k. At A, the first two rows of B annihilate the nominal clock column, but the proof does not pretend they annihilate every perturbed clock column. QED.

For noise/preparation tradeoffs, the same derivative box remains valid for rho<=rho0, while the independently propagated preparation bound scales as E(rho)<=rho/rho0 E(rho0). For any desired diameter delta, the explicit sufficient region is

    0<=rho<=rho0,
    2[(rho/rho0)b_i+eta c_i] <= delta(1-k), for i=1,2,3.

This is an intersection of exact half-planes in (rho,eta), not a probabilistic confidence region.

## Nonlinear source-to-certificate proof

### Smoothness and variational equations

The mass determinant is m2*l2^2*(1+m2*sin(theta1-theta2)^2)>0. Exponentials keep m2,l2 positive for every finite u,v. Thus F and exp(e)F are smooth on the entire real state/parameter space; accepted finite tubes give compact regions with bounded derivatives. Teschl's *Ordinary Differential Equations and Dynamical Systems*, Theorems 2.2/2.5 (local existence and uniqueness), 2.10 and 2.11 (smooth dependence, including constant parameters), provide the standard flow facts used here. Their hypotheses are explicitly satisfied by this determinant and compact-tube condition. The complete numerical enclosure argument is supplied below rather than delegated to a sampled solver.

Primary author source: https://www.mat.univie.ac.at/~gerald/ftp/book-ode/ode.pdf (Theorems 2.10–2.11 in section 2.4). The proof constructs the 15-dimensional state (z,d_u z,d_v z,u,v,e), with u'=v'=e'=0. Forward dual arithmetic gives d_u z'=D_z(exp(e)F)d_u z+partial_u(exp(e)F), and similarly for v. Preparation is parameter-independent, so both initial derivative columns are exactly zero even for a nonzero preparation box. The exact clock derivative is partial_e y_i=tau_i exp(e)F_sensor(z(tau_i);u,v), since the field is autonomous. It is valid at finite e, not just e=0.

### Picard–Taylor enclosure at each step

Let X0 enclose every exact augmented initial state at a segment start. Select an actual polynomial p(t), with exact dyadic coefficients, on [0,h]. Arb evaluates outward a defect bound d>=sup|p'-G(p)|. The implementation retains defect coefficients through degree q-1 at zero and bounds the degree-q Taylor remainder by evaluating its qth derivative/q! on the whole segment using interval power-series substitution. Rational vector-field denominators must exclude zero in every accepted evaluation; nonfinite values fail closed.

Let a rectangular box contain p([0,h])+[-r,r], and let A_ij>=sup|partial_j G_i| there. The strict componentwise gate

    |X0-p(0)| + h d + h A r < r

makes the Picard integral operator map the polynomial tube into itself. Equivalently, a first exit would satisfy an error strictly less than its boundary radius, a contradiction. Smoothness supplies local uniqueness; the bounded tube allows continuation throughout the segment. The left side is also an endpoint error radius at p(h). Induction over an exact rational partition proves all endpoint balls enclose every trajectory from the declared initial/parameter box.

The implementation inherits the audited polynomial/defect method from the historical solver but changes to a 15-coordinate RHS and retains already-sufficient radii during tube search. This latter change is required for nonzero initial boxes: multiplying every component at every unsuccessful iteration can inflate the driving uncertainty as fast as the driven sensitivity radii. Only acceptance of the strict mathematical inequality has proof authority; a failed search is not a nonexistence theorem.

### Preparation bias without counting parameter variation as preparation

Within each accepted state tube, let A_z be the upper-left 4-by-4 block of the absolute augmented Jacobian. For two trajectories with identical s and preparations p and 0, the mean-value theorem along the state segment gives

    |Delta z(t)| <= e0 + integral_0^t A_z |Delta z(r)| dr.

Both trajectories and their segment lie in the convex state tube; s is shared, so no parameter columns belong in A_z. A strict vector bound e0+h A_z q<q again rules out first exit and gives endpoint bound e1=e0+h A_z q. Start with e0=(rho0,rho0,rho0,rho0). Induction yields E_i at each sensor endpoint. There is no defect term because this is the exact difference equation, not a comparison with an approximate trajectory. The bound is homogeneous in initial rho; using the same accepted A_z values certifies E_i(rho)<=rho/rho0 E_i(rho0). This separates preparation bias from the genuine source/clock derivative uncertainty.

## Exact finite arithmetic and quantitative result

The independent checker imports no solver, NumPy, SciPy, or Arb. It reads rational row bounds, verifies the literal seven-row contract and globally shared clock, forms A from nominal enclosure midpoints, computes the weighted left inverse by exact Gaussian elimination, checks BA=I, reconstructs interval B(J-A), and proves k<1. Noise square roots are rounded upward using integer square-root inequalities. All threshold comparisons use Fractions; displayed decimals have no decision authority.

At eta=10^-7 and rho=rho0, the certified diameter bounds are:

| shares | k (rounded) | joint/physical maximum diameter bound |
|---|---:|---:|
| selected A+B: (2/3,1/3,0) | 0.077460403 | 2.011628e-5 |
| uniform A+B+C: (1/3,1/3,1/3) | 0.083249135 | 2.489142e-5 |
| uniform A+B: (1/2,1/2,0) | 0.076958234 | 1.979238e-5 |

These rounded diameter values are rounded upward. The exact records are comparison.json. Selected A+B gives a roughly 19% smaller sufficient bound than uniform A+B+C, while uniform A+B is about 1.6% better than selected A+B in this preparation-dominated comparison. This is a comparison of certified bounds, not a proof of true minimax superiority.

For target delta=10^-4 and rho=rho0, maximum noise radii admitted by the same half-plane certificate are approximately 5.67935565e-6, 4.39929761e-6, and 5.08139878e-6 respectively. Use noise_region.json for exact rational endpoints. The tiny preparation tolerance is a proved finite nonzero region, not evidence that a laboratory can achieve that tolerance.

## Boundary review and counterexamples

1. Nonzero errors cannot generally permit exact recovery: in scalar y=x+p+n with |p|<=rho, |n|<=eta, the distinct sources x=±(rho+eta) produce identical y=0 by opposite admissible p,n. Its feasible-set diameter is exactly 2(rho+eta). Our theorem appropriately gives error bounds.
2. A failed k<1 test is not impossibility: f(x)=2x, A=1 gives k=1 but f remains injective.
3. Shared-clock semantics matter. Independent per-output clocks would have different nuisance incidence and source dimension; the literal checker rejects such a declaration. No certification is transferred to that model.
4. rho=0 reduces preparation bias to zero analytically. Production hulls retain only a tiny outward rounding allowance. eta=0 leaves the bounded-preparation term; both zero give injectivity for fixed zero preparation within S.
5. W must be positive on active rows. Zero-share rows are omitted. Arbitrary reweighting without recomputing the noise metric is invalid.
6. The entire source segment must remain in S; convexity is essential to this proof. Angles are unwrapped, so no discontinuous wrap convention enters the sensor map.

## Evidence, sources, and trusted components

Evidence status: analytic theorem plus outward computational certificate, conditional on the declared mechanics and metric. Same-source deep replay recomputes the complete nonlinear enclosure rather than trusting supplied matrices. A second rational checker verifies the decisive algebra. The alternate 192-bit/order-9/step-1/125 proof is a separate outward time partition; it still shares Arb and the field implementation. Independent mechanical matrix-solve RHS and finite differences check differentiation, and finite nonlinear held-out cases check box containment and preparation/clock semantics; those numerical controls are not the proof.

Arb's outward arithmetic dependency is documented in F. Johansson, *Arb: Efficient Arbitrary-Precision Midpoint-Radius Interval Arithmetic*, IEEE Transactions on Computers 66(8), 1281–1292 (2017), DOI 10.1109/TC.2017.2690633; author's paper https://fredrikj.net/math/arbpaper.pdf. The source explains the interval implementation used; it does not independently validate this ODE application. Trusted components remain python-flint/Arb elementary functions and series operations, Python integer arithmetic, and the supplied analytic step proof. No formal proof-assistant or hardware validation claim is made.
