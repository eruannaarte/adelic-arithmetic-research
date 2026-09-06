# An open family of nonidentifying harmonic schedules

## Model and theorem

The source is a labelled tuple \(q=(q_1,q_2,q_3)\), where each \(q_j\) is a probability vector on exponents \(0,1,2,3\). The prime labels are \((2,3,5)\). A known, fixed time \(t\) gives one raw complex reading

\[
F_t(q)=\prod_{j=1}^3\sum_{a=0}^3q_{j,a}e^{-ita\log p_j}.
\]

Source distance is the square root of the sum of the three squared Euclidean factor distances. Data distance is raw complex Euclidean distance on six readings, without division by six. The times are known design variables; the theorem does not require uncertain clocks or sensor noise.

Let

\[
t^0=(15.790052,25.962780,28.039208,28.695603,29.332467,29.966619),
\qquad \epsilon=1/40000.
\]

**Theorem U-H.** For every \(t\) in the entire six-dimensional closed box \(\|t-t^0\|_\infty\le\epsilon\):

1. Every pair of different product vertices has response/factor-distance ratio greater than \(1.03\).
2. There exist two product distributions \(q(t),r(t)\), all of whose factor probabilities exceed \(0.07\), with factor distance greater than \(0.79\), such that \(F_{t_l}(q(t))=F_{t_l}(r(t))\) for all six readings.
3. The scalar query \(Q(q)=q_{2,1}\), the probability of exponent one in the prime-3 factor, has the two fixed answers

\[
Q(q(t))=0.083208071567702588,
\qquad Q(r(t))=0.63280942665025819.
\]

Consequently the answer set at their common observation has diameter at least

\[
\Delta_Q=0.549601355082555602.
\]

Every deterministic estimator of this scalar query has worst-case absolute error at least \(\Delta_Q/2=0.274800677541277801\), even with zero noise. The bit query \(\mathbf 1\{q_{2,1}>1/2\}\) cannot be uniformly recovered. The full source-separation floor is zero throughout the time box.

The collision pair can be chosen as a continuous branch. In the 18 complement coordinates defined below, its infinity-norm variation is bounded by \(3.567017552\|t-s\|_\infty\). This is a bound for the combined pair's complement coordinates, not the Euclidean factor metric.

The quantifiers are \(\forall t\ \exists q(t),r(t)\). The result does not claim that a single fixed pair collides for every perturbed time. The whole box has maximum time \(29.966644<30\); no conclusion about all schedules below 30 follows.

## Parameterized contraction lemma, with proof

Let \(f(x,t)\in\mathbb R^d\) be continuously differentiable on a neighborhood of all points below. Let \(x\) denote the \(d\) active source coordinates, with any other coordinates frozen. Fix rational matrices \(R\in\mathbb Q^{d\times d}\), \(P\in\mathbb Q^{d\times m}\), a center \((x_0,t_0)\), time radius \(\epsilon>0\), and root radius \(\rho>0\). Write

\[
C(\delta)=x_0+P\delta,\quad
T=\{t_0+\delta:\|\delta\|_\infty\le\epsilon\},\quad
Y=[-\rho,\rho]^d.
\]

Let rectangular interval enclosures \(C\) and \(X\) contain every \(C(\delta)\) and \(C(\delta)+y\), respectively. Suppose interval differentiation and outward arithmetic establish

\[
L\ge\sup_{X\times T}\|I-RD_xf\|_\infty,\qquad L<1,
\]

\[
e_0\ge\|Rf(x_0,t_0)\|_\infty,
\quad
M\ge\sup_{C\times T}\|R(D_xf\,P+D_tf)\|_\infty,
\quad e=e_0+\epsilon M,
\]

and \(e+L\rho<\rho\). Then every \(\delta\in[-\epsilon,\epsilon]^m\) has exactly one root of \(f(C(\delta)+y,t_0+\delta)=0\) within \(Y\).

