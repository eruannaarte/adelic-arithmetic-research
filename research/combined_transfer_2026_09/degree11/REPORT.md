# Degree eleven: the missing comparison is now verified

Degree eleven does **not** meet the fixed amplitude-4000, frequency-3 recovery
requirement under the tested complete certificate. It does certify amplitude
500 with all other allowances unchanged. The conclusion is a useful tradeoff,
not a universal degree threshold or an impossibility result.

Both designs use the same 8,900 physical readings. Their specified weighted
noise balls differ. The coefficient source is every integer sequence within
the complete d_14 envelope, with known a(1)=1; it is not asserted to be the
class of actual number-field coefficients. All positive-degree polynomial
nuisance coefficients through degree eleven remain unrestricted.

| Complete quantity | Multiscale W | Outer W |
|---|---:|---:|
| Complete degree-eleven coefficient bias, upward | 0.250872050 | 0.299828590 |
| Augmented Gram floor, downward | 0.999242040 | 0.998969849 |
| Weighted frequency-3 family factor, upward | 7.387576e−8 | 7.392804e−8 |
| B=4000 error bound with preceding pair clock, upward | 1.092609098 | 1.142203362 |
| B=4000 error bound with new orbit clock, upward | 1.092523325 | 1.142117571 |
| B=500 error bound with new orbit clock, upward | **0.445865330** | **0.494913819** |

The integer threshold is strictly below 1/2. In the amplitude-4000 test only
32 of 49 scalar gates pass; at amplitude 500 all 49 pass. The improved orbit
clock barely affects this particular obstruction to certification: the
nonpolynomial approximation allowance dominates the deficit. The result
helps identify where further effort is useful.

The new degree's inverse is fully reconstructed. Its Schur and complete tail
bounds are recomputed using the first eleven physical nuisance channels;
the degree-twelve decoded bias is not transferred without proof. Even and
odd polynomial parity supplies valid degree-eleven approximants from earlier
rational constructions, with complete Taylor remainder channels. See
[the proof](PROOFS.md) and [exact evidence](evidence.json).

The positive result is also operational. Two raw data sets have actual
nonzero degree-eleven polynomial drift of scale 10^20, the boundary affine
clock, sinusoidal drift, sensor noise and a distinct model-mismatch term.
Both weight designs rebuild and solve the true 61-column augmented model;
normal and reading-space residual identities are checked independently.
All four residual upper bounds are below 1.1900e−43 at 320 bits and replay
at 384 bits. The amplitude-500 answers equal the 49 unknown fixture integers.
The amplitude-4000 data are explicitly returned as not certified by the
uniform contract. A small solver residual never supplies a missing physical
family or calibration guarantee.

The classical dense construction has 542,900 forward entries, 1,089,521
entries if X, X*W and its Gram are stored, and 33,116,900 complex multiply-
accumulates for a full Gram formation. Degree twelve would require 34,211,600
such operations. These are declared arithmetic counts; the actual interval
library may use other algorithms. In the recorded 320-bit run the two model
constructions took about 2.76 and 3.11 seconds, proposals about 0.13 seconds,
and dual residual checks about 0.22 seconds each. Timings are one-run
observations, not universal benchmarks.

The least passing degree is now twelve **among the tested 6,8,10,11,12** for
B=4000 and Omega=3. The new positive degree-eleven profile is useful when
amplitude is limited: a conservative common choice B=500 is rigorously
accepted in both designs. A sharper bound for correlated Taylor residuals,
or for the actual projected sinusoid family, could improve that threshold;
the present failure does not rule it out.
