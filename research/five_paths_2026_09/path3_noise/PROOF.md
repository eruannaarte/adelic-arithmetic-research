# Path 3: arithmetic sensing with actual sensor noise

## Scope, baseline, and new statement

The historical multiscale degree-14 certificate bounds noiseless coefficient bias by 0.4980274167750795, just below the half-integer rounding threshold. It supplies no sensor-noise guarantee by itself. This extension retains its complete finite plus infinite tail and Gram bounds, propagates noise through the actual decoder on 8,900 distinct observations, certifies nonzero deterministic and Gaussian noise tolerances, and proves that one target's noise variance actually increases under multiscale weighting. These are new consequences of the existing arithmetic envelope, not a new number-theoretic theorem or a claim of hardware validation.

## Mathematical acquisition model

Let a_k be nonnegative integers with a_k<=d_14(k), where d_14 is the coefficient of zeta(s)^14. The Dirichlet series F(2+it)=sum_(k>=1) a_k k^(-2-it) converges absolutely because sum d_14(k)k^-2=zeta(2)^14<infinity. The result applies to this coefficient envelope, hence to any actual degree-14 arithmetic source known to satisfy it. It does not infer realizability of every envelope sequence.

Measure y_j=F(2+it_j)+epsilon_j at

    t_j=(2j+1-8900)/10, j=0,...,8899.

The short grid T=510,m=2550 is exactly the outer grid's indices 3175,...,5724; no additional measurements occur. For the fixed eight binary64 coefficients c_l in REFERENCE_COEFFICIENTS (interpreted as exact dyadic rationals), define

    w_j^(m)= [1+2 sum_(l=1)^8 c_l cos(2pi*l*(j+1/2)/m)]/m.

The single-window weights are w^L with m=8900. Extend w^S from m=2550 by zero outside the shared indices. The multiscale weights are w=alpha w^S+(1-alpha)w^L, alpha=125/65536. Positivity at every actual sample is proved by outward cosine evaluation. Exact roots-of-unity cancellation gives sum w^L=sum w^S=sum w=1, since every harmonic index is strictly below its grid size. A floating sum merely containing one would not establish this identity by itself.

For retained n=1,...,50 set Phi_(j,n)=exp(-it_j log n), D=diag(n^2), W=diag(w_j), G=Phi* W Phi, and

    a_hat = D G^(-1) Phi* W y.

The finite retained signal is Phi D^(-1)a. The decoder is post-processing the original local complex measurements. It neither acquires arbitrary global linear functionals nor counts an inner-grid sample twice.

## Complete arithmetic bias and Neumann bounds

Let T_n bound |(Phi* W tail)_n|. The source artifacts enclose its finite sum over 51<=k<=10^6 and its complete k>10^6 tail separately. The multiscale finite bound uses the signed mixture response before absolute values; the remote bound is the exact upward-rounded positive mixture of verified remote components. The new parser binds the matching time/sample/window/degree contracts and both formal remote dependency hashes; those checks establish identity, while fresh dependency reconstruction establishes the inequalities.

Let E=G-I and q_n>=sum_m |E_(n,m)|, q=max q_n<1. The source Gram has exact diagonal one. The Neumann series gives

    G^(-1)=I+R,  R=-E+E^2-E^3+...,
    sum_m |R_(n,m)| <= delta_n := q_n/(1-q).

Indeed the absolute row sum of E^r is at most q_n q^(r-1), by induction; summing proves the inequality. Consequently the deterministic decoded coefficient bias is bounded by

    b_n=n^2[T_n+q_n max_m T_m/(1-q)].

The current maxima are b_multi=0.4980274167750795 and b_single=0.5959293953409309. The latter does not certify rounding even without noise. It is failure of this sufficient bias certificate, not proof that actual single-window recovery is impossible.

## Adversarial bounded noise theorem

For any fixed noise vector epsilon satisfying epsilon*W epsilon<=eta^2, the coefficient-noise error obeys

    |(D G^(-1)Phi*W epsilon)_n| <= n^2 eta/sqrt(1-q).

Proof: G is Hermitian. Symmetry of |E| and 2|x_n||x_m|<=|x_n|^2+|x_m|^2 imply |x*Ex|<=q||x||_2^2, hence G >= (1-q)I. The squared W^(-1)-dual norm of row n of G^(-1)Phi*W is (G^(-1))_(n,n), since Phi*W Phi=G. It is at most 1/(1-q). Weighted Cauchy–Schwarz proves the claim.

Therefore all 50 real integer coefficients round correctly whenever

    eta^2 < min_n [(1/2-b_n)^2(1-q)/n^4],

provided every b_n<1/2. Strict inequality avoids half-integer ties; bounding complex modulus is sufficient for rounding the real part. The multiscale squared threshold is about 6.22103022075e-13, or eta<7.88735077244e-7. The declared rational eta=7e-7 is certified strictly.

