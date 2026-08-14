# Operational Information Geometry V — independent continuum scaling audit

## Fixed-domain response flow, singular initial layers, and a diffusive causal envelope

- **Research lane:** continuum and scale-flow audit
- **Date:** 14 August 2026
- **Status:** independent theorem/computation package for integration into Stage V;
  not peer reviewed
- **Reproduction:** `oig_v_scaling_continuum.py`
- **Independent tests:** `test_oig_v_scaling_continuum.py`

## Executive result

Stage IV's one-way response has a meaningful fixed-domain continuum candidate,
but only after three distinctions are made.

1. The path graph should be read as a **cell-centred Neumann finite-volume
   discretization**, with (h=1/n) and (L_n/h^2). The tempting endpoint
   convention (h=1/(n-1)) creates a first-order boundary-location artifact.
2. Fixed positive observation times smooth both a pure target atom and a smooth
   target background, and the first fixed set of source-mode response singular
   values stabilizes. The (t=0) jet does not behave uniformly: its norm stays
   finite for a smooth target density but diverges as (n^{5/2}) for an atom.
3. Stage IV's Poisson jump-count cone becomes physically vacuous under
   diffusive scaling. A signed-jump exponential-martingale argument gives a new
   finite-(h) leakage envelope with a nontrivial Gaussian continuum limit.

There is also a negative thermodynamic result. If the modulation
(D_i=(i+1/2)/n) is stretched over an expanding fixed-spacing path, a localized
arrow decays exactly as (1/n). A nontrivial infinite-volume arrow therefore
requires a modulation profile fixed in physical coordinates; it cannot be
inferred from fixed-domain refinement alone.

## 1. The three limits are not interchangeable

This audit separates:

1. **Fixed-domain refinement:** (h_n=1/n), physical length one,
   (h_n^{-2}L_n), and fixed physical observation times.
2. **Infinite volume:** (h) fixed and (n	oinfty), so the boundary recedes
   and the global spectral gap closes.
3. **Joint continuum/infinite-volume flow:** (h_n	o0) and
   (n h_n	oinfty).

The third needs uniform localization and modulation assumptions and is not a
formal consequence of either of the first two. In particular, the fixed-domain
profile (d(x)=x) is bounded, while extending a nonzero linear slope over an
infinite line makes the rate (1+g d(x)) eventually unbounded or negative in
one direction. A bounded fixed-scale profile such as a shifted sigmoid is a
different model and should be declared as such.

## 2. Cell-centred Neumann scaling

Let (L_n) be the ordinary path graph Laplacian on (n) cells. Its spectrum is
exactly

\[
 \lambda_{k,n}=4\sin^2\!\left(\frac{k\pi}{2n}\right),
 \qquad 0\leq k<n.
\]

### Proposition 2.1 — the cell-centred convention is second order

With cell centres (x_i=(i+1/2)/n), spacing (h=1/n), and
(A_n=h^{-2}L_n), every fixed mode satisfies

\[
 \lambda_k(A_n)
 =(k\pi)^2-\frac{(k\pi)^4}{12n^2}+O(n^{-4}).
\]

If the same endpoint rows are instead labelled with spacing (1/(n-1)), then

\[
 (n-1)^2\lambda_{k,n}
 =(k\pi)^2\left(1-\frac{2}{n}+O(n^{-2})\right).
\]

Thus the latter convention still converges, but its effective boundary is
shifted at first order. It is not the second-order endpoint Neumann stencil.

The first nonzero eigenvalue audit is:

| (n) | (n^2\lambda_{1,n}) | relative error | ((n-1)^2\lambda_{1,n}) | relative error |
|---:|---:|---:|---:|---:|
| 8  | 9.74341984 | (-1.2785\times10^{-2}) | 7.45980581 | (-2.4416\times10^{-1}) |
| 16 | 9.83793643 | (-3.2086\times10^{-3}) | 8.64662382 | (-1.2391\times10^{-1}) |
| 32 | 9.86167978 | (-8.0293\times10^{-4}) | 9.25495534 | (-6.2277\times10^{-2}) |
| 64 | 9.86762277 | (-2.0078\times10^{-4}) | 9.56166864 | (-3.1200\times10^{-2}) |

