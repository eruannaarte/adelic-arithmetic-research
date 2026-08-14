# Operational Information Geometry V

## Scale flow, continuum response, and protocol boundaries

- **Research, theorem development, computation, and writing:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Date:** 14 August 2026
- **Status:** research manuscript and computer-assisted evidence; not peer reviewed
- **Canonical laboratory:** `operational_information_geometry_v.py`
- **Independent continuum laboratory:** `oig_v_scaling_continuum.py`
- **Outward-rounded adjacent certificate:** `oig_iv_certificate.py`

## Abstract

Operational Information Geometry begins with a finite premise: states are
geometrically separated only to the extent that a declared experiment can
distinguish their histories. Stage IV introduced an exactly one-way subsystem
response inside a symmetric continuous-time Markov generator. This stage asks
which parts of that construction survive refinement, which depend on the
measurement protocol, and which disappear under another limit.

The answer is deliberately mixed. For the cell-centred path discretization,
the correct fixed-domain scaling is

\[
 x_j=\frac{j+1/2}{n},\qquad A_n=n^2L_n,
 \qquad t_{\rm graph}=n^2\tau,
\]

with graph distance divided by \(n\) and probability vectors converted to
density-normalized \(L^2\) channels. The low spectrum then converges to the
Neumann interval spectrum with an explicit \(O(n^{-2})\) bound. A transient
spectral dimension has noncommuting limits: it is zero at arbitrarily short
time for every fixed finite chain, but tends to the number of product factors
in the mesoscopic window \(n^{-2}\ll\tau_n\ll1\).

The directed response admits an exact target-mode reduction to matrices of size
\(n\). For a smooth single-mode background, its first continuum causal jet has
an exact parity rule, and fixed-mode response Gramians converge numerically at
second-order rate. A target atom behaves differently: its raw first-jet norm
diverges as \(n^{5/2}\), although positive-time heat smoothing yields stable
low-mode responses. Thus refinement and the initial-time limit do not commute.

Stage IV's Poisson jump-count envelope remains exact but becomes physically
vacuous under diffusive scaling. A signed-displacement exponential-martingale
argument replaces it with a finite-lattice leakage bound whose continuum radius
is proportional to \(\sqrt t\). Several protocol boundaries are also exact:
symmetry can leave a three-dimensional source subspace invisible; a stationary
target is silent to endpoint marginals but visible to jump activity; adjoint
ports restore reciprocity for a symmetric propagator; and fixed linear
initial-state interventions have no nonlinear amplitude jet.

The result is not a spacetime theory. It is a sharper toy model of how an
operational geometry can possess a meaningful scale flow while retaining
explicit dependencies on preparation, regularity, sensor choice, and limit
order.

## 1. Status ledger

The manuscript keeps four epistemic categories separate.

### Proved analytically

1. the exact path spectrum and its \(O(n^{-2})\) low-mode error bound;
2. the fixed-system and mesoscopic spectral-dimension limits;
3. the target-mode response reduction;
4. the smooth first-jet parity rule;
5. the smooth-versus-atomic first-jet scaling laws;
6. the target-bandwidth causal-jet rank bound;
7. degeneration of the raw Poisson physical radius;
8. a finite-lattice signed-displacement leakage envelope;
9. expanding-domain flattening for a stretched modulation ramp;
10. the symmetry-invisibility, path-activity, conjugate-port reciprocity, and
    amplitude-linearity boundaries; and
11. an outward-rounded bracket for the Stage IV finite-grid E-design.

### Computed with independent tests

1. convergence of fixed low-mode response Gramians;
2. convergence of actual 99-percent leakage radii;
3. the rank-two reflection-symmetric response control;
4. endpoint-marginal silence versus nonzero path-activity response; and
5. the interval proof ledger on both exact and frozen binary64 time grids.

### Hypothesized, with evidence but no complete proof here

1. operator-norm convergence of fixed-mode response histories uniformly for
   \(t\ge t_0>0\); and
2. positive-time response convergence for mollified or atomic targets under
   an appropriate smoothing norm.

### Not claimed

No result identifies physical spacetime, derives relativity or quantum theory,
selects a fundamental number system, or establishes a new law of nature.

## 2. Three limits and one renormalization dictionary

Let \(L_n\) be the ordinary combinatorial Laplacian of the path on \(n\)
vertices. Three limits must not be conflated.

1. **Fixed-domain refinement:** \(h_n=1/n\), physical length one,
   \(A_n=h_n^{-2}L_n\), and fixed physical time \(\tau\).
2. **Infinite volume:** \(h\) stays fixed while \(n\to\infty\), so the domain
   length and boundary distance grow.
