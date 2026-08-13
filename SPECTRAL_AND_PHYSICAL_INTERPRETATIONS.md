# Spectral and Physical Interpretations

## Stage 6 of the order–factorization and adelic-geometry program

**Status:** completed first spectral and noisy-recovery layer, 2026-08-12.
The prime-mode partition identities, Tate local factors, and number-field ideal
spectra are classical or elementary reformulations of classical facts. The
finite observability experiments are new computations within this workspace,
not general recovery theorems. No claim about the Riemann zeros or new physics
is made.

## Abstract

Prime factorization has a canonical occupation-number representation. Assign
one bosonic mode to each prime `p`, occupation `k_p=v_p(n)`, and energy
`log p`. The total energy of the state representing `n` is then

`sum_p v_p(n) log p=log n`.

For a finite prime set `S`, the heat trace factorizes exactly:

`Tr exp(-s H_S)=product_(p in S) (1-p^(-s))^(-1)`.

This is not merely suggestive notation. With multiplicative Haar measure
normalized by `vol(Z_p^x)=1`, the local trace is precisely Tate's local shell
integral

`integral_(Q_p^x) 1_(Z_p)(x)|x|_p^s d^x x`.

The Archimedean Gaussian supplies the gamma factor. Thus the finite Fock tensor
product, the `p`-adic valuation shells, and the Euler factors are three views of
the same local object.

The construction extends to prime ideals of a number field. Splitting becomes
mode multiplicity, inertia changes the mode energy through the residue degree,
and ramification appears in the divisor relation rather than as a repeated
Euler mode.

Finally, a finite noisy experiment asks whether an unknown sparse set of active
prime modes can be inferred from time samples. Recovery succeeds only after the
observation window and sample count resolve the crowded logarithmic
frequencies. This gives the program a falsifiable inverse problem while also
exposing its limitations.

## 1. The arithmetic Fock space

Fix a finite set of primes `S`. Define

`H_Space=Hilbert tensor product_(p in S) l^2(N_0)`.

Its standard basis is indexed by occupation vectors

`k=(k_p)_(p in S)`, `k_p>=0`.

Define number operators `N_p|k>=k_p|k>` and the Hamiltonian

`H_S=sum_(p in S) (log p) N_p`.                            (1)

### Theorem A (finite prime-mode spectral dictionary)

The map

`|k> -> n(k)=product_(p in S) p^(k_p)`

is a bijection from the Fock basis to the positive `S`-smooth integers. Under
this bijection:

1. `H_S|k>=log(n(k))|k>`;
2. for `Re(s)>0`,

   `Tr exp(-s H_S)=product_(p in S)(1-p^(-s))^(-1)`;       (2)

3. the time evolution is

   `exp(-it H_S)|n>=n^(-it)|n>`.

#### Proof

Unique factorization gives the basis bijection. Equation (1) yields

`sum_p k_p log p=log product_p p^(k_p)=log n(k)`.

Since `S` is finite and `Re(s)>0`, the trace is absolutely convergent and
separates into geometric series:

`sum_k exp(-s sum_p k_p log p)`

`=product_p sum_(k_p>=0) p^(-s k_p)`

`=product_p (1-p^(-s))^(-1)`.

The time-evolution formula follows from the same eigenvalue identity. QED.

### Infinite prime limit

Taking all primes identifies the basis with every positive integer, so the
Hamiltonian on `l^2(N)` is

`H|n>=log n |n>`.

It is a positive self-adjoint diagonal operator with compact resolvent. Its
heat operator is trace class exactly for real `beta>1`, where

`Tr exp(-beta H)=sum_(n>=1)n^(-beta)=zeta(beta)`.           (3)

The spectral counting function is

`N_H(E)=#{n:log n<=E}=floor(exp(E))`.

Thus the pole at `beta=1` reflects exponential state growth. This is a valid
statistical-mechanical encoding, but its spectrum is `log n`, not the
ordinates of the Riemann zeros.

## 2. The local adelic meaning of one mode

Normalize multiplicative Haar measure on `Q_p^x` by

