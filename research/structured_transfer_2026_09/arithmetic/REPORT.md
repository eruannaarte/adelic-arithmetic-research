# Oscillatory geometry improves the complete clock guarantee

The complete arithmetic clock allowance is now less than 6.416861e-8 for
the original clock rectangle, compared with the previous 1.601465e-7. This
is approximately a 2.50-fold reduction, for the entire infinite divisor
envelope on the same 8,900 readings. A new example permits sixty times the
original slope and offset errors and still recovers every one of the 49
unknown integers with both physical windows. The previous pointwise clock
bound fails the outer-window sufficient certificate at these same settings.

## The mathematical gain uses every source coefficient

The shared affine clock has slope error at most h/10^14 and offset error
at most h/10^11. Evenness of the physical window first replaces the maximum
sample-time bound by the actual weighted clock-direction norm. This lowers
the base allowance to about 8.775e-8.

The further improvement uses a complete pairing of integers: every n lies
in exactly one pair (m,2m) whose first member has even 2-adic valuation.
Each pair has exactly the phase gap log 2. A single actual weighted phase
correlation, evaluated at all four shared-clock corners, is below 2.959e-8.
Divisor multiplicativity bounds the envelope coefficient ratios within each
valuation class. Their complete masses have positive generating-series
formulas, so they can be summed without replacing the source by a finite
synthetic example. Twenty refined classes and a complete bound for all
remaining classes give a derivative norm below 6196.224551, compared with
the retained pointwise envelope below 8473.355258.

This phase step reduces the weighted-only bound by about 26.87%. A complete
second-order exponential remainder is charged separately; it is below
4.860e-18 at the original clock rectangle. The four-corner calculation keeps
the same slope and offset across every reading. The envelope ratio is never
imposed on the actual, independently variable source coefficients.

| Window | Prior pointwise clock bound | Weighted clock bound | Weighted phase bound, including nonlinear remainder |
|---|---:|---:|---:|
| Multi | <1.601465e-7 | <8.774557e-8 | <6.416482e-8 |
| Outer | <1.601465e-7 | <8.775077e-8 | <6.416861e-8 |

The same bound survives the correct nuisance projection by contraction.
The new gain is established before that projection; a sharper bound on
individual projected query directions remains a separate opportunity.
[PROOFS.md](PROOFS.md) provides the full argument and all tail identities.

## Least tested degree under the requirement fixed in advance

Hold amplitude <=4000, frequency <=3, sensor radius 4e-5, separate mismatch
radius 1e-6, the original clock rectangle, and a freshly verified normal
residual <=1e-30 fixed. Charge the complete arithmetic tail, physical Gram
floor, weighted sinusoidal approximation, digital correction and clock
distortion together. The resulting maximum coefficient-error bounds are:

| Degree | Multi | Outer | All 49 errors strictly below 1/2? |
|---:|---:|---:|---|
| 6 | 10796.119958 | 10805.524094 | No |
| 8 | 309.681865 | 309.992833 | No |
| 10 | 6.368126 | 6.422153 | No |
| 12 | 0.438350 | 0.487394 | Yes, both windows |

Degree 12 is the least passing degree among 6,8,10,12 for this contract.
The lower-degree failures concern this sufficient certificate; they neither
prove nonidentifiability nor rule out a better approximation. Degree 11 and
other untested degrees have no claim here. Increasing the degree was not
needed to exploit the better clock geometry.

## A demonstrated consequence at sixty times the clock uncertainty

Now set slope error <=6e-13 and offset error <=6e-10 while keeping the
other requirements unchanged. The sinusoidal frequency bound is enlarged
consistently to 3(1+6e-13), and arbitrary phase includes the clock offset.
Degree-12 complete clock radii are below 3.849889e-6 and 3.850117e-6.

The new readings use both nonzero clock errors at their positive endpoints,
a degree-six polynomial of size 10^20 evaluated at the true time, the
true-time sinusoid 4000 sin(3t'/890+1/3), mismatch 9e-7 cos(t'/17), and
sensor perturbation 3.9e-5 exp(it'/11). Their exact rational digitization
is separately charged to the sensor allowance. Affine composition preserves
the unrestricted polynomial nuisance exactly.

| Window | New complete coefficient-error bound | Prior pointwise clock bound on the same contract | Recovered integers |
|---|---:|---:|---:|
| Multi | <0.447818 | <0.462221 | 49/49 |
| Outer | <0.496864 | >0.511267 | 49/49 with the new bound |

The outer result turns a failed sufficient guarantee into a passed one.
It does not establish a sixty-fold improvement in maximal allowable clock
error: the previous original example did not exhaust its clock capacity.
The actual new source's timing distortion is below 1.674067e-8, still much
smaller than the full-class allowance; no finite-fixture measurement is
substituted for that allowance.

## Computational cost and validation

The physical augmented matrix has dimension 8900 by (50+p). Classical full
Gram formation costs 8900(50+p)^2 complex multiply-accumulates. Right-hand
side formation costs 8900(50+p); a dense solve has O((50+p)^3) arithmetic
cost. These are declared algorithmic counts; Arb may use different matrix
algorithms and its bit-arithmetic cost depends on precision.

| Degree | Complex solve dimension | Forward matrix entries | Full Gram multiply-accumulates | Measured matrix reconstruction, multi / outer |
|---:|---:|---:|---:|---:|
| 6 | 56 | 498400 | 27910400 | 2.47 / 3.03 s |
| 8 | 58 | 516200 | 29939600 | 2.98 / 3.14 s |
| 10 | 60 | 534000 | 32040000 | 3.30 / 3.25 s |
| 12 | 62 | 551800 | 34211600 | 3.39 / 3.44 s |

The measurements are one sequential run per degree/window on macOS arm64,
Python 3.12.14, at 320-bit precision with one BLAS/OpenMP thread. Matrix
times include actual phases, physical weights, polynomial basis, complete
tail-premise checks and Gram verification. Replaying both residual forms
took 0.217–0.227 seconds per baseline proposal. Fresh degree-12 enlarged-clock
proposals took 0.131 seconds each; their dual residual checks took about
0.227 seconds. The actual new data took 1.13 seconds to reconstruct. The
complete clock-bound producer took 0.33 seconds. These local measurements
are not universal performance guarantees.

Eight meaningful tests pass, including rejection of false decorrelation,
missing clock corners, omitted nonlinear remainder and overclaimed complete
mass. An independent consumer checks every physical clock corner and the
complete infinite mass formulas at 384 bits, including a separate zeta
power-series cross-check. Eight baseline matrices and both residual forms
were reconstructed for the fixed-degree/cost study. Both new degree-12
models, exact readings and returned proposals replay at 384 bits and retain
all 49 correct integers. The inherited 184 weighted approximation bounds,
16 remainder moments and complete arithmetic tails retain their prior
artifact bindings; they were not replaced by new sampled surrogates.

The next useful arithmetic target is to use larger multiplicative blocks
or a quotient-specific phase correlation while retaining complete masses
and the common clock. That could reduce the substantial remaining gap
between the uniform envelope and the synthetic example. Clock and mismatch
membership still require a justified model or calibration; this work does
not supply an apparatus calibration or a number-field realization.
