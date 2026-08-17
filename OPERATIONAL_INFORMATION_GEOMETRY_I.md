# Operational Information Geometry I

## Geometry from distinguishable histories in a finite factorization universe

- **Research lead, mathematics, software, and manuscript:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Date:** 13 August 2026
- **Status:** first theorem-and-falsification layer; not peer reviewed

## Abstract

This paper replaces the slogan “reality is information” with a finite and
falsifiable question: when do restricted observations of a dynamics force a
geometry on otherwise unlabelled states?

For a finite linear dynamics and a declared observation protocol, stack the
observable histories into a linear map \(\mathcal O\). The formula

\[
 d_{\mathcal O}(x,y)=\|\mathcal O(x-y)\|_2
\]

is a pseudometric on latent states and an exact metric on the quotient by
operational indistinguishability. Its Gram matrix is positive semidefinite.
Under isotropic Gaussian sensor noise, the same distance has a direct testing
meaning: the exact equal-prior error for distinguishing two pure states is
\(\Phi(-d_{\mathcal O}/(2\nu))\). Thus topology, metric, dynamics, and
distinguishability are tied to one specified experiment, without presupposing
physical space.

We test this construction on 216 smooth integers
\(2^a3^b5^c\), \(0\leq a,b,c<6\). Allowed transitions multiply or divide by
one prime; the observer receives 32 signed coarse channels at 14 diffusion
times but receives no exponent coordinates. The resulting compressed
operational distances correlate \(0.933\) with the complete-observation
geometry, classify the actual transition edges with locality AUC \(0.9943\),
and recover a finite-scale spectral dimension \(2.916\) with exactly three
stable observable slow modes. An exact product-spectrum theorem explains the
three modes.

The principal control is deliberately severe: 32 connected random graphs
preserve every vertex degree, all integer labels, the number of edges, sensors,
times, and noise protocol, while rewiring only the transition relation.
Operational locality remains high in the representative control (AUC
\(0.9788\)). It is therefore a generic consequence of observing diffusion, not
evidence of arithmetic geometry. In contrast, the three-dimensional plateau,
three slow directions, and most alignment with exponent distance disappear
under rewiring. Finally, the history map is numerically full rank yet has
condition number \(4.10\times10^9\): pure-state recognition is robust at the
declared noise, but arbitrary-mixture reconstruction is not. These positive
and negative results define a disciplined first model of operational
“physicalization”: stable, observable structure induces geometry, while
unobservable distinctions are quotiented away.

## 1. The question made operational

The motivating intuition is that stable relations may be more primitive than
a pre-existing space in which objects sit. The useful mathematical version is
not “everything is information.” It is:

> Given latent alternatives, allowed dynamics, restricted interventions or
> observations, and noise, which distinctions persist, which distinctions can
> actually be made, and what geometry is forced by those answers?

This formulation refuses to decide in advance whether information or physical
reality is primary. Both are represented by the same operational structure.
An observer can call two states different only through a protocol that can
distinguish them. A feature can behave as an effective physical degree of
freedom only if the dynamics preserves it long enough and the observation
channels couple to it strongly enough.

The word **operational** is essential. A different dynamics, sensor family,
time window, or noise model can induce a different geometry. The construction
does not claim an observer-independent metric without additional invariance or
universality theorems.

## 2. Finite observable-history geometry

Let the latent real vector space be \(X=\mathbb R^n\). Pure alternatives are
the basis vectors \(e_1,\ldots,e_n\); probability mixtures form the simplex in
\(X\). Let \(L\) be a symmetric positive semidefinite generator and

\[
 P_t=e^{-tL}
\]

its diffusion semigroup. Let \(C\in\mathbb R^{q\times n}\) be a fixed family
of measurement channels, and let \(0\leq t_1<\cdots<t_m\) be the observation
times. Define the stacked observable-history operator

\[
 \mathcal O=
 \begin{bmatrix}
 CP_{t_1}\\
 CP_{t_2}\\
 \vdots\\
 CP_{t_m}
 \end{bmatrix}
 \in\mathbb R^{qm\times n}.
\]

The data signature of \(x\) is \(\mathcal Ox\). We define

