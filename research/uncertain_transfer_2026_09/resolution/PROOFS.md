# Seven rows with explicit clock and generator uncertainty

The source is a nonzero vector \(u\in\mathbb R^2\), its unknown label is
\(j\in\{490,\ldots,510\}\), and the seven rows are
\(490,492,496,500,504,508,510\). The finite generator, source injection and
row functionals are exactly those in the preceding spatial packages. These
rows are global averages in the transverse coordinate, not point sensors.
Let \(A_j(t)\) be the normalized physical forward map and let
\(\alpha(t)=(1+t)^{1/4}\). The actual and nominal shared times both belong to
\([1,2]\). All norms below are Euclidean operator or vector norms.

## Exact complete-time spatial certificate

Let \(P_j(t)\) be the degree-32 rational polynomial from the midpoint of every
inherited outward kernel coefficient interval. The complete finite-boundary,
periodic-image, Taylor and coefficient-rounding bounds imply
\[
 \|A_j(t)-\alpha(t)P_j(t)\|\le\rho=10^{-9}
 \qquad(j=490,\ldots,510;\ 1\le t\le2).
\]
This is the same defining finite model and the same complete approximation
premise as before. The kernel reconstruction is separate from evaluating a
saved matrix.

The new rational certificate proves, on the entire interval,
\[
 \lambda_{\min}(P_j^TP_j)>1.5\,10^{-8},\qquad
 \lambda_{\min}([P_j,-P_k]^T[P_j,-P_k])>5\,10^{-14}\quad(j\ne k).
\]
There are 21 individual cases and 210 unordered pairs. Each has an exact
partition of \([1,2]\); together these use 861 nonempty cells and 3,743
case records. For each cell the supplied rational preconditioner \(R\)
satisfies
\[
 \|I-(M(c)R)^T(M(c)R)\|_\infty<1-\gamma^2,
 \quad \sup_t\|(M(t)-M(c))R\|\le e,
 \quad e+\sqrt{f\|R\|_F^2}<\gamma,
\]
where \(\gamma=999999/10^6\), \(M=P_j\) or \([P_j,-P_k]\), and \(f\)
is its stated floor. The first inequality also implies that \(R\) is
invertible. For every vector \(v\),
\(\|M(t)Rv\|>(\gamma-e)\|v\|>\sqrt f\|R\|_F\|v\|\), hence
\(\|M(t)w\|>\sqrt f\|w\|\). The consumer recomputes every point Gram
matrix and every full polynomial-cell variation with exact rationals, using
Horner translation independently of the producer's binomial translation.
The explicit rational square-root upper bounds are checked by squaring.

Since \(\alpha\ge19/16\), the physical approximate-map floors are
\[
 \mu=\frac{1083}{51200000000},\qquad
 \lambda=\frac{361}{5120000000000000}.
\]
No assertion of optimal row count or optimal placement follows from these
lower bounds.

## A verified time derivative bound

Write each scalar entry as \(p(t)=\sum_{k=0}^{32}c_k(t-3/2)^k\). Define
\[
 B_0(p)=\sum_{k=0}^{32}|c_k|2^{-k},\qquad
 B_1(p)=\sum_{k=1}^{32}k|c_k|2^{-(k-1)}.
\]
On \([1,2]\), \(\alpha\le4/3\) and \(\alpha'\le1/6\). The latter
follows from \(\alpha'=1/[4(1+t)^{3/4}]\) and
\((3/2)^4<2^3\). Therefore
\[
 \| (\alpha P_j)'(t)\|^2
 \le \sum_{\text{rows, ports}}\bigl(B_0(p)/6+4B_1(p)/3\bigr)^2
 < (37/1000)^2.
\]
`timing.py` recomputes these 21 rational inequalities from all the defining
coefficients. Consequently \(L=37/1000\) is a uniform Lipschitz constant.

## Generator mismatch

Allow a shared finite generator \(H'\) with the same source injection,
row functionals and normalization, assuming \(H,H'\) are self-adjoint
positive semidefinite and \(\|H'-H\|\le\varepsilon_H\). Duhamel's identity
and the contraction of both exponential semigroups give
\[
 e^{-tH'}-e^{-tH}
 =-\int_0^t e^{-(t-s)H'}(H'-H)e^{-sH}\,ds,
 \qquad \|e^{-tH'}-e^{-tH}\|\le t\varepsilon_H.
\]
The source injection and selected row map have norm at most one. Thus the
normalized forward discrepancy is at most
\((4/3)\,2\varepsilon_H=8\varepsilon_H/3\).
No commutation assumption is required for this bound.

For \(|t_1-t_0|\le h\), with both times in \([1,2]\), split the difference
at \(\alpha(t_1)P_j(t_1)\). The result is
\[
 \|A'_j(t_1)-\alpha(t_0)P_j(t_0)\|
 \le \rho+Lh+8\varepsilon_H/3.
\]
Only one inherited approximation radius is needed. Derivatives of the unknown
approximation remainder are neither assumed nor used. This is shared snapshot
timing uncertainty; arbitrary distinct acquisition times for the seven rows
would require a separately declared model and bound.

## Label and source recovery

For sensor error \(\eta\|u\|\) and verified normalization error
\(\xi\|u\|\), set
\[
 \delta=\eta+\rho+\xi+Lh+8\varepsilon_H/3.
\]
Each admissible physical observation is within \(\delta\|u\|\) of its
nominal approximate image. If \(2\delta^2<\lambda\), two distinct labels'
relative tubes are disjoint: the sum of their radii is at most
\(\sqrt2\delta\sqrt{\|u\|^2+\|v\|^2}\), whereas their approximate
images are separated by more than
\(\sqrt\lambda\sqrt{\|u\|^2+\|v\|^2}\). After the correct label is
selected, ordinary least squares has relative error at most
\(\delta/\sqrt\mu\). Thus error strictly below \(10^{-3}\) follows from
\(\delta^2<10^{-6}\mu\).

Both strict gates hold for:

| Profile | Sensor radius | Clock error \(h\) | Generator norm error | Total \(\delta\) |
| --- | ---: | ---: | ---: | ---: |
| Known clock/model | \(1.4\,10^{-7}\) | 0 | 0 | \(1.42\,10^{-7}\) |
| Uncertain clock/model | \(1.1\,10^{-7}\) | \(5\,10^{-7}\) | \(10^{-9}\) | \(799/(6\,10^9)\) |

Both include \(\rho=\xi=10^{-9}\). The source error squared bounds are,
respectively, \(10082/10576171875\) and \(638401/761484375000\).

## Raw observations with nonzero uncertainty

For the fixture family \(H'=H+\lambda I\), \(0<\lambda\le10^{-9}\),
the full perturbed finite response equals \(e^{-\lambda t}A_j(t)u\).
`fixtures.py` outwardly evaluates
\(e^{-\lambda t_1}\alpha(t_1)P_j(t_1)u\), rounds each raw coordinate to a
fixed rational grid, then adds a rational sensor vector of norm
\(\eta\|u\|/4\). Its discrepancy from the actual full finite model is
bounded by \((\rho+\text{rounding}+\eta/4)\|u\|<\eta\|u\|\).
This proves that the exact raw fixtures meet the declared physical observation
promise. The decoder still charges its own approximation and uncertainty
budgets; construction error is part of the separately verified sensor budget.

The fixtures use nonzero time errors at both endpoints and at the midpoint,
nonzero generator mismatch, three labels, and source scales \(10^{-8},1,10^8\).
A 320-bit replay reconstructs every raw rational value. These are mathematical
synthetic observations, not empirical calibration data.
