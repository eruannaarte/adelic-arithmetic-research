# Eleven separated rows: transfer from the full finite model to joint recovery

## 1. Experiment, approximation, and theorem

Use the same finite diffusion model as the previous resolution packages:
\[
H_f=I_y\otimes L_x+L_y\otimes V,\qquad
T_j(\tau)u=\alpha(\tau)(I_y\otimes e^T)e^{-\tau H_f}(\delta_j\otimes Uu),
\quad \alpha(\tau)=(1+\tau)^{1/4}.
\]
Both finite paths have 1,001 vertices. Their Laplacians have edge weight one and endpoint degree one. At midpoint $x_i=(i+1/2)/1001$, $V_{ii}=1+(4/5)x_i$. The vector $e$ is the unit constant vector. The two columns of $U$ are the normalized midpoint cosine modes one and two, so $U^TU=I$ and $e^TU=0$.

The known time is any real $\tau\in[1,2]$. The unknown target index is $j\in\{490,\ldots,510\}$; the source is any nonzero $u\in\mathbb R^2$. Acquire exactly the eleven real spatial-average rows
\[
I=\{485,488,491,494,497,500,503,506,509,512,516\}.
\]
These are separated and asymmetric. Every row retains the same global $x$-average and original output normalization. Let $A_j=P_I T_j$.

The source calibrations remain
\[
S_0=I,\quad S_1=\operatorname{diag}(1+\pi^2,1+4\pi^2),\quad
S_2=\operatorname{diag}\!\left(1+4n^2\sin^2\frac{\pi}{2n},
                              1+4n^2\sin^2\frac{\pi}{n}\right).
\]
Each is at least $I$, and both H1 calibrations are at most $41I$. For the latter claim, $\sin x\le x$ gives $S_2\le S_1$ and $\pi<22/7$ gives $1+4\pi^2<41$. The familiar upper bound on $\pi$ can itself be checked from the positive integral
\[
0<\int_0^1\frac{x^4(1-x)^4}{1+x^2}\,dx=\frac{22}{7}-\pi,
\]
whose evaluation follows by polynomial division and integration of $(1+x^2)^{-1}$.

The new certificate constructs exact rational polynomial maps $P_j(\tau)$ and the physical approximate maps $\widetilde A_j(\tau)=\alpha(\tau)P_j(\tau)$. It proves, uniformly over all times and targets,
\[
\|A_j-\widetilde A_j\|_2<\rho:=10^{-9},                                      \tag{1}
\]
\[
\lambda_{\min}(\widetilde A_j^T\widetilde A_j)>
\mu_0:=\left(\frac{19}{16}\right)^2\frac7{10^8}
       =9.87109375\cdot10^{-8},                                             \tag{2}
\]
and, for every distinct pair $j,k$,
\[
\lambda_{\min}\!\left(
[\widetilde A_j,-\widetilde A_k]^T[\widetilde A_j,-\widetilde A_k]\right)>
\lambda_0:=\left(\frac{19}{16}\right)^2\frac1{10^{11}}.                       \tag{3}
\]
There are 21 individual cases and 210 pair cases. Source whitening gives (2)–(3) divided by 41 for either H1 calibration; (1) remains valid in either source norm because $S_m\ge I$.

**Theorem.** Under sensor noise $\|\epsilon\|_2\le3\cdot10^{-7}\|u\|_2$, the eleven rows identify the target and recover the source with relative L2 error below $10^{-3}$. Under either separately calibrated assumption $\|\epsilon\|_2\le3\cdot10^{-8}\|u\|_{S_m}$, they do the same with relative $S_m$ error below $10^{-3}$. These claims also admit an additional **conditional** computed-data error of norm at most $10^{-9}\|u\|_{S_m}$. This last allowance is a budget to be verified by an implementation, not a claim that arbitrary floating arithmetic satisfies it.

The decoder uses target-dependent image-space feasibility, proved in Section 6. It does not reuse the former centroid after deleting intermediate rows. Eleven is a proved sufficient number, not an optimum; the previous four-row necessary bound still applies to unrestricted joint recovery.

## 2. A periodic transverse surrogate and its complete image error

Keep the exact 1,001-cell $x$ path but temporarily replace the transverse path by the cycle of length $N=64$. Its Fourier frequencies have
\[
\omega_\ell=4\sin^2(\pi\ell/N),\qquad A_\ell=L_x+\omega_\ell V.
\]
The unnormalized kernel at displacement $d$ is
\[
K_d(\tau)=\frac1N\sum_{\ell=0}^{N-1}e^{2\pi i\ell d/N}
\,e^T e^{-\tau A_\ell}U.                                                   \tag{4}
\]
It is real and even in $d$. Opposite frequencies combine to the cosine weights used in the producer; the Nyquist mode has weight $(-1)^d/N$.