`vol(Z_p^x,d^x x)=1`.

Then

`Z_p={0} disjoint_union union_(k>=0) p^k Z_p^x`,

and the singleton `{0}` has measure zero. Every multiplicative shell has
volume one, while `|x|_p=p^(-k)` on `p^k Z_p^x`.

### Theorem B (prime mode equals a Tate shell integral)

For `Re(s)>0`,

`integral_(Q_p^x) 1_(Z_p)(x)|x|_p^s d^x x`

`=sum_(k>=0)p^(-ks)`

`=(1-p^(-s))^(-1)`                                        (4)

`=Tr_(l^2(N_0)) exp(-s(log p)N_p)`.

#### Proof

Integrate shell by shell. The normalized shell measure is one and the
integrand is constant `p^(-ks)` on the `k`th shell. Absolute convergence for
`Re(s)>0` permits summation, giving the geometric series. The last equality is
the one-mode case of Theorem A. QED.

This provides the cleanest spectral–adelic bridge in the project:

| description | local coordinate | weight |
|---|---|---|
| prime factorization | `v_p(n)=k` | `p^(-ks)` |
| bosonic mode | occupation `N_p=k` | `exp(-s k log p)` |
| `p`-adic geometry | shell `p^k Z_p^x` | `|x|_p^s=p^(-ks)` |

These are not three numerical coincidences; the same valuation labels all
three.

### The Archimedean place

At infinity, with `d^x x=dx/|x|` and Gaussian

`f_infinity(x)=exp(-pi x^2)`,

direct substitution gives

`integral_(R^x) f_infinity(x)|x|^s d^x x`

`=pi^(-s/2) Gamma(s/2)`.                                  (5)

Combining (4) over all finite primes with (5) yields the standard Tate zeta
integral

`pi^(-s/2) Gamma(s/2) zeta(s)`

in its initial half-plane of convergence. The gamma factor comes from the real
Gaussian; the Euler factors come from finite valuation shells.

The functional equation is not forced by the prime-mode trace alone. It arises
after the global test function is placed on the adeles and Poisson summation
relates it to its Fourier transform, as developed in Stage 3.

## 3. Twists, fermions, and the prime-power signal

### Twisted traces

Let `chi` be completely multiplicative on the selected primes, with
`|chi(p)|<=1`. Put a diagonal contraction on the occupation basis:

`T_chi|k>=product_p chi(p)^(k_p)|k>`.

Then

`Tr(T_chi exp(-sH_S))`

`=product_(p in S)(1-chi(p)p^(-s))^(-1)`.                 (6)

For a Dirichlet character this is the finite Euler product of its `L`-function.
The twist supplies phase data that order rigidity alone cannot determine.

### Fermionic variants

Restrict every occupation to `k_p in {0,1}`. The basis is then indexed by
square-free `S`-smooth integers, and

`Tr_F exp(-sH_S)=product_p(1+p^(-s))`

`=Z_S(s)/Z_S(2s)`.                                        (7)

The parity supertrace is

`Str_F exp(-sH_S)=product_p(1-p^(-s))=1/Z_S(s)`.          (8)

These are exact finite identities. In the infinite system their direct trace
meaning is confined to a convergence half-plane; analytic continuation does
not automatically remain a Hilbert-space trace.

### Thermodynamic prime powers

For real `beta>0` and finite `S`, logarithmic differentiation of (2) gives

`-d/d beta log Z_S(beta)`

`=sum_(p in S) log(p)/(p^beta-1)`

`=sum_(p in S) sum_(k>=1) log(p)p^(-k beta)`.              (9)

The canonical mean energy is therefore supported on prime powers. Equation
(9) is the finite Euler-product logarithmic derivative, equivalently the
finite von Mangoldt signal divided by its integer arguments to the power
`beta`.

The energy variance is

`d^2/d beta^2 log Z_S(beta)`

`=sum_p (log p)^2 p^beta/(p^beta-1)^2>0`.                 (10)

