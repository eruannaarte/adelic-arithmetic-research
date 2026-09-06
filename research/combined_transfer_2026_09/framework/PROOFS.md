# Joint-budget transfer with demonstrated acquisition consequences

This is a self-contained corollary of the existing
[restriction and nuisance theorem](../../transfer_theorem_2026_09/framework/PROOFS.md),
[uncertain-acquisition extension](../../uncertain_transfer_2026_09/framework/PROOFS.md)
and [directional inverse extension](../../structured_transfer_2026_09/framework/PROOFS.md).
Its purpose is to state precisely which guarantees the new combined
certificates establish. The argument uses finite-dimensional projection,
Cauchy--Schwarz and verified complete model bounds. No historical novelty or
optimality assertion is made.

## 1. The answer set and the experiment come first

An admissible explanation `theta` includes the source and every bounded,
shared or correlated uncertainty. Its requested answer is `q(theta)`. Let

\[
y=f(\theta)+B_\theta\beta+e,\qquad
\|e\|_W\le\eta_\theta,
\]

where `W` is positive definite and `beta` is unrestricted for each
explanation. Write `Y(theta)` for this allowed observation set. For a promised
observation in their union, the exact answer set is

\[
\mathcal Q(y)=\{q(\theta):y\in Y(\theta)\}.
\]

Restricting or processing data must retain the actual physical error set.
For a linear restriction `R`, that set is `R{e:||e||_W<=eta}`; it is not
automatically an independently rescaled ball in the retained coordinates.
For example, for `r` in the range of `R`, its least original squared noise
cost is

\[
\min_{Re=r}\|e\|_W^2
=r^*(RW^{-1}R^*)^\dagger r. \tag{1}
\]

To prove (1), put `A=RW^(-1/2)` and `h=W^(1/2)e`. The minimum-norm solution
of `Ah=r` is `A^*(AA^*)^dagger r`: it is feasible and orthogonal to `ker A`.
Every other solution adds a vector in that kernel and increases the squared
norm. Unrestricted retained nuisance is eliminated by minimizing this cost
over `r-RB_theta beta`. The preceding theorem gives the equivalent exact
profiled projection and the criteria for interchanging restriction and
elimination. A newly specified sensor with a different physical noise model
must instead state that model explicitly.

Suppose a fixed valid processing map `L`, including any exact nuisance
operation, and a verified computed output `v` satisfy

\[
LB_\theta=0\quad\hbox{for every admitted }\theta,
\qquad v=c(\theta)+d(\theta)+r(\theta)
\tag{2}
\]

for every actual explanation. Bounds on `d,r` must include the true clock and
model, all omitted source terms, and every relevant processing error. Shared
coordinates remain shared within each explanation. Competing explanations
may have different allowed uncertainty values.

**Outer-answer transfer.** If certified sets `C(theta)` contain every
right-hand side of (2), then

\[
\mathcal Q(y)\subseteq\{q(\theta):v\in C(\theta)\}. \tag{3}
\]

**Proof.** Substitute each admissible explanation of `y` in (2). It passes
its outer feasibility test, so its answer belongs to the right side. Another
proved outer inclusion composes by transitivity. A singleton right side
determines the discrete query. A supplied enclosing ball gives its continuous
absolute error bound. A multiple-answer outer set is an inconclusive
certificate; it is not proof that actual alternatives exist. QED.

Exact nuisance removal is a substantive premise. If `LB_theta beta0` is
nonzero for some admitted explanation and nuisance direction, scaling
`beta0` makes its processed output unbounded. No finite uniform leakage
allowance is then available without changing the nuisance-amplitude model or
the processing. A small numerical residual does not remove this obstruction.

## 2. Relative source recovery with structured physical directions

In the source-relative branch, let `j` be a finite label and `u` any nonzero
real source vector. All matrices and norms below are in the declared final
observation space and Euclidean source coordinates. Suppose (2) has the form

\[
v=A_j u+D_j(z)u+e_j,\qquad
D_j(z)=\sum_r z_rD_{jr},\quad z\in Z_j,
\quad\|e_j\|\le b_j\|u\|. \tag{4}
\]

Here `b_j` contains the unstructured sensor, approximation, verified
processing and complete nonlinear remainders. Suppose

\[
A_j^*A_j\succeq\mu_j I>0,\qquad
F_j\ge\sup_{z\in Z_j}\|D_j(z)\|,\qquad
V_j\ge\sup_{z\in Z_j}\|A_j^\dagger D_j(z)\|,
\quad\delta_j=b_j+F_j. \tag{5}
\]

**Joint relative-transfer corollary.** Assume for each unequal-label pair
there are positive numbers `c_jk,c_kj` such that

\[
[A_j,-A_k]^*[A_j,-A_k]
\succ\operatorname{diag}(c_{jk}I,c_{kj}I),
\qquad {\delta_j^2\over c_{jk}}+
       {\delta_k^2\over c_{kj}}\le1. \tag{6}
\]

