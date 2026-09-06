# Master proof appendix and reproduction map

This appendix is the annotated entry point to the five complete proof files. They are part of this package, not omitted supplementary arguments. Read each model definition before its theorem: the paths use different source classes, output norms, and unknowns. The [claim/evidence index](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/CLAIM_EVIDENCE_INDEX.md) gives numbered claims and exact artifact locations. This document supplies the dependency order, accepted results, trusted implementation boundaries, and reproduction commands without duplicating all five proofs.

The proof chain has three distinct layers: an analytic theorem establishes what interval premises imply; an outward producer constructs those premises from the declared source model; an exact checker reconstructs their finite consequences. Regression tests, numerical held-outs, and hashes provide additional controls and identity checks. They do not replace either mathematical arguments or numerical premise reconstruction. Full reproduction requires the applicable layers below. The existing research files imported by the producers remain part of the local proof dependency graph.

## A. Complete proof files and reading order

### A1. Finite preparation and a fixed nonlinear inverse

Read [Path1 PROOF.md](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path1_preparation/PROOF.md) in this order:

1. **Exact model and quantifiers:** finite source box, four-coordinate preparation per launch, one shared finite clock, seven physical scalar readouts, and the weighted adversarial norm.
2. **Finite nonlinear inverse theorem and complete proof (P1-1):** form a fixed rational weighted left inverse B; integrate the source chord while holding one preparation fixed; bound the second preparation difference by twice its uniform bias; apply weighted Cauchy–Schwarz; rearrange using k<1. This produces both joint and componentwise feasible-set diameters.
3. **Nonlinear source-to-certificate proof (P1-2):** positivity of the mechanical mass determinant gives smoothness; nested differentiation produces the parameter sensitivities; autonomy gives the exact finite clock derivative. The defect Taylor remainder and strict Picard tube gate enclose every trajectory. A separate four-dimensional state-difference gate propagates preparation bias at shared parameters, proving homogeneity for smaller preparation radii.
4. **Exact arithmetic, quantitative results, and boundaries (P1-3 through P1-5):** exact interval left-inverse algebra gives the three designs and the preparation/noise half-planes. Scalar counterexamples separate sufficient-test failure from impossibility and positive-error estimation from exact recovery.

The hypotheses concern a smooth local mechanical model and a finite box; they do not require global bounded pendulum flow for arbitrary parameters. Convexity keeps the source chord inside the certified region. Preparation is fixed when differentiating the source. Separate launch enclosures are conservative for a globally shared clock, not a change to independent-clock semantics. [Independent audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path1_preparation/AUDIT.md) checked these connections and an additional analytically solvable linear-flow control.

### A2. Harmonic count, global separation, and finite clock displacement

Read [Path2 PROOFS.md](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path2_harmonic/PROOFS.md):

1. **Sections 1–2 (P2.1):** the labelled factor-product simplex, exact harmonic map, and factor/data norms; the half-DFT floor and a complete elementary prime-log orbit-density argument prove the upper count. The reversal-antisymmetric source sphere and Borsuk's antipodal theorem give the matching lower count. Marginals prove that the paired tensors differ; the proof covers closed-simplex boundaries and arbitrarily small neighborhoods of the uniform source.
2. **Section 3 (P2.2):** differential dimension necessity and the calibrated odd/even frequency Vandermonde construction establish the distinct local count. An actual interior five-reading derivative determinant is enclosed away from zero. Its small magnitude is not advertised as a usable noise floor.
3. **Section 4 (P2.3):** phase centering yields sharper factor derivative constants; individual target/off-axis errors produce a nonnegative block majorant. A Gram row-sum bound controls its operator norm. Integration of the derivative difference over every convex factor chord establishes global separation, not merely local rank.
4. **Sections 5–6 (P2.4 and P2.3-balanced):** a row rotation is legal for one fixed realized clock. A separate finite raw-response derivative bound handles an unknown clock, its displaced response fibres, and global nominal fitting. Shared affine errors fit inside an explicit absolute timing box. Exact schedules are compared under the same improved majorant.
5. **Section 7 (P2-time-obstruction):** a legal third-difference factor perturbation proves the cubic small-time constraint. A resonant schedule gives a genuine exact collision. These do not prove shortest possible acquisition times.

The count model assumes r>=1 and s>=2, known distinct primes, fixed nonadaptive readings, probability normalization, and no tail/gain uncertainty. Shorter schedules trade away some floor. A global least-squares minimizer exists by compactness but no efficient algorithm to obtain it is established. [SOURCES.md](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path2_harmonic/SOURCES.md) and [AUDIT.md](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path2_harmonic/AUDIT.md) record theorem and implementation checks.

