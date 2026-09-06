# Independent Path 5 audit

**Verdict:** no defect found in the central remainder theorem, continuum-floor transfer, metric conventions, or canonical exact certificate. The scope remains fixed n=1001, K=2, central target, and 1<=tau<=2. This audit adds independent derivations and targeted computations; it did not rerun both expensive full n=1001 coefficient generations.

## 1. Signed spectral weights and the tensor derivative estimate

The Gram product is not generally a positive scalar Laplace mixture. Positivity of the matrix generator does not make every coefficient in its spectral representation positive. The appendix avoids this mistake by bounding the operator matrix element between tensor vectors.

An explicit independent justification is useful. For B=A tensor I+I tensor A and its orthogonal spectral projectors P_lambda, let E=e tensor e and U=u_i tensor u_j. Then

    sum_lambda |<E,P_lambda U>|
      <= sum_lambda ||P_lambda E|| ||P_lambda U||
      <= ||E|| ||U|| <= 1.

The second inequality is Cauchy–Schwarz and orthogonality of the projectors. Thus the signed spectral measure has total variation at most one, even when its total signed mass vanishes. Since lambda>=0,

    |d^k <E,exp(-tB)U>/dt^k|
      <= sup_(lambda>=0) lambda^k exp(-t lambda)
      <= k! a^(-k), t>=a>0.

This independently reconstructs the key step without assuming positive spectral coefficients. For continuum multiplication, the identical total-variation bound is the L1 norm of e(x)u_i(x)e(y)u_j(y), bounded by two applications of Cauchy–Schwarz. The outer finite weights have mass1000/1001; the continuum outer integral has mass one. Both preserve the bound.

A concrete signed control used A=diag(0,5), e=(1,1)/sqrt2, and u=(1,-1)/sqrt2. Its squared amplitude is

    R(t)=1/4-1/2 exp(-5t)+1/4 exp(-10t).

The spectral coefficients include a negative weight and have total variation exactly one. An independent 256-bit Arb computation checked the derivative inequality for k=0,...,30 at t=1,5/4,3/2,2 (124 cases). All passed. These cases are controls; the spectral-projector argument proves the general claim. The normalized derivative remainder then follows from the ordinary Leibniz formula and Taylor integral remainder, with the displayed factorials and rational binomial coefficients checked.

The hypotheses matter. A negative scalar generator grows, and a nonnormal matrix with positive eigenvalues can have arbitrarily large transient response. The existing negative controls address both cases. No commutation of L_n and V_n is assumed; only the two different tensor factors commute.

## 2. Common-core floor and metrics

I rederived the change of variables s=tau*4sin²(pi xi/2). Relative to (1/(2pi))s^(-1/2)ds, the density is

    2 sqrt(1+tau)/sqrt(4tau-s) >= 1.

For tau>=1, the fixed core [0,7/4] lies inside [0,4tau]. Restricting a positive-semidefinite outer-product integrand therefore gives G(tau)>=H_(7/4). Multiplying that core by sqrt2 exp(-7/4)<1 preserves a valid lower bound. This is the correct direction of the Loewner inequality.

A separate 256-bit common-core integration was written directly from the closed form for F_k, without calling `_common_core_entry`. All three new entry enclosures overlapped baseline.json, and both shifted principal-minor inequalities were reproved for the recorded L2 and H1 floors. This remains an independent expression using the same trusted Arb quadrature library.

All 36 saved inverse metric products were independently recomputed at256 bits: two cells, three metric choices, finite/continuum factors, and three symmetric entries. Every value was enclosed. Exact L2 identity factors correctly permit equality at interval endpoints. Natural discrete H1 uses S_n on the finite Gram and S on the continuum Gram; replacing both by S would change the claim. The present code preserves that distinction. Source hashes recorded in the certificate matched the current imported coefficient implementations.

The final transfer is valid under those metrics: an error bound U for the whitened difference gives finite floor at least ell-U by the Rayleigh quotient. There is no missing metric factor or implicit physical covariance interpretation.

## 3. Coefficient and exact-checker review

The shifted finite exponential estimate uses spectral enclosure [omega,4+(9/5)omega], centre2+(7/5)omega and radius2+(2/5)omega. Their difference is omega, giving the displayed exp(-c omega) remainder after shifting. Repeated applications of -A/k generate derivative coefficients, while the separate operator remainder is multiplied by ||A||^k/k!. Time Taylor remainders are added separately after coefficient differences are formed; they do not replace finite-exponential or quadrature error.

The continuum coefficient callback uses meromorphic operations and constant square roots. A complex enclosure through a denominator zero returns an indeterminate interval to permit quadrature subdivision. Returned finite enclosures, not requested tolerances, supply the certificate premises.

The Fraction-only checker reconstructs interval Horner evaluation, both positive-definiteness tests UI+E and UI-E, the metric-specific remainders, inherited floors, and exact adjacent-cell coverage. Off-diagonal uncertainty is included in the determinant criterion. Its documented trust split is essential: supplied coefficient and whitening intervals are numerical premises; the fast checker alone would not reject every newly fabricated but self-consistent premise. Regeneration connects them to the differential model.

## 4. Executed checks and limits

Fresh audit commands:

```sh
/private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/five_paths_2026_09/path5_resolution -p test_resolution.py -v
python3 research/five_paths_2026_09/path5_resolution/check_certificate.py
```

Results: **16/16 tests passed**; exact checker passed all three metrics. Certified finite floors remain approximately1.1764481493e-7 (L2),1.2928209881e-9 (declared H1), and1.3728294274e-9 (natural discrete H1). The fresh signed-measure, common-core, metric-product and source-hash checks described above also passed.

No target-placement robustness, increasing source bandwidth, minimal resolution, local sensor hardware implementation, or all-time finite-grid statement follows. In particular, at fixed n every retained positive target mode eventually decays exponentially, while the normalized continuum Gram retains its common-core floor. A fixed grid therefore cannot inherit a positive continuum floor uniformly for all late times. The appendix correctly records that informative limitation.
