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

Stages VI and VII then prove the fixed-mode continuum limit and resolve the
smooth-to-atomic initial layer. A concentrating target of width
\(\varepsilon\) has an explicit continuum phase function in
\(t/\varepsilon^2\); at \(\varepsilon/h=O(1)\), an explicit lattice phase
retains cell placement and preparation rules. The two charts match, while an
adversarial audit separates multiplication-moment order from the complete
noncommutative causal-word hierarchy.

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

Run the Stage VI fixed-mode continuum theorem, high-precision audit, and
adversarial controls:

    python -m pip install -r oig_vi_fixed_mode_requirements.txt
    python oig_vi_fixed_mode_convergence.py
    python -m unittest -v test_oig_vi_fixed_mode_convergence.py
    python oig_vi_adversarial_controls.py
    python -m unittest -v test_oig_vi_adversarial_controls.py

See [OPERATIONAL_INFORMATION_GEOMETRY_VI.md](OPERATIONAL_INFORMATION_GEOMETRY_VI.md)
for compact Mosco convergence, positive-time embedded semigroup convergence,
fixed-response convergence through time zero, the smooth positive-time
\(O(n^{-2})\) theorem, atomic and growing-band boundaries, and the next
mollifier target.

Run the Stage VII smooth-to-atomic phase laboratories:

    python -m pip install -r oig_vii_mollifier_requirements.txt
    python -m unittest -v test_oig_vii_mollifier_phase.py
    python oig_vii_mollifier_phase.py --fast
    python oig_vii_mollifier_phase.py
    python oig_vii_adversarial_controls.py
    python -m unittest -v test_oig_vii_adversarial_controls.py

See [OPERATIONAL_INFORMATION_GEOMETRY_VII.md](OPERATIONAL_INFORMATION_GEOMETRY_VII.md)
for the continuum and lattice phase laws, their matching limit, odd/even ramp
critical widths, fixed-positive-time atomic universality, and the explicit
boundary between multiplication moments and complete causal order.

Run the Stage VIII uniform three-parameter atlas and adversarial controls:

    python -m pip install -r oig_viii_three_parameter_requirements.txt
    python -m unittest -v test_oig_viii_three_parameter.py
    python -m unittest -v test_oig_viii_adversarial_controls.py
    python oig_viii_three_parameter.py --fast
    python oig_viii_three_parameter.py

See [OPERATIONAL_INFORMATION_GEOMETRY_VIII.md](OPERATIONAL_INFORMATION_GEOMETRY_VIII.md)
for the quantitative resolved and lattice charts, the direct simultaneous
atomic theorem, reflecting-boundary crossover, critical-width resolution
certificates, and the discrete-moment obstruction. The dedicated dependency
surface, exact source digests, reference environment, and complete validation
commands are frozen in
[OIG_VIII_REPRODUCIBILITY_MANIFEST.md](OIG_VIII_REPRODUCIBILITY_MANIFEST.md).

Run the outward-rounded finite-grid E-design certificate separately:

```sh
python -m pip install -r oig_iv_certificate_requirements.txt
python oig_iv_certificate.py --grid both
python -m unittest -v test_oig_iv_certificate.py
```

The certificate proves
`4.982412e-9 <= z_* <= 4.982942e-9` on both the exact canonical grid and the
frozen binary64 grid. It does not certify a continuum-time optimum.

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

Run adaptive mode exchange and the exact support-optimality layer:

```sh
python adaptive_multiscale_exchange.py
```

Starting from two modes, four full-tail exchange rounds keep selecting
`T=510`. Exact rational duals weakened over 192-bit Arb intervals then prove
that `T=510` uniquely beats every other declared short time from 300 through
800 for the resulting fourteen-mode objective. The published dyadic weight
retains a rigorous support gap above `5.07e-7`. See
`ARITHMETIC_SENSING_V_ADAPTIVE_EXCHANGE.md`.

Close the finite residual with a complete million-mode stopping certificate:

```sh
python verify_residual_stopping_certificate.py --processes 5
```

The fourteen-mode duals eliminate 45 competing supports, and complete Arb
duals eliminate the remaining five. The exact published `T=510` design beats
every other declared pair support on the complete target-50 finite objective,
with closest gap `5.0873130853e-7`. See
`ARITHMETIC_SENSING_V_RESIDUAL_STOPPING.md`.

For the public synthesis of the complete progression, see
`ARITHMETIC_SENSING_V_COMPLETE.md`.

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

- `ARITHMETIC_SENSING_V_COMPLETE.md` — canonical unified Arithmetic Sensing V
  publication, from log-Mellin geometry through residual stopping
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
- `ARITHMETIC_SENSING_V_ADAPTIVE_EXCHANGE.md` — adaptive mode rows, exact
  rational duality, and Arb-robust pair-support selection
