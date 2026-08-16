"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const core = require("./wind-tunnel-core.js");

function maxAbsolute(values) {
  return Math.max(...values.map(Math.abs));
}

function maximumStateDifference(left, right) {
  assert.equal(left.states.length, right.states.length);
  let maximum = 0;
  for (let index = 0; index < left.states.length; index += 1) {
    for (let component = 0; component < 4; component += 1) {
      maximum = Math.max(maximum, Math.abs(left.states[index][component] - right.states[index][component]));
    }
  }
  return maximum;
}

function scaledEnergyDrift(trajectory, parameters) {
  const initial = core.energy(trajectory.states[0], parameters);
  const scale = Math.max(1, Math.abs(initial));
  return Math.max(...trajectory.states.map(state => Math.abs(core.energy(state, parameters) - initial) / scale));
}

test("mechanics preserve the hanging equilibrium and rigid-rod geometry", () => {
  const p = core.DEFAULT_PARAMETERS;
  assert.deepEqual(core.rhs(0, [0, 0, 0, 0], p), [0, 0, -0, 0]);

  const state = [0.73, -1.21, 0.4, -0.7];
  const positions = core.bobPositions(state, p);
  const firstLength = Math.hypot(
    positions.bob1[0] - positions.pivot[0],
    positions.bob1[1] - positions.pivot[1]
  );
  const secondLength = Math.hypot(
    positions.bob2[0] - positions.bob1[0],
    positions.bob2[1] - positions.bob1[1]
  );
  assert.ok(Math.abs(firstLength - p.l1) < 1e-14);
  assert.ok(Math.abs(secondLength - p.l2) < 1e-14);
});

test("the declared mechanical energy has zero directional derivative along the ODE", () => {
  const p = core.DEFAULT_PARAMETERS;
  const state = [0.83, -0.47, 0.61, -0.92];
  const flow = core.rhs(0, state, p);
  const step = 2e-7;
  const plus = state.map((value, index) => value + step * flow[index]);
  const minus = state.map((value, index) => value - step * flow[index]);
  const derivative = (core.energy(plus, p) - core.energy(minus, p)) / (2 * step);
  assert.ok(Math.abs(derivative) < 2e-7, `dE/dt = ${derivative}`);
});

test("fixed-step forecast and adaptive outcome solvers agree on a regular launch", () => {
  const p = core.DEFAULT_PARAMETERS;
  const times = core.makeTimes(3, 121);
  const initial = [0.8, -0.35, 0.15, -0.22];
  const fixed = core.simulateRK4(initial, times, p, 1 / 320);
  const adaptive = core.simulateAdaptive(initial, times, p);

  assert.ok(maximumStateDifference(fixed, adaptive) < 2e-7);
  assert.ok(scaledEnergyDrift(fixed, p) < 2e-8);
  assert.ok(scaledEnergyDrift(adaptive, p) < 2e-9);
  assert.ok(adaptive.accepted > 0);
});

test("information gains are the square roots of the response-Gram eigenvalues", () => {
  const information = core.informationFromGradients([
    [1, 0], [0, 2], [-1, 0], [0, -2]
  ]);

  assert.deepEqual(information.gram, [[0.5, 0], [0, 2]]);
  assert.ok(Math.abs(information.weakestGain - Math.sqrt(0.5)) < 1e-14);
  assert.ok(Math.abs(information.strongestGain - Math.sqrt(2)) < 1e-14);
  assert.ok(Math.abs(
    information.strongestDirection[0] * information.weakestDirection[0]
      + information.strongestDirection[1] * information.weakestDirection[1]
  ) < 1e-14);
  assert.ok(Math.abs(Math.hypot(...information.strongestDirection) - 1) < 1e-14);
  assert.ok(Math.abs(Math.hypot(...information.weakestDirection) - 1) < 1e-14);
});

test("centred finite-difference responses converge when their step is halved", () => {
  const shared = {
    initialState: [0.8, -0.35, 0.1, -0.05],
    duration: 1.25,
    sampleCount: 61,
    sensor: "tip-x",
    forecastStep: 1 / 240,
    preparationRadius: 1e-4,
    noiseRadius: 1e-6
  };
  const coarse = core.forecastExperiment({ ...shared, derivativeStep: 4e-5 });
  const fine = core.forecastExperiment({ ...shared, derivativeStep: 2e-5 });
  const differences = coarse.gradients.flatMap((row, index) => row.map(
    (value, axis) => value - fine.gradients[index][axis]
  ));
  assert.ok(maxAbsolute(differences) < 2e-7, `max response discrepancy ${maxAbsolute(differences)}`);
});

