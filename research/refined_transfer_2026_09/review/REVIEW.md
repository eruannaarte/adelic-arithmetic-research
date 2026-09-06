# Independent mathematical and computational review

The normalization wrapper, seven-row transfer and weighted sinusoidal drift
extension fit the unchanged transfer theorem. No mathematical blocker was found
in the reviewed proof contracts and code. This review is a second-agent audit,
not external peer review or an assertion of historical novelty.

Five executable reviews use different controls from the primary implementations:

| Review | Independent evidence |
|---|---|
| [Normalization lemma](normalization_review.py) | 130 exact inverse-root enclosures; both closed budget endpoints and adjacent failures; explicit counterexamples to charging a normalized error as a physical error and to omitting sensor error from the gain. |
| [Normalization implementation](normalization_implementation_review.py) | 15 homogeneity cases over 200 decimal orders of amplitude; eight receipt corruptions and seven additional data/domain/budget refusals; rational-root zero-budget case. |
| [Weighted approximation](weighted_moment_review.py) | Fresh physical cosine weights and 320-bit moment quadratic forms verify all 24 rational polynomial residual bounds and six complete weighted Taylor moments; exact parity validates the arbitrary-phase bound. |
| [Seven-row point floors](seven_point_review.py) | Direct polynomial power sums and outward 320-bit LDL pivots certify ten physical approximate-map point floors, including the narrow source case at time one and endpoints/centers of the deepest certificate cells. |
| [Raw physical fixtures](raw_fixture_review.py) | All 72 exact raw vectors are reconstructed independently; generation and decoding quartic bounds, actual finite-model sensor promises, profile/data bindings and exact least-squares source-error enclosures are checked. |

The seven-row source gate has the exact squared-error fraction
\(332928/333925<1\) of its \(0.001\) target. Its pair gate uses
\(166464/225625<1\) of the certified squared separation floor. These are strict
gates despite the narrow source margin. The ten extra point checks are
additional evidence only; the full-time theorem requires all 231 case-specific
covers and the complete model errors, verified by the main consumer.

The weighted family bound applies to every real phase and
\(|\omega|\le1\) because the drift remainder splits into exactly orthogonal
odd and even vectors under the physical even weights. Its norm is therefore
bounded by the larger parity bound. A triangle inequality by itself would not
justify that maximum. The rational polynomial approximants are verified by
their actual norm residuals; no unproved best-approximation or projection
optimality premise is needed. The final sine/cosine Taylor remainders cover
every omitted term through the weighted \(x^{21}\) and \(x^{22}\) bounds.

The delivered arithmetic demonstration also retains the complete arithmetic
tail, data-dependent normal residual and joint sensor/drift/digitization
budget. Its comparison with pointwise Taylor is a certified improvement in the
sufficient drift allowance, not a claim of failure of every decoder that uses
the previous readings. A physical drift-family premise remains external to
the normal residual.

Both code-review notes were addressed and checked. The secondary arithmetic
consequence consumer explicitly rejects a negative claimed residual and a
nonpositive Gram floor. The normalization wrapper returns its source-accuracy
statement only when the decision is unique; otherwise that field is null.

The final raw-fixture audit proves the actual sensor promise, rather than only
comparing the fixture to the polynomial surrogate. Its raw vector is
\(y=P_j u/r_g+d\), where \(\|d\|_2=\eta\|u\|_2/4\). The verified scalar
bound \(|\alpha r_g-1|\le e_g\), complete physical map error \(\rho\), and
derived bound \(\|P_j\|<2\) give

\[
\|y-A_ju\|_2\le
\left(\rho+2e_g/r_g+\eta/4\right)\|u\|_2
<\eta\|u\|_S.
\]

Every inequality and raw-vector equality is checked exactly in all 72 cases.
The additional source-error scan recomputes the ordinary least-squares estimate
with direct polynomial power evaluation, independently of the delivered
decoder. All published squared-error upper bounds enclose those errors and
remain below their stated accuracy targets. For H1, using
\(41\|\widehat u-u\|_2^2/\|u\|_2^2\) is a valid upper bound because
\(I\preceq S\preceq41I\).

The common adapter's specialization was also reviewed: its 3,391 whole-cell
gates, two global spatial gates, 98 integer gates and 18 actual-normalization
charge gates correctly specialize the unchanged transfer predicates. The 72
packet validations are counted separately. All 15 bound inputs in the saved
3,509-gate receipt matched their recorded hashes at final review; the adapter
still relies on the explicitly separate physical-model and residual replays.

To reproduce the independent checks from the project root:

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/review/normalization_review.py
PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/review/normalization_implementation_review.py
PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/review/weighted_moment_review.py
PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/review/seven_point_review.py
PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/review/raw_fixture_review.py
```

Each command is read-only and emits a JSON receipt. Saved results with the same
base filename document this review. The scripts do not import the weighted
approximation producer or consumer, and the seven-row point review does not
import either spatial certificate implementation.