**Proof.** Along the parameter chord \(s\mapsto(C(s\delta),t_0+s\delta)\), the fundamental theorem of calculus gives

\[
Rf(C(\delta),t_0+\delta)
=Rf(x_0,t_0)+\int_0^1R(D_xf\,P+D_tf)\delta\,ds.
\]

Every point on this chord belongs to \(C\times T\), so its infinity norm is at most \(e_0+\epsilon M=e\). For fixed \(\delta\), define

\[
S_\delta(y)=y-Rf(C(\delta)+y,t_0+\delta).
\]

The source derivative and a second chord integral show that \(S_\delta\) has Lipschitz constant at most \(L\) on \(Y\). Moreover \(\|S_\delta(y)\|_\infty\le e+L\rho<\rho\), so it maps the closed box into itself. Iteration starting anywhere in the box is Cauchy, because successive differences are bounded by a geometric series with ratio \(L<1\). Completeness gives a fixed point, and the contraction inequality makes it unique.

A fixed point gives \(Rf=0\). At any point in the box, \(\|I-RD_xf\|<1\) makes \(RD_xf\) invertible by its convergent geometric inverse series. Since these are finite square matrices, \(R\) is invertible. Thus \(Rf=0\) implies \(f=0\). Conversely every zero is a fixed point. This proves existence and local uniqueness. QED.

For branch regularity, additionally let

\[
B\ge\sup_{X\times T}\|R(D_xf\,P+D_tf)\|_\infty.
\]

At a fixed \(y\), a parameter chord gives \(\|S_\delta(y)-S_\gamma(y)\|_\infty\le B\|\delta-\gamma\|_\infty\). Apply this and the contraction to the two fixed points and rearrange:

\[
\|y(\delta)-y(\gamma)\|_\infty
\le\frac{B}{1-L}\|\delta-\gamma\|_\infty.
\]

Adding the affine-center difference proves that the full active-coordinate branch has Lipschitz constant at most \(\|P\|_\infty+B/(1-L)\). Frozen coordinates do not change. No unproved implicit-function or numerical-root assertion is needed.

## Exact construction from the harmonic model

For each of the two sources and each factor, use probabilities at exponents 1, 2, 3 as complement coordinates. Exponent-zero probability is one minus their sum. This gives 18 real coordinates for a pair. The 18 rational center coordinates and the ordered active set

\[
(16,6,17,1,10,15,7,8,2,4,11,0)
\]

are frozen in [inputs.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/inputs.json). Indices start at zero. The six inactive coordinates remain fixed. The residual \(f\in\mathbb R^{12}\) consists of the six real parts, followed by the six imaginary parts, of \(F_{t_l}(q)-F_{t_l}(r)\).

The exact rational matrix \(R\) is the previously proposed point-Jacobian inverse rounded to multiples of \(10^{-12}\). The exact rational predictor \(P\) is obtained by rounding \(-R D_tf(x_0,t_0)\) to the same rational grid. The source-center and matrix proposals are merely inputs: both complete replays independently verify all necessary inequalities. Inverting an approximate Jacobian is not a proof premise.

The new root radius is \(\rho=1/30000\). If the \(i\)-th row of \(P\) has absolute sum \(p_i\), then the rectangular center enclosure has active radius \(\epsilon p_i\), and the full root enclosure has radius \(\epsilon p_i+\rho\). These contain every correlated moving center and root box, even though interval evaluation allows more combinations than the actual parameterized family.

Write \(E_{lja}=e^{-it_l a\log p_j}\) and \(\chi_{lj}=\sum_aq_{j,a}E_{lja}\). Every active-source derivative is

\[
\pm(E_{lja}-1)\prod_{h\ne j}\chi_{lh},
\]

with sign depending on the member of the source pair. The time derivative of one source response is

\[
\sum_j\left(\sum_a(-ia\log p_j)q_{j,a}E_{lja}\right)
\prod_{h\ne j}\chi_{lh}.
\]