\[
 G=\mathcal O^{\mathsf T}\mathcal O,
 \qquad
 d_{\mathcal O}(x,y)^2
 =(x-y)^{\mathsf T}G(x-y).
\]

### Theorem 2.1 — operational quotient metric

For any linear history operator \(\mathcal O:X\to\mathbb R^M\):

1. \(G=\mathcal O^{\mathsf T}\mathcal O\) is positive semidefinite;
2. \(d_{\mathcal O}(x,y)=\|\mathcal O(x-y)\|_2\) is a pseudometric on \(X\);
3. \(x\sim y\) if and only if \(x-y\in\ker\mathcal O\) is an equivalence
   relation; and
4. \(d_{\mathcal O}\) descends to a genuine metric on
   \(X/\ker\mathcal O\).

#### Proof

For every \(v\),

\[
 v^{\mathsf T}Gv
 =v^{\mathsf T}\mathcal O^{\mathsf T}\mathcal Ov
 =\|\mathcal Ov\|_2^2\geq0.
\]

Nonnegativity and symmetry of \(d_{\mathcal O}\) follow from the Euclidean
norm. Its triangle inequality is

\[
 \|\mathcal O(x-z)\|_2
 \leq \|\mathcal O(x-y)\|_2+\|\mathcal O(y-z)\|_2.
\]

The only metric axiom that can fail is separation:
\(d_{\mathcal O}(x,y)=0\) exactly when \(x-y\in\ker\mathcal O\). Equality
modulo this kernel is an equivalence relation, the distance is independent of
the chosen coset representatives, and distinct cosets have positive distance.
\(\square\)

This elementary statement is the logical core. It does not pretend that
unobserved distinctions secretly have zero ontological distance. It says that
the declared experiment contains no fact that separates them.

### Corollary 2.2 — pure-state geometry

Let \(o_i=\mathcal Oe_i\), the \(i\)-th column of \(\mathcal O\). Then

\[
 d_{\mathcal O}(e_i,e_j)=\|o_i-o_j\|_2.
\]

Consequently the finite pure-state quotient embeds isometrically in ordinary
Euclidean data space. Its operational topology is the topology generated by
balls in observable-history distance.

### Theorem 2.3 — exact Gaussian discrimination meaning

Suppose one of two pure states \(e_i,e_j\) is chosen with equal prior
probability and the complete observed history is

\[
 Z=\mathcal Oe_k+\eta,
 \qquad \eta\sim N(0,\nu^2I_M).
\]

The nearest-signature rule is Bayes optimal and its exact error probability is

\[
 P_{\mathrm{err}}(i,j)
 =\Phi\!\left(-\frac{d_{\mathcal O}(e_i,e_j)}{2\nu}\right),
\]

where \(\Phi\) is the standard normal cumulative distribution function.

#### Proof

Let \(\delta=o_i-o_j\). The likelihood-ratio boundary is the hyperplane
perpendicular to \(\delta\) through \((o_i+o_j)/2\). Under either hypothesis,
the signed projection onto \(\delta/\|\delta\|_2\) has variance \(\nu^2\) and
its mean lies \(\|\delta\|_2/2\) from that boundary. The error is therefore
\(\Phi(-\|\delta\|_2/(2\nu))\). Apply Corollary 2.2. \(\square\)

For nearest-signature recognition among all \(n\) pure states, a direct union
bound for state \(i\) is

\[
 P_i(\text{error})
 \leq \sum_{j\ne i}
 \Phi\!\left(-\frac{d_{\mathcal O}(e_i,e_j)}{2\nu}\right).
\]

### Definition 2.4 — operational physicalization

For a nondegenerate eigenmode \(v_k\) of \(L\), with
\(Lv_k=\lambda_kv_k\), persistence is measured by
\(\log2/\lambda_k\) and observation energy by \(\|\mathcal Ov_k\|_2^2\).
For a degenerate eigenspace \(E_\lambda\), however, individual numerical
eigenvectors are not canonical. Let \(V_\lambda\) be any orthonormal basis of
that eigenspace. The **physicalized dimension relative to the protocol** at
thresholds \((\tau,E_0)\) is the number of squared singular values of
\(\mathcal O V_\lambda\) at least \(E_0\), provided

