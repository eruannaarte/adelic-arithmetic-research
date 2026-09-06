# Eight and nine separated rows, with a specific seven-row obstruction

## 1. The unchanged physical experiment

Use the finite diffusion model from the
[preceding complete model proof](../../transfer_theorem_2026_09/resolution/PROOFS.md).
Both reflecting paths have 1,001 vertices. With endpoint degree-one path
Laplacians, midpoint potential $V_{ii}=1+(4/5)(i+1/2)/1001$, unit constant
vector $e$, and normalized midpoint cosine source modes one and two $U$,

\[
H=I_y\otimes L_x+L_y\otimes V,\qquad
T_j(t)u=\alpha(t)(I_y\otimes e^T)e^{-tH}(\delta_j\otimes Uu),
\quad \alpha(t)=(1+t)^{1/4}.                                               \tag{1}
\]

The time is known and may be any real $t\in[1,2]$. The target is any
$j\in\{490,\ldots,510\}$ and the source is any nonzero $u\in\mathbb R^2$.
Each retained row is still a global average in $x$ at one transverse location.
It is not a fully local point sensor.

Let row offsets be measured about 500. Two sufficient banks are

\[
B_9=(-15,-12,-8,-4,0,4,8,12,16),\qquad
B_8=(-12,-10,-6,-2,2,6,10,14).                                             \tag{2}
\]

They acquire respectively nine and eight distinct, separated rows. Both are
asymmetric. They are different designs, not a claim that arbitrary deletions
from the previous eleven-row bank preserve recovery.

The source norms remain $S_0=I$,
$S_1=\operatorname{diag}(1+\pi^2,1+4\pi^2)$ and

\[
S_2=\operatorname{diag}\!\left(1+4n^2\sin^2\frac{\pi}{2n},
                              1+4n^2\sin^2\frac{\pi}{n}\right),\quad n=1001.
\]

The established bounds are $I\preceq S_1,S_2\preceq41I$.

## 2. Complete model errors and new continuous floors

The hash-bound [Taylor kernel](../../transfer_theorem_2026_09/resolution/kernel.json)
keeps the exact finite $x$ path and a period-64 transverse surrogate. It encloses
every coefficient through order 32 for distances 0 through 26 and both source
modes. The coefficient intervals are reconstructed from the defining generator
by outward arithmetic; they are not fitted to a saved response matrix.

For every bank in (2), and also the seven-row bank below, all used distances
are at most 26. The inherited complete per-entry errors are

\[
e_* = 2^{-33}+10^{-24}+10^{-500}+2\cdot10^{-30}.                            \tag{3}
\]

These respectively bound the full omitted time series, all periodic images,
the difference from the actual finite transverse boundaries, and coefficient
rounding. Their proofs use the positive-semidefinite spectral bound on the
time derivative, a Laurent coefficient bound with complete geometric image
sum, and a complete uniformization tail starting at walk 491. None depends on
which of these rows is retained. Their exact rational inequalities are rerun
by the new consumer.

Let $P_j(t)$ use exact rational midpoints of the kernel intervals and set
$\widetilde A_j(t)=\alpha(t)P_j(t)$ for the selected rows. Since
$19/16<\alpha<4/3$ and each bank has at most nine rows,

\[
\|A_j-\widetilde A_j\|_2^2\le(4/3)^2(2|B|)e_*^2<10^{-18},
\qquad \rho=10^{-9}.                                                       \tag{4}
\]

Here $A_j$ is the actual normalized finite-graph response restricted to the
bank. Thus $\rho$ is already in the physical output normalization.

The new exact certificates establish, for all times and targets,

\[
P_j^TP_j\succ s_BI,\qquad
[P_j,-P_k]^T[P_j,-P_k]\succ p_BI\quad(j\ne k),                             \tag{5}
\]

with

