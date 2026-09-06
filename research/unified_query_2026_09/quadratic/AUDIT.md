# Independent audit: joint quadratic query

Auditor: the resolution/sensing-bank agent, independently of the quadratic producer. I reviewed the final proof and decoder, reconstructed the actual arithmetic with a separate implementation, checked every pair and guarantee, ran the focused tests, and verified the physical sensor's directional noise map. **Verdict: the conditional query guarantees, complete-tail accounting, realizability, and abstaining decoder are supported. No unresolved mathematical or implementation defect was found.**

One reporting sentence was corrected during review: the quoted gains are computed from **square roots** of exact squared-radius ratios. The table's numbers already used that convention; neither the certificate nor its numerical values changed. The largest radius gain is 0.4001361741%, and the all-split radius gain is 0.3560860567%.

## Arithmetic coverage and explicit actual fields

The 16 selected indices are exactly those at most 50 supported on primes 2, 3, 5, 7 that contain a factor 5 or 7. For fixed $a(2),a(3)$, the nine possibilities for $a(5),a(7)$ exhaust their coefficients by the quadratic Euler factors and coprime multiplicativity. The formulas for $a(25)$, $a(49)$, $a(35)$, and $a(50)$ are consistent, including ramified and inert cases.

The proof's finite-prime CRT/Dirichlet construction handles the prime 2 separately and produces positive fundamental discriminants. I also supplied an entirely finite existence check: **all 81 patterns occur among explicitly verified fundamental discriminants no larger than 1,365**. The independent implementation trial-divides the squarefree radicand, forms its correct positive fundamental discriminant, evaluates its quadratic character, and computes coefficients by the divisor sum
\[
a_D(n)=\sum_{d\mid n}\chi_D(d).
\]
This is independent of the producer's product of local prime-power sums. The resulting full 50-term prefixes reproduce every one of the 81 selected templates.

The witnesses, exact factorizations, and coefficient prefixes are recorded in [audit_independent.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/quadratic/audit_independent.json). That explicit finite table is sufficient for the realizability claim used here. It does not assume that an infinite all-inert formal pattern is a number field.

## Pair radii and noncircular query logic

The inherited inverse estimates normalized coefficients $a(n)/n^2$. Reconstructing the full-tail support directly from the source vectors gives
\[
b_n=\tau_n+q_n\max_m\tau_m/(1-q).
\]
For the real direction $\Delta=c_i-c_j$, the support function of that coordinate enclosure is $h=\sum|\Delta_n|b_n$. The exact sensor map has weighted dual squared norm $\Delta^*G^{-1}\Delta$, bounded by $S/(1-q)$ with $S=\|\Delta\|^2$. The expression
\[
R_{ij}^2=(1-q)(S/2-h)^2/S
\]
therefore follows from separating the two directional slabs; the code verifies $S>2h$ before forming it. All 27 unordered unequal-query pairs per anchor, hence all **243** pair directions, are present.

The classifier includes a template if it passes every slab incident to that template. Under the input contract, the actual template satisfies all its slabs, independently of whether its sufficient uniform radius is met. If the noise radius is below the actual template's minimum pair radius, every template with a different $a(5)$ fails its separating slab. Templates with another $a(7)$ but the same query may remain. The algorithm consequently does not need to identify $a(7)$ or look up a budget from an unknown true template.

The performance theorem is properly conditional on the actual template, while the algorithm's validity is unconditional within the admitted model and certified anchors. This is not a claim that all fields enjoy the largest conditional radius. The inert-$7$, query-$0/1$ pair reproduces the old Q3 radius exactly in every anchor stratum, so the unchanged worst-case conclusion follows from an explicit equality.

The anchors use the same physical noise vector as the query, rather than separate budgets. The largest declared squared radius is only **0.176463** times the globally sufficient anchor squared radius. Thus the anchor step does not assume an unproved noise reduction or an unknown query value. The supplied code checks the anchor bound directly before rounding.

## Decoder, numerical error, and returned sets

The **answer_set** function returns an outer set of possible query labels. A singleton certifies the answer. An empty set signals that the supplied values and declared model/error contract are inconsistent; **decode** never turns it into an answer. **None** denotes inability to certify the anchors. These distinct states are correctly implemented and independently exercised.

A supplied absolute coefficient error $\nu_n$ is divided by $n^2$ before it is added to the normalized anchor error and the directional support. This is the correct scaling. The canonical table assumes the exact mathematical sensing inverse. Converting a floating estimate to a rational only fixes its stored value; it does not prove zero upstream numerical error. The final proof states that limitation.

Direct decoder calls verify the entire source-bound certificate before making a decision. The final implementation compares JSON types recursively, rejecting bool/int substitutions, and checks local arithmetic argument types and domains. No scientific radius changed during that hardening.

## Executed independent checks

- The new exact audit implementation does **not** call the producer's build function. It invokes the inherited sensor contract checker, independently forms all character/divisor-sum templates, recomputes all 243 pairs, verifies all 81 sufficient radii and prior-Q3 comparisons, and checks every strict anchor inequality. All checks passed.
- All **seven focused tests passed**, including actual-grid worst-direction propagation, ambiguity preservation, direct-decoder certificate tampering, and numerical-error accounting. The suite was rerun after the final input-type hardening.
- On the actual 8,900-row physical grid, I independently formed the combined reused-window weights, $\Phi$, $G$, and the weighted inverse. Every one of the **243** pair dual gains obeyed its certified bound; the largest actual-to-certified squared-gain ratio was below **0.999245**. The direct row calculation $\sum_j|(\Delta^*K)_j|^2/w_j$ agreed with $\Delta^*G^{-1}\Delta$.
- I independently checked the iid covariance identity $KK^*=G^{-1}\Phi^*W^2\Phi G^{-1}$ and the positive reused inner/outer cross term. These are physical-map controls; the theorem itself assumes a deterministic weighted noise ball and no statistical distribution.
- All **81 explicit actual-field prefixes** passed the public decoder at their declared template radii. This is a template/interface check on genuine field coefficients, not a fresh evaluation of 81 full zeta sample vectors. The complete full-field sensing guarantee still uses the inherited infinite-tail certificate.
- Additional controls produced an empty outer set from incompatible large coefficients, distinct anchor abstention at an oversized noise radius, and enlarged survivor sets after adding numerical uncertainty while keeping the anchor proof available.

## Scope and trust boundary

The common noise support, complete arithmetic tails, and same physical acquisition are retained. The new calculations are exact finite consequences of the previously audited Gram and finite-plus-remote tail enclosures. Those original numerical enclosures have the recorded full-model replay in the earlier package; this audit rechecked their mathematical contracts and all new consequences, without rerunning unchanged expensive tail production.

The result is a modest conditional improvement in a sufficient physical-sensor certificate. It does not give a sharp minimax threshold, a statistical advantage under arbitrary covariance, a proof that all methods fail to recover $a(7)$ at the quoted noise, or hardware validation. The finite answer-set construction, actual-field realization, and explicit worst-case equality support the more limited claims in the final report.
