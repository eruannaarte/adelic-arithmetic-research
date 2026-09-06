# Smaller asymmetric banks: complete mathematical argument

## 1. Model and precise claim

Retain the finite model and source calibrations from the prior [resolution proofs](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/resolution/PROOFS.md). Here $n=1001$, $g=4/5$, $K=2$, and the known observation time is any real $\tau\in[1,2]$. The unknown target is an integer $j\in\{490,\ldots,510\}$. Write

\[
H=I_y\otimes L_x+L_y\otimes V,\qquad
T_j(\tau)u=\alpha(I_y\otimes e^T)e^{-\tau H}(\delta_j\otimes Uu),
\quad \alpha=(1+\tau)^{1/4}.
\]

The path Laplacians have endpoint degree one, interior degree two, and edge entries (-1). The diagonal matrix $V$ has entries $1+(4/5)(x+1/2)/1001<9/5$. The normalized constant vector $e$ has norm one; the two midpoint cosine columns of $U$ are orthonormal. These definitions use all transverse modes when transformed to real space; off-center odd modes are retained. Each row still averages globally over the $x$ coordinate.

For a row index set $I$, let $T_j^I=P_I T_j$, with no rescaling after restriction. The three source metrics are

\[
S_0=I,\quad S_1=\operatorname{diag}(1+\pi^2,1+4\pi^2),\quad
S_2=\operatorname{diag}(1+4n^2\sin^2(\pi/(2n)),1+4n^2\sin^2(\pi/n)).
\]

**Theorem.** Both of the following asymmetric banks identify the unknown target and recover the two-dimensional source with the stated guarantees, uniformly for every known time in $[1,2]$ and every nonzero real source:

| Bank | Number of directly acquired real rows | Retained fraction of every original central information floor | Certified centroid error at relative output noise $10^{-3}$ |
|---|---:|---:|---:|
| $I_{50}=\{476,\ldots,525\}$ | 50 | $>99\%$ | $<0.100347$ cells |
| $I_{48}=\{477,\ldots,524\}$ | 48 | $>97\%$ | $<0.130178$ cells |

Their midpoint is 500.5 rather than the prior center 500. A discrete query decoder rounds the energy centroid to obtain $j$, then uses the least-squares inverse for that recovered label. Under the original absolute source-relative noise allowances

\[
\|\epsilon\|_2\le 3\cdot10^{-7}\|u\|_2
\quad\hbox{or}\quad
\|\epsilon\|_2\le3\cdot10^{-8}\|u\|_{S_m}\quad(m=1,2),
\]

the label is exact and the corresponding relative source error is less than $10^{-3}$. Each inequality is a separate calibrated noise assumption. The proof covers all noise vectors in the stated Euclidean ball, without a probability distribution.

The inherited premises are the central continuous-time finite Gram certificate, the R1 placement floor $c_m$, and the R2 complete finite-boundary first-moment estimate. They are rechecked by the prior rational checkers. The new spatial-tail calculation below is a direct analytic consequence of the actual finite generator, with rational bounds; it introduces no sampled matrix or new numerical integration premise.

## 2. Weighted semigroup lemma

Fix a real $a>1$ and a target $j$. On the finite state space define diagonal weights

\[
(W_\pm f)_{y,x}=a^{\pm(y-j)}f_{y,x}.
\]

These are finite invertible matrices, even though their entries become large. They are a proof device; the acquisition or decoder does not multiply readings by these weights. If $z(t)=e^{-tH}(\delta_j\otimes Uu)$, then

\[
\|W_\pm z(t)\|_2^2
\le \exp\{2v_*t(a+a^{-1}-2)\}\,\|u\|_2^2,
\qquad v_*=9/5. \tag{1}
\]

**Proof.** The $x$-edge terms commute with $W_\pm$ because their two endpoints have the same $y$, and still contribute a nonnegative quadratic form. A transverse edge with weight $v_x$, and endpoint values (p,q), contributes to the real quadratic form of $W_\pm H W_\pm^{-1}$

\[
v_x\bigl(|p|^2+|q|^2-(a+a^{-1})\operatorname{Re}(\bar p q)\bigr)
\ge -\frac{v_x}{2}(a+a^{-1}-2)(|p|^2+|q|^2),
\]

using $2\operatorname{Re}(\bar p q)\le |p|^2+|q|^2$. Each state belongs to at most two transverse edges; hence

\[
\operatorname{Re}\langle w,W_\pm H W_\pm^{-1}w\rangle
\ge -v_*(a+a^{-1}-2)\|w\|_2^2.
\]

