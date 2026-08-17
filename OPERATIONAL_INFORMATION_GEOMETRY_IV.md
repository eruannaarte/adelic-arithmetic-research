# Operational Information Geometry IV

## Interventions, finite causal jets, and Poisson causal envelopes

- **Research lead, mathematics, software, and manuscript:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Date:** 13 August 2026
- **Status:** fourth theorem-and-falsification layer; not peer reviewed

## Abstract

Operational Information Geometry I--III studied distances induced by observable
histories, protocol dependence, composition, and interactions. This fourth layer
adds interventions. For a generator \(L\), an intervention injection \(J_A\), and
an observation \(M_B\), define the directed response operator

\[
 R_{B\leftarrow A}(t)=M_Be^{-tL}J_A.
\]

This object is directional even when \(L\) and every diffusion distance derived
from it are symmetric.

We prove four main results.

First, independent product dynamics have exactly zero cross-response in both
directions for mass-preserving subsystem interventions. A reciprocal
diagonal-edge Markov interaction activates both directions.

Second, the symmetric graph Laplacian

\[
 L_{\to}=L_A\otimes I+I\otimes L_B+gD_A\otimes L_B,
 \qquad g\geq0,
\]

where \(D_A\) is nonnegative and diagonal, gives an exact one-way subsystem
channel. The \(A\)-marginal is autonomous, so

\[
 R_{A\leftarrow B}(t)=0
 \quad\hbox{for every }t\geq0,
\]

while \(A\)-interventions generally change the later \(B\)-marginal. In the
six-by-six reference model, the stacked \(A\to B\) response has norm
\(0.346783\), rank 5, and directionality index \(1-9.7\times10^{-15}\). The
reverse response has norm \(1.68\times10^{-15}\) and numerical rank 0. Thus a
reversible microscopic diffusion can produce directed macroscopic intervention
response relative to a declared subsystem partition.

Third, we prove a finite causal-jet theorem. In an \(N\)-dimensional linear
system, the channel \(Ce^{-tL}J\) vanishes for all time if and only if

\[
 CL^kJ=0,\qquad 0\leq k<N.
\]

More generally, the kernel of this finite stacked jet is exactly the subspace of
intervention directions invisible for every time. In the one-way model, the
forward jet has cumulative ranks \(0,1,3,5\) through derivative orders
\(0,1,2,3\). Exact autonomy, and an independent exact-rational calculation,
make every reverse coefficient zero. The floating audit only verifies that the
characteristic-time-scaled Taylor terms are below threshold; unscaled high
powers are not numerically stable. This replaces a sampled-time near-zero
observation with a finite algebraic certificate.

Fourth, continuous-time Markov evolution has no strict finite propagation cone
on a connected finite graph. Uniformization supplies the correct substitute. If
\(\Lambda\geq\max_x L_{xx}\), \(P=I-L/\Lambda\), and \(d(x,y)\) is support-graph
distance, then

\[
 \sum_{d(y,x)\geq r}\bigl(e^{-tL}\bigr)_{yx}
 \leq \Pr\{\operatorname{Pois}(\Lambda t)\geq r\}.
\]

All 36 states already have positive probability at \(t=0.02\), disproving a
strict cone. Nevertheless every measured distance-tail obeys the Poisson bound;
at \(t=0.2\), the actual masses beyond distances 1 through 6 are respectively
\(0.5595,0.1617,0.02515,0.002216,1.128\times10^{-4},2.861\times10^{-6}\), all
below their exact uniformization envelopes.

Finally, random compressed response sensors are compared with the complete
response geometry. Independently refreshing a single channel at 20 times gives
full response rank in all 32 seeds and median scale-free dilation \(2.614\),
whereas repeating one channel succeeds in 30 of 32 seeds and has median dilation
\(181.15\). With six refreshed channels the median falls to \(1.378\). These are
finite empirical protocol audits, not universal random-embedding theorems.

The unexpected conditioning gap motivated two further audits. The forward arrow
has full rank for all six localized \(B\)-backgrounds, but its endpoint-marginal
response vanishes when the intervention is tensorized with a stationary
\(B\)-profile: changing a diffusion rate cannot move that independent
equilibrium preparation. A trajectory sensor can still detect the changed jump
clock. Over 120 candidate times, a positive E-optimal response
design was therefore computed. Its six-time dyadic schedule attains weakest
information \(4.98241\times10^{-9}\), within \(1.061\times10^{-4}\) relative of
a floating dual upper bound and \(1.47\times10^6\) times the best single-time
floor. A subsequent Arb certificate rigorously brackets the finite-grid optimum
between \(4.982412\times10^{-9}\) and \(4.982942\times10^{-9}\). It does not
certify a continuum-time optimum.