The implementation verifies truncated versions of (4) and (9) with explicit
geometric tail bounds.

## 4. Number fields: prime splitting becomes spectral branching

For a number field `K`, replace positive integers by nonzero integral ideals.
On `l^2({nonzero integral ideals})`, define

`H_K|a>=log N(a)|a>`.

Unique factorization of ideals gives

`Tr exp(-sH_K)=product_P(1-N(P)^(-s))^(-1)=zeta_K(s)`      (11)

for `Re(s)>1`.

For a rational prime `p`, the energy of a prime ideal `P|p` is

`log N(P)=f_P log p`,

where `f_P` is its residue degree. Consequently:

- a split quadratic prime gives two modes of energy `log p`;
- an inert quadratic prime gives one mode of energy `2 log p`;
- a ramified quadratic prime gives one mode of energy `log p`.

The ramification index occurs in

`(p)=product_(P|p) P^(e_P)`,

but the Dedekind Euler product has one factor per prime ideal, not one per
ramification multiplicity.

At `s=2`, the exact laboratory factors include:

| field | prime behavior | exact local factor |
|---|---|---:|
| `Q(i)` | `2` ramified | `4/3` |
| `Q(i)` | `3` inert | `81/80` |
| `Q(i)` | `5` split | `(25/24)^2` |
| `Q(sqrt(5))` | `2` inert | `16/15` |
| `Q(sqrt(5))` | `5` ramified | `25/24` |
| `Q(sqrt(5))` | `11` split | `(121/120)^2` |

### The unit obstruction

The prime-ideal occupation labels have no explicit unit modes because
`(u)=O_K` and `|N(u)|=1`. If one
instead labels states by algebraic integers, unit multiples have the same norm
energy. In a real quadratic field the infinite unit group creates infinite
zero-cost degeneracy and the naive trace diverges.

This is structurally informative: ideal space has already quotiented out the
unit lattice. The analytic residue of a Dedekind zeta function can encode the
regulator in combination with the class number and other field invariants, but
the regulator is not present as a visible unit-lattice spacing in the local
prime-ideal modes. Recovering that geometry directly requires an additional
Archimedean observable, a quotient/fundamental domain, or an idele-class
dynamics.

## 5. Finite, noisy, sparse prime-mode recovery

The one-particle subspace of a finite candidate system has basis `|p>`, with

`H_1|p>=log p |p>`.

For an initial sparse vector `|psi>=sum_p a_p|p>` and an observation vector
that couples equally to the candidate modes, the measured complex signal is

`y(t_j)=sum_p a_p exp(-i t_j log p)+eta_j`.                (12)

The experiment supplies candidate frequencies `log p`, draws randomized
observation times, adds complex Gaussian noise, and uses Orthogonal Matching
Pursuit (OMP) to infer the active support.

This is a deliberately modest inverse problem. It does not discover the prime
dictionary from no assumptions. Standard OMP theorems for random Gaussian or
Bernoulli measurement matrices do not directly apply to this random-time
log-prime Vandermonde dictionary.

### Crowded-mode test

The candidates are the 25 primes through `97`; the four active modes are

`73,79,83,89`.

Their smallest candidate log-frequency gap is approximately

`0.0277796`.

All trials below use complex noise standard deviation `0.02` and 64 randomized
samples. The “resolution proxy” is `2*pi/T`; it is a guide, not a recovery
theorem.

| window `T` | `2*pi/T` | mean coherence | exact recoveries |
|---:|---:|---:|---:|
| 5 | 1.2566 | 0.9992 | 0/40 |
| 15 | 0.4189 | 0.9930 | 0/40 |
| 40 | 0.1571 | 0.9490 | 0/40 |
| 100 | 0.0628 | 0.7222 | 35/40 |
| 250 | 0.0251 | 0.3030 | 40/40 |

The transition tracks dictionary decorrelation. It is not simply a noise
effect: with a short window the neighboring exponentials are nearly the same
measurement vector.

### Sample-count test at `T=250`

