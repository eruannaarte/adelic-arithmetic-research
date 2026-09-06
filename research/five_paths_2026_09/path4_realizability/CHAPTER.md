## 4. Arithmetic constraints improve a discrete query beyond its envelope limit

The earlier observability work distinguished recoverable integer questions from unstable continuous reconstruction. Its unresolved arithmetic issue was whether coefficient patterns used to prove impossibility correspond to actual number fields. We now settle a tractable part of that issue for **all real quadratic fields**, without a discriminant ceiling, and use it to improve a query guarantee. Here a(n) counts integral ideals of norm n, and readings are values of the field's Dedekind zeta function on Re(s)=2.

There is an exact finite-prefix criterion. For any N, the coefficients a(1),…,a(N) are realizable precisely when a(1)=1, coprime multiplicativity holds, each prime coefficient belongs to{0,1,2}, and

\[
a(p^k)=\sum_{j=0}^{k}(a(p)-1)^j\qquad(p^k\le N).
\]

Every compatible prefix occurs in infinitely many distinct real quadratic fields. The proof prescribes splitting, inertia, or ramification at each relevant prime using the Chinese remainder theorem, then applies Dirichlet's theorem to a coprime progression. Thus a finite prefix can determine local arithmetic information while leaving field identity unresolved. This is a consequence of classical arithmetic, newly applied to the project's source-class question; no priority claim is made for the underlying realization principle.

For a concrete example, discriminants453,3165,381 all give a(2)=0,a(3)=1, but their a(5) values are0,1,2. Their arithmetic also forces a(20)=a(45)=a(5). In general, a(20)=a(4)a(5) and a(45)=a(9)a(5), with a(4),a(9) each1 or3. A coefficient-envelope collision changing only a(5) is therefore impossible for quadratic prefixes of length at least20.

This constraint has a measurable consequence on the same8900-observation grid used in Path3. First recover a(2),a(3), which fixes a(4),a(9). Then estimate a(5) by combining the unrounded coefficient estimates at5,20,45, with weights chosen to minimize a conservative noise-amplification bound. Complete divisor-function tails, including every integer beyond the finite sum, are retained.

For every real quadratic field, this two-stage decoder recovers a(5) under adversarial weighted observation error

\[
\|\epsilon\|_W\le\mathbf{0.02001}.
\]

The sufficient boundary is above0.02003156 in the least favorable arithmetic case. By comparison, the larger independent coefficient envelope has two allowed sources differing only at5 whose responses are distance1/25 apart. Noise of radius**0.02** makes them indistinguishable. The new actual-field guarantee strictly exceeds that envelope limit, using the same readings, measure, query, and noise norm. The gain is small; its significance is a rigorously demonstrated difference between source classes.

The appendix also gives an exact compact-set criterion for robust label recovery and a simple example where convexifying integral uncertainty collapses a positive threshold to zero. These examples are kept distinct from number-field realizability. Exact field witnesses, a rational tail/consequence checker, and a higher-precision finite-tail replay support the arithmetic result. It does not recover the whole field, establish the optimal radius, or settle realizability for higher-degree envelope extremizers.
