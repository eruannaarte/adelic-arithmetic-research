# Operational Information Geometry VIII — reproducibility manifest

- **Canonical research commit:** `66d5255fc376893681502e6bf43f368283ee8d47`
- **Repository:** `eruannaarte/adelic-arithmetic-research`
- **Branch prepared for publication:** `codex/oig-uniform-three-parameter`
- **Research status:** theorem package with executable numerical and adversarial audits; not peer reviewed
- **Scope:** the declared one-way parabolic Markov model; not a physical theory

This manifest identifies the smallest committed environment and the exact
artifacts needed to reproduce Stage VIII. The canonical research commit is
recorded separately from later publication-only commits so that the theorem,
laboratory, and tests remain an immutable unit.

## 1. Minimal environment

Python 3.11 or newer is required. The dedicated dependency surface is
committed in `oig_viii_three_parameter_requirements.txt`:

```text
numpy>=2.2,<3
scipy>=1.15,<2
```

The repository-wide `requirements.txt` and `pyproject.toml` additionally
declare `mpmath` and `python-flint` because earlier arithmetic and interval
certificate stages use them. They are not imported by the Stage VIII
laboratory or its focused tests.

The reference validation host used:

```text
Python 3.12.9
NumPy 2.4.6
SciPy 1.15.2
```

## 2. Reproduction commands

From a clean checkout of the canonical research commit:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r oig_viii_three_parameter_requirements.txt

python -m py_compile \
  oig_viii_three_parameter.py \
  test_oig_viii_three_parameter.py \
  test_oig_viii_adversarial_controls.py

python -m unittest -v test_oig_viii_three_parameter.py
python -m unittest -v test_oig_viii_adversarial_controls.py
python oig_viii_three_parameter.py --fast
python oig_viii_three_parameter.py
python -m unittest discover -v
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## 3. Expected validation boundary

At the canonical research commit:

- the two focused Stage VIII suites pass 20 of 20 tests;
- complete repository discovery passes 231 of 231 tests;
- the full Stage VIII numerical laboratory takes about 13 seconds on the
  reference host; and
- Python bytecode compilation and `git diff --check` are clean.

The exact finite modal reduction is algebraic. Numerical phase integrals,
floating-point convergence orders, and nonlinear fits are regression and
falsification evidence, not outward-rounded interval certificates.

## 4. Canonical artifacts and SHA-256 digests

The following digests are for the files exactly as committed in
`66d5255fc376893681502e6bf43f368283ee8d47`.

| Artifact | Role | SHA-256 |
|---|---|---|
| `OPERATIONAL_INFORMATION_GEOMETRY_VIII.md` | canonical synthesis | `118c65ed5ec7befc4ebd5ee3f188eefd54aa937898e1d44af9e5f8da11c7f58e` |
| `OIG_VIII_RESOLVED_UNIFORM_THEOREM.md` | resolved-chart proof | `cf1c700fe8d26a93bc9c3329d0ae5ac93de5b02cd94b27b470e2e501705d1ee0` |
| `OIG_VIII_LATTICE_UNIFORM_THEOREM.md` | lattice, atomic-tail, and boundary proofs | `ba09dd6c4d1315c08b796930385b43f3d3b8a5afd995937254dc9308fc3b50e6` |
| `OIG_VIII_ADVERSARIAL_AUDIT.md` | independent proof and boundary audit | `e2b8fe1da6a7f8ab7849ea4e2f60c49124a59c1d996fed7d39089f708ec41b4b` |
| `oig_viii_three_parameter.py` | executable laboratory | `e662a2c813d00048ea5c138daad004625cc58fec8c7c489fbcba47da2e82b987` |
| `oig_viii_three_parameter.md` | numerical report and counterexamples | `d1c29ed5cad5d4f1833f2c3f18f6c44d9c15182f9060e8ec1583d6464aaa8ba2` |
| `test_oig_viii_three_parameter.py` | primary regression/falsification suite | `1da58979ededdf85251fd445d807828b6d87eb792d50e91ef9bb33a70bc8c0fe` |
| `test_oig_viii_adversarial_controls.py` | independent boundary-image control | `37f874ed0b55d2c52ad7b1fbe9a4670d7f5502005075dcccac1bbd932db7b2c5` |
| `oig_viii_three_parameter_requirements.txt` | minimal dependencies | `dbd1b4c4e7ce1c619c8e7f006a7dda252a0d881abfcc63fa53db733bf27997c2` |

Verify the manifest on macOS or Linux with:

```sh
shasum -a 256 \
  OPERATIONAL_INFORMATION_GEOMETRY_VIII.md \
  OIG_VIII_RESOLVED_UNIFORM_THEOREM.md \
  OIG_VIII_LATTICE_UNIFORM_THEOREM.md \
  OIG_VIII_ADVERSARIAL_AUDIT.md \
  oig_viii_three_parameter.py \
  oig_viii_three_parameter.md \
  test_oig_viii_three_parameter.py \
  test_oig_viii_adversarial_controls.py \
  oig_viii_three_parameter_requirements.txt
```

## 5. Public interpretation boundary

The reproducible result is a quantitative atlas for a chosen finite-to-
continuum response model. It does not establish that physical reality is a
lattice, a diffusion, or an information substrate. The public account should
retain the null-port, placement, boundary, resolution, and pre-asymptotic
counterexamples in the canonical falsification ledger.