## 1. Why passive geometry is not causality

A passive history map has the form

\[
 \mathcal O x=
 \begin{bmatrix}
 C_1e^{-t_1L}x\\
 \vdots\\
 C_me^{-t_mL}x
 \end{bmatrix}.
\]

Its Gram matrix is symmetric, and the associated distance between two latent
states is symmetric. Neither fact answers whether changing subsystem \(A\)
changes later observations of subsystem \(B\). Direction requires two distinct
operational declarations:

1. which perturbations count as interventions on the proposed source; and
2. which measurements count as responses of the proposed target.

This paper therefore does not attempt to infer causal direction from a passive
distance matrix. It defines a directed operator and tests it against zero,
reciprocal, and one-way controls.

The word *causal* is used in this finite model only for intervention-response
dependence. It does not assert relativistic causality, counterfactual causal
identification from uncontrolled data, or a fundamental causal structure of the
universe.

## 2. Declared interventions and response geometry

Let \(A\) and \(B\) have \(n_A,n_B\) states. Joint distributions are column
vectors in
\(\mathbb R^{n_A}\otimes\mathbb R^{n_B}\). Define the marginal maps

\[
 M_A=I_A\otimes\mathbf1_B^{\mathsf T},
 \qquad
 M_B=\mathbf1_A^{\mathsf T}\otimes I_B.
\]

Let \(H_A\) and \(H_B\) be orthonormal bases for the simplex tangent spaces
\(\mathbf1_A^\perp\) and \(\mathbf1_B^\perp\). Fix background states \(a_0,b_0\)
and define localized intervention injections

\[
 J_A=H_A\otimes e_{b_0},
 \qquad
 J_B=e_{a_0}\otimes H_B.
\]

Every column has zero total mass. For sufficiently small amplitude it is the
linearization of a valid probability intervention around a positive reference
distribution; the code works directly with its tangent.

### Definition 2.1 — directed response kernel

The response from an \(A\)-intervention to a later \(B\)-measurement is

\[
 R_{B\leftarrow A}(t)=M_Be^{-tL}J_A.
\]

The reverse response is a separately defined operator

\[
 R_{A\leftarrow B}(t)=M_Ae^{-tL}J_B.
\]

No transpose relation is assumed. At declared times \(t_1,\ldots,t_m\), stack
the response blocks into

\[
 \mathcal R_{B\leftarrow A}
 =\begin{bmatrix}R_{B\leftarrow A}(t_1)\\\vdots\\
 R_{B\leftarrow A}(t_m)\end{bmatrix}.
\]

Its response Gram

\[
 G_{B\leftarrow A}=\mathcal R_{B\leftarrow A}^{\mathsf T}
                    \mathcal R_{B\leftarrow A}
\]

defines a symmetric geometry on \(A\)-intervention directions. The geometry is
symmetric *within its source tangent*, while the label \(B\leftarrow A\) remains
directed. Swapping source and target constructs a different Gram.

### Definition 2.2 — directionality index

For stacked Frobenius norms \(s_{A\to B}\) and \(s_{B\to A}\), define

\[
 \Delta_{A,B}
 =\frac{s_{A\to B}-s_{B\to A}}
        {s_{A\to B}+s_{B\to A}}
\]

when the denominator is nonzero. It lies in \([-1,1]\). It is a descriptive
index, not a hypothesis-test statistic.

## 3. Independent and reciprocal controls

Let

\[
 L_0=L_A\otimes I+I\otimes L_B.
\]

### Theorem 3.1 — independent dynamics have no cross-response

For every \(t\geq0\),

\[
 M_Be^{-tL_0}J_A=0,
 \qquad
 M_Ae^{-tL_0}J_B=0.
\]

#### Proof

The product semigroup factors:

\[
 e^{-tL_0}=e^{-tL_A}\otimes e^{-tL_B}.
\]

Therefore

\[
 M_Be^{-tL_0}J_A
 =\bigl(\mathbf1_A^{\mathsf T}e^{-tL_A}H_A\bigr)
   \otimes\bigl(e^{-tL_B}e_{b_0}\bigr)=0,
\]

because \(\mathbf1_A^{\mathsf T}e^{-tL_A}=\mathbf1_A^{\mathsf T}\) and
\(\mathbf1_A^{\mathsf T}H_A=0\). The reverse identity is analogous. \(\square\)

