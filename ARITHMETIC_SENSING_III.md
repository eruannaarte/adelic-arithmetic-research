# Arithmetic Sensing III

## Convex arithmetic window design and the unavoidable-alias theorem

**Status:** first optimized-quadrature theorem layer  
**Date:** 12 August 2026  
**Companions:** `ARITHMETIC_SENSING.md`, `ARITHMETIC_SENSING_II.md`

## Abstract

Arithmetic Sensing II proved a complete quadratic-field recovery certificate
using a Hann-weighted midpoint grid. This continuation asks whether the window
can be designed for the logarithmic integer frequencies themselves, instead of
borrowed unchanged from conventional signal processing.

The answer is yes, within a controlled finite-dimensional family. A positive
cosine-series window is chosen by a linear program whose constraints enforce:

1. nonnegative quadrature weights;
2. a cap on the largest sampling density;
3. a rigorous Gershgorin lower bound on the target Gram matrix;
4. minimax suppression of a divisor-weighted arithmetic boundary tail.

The finite optimization is globally solved within its declared family and
frequency truncation. Its output is then audited independently against the
exact Gram matrix and a million-term, alias-safe infinite-tail certificate.

At `N=50`, `sigma=2`, `T=1,000`, and `m=5,000`, an eight-harmonic positive
window gives

```text
minimum Gram eigenvalue:              0.98182107
complete quadratic-tail bound:        0.000232014
effective sample count:               2759.61
```

The complete-tail certificate is 117 times smaller than the previous Hann
bound `0.0271845` at the same resources. For `m=100,000` and sensor noise
`nu=0.01`, the optimized design gives a tail bound `0.0000478553` and a Gaussian
rounding-failure bound `6.09*10^-10`. A more noise-balanced density cap produces
a 54.8-fold tail improvement and a smaller Gaussian failure bound than Hann.

The same analysis proves a hard limitation: every weighting of a fixed uniform
midpoint grid has unit-magnitude responses at its exact grid aliases. Weight
optimization can suppress pre-alias leakage but cannot remove the aliases;
their location must be controlled jointly through `m/T`.

## 1. Positive trigonometric design family

Fix midpoint times

\[
t_j=\left(j+\frac12\right)\frac{T}{m},
\qquad 0\leq j<m.
\]

For a harmonic order `H<m`, define

\[
w_j(c)=\frac1m\left[
1+2\sum_{r=1}^Hc_r
\cos\left(\frac{2\pi r t_j}{T}\right)
\right].
\]

The midpoint cosine sums vanish for `1<=r<m`, so

\[
\sum_jw_j(c)=1.
\]

Requiring the bracketed density to be nonnegative makes these valid positive
quadrature weights.

Let `K_(U,m)` be the exact uniform midpoint kernel from Arithmetic Sensing II.
The window kernel is

\[
K_c(\omega)=K_{U,m}(\omega)
+\sum_{r=1}^Hc_r\left[
K_{U,m}(\omega+r\Omega)
+K_{U,m}(\omega-r\Omega)
\right],
\qquad \Omega=\frac{2\pi}{T}.
\]

Because the weights are symmetric about `T/2`, the centered response

\[
R_c(\omega)=e^{-iT\omega/2}K_c(\omega)
\]

is real and affine in `c`.

## 2. The alias limitation

### Theorem A — unavoidable midpoint-grid aliases

Let `w_j` be arbitrary complex weights satisfying `sum w_j=1`; positivity and
symmetry are not required. At every integer grid alias

\[
\omega_q=\frac{2\pi qm}{T},\qquad q\in\mathbb Z,
\]

the midpoint kernel satisfies

\[
K_w(\omega_q)=(-1)^q,
\qquad |K_w(\omega_q)|=1.
\]

**Proof.** At `t_j=(j+1/2)T/m`,

\[
e^{it_j\omega_q}
=e^{2\pi iq(j+1/2)}=(-1)^q
\]

for every `j`. The common phase factors out of the weighted sum.

