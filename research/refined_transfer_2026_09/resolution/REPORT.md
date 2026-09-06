# Seven rows satisfy the fixed noise and accuracy contract

The asymmetric bank

\[
(488,490,497,500,504,508,510)
\]

uses **seven separated rows** and identifies every target from 490 through 510,
for every nonzero two-mode source and every known time in \([1,2]\), in the
unchanged finite diffusion model.

The sensor error is bounded by \(10^{-7}\) times the Euclidean source norm.
Charging both the \(10^{-9}\) model error and the full \(10^{-9}\) computed-data
allowance, the source relative error is **below 0.000998507**. Thus the
requirement fixed before the search—noise radius \(10^{-7}\), source accuracy
below \(0.001\)—is met without relaxation.

| Exact certificate quantity | Value |
|---|---:|
| Row offsets about 500 | \((-12,-10,-3,0,4,8,10)\) |
| Smallest consecutive gap | 2 |
| Unnormalized individual Gram floor | \(7.4\cdot10^{-9}\) |
| Unnormalized two-target Gram floor | \(2\cdot10^{-14}\) |
| Separate cases | 21 individual + 210 pairs |
| Nonempty time cells | 1,051 |
| Case-specific whole-cell records | 3,391 |
| Exact source relative error squared bound | \(5202/5217578125\) |

The [proof](PROOFS.md) turns these exact floors and complete physical
remainders into disjoint query tubes and a bounded least-squares inverse.
Every case separately covers the full time interval. The
[standard-library checker](check.py) recomputes all acceptance inequalities
using rational arithmetic; no sampled singular value establishes the claim.

The noise–acquisition tradeoff remains explicit:

| Bank | Euclidean sensor radius | Certified relative source accuracy |
|---|---:|---:|
| Previous nine rows | \(3\cdot10^{-7}\) | \(<0.000998\) |
| Previous eight rows | \(2.3\cdot10^{-7}\) | \(<0.000977\) |
| New seven rows | \(10^{-7}\) | \(<0.000998507\) |

All three charge the same \(10^{-9}\) model and \(10^{-9}\) computed-data
budgets. These are different fixed banks and sufficient guarantees, not a
claim about arbitrary row deletion or optimal noise thresholds. The new
seven-row result states only the Euclidean source calibration.

The search also yielded a useful adverse example. A different seven-row bank
that won on 17 sample times has an actual physical ambiguity at the interior
time \(1.221707459\). The exact collision witness works already below sensor
radius \(1.463\cdot10^{-9}\), so it certainly fails the fixed \(10^{-7}\)
requirement. The [obstruction](coarse_grid_obstruction_checked.json) applies
to that particular bank. This demonstrates why complete-time certification
changes which design should be chosen.

The decoder is implemented in [decoder.py](decoder.py), and executable
validation is described in [README.md](README.md). All eight focused tests
passed. Five independent floating finite-model diagnostics also passed,
including noise in the weakest information direction; their largest source
error was approximately \(0.00097055\). Those diagnostics are not proof
inputs. Independent outward 320-bit checks of ten selected map floors are
recorded in the [review](../review/seven_point_review.json).

The physical source,
known-time and uncertainty promises remain necessary; rows still measure
spatial averages. The four-channel lower benchmark is unchanged and the
minimum sufficient row count remains open.

The next useful spatial objective is to compare six-row candidates under a
noise requirement fixed in advance, using the proven interior-time collision
as an early rejection tool. Improving the present seven-row noise margin is
a separate optimization problem: the current certificate meets its accuracy
target with a narrow source-floor margin, so a sampled pair improvement alone
would not improve the final recovery guarantee.