\[
 \frac{\log2}{\lambda}\geq\tau.
\]

The singular values are unchanged when \(V_\lambda\) is rotated, so this count
is basis invariant. Stage 2 identified and corrected the original
eigenvector-by-eigenvector implementation of this definition. The reference
random protocol still has physicalized dimension three; the correction changes
only the reported energy coordinates, not the Stage 1 count or conclusions.

Persistence and observation energy are both relative to the actual protocol.
This is a deliberately modest use of “physicalized.” It identifies effective
degrees of freedom inside a model. It is not a claim that the model creates
matter, spacetime, or quantum fields.

## 3. The factorization toy universe

Fix distinct primes \(p_1,\ldots,p_r\) and a side length \(s\geq2\). The pure
states are

\[
 \mathcal S_{r,s}
 =\left\{\prod_{j=1}^r p_j^{a_j}:0\leq a_j<s\right\}.
\]

Unique factorization makes the exponent vector
\(a=(a_1,\ldots,a_r)\) unique. Two states are joined by an allowed transition
when their exponent vectors differ by \(1\) in exactly one coordinate. In
arithmetic language, one transition multiplies or divides by one generating
prime while staying inside the cutoff.

For the reference experiment,

\[
 (p_1,p_2,p_3)=(2,3,5),\qquad r=3,\qquad s=6.
\]

There are \(6^3=216\) states and

\[
 r(s-1)s^{r-1}=3\cdot5\cdot6^2=540
\]

undirected transition edges.

The observer is not supplied the exponents, Manhattan distance, or the values
of the integer labels. The measurement matrix consists of \(q=32\) fixed
Rademacher rows, with entries \(\pm1/\sqrt q\), generated from seed 20260813.
Histories are observed at 14 logarithmically spaced times from 1 to 8.

### Theorem 3.1 — exact product spectrum

The transition graph of \(\mathcal S_{r,s}\) is the Cartesian product

\[
 P_s\square\cdots\square P_s=P_s^{\square r},
\]

and its graph Laplacian is the Kronecker sum

\[
 L=\sum_{j=1}^{r}
 I_s^{\otimes(j-1)}\otimes L_{P_s}\otimes
 I_s^{\otimes(r-j)}.
\]

Its eigenvalues, indexed by \(0\leq k_j<s\), are

\[
 \lambda_{k_1,\ldots,k_r}
 =\sum_{j=1}^{r}\left(2-2\cos\frac{\pi k_j}{s}\right).
\]

In particular, its smallest nonzero eigenvalue is

\[
 \lambda_*=2-2\cos(\pi/s)
\]

with multiplicity exactly \(r\).

#### Proof

Changing one prime exponent by one is exactly adjacency in one copy of the
path \(P_s\), with all other coordinates fixed. This proves the Cartesian
product and Kronecker-sum statements. The path Laplacian has eigenvalues
\(2-2\cos(\pi k/s)\), \(0\leq k<s\). Tensor products of path eigenvectors
diagonalize the Kronecker sum, and eigenvalues add. The least positive sum has
one coordinate equal to \(1\) and all others zero, giving \(r\) independent
modes. \(\square\)

For \(r=3,s=6\),

\[
 \lambda_*=2-2\cos(\pi/6)=0.2679491924\ldots
\]

and the three associated half-lives are
\(\log2/\lambda_*=2.58686\ldots\). The threefold degeneracy is not discovered
by numerical fitting; it is forced exactly by independent prime directions.

## 4. Diagnostics and falsification design

### 4.1 Complete and compressed operational geometries

The **complete-observation** reference uses \(C=I_{216}\). The compressed
observer uses the 32 signed channels. We compare all \({216\choose2}=23{,}220\)
pairwise distances by Spearman correlation. The complete geometry is not the
ground truth of the universe; it is the richest geometry available from the
same dynamics and time window.

### 4.2 Locality AUC

For each actual transition edge and each nonedge, compare operational
distance. The locality AUC is

\[
 \Pr\{d_{\mathcal O}(\text{random edge})
       <d_{\mathcal O}(\text{random nonedge})\},
\]