test("held-out perturbation has the declared radius and matches the local forecast at small radius", () => {
  const forecast = core.forecastExperiment({
    initialState: [0.8, -0.35, 0.1, -0.05],
    duration: 1.5,
    sampleCount: 91,
    sensor: "tip-x",
    preparationRadius: 1e-5,
    noiseRadius: 2e-7,
    derivativeStep: 1e-5,
    forecastStep: 1 / 320
  });
  const outcome = core.runIndependentOutcome(forecast, [3, 4]);
  const initialDifference = outcome.actual.states[0].slice(0, 2).map(
    (value, axis) => value - forecast.config.initialState[axis]
  );

  assert.ok(Math.abs(Math.hypot(...initialDifference) - forecast.config.preparationRadius) < 1e-15);
  assert.ok(Math.abs(outcome.actualAmplification - outcome.predictedAmplification) < 3e-4);
  assert.ok(outcome.coverage > 0.99);
  assert.ok(outcome.refinementDiscrepancy < 2e-8);
  assert.ok(outcome.maxEnergyDrift < 2e-9);
  const expectedClassification = outcome.endpointDistance <= 2 * forecast.config.noiseRadius
    ? "confusable at the declared endpoint noise"
    : "separated at the declared endpoint noise";
  assert.equal(outcome.classification, expectedClassification);

  // These are numerical methods, not proof-producing or outward-enclosure paths.
  assert.doesNotMatch(forecast.method, /certif|proof|enclos/i);
  assert.doesNotMatch(outcome.method, /certif|proof|enclos/i);
});

test("active recommendation maximizes the declared post-measurement Gram floor", () => {
  const times = [0, 1, 2, 3];
  const currentGram = [[0.1, 0.02], [0.02, 0.05]];
  const gradientsBySensor = {};
  core.SENSORS.forEach((sensor, sensorIndex) => {
    gradientsBySensor[sensor.id] = times.map((_, timeIndex) => [
      (sensorIndex + 1) * (timeIndex + 1) / 10,
      (7 - sensorIndex) * (4 - timeIndex) / 13
    ]);
  });

  const recommendation = core.recommendNextExperiment(currentGram, gradientsBySensor, times);
  let expected = null;
  const gain = 1 / times.length;
  for (const sensor of core.SENSORS) {
    for (let index = 1; index < times.length; index += 1) {
      const [x, y] = gradientsBySensor[sensor.id][index];
      const floor = core.eigen2x2(
        currentGram[0][0] + gain * x * x,
        currentGram[0][1] + gain * x * y,
        currentGram[1][1] + gain * y * y
      )[0];
      if (!expected || floor > expected.floor) expected = { sensor: sensor.id, time: times[index], floor };
    }
  }

  assert.equal(recommendation.sensor, expected.sensor);
  assert.equal(recommendation.time, expected.time);
  assert.ok(Math.abs(recommendation.informationFloor - expected.floor) < 1e-15);
  assert.ok(recommendation.informationFloor >= core.eigen2x2(0.1, 0.02, 0.05)[0]);
  assert.ok(Math.abs(recommendation.weakestGain - Math.sqrt(recommendation.informationFloor)) < 1e-15);
});

test("public numerical entry points reject inputs that could invalidate evidence semantics", () => {
  const times = core.makeTimes(1, 11);
  assert.throws(() => core.simulateRK4([0, 0, 0, 0], times, undefined, 0), RangeError);
  assert.throws(() => core.simulateRK4([0, 0, 0, 0], times, undefined, -0.01), RangeError);
  assert.throws(() => core.simulateAdaptive([0, 0, 0, 0], [0, 0.5, 0.5]), RangeError);
  assert.throws(() => core.simulateAdaptive([0, 0, 0, 0], times, undefined, { initialStep: 0 }), RangeError);
  assert.throws(() => core.simulateAdaptive([0, 0, 0, 0], times, undefined, { maxStep: -1 }), RangeError);
  assert.throws(() => core.forecastExperiment({ derivativeStep: 0 }), RangeError);
  assert.throws(() => core.forecastExperiment({ preparationRadius: -0.1 }), RangeError);
  assert.throws(() => core.forecastExperiment({ noiseRadius: -0.1 }), RangeError);
  const forecast = core.forecastExperiment({ duration: 0.2, sampleCount: 9 });
  assert.throws(() => core.runIndependentOutcome(forecast, [0, 0]), RangeError);
  assert.throws(() => core.runIndependentOutcome(forecast, [1, NaN]), TypeError);
});