The reciprocal control adds both diagonal edges in every square cell of the
six-by-six product grid. Its generator remains a symmetric graph Laplacian.
It activates equal cross-response norms \(0.175263\) in both directions and has
directionality index \(-2.38\times10^{-16}\). Under the declared localized
background, each cross-history has rank 2 rather than the maximum 5. The
control is therefore reciprocal but not fully informative; reciprocity and
recoverability are separate questions.

## 4. A symmetric microscopic generator with one-way macroscopic response

Let \(D_A=\operatorname{diag}(d_1,\ldots,d_{n_A})\) with \(d_a\geq0\), and set

\[
 L_{\to}=L_A\otimes I+I\otimes L_B+gD_A\otimes L_B,
 \qquad g\geq0.
\]

The interpretation is concrete: transitions in \(B\) retain the graph of
\(L_B\), but their rate depends on the current \(A\)-state through
\(1+gd_a\). Transitions in \(A\) do not depend on \(B\).

### Theorem 4.1 — Markov validity and reversibility

If \(L_A,L_B\) are symmetric graph Laplacians, then \(L_{\to}\) is a symmetric
graph Laplacian.

#### Proof

All three Kronecker terms are symmetric. Their off-diagonal entries are
nonpositive: the first two are graph Laplacians on coordinate edges, while
\(D_A\otimes L_B\) is a nonnegative blockwise rescaling of \(L_B\). Each term
kills the all-ones vector, so row and column sums vanish. \(\square\)

Thus \(e^{-tL_{\to}}\) is a symmetric stochastic kernel and the uniform
distribution is reversible.

### Theorem 4.2 — exact marginal autonomy and one-way response

The \(A\)-marginal obeys

\[
 M_AL_{\to}=L_AM_A
\]

and hence

\[
 M_Ae^{-tL_{\to}}=e^{-tL_A}M_A.
\]

Consequently, every intervention \(J\) with \(M_AJ=0\) has exactly zero later
\(A\)-response. In particular,

\[
 R_{A\leftarrow B}(t)=0
\]

for all \(t\geq0\).

#### Proof

Multiplying the three generator terms by
\(M_A=I_A\otimes\mathbf1_B^{\mathsf T}\) gives

\[
 M_A(L_A\otimes I)=L_AM_A,
\]

while the remaining terms vanish because
\(\mathbf1_B^{\mathsf T}L_B=0\). Equality of the semigroups follows from the
power series or the uniqueness of the marginal differential equation. Finally,
\(M_AJ_B=e_{a_0}(\mathbf1_B^{\mathsf T}H_B)=0\). \(\square\)

### Proposition 4.3 — the forward channel activates at first order

The forward derivative at zero is

\[
 \frac{d}{dt}R_{B\leftarrow A}(0)
 =-g\bigl(\mathbf1_A^{\mathsf T}D_AH_A\bigr)
       \otimes\bigl(L_Be_{b_0}\bigr).
\]

It is nonzero whenever the modulation is nonconstant in an intervention
direction and the \(B\)-background is not stationary.

#### Proof

Differentiate the exponential. The two independent terms vanish under the
same zero-sum calculation as Theorem 3.1. The mixed term factors into the
displayed expression. \(\square\)

### Corollary 4.4 — metric symmetry does not imply causal reciprocity

The microscopic generator and heat kernel can be symmetric while the declared
subsystem intervention relation is exactly directed.

This is not a violation of microscopic reversibility. State-space adjacency
and intervention-response dependence answer different questions. In this
example the weighted product graph is undirected, but one coordinate controls
the rate attached to edges of the other coordinate.

For \(D_A=\operatorname{diag}(0,0.2,0.4,0.6,0.8,1)\), \(g=0.8\), localized
backgrounds \(a_0=b_0=0\), and 20 times from \(0.01\) to \(2\), the computed
comparison is:

| generator | \(\|\mathcal R_{B\leftarrow A}\|_F\) | rank | \(\|\mathcal R_{A\leftarrow B}\|_F\) | rank | \(\Delta_{A,B}\) |
|---|---:|---:|---:|---:|---:|
| independent | \(1.73\times10^{-15}\) | 0 | \(1.57\times10^{-15}\) | 0 | 0 |
| reciprocal diagonal-edge | 0.175263 | 2 | 0.175263 | 2 | \(-2.38\times10^{-16}\) |
| one-way rate modulation | 0.346783 | 5 | \(1.68\times10^{-15}\) | 0 | \(1-9.7\times10^{-15}\) |

The tiny nominal responses in the exact-zero cases are floating-point matrix
exponential residue. They are not treated as physical signals.

### Theorem 4.5 — stationary tensor-background endpoint silence

Let \(b\in\ker L_B\) and replace the localized injection by

\[
 J_A^{(b)}=H_A\otimes b.
\]