### A3. Complete arithmetic tails with adversarial and Gaussian sensor noise

Read [Path3 PROOF.md](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path3_noise/PROOF.md):

1. **Acquisition model and complete bias/Neumann bounds (P3-5):** establish absolute convergence under d14, exact nesting and normalization of the positive weights, the actual 8900-row decoder, and the complete finite-plus-remote tail premises. A rowwise Neumann argument bounds inverse correction and deterministic coefficient bias.
2. **Adversarial bounded-noise theorem (P3-1):** Hermitian Gram control yields G>=(1-q)I. The exact decoder dual norm then bounds the coefficient noise by n² eta/sqrt(1-q); strict half-integer margins prove simultaneous rounding. A common coordinatewise noise condition permits an identical physical assumption for both differently weighted designs.
3. **Actual covariance and variance bounds (P3-3, P3-4):** propagate the original observation covariance through the full decoder. Nested reused readings contribute a cross term. Triangle and reverse-triangle inequalities with rowwise Neumann bounds certify the target-50 variance increase.
4. **Circular Gaussian guarantee (P3-2):** derive the modulus tail from the stated proper complex density, then apply a union bound including deterministic bias. Decoded coefficients need not be independent. The variance convention is E|epsilon_j|²=sigma², not variance sigma² for each real component.

The inherited numerical tail premises are supported by [Arithmetic Sensing V](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_SENSING_V.md), especially exact continuum positivity and the all-alias log-Mellin theorem, and [the end-to-end certificate account](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_SENSING_V_END_TO_END.md). Current full remote/finite/Gram reconstruction records are separate from the fast consequence check. The [audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path3_noise/AUDIT.md) documents a repaired source-binding gap. Sensor calibration and actual decoder numerical error are outside the mathematical noise law.

### A4. Real quadratic prefixes and a constrained arithmetic query

Read [Path4 PROOF.md](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path4_realizability/PROOF.md):

1. **P4.1:** prime splitting and ideal factorization imply the exact multiplicative local coefficient rule. The converse prescribes local signs, constructs unit residues modulo 8 and the odd primes, applies CRT, then invokes Dirichlet's theorem. The chosen auxiliary prime exceeds all prescribed primes, giving a squarefree positive radicand and infinitely many distinct fields. Prime 2 and ramification are treated separately. The prefix count follows because each prefix uniquely determines its prime signs.
2. **P4.2 and P4.2-field-obstruction:** distances between compact labelled response sets give the exact deterministic noise threshold, including equality. Convex hulls preserve linear extrema but may shrink separation; a sufficient supporting-functional equality certificate and an explicit strict-gap example are proved. Multiplicativity shows why an isolated coefficient-5 envelope perturbation cannot be a quadratic-field prefix perturbation for N>=20.
3. **P4.3-tail:** verify the normalized positive physical measure, exact Gram geometry, and complete d2 arithmetic tail. The finite part covers 51 through 10000. The next part ends at 1e9 and has sine denominators uniformly separated from zero; concavity bounds all their values. Divisor summation and partial summation control the mass above both cutoffs. The final unit response bound covers all higher aliases and every remaining integer.
4. **P4.3-query:** recover the two anchors a(2),a(3), then infer a(4),a(9) and combine indices 5,20,45. Multiplicativity proves exact query normalization; the Gram dual-norm identity supplies the noise bound. All four cases and both anchors pass simultaneously for the same arbitrary noise vector.
5. **P4.3-class-separation:** the field guarantee at eta=.02001 exceeds the independent d2-envelope midpoint obstruction at .02 under exactly the same query, samples, weights, and norm. The obstructing envelope pair is not claimed to be field-realizable.

No discriminant ceiling is imposed. A finite prefix does not identify a field, even without noise. The convex-gap example itself is elementary; the actual arithmetic separation uses the later constrained-query theorem. The [independent audit](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path4_realizability/AUDIT.md) rederived the field construction, tail partition, estimator algebra, and arithmetic endpoint checks.

### A5. A wider fixed-resolution continuum-to-finite transfer

Read [Path5 APPENDIX.md](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path5_resolution/APPENDIX.md):