3. **Joint continuum/infinite volume:** \(h_n\to0\) and \(nh_n\to\infty\).

The third is not a formal consequence of the first two. It needs uniform
assumptions on localization, modulation, and observation.

For fixed-domain refinement, the operational dictionary is

| finite object | physical normalization |
|---|---|
| vertex \(j\) | \(x_j=(j+1/2)/n\) |
| generator \(L_n\) | \(A_n=n^2L_n\) |
| graph time | \(t_{\rm graph}=n^2\tau\) |
| graph distance | \(h_nd_{\rm graph}=d_{\rm graph}/n\) |
| sampled \(L^2\) density mode \(U\) | probability perturbation \(U/\sqrt n\) |
| probability marginal | density-normalized output multiplied by \(\sqrt n\) |

The cell-centred convention is material. Labelling the same endpoint rows with
spacing \(1/(n-1)\) converges to the same spectrum only with an \(O(n^{-1})\)
effective-boundary shift.

## 3. Exact path spectrum

### Theorem 3.1 — cell-centred Neumann spectrum

For \(0\le k<n\), define

\[
 u_{0,n}(j)=\frac1{\sqrt n},\qquad
 u_{k,n}(j)=\sqrt{\frac2n}
 \cos\!\left(\frac{\pi k(j+1/2)}n\right),\quad k\ge1.
\]

These vectors form an orthonormal eigenbasis of \(A_n=n^2L_n\), with

\[
 \mu_{k,n}=4n^2\sin^2\!\left(\frac{\pi k}{2n}\right).
\]

For every fixed nonzero mode,

\[
 0\le (\pi k)^2-\mu_{k,n}
 \le \frac{\pi^4k^4}{12n^2}.
\]

#### Proof

Substitution in the path difference equation gives the eigenpairs, including
the one-sided endpoint rows. Orthogonality is the discrete cosine transform.
Put \(x=\pi k/(2n)\). Since \(\sin x\le x\), the error is nonnegative. Also
\(\sin x\ge x-x^3/6\) on the relevant interval, hence
\(x^2-\sin^2x\le x^4/3\). Multiplication by \(4n^2\) gives the bound.
\(\square\)

For the first mode, the relative errors at \(n=8,16,32,64\) are respectively
\(1.2785\times10^{-2}\), \(3.2086\times10^{-3}\),
\(8.0293\times10^{-4}\), and \(2.0078\times10^{-4}\). Doubling \(n\)
divides the error by approximately four.

## 4. Spectral dimension is a scale-window statement

For a product of \(d\) identical path factors, remove the stationary mode and
define

\[
 S_n(\tau)=\sum_{k=0}^{n-1}e^{-\tau\mu_{k,n}},
 \qquad
 \Theta_{n,d}(\tau)=S_n(\tau)^d-1.
\]

The transient effective spectral dimension is

\[
 D_{n,d}(\tau)
 =-2\frac{d\log\Theta_{n,d}}{d\log\tau}
 =\frac{2\tau d E_n(\tau)S_n(\tau)^{d-1}}
        {S_n(\tau)^d-1},
\]

where \(E_n(\tau)=\sum_k\mu_{k,n}e^{-\tau\mu_{k,n}}\).

### Theorem 4.1 — the ultraviolet limits do not commute

For every fixed \(n\) and \(d\),

\[
 \lim_{\tau\downarrow0}D_{n,d}(\tau)=0.
\]

If instead \(\tau_n\downarrow0\) while

\[
 n^2\tau_n\longrightarrow\infty,
\]

then

\[
 \lim_{n\to\infty}D_{n,d}(\tau_n)=d.
\]

#### Proof

At fixed \(n\), \(S_n(\tau)=n+O(\tau)\) and \(E_n(\tau)=O(1)\), so the
explicit factor \(\tau\) forces the first limit to zero.

In the mesoscopic window, the modes contributing materially have
\(k=O(\tau_n^{-1/2})=o(n)\). Theorem 3.1 and a Gaussian tail split therefore
give the uniform asymptotics

\[
 S_n(\tau_n)\sim\frac1{2\sqrt{\pi\tau_n}},
 \qquad
 E_n(\tau_n)\sim\frac1{4\sqrt\pi\,\tau_n^{3/2}}.
\]

Since \(S_n\to\infty\), the removed stationary term is negligible. Substituting
the two asymptotics gives \(D_{n,d}\to d\). \(\square\)

The sample path \(\tau_n=n^{-3/2}\) makes both inequalities visible. For
three factors:

| \(n\) | 32 | 64 | 128 | 256 | 512 |
|---:|---:|---:|---:|---:|---:|
| \(D_{n,3}(n^{-3/2})\) | 2.7528 | 2.8387 | 2.9024 | 2.9435 | 2.9683 |

This resolves an ambiguity in finite spectral profiles. A finite chain has
dimension zero at its ultimate ultraviolet endpoint. The product dimension is
the stable value after separating lattice scale from observation scale; it is
not obtained by taking \(\tau\to0\) first.

## 5. One-way generator and exact modal response reduction

On the unit square, let

\[
 G_n=A_n\otimes I+(I+gD_n)\otimes A_n,
 \qquad D_n=\operatorname{diag}(x_0,\ldots,x_{n-1}),quad g\ge0.
\]

It is a symmetric Markov graph Laplacian. Formally, its continuum equation is

\[
 \partial_\tau p
 =\partial_x^2p+(1+gx)\partial_y^2p
\]

with reflecting boundaries. The \(x\)-marginal is autonomous.

Let \(A_nu_\ell=\mu_{\ell,n}u_\ell\), let \(q\) be a target background, let
\(H\) collect source directions, and write
\(\beta_\ell=u_\ell^{\mathsf T}q\). Use

\[
 J_A=H\otimes q,
 \qquad M_B=\mathbf1^{\mathsf T}\otimes I.
\]

### Theorem 5.1 — target-mode reduction

In the target eigenbasis, the \(\ell\)-th output row of the response is

\[
 \widehat R_\ell(\tau)
 =\beta_\ell\mathbf1^{\mathsf T}
 e^{-\tau K_{\ell,n}}H,
 \qquad
 K_{\ell,n}=A_n+\mu_{\ell,n}(I+gD_n).
\]

The stationary row \(\ell=0\) vanishes on every mass-zero source direction.
The all-time visible source quotient is the span of the Krylov rows

\[
 \mathbf1^{\mathsf T}K_{\ell,n}^kH,
 \qquad \beta_\ell\ne0,quad k\ge0.
\]

#### Proof

Conjugating only the target coordinate by its orthogonal eigenbasis makes
\(G_n\) a direct sum of the displayed \(K_{\ell,n}\). The target background
contributes \(\beta_\ell\), and marginalization contracts the source factor
with \(\mathbf1^{\mathsf T}\). Analyticity of the exponential identifies the
visible row space with the corresponding finite Krylov span. \(\square\)

This reduction replaces dense \(n^2\)-state exponentials with target-mode
problems of size \(n\). It also explains stationary silence, target-bandwidth
effects, symmetry-induced rank loss, and the continuum response used below.

## 6. Density-normalized fixed-mode response

Let the source modes be the first five continuum-normalized cosines and let the
target density be

\[
 \rho_B(y)=1+a\sqrt2\cos(\pi y),
 \qquad a=0.4,quad g=0.8.
\]

At cell centres, source density modes become probability injections after a
factor \(n^{-1/2}\), while the measured target probability marginal is
multiplied by \(n^{1/2}\). These factors remove the trivial scaling that would
otherwise arise from changing the number of cells.

For 30 fixed times from \(0.001\) to \(0.5\), the response Gram relative to an
\(n=512\) reference behaves as follows:

| \(n\) | relative Gram error | first-jet maximum error |
|---:|---:|---:|
| 8 | \(1.3053\times10^{-2}\) | \(1.7391\times10^{-2}\) |
| 16 | \(3.2428\times10^{-3}\) | \(4.3583\times10^{-3}\) |
| 32 | \(8.0737\times10^{-4}\) | \(1.0902\times10^{-3}\) |
| 64 | \(1.9941\times10^{-4}\) | \(2.7260\times10^{-4}\) |
| 128 | \(4.7475\times10^{-5}\) | \(6.8152\times10^{-5}\) |

The roughly fourfold improvement under doubling is consistent with the
cell-centred second-order spectrum. All five singular values remain positive,
but the limiting response is ill-conditioned: its condition number is about
\(1.48\times10^5\). Algebraic visibility therefore does not imply easy
recovery.

### Hypothesis 6.1 — fixed-mode response convergence

For a bounded smooth modulation, sufficiently regular target background, a
fixed number of source modes, and \(\tau\ge\tau_0>0\), the density-normalized
discrete response Gram converges in operator norm to the continuum response
Gram. For the cell-centred scheme the error is \(O(n^{-2})\).

The tables support this statement, but this manuscript does not supply the
needed uniform semigroup or resolvent estimate. It remains a hypothesis.

## 7. First causal jets: parity and regularity

### Theorem 7.1 — continuum parity selection

Let