| Bank | $s_B$ | $p_B$ | Nonempty cells | Case-specific records |
|---|---:|---:|---:|---:|
| Nine rows | $6.5\cdot10^{-8}$ | $10^{-11}$ | 39 | 1,283 |
| Eight rows | $4\cdot10^{-8}$ | $10^{-12}$ | 43 | 1,174 |

There are 21 individual cases and 210 distinct target-pair cases per bank.
Every case's cells must separately cover exactly $[1,2]$, including both
endpoints. Coverage by the union of unrelated cases would be insufficient.

For completeness, the certificate mechanism is the following elementary
singular-value argument. On a cell with center $c$ and radius $r$, a rational
preconditioner $R$ is proposed for $M=P_j$ or $[P_j,-P_k]$. Exact arithmetic
verifies

\[
\|I-(M(c)R)^T M(c)R\|_\infty<1-\gamma^2,quad
\|[M(t)-M(c)]R\|_2\le E,quad
E+w<\gamma,\quad w^2\ge f\|R\|_F^2,                                     \tag{6}
\]

where $\gamma=999999/10^6$ and $f=s_B$ or $p_B$. The symmetric row-sum bound
implies the center's smallest singular value exceeds $\gamma$. In particular
$R$ is invertible. Consequently

\[
\|M(t)v\|>(\gamma-E)\|R^{-1}v\|
\ge\frac{\gamma-E}{\|R\|_F}\|v\|>\sqrt f\|v\|.
\]

The whole-cell $E$ comes from translating each exact polynomial, multiplying
by $R$ before taking absolute values, and summing every nonconstant Taylor
term against $r^k$. The producer uses binomial translation; the consumer uses
Horner composition and recomputes all rational bounds. Floating Cholesky
factors only propose $R$. They do not establish (5).

Multiplying (5) by the normalization lower bound gives
$\mu_B=(19/16)^2s_B$ and $\lambda_B=(19/16)^2p_B$. For either H1 norm, both
floors can be divided by 41; (4) remains valid because $S\succeq I$.

## 3. Transfer to target identification and source accuracy

For a source norm $S$, assume sensor error
$\|\epsilon\|_2\le\eta\|u\|_S$. An optional independently verified computed-data
error may contribute $\xi\|u\|_S$, with $0\le\xi\le10^{-9}$. Define
$\delta=\eta+\rho+\xi$. Let $c_S=1$ for L2 and $c_S=41$ for either H1 norm.

The unchanged transfer theorem gives the two sufficient conditions

\[
\lambda_B/c_S>2\delta^2,\qquad
\frac{\delta}{\sqrt{\mu_B/c_S}}<\varepsilon.                              \tag{7}
\]

The first identifies the target. Indeed, if two nonzero candidate sources
yielded the same allowed observation, their approximate response difference
would have norm at most
$\delta(\|u\|_S+\|v\|_S)\le\sqrt2\delta
\sqrt{\|u\|_S^2+\|v\|_S^2}$, contradicting the block floor.
For the correct target, the least-squares inverse and the individual floor
give the second, the source's relative $S$-norm error.

The following are strict guarantees with the full $\xi=10^{-9}$ allowance.
Displayed error numbers are outward-rounded upper bounds from exact rational
squared bounds, not sampled maxima.

| Bank and calibration | Sensor radius $\eta$ | Source relative error |
|---|---:|---:|
| Nine, L2 | $3\cdot10^{-7}$ | $<0.000998$ |
| Nine, either H1 | $3\cdot10^{-8}$ | $<0.000678$ |
| Eight, L2 | $2.3\cdot10^{-7}$ | $<0.000977$ |
| Eight, L2 at original noise | $3\cdot10^{-7}$ | $<0.001272$ |
| Eight, either H1 | $3\cdot10^{-8}$ | $<0.000863$ |

Nine rows preserve all previous noise allowances and the $0.001$ accuracy
target. Eight rows keep that accuracy if the L2 noise allowance is reduced
from $3\cdot10^{-7}$ to $2.3\cdot10^{-7}$, or keep the old L2 allowance with
the slightly weaker $0.0013$ accuracy target. Both H1 profiles retain their old
noise and accuracy allowances. The bounds concern different calibrated noise
models; they must not be interchanged without the source norm.