1. **Section 1:** define the exact n=1001, K=2 central-target finite and continuum Grams, normalization, and three source metrics. Natural discrete H1 and declared continuum H1 are whitened separately.
2. **Section 2, Theorem 1 (P5.1):** the tensor-product identity converts a product of responses into a PSD semigroup response. Spectral decay gives the k! a^-k derivative bound. Leibniz and Taylor's remainder then give the explicit normalized-Gram formula, independent of generator norm. The required nonnegative weights, unit vector norms, symmetric PSD generators, and a>0 are checked for both models.
3. **Section 3:** connect actual finite tridiagonal matrix actions and rigorous continuum quadrature to each coefficient interval. The finite exponential remainder stays in the coefficients; the distinct time-cell Taylor remainder is added afterward. The full noncommuting Laplacian-plus-potential generator is retained.
4. **Section 4 (P5.2):** freshly integrate the common core, verify rational principal minors, and derive density domination proving the inherited continuum floors for tau>=1.
5. **Section 5 (P5.3):** rational interval Horner evaluation encloses each continuous time cell. Both UI+E and UI-E pass exact robust 2-by-2 positivity tests. A direct Rayleigh inequality transfers the positive floor; exact cover topology joins [1,3/2] and [3/2,2].
6. **Section 6 (P5.5):** negative/nonnormal and unnormalized-source counterexamples locate the theorem's boundaries. Fixed finite grids decay at late time and cannot inherit a positive continuum floor on the entire half-line. Growing bandwidth, displaced targets, and minimal-grid claims are not inferred.

The [claim index](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path5_resolution/CLAIM_INDEX.md) and [validation record](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path5_resolution/VALIDATION.json) distinguish the continuous proof from small-grid and precision-refinement controls.

## B. Accepted results and remaining trusted components