Then

\[
 M_Be^{-tL_{\to}}J_A^{(b)}=0
\]

for every \(t\geq0\).

#### Proof

The subspace \(X_A\otimes\operatorname{span}\{b\}\) is invariant under
\(L_{\to}\). On it, both terms containing \(L_B\) vanish, leaving only
\(L_A\otimes I\). Consequently

\[
 e^{-tL_{\to}}(H_A\otimes b)
 =(e^{-tL_A}H_A)\otimes b.
\]

Applying \(M_B=\mathbf1_A^{\mathsf T}\otimes I_B\) gives zero because
\(\mathbf1_A^{\mathsf T}e^{-tL_A}H_A=0\). \(\square\)

This sharpens the interpretation of the arrow. The theorem requires the full
factorized injection \(H_A\otimes b\), not merely a joint perturbation whose
\(B\)-marginal happens to be stationary. Correlated preparations are outside
its hypothesis. The reverse \(B\to A\) channel is forbidden for every declared
background, while the forward \(A\to B\) endpoint channel activates away from
the stationary tensor preparation. It is not a claim that every
\(A\)-perturbation produces a visible \(B\)-change in every context, nor that
path-space observables are silent at equilibrium.

Numerically, each of the six pure \(B\)-background states gives forward rank 5.
The response norms range from \(0.346783\) to \(0.395404\), and response-matrix
condition numbers range from \(1.868\times10^3\) to
\(2.785\times10^3\). The uniform stationary background gives norm
\(1.05\times10^{-15}\) and rank 0, agreeing with the theorem.

## 5. Finite causal jets

Sampled times can only show that a channel was small at those samples. Linear
finite-dimensional dynamics allow a stronger statement.

### Definition 5.1 — causal jet

For a response \(F(t)=Ce^{-tL}J\), define its order-\(q\) jet by

\[
 \mathcal J_q(C,L,J)=
 \begin{bmatrix}
 CJ\\CLJ\\\vdots\\CL^qJ
 \end{bmatrix}.
\]

Signs and factorials from the exponential series do not affect its kernel or
rank.

### Theorem 5.2 — finite all-time vanishing certificate

If \(L\) is \(N\times N\), then

\[
 Ce^{-tL}J=0\quad\hbox{for all }t
\]

if and only if

\[
 CL^kJ=0,\qquad 0\leq k<N.
\]

#### Proof

If the response is identically zero, all derivatives at zero vanish, giving
the finite conditions. Conversely, Cayley--Hamilton expresses every power
\(L^k\), \(k\geq N\), as a linear combination of
\(I,L,\ldots,L^{N-1}\). Hence all coefficients in the exponential series vanish
after multiplication by \(C\) and \(J\). \(\square\)

### Theorem 5.3 — finite intervention quotient

For an intervention direction \(u\), the following are equivalent:

1. \(Ce^{-tL}Ju=0\) for every \(t\);
2. \(CL^kJu=0\) for \(0\leq k<N\);
3. \(u\in\ker\mathcal J_{N-1}(C,L,J)\).

Therefore

\[
 \operatorname{rank}\mathcal J_{N-1}
\]

is exactly the dimension of the all-time distinguishable intervention
quotient.

This is a response-channel version of the classical finite observability rank
idea. The statement is elementary, but it closes an important logical gap in
the present program: sampled response is upgraded to an all-time algebraic
claim.

### Definition 5.4 — causal order

If \(q\) is the first order for which \(CL^qJ\neq0\), call \(q\) the causal
order of the channel. Then

\[
 Ce^{-tL}J=\frac{(-t)^q}{q!}CL^qJ+O(t^{q+1}).
\]

In the reference model, the forward channel has causal order 1. When scaled by
a characteristic time \(0.1\), its cumulative jet ranks are

\[
 0,1,3,5
\]

through orders 0, 1, 2, and 3. All five \(A\)-simplex tangent directions are
therefore distinguishable from sufficiently rich short-time \(B\)-responses,
even though the instantaneous first derivative alone has rank 1.

For the reverse channel, the characteristic-time-scaled Taylor terms
\(0.1^k C L^kJ/k!\) through order 35 are below the declared \(10^{-11}\)
threshold, in agreement with the exact autonomy proof. Raw floating powers
amplify roundoff at high order and are not zero to absolute precision. The
structural identity (and exact-rational arithmetic), not the floating
threshold, is the certificate.

## 6. Passive visibility is not directed influence

Stage III found a 25-dimensional passive correlation kernel for independent
local marginal histories. Interactions can rotate some or all of those modes
into view. This does not make passive rank a causal-direction test.

