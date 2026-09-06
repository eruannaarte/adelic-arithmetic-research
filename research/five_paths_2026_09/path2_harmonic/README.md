# Path 2: harmonic reading complexity with acquisition constraints

Start with [CHAPTER.md](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path2_harmonic/CHAPTER.md). Full derivations and scope are in [PROOFS.md](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path2_harmonic/PROOFS.md); every finite claim is reconstructed from [inputs.json](/Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path2_harmonic/inputs.json) by the small checker.

The before/after result is a new six-reading time–stability tradeoff: maximum time 2773.804407 with factor floor greater than .815089 under absolute clock error .001, compared with the old time 220023.423. Re-evaluating the old schedule with the same sharper theorem gives floor 1.23914, so no domination is claimed. A separate finite-amplitude bound handles the unknown shared clock. The package also supplies an actual five-reading locally invertible example and a cubic small-time obstruction.

## Fresh checks

The existing shared runtime is `/private/tmp/math-five-paths-venv/bin/python`. Re-create a clean environment if needed with Python 3.12 and dependencies `python-flint==0.9.0`, `numpy==2.5.2`; numerical FLINT version used here is 3.6.0. The certificate itself uses only python-flint and the Python standard library. NumPy is used for discovery and supplementary tests.

```bash
cd /Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path2_harmonic
/private/tmp/math-five-paths-venv/bin/python certificate_checker.py
/private/tmp/math-five-paths-venv/bin/python -m unittest -q test_certificate.py
```

Expected: `verified: true`, the four schedule bounds reported in `PROOFS.md`, and `Ran 15 tests ... OK`. The test suite also reconstructs the same rational finite consequences at 512 bits. The ordinary check compares a full recomputation with the stored certificate; hashes are not used as a substitute for proof.

Reproduce the old formal baseline independently:

```bash
cd /Volumes/KINGSTON/Vibecoding/Math
/private/tmp/math-five-paths-venv/bin/python arithmetic_observability_full_segre.py --verify arithmetic_observability_full_segre_certificate.json
```

Expected payload `02a00b4a1bb18ab366cd1de844f1f23101f5c3f424329b12e268d981b42179fc` and `verified: true`.

Candidate discovery is optional and nonformal:

```bash
cd /Volumes/KINGSTON/Vibecoding/Math/research/five_paths_2026_09/path2_harmonic
/private/tmp/math-five-paths-venv/bin/python search_schedule.py --caps 3000,5000,10000
/private/tmp/math-five-paths-venv/bin/python search_schedule.py --caps 1000,1500,2000,2500
```

Those two sub-second searches generated `discovery.json` and `pilot_shorter.json`. Their floating-point diagnostics are not certificate inputs. The selected rational times were frozen in `inputs.json`; the checker reconstructs them independently. No expensive validation is needed. To regenerate the canonical certificate deliberately, run `certificate_checker.py --write` and then rerun the normal check.

## Evidence files

- `PREREGISTRATION.md`: frozen model, cost, clock, noise, and decision criteria before search.
- `PROOFS.md`: complete count reconstruction, local/global distinction, new global majorant, unknown-clock theorem, worked schedules, and counterexample review.
- `certificate_checker.py`, `inputs.json`, `certificate.json`: exact input-to-consequence connection.
- `test_certificate.py`: 15 focused controls, including source-model and boundary checks.
- `CLAIMS.json`: claim-to-evidence map.
- `SOURCES.md`: primary theorem source and dependency/hypothesis checks.
- `borsuk_1933_source.pdf`: publisher's scan and visually checked original statement on printed p178. These are attributed third-party research sources, not newly authored work.
- `PROGRESS.md`: compact development record and remaining boundaries.

The existing root research files were not modified. The parent report may use this chapter and appendix as one part of the five-path synthesis.