The continuum value is (pi^2=9.86960440\ldots). Doubling (n) divides the
cell-centred error by approximately four.

## 3. Fixed-domain directed continuum candidate

Set

\[
 G_n=A_n\otimes I+(I+gD_n)\otimes A_n,
 \qquad (D_n)_{ii}=x_i,\quad g=0.8.
\]

This is the Stage IV one-way generator under the cell-centred scaling. Its
formal continuum equation on ([0,1]^2) is

\[
 \partial_t p
 =\partial_a^2p+(1+ga)\partial_b^2p,
\]

with reflecting boundaries. Integrating in (b) leaves the autonomous
(A)-marginal heat equation. Consequently the exact all-(n) zero response
(B\to A) and equilibrium-target silence survive the limit formally.

The present package does not claim a completed semigroup-convergence proof.
The standard finite-volume spectrum and the exact response reduction below
make such a proof plausible for smooth data; distributional backgrounds need
additional regularity estimates.

### Proposition 3.1 — exact modal reduction

Let (A_n v_\ell=\mu_\ell v_\ell), let (q) be the target background, and let
(H) contain declared source directions. In the (v_\ell) output mode,

\[
 M_Be^{-tG_n}(H\otimes q)
 \quad\longleftrightarrow\quad
 \langle v_\ell,q\rangle\,
 \mathbf1^{\mathsf T}
 e^{-t[A_n+\mu_\ell(I+gD_n)]}H.
\]

#### Proof

Conjugate only the (B) coordinate by the orthogonal eigenbasis of (A_n).
The joint generator becomes the direct sum of the displayed (n\times n)
matrices. Marginalization contracts the (A) factor against
(mathbf1^{\mathsf T}), and the initial target background supplies
(langle v_\ell,q\rangle). This also gives an (O(n^4))-rather than dense
(O(n^6))-type reproduction route.

## 4. A regularity bifurcation at the first causal jet

For a mass-preserving orthonormal source tangent (H_n) and target background
(q_n), the first forward causal coefficient is exactly

\[
 M_BG_n(H_n\otimes q_n)
 =g(A_nq_n)(\mathbf1^{\mathsf T}D_nH_n).
\]

It has rank one whenever (q_n) is nonstationary and (D_n) is nonconstant.
Moreover,

\[
 \|\mathbf1^{\mathsf T}D_nH_n\|^2
 =\sum_i(x_i-\bar x)^2
 =\frac{n^2-1}{12n}.
\]

### Theorem 4.1 — smooth backgrounds converge; atoms have a singular jet

Take

\[
 q^{\rm sm}_{n,i}=\frac{1+a\cos(\pi x_i)}{n},\qquad 0\leq a<1,
\]

or an interior atom (q_n^\delta=e_j). Then

\[
 \begin{aligned}
 \|M_BG_n(H_n\otimes q_n^{\rm sm})\|_F
 &=\frac{ga\lambda_{1,n}^{(h)}}{\sqrt{24}}
   \frac{\sqrt{n^2-1}}{n}
 \longrightarrow \frac{ga\pi^2}{\sqrt{24}},\\
 \|M_BG_n(H_n\otimes q_n^\delta)\|_F
 &=g n^2\sqrt{\frac{n^2-1}{2n}}
 \sim \frac{g}{\sqrt2}n^{5/2},
 \end{aligned}
\]

where (lambda_{1,n}^{(h)}=4n^2\sin^2(\pi/(2n))).

#### Proof

The smooth cosine is the first path eigenvector, has Euclidean norm
(sqrt{n/2}), and occurs in the probability vector with coefficient (a/n).
Thus
(|A_nq_n^{\rm sm}|=a\lambda_{1,n}^{(h)}/\sqrt{2n}).
For an interior atom, (A_ne_j) has entries (n^2(-1,2,-1)) and norm
(sqrt6n^2). Multiply either result by the exact modulation-row norm above.

For the reference (a=0.5,g=0.8), the finite smooth limit is
(0.8058498249\), while the normalized atom limit is
(0.8/\sqrt2=0.5656854249\).