\[
 \phi_k(x)=\sqrt2\cos(k\pi x),
 \qquad \rho_B(y)=1+a\phi_\ell(y).
\]

For modulation \(D(x)=x\), the derivative at zero of the \(\ell\)-th target
mode produced by the \(k\)-th source mode is

\[
 \dot r_{\ell k}(0)=
 \begin{cases}
 \displaystyle\frac{2\sqrt2\,ag\ell^2}{k^2},&k\text{ odd},\\[6pt]
 0,&k\text{ even}.
 \end{cases}
\]

#### Proof

The independent source and target terms vanish after marginalization. The
mixed term gives

\[
 \dot r_{\ell k}(0)
 =-ag(\ell\pi)^2\int_0^1x\phi_k(x)\,dx.
\]

The integral is zero for even \(k\), and equals
\(-2\sqrt2/(k\pi)^2\) for odd \(k\). \(\square\)

For \(a=0.4\), \(g=0.8\), and \(\ell=1\), the first five values are

\[
 (0.90509668,\ 0,\ 0.10056630,\ 0,\ 0.03620387).
\]

The \(n=128\) discrete maximum error is \(6.82\times10^{-5}\), while its even
entries vanish to floating residue below \(2\times10^{-16}\).

The preceding theorem uses a smooth target mode. A full-tangent norm exposes a
regularity boundary.

### Theorem 7.2 — smooth backgrounds converge; atoms have a singular jet

Let \(H_n\) be an orthonormal basis of the source simplex tangent. For

\[
 q^{\rm sm}_{n,j}=\frac{1+a\cos(\pi x_j)}n
\]

and an interior atom \(q_n^\delta=e_j\), the Frobenius norm of the first
forward coefficient satisfies

\[
 \begin{aligned}
 \|M_BG_n(H_n\otimes q_n^{\rm sm})\|_F
 &=\frac{ga\mu_{1,n}}{\sqrt{24}}
   \frac{\sqrt{n^2-1}}n
 \longrightarrow\frac{ga\pi^2}{\sqrt{24}},\\
 \|M_BG_n(H_n\otimes q_n^\delta)\|_F
 &=gn^2\sqrt{\frac{n^2-1}{2n}}
 \sim\frac g{\sqrt2}n^{5/2}.
 \end{aligned}
\]

#### Proof

The first coefficient is a rank-one outer product, up to sign,

\[
 g(A_nq_n)(\mathbf1^{\mathsf T}D_nH_n).
\]

Since \(H_nH_n^{\mathsf T}\) projects onto the zero-sum subspace,

\[
 \|\mathbf1^{\mathsf T}D_nH_n\|^2
 =\sum_j(x_j-1/2)^2=\frac{n^2-1}{12n}.
\]

The smooth cosine is an eigenvector and gives
\(\|A_nq_n^{\rm sm}\|=a\mu_{1,n}/\sqrt{2n}\). For an interior atom,
\(A_ne_j\) has the three entries \(n^2(-1,2,-1)\), hence norm
\(\sqrt6n^2\). Multiplication gives the formulas. \(\square\)

For \(g=0.8\) and \(a=0.5\), the smooth limit is \(0.8058498249\). At the
initial-layer time \(\tau_n=0.1/n^2\), the atomic leading response grows as
\(\sqrt n\), whereas the smooth leading response decays as \(n^{-2}\). At
fixed positive times both audited low-mode spectra stabilize because the heat
semigroup smooths the atom. A finite atom is valid; it simply is not an
\(L^2\)-regular continuum initial jet.

## 8. Target bandwidth limits causal-jet rank

### Theorem 8.1 — modal-support rank bound

Suppose the target background has \(s\) nonzero coefficients among
nonstationary target modes. If \(\mathcal J_{\le r}\) stacks the forward
response jet through order \(r\), then

\[
 \operatorname{rank}\mathcal J_{\le r}
 \le
 \min\!\left\{n-1,\sum_{k=1}^r\min(k,s)\right\}.
\]

#### Proof

For target eigenvalue \(\mu\), the order-\(k\) row is proportional to

\[
 \mathbf1^{\mathsf T}[A_n+\mu(I+gD_n)]^kH_n.
\]

This is a vector-valued polynomial in \(\mu\) of degree at most \(k\). Its
constant coefficient is zero because
\(\mathbf1^{\mathsf T}A_n^kH_n=0\). Evaluation on \(s\) active values of
\(\mu\) therefore adds at most \(\min(k,s)\) row directions at order \(k\).
Sum over the orders and cap by the source tangent dimension. \(\square\)

