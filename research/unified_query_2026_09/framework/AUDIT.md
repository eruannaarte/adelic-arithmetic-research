# Independent audit of the answer-set framework

Auditor: `/root/polynomial_drift`, 2026-09-05. **Verdict: the framework's mathematical statements and directional checker are sound within their stated domains.** I independently reviewed the full proofs rather than relying on the six tests. One notation clarification was made in the polynomial application: its common radius must include the rational correction error, so the specialization now explicitly uses \(\eta_{\rm total}=\eta+\xi\). The actual noise certificate already charged that error; no numerical conclusion changed.

## Exact answer sets and deterministic minimax recovery

The exact-discrete criterion is both necessary and sufficient for arbitrary decoders on promised observations. Shared nuisance variables remain coordinates of the joint admissible set. The singleton construction establishes existence only; the text correctly excludes automatic measurability or computational feasibility.

For a bounded nonempty query set in a finite-dimensional normed space, the supremum-distance function is finite, 1-Lipschitz and coercive after fixing any member of the set. Thus it attains a minimum on a compact ball even if the query set itself is not closed. Choosing such a center for each promised observation proves the matching minimax upper bound; the pointwise radius gives the lower bound. Unbounded sets and unbounded suprema have infinite risk. The distinction between radius and half-diameter is necessary: the supplied equilateral-triangle example correctly prevents an invalid generic factor-of-two inference. No infinite-dimensional center-existence assertion is made.

## Transfer and exact quotient hypotheses

Observation-set containment directly yields query-set containment. Composition is valid only after mapping the earlier uncertainty sets through the later transformation. The framework explicitly includes numerical preprocessing errors and does not add scalar radii before matching spaces and norms. Relaxing a correlated uncertainty set to a larger product is conservative; replacing it by a smaller or incorrectly independent set need not be. The text correctly distinguishes multiple outer answers from actual ambiguity and treats an empty set as rejection of the promised contract.

The nuisance quotient is an exact equivalence under its actual hypotheses: finite-dimensional positive-definite metric, one fixed nuisance range, an unrestricted nuisance coefficient independently available for every admissible source and structured nuisance state, and a full weighted noise ball. The reverse direction constructs the projected residual as noise and the complementary residual as an allowed nuisance. Bounded or source-correlated structured variables may remain inside the nonlinear source map; union must be over their actual incidence set. Full column rank of the nuisance matrix is unnecessary because only its range is used. The caveats about source-dependent nuisance matrices, bounded nuisance, row restriction and the corresponding noise metric are correct.

As an independent exact control, I checked 25 rational residuals with \(W=\operatorname{diag}(1,4)\) and nuisance range \(\operatorname{span}(1,1)\). The proper complementary projector is

\[
P=\begin{pmatrix}4/5&-4/5\\-1/5&1/5\end{pmatrix},\qquad
\|Py\|_W^2=\tfrac45(y_1-y_2)^2.
\]

Every projected residual was contractive and orthogonal in \(W\), with a complementary residual in the nuisance range. The ordinary Euclidean projector gives \((1/2,-1/2)\) from \((1,0)\), increasing the \(W\)-norm squared from 1 to \(5/4\). This demonstrates why the actual metric in the lifting theorem is essential.

## Directional certificate and common applications

The slab bounds follow from the two one-sided support bounds and one dual norm for the actual composed noise map. For orientation \(\ell(c_i-c_j)>0\), the relevant gap is the negative support at template \(i\) plus the positive support at template \(j\). The order in the displayed asymmetric formula is correct. A strict support gap is required before squaring, and the zero-gain case is treated separately. Slabs are closed, so equality at their touching boundary is retained as ambiguity rather than incorrectly certified separation.

The callable checker restricts to nonnegative support upper bounds, a conservative valid subcase of the general support statement. It uses exact rational arithmetic and correctly handles the two sides of a slab, zero noise gain, and closed endpoints. I independently checked 104 asymmetric scalar cases, including exact touching endpoints. In the scalar interval model these cases attain the computed boundary, so the checks exercise the one-sided orientation as well as the strict/non-strict distinction.

The quadratic instantiation uses the full normalized difference vector: \(d=S\), support \(h\), and squared gain \(S/(1-q_G)\). Substitution yields exactly \((1-q_G)(S/2-h)^2/S\). The polynomial instantiation uses separation one, symmetric complete coefficient bias, and squared gain \(n^4/(1-Q_p)\); the common gate is applied to \(\eta+\xi\), not merely the sensor radius. These are valid instances of the same directional theorem while retaining different source classes and observation metrics. The broader nonlinear preparation and finite-resolution transfers need their separately supplied model-to-enclosure proofs; the framework does not replace those proofs with generic terminology.