| samples | mean coherence | exact recoveries |
|---:|---:|---:|
| 8 | 0.7991 | 5/40 |
| 12 | 0.6586 | 25/40 |
| 16 | 0.5762 | 35/40 |
| 24 | 0.4713 | 40/40 |
| 32 | 0.4174 | 40/40 |
| 64 | 0.3036 | 40/40 |

### Noise test at `T=250`, 64 samples

| noise standard deviation | exact recoveries | mean relative coefficient error |
|---:|---:|---:|
| 0 | 40/40 | `<10^-15` |
| 0.02 | 40/40 | 0.0023 |
| 0.1 | 40/40 | 0.0120 |
| 0.5 | 40/40 | 0.0647 |
| 2.0 | 38/40 | 0.2664 |
| 4.0 | 5/40 | 0.8851 |

Regular time grids can create exact aliases despite a long total window. The
experiment therefore randomizes sample times. Every percentage above is a
finite seeded Monte Carlo result, not a probability bound.

## 6. What is physically meaningful?

### Mathematically controlled interpretations

1. **Independent local modes.** Euler factorization is exactly tensor-product
   factorization of noninteracting occupation modes.
2. **Valuation energy.** The logarithmic Hamiltonian is additive because
   valuations and logarithms turn multiplication into addition.
3. **Locality by place.** Each finite place contributes one geometric heat
   trace; the real place contributes a Mellin/Gaussian factor of a different
   analytic kind.
4. **Prime-power response.** Thermodynamic differentiation exposes repeated
   occupation of individual prime modes.
5. **Splitting spectroscopy.** Over a number field, local mode multiplicity and
   energy distinguish split, inert, and ramified behavior in the quadratic
   examples.

### Engineering interpretation

A bank of oscillatory modes with frequencies proportional to `log p` could
encode multiplicative data additively. Sparse spectral measurements could then
identify which preconfigured prime channels are active. This is a possible
signal-processing architecture, not evidence that nature already implements
it.

The absolute physical energy scale is undetermined. Replacing (1) by

`H_physical=kappa sum_p (log p)N_p`

changes only the dimensionless combination `s=beta*kappa`. Order and
factorization select relative logarithmic energies, not the constant `kappa`,
the particles, the coupling mechanism, or a laboratory platform.

## 7. Why this does not solve the Riemann hypothesis

Several sharp obstructions prevent overinterpretation.

1. **Wrong spectrum.** The eigenvalues are `log n`, whereas a Hilbert–Pólya
   program seeks an independently defined self-adjoint operator whose
   eigenvalues are zero ordinates.
2. **Heat trace versus analytic continuation.** Equation (3) is a trace only
   for `Re(s)>1`. Its meromorphic continuation into the critical strip is not
   supplied by the trace-class operator.
3. **No zeros in the direct Euler region.** Every local bosonic factor is
   nonzero for `Re(s)>0`, and the infinite Euler product is nonzero where it
   converges absolutely.
4. **Encoding is cheap.** A diagonal Hamiltonian can be manufactured from many
   prescribed Dirichlet series. Reproducing a partition function is much
   weaker than deriving its analytic continuation or zero set.
5. **No prime-orbit dynamics.** This construction has independent occupation
   modes, not a chaotic classical dynamics whose periodic orbits explain the
   explicit formula.
6. **No functional equation from the Hamiltonian.** The functional equation
   enters through global Fourier duality and Poisson summation, additional
   structure external to the diagonal Fock trace.

The Bost–Connes system is a much richer quantum statistical system: beyond a
zeta partition function, it has a noncommutative observable algebra, arithmetic
symmetry, KMS states, and symmetry breaking. The present Fock model isolates
the elementary local factor mechanism and should not be presented as a new
Bost–Connes construction.

Berry and Keating's spectral analogy instead asks for unknown chaotic dynamics
whose periods involve multiples of logarithms of primes. Merely installing
`log p` as oscillator frequencies assumes the arithmetic data rather than
deriving such dynamics.

## 8. Falsifiable hypotheses for the next stage

### H1 — sparse observability is controlled by log-frequency geometry