Then every promised reading determines its label. Its ordinary nominal
least-squares estimate obeys

\[
{\|\widehat u-u\|\over\|u\|}
\le V_j+{b_j\over\sqrt{\mu_j}}. \tag{7}
\]

**Proof.** The correct observation belongs to the tube
`||v-A_j u||<=delta_j||u||`. If two different tubes met, their center
difference would be at most `delta_j||u||+delta_k||w||`. Weighted
Cauchy--Schwarz and (6) bound its square above by
`c_jk||u||^2+c_kj||w||^2`, contradicting the strict Gram inequality.
Thus at most one label survives, and (3) guarantees the true one survives.
Since `A_j^dagger A_j=I`, the estimate error equals
`A_j^dagger D_j(z)u+A_j^dagger e_j`. Apply (5) and
`||A_j^dagger||<=1/sqrt(mu_j)` to obtain (7). Any additional solve error
must be verified and charged; the present spatial decoder uses exact
rational solves. QED.

For a linear query `Q_j u`, the same proof replaces `V_j` by
`sup_z ||Q_j A_j^dagger D_j(z)||` and the remaining inverse gain by
`||Q_j A_j^dagger||`. This remains a source-relative estimate unless an
absolute source-amplitude bound is supplied.

For a parameter rectangle, each norm in (5) is convex in `z`. Expressing a
point as a convex combination of corners proves that bounds on all joint
corner matrices suffice. A nonlinear map must first be expanded with its
complete remainder in `b_j`; convexity of its linearized term does not bound
an omitted nonlinear term.

## 3. Absolute weighted integer recovery with a verified inverse

The arithmetic branch uses an absolute complex weighted reading norm, not
the spatial branch's source-relative norm. Let `X` be the actual finite
augmented matrix, containing arithmetic columns and the exact polynomial
nuisance basis. Let

\[
G=X^*WX\succeq fI>0.
\]

After complete known centering, write the actual data as

\[
y-\widetilde u=X\theta_0+h+e,
\qquad\|e\|_W\le\Delta. \tag{8}
\]

The vector `h` is the entire centered arithmetic tail. Suppose its decoded
query coordinates satisfy

\[
\left|n^2(G^{-1}X^*Wh)_n\right|\le A_n,
\qquad n=2,\ldots,50, \tag{9}
\]

uniformly over the declared infinite source class. The first source
coefficient is known; its constant arithmetic column also represents the
unrestricted constant nuisance, so that fitted coordinate is not returned
as an unknown arithmetic answer. For a rational proposed solution
`theta_tilde`, verify from the actual data and actual matrix that

\[
\|G\widetilde\theta-X^*W(y-\widetilde u)\|_2\le\rho_N. \tag{10}
\]

**Joint integer-transfer corollary.** Every unknown integer query obeys

\[
|n^2\widetilde\theta_n-a(n)|
\le E_n:=A_n+n^2\left({\Delta\over\sqrt f}+{\rho_N\over f}\right).
\tag{11}
\]

Thus all 49 integers are recovered by nearest-integer rounding when, for
each `n=2,...,50`, the exact strict gates

\[
m_n:=\tfrac12-A_n-{n^2\rho_N\over f}>0,
\qquad n^4\Delta^2<m_n^2 f \tag{12}
\]

hold. The same bound gives an explicit error disk when a rounding gate does
not pass, but such failure alone proves no indistinguishable sources.

**Proof.** Subtract `G theta_0` from (10) using (8). The error in the proposed
solution is the sum of the complete decoded tail, `G^(-1)X^*W e`, and a
normal-residual term of norm at most `rho_N/f`. The weighted least-squares
gain is at most `1/sqrt(f)`, since the whitened matrix `W^(1/2)X` has smallest
singular value at least `sqrt(f)`. Apply (9) coordinatewise and multiply by
`n^2` to obtain (11). Conditions (12), with their sign checks, are exactly
`E_n<1/2` written without an uncertified square root. The real part is then
within less than one half of its true integer. QED.

The complete actual uncertainty budget used here is

\[
\Delta=\eta+\kappa+\Xi+\tau_W(h)
       +B\,K_{W,p}\!\left(\Omega(1+h/10^{14})\right). \tag{13}
\]

These terms charge, respectively, sensor error, declared model mismatch,
digital centering, complete source-clock distortion, and approximation of
the declared sinusoidal drift family by the degree-`p` nuisance space.
All may act together. Their norm sum is a containing error set, not an
independence or noise-distribution assumption. Altering `p` changes `X`, `f`,
`A_n`, the approximation and the actual residual; changing only the
approximation factor is not a valid degree comparison.

## 4. Complete clock blocks and their transfer scope

For the source `sum a(n)n^(-2-it)` with every integer
`0<=a(n)<=d_14(n)`, write `n=2^k m`, `m` odd, and
`u_k=binom(k+13,13)/4^k`. In each orbit the actual derivative coefficients
are bounded by