This is not merely a numerical-conditioning problem. A Dirac target is outside
the (L^2) domain relevant to the initial derivative of a second-order
generator. Stage IV's finite atom is legitimate at every (n), but its raw
(t=0) jet has no finite continuum norm.

## 5. Positive-time response spectra do stabilize

To avoid comparing tangent spaces of changing dimension, the computation fixes
the first four nonconstant (A)-modes. Both source and output are probability
mass vectors; converting both to density-weighted (L^2) norms multiplies them
by the same (h^{-1/2}), so the operator singular values are unchanged.

The protocol has 20 fixed physical times geometrically spaced from (0.01) to
(2). The first four response singular values are:

| (n) | atom background | smooth-cosine background |
|---:|:---|:---|
| 8  | 0.20053360, 0.00919664, 0.00282019, 0.00019726 | 0.04027566, 0.00072098, (6.0802\!\times10^{-5}), (1.2152\!\times10^{-6}) |
| 16 | 0.18992129, 0.00792338, 0.00279939, 0.00016370 | 0.04046056, 0.00073274, (6.3906\!\times10^{-5}), (1.1029\!\times10^{-6}) |
| 32 | 0.18823217, 0.00771873, 0.00278459, 0.00014871 | 0.04050597, 0.00073447, (6.4596\!\times10^{-5}), (1.0649\!\times10^{-6}) |
| 64 | 0.18784080, 0.00767553, 0.00278073, 0.00014453 | 0.04051727, 0.00073482, (6.4763\!\times10^{-5}), (1.0550\!\times10^{-6}) |

The leading smooth-background differences shrink by a factor (4.02) from
(16\to32) versus (32\to64), consistent with second-order convergence.
The atom also stabilizes for this protocol because every declared time stays
strictly positive and the heat semigroup smooths the atom.

This convergence is not uniform down to time zero. At
(t_n=0.1/n^2), using the complete source tangent:

| (n) | atom (s_1(t_n)/\sqrt n) | smooth (n^2s_1(t_n)) | smooth first-jet norm |
|---:|---:|---:|---:|
| 8  | 0.0354023 | 0.0766304 | 0.7893072 |
| 16 | 0.0358329 | 0.0795645 | 0.8016937 |
| 32 | 0.0359450 | 0.0803270 | 0.8048095 |
| 64 | 0.0359737 | 0.0805202 | 0.8055897 |

The atom response grows as (sqrt n) in this initial layer; the smooth response
decays as (n^{-2}). The limits (t\downarrow0) and (n\to\infty) therefore do
not commute for the atomic intervention protocol.

### Hypothesis V.1 — fixed-mode response convergence

For (d,q\) sufficiently smooth, any fixed number (K) of source Neumann
modes, and observation times bounded below by (t_0>0), the discrete response
Gram converges in operator norm to the continuum response Gram, with
second-order error for the cell-centred scheme. For a target delta sequence the
same should hold for (t_0>0), but not uniformly as (t_0\downarrow0).

The tables support this hypothesis but do not prove it. A proof should use
finite-volume resolvent or form convergence plus uniform heat-smoothing bounds.

## 6. Target bandwidth controls causal-jet rank growth

The modal reduction also yields a finite theorem that was not explicit in
Stage IV.

### Theorem 6.1 — modal-support causal-jet bound

Suppose (q) has (s) nonzero coefficients among the nonstationary target
eigenmodes. Let (mathcal J_{\le r}) be the forward response jet stacked through
order (r). Then

\[
 \operatorname{rank}\mathcal J_{\le r}
 \leq
 \min\left\{n-1,\sum_{k=1}^{r}\min(k,s)\right\}.
\]

#### Proof

In target mode (mu), the order-(k) response row is proportional to

\[
 \mathbf1^{\mathsf T}[A_n+\mu(I+gD_n)]^kH_n.
\]

It is a vector-valued polynomial in (mu) of degree at most (k). Its
constant term is zero because
(mathbf1^{\mathsf T}A_n^kH_n=0). Evaluations at (s) active target
eigenvalues therefore span at most (min(k,s)) new row directions. Sum over
orders and cap by the source dimension (n-1).

Consequences:

- A single nonstationary target mode can add at most one source direction per
  derivative order; full rank needs at least (n-1) orders.
- A broadband target can grow at most with triangular numbers
  (1,3,6,10,15,\ldots). Hence even in the best case full rank needs
  (r(r+1)/2\ge n-1).
- Stage IV's six-state atom reaching ranks (1,3,5) by order three is close to
  the broadband ceiling (1,3,5) after the source-dimension cap.

Thus causal order one and rapid full-rank recovery are distinct properties.
The former needs only one active target mode; the latter depends on target
bandwidth.

## 7. Why the Poisson cone fails in the continuum

For the directed cell generator, the maximum exit rate satisfies

\[
 \Lambda_n=(4+2g+O(n^{-1}))n^2.
\]

At fixed physical (t>0), a fixed-quantile Poisson jump count obeys

\[
 q_{1-\delta}(\Lambda_nt)=\Lambda_nt+O(\sqrt{\Lambda_nt}).
\]

Multiplying by the physical jump length (h=1/n) gives

\[
 hq_{1-\delta}(\Lambda_nt)
 =(4+2g)nt+O(\sqrt t),
\]

which diverges and then caps at the domain eccentricity. The issue is exact:
uniformization counts every jump, including the overwhelming number that
backtrack. The actual diffusive spread is (O(\sqrt t)).

At (t=c/n^2), the Poisson physical radius shrinks as (1/n); at the
intermediate scale (t=c/n), it is finite while the actual diffusive radius
shrinks as (n^{-1/2}). Neither rescales the jump-count envelope into a tight
fixed-time continuum cone.

## 8. A diffusive finite-(h) causal envelope

