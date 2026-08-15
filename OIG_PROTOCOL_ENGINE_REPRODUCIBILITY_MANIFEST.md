# Operational Information Geometry protocol engine — reproducibility manifest

## Release identity

- **Repository:** `https://github.com/eruannaarte/adelic-arithmetic-research`
- **Publication branch:** `codex/oig-finite-transfer`
- **Canonical research commit:** `4061270`
- **Prepared:** 15 August 2026
- **Status:** proved within the declared finite and continuum models; not peer
  reviewed

The canonical research commit contains the Arithmetic Observability Atlas
integration. A later packaging commit may add this manifest and the dedicated
dependency file without changing the theorem code or reference certificate.

## Supported runtime

- Python 3.11 or newer
- NumPy 2.2 or newer, below 3
- SciPy 1.15 or newer, below 2
- mpmath 1.3 or newer, below 2
- gmpy2 2.2 or newer, below 3
- python-flint 0.9.x

The full dependency declaration is
`oig_protocol_engine_requirements.txt`. The release was validated with Python
3.12.9, NumPy 2.4.6, SciPy 1.15.2, mpmath 1.3.0, gmpy2 2.3.1, and
python-flint 0.9.0.

NumPy and SciPy support the finite response and generalized-eigenvalue
calculations. python-flint supplies Arb interval arithmetic for the outward
certificates. mpmath and gmpy2 are retained because the complete protocol
engine release includes the high-precision and exact-arithmetic precursor
certificate layers referenced by the canonical manuscript.

## Clean installation

```bash
git clone https://github.com/eruannaarte/adelic-arithmetic-research.git
cd adelic-arithmetic-research
git checkout codex/oig-finite-transfer
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r oig_protocol_engine_requirements.txt
```

On Windows PowerShell, replace the activation command with:

```powershell
.venv\Scripts\Activate.ps1
```

## Canonical manuscripts

- `OPERATIONAL_INFORMATION_GEOMETRY_PROTOCOL_ENGINE.md` — public narrative
  authority
- `OIG_ARITHMETIC_ATLAS_PROTOCOL_INTEGRATION.md` — Atlas-to-engine synthesis
- `OIG_PROTOCOL_DESIGN_ENGINE.md` — exact quotient and E-design kernel
- `OIG_QUERY_PROTOCOL_DESIGN_THEOREM.md` — query recovery and nuisance
  profiling
- `OIG_QUERY_CANDIDATE_LIBRARY.md` — finite common-contract selection
- `OIG_STRUCTURED_NUISANCE_THEOREM.md` — correlated zonotope separation
- `OIG_ROBUST_MODEL_AWARE_QUOTIENT.md` — model secants, tangents, tubes, and
  nominal-null rules
- `OIG_UNIFORM_LATTICE_TRANSFER_THEOREM.md` — resolution-aware finite transfer
- `OIG_UNIFORM_LATTICE_EXPLICIT_CONSTANTS.md` — global analytic schedules
- `oig_uniform_lattice_arb_cover.md` — practical compact interval certificate

The corresponding adversarial audit authorities are:

- `OIG_PROTOCOL_ENGINE_ADVERSARIAL_AUDIT.md`
- `OIG_INTERVAL_PROTOCOL_DESIGN_AUDIT.md`
- `OIG_QUERY_PROTOCOL_DESIGN_ADVERSARIAL_AUDIT.md`
- `OIG_STRUCTURED_ROBUST_INTEGRATION_ADVERSARIAL_AUDIT.md`
- `OIG_UNIFORM_LATTICE_ADVERSARIAL_AUDIT.md`

## Proof-producing programs

- `oig_protocol_design_engine.py`
- `oig_interval_protocol_design.py`
- `oig_query_protocol_design.py`
- `oig_query_candidate_library.py`
- `oig_structured_nuisance.py`
- `oig_robust_model_quotient.py`
- `oig_robust_model_quotient_demo.py`
- `oig_atlas_protocol_integration.py`
- `oig_neumann_matched_frame.py`
- `oig_hidden_network_protocol_demo.py`
- `oig_uniform_lattice_transfer.py`
- `oig_uniform_lattice_arb_cover.py`

## Reference certificates

- `certificates/oig_atlas_protocol_integration.json`
- `certificates/oig_hidden_protocol_design.json`
- `certificates/oig_neumann_matched_frame.json`
- `certificates/oig_uniform_lattice_arb_cover.json`

Exact rational fields and Arb intervals are authoritative. Displayed decimal
summaries are included for readability and must not replace the exact fields
in a theorem decision.

## Focused validation

```bash
python -m unittest -v \
  test_oig_protocol_design_engine.py \
  test_oig_protocol_engine_adversarial_controls.py \
  test_oig_interval_protocol_design.py \
  test_oig_interval_protocol_design_adversarial.py \
  test_oig_neumann_matched_frame.py \
  test_oig_query_protocol_design.py \
  test_oig_query_protocol_design_adversarial.py \
  test_oig_query_candidate_library.py \
  test_oig_query_candidate_library_adversarial.py \
  test_oig_structured_nuisance.py \
  test_oig_structured_nuisance_adversarial.py \
  test_oig_robust_model_quotient.py \
  test_oig_robust_model_quotient_adversarial.py \
  test_oig_atlas_protocol_integration.py \
  test_oig_atlas_protocol_integration_adversarial.py
```

Verify the committed end-to-end report independently:

```bash
python oig_atlas_protocol_integration.py \
  --verify certificates/oig_atlas_protocol_integration.json
python -m unittest -v test_oig_protocol_artifacts.py
```

The compact Arb certificate is intentionally slower:

```bash
python -m unittest -v test_oig_uniform_lattice_arb_cover.py
```

Run the complete repository validation with:

```bash
python -m unittest discover -v
```

At canonical integration commit `4061270`, the complete repository reported
920 tests passing with one expected skip. The independent Atlas-integration
adversarial matrix reported 126/126 passing before the final full discovery.
The focused protocol-engine command above reports 155/155 passing on the
packaging state.

## Exact pinned composition

The committed Atlas-integration certificate reconstructs this complete chain:

1. a finite common-contract library uniquely selects the scalar response
   \(H=[2]\) over \(H=[1]\) and a blind candidate;
2. the same response, source metric, and output calibration are reused in the
   structured-nuisance and response-tube layers;
3. the structured response difference is recomputed as \(H(1)=2\);
4. the structured certificate gives \(d^2=9/4\) and critical equal-noise
   radius square \(9/16\); and
5. the declared noise-radius square satisfies the exact inequality
   \(1/4<9/16\).

The verifier rejects nested tampering, incoherent child substitution, altered
scope, surplus theorem claims, and inconsistent metrics.

## Scope boundary

This release certifies declared mathematical models. It does not certify that
a physical system belongs to one of those models. In particular:

- the finite candidate-library optimum is not a continuous-design optimum;
- externally supplied tail bounds, response enclosures, or exhaustive model
  lists remain declared premises;
- the general model-aware quotient object is a partial geometry audit until a
  compatible response-box information budget is composed with it;
- matched modal sensors need not be local or directly realizable hardware;
- no result establishes a physical law or a claim about the substrate of
  reality; and
- the work has not undergone independent specialist peer review.

## Attribution

- **Research, theorem development, implementation, computation, and writing:**
  Codex (OpenAI)
- **Originating research direction, intuition, and computational environment:**
  TGN's human founder

This attribution records provenance. It is not a literature-priority claim.
