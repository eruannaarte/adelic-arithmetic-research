# Path 2 proof appendix: reading count, acquisition time, and clock error

Status: analytic results proved below, with finite numerical inequalities independently reconstructed by `certificate_checker.py`. This is a new application and refinement of classical Fourier and perturbation arguments; no historical-priority claim is made. The exact count is a reconstructed baseline, not a new result of this package.

## 1. Model, norms, and baseline

Let `r>=1`, `s>=2`, `d=s-1`, and let `p_1,...,p_r` be distinct known primes. Write `lambda_j=log p_j`. Each factor `q_j` belongs to the closed simplex

`Delta_(s-1)={q in R^s:q_a>=0, sum q_a=1}`.

The source is `Psi(q)=q_1 tensor ... tensor q_r`. Its labelled factors are its one-axis marginals, so this parametrization is injective even on the boundary. Define

`chi_q(theta)=sum_(a=0)^d q_a exp(-ia theta)`,

`F_T(q)_ell=H_(t_ell)Psi(q)=product_j chi_(q_j)(lambda_j t_ell)`.

A reading is one complex scalar at a fixed nonadaptive time. The data norm is the unnormalized Euclidean norm on `C^m`, and the factor norm is `||q-q'||_fac^2=sum_j||q_j-q'_j||_2^2`. Complex data are realified isometrically whenever a real linear map is used. No unknown amplitude, off-box tail, unknown prime, or independently adjustable source phase is admitted.

AO VI's baseline has `r=3,s=4,p=(2,3,5)` and six rational readings

`(90540.692,220023.423,27819.627,94581.299,18084.130,75110.287)`.

Its stated target/off-axis phase boxes `tau<.001`, `delta<.017` imply the factor floor `sqrt(2)-9 sqrt(1202)/500 > .7901`. Both its original 384-bit verifier and this package's phase reconstruction reproduced those inequalities. The original verifier returned payload `02a00b4a1bb18ab366cd1de844f1f23101f5c3f424329b12e268d981b42179fc`.

## 2. Reconstructing the exact global count

**Theorem P2.1 (global count, reconstructed).** The smallest number of fixed complex harmonic readings that is globally injective on the above product model is `M=r floor(s/2)`.

**Upper proof.** Put `k=floor(s/2)` and `omega_l=2 pi l/s`, `1<=l<=k`. If `h` is real and has zero sum, finite geometric-series orthogonality gives Parseval,

`sum_(l=0)^(s-1) |sum_a h_a exp(-ia omega_l)|^2=s||h||^2`.

The zero coefficient vanishes. Other frequencies occur in conjugate pairs; for even `s` the Nyquist coefficient is an unpaired real coefficient. Hence the chosen half obeys

`sum_(l=1)^k |hat h_l|^2 >= (s/2)||h||^2`.

Thus the ideal factor-isolating map with rows `G_(j,l)(q)=chi_(q_j)(omega_l)` has global factor floor `sqrt(s/2)`. Prime harmonic times can approximate its phase matrix arbitrarily closely: `lambda_1,...,lambda_r` are rationally independent, since an integer relation exponentiates to a forbidden prime factorization of 1. The elementary density argument below therefore supplies one distinct positive time near each ideal torus point. The uniform derivative perturbation theorem P2.3 gives a positive global factor floor when the phase errors are sufficiently small. This proves the upper count, including every boundary factor.

Here is a self-contained form of the density fact used in that argument. If a positive tail of the orbit `t lambda mod 2pi`, `t>=T_0`, missed a box of radius `delta in (0,pi)` around a torus point `phi`, consider

`P_K(x)=product_j ((1+cos(x_j-phi_j))/2)^K`.

It is a finite trigonometric polynomial. Every nonconstant Fourier term has time average zero because its frequency is a nonzero integer combination of the `lambda_j`. The mean is therefore its constant Fourier coefficient `b_K^r`, where `b_K=binom(2K,K)/4^K >= 1/(2K+1)`. The inequality follows because the largest of the `2K+1` binomial coefficients is at least their average. Outside the box, `P_K <= a^K` with `a=(1+cos delta)/2<1`, whereas `b_K^r >= (2K+1)^(-r)`. For sufficiently large `K`, `a^K < (2K+1)^(-r)`, a contradiction to the time average. The same proof applies after any `T_0`, so times can be positive and distinct. This reconstructs the needed Kronecker consequence without assuming a quantitative recurrence bound.

