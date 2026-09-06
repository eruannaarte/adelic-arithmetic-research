# A six-channel experiment with a joint physical uncertainty contract

The predeclared contract passes. Six readings at rows **485, 493, 499, 501,
507 and 515** identify every target from 490 through 510 and recover every
nonzero two-mode source with relative Euclidean error below **0.000852831068**.
The theorem covers every nominal and true model time in [1,2], sensor radius
`3e-8` times the source norm, shared clock displacement `1e-8`, and shared
potential uncertainty `|g-4/5| <=1e-8`.

These are mathematical model tolerances. Their physical adequacy requires a
choice of units and justified preparation, clock and potential calibration.

| Contribution | Certified allowance |
|---|---:|
| Sensor error, relative to source norm | `3e-8` |
| Complete nominal model approximation | `1e-9` |
| Verified arithmetic normalization | `1e-9` |
| Full nonlinear joint remainder | `<1.711669e-14` |
| Joint clock/potential forward direction | `<4.3e-10` |
| Total physical label tube | `<3.243001712e-8` |
| Newly certified label tube limit | `3.25e-8` |
| Joint inverse influence | `<6.8e-7` |
| Complete relative source error | `<0.000852831068` |

The earlier six-channel certificate assumed known time and potential. The
earlier physical uncertainty certificate used seven channels. This result
recomputes the directional matrices for the six selected rows and enlarges
the pair separation certificate. It therefore establishes the combined
experiment rather than inferring it from the two separate guarantees.

The independent exact-polynomial consumer verifies **1,280 records** covering
all 21 single-target cases and 210 target pairs, with adaptive rational time
cells. The independent 320-bit directional consumer verifies **2,688 cells**,
including every recorded forward/inverse bound. Complete periodic-image,
finite-boundary, Taylor and mixed-parameter errors remain charged.

The separate global inverse estimate also passes this small rectangle, with
relative source error below `0.000863601842`. Thus structured inversion is a
sharper bound here, but is not necessary for the successful source gate. No
maximal tolerance, optimal bank, or general six-channel lower theorem follows.

Twenty-four synthetic raw datasets were reconstructed from the actual finite
generator at true clock and potential endpoints. They include all four sign
corners at the middle time, admissible endpoint-time displacements, three
targets and source amplitudes from `1e-8` to `1e8`. The exact decoder recovered
every target, verified every normalization receipt, and observed source error
below `0.000023687366`. A 320-bit replay re-establishes the actual observations;
these examples are not laboratory data or the proof of universal recovery.

Fresh full-model replays recover all 1,782 nominal coefficient intervals at
320 bits and all 1,782 potential-derivative intervals at 384 bits. Thirteen
adverse tests pass, including changed rows, missing time coverage, false
directional bounds, altered kernel bindings, substitution of the old smaller
pair budget, false principal minors, invalid weights, excessive uncertainty,
inexact input and zero data.

The [proof](PROOFS.md), [checked certificate](checked.json), and
[reproduction guide](README.md) give the complete route from the physical
generator to the guaranteed answer. The next spatial question is to enlarge
the joint uncertainty region under a fixed sensor and source-accuracy budget,
or determine a scoped obstruction. This certificate establishes one small,
nonzero region; it does not determine that region's frontier.
