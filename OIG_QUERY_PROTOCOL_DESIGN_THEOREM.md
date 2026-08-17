# Exact query-directed protocol certificates

## Finite common-nuisance theorem, minimax amplification, and mixture semantics

- **Theory synthesis and implementation:** Codex (OpenAI)
- **Research programme:** Operational Information Geometry / Arithmetic Observability
- **Date:** 15 August 2026
- **Status:** exact finite-linear certificate layer; not peer reviewed

## 1. Result

The implementation `oig_query_protocol_design.py` turns the local-query theorem
of Arithmetic Observability I into a serialized, independently verifiable
certificate for exact rational finite models.  It supports:

- rational source, data, and query metrics;
- exact metric-orthogonal elimination of an unrestricted linear nuisance;
- the exact kernel test \(\ker A\subseteq\ker L\);
- an exact rational decoder factoring the query through the effective data;
- rigorous rational lower and upper bounds on the squared minimax
  amplification;
- both shared-nuisance and independently re-fit-nuisance protocol mixtures,
  with their different composition laws encoded in the report; and
- JSON-compatible reports whose theorem fields are reconstructed by a separate
  verifier.

This is a finite-dimensional real linear theorem.  It is not evidence that a
physical system, continuum model, or uncertain numerical response is described
by the declared rational matrices.  It certifies a supplied protocol mixture;
it does not claim global design optimality.

## 2. Exact nuisance quotient

Let

```text
y = H x + B z + eta
```

with source `x`, an unrestricted nuisance `z`, and data noise `eta`.  Let `S`,
`W`, and `T` be exact rational symmetric positive definite metrics on the
source, data, and query spaces.  The desired query is `Lx`.

Choose by exact row reduction any full-column-rank matrix `B0` spanning
`ran(B)`.  Define

```text
P = I - B0 (B0^T W B0)^(-1) B0^T W,
A = P H.
```

Every operation is rational.  No floating projector or numerical rank
threshold appears.  Direct multiplication proves

```text
P^2 = P,
P B = 0,
P^T W = W P.
```

Thus `P` is the `W`-orthogonal projector onto the complement of `ran(B)`, and
the exact profiled information form is

```text
G_eff = A^T W A.
```

The implementation serializes `B0`, `P`, `A`, and `G_eff`.  The verifier
rebuilds all four from the declared inputs and requires the three exact
projector decision flags.

## 3. Query identifiability and a constructive factor

### Theorem 3.1

For finite real vector spaces, the following are equivalent:

1. `Lx` is determined by `Ax`;
2. `ker(A) subset ker(L)`;
3. there is a unique map on `ran(A)` whose composition with `A` is `L`.

The implementation computes an exact rational basis of `ker(A)`.  If the
kernel condition fails, the report contains a rational witness `h` with

```text
A h = 0,    L h != 0.
```

For an unbounded source class, multiples of `h` prove infinite minimax query
error even at zero noise.

When the kernel condition holds, let `C` be the deterministic exact row basis
of `A`.  The source metric selects the minimum-cost injection

```text
J = S^(-1) C^T (C S^(-1) C^T)^(-1),
C J = I.
```

Put

```text
A_r = A J,
L_r = L J,
G   = A_r^T W A_r,
Q   = L_r^T T L_r.
```

`G` is positive definite.  The exact rational matrix

```text
D = L_r G^(-1) A_r^T W
```

satisfies

```text
D A = L,
D H = L,
D B = 0.
```

Consequently `D y` is a nuisance-invariant linear query estimator.  Although
`J` uses `S` to choose quotient coordinates, the induced decoder and minimax
amplification are coordinate-invariant.

## 4. Exact minimax amplification certificate

For data noise `||eta||_W <= epsilon`, define

```text
kappa^2 = max_(v != 0) (v^T Q v)/(v^T G v).
```

This is the squared norm of the unique query factor on `ran(A)`.  The standard
two-point argument from Arithmetic Observability I proves the exact minimax
identity

```text
inf_decoder sup_(x,z,||eta||_W<=epsilon)
    ||estimated_query - Lx||_T
  = kappa * epsilon.
```

The exact value of `kappa^2` can be algebraic rather than rational.  The report
therefore does not mislabel a floating eigenvalue as exact.  For a nonzero
identifiable query, it supplies an exact rational bracket:

```text
kappa_lower^2 <= kappa^2 < kappa_upper^2.
```

The lower bound is the exact Rayleigh quotient of a serialized nonzero rational
witness.  A floating generalized eigenvector may propose that witness, but a
coordinate Rayleigh quotient is used as an exact fallback when the declared
rationals lie outside binary64 range.  The upper bound is constructed from an
exact row-sum spectral bound, tightened by exact dyadic bisection, and accepted
only when rational LDL proves

```text
kappa_upper^2 G - Q > 0.
```

Floating generalized eigensolvers are optional witness heuristics only; they
decide no theorem field and are not required for completeness on exact rational
inputs.  For the zero query, the exact interval is `[0,0]`.

## 5. Two protocol-mixture models that must not be conflated

Let protocol `i` have response `H_i`, nuisance response `B_i`, data metric
`W_i`, positive cost `c_i`, and exact budget share `p_i`.  Its physical weight
is

