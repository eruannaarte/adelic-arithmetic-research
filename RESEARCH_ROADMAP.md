# Order–Factorization and Adelic Geometry: Recommended Work Order

**Updated:** 2026-08-13

This roadmap keeps the adelic line as the main program while preserving finite
arithmetic rigidity as an adjacent branch that can be resumed when it becomes a
dependency.

## Main line

### Stage 1 — Abstract ordered-monoid rigidity — complete

Prove that an extensive real scalar respecting a nontrivial multiplicative
size is a constant multiple of logarithmic size. Extend from monoids to groups
and audit all assumptions.

Deliverable: `ABSTRACT_ORDERED_MONOID_RIGIDITY.md`.

### Stage 2 — Local–global calibration on `Q_(>0)` — complete

Construct the logarithmic valuation embedding, prove local calibration at each
place, show that global conservation synchronizes the local scales, derive the
product-order obstruction, and analyze finite-prime lattice geometry.

Deliverables: `LOCAL_GLOBAL_ADELIC_CALIBRATION.md`,
`adelic_log_geometry.py`, and `test_adelic_log_geometry.py`.

### Stage 3 — Lift from the log skeleton to the rational adeles — complete

Work with the actual restricted product

`A_Q = R times restricted_product_p Q_p`

and its idele group. Specify the topology, diagonal rational embedding, local
and global additive characters, Haar normalization, self-duality, and Poisson
summation. Determine which parts admit a rigidity interpretation and which are
additional analytic structure.

Primary test: reproduce the adelic Poisson formula first for a controlled class
of factorable test functions without claiming anything new about zeta.

Result: diagonal `Q` is exhibited as a discrete, cocompact, self-annihilating
lattice in `A_Q`; the standard global character and self-dual Haar measure are
fixed; and Poisson summation is derived explicitly for Gaussian times
compact-open test functions.

Deliverables: `RATIONAL_ADELES_AND_POISSON.md`, `adelic_poisson.py`, and
`test_adelic_poisson.py`.

### Stage 4 — Extend from `Q` to number fields — complete

Generalize local–global calibration to normalized places of a number field.
Handle complex-place weights, units, ideal classes, the logarithmic unit
lattice, and the regulator. Test first on `Q(i)` and `Q(sqrt(5))` using exact
ideal arithmetic.

Primary theorem target: identify the weakest conditions under which local
order and global conservation synchronize all place calibrations.

Result: local order calibrates every place separately; Dirichlet's unit lattice
synchronizes all Archimedean scales; and finite ideal classes synchronize every
finite prime with that common scale. Exact quadratic laboratories verify unit,
splitting, ramification, ideal-factorization, regulator, discriminant, and
self-dual-volume behavior.

Deliverables: `NUMBER_FIELD_ADELIC_CALIBRATION.md`,
`quadratic_adelic_geometry.py`, and `test_quadratic_adelic_geometry.py`.

### Stage 5 — Finite local–global reconstruction — complete first layer

Replace infinite comparison axioms with bounded-height rational or ideal data.
Measure which local coordinates and global relations are recoverable, and at
what rate. Produce exact rational certificates where possible.

Arithmetic acceleration becomes a direct dependency at this stage. Begin with
minimal finite relation sets and exact certificates over `Q`, then compare the
effects of split primes and unit lattices over `Q(i)` and `Q(sqrt(5))`.

Result: the two-prime subsystem reduces exactly to bounded pure-power
comparisons; the full rational model admits sparse, exactly verified dual
certificates and is over 3,100 times narrower at cutoff 100,000; and
coefficient-height-two principal-element bases synchronize every active place
in both quadratic laboratories. Larger bounded boxes retain nullity one through
height eight, while rational-integer-only controls fail to distinguish the
field-specific directions.

Deliverables: `ARITHMETIC_ACCELERATION.md`,
`FINITE_LOCAL_GLOBAL_RECONSTRUCTION.md`, `two_prime_rigidity.py`,
`exact_rigidity_certificates.py`, `arithmetic_acceleration.py`,
`finite_number_field_reconstruction.py`, and their tests.

### Stage 6 — Spectral and physical interpretations — complete first layer

Only after the local–global structure is stable, study factorable test
functions, Euler products, twisted traces, and engineered prime-mode systems.
Keep encoding zeta separate from explaining its zeros.

Result: prime valuations become exact bosonic occupations with energy `log p`;
their heat traces equal both finite Euler products and normalized `p`-adic Tate
shell integrals. Twisted, fermionic, prime-power, and quadratic prime-ideal
variants are verified. A noisy sparse-recovery laboratory identifies an
observability transition for crowded log-prime modes while documenting alias,
coherence, sample-count, and noise failure regimes. The unit regulator is shown
to be absent as an explicit lattice direction from the local prime-ideal modes;
direct geometric recovery requires an Archimedean channel.