A single target mode can reveal at most one new source direction per derivative
order. A broadband target grows at most at triangular-number speed. This
explains why Stage IV's atomic target reached cumulative ranks \(1,3,5\) by
orders one through three while a smooth single-mode target reveals directions
much more slowly.

## 9. The Poisson cone is exact and continuum-trivial

Stage IV used uniformization. With
\(\Lambda_n=\max_x(G_n)_{xx}\), the number of discrete jumps is bounded by a
Poisson variable of mean \(\Lambda_n\tau\). For the directed product path,

\[
 \frac{\Lambda_n}{n^2}\longrightarrow 4+2g.
\]

Consequently, a fixed Poisson quantile has physical radius

\[
 \frac{q_{1-\delta}(\Lambda_n\tau)}n
 =(4+2g)n\tau+O(\sqrt\tau).
\]

At every fixed positive \(\tau\), this eventually exceeds the \(O(1)\) domain
eccentricity. The finite bound remains true; it has ceased to measure
continuum displacement because it counts backtracking jumps as progress.

## 10. A diffusive finite-lattice leakage envelope

Let \(h=1/n\) and \(c=2+g\). Define

\[
 I_h(r,\tau;c)=
 \frac rh\operatorname{arsinh}\!\left(\frac{rh}{2c\tau}\right)
 -\frac{2c\tau}{h^2}
 \left(\sqrt{1+\left(\frac{rh}{2c\tau}\right)^2}-1\right).
\]

### Theorem 10.1 — signed-displacement bound

For the directed reflected nearest-neighbour walk started at a declared cell,

\[
 \Pr\{h,d_1(X_\tau,X_0)\ge r\}
 \le \min\{1,4e^{-I_h(r,\tau;2+g)}\}.
\]

Moreover,

\[
 I_h(r,\tau;c)\longrightarrow\frac{r^2}{4c\tau},
\]

so a sufficient continuum leakage radius is

\[
 r_\delta(\tau)
 =\sqrt{4(2+g)\tau\log(4/\delta)}.
\]

#### Proof

Lift each reflected path coordinate to a symmetric walk on \(\mathbb Z\) with
the explicit paired-cell fold

\[
 \phi_n(k)=\min\{r,2n-1-r\},\qquad r=k\bmod 2n.
\]

This map is one-Lipschitz and has a two-point plateau at each boundary. An
attempted outward jump at a plateau becomes a self-loop, so the folded chain
has exactly the one-sided endpoint rate of the path. The source
coordinate has rate \(h^{-2}\) in each sign. Conditional on the lifted source,
the target has equal sign rates bounded by \((1+g)h^{-2}\).

For any of the four sign pairs, applying the lifted, state-dependent generator
to the exponential and using Dynkin--Gronwall gives

\[
 \mathbb E e^{\theta(\sigma_1\Delta X+\sigma_2\Delta Y)}
 \le
 \exp\!\left[
  \frac{2(2+g)\tau}{h^2}(\cosh\theta-1)
 \right].
\]

Folding cannot increase endpoint \(L^1\) distance. Apply Chernoff's inequality
to each sign pair, optimize at

\[
 \theta=\operatorname{arsinh}\!\left(\frac{rh}{2(2+g)\tau}\right),
\]

and take a union bound. Taylor expansion in \(h\) gives the continuum limit.
\(\square\)

At \(g=0.8\), \(\tau=0.005\), and \(\delta=0.01\):

| \(n\) | actual 99% radius | raw Poisson radius | graph-capped Poisson radius | signed bound |
|---:|---:|---:|---:|---:|
| 8 | 0.5000 | 0.6250 | 0.6250 | 0.6782 |
| 16 | 0.4375 | 0.8750 | 0.8750 | 0.6126 |
| 32 | 0.4375 | 1.2813 | 1.0000 | 0.5888 |
| 64 | 0.4375 | 2.1719 | 1.0000 | 0.5817 |

The limiting signed bound is \(0.5792426\). It is conservative but nontrivial.
This is a parabolic diffusion envelope, not a strict causal cone and not a
relativistic speed limit.

## 11. Expanding-domain falsification

Fixed-domain refinement does not imply a surviving infinite-volume arrow.
Keep lattice spacing one and stretch the ramp over an expanding path:

\[
 D_{n,j}=\frac{j+1/2}{n}.
\]

For the normalized local contrast
\(u=(e_i-e_{i+1})/\sqrt2\) and an interior atomic target,

\[
 \|M_BG_n(u\otimes q)\|
 =\frac{g\sqrt3}{n}.
\]