| generator | simplex-tangent rank | simplex-tangent blind dimension | tangent condition number | \(A\to B\) rank | \(B\to A\) rank |
|---|---:|---:|---:|---:|---:|
| independent | 10 | 25 | 1.446 | 0 | 0 |
| reciprocal diagonal-edge | 26 | 9 | \(4.097\times10^3\) | 2 | 2 |
| one-way rate modulation | 35 | 0 | \(3.623\times10^7\) | 5 | 0 |

The directional interaction makes the passive local history algebraically
full rank, but its smallest singular value is only
\(2.76\times10^{-7}\). Thus two conclusions coexist:

1. there is no exact passive blind subspace in this finite model; and
2. stable recovery is still extremely poor.

The corresponding ambient ranks are 11, 27, and 36; each includes the conserved
total-mass direction and is not the correct space for comparing probability
differences. More importantly, full tangent rank 35 does not reveal that the reverse
\(B\to A\) intervention channel is exactly zero. Direction is supplied by the
ordered pair \((J,M)\), not by observability rank alone.

## 7. Continuous-time propagation has an approximate, not strict, cone

Let \(L\) be a finite Markov graph Laplacian under the column-vector convention:
off-diagonal entries are nonpositive and column sums vanish. Choose

\[
 \Lambda\geq\max_xL_{xx},
 \qquad P=I-\frac{L}{\Lambda}.
\]

Then \(P\) is column stochastic and nonnegative.

### Theorem 7.1 — uniformization identity

For every \(t\geq0\),

\[
 e^{-tL}
 =e^{-\Lambda t}
  \sum_{k=0}^{\infty}\frac{(\Lambda t)^k}{k!}P^k.
\]

#### Proof

Since \(L=\Lambda(I-P)\) and \(I\) commutes with \(P\), expand
\(e^{-\Lambda t(I-P)}=e^{-\Lambda t}e^{\Lambda tP}\). \(\square\)

This is the classical uniformization or randomization identity.

Let \(d(y,x)\) be shortest-path distance from \(x\) to \(y\) in the directed
support graph of \(P\), ignoring self-loops.

### Theorem 7.2 — Poisson causal envelope

Starting from state \(x\), for every integer \(r\geq1\),

\[
 \sum_{d(y,x)\geq r}(e^{-tL})_{yx}
 \leq \Pr\{N_t\geq r\},
 \qquad N_t\sim\operatorname{Pois}(\Lambda t).
\]

#### Proof

If \(d(y,x)\geq r\), then \((P^k)_{yx}=0\) for \(k<r\). Apply Theorem 7.1,
sum over such \(y\), and use that every column of \(P^k\) has total mass one.
\(\square\)

### Corollary 7.3 — no strict finite cone on a connected CTMC graph

If \(y\) is reachable from \(x\), then

\[
 (e^{-tL})_{yx}>0
\]

for every \(t>0\).

#### Proof

Some finite path length \(k\) has \((P^k)_{yx}>0\). Its term in the
uniformization series is strictly positive for \(t>0\), and all other terms are
nonnegative. \(\square\)

Thus a continuous-time Markov model is not finite-speed in the strict support
sense. Its operational cone must include a leakage tolerance.

### Definition 7.4 — effective radius

For tolerance \(0<\delta<1\), define

\[
 r_\delta(t)=\min\left\{r:
 \sum_{d(y,x)>r}(e^{-tL})_{yx}\leq\delta\right\}.
\]

Uniformization guarantees any radius satisfying

\[
 \Pr\{\operatorname{Pois}(\Lambda t)>r\}\leq\delta.
\]

For the one-way reference generator, \(\Lambda=5.28\), the source is the center
state \((2,2)\), and the graph shells have sizes

\[
 (1,4,8,10,8,4,1).
\]

At one-percent leakage:

| time | actual radius | Poisson-guaranteed radius | graph-capped guarantee |
|---:|---:|---:|---:|
| 0.02 | 1 | 1 | 1 |
| 0.05 | 2 | 2 | 2 |
| 0.10 | 2 | 3 | 3 |
| 0.20 | 3 | 4 | 4 |
| 0.50 | 4 | 7 | 6 |
| 1.00 | 5 | 11 | 6 |

The Poisson estimate is rigorous but becomes trivial once its radius exceeds
the finite graph eccentricity 6. At \(t=0.2\), the full tail audit is:

| minimum distance | actual mass | Poisson bound |
|---:|---:|---:|
| 1 | 0.559502 | 0.652156 |
| 2 | 0.161678 | 0.284832 |
| 3 | 0.0251510 | 0.0908850 |
| 4 | 0.00221581 | 0.0226157 |
| 5 | \(1.12820\times10^{-4}\) | 0.00459257 |
| 6 | \(2.86063\times10^{-6}\) | \(7.86094\times10^{-4}\) |

