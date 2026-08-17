# Operational Information Geometry III

## Composition, hidden interactions, and positive multiscale observation

- **Research lead, mathematics, software, and manuscript:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Cross-branch methodological input:** *Arithmetic Sensing V*
- **Date:** 13 August 2026
- **Status:** third theorem-and-falsification layer; not peer reviewed

## Abstract

The first two layers of Operational Information Geometry derived geometry from
observable histories and identified its dependence on sensor and time
protocols. This paper studies composition. Two questions are separated:

1. how do operational geometries combine when two systems are independent?
2. which measurements distinguish genuine dynamics coupling from a geometry
   created by the observer's composition rule?

For independent generators \(L_A,L_B\), the composite generator is the
Kronecker sum

\[
 L_0=L_A\otimes I+I\otimes L_B,
\]

and its semigroup factors exactly. Two different operational composition laws
then arise. A two-clock tensor protocol has exactly factored Gram
\(G_A\otimes G_B\). A pooled local-marginal protocol gives the Cartesian law

\[
 d^2((a,b),(a',b'))=d_A(a,a')^2+d_B(b,b')^2
\]

on pure product states. It separates every pure state but has the complete
correlation kernel

\[
 \mathbf1_A^\perp\otimes\mathbf1_B^\perp,
\]

of dimension \((n_A-1)(n_B-1)\). For two six-state systems, the history rank
is 11 and the kernel dimension is 25, both exactly as predicted. Thus even
independent systems have no unique “composite geometry” until the permitted
observers are declared.

We introduce a controlled mixed dissipative interaction

\[
 L_g=L_A\otimes I+I\otimes L_B+gL_A\otimes L_B,
 \qquad g\geq0.
\]

Its product-mode eigenvalues are

\[
 \lambda_{ij}=\alpha_i+\beta_j+g\alpha_i\beta_j.
\]

The signed mixed spectral contrast

\[
 \kappa_{ij}
 =\lambda_{ij}-\lambda_{i0}-\lambda_{0j}+\lambda_{00}
 =g\alpha_i\beta_j
\]

cancels all additive subsystem dynamics. A two-time decay ratio cancels sensor
gain as well. Sixteen unrelated four-channel random joint sensors recover
\(g=0.4\) over all 25 nonconstant product modes with maximum numerical error
\(1.14\times10^{-14}\).

The interaction is exactly invisible to every local marginal history. This
comes with a sharp scope boundary: \(L_g\) is symmetric, conservative, and
positive semidefinite, but not a Markov graph Laplacian. We prove that a
nonzero linear Markov generator cannot preserve both marginals for every
initial distribution. A genuine diagonal-edge Markov interaction at
\(g=0.4\) changes the local marginal history by \(12.64\%\), as the no-go
theorem requires.

Finally, Arithmetic Sensing V's cancellation and positive time-diversity
principles are transferred to interaction sensing. Six candidate time scales
are mixed by a finite linear program that maximizes the worst fraction of each
mode's oracle Fisher information. Adaptive mode exchange terminates after all
25 modes are audited. The dyadic design

\[
 \frac1{4096}(310,1873,0,0,1307,606)
\]

on scale centers \((0.06,0.12,0.24,0.48,0.96,1.92)\) raises the worst relative
information from the best single scale's \(0.17435\) to \(0.45550\), a factor
of \(2.6125\). This is a reproducible finite optimization result, not an
interval-certified global optimum.

## 1. Why composition needs its own operational rule

Suppose systems \(A\) and \(B\) have latent spaces
\(X_A=\mathbb R^{n_A}\) and \(X_B=\mathbb R^{n_B}\). The composite latent
space is

\[
 X_{AB}=X_A\otimes X_B.
\]

That tensor product does not by itself select a metric. At least three observer
architectures are natural:

1. **local marginal observation:** measure each subsystem while summing over
   the other;
2. **tensor observation:** correlate every history channel of \(A\) with every
   history channel of \(B\);
3. **generic joint observation:** use channels on the composite space that need
   not factor or localize.

