# Adelic Arithmetic Research

This repository contains the manuscripts, executable laboratories, and tests
for two TGN research publications and one new operational-geometry research
program:

1. **The Geometry Arithmetic Remembers** — an eight-stage path from ordered
   multiplicative rigidity through adelic harmonic analysis, number-field
   calibration, spectral interpretation, and inverse reconstruction.
2. **Arithmetic Sensing** — stable recovery of finite Dirichlet coefficients
   from noisy global traces, deterministic tapered quadrature, complete
   analytic-tail certificates, and explicit nonidentifiability results.
3. **Operational Information Geometry** — a finite, falsifiable construction
   in which restricted histories induce a quotient geometry, tested on a
   factorization universe against degree-preserving random controls, followed
   by protocol-invariance, common-kernel, composition, interaction, and
   directed-intervention audits.

The fifth operational-geometry layer supplies the first controlled scale flow:
cell-centred continuum normalization, noncommuting spectral-dimension limits,
target-mode response reduction, smooth-versus-atomic regularity, a diffusive
signed-displacement leakage theorem, and exact protocol counterexamples. The
adjacent Stage IV E-design is also independently bracketed with rational
witnesses and 192-bit Arb arithmetic.

The active continuation also includes continuum-certified arithmetic window
design. Its eight-harmonic positive quadrature and alias-by-alias remainder
theorem improve the complete-tail bound at `N=50`, `sigma=2`, `T=1000`, and
`m=5000` from Hann's `0.0270048` to `0.0000456318` under a declared sampling-
density cap. The fixed-degree extension certifies all number fields through
degree four at the same parameters, while an enriched 2-adic probe separates
an explicit pair that complete Dedekind-zeta data cannot distinguish.

The work was developed by **Codex (OpenAI)** from an originating question and
research environment provided by TGN's human founder. It has not undergone
formal peer review. Classical ingredients and new constructions are identified
in the individual manuscripts; no literature-priority claim is made without
independent specialist review.

## Headline Arithmetic Sensing result

For every quadratic number field, the committed deterministic certificate at

```text
N = 50, sigma = 2, T = 1000, m = 5000
```

bounds the complete omitted-tail coefficient error by `0.0271845`, below the
`1/2` exact-integer rounding threshold. The Hann midpoint sampling design is
deterministic, so there is no random-design failure event.

At 100,000 readings and independent circular complex Gaussian sensor noise of
standard deviation `0.01`, the computed rounding-failure bound is
`8.84e-11` under the stated model.

These are finite recovery theorems in the half-plane `sigma>1`. They are not
results about zeta zeros or the Riemann hypothesis.

## Install

Python 3.11 or newer is recommended.

```sh
git clone https://github.com/eruannaarte/adelic-arithmetic-research.git
cd adelic-arithmetic-research
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Validate everything

```sh
python -m unittest discover -v
```

The test count is reported by the discovery command and grows with each
research layer.

## Reproduce Arithmetic Sensing I

The random-time first theorem layer separates Gram conditioning, measurement
noise, coherent population-tail bias, and finite-sample tail fluctuation:

```sh
python arithmetic_sensing.py \
  --maximum-norm 50 \
  --sample-count 200 \
  --trials 40
```

This full audit includes large random designs and can take longer than the unit
tests. See `ARITHMETIC_SENSING.md` for the theorem and interpretation.

## Reproduce Arithmetic Sensing II

Headline deterministic certificate with sensor noise:

```sh
python deterministic_arithmetic_sensing.py \
  --maximum-norm 50 \
  --sigma 2 \
  --observation-time 1000 \
  --sample-count 100000 \
  --truncation 1000000 \
  --window hann \
  --noise-sigma 0.01
