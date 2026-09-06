# Reproduce the eleven-row certificate

This package proves joint target/source recovery from eleven separated spatial averages for the original finite model. Begin with [REPORT.md](REPORT.md), then [PROOFS.md](PROOFS.md). [OBJECTIVE.md](OBJECTIVE.md) records the starting objective and comparison budget. [AUDIT.md](AUDIT.md) is the independent review.

Use the existing research runtime:

    MATH_TRANSFER_PYTHON=/private/tmp/math-five-paths-venv/bin/python

Run these from the Math repository root.

## Exact consequence check

    $MATH_TRANSFER_PYTHON -S research/transfer_theorem_2026_09/resolution/check.py

This needs only the standard library. It independently checks the exact polynomial certificate, all 231 separate time covers, complete analytic error budgets, and all three noise/source calibrations. It returns the rational interface used by the parent transfer theorem. Its kernel premise is the outward enclosure file; a matching hash binds that premise but does not reconstruct the physical model.

Files: [check.py](check.py), [certificate.json](certificate.json), [kernel.json](kernel.json), [checked_interface.json](checked_interface.json).

## Full model reconstruction

    $MATH_TRANSFER_PYTHON research/transfer_theorem_2026_09/resolution/kernel.py
    $MATH_TRANSFER_PYTHON research/transfer_theorem_2026_09/resolution/kernel.py --precision 256

Both commands reconstruct every finite-x Fourier coefficient and complete exponential remainder, then demand equality with the saved outward rational intervals. They use python-flint/Arb. The observed 192-bit and 256-bit exports agree. This replay plus the proved boundary, image, and time charges connects the polynomial premise to the actual finite model.

To rebuild proposed preconditioners and independently check their exact consequences:

    OPENBLAS_NUM_THREADS=1 $MATH_TRANSFER_PYTHON research/transfer_theorem_2026_09/resolution/produce.py

This command does not change the certificate. It uses NumPy only for proposals, then exact rational producer checks and the independent consumer. Explicit --write options on the producers replace their corresponding generated files; they are not needed for verification.

Files: [kernel.py](kernel.py), [produce.py](produce.py), [exact.py](exact.py).

## Decoder and adverse tests

    $MATH_TRANSFER_PYTHON -m unittest discover -s research/transfer_theorem_2026_09/resolution -p test_resolution.py -v

Nine tests verify all labels at the time endpoints and center, multiple source directions, calibrated noise, exact polynomial translation, incompatible/zero-data behavior, and rejection of a missing pair's time cover or changed premises.

[decoder.py](decoder.py) exposes CertifiedBank().decode(data, tau, metric, numerical_relative_radius). It accepts eleven **exact rational** unnormalized data coordinates \(z=y/(1+\tau)^{1/4}\), exact rational time in [1,2], one of L2 / declared_H1 / natural_discrete_H1, and an optional relative computed-data allowance between 0 and \(10^{-9}\). No true label is supplied.

It returns a unique target and exact rational least-squares source estimate, an incompatible empty set, or abstention. Zero data are outside the nonzero-source theorem and raise an error. Converting measured data or the normalizing fourth root to rationals requires an independently justified error allowance; parsing a decimal is not itself that justification. The mathematical theorem covers all known real times, while this reference implementation deliberately exposes only exactly represented rational times. Uncertain time requires a new model-error allowance.

## Independent and diagnostic checks

    $MATH_TRANSFER_PYTHON research/transfer_theorem_2026_09/resolution/independent_audit.py
    OPENBLAS_NUM_THREADS=1 $MATH_TRANSFER_PYTHON research/transfer_theorem_2026_09/resolution/forward_checks.py

The first reconstructs independent analytic and small-model controls plus 16 selected full-x coefficients by a different expansion, as described in the audit. The second performs full finite-grid floating diagnostics, including the physical endpoints in both directions, and exercises the unknown-label decoder in 27 calibrated cases. The saved output is [forward_checks.json](forward_checks.json); pass --write explicitly to refresh it. The default command runs the diagnostics and prints their summary without changing files. The saved output is not a source of uniform mathematical bounds or a certified floating error budget.

Discovery files [discover.py](discover.py), [discovery.json](discovery.json), and [discovery_refined.json](discovery_refined.json) are retained as proposals only. No unsuccessful proposal is called an impossibility result. [VALIDATION.json](VALIDATION.json) records completed checks.

The proof assumes the declared linear finite model, exact preparation of the two-dimensional source subspace, the specified noise norms, and known observation time. Eleven rows refers to directly acquired global-x spatial averages, not eleven fully local point detectors.