```text
alpha_i = p_i/c_i.
```

Zero-weight protocols are omitted from the assembled experiment so that its
data metric remains positive definite.

### 5.1 One nuisance shared across protocols

If a single nuisance vector `z` affects every active protocol, assemble

```text
H_stack = vertical_stack(H_i),
B_stack = vertical_stack(B_i),
W_stack = block_diag(alpha_i W_i),
```

and profile `B_stack` only after assembly.  The Schur-complement term couples
the protocols.  In general,

```text
profile(sum of protocols) != sum(profile(each protocol)).
```

Therefore an optimizer that treats individually profiled information matrices
as linearly additive is not justified for this shared-nuisance model.  The API
`certify_query_protocol_mixture` certifies only the declared mixture.

### 5.2 Nuisance independently re-fit per protocol

If every protocol gets a separate nuisance parameter `z_i`, use a block
diagonal nuisance response.  The exact projector is then block diagonal and

```text
G_profiled(alpha)
  = sum_i alpha_i H_i^T W_i P_i H_i.
```

This dependence on the physical weights is linear.  Ordinary information-form
E-design is mathematically compatible with these candidate profiled forms.
The API `certify_query_independent_nuisance_mixture` serializes both the
individually profiled sum and the assembled profiled form; construction and
verification require exact equality.

No optimality claim follows merely from this equality.  A selected mixture
still needs an appropriate primal/dual design certificate before it can be
called globally optimal or near-optimal.

## 6. Strict query-directed gain

Consider

```text
H = I_3,
B = (1,1,0)^T,
S = W = I,
L = [[1,-1,0],
     [0, 0,1]],
T = I_2.
```

Exact nuisance elimination gives

```text
P = A = [[ 1/2,-1/2,0],
         [-1/2, 1/2,0],
         [ 0,   0,  1]].
```

The effective rank is two, so full recovery of the three-dimensional source
is impossible: the common mode `(1,1,0)` is blind.  Nevertheless

```text
L(1,1,0)^T = 0,
```

so the nontrivial two-dimensional query is exactly identifiable.  The exact
decoder is

```text
D = [[1,-1,0],
     [0, 0,1]],
```

and the true squared amplification is exactly `kappa^2=2`.  The implementation
finds the exact lower witness value `2` and an outward rational LDL-certified
upper bound.  This is a strict operational gain: the useful query is recovered
with finite sharp conditioning even though complete state recovery is
impossible.

A second one-dimensional example separates the two mixture semantics.  The
protocols

```text
y_1 = x + z + eta_1,
y_2 = 2x + z + eta_2
```

are individually blind after independently profiling `z`.  With equal weights
and one *shared* `z`, their difference identifies `x` and gives exactly
`kappa^2=4`.  With independent `z_1,z_2`, the exact profiled information sum is
zero and the query is unidentifiable.  Both conclusions are covered by tests.

## 7. Serialized verification boundary

`verify_query_protocol_report` independently reconstructs:

- strict JSON dimensions and model/schema choices;
- all declared exact rational matrices;
- mixture costs, budget shares, physical weights, active support, and assembly;
- the exact nuisance basis, projector, effective response, and information;
- nuisance and effective ranks;
- the kernel inclusion or its exact counterexample;
- quotient coordinates, injection, reduced forms, and exact decoder;
- all factorization and nuisance-annihilation flags;
- the rational Rayleigh lower witness; and
- the positive-definite upper shift.

Reports survive a JSON serialization round trip.  Adversarial tests mutate
projectors, ranks, kernel flags and witnesses, metrics, decoders, amplification
bounds, mixture semantics, physical weights, active support, and independent
linear-sum flags; the verifier rejects each mutation.

## 8. Public API and tests

Public names:

```text
QueryProtocol
certify_query_model
certify_query_protocol_mixture
certify_query_independent_nuisance_mixture
verify_query_protocol_report
```

Focused validation:

```text
python -m unittest -v test_oig_query_protocol_design.py
python -m unittest -v test_oig_query_protocol_design_adversarial.py
```

The suite covers exact correlated/nondiagonal metrics, identifiable partial
queries, unidentifiable witnesses, the zero-query edge case, both nuisance
mixture semantics, unequal costs, zero shares, binary-float rejection, JSON
round trips, and adversarial report mutations.  The primary suite contains
thirteen tests, and the independent adversarial suite contains ten test
methods with additional mutation subcases.

## 9. What is proved and what remains open

Proved here for the declared rational finite model:

- exact nuisance projection;
- exact local-query identifiability or an exact counterexample;
- exact factorization and a nuisance-invariant decoder;
- the minimax identity, with an exact rational bracket for its potentially
  algebraic amplification constant; and
- the correct composition law for each of the two encoded nuisance semantics.

Not proved here:

- correctness of an external numerical or physical forward model;
- continuum-to-finite transfer or interval enclosure of irrational responses;
- completeness of a candidate protocol family;
- global optimality of a chosen mixture without a separate dual certificate;
- nonlinear, constrained, integer-lattice, Bayesian, or distributionally
  robust query recovery.

The natural next integration step is to combine this exact query quotient with
the interval response-box layer, then optimize independently profiled candidate
forms for a declared query objective while retaining a dual optimality bound.