These protocols have different Gramians even for exactly independent
dynamics. A non-product operational metric is therefore not, by itself,
evidence of interaction.

The Stage III policy is:

> Establish the exact composition law associated with each observer class,
> use the corresponding independent dynamics as the zero-interaction control,
> and call only deviations from that declared control an interaction signal.

## 2. Exact independent composition

Let \(L_A,L_B\) be symmetric positive semidefinite generators with constant
zero modes. Define

\[
 L_0=L_A\otimes I_B+I_A\otimes L_B.
\]

### Theorem 2.1 — semigroup factorization

For every \(t\geq0\),

\[
 e^{-tL_0}=e^{-tL_A}\otimes e^{-tL_B}.
\]

#### Proof

The matrices \(L_A\otimes I_B\) and \(I_A\otimes L_B\) commute. Therefore
the exponential of their sum is the product of their exponentials. The two
factors are \(e^{-tL_A}\otimes I_B\) and
\(I_A\otimes e^{-tL_B}\); multiplying them gives the result. \(\square\)

Equivalently, if \(L_Au_i=\alpha_i u_i\) and
\(L_Bv_j=\beta_jv_j\), then \(u_i\otimes v_j\) is an eigenvector of
\(L_0\) with eigenvalue \(\alpha_i+\beta_j\).

### 2.1 Two-clock tensor protocol

Let \(\mathcal O_A\) and \(\mathcal O_B\) be complete subsystem history
maps, possibly using different time sets. Define

\[
 \mathcal O_\otimes=\mathcal O_A\otimes\mathcal O_B.
\]

Operationally, this protocol forms every pair of subsystem history channels;
it is a two-clock construction rather than a single synchronized composite
time.

### Theorem 2.2 — tensor Gram law

The tensor protocol satisfies

\[
 G_\otimes
 =\mathcal O_\otimes^{\mathsf T}\mathcal O_\otimes
 =G_A\otimes G_B.
\]

#### Proof

Use
\((R\otimes S)^{\mathsf T}(R\otimes S)
=(R^{\mathsf T}R)\otimes(S^{\mathsf T}S)\). \(\square\)

For pure product states, the signature is
\(o_a^A\otimes o_b^B\). Its geometry is a tensor geometry; it is generally
not the Cartesian sum of subsystem squared distances.

### 2.2 Local Cartesian protocol

Let \(\mathbf1_A,\mathbf1_B\) denote all-ones vectors. Define

\[
 \mathcal O_{\rm loc}=
 \begin{bmatrix}
 \mathcal O_A\otimes\mathbf1_B^{\mathsf T}\\
 \mathbf1_A^{\mathsf T}\otimes\mathcal O_B
 \end{bmatrix}.
\]

For a pure product state,

\[
 \mathcal O_{\rm loc}(e_a\otimes e_b)
 =\begin{bmatrix}\mathcal O_Ae_a\\\mathcal O_Be_b\end{bmatrix}.
\]

### Theorem 2.3 — Cartesian pure-state law

For pure product states,

\[
 d_{\rm loc}((a,b),(a',b'))^2
 =d_A(a,a')^2+d_B(b,b')^2.
\]

#### Proof

Subtract the two displayed signatures and take the squared Euclidean norm of
the stacked vector. \(\square\)

The result is exact for any subsystem history maps. It is selected by the
local observer architecture, not forced by the tensor product alone.

## 3. The correlation kernel

For a general joint vector \(x\in X_A\otimes X_B\), local observation depends
only on the two marginals

\[
 M_A=I_A\otimes\mathbf1_B^{\mathsf T},
 \qquad
 M_B=\mathbf1_A^{\mathsf T}\otimes I_B.
\]

### Theorem 3.1 — local observers miss all pure correlations

If the subsystem history maps are injective, then

\[
 \ker\mathcal O_{\rm loc}
 =\mathbf1_A^\perp\otimes\mathbf1_B^\perp.
\]

Consequently,

\[
 \dim\ker\mathcal O_{\rm loc}
 =(n_A-1)(n_B-1),
\]

and

\[
 \operatorname{rank}\mathcal O_{\rm loc}=n_A+n_B-1.
\]