## 4. Exact query decoder

[decoder.py](decoder.py) accepts the bank, exact rational time and normalized
rational data $z=y/\alpha(t)$; it does not accept a true target label. For each
target, write $G=P_j^TP_j$, $r=P_j^Tz$ and
$b^2=c_S(\delta/(19/16))^2$. Conditions (7) imply $G-b^2I\succ0$.
The target is feasible exactly when

\[
\min_v\{\|z-P_jv\|^2-b^2\|v\|^2\}
=\|z\|^2-r^T(G-b^2I)^{-1}r\le0.                                         \tag{8}
\]

The H1 use of $41I$ is a conservative enlargement of its true source-dependent
tube; (7) excludes intersections even of these enlarged tubes. For promised
nonzero data the true target is included and no wrong target is included.
After selecting the unique target the source estimate is the ordinary
$G^{-1}r$, not the minimizer in (8). Its error is bounded using the actual
source norm and (7). Empty feasibility returns `incompatible`; multiple
feasibility returns `abstain`. Zero data, invalid times, float inputs and
unbudgeted numerical radii are rejected.

The theorem covers all real known times. This exact decoder interface covers
rational times and already-normalized rational data. Approximate time or
normalization needs its own error allowance. The optional $\xi$ remains a
conditional budget, not an automatic certification of a floating acquisition
or normalization routine.

## 5. A genuine obstruction for one seven-row proposal

Consider specifically

\[
B_7=(-15,-10,-5,0,5,10,16),\qquad
t=285/256,\qquad j=507, k=508.                                           \tag{9}
\]

[obstruction_7.json](obstruction_7.json) records a rational nonzero pair
$(u,v)\in\mathbb R^2\times\mathbb R^2$. The checker evaluates its polynomial
response difference exactly and combines it with the full model error (4).
With rational square-root enclosures it proves

\[
\|A_ju-A_kv\|_2
\le\frac43\|P_ju-P_kv\|_2+\rho(\|u\|_2+\|v\|_2)
<3\cdot10^{-8}(\|u\|_2+\|v\|_2).                                        \tag{10}
\]

Two Euclidean balls intersect whenever their center distance is at most the
sum of their radii. More explicitly, the weighted point

\[
y=\frac{\|v\|_2 A_ju+\|u\|_2 A_kv}{\|u\|_2+\|v\|_2}
\]

is within $3\cdot10^{-8}\|u\|_2$ of the first response and
$3\cdot10^{-8}\|v\|_2$ of the second. Thus at the allowed noise radius
$3\cdot10^{-8}$ no decoder can always identify the target for **this bank**.
The checked sufficient collision radius is below $2.053\cdot10^{-8}$.

Unlike a failed lower-floor computation, (10) constructs a genuine ambiguity
in the actual finite model with allowed relative sensor errors. It explains
why reducing row count can destroy noise tolerance even when sampled
identifiability appears plausible. It does not rule out other seven-row banks,
prove eight is optimal, or improve the universal necessary four-row benchmark.

## 6. Validation and scope

All 2,457 case-specific time records are checked with exact rational arithmetic.
The unchanged physical kernel is fully reconstructed again at 256 bits.
Eight focused tests exercise missing pair coverage, changed rows/floors,
corrupted preconditioners, all 21 unknown labels at endpoint and interior
times, all noise profiles, invalid inputs, and corruption of the seven-row
obstruction. A separate direct finite-million-state uniformization algorithm
provides 63 floating regression cases across both banks and all profiles.
Those diagnostics are not proof inputs or a verified floating rounding budget.

The target range, two-mode source class, known time and spatial-average
readouts remain essential. There is no positive source-independent absolute
noise allowance without an amplitude lower bound. Neither the sampled search
nor the failed seven-row example is a global acquisition optimum.
