# Seven separated rows at a fixed noise requirement

## 1. Model, promise and fixed objective

Retain exactly the finite diffusion model of the
[complete model proof](../../transfer_theorem_2026_09/resolution/PROOFS.md).
Both path Laplacians have 1,001 vertices and reflecting, degree-one endpoints.
For the normalized constant vector \(e\), the two normalized midpoint cosine
source modes \(U\), and
\(V_{ii}=1+\frac45(i+\frac12)/1001\), the response is

\[
H=I_y\otimes L_x+L_y\otimes V,\qquad
T_j(t)u=(1+t)^{1/4}(I_y\otimes e^T)e^{-tH}(\delta_j\otimes Uu).
\]

The target is any integer \(490\le j\le510\), the source is any nonzero
\(u\in\mathbb R^2\), and time is known and may be any real \(t\in[1,2]\).
The source norm here is Euclidean. Each acquired coordinate is still a
global average along the \(x\) direction at one transverse row.

The [protocol](../PROTOCOL.md) fixed the objective before searching:
seven integer row offsets in \([-16,16]\), gaps at least two, sensor error
\(\|\epsilon\|_2\le10^{-7}\|u\|_2\), model budget \(\rho=10^{-9}\),
computed-data allowance \(\xi=10^{-9}\), and source relative accuracy
strictly below \(10^{-3}\).

The successful fixed bank is

\[
B=(-12,-10,-3,0,4,8,10),
\qquad \text{physical rows }(488,490,497,500,504,508,510).                 \tag{1}
\]

Its consecutive gaps are \(2,7,3,4,4,2\). It does not depend on the target,
source direction, time, or data.

## 2. Complete physical approximation

Let \(P_j(t)\) be the seven-by-two rational polynomial map built from the
midpoints of the inherited, outward-enclosed
[Taylor kernel](../../transfer_theorem_2026_09/resolution/kernel.json).
The certificate binds that exact file by SHA-256. A separate kernel replay
reconstructs its coefficients from the finite \(x\) generator; binding a file
alone would not prove that physical premise.

All used displacements are at most 22, within the inherited range 0 through 26.
The complete per-entry remainder remains

\[
e_*=2^{-33}+10^{-24}+10^{-500}+2\cdot10^{-30}.
\]

These four terms respectively enclose the omitted time series, all periodic
images, the finite transverse boundary correction, and coefficient rounding.
The new consumer reruns their rational error inequalities. In particular, with
\(\alpha(t)=(1+t)^{1/4}\), \(a_0=19/16<\alpha(t)<4/3=a_1\), and \(A_j\)
the actual physical map restricted to (1),

\[
\|A_j(t)-\alpha(t)P_j(t)\|_2^2
\le a_1^2(14)e_*^2<10^{-18}=\rho^2.                                    \tag{2}
\]

This is a uniform operator bound, so it applies to every source direction
and amplitude. No sampled-time approximation is substituted for (2).

## 3. Exact certification of all target pairs and all times

The new [certificate](certificate_7.json) establishes simultaneously

\[
P_j(t)^TP_j(t)\succ sI_2,\qquad
[P_j(t),-P_k(t)]^T[P_j(t),-P_k(t)]\succ pI_4,\quad j\ne k,                \tag{3}
\]

where

\[
s=\frac{74}{10^{10}}=7.4\cdot10^{-9},
\qquad p=\frac{2}{10^{14}}=2\cdot10^{-14}.                              \tag{4}
\]

There are 21 individual and 210 unordered pair cases. The certificate contains
1,051 nonempty time cells and 3,391 case-specific records. For **each case
separately**, its closed cells cover exactly \([1,2]\), with no missing
interval. Different cases may use different subdivisions.

Here is the complete algebraic certificate argument. On a cell of center \(c\)
and radius \(r\), let \(M=P_j\) or \(M=[P_j,-P_k]\), and let \(R\) be its
recorded rational square preconditioner. With
\(\gamma=999999/10^6\), the checker proves

\[
\|I-(M(c)R)^TM(c)R\|_\infty<1-\gamma^2,\quad
\|(M(t)-M(c))R\|_2\le E,\quad
E+w<\gamma,\quad w^2\ge f\|R\|_F^2,                                   \tag{5}
\]

for \(f=s\) or \(p\). The symmetric row-sum bound implies
\(\sigma_{\min}(M(c)R)>\gamma\); consequently \(R\) is invertible.
The triangle inequality then gives, for every nonzero \(v\),

