# Independent review of the normalization transfer

The proposed wrapper is mathematically sound for exact rational physical
readings and exact rational known time. The scalar computation requires no
model reconstruction beyond the already established bank premises.

Let the actual acquired physical observation be
\(y=A_j(t)u+e\), with \(\|e\|_2\le\eta\|u\|_S\) and \(S\succeq I\).
The reflecting generator is symmetric positive semidefinite. Its exponential,
the source isometry, the unit constant average and restriction to distinct rows
are contractions. Therefore

\[
\|A_j(t)S^{-1/2}\|_2\le\alpha(t)<C:=4/3,
\qquad \|y\|_2\le(C+\eta)\|u\|_S.
\]

For a positive rational multiplier \(r\), define \(z=ry\) exactly. The decoder
interprets this vector in unnormalized model coordinates, so the relevant
additional physical error is

\[
\alpha z-y=(\alpha r-1)y.
\]

Consequently the condition \(|\alpha r-1|\le\epsilon\), where
\(\epsilon=\xi/(C+\eta)<1\), certifies the existing physical allowance
\(\|\alpha z-y\|_2\le\xi\|u\|_S\). This is uniform over unknown label and
source amplitude. Equivalently, nonzero measured data gives the valid lower
bound \(\|u\|_S\ge\|y\|_2/(C+\eta)\); the wrapper does not need to estimate
that norm to apply the relative multiplier criterion.

For rational \(t,r,\epsilon\), the positive-root criterion is exactly

\[
(1-\epsilon)^4\le(1+t)r^4\le(1+\epsilon)^4.
\]

The sign checks \(r>0\) and \(0\le\epsilon<1\) are essential. Fourth powers
alone accept a negative multiplier. Since the inverse normalization lies
strictly between \(3/4\) and \(16/19\), rational bisection supplies a multiplier
for every positive requested radius. A zero radius generally cannot be achieved
with rational \(r\); it may only be claimed when exact normalization is proved.

The original sensor allowance remains \(\eta\). The decoder must be called
with the separately certified \(\xi\), after forming \(z\); neither dropping
\(\eta\) from the measured-output upper bound nor confusing normalized and
physical output errors is valid. The exact adversarial controls in
[normalization_review.py](normalization_review.py) demonstrate both failures.

Zero exact physical data can be rejected consistently with the existing
promise: the individual approximate-map floor and model error imply
\(\|A_j(t)u\|_2>(\sqrt{\mu_S}-\rho)\|u\|_S\), and every inherited
calibration has \(\sqrt{\mu_S}>\rho+\eta\). Thus no promised nonzero source
can produce zero data. The zero-vector rejection does not establish anything
about an uncalibrated observation.

The wrapper does not certify an approximate acquisition time, an error in the
sensor calibration, conversion of arbitrary floating data to the promised
physical readings, or an uncharged final rounding of its rational output.
Those are different error channels. Conversely, rationality of the data does
not require noise-free data: the existing physical sensor allowance may already
include acquisition rounding if that contract has been justified externally.

The delivered [implementation](../normalization/normalize.py) matches the
lemma. Its independently executed
[interface controls](normalization_implementation_review.py) cover 15 cases
with source-scale changes from \(10^{-100}\) to \(10^{100}\), eight malformed
receipts, seven further data/domain/budget refusals, and exact rational
normalization with zero budget. The wrapper chooses the sensor radius and
maximum numerical charge from its validated bank profile and passes the
actually charged radius to the predecessor decoder. The standalone packet
verifier validates the time and calibration stated in the packet; an external
caller must still match those fields to the acquisition being interpreted.

No mathematical blocker was found. The independent controls supplement the
bank-specific end-to-end tests; they do not replace the complete physical model
premises or certify arbitrary changes to the Python objects after validation.
