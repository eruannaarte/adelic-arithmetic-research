# Adelic Arithmetic Research

This repository contains the manuscripts, executable laboratories, and tests
for two TGN research publications:

1. **The Geometry Arithmetic Remembers** — an eight-stage path from ordered
   multiplicative rigidity through adelic harmonic analysis, number-field
   calibration, spectral interpretation, and inverse reconstruction.
2. **Arithmetic Sensing** — stable recovery of finite Dirichlet coefficients
   from noisy global traces, deterministic tapered quadrature, complete
   analytic-tail certificates, and explicit nonidentifiability results.

The active continuation includes continuum-certified arithmetic window design
and a log-Mellin convolution certificate for higher-degree coefficient tails.
At `N=50`, `sigma=2`, `T=1000`, and `m=5000`, the eight-harmonic positive
quadrature bounds the complete quadratic tail by `0.0000456318`. The new
fixed-degree argument certifies every number field through degree eight at the
same parameters, with a degree-eight bound of `0.376282`; degree nine is the
first failure at `1.13679`. An exact rational Sturm calculation independently
certifies positivity and the density cap for the published window.

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

## Reproduce Arithmetic Sensing V

Run the exact density certificate, the default degree-five report, and the
enriched local-moment channel:

```sh
python arithmetic_sensing_v.py
```

The longer continuation studies are opt-in:

```sh
python arithmetic_sensing_v.py --degree-study
python arithmetic_sensing_v.py --bin-study
python arithmetic_sensing_v.py --degree-aware-study
python arithmetic_sensing_v.py --degree-nine-time-study
python arithmetic_sensing_v.py --noise-study
```

See `ARITHMETIC_SENSING_V.md` for the log-Mellin convolution theorem, the
degree-eight recovery boundary, degree-nine time continuation, sampling/noise
costs, and exact local collision separation.

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
- `ARITHMETIC_SENSING_V.md` — exact positivity, Mellin-convolution tails,
  degree-eight universality, and quantitative continuation costs
- `STAGE_9_ARITHMETIC_SENSING_PLAN.md` — research plan and falsification rules

`RESEARCH_ROADMAP.md` records the overall sequence and the boundary between
proved results, computation, conjecture, and interpretation.

## Code map

- `arithmetic_sensing.py` — random sensing and complete quadratic-tail bounds
- `deterministic_arithmetic_sensing.py` — Hann midpoint and alias-safe theorem
- `arithmetic_indistinguishability.py` — two-ball lower bound and Perlis metadata
- `optimized_arithmetic_quadrature.py` — convex arithmetic window design
- `fixed_degree_arithmetic_sensing.py` — universal `d_d` coefficient envelopes
- `arithmetic_sensing_iv.py` — Stage IV reproduction and continuation studies
- `arithmetic_sensing_v.py` — Stage V reproduction and boundary studies
- `exact_trigonometric_positivity.py` — exact rational Sturm certificates
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
