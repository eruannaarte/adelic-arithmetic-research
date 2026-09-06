# Per-experiment joint launch calibration protocol

**Purpose.** Supply defensible initial-state support intervals for the fixed five-reading A+B experiment and check that they imply a specified physical-query diameter. The supplied worked record is synthetic. Actual launch calibration and physical model validation remain **NOT_RUN**.

## Record the exact experiment

Use the two nominal launches A=(0.8,-0.35,0,0), B=(-0.6,0.9,0,0). A supplies theta1 and theta2 at nominal time 1 and scaled omega2 at 1.5. B supplies theta1 at 0.75 and scaled omega1 at 1.25. Do not re-prepare within a group. Both groups share one clock-dilation parameter in [-0.0001,0.0001]. The log mass and length ratios have that same source-box radius. Changing these structural assumptions needs a new certificate.

Each record has a unique experiment identifier, two distinct launch identifiers, the fixed coordinate order, unit and clock declarations, and evidence references for the source operating box, readout-noise bound, model, and time/velocity reference. The schema accepts either selected or uniform A+B budget shares; each implies its own prescribed weighted noise norm.

The count of five refers to the dynamical outputs. Initial-state measurements and characterization of the common reference add calibration acquisitions and other resources. Record those costs separately; the existing dynamical group costs are not a total experimental cost, and no total is asserted before the apparatus and metrology procedure are specified.

## Bound initial states on the launches actually used

Measure each launch's two unwrapped initial angles and two scaled physical angular velocities. Record the measured state and the time to which it refers. The theorem's velocities are sqrt(l1/g) times physical angular velocity. A derivative measured with the experiment's uncertain nominal clock must be converted with a bound that covers its entire possible clock dilation. Angle wrapping, uncertain dimensional conversion, release delay, and release-induced motion must be accounted for before constructing the interval record.

Keep the measurement timestamp and launch-origin conversion evidence in the raw records referenced by the launch's `evidence_reference`; the exact interval interface does not authenticate these external records or infer their timing.

Separate a single four-component instrument correction shared across A and B from each launch's separate bounded residual. Use signed intervals with the explicit convention:

    true initial state = measured initial state
                         + shared systematic correction
                         + launch-specific residual.

The shared vector can contain different corrections for the two angles and two velocities, but its realized values must apply to both launches. If this premise is unsupported, put the uncertainty in separate launch residuals instead. This may require a tighter specification; it must not be silently marked shared to obtain a better bound.

The local interval must include finite resolution, unshared calibration uncertainty, conversion uncertainty, and motion between the measurement and model launch origin. It may include a certified bounded operating spread if individual launches are not measured. A historical maximum or sample percentile alone is not such a support certificate. No iid assumption, normal distribution, or square-root-of-sample-size reduction is used.

## Start with the interior worked specification

The synthetic worked record provides a concrete acceptance target, not an assertion of apparatus capability:

- Local residual radius 0.000005 in all A coordinates and all B coordinates except B.theta1, whose radius is 0.000003.
- Shared instrument correction radius 0.000001 in each coordinate.
- Known offsets from nominal of (1,-1,1,-1) micro-units for A and (5,1,-1,1) micro-units for B. These are illustrative measured centers, not compulsory adjustments.
- Weighted readout-noise radius 0.0000001 and source-diameter target 0.0001.

Angles are in radians; velocity micro-units are dimensionless scaled physical velocities. The checker uses exact rational strings, not these abbreviated display values. With the declared centers this recipe has more than 35.79% target slack in every certificate row. It permits other measured centers whenever the full support remains in the original outer box; center changes alone do not worsen the ambiguity bound.

## Assess and retain the result

Save a record following [record.schema.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/record.schema.json). The [synthetic record](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/synthetic_calibration.json) is a complete shape example. Keep its evidence kind synthetic unless the content is replaced by actual launch records with independently assessable evidence. Run:

```sh
/private/tmp/math-five-paths-venv/bin/python -S research/unified_query_2026_09/preparation/calibration_bridge.py --record /absolute/path/to/record.json
```

An accepted record supplies the source-diameter bound, row slack, maximum allowed weighted readout-noise radius, and source-artifact hashes. A rejection identifies a mathematical contract failure; it is not a proof that recovery is impossible. If the bounds are too loose, the exact row inequalities identify the coordinate or noise budget to improve. Do not reduce the recorded uncertainty merely to pass.

The checker verifies mathematics conditional on declared support and model premises. Evidence-reference strings are not signatures or automatic proof of metrological provenance. A physical-record label retains an explicit requirement for external provenance and model validation. Preserve raw measurement records and the supporting calibration specifications with the assessment.

## Relationship to the existing atlas and chamber

The current chamber and atlas can test data plumbing, numerical sensitivity, synthetic adversarial support, and timing/coordinate conventions. Their internal tests do not measure launch tolerances. Their live initial-angle tube, added velocity/parameter/clock stressors, and older exact-preparation certificate have different scopes. The bridge deliberately does not accept those browser exports as calibration records. A later interface adapter should retain the distinction between a synthetic fixture, a conditional mathematical certificate, and a physically supported calibration.
