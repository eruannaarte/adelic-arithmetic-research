## 1. A nonlinear experiment with bounded preparation and clock error

The original double-pendulum result certified that five observations recover two infinitesimal mass/length directions after removing one shared clock direction. It assumed exact preparation. The new result permits **finite, unknown preparation error**, a finite shared clock change, and adversarial sensor noise, and returns an explicit recovery error.

Write u=log(m2/m1), v=log(l2/l1), and let the globally shared clock multiply observation time by exp(e). Throughout |u|,|v|,|e|<=10^-4, each launch may have independent errors of at most rho=10^-7 in both initial angles and both dimensionless angular velocities. Preparation is unknown but remains common to that launch's observations. Its effect is propagated through the nonlinear equations; it is neither measured nor fitted away.

For the selected A+B experiment, outward integration encloses all relevant derivatives over this entire finite box. A fixed, exactly computed weighted left inverse B has uniform Jacobian-deviation norm k<0.077461. Separately certified preparation-output bounds E and the weighted sensor-noise bound ||W^(1/2)n||_2<=eta yield

\[
\|s-s'\|_\infty\le
\frac{2\max_i\{\sum_j|B_{ij}|E_j+
\eta\sqrt{\sum_j B_{ij}^2/w_j}\}}{1-k},
\qquad s=(u,v,e).
\]

This holds for any two parameter vectors consistent with the same observations and allowed uncertainties. Thus any feasible estimate lies within the stated error of the true parameters. The clock remains one shared nuisance; its nonlinear change is included in the derivative bounds rather than removed using an unavailable true-state projector.

At eta=10^-7, the worked comparison is:

| Budget allocation | Certified maximum parameter error |
|---|---:|
| Selected A+B, shares (2/3,1/3,0) | <2.011628e-5 |
| Uniform A+B+C, shares (1/3,1/3,1/3) | <2.489142e-5 |
| Uniform A+B, shares (1/2,1/2,0) | <1.979238e-5 |

All designs have the same seven available local sensors, additive group costs, total budget, and noise rule. The selected design improves the sufficient bound relative to uniform use of all groups, but uniform A+B slightly improves the preparation-dominated bound. Earlier optimality for a different local-information objective therefore supplies no blanket ranking under uncertainty. Conversely, for a required error of 10^-4, the selected design certifies a larger noise allowance than either uniform comparison: approximately 5.68e-6 versus 4.40e-6 and 5.08e-6. Exact half-plane inequalities describe the preparation/noise tradeoff.

The proof uses outward Picard–Taylor tubes and a separate rational checker; alternate time partitions, independent mechanical evaluations, and finite nonlinear controls pass. This is a finite neighbourhood certificate, extending the earlier point-derivative result. The preparation tolerance is small and unvalidated experimentally. The comparison concerns proved sufficient bounds, not actual minimax errors, global parameter recovery, or apparatus performance. A larger region requires sharper enclosures or additional preparation measurements.