No violation occurs. Yet all 36 transition probabilities are already strictly
positive at \(t=0.02\), with the smallest equal to
\(6.22\times10^{-12}\). That is the explicit negative control against claiming
a hard light cone.

### 7.1 Two inequivalent causal geometries

The result exposes a useful distinction:

- the microscopic propagation envelope uses graph distance in the 36-state
  Markov chain and is undirected here because the generator is symmetric;
- the macroscopic subsystem response relation is directed because the
  \(A\)-marginal is autonomous while the \(B\)-marginal is not.

Neither geometry replaces the other. A future continuum theory must declare
which interventions, coarse-grainings, and leakage scale define its cone.

## 8. Protocol invariance on the response quotient

Let \(\mathcal R\) be the complete stacked response and let \(S\) be a
block-diagonal history sensor, possibly using a different output compression at
each time. The compressed response is \(S\mathcal R\).

### Proposition 8.1 — deterministic response-embedding criterion

If, for every \(z\in\operatorname{range}\mathcal R\),

\[
 (1-\varepsilon)\|z\|^2
 \leq\|Sz\|^2
 \leq(1+\varepsilon)\|z\|^2,
\]

then

\[
 (1-\varepsilon)G
 \preceq \widetilde G
 \preceq(1+\varepsilon)G,
\]

where \(G=\mathcal R^{\mathsf T}\mathcal R\) and
\(\widetilde G=\mathcal R^{\mathsf T}S^{\mathsf T}S\mathcal R\). Consequently
all response distances are preserved within factors
\(\sqrt{1-\varepsilon}\) and \(\sqrt{1+\varepsilon}\).

#### Proof

Apply the assumed inequality to \(z=\mathcal Ru\) for every intervention
coefficient vector \(u\). The resulting quadratic-form inequalities are exactly
the Loewner inequalities. \(\square\)

This proposition states the right conditional notion of protocol invariance:
different instruments need not agree on the full output space; they need only
embed the realized response subspace.

The reference experiment compresses the six \(B\)-marginal channels with
normalized Rademacher sensors, either repeated at all 20 times or independently
refreshed. The scale-free dilation is the square root of the ratio between the
largest and smallest generalized Gram eigenvalues. It measures shape after
allowing an arbitrary global gain; it is not by itself the unrescaled
\((1\pm\varepsilon)\) guarantee in Proposition 8.1. The source norm and output
noise metric must also be declared before response magnitudes can be compared
across instruments.

| channels/time | repeated full-rank fraction | repeated median dilation | refreshed full-rank fraction | refreshed median dilation |
|---:|---:|---:|---:|---:|
| 1 | 0.9375 | 181.150 | 1.0000 | 2.6138 |
| 2 | 1.0000 | 4.5945 | 1.0000 | 1.8750 |
| 3 | 1.0000 | 2.6958 | 1.0000 | 1.6720 |
| 4 | 1.0000 | 2.1638 | 1.0000 | 1.6097 |
| 6 | 1.0000 | 1.7891 | 1.0000 | 1.3782 |

Each fraction uses 32 fixed seeds. The complete response Gram is itself badly
conditioned, \(3.49\times10^6\), because later causal-jet directions are much
weaker than the leading one. Refreshing sensors across time substantially
reduces the additional compression bottleneck.

This is evidence for conditional protocol stability, not a proof that these
finite channel counts work for all random seeds or all generators.

## 9. Positive multiscale design for weak causal directions

The complete forward response has rank 5, but its Gram condition number is
\(3.49\times10^6\). This makes time diversity a material part of stable
intervention recovery rather than a cosmetic sampling choice.

For candidate times \(t_i\), define the per-time information matrices

\[
 A_i=R_{B\leftarrow A}(t_i)^{\mathsf T}
     R_{B\leftarrow A}(t_i).
\]

The positive E-design problem is

\[
 \begin{aligned}
 \text{maximize }&z\\
 \text{subject to }&\sum_iw_iA_i\succeq zI,\\
 &w_i\geq0,\qquad\sum_iw_i=1.
 \end{aligned}
\]

It maximizes Fisher information in the weakest intervention direction under a
unit total observation budget.

### Proposition 9.1 — finite primal/dual bracket

Let \(w\) be any feasible positive design. If \(Z\succeq0\),
\(\operatorname{tr}Z=1\), and

\[
 \operatorname{tr}(ZA_i)\leq\mu
\]