\[
\|M(t)v\|>(\gamma-E)\|R^{-1}v\|
\ge\frac{\gamma-E}{\|R\|_F}\|v\|>\sqrt f\,\|v\|.
\]

For the whole-cell bound in (5), each degree-32 polynomial is translated
exactly to \(c\), multiplied by \(R\) before absolute values are taken, and
every nonconstant coefficient is summed against \(r^k\). The resulting
entrywise bounds are combined in Frobenius norm. The producer uses binomial
translation; the independent consumer calculation uses Horner composition.
Floating Cholesky factors only propose the rational \(R\). Every acceptance
inequality and every case's coverage are checked with exact fractions.

## 4. Transfer and decoder

Set

\[
\delta=10^{-7}+10^{-9}+10^{-9}=\frac{51}{500000000},\quad
\mu=a_0^2s=\frac{13357}{1280000000000},\quad
\lambda=a_0^2p=\frac{361}{12800000000000000}.
\]

The unchanged [transfer theorem](../../transfer_theorem_2026_09/framework/PROOFS.md)
now applies through the exact strict inequalities

\[
\lambda>2\delta^2,\qquad
\frac{\delta^2}{\mu}=\frac{5202}{5217578125}
<(0.000998507)^2<10^{-6}.                                               \tag{6}
\]

If two distinct targets with nonzero sources \(u,v\) explained the same
observation, their approximate response difference would be at most
\(\delta(\|u\|+\|v\|)\le\sqrt2\delta\sqrt{\|u\|^2+\|v\|^2}\).
The pair floor in (6) excludes this. For the correct target, the least-squares
inverse has norm at most \(1/\sqrt\mu\), so the source relative error is
strictly below \(0.000998507\).

The source gate is the tighter certified constraint: these deliberately
conservative floors allow a sensor radius below
\(10^{-3}\sqrt\mu-\rho-\xi\), approximately \(1.0015261\cdot10^{-7}\).
This is a consequence of the recorded floors, not the optimal physical
noise threshold. The requirement \(10^{-7}\) was fixed before discovery.

[decoder.py](decoder.py) implements the same exact rational feasibility test
as the preceding decoder. It accepts normalized rational data \(z=y/\alpha\)
and exact rational time, without a true-target input. Writing
\(G=P_j^TP_j\), \(r=P_j^Tz\), and \(b^2=(\delta/a_0)^2\), it checks

\[
\|z\|^2-r^T(G-b^2I)^{-1}r\le0.                                        \tag{7}
\]

The matrices \(G-b^2I\) are positive definite by (6). Equation (7) exactly
tests whether some source lies in the conservatively enlarged relative
noise tube. The true target is feasible, and (6) excludes a second target.
The returned source is the ordinary \(G^{-1}r\). Empty feasibility is
reported as incompatible; multiple feasibility leads to abstention.

Zero observations, floating inputs, out-of-range times and unbudgeted
computed error are rejected. The theorem includes every real known time;
the executable exact interface takes rational time. A normalization wrapper
may discharge \(\xi\), but uncharged time uncertainty or arbitrary floating
rounding is not implicitly allowed.

## 5. Why the search cannot be its own certificate

The bounded search examined 1,214 distinct banks on 17 times, then refined
30 leading candidates using 129 times and local time minimizations.
These floating calculations propose designs only.

The coarse-grid winner was
\(B_{\rm coarse}=(-11,-8,-4,0,4,8,11)\), with sampled unnormalized pair
floor above \(1.11\cdot10^{-12}\). Its interior-time behavior is different.
At the exact rational time
\(t=1221707459/10^9\), targets \(492,493\), the rational source pair in
[coarse_grid_obstruction.json](coarse_grid_obstruction.json) satisfies

\[
\|A_{492}u-A_{493}v\|
\le a_1\|P_{492}u-P_{493}v\|+\rho(\|u\|+\|v\|)
<1.463\cdot10^{-9}(\|u\|+\|v\|).
\]

The separate exact [obstruction checker](obstruction.py) proves this using
rational square-root enclosures and the complete physical error (2).
Consequently the two physical sensor-error balls intersect at the fixed
allowed radius \(10^{-7}\). No decoder can always identify the target for
this particular bank. The successful bank (1) passes the uniform proof,
despite looking weaker on the coarse grid.

This establishes a design consequence of query transfer: reducing channels
requires control of the weakest pair over the **entire** admissible time
range. It does not prove seven is optimal or obstruct other seven-row banks.