**Consequence.** It is impossible to impose a strict alias-height constraint
on any weighting of a fixed uniform grid. One must instead:

- place the first alias sufficiently far into the decaying arithmetic tail by
  choosing `m/T`;
- suppress leakage before the alias through the weights;
- and retain an analytic bound on the remote tail at and beyond the aliases.

This explains why a pure window optimizer without an alias-location condition
would certify the wrong problem.

## 3. A finite linear program

Let the target frequencies be

\[
\Delta_{n\ell}=\log(n/\ell),
\qquad 1\leq n\ne\ell\leq N,
\]

and let the finite design tail be `N<k<=M_d`. Introduce nonnegative auxiliary
variables satisfying

\[
z_{n\ell}\geq |R_c(\Delta_{n\ell})|,
\]

\[
u_{nk}\geq
\left|R_c\!\left(\log\frac nk\right)\right|.
\]

Since every centered response is real and affine in `c`, each absolute value
is represented by two linear inequalities.

### Conditioning constraint

For a requested `gamma in (0,1)`, impose

\[
\sum_{\ell\ne n}z_{n\ell}\leq1-\gamma,
\qquad 1\leq n\leq N.
\]

The realized Hermitian Gram matrix has diagonal one, so Gershgorin gives

\[
\lambda_{\min}(G_c)\geq\gamma.
\]

### Positivity and noise-control constraints

On every midpoint, impose

\[
0\leq
1+2\sum_{r=1}^Hc_r\cos(2\pi r t_j/T)
\leq C.
\]

The upper density cap `C` prevents a leakage objective from concentrating all
weight on very few readings and silently destroying the sensor-noise
performance.

### Arithmetic-tail objective

Introduce `q` and impose for every target `n`

\[
n^\sigma\sum_{N<k\leq M_d}
\tau(k)k^{-\sigma}u_{nk}\leq q.
\]

Minimize `q`. This is a linear program.

### Theorem B — finite-family optimality

If the linear program is feasible, its optimum is the global minimum of the
declared finite divisor-weighted leakage proxy over all order-`H` cosine
windows satisfying the sampled positivity, density, and Gershgorin
constraints.

This theorem says exactly what the optimizer solves. It does **not** say that
the finite proxy equals the final coefficient error, that the cosine family is
globally optimal among all windows, or that tail norms above `M_d` are absent.
Those points are handled by independent certification.

## 4. Independent complete-tail certification

After solving the LP, the code discards its auxiliary variables and
recomputes:

1. the exact realized kernel `K_c`;
2. the exact target Gram matrix `G_c` and its eigenvalues;
3. every divisor-envelope correlation through a separate truncation `M`;
4. a rigorous analytic remainder beyond `M`;
5. the final coefficient bound `D_sigma |G_c^(-1)| b`;
6. the exact weighted Gaussian sensor-noise covariance.

For an order-`H` cosine window, define the safe pre-alias endpoint

\[
L_H=\frac{\pi m}{T}-H\Omega.
\]

Before `L_H`, every shifted uniform component remains within half its first
alias. For a target `n`, a finite tail cutoff `M`, and

\[
\omega_0=\log\frac{M+1}{n}>H\Omega,
\]

the unenumerated kernel is bounded by

\[
\frac{\pi}{T}
\left[
\frac1{\omega_0}
+\sum_{r=1}^H|c_r|
\left(
\frac1{\omega_0+r\Omega}
+\frac1{\omega_0-r\Omega}
\right)
\right].
\]

The mass beyond `n exp(L_H)` is controlled by the elementary divisor-tail
bound from Arithmetic Sensing II, even at every exact alias. Therefore the
certificate is valid for the complete infinite tail, not only the LP's finite
design frequencies.

## 5. Optimized design

Parameters used for discovery:

```text
N=50, sigma=2, T=1000, m=5000
H=8, design tail M_d=300
required Gershgorin lower bound gamma=0.98
maximum sampling density C=2.5
```