test("seed streams and all six structured laws are deterministic and bounded", () => {
  const first = core.createSeededPRNG("seed-a");
  const second = core.createSeededPRNG("seed-a");
  const sequence = Array.from({ length: 8 }, () => first());
  assert.deepEqual(sequence, Array.from({ length: 8 }, () => second()));
  assert.notEqual(core.deriveSeed("master", "member", 0), core.deriveSeed("master", "member", 1));
  assert.equal(core.structuredLawValue("off", 0.4, 2), 0);
  assert.equal(core.structuredLawValue("linear", -0.4, 2), -0.4);
  assert.equal(core.structuredLawValue("quadratic", 0, 2), -1);
  assert.ok(Math.abs(core.structuredLawValue("sinusoidal", 0.5, 2) - 1) < 1e-15);
  assert.equal(core.structuredLawValue("radial", 0, 2), -1);
  assert.equal(core.structuredLawValue("geometric", 0, 2), 0);
  for (const law of core.ENSEMBLE_LAWS) {
    for (let index = 0; index <= 20; index += 1) {
      assert.ok(Math.abs(core.structuredLawValue(law, -1 + index / 10, 2)) <= 1 + 1e-15);
    }
  }
});

test("ensemble declarations are canonical, committed, and reject tampering", () => {
  const forecast = core.forecastExperiment({ duration: 0.3, sampleCount: 13 });
  const options = {
    size: 4,
    seed: "canonical",
    uncertainty: { kind: "bounded", scale: 0.003 },
    structured: { law: "geometric", alpha: 0.002, direction: "custom", customDirection: [3, 4] }
  };
  const left = core.buildEnsembleDeclaration(forecast, options);
  const right = core.buildEnsembleDeclaration(forecast, options);
  assert.deepEqual(left, right);
  assert.equal(left.structured.alphaRadians, 0.002);
  assert.deepEqual(left.structured.directionVector, [0.6, 0.8]);
  assert.equal(left.members[0].s, -1);
  assert.equal(left.members[3].s, 1);
  const tampered = structuredClone(left);
  tampered.members[0].structuredOffset[0] += 1e-3;
  assert.throws(() => core.runEnsemble(forecast, tampered), /commitment mismatch/);

  const rebound = structuredClone(left);
  rebound.q0[0] += 0.1;
  const reboundPayload = { ...rebound }; delete reboundPayload.declarationId;
  rebound.declarationId = core.checksum(core.stableSerialize(reboundPayload));
  assert.throws(() => core.runEnsemble(forecast, rebound), /not bound to the supplied frozen forecast semantics/);

  const mutatedForecast = structuredClone(forecast);
  mutatedForecast.gradients[2][0] += 0.01;
  assert.throws(() => core.runEnsemble(mutatedForecast, left), /not bound to the supplied frozen forecast semantics/);

  const samplingTamper = structuredClone(left);
  samplingTamper.realism.sensor.samplingLaw = "an undeclared alternative draw";
  const samplingPayload = { ...samplingTamper }; delete samplingPayload.declarationId;
  samplingTamper.declarationId = core.checksum(core.stableSerialize(samplingPayload));
  assert.throws(() => core.runEnsemble(forecast, samplingTamper), /sampling law or support is noncanonical/);
});

test("complete public result and laboratory commitments reject visible evidence tampering", () => {
  const forecast = core.forecastExperiment({ duration: 0.25, sampleCount: 11, preparationRadius: 0.001, noiseRadius: 0.001 });
  const result = core.runEnsemble(forecast, { size: 3, seed: "result-integrity", retainTrajectories: true });
  assert.equal(core.verifyEnsembleResult(result).valid, true);
  const payload = {
    schemaVersion: result.schemaVersion,
    declaration: result.declaration,
    comparisonBaseline: result.comparisonBaseline,
    members: result.members,
    summary: result.summary
  };
  assert.equal(result.resultId, core.checksum(core.stableSerialize(payload)));
  const sensorTamper = structuredClone(result);
  sensorTamper.members[0].actualSensorSeries[2] += 0.001;
  assert.throws(() => core.verifyEnsembleResult(sensorTamper), /retained ensemble series|complete public scientific payload/);

  const study = core.runLaboratoryStudy({
    forecast,
    ensembleOptions: { uncertainty: { kind: "bounded", scale: 0 }, retainTrajectories: false },
    sizes: [2, 3], horizons: [0.25], laws: ["off"], amplitudes: [0], repeats: 1, baseSeed: "study-integrity"
  });
  assert.equal(core.verifyLaboratoryResult(study).valid, true);
  const studyTamper = structuredClone(study);
  studyTamper.cells[0].aggregate.sampleCoverage.mean = 0.123;
  assert.throws(() => core.verifyLaboratoryResult(studyTamper), /aggregate|complete public scientific payload/);
  const compactMemberTamper = structuredClone(study);
  compactMemberTamper.cells[0].runs[0].members[0].audit.coverage *= 0.5;
  const compactRun = compactMemberTamper.cells[0].runs[0];
  const compactRunPayload = { ...compactRun }; delete compactRunPayload.resultId;
  compactRun.resultId = core.checksum(core.stableSerialize(compactRunPayload));
  const compactStudyPayload = { ...compactMemberTamper }; delete compactStudyPayload.studyId;
  compactMemberTamper.studyId = core.checksum(core.stableSerialize(compactStudyPayload));
  assert.throws(
    () => core.verifyLaboratoryResult(compactMemberTamper),
    /compact laboratory member scientific payload integrity mismatch/
  );
  const duplicateCell = structuredClone(study);
  duplicateCell.cells[1] = structuredClone(duplicateCell.cells[0]);
  const duplicatePayload = { ...duplicateCell }; delete duplicatePayload.studyId;
  duplicateCell.studyId = core.checksum(core.stableSerialize(duplicatePayload));
  assert.throws(() => core.verifyLaboratoryResult(duplicateCell), /duplicated|incomplete/);
  const seedTamper = structuredClone(study);
  seedTamper.baseSeed = "different-base-seed";
  const seedPayload = { ...seedTamper }; delete seedPayload.studyId;
  seedTamper.studyId = core.checksum(core.stableSerialize(seedPayload));
  assert.throws(() => core.verifyLaboratoryResult(seedTamper), /repeat seed|noncanonical/);
});

