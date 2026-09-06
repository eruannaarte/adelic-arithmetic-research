# Combined acquisition and uncertainty: three completed objectives

The transfer theorem now supports a six-channel spatial experiment with
declared clock and potential uncertainty, a substantially tighter complete
arithmetic clock bound, and a verified degree-eleven cost--amplitude
comparison. Each result uses a complete route from its defining model to
its final query guarantee. The [protocol](PROTOCOL.md) records the contracts
fixed before testing.

The common research question remains: **what can a limited experiment
determine about a specified question, despite structured uncertainty?**
The [joint-budget transfer corollary](framework/PROOFS.md) supplies a precise
answer: retain every legal explanation through nuisance removal and finite
approximation, then prove that the remaining query answers are separated or
enclosed to the required accuracy.

## 1. Six channels retain a joint physical uncertainty guarantee

The rows **485, 493, 499, 501, 507 and 515** identify any of the 21 targets
from 490 through 510 and recover every nonzero source in the prescribed two
orthonormal modes. The guarantee holds throughout nominal and true model
times in [1,2], with sensor error at most `3e-8` times the source norm,
shared clock displacement at most `1e-8`, and shared potential uncertainty
`|g-4/5|<=1e-8`.

The complete relative source error is below **0.000852831068**, meeting the
fixed target `0.001`. The total physical label tube is below
`3.243001712e-8`, inside the newly certified radius `3.25e-8`.

This required new combined calculations. The earlier six-row certificate
assumed known time and potential; the earlier structured physical certificate
used seven rows. The present six-row directional matrices and enlarged
weighted-pair separation have both been recomputed. The proof charges the
full nonlinear clock/potential cross term, complete model approximation and
verified nominal-time normalization.

All **1,280** single-target/pair records and **2,688** directional time cells
pass independent consumers. Twenty-four raw synthetic experiments, generated
from the actual finite physical generator at true clock and potential
endpoints, recover every target. Full physical coefficient and raw-data
replays support that route; the uniform theorem comes from the all-source,
all-time certificates.

The coarse inverse control also meets the source target, with error below
`0.000863601842`. Structured inversion sharpens this bound, but is not
necessary to pass this particular small uncertainty box. The demonstrated
advance is the combined six-channel acquisition contract. Its tolerances are
in the specified model units and still need justified physical calibration
for an apparatus application.

Evidence: [spatial report](spatial/REPORT.md), [proof](spatial/PROOFS.md),
[complete consumer output](spatial/checked.json),
[independent review](review/SPATIAL_REVIEW.md).

## 2. Complete multiplicative blocks more than halve the clock allowance

The arithmetic experiment retains the same **8,900 complex readings** and
the entire source class `0<=a(n)<=d_14(n)` of integer coefficients, with
known `a(1)=1`. Its target is the 49 unknown integers `a(2),...,a(50)`.
The two physical weightings have different weighted noise norms; their
numerical tolerances should be read with those norms attached.

Every positive integer is written uniquely as `2^k m`, with `m` odd. The new
bound groups 32 successive valuations in each orbit and verifies their actual
oscillatory phase correlations. Complete geometric tails include all larger
valuations, and complete odd-integer generating series include every odd
starting integer. Actual coefficients may vanish independently: the proof
does not impose the multiplicative ratios of their envelope on them.

The resulting complete clock-distortion bound is below **2.987008e-8** at
the base rectangle `|delta_a|<=1e-14`, `|delta_b|<=1e-11`. This is more than
53.45% smaller than the preceding all-integer pair bound. The improvement is
proved before exact polynomial nuisance projection and remains valid after
it by contraction.

The predeclared operational consequence uses **h=120** times those clock
radii: `|delta_a|<=1.2e-12`, `|delta_b|<=1.2e-9`. At degree twelve, sinusoidal
amplitude at most 4000, frequency at most 3, weighted sensor radius `4e-5`
and separate mismatch radius `1e-6`, both complete integer certificates pass:

| Physical weighting | New maximum coefficient error | Previous pair formula at the same h=120 |
|---|---:|---:|
| Multiscale | `<0.447153367` | `<0.457446227`; passes |
| Outer window | `<0.496198708` | `>0.506493579`; sufficient gate fails |

All 49 strict rounding gates pass under the new bound. Fresh 384-bit
reconstruction verifies the same actual raw readings, saved proposed
inverses and two normal-residual identities. A separate review reconstructs
all 248 clock-corner/phase-lag correlations at 448 bits and independently
checks both infinite valuation tails against exact generating-function
totals.

For the stated degree-twelve formula and a separately verified normal
residual at most `1e-30`, the largest passing integer clock multipliers are
827 for multiscale and 170 for the outer window, compared with 385 and 79
for the preceding pair formula. These are exact integer boundaries of the
specified monotone sufficient formulas. They do not establish optimal
clock tolerances across all possible methods. The actual physical examples
use the independently fixed, less marginal h=120 contract.

Evidence: [block report](blocks/REPORT.md), [complete proof](blocks/PROOFS.md),
[exact consequences](blocks/consequences.json),
[independent review](review/BLOCK_REVIEW.md).

## 3. Degree eleven exposes the cost--amplitude tradeoff

The missing degree-eleven construction now has its own complete-tail
inverse, Gram floor, weighted drift approximation and actual residual
certificate. Removing the twelfth polynomial column requires recomputing
the inverse-dependent tail bounds. Exact parity supplies valid degree-eleven
approximants, while complete Taylor remainder channels remain charged.