The zero mode vanishes exactly. Since $L_x e=0$, $e^T e^{-\tau L_x}=e^T$, and the midpoint cosine sums give $e^TU=0$. Their zero means and orthonormality follow directly from the finite geometric sum of complex exponentials. An approximately zero computed mode is not substituted for this identity.

We now charge all periodic images. For complex $z\ne0$, define
\[
B(z)=L_x+(2-z-z^{-1})V,\qquad F(z)=e^{-\tau B(z)}.
\]
On $|z|=a>1$, its Hermitian part obeys
\[
\operatorname{Re}\langle v,B(z)v\rangle
\ge-v_*(a+a^{-1}-2)\|v\|^2,\qquad v_*=9/5.
\]
Indeed $L_x$ is positive semidefinite and the real part of $2-z-z^{-1}$ is at least $2-a-a^{-1}$. Differentiating the squared norm of the finite-dimensional complex evolution yields
\[
\|F(z)\|_2\le \exp\{\tau v_*(a+a^{-1}-2)\}.
\]
The same bound holds on $|z|=1/a$. Cauchy's Laurent coefficient formula therefore bounds every coefficient operator by
\[
\|F_d\|_2\le a^{-|d|}\exp\{\tau v_*(a+a^{-1}-2)\}.                           \tag{5}
\]
The Laurent series converges absolutely on the unit circle. Averaging its values on the $N$th roots of unity selects exactly the coefficients whose indices agree modulo $N$. Thus (4) is the sum of the infinite-lattice kernel and **all** its images, not a finite-image approximation.

Every retained displacement satisfies $|d|\le26$. Summing (5) over nonzero images and taking $a=8$ gives the uniform row-operator bound
\[
E_{\rm image}\le
\exp\!\left\{\frac{18}{5}(8+8^{-1}-2)\right\}
\frac{8^{-38}+8^{-90}}{1-8^{-64}}
<10^{-24}.                                                               \tag{6}
\]
The expression increases with $|d|$ on this range, so its endpoint value bounds all selected rows and labels. Source and observation vectors have norm one. The checker verifies the exponential upper bound by a positive rational Taylor sum with a complete geometric remainder.

The Laurent coefficients describe the infinite transverse graph: expanding the exponential in powers gives the same finite-length walks, with the same exact finite $x$ dynamics. To compare it with the actual transverse path, uniformize the single-response generator at rate $q=28/5$. Its transition operator is symmetric, nonnegative, stochastic, and an L2 contraction; the infinite version is also contractive by Jensen's inequality and the unit column sums.

For a target at boundary distance at least 490, finite and infinite walk powers applied at the target agree through order 490. A walk must reach the endpoint and take another step to encounter its modified diagonal or cross it. Therefore, with $\mu=2q=56/5$, their unnormalized output difference in norm is at most
\[
E_{\rm finite}\le
2\sum_{r\ge491}\frac{\mu^r}{r!}
\le\frac{2\mu^{491}}{491!(1-\mu/492)}
<10^{-500}.                                                              \tag{7}
\]
The exponential prefactor has been conservatively discarded. This is a bound on the actual finite boundary error, for every source direction. It does not assume the physical path is periodic.

## 3. Complete model-to-Taylor reconstruction

All polynomial coefficients are reconstructed at the single center $c=3/2$. For each nonzero Fourier mode,
\[
\omega_\ell I\le A_\ell\le (4+(9/5)\omega_\ell)I.
\]
Choose spectral center $c_\ell=2+(7/5)\omega_\ell$ and radius
$r_\ell=2+(2/5)\omega_\ell$. Then $\|A_\ell-c_\ell I\|_2\le r_\ell$ and
$c_\ell-r_\ell=\omega_\ell$. Truncating the shifted exponential at degree 80 gives the operator error
\[
\left\|e^{-cA_\ell}-e^{-cc_\ell}
  \sum_{h=0}^{80}\frac{[-c(A_\ell-c_\ell I)]^h}{h!}\right\|_2
\le e^{-c\omega_\ell}\frac{(cr_\ell)^{81}}{81!}.                             \tag{8}
\]
This follows from the scalar positive-series bound
$\sum_{h>80}x^h/h!\le e^x x^{81}/81!$ and the symmetric spectral theorem.
It never commutes $L_x$ with $V$.

