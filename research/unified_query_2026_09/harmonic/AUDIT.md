# Independent audit: uniform harmonic collision family

Auditor: the resolution/sensing-bank agent, independently of the harmonic producer. I reviewed the complete parameterized-contraction proof, both original-model reconstructions, coordinate conventions, exported certificate gates, query consequences, and tests. I also performed separate rational source-box and all-vertex calculations. **Verdict: the open family of nonidentifying schedules and its scalar/bit query obstructions are supported. No unresolved mathematical or implementation defect was found.**

## Uniform existence, rather than a point root

The active system has 12 real coordinates and 12 real equations, with six other source-pair coordinates frozen. The residual ordering, six real rows followed by six imaginary rows, matches both Jacobians. The exact rational preconditioner and predictor are proposals whose consequences are rebuilt from the model; an approximate inverse or near-zero point residual is not treated as a proof.

The moving center is $C(\delta)=x_0+P\delta$. The implemented source-center enclosure has radius $\epsilon\sum_j|P_{ij}|$ in each active coordinate, and the root enclosure adds $\rho$. These rectangles contain every correlated moving center and every translated root box. They deliberately permit additional coordinate combinations, which enlarges the interval enclosure without invalidating it.

The crucial center residual is bounded through the full chain derivative
\[
R(D_xf\,P+D_tf)
\]
over the complete center/time rectangle. Integrating along $s\mapsto(C(s\delta),t_0+s\delta)$ gives $e_0+\epsilon M$. The code includes both terms; it does not replace the moving-center residual by the point residual or omit the time Taylor effect.

On the full root/time rectangle, $\|I-RD_xf\|_\infty\le L<1$. For each fixed time vector, this makes the map on the common deviation box a contraction. The strict inequality $e+L\rho<\rho$ gives a self-map of a complete closed box. The contraction argument proves an actual fixed point, not merely a small residual. Because $RD_xf$ is invertible by its Neumann series, the square matrix $R$ is invertible, so a fixed point of the preconditioned map is an exact zero of the original residual.

The quantifiers are correctly stated as **for every time vector there exists a source pair**, with the pair allowed to depend on the time. Local uniqueness is within the particular moving active-coordinate box. The result does not claim one fixed pair works at every time or that all schedules below 30 fail.

## Branch regularity and the query

The branch derivative bound uses the **full root rectangle**, rather than the smaller center rectangle used for the initial residual. For a fixed deviation $y$, the parameter chord between $C(\delta)+y$ and $C(\gamma)+y$ stays in that full rectangle. Comparing the two contraction fixed points then gives
\[
\|y(\delta)-y(\gamma)\|_\infty
\le \frac{B}{1-L}\|\delta-\gamma\|_\infty.
\]
Adding the affine predictor term supplies the reported complement-coordinate branch Lipschitz bound. Its norm is for all 18 complement coordinates of the pair; it is not silently converted to a Euclidean probability-factor norm.

Indices 3 and 12 are the exponent-one probabilities in the prime-3 factors of the two sources. Neither belongs to the active list. Their difference is therefore exactly
\[
0.63280942665025819-0.083208071567702588
=0.549601355082555602
\]
at every certified root. They lie on opposite sides of one half. At their common observation, any deterministic estimator gives the same value for both possibilities, so the triangle inequality forces worst-case absolute error at least half the gap. This establishes an actual continuous-query obstruction and an unrecoverable bit query even without noise.

## Model-to-interval connection

In the factored response, differentiation of an exponent-one/two/three complement coordinate correctly changes the factor by $E_a-1$, because its exponent-zero probability changes by the negative of that coordinate. The time derivative differentiates every factor and affects only the corresponding reading's real and imaginary rows.

The independent reconstruction expands all 64 integer labels, differentiates their probability products directly, and uses the logarithm of each complete integer label in the time derivative. Its source and time derivatives agree with the factored implementation at the exact center, but its full-box interval enclosures are computed separately. Both methods close their strict source-contraction and self-map inequalities. They share Arb's interval arithmetic; the audit does not describe them as independent implementations of numerical inclusion arithmetic.

All factor probabilities are normalized by their complement-coordinate definition. The proof checks positivity and pair separation throughout the complete rectangular source enclosure, not only at the proposed center. My separate exact-rational interval calculation gives
\[
\min q_{j,a}\ge0.0770667338208548,\qquad
\|q-r\|_{\rm factors}^2\ge0.6397654369475206.
\]
These bounds support the reported conservative claims of probabilities above 0.07 and factor distance above 0.79.

## Vertex separation remains uniform

A product vertex has integer label $N=2^{a_1}3^{a_2}5^{a_3}$. Two vertices differing in $k$ factors have squared factor distance $2k$, so their squared response/factor ratio is
\[
\sum_{\ell=1}^6(1-\cos(t_\ell\log(N/M)))/k.
\]
This matches the declared raw complex Euclidean output norm, with no division by six. The 171 oriented exponent differences exhaust all possibilities.

I independently evaluated the raw complex responses of all 64 vertices at the center with 192-bit Arb arithmetic, checked all **2,016** unordered pairs, and subtracted the global time-Lipschitz allowance $6\epsilon|\log(N/M)|/k$ for each pair. The resulting uniform squared floor is above **1.0680255458**, which still exceeds $1.03^2=1.0609$. This independently confirms that the whole time box retains strong vertex separation while admitting exact interior collisions.

## Executed checks and limits

All **ten tests passed** in a fresh process. They include both complete factored reconstructions at 256 and 384 bits, both independent 64-label reconstructions at those precisions, source and time derivative identities, all-vertex controls, fixed query consequences, invalid-domain rejection, oversized-box failures, and the failure of the same certificate when its moving predictor is removed. The two precisions produce identical public rational certificates.

I separately checked the published rational self-map inequalities for both algebraic reconstructions, the exact fixed query gap, the active-coordinate census, and the complete source rectangle. The independent auxiliary evidence is recorded in [independent_audit_checks.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/independent_audit_checks.json).

The theorem proves a small open failure neighborhood around the given schedule, not a maximal domain or a classification of all short schedules. It establishes mathematical nonidentifiability in the labelled product model. No hardware validation, uncertain-clock assumption, or empirical noise law is needed or supplied. Within this scope, it materially strengthens the previous isolated collision: vertex-only validation fails robustly throughout an explicitly certified set of designs, and the hidden ambiguity changes a concrete scalar question by more than one half.
