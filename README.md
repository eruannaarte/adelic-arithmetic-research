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
and a cancellation-aware log-Mellin certificate for higher-degree coefficient
tails. At `N=50`, `sigma=2`, `T=1000`, and `m=5000`, the eight-harmonic
positive quadrature bounds the complete quadratic tail by `0.0000456318`. An
exact common-numerator identity removes a triangle-inequality artifact in the
remote theorem and now certifies every number field through degree thirteen at
the same parameters. Degree thirteen gives `0.330597`; degree fourteen is the
first failure of this sufficient certificate at `0.842697`. Exact rational
Sturm calculations independently certify the published window and the new
all-alias optimization candidate over the full continuum.

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
python arithmetic_sensing_v.py --degree-study --maximum-study-degree 15
python arithmetic_sensing_v.py --bin-study
python arithmetic_sensing_v.py --degree-aware-study
python arithmetic_sensing_v.py --degree-nine-time-study
python arithmetic_sensing_v.py --noise-study
```

See `ARITHMETIC_SENSING_V.md` for the log-Mellin convolution theorem, the
original degree-eight boundary, degree-nine time continuation, sampling/noise
costs, and exact local collision separation. The later cancellation theorem
supersedes that numerical boundary without altering the original argument.

Verify the outward-rounded MPFR/dyadic remote-tail artifact:

```sh
python verify_mellin_certificate.py
```

The checker reconstructs the exact dyadic convolutions for degrees 5, 8, and
9. See `ARITHMETIC_SENSING_V_VERIFIED_MELLIN.md` for its proof boundary.

Verify the cancellation-aware degree 9/13/14 frontier and reproduce the
all-alias optimization candidate:

```sh
python verify_mellin_certificate.py \
  --certificate certificates/arithmetic_sensing_v_cancellation_frontier.json \
  --degrees 9,13,14 --skip-hybrid-report
python all_alias_mellin_optimization.py --complete-certificate
```

See `ARITHMETIC_SENSING_V_ALL_ALIAS_OPTIMIZATION.md` for the exact response
factorization, directed interval theorem, new degree-thirteen frontier,
optimizer falsification experiments, and remaining formal boundary.

Close that formal boundary with the end-to-end checker:

```sh
python verify_end_to_end_certificate.py --processes 8
```

This composes the remote artifact with one hundred million Arb finite-response
evaluations and an inverse-free Gram theorem. Degree thirteen is formally
certified at `0.3308795520`; degree fourteen first fails at `0.8438209207`.
See `ARITHMETIC_SENSING_V_END_TO_END.md`.

Reproduce the compact degree-fourteen resource-boundary study:

```sh
python degree_fourteen_resource_law.py
```

At `T=1000`, the formal endpoint at 14,690 samples misses the strict threshold
at `0.5000009667`, while 14,691 formally pass at `0.4999975382`. Along
`m/T=5`, the adjacent formal boundary is `T=1892/1893`. See
`ARITHMETIC_SENSING_V_DEGREE_14_RESOURCE_LAW.md`.

Reproduce the resonance-aware nested time ensemble:

```sh
python time_ensemble_design.py
```

The ratios `51/50` and `52/50` explain more than 99% of the two largest finite
resource peaks. A positive reweighting of a 2,500-point central subset inside
an 8,950-point grid suppresses the dominant lobe. Its formal endpoint is
`0.4972362699` at maximum time 1,790, improving both resource coordinates of
the previous ratio-five frontier. See `ARITHMETIC_SENSING_V_TIME_DIVERSITY.md`.

Run the arithmetic multiscale design algorithm:

```sh
python arithmetic_multiscale_sensing.py
```

The dangerous-mode detector, positive minimax LP, sparse-support search, and
exact dyadic rationalization produce a nested candidate using 8,900 distinct
readings through time 1,780. Its independent all-target Arb/MPFR endpoint is
`0.4980274168`. See `ARITHMETIC_SENSING_V_MULTISCALE.md`.

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
- `ARITHMETIC_SENSING_V_VERIFIED_MELLIN.md` — MPFR-directed bins, exact dyadic
  convolution, and the compact remote-tail checker
- `ARITHMETIC_SENSING_V_ALL_ALIAS_OPTIMIZATION.md` — cancellation geometry,
  the degree-thirteen frontier, and actual all-alias window search
- `ARITHMETIC_SENSING_V_END_TO_END.md` — Arb finite tails, inverse-free Gram
  control, and the formal degree-thirteen frontier
- `ARITHMETIC_SENSING_V_DEGREE_14_RESOURCE_LAW.md` — exact sampling and
  observation thresholds amid logarithmic resonances
- `ARITHMETIC_SENSING_V_TIME_DIVERSITY.md` — resonance attribution and a
  formally certified nested two-window sensing measure
- `ARITHMETIC_SENSING_V_MULTISCALE.md` — convex response-signature design,
  sparse positive minimax search, and an 8,900-reading formal certificate
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
- `verified_mellin_certificate.py` — directed MPFR and exact convolution core
- `verify_mellin_certificate.py` — compact-artifact builder and checker
- `all_alias_mellin_optimization.py` — million-term plus all-alias candidate
  objective and independent candidate audit
- `verified_end_to_end_certificate.py` — Arb finite sums and localized Neumann
  consequence
- `verify_end_to_end_certificate.py` — compact end-to-end artifact builder and
  checker
- `degree_fourteen_resource_law.py` — fixed-time density and fixed-ratio
  observation scans
- `time_ensemble_design.py` — dominant-mode attribution and nested-ensemble
  exploration
- `arithmetic_multiscale_sensing.py` — dangerous-mode detection, positive
  minimax design, sparse-support search, and exact nested-grid realization
- `verify_time_ensemble_certificate.py` — formal signed multi-time Arb
  certificate builder and checker
- `verify_multiscale_certificate.py` — reference multiscale artifact builder
  and checker
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