\[
{d_{14}(m)\over m^2}\,u_k(\log m+k\log2).
\]

For each shared clock corner put `d_j=±1±t_j/1000`. On the actual physical
grid, bounds `gamma_l` on the normalized correlations at lags
`l log2`, `1<=l<=31`, give

\[
\left\|d\sum_{k=0}^{31}c_k e^{-ik t\log2}\right\|_W^2
\le S_2\Lambda\sum_{k=0}^{31}|c_k|^2,
\qquad\Lambda=1+2\sum_{l=1}^{31}\gamma_l. \tag{14}
\]

Expanding the square and applying `2|c_k c_l|<=|c_k|^2+|c_l|^2` proves
(14). It holds for arbitrary actual coefficients. Their squared magnitudes
can therefore be replaced monotonically by the envelope; no multiplicative
ratio is imposed on the unknown coefficients.

Let `U^2=sum_(k<32)u_k^2`, `V^2=sum_(k<32)k^2u_k^2`. The complete geometric
tail bounds `T0,T1` control `sum_(k>=32)u_k` and `sum_(k>=32)k u_k`. The
complete positive odd-integer series are

\[
O=(3\zeta(2)/4)^{14},\qquad
O_1=14(3\zeta(2)/4)^{13}
\left(\tfrac34\sum_n{\log n\over n^2}
      -\tfrac14\log2\,\zeta(2)\right).
\]

Triangle inequalities first over retained coefficients, then over omitted
valuations and all odd starting integers give

\[
\mathcal B=\sqrt\Lambda(O_1U+\log2\,OV)
                 +O_1T_0+\log2\,OT_1.
\]

Absolute convergence follows by expanding fourteen absolutely convergent
positive Dirichlet series. The same expansion gives the complete second
derivative envelope
`D2=14 Z^13 L2+182 Z^12 L^2`, where
`Z=sum n^-2`, `L=sum log(n)n^-2` and `L2=sum log(n)^2 n^-2`.
The exact exponential remainder `|exp(-iz)-1+iz|<=z^2/2` and the fourth
direction moment `S4` therefore yield

\[
\tau_W(h)\le h\,{\mathcal B\sqrt{S_2}\over10^{11}}
       +h^2\,{D_2\sqrt{S_4}\over2\,10^{22}}. \tag{15}
\]

Convexity covers the entire shared slope/offset rectangle. Every omitted
valuation and odd starting integer remains in (15); 32 is a computational
block length. [The complete block proof](../blocks/PROOFS.md) supplies the
explicit rational tails and all outward numerical premises.

An affine change of time preserves every polynomial of degree at most `p`,
so the unrestricted polynomial nuisance is still exactly representable.
Its weighted orthogonal quotient is a contraction; (15) remains valid after
that quotient. This asserts no additional phase gain after projection. In
particular, removal of the common orbit phase `exp(-it log m)` is norm
invariant before projection, but need not be after projection. A future
projected-phase construction must retain that dependence or prove a valid
replacement bound.

## 5. The demonstrated consequences

The [six-row spatial certificate](../spatial/PROOFS.md) establishes (4)--(7)
for rows `485,493,499,501,507,515`, all 21 target labels, all nonzero two-mode
sources and all admissible nominal and true times in [1,2]. At sensor radius
`3e-8`, clock radius `1e-8` and potential radius `1e-8`, the newly enlarged
pair tube `3.25e-8` contains the complete radius `<3.243001712e-8`.
The relative source error is `<0.000852831068`. Its coarse inverse control
also passes, at `<0.000863601842`; directional inversion is not essential
for this particular small box.

The [degree-twelve arithmetic consequence](../blocks/REPORT.md) uses (15)
inside (13), with `h=120`, `B=4000`, `Omega=3`, `eta=4e-5`, `kappa=1e-6`,
`Xi=1e-20` and a separately verified normal residual. Both windows pass all
49 gates, with errors `<0.447153367` and `<0.496198708`. At precisely the same
contract, the preceding outer-window pair formula exceeds `0.506493579` and
fails its sufficient gate.

The [degree-eleven construction](../degree11/PROOFS.md) recomputes its own
inverse, complete tail channels and parity-correct approximation. At the
base clock `h=1`, with the same sensor, mismatch and frequency allowances,
`B=4000` fails the complete all-coordinate sufficient test; the displayed
orbit-clock upper bounds are `1.092523325` and `1.142117571`. At `B=500`,
the same construction passes all 49 gates, with errors `<0.445865330` and
`<0.494913819`. Thus degree choice is a quantified cost--amplitude tradeoff,
not a universal lower-degree impossibility theorem.

These are three instances of one transfer discipline: declare the joint
experiment, remove only the nuisance justified by that experiment, retain
complete model errors, and verify the final query gate. The original five
paths remain distinct model families; their connection is recorded in the
[integrated report](../REPORT.md), rather than identified by equal-looking
numerical tolerances.