test("zero realism and law off produce identical members with exact zero draws", () => {
  const forecast = core.forecastExperiment({ duration: 0.4, sampleCount: 17, preparationRadius: 0, noiseRadius: 0 });
  const declaration = core.buildEnsembleDeclaration(forecast, {
    size: 5,
    seed: "ideal",
    uncertainty: { kind: "bounded", scale: 0 },
    structured: { law: "off", alpha: 0 },
    retainTrajectories: true
  });
  const result = core.runEnsemble(forecast, declaration);
  assert.equal(declaration.uncertainty.distribution, "deterministic-zero");
  assert.equal(declaration.uncertainty.requestedDistribution, "uniform-disk");
  for (const member of result.members) {
    assert.deepEqual(member.draws.angleOffset, [0, 0]);
    assert.deepEqual(member.draws.velocityOffset, [0, 0]);
    assert.deepEqual(member.draws.parameterLogOffsets, [0, 0, 0, 0, 0]);
    assert.equal(member.draws.clockFraction, 0);
    assert.ok(member.draws.sensorNoise.every(value => value === 0));
    assert.deepEqual(member.actualSensorSeries, result.members[0].actualSensorSeries);
  }
  assert.equal(result.summary.coverage.wilson95, null);
  assert.equal(result.summary.gates.status, "resolved");
});

test("structured offsets vary known centres independently of stochastic realism", () => {
  const forecast = core.forecastExperiment({ duration: 0.3, sampleCount: 13, preparationRadius: 0, noiseRadius: 0 });
  const result = core.runEnsemble(forecast, {
    size: 3,
    seed: "structure",
    uncertainty: { kind: "bounded", scale: 0 },
    structured: { law: "linear", alpha: 0.02, direction: "custom", customDirection: [1, 0] },
    retainTrajectories: true
  });
  assert.deepEqual(result.members.map(member => member.structuredOffset[0]), [-0.02, 0, 0.02]);
  assert.deepEqual(result.members.map(member => member.initialState[0]), [0.78, 0.8, 0.8200000000000001]);
  assert.notDeepEqual(result.members[0].structuredCentreSeries, result.members[2].structuredCentreSeries);
});

test("velocity, positive parameter, clock, and sensor realism draws alter outcomes and remain explicit", () => {
  const forecast = core.forecastExperiment({ duration: 0.4, sampleCount: 17, preparationRadius: 0, noiseRadius: 0 });
  const result = core.runEnsemble(forecast, {
    size: 3,
    seed: "realism",
    uncertainty: { kind: "bounded", scale: 0 },
    structured: { law: "off", alpha: 0 },
    realism: {
      velocity: { kind: "bounded", scale: 0.04 },
      parameters: { kind: "bounded", scale: 0.02 },
      clock: { kind: "bounded", scale: 0.01 },
      sensor: { kind: "bounded", scale: 0.005 }
    },
    retainTrajectories: true
  });
  assert.ok(result.members.some(member => member.draws.velocityOffset.some(value => value !== 0)));
  assert.ok(result.members.every(member => Object.values(member.parameters).every(value => value > 0)));
  assert.ok(result.members.some(member => member.draws.parameterMultipliers.some(value => value !== 1)));
  assert.ok(result.members.some(member => member.draws.clockFraction !== 0));
  assert.ok(result.members.some(member => member.draws.sensorNoise.some(value => value !== 0)));
  assert.ok(result.members.some(member => member.memberTimes.at(-1) !== forecast.times.at(-1)));
  assert.notDeepEqual(result.members[0].actualSensorSeries, result.members[1].actualSensorSeries);
  assert.match(result.declaration.predictionBoundary, /unpropagated stressors/);
  assert.equal(result.declaration.uncertainty.samplingLaw, "deterministic zero initial-angle two-vector");
  assert.match(result.declaration.realism.velocity.samplingLaw, /uniform-by-area.*Euclidean disk/);
  assert.match(result.declaration.realism.velocity.support, /velocityOffset.*scale radians\/second/);
  assert.match(result.declaration.realism.parameters.samplingLaw, /componentwise uniform log-coordinate/);
  assert.match(result.declaration.realism.parameters.support, /exp\(-scale\),exp\(scale\)/);
  assert.match(result.declaration.realism.clock.samplingLaw, /uniform fractional-clock draw/);
  assert.match(result.declaration.realism.sensor.samplingLaw, /uniform draws.*each nominal sample/);
});