Its contribution to \(D_tf\) appears only in the real and imaginary rows of that reading. These formulas are differentiated from the defining model and evaluated over complete source and time intervals. They supply the Jacobians in the lemma; no saved numerical response matrix is assumed.

The outward rational exports from the factored computation are

| Quantity | Proved bound |
|---|---:|
| Source contraction \(L\) | \(0.218567913\) |
| Moving-center residual \(e\) | \(0.000003233\) |
| Self-map radius \(e+L\rho\), directly exported | \(0.000010519\) |
| Self-map ratio before separate export rounding | \(0.315553777\) |
| All-probability lower bound | \(0.077066733\) |
| Factor-distance squared lower bound | \(0.639764740\) |
| Vertex-floor squared lower bound | \(1.068025824\) |

The exported bounds also close \(e+L\rho<\rho\) when combined as exact rational numbers. Both source claims hold throughout the full rectangular source enclosure, and therefore at the exact roots supplied by the lemma. This proves the interior-collision part of U-H.

The second factor's exponent-one coordinates have global complement indices 3 and 12. Neither is active, so their exact values are the two decimals displayed in the theorem for every root. Their gap proves the scalar answer-diameter claim. At a common observation, an estimator must give the same value \(z\) for both sources. The triangle inequality gives \(\Delta_Q\le|Q(q)-z|+|Q(r)-z|\), proving the error lower bound. Their positions on opposite sides of \(1/2\) prove the bit-query obstruction.

## Uniform vertex separation

A product vertex corresponds to an integer label \(N=2^{a_1}3^{a_2}5^{a_3}\), with \(a_j\in\{0,1,2,3\}\), and response \(e^{-it\log N}\). Two vertices differing in \(k\) factors have squared factor distance \(2k\). Their squared normalized response distance is exactly

\[
\sum_{l=1}^6\frac{1-\cos(t_l\log(N/M))}{k}.
\]

All distinct source-pair differences are represented by the 171 oriented exponent differences in \(\{-3,\ldots,3\}^3\). The checker enumerates every one with exact integer labels and evaluates the displayed expression on the whole six-time interval box. The least exported lower bound is \(1.068025824>1.03^2\). The classification is exhaustive; no time sampling or vertex sampling is used for the proof.

## Independent reconstruction, trust boundary, and limits

The second complete replay expands all 64 integer-label terms

\[
F_t(q)-F_t(r)=\sum_{a\in\{0,1,2,3\}^3}
\left(\prod_jq_{j,a_j}-\prod_jr_{j,a_j}\right)
 e^{-it\log(2^{a_1}3^{a_2}5^{a_3})}.
\]

It differentiates each amplitude directly and differentiates the phase using the log of the full integer label. It does not call the factored response or derivative. Its wider interval enclosure still gives \(L\le0.496731191\), moving-center residual at most \(0.000009681\), and self-map ratio at most \(0.787139442<1\). Thus it independently proves the same uniform root theorem from the original model. Both 256-bit and 384-bit replays produce identical rational public certificates.

Exact Fraction arithmetic, Python execution semantics, and Arb's outward inclusion semantics are trusted. The two algebraic reconstructions share the Arb library; this is not a proof-assistant formalization or an independent implementation of interval arithmetic. A separate raw-response control enumerates all 2,016 vertex pairs and applies a global time-Lipschitz allowance. Ten tests exercise reconstruction, derivative identities, frozen query consequences, and rejected malformed or overambitious claims. Test counts are not substituted for the contraction proof.

The time radius is deliberately small and conservative. It proves an open failure neighborhood, not a maximal collision domain, optimal time horizon, or impossibility for every six-reading schedule below 30. Failure of a larger proposed interval certificate is retained as a failed sufficient test, not a theorem of recovery or nonrecovery outside the certified box. This result concerns the declared labelled product model; it asserts neither physical sensor validation nor a theorem for arbitrary arithmetic sequences.
