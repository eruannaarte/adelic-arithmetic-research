# Operational Information Geometry VI — adversarial audit

## Scope and verdict

This memo is an independent falsification lane for the fixed-mode
discrete-to-continuum response theorem.  It does not modify the Stage VI
manuscript.

The central qualitative statement survives: on the fixed interval, generalized
Mosco convergence gives convergence of every fixed source/target modal response,
uniformly on a compact time interval including \(t=0\).  The compactness of the
one-dimensional energy embedding yields a stronger full-semigroup operator-norm
statement for times bounded away from zero.

The second-order rate has a sharp boundary.  It is valid for the declared smooth,
fixed-mode, cell-centred protocol, but it is not a consequence of Mosco
convergence and fails under several seemingly small changes.  Exact controls
below produce first order for a midpoint-sampled jump, order \(3/2\) for a
half-Hölder profile, first order for a nearest-cell atom, first order under an
incorrect endpoint spacing convention, and a nonzero limiting error when modes
grow and time shrinks diffusively.

The following three assertions must remain separate:

1. convergence of finitely many scalar matrix elements;
2. operator-norm convergence of a fixed finite response or Gram matrix; and
3. operator-norm convergence of the full embedded semigroup.

The first two can include \(t=0\).  The third cannot.

## 1. Qualitative theorem with minimal assumptions

Put \(h=1/n\), equip \(H_h=\mathbb R^n\) with

\[
 \langle z,w\rangle_h=h\sum_jz_jw_j,
\]

let \(J_h:H_h\to L^2(0,1)\) be piecewise-constant reconstruction, and let
\(P_h=J_h^*\) be cell averaging.  Let

\[
 K_{\ell,h}=A_h+\mu_{\ell,h}M_{v_h},
 \qquad
 K_\ell=-\partial_x^2+(\ell\pi)^2M_v
\]

with Neumann boundary conditions.  For a clean Markov interpretation assume
\(0<v_-\le v_h,v\le v_+<\infty\).  For the analytic convergence alone a common
lower bound after a scalar shift suffices.

A useful minimal hypothesis is

\[
 \sup_h\|v_h\|_\infty<\infty,
 \qquad J_hv_h\to v\text{ in }L^1(0,1),
 \qquad \mu_{\ell,h}\to(\ell\pi)^2
\]

for each fixed \(\ell\).  Cell averages of an \(L^\infty\) profile satisfy this.
Point values of a merely measurable profile do not: they are representative
dependent and can fail to converge altogether.  The manuscript's stronger
assumption of a continuous profile sampled at cell centres is safe.

The discrete Dirichlet energies control the piecewise-linear interpolants in
\(H^1(0,1)\).  Their difference from \(J_hz_h\) is \(o(1)\) in \(L^2\) on every
bounded-energy family.  Rellich compactness therefore gives asymptotic
compactness as well as Mosco convergence.  The consequences are:

### Fixed vectors and fixed modes

If \(f_h\to f\) strongly in the varying-space sense, then

\[
 \sup_{0\le t\le T}
 \|J_he^{-tK_{\ell,h}}f_h-e^{-tK_\ell}f\|_2\to0.
\]

Thus fixed modal matrix elements, finite response matrices, and their finite
Grams converge uniformly on \([0,T]\).  No positive \(t_0\) is needed for this
plain convergence result.

### Full embedded semigroup

Compact Mosco convergence implies, for every fixed \(t>0\),

\[
 \|J_he^{-tK_{\ell,h}}P_h-e^{-tK_\ell}\|_{L^2\to L^2}\to0.
\]

One direct proof is a weak-unit-vector contradiction.  If the norm did not
vanish, choose unit \(f_h\rightharpoonup f\).  Since
\(\Pi_h:=J_hP_h\to I\) strongly, \(P_hf_h\) converges generalized-weakly to \(f\).
Compact convergence sends the discrete semigroup images strongly to
\(e^{-tK_\ell}f\), while compactness of the continuum heat semigroup sends
\(e^{-tK_\ell}f_h\) to the same limit.  This contradicts the assumed norm gap.

Spectral calculus makes the family equicontinuous for \(t\ge t_0>0\).  For a
nonnegative generator,

\[
 \|e^{-tA}-e^{-sA}\|
 \le {|t-s|\over e\,t_0},\qquad s,t\ge t_0,
\]

and the same estimate holds on every grid.  Pointwise norm convergence is
therefore uniform on \([t_0,T]\).

It cannot include zero.  At \(t=0\),

\[
 J_he^{-0K_{\ell,h}}P_h=\Pi_h,
 \qquad \|\Pi_h-I\|=1
\]

