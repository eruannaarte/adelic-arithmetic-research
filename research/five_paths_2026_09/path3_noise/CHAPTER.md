## 3. Arithmetic sensing: bias improvement survives some noise, while variance rises

The multiscale arithmetic sensor previously recovered 50 integer coefficients from 8,900 complex observations with certified noiseless error below 0.498028. That narrow margin below one half left an essential question: does any useful guarantee survive actual measurement error?

The new calculation follows noise through the implemented weighted decoder, retaining the complete arithmetic tail and Gram bounds. The 2,550 short-window samples are already among the 8,900 long-window observations. Their weights are added before computing covariance; they do not provide independent copies of the sensor noise.

For coefficient n, let b_n be the complete deterministic bias bound, and let q<1 bound the Gram defect. If the sensor error satisfies

\[
\sum_j w_j|\epsilon_j|^2\le\eta^2,
\]

then its decoded contribution has magnitude at most n²η/√(1−q). Provided every b_n<1/2, all 50 integers are recovered by rounding whenever

\[
\eta^2<\min_{1\le n\le50}
\frac{(1/2-b_n)^2(1-q)}{n^4}.
\]

The multiscale certificate permits η<7.88735×10⁻⁷; the declared rational radius **7×10⁻⁷** passes strictly. For identical assumptions across designs, a common bound |ε_j|≤7×10⁻⁷ on every physical reading implies both designs' weighted bounds because both weight vectors have total mass one. The single-window control's existing bias bound is approximately 0.595929, so this calculation cannot certify its rounding even without noise. That is an insufficient certificate, not an impossibility result.

Under the separate assumption of independent circular complex Gaussian errors with E|ε_j|²=10⁻¹⁰, exact covariance propagation and a union bound give probability of any rounding failure below **5.466×10⁻¹⁴** for multiscale sensing. This probability includes the deterministic tail bias. It depends on the stated distribution; it is not an adversarial-noise guarantee or a measured hardware error rate.

The comparison also disproves a tempting blanket advantage. For coefficient 50, outward variance bounds prove

\[
\frac{\operatorname{Var}_{\rm multiscale}}
{\operatorname{Var}_{\rm single}}>1.000265975.
\]

Multiscale weighting improves the bias certificate while increasing this coefficient's iid noise variance. Treating the nested readings as independent would incorrectly remove a covariance term; a direct numerical check shows that omission understates the squared-weight sum by roughly 0.51%.

The extension consists of explicit noise tolerances, a distribution-specific probability guarantee, and a certified bias–variance tradeoff at equal acquisition budget. A separate rational checker verifies the decisive inequalities; complete finite and infinite arithmetic-tail reconstructions establish their inputs. The results apply to the degree-14 coefficient envelope and its verified arithmetic subclasses. Physical noise calibration, extra decoder-rounding error, and broader claims of statistical superiority remain separate questions.