For a fixed candidate dictionary and sparsity, recovery should improve as
randomized time samples lower the mutual coherence; nearby large primes should
be the hardest modes because `log q-log p` is small.

This is supported by the Stage 6 experiment. A theorem would require recovery
bounds for this structured random-time matrix, not an import of Gaussian-matrix
OMP results.

### H2 — splitting can be inferred from local spectral branching

Given rational-prime labels and sufficiently resolved prime-ideal heat data,
the pattern

`two modes at log p / one mode at 2log p / one mode at log p`

should distinguish split/inert/ramified behavior in quadratic fields. Tests
should add noise and overlapping modes from many rational primes.

### H3 — direct unit-lattice recovery requires an Archimedean channel

Prime-ideal occupation labels do not exhibit the real-quadratic unit lattice,
because unit multiplication is invisible to ideals. Adding the logarithmic
embedding of units should make the regulator directly recoverable as a lattice
spacing or covolume. This claim concerns geometric identification, not the
analytic class-number formula, where a zeta residue contains a product
involving the regulator. Failure of the augmented measurement would falsify
the proposed inverse construction.

### H4 — factorization is equivalent to absence of cross-mode interaction

If a Hamiltonian contains genuine terms such as

`J_pq N_p N_q`,

its partition function generally stops factoring into Euler factors. Measuring
mixed cumulants therefore provides a direct test of whether an implemented
system realizes independent arithmetic modes or only approximately imitates
them.

### H5 — finite rigidity backbones are sparse calibration experiments

The exact Stage 5 dual certificates identify small sets of comparisons that
determine narrow prime-energy ratios. They can be reinterpreted as sparse
calibration protocols for an imperfect logarithmic mode bank. Robust versions
should quantify how certificate error propagates under noisy order data.

## 9. Reproduction

```text
python3 spectral_adelic_system.py --prime-limit 19 --sigma 2 --maximum-shell 12
python3 number_field_spectral_system.py --primes 2 3 5 11 --sigma 2

python sparse_prime_mode_recovery.py \
  --prime-limit 97 --active-primes 73 79 83 89 \
  --samples 64 --noise 0.02 --trials 40

python -m unittest discover -v
```

The finite Euler products at integral `s`, ideal factorizations, and occupation
labels are checked exactly. Complex traces and noisy recovery use floating
point. Local shell and prime-power truncations carry analytic geometric tail
bounds.

## 10. Sources and novelty boundary

The local zeta integrals, restricted products, Fourier normalization, and
Poisson mechanism are classical and follow [J. Tate, *Fourier Analysis in
Number Fields and Hecke's Zeta-Functions*
(1950)](https://sites.math.rutgers.edu/~alexk/2023S572/Tate1950.pdf).

The primary precedent for a number-theoretic quantum statistical system with
Riemann-zeta partition function and arithmetic symmetry is [J.-B. Bost and A.
Connes, *Hecke Algebras, Type III Factors and Phase Transitions with
Spontaneous Symmetry Breaking in Number Theory*
(1995)](https://repo-archives.ihes.fr/FONDS_IHES/I_Prepublications/CONNES/1994-1998/M_95_38/M_95_38.pdf).

The contrast with a genuine zero-spectrum program is informed by [M. Berry and
J. Keating, *The Riemann Zeros and Eigenvalue Asymptotics*
(1999)](https://epubs.siam.org/doi/10.1137/S0036144598347497), which describes
an unknown Hermitian operator/chaotic-dynamics analogy and prime-logarithmic
periodic-orbit structure.

OMP and its random-measurement recovery theory are due to work including [J.
Tropp and A. Gilbert, *Signal Recovery From Random Measurements Via Orthogonal
Matching Pursuit*
(2007)](https://authors.library.caltech.edu/records/hg25b-hf247). Its Gaussian
and Bernoulli guarantees are cited as methodological background, not claimed
for the structured matrix tested here.

The elementary Fock identities and finite noisy experiments are supplied as an
auditable bridge among those established subjects. No literature-priority
claim is made.