for every candidate \(i\), then

\[
 \lambda_{\min}\!\left(\sum_iw_iA_i\right)\leq\mu.
\]

Thus a computed primal floor and any audited dual pair \((Z,\mu)\) bracket the
finite-grid optimum.

#### Proof

For \(G=\sum_iw_iA_i\),

\[
 \lambda_{\min}(G)
 \leq\operatorname{tr}(ZG)
 =\sum_iw_i\operatorname{tr}(ZA_i)
 \leq\mu.
\]

The first inequality follows by diagonalizing \(G\): a positive trace-one \(Z\)
forms a convex average of its Rayleigh values. \(\square\)

The reference computation uses 120 geometric candidate times from \(0.001\) to
\(10\). Floating sequential quadratic optimization finds a minimum eigenvalue

\[
 z_{\rm primal}=4.98293778\times10^{-9}.
\]

A positive trace-one dual witness constructed in the computed two-dimensional
minimum eigenspace gives

\[
 z_\star\leq\mu_{\rm dual}=4.98294116\times10^{-9}.
\]

The relative floating primal/dual gap is \(6.78\times10^{-7}\). Rounding the
primal weights to denominator 4096 produces the positive schedule

| time | numerator |
|---:|---:|
| 0.1213482768 | 963 |
| 0.3586095482 | 71 |
| 0.3874675120 | 669 |
| 0.8401749869 | 1289 |
| 3.3838551534 | 294 |
| 3.6561601441 | 810 |

The numerators sum exactly to 4096. The dyadic design has weakest information

\[
 z_{\rm dyadic}=4.98241290\times10^{-9},
\]

which is \(0.999894\) of the floating dual upper bound. It improves the uniform
120-time grid by a factor \(2.4310\). The best single candidate time is
\(0.840175\), but its weakest information is only
\(3.39097\times10^{-15}\); the dyadic schedule improves this by a factor
\(1.4693\times10^6\). Its Gram condition number is
\(1.6485\times10^6\), about half the original 20-time design's value, though
still large.

This is the first point in Stage IV where the positive multiscale logic of
Arithmetic Sensing becomes necessary: different causal-jet directions emerge
at different time orders. The finite-grid primal and dual are fully audited in
floating point, and the primal weights are dyadic. A rigorous outward-rounded
PSD certificate remains a separate task.

## 10. What changed from the Stage IV plan

All six planned tasks were completed:

1. a directed intervention-response kernel was defined;
2. symmetric diffusion geometry was separated from directed influence;
3. a finite propagation envelope was proved for the Markov control;
4. passive and interventional blind directions were compared;
5. compressed local protocols were audited on the response quotient; and
6. only positivity-preserving Markov generators were used for probability
   propagation.

The adjacent Stage III multiscale certificate was not needed for the core Stage
IV theorems. No exact directionality or propagation statement depends on the
older optimized four-scale design.

Two unexpected results nevertheless justified going beyond the initial plan:

1. the finite causal-jet theorem turns numerical directionality into an
   all-time finite-dimensional statement and gives a natural response quotient;
2. the large response condition number makes a new positive multiscale schedule
   worthwhile, so a dyadic primal and finite floating dual audit were completed.

The stationary-background theorem was also added to prevent overreading the
one-way example as a response that must be active in every context.

## 11. Falsification ledger

The work was organized so that each attractive interpretation has a nearby
failure mode.

| possible overclaim | control or boundary |
|---|---|
| any non-product geometry is interaction | exact independent Kronecker-sum control |
| any interaction is directional | reciprocal diagonal-edge Markov control |
| symmetric generator means reciprocal macro-causality | exact one-way rate-modulation counterexample |
| sampled near-zero means identically zero | complete order-\(N-1\) causal jet plus structural proof |
| full passive tangent rank gives stable reconstruction | tangent condition number \(3.62\times10^7\) |
| passive rank determines causal direction | tangent rank 35 coexists with exact reverse response 0 |
| a structural arrow must respond in every endpoint protocol | exact endpoint silence for a stationary tensor background, but path activity remains visible |
| a local Markov graph has strict finite speed | all 36 states positive for every tested \(t>0\) |
| no hard cone means no locality | uniformization Poisson tail theorem |
| one successful compressed sensor proves invariance | 32-seed rank and dilation distribution |
| a floating design is a global exact optimum | explicit finite-grid and non-interval scope |

## 12. Limitations

The results are exact within a small model class, and that boundary matters.

- The state space is finite and the dynamics are linear.
- Interventions are tangent perturbations around declared backgrounds.
- Direction is relative to a chosen tensor-factor decomposition.
- The one-way example encodes rate modulation by construction; it does not infer
  a hidden causal mechanism from data.