The two W-norm balls differ between designs. For an identical adversarial assumption on the same physical sensor vector, impose |epsilon_j|<=7e-7 for every j. Both measures have total mass one, so this common bound implies both weighted-norm bounds. It certifies multiscale rounding; the present single-window bias certificate remains insufficient. No lower noise level can be inferred as necessary for single-window recovery.

## Actual reused-reading covariance and variance bounds

Assume epsilon has mean zero and covariance Sigma=E[epsilon epsilon*]. Then exact linear propagation gives

    Cov(a_hat-a) = D G^(-1) Phi* W Sigma W Phi G^(-1) D.

The two Gram inverses are Hermitian. This formula follows directly by multiplying epsilon by the decoder on the left and its conjugate transpose on the right. It remains valid for arbitrary observation correlations when Sigma is the true covariance. The subsequent diagonal bounds specialize to Sigma=sigma^2 I.

For iid circular complex noise, define v_n as the variance divided by sigma^2. Set S2=sum_j w_j^2. The raw row exp(it_j log n)w_j has Euclidean norm sqrt(S2). Applying the rowwise Neumann correction and the triangle/reverse-triangle inequalities proves, whenever delta_n<1,

    n^4 S2(1-delta_n)^2 <= v_n <= n^4 S2(1+delta_n)^2.

No independence between decoded coefficients is needed. Outward enclosures for S2 and exact rational q_n yield the saved variance intervals.

The physical reuse is decisive:

    S2_multi = alpha^2 ||w^S||_2^2 +(1-alpha)^2 ||w^L||_2^2
               +2alpha(1-alpha)<w^S,w^L>.

The cross term is present because a shared sample has one error, multiplied by the sum of its two weights. Treating the component errors independently drops a positive term and describes a different experiment. Independent direct numerical covariance reconstruction finds that omission would understate S2 by approximately 0.5068%. The producer includes it.

Exact discrete Fourier orthogonality also gives the independent identity

    S2_single=(1+2 sum_l c_l^2)/8900,

because 8900 exceeds twice the largest harmonic. Outward direct summation encloses that exact rational value. Finally, the certified lower variance for target 50 under multiscale weighting divided by the certified upper single-window variance exceeds 1.000265975. Thus v_50,multi>v_50,single is proved: multiscale weighting buys a better deterministic bias certificate while increasing that target's iid noise variance. A direct 8900-by-50 floating decoder calculation gives ratio about 1.001273, strictly inside the rigorous interval conclusion; it is a diagnostic, not the proof.

## Circular Gaussian rounding guarantee

Now assume independent proper circular complex epsilon_j with density exp(-|z|^2/sigma^2)/(pi sigma^2); equivalently E|epsilon_j|^2=sigma^2 and the real and imaginary parts each have variance sigma^2/2. Let sigma=10^-5. A linear combination remains proper circular Gaussian, with variance sigma^2 v_n. Integrating its density in polar coordinates gives exactly

    P(|noise_n|>=r)=exp[-r^2/(sigma^2 v_n)].

This derivation fixes the convention; using sigma as the standard deviation of each real component would introduce a factor of two and invalidate the printed bound. By the triangle inequality, target n can fail the sufficient rounding condition only if |noise_n|>=1/2-b_n. A union bound, requiring no independence between the 50 decoded errors, therefore gives

    P(any rounding failure) <= sum_n exp[-(1/2-b_n)^2/(sigma^2 v_n,upper)]
                              <5.466e-14.

The failure bound includes the complete deterministic arithmetic bias. It assumes the exact stated Gaussian sampling law, absent hardware/model error and absent additional numerical decoder error. check_consequences.py independently verifies the saved exponential bound using rational lower Taylor sums for exp(x), not Arb or a float exponential.

## Validation and residual obligations

Fast producer replay rebuilds all Gram rows and the 8,900 actual weights. The independent consequence checker imports only the standard library and reconstructs the Neumann, variance, deterministic-radius, Gaussian-tail and variance-inflation conclusions. audit_checks.py adds direct full decoder covariance, exact grid reuse, strict half-integer boundary, and source-mutation checks. It found and repaired a genuine parser gap: the single-window remote tail previously was read without validating/binding its formal digest, so a stale-hash all-zero remote could falsely lower the bias to 0.10936. The repaired parser rejects stale, readdressed mismatched, and wrong-contract dependencies; source values and final numerical certificates did not change.

Complete tail replay is separate and more expensive. multiscale_rebuild.json records full finite multiscale reconstruction; rebuild_dependencies.py rebuilds both MPFR remotes and the full single-window finite/Gram source, writing dependency_rebuild.json on completion. Both records now report PASS: the multiscale reconstruction took417s, and both remote reconstructions plus the single-window reconstruction took394s. Fast mathematical consequence checks remain logically conditional on these independently reconstructed inputs. These source verifiers rely on exact dyadic integer arithmetic, Arb and MPFR outward arithmetic, and the earlier arithmetic-tail proofs. Neither artifact hashes nor a test count replace those premises. No literature novelty, physically calibrated noise law, or realization of every coefficient-envelope element is claimed.