Deliverables: `SPECTRAL_AND_PHYSICAL_INTERPRETATIONS.md`,
`spectral_adelic_system.py`, `number_field_spectral_system.py`,
`sparse_prime_mode_recovery.py`, and their tests.

### Stage 7 — Inverse adelic spectral geometry — complete first layer

Turn the forward local-factor construction into an inverse problem. Determine
which place data—prime support, splitting type, finite calibration, and unit
regulator—can be reconstructed from incomplete, noisy traces or responses.
Seek recovery guarantees for structured log-prime measurement matrices and
robust versions of the Stage 5 rigidity certificates. Test interacting modes
as explicit countermodels to Euler factorization.

Primary boundary: recovering a known adelic decomposition from data is not the
same problem as producing a spectral realization of zeta zeros.

Result: two labelled local coefficients classify quadratic splitting exactly;
noisy local heat traces recover split/inert/ramified behavior across the two
quadratic laboratories; a noisy Archimedean unit channel recovers `log(phi)`
with an exact variance law; Stage 5 certificates acquire rigorous defect
budgets; and a realized log-prime dictionary satisfies a deterministic
noiseless OMP coherence guarantee. Repulsive cross-mode interactions give
exact countermodels to Euler factorization and demonstrate that one aggregate
partition value is not identifiable evidence for an underlying free geometry.

Deliverables: `INVERSE_ADELIC_SPECTRAL_GEOMETRY.md`,
`inverse_splitting_recovery.py`, `inverse_regulator_recovery.py`,
`robust_rigidity_certificates.py`, `interacting_prime_modes.py`, extensions to
`sparse_prime_mode_recovery.py`, and their tests.

### Stage 8 — Global inverse reconstruction and class-group obstructions — complete first layer

Pass from labelled local probes to partially aggregated global data. Establish
what additional priors make an Euler decomposition identifiable, extend the
inverse laboratory to fields with nontrivial class group, and seek random-time
sample-complexity bounds. Develop redundant minimum-noise rigidity backbones
and joint recovery of unit lattices with unknown generators.

Result: full response curves and controlled finite Dirichlet traces are shown
to identify their coefficient sequences, while experiments expose sharp
conditioning and omitted-tail failures. In `Q(sqrt(-5))`, a principal-divisor
matrix has Smith invariants `(1,1,2)`, recovering the class obstruction as an
integral index invisible over `R`. Minimum-mass and alternative rigidity
backbones improve amplitude-noise and missing-edge robustness. Unknown
rank-one unit samples recover the fundamental regulator exactly when their
integer multipliers are primitive.

Deliverables: `GLOBAL_INVERSE_RECONSTRUCTION.md`,
`class_group_obstruction.py`, `global_trace_inversion.py`,
`redundant_rigidity_backbones.py`, `unknown_unit_lattice.py`, and their tests.

### Stage 9 — Arithmetic sensing — first theorem layer complete

Develop an information theory for recovering local arithmetic structure from
noisy aggregate global traces. Prove nonasymptotic conditioning bounds for
random-time logarithmic Fourier dictionaries, incorporate analytic Dedekind-tail
budgets into stable finite recovery, and establish lower bounds or explicit
indistinguishable models when reconstruction is impossible.

Use higher-rank unit lattices and larger or noncyclic class groups as exact
structured laboratories. Recover unit lattices only up to `GL_r(Z)`, distinguish
continuous rank from integral torsion, and compare fields with identical or
nearly identical finite trace data. The desired output is both a recovery theory
and an impossibility theory: every positive algorithmic result should carry a
quantitative guarantee, and every nonidentifiability claim should carry an
explicit collision or information bound.

Primary first target: a stable finite Dirichlet-coefficient theorem with three
separate terms in its error bound—measurement noise, matrix conditioning, and
the omitted analytic tail—followed by matching computational tests.

Result: the least-squares error is decomposed exactly into realized Gram
conditioning, measurement noise, coherent population tail bias, and
finite-sample tail fluctuation. Uniform-time sampling produces an explicit sinc
Gram kernel; matrix Chernoff gives a nonasymptotic design guarantee; and
quadratic Dedekind coefficients admit field-uniform `tau(n)` tail certificates.
A coefficientwise Bernstein–Gaussian theorem certifies exact integer rounding
when its computed margins are below `1/2`. At `N=50`, `sigma=2`, `T=10,000`,
and 500,000 samples, all 20 held-out designs certify against the complete
quadratic tail and noise standard deviation `0.01` under the stated probability
budget.

Deliverables: `ARITHMETIC_SENSING.md`, `arithmetic_sensing.py`, and
`test_arithmetic_sensing.py`.

### Stage 9 continuation — deterministic arithmetic sensing — complete theorem layer