**Lower proof.** Reverse factor coordinates by `(Rq)_a=q_(d-a)`. Its antisymmetric subspace `A_-={b:Rb=-b}` has dimension `k`, and every such vector has zero sum. Set `u=(1/s,...,1/s)`. On any sufficiently small sphere of radius `rho>0` in `A_-^r`, both tuples `(u+b_j)_j` and `(u-b_j)_j` lie in the simplex interior and are distinct. Since

`chi_(Rq)(theta)=exp(-id theta) overline(chi_q(theta))`,

the centered reading `B_b(t)=exp(id t sum lambda_j/2) F_t(u+b)` satisfies `B_(-b)(t)=overline(B_b(t))`. Consequently

`Gamma(b)=(Im B_b(t_1),...,Im B_b(t_m))`

is a continuous odd map `S^(rk-1)->R^m`. If `m<=rk-1`, append zero coordinates and apply Borsuk's antipodal theorem to obtain `Gamma(b)=Gamma(-b)`. Oddness makes both zero. Every centered reading is then real and the two product tensors have exactly equal raw readings. Marginals distinguish the tensors. The sphere radius may tend to zero, proving collisions arbitrarily close to the uniform product. For `rk=1,m=0`, the same conclusion is immediate without a topological theorem. This proves the lower count.