for every finite grid.  This is the cleanest separator between fixed-mode
convergence and full operator-norm convergence.

The relevant primary framework is Kuwae and Shioya,
[Convergence of spectral structures](https://doi.org/10.4310/cag.2003.v11.n4.a1),
especially their compact-Mosco/compact-semigroup equivalence.  The common-space
norm upgrade is also consistent with the classical collectively compact
operator framework of Anselone and Palmer,
[Pacific Journal of Mathematics 25 (1968)](https://msp.org/pjm/1968/25-3/pjm-v25-n3-p02-p.pdf).

## 2. What Mosco convergence does not provide

Mosco convergence supplies no algebraic rate.  A statement of \(O(h^2)\) needs
quantitative regularity, a precise representation rule, fixed physical modes,
and a time regime.  The following exact and numerical controls delimit those
requirements.

### 2.1 A midpoint-sampled jump is only first order

For a target transverse mode \(\ell\), source mode \(k\), target amplitude
\(a\), and modulation \(d\), the first constant-output response derivative is

\[
 r'_{\ell k,h}(0)
 =-ag\mu_{\ell,h}\,{1\over n}\sum_{j=0}^{n-1}
 d(x_j)\phi_k(x_j).
\]

Take

\[
 d(x)=\mathbf1_{[0,1/3)}(x),\quad
 k=\ell=1,\quad a=0.2,\quad g=0.6.
\]

Along dyadic \(n\), the sampled interface is displaced by exactly order \(h\).
The jet error obeys

\[
 n\,|r'_{11,h}(0)-r'_{11}(0)|\longrightarrow 0.279\ldots,
\]

so no \(O(h^2)\) estimate can hold under boundedness alone.  The finite-time
modal response at \(t=0.05\) exhibits the same rate:

| \(n\) | \(\lvert R_n-R_{2n}\rvert\), smooth ramp | ratio to next | \(\lvert R_n-R_{2n}\rvert\), jump | ratio to next |
|---:|---:|---:|---:|---:|
| 32 | \(1.35645\times10^{-5}\) | 4.0042 | \(1.28031\times10^{-3}\) | 1.9688 |
| 64 | \(3.38754\times10^{-6}\) | 4.0011 | \(6.50287\times10^{-4}\) | 2.0162 |
| 128 | \(8.46660\times10^{-7}\) | 4.0003 | \(3.22534\times10^{-4}\) | 1.9921 |
| 256 | \(2.11652\times10^{-7}\) | 4.0003 | \(1.61910\times10^{-4}\) | 2.0040 |

The jump counterexample concerns point sampling.  Exact cell averages can
improve a single finite-jump profile, which is another reason the sampling rule
must appear in the theorem.

### 2.2 Continuous is not enough for a second-order rate

For

\[
 d(x)=|x-1/3|^{1/2},
\]

the exact continuum integral can be computed by splitting at the cusp.  The
first-jet errors are

| \(n\) | jet error | ratio to next |
|---:|---:|---:|
| 2048 | \(2.05616\times10^{-7}\) | 2.738 |
| 4096 | \(7.51003\times10^{-8}\) | 2.745 |
| 8192 | \(2.73563\times10^{-8}\) | 2.781 |

These ratios approach \(2^{3/2}\), not \(4\).  Continuity is sufficient for
plain Mosco convergence but not for the quantitative theorem.

### 2.3 Atomic fixed coefficients converge, generically at first order

An atom is not an \(L^2\) vector and is not covered by Mosco convergence as an
initial datum.  It can enter a fixed target-mode response only through a
separately normalized scalar coefficient.  For a nearest-cell atom at \(y_0\),

\[
 \widehat\delta_{\ell,h}
 =\sqrt n\,u_{\ell,h}(j_h)=\phi_\ell(x_{j_h})
 \longrightarrow \phi_\ell(y_0).
\]

At \(y_0=1/3\), \(\ell=1\), and dyadic \(n\), the cell-centre displacement is
\(\pm1/(6n)\), hence

\[
 n\,|\widehat\delta_{1,h}-\phi_1(1/3)|
 \longrightarrow {\pi\sqrt6\over12}=0.64127\ldots.
\]

The control values are:

| \(n\) | nearest-cell error | \(n\) times error | two-cell split error | \(n^2\) times error |
|---:|---:|---:|---:|---:|
| 128 | \(5.00403\times10^{-3}\) | 0.64052 | \(2.93000\times10^{-5}\) | 0.48005 |
| 256 | \(2.50646\times10^{-3}\) | 0.64165 | \(7.42995\times10^{-6}\) | 0.48693 |
| 512 | \(1.25212\times10^{-3}\) | 0.64109 | \(1.84440\times10^{-6}\) | 0.48350 |

A two-cell positive split preserving both mass and first moment restores
second order for each fixed smooth mode.  This is the right atomic convention
if an \(O(h^2)\) fixed-coefficient theorem is desired.

This result does not regularize the full-band atom.  Passing an actual atom
through the semigroup, or summing a growing family of its target coefficients,
retains the singular initial layer found in Stage V.

### 2.4 Endpoint relabelling loses one order

The path matrix in this project is the cell-centred matrix with \(h=1/n\):

\[
 \mu_{1,h}=4n^2\sin^2(\pi/(2n))
 =\pi^2+O(n^{-2}).
\]

If the same matrix is relabelled as an endpoint grid with \(h=1/(n-1)\), then

\[
 \widetilde\mu_{1,h}
 =4(n-1)^2\sin^2(\pi/(2n)),
 \qquad
 n|\widetilde\mu_{1,h}-\pi^2|\to2\pi^2.
\]

At \(n=1024\), the two absolute errors are \(7.74\times10^{-6}\) and
\(1.927\times10^{-2}\), respectively.  A genuinely different, correctly
constructed node-centred Neumann scheme may recover second order; changing only
the spacing label does not.

### 2.5 Growing modes and shrinking times give a constant counterexample

For even \(n\), choose \(k_n=n/2\) and \(t_n=n^{-2}\).  Even for the free
Neumann heat semigroup,

\[
 \mu_{k_n,n}=2n^2,
 \qquad
 \lambda_{k_n}={\pi^2n^2\over4}.
\]

Therefore

\[
 \left|e^{-t_n\mu_{k_n,n}}-e^{-t_n\lambda_{k_n}}\right|
 =\left|e^{-2}-e^{-\pi^2/4}\right|
 =0.0505303107655\ldots
\]

for every even \(n\).  Full operator-norm convergence is not uniform as
\(t\downarrow0\), and a fixed-mode \(O(h^2)\) constant cannot be used for a
growing cutoff.

More generally,

\[
 (k\pi)^2-\mu_{k,h}\sim{\pi^4k^4\over12n^2}.
\]

Absolute eigenvalue convergence already fails for \(k\asymp n^{1/2}\).
Relative convergence is less restrictive, and fixed positive time suppresses
high modes exponentially, but any joint \(k_n,t_n,n\) theorem needs explicit
scaling relations.

## 3. Projected semigroups are not truncated semigroups

Let \(P\) project onto a fixed finite cosine space and let \(K\) include a
nonconstant multiplication potential.  In general,

\[
 P e^{-tK}P\ne e^{-tPKP}\big|_{PH}.
\]

The Taylor expansions differ at second order:

\[
 P e^{-tK}P-e^{-tPKP}
 ={t^2\over2}PK(I-P)KP+O(t^3).
\]

For the ramp \(d(x)=x\), multiplication couples every finite low-mode space to
its complement, so this term is nonzero.  Consequently:

- computing the full \(n\times n\) reduced semigroup and then selecting fixed
  input/output modes is correct;
- exponentiating a fixed \(K\times K\) modal block is a different Galerkin
  model and has a truncation error which does not vanish merely because
  \(n\to\infty\);
- a separate \(K\to\infty\) estimate is needed.

The Stage VI continuum laboratory's two-step block-Duhamel estimate correctly
accounts for this distinction.  Its factor \(b^2\) reflects the required exit
from and return to the retained modal block; it does not silently equate the two
semigroups.

## 4. Normalization audit

Let \(u_{k,h}\) be a Euclidean-normalized DCT vector.  A unit continuum density
mode is represented as a probability perturbation \(u_{k,h}/\sqrt n\).  A
probability output coefficient becomes a continuum density coefficient after
multiplication by \(\sqrt n\).  Hence the correctly normalized scalar is

\[
 \sqrt n\,u_{\ell,h}^{\mathsf T}T_h
 \left({u_{k,h}\over\sqrt n}\right)
 =u_{\ell,h}^{\mathsf T}T_hu_{k,h}.
\]

Using neither factor produces the same number by accidental cancellation, but
it assigns the wrong physical norm to both the source cost and output noise.
Using only one factor forces the response to zero like \(n^{-1/2}\) or makes it
diverge like \(n^{1/2}\).  Every theorem about an operational Gram must declare
both port metrics even when the two conversion factors cancel algebraically.

For an atom \(q_h=e_{j_h}\), the fixed density coefficient is
\(\sqrt n\,u_{\ell,h}^{\mathsf T}q_h\).  Omitting \(\sqrt n\) incorrectly sends every
fixed nonconstant coefficient to zero.

## 5. Exact reflection obstruction

Let \(S f(x)=f(1-x)\).  If \(d(x)=d(1-x)\), then \(K_\ell S=SK_\ell\).  The
constant output is even, while

\[
 S\phi_k=(-1)^k\phi_k.
\]

Thus

\[
 \langle1,e^{-tK_\ell}\phi_k\rangle=0
 \quad\text{for every odd }k\text{ and every }t\ge0.
\]

The same statement is exact on a reflection-symmetric grid.  Therefore a
response Gram may converge at second order to a singular matrix.  Rank
stability requires the manuscript's explicit condition that the limiting
smallest singular value be positive; convergence alone cannot supply it.

## 6. Fixed domain is essential

The compact-Mosco argument uses Rellich compactness on \([0,1]\).  It does not
transfer unchanged to an expanding domain.  If the lattice spacing is held
fixed while \(n\to\infty\), the limiting heat semigroup on a line or half-line
is not compact.  If the profile is instead stretched as \(d_j=d((j+1/2)/n)\),
its local modulation gradient is \(O(1/n)\), and directional coupling can
flatten.  Fixed-domain refinement and thermodynamic expansion are different
limits and should not share a theorem statement.

## 7. Corrections incorporated into the proof memo

The final proof memo incorporates the audit's local corrections:

1. the duplicated definition of \(\beta_{\ell,h}\) was removed;
2. the piecewise-linear interpolation estimate is stated only for
   \(u\in H^2(0,1)\) satisfying \(u'(0)=u'(1)=0\), which is sufficient because
   both primal and dual Neumann resolvent solutions have this compatibility;
3. the Mosco cell-average map \(P_h\) is separated from the exact lumped load
   map \(Q_h\); and
4. the boundary quadrature discussion uses the global
   \(h^2\|I_hz\|_{H^1}\|I_hw\|_{H^1}\) estimate rather than assigning an
   unqualified \(O(h^2)\) defect to an arbitrary boundary hat.

The remainder of the fixed-mode reduction, reaction-rate Duhamel estimate,
target midpoint normalization, finite-history Gram argument, and continuum
Galerkin tail structure passed this audit.

Quantitative norm-resolvent estimates for discrete Neumann operators are an
established numerical-analysis boundary rather than a novelty claim; for
context see Cornean, Garde, and Jensen,
[Discrete approximations to Dirichlet and Neumann Laplacians](https://arxiv.org/abs/2211.01974).
The OIG-specific contribution is the exact response reduction, physical port
normalization, and application of those approximation ideas to the directed
sensing Gram.

## 8. Ranked next tests

1. **Mollifier phase diagram.**  Prove the regimes
   \(\varepsilon_h/h\to\infty\), \(\varepsilon_h/h\to c\), and
   \(\varepsilon_h/h\to0\), crossed with fixed \(t>0\) and
   \(t_h/h^2\to\tau\).  Include nearest-cell and moment-preserving atom rules.
2. **Quantitative embedded-semigroup rate.**  Full embedded operator-norm
   convergence on \([t_0,T]\) is now established, clearly separated from the
   fixed response matrix and from \(t=0\).  Determine the sharp rate for the
   exact piecewise-constant reconstruction pair.
3. **Growing-mode map.**  Determine admissible relations among \(K_h,L_h,t_h\)
   using the exact \(k^4h^2\) eigenvalue defect and heat damping.
4. **Rough-coefficient ladder.**  Test cell averages versus point samples for
   \(BV\), \(C^{0,\alpha}\), and merely \(L^\infty\) modulations.  Formulate the
   rate in terms of an explicit quadrature/approximation modulus rather than a
   vague regularity adjective.
5. **Symmetry-breaking conditioning.**  Put
   \(d=d_{\rm even}+\epsilon d_{\rm odd}\) and derive the first nonzero power of
   \(\epsilon\) in each formerly invisible singular value.
6. **Port-metric invariance.**  Add tests which change source/output units one
   at a time and verify the predicted \(n^{\pm1/2}\) behavior, preventing the
   two-wrong-normalizations cancellation from masking a convention error.

## 9. Reproduction

The independent controls are in `oig_vi_adversarial_controls.py`; their tests
are in `test_oig_vi_adversarial_controls.py`.

Run:

    python -m unittest -v test_oig_vi_adversarial_controls.py

The seven tests cover smooth second order, discontinuous first order,
half-Hölder intermediate order, atomic placement order, the endpoint-spacing
trap, the shrinking-time/growing-mode constant gap, and exact reflection
invisibility.