```

Expected principal outputs, up to floating-point roundoff:

```text
lambda_min                         0.9843902957
worst_tail_coefficient_bound       0.0270066166
integer_tail_certificate           true
gaussian_rounding_failure_bound    8.84e-11
```

Run the explicit lower-bound and exact-collision report:

```sh
python arithmetic_indistinguishability.py
```

See `ARITHMETIC_SENSING_II.md` for the proof, alias treatment, limitations, and
source boundary.

## Reproduce Arithmetic Sensing III

Optimize a positive cosine-series window and independently certify it against
the complete tail:

```sh
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
```

See `ARITHMETIC_SENSING_III.md` for the linear program, the independent
certificate, and the theorem showing why no weighting of a fixed midpoint grid
can remove its exact aliases.

## Reproduce Arithmetic Sensing IV

Recompute the continuum factors, alias-band remainder, million-term quadratic
certificate, held-out bands, and enriched local probe:

```sh
python arithmetic_sensing_iv.py
```

The two larger studies are opt-in:

```sh
python arithmetic_sensing_iv.py --degree-study
python arithmetic_sensing_iv.py --ratio-study
```

See `ARITHMETIC_SENSING_IV.md` for the interval divisor theorem, continuation
tables, fixed-degree extension, and novelty boundary.

## Reproduce Operational Information Geometry

Run the focused theorem and falsification tests:

```sh
python -m unittest -v test_operational_information_geometry.py
```

Recompute the reference factorization universe and 32 connected
degree-preserving controls:

```sh
python operational_information_geometry.py --controls 32
```

See `OPERATIONAL_INFORMATION_GEOMETRY_I.md` for the operational quotient
metric, exact Gaussian testing interpretation, product-spectrum theorem,
matched controls, negative result for arbitrary-mixture recovery, and scope.

Run the Stage II protocol-invariance and mixture-recovery laboratory:

```sh
python -m unittest -v test_operational_information_geometry_ii.py
python operational_information_geometry_ii.py --protocols 16
```

See `OPERATIONAL_INFORMATION_GEOMETRY_II.md` for the finite random-projection
guarantee, schedule dependence, exact 125-dimensional common blind subspace,
explicit nonnegative mixture collision, and early refreshed-sensor remedy.

Run the Stage III composition and interaction laboratory:

```sh
python -m unittest -v test_operational_information_geometry_iii.py
python operational_information_geometry_iii.py --interaction-strength 0.4
```

See `OPERATIONAL_INFORMATION_GEOMETRY_III.md` for exact Cartesian and tensor
composition laws, the correlation kernel, signed mixed spectral witness,
Markov no-go boundary and control, and positive multiscale interaction design.

Run the Stage IV intervention and causal-envelope laboratory:

```sh
python -m unittest -v test_operational_information_geometry_iv.py
python operational_information_geometry_iv.py --protocol-seeds 32
```

See `OPERATIONAL_INFORMATION_GEOMETRY_IV.md` for the directed response kernel,
an exactly one-way subsystem response inside a symmetric Markov generator, the
finite causal-jet theorem, passive-versus-interventional ranks, the
uniformization Poisson propagation envelope, stationary-background control,
compressed-protocol audits, and positive multiscale response design.

Run the Stage V scale-flow and continuum laboratories:

```sh
python -m unittest -v test_operational_information_geometry_v.py
python operational_information_geometry_v.py
python -m unittest -v test_oig_v_scaling_continuum.py
python oig_v_scaling_continuum.py --maximum-side-length 64
```

See `OPERATIONAL_INFORMATION_GEOMETRY_V.md` for the exact path scaling,
mesoscopic dimension theorem, directed modal reduction, causal-jet regularity
and symmetry bounds, diffusive leakage envelope, expanding-domain control,
path-space sensor result, and next proof targets.

Run the outward-rounded finite-grid E-design certificate separately:

```sh
python -m pip install -r oig_iv_certificate_requirements.txt
python oig_iv_certificate.py --grid both
python -m unittest -v test_oig_iv_certificate.py
```

The certificate proves
`4.982412e-9 <= z_* <= 4.982942e-9` on both the exact canonical grid and the
frozen binary64 grid. It does not certify a continuum-time optimum.

## Manuscript map

### Publication 1 — The Geometry Arithmetic Remembers

- `THE_GEOMETRY_ARITHMETIC_REMEMBERS.md` — public synthesis
- `ABSTRACT_ORDERED_MONOID_RIGIDITY.md`
- `LOCAL_GLOBAL_ADELIC_CALIBRATION.md`
- `RATIONAL_ADELES_AND_POISSON.md`
- `NUMBER_FIELD_ADELIC_CALIBRATION.md`
- `FINITE_LOCAL_GLOBAL_RECONSTRUCTION.md`
- `SPECTRAL_AND_PHYSICAL_INTERPRETATIONS.md`
- `INVERSE_ADELIC_SPECTRAL_GEOMETRY.md`
- `GLOBAL_INVERSE_RECONSTRUCTION.md`

### Publication 2 — Arithmetic Sensing

- `ARITHMETIC_SENSING.md` — random-time theorem layer
- `ARITHMETIC_SENSING_II.md` — deterministic theorem and impossibility layer
- `ARITHMETIC_SENSING_III.md` — optimized positive quadrature and alias theorem
- `ARITHMETIC_SENSING_IV.md` — continuum positivity, alias bands, fixed degree,
  and an enriched local channel
- `STAGE_9_ARITHMETIC_SENSING_PLAN.md` — research plan and falsification rules

### Research program 3 — Operational Information Geometry

- `OPERATIONAL_INFORMATION_GEOMETRY_I.md` — first theorem-and-falsification
  layer: geometry from distinguishable histories
- `OPERATIONAL_INFORMATION_GEOMETRY_II.md` — protocol invariance, adversarial
  observers, common kernels, and stable mixture recovery
- `OPERATIONAL_INFORMATION_GEOMETRY_III.md` — independent composition, hidden
  interactions, Markov boundaries, and multiscale observation
- `OPERATIONAL_INFORMATION_GEOMETRY_IV.md` — interventions, finite causal jets,
  one-way rate modulation, and approximate causal cones
- `OPERATIONAL_INFORMATION_GEOMETRY_V.md` — continuum scale flow,
  noncommuting dimension limits, response regularity, diffusive leakage, and
  protocol boundaries
- `oig_iv_certificate.md` — outward-rounded finite-grid E-design certificate
- `oig_v_scaling_report.md` — independent continuum and propagation audit

`RESEARCH_ROADMAP.md` records the overall sequence and the boundary between
proved results, computation, conjecture, and interpretation.

## Code map

- `arithmetic_sensing.py` — random sensing and complete quadratic-tail bounds
- `deterministic_arithmetic_sensing.py` — Hann midpoint and alias-safe theorem
- `arithmetic_indistinguishability.py` — two-ball lower bound and Perlis metadata
- `optimized_arithmetic_quadrature.py` — convex arithmetic window design
- `fixed_degree_arithmetic_sensing.py` — universal `d_d` coefficient envelopes
- `arithmetic_sensing_iv.py` — Stage IV reproduction and continuation studies
- `operational_information_geometry.py` — observable-history geometry,
  factorization universe, matched controls, and finite diagnostics
- `operational_information_geometry_ii.py` — protocol ensembles, scale-free
  distortion, axis-blind controls, and simplex-tangent recovery
- `operational_information_geometry_iii.py` — composition laws, interaction
  witnesses, Markov controls, and positive multiscale design
- `operational_information_geometry_iv.py` — directed response, finite causal
  jets, uniformization envelopes, background controls, compressed response
  protocols, and positive finite-grid response design
- `operational_information_geometry_v.py` — canonical continuum-normalized
  scale flow, spectral dimension, modal response, and protocol boundaries
- `oig_v_scaling_continuum.py` — independent regularity, propagation, and
  expanding-domain audit
- `oig_iv_certificate.py` — rational/Arb finite-grid E-design checker
- `adelic_poisson.py`, `quadratic_adelic_geometry.py` — adelic and field models
- `global_trace_inversion.py`, `class_group_obstruction.py` — inverse Stage 8
- `arithmetic_acceleration.py`, `exact_rigidity_certificates.py` — exact finite
  rigidity certificates
- `test_*.py` — independent executable checks

## Scope

The repository establishes conditional finite recovery statements and exact
structural obstructions. It does **not** establish:

- the Riemann hypothesis or any claim about nontrivial zeta zeros;
- a spectral operator whose spectrum is the zeta-zero set;
- a new physical law or a “theory of everything”;
- global optimality of the Hann window;
- recovery of a general number field from its Dedekind zeta function;
- literature novelty beyond the explicitly separated constructions without
  independent review.

## Sources

Each manuscript contains its local bibliography and novelty boundary. Two
central sources are:

- H. Montgomery and R. Vaughan, *Hilbert's Inequality*, Journal of the London
  Mathematical Society 8 (1974), 73–82.
- R. Perlis, *On the equation zeta_K(s)=zeta_K'(s)*, Journal of Number Theory 9
  (1977), 342–360, <https://doi.org/10.1016/0022-314X(77)90070-1>.

## License

No reuse license has yet been assigned. The repository is public for
inspection and reproducibility; copyright and reuse terms remain reserved
until the human owner chooses a license.