The one accepted topological theorem is **Satz II on printed page 178** of [Borsuk's original 1933 paper](https://www.impan.pl/shop/en/publication/transaction/download/product/93008): a continuous map `S^n->R^n` identifies an antipodal pair. The publisher's scan was downloaded and that statement visually checked on printed page178. Here the sphere is Euclidean and compact, `Gamma` is a polynomial/trigonometric continuous function of its real coordinates, the codomain is padded to exactly `R^(rk-1)`, and antipodality is exactly coefficient reversal. These verify every hypothesis. We use the accepted theorem rather than claiming to re-prove algebraic topology.

## 3. Local stability is a different count

**Proposition P2.2 (local stable count).** Put `D=r(s-1)`. At least `ceil(D/2)` complex readings are necessary for an inverse that is locally Lipschitz in the full factor-coordinate dimension. There exist schedules with that many readings and simplex-interior points around which local Lipschitz recovery holds. Thus for `r=3,s=4`, five readings can be locally stable somewhere although every five-reading schedule fails global identification.

**Proof.** A local inverse-Lipschitz lower bound implies an injective differential by taking directional difference quotients. A real map into `2m` coordinates cannot have injective differential on a `D`-dimensional tangent space unless `2m>=D`.

For sufficiency, use local coordinates `q_j(a)=x_(j,a)` for `a>=1` and `q_j(0)=1-sum_(a>=1)x_(j,a)`. At the product vertex where all mass is at exponent zero, the derivative columns are `exp(-i nu_b t)-1`, with the `D` positive frequencies `nu_b=a log p_j`, `1<=a<=d`. They are distinct: equality of two would imply equality of distinct prime powers. Choose times `t_l=epsilon l`, `l=1,...,m`, `m=ceil(D/2)`. Use the `m` imaginary rows and the first `D-m` real rows. Their Taylor expansions start with odd powers `nu,nu^3,...,nu^(2m-1)` and even powers `nu^2,nu^4,...,nu^(2(D-m))`, respectively.

Within each parity block, the matrices of coefficients `l^(2a-1)` or `l^(2a)` are invertible Vandermonde matrices in distinct `l^2`, with nonzero row factors. Multiply by their inverses and scale the resulting rows by the corresponding nonzero factorials and powers of `epsilon`. As `epsilon->0`, the calibrated `D x D` minor tends, up to row signs and order, to `(nu_b^a)_(1<=a,b<=D)`. Its determinant is `product_b nu_b` times the nonzero Vandermonde determinant of the distinct frequencies. The uncalibrated minor is therefore nonzero for all sufficiently small positive `epsilon`. Fix one such epsilon. Continuity of the derivative then moves the nonzero minor from the vertex into the simplex interior. In a small convex neighborhood of that interior point the chosen square derivative stays close enough to its invertible value that integration along a chord gives a positive inverse-Lipschitz constant. This proves local stability without equating derivative rank with global recovery.

As a finite worked witness, the five exact times `(1/10,2/10,3/10,4/10,5/10)` at the interior tuple whose factors all equal `(97/100,1/100,1/100,1/100)` have a nonzero nine-by-nine differential minor. Select all five imaginary rows and the first four real rows, with columns `q_j(a)`, `a=1,2,3`, and `q_j(0)` their complement. The 384-bit checker reconstructs each raw harmonic derivative and encloses its determinant strictly between `-6.8e-35` and `-6.7e-35`. This supplies an actual arithmetic schedule and interior point for local stability. Its tiny determinant does not supply a useful noise guarantee, and every five-reading schedule still has the global collisions from P2.1. For the six-reading designs below, the stronger global theorem supplies a uniform quantitative floor.

## 4. A sharper global separation theorem with clock boxes

Define `z_a=a-d/2`, `D_s=d/2`, `A_s=(sum_a z_a^2)^(1/2)=sqrt(s(s^2-1)/12)`, and the centered factor polynomial

`psi_q(theta)=sum_a q_a exp(-iz_a theta)`.

For each row `ell=(j,l)`, choose integer windings `n_(ell,a)` and nominal time `t_ell`. Let the actual time be `t_ell+h_ell` with `|h_ell|<=rho_ell`. Define nonnegative phase-error bounds

`e_(ell,a)=|lambda_a t_ell-2pi n_(ell,a)-1_(a=j) omega_l|+lambda_a rho_ell`.

Define the nonnegative `M x r` block majorant `B` by

`B_(ell,a)=A_s e_(ell,a)` for `a!=j`,

`B_(ell,j)=A_s e_(ell,j)+sqrt(s) D_s sum_(a!=j)e_(ell,a)`.

Set `Gamma=max_i sum_j (B^T B)_(i,j)`.

**Theorem P2.3 (global count–phase–clock bound).** For every allowed time-perturbation vector, every pair of closed-simplex factor tuples satisfies

`||F_(T+h)(q)-F_(T+h)(q')||_2 >= [sqrt(s/2)-sqrt(Gamma)] ||q-q'||_fac`.

If the bracket is positive the actual schedule is globally injective. An ambient tensor floor is the same bracket divided by `sqrt(r)`.

**Proof.** For a probability vector, convexity and the elementary inequality `|exp(ix)-1|<=|x|` give `|psi_q(theta)|<=1` and `|psi_q(theta)-1|<=D_s|theta|`. For a zero-sum real vector `h`, Cauchy–Schwarz gives

`|psi_h(theta)-psi_h(omega)|<=A_s|theta-omega| ||h||`,

`|psi_h(theta)|<=A_s|theta| ||h||`, and `|psi_h(omega)|<=sqrt(s)||h||`.

The first inequality follows by integrating the vector derivative whose Euclidean norm is `A_s`; the second uses `psi_h(0)=0`. No unbounded source norm is hidden in these inequalities.

Put `theta_(ell,a)=lambda_a(t_ell+h_ell)-2pi n_(ell,a)`. Multiplying each raw row by the known unit scalar

`(-1)^(d sum_a n_(ell,a)) exp(id(t_ell+h_ell)sum_a lambda_a/2)`

converts it exactly into `product_a psi_(q_a)(theta_(ell,a))`. This preserves the data norm for a fixed realized schedule. The ideal map is the corresponding row-rotated factor DFT `G_(j,l)=psi_(q_j)(omega_l)` and has the same lower floor `sqrt(s/2)` as in P2.1.

Differentiate the product. The target derivative term differs from `psi_(h_j)(omega_l)` by at most

`[A_s e_(ell,j)+sqrt(s)D_s sum_(a!=j)e_(ell,a)] ||h_j||`.

Indeed, first change the target phase, then telescope the product of off-axis factors around 1; every intervening factor has modulus at most 1. Each off-axis derivative term is at most `A_s e_(ell,a)||h_a||`. Writing `v_a=||h_a||`, the vector of row errors is componentwise bounded by `Bv`, hence `||(DF-DG)h||<=||B||_2||h||_fac` uniformly over the product of simplices and every clock perturbation in the box.

Because `B^T B` is symmetric and nonnegative, its largest eigenvalue is at most its largest row sum: for an eigenvector choose a largest-magnitude component and apply the triangle inequality. Thus `||B||_2<=sqrt(Gamma)`. Integrate `DF-DG` along the straight factor-coordinate chord, which stays inside the product of simplices. Since `G` is linear, reverse triangle inequality proves the factor lower bound. Finally tensor telescoping and `||q_j||<=1` give `||Psi(q)-Psi(q')||<=sum_j||q_j-q'_j||<=sqrt(r)||q-q'||_fac`, proving the tensor bound.

The exact unit rotation is a proof device for a fixed clock. If the clock is unknown, its unknown phase is not available to a decoder. The next section treats that nuisance separately.

## 5. Unknown common clock and finite recovery errors

Let `Omega=d sum_j log p_j`. Every probability tensor is supported on frequencies in `[0,Omega]`; direct differentiation of its finite harmonic sum gives `|d H_t p/dt|<=Omega`. Therefore, for all sources and all shifts in a box,

`||H_(T+h)p-H_T p||_2 <= Omega (sum_ell rho_ell^2)^(1/2) =: V`.

This is a finite-amplitude bound, not a first-order approximation. It includes a single shared additive clock offset `h_ell=delta`, `|delta|<=rho`, with `V=Omega sqrt(M)rho`. A common affine clock `h_ell=delta+beta t_ell`, `|delta|<=rho_0`, `|beta|<=b_0`, is covered by `rho_ell=rho_0+b_0|t_ell|`. No independent-noise or covariance assumption is involved.

**Corollary P2.4 (known-clock and unknown-clock recovery).** Suppose the nominal map has factor floor `c_0>0`, and data satisfy `y=H_(T+h)Psi(q)+eta` with `||eta||<=epsilon` and shifts bounded as above. Every global least-squares minimizer `q_hat` on the nominal product model satisfies

`||q_hat-q||_fac <= 2(epsilon+V)/c_0`.

If the realized clock is known and its map has floor `c_h>0`, fitting that realized map instead gives `||q_hat-q||_fac<=2epsilon/c_h`. If two clock-nuisance fibres are compared, their distance is at least `(c_0||q-q'||_fac-2V)_+`.

**Proof.** Compactness makes a nominal minimizer exist. The true nominal model point has residual at most `epsilon+V`; hence so does the minimizer. Triangle inequality bounds the distance between their nominal responses by twice that residual, and the global lower floor finishes the proof. The known-clock version sets the drift budget to zero in the realized map. For fibres, apply the same triangle inequality to two allowed finite shifts and infimize. Clock values may differ between two explanations of one dataset, but each explanation uses one common clock across its readings when that is the declared model. The larger box bound remains valid for this correlated nuisance.

The corollary is an existence-and-stability result for global least squares. No efficient globally optimizing decoder is claimed. It also does not turn a continuous parameter into an exactly identifiable quantity under positive adversarial noise.

## 6. Certified six-reading tradeoffs

For `s=4`, the improved constants are `A_s=sqrt(5)` and `sqrt(s)D_s=3`. The old AO VI bound used a single worst phase box and the larger coefficient `d sqrt(s)=6`, followed by a Frobenius-style pooling. Centering the phases and retaining individual row errors are the two analytical improvements here.

The following bounds all use the same new theorem, six readings, and every independent absolute timing offset bounded by `1/1000`:

| Schedule | Maximum time | Global factor floor exceeds | Global tensor floor exceeds | Pure shared clock-rate radius sufficient |
|---|---:|---:|---:|---:|
| AO VI baseline | 220023.423 | 1.239141702928 | 0.715418795749 | 4.54497065069e-9 |
| Short | 1463.985949 | 0.503910443491 | 0.290932830197 | 6.83066665143e-7 |
| Balanced | 2773.804407 | 0.815089139403 | 0.470591934047 | 3.60515686497e-7 |
| Higher floor | 8081.202441 | 1.090781011902 | 0.629762710848 | 1.23743961038e-7 |

Displayed decimals are rounded downward; exact rational endpoints are in `certificate.json`. The clock-rate entries use `|beta|<=.001/T_max` and zero additive offset, so `|beta t_ell|<=.001`. They are sufficient radii, not maximal allowable clock errors. A nonzero additive offset and rate error share the same box budget; they cannot both consume the full separate budget simultaneously.

The balanced schedule is

`(2041.772404,2533.650963,1042.357996,534.842867,1921.720700,2773.804407)`.

The associated integer winding rows are

`(225,357,523), (279,443,649), (115,182,267), (59,93,137), (212,336,492), (306,485,710)`.

Rows target `(axis,phase)=(1,pi/2),(1,pi),(2,pi/2),(2,pi),(3,pi/2),(3,pi)`. All decimals denote exact rationals. The balanced maximum time is smaller than the old maximum by a factor `79.3218953884`; the short design is smaller by `150.2906658020`. The balanced robust floor exceeds the *old published* .7901, but the old schedule also benefits from the improved analysis and has the stronger 1.2391 floor shown in the table. Consequently this is a time–stability tradeoff, not domination under identical constants.

At sensor-noise radius `epsilon=.001` and unknown common offset `|delta|<=.001`, the universal raw clock-drift radius is at most `.024993594299`. Using the conservative robust floor of the balanced design even for its nominal map, P2.4 gives factor error at most `.063780985521`. If the realized clock is known, the same sensor noise gives factor error at most `.002453719359`. These two statements must not be interchanged.

## 7. An elementary time lower bound and boundary review

There is also a modest necessary time constraint independent of the sufficient phase design. For `s=4`, let `h=(-1,3,-3,1)` and change one factor from `u-a h` to `u+a h`, where `u=(1/4,...,1/4)` and `0<a<=1/12`; keep all other factors at exponent-zero vertices. These are legal simplex factors. The factor norm of their difference is `2a sqrt(20)`, while the single-prime harmonic difference has magnitude

`2a |exp(-it log p)-1|^3`.

Thus every schedule with `m` readings and `|t_ell|<=T_max` has global factor floor at most

`sqrt(m/20) min(T_max log p,2)^3`.

In particular achieving a prescribed positive global floor `c` requires

`T_max >= (c sqrt(20/m))^(1/3)/log p`.

Take the smallest prime for the strongest member of this family. The bound demonstrates cubic loss at small time; it does not explain the much larger Diophantine recurrence times of our sufficient construction or certify time optimality.

Boundary and counterexample checks:

- `r=1` and `s=2` are included in P2.1; the half-DFT inequality is conservative but valid for the unpaired Nyquist coefficient. A zero-reading collision handles the zero-dimensional sphere case.
- Simplex vertices and faces are included in the global proof because all bounds use nonnegativity, normalization, and convex chords. Strict positivity is used only to put the lower-bound reflection sphere in the interior and to state a local neighborhood.
- Equal primes or coincident prime-power frequencies invalidate the density/local Vandermonde argument; distinct known primes are essential.
- Duplicate/zero times, wrong windings, bad schedules, and excessive clock uncertainty fail the finite certificate controls. Failure of that sufficient certificate is not itself a proof of noninjectivity.
- An actual blind six-reading control is `t_l=2pi l/log 2`, `1<=l<=6`. All times are distinct, but `chi_(q_1)(t_l log 2)=1` for every first factor. Keeping the other factors at exponent-zero vertices and changing the first from exponent-zero to exponent-one produces exactly the same six values, all equal to 1. A correct reading count alone cannot ensure global identification.
- A Jacobian rank observed at isolated source points cannot replace the uniform derivative-error bound. P2.3 controls all chords; P2.2 makes only a local claim.
- Infinite Euler products, coefficient tails, unknown gain, and field realizability are outside this finite model.

## 8. Finite verification and trusted components

The checker creates each prime logarithm, pi, time, winding, and clock radius directly from exact integer or rational inputs. At 384-bit Arb precision it encloses every nominal phase error and adds the full clock-box error `lambda_a rho`. Each outward endpoint is rounded upward again to a rational grid of `10^-12`. Thereafter the block matrix, its Gram row sums, the square-root upper bound, and floor consequences use only Python exact integers and fractions. The radical constants are independently checked by squaring: `A_upper^2>=5` and `0<sqrt2_lower^2<2`. `isqrt` plus an exact square comparison supplies the outward square root of each rational Gram bound. No supplied floating response matrix is trusted.

The resulting file is compared with a fresh complete reconstruction. Repeating at 512 bits produces identical rational consequences. The 15-test suite also exercises direct raw harmonic evaluations, their exact centering identity, all 64 product-vertex derivatives at three common-clock values, simplex-boundary secants, an exactly blind resonant schedule, negative noise/floor input rejection, and finite unknown-clock drift. Those floating direct-model checks are regressions; the proof is the analytic argument plus the outward phase reconstruction. The separate five-reading local witness reconstructs a determinant from its raw harmonic derivative formula using Arb.

The trusted numerical components are Python exact arithmetic and `python-flint 0.9.0`/FLINT `3.6.0`/Arb logarithm, pi, elementary arithmetic, and endpoint conversion. Arb's inclusion contract is described in [Johansson's paper](https://arxiv.org/abs/1611.02831) and the [author's ball-semantics documentation](https://fredrikj.net/arb/using.html). Exact inputs avoid binary64-to-decimal ambiguity. We did not formally verify the Arb library, mechanize the analytic proofs, prove the search optimal, or independently implement transcendental arithmetic.

No expensive reconstruction is required: the certificate and focused tests finish in under a second on the current machine. The discovery scan is reproducible but contributes no correctness assumption to the final witness.
