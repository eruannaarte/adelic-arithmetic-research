# Three adaptive preparation results: proofs and model contract

## Shared model and meaning of a certificate

The source is s=(u,v,e) in S=[-10^-4,10^-4]^3, with m1=l1=g=1, m2=exp(u), l2=exp(v). The physical queries are u,v; e is one global unknown clock. Nominal-time dynamics are z'=exp(e)F(z;u,v). All angles are unwrapped. Launches are A=(4/5,-7/20,0,0), B=(-3/5,9/10,0,0), C=(6/5,2/5,0,0). Actual launch g is z_g+p_g, where four coordinates of p_g are unknown bounded errors shared by all its readings. Preparations need not follow a distribution and are not observed or fitted jointly as additional sources.

The available readings are A:(theta1 at 1, theta2 at 1, omega2 at 3/2), B:(theta1 at 3/4, omega1 at 5/4), C:(theta2 at 1, omega2 at 3/2). Their individual costs are respectively (1,1,3/2,1,5/4,1,3/2); group charges are c=(7/2,9/4,5/2). For budget shares a_g>=0 summing to one, every active row in group g has w_j=a_g/c_g. Observation o=f(s,p)+n obeys ||W^(1/2)n||_2<=eta. Within each budget design, this declared deterministic metric is held fixed across decoder/bound comparisons. Across different budget shares, W changes by the same budget-to-noise rule; eta is unchanged. Actual laboratory preparation accuracy and the relation of expenditure to noise have not been measured.

## Cycle 1: signed shared-preparation projection theorem

Let S and P be convex boxes, with |p_j|<=rho_j, and let f be C^1 on a neighborhood of S x P. Suppose J contains every source Jacobian D_s f(s,p), and Pmat contains every preparation Jacobian D_p f(s,p). Let A be a fixed m-by-d full-column-rank rational matrix, and B any fixed rational left inverse, BA=I. The concrete default is (A^T W A)^-1 A^T W. Form interval products before absolute values, and define

R_ij = sup |[B(J-A)]_ij|,
H_ij = sup |[B Pmat]_ij|,
c_i >= sqrt(sum_j B_ij^2/w_j),
v_i = 2(sum_j H_ij rho_j + eta c_i).

Here a preparation column has nonzero entries only in its launch's rows. Interval summation over those rows takes place before the absolute value; all admissible correlations between different launch errors are still allowed. If k=max_i sum_j R_ij<1, every two sources consistent with the same observation have

    ||s-s'||_infinity <= max_i v_i/(1-k).

This is a finite-amplitude, uniform nonlinear result. In particular, it does not replace a bounded unknown preparation by a nominal perturbation parameter.

**Proof.** At fixed p, integrate D_s f along the segment from s' to s. Then B(f(s,p)-f(s',p))=(s-s')+E(s-s'), where |E|<=R. At fixed s', integrate D_p f along the segment from p' to p. By the interval product enclosure, the absolute value of its i-th decoded component is at most sum_j H_ij|p_j-p'_j|<=2 sum_j H_ij rho_j. The equality of the observations and weighted Cauchy–Schwarz bound each of the two noise vectors by eta c_i. Consequently x=|s-s'| satisfies x<=Rx+v. Taking the infinity norm and using k<1 proves the bound. No state-dependent decoder is used. QED.

For equal preparation radii, the old absolute-before-projection alternative has Hbad_ik=sum_j |B_ij| sup|Pmat_jk|. Triangle inequality proves H<=Hbad componentwise. This is a justified tightening, although strict improvement is instance-dependent. It cannot be used if the readings came from separately prepared launches; those would have separate preparation columns.

**Nonlinear enclosure of J and Pmat.** `full_sensitivity.py` integrates the 31-dimensional state (z4, d_u z4, d_v z4, d_p1 z4,...,d_p4 z4, u,v,e). Its six-direction forward dual arithmetic differentiates the declared rational/trigonometric field exactly at the expression level. Initial physical-source derivatives are zero; preparation derivatives are the 4-by-4 identity, uniformly for the full initial preparation box. The initial source box is carried as three constant interval coordinates. Thus the sensitivity columns are partial derivatives with preparation fixed, or source fixed, as required. The exact clock derivative at a reading is tau exp(e)F_sensor(z(tau);u,v), by autonomous time dilation; this identity holds at every finite e in the box.

