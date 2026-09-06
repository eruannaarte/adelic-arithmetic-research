# Independent audit of quadratic cycles Q1–Q3

Auditor: preparation/dynamics agent, independently of this producer. **Verdict:** Q1's exact finite-prefix minima, Q2's nonattained infinite infimum, and Q3's conditional finite-sensor guarantees are supported by the stated premises and proofs. All fourteen current tests and all three standard-library checkers pass. A missing term in Q2's final approximation-gap sentence and an executable certificate-validation gap in Q3 were identified and repaired. No certificate values required changing.

## Q1: finite arithmetic geometry and genuine witnesses

I independently checked the lower-bound decomposition in [PROOFS.md](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/quadratic/PROOFS.md:5). Any change at prime2 or3 costs at least1/81 in the squared normalized metric, more than any claimed minimum. With those coordinates equal, the local Euler factors force equal positive a(4),a(9), each at least1, and differences at20 and45 equal these multipliers times the query difference. The25 coefficient distinguishes query2 from0/1. All other metric contributions are nonnegative, so there is no omitted-coordinate cancellation.

The three all-inert-except5 patterns attain these bounds: through50, only coordinates5,20,25,45 can differ. The finite CRT/Dirichlet theorem has the needed hypotheses and no discriminant ceiling; in particular, it does not claim one field realizes an infinite sign prescription. The resulting prefix set is finite even though each prefix has infinitely many field realizations, so a minimizing pair exists. Its normalized midpoint proves failure for closed noise balls at the finite critical radius.

I separately verified all **38 recursive Lucas prime nodes**, bottom-up, using Python integer factor products, modular powers, and gcds rather than `geometry.check_prime`. Complete n−1 factorization and certified factor primality establish the order criterion; this is a proof of primality, not a probable-prime declaration. As a negative control,341 passes the base2 Fermat congruence but fails the required gcd/order condition.

For each recorded discriminant35473497127622875037,12470811778107064205,9894082171941632381, I independently evaluated the Kronecker character using binary Jacobi reciprocity, handling the power of2 separately, then formed every coefficient by the divisor sum `a(n)=sum_(d|n) chi_D(d)`. All150 resulting coefficients agreed with the saved prefixes. The certified auxiliary primes, R in{1,5}, and D≡5 mod8 prove positivity, squarefreeness, and the correct fundamental-discriminant convention. Thus the minimizing points really are quadratic-field data.

The checker does not verify the descriptive CRT residue/modulus fields, but the prime/discriminant/symbol/prefix checks independently establish every witness property needed for attainment. This does not leave a gap in the minimum theorem. It should not be described as a general checker of every stored metadata field.

## Q2: infinite separation, strictness, and endpoint topology

The decisive support set simplifies to `E={5m²:m>=1}`. The stated odd-5-power representation is unique, and its normalized squared weight is zeta(8)/625. I checked the equality of these descriptions explicitly through10^6 (447 integers), in addition to deriving it algebraically.

At every prime, coefficients at even exponents are positive odd integers. Consequently query0 gives zero on E, query1 gives an odd positive value, and query2 an even positive value. This proves a universal unit gap on E even when the two fields have different splitting patterns elsewhere. Query0 versus2 gives at least twice that gap; query1 versus2 has the additional forced gap2 at25. Neither pair can attain the global infimum.

For query0 versus1, the split-prime argument is valid: if d>1 is squarefree and p divides100d−1, then p is odd, p≠5, p does not divide d, and `(10d)^2=d mod p` is a nonzero square. Thus p splits. At5p² the ramified-at5 field has coefficient3, versus0 in the inert-at5 field. This forces strict excess over the putative infimum. For the actual query1 witness in Q1, independent factor discovery followed by trial-division primality verification gives p=233 and coordinate271445; its squared excess alone is at least8/5429094305066663400625.

The formal limiting sequences are not fields, precisely because they have no split prime. Finite CRT/Dirichlet approximants are actual fields, and the tail estimate proves convergence. The estimate uses `|a_K-a_L|<=d2`, not an unnecessary factor2: both coefficients lie in[0,d2]. The exact prime-power identity `d4(p^e)-d2(p^e)^2=(e+1)e(e-1)/6` is nonnegative for every integer e>=0. Multiplicativity, absolute Dirichlet convolution, and zeta(2)<2 justify the complete tail bound16/N². This also places all response sequences in the declared Hilbert space.

The endpoint conclusion is correct for the explicitly stated meaning of recovery: uniqueness on promised full-sequence observations. Every actual unequal-label pair has distance strictly greater than delta, so closed balls of radius delta/2 remain disjoint. This is not an efficient-decoder or finite-physical-sensor assertion. Above that radius, actual approximants supply a midpoint collision.

**Repair confirmed.** The original final sentence only required16/N²<(2eta)², omitting the baseline squared distance. It now correctly requires `16/N²<(2eta)²-delta²`, whose right side is positive. No numerical artifact changed.

I independently bracketed zeta(8) using200 terms and integral remainder bounds. This stronger interval lies inside the saved100-term interval, and its squared critical-radius enclosure fits the saved rational square-root bracket. The resulting critical radius is approximately0.02004073208441193. An elementary nonattainment control, centers−1−1/k and1+1/k, confirms why closed radius1 balls remain disjoint even though their distance infimum is2; centers−1 and1 show the contrasting attained finite endpoint.