At the **base clock h=1**, frequency at most 3, sensor radius `4e-5`,
mismatch radius `1e-6` and the new orbit clock bound, the results are:

| Sinusoidal amplitude bound | Multiscale error bound | Outer error bound | All 49 integer gates |
|---|---:|---:|---|
| 4000 | `1.092523325` | `1.142117571` | No; 32 pass in each design |
| 500 | `<0.445865330` | `<0.494913819` | Yes, both designs |

The first row is a failure of the tested sufficient certificate, rather than
a collision or a degree lower bound. Its dominant deficit is the
nonpolynomial approximation allowance: replacing the preceding pair clock
by the tighter orbit clock changes these errors only slightly. The second
row provides a useful positive profile with lower amplitude.

The physical degree-eleven inverse uses 61 augmented columns instead of
degree twelve's 62. A classical dense Gram construction takes 33,116,900
complex multiply-accumulates instead of 34,211,600, with the same 8,900
acquired readings. These are explicit arithmetic counts; library runtime
depends on its algorithm and machine.

The synthetic raw data include nonzero degree-eleven polynomial nuisance
of scale `1e20`, actual shared clock error, sinusoidal drift, sensor error
and distinct mismatch. Four actual inverse checks, covering both amplitudes
and weightings, replay at 384 bits. The amplitude-500 answers are certified;
the amplitude-4000 answers are explicitly left uncertified by the uniform
contract. Twelve remains the least passing degree **among the tested
6,8,10,11,12** for amplitude 4000 and frequency 3 under these constructions.
Untested degrees and sharper degree-eleven approximations are not excluded.

Evidence: [degree-eleven report](degree11/REPORT.md),
[proof](degree11/PROOFS.md), [orbit comparison](degree11/orbit_comparison.json),
[independent review](review/DEGREE11_REVIEW.md).

## 4. What is unified, and what remains model-specific

The common object is the set of answers consistent with an observation.
The transfer theorem first preserves or safely enlarges that set through
the actual processing steps. Its final quantitative tests then take the
form required by the query: weighted pair separation and source error for
spatial sensing, or complete coefficient disks and strict integer rounding
for arithmetic sensing.

The five original research paths supplied different parts of this framework:

| Original path | Contribution to the common question | Research origin |
|---|---|---|
| Experimental design with preparation and clock uncertainty | Shared physical nuisance must follow its actual experimental incidence | [Preparation work](../five_paths_2026_09/path1_preparation/PROOF.md) |
| Harmonic acquisition | Reading count, acquisition time and global separation are distinct costs | [Harmonic work](../five_paths_2026_09/path2_harmonic/PROOFS.md) |
| Multiscale arithmetic sensing | Complete infinite tails and the actual reused-reading noise norm enter recovery together | [Noise work](../five_paths_2026_09/path3_noise/PROOF.md) |
| Discrete arithmetic queries | The admissible source class and arithmetic relations change which answers are possible | [Realizability work](../five_paths_2026_09/path4_realizability/PROOF.md) |
| Finite-resolution observation | Restricted measurements and approximation error must be compared with the weakest information direction | [Resolution work](../five_paths_2026_09/path5_resolution/APPENDIX.md) |

The [original five-path synthesis](../five_paths_2026_09/REPORT.md) and the
[transfer framework](../transfer_theorem_2026_09/framework/PROOFS.md) remain
records of their own models and stages. This round develops two of those
model families in depth. It does not assert that all five have one physical
noise model, nor that the unrestricted divisor envelope is the class of
actual number-field coefficients.

The new [joint-budget corollary](framework/PROOFS.md) proves the needed
composition explicitly. It retains unrestricted nuisance only when exact
annihilation or exact augmented representation is justified, transports the
physical error metric, keeps joint directions before inverse bounds, and
charges the complete numerical residual. This is mathematical usefulness
through demonstrated consequences, without asserting historical priority
for its classical ingredients.

## 5. Verification and the next focused objectives

The three packages contain 32 positive/adverse tests and independent internal
proof/computation reviews. Whole-time spatial inequalities, actual arithmetic
phase sums, actual finite-model kernels, new degree-eleven tail channels,
raw readings and numerical residuals all have documented reconstruction
routes. Historical complete arithmetic-tail enumerations remain identified
inherited premises with their earlier replay commands. A hash verifies which
premise was used; it does not prove that premise's numerical content.

The [reproduction guide](README.md) separates fast consequence checks from
fresh model reconstruction and expensive inherited-tail replay. These checks
establish the stated mathematical implications. Physical calibration, source
family membership and empirical noise laws remain separate evidence.

The next objectives follow the remaining dominant terms:

1. **Spatial tolerance region:** enlarge the six-row joint clock/potential
   region under a sensor and source-accuracy requirement fixed in advance,
   then certify the enlarged region or give a scoped obstruction. The present
   small box establishes feasibility but does not locate its frontier.
2. **Additional arithmetic phase structure:** combine powers of 2 and 3 with
   complete coprime starting classes and both infinite valuation tails, or
   obtain a direct bound after exact nuisance projection. The latter must
   retain the dependence on the odd starting integer: projection generally
   does not commute with its common phase multiplier.
3. **Degree-eleven approximation:** bound correlations between Taylor
   residuals, or the actual projected sinusoid family, against a fixed
   amplitude target. The current amplitude-4000 failure identifies this
   approximation term as more important than another small clock improvement.

Each objective should keep the same complete query budget and report its
acquisition or computation cost. A reduced intermediate bound becomes a
research consequence only when it changes a certified answer, a declared
error tolerance, or a precisely stated obstruction.