Indeed,
\(|\mathbf1^{\mathsf T}D_nu|=1/(\sqrt2n)\) and
\(\|L_nq\|=\sqrt6\). Thus a locally normalized arrow vanishes because the
profile becomes locally flat. A nontrivial infinite-volume model must instead
declare a bounded modulation fixed in physical coordinates, or explicitly
rescale its interaction strength. A globally linear nonzero slope is not a
bounded rate profile on the whole line.

## 12. Symmetry, stationarity, and reversibility boundaries

### Theorem 12.1 — symmetry-protected invisible sources

Let \(S\) be an orthogonal source-state permutation satisfying

\[
 S\mathbf1=\mathbf1,\qquad SL_A=L_AS,qquad SD_A=D_AS.
\]

Then \(G\) commutes with \(S\otimes I\), while
\(M_B(S\otimes I)=M_B\). Every source intervention \(h\) in a nontrivial
representation, and in particular every \(Sh=-h\), is invisible to the target
marginal for all time.

For an odd vector,

\[
 M_Be^{-tG}(h\otimes b)
 =M_B(S\otimes I)e^{-tG}(h\otimes b)
 =M_Be^{-tG}(Sh\otimes b)
 =-M_Be^{-tG}(h\otimes b),
\]

so the response is zero.

On the six-path, take

\[
 D=\operatorname{diag}(0,1/2,1,1,1/2,0).
\]

Reflection preserves both \(L_A\) and \(D\). Its odd source-tangent subspace
has dimension three; the even tangent has dimension two. Symmetry proves
response rank at most two. In rational difference coordinates, the order-one
and order-two jet contains a \(2\times2\) minor equal to \(32/125\), proving
rank at least two. Hence the all-time visible quotient has exact dimension two.
The sampled response singular values are

\[
 0.348336,\quad0.009565,\quad
 1.07\times10^{-15},\quad6.00\times10^{-16},\quad5.20\times10^{-16}.
\]

Directionality therefore does not imply source identifiability. Full rank
requires a cyclicity or symmetry-breaking condition, not merely nonconstant
modulation.

### Theorem 12.2 — endpoint silence does not imply path silence

Let the source intervention be tensorized with the uniform stationary target
profile \(\pi_B\). Then

\[
 e^{-tG}(h\otimes\pi_B)=e^{-tL_A}h\otimes\pi_B,
\]

and the target endpoint marginal is zero for mass-zero \(h\). Nevertheless,
the instantaneous response of the expected target jump rate is

\[
 \delta r_B(t)
 =g\,\overline{\deg}_B\,
 d^{\mathsf T}e^{-tL_A}h,
\]

which is generally nonzero.

The formula follows because the target remains uniform conditional on the
source path, but its clock is multiplied by \(1+gd(A_t)\). In the six-path
audit, the endpoint response norm is \(1.09\times10^{-15}\), while the stacked
jump-rate response norm is \(3.7872\) and has rank three. “Stationary silence”
is therefore a statement about a factorized preparation and endpoint-marginal
sensor, not absence of channel capacity.

### Theorem 12.3 — conjugate ports restore reciprocity

Let \(K_t=e^{-tL}\) be symmetric. For any sensors \(C_A,C_B\), choose their
adjoint injections \(J_A=C_A^{\mathsf T}\) and
\(J_B=C_B^{\mathsf T}\). Then

\[
 C_BK_tJ_A=(C_AK_tJ_B)^{\mathsf T}.
\]

This is immediate from \(K_t^{\mathsf T}=K_t\). In the reference model,
conjugate marginal-tangent ports have reciprocity error
\(7.29\times10^{-16}\). The localized Stage IV ports are not conjugate: their
forward norm is \(0.2878\), while the reverse is \(1.75\times10^{-15}\).

There is no contradiction with microscopic reversibility. Symmetry constrains
responses at conjugate ports; an operational arrow can arise from asymmetric,
localized preparations and marginal measurements. Response magnitudes and the
directionality index also depend on the declared source-cost and whitened
output-noise metrics. Exact zero/nonzero and quotient rank are the more robust
claims.

## 13. No nonlinear amplitude jet in the fixed linear model

### Proposition 13.1 — amplitude-linearity no-go

For fixed \(L,M,J\),

\[
 y(t;u)=Me^{-tL}(p_0+Ju)
\]

is affine in \(u\). Every pure or mixed derivative of order at least two with
respect to initial-state intervention amplitudes is identically zero.

Therefore, “try larger perturbations” cannot create dynamical nonlinear
curvature in the present model. A meaningful extension must specify at least
one of:

1. a control-dependent generator \(L(u)\);
2. nonlinear state dynamics or measurements;
3. finite replacement or conditioning interventions; or
4. joint variation of interaction parameters and initial state.