The failed Poisson cone suggests replacing jump count by signed displacement.
This is the same broad large-deviation philosophy used for graph heat kernels
by E. B. Davies, [“Large Deviations for Heat Kernels on
Graphs”](https://doi.org/10.1112/jlms/s2-47.1.65), *Journal of the London
Mathematical Society* 47 (1993), 65–72. The bound below is derived directly for
this two-coordinate model and is not asserted to be Davies's exact theorem.

### Theorem 8.1 — finite-lattice (L^1) leakage bound

Let (X_t) be the directed Markov walk generated by (G_n), started at a
declared cell, and let (d_1) be product-path graph distance. Put
(h=1/n), (c=2+g), and

\[
 I_h(r,t;c)=
 \frac rh\operatorname{arsinh}\!\left(\frac{rh}{2ct}\right)
 -\frac{2ct}{h^2}
 \left(\sqrt{1+\left(\frac{rh}{2ct}\right)^2}-1\right).
\]

Then

\[
 \Pr\{h d_1(X_t,X_0)\ge r\}
 \le \min\{1,4e^{-I_h(r,t;2+g)}\}.
\]

As (h\to0),

\[
 I_h(r,t;c)\longrightarrow \frac{r^2}{4ct},
\]

so a sufficient radius for leakage at most (delta) tends to

\[
 r_\delta(t)=
 \sqrt{4(2+g)t\log(4/\delta)}.
\]

#### Proof sketch

Use the explicit paired-cell fold

\[
 \phi_n(k)=\min\{r,2n-1-r\},\qquad r=k\bmod 2n.
\]

It is one-Lipschitz from the integer line to the (n)-path. Its two-point
plateau at either endpoint makes one lifted jump an invisible self-transition
and the other the single inward path jump, giving exactly the required
endpoint rate. Lift (A) with rate (h^{-2}) in each sign. Conditional on the
lifted (A)-path, lift (B) with equal sign rates

\[
 h^{-2}[1+g x_{\phi_n(\widetilde A)}]\le (1+g)h^{-2}.
\]

For any of the four sign pairs, applying the lifted generator to the
exponential of signed displacement and then Dynkin--Gronwall bounds the moment
by

\[
 \exp\left\{\frac{2(2+g)t}{h^2}(\cosh\theta-1)\right\}.
\]

Independence of the coordinates is not used; only the predictable target-rate
bound is needed. Folding cannot increase endpoint distance. Apply Chernoff's
inequality, optimize at
(	heta=\operatorname{arsinh}(rh/[2(2+g)t])), and take a union bound over the
four orthants. Folding cannot increase graph distance.

For (g=0.8,t=0.005,delta=0.01):

| (n) | (Lambda_n/n^2) | actual 99% physical radius | Poisson uncapped radius | Poisson capped radius | diffusive radius |
|---:|---:|---:|---:|---:|---:|
| 8  | 5.3000 | 0.5000 | 0.6250 | 0.6250 | 0.6782 |
| 16 | 5.4500 | 0.4375 | 0.8750 | 0.8750 | 0.6126 |
| 32 | 5.5250 | 0.4375 | 1.2813 | 1.0000 | 0.5888 |
| 64 | 5.5625 | 0.4375 | 2.1719 | 1.0000 | 0.5817 |

The continuum diffusive radius is (0.5792426). Every audited distance tail
for (n=8,12,16,24,32,48,64) lay below both rigorous bounds to floating
precision. Unlike the Poisson bound, the new radius approaches a finite value
and remains nontrivial relative to the unit-square diameter.

The factor four and the worst-case rate (1+g) make this envelope conservative.
An intrinsic-metric or mode-sensitive refinement could be materially sharper.

## 9. Expanding-domain falsification control

Fixed-domain continuum convergence does not prove an infinite-volume arrow.
Take lattice spacing one, an expanding (n)-cell path, and retain the stretched
profile (D_i=(i+1/2)/n). For the localized normalized source contrast

\[
 u=(e_i-e_{i+1})/\sqrt2
\]

and an interior atomic target background, the first response coefficient has
the exact norm

\[
 g|\mathbf1^{\mathsf T}Du|\,\|L_ne_j\|
 =\frac{g}{\sqrt2 n}\sqrt6
 =\frac{g\sqrt3}{n}.
\]

The computation gives (n) times the jet norm equal to
(1.3856406461=0.8\sqrt3) at every audited size. Thus the local arrow vanishes
when the same normalized ramp is stretched over a receding boundary.

This failure is informative. A nontrivial infinite-volume limit must declare a
bounded physical modulation (d(a)) whose local variation does not flatten,
or else rescale the interaction strength. Those choices define different
operational theories.

## 10. What survived, what failed, and what is now testable

### Survived under fixed-domain refinement

- The exact autonomous (A)-marginal and zero (B\to A) channel.
- Causal order one for every nonstationary target background.
- A stable fixed-positive-time low-mode response spectrum.
- Equilibrium-target silence.
- A physical leakage envelope after replacing raw jump count by signed
  displacement.

### Failed without qualification

- The atomic (t=0) causal-jet norm: it diverges as (n^{5/2}).
- Uniformization as a continuum physical cone: its uncapped radius diverges and
  its capped radius becomes the whole domain.
- Transfer from fixed-domain refinement to infinite volume: a stretched ramp
  makes a localized arrow vanish as (1/n).
- Comparing full numerical rank across (n): the tangent dimension grows and
  arbitrarily small singular values are protocol- and tolerance-dependent.

### Next rigorous targets

1. Prove Hypothesis V.1 by finite-volume form/resolvent convergence and obtain a
   uniform (t\ge t_0) response-operator error.
2. Replace the target atom by mollifiers of width
   \(\varepsilon_n\) and map the phase diagram relating
   \(\varepsilon_n,h_n,t_n\).
3. Optimize the new diffusive envelope in the generator's intrinsic metric,
   reducing the four-orthant and worst-rate losses.
4. Study a joint limit (h_n\to0,n h_n\to\infty) with a bounded modulation
   profile fixed in physical coordinates.
5. Combine the modal-support rank theorem with noise thresholds: high formal
   jet rank need not mean statistically detectable causal directions.

## Reproduction

Run:

```bash
python oig_v_scaling_continuum.py --maximum-side-length 64
python -m unittest -v test_oig_v_scaling_continuum.py
```

The laboratory uses exact path-spectrum formulas, dense (n\times n) modal
response reductions, and sparse `expm_multiply` propagation. The eight
independent tests check the closed forms, modal reduction against a dense joint
calculation, Markov structure, rank bound, asymptotic scalings, and both leakage
envelopes.