with ties worth one half. It tests whether adjacency can be recovered from
histories, but does not by itself diagnose arithmetic structure.

### 4.3 Finite-scale spectral dimension

With Laplacian eigenvalues \(\lambda_j\), remove the stationary mode from the
normalized heat trace:

\[
 H(t)=\frac1n\sum_{j=0}^{n-1}e^{-t\lambda_j}-\frac1n,
 \qquad
 d_s(t)=-2\frac{d\log H(t)}{d\log t}.
\]

The reported dimension is the median of \(d_s(t)\) on the preregistered
finite-scale window \(1\leq t\leq3\); plateau roughness is its median absolute
deviation on that window. This is an effective finite-scale diagnostic, not a
Hausdorff dimension and not an asymptotic dimension of a finite set.

### 4.4 Propagation

Start diffusion at the interior exponent state \((2,2,2)\). At each time,
measure the root-mean-square radius using the already derived operational
distance. Fit \(R(t)\propto t^\alpha\) on \(0.03\leq t\leq0.2\). Ordinary
diffusion predicts \(\alpha=1/2\).

### 4.5 Degree-preserving controls

Each control performs 20 successful double-edge swaps per original edge,
rejects loops and repeated edges, and retains only connected outcomes. It
preserves:

- the 216 vertices and their integer labels;
- every individual vertex degree;
- all 540 edges in total;
- the same 32 measurement channels and 14 times;
- the noise model and all diagnostic code.

Only the transition relation is randomized. Coordinates are retained solely
for the held-out audit against the original exponent distance; they are never
given to the history construction.

The controls make the following distinction falsifiable:

- if locality also appears after rewiring, locality is a generic signature of
  observing a diffusion on a graph;
- if the three-dimensional plateau and three slow modes survive rewiring, they
  cannot be attributed specifically to the product factorization relation;
- if hidden exponent alignment remains unchanged, the measurement pipeline is
  leaking coordinate labels or the control is ineffective.

## 5. Results

All numbers below were recomputed by the committed program in binary64
arithmetic. The exact graph counts and product-spectrum theorem do not depend
on floating-point computation.

### 5.1 Reference universe and representative control

| Diagnostic | factorization universe | degree-preserving control, seed 1 |
|---|---:|---:|
| compressed vs complete distance Spearman | 0.93294 | 0.84874 |
| compressed vs own graph distance Spearman | 0.82242 | 0.47478 |
| compressed vs original exponent distance Spearman | 0.82242 | 0.24891 |
| edge locality AUC | 0.99428 | 0.97881 |
| spectral dimension, \(t\in[1,3]\) | 2.91632 | 5.85587 |
| plateau median absolute deviation | 0.03442 | 1.02098 |
| spectral gap | 0.26795 | 1.07836 |
| physicalized modes at \((\tau,E_0)=(2,0.1)\) | 3 | 0 |
| minimum pure-state signature distance | 0.06844 | 0.04914 |
| history-map condition number | \(4.097\times10^9\) | \(3.428\times10^9\) |

The equality between graph and exponent correlations in the factorization
universe is expected: graph distance on the Cartesian product is precisely
Manhattan distance in exponent coordinates. Their separation in the control
is an important check that the rewiring actually breaks that structure.

### 5.2 Control ensemble

Across 32 independently seeded connected degree-preserving controls:

| Diagnostic | mean | standard deviation | minimum | median | maximum |
|---|---:|---:|---:|---:|---:|
| spectral dimension | 5.77711 | 0.08420 | 5.51834 | 5.79367 | 5.91433 |
| plateau deviation | 0.98807 | 0.03801 | 0.88844 | 0.99431 | 1.05482 |
| spectral gap | 1.00405 | 0.05143 | 0.89549 | 1.00958 | 1.10926 |
| nonconstant modes with \(\lambda\leq0.5\) | 0 | 0 | 0 | 0 | 0 |

The factorization value \(d_s=2.91632\) lies far outside this computed
ensemble, and its plateau is about 29 times flatter than the control mean.
None of the 32 controls has even one nonconstant eigenvalue below 0.5, whereas
the product graph has exactly three. These are finite computational contrasts,
not population-level p-values.

