# Independent audit: joint preparation-calibration bridge

Auditor: `/root/polynomial_drift`, 2026-09-05. **Verdict: the conditional diameter theorem, record checker and quantitative synthetic specification are supported. No mathematical or implementation defect remains.** This review added explicit documentation of calibration acquisition costs and the infinity-norm diameter interpretation; neither change altered the numerical certificate. Physical calibration remains **NOT_RUN**.

## Source, clock and finite-flow connection

The source coordinates are the two log ratios and one shared clock parameter. The full ODE is scaled by \(e^\epsilon\) with respect to nominal time. The initial velocity coordinates are physical angular velocities multiplied by \(\sqrt{l_1/g}\), so they are distinct from angular derivatives with respect to the uncertain nominal clock. The record contract and protocol preserve that convention and require conversion errors to cover the whole admissible clock range. The two fixed launch states, five output coordinates, sample times, group costs and weights match the inherited A+B experiment.

The derivative premises cover the entire source box of radius \(10^{-4}\) and preparation box of radius \(10^{-5}\). They are finite-box flow enclosures, not a nominal linearization used beyond its certified domain. The new bridge reconstructs its decoder and gains from those artifacts and invokes the prior exact verifier. The recorded nominal and two preparation-box outward ODE replays were performed during this extension. I did not repeat those unchanged deep integrations; I checked their explicit validation record and reviewed the new use of their derivative bounds.

Splitting the difference between two consistent worlds into a source segment at fixed preparation and a preparation segment at fixed source is valid. These intermediate points need only lie in the globally validated outer box; the proof does not require a possibly source-correlated physical nuisance law to realize each intermediate point. The box bounds cover those paths, and the actual endpoints retain their joint calibration incidence.

## Known centers and shared systematic uncertainty

The model \(p_A=m_A+b+v_A\), \(p_B=m_B+b+v_B\) properly separates measured centers from unknown widths. Asymmetric correction intervals are recentered by moving their midpoints into the known offsets. The containment test pays \(|m|+\sigma+r\) in every coordinate. Thus known-center information is not used to leave the inherited domain. When comparing worlds consistent with one record, the centers cancel and the support widths alone bound their difference.

The common systematic vector is differentiated through both launch preparations. Summing those signed columns before taking absolute values is necessary and is exactly what the checker does. The local residual columns remain separate. The triangle-inequality comparison to independent launch offsets is conservative, with no assumed probabilistic independence or averaging law. Source dependence or correlation of the residuals does not invalidate a containing deterministic support.

I independently reconstructed, using only exact rational arithmetic and the raw nominal/finite-box artifacts, the identity \(BA=I\), every source-contraction row, all local and common preparation gains, and the weighted noise-gain inequalities. The direct common-column sum includes all five sensor rows, rather than importing the bridge's assembled common gains. All reconstructed values match the certificate.

I also reparameterized the synthetic record with asymmetric common and local correction intervals, compensated their midpoints in the measured states, and verified that the same joint physical support yields identical centers, widths, outer extents, row loads and diameter. This exercises the signed correction convention beyond symmetric fixture intervals.

## Diameter proof, noise budget and reported gain

After applying the fixed decoder, the source difference satisfies \(x\le Rx+v\) componentwise. Choosing an index attaining \(\|x\|_\infty\) gives the displayed maximum of the rowwise quotients, rather than an invalid inversion of a signed interval matrix. Every row has contraction below one. The target inequalities and the solved readout-noise boundary follow exactly. Equality at the fixed-certificate noise boundary is admissible because the target is a non-strict diameter inequality; the next larger rational noise budget is rejected by the tests.

The certificate gives source diameter approximately \(6.0052210651\times10^{-5}\) in the infinity norm. The physical query is the pair of log parameters \((u,v)\), whose coordinate projection cannot increase that norm. This is a consistent-set diameter statement. The proof and report now explicitly avoid claiming a half-diameter error for a particular point estimator without an independently justified inverse or enclosing center. No Euclidean norm or exponentiated physical ratio is silently substituted.

The independently reconstructed normalized row loads are approximately 0.6420269184, 0.6051979067 and 0.2874388387. The fixed sufficient weighted noise boundary is approximately \(2.4787859584\times10^{-6}\). The boundary is exact for the supplied row inequalities and their rounded-up gains; it is not a sharp nonlinear minimax threshold. The zero-centered enclosing-box control deliberately enlarges the support and fails a sufficient row test. It is not a claim that the actual calibrated support becomes unrecoverable. The independent-offset control likewise tests loss of a specific correlation premise.

## Calibration meaning, resources and record truthfulness

The five readings are the dynamical outputs. Measuring initial states and characterizing a common instrument reference add acquisitions and calibration resources. The existing group costs do not include these tasks. The proof, report and calibration protocol now state that full cost remains to be determined for a selected apparatus and metrology procedure. This matters when comparing the bridge with an uncalibrated experiment.

The release-time transport calculation is dimensionally and mathematically correct: an initial physical scaled velocity bound \(V\), acceleration bound \(A\), and physical dimensionless delay \(h\) imply changes bounded by \(Ah\) in velocity and \(Vh+Ah^2/2\) in angle. Those bounds require their own evidence. The protocol retains measurement timestamps and launch-origin conversion evidence in referenced raw records; the algebraic interface cannot authenticate them.

The checker strictly validates shapes, exact rational strings, unit and clock contracts, four-coordinate incidence, two distinct launch identifiers, no re-preparation within grouped readings, support containment, and mathematical budget gates. Source artifacts are cached by immutable byte contents and reparsed before exposure, so mutation of a returned object does not poison subsequent validation. Evidence-reference strings are required but are not treated as proof of their contents. A record labelled physical still receives an explicit external-provenance/model-validation requirement. The supplied record remains labelled synthetic.

A finite sequence of successful calibration trials cannot certify a future worst-case support without an additional operating-envelope premise or an observation of the actual launch. The stated counterexample correctly illustrates this. Browser simulations and their internal integrator or adversarial checks do not supply physical metrology, and the package does not promote them into such evidence.

## Executed validation

The standard-library exact bridge replay and all ten tests passed in fresh processes under `python -S`. The independent derivative/gain reconstruction, asymmetric interval control and exact numerical consequences are recorded in [independent_audit_checks.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/independent_audit_checks.json). The three inherited full ODE replays retain the explicit recorded status described above. No changes to prior artifacts were needed.

The supported result is therefore a conditional mathematical route from defensible joint calibration records to a query-diameter guarantee, together with a synthetic interior specification that has substantial margin. Actual apparatus tolerances, readout noise support, external time reference and model adequacy remain empirical inputs to be supplied.