Replace random-time empirical least squares by deterministic weighted
midpoint quadrature. Derive exact uniform and Hann grid kernels, control the
complete quadratic Dedekind tail across remote sampling aliases, and retain an
exact sensor-noise covariance. Develop quantitative and exact impossibility
results alongside the recovery theorem.

Result: the dependence between a random empirical Gram inverse and its tail
correlations blocks the naive direct Bernstein improvement. A Hann midpoint
design removes that random dependence entirely. At `N=50`, `sigma=2`,
`T=1,000`, and 5,000 grid points, the complete quadratic tail is bounded by
`0.0271845`, certifying noiseless integer rounding. With 100,000 readings and
circular complex noise `nu=0.01`, the Gaussian rounding-failure bound is
`8.84*10^-11`. An explicit adjacent-mode pair gives a positive adversarial
ambiguity radius, while Perlis' degree-eight fields give an exact zero-distance
collision for field identification from complete Dedekind-zeta data. The
proposed exact-discriminant field-specific certificate is rejected as circular
because the discriminant already determines every quadratic zeta coefficient.

Deliverables: `ARITHMETIC_SENSING_II.md`,
`deterministic_arithmetic_sensing.py`,
`arithmetic_indistinguishability.py`, and their tests.

### Stage 9 continuation — optimized arithmetic quadrature — first layer complete

Optimize positive midpoint weights specifically for logarithmic integer
frequencies, subject to target conditioning, sampling-density, and alias-safety
constraints.

Result: every weighting of a fixed midpoint grid is proved to have unit
magnitude at the exact grid aliases, so alias suppression by weights alone is
impossible. A linear program over positive cosine-series windows instead
minimizes a divisor-weighted pre-alias leakage proxy while enforcing a
Gershgorin Gram bound. At `N=50`, `sigma=2`, `T=1,000`, and `m=5,000`, an
eight-harmonic window independently certifies the complete quadratic tail by
`0.000232014`, 117 times tighter than the Hann certificate while satisfying
the declared conditioning and sampling-density constraints. A more
noise-balanced Pareto point is 54.8 times tighter. The improvement survives a
million-term exact kernel audit plus analytic remote-alias control.

Deliverables: `ARITHMETIC_SENSING_III.md`,
`optimized_arithmetic_quadrature.py`, and its tests.

### Stage 9 continuation — Arithmetic Sensing IV — six-step expansion complete

Replace midpoint-only density checks by whole-interval certificates, resolve
the unenumerated divisor tail alias by alias, test harmonic/cutoff stability,
optimize the sampling ratio on a certified grid, extend the envelope to fixed
degree, and exhibit a local channel that breaks a Dedekind-zeta collision.

Result: a Chebyshev extremum exchange plus margin-shifted Fejer--Riesz factors
certifies the optimized density on the full period. Dirichlet-hyperbola and
Abel bounds on individual log-frequency intervals sharpen the 5,000-sample
quadratic coefficient certificate from `0.000232014` to `0.0000456318`.
Held-out leakage improves monotonically through `H=2,4,6,8`, and the optimized
coefficients stabilize through `M_d=100,150,200,300`. Re-optimization on a
sampling-ratio grid finds that `m/T=4.42`, just above the million-term alias
threshold, retains a `0.0000458959` bound. The universal `d_d` extension
certifies degrees two through four and fails to certify degree five at the same
parameters. For the Perlis pair from `x^8-33` and `x^8-528`, identical local
Euler data at 2 is separated by local component dimensions `(1,1,2,4)` versus
`(2,2,2,2)`.

Deliverables: `ARITHMETIC_SENSING_IV.md`, `arithmetic_sensing_iv.py`,
`fixed_degree_arithmetic_sensing.py`, expanded local-probe and optimized-
quadrature modules, and their tests.

### Stage 9 continuation — Arithmetic Sensing V — theorem layer complete

Replace the coarse pre-alias estimate for the universal fixed-degree envelope
`d_d=1^{*d}` by a positive log-Mellin convolution certificate. Partition one
zeta factor into logarithmic bins, convolve the certified bin masses `d` times,
pair those masses with interval suprema of the sampling kernel, and close the
remaining remote tail analytically. Certify the published trigonometric window
over the continuum with exact rational arithmetic, then measure where degree,
observation time, sensor count, and enriched local information change the
recovery conclusion.

Result: the old degree-five failure is traced to a deliberately coarse remote
remainder, not to observed tail mass. The new positive convolution bound gives
`0.00775069` in degree five and certifies every number field through degree
eight at the Stage IV parameters; degree nine is the first failure, at
`1.13679`. Holding `m/T=5`, degree nine crosses the `1/2` rounding threshold by
`T=2450`. Exact Sturm sequences prove
`10^-5 < p(theta) < 2.499999995` for the rationalized eight-harmonic density.
For quadratic fields with sensor noise `0.01`, about 67,200 readings make the
stated union-bound failure probability smaller than `10^-6`. Finally, power
moments of the 2-adic component dimensions separate the Perlis collision at
moment order two, with integer observation distance six and adversarial
ambiguity radius three.