test("N=1 default ensemble preserves the legacy held-out outcome", () => {
  const forecast = core.forecastExperiment({ duration: 0.5, sampleCount: 21, preparationRadius: 0.002, noiseRadius: 0.001 });
  const legacy = core.runIndependentOutcome(forecast);
  const ensemble = core.runEnsemble(forecast, { size: 1, retainTrajectories: true });
  assert.deepEqual(ensemble.members[0].actualSensorSeries, legacy.actualSensor);
  assert.equal(ensemble.members[0].audit.coverage, legacy.coverage);
  assert.ok(Math.abs(ensemble.members[0].audit.amplification.actual - legacy.actualAmplification) < 1e-14);
  assert.equal(
    ensemble.declaration.uncertainty.samplingLaw,
    "deterministic held-out boundary direction derived from the frozen initial state"
  );
  assert.equal(ensemble.declaration.uncertainty.distribution, "deterministic-held-out-boundary");
  assert.equal(ensemble.declaration.uncertainty.requestedDistribution, "uniform-disk");
  assert.equal(ensemble.declaration.uncertainty.support, "||angleOffset||_2 = scaleRadians radians");
  assert.ok(Math.abs(Math.hypot(...ensemble.members[0].draws.angleOffset) - forecast.config.preparationRadius) < 1e-15);
});

test("probabilistic bands combine independent angle and sensor variance and label Wilson event", () => {
  const forecast = core.forecastExperiment({ duration: 0.3, sampleCount: 13, preparationRadius: 0, noiseRadius: 0 });
  const declaration = core.buildEnsembleDeclaration(forecast, {
    size: 8,
    seed: "probability",
    uncertainty: { kind: "probabilistic", scale: 0.002, confidenceMultiplier: 2 },
    realism: {
      velocity: { kind: "probabilistic", scale: 0.0001 },
      parameters: { kind: "probabilistic", scale: 0.0001 },
      clock: { kind: "probabilistic", scale: 0.0001 },
      sensor: { kind: "probabilistic", scale: 0.003 }
    },
    retainTrajectories: true
  });
  const result = core.runEnsemble(forecast, declaration);
  const gradientNorm = Math.hypot(...forecast.gradients[5]);
  const expected = 2 * Math.sqrt((0.002 * gradientNorm) ** 2 + 0.003 ** 2);
  assert.ok(Math.abs(result.members[0].tubeRadius[5] - expected) < 1e-15);
  assert.equal(result.summary.coverage.wilson95.event, "whole-horizon member survival (no sampled tube exit)");
  assert.equal(result.summary.coverage.wilson95.trials, result.summary.resolvedMemberCount);
  assert.match(declaration.uncertainty.samplingLaw, /independent centred normal coordinates/);
  assert.equal(declaration.uncertainty.support, "R^2 in radians (unbounded)");
  assert.match(declaration.realism.velocity.samplingLaw, /independent centred normal coordinates/);
  assert.match(declaration.realism.parameters.support, /physical multipliers are positive exponentials/);
  assert.equal(
    declaration.realism.clock.samplingLaw,
    "clockFraction = tanh(scale*z) for one seeded standard-normal z"
  );
  assert.match(declaration.realism.sensor.support, /unbounded/);
  assert.ok(result.members.every(member =>
    member.audit.endpointClassification.classification === "unclassified"
      && member.audit.endpointClassification.hardRadiusTest === false
  ));
  for (const member of result.members) {
    const firstExit = member.audit.inside.findIndex(value => !value);
    const reentryOffset = firstExit < 0 ? -1 : member.audit.inside.slice(firstExit + 1).findIndex(Boolean);
    const expectedReentry = reentryOffset < 0 ? null : firstExit + 1 + reentryOffset;
    assert.equal(member.audit.projectedReconvergence.reentryIndex, expectedReentry);
    assert.equal(member.audit.projectedReconvergence.exitedThenReenteredTube, expectedReentry !== null);
    assert.equal(member.audit.projectedReconvergence.withinDeclaredReadoutRadius, expectedReentry !== null);
  }
});

