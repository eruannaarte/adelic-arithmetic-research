# 5. A wider time window for finite-resolution sensing

A continuum model can have a positive information floor while its discretization loses the weakest informative direction. The relevant test is therefore whether the full matrix error is smaller than the smallest continuum information value, under the same source and output calibration.

For the existing two-port Neumann benchmark, the previous certificate covered only lattice times 1≤tau≤1.2 at n=1001. We now certify **every tau∈[1,2] at the same resolution**, retaining the full diffusion–modulation generator and exactly central target. The interval length increases fivefold. The source band remains the first two cosine modes, and the interaction is V(x)=1+4x/5.

| Source metric | Uniform matrix-error upper | Uniform finite information floor |
|---|---:|---:|
| L2 | 2.55072×10^-8 | >1.17644×10^-7 |
| Continuum H1 | 2.25949×10^-9 | >1.29282×10^-9 |
| Natural discrete H1 | 2.17949×10^-9 | >1.37282×10^-9 |

The numbers are conservative summaries of exact rational endpoints. The natural discrete calculation uses its own grid-dependent energy metric; substituting the continuum metric would answer a different question.

The enabling step is an improved analytic remainder. A raw Gram entry is a product of two semigroup responses. On a tensor product space this product has the positive symmetric generator A⊗I+I⊗A. At time t≥a>0, spectral decay gives the derivative bound k!/a^k, independently of the potentially large generator norm. Combining this with the derivatives of sqrt(1+t) gives an explicit rational Taylor remainder. On the cell [1,1.5], its two-family entry bound is below 1.882×10^-11; the earlier generator-norm bound exceeds 0.00259. The improvement is more than 10^8-fold for this remainder, allowing two degree-18 Taylor cells to close the wider interval.

The proof is computationally certified rather than inferred from sampled times. Arb encloses every finite and continuum Taylor coefficient. A separate rational checker reconstructs polynomial ranges, remainders, two-by-two spectral inequalities, the gap-free time cover, and the positive transferred floors. Fresh 256-bit quadrature revalidates the inherited continuum floors. An independently implemented dense Arb matrix exponential checks small-grid coefficients and derivatives.

For example, the natural discrete row guarantees that throughout [1,2], the squared normalized response to any two-port intervention is at least 1.37282×10^-9 times its discrete H1 source cost. Thus n=1001 is an explicit sufficient resolution for this time window. It is not claimed minimal.

This result is a useful application of classical spectral and validated-numerical methods, not a new general spectral theorem. It does not extend to arbitrary source bandwidth, displaced targets, or physical local detectors. Nor can any fixed grid work for all late times: its finite response eventually decays, while the normalized continuum information remains positive. The next justified extension is target-placement robustness or a larger source band, with its smaller spectral floor explicitly included.
