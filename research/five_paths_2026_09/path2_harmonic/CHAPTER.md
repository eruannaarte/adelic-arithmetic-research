## Harmonic acquisition: six readings at much shorter times

How expensive is a mathematically minimal experiment? For three known prime axes `(2,3,5)`, each carrying an arbitrary probability distribution on four exponent states, the existing theory gives an exact answer in reading count: six complex harmonic values suffice globally, and every smaller schedule has exact collisions. But its certified six-reading example reaches time `220023.423`. Reading count alone conceals a substantial acquisition cost.

We reconstructed both sides of that theorem. A factor DFT supplies the upper construction; reversal symmetry and Borsuk's antipodal theorem supply the matching obstruction, including collisions arbitrarily close to the uniform product. Local recovery is different: five readings can have an injective differential at an interior point, as a new Arb-certified example demonstrates, while still failing globally.

The main extension is a quantitative time–clock–stability tradeoff. Centering each exponent alphabet and retaining the individual phase errors yields a tighter derivative bound than the original common phase box. Because that bound holds over the entire product of closed simplices, integration along every factor-coordinate chord proves global separation; sampled Jacobian ranks are unnecessary.

At six readings and absolute time errors bounded by `0.001`, the same improved theorem gives:

| Design | Maximum time | Certified global factor floor |
|---|---:|---:|
| Existing schedule | 220023.423 | greater than 1.2391 |
| New short schedule | 1463.985949 | greater than 0.5039 |
| New balanced schedule | 2773.804407 | greater than 0.8150 |
| New higher-floor schedule | 8081.202441 | greater than 1.0907 |

The floor `c` means every pair of factor tuples satisfies `||data-data'||_2 >= c||q-q'||_fac`. The balanced design reduces maximum time by a factor of **79.3**. The old schedule retains the strongest floor when evaluated with the same new bound: this is a measured tradeoff, not an across-the-board improvement.

The timing theorem covers independent bounded offsets and therefore also a single shared offset. A pure shared clock-rate error `beta` is covered when `|beta|T_max<=0.001`; the balanced schedule consequently permits `|beta|<=3.6051e-7`, compared with `4.5449e-9` for the old schedule.

Unknown timing requires a separate finite nuisance bound. For the balanced schedule, adversarial raw-data noise of Euclidean radius `0.001` plus an unknown shared time offset of `0.001` gives factor-recovery error at most **0.063781** for every global nominal least-squares minimizer. If the realized timing is known, the same sensor noise gives error at most **0.002454**. Neither claim assumes independent noise samples.

The proof appendix and small checker reconstruct prime logarithms and acquisition phases with outward Arb intervals, then derive the decisive bounds using exact rational arithmetic. The original baseline verifier, a 512-bit refinement, and 15 focused controls pass. These results apply to the finite normalized product model and its declared metrics. They do not establish the shortest possible acquisition time, an efficient global optimizer, or a theorem for infinite arithmetic tails.