test("bounded endpoint classifications, compact outcomes, outliers, and full-state comparisons reconstruct", () => {
  const forecast = core.forecastExperiment({ duration: 0.8, sampleCount: 33, preparationRadius: 0.01, noiseRadius: 0 });
  const result = core.runEnsemble(forecast, {
    size: 12,
    seed: "endpoint-and-state",
    uncertainty: { kind: "bounded", scale: 0.01 },
    realism: { sensor: { kind: "bounded", scale: 0.004 } },
    retainTrajectories: true
  });
  assert.equal(core.verifyEnsembleResult(result).valid, true);
  for (const member of result.members) {
    const endpoint = member.audit.endpointClassification;
    assert.equal(endpoint.cutoff, 0.008);
    assert.equal(endpoint.distance, Math.abs(endpoint.actualEndpoint - endpoint.structuredCentreEndpoint));
    assert.equal(endpoint.classification, endpoint.distance <= endpoint.cutoff ? "confusable" : "separated");
    assert.equal(member.compactOutcome.terminalSensor, member.actualSensorSeries.at(-1));
    const terminal = member.trajectory.states.at(-1);
    const baseline = result.comparisonBaseline.states.at(-1);
    const scale = result.declaration.fullStateMetric.velocityScaleSeconds;
    const wrap = value => Math.atan2(Math.sin(value), Math.cos(value));
    const expectedStateDistance = Math.hypot(
      wrap(terminal[0] - baseline[0]), wrap(terminal[1] - baseline[1]),
      scale * (terminal[2] - baseline[2]), scale * (terminal[3] - baseline[3])
    );
    assert.ok(Math.abs(member.audit.fullStateComparison.terminalStateDistance - expectedStateDistance) < 1e-15);
    if (member.audit.projectedReconvergence.reentryIndex !== null) {
      assert.equal(
        member.audit.fullStateComparison.outputReentryStateDistance,
        member.fullStateDistanceSeries[member.audit.projectedReconvergence.reentryIndex]
      );
    }
  }
  const outliers = result.summary.terminalOutliers;
  assert.equal(outliers.count, outliers.memberIds.length);
  assert.ok(outliers.representatives.every(item => outliers.memberIds.includes(item.id)));

  const tampered = structuredClone(result);
  tampered.members[0].actualSensorSeries[0] += 0.01;
  const tamperedPayload = { ...tampered }; delete tamperedPayload.resultId;
  tampered.resultId = core.checksum(core.stableSerialize(tamperedPayload));
  assert.throws(() => core.verifyEnsembleResult(tampered), /retained ensemble series/);
});

test("strict verification replays retained and compact scientific fields instead of trusting self-checksums", () => {
  const recommit = result => {
    const payload = { ...result };
    delete payload.resultId;
    result.resultId = core.checksum(core.stableSerialize(payload));
    return result;
  };
  const forecast = core.forecastExperiment({ duration: 0.3, sampleCount: 13 });
  const retained = core.runEnsemble(forecast, {
    size: 3, seed: "strict-retained-verifier", retainTrajectories: true
  });
  const retainedMutations = [
    value => { value.comparisonBaseline.times[1] += 1e-5; },
    value => { value.comparisonBaseline.method = "unverified method"; },
    value => { value.members[0].audit.coverage *= 0.5; },
    value => { value.members[0].audit.persistentExitIndex = 0; },
    value => { value.summary.timewise.survival[1] *= 0.5; },
    value => { value.summary.covariance.terminalState[0][0] += 1e-4; }
  ];
  for (const mutate of retainedMutations) {
    const tampered = structuredClone(retained);
    mutate(tampered);
    recommit(tampered);
    assert.throws(() => core.verifyEnsembleResult(tampered), /integrity mismatch/);
  }

  const compact = core.runEnsemble(forecast, {
    size: 3, seed: "strict-compact-verifier", retainTrajectories: false
  });
  const compactMutations = [
    value => { value.members[0].compactOutcome.sensorMinimum -= 0.1; },
    value => { value.members[0].compactOutcome.sensorRms += 0.1; },
    value => { value.members[0].compactOutcome.sensorSeriesDigest = "00000000"; },
    value => { value.members[0].audit.inside[0] = !value.members[0].audit.inside[0]; }
  ];
  for (const mutate of compactMutations) {
    const tampered = structuredClone(compact);
    mutate(tampered);
    recommit(tampered);
    assert.throws(() => core.verifyEnsembleResult(tampered), /compact ensemble outcome.*integrity mismatch/);
  }
});

