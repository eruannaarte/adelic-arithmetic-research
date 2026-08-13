# Stage 9 Research Plan: Arithmetic Sensing

**Status:** first and deterministic-continuation theorem targets completed,
2026-08-12. The random-time theory is developed in `ARITHMETIC_SENSING.md`.
`ARITHMETIC_SENSING_II.md` replaces the random design by an exact Hann
midpoint quadrature, proves an alias-safe complete-tail certificate, and adds
explicit quantitative and number-field nonidentifiability results.

## Research question

How many noisy aggregate measurements are needed to recover a specified amount
of local arithmetic structure, and which arithmetic distinctions are destroyed
by aggregation before any algorithm sees the data?

This combines the adelic program with information science. Stage 8 supplied a
finite log-Fourier inverse, empirical conditioning thresholds, an omitted-tail
failure, and an exact class-group collision between real and integral geometry.
Stage 9 will turn those observations into quantitative recovery and
impossibility theorems.

## First theorem target

Let

`y_j = sum_(n<=N) a_n n^(-sigma-it_j) + r_j + eta_j`,

where `eta` is measurement noise and `r` is the contribution of the omitted
Dirichlet tail. For the random-time design matrix `A`, prove a bound of the form

`||a_hat-a|| <= C(sigma,N,T,m,delta) (||eta|| + ||r||)`

with probability at least `1-delta`, followed by an integer-recovery corollary
when every coefficient error is below `1/2`.

**Result:** completed. The final theorem is coefficientwise and sharper than
the originally proposed global norm inequality. It separates population tail
bias from finite-sample tail fluctuation as well as from Gaussian measurement
noise. A universal quadratic-field instance certifies exact rounding for
`N=50`, `sigma=2`, `T=10,000`, and 500,000 samples.

The bound must expose three independently testable quantities:

1. the smallest singular value or an appropriate restricted singular value;
2. the stochastic measurement-noise budget;
3. an analytic upper bound for the omitted Dedekind tail.

## Work packages

### 1. Random log-Fourier conditioning

- Derive the expected Gram kernel for times uniform on `[0,T]`.
- Bound off-diagonal entries using frequency gaps `|log n-log m|`.
- Compare Gershgorin/coherence bounds with matrix concentration bounds.
- Identify how `T`, sample count, and `N` must scale for stable inversion.
- Test whether arithmetic clustering creates sharper or worse behavior than a
  generic separated-frequency model.

### 2. Analytic tail control

- Begin with nonnegative coefficient classes and known growth envelopes.
- Bound `sum_(n>N) a_n n^(-sigma-it)` uniformly in time.
- Separate deterministic worst-case bounds from average-time cancellation.
- Jointly estimate a low-dimensional nuisance tail when a worst-case bound is
  too pessimistic.

### 3. Information-theoretic impossibility

- Construct coefficient sequences or number-field examples whose sampled
  traces are indistinguishable within a prescribed noise radius.
- Use two-point testing first; introduce Fano or Le Cam bounds only when the
  model family justifies them.
- Distinguish sampling failure from structural aggregation failure.
- Treat “same ideal counts, different principal relations” as a model case.

**Result:** first layer completed. The normalized integer Dirichlet
polynomials `1+50^-s` and `1+51^-s` give a computed two-ball ambiguity radius.
Perlis' nonisomorphic degree-eight fields with equal Dedekind zeta functions
give an exact structural collision: aggregate zeta data cannot identify the
field, even when complete and noiseless.

### 4. Higher-rank unit lattices

- Recover an unlabelled rank-`r` lattice only up to `GL_r(Z)`.
- Identify primitivity through saturation or Smith normal form.
- Quantify basis ambiguity and noise stability using successive minima.
- Start with a totally real cubic field of unit rank two after independently
  validating its exact arithmetic data.

### 5. Larger class groups

- Select one cyclic class group of order greater than two and one noncyclic
  example.
- Build exact principal-divisor matrices on controlled prime-ideal supports.
- Recover their torsion quotients by Smith normal form.
- Determine the minimum principal-relation data needed beyond aggregate ideal
  counts.

## Falsification criteria

The first approach should be rejected or revised if:

- random-time matrices remain exponentially ill-conditioned in the proposed
  scaling regime;
- available tail bounds swamp the integer-separation threshold;
- the claimed arithmetic prior is merely equivalent to supplying the unknown
  coefficients;
- higher-rank recovery depends on an unreported preferred basis;
- numerical success disappears under held-out seeds or modest cutoff changes.

## Recommended order

1. Prove the deterministic noise-plus-tail perturbation lemma.
2. Compute the exact expected random-time Gram kernel.
3. Seek a finite-`N` probability bound and test its constants.
4. Add a quadratic Dedekind-tail envelope and rerun Stage 8 inversion.
5. Construct a matching or near-matching indistinguishability example.
6. Only then begin the higher-rank and larger-class-group laboratories.

The local machine should suffice for theorem discovery and moderate Monte
Carlo work. The accessible Windows machine becomes useful for large parameter
sweeps after the design and falsification criteria are fixed.
