# Independent mathematical and computational review

Reviewed 2026-09-05 by a separate agent. The common theorem, spatial clock/model
budget, raw decoder and arithmetic degree comparison are supported by the
checks below. No unresolved mathematical issue was found within the declared
contracts. These are model-based guarantees and synthetic reconstructions;
none establishes apparatus calibration or empirical family membership.

## The shared acquisition theorem and its obstruction

The proof in [CLOCK_NUISANCE.md](CLOCK_NUISANCE.md) independently derives the
nuisance condition: a fixed quotient admits a finite bound uniform over
unrestricted nuisance coefficients exactly when it annihilates every allowed
acquisition-dependent nuisance image. Scaling a leaked direction proves
necessity. Clock, model and sensor errors may be correlated; summing valid
norm bounds remains conservative without an independence assumption.

The polynomial-clock characterization is especially useful here. For m>p²
distinct nominal samples and p>=1, preserving the entire degree-p polynomial
sample space is equivalent to the actual sampled times being affine in the
nominal times. This includes all four tested degrees on 8,900 readings.
Arbitrarily small independent jitter can violate the condition. The rational
finite-difference witnesses prove unbounded leakage by scaling linear drift.
This obstructs the declared uniform quotient error budget; it is not an
impossibility theorem for every possible joint decoder.

The positive affine-clock route correctly absorbs every unrestricted
polynomial coefficient, enlarges the sinusoidal frequency, and charges the
complete arithmetic signal distortion separately. A small computed normal
residual does not establish the acquisition or drift premises.

## Reconstructed quantitative checks

| Independent check | What was rederived |
|---|---|
| [clock_review.py](clock_review.py), [result](clock_review.json) | Exact finite-difference witnesses for degrees 6,8,10,12; a complete derivative envelope from a fresh cutoff of 10,000 and positive integral tails; the declared affine-clock radius |
| [weighted_review.py](weighted_review.py), [result](weighted_review.json) | All 184 rational approximant norms, 16 complete remainder norms and all 32 degree/frequency factors, using original physical cosine weights and independently accumulated symmetric moments at 384 bits |
| [spatial_review.py](spatial_review.py), [result](spatial_review.json) | Uniform derivative bound 0.037 for all 21 targets; complete inherited physical error; both strict uncertainty profiles; 693 outward point Gram-floor checks; all 12 actual perturbed-model raw sensor promises |
| [raw_review.py](raw_review.py), [result](raw_review.json) | All 12 exact normalization packets, interval/nominal-time bindings, physical error charges, 252 candidate feasibility decisions, ordinary Gram source estimates and actual source-error enclosures |
| [arithmetic_review.py](arithmetic_review.py), [result](arithmetic_review.json) | Every one of the 8,900 raw complex readings reconstructed at 384 bits; coefficient envelope and acquisition promises; all 392 actual coordinate gates; all 80 actual/planning budget rows and degree choices |

These scripts import no current producer or decoder. The arithmetic raw replay
uses direct polynomial powers and separate sine/cosine components, independently
of the producer's Horner and complex-exponential expressions. The spatial raw
replay likewise uses direct polynomial powers and an independent rational
least-squares/feasibility implementation. The derivative audit uses a different
positive-series cutoff from the producer.

The spatial point checks supplement the separate exact full-time cell
consumer; they are not a replacement for its continuous coverage. The complete
arithmetic tail bounds are preserved predecessor premises, and the normal
residuals are independently bound to the fixed raw data and proposals and
reconstructed by the outward 384-bit replay. This review independently checks
their subsequent consequences; it does not claim a second implementation of
the entire infinite-tail or augmented-residual producer.

## The raw clock wrapper

Static review of [raw_clock.py](../framework/raw_clock.py) and
[uncertainty.py](../framework/uncertainty.py) confirms that:

- The nominal exact rational time is used only for normalization and nominal
  forward evaluation. The actual interval lies in [1,2] and its maximum
  distance from the nominal time supplies the distinct timing charge.
- Both physical generators are required to be self-adjoint and positive
  semidefinite. Their contraction bound justifies the normalization gain
  4/3 plus the physical sensor radius; clock and generator mismatch are then
  included in the forward discrepancy. No unproved derivative of a saved
  approximation remainder is taken, and its radius is charged once.
- The pair floor controls label separation while the individual source floor
  controls accuracy. Feasibility is checked in normalized coordinates with
  the correctly transformed radius, then the ordinary source least-squares
  estimate is returned. An incompatible or non-unique result carries no
  source-accuracy assertion.
- Exact input types and nonnegative bounds are checked. The validated kernel
  coefficients are stored as nested tuples. Unknown source amplitude and
  target are not inputs to normalization or decoding; fixture amplitudes are
  used only by the independent validation of the returned answers.

## Review correction and limits of the comparison

Review identified one scope issue in the preliminary frequency-capacity
presentation: a normal residual observed on the actual frequency-three
fixture cannot be transferred automatically to different future readings.
The final tables now use the explicit future residual ceiling 10^(-30) for
all 32 hypothetical frequency capacities and all 40 planning budgets. Future
data must establish their own family membership and verify that residual
ceiling. The eight actual rows retain their individually reconstructed
residuals. The independent consequence audit checks this distinction.

Both degree-twelve actual inverses recover all 49 unknown integer
coefficients. Their complete error bounds are below 0.438590 (multiscale) and
0.487634 (outer). The failed degree-six/eight/ten sufficient bounds are
retained as controls, without being relabeled as information-theoretic
impossibility. The degree comparison optimizes the displayed sufficient
bounds over the four tested degrees, not all possible approximants or sensing
systems. The spatial bank is improved and certified, not proved minimal.

## Replay

Run the five scripts in the table with the project's Python runtime
`/private/tmp/math-five-paths-venv/bin/python`, setting
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`.
Each prints a fresh JSON audit and exits nonzero on a failed check. The clock,
weighted, spatial and arithmetic reviews require python-flint; the raw review
uses only the Python standard library. The parent reproduction guide records
the separate full-time consumer and outward residual/tail reconstruction paths.