Applying $(-A_\ell)^k/k!$ to the enclosed center state gives each Taylor coefficient through order 32. The error (8) is multiplied by
$(4+(9/5)\omega_\ell)^k/k!$ before projection onto $e$. Outward Arb tridiagonal actions, finite Fourier sums, and these complete exponential remainders enclose all 27 displacement kernels and both source columns.

Each coefficient interval is rounded outward to a rational grid of size $10^{-30}$, with width at most that amount. Its exact rational midpoint defines the exported polynomial coefficient. On $|\tau-c|\le1/2$, the total midpoint coefficient error is less than $2\cdot10^{-30}$ per matrix entry.

The omitted time series is bounded independently of the generator norm. For a symmetric positive semidefinite generator $H$ and $s\ge1$,
\[
\frac{\|H^{33}e^{-sH}\|_2}{33!}\le1,
\]
because $e^\lambda\ge\lambda^{33}/33!$ for $\lambda\ge0$. Taylor's integral remainder on $[1,2]$ therefore gives the operator remainder
\[
E_{\rm time}\le 2^{-33}.                                                    \tag{9}
\]
The finite cycle generator meets these hypotheses. This proves continuous-time coverage; testing finitely many times is not its replacement.

Combining (6)–(9), each unnormalized entry of the two-column target map differs from the rational polynomial by at most
\[
e_* = 2^{-33}+10^{-24}+10^{-500}+2\cdot10^{-30}.
\]
The exact normalization obeys $19/16<\alpha(\tau)<4/3$, as verified by taking fourth powers. The physical operator norm is bounded by its Frobenius norm, so
\[
\|A_j-\alpha P_j\|_2^2
\le (4/3)^2\,22\,e_*^2 <10^{-18}.                                         \tag{10}
\]
This proves (1), with the declared $10^{-9}$ error already expressed in the **normalized physical output**. It includes all four approximation sources, rather than an uncharged time or infinite-tail term.

## 4. Exact whole-cell preconditioned floors

For each target use the polynomial matrix $M=P_j$; for a target pair use
$M=[P_j,-P_k]$. Its columns number $d=2$ or $d=4$. The complete time interval is covered separately for every case by rational cells $[a,b]$.

At the center $c_0=(a+b)/2$, an ordinary floating Cholesky factor proposes a preconditioner. Its entries are rounded to exact decimal rationals, giving $R$. The floating proposal has no authority: all following quantities are recomputed exactly from the polynomial.

Let $B_0=M(c_0)R$ and suppose the exact row-sum defect satisfies
\[
\|I-B_0^T B_0\|_\infty\le d_0<1-\gamma^2,
\qquad \gamma=999999/10^6.
\]
Since the defect is symmetric, the row bound implies
$\|B_0v\|>\gamma\|v\|$ for every nonzero $v$. In particular $R$ is invertible.

Translate each exact polynomial to the cell center and multiply by $R$
**before** taking absolute values. For $|h|\le r=(b-a)/2$,
\[
M(c_0+h)R-B_0=\sum_{q=1}^{32}B_qh^q.
\]
The scalar entry bounds $\sum_{q\ge1}|(B_q)_{ij}|r^q$ give an exact squared
Frobenius bound $E^2$ on that difference. Let rational $e,w\ge0$ satisfy
\[
e^2\ge E^2,\qquad
w^2\ge f\|R\|_F^2,\qquad e+w<\gamma.                                      \tag{11}
\]
Then, for any nonzero $v$,
\[
\|M(\tau)v\|\ge
(\gamma-e)\|R^{-1}v\|
\ge \frac{\gamma-e}{\|R\|_F}\|v\|>\sqrt f\,\|v\|.
\]
Thus the unpreconditioned Gram floor exceeds $f$ throughout the cell.

The accepted source floor is $7\cdot10^{-8}$ and the accepted pair floor is
$10^{-11}$. The independent consumer uses a different polynomial-translation algorithm (Horner composition rather than binomial translation), rechecks every rational inequality (11), and requires each individual case's sorted cells to cover exactly $[1,2]$ without overlap or gaps. A union of different cases' cells would not suffice.

The completed certificate contains 46 nonempty time cells and 895 individual whole-cell records. Together they cover all 231 cases. Multiplication by
$\alpha^2>(19/16)^2$ proves the physical floors (2)–(3).

## 5. Transfer to all three calibrated uncertainty models

For either H1 source metric $S$, $S\le41I$ gives
\[
\widetilde A_j^T\widetilde A_j\ge(\mu_0/41)S.
\]
The same argument on the direct sum of two source spaces gives the pair floor
$\lambda_0/41$ after whitening both source blocks. No extra measurements or output renormalization are introduced.