- `ARITHMETIC_SENSING_V_RESIDUAL_STOPPING.md` — selected-mode screening,
  complete million-mode duals, and the finite pair-support stopping theorem
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
- [OPERATIONAL_INFORMATION_GEOMETRY_VI.md](OPERATIONAL_INFORMATION_GEOMETRY_VI.md)
  — fixed-mode continuum theorem, sharp positive-time response rate, and
  time-zero boundary
- [OIG_VI_FIXED_MODE_RESPONSE_THEOREM.md](OIG_VI_FIXED_MODE_RESPONSE_THEOREM.md)
  — detailed Mosco and quantitative finite-element proof
- [oig_vi_fixed_mode_convergence.md](oig_vi_fixed_mode_convergence.md) —
  exact modal expansion, high-precision audit, and outward-rounded finite-block
  checks
- [OIG_VI_ADVERSARIAL_AUDIT.md](OIG_VI_ADVERSARIAL_AUDIT.md) — rate, atom,
  endpoint, symmetry, and growing-band falsification controls
- [OPERATIONAL_INFORMATION_GEOMETRY_VII.md](OPERATIONAL_INFORMATION_GEOMETRY_VII.md)
  — smooth-to-atomic phase diagram, continuum/lattice matching, and critical
  width boundary
- [OIG_VII_CONTINUUM_MOLLIFIER_THEOREM.md](OIG_VII_CONTINUUM_MOLLIFIER_THEOREM.md)
  — detailed balanced, early, atomic, and finite-cell proofs
- [oig_vii_mollifier_phase.md](oig_vii_mollifier_phase.md) — full-generator,
  high-precision, lattice, bridge, and phase-ridge audit
- [OIG_VII_ADVERSARIAL_AUDIT.md](OIG_VII_ADVERSARIAL_AUDIT.md) — sampling,
  boundary, operator-topology, and mixed-word counterexamples
- [OPERATIONAL_INFORMATION_GEOMETRY_VIII.md](OPERATIONAL_INFORMATION_GEOMETRY_VIII.md)
  — uniform three-parameter atlas, simultaneous atomic theorem, boundary
  crossover, and critical-resolution barrier
- [OIG_VIII_RESOLVED_UNIFORM_THEOREM.md](OIG_VIII_RESOLVED_UNIFORM_THEOREM.md)
  — detailed balanced, early, ultra-early, and heat-resolved comparison proof
- [OIG_VIII_LATTICE_UNIFORM_THEOREM.md](OIG_VIII_LATTICE_UNIFORM_THEOREM.md)
  — finite-cell chart, joint atomic tail, variance criterion, and boundary law
- [oig_viii_three_parameter.md](oig_viii_three_parameter.md) — rectangular
  stress scan, overlap rates, critical slowdown, and explicit counterexamples
- [OIG_VIII_ADVERSARIAL_AUDIT.md](OIG_VIII_ADVERSARIAL_AUDIT.md) — independent
  normalization, rate, null-port, boundary, and proof-gap audit
- [OIG_VIII_REPRODUCIBILITY_MANIFEST.md](OIG_VIII_REPRODUCIBILITY_MANIFEST.md)
  — minimal dependencies, immutable theorem commit, source digests, and
  validation commands
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
- [oig_vi_fixed_mode_convergence.py](oig_vi_fixed_mode_convergence.py) —
  exact midpoint structure, fixed-block expansion, high-precision continuum
  comparison, and Galerkin-tail audit
- [oig_vi_adversarial_controls.py](oig_vi_adversarial_controls.py) —
  nonsmooth, atomic, endpoint, symmetry, and growing-band controls
- [oig_vii_mollifier_phase.py](oig_vii_mollifier_phase.py) — continuum and
  lattice phase functions, full finite modal responses, bridge, and ridge
  audits
- [oig_vii_adversarial_controls.py](oig_vii_adversarial_controls.py) —
  lattice-phase, boundary, sampling, topology, symmetry, and mixed-jet controls
- [oig_viii_three_parameter.py](oig_viii_three_parameter.py) — finite,
  lattice, continuum, early, and atomic chart comparisons plus hostile paths
- `oig_iv_certificate.py` — rational/Arb finite-grid E-design checker
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
- `adaptive_multiscale_exchange.py` — million-term mode exchange and exact
  rational/Arb support-frontier certificates
- `verify_time_ensemble_certificate.py` — formal signed multi-time Arb
  certificate builder and checker
- `verify_multiscale_certificate.py` — reference multiscale artifact builder
  and checker
- `verify_adaptive_multiscale_certificate.py` — self-contained exact dual
  artifact builder and checker
- `residual_stopping_envelope.py` — two-layer complete finite support audit
- `verify_residual_stopping_certificate.py` — compact residual-stopping
  artifact builder and checker
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