For $w=W_\pm z$, differentiation gives
$d\|w\|^2/dt\le2v_*(a+a^{-1}-2)\|w\|^2$.
Multiplying by the negative scalar exponential and integrating proves (1). At time zero the weighted initial vector has norm $\|u\|_2$, because all its mass is at $y=j$ and $U$ is an isometry. This does not commute $L_x$ with $V$. Endpoint degree one only improves the bound. $\square$

Projection onto $e$ contracts each row norm and commutes with $W_\pm$. Since $\alpha^2=\sqrt{1+\tau}<2$, (1) gives for the normalized output $y=T_j u$

\[
\sum_k a^{\pm2(k-j)}|y_k|^2\le K(a)\|u\|_2^2,
\quad K(a)=2\exp\{(36/5)(a+a^{-1}-2)\}. \tag{2}
\]

The same single expression holds throughout the continuous time interval, including its endpoints.

## 3. Exact missing-energy and missing-moment bounds

For a consecutive bank $I=\{\ell,\ldots,h\}$, the nearest discarded distances from target $j$ are

\[
r_-(j)=j-\ell+1,\qquad r_+(j)=h-j+1.
\]

Equation (2), applied separately on the left and right, yields

\[
\|(I-P_I^*P_I)T_j u\|_2^2
\le K(a)\left(a^{-2r_-}+a^{-2r_+}\right)\|u\|_2^2. \tag{3}
\]

For $r\ge1$, if $a^2\ge (r+1)/r$, then $d a^{-2d}\le r a^{-2r}$ for every integer $d\ge r$: the successive ratio is $(1+1/d)/a^2\le1$. Thus the absolute discarded energy first moment obeys

\[
\sum_{k\notin I}|k-j|\,|y_k|^2
\le K(a)\left(r_-a^{-2r_-}+r_+a^{-2r_+}\right)\|u\|_2^2. \tag{4}
\]

These are bounds on every source combination, including cancellations. Taking the maximum of each right side over the complete finite set of 21 labels is exact, not a sampling approximation to unknown time or source direction.

Use $a=9/2$ for $I_{50}$, and $a=4$ for $I_{48}$. The exponent in (2) is exactly $98/5$ or $81/5$. The certificate encloses its exponential by positive Taylor sums and a geometric remainder; the producer uses degree 160 and the independent checker uses degree 180. Explicitly, for $0\le x<N+2$,

\[
e^x\le\sum_{k=0}^N\frac{x^k}{k!}
+\frac{x^{N+1}}{(N+1)!}\frac1{1-x/(N+2)}. \tag{5}
\]

All arithmetic in (3)–(5), the maximization, and outward rounding uses exact rational numbers. Let $L_I$ and $M_I$ denote the resulting missing-energy and missing-moment upper bounds. The certified energy losses are

\[
L_{50}<1.647504\cdot10^{-11},\qquad
L_{48}<3.012457\cdot10^{-10}. \tag{6}
\]

## 4. Information transfer with source calibration

The exact identity

\[
T_j^T T_j-(T_j^I)^T T_j^I
=T_j^T(I-P_I^*P_I)T_j
\]

is positive semidefinite. Equation (3) bounds its operator norm by $L_I$. If $S_m\ge s_m I$, conjugating by $S_m^{-1/2}$ bounds its calibrated norm by $L_I/s_m$. Consequently the inherited placement floor transfers to

\[
c_m^I=c_m-L_I/s_m. \tag{7}
\]

We use $s_0=1$, $s_1=s_2=9$. For $S_1$ this follows from the elementary bound $\pi>3$. For $S_2$, sine is increasing on $[0,\pi/2]$, and $\sin x\ge x-x^3/6$ there. Hence its first diagonal entry is greater than

\[
1+9\left(1-\frac{3}{8n^2}\right)^2>9\quad(n=1001),
\]

and its second diagonal entry is larger. The checker verifies the last rational inequality. The bound $\pi>3$ follows, for example, by comparing a unit-circle circumference with its strictly shorter inscribed regular hexagon. The sine inequality follows by integrating $\cos x\ge1-x^2/2$.

The checker requires all three values (7) to exceed 99% or 97% of their respective original central floors. It pays both the inherited R1 placement loss and the new acquisition loss. The H1 source calibration matters: using the L2 loss unchanged in every metric would unnecessarily discard the certified 50-row guarantee.

## 5. Unknown-target and source decoder

For all permitted targets, the distance to either full-grid boundary is at least 490. The previously proved R2 estimate gives

\[
\left|\sum_{k=0}^{1000}(k-j)|y_k|^2\right|
\le B\|u\|_2^2,\quad
B=8\mu\frac{\mu^{490}}{490!(1-\mu/491)},\quad \mu=56/5.
\]