Deliverables: `ARITHMETIC_SENSING_V.md`, `arithmetic_sensing_v.py`,
`exact_trigonometric_positivity.py`, strengthened fixed-degree and local-probe
modules, and their tests.

**Verified-Mellin milestone:** the heuristic one-factor safety multiplier is
replaced by 192-bit directed MPFR boundaries, `2^-96` dyadic bin upper bounds,
and exact carry-free integer convolution. The committed 11-kilobyte checker
artifact reconstructs all remote target bounds for degrees 5, 8, and 9 and
confirms that the degree-eight/degree-nine boundary is unchanged. The formal
scope is the post-million Mellin remainder; the finite vectorized sum and Gram
inverse remain explicitly hybrid.

Deliverables: `ARITHMETIC_SENSING_V_VERIFIED_MELLIN.md`,
`verified_mellin_certificate.py`, `verify_mellin_certificate.py`,
`certificates/arithmetic_sensing_v_verified_mellin.json`, and their tests.

**Cancellation and all-alias optimization milestone:** an exact
common-numerator factorization is used before taking absolute values, yielding
a directed-MPFR interval theorem that preserves the cosine window's intended
cancellation. At the unchanged `N=50`, `sigma=2`, `T=1000`, `m=5000`
resources, the reference window now certifies every fixed-degree number field
through degree thirteen (`0.330597`); degree fourteen is the first failure of
this sufficient proof (`0.842697`). The former degree-nine remote bound falls
by about 247 times. A search containing every million-term finite response and
every retained Mellin alias bin improves the degree-nine complete bound by a
further 3.77%, while remote-only and single-target searches supply explicit
negative controls. The formal artifact covers the remote terms; finite sums
and the Gram inverse remain hybrid.

Deliverables: `ARITHMETIC_SENSING_V_ALL_ALIAS_OPTIMIZATION.md`,
`all_alias_mellin_optimization.py`, cancellation-aware extensions to the
kernel and verified-Mellin modules,
`certificates/arithmetic_sensing_v_cancellation_frontier.json`, and their
tests.

**End-to-end formal-numerics milestone:** checked unsigned-integer convolution
constructs the degree-13 and degree-14 divisor coefficients through one
million, and Arb encloses every finite response and Gram off-diagonal. A
localized Neumann theorem replaces numerical matrix inversion while avoiding
the false global pairing of target 1's largest raw tail with target 50's
quadratic scale. Composed with the directed-MPFR remote artifact, degree
thirteen is formally certified at `0.3308795520`; degree fourteen is the first
failure at `0.8438209207`. The formal frontier therefore agrees with the hybrid
frontier. A proposed single Mellin certificate beginning at norm 50 is rejected
because tuple-bin width destroys adjacent-mode cancellation and gives a bound
above 12.

Deliverables: `ARITHMETIC_SENSING_V_END_TO_END.md`,
`verified_end_to_end_certificate.py`, `verify_end_to_end_certificate.py`,
`certificates/arithmetic_sensing_v_end_to_end.json`, and their tests.

## Adjacent target — arithmetic acceleration

**Status:** first exact study completed in Stage 5; asymptotic questions remain
active.

The empirical finite-rigidity bounds converge far faster than the universal
power-squeeze argument explains. The working term **arithmetic acceleration**
means the extra rigidity supplied by the dense web of factorization relations
among nearby integers.

Subprojects:

1. solve the two-prime continued-fraction model exactly;
2. extract exact rational dual certificates from the finite LP, then add exact
   primal witnesses;
3. identify the sparse dual-support “rigidity backbone”;
4. test the conjectured `N^(-1+o(1))` interval width at larger cutoffs;
5. relate the useful adjacent pairs to smooth neighbors and linear forms in
   logarithms.

Continue this branch when any of the following occurs:

- Stage 3 or 4 requires quantitative control of finite projections;
- exact primal witnesses are needed to certify finite optimality;
- a claimed adelic reconstruction rate depends on it;
- an exact public certificate is needed;
- computational evidence contradicts the assumed separation between universal
  Archimedean rigidity and arithmetic acceleration.

## Validation rules for every stage

1. Separate established mathematics, new proofs, conjectures, and
   interpretations explicitly.
2. Give counterexamples showing why each structural assumption is needed.
3. Do not infer an intrinsic metric from a convenient coordinate metric.
4. Use exact arithmetic or independently checkable certificates when feasible.
5. Treat numerical agreement as evidence or verification, never as proof of an
   infinite statement.
6. Do not present a zeta encoding as progress on the Riemann hypothesis without
   an independently defined operator and new control of its spectrum.