The mass determinant m*l^2*(1+m*sin(theta1-theta2)^2)>0 throughout real state space and all finite u,v. This proves local smoothness; the accepted compact tubes give bounded derivatives and continuation on every observation interval. Standard smooth-flow and parameter-dependence hypotheses are therefore checked, rather than assumed from a numerical trajectory. Primary reference: Gerald Teschl, *Ordinary Differential Equations and Dynamical Systems*, Theorems 2.10–2.11, [author's text](https://www.mat.univie.ac.at/~gerald/ftp/book-ode/ode.pdf).

For completeness, each outward integration step chooses an actual polynomial q(t) with exact dyadic coefficients. Let d>=sup_[0,h]|q'-G(q)|, let Aabs bound the absolute augmented Jacobian throughout q([0,h])+[-r,r], and let b=|X0-q(0)|+h d. The strict componentwise inequality b+h Aabs r<r excludes a first exit: integrating the differential error up to an alleged first exit bounds it strictly below the boundary. Local smoothness and the bounded tube allow continuation to h. The endpoint error b+h Aabs r therefore encloses the exact flow from every X0. Induction over exact rational steps proves all reported endpoints. The defect is bounded by its Taylor coefficients through order q-1 at zero and a qth-derivative remainder over the entire step, evaluated with outward interval power-series substitution. A failed or nonfinite enclosure cannot pass a strict gate. This is the same audited first-exit construction as the preserved Path 1, extended to the full preparation variational system; no differential inequality for separate absolute output biases is substituted for Pmat.

Arb is the outward-arithmetic dependency, not an independent validator of this application: Fredrik Johansson, *Arb: Efficient Arbitrary-Precision Midpoint-Radius Interval Arithmetic*, DOI 10.1109/TC.2017.2690633, [author paper](https://fredrikj.net/math/arbpaper.pdf). Exact rational export encloses the Arb endpoints. The standard-library consequence checker validates the model incidence, dimensions, costs, shares, BA=I, interval products, and rational inequalities; source-to-output replay is needed to verify that the supplied ODE intervals came from this producer. Neither SciPy diagnostic trajectories nor decimal summaries carry proof authority.

**Worked finite instance.** At rho=10^-6 and eta=10^-7, the shared-preparation diameter bounds are <1.640686e-5 for selected A+B, <1.600212e-5 for uniform A+B, and <2.112889e-5 for uniform A+B+C. The corresponding absolute-before-projection bounds on the identical sensitivity intervals are <2.962140e-5, <3.021550e-5, and <3.556746e-5. The preserved baseline at rho=10^-7 had bounds about 2.011627e-5, 1.979238e-5, and 2.489141e-5. Thus this instance certifies a ten-times-larger four-coordinate preparation radius with a smaller source diameter. The comparison is between sufficient upper bounds; it is not a theorem that one design has smaller actual minimax ambiguity.

**Sharp control and limitation.** With readings y1=x+p and y2=p and decoder B=(1,-1), BP=0: the shared preparation cancels exactly. Treating the two p values as separate unknowns changes BP and destroys cancellation. Conversely y=x+p has diameter 2rho at zero noise, so no generic theorem can infer exact recovery with nonzero preparation. k>=1 is failure of a sufficient criterion, not an impossibility theorem. All parameter segments must remain in the stated convex box.

## Cycle 2: a convex finite-robustness synthesis criterion

The left inverse in Cycle 1 need not be weighted least squares. We now synthesize a *fixed* decoder for the finite uncertainty task itself. Put D=J-A. For one prospective decoder row b, write D=Dmid+[-Drad,Drad] and Pmat=Pmid+[-Prad,Prad], using exact midpoint/radius decompositions. Then

    r(b) = ||b Dmid||_1 + sum_j |b_j| sum_c Drad_jc,
    h(b) = ||b Pmid||_1 + sum_j |b_j| sum_q Prad_jq

are exactly the row bounds used by interval summation. The weighted noise gain c(b)=sqrt(sum_j b_j^2/w_j) is convex. For any target delta>0 the feasibility function

    Phi(b)=delta r(b)+2rho h(b)+2eta c(b)

is convex on the affine subspace bA=e_i. Replacing c(b) by the conservative bound sum_j |b_j| sqrt_upper(1/w_j) gives a linear epigraph program after one nonnegative auxiliary variable for each absolute value. Its coefficients use the finite source/preparation enclosures, not only nominal sensitivities. The implementation scales its floating objective by delta for candidate generation; optimization status and objective values are diagnostic only.

**Rational correction.** If btilde is a rounded numerical candidate and B0 A=I is the exact baseline inverse, define b=btilde+(e_i-btilde A)B0. Direct multiplication gives bA=e_i exactly. Every final consequence is then recomputed from b using rational interval arithmetic and the tighter quadratic noise gain. Thus neither the numerical optimizer nor approximate equality constraints are trusted. The correction is not assumed to preserve optimality; it is accepted only if its exact certificate passes.

**Row-specific target theorem.** In Cycle 1 let k_i=sum_j R_ij and assume max k_i<1. If every row satisfies

    delta k_i + 2rho h_i + 2eta c_i <= delta,

then every feasible source pair has infinity distance at most delta. Indeed, for x<=Rx+v let M=max_i x_i. Choose an index attaining M. If M>delta, its row gives M<=k_i M+delta(1-k_i), which contradicts k_i<1. This retains each row's contraction allowance instead of replacing all of them by the worst row.

For a fixed decoder and an outer validated preparation radius rho0, the exact sufficient region is the intersection of half-planes

    0<=rho<=rho0, eta>=0,
    2rho h_i+2eta c_i<=delta(1-k_i) for all i.

The recorded maximum radius at fixed eta is min(rho0, min_i [delta(1-k_i)-2eta c_i]/(2h_i)); the instance has every h_i>0 and positive numerators. It is the boundary of this certificate, not a claimed fundamental boundary of the nonlinear inverse problem.

**Worked comparison.** The primary box rho0=10^-5 did not meet delta=10^-4 for any synthesized decoder. This negative result is retained in `cycle2_certificate.json`. Reusing those same uniform derivative bounds and already fixed decoders, the revised rho=7*10^-6 passes for all three designs, while the original least-squares decoder fails the same row criterion for all three. At eta=10^-7 the admissible radius boundaries are approximately:

| Fixed budget shares | Synthesized fixed decoder | Least squares |
|---|---:|---:|
| selected A+B, (2/3,1/3,0) | 7.66441636e-6 | 6.50386678e-6 |
| uniform A+B, (1/2,1/2,0) | 7.68349239e-6 | 6.59700324e-6 |
| uniform A+B+C, (1/3,1/3,1/3) | 7.66570699e-6 | 5.00351846e-6 |

Exact endpoints, including upward square-root rounding, are in `cycle2_calibration.json`. The optimized statistic uses only the same local readings. It is not an additional sensor or an assumption that initial states have been observed. This is a reproducible certificate improvement over the specified decoder controls, not a proof of global optimality of either decoder or budget allocation.

**Control.** A nominal preparation derivative can vanish and still be unsafe to ignore: f(s,p)=s+sp has D_p f(0,0)=0, but f(2/5,0)=f(8/25,1/4)=2/5. Unknown finite preparation creates ambiguity even with noiseless data. Our synthesis uses the entire uniform Pmat and includes the finite J-A term. Dropping either term does not inherit the theorem.

## Cycle 3: anisotropic calibration and a global volume certificate

The preceding equal-radius boundary was a sufficient specification of eight different unknown launch coordinates. It need not be a good way to spend preparation accuracy. Fix the already synthesized decoder and its finite derivative enclosures, eta, delta, and outer cap rho0=10^-5. Write rho_j=rho0 x_j for the eight A+B preparation coordinates. The theorem permits exactly the following sufficient calibration polytope:

    0 < x_j <= 1,
    Gx <= 1,
    G_ij = rho0 H_ij / b_i,
    b_i = [delta(1-k_i)-2eta c_i]/2 > 0.

The three row bounds k_i and every b_i are checked positive/contractive as required. All entries of G are nonnegative rationals. We optimize the product V(x)=product_j x_j (equivalently log volume) only over this polytope. The actual eight-dimensional preparation box has volume (2rho0)^8 V(x); volume ratios therefore equal normalized-product ratios. C is inactive in both A+B designs, so no unused preparation coordinate is counted as free volume. This compares selected versus uniform A+B budget shares with equal access and total cost, the same budget-to-noise rule, and the same eta; their weight matrices W differ with the shares.

**Global rational upper-bound theorem.** For any nonnegative rational multipliers lambda in R^3 and mu in R^8, set a_j=(G^T lambda)_j+mu_j and C=sum_i lambda_i+sum_j mu_j. If every a_j>0, then every feasible box obeys

    V(x) <= U = (C/8)^8 / product_j a_j.

**Proof.** Gx<=1 and x<=1, multiplied by nonnegative multipliers and summed, imply sum_j a_j x_j<=C. The eight numbers a_j x_j are positive. The arithmetic–geometric mean inequality gives product_j(a_j x_j)<=(C/8)^8; division by product a_j proves the claim. One elementary proof of AM–GM here is to fix a positive sum and maximize the product on its closed simplex: the boundary product is zero, and any unequal pair is improved by replacing it with two copies of its mean because ((a+b)/2)^2-ab=(a-b)^2/4>0. At a maximum all eight entries are equal, giving the stated inequality. Thus the only global optimization theorem used has been proved directly. QED.

A rational feasible point gives a lower bound V on the maximum; nonnegative rational multipliers give the upper bound U. Their exact ratio V/U certifies how close the returned point is to the best box supported by this *fixed* certificate. No optimizer convergence claim, floating logarithm, or approximate Karush–Kuhn–Tucker equality is needed. SciPy generates primal and multiplier candidates only. The checker verifies feasibility, positive weights, nonnegative multipliers, every derived number, and the rational inequality V/U>=999/1000. This proves the preregistered 99.9% goal and considerably more.

**Worked instance and limitation.** At eta=10^-7 and delta=10^-4, the selected A+B certificate permits all coordinate radii to equal 10^-5 except B.theta1, whose certified radius is exactly 6270072214/10^15. Its geometric mean radius is approximately 9.43320055e-6; the normalized volume is 5.26550258 times the best isotropic volume for the same decoder and outer enclosure. The ratio to the rigorous global upper bound exceeds 0.99999999998.

Uniform A+B gives B.theta1 radius 6300536639/10^15, with the other coordinates at 10^-5 or 10^-5 minus 10^-15 because of downward candidate rounding. Its geometric mean is approximately 9.43891755e-6; its volume is 5.18690410 times its corresponding isotropic volume, and its global optimality ratio exceeds 0.99999999946. These claims use exact certificate fractions; the displayed decimal geometric means are diagnostic. The weaker statement that each geometric mean is at least 8*10^-6 is checked by the exact eighth-power inequality, without taking roots.

The highly uneven optimal box identifies B.theta1 as the binding *mathematical calibration coordinate for these fixed decoders and enclosures*. It does not show that the actual nonlinear inverse problem requires precisely that tolerance, or that a laboratory can achieve any of these values. Radii beyond the validated outer cap are not certified even if the half-plane algebra alone would allow them. Likewise, changing the sensor set, re-preparing between readings, adding independent clocks, or changing the noise metric requires a new model and certificate.

**Controls.** The checker rejects any negative dual multiplier, nonpositive AM–GM weight, radius beyond the outward-validated cap, coordinate permutation, or violated calibration half-plane. Increasing B.theta1 beyond its binding face fails the declared finite certificate. An exact unit-cube control with lambda=0, mu=(1,...,1), x=(1,...,1) attains U=V=1 and checks the normalization. These are controls of the theorem and certificate boundary, not physical counterexamples to recoverability.