Write $\eta_m=3\cdot10^{-7}$ for L2 and $\eta_m=3\cdot10^{-8}$ for either H1 calibration. If a computed-data error bound $\xi_m\le10^{-9}$ is independently available, the actual observation lies within
\[
\|y-\widetilde A_j u\|\le
\delta_m\|u\|_{S_m},\qquad
\delta_m=\eta_m+\rho+\xi_m.                                                \tag{12}
\]
Taking $\xi_m=0$ gives the pure sensor/model guarantee.

If two different target/source pairs fitted the same observation, (12) and the triangle inequality would imply
\[
\|\widetilde A_j u-\widetilde A_k v\|
\le\delta_m(\|u\|_{S_m}+\|v\|_{S_m})
\le\sqrt2\,\delta_m
       \sqrt{\|u\|_{S_m}^2+\|v\|_{S_m}^2}.
\]
But (3), divided by 41 when appropriate, gives a strictly larger lower bound. The exact checker verifies
\[
\lambda_m>2\delta_m^2,\qquad
\delta_m^2<10^{-6}\mu_m.                                                  \tag{13}
\]
Thus target tubes are disjoint. After identifying the target, the
least-squares inverse of $\widetilde A_j$ has calibrated gain at most
$1/\sqrt{\mu_m}$. Applying it to (12) proves relative source error below
$10^{-3}$.

These inequalities use the same observation error in both stages. They do not assume independent source-coordinate or target-query noises. A shared model perturbation is conservatively enclosed by (1); regarding its restrictions separately only enlarges the admissible sets.

## 6. A feasible-label decoder, including its boundary cases

The executable rational decoder accepts the unnormalized data $z=y/\alpha$ at an exactly specified rational time. Dividing the data requires either exact mathematical normalization or a charged computed-data error. The theorem above applies to every real known time; the rational input interface does not assert a bound on unprovided timing error.

For L2 set $b^2=(\delta_0/(19/16))^2$. For H1 use the conservative Euclidean
source envelope $b^2=41(\delta_m/(19/16))^2$, since $\|u\|_{S_m}\le\sqrt{41}\|u\|_2$. This can enlarge feasible sets while still preserving the disjointness guaranteed by (13).

For a candidate map $P=P_j(\tau)$ and nonzero $z$, a compatible nonzero source exists precisely when
\[
\min_u\{\|z-Pu\|^2-b^2\|u\|^2\}\le0.
\]
The certified floor makes $P^TP-b^2I$ positive definite. Completing the square evaluates this minimum exactly as
\[
\|z\|^2-(P^Tz)^T(P^TP-b^2I)^{-1}(P^Tz).                                  \tag{14}
\]
The true label satisfies (14). Other labels are excluded by the pair floor applied to these conservatively enlarged Euclidean tubes. Once one label survives, ordinary least squares uses $(P^TP)^{-1}P^Tz$, not the minimizer in (14), for the source estimate.

A zero observation is rejected. With nonzero source and error smaller than the source floor, it is outside the stated valid-data model; allowing $u=0$ would otherwise make the feasibility test vacuous at zero. An empty feasible-label set denotes incompatible data/budgets. More than one label causes abstention. No returned label depends on a true-target oracle.

The same argument works with a fixed absolute sensor allowance if a positive source-amplitude lower bound is supplied: $\|\epsilon\|\le\eta_m a_{\min}$ and
$\|u\|_{S_m}\ge a_{\min}$. There is no positive absolute-noise localization guarantee uniformly down to vanishing source amplitude.

## 7. Meaning and verification limits

The reduction is from 48 consecutive rows to 11 separated rows, a 77.08% reduction in directly acquired spatial-average channels. The same sensor allowances and the same $10^{-3}$ source-error targets are retained. No claim is made that 11 is minimal or that all row subsets of that size work.

Direct acquisition requires these eleven spatial averages to be available. Forming them from an already acquired full modal vector would be post-processing. Each row still averages globally over $x$; this is not a theorem about eleven fully local point detectors.

The physical finite-x dynamics, all periodic mode coefficients, and the complete analytic remainders are reconstructed in the new package. The consumer proves exact consequences of the outward coefficient premises and their explicit model connection. Their hash binds the premise but does not prove it. Interval inclusion arithmetic remains a trusted numerical component. Floating discovery and forward examples are diagnostic; the continuous-time floors and all-source pair separation come from the stated proofs and exact checks.

The next research question is whether a smaller bank or larger source band can satisfy the same complete image-space certificate. This package completes the eleven-row result before making any such claim.