A softmax or another curved coordinate chart on the simplex would create
coordinate curvature, not by itself nonlinear dynamics.

## 14. Completed adjacent target: an outward-rounded E-design certificate

Stage IV's six-time dyadic design is now independently certified. In the
rational difference basis

\[
 E=(e_0-e_5,\ldots,e_4-e_5),
 \qquad Q=E^{\mathsf T}E,
\]

the criterion is the smallest generalized eigenvalue of
\(G(w)=\sum_iw_iA_i\) relative to \(Q\). A 192-bit Arb computation proves

\[
 \boxed{
 4.982412\times10^{-9}
 \le z_*
 \le4.982942\times10^{-9}}
\]

on both the exact algebraic 120-time grid and the exact binary64 values
returned by the original NumPy grid.

The lower bound uses the exact dyadic numerators

\[
 (963,71,669,1289,294,810)/4096
\]

at zero-based grid indices \(62,76,77,87,105,106\), plus Arb-certified
positive leading principal minors of \(G-z_LQ\). The upper bound uses an exact
rational factorization \(Z=BB^{\mathsf T}/S\), proving \(Z\succeq0\) and
\(\operatorname{tr}(ZQ)=1\), followed by outward evaluation of all 120 dual
constraints. Every recorded ball radius is below \(10^{-54}\); the closest
dual constraint retains more than \(8\times10^{-16}\) slack.

This is a finite-grid computer-assisted theorem, not a continuum-time optimum
or a formal-proof-assistant derivation.

### Proposition 14.1 — noise interpretation of the E-floor

Assume independent whitened Gaussian output noise with covariance
\(\sigma^2I\), \(N\) independent observations allocated according to design
\(w\), and a source displacement \(au\) with \(\|u\|=1\). If
\(G(w)\succeq zI\) in the declared source metric, the equal-prior optimal error
for distinguishing zero from \(au\) obeys

\[
 P_{\rm err}(u)
 \le
 \Phi\!\left(-\frac{a\sqrt{Nz}}{2\sigma}\right).
\]

Thus \(P_{\rm err}\le\alpha\) for every declared unit direction whenever

\[
 N\ge
 \frac{4\sigma^2[\Phi^{-1}(1-\alpha)]^2}{a^2z}.
\]

This does not solve zero-versus-nonzero testing without assumptions. No finite
noisy experiment can uniformly distinguish an exact zero channel from
arbitrarily weak alternatives. A valid theorem must declare a minimum effect
\(a\), excitation lower bound, calibration, noise metric, and model-error
budget.

## 15. Falsification ledger

| tempting statement | result or counterexample |
|---|---|
| the finite ultraviolet dimension is the product dimension | fixed \(n\), \(\tau\downarrow0\) gives zero; \(d\) appears only in \(n^{-2}\ll\tau\ll1\) |
| any continuum labelling works equally well | endpoint labelling of the same stencil introduces \(O(n^{-1})\) boundary error |
| an atom and smooth density have the same initial continuum response | atom first jet diverges as \(n^{5/2}\); smooth jet converges |
| one active target mode rapidly identifies every source mode | it adds at most one jet direction per order |
| the exact Poisson cone is a useful continuum cone | its physical radius grows like \(n\tau\) and becomes domain-trivial |
| no strict cone means no quantitative locality | signed displacement yields a finite \(\sqrt\tau\) leakage radius |
| fixed-domain convergence proves an infinite-volume arrow | a stretched ramp makes local arrow strength \(g\sqrt3/n\) |
| a directed channel identifies every source direction | reflection-symmetric modulation leaves three directions invisible |
| stationary target means no detectable influence | endpoint marginal is silent, jump activity is not |
| symmetric microscopic dynamics forbids every operational arrow | conjugate ports are reciprocal; localized nonconjugate ports need not be |
| larger initial perturbations reveal second-order dynamics | fixed linear propagation is exactly affine in amplitude |
| a numerical optimum is a proof | rational primal/dual witnesses and Arb enclosures provide the finite-grid bracket |

## 16. Interpretation

The scale flow supplies a precise version of one part of the motivating idea.
An operational geometry is not merely a pattern in raw numbers. It consists of

1. a state or hypothesis space;
2. allowed preparations;
3. a dynamics;
4. measurements and their noise metric; and
5. a rule for comparing scales.

Stable geometric structure is what survives the declared renormalization and
nearby falsification controls. In this model, the Neumann spectrum, mesoscopic
factor dimension, smooth directed response, and diffusive leakage profile
survive. Atomic initial jets, the raw Poisson radius, stretched infinite-volume
ramps, and symmetry-protected source directions do not.