test("response refinement gates regular launches and rejects the energetic T=30 response", () => {
  const regular = core.forecastExperiment({
    initialState: [0.35, 0.18, 0, 0], duration: 4, sampleCount: 81
  });
  assert.equal(regular.responseRefinement.passed, true);
  assert.ok(regular.responseRefinement.maximumRelativeDiscrepancy < 0.05);
  const regularOutcome = core.runIndependentOutcome(regular);
  assert.equal(regularOutcome.evidenceGates.energyTolerance, 1e-7);
  assert.equal(regularOutcome.evidenceGates.energyPassed, true);
  assert.equal(regularOutcome.evidenceGates.responseRefinementPassed, true);

  const strictEnergy = core.forecastExperiment({
    initialState: [0.35, 0.18, 0, 0], duration: 1, sampleCount: 41,
    energyDriftTolerance: 0
  });
  const strictEnergyOutcome = core.runIndependentOutcome(strictEnergy);
  assert.ok(strictEnergyOutcome.maxEnergyDrift > 0);
  assert.equal(strictEnergyOutcome.evidenceGates.energyPassed, false);
  assert.equal(strictEnergyOutcome.evidenceGates.baselineRefinementPassed, true);
  assert.equal(strictEnergyOutcome.evidenceGates.responseRefinementPassed, true);
  assert.equal(strictEnergyOutcome.evidenceGates.refinedEvidencePassed, false);
  const strictDeclaration = core.buildEnsembleDeclaration(strictEnergy, { size: 2 });
  assert.equal(strictDeclaration.gates.maxEnergyDrift, strictEnergy.config.energyDriftTolerance);
  assert.equal(
    strictDeclaration.gates.maxRefinementDiscrepancy,
    strictEnergy.config.baselineRefinementTolerance
  );

  const energetic = core.forecastExperiment({
    initialState: [1.95, -1.15, 0.35, -0.2], duration: 30, sampleCount: 601
  });
  assert.equal(energetic.responseRefinement.passed, false);
  assert.ok(energetic.responseRefinement.maximumRelativeDiscrepancy > 0.05);
  const energeticOutcome = core.runIndependentOutcome(energetic);
  assert.equal(energeticOutcome.evidenceGates.refinedEvidencePassed, false);
  const ensemble = core.runEnsemble(energetic, {
    size: 2, seed: "response-gate", uncertainty: { kind: "bounded", scale: 0.001 },
    retainTrajectories: false
  });
  assert.equal(ensemble.summary.gates.responseRefinementPassed, false);
  assert.equal(ensemble.summary.gates.refinedEvidenceStatus, "unresolved");
  assert.ok(ensemble.members.every(member => member.audit.unresolvedReasons.includes("response-refinement-gate")));
});

test("incomplete or all-unresolved probabilistic ensembles withhold Wilson and fail energy counts closed", () => {
  const forecast = core.forecastExperiment({ duration: 0.3, sampleCount: 13 });
  const declaration = core.buildEnsembleDeclaration(forecast, {
    size: 5,
    uncertainty: { kind: "probabilistic", scale: 0.001 },
    gates: { maxResponseRefinementDiscrepancy: 0 },
    retainTrajectories: true
  });
  const allUnresolved = core.runEnsemble(forecast, declaration);
  assert.equal(allUnresolved.summary.resolvedMemberCount, 0);
  assert.equal(allUnresolved.summary.coverage.wilson95, null);
  assert.match(allUnresolved.summary.coverage.intervalInterpretation, /incomplete/);

  const mixedMembers = structuredClone(allUnresolved.members);
  mixedMembers[0].audit.status = "resolved";
  mixedMembers[0].audit.unresolvedReasons = [];
  const mixed = core.summarizeEnsemble(forecast, declaration, mixedMembers);
  assert.equal(mixed.coverage.wilson95, null);
  mixedMembers[1].audit = { status: "unresolved", unresolvedReasons: ["solver-error"] };
  const solverErrorSummary = core.summarizeEnsemble(forecast, declaration, mixedMembers);
  assert.equal(solverErrorSummary.gates.energyPassCount, declaration.size - 1);
});

test("laboratory grids laws and amplitudes while preserving fixed observation cadence", () => {
  const forecast = core.forecastExperiment({ duration: 0.2, sampleCount: 9, preparationRadius: 0, noiseRadius: 0 });
  const study = core.runLaboratoryStudy({
    forecast,
    ensembleOptions: { uncertainty: { kind: "bounded", scale: 0 } },
    sizes: [2],
    horizons: [0.2, 0.4],
    laws: ["off", "linear"],
    amplitudes: [0, 0.001],
    repeats: 1,
    baseSeed: "lab-test"
  });
  assert.equal(study.cells.length, 8);
  assert.deepEqual(study.sampling.realized.map(item => item.sampleCount), [9, 17]);
  assert.ok(study.sampling.realized.every(item => Math.abs(item.observationStep - 0.025) < 1e-15));
  assert.equal(study.cells[0].runs[0].members.length, 2);
});