#### Proof

Decompose each subsystem space as
\(\operatorname{span}\{\mathbf1\}\oplus\mathbf1^\perp\). The joint space
then splits orthogonally into constant, left-local, right-local, and
\(\mathbf1_A^\perp\otimes\mathbf1_B^\perp\) components. Both marginals
annihilate the last component. On the first three components, at least one
marginal is nonzero, and injective subsystem histories preserve it. The
dimension formulas follow. \(\square\)

This is the two-system version of Stage II's common blind-subspace theorem.
Local observers can distinguish all pure pairs while remaining blind to every
change in correlation that preserves both marginals.

## 4. Reference composition experiment

Each subsystem is the six-state exponent path for one prime:

\[
 \{2^a:0\leq a<6\},
 \qquad
 \{3^b:0\leq b<6\}.
\]

The independent composite has 36 states \((a,b)\). Complete subsystem histories
are sampled at 14 geometric times from 0.02 to 1.

| independent diagnostic | computed | exact prediction |
|---|---:|---:|
| maximum Cartesian squared-distance error | \(3.91\times10^{-14}\) | 0 |
| local history rank | 11 | \(6+6-1=11\) |
| local correlation-kernel dimension | 25 | \(5\cdot5=25\) |
| minimum local pure-state margin | 3.53562 | positive |
| tensor history rank | 36 | 36 |
| relative tensor-Gram factorization error | \(2.92\times10^{-16}\) | 0 |

The independent controls pass. They also make the conceptual boundary
concrete: the local protocol gives Cartesian geometry, while the two-clock
protocol gives tensor geometry. Both are correct relative to their declared
operations.

## 5. A mixed dissipative interaction

For \(g\geq0\), define

\[
 L_g=L_A\otimes I+I\otimes L_B+gL_A\otimes L_B.
\]

All three terms commute and are simultaneously diagonalized by product
eigenvectors.

### Theorem 5.1 — exact mixed spectrum

If \(L_Au_i=\alpha_i u_i\) and \(L_Bv_j=\beta_jv_j\), then

\[
 L_g(u_i\otimes v_j)
 =(\alpha_i+\beta_j+g\alpha_i\beta_j)(u_i\otimes v_j).
\]

The generator is symmetric, positive semidefinite, and conservative:
\(L_g\mathbf1=0\).

#### Proof

Apply each Kronecker term to \(u_i\otimes v_j\). Its three eigenvalues are
\(\alpha_i\), \(\beta_j\), and \(g\alpha_i\beta_j\), respectively. They are
nonnegative. Both subsystem Laplacians kill their constant vectors, proving
conservation. \(\square\)

### Definition 5.2 — mixed spectral curvature

Define

\[
 \kappa_{ij}
 =\lambda_{ij}-\lambda_{i0}-\lambda_{0j}+\lambda_{00}.
\]

This is a finite mixed second difference of decay rates. It deserves the word
“curvature” only in this restricted algebraic sense: it measures failure of an
additive product spectrum. It is not Riemannian curvature or spacetime
curvature.

### Corollary 5.3 — exact interaction witness

For the mixed model,

\[
 \boxed{\kappa_{ij}=g\alpha_i\beta_j.}
\]

In the independent control \(g=0\), every mixed curvature vanishes.

The order of operations matters. The four signed rates must be combined before
an absolute value is taken. Replacing the signed contrast by a sum of
magnitudes destroys the cancellation of the additive subsystem dynamics.

## 6. Which observers see the interaction?

### Theorem 6.1 — exact marginal blindness of the mixed model

For every \(t\geq0\),

\[
 M_Ae^{-tL_g}=e^{-tL_A}M_A,
 \qquad
 M_Be^{-tL_g}=e^{-tL_B}M_B.
\]

Thus every local marginal history is independent of \(g\).

#### Proof

Because \(\mathbf1_B^{\mathsf T}L_B=0\),

\[
 M_A(L_A\otimes I)=L_AM_A,
 \quad M_A(I\otimes L_B)=0,
 \quad M_A(L_A\otimes L_B)=0.
\]