- The propagation theorem is a graph-distance upper bound, not a Lorentzian
  metric or a Lieb--Robinson theorem.
- The random-protocol experiment is not interval certified and has only 32
  seeds.
- The multiscale response design is optimized only over 120 declared times. Its
  separate Arb certificate is outward-rounded on that grid, not over continuum
  time.
- Floating-point ranks use explicit absolute and relative thresholds. Exact
  zero claims are supported separately by algebraic identities.
- No claim is made about quantum fields, spacetime, fundamental information,
  or a physical law.
- Publication novelty has not been established by a systematic literature
  review or peer review.

## 13. Reproduction

Run the focused Stage IV tests:

```sh
python -m unittest -v test_operational_information_geometry_iv.py
```

Recompute the full reference report:

```sh
python operational_information_geometry_iv.py
```

Change the two coupling controls or the protocol ensemble:

```sh
python operational_information_geometry_iv.py \
  --reciprocal-strength 0.4 \
  --directed-strength 0.8 \
  --protocol-seeds 64
```

Run the full repository suite:

```sh
python -m unittest discover -v
```

The implementation is in `operational_information_geometry_iv.py`; independent
checks are in `test_operational_information_geometry_iv.py`.

## 14. Source and novelty boundary

The state-space input/output formalism and finite observability ideas belong to
classical linear systems theory; see R. E. Kalman, “Contributions to the Theory
of Optimal Control,” *Boletín de la Sociedad Matemática Mexicana* 5 (1960),
102--119,
<https://boletin.math.org.mx/pdf/2/5/BSMM%282%29.5.102-119.pdf>.

The Poisson expansion is the classical uniformization construction introduced
by A. Jensen, “Markoff Chains as an Aid in the Study of Markoff Processes,”
*Scandinavian Actuarial Journal* 1953(sup1), 87--91,
<https://doi.org/10.1080/03461238.1953.10419459>.

Autonomous environments that modulate another chain's rates and the associated
marginal/lumpability questions are standard Markov-process mechanisms; see
A. Economou, “Generalized product-form stationary distributions for Markov
chains in random environments with queueing applications,” *Advances in
Applied Probability* 37 (2005), 185--211,
<https://doi.org/10.1239/aap/1113402405>, and F. Ball and G. F. Yeo,
“Lumpability and marginalisability for continuous-time Markov chains,”
*Journal of Applied Probability* 30 (1993), 518--528,
<https://doi.org/10.2307/3214762>.

Within this research program, the new contribution is the explicit assembly and
audit of:

- localized simplex-tangent intervention geometries;
- the symmetric rate-modulated product generator as an exact macro-directional
  control;
- the finite causal-jet quotient as an all-time certificate;
- the side-by-side separation of passive rank, directed response, and
  uniformization propagation; and
- the refreshed compressed-sensor experiment and positive multiscale design on
  the response quotient.

These constructions may overlap existing work in lumpability, controlled Markov
processes, functional observability, compartmental systems, or causal dynamical
systems. No claim of literature priority is made without a dedicated search and
expert review.

## 15. Next research order

### Immediate target — Stage V: continuum and scale flow

The natural next step is to vary the factor side length and lattice spacing
while tracking three distinct objects:

1. diffusion geometry of the microscopic generator;
2. directed response geometry on intervention quotients; and
3. leakage-radius flow from the Poisson causal envelope.

The central question is whether any normalized response spectrum, causal order,
or effective propagation profile stabilizes as boundaries recede.

### Completed adjacent target — interval-certified causal-jet design

The floating design has now been upgraded: `oig_iv_certificate.py` uses a
rational tangent metric, exact dyadic primal, rational PSD dual, and 192-bit Arb
balls to prove
\(4.982412\times10^{-9}\le z_*\le4.982942\times10^{-9}\) on both the canonical
and frozen binary64 120-time grids. The next statistical layer should derive
noise-aware lower bounds under an explicit minimum-effect assumption; no finite
noisy protocol can uniformly separate exact zero from arbitrarily weak nonzero
channels.

### Further target — genuinely nonlinear interventions

For fixed linear \(L\), linear \(M\), and initial perturbation \(p_0+Ju\), the
response \(Me^{-tL}(p_0+Ju)\) is exactly affine in \(u\); every second amplitude
derivative is zero. A nontrivial second-order target must therefore declare a
control-dependent generator \(L(u)\), nonlinear dynamics or measurement, or a
finite replacement intervention. Coordinate curvature from merely
reparameterizing the simplex would not be dynamical nonlinearity.
