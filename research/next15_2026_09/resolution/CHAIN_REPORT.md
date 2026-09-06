# From exact placement to an explicit restricted readout

The earlier finite-resolution result certified a two-source Neumann model only at an exactly central target. It compared three source calibrations with the weakest continuum information value, using n=1001 and every lattice time in[1,2]. These three adaptive cycles preserve that generator, source band, and time interval while addressing successively different operational questions: moving the target, locating an unknown target, and restricting the observation operator. Each objective was recorded before its confirmatory work; successors were selected from the preceding result's unresolved limitation.

## R1. Placement robustness from graph locality

The first question was whether the central guarantee survives substantial target displacement. A direct phase-error estimate would discard cancellations between target modes and can overwhelm the small information floor. Instead, the product defining each Gram entry was lifted to a weighted graph semigroup on one transverse coordinate and two source coordinates. Its generator retains the full noncommuting diffusion and modulation terms.

Uniformizing this graph produces a symmetric stochastic matrix. Target-diagonal blocks of its powers agree under interior translation until a closed walk can reach a boundary, encounter its changed diagonal, and return. For a target at boundary distance d, the first possible discrepancy is at order2d+1. The remaining exponential series has an explicit rational bound. This is a structural finite-propagation argument, not a sampled sweep over target positions.

At d=41, the full two-by-two Gram error is below3.252891e-12 for every time in[1,2]. Therefore all919 targets indexed41 through959 retain more than99% of every inherited finite information floor. Conservative floors are1.1764156e-7 in L2,1.2895680e-9 in continuum H1, and1.3695765e-9 in natural discrete H1. The same proof adds the placement error to each finite-to-continuum error bound.

Exact small-graph matrix powers confirm both agreement through the predicted order and the first boundary-sensitive discrepancy. A dense Arb matrix exponential supplies a separate finite-time control. Boundary targets fail the translation identity already at first order. The guard distance is sufficient, not optimal. More importantly, this result controls each realized target separately; it does not provide a decoder when that target is unknown.

## R2. Recovering an unknown location before the source

That distinction determined the second objective. The full modal response can be transformed orthogonally into spatial coordinates without changing its Euclidean noise norm. On an infinite transverse lattice, the response is reflection-symmetric about the target for every combination of the two source modes. Its energy centroid therefore equals the target even when those source modes cancel strongly.

A new first-moment walk bound controls the finite lattice's departure from that symmetry. Unlike R1's closed-walk argument, it compares complete output vectors and weights the remainder by walk length. Dividing the resulting energy-moment error by the certified source floor controls the noiseless centroid uniformly over all nonzero source directions. A separate deterministic inequality controls centroid perturbation by sensor noise.

For any unknown target from47 through953, relative output noise of1e-4 still leaves total centroid error below0.279067 cells. Rounding identifies the integer target exactly. The decoder then uses the correctly selected two-column least-squares inverse. An absolute allowance of3e-8 per unit L2 source norm, or3e-9 per unit of either H1 source norm, gives relative source error below1e-4. These are different calibrated statements, not interchangeable physical noise specifications.

A direct1002001-state graph simulation at target47, time2, and source(3/5,4/5) recovers the target under its recorded sensor perturbation. It is labelled a floating regression, while the guarantee comes from the analytic inequalities and exact checker. Zero source remains a necessary exclusion: all targets then give identical observations. Likewise, no positive absolute noise tolerance can localize arbitrarily small sources without an amplitude lower bound. R2 solves unknown discrete placement but still uses the full spatial output.

## R3. A smaller observation operator with a declared placement prior

The third objective followed from that remaining cost and from the centroid bound's long spatial lever arm. With additional prior information that the target lies within ten cells of500, the observation operator was restricted to one spatial window. A walk cannot contribute outside this window before crossing its guard margin. The discarded operator therefore has a controlled norm, and its Gram loss is positive semidefinite. A second bound controls the discarded energy's first moment; no renormalization is introduced after restriction.

The resulting window451 through549 has99 channels. Its information loss is below4.923987e-12, retaining more than99% of the original central floors in all three metrics. Relative window-output noise of1e-3 gives centroid error below0.198181 cells. Source-relative allowances3e-7 in L2 or3e-8 in H1 then give relative source error below1e-3. A full-grid regression with noise along the least singular observed direction recovers target510 and has source error about0.000150794.

This is not a proof that99 channels are necessary. Two distinct channels placed symmetrically about a central target, however, are exactly identical source functionals and have rank at most one. That obstruction motivates the next unexecuted question: certify a smaller asymmetric spatial bank with the same target prior and calibrated recovery margin.

The acquisition distinction matters. Off-center targets generally activate odd modes absent at exact center. The full output representation has1001 spatial coordinates, equivalent to1000 potentially nonzero modes. Each proposed spatial channel still averages globally across the source coordinate. Direct99-channel acquisition requires those readouts to be available; forming them from already acquired modal data is only post-processing. The package proves three model-specific extensions, with eleven focused controls and exact consequence checks, without claiming hardware validation, arbitrary bandwidth, timing robustness, or a literature-priority result.