### 5.3 The three stable directions

At the declared thresholds, the factorization universe has exactly three
stable observable modes:

| invariant energy direction | eigenvalue | half-life | observation energy |
|---:|---:|---:|---:|
| 1 | 0.26794919 | 2.58686 | 3.75161 |
| 2 | 0.26794919 | 2.58686 | 3.37553 |
| 3 | 0.26794919 | 2.58686 | 2.73224 |

The equal eigenvalues and their multiplicity are exact consequences of
Theorem 3.1. The three energies are the squared singular values of the history
map restricted to the slow eigenspace. They are invariant under rotations of
the numerical eigenbasis and are unequal because the random measurement
channels couple anisotropically to that eigenspace.

### 5.4 Measurement-budget sweep

For each channel count, 16 new Rademacher measurement matrices were compared
with the complete-observation geometry:

| channels | mean distance Spearman | standard deviation |
|---:|---:|---:|
| 4 | 0.62180 | 0.05508 |
| 8 | 0.75663 | 0.04293 |
| 16 | 0.87048 | 0.02857 |
| 32 | 0.91998 | 0.01278 |
| 64 | 0.95478 | 0.00846 |

The improvement is monotone in this tested sweep. It is an empirical
concentration pattern, not yet a finite-sample theorem for random channels.

### 5.5 Noise and identifiability

For the reference 32-channel seed, the minimum distance between two pure-state
signatures is

\[
 \delta_{\min}=0.06844465.
\]

Declare \(\nu=\delta_{\min}/8=0.00855558\). The worst computed nearest-
signature union bound is

\[
 3.1925\times10^{-5}.
\]

Pure-state recognition is therefore certified as robust under this exact
Gaussian model and declared noise level.

The same statement emphatically does not extend to arbitrary mixtures. The
stacked \(448\times216\) history matrix is numerically full rank, but its
smallest singular value is \(7.47\times10^{-10}\) and its condition number is
\(4.10\times10^9\). Long-time diffusion damps high-frequency modes, so some
mixture directions are nearly invisible. A tiny perturbation can be amplified
by billions in unconstrained inversion.

This is not an implementation defect to be tuned away after seeing the data.
It is the first major boundary of the theory:

> Separated prototypes can be classified reliably even when stable recovery
> of an arbitrary superposition or mixture is impossible.

### 5.6 Propagation

The fitted early operational propagation exponent is

\[
 \alpha=0.49434,
\]

close to the diffusive value \(1/2\). This confirms internal consistency: the
geometry derived from diffusion makes early diffusion look diffusive. Because
the same qualitative behavior is expected on many graphs, it is not evidence
for arithmetic specificity or physical spacetime.

## 6. What survived falsification

Three claims survive, at three different logical strengths.

### Proved for every finite linear protocol

1. Observable histories induce a positive semidefinite Gram geometry.
2. Operational indistinguishability is exactly the kernel quotient.
3. Under the stated Gaussian noise model, operational distance is exact binary
   testing distance.

### Proved for every finite prime box

1. Single-prime transitions form a Cartesian product of paths.
2. The spectrum is a sum of path spectra.
3. The slowest nonconstant eigenvalue has one independent direction per prime.

### Computed for the declared reference experiment

1. Thirty-two coordinate-free channels retain most of the complete geometry.
2. The factorization graph exhibits a flat effective dimension near three.
3. Matched degree-preserving rewiring destroys the three slow modes and most
   exponent alignment.
4. Operational edge locality remains high after rewiring and is therefore
   generic, not arithmetic-specific.
5. Pure alternatives are noise-robust at the declared level, while arbitrary
   mixture inversion is extremely ill-conditioned.

The negative control result is as important as the positive one. Without it,
high edge locality could easily be misreported as discovery of a special
number geometry. The experiment instead says something more precise: dynamics
generically induces local operational geometry; factorization selects a
specific low-dimensional product geometry within that broad mechanism.

## 7. Relation to established work and novelty boundary

The framework uses classical ideas:

- Kalman's observability formalized when internal states can be determined
  from outputs of a dynamical system [Kalman 1960](https://boletin.math.org.mx/pdf/2/5/BSMM%282%29.5.102-119.pdf).
- Diffusion geometry and diffusion distance extract multiscale geometry from
  transition dynamics [Coifman and Lafon 2006](https://doi.org/10.1016/j.acha.2006.04.006).
- Statistical distinguishability as geometry has a long history; a central
  quantum formulation is [Braunstein and Caves 1994](https://doi.org/10.1103/PhysRevLett.72.3439).
- Cartesian-product graph spectra and path Laplacians are standard spectral
  graph theory.

The present contribution is a research synthesis and explicit falsification
laboratory:

1. place a finite observable-history quotient metric, an exact Gaussian
   discrimination formula, and a persistence/observability criterion in one
   operational model;
2. instantiate the model on prime-factor transitions without giving the
   observer factorization coordinates;
3. separate generic dynamics-induced locality from product-specific arithmetic
   structure using connected degree-preserving rewiring;
4. record the sharp empirical division between robust pure-state recognition
   and ill-conditioned mixture reconstruction.

The quotient and product-spectrum theorems are elementary once formulated.
No claim of literature priority is made for those ingredients or for the broad
idea of emergent geometry from dynamics. Independent specialist review and a
deeper literature audit are required before making any novelty claim about the
combined construction.

## 8. Scope and nonclaims

This paper does **not** establish:

- that physical reality is made of information;
- that actual spacetime is a factorization graph;
- a derivation of quantum mechanics, particles, energy, or matter;
- observer-independent geometry from one chosen sensor protocol;
- a continuum or Lorentzian limit;
- a relationship to zeta zeros or the Riemann hypothesis;
- robust recovery of arbitrary mixtures;
- universality beyond the finite models explicitly proved or tested.

The finite toy universe is valuable precisely because every dependency can be
declared, tested, and broken by controls. Physical interpretation should wait
for protocol-invariance theorems, causal/interventional structure, composition
laws, and continuum-limit evidence.

## 9. Reproduction

Install NumPy and SciPy, then run the focused tests:

```sh
python -m unittest -v test_operational_information_geometry.py
```

Reproduce the 32-control report:

```sh
python operational_information_geometry.py --controls 32
```

Validate the entire research repository:

```sh
python -m unittest discover -v
```

The program fixes all reference seeds and prints the complete parameter set,
control summaries, margins, condition number, channel sweep, and falsification
readout as JSON.

## 10. Next research order

### Stage 2 — protocol invariance

Sample broad families of sensors and time schedules. Seek bi-Lipschitz bounds
showing that different sufficiently rich protocols induce approximately the
same quotient geometry. A geometry that exists only for one measurement seed
is not a convincing candidate for an observer-independent structure.

Primary tests:

1. derive random-projection guarantees for the finite pure-state signature
   cloud;
2. separate the channel count needed for pure-state distances from that needed
   for mixture conditioning;
3. adversarially optimize sensors that erase one prime direction;
4. characterize the intersection of kernels across a protocol class.

### Stage 3 — compositional geometry

Compare independent systems, weakly coupled systems, and interacting systems.
Test when history Gramians factor as tensor products or Kronecker sums and how
an interaction term creates curvature-like deviations from product geometry.

### Stage 4 — intervention and causal cones

Observations alone are correlational. Add localized interventions and define
directed influence by response histories. Test whether finite propagation
rules induce operational causal cones distinct from the symmetric diffusion
metric.

### Stage 5 — continuum and scale flow

Increase the prime-box side length, track spectral-dimension plateaus, and
renormalize time and distance. Determine which diagnostics converge, which are
finite-boundary artifacts, and whether product dimension remains protocol
stable.

### Adjacent target — stable mixture recovery

The \(4.10\times10^9\) condition number is a concrete obstruction, not an
afterthought. Test early-time sampling, derivative channels, sparse/nonnegative
priors, and designed interventions. The aim is not to force inversion to work,
but to identify the exact model classes for which it can be certified.

The next immediate target is Stage 2. It directly attacks the largest
conceptual weakness of Stage 1: dependence on the observer's chosen channels.
