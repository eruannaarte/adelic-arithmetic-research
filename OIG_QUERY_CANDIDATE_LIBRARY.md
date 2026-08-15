# Operational Information Geometry: Exact Finite-Library Query Design

- **Status:** proved and implemented for a declared finite library of exact
  rational query certificates
- **Date:** 2026-08-15
- **Implementation:** `oig_query_candidate_library.py`
- **Tests:** `test_oig_query_candidate_library.py`

## 1. Result

The query-directed certificate layer answers a fixed-design question:

> For this response, nuisance semantics, metric, and query, is the query
> identifiable, and what is its minimax noise amplification?

The finite-library layer turns those fixed-design certificates into a modest
but fully proved experimental-design engine. Given an explicitly declared list
of candidates, it:

1. independently verifies every embedded child certificate;
2. excludes candidates proved unidentifiable under the child model;
3. selects the identifiable candidate with the smallest certified upper bound
   on squared minimax amplification;
4. encloses the best squared minimax amplification available in the library;
5. certifies a unique winner only under a strict, exact interval separation;
6. embeds all inputs needed for standalone reconstruction.

This is finite-library design, not continuous optimization. It says nothing
about protocols or budget mixtures that were not declared.

## 2. Finite-library theorem

Let the declared library contain candidates indexed by \(i=1,\ldots,N\). For
every query-identifiable candidate, suppose the child certificate proves

\[
  0 \leq \ell_i \leq \kappa_i^2 \leq u_i,
\]

where \(\kappa_i\) is its minimax query-noise amplification. A candidate that
is not identifiable has infinite minimax loss in the child theorem's
unbounded-source model. Let \(I\) be the set of identifiable candidates.

If \(I\neq\varnothing\), define

\[
  \ell_{\mathrm{lib}}=\min_{i\in I}\ell_i,
  \qquad
  u_{\mathrm{lib}}=\min_{i\in I}u_i.
\]

Then

\[
  \ell_{\mathrm{lib}}
  \leq
  \min_{i\in I}\kappa_i^2
  \leq
  u_{\mathrm{lib}}.
\]

The proof is immediate but useful. Since
\(\ell_i\leq\kappa_i^2\) for every \(i\), taking minima preserves the lower
inequality. Choose any index attaining \(\min_i u_i\). Its true value is at
most that upper bound, proving the upper inequality.

The implementation selects

\[
  i_* = \operatorname*{arg\,min}_{i\in I}(u_i,i),
\]

where the second coordinate is declaration order and supplies a deterministic
tie break. Thus its reported upper bound is exactly
\(u_{\mathrm{lib}}\).

### Unique-winner certificate

The selector reports a unique winner only if

\[
  u_{i_*} < \ell_j
  \qquad\text{for every identifiable }j\neq i_*.
\]

Then

\[
  \kappa_{i_*}^2
  \leq u_{i_*}
  < \ell_j
  \leq \kappa_j^2,
\]

so candidate \(i_*\) strictly beats every finite competitor. If there is only
one identifiable candidate, this universal condition is vacuously satisfied;
all remaining candidates have infinite child-model loss. If any competitor
interval overlaps or touches the selected interval, the engine deliberately
withholds uniqueness.

## 3. Common comparison contract

Minimax amplifications are comparable only when they answer the same
scientific query in the same source and loss calibration. The engine therefore
requires every verified child to agree exactly on:

- source dimension;
- rational source metric;
- query dimension;
- rational query operator;
- rational query metric.

This prevents a zero query, a rescaled query loss, or a lower-dimensional task
from appearing to beat a candidate that solves a different problem. A mixed
library is rejected before any selection is made.

The serialized contract also states the noise-radius convention. For every
candidate \(i\), the same numerical \(\epsilon\) bounds
\(\lVert\eta_i\rVert_{W_i}\), where \(W_i\) is that candidate's declared and
verified output metric; query error is measured in the common query metric.
Candidate-specific output metrics remain permissible because they encode the
calibrated noise and budget model of each design. Their calibration is a model
declaration, not something this finite algebraic layer can establish from raw
physical data.

The common contract is embedded in the report and reconstructed by the
standalone verifier. Nuisance semantics and observation dimensions may differ
across candidates, because those are properties of the competing experimental
designs rather than of the task being compared.

## 4. Candidate semantics remain local

A library may combine all three child certificate types:

- one finite experiment with one unrestricted nuisance space;
- a protocol mixture with one nuisance vector shared across active protocols;
- a protocol mixture whose nuisance is independently re-fit in each active
  protocol.

The finite selector never reinterprets these models. Each child report carries
its own exact response, metrics, nuisance construction, factorization, and
proof boundary. In particular, a shared-nuisance mixture is not silently
replaced by an independent-refit information sum.

This matters even in one dimension. If two protocols observe

\[
  y_1=x+z+\eta_1,
  \qquad
  y_2=2x+z+\eta_2,
\]

then their difference identifies \(x\) when the same \(z\) is shared. If each
protocol gets its own freely re-fit nuisance, neither observation constrains
\(x\). The library engine verifies and compares those distinct conclusions
without conflating them.