test("async ensemble cancellation is observed between independently seeded members", async () => {
  const forecast = core.forecastExperiment({ duration: 0.2, sampleCount: 9, preparationRadius: 0, noiseRadius: 0 });
  let cancelled = false;
  await assert.rejects(
    core.runEnsembleAsync(forecast, { size: 20, uncertainty: { kind: "bounded", scale: 0 } }, {
      yieldEvery: 1,
      isCancelled: () => cancelled,
      onProgress: progress => { if (progress.completed >= 1) cancelled = true; }
    }),
    error => error && error.code === "OIG_CANCELLED"
  );
});

test("single-job asynchronous laboratories report nested member progress", async () => {
  const forecast = core.forecastExperiment({ duration: 0.2, sampleCount: 9 });
  const progress = [];
  const study = await core.runLaboratoryStudyAsync({
    forecast,
    ensembleOptions: { uncertainty: { kind: "bounded", scale: 0.001 } },
    sizes: [5], horizons: [0.2], laws: ["off"], amplitudes: [0], repeats: 1,
    baseSeed: "nested-progress", observationStep: 0.025
  }, {
    yieldEvery: 1,
    onProgress: update => progress.push(update)
  });
  assert.equal(study.cells.length, 1);
  assert.ok(progress.some(update =>
    update.phase === "laboratory-members" && update.fraction > 0 && update.fraction < 1
  ));
  assert.equal(progress.at(-1).phase, "laboratory-runs");
  assert.equal(progress.at(-1).fraction, 1);
  for (let index = 1; index < progress.length; index += 1) {
    assert.ok(progress[index].fraction >= progress[index - 1].fraction);
  }
});

test("N=1000,T=30 laboratory export is compact and guarded by a conservative byte preflight", { timeout: 15000 }, () => {
  const forecast = core.forecastExperiment({
    duration: 1, sampleCount: 41, preparationRadius: 0.001, noiseRadius: 0.001
  });
  const study = core.runLaboratoryStudy({
    forecast,
    ensembleOptions: {
      uncertainty: { kind: "bounded", scale: 0.001 },
      solverOptions: { rtol: 1e-5, atol: 1e-7, initialStep: 0.05, maxStep: 0.25 },
      gates: {
        maxEnergyDrift: 1,
        maxRefinementDiscrepancy: 1,
        maxResponseRefinementDiscrepancy: 1
      }
    },
    sizes: [1000], horizons: [30], laws: ["off"], amplitudes: [0], repeats: 1,
    baseSeed: "compact-size-gate", observationStep: 1 / 40
  });
  const run = study.cells[0].runs[0];
  const member = run.members[0];
  assert.equal(run.members.length, 1000);
  assert.equal("nominalTimes" in member, false);
  assert.equal("memberTimes" in member, false);
  assert.equal("draws" in member, false);
  assert.equal("inside" in member.audit, false);
  assert.equal(member.drawSummary.sensorNoise.sampleCount, 1201);
  const bytes = Buffer.byteLength(JSON.stringify(study, null, 2));
  assert.ok(bytes < 8 * 1024 * 1024, "compact N=1000,T=30 export was " + bytes + " bytes");
  assert.ok(bytes <= study.resourceEstimate.estimatedExportBytes);
  assert.ok(study.resourceEstimate.estimatedExportBytes <= core.LABORATORY_MAX_ESTIMATED_EXPORT_BYTES);

  assert.throws(() => core.runLaboratoryStudy({
    forecast,
    sizes: [5000], horizons: [120], laws: core.ENSEMBLE_LAWS.slice(),
    amplitudes: [0, 1], repeats: 100, observationStep: 0.025
  }), /estimated compact export exceeds/);
});

test("50-member laboratory performance smoke remains within a conservative CI budget", { timeout: 15000 }, () => {
  const forecast = core.forecastExperiment({
    duration: 0.5,
    sampleCount: 11,
    preparationRadius: 0.001,
    noiseRadius: 0.001
  });
  const started = Date.now();
  const study = core.runLaboratoryStudy({
    forecast,
    ensembleOptions: {
      uncertainty: { kind: "bounded", scale: 0.001 },
      structured: { law: "linear", alpha: 0.002, direction: "oig-weakest" },
      retainTrajectories: false
    },
    sizes: [50],
    horizons: [3],
    laws: ["linear"],
    amplitudes: [0.002],
    repeats: 1,
    baseSeed: "ci-performance-smoke"
  });
  const elapsed = Date.now() - started;
  assert.equal(study.cells[0].runs[0].members.length, 50);
  assert.equal(study.cells[0].runs[0].summary.unresolvedMemberCount, 0);
  assert.ok(elapsed < 5000, "50-member smoke took " + elapsed + " ms (budget 5000 ms)");
});
