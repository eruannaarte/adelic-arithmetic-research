# Independent review of the common application adapter

Status: **PASS for the inspected noise adapter, retained three-model reconstruction, and the framework/arithmetic portions of the root report.** This bounded review does not audit the new spatial operator proof or its quantitative claims; that review is being conducted separately. No scientific code change was required.

The reviewer inspected `applications.py`, the called scalar and residual functions in `transfer.py`, both old and new noise certificate contracts, the prior centered no-drift evidence, and the current root `REPORT.md`. The review checks the mathematical mapping of already verified model premises to the common theorem; it is not another independent reconstruction of the noise producer authored by this reviewer. The new physical-tail package is under a separate agent's independent audit.

## New arithmetic mapping

Before using a record, `check_new_noise` invokes the strict native consumer with the matching core/extended evidence mode. Thus the complete arithmetic and nuisance-tail consequences, source normalization, physical acquisition and digital correction contract are checked first.

For coefficient index n, the verified native bias is A_n, and the augmented Gram floor is f=1-q>0. The scalar output of interest is the actual integer a(n), so the spacing is one and the absolute-error enclosure has radius

    A_n + n^2(eta+Xi)/sqrt(f).

The common adapter correctly supplies `distance=1`, `support_sum=2*A_n`, `gain_squared=n^4/f`, and `radius=eta+Xi`. The common formula consequently returns

    (1-2*A_n)^2 / (4*n^4/f) = (1/2-A_n)^2*f/n^4.

The sign check is retained before squaring. The minimum over n=2,...,50 is exactly equal to the native `sufficient_total_noise_radius_squared` in every case. The constant coordinate is properly omitted: a(1)=1 is supplied, while its fitted constant is combined with unrestricted constant drift. No imaginary integer label or unnormalised Fourier coefficient is substituted for the requested a(n).

For a verified exact physical normal residual of Euclidean norm at most rho, the augmented coefficient-vector error is at most rho/f. Rescaling its n-th coordinate gives n^2*rho/f. The adapter calls `normal_residual_error_bound(f,rho)` and multiplies by n^2, then adds this amount to the one-sided bias before doubling the support sum. This is the correct inverse-Gram gain. It is distinct from the physical observation-error gain n^2/sqrt(f). It does not double count the digital error and does not silently charge the residual as if it were sensor noise.

The imported rho=1/10^8 is conditional on certified evaluation of the exact physical normal equations. The native consumer verifies all corresponding margins; neither the common adapter nor the report represents a floating residual as such a certificate. A merely close approximate nuisance projector remains insufficient under unrestricted drift amplitudes.

## Previous models and coverage

The quadratic adapter uses squared center distance s, the native complete directional support h from each side, and gain squared s/(1-q). Its common boundary is the same exact rational native pair boundary.

The older polynomial adapter applies the same integer-coordinate normalization and explicitly includes its inherited midpoint error. Only certified native degree cases are counted. For preparation, the adapter uses the row contraction, actual projected local and shared uncertainty gains, target diameter, and weighted readout gain. The saved case lies strictly inside the valid diameter boundary. Its strict interior check does not alter the underlying theorem's non-strict allowed endpoint.

The following command was run successfully during this review:

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/transfer_theorem_2026_09/framework/applications.py --extended-noise
```

It checks 243 earlier quadratic pairs, 441 earlier polynomial coordinates and 3 preparation rows: **687** inherited scalar gates. The new table contains 2 designs × 4 degrees × 49 unknowns = **392** rounding gates and **392** additional conditional normal-residual gates. These are application inequalities within the proved theorems, not separate new theorems or empirical trials.

## Root report and comparison scope

The table agrees with the exact new evidence: multiscale degree six/eight at 10^-4 and degree ten/twelve at 9.9*10^-5; outer degree six/eight/ten at 8*10^-5 and twelve at 7.9*10^-5. The earlier centered no-drift allowances were checked directly against `research/next15_2026_09/noise/cycle2_evidence.json`; they are indeed 10^-4 and 8*10^-5. The predecessor quintic multiscale allowance is 1.6*10^-5. The known-a(1) hypothesis in the polynomial theorem remains explicit; the report compares declared noise allowances, not identical nuisance/prior information in the earlier no-drift problem.

The physical readings and each design's weight vector are unchanged. The two columns retain their respective W-balls and do not imply an unspecified common random-noise comparison. The report correctly distinguishes sharper sufficient tail enclosures from increased physical information or a sharp degree/noise optimum. All new complete bias figures are rounded upward. The old failed sufficient degree-six gate is not called an impossibility theorem.

Three wording clarifications were made directly in the root report: the profiled cost is the **squared norm** of the relevant projection; the finite band consists of frequencies **log(n)** for indices 51 through 10^12; and the report now lists the exact 687+392+392 gate coverage and conditional residual allowance explicitly. These changes do not alter any scientific result. The root reproduction guide was not yet present at the time of this bounded review.