The new checker verifies exactly that $B<10^{-400}$. Subtracting the discarded moment (4) and using the retained L2 floor gives the noiseless restricted centroid bound

\[
\left|\frac{\sum_{k\in I}k|y_k|^2}{\|P_Iy\|_2^2}-j\right|
\le\beta_I:=\frac{10^{-400}+M_I}{c_0^I}. \tag{8}
\]

For arbitrary noise $\|\epsilon\|\le\nu\|P_Iy\|$, subtract the noiseless centroid inside its perturbed numerator. Every retained index lies in an interval of diameter $h-\ell$. Cauchy–Schwarz and $\|P_Iy+\epsilon\|\ge(1-\nu)\|P_Iy\|$ give

\[
|C(P_Iy+\epsilon)-C(P_Iy)|
\le(h-\ell)\frac{2\nu+\nu^2}{(1-\nu)^2}. \tag{9}
\]

At $\nu=10^{-3}$, (8) plus (9) is less than 0.100347 or 0.130178, respectively. Both are strictly less than one half, so rounding identifies the true label. The decoder takes only the retained readings, their actual indices, and the known time; it does not receive the true target as an input.

After rounding, use the Moore–Penrose inverse $(T_j^I)^{\dagger}$. The floor (7) proves full column rank. The calibrated inverse identity

\[
(T_j^I S_m^{-1/2})^{\dagger}=S_m^{1/2}(T_j^I)^{\dagger}
\]

then yields $\|\widehat u-u\|_{S_m}\le\|\epsilon\|/\sqrt{c_m^I}$. The rational checker verifies that each declared source-relative radius $\eta_m$ satisfies both $\eta_m^2<10^{-6}c_m^I$ and the error target $\eta_m^2/c_m^I<10^{-6}$. Therefore that radius implies the relative output-noise premise and relative source error below $10^{-3}$. No arbitrary left inverse is substituted.

This is a concrete answer-set transfer: restriction loses a bounded amount of source information and a bounded first moment; the remaining observation forces one discrete label, after which its continuous-source uncertainty admits the stated enclosure. With a known positive lower bound $a\le\|u\|_{S_m}$, the fixed absolute allowance $\|\epsilon\|\le\eta_m a$ is sufficient. A positive absolute radius without a source-amplitude lower bound cannot hold uniformly near zero.

## 6. A necessary lower bound for joint queries

**Proposition.** Suppose the real source space is all of $\mathbb R^r\setminus\{0\}$, at least two target labels are possible, and their measurements at a fixed known time are linear maps into $\mathbb R^m$. Exact noiseless recovery of both target and source for every admissible pair requires $m\ge2r$.

**Proof.** Each label map must have rank $r$; otherwise its source is already nonidentifiable when that label is known. For two labels, their image subspaces have intersection dimension at least (2r-m), by the dimension formula for a sum of subspaces. If $m<2r$, choose a nonzero vector in that intersection. Its two preimages are nonzero sources with different labels and identical data. $\square$

Thus this problem needs at least four real rows. The proposition is compatible with the old symmetric-pair rank-one obstruction but is stronger for the joint query: even three otherwise well-chosen rows cannot identify an arbitrary two-dimensional source and its label. It neither proves four rows sufficient nor asserts that 48 is optimal. Discrete source alphabets, a known source norm, or other restrictions would change the admissible model and need a separate argument.

## 7. Validation and limits

The standard-library checker rechecks the inherited rational source certificates and all new exact bounds. Eight focused tests include altered acquisition/noise/certificate rejection, a separately assembled noncommuting finite graph, a whole-source-subspace Arb exponential control, missing-moment envelopes, centroid perturbations, and exact low-dimensional collisions. The full-grid diagnostic independently rebuilds outputs by the finite graph stencil on 1,002,001 states at two times and two extreme target positions; its decoder first recovers the label and then constructs the corresponding inverse. Those finite tests support implementation review; (1)–(9), not the sampled cases, establish the uniform mathematical result.

The 50 and 48 rows must be directly available for the stated acquisition savings. Computing them from an already measured complete modal vector is post-processing. They remain global $x$-averages, not fully local point detectors. Time is known exactly; subcell placement, source modes beyond two, calibration errors, and arithmetic error of a deployed least-squares implementation are outside the present certificate. The new degree-160/180 exponential evaluations are replayed exactly; the inherited central Arb coefficient-generation premises retain their previous audited replay status. No claim of empirical hardware validation, globally minimal bank size, or literature priority is made.

The next justified objective is to move from these consecutive asymmetric banks to separated rows while preserving an explicit all-source label-separation margin. Such a bank needs a decoder for the full union of target-dependent two-dimensional image spaces; the consecutive energy centroid cannot simply be reused after arbitrary gaps.