## Centering, endpoints and cost claims

A known deterministic translation is a bijection of the observation space. Transporting observation sets and decoders proves preservation of the exact answer sets and minimax risk. Consequently the prior factor greater than 127 describes a certified decoder/noise allowance; it is not an increase of intrinsic information from subtracting a known vector. The correction's own numerical error must still be charged. The framework states this distinction explicitly.

For equal-radius closed balls in a normed vector space, the midpoint proves overlap exactly when two actual centers are at distance at most twice the radius. Thus when the unequal-query distance infimum equals twice the noise radius, attainment determines failure. A nonattained endpoint can remain identifiable, without implying a computable decoder or a positive uniform slack. Replacing the actual source class by a closure can introduce new pairs and change this endpoint result. The approximation transfer using the sum of two source-error bounds is a sufficient triangle-inequality statement, correctly distinguished from a sharp boundary.

The resource discussion also respects these directions: a successful uniform outer certificate gives a feasible design and an upper cost bound; an exact collision gives an obstruction; a failed sufficient bound gives neither. Invertible processing, nuisance quotients with lifting, and irreversible row restriction have different roles and are not conflated.

## Executed checks and scope

All six directional tests passed under `python -S`. The additional exact quotient and asymmetric-support controls are recorded in [independent_audit_checks.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/framework/independent_audit_checks.json). The central conclusion rests on the reviewed proofs; these finite controls corroborate the implemented algebra. Model-derived supports and gains are certified in the application packages, and arbitrary caller-supplied bounds would give only a conditional algebraic statement.

No claim of historical novelty for the general optimal-recovery, support-function or quotient arguments is needed. Their useful role here is to state the common hypotheses precisely and transfer guarantees without discarding arithmetic realizability, shared uncertainty, physical noise geometry, or complete approximation errors.

## Follow-up: shared checker for three models

I independently reviewed the added [check_applications.py](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/framework/check_applications.py) and the nonlinear-preparation specialization. The adapter first invokes the actual model checkers; its scalar inputs are therefore tied to the checked application certificates rather than supplied arbitrarily. The standalone standard-library run passes **687 scalar gates across three models**.

For all 243 quadratic pairs, it maps the squared normalized template difference to separation \(S\), assigns the complete directional tail support \(h\) on both relevant sides, and uses squared physical gain \(S/(1-q_G)\). Exact comparison reproduces the original pair radius. It neither substitutes independent decoded-coordinate noise nor changes the units of the tail supports.

For the 441 polynomial coordinate gates, the 49 unknown indices across nine certified design/degree combinations map to separation one, complete coefficient bias \(A_n\) on both sides, and squared gain \(n^4/(1-Q_p)\). The adapter explicitly adds the fixed digital correction radius before testing the strict inequality. It verifies that the minimum common-function radius equals the saved complete all-coordinate radius. The unreported constant coefficient is correctly excluded, and failed sufficient design/degree cases are not promoted into passing claims.

For preparation, the adapter reconstructs \(h_i\) from the local and common widths and their projected gains; measured center offsets are not incorrectly charged as uncertainty widths. It maps separation to \(\Delta(1-k_i)\), both supports to \(h_i\), and squared gain to \(c_i^2\). The resulting squared radius is exactly the square of \([\Delta(1-k_i)/2-h_i]/c_i\). The positive-gap check is satisfied for the saved interior fixture, so taking that positive root is justified. The minimum of these three roots exactly reproduces the bridge's fixed noise boundary.

The appended nonlinear proof also gives the correct endpoint semantics. If a source pair had infinity distance \(M>\Delta\), an attaining coordinate would satisfy \((1-k_i)M\le2h_i+2\eta c_i\). The certified non-strict bound \(2h_i+2\eta c_i\le(1-k_i)\Delta\) contradicts this. Thus equality at the noise boundary still certifies diameter at most \(\Delta\); unlike integer rounding, it does not require strict separation at \(\Delta\). I checked the exact saved preparation boundary independently: row zero is equal in both the original affine inequality and the adapter's squared gate, the other two rows have slack, and increasing the radius by \(10^{-15}\) fails a gate. The adapter's `>` rejection for preparation and `>=` rejection for polynomial rounding reflect this distinction correctly.

No further mathematical issue was found. This adapter establishes a shared algebraic verification route; it does not create 687 independent theorems or replace the separately reviewed physical-model and complete-tail premises.