The optimized coefficients are

\[
\begin{aligned}
c_1={}&-0.6264119552599481,\\
c_2={}& 0.1159282765690596,\\
c_3={}& 0.0016529449271753,\\
c_4={}& 0.0095090113473966,\\
c_5={}&-0.0006326825432905,\\
c_6={}&-0.0001320496814286,\\
c_7={}& 0.0003945156501663,\\
c_8={}&-0.0003021786328145.
\end{aligned}
\]

Independent realized quantities are:

| quantity | value |
|---|---:|
| minimum weight | `2.35*10^-9` |
| maximum density `m max(w_j)` | 2.50000 |
| effective sample count | 2759.61 |
| exact minimum Gram eigenvalue | 0.981821 |
| Gershgorin lower bound | 0.980000 |
| first alias frequency | 31.4159 |
| first alias magnitude | 1.000000 |
| pre-alias endpoint | 15.6577 |

The million-term certificate cutoff requires only

\[
\log(1,000,001)=13.8155<15.6577,
\]

so every explicitly enumerated target-tail frequency is inside the safe
pre-alias region for `n>=1`. The remainder theorem then controls the remote
aliases.

## 6. Falsification and tradeoff sweep

An audit of the first LP formulation found an unnecessary hidden coefficient
box `|c_r|<=1/2`. Because its solution touched that boundary, the box was
removed and the leading designs were recomputed. This matters: it prevents a
claim of optimality over a family narrower than the one stated in the theorem.

The density cap gives a genuine leakage/noise tradeoff. Every optimized result
below uses `H=8`, `M_d=300`, and `gamma=0.98`, then undergoes the independent
million-term complete-tail audit:

| design | max density | exact `lambda_min` | effective samples | complete-tail bound | improvement over Hann |
|---|---:|---:|---:|---:|---:|
| Hann | 2.000 | 0.984390 | 3333.33 | 0.0271845 | 1.0 |
| balanced optimized | 2.000 | 0.982433 | 3253.48 | 0.000495807 | 54.83 |
| tail-optimized | 2.500 | 0.981821 | 2759.61 | 0.000232014 | 117.17 |

The improvement is not produced by violating the `0.98` conditioning demand
or by negative quadrature. The tail-optimized point does spend more effective
samples, exactly as its larger density cap permits. Reporting both Pareto
points makes that cost visible.

The improvement survived expansion from the finite LP objective through norm
300 to a million-term exact kernel sum plus the analytic infinite remainder.

## 7. Sensor noise and held-out arithmetic control

Reusing the `H=8` coefficients at increasing grid densities gives:

| samples | complete-tail bound | Gaussian failure bound at `nu=0.01` |
|---:|---:|---:|
| 5,000 | 0.000232014 | 1.0 |
| 20,000 | 0.0000478558 | 0.06778 |
| 50,000 | 0.0000478554 | `5.13*10^-5` |
| 100,000 | 0.0000478553 | `6.09*10^-10` |

The first row certifies noiseless tail recovery but the stated sensor noise is
too large for the Gaussian union bound at that sampling density. Tail leakage
and sensor noise are separate resources.

For a held-out `Q(sqrt(-5))` tail through norm 2,000, the 5,000-point optimized
design produced:

```text
maximum complex coefficient error: 0.000002105
maximum real coefficient error:    0.000001771
integer rounding:                   success
```

This empirical control is not used in the universal proof.

## 8. Interpretation

The optimized weights are not revealing a new axiom of numbers. They are a
measurement geometry adapted to a known arithmetic spectrum: the frequencies
are logarithmic ratios of integers, and the tail cost is weighted by the
quadratic divisor envelope. The interesting structural observation is that a
small number of positive trigonometric corrections can exploit the irregular
placement and weighting of those arithmetic frequencies much more effectively
than a generic window. The conditioning loss is small; the noise-averaging cost
is controlled explicitly by the density cap and displayed as a Pareto tradeoff.

There is a useful geometric separation:

- `T` sets the scale at which nearby log-norms can separate;
- the window shapes leakage inside the resolvable band;
- `m/T` places the sampling aliases;
- positivity makes the measurement a genuine weighted average;
- the Gram constraint preserves the target-coordinate geometry;
- the divisor envelope turns leakage into a field-uniform arithmetic risk.

## 9. What is proved, computed, and open

### Proved here

- exact alias magnitude one for every weighting of a midpoint grid;
- affine real centered responses for the cosine family;
- linear-program formulation and finite-family global optimality;
- Gershgorin conditioning from the LP constraints;
- alias-safe complete-tail certification for finite cosine-series windows;
- exact post-design sensor-noise covariance by the previous weighted theorem.

### Computed and independently checked

- global HiGHS solutions of the declared finite LP instances;
- positive realized weights and density caps;
- exact Gram spectra and effective sample counts;
- million-term complete-tail certificates with analytic remainders;
- density-cap Pareto and hidden-constraint falsification checks;
- held-out quadratic-field recovery.

### Not established

- global optimality among all positive weights or all observation schedules;
- stability of the displayed coefficients under every larger design cutoff;
- a closed-form extremal window;
- an all-alias band sum sharper than the current safe-region-plus-remote-tail
  decomposition;
- optimal joint scaling in `N`, `T`, and `m`;
- any result about zeta zeros or a physical law.

## 10. Next steps

1. Replace pointwise midpoint positivity by an exact nonnegative
   trigonometric-polynomial representation, so positivity holds continuously
   on `[0,T]`.
2. Sum the divisor tail alias band by alias band rather than paying the coarse
   remote tail after half the first alias.
3. Perform cutoff continuation in `M_d` and harmonic continuation in `H`, with
   warm starts and held-out frequency bands.
4. Optimize `m/T` jointly with the weights on a discrete certified grid of
   admissible ratios.
5. Extend `tau=d_2` to fixed-degree envelopes `d_d`.
6. Test enriched local measurement channels that can separate arithmetic
   objects lying in the same Dedekind-zeta equivalence class.

Arithmetic acceleration remains adjacent: after the analytic measurement
layer is certified, multiplicativity-aware integer decoding may lower the
required sensor precision further.

## 11. Reproduction

```text
python optimized_arithmetic_quadrature.py \
  --maximum-norm 50 \
  --sigma 2 \
  --observation-time 1000 \
  --sample-count 5000 \
  --harmonics 8 \
  --design-tail-cutoff 300 \
  --certificate-truncation 1000000 \
  --gershgorin-lower-bound 0.98 \
  --density-cap 2.5 \
  --noise-sigma 0.01

python -m unittest -v test_optimized_arithmetic_quadrature.py
python -m unittest discover -v
```

The full optimization is slower than evaluation of the published coefficient
vector. The local machine was sufficient; the Windows computer was not used.

## 12. Sources and novelty boundary

Window optimization has a deep classical history. Dolph's equal-ripple array
design optimizes a beamwidth/sidelobe tradeoff, while Slepian's discrete
prolate sequences optimize spectral energy concentration. Those objectives are
not the arithmetic divisor-weighted minimax objective used here:

- C. L. Dolph, [*A Current Distribution for Broadside Arrays Which Optimizes
  the Relationship between Beam Width and Side-Lobe Level*](https://doi.org/10.1109/JRPROC.1946.225956),
  Proceedings of the IRE 34 (1946), 335–348.
- D. Slepian, [*Prolate Spheroidal Wave Functions, Fourier Analysis, and
  Uncertainty—V: The Discrete Case*](https://doi.org/10.1002/j.1538-7305.1978.tb02104.x),
  Bell System Technical Journal 57 (1978), 1371–1430.

The exact arithmetic-frequency LP, its positive conditioning constraints, the
unavoidable-alias theorem in this sensing context, and the certified numerical
design are constructions of this research program. No literature-priority
claim is made without independent specialist review.