## Validation and limits

At the Q1/Q2 audit stage, fresh commands were `python -m unittest discover -s research/next15_2026_09/quadratic -p 'test_*.py' -v`, `python -S .../geometry.py`, and `python -S .../infinite_geometry.py`, using the prepared runtime. All eight tests and both exact checkers passed. The independent arithmetic checks above used separate implementations; numerical decimal summaries were not decision inputs.

Q1 and Q2 use normalized coefficient metrics. Their sharpness is not automatically a sharp bound for the8900-reading zeta observation operator. Q2's infinitude relies on the cited Dirichlet progression theorem with its coprimality hypotheses; finite witness enumeration alone cannot replace that input. The small rational checker instantiates the analytic infinite result rather than proving the limit by finite testing. These distinctions are correctly maintained in the current proof.

## Q3: actual finite-sensor conditional recovery

I read the appended Q3 theorem, the complete inherited Path4 tail proof and checker, `conditional_query.py`, its certificate, and all interface controls. This cycle correctly returns to the actual8900-reading weighted zeta sensor; it does not import Q1/Q2's coefficient-metric threshold into that sensor.

The seven retained indices are exactly5m<=50 with m2,3-smooth and coprime to5. Their coefficients are linear in a(5), with multipliers obtained from the correctly recovered a(2),a(3) and their local prime-power recurrences. The45 coordinate uses a(9); the40 coordinate uses a(8); the30 coordinate uses coprime multiplicativity a(2)a(3). No unknown a(7) or nonlinear a(25) relation is silently assumed.

I independently reconstructed all nine rational multiplier vectors, J values, weights, bias bounds, and radii from the raw complete-tail and Gram-row vectors, rather than trusting the stored final consequences. The unbiased identity and Cauchy–Schwarz optimum are exact. The weighted noise calculation correctly uses `v*G^-1 v`, with the same reused readings and one positive weight matrix W; it does not treat nested observations as independent. The norm of the real final query is bounded by the complex weighted operator norm, so passing to real parts and integer rounding is valid.

Every declared noise radius passes both anchor inequalities. In particular, the largest declared radius0.02324 uses only0.175132225 of the squared global anchor allowance. Thus anchors can be certified before choosing a stratum: the selection is not circular, and no statistical independence or union-probability assumption is needed. When the supplied budget exceeds the recovered stratum's certified radius, the decoder abstains. The result remains conditional; it does not promise the best radius uniformly over all fields.

For a(2)=a(3)=2, the independently recomputed squared gain exceeds `(1.1421)^2`, proving the advertised greater-than14.21% improvement over the original three-coordinate bound in the *same stratum* and under identical source/tail/Gram premises. For a(2)=a(3)=0 the new squared gain is exactly1. The new linear combination minimizes the stated Euclidean/Neumann noise bound, not the exact Gram-dependent gain or a joint bias/noise objective; the proof correctly restricts its optimality claim.

### Source binding and executable repair

The inherited source's independent standard-library checker passed afresh. It verifies the source class, exact measurement sizes, positive normalized window, complete remote tail using rational logarithm/pi/sine inequalities, vector lengths, finite-plus-remote composition, and baseline inverse-tail consequences. The saved `base_tail_replay.json` equals the original source document exactly. I verified that equality, but did **not** repeat the497500-term Arb producer run in this audit; the freshly recorded replay remains the finite-tail/Gram enclosure dependency.

The original `decode()` function did not call the certificate checker. A concrete regression supplied an exact realizable query1 coefficient prefix with a forged zero weight vector and obtained false label0, while a separate `check()` invocation correctly rejected the same certificate. The final-decision function therefore needed an enforced checked-input contract, not just a standalone verifier nearby.

With the root author's authorization, I repaired only `conditional_query.py` and its focused tests. The [decoder](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/quadratic/conditional_query.py:117) now validates the provided certificate before any stratum lookup. The [source reader](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/quadratic/conditional_query.py:18) reads immutable bytes and parses a fresh document on every call; it invokes the inherited checker for each new content digest and caches only verified digests. Returned mutable documents are never cached. The inherited checker still treats the finite/Gram outward vectors as separately replayed premises; the cache does not turn their hashes into mathematical proofs.

Two new tests reject direct forged-weight/budget decoding, prove that mutating a returned source document cannot poison a later read, and reject a changed remote endpoint or source class in fresh source bytes. Canonical certificate artifacts and all quantitative bounds are unchanged.

### Final validation and interface limits

The full quadratic suite now passes **14 tests** in1.287 seconds: four Q1, four Q2, and six Q3 tests. All three checkers run successfully with `python -S`, including the inherited rational checker reached by Q3. The existing full-grid interface test forms the actual8900-row complex design and combined reused-grid weights, measures all nine query gains, and tests worst-direction sensor noise on27 finite-part controls. Those are interface diagnostics; the full-field guarantee still uses the complete infinite tail theorem.

The last rational combination and rounding add no floating-point error, but the upstream complex sensing inverse is an exact mathematical operator in the theorem. Any numerical implementation error before that final decision must fit the stated observation/coefficient error contract. Neither finite-part simulations nor conversion of binary floating values to Fractions certifies that upstream error automatically. This limitation is explicit and must remain in summaries of the implementation.