## 5. Exact report structure

The schema is

```text
oig-query-candidate-library-certificate-v1
```

Every candidate row contains:

- a declaration-order index and unique name;
- the complete sealed child query certificate;
- the freshly reconstructed child-verifier result;
- one of three classifications:
  - `identifiable-finite-loss`,
  - `identifiable-zero-query`,
  - `unidentifiable-infinite-loss`;
- canonical rational lower and upper strings, or `null` for an unidentifiable
  candidate.

The selection block contains:

- the deterministic winner, if one exists;
- the exact finite-library lower and upper bounds;
- an exact comparison against every other identifiable candidate;
- the uniqueness decision and its stated basis.

The common-comparison block contains the exact source/query declarations, the
shared numerical-noise-radius convention, and exact verification flags. It is
the contract under which the numeric candidate ordering has meaning.

All theorem-bearing scalar values use canonical `numerator/denominator`
strings. Any floating values nested inside a child query certificate are
descriptive displays inherited from that child and are not used by the
library theorem or verifier.

If every candidate is unidentifiable, the outcome is
`no-identifiable-candidate`; the winner and finite rational bounds are `null`.

## 6. Standalone verification

`verify_query_candidate_library_report` needs only the serialized report. It
performs the following reconstruction:

1. enforce the exact top-level schema, including the absence of surplus
   fields;
2. re-run the standalone verifier for every embedded child certificate;
3. extract every source/query declaration and enforce the exact common
   comparison contract;
4. recover each exact rational interval from the verified child theorem;
5. reconstruct classifications and finite eligibility;
6. recompute both library minima and the declaration-order selection;
7. recompute every strict uniqueness comparison;
8. compare the reconstructed report with the serialized report using
   type-strict JSON equality;
9. verify the embedded independent-verification block.

Consequently, changing a candidate response, a child theorem field, a library
bound, the selected index, the uniqueness flag, or the verification block
invalidates the certificate.

## 7. Python interface

Previously sealed reports can be named directly:

```python
from oig_query_candidate_library import (
    QueryCandidate,
    certify_query_candidate_library,
    verify_query_candidate_library_report,
)

candidate = QueryCandidate.from_report("baseline", child_report)
report = certify_query_candidate_library([candidate])
assert verify_query_candidate_library_report(report)["passed"]
```

The convenience factories construct and seal exact child specifications:

```python
candidate = QueryCandidate.single_model(
    "gain two",
    [[2]],       # response
    None,        # no nuisance
    [[1]],       # source metric
    [[1]],       # output metric
    [[1]],       # query
    [[1]],       # query metric
)
```

`QueryCandidate.shared_mixture(...)` and
`QueryCandidate.independent_mixture(...)` accept the corresponding exact
`QueryProtocol` list and rational budget shares. For compact programmatic use,
the main entry point also accepts `(name, sealed_child_report)` tuples.

Binary floating declarations remain forbidden by the child certificate APIs.
The library selector itself uses only exact `Fraction` comparisons. A test with
a response gain of \(10^{400}\) exercises the path beyond binary64 range.

## 8. Demonstrated edge cases

The focused suite proves the implementation behavior for:

- a strict winner among two identifiable designs and one unidentifiable design;
- exact recovery of the finite-library bracket;
- tied upper bounds with deterministic selection but no uniqueness claim;
- one and multiple zero-query candidates;
- rejection of a zero-query candidate mixed with a nonzero-query task;
- rejection of source-dimension, query-dimension, source-metric, query, and
  query-metric mismatches;
- a single identifiable candidate among blind alternatives;
- an all-unidentifiable library;
- shared-nuisance versus independent-refit semantics;
- direct composition of an existing sealed report;
- JSON serialization and standalone verification;
- exact rationals outside floating-point range;
- duplicate names, malformed inputs, invalid children, missing verification,
  type confusion, surplus fields, and theorem-field tampering.

## 9. Reproduction

From the repository root:

```bash
python -m unittest -v test_oig_query_candidate_library.py
python -m unittest -v test_oig_query_candidate_library_adversarial.py
```

The primary suite contains fifteen tests and the independent adversarial suite
contains four comparability controls. Neither requires network access.

## 10. Boundary and next extension

The result is intentionally narrow. It does **not** prove:

- optimality over a continuous budget simplex;
- completeness of the candidate library;
- validity of an external continuum or physical forward model;
- robustness to model uncertainty beyond what an embedded child certificate
  actually proves;
- physical correctness of the declared candidate-specific output-metric
  calibration merely because it is algebraically well formed.

The engine now enforces exact equality of the query, query metric, source
metric, dimensions, and stated noise-radius convention. The workflow remains
responsible for grounding those declarations and each output metric in a
scientifically meaningful calibration. The natural next step is to compose
this finite selector with the
structured-nuisance and model-uncertainty certificates, retaining separate
proof obligations for query identifiability, bounded nuisance separation, and
robustness of the declared model family.