That is a useful mathematical bridge between abstract distinguishability and a
spatial continuum, but it remains a bridge inside a deliberately chosen
parabolic Markov model. The product dimension is put into the factorization;
the computation shows when an observer recovers it, not why nature has a
particular dimension. The model has instantaneous positive heat-kernel tails
and therefore cannot represent relativistic causality. These limitations are
part of the result.

## 17. Next research order

1. **Prove fixed-mode response convergence.** Establish form or resolvent
   convergence and a uniform \(t\ge t_0\) error for the reduced response
   operators.
2. **Map the mollifier phase diagram.** Replace an atom by width
   \(\varepsilon_n\) and classify regimes of \(\varepsilon_n/h_n\) and
   \(t_n/h_n^2\).
3. **Sharpen the leakage metric.** Replace the four-orthant worst-rate bound by
   an intrinsic-metric or mode-sensitive inequality.
4. **Construct a genuine joint limit.** Take \(h_n\to0\), \(nh_n\to\infty\)
   with a bounded modulation profile fixed in physical coordinates.
5. **Characterize cyclic visibility.** Turn the modal/Krylov description into
   necessary and sufficient symmetry-aware rank conditions with quantitative
   noise thresholds.
6. **Develop path-space sensing.** Use tilted generators to study jump counts,
   holding times, and two-time correlations, especially at stationary endpoint
   backgrounds.
7. **Introduce controlled nonlinearity only after declaration.** Compare
   explicit control-dependent generators or finite replacement interventions,
   with coordinate effects separated from dynamical curvature.

## 18. Reproduction

Run the canonical Stage V audit:

```sh
python operational_information_geometry_v.py
python -m unittest -v test_operational_information_geometry_v.py
```

Run the independent continuum and propagation audit:

```sh
python oig_v_scaling_continuum.py --maximum-side-length 64
python -m unittest -v test_oig_v_scaling_continuum.py
```

Run the outward-rounded Stage IV adjacent certificate:

```sh
python oig_iv_certificate.py --grid both
python -m unittest -v test_oig_iv_certificate.py
```

Run the complete repository suite:

```sh
python -m unittest discover -v
```

The interval checker additionally requires `python-flint>=0.9`, as recorded in
`oig_iv_certificate_requirements.txt`.

## 19. Sources and novelty boundary

Finite-state observability and Krylov rank belong to classical systems theory;
see E. G. Gilbert, “Controllability and Observability in Multivariable Control
Systems,” *Journal of the Society for Industrial and Applied Mathematics,
Series A: Control* 1 (1963), 128--151,
<https://doi.org/10.1137/0301009>.

Autonomous random environments and marginal Markov structure are established
topics; see A. Economou, “Generalized product-form stationary distributions for
Markov chains in random environments with queueing applications,” *Advances in
Applied Probability* 37 (2005), 185--211,
<https://doi.org/10.1239/aap/1113402405>, and F. Ball and G. F. Yeo,
“Lumpability and marginalisability for continuous-time Markov chains,”
*Journal of Applied Probability* 30 (1993), 518--528,
<https://doi.org/10.2307/3214762>.

The signed-displacement bound is derived directly here for this model. Its
large-deviation perspective is adjacent to E. B. Davies, “Large Deviations for
Heat Kernels on Graphs,” *Journal of the London Mathematical Society* 47
(1993), 65--72, <https://doi.org/10.1112/jlms/s2-47.1.65>. It is not asserted
to be Davies's theorem.

The conjugate-port identity is elementary linear algebra; its physical context
is the reciprocity program of L. Onsager, “Reciprocal Relations in Irreversible
Processes. I,” *Physical Review* 37 (1931), 405--426,
<https://doi.org/10.1103/PhysRev.37.405>.

The finite-grid dual belongs to optimal-design theory; see J. Kiefer, “General
Equivalence Theory for Optimum Designs (Approximate Theory),” *The Annals of
Statistics* 2 (1974), 849--879,
<https://doi.org/10.1214/aos/1176342810>. Arb's enclosing arithmetic is
described by F. Johansson, “Arb: Efficient Arbitrary-Precision Midpoint-Radius
Interval Arithmetic,” *IEEE Transactions on Computers* 66 (2017), 1281--1292,
<https://doi.org/10.1109/TC.2017.2690633>.

Within this research program, the contribution is the explicit operational
assembly and audit: the renormalization dictionary, noncommuting dimension
limit, response-mode reduction, regularity bifurcation, model-specific
diffusive envelope, protocol counterexamples, and certified design are made to
constrain one another. No broad literature-priority claim is made without
specialist review.