Hence \(M_AL_g=L_AM_A\). Apply this identity term by term to the exponential
series. The right marginal is symmetric. \(\square\)

This is an exact observer obstruction, not a small-signal effect. Local data
cannot distinguish any two strengths \(g\) in this model.

### 6.1 The Markov boundary

The mixed generator is not a graph Laplacian: \(L_A\otimes L_B\) creates some
positive off-diagonal entries. Its exponential can have negative entries, so
it evolves signed information perturbations rather than arbitrary probability
distributions.

This limitation is unavoidable if exact marginal blindness is required for
every state.

### Theorem 6.2 — no nontrivial universally marginal-blind Markov interaction

Let \(K\) be a finite continuous-time Markov graph Laplacian on the product
states: its off-diagonal entries are nonpositive and its column sums vanish.
If

\[
 M_AK=0
 \quad\text{and}\quad
 M_BK=0,
\]

then \(K=0\).

#### Proof

Fix a column corresponding to \((a,b)\). For any \(a'\ne a\), the
\(a'\)-component of \(M_AKe_{(a,b)}\) is a sum of off-diagonal entries
\(K_{(a',b'),(a,b)}\), all nonpositive. The sum is zero, so every such entry is
zero. Therefore no transition changes the first coordinate. Applying the same
argument to \(M_BK=0\) shows that no transition changes the second coordinate.
No off-diagonal transition remains, and conservation forces the diagonal to
vanish. \(\square\)

A truly stochastic interaction can be locally invisible for selected initial
states or finite protocols, but not universally invisible to both complete
marginals in this linear single-copy model.

### 6.2 Genuine Markov control

As a control, add both diagonal edges to every square cell of the \(6\times6\)
product grid. This interaction is an ordinary graph Laplacian and its heat
kernel is nonnegative.

At \(g=0.4\):

| diagnostic | result |
|---|---:|
| graph-Laplacian sign and conservation checks | pass |
| minimum heat-kernel entry at \(t=0.1\) | \(1.45\times10^{-9}\) |
| relative local-marginal history change | 0.12641 |

The local change is not a defect. It is the behavior forced by Theorem 6.2.

## 7. Sensor-independent recovery of the mixed coupling

Let \(w_{ij}=u_i\otimes v_j\). For any joint sensor \(C\) with
\(Cw_{ij}\ne0\),

\[
 \|Ce^{-tL_g}w_{ij}\|_2
 =e^{-t\lambda_{ij}}\|Cw_{ij}\|_2.
\]

Therefore two times \(t_1<t_2\) give

\[
 \widehat\lambda_{ij}
 =\frac{\log\|Ce^{-t_1L_g}w_{ij}\|_2
       -\log\|Ce^{-t_2L_g}w_{ij}\|_2}
       {t_2-t_1}
 =\lambda_{ij}.
\]

Sensor gain cancels. Combine four such rates in the signed mixed contrast and
obtain

\[
 \widehat g_{ij}
 =\frac{
 \widehat\lambda_{ij}-\widehat\lambda_{i0}
 -\widehat\lambda_{0j}+\widehat\lambda_{00}}
 {\alpha_i\beta_j}.
\]

### Reference result

For \(g=0.4\), all 25 nonconstant product modes were tested under 16 unrelated
four-channel sign sensors at times 0.05 and 0.35.

| diagnostic | result |
|---|---:|
| total coupling estimates | 400 |
| smallest tested sensor gain | 0.11815 |
| mean recovered \(g\) | 0.4000000000000 |
| standard deviation across estimates | \(1.45\times10^{-15}\) |
| maximum absolute error | \(1.14\times10^{-14}\) |
| exact curvature-formula error | \(2.22\times10^{-15}\) |

This is a noiseless finite identity check. Under noise, logarithms of small
amplitudes become unstable; the multiscale design below addresses observation
allocation, not that identity itself.

Preparing a signed eigenmode can be interpreted as comparing the responses to
two nearby probability mixtures around the uniform state. It is an active
laboratory capability, not passive recovery from one unknown initial state.

## 8. Geometry can move less than the interaction spectrum

Use complete observation at 14 times from 0.02 to 1. Let \(G_0\) be the
independent Gram and \(G_g\) the coupled Gram. Define

\[
 \eta_g=
 \left\|G_0^{-1/2}(G_g-G_0)G_0^{-1/2}\right\|_2.
\]

### Proposition 8.1 — relative Gram deformation bound

If \(\eta_g<1\), then every vector satisfies

\[
 (1-\eta_g)v^{\mathsf T}G_0v
 \leq v^{\mathsf T}G_gv
 \leq(1+\eta_g)v^{\mathsf T}G_0v.
\]

#### Proof

Apply the operator-norm bound to
\(G_0^{-1/2}(G_g-G_0)G_0^{-1/2}\) and substitute
\(G_0^{1/2}v\). \(\square\)

The strength sweep is:

| \(g\) | complete Gram change | relative-form deformation \(\eta_g\) | pure-metric dilation | local history change |
|---:|---:|---:|---:|---:|
| 0.05 | 0.01491 | 0.06673 | 1.01127 | \(1.54\times10^{-15}\) |
| 0.10 | 0.02875 | 0.12655 | 1.02203 | \(1.74\times10^{-15}\) |
| 0.20 | 0.05375 | 0.22952 | 1.04226 | \(1.92\times10^{-15}\) |
| 0.40 | 0.09560 | 0.38753 | 1.07856 | \(1.74\times10^{-15}\) |
| 0.80 | 0.15828 | 0.59108 | 1.13939 | \(2.05\times10^{-15}\) |

At \(g=0.4\), the complete history Gram changes by nearly 10%, yet the finite
pure-state metric changes by scale-free dilation only 1.079. Pure geometry can
therefore look stable while joint dynamical modes carry a clear interaction.
The mixed spectral contrast is more specific than raw metric deformation.

A 12-channel random joint sensor sees a relative Gram change 0.10579 at
\(g=0.4\), whereas the local observer sees exactly none. Detection is a joint
property of dynamics and protocol.

## 9. What Arithmetic Sensing V contributes

The canonical Arithmetic Sensing V manuscript was audited as a separate line
of work. Its number-field recovery conclusions do not transfer to this toy
universe. Four methodological principles do.

### 9.1 Preserve cancellation before bounding

Arithmetic Sensing V found that taking absolute values before exposing a
shared signed numerator destroyed designed cancellation. Here, the analogous
mistake would be to take magnitudes of the four decay rates separately. The
signed mixed contrast cancels the entire additive product spectrum first:

\[
 (\alpha_i+\beta_j+g\alpha_i\beta_j)
 -\alpha_i-\beta_j+0=g\alpha_i\beta_j.
\]

### 9.2 Time and sample count are different resources

An interaction mode with decay rate \(\lambda\) contributes different
information at different times. Repeating a poor time cannot be treated as
equivalent to observing a useful scale.

### 9.3 Positive time diversity

Arithmetic Sensing V combined centered windows with positive weights. Here we
combine candidate observation schedules with positive weights, retaining a
genuine acquisition measure and a linear information objective.

### 9.4 Adaptive mode exchange

Optimizing on a guessed list of dangerous modes can miss a worse held-out
mode. The Stage III optimizer begins with the slowest and fastest modes, audits
all 25 interaction modes, adds the worst exposed mode, and repeats until the
audited worst mode is already constrained.

The Mellin-tail bounds, degree frontiers, Arb/MPFR enclosures, exact LP duals,
and stopping theorem of Arithmetic Sensing V are **not** imported. Stage III's
multiscale result remains a binary64 finite optimization with a complete
enumerated audit, not a formal interval certificate.

## 10. Positive multiscale interaction design

Suppose a known-amplitude scalar mode is observed with independent Gaussian
noise:

\[
 z(t)=e^{-\lambda t}+\varepsilon(t),
 \qquad \varepsilon(t)\sim N(0,\nu^2).
\]

Ignoring the common factor \(\nu^{-2}\), the Fisher information for
\(\lambda\) at a schedule \(\mathcal T\) is

\[
 J_{\mathcal T}(\lambda)
 =\sum_{t\in\mathcal T}t^2e^{-2\lambda t}.
\]

For a positive schedule mixture \(w_r\geq0\), \(\sum_rw_r=1\), information
adds:

\[
 J_w(\lambda)=\sum_rw_rJ_r(\lambda).
\]

For each declared interaction-mode rate \(\lambda_k\), normalize by its best
candidate schedule:

\[
 Q_{rk}=\frac{J_r(\lambda_k)}{\max_sJ_s(\lambda_k)}.
\]

The robust design problem is the linear program

\[
 \max_{w,z}\ z
 \quad\text{subject to}\quad
 \sum_rw_rQ_{rk}\geq z\ \text{for every }k,
 \quad w\geq0,
 \quad\sum_rw_r=1.
\]

It maximizes the worst fraction of the per-mode schedule oracle.

### 10.1 Candidate schedules

The six scale centers are

\[
 c=(0.06,0.12,0.24,0.48,0.96,1.92).
\]

Each center uses five relative times

\[
 c_r(0.5,0.7,1,1.4,2).
\]

At \(g=0.4\), the 25 interaction-mode rates range from 0.56462 to 13.03538.

### 10.2 Exchange and audit

| exchange round | constrained modes | restricted floor | audited floor | new worst mode |
|---:|---:|---:|---:|---:|
| 1 | 2 | 0.50376 | 0.16620 | 6 |
| 2 | 3 | 0.46035 | 0.39388 | 7 |
| 3 | 4 | 0.45591 | 0.45108 | 3 |
| 4 | 5 | 0.45554 | 0.45554 | already constrained |

The finite exchange terminates after five active mode constraints. Every one
of the 25 declared modes is then audited.

### 10.3 Design result

The continuous optimum is

\[
 w_*=(0.0757212,0.4571763,0,0,0.3191802,0.1479223),
\]

with worst oracle fraction 0.4555442. Rounding to denominator 4096 while
preserving positivity and unit mass gives

\[
 \boxed{
 w_{\rm dyadic}
 =\frac1{4096}(310,1873,0,0,1307,606)}.
\]

Its audited floor is 0.45549784. The best single candidate is center 0.24,
whose worst fraction is only 0.17435259. Therefore

\[
 \frac{0.45549784}{0.17435259}=2.61251.
\]

The design uses both early scales and late scales. Intermediate centers 0.24
and 0.48 receive zero weight even though 0.24 is the best individual schedule.
Robust composition is not obtained by selecting the best average scale; it is
obtained by complementing weaknesses across modes.

This is an exact evaluation of the printed dyadic weights in binary64 over all
25 declared modes. It is not a proof of optimality over continuous times,
other schedule shapes, or unenumerated systems.

## 11. What Stage III establishes

### Exact theorems

1. Independent Kronecker-sum dynamics factorizes at every time.
2. Two-clock tensor histories have Gram \(G_A\otimes G_B\).
3. Local histories give an exact Cartesian pure-state metric.
4. Local histories have correlation kernel
   \(\mathbf1_A^\perp\otimes\mathbf1_B^\perp\).
5. The mixed dissipative generator has spectrum
   \(\alpha_i+\beta_j+g\alpha_i\beta_j\).
6. Its signed mixed spectral curvature is exactly \(g\alpha_i\beta_j\).
7. It is exactly invisible to all complete marginal histories.
8. No nonzero linear Markov generator is universally invisible to both
   marginals.
9. Two-time rate ratios remove fixed sensor gain whenever the mode is seen.
10. Relative Gram perturbations give explicit bi-Lipschitz quadratic-form
    bounds.

### Computed finite results

1. All independent composition rank and factorization identities pass to
   numerical precision.
2. Sixteen random joint sensors recover \(g=0.4\) over all tested modes with
   maximum error \(1.14\times10^{-14}\).
3. Local histories remain unchanged to \(2.1\times10^{-15}\) throughout the
   mixed-coupling sweep.
4. A genuine Markov diagonal interaction changes the local history by 12.64%
   at \(g=0.4\).
5. Positive multiscale design improves worst relative Fisher information by a
   factor 2.6125 over the best single candidate schedule.

### Falsification boundaries

1. A non-Cartesian operational metric does not prove interaction; tensor or
   generic joint sensors can create one under independent dynamics.
2. Stable pure-state geometry does not prove absence of interaction.
3. Local marginal agreement does not prove independence outside the Markov
   model class.
4. Exact universal marginal blindness and nontrivial linear Markov dynamics
   cannot coexist.
5. The word “curvature” here names a mixed spectral defect, not physical
   spacetime curvature.

## 12. Literature and novelty boundary

Kronecker products, Kronecker sums, commuting matrix exponentials, Fisher
information, and finite linear programming are classical. Historical context
for Kronecker matrix algebra includes the direct-product and Kronecker-sum
treatment in [MacDuffee (1965)](https://doi.org/10.1016/S0076-5392(08)60714-6).
Positive design measures and minimax experimental-design ideas belong to the
classical optimal-design tradition; see
[Kiefer and Wolfowitz (1960)](https://doi.org/10.4153/CJM-1960-030-4).

The project contribution is the explicit synthesis:

1. distinguish Cartesian local and tensor two-clock operational composition;
2. connect their pure-state success to exact correlation kernels;
3. construct a marginal-blind mixed dissipative model and place it beside a
   Markov no-go theorem and Markov control;
4. use a sensor-gain-free signed mixed decay contrast as the interaction
   witness;
5. transfer Arithmetic Sensing V's positive multiscale and adaptive-exchange
   logic to finite interaction Fisher information.

The elementary tensor identities and optimization ingredients are not claimed
as new. Independent literature review and peer review are required before any
priority claim about the combined operational framework.

## 13. Scope and nonclaims

This paper does **not** establish:

- that physical systems use the mixed generator \(L_g\);
- a fundamental law of interaction or composition;
- quantum entanglement, despite the use of tensor products and correlations;
- spacetime curvature;
- positivity preservation for the marginal-blind mixed generator;
- passive identification of interactions from one unknown state;
- optimality of the multiscale design outside six candidate schedules and 25
  declared modes;
- interval-certified optimality of the dyadic design;
- a continuum or infinite-system limit;
- a connection to zeta zeros or the Riemann hypothesis.

The result is a controlled finite language for asking which composition and
interaction features survive specified observers.

## 14. Reproduction

Run the Stage III tests:

```sh
python -m unittest -v test_operational_information_geometry_iii.py
```

Recompute the independent composition controls, coupling sweep, random-sensor
witness, Markov control, and multiscale design:

```sh
python operational_information_geometry_iii.py --interaction-strength 0.4
```

Run all three Operational Information Geometry layers:

```sh
python -m unittest -v \
  test_operational_information_geometry.py \
  test_operational_information_geometry_ii.py \
  test_operational_information_geometry_iii.py
```

Validate the full repository:

```sh
python -m unittest discover -v
```

## 15. Next research order

### Immediate target — Stage IV: interventions and operational causal cones

Stage III shows that passive local marginals can miss a signed interaction and
that a Markov interaction must alter some marginal somewhere. Stage IV should
make “somewhere” and “when” precise using interventions.

Primary tasks:

1. define a directed response kernel from a localized perturbation in subsystem
   \(A\) to later observations in subsystem \(B\);
2. separate symmetric metric proximity from directed causal influence;
3. derive finite propagation bounds for the diagonal-edge Markov control;
4. compare passive blind subspaces with interventionally visible directions;
5. test whether different sufficiently rich local intervention protocols agree
   on an effective causal cone;
6. keep the signed mixed model as a linear-amplitude control while using the
   Markov model for probability propagation.

### Adjacent theorem target — certify the multiscale design

If Stage IV depends materially on the four-scale dyadic design, import the
stronger verification architecture of Arithmetic Sensing V: rational primal
and dual witnesses, outward interval evaluation, and an explicit stopping
claim over the declared schedule family. Until then, the current finite audit
is sufficient and accurately scoped.