| Path | Accepted mathematical inputs and checked hypotheses | Remaining implementation/premise trust |
|---|---|---|
| 1 | [Teschl, ODEs, Theorems 2.2/2.5 and 2.10–2.11](https://www.mat.univie.ac.at/~gerald/ftp/book-ode/ode.pdf): smooth local flow, uniqueness, and parameter dependence. Positive mass determinant makes the field smooth; accepted compact tubes supply finite continuation. The inverse and enclosure arguments are supplied in full. | Python integers/Fractions; [Arb arithmetic](https://arxiv.org/abs/1611.02831), series and nested differentiation implementation; the declared mechanical model. Complete replay checks the source-to-interval connection. |
| 2 | [Borsuk 1933, Satz II, printed p178](https://www.impan.pl/shop/en/publication/transaction/download/product/93008): a continuous sphere map identifies an antipodal pair. The map is continuous, odd, and padded to the required Euclidean codomain. Prime-log density, DFT bounds, local construction, and perturbation proofs are supplied rather than imported. | Python exact arithmetic; Arb logarithms, pi, elementary operations, and the local determinant. Known prime frequencies and exact rational schedule inputs. Topology is an accepted theorem, not mechanically verified. |
| 3 | The new Neumann, dual-norm, covariance, and Gaussian-tail results are proved directly. Historical [AS V Theorems A–B](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_SENSING_V.md) supply exact window positivity and the all-alias tail framework; their hypotheses are bound to the actual degree/window/grid artifacts and rebuilt. Standard Sturm/Dirichlet-convolution ingredients remain accepted in those earlier proofs. | Prior arithmetic-tail arguments; exact dyadic integer calculations; Arb finite/Gram calculations; [MPFR directed rounding](https://www.mpfr.org/mpfr-current/mpfr.html) through gmpy2 for remotes; exact source binding. The Gaussian law and coefficient envelope are assumptions, not empirical measurements. |
| 4 | [Milne ANT v3.08, Theorems 3.7 and 3.41, and Example 3.44](https://www.jmilne.org/math/CourseNotes/ANTc.pdf): ideal factorization and quadratic splitting, using the correct full ring of integers. CRT (Theorem 1.14) applies to pairwise coprime moduli. [Dirichlet's original progression theorem, translation](https://arxiv.org/abs/0808.1408), applies because the constructed residue is a unit. Compactness is required for the response-distance equality case. | Python exact arithmetic and the existing rational Sturm implementation; accepted arithmetic infinitude theorem; Arb finite-tail and Gram vectors. The light checker independently reconstructs remote log/pi/sine bounds by rational series but does not reconstruct its supplied finite vector. |
| 5 | [Axler, LADR 4e, Theorem 7.29](https://linear.axler.net/LADR4e.pdf): real spectral theorem for the symmetric finite/tensor generators. The continuum estimate is proved by bounded multiplication and scalar integration. Positivity, vector normalization, and positive time endpoints are checked. | Arb elementary arithmetic, tridiagonal coefficient actions, and [validated integration](https://arxiv.org/abs/1802.07942). The [FLINT integration contract](https://flintlib.org/doc/acb_calc.html#acb-calc-integrate) requires valid finite-path and holomorphic callback enclosures; these are checked in the proof. The continuum premise is freshly integrated, then rationally checked. |

Ball arithmetic is an inclusion contract, not a claim that a requested tolerance was achieved. Nonfinite balls fail the relevant numerical gates. Exported rational bounds and actual widths decide acceptance. All paths still trust their analytic arguments and the relevant library implementations; none claims formal proof-assistant certification. Classical ingredients and accepted theorems are attributed; new project-level applications and concrete certificates are identified in the claim index.

## C. Exact checks and full regeneration commands

Run from the repository root. The prepared session interpreter is Python 3.12.14 with python-flint 0.9.0 / FLINT 3.6.0, NumPy 2.5.2, SciPy 1.18.1, mpmath 1.4.1 and gmpy2 2.3.1. Path-local READMEs and requirements describe the subsets used. A fresh machine needs its own compatible environment; `/private/tmp` is session-local.

```sh
cd /Volumes/KINGSTON/Vibecoding/Math
FIVE_PATHS_PY=/private/tmp/math-five-paths-venv/bin/python
```

The blocks below assume that shell variable. Most checks are read-only; explicit producer commands create the indicated fresh artifacts. The older fixed-output baseline/witness and validation-record scripts regenerate their named package records. These are reproducibility operations, not discovery searches.

### C1. Path 1

Exact consequence check, then complete nominal/finite/alternate nonlinear reconstruction and controls:

```sh
python3 research/five_paths_2026_09/path1_preparation/checker.py research/five_paths_2026_09/path1_preparation/region.json research/five_paths_2026_09/path1_preparation/nominal.json
"$FIVE_PATHS_PY" research/five_paths_2026_09/path1_preparation/validate.py
```

Expected: all three designs certified and nine tests pass. The first command assumes supplied intervals; the second rebuilds them and checks every scientific/input/provenance field. An optional explicit fresh primary artifact is:

```sh
"$FIVE_PATHS_PY" research/five_paths_2026_09/path1_preparation/preparation.py --radius 1/10000 --preparation 1/10000000 --output /private/tmp/path1-region-fresh.json
```

This producer refuses an existing output. [Path1 README](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path1_preparation/README.md) provides nominal and alternate settings.

### C2. Path 2

The ordinary checker already performs complete input-to-Arb phase/local-witness reconstruction followed by exact consequences; it is not merely a stored-matrix check:

```sh
"$FIVE_PATHS_PY" research/five_paths_2026_09/path2_harmonic/certificate_checker.py
"$FIVE_PATHS_PY" -m unittest discover -s research/five_paths_2026_09/path2_harmonic -p test_certificate.py -v
"$FIVE_PATHS_PY" arithmetic_observability_full_segre.py --verify arithmetic_observability_full_segre_certificate.json
```

Expected: complete certificate verification, 15 tests, and original baseline verification. To regenerate an explicit fresh copy, including all canonical exact consequences:

```sh
"$FIVE_PATHS_PY" research/five_paths_2026_09/path2_harmonic/certificate_checker.py --write --certificate /private/tmp/path2-certificate-fresh.json
"$FIVE_PATHS_PY" research/five_paths_2026_09/path2_harmonic/certificate_checker.py --certificate /private/tmp/path2-certificate-fresh.json
```

The tests include a 512-bit replay. Optional floating schedule searches in [Path2 README](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path2_harmonic/README.md) are not proof dependencies.

### C3. Path 3

Fast exact consequences and source/decoder controls:

```sh
python3 research/five_paths_2026_09/path3_noise/check_consequences.py
"$FIVE_PATHS_PY" research/five_paths_2026_09/path3_noise/audit_checks.py
"$FIVE_PATHS_PY" research/five_paths_2026_09/path3_noise/noise_certificate.py --write /private/tmp/path3-noise-fresh.json
```

Expected: exact margins/variance/Gaussian inequalities pass and five focused controls pass. These commands rebuild the actual weights and Gram consequences, but the complete arithmetic tails require both following commands:

```sh
"$FIVE_PATHS_PY" research/five_paths_2026_09/path3_noise/rebuild_dependencies.py
"$FIVE_PATHS_PY" verify_multiscale_certificate.py --certificate certificates/arithmetic_sensing_v_multiscale_end_to_end.json --processes 4
```

The first reconstructs both MPFR remotes and the full single-window finite/Gram premise; the second reconstructs the full multiscale finite/Gram premise. Recorded fresh runtimes were approximately 394 and 417 seconds. See [Path3 README](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path3_noise/README.md). Identity hashes alone do not discharge either reconstruction.

### C4. Path 4

Exact query/remote consequences, exact finite arithmetic witnesses, and focused controls:

```sh
python3 research/five_paths_2026_09/path4_realizability/check_certificate.py
python3 research/five_paths_2026_09/path4_realizability/quadratic.py
"$FIVE_PATHS_PY" -m unittest discover -s research/five_paths_2026_09/path4_realizability -p test_query_certificate.py -v
```

Expected: radius 2001/100000 verified, 27 field witnesses regenerated, and 11 query controls pass. The witness file is a finite illustration; infinitude follows from the analytic CRT/Dirichlet proof. Full finite-tail/Gram reconstruction and precision refinement are:

```sh
"$FIVE_PATHS_PY" research/five_paths_2026_09/path4_realizability/query_certificate.py --precision 192 --output /private/tmp/path4-query-fresh.json
python3 research/five_paths_2026_09/path4_realizability/check_certificate.py /private/tmp/path4-query-fresh.json
"$FIVE_PATHS_PY" research/five_paths_2026_09/path4_realizability/query_certificate.py --precision 256 --output /private/tmp/path4-query-refinement.json
python3 research/five_paths_2026_09/path4_realizability/check_certificate.py /private/tmp/path4-query-refinement.json
```

Each producer rebuilds the defining finite d2 tails, Gram rows, positive-measure contract, and the complete remote bound. The standard-library checker independently reconstructs the remote transcendental endpoints by rational series and the query algebra, while treating the finite-tail/Gram vectors as premises. Both stages are necessary for the full numerical proof.

### C5. Path 5

Fast exact continuous-cover check and focused controls:

```sh
python3 research/five_paths_2026_09/path5_resolution/check_certificate.py
"$FIVE_PATHS_PY" -m unittest discover -s research/five_paths_2026_09/path5_resolution -p test_resolution.py -v
```

Expected: three positive uniform finite floors and 16 tests pass. Full numerical premise regeneration consists of the continuum baseline and both n=1001 cells:

```sh
"$FIVE_PATHS_PY" research/five_paths_2026_09/path5_resolution/revalidate_baseline.py
"$FIVE_PATHS_PY" research/five_paths_2026_09/path5_resolution/generate_certificate.py --interval 1 3/2 --output /private/tmp/path5-cell-1.json
"$FIVE_PATHS_PY" research/five_paths_2026_09/path5_resolution/generate_certificate.py --interval 3/2 2 --output /private/tmp/path5-cell-2.json
"$FIVE_PATHS_PY" research/five_paths_2026_09/path5_resolution/generate_certificate.py --assemble /private/tmp/path5-cell-1.json /private/tmp/path5-cell-2.json --output /private/tmp/path5-certificate-fresh.json
python3 research/five_paths_2026_09/path5_resolution/check_certificate.py /private/tmp/path5-certificate-fresh.json
```

The baseline script writes its named package record. Each full finite cell previously took approximately one minute and also validates the continuum coefficient integrals. The canonical settings are 192 bits, order 18, exponential degree 64. The [Path5 README](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path5_resolution/README.md) gives the optional 256-bit/order-20/degree-72 regeneration and `validate_refinement.py` comparison. Stored refinement evidence is supplementary to the canonical full proof and still shares Arb.

## D. Interpretation boundaries across the five paths

The results cannot be combined by carrying a guarantee across changed norms or source classes. Path2 is a finite factor-product harmonic model; Paths3–4 use complete arithmetic Dirichlet tails. Path3 recovers all 50 envelope coefficients at a tiny noise radius; Path4 recovers one constrained field query at a different radius. Path1 concerns nonlinear mechanical inverse uncertainty with actual local scalar readouts; Path5 uses a declared modal output-energy norm. Only explicitly matched comparisons inside each path are asserted.

Every promoted numerical statement has a complete inequality/proof route above. A positive certificate need not be sharp; a failed sufficient certificate is not an impossibility theorem. Exact collision examples are identified separately. The package establishes reproducible mathematical applications and finite numerical proofs; it leaves optimality, broad realizability beyond the quadratic theorem, growing-band transfer, efficient global decoding, and empirical sensor/model validation unproved.
