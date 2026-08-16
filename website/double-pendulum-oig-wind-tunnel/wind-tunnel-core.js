(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.OIGWindTunnelCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const DEFAULT_PARAMETERS = Object.freeze({ m1: 1, m2: 1, l1: 1, l2: 1, g: 9.81 });
  const SENSORS = Object.freeze([
    { id: "tip-x", label: "tip horizontal position" },
    { id: "tip-y", label: "tip vertical position" },
    { id: "sin-theta-1", label: "arm 1 phase (sin θ₁)" },
    { id: "sin-theta-2", label: "arm 2 phase (sin θ₂)" },
    { id: "omega-1", label: "scaled angular velocity ω₁" },
    { id: "omega-2", label: "scaled angular velocity ω₂" }
  ]);

  function assertFiniteVector(state, length = 4) {
    if (!Array.isArray(state) || state.length !== length || state.some(value => !Number.isFinite(value))) {
      throw new TypeError(`state must be a finite ${length}-vector`);
    }
  }

  function validateParameters(parameters) {
    const p = Object.assign({}, DEFAULT_PARAMETERS, parameters || {});
    for (const key of ["m1", "m2", "l1", "l2", "g"]) {
      if (!Number.isFinite(p[key]) || p[key] <= 0) throw new RangeError(`${key} must be positive`);
    }
    return p;
  }

  function rhs(_time, state, parameters) {
    assertFiniteVector(state);
    const p = validateParameters(parameters);
    const [theta1, theta2, omega1, omega2] = state;
    const delta = theta1 - theta2;
    const c = Math.cos(delta);
    const s = Math.sin(delta);
    const m11 = (p.m1 + p.m2) * p.l1 * p.l1;
    const m12 = p.m2 * p.l1 * p.l2 * c;
    const m22 = p.m2 * p.l2 * p.l2;
    const f1 = -p.m2 * p.l1 * p.l2 * s * omega2 * omega2
      - (p.m1 + p.m2) * p.g * p.l1 * Math.sin(theta1);
    const f2 = p.m2 * p.l1 * p.l2 * s * omega1 * omega1
      - p.m2 * p.g * p.l2 * Math.sin(theta2);
    const determinant = m11 * m22 - m12 * m12;
    const alpha1 = (f1 * m22 - f2 * m12) / determinant;
    const alpha2 = (m11 * f2 - m12 * f1) / determinant;
    return [omega1, omega2, alpha1, alpha2];
  }

  function energy(state, parameters) {
    assertFiniteVector(state);
    const p = validateParameters(parameters);
    const [theta1, theta2, omega1, omega2] = state;
    const kinetic = 0.5 * (p.m1 + p.m2) * p.l1 * p.l1 * omega1 * omega1
      + 0.5 * p.m2 * p.l2 * p.l2 * omega2 * omega2
      + p.m2 * p.l1 * p.l2 * omega1 * omega2 * Math.cos(theta1 - theta2);
    const potential = -(p.m1 + p.m2) * p.g * p.l1 * Math.cos(theta1)
      - p.m2 * p.g * p.l2 * Math.cos(theta2);
    return kinetic + potential;
  }

  function bobPositions(state, parameters) {
    assertFiniteVector(state);
    const p = validateParameters(parameters);
    const [theta1, theta2] = state;
    const x1 = p.l1 * Math.sin(theta1);
    const y1 = -p.l1 * Math.cos(theta1);
    return {
      pivot: [0, 0, 0],
      bob1: [x1, y1, 0],
      bob2: [x1 + p.l2 * Math.sin(theta2), y1 - p.l2 * Math.cos(theta2), 0]
    };
  }

  function addScaled(base, increments) {
    return base.map((value, index) => value + increments.reduce((sum, term) => sum + term.scale * term.vector[index], 0));
  }

  function rk4Step(time, state, step, parameters) {
    const k1 = rhs(time, state, parameters);
    const k2 = rhs(time + step / 2, addScaled(state, [{ scale: step / 2, vector: k1 }]), parameters);
    const k3 = rhs(time + step / 2, addScaled(state, [{ scale: step / 2, vector: k2 }]), parameters);
    const k4 = rhs(time + step, addScaled(state, [{ scale: step, vector: k3 }]), parameters);
    return addScaled(state, [
      { scale: step / 6, vector: k1 },
      { scale: step / 3, vector: k2 },
      { scale: step / 3, vector: k3 },
      { scale: step / 6, vector: k4 }
    ]);
  }

  function makeTimes(duration, count) {
    if (!Number.isFinite(duration) || duration <= 0 || !Number.isInteger(count) || count < 2) {
      throw new RangeError("duration and sample count are invalid");
    }
    return Array.from({ length: count }, (_, index) => duration * index / (count - 1));
  }

  function simulateRK4(initialState, times, parameters, maximumStep = 1 / 160) {
    assertFiniteVector(initialState);
    if (!Array.isArray(times) || times.length < 2 || times[0] !== 0
      || times.some((value, index) => !Number.isFinite(value) || (index > 0 && value <= times[index - 1]))) {
      throw new RangeError("times must be finite, begin at zero, and increase strictly");
    }
    if (!Number.isFinite(maximumStep) || maximumStep <= 0) throw new RangeError("maximumStep must be positive");
    const p = validateParameters(parameters);
    const states = [initialState.slice()];
    let state = initialState.slice();
    let time = 0;
    for (let index = 1; index < times.length; index += 1) {
      const target = times[index];
      if (!(target > time)) throw new RangeError("times must increase strictly");
      while (time < target - 1e-15) {
        const step = Math.min(maximumStep, target - time);
        state = rk4Step(time, state, step, p);
        time += step;
      }
      states.push(state.slice());
    }
    return { times: times.slice(), states, method: "fixed-step RK4", maximumStep };
  }

  // Dormand-Prince 5(4): intentionally separate from the forecast RK4 path.
  function dopriStep(time, state, step, parameters) {
    const k1 = rhs(time, state, parameters);
    const k2 = rhs(time + step / 5, addScaled(state, [{ scale: step / 5, vector: k1 }]), parameters);
    const k3 = rhs(time + 3 * step / 10, addScaled(state, [
      { scale: step * 3 / 40, vector: k1 }, { scale: step * 9 / 40, vector: k2 }
    ]), parameters);
    const k4 = rhs(time + 4 * step / 5, addScaled(state, [
      { scale: step * 44 / 45, vector: k1 }, { scale: step * -56 / 15, vector: k2 }, { scale: step * 32 / 9, vector: k3 }
    ]), parameters);
    const k5 = rhs(time + 8 * step / 9, addScaled(state, [
      { scale: step * 19372 / 6561, vector: k1 }, { scale: step * -25360 / 2187, vector: k2 },
      { scale: step * 64448 / 6561, vector: k3 }, { scale: step * -212 / 729, vector: k4 }
    ]), parameters);
    const k6 = rhs(time + step, addScaled(state, [
      { scale: step * 9017 / 3168, vector: k1 }, { scale: step * -355 / 33, vector: k2 },
      { scale: step * 46732 / 5247, vector: k3 }, { scale: step * 49 / 176, vector: k4 },
      { scale: step * -5103 / 18656, vector: k5 }
    ]), parameters);
    const fifth = addScaled(state, [
      { scale: step * 35 / 384, vector: k1 }, { scale: step * 500 / 1113, vector: k3 },
      { scale: step * 125 / 192, vector: k4 }, { scale: step * -2187 / 6784, vector: k5 },
      { scale: step * 11 / 84, vector: k6 }
    ]);
    const k7 = rhs(time + step, fifth, parameters);
    const fourth = addScaled(state, [
      { scale: step * 5179 / 57600, vector: k1 }, { scale: step * 7571 / 16695, vector: k3 },
      { scale: step * 393 / 640, vector: k4 }, { scale: step * -92097 / 339200, vector: k5 },
      { scale: step * 187 / 2100, vector: k6 }, { scale: step / 40, vector: k7 }
    ]);
    return { state: fifth, error: fifth.map((value, index) => value - fourth[index]) };
  }

  function simulateAdaptive(initialState, times, parameters, options) {
    assertFiniteVector(initialState);
    if (!Array.isArray(times) || times.length < 2 || times[0] !== 0
      || times.some((value, index) => !Number.isFinite(value) || (index > 0 && value <= times[index - 1]))) {
      throw new RangeError("times must be finite, begin at zero, and increase strictly");
    }
    const p = validateParameters(parameters);
    const config = Object.assign({ rtol: 2e-10, atol: 2e-12, initialStep: 1e-3, maxStep: 0.025 }, options || {});
    for (const key of ["rtol", "atol", "initialStep", "maxStep"]) {
      if (!Number.isFinite(config[key]) || config[key] <= 0) throw new RangeError(`${key} must be positive`);
    }
    const states = [initialState.slice()];
    let state = initialState.slice();
    let time = 0;
    let step = Math.min(config.initialStep, config.maxStep);
    let accepted = 0;
    let rejected = 0;
    for (let index = 1; index < times.length; index += 1) {
      const target = times[index];
      while (time < target - 1e-15) {
        step = Math.min(step, config.maxStep, target - time);
        const trial = dopriStep(time, state, step, p);
        let norm = 0;
        for (let component = 0; component < 4; component += 1) {
          const scale = config.atol + config.rtol * Math.max(Math.abs(state[component]), Math.abs(trial.state[component]));
          norm = Math.max(norm, Math.abs(trial.error[component]) / scale);
        }
        if (norm <= 1) {
          state = trial.state;
          time += step;
          accepted += 1;
        } else {
          rejected += 1;
        }
        const factor = norm === 0 ? 4 : Math.max(0.2, Math.min(4, 0.9 * Math.pow(norm, -0.2)));
        step *= factor;
        if (step < 1e-10) throw new Error("adaptive outcome solver step underflow");
      }
      states.push(state.slice());
    }
    return { times: times.slice(), states, method: "adaptive Dormand–Prince 5(4)", accepted, rejected, config };
  }

  function sensorValue(sensor, state, parameters) {
    const p = validateParameters(parameters);
    const speed = Math.sqrt(p.g / p.l1);
    switch (sensor) {
      case "tip-x": return bobPositions(state, p).bob2[0] / (p.l1 + p.l2);
      case "tip-y": return bobPositions(state, p).bob2[1] / (p.l1 + p.l2);
      case "sin-theta-1": return Math.sin(state[0]);
      case "sin-theta-2": return Math.sin(state[1]);
      case "omega-1": return state[2] / speed;
      case "omega-2": return state[3] / speed;
      default: throw new RangeError(`unknown sensor: ${sensor}`);
    }
  }

  function sensorSeries(sensor, trajectory, parameters) {
    return trajectory.states.map(state => sensorValue(sensor, state, parameters));
  }

  function eigen2x2(a, b, d) {
    const trace = a + d;
    const radius = Math.hypot(a - d, 2 * b);
    return [Math.max(0, (trace - radius) / 2), Math.max(0, (trace + radius) / 2)];
  }

  function informationFromGradients(gradients) {
    let a = 0;
    let b = 0;
    let d = 0;
    for (const [x, y] of gradients) {
      a += x * x / gradients.length;
      b += x * y / gradients.length;
      d += y * y / gradients.length;
    }
    const values = eigen2x2(a, b, d);
    const angle = 0.5 * Math.atan2(2 * b, a - d);
    return {
      gram: [[a, b], [b, d]],
      weakestGain: Math.sqrt(values[0]),
      strongestGain: Math.sqrt(values[1]),
      strongestDirection: [Math.cos(angle), Math.sin(angle)],
      weakestDirection: [-Math.sin(angle), Math.cos(angle)]
    };
  }

  function forecastExperiment(options) {
    const config = Object.assign({
      initialState: [0.8, -0.35, 0, 0], duration: 4, sampleCount: 241,
      sensor: "tip-x", preparationRadius: 0.01, noiseRadius: 0.015,
      derivativeStep: 2e-5, forecastStep: 1 / 160,
      responseRefinementTolerance: 0.05, baselineRefinementTolerance: 1e-6,
      energyDriftTolerance: 1e-7,
      parameters: DEFAULT_PARAMETERS
    }, options || {});
    assertFiniteVector(config.initialState);
    for (const key of ["duration", "preparationRadius", "noiseRadius", "derivativeStep", "forecastStep",
      "responseRefinementTolerance", "baselineRefinementTolerance", "energyDriftTolerance"]) {
      if (!Number.isFinite(config[key])) throw new RangeError(`${key} must be finite`);
    }
    if (config.duration <= 0 || config.derivativeStep <= 0 || config.forecastStep <= 0
      || config.responseRefinementTolerance <= 0 || config.baselineRefinementTolerance <= 0
      || config.energyDriftTolerance < 0
      || config.preparationRadius < 0 || config.noiseRadius < 0) {
      throw new RangeError("duration and integration steps must be positive; uncertainty and energy tolerances must be nonnegative");
    }
    if (!Number.isInteger(config.sampleCount) || config.sampleCount < 2) throw new RangeError("sampleCount must be an integer at least two");
    if (!SENSORS.some(sensor => sensor.id === config.sensor)) throw new RangeError(`unknown sensor: ${config.sensor}`);
    const p = validateParameters(config.parameters);
    const times = makeTimes(config.duration, config.sampleCount);
    const baseline = simulateRK4(config.initialState, times, p, config.forecastStep);
    const perturbed = [];
    const refinedPerturbed = [];
    for (let axis = 0; axis < 2; axis += 1) {
      const plus = config.initialState.slice();
      const minus = config.initialState.slice();
      plus[axis] += config.derivativeStep;
      minus[axis] -= config.derivativeStep;
      perturbed.push({
        plus: simulateRK4(plus, times, p, config.forecastStep),
        minus: simulateRK4(minus, times, p, config.forecastStep)
      });
      const refinedPlus = config.initialState.slice();
      const refinedMinus = config.initialState.slice();
      refinedPlus[axis] += config.derivativeStep / 2;
      refinedMinus[axis] -= config.derivativeStep / 2;
      refinedPerturbed.push({
        plus: simulateRK4(refinedPlus, times, p, config.forecastStep),
        minus: simulateRK4(refinedMinus, times, p, config.forecastStep)
      });
    }
    const baselineSensor = sensorSeries(config.sensor, baseline, p);
    const gradientsBySensor = {};
    for (const sensor of SENSORS) {
      const plus0 = sensorSeries(sensor.id, perturbed[0].plus, p);
      const minus0 = sensorSeries(sensor.id, perturbed[0].minus, p);
      const plus1 = sensorSeries(sensor.id, perturbed[1].plus, p);
      const minus1 = sensorSeries(sensor.id, perturbed[1].minus, p);
      gradientsBySensor[sensor.id] = times.map((_, index) => [
        (plus0[index] - minus0[index]) / (2 * config.derivativeStep),
        (plus1[index] - minus1[index]) / (2 * config.derivativeStep)
      ]);
    }
    const gradients = gradientsBySensor[config.sensor];
    const refinedPlus0 = sensorSeries(config.sensor, refinedPerturbed[0].plus, p);
    const refinedMinus0 = sensorSeries(config.sensor, refinedPerturbed[0].minus, p);
    const refinedPlus1 = sensorSeries(config.sensor, refinedPerturbed[1].plus, p);
    const refinedMinus1 = sensorSeries(config.sensor, refinedPerturbed[1].minus, p);
    const refinedGradients = times.map((_, index) => [
      (refinedPlus0[index] - refinedMinus0[index]) / config.derivativeStep,
      (refinedPlus1[index] - refinedMinus1[index]) / config.derivativeStep
    ]);
    const information = informationFromGradients(gradients);
    const refinedInformation = informationFromGradients(refinedGradients);
    let responseDifferenceSquare = 0;
    let refinedResponseSquare = 0;
    for (let index = 0; index < times.length; index += 1) for (let axis = 0; axis < 2; axis += 1) {
      responseDifferenceSquare += (gradients[index][axis] - refinedGradients[index][axis]) ** 2;
      refinedResponseSquare += refinedGradients[index][axis] ** 2;
    }
    const responseDenominator = 2 * times.length;
    const responseDifferenceRms = Math.sqrt(responseDifferenceSquare / responseDenominator);
    const refinedResponseRms = Math.sqrt(refinedResponseSquare / responseDenominator);
    const responseRelativeRms = responseDifferenceRms / Math.max(1e-12, refinedResponseRms);
    const weakestGainRelativeShift = Math.abs(information.weakestGain - refinedInformation.weakestGain)
      / Math.max(1e-12, refinedInformation.weakestGain);
    const strongestGainRelativeShift = Math.abs(information.strongestGain - refinedInformation.strongestGain)
      / Math.max(1e-12, refinedInformation.strongestGain);
    const maximumRelativeDiscrepancy = Math.max(
      responseRelativeRms, weakestGainRelativeShift, strongestGainRelativeShift
    );
    const responseRefinement = {
      selectedSensor: config.sensor,
      coarseDerivativeStep: config.derivativeStep,
      refinedDerivativeStep: config.derivativeStep / 2,
      coarseGradients: gradients,
      refinedGradients,
      responseDifferenceRms,
      refinedResponseRms,
      responseRelativeRms,
      coarseWeakestGain: information.weakestGain,
      refinedWeakestGain: refinedInformation.weakestGain,
      weakestGainRelativeShift,
      coarseStrongestGain: information.strongestGain,
      refinedStrongestGain: refinedInformation.strongestGain,
      strongestGainRelativeShift,
      maximumRelativeDiscrepancy,
      tolerance: config.responseRefinementTolerance,
      passed: Number.isFinite(maximumRelativeDiscrepancy)
        && maximumRelativeDiscrepancy <= config.responseRefinementTolerance,
      interpretation: "Centred initial-angle response at h versus h/2; a numerical refinement gate, not an outward derivative enclosure."
    };
    const tubeRadius = gradients.map(row => config.preparationRadius * Math.hypot(row[0], row[1]) + config.noiseRadius);
    const recommendation = recommendNextExperiment(information.gram, gradientsBySensor, times);
    return {
      config, times, baseline, baselineSensor, gradients, gradientsBySensor, tubeRadius,
      information, responseRefinement, recommendation,
      method: "frozen RK4 centre plus centred finite-difference response"
    };
  }

  function recommendNextExperiment(currentGram, gradientsBySensor, times) {
    let best = null;
    const stride = Math.max(1, Math.floor(times.length / 24));
    for (const sensor of SENSORS) {
      const rows = gradientsBySensor[sensor.id];
      for (let index = stride; index < times.length; index += stride) {
        const [x, y] = rows[index];
        const gain = 1 / Math.max(1, times.length);
        const a = currentGram[0][0] + gain * x * x;
        const b = currentGram[0][1] + gain * x * y;
        const d = currentGram[1][1] + gain * y * y;
        const floor = eigen2x2(a, b, d)[0];
        if (!best || floor > best.informationFloor) {
          best = {
            sensor: sensor.id,
            sensorLabel: sensor.label,
            time: times[index],
            informationFloor: floor,
            weakestGain: Math.sqrt(floor)
          };
        }
      }
    }
    return best;
  }

  function deterministicDirection(initialState) {
    const phase = initialState.reduce((sum, value, index) => sum + Math.sin((index + 1) * value * 1.731), 0);
    const angle = (phase * 12.9898) % (2 * Math.PI);
    return [Math.cos(angle), Math.sin(angle)];
  }

  function runIndependentOutcome(forecast, direction) {
    const deltaDirection = direction === undefined
      ? deterministicDirection(forecast.config.initialState)
      : direction;
    if (!Array.isArray(deltaDirection) || deltaDirection.length !== 2
      || deltaDirection.some(value => !Number.isFinite(value))) {
      throw new TypeError("held-out direction must be a finite two-vector");
    }
    const norm = Math.hypot(deltaDirection[0], deltaDirection[1]);
    if (!(norm > 0)) throw new RangeError("held-out direction must have positive norm");
    const unit = [deltaDirection[0] / norm, deltaDirection[1] / norm];
    const actualInitial = forecast.config.initialState.slice();
    actualInitial[0] += forecast.config.preparationRadius * unit[0];
    actualInitial[1] += forecast.config.preparationRadius * unit[1];
    const actual = simulateAdaptive(actualInitial, forecast.times, forecast.config.parameters);
    const independentBaseline = simulateAdaptive(forecast.config.initialState, forecast.times, forecast.config.parameters);
    const actualSensor = sensorSeries(forecast.config.sensor, actual, forecast.config.parameters);
    const refinedBaselineSensor = sensorSeries(forecast.config.sensor, independentBaseline, forecast.config.parameters);
    let inside = 0;
    let squareDifference = 0;
    let squarePredicted = 0;
    let squareRefinement = 0;
    for (let index = 0; index < forecast.times.length; index += 1) {
      const difference = actualSensor[index] - refinedBaselineSensor[index];
      const predicted = forecast.config.preparationRadius
        * (forecast.gradients[index][0] * unit[0] + forecast.gradients[index][1] * unit[1]);
      const allowed = forecast.tubeRadius[index];
      if (Math.abs(actualSensor[index] - forecast.baselineSensor[index]) <= allowed + 1e-12) inside += 1;
      squareDifference += difference * difference;
      squarePredicted += predicted * predicted;
      squareRefinement += Math.pow(refinedBaselineSensor[index] - forecast.baselineSensor[index], 2);
    }
    const denominator = Math.max(1, forecast.times.length);
    const energy0 = energy(actual.states[0], forecast.config.parameters);
    const energyScale = Math.max(1, Math.abs(energy0));
    const maxEnergyDrift = Math.max(...actual.states.map(state => Math.abs(energy(state, forecast.config.parameters) - energy0) / energyScale));
    const actualAmplification = Math.sqrt(squareDifference / denominator) / Math.max(1e-15, forecast.config.preparationRadius);
    const predictedAmplification = Math.sqrt(squarePredicted / denominator) / Math.max(1e-15, forecast.config.preparationRadius);
    const refinementDiscrepancy = Math.sqrt(squareRefinement / denominator);
    const endpointDistance = Math.abs(actualSensor[actualSensor.length - 1] - refinedBaselineSensor[refinedBaselineSensor.length - 1]);
    return {
      actual, independentBaseline, actualSensor, refinedBaselineSensor, direction: unit,
      coverage: inside / forecast.times.length,
      actualAmplification, predictedAmplification, refinementDiscrepancy, maxEnergyDrift,
      endpointDistance,
      classification: endpointDistance <= 2 * forecast.config.noiseRadius ? "confusable at the declared endpoint noise" : "separated at the declared endpoint noise",
      evidenceGates: {
        energyTolerance: forecast.config.energyDriftTolerance,
        energyPassed: Number.isFinite(maxEnergyDrift) && maxEnergyDrift <= forecast.config.energyDriftTolerance,
        baselineRefinementTolerance: forecast.config.baselineRefinementTolerance,
        baselineRefinementPassed: refinementDiscrepancy <= forecast.config.baselineRefinementTolerance,
        responseRefinementTolerance: forecast.config.responseRefinementTolerance,
        responseRefinementMaximumRelativeDiscrepancy: forecast.responseRefinement.maximumRelativeDiscrepancy,
        responseRefinementPassed: forecast.responseRefinement.passed,
        refinedEvidencePassed: Number.isFinite(maxEnergyDrift)
          && maxEnergyDrift <= forecast.config.energyDriftTolerance
          && refinementDiscrepancy <= forecast.config.baselineRefinementTolerance
          && forecast.responseRefinement.passed
      },
      method: "held-out adaptive Dormand–Prince 5(4) trajectory"
    };
  }

  const ENSEMBLE_SCHEMA_VERSION = "oig-double-pendulum-ensemble-v1";
  const ENSEMBLE_LAWS = Object.freeze(["off", "linear", "quadratic", "sinusoidal", "radial", "geometric"]);
  const ENSEMBLE_DIRECTIONS = Object.freeze(["custom", "oig-weakest", "oig-strongest"]);
  const ENSEMBLE_FORMULA = "q_i = q_0 + scaleRadians * xi_i + alphaRadians * f(s_i) * v";
  const ENSEMBLE_SOURCE_SUBSPACE = Object.freeze(["theta1 (radians)", "theta2 (radians)"]);
  const ENSEMBLE_PARAMETER_COORDINATES = Object.freeze(["log(m1)", "log(m2)", "log(l1)", "log(l2)", "log(g)"]);
  const ENSEMBLE_CLOCK_MAP = "t_actual = (1 + clockFraction) * t_nominal; bounded draws are linear and probabilistic draws use tanh(scale*z)";
  const ENSEMBLE_PREDICTION_BOUNDARY = "Only the known structured initial-angle offset shifts each predicted centre. Hidden initial-angle response and additive selected-sensor noise are propagated into the declared linearized tube/distribution. Velocity, parameter, and clock draws alter outcomes but remain unpropagated stressors.";
  const LABORATORY_MAX_ESTIMATED_EXPORT_BYTES = 512 * 1024 * 1024;

  class CancellationError extends Error {
    constructor(message = "ensemble computation cancelled") {
      super(message);
      this.name = "CancellationError";
      this.code = "OIG_CANCELLED";
    }
  }

  function stableSerialize(value) {
    if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
    if (typeof value === "number") {
      if (!Number.isFinite(value)) throw new TypeError("deterministic serialization requires finite numbers");
      return JSON.stringify(Object.is(value, -0) ? 0 : value);
    }
    if (Array.isArray(value)) return "[" + value.map(stableSerialize).join(",") + "]";
    if (value && typeof value === "object") {
      const keys = Object.keys(value).filter(key => value[key] !== undefined).sort();
      return "{" + keys.map(key => JSON.stringify(key) + ":" + stableSerialize(value[key])).join(",") + "}";
    }
    throw new TypeError("value is not deterministically serializable");
  }

  function deriveSeed(masterSeed, ...coordinates) {
    if (!(typeof masterSeed === "string" || (Number.isSafeInteger(masterSeed) && masterSeed >= 0))) {
      throw new TypeError("seed must be a string or a nonnegative safe integer");
    }
    return checksum(stableSerialize(["oig-member-seed-v1", masterSeed, ...coordinates]));
  }

  function createSeededPRNG(seed) {
    let state = parseInt(deriveSeed(seed, "prng"), 16) >>> 0;
    return function next() {
      state = (state + 0x6D2B79F5) >>> 0;
      let value = state;
      value = Math.imul(value ^ (value >>> 15), value | 1);
      value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
      return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    };
  }

  function normalDraws(seed, count) {
    const random = createSeededPRNG(seed);
    const values = [];
    while (values.length < count) {
      const u1 = Math.max(Number.MIN_VALUE, random());
      const u2 = random();
      const radius = Math.sqrt(-2 * Math.log(u1));
      values.push(radius * Math.cos(2 * Math.PI * u2));
      if (values.length < count) values.push(radius * Math.sin(2 * Math.PI * u2));
    }
    return values;
  }

  function boundedDiskDraw(seed) {
    const random = createSeededPRNG(seed);
    const radius = Math.sqrt(random());
    const angle = 2 * Math.PI * random();
    return [radius * Math.cos(angle), radius * Math.sin(angle)];
  }

  function boundedComponentDraws(seed, count) {
    const random = createSeededPRNG(seed);
    return Array.from({ length: count }, () => 2 * random() - 1);
  }

  function validateForecastForEnsemble(forecast) {
    if (!forecast || typeof forecast !== "object" || !forecast.config || !forecast.information) {
      throw new TypeError("forecast must be a frozen forecastExperiment result");
    }
    assertFiniteVector(forecast.config.initialState);
    if (!Array.isArray(forecast.times) || forecast.times.length < 2
      || !Array.isArray(forecast.baselineSensor) || forecast.baselineSensor.length !== forecast.times.length
      || !Array.isArray(forecast.gradients) || forecast.gradients.length !== forecast.times.length
      || forecast.gradients.some(row => !Array.isArray(row) || row.length !== 2 || row.some(value => !Number.isFinite(value)))) {
      throw new TypeError("forecast has inconsistent time, sensor, or initial-angle response arrays");
    }
  }

  function frozenForecastGeometry(forecast) {
    validateForecastForEnsemble(forecast);
    return {
      schemaVersion: "oig-frozen-forecast-commitment-v1",
      config: forecast.config,
      times: forecast.times,
      baselineSensor: forecast.baselineSensor,
      gradients: forecast.gradients,
      tubeRadius: forecast.tubeRadius,
      information: forecast.information,
      responseRefinement: forecast.responseRefinement,
      recommendation: forecast.recommendation,
      method: forecast.method
    };
  }

  function computeForecastCommitment(forecast) {
    return checksum(stableSerialize(frozenForecastGeometry(forecast)));
  }

  function finiteNonnegative(value, name) {
    if (!Number.isFinite(value) || value < 0) throw new RangeError(name + " must be finite and nonnegative");
    return value;
  }

  function structuredLawValue(law, coordinate, geometricRate) {
    switch (law) {
      case "off": return 0;
      case "linear": return coordinate;
      case "quadratic": return 2 * coordinate * coordinate - 1;
      case "sinusoidal": return Math.sin(Math.PI * coordinate);
      case "radial": return 2 * Math.abs(coordinate) - 1;
      case "geometric":
        if (coordinate === 0) return 0;
        return Math.sign(coordinate) * Math.expm1(geometricRate * Math.abs(coordinate)) / Math.expm1(geometricRate);
      default: throw new RangeError("unknown structured law: " + law);
    }
  }

  function structuredLawFormula(law, geometricRate) {
    return {
      off: "f(s)=0",
      linear: "f(s)=s",
      quadratic: "f(s)=2s^2-1",
      sinusoidal: "f(s)=sin(pi s)",
      radial: "f(s)=2|s|-1",
      geometric: "f(s)=sign(s) expm1(" + geometricRate + "|s|)/expm1(" + geometricRate + ")"
    }[law];
  }

  function normalizeComponent(component, fallbackKind, aliasScale, unit, name) {
    const source = component && typeof component === "object" ? component : {};
    const scale = finiteNonnegative(source.scale === undefined ? aliasScale : source.scale, name + ".scale");
    const kind = scale === 0 ? "off" : (source.kind || fallbackKind);
    if (!["off", "bounded", "probabilistic"].includes(kind)) {
      throw new RangeError(name + ".kind must be off, bounded, or probabilistic");
    }
    const resolvedScale = kind === "off" ? 0 : scale;
    return Object.assign(
      { kind, scale: resolvedScale, unit },
      realismSamplingMetadata(name.replace("realism.", ""), kind, resolvedScale)
    );
  }

  function angleSamplingMetadata(kind, scaleRadians, legacySingleDirection) {
    if (scaleRadians === 0) return {
      samplingLaw: "deterministic zero initial-angle two-vector",
      support: "angleOffset = [0,0] radians"
    };
    if (legacySingleDirection && kind === "bounded") return {
      samplingLaw: "deterministic held-out boundary direction derived from the frozen initial state",
      support: "||angleOffset||_2 = scaleRadians radians"
    };
    return kind === "bounded"
      ? {
          samplingLaw: "seeded uniform-by-area draw on the two-dimensional Euclidean disk",
          support: "||angleOffset||_2 <= scaleRadians radians"
        }
      : {
          samplingLaw: "two seeded independent centred normal coordinates with standard deviation scaleRadians",
          support: "R^2 in radians (unbounded)"
        };
  }

  function actualAngleDistribution(kind, scaleRadians, legacySingleDirection) {
    if (scaleRadians === 0) return "deterministic-zero";
    if (legacySingleDirection && kind === "bounded") return "deterministic-held-out-boundary";
    return kind === "bounded" ? "uniform-disk" : "normal";
  }

  function realismSamplingMetadata(name, kind, scale) {
    if (kind === "off" || scale === 0) {
      const zeroShape = {
        velocity: "angular-velocity two-vector",
        parameters: "five log-parameter coordinates",
        clock: "fractional clock scalar",
        sensor: "selected-sensor sample sequence"
      }[name];
      return {
        samplingLaw: "deterministic zero " + zeroShape,
        support: name === "sensor" ? "sensorNoise[k] = 0 at every nominal sample" : "exact singleton {0} in every coordinate"
      };
    }
    const laws = {
      velocity: kind === "bounded"
        ? {
            samplingLaw: "seeded uniform-by-area draw on the two-dimensional Euclidean disk",
            support: "||velocityOffset||_2 <= scale radians/second"
          }
        : {
            samplingLaw: "two seeded independent centred normal coordinates with standard deviation scale",
            support: "R^2 in radians/second (unbounded)"
          },
      parameters: kind === "bounded"
        ? {
            samplingLaw: "five seeded independent componentwise uniform log-coordinate draws on [-scale,scale]",
            support: "each log offset is in [-scale,scale], so each positive multiplier is in [exp(-scale),exp(scale)]"
          }
        : {
            samplingLaw: "five seeded independent centred normal log-coordinate draws with standard deviation scale",
            support: "R^5 in log coordinates (unbounded); physical multipliers are positive exponentials"
          },
      clock: kind === "bounded"
        ? {
            samplingLaw: "one seeded uniform fractional-clock draw on [-scale,scale]",
            support: "clockFraction in [-scale,scale] with scale < 1"
          }
        : {
            samplingLaw: "clockFraction = tanh(scale*z) for one seeded standard-normal z",
            support: "clockFraction in (-1,1)"
          },
      sensor: kind === "bounded"
        ? {
            samplingLaw: "seeded independent componentwise uniform draws on [-scale,scale] at each nominal sample",
            support: "sensorNoise[k] in [-scale,scale] in selected normalized sensor units"
          }
        : {
            samplingLaw: "seeded independent centred normal draws with standard deviation scale at each nominal sample",
            support: "R at each nominal sample in selected normalized sensor units (unbounded)"
          }
    };
    return laws[name];
  }

  function normalizeRealism(options, uncertaintyKind) {
    const realism = options.realism && typeof options.realism === "object" ? options.realism : {};
    const aliases = options.nuisances && typeof options.nuisances === "object" ? options.nuisances : {};
    const result = {
      velocity: normalizeComponent(realism.velocity, uncertaintyKind, aliases.velocityRadius || 0, "radians/second", "realism.velocity"),
      parameters: normalizeComponent(realism.parameters, uncertaintyKind, aliases.parameterLogRadius || 0, "log multiplicative coordinate", "realism.parameters"),
      clock: normalizeComponent(realism.clock, uncertaintyKind, aliases.clockOffsetRadius || 0, "fractional observation time", "realism.clock"),
      sensor: normalizeComponent(realism.sensor, uncertaintyKind, aliases.sensorNoiseRadius || 0, "selected normalized sensor output", "realism.sensor")
    };
    if (result.clock.kind === "bounded" && result.clock.scale >= 1) {
      throw new RangeError("bounded fractional clock scale must be smaller than one");
    }
    return result;
  }

  function resolveStructuredDirection(forecast, structured) {
    const mode = structured.direction || "oig-weakest";
    if (!ENSEMBLE_DIRECTIONS.includes(mode)) throw new RangeError("unknown structured direction: " + mode);
    let direction;
    if (mode === "custom") direction = structured.customDirection;
    else if (mode === "oig-weakest") direction = forecast.information.weakestDirection;
    else direction = forecast.information.strongestDirection;
    if (!Array.isArray(direction) || direction.length !== 2 || direction.some(value => !Number.isFinite(value))) {
      throw new TypeError("structured direction must resolve to a finite two-vector");
    }
    const norm = Math.hypot(direction[0], direction[1]);
    if (!(norm > 0)) throw new RangeError("structured direction must have positive norm");
    return { mode, vector: [direction[0] / norm, direction[1] / norm] };
  }

  function makeEndpointClassificationPolicy(forecast, legacySingleDirection, law, realism) {
    const preserveLegacyEndpoint = legacySingleDirection && law === "off"
      && Object.values(realism).every(component => component.kind === "off");
    const policy = preserveLegacyEndpoint
      ? {
          mode: "hard-equal-noise-two-radius",
          sensor: forecast.config.sensor,
          sensorLaw: "bounded legacy readout allowance",
          radiusPerReading: forecast.config.noiseRadius,
          cutoff: 2 * forecast.config.noiseRadius
        }
      : realism.sensor.kind === "probabilistic"
        ? {
            mode: "unclassified-probabilistic-sensor",
            sensor: forecast.config.sensor,
            sensorLaw: "probabilistic",
            radiusPerReading: null,
            cutoff: null
          }
        : {
            mode: "hard-equal-noise-two-radius",
            sensor: forecast.config.sensor,
            sensorLaw: realism.sensor.kind === "off" ? "bounded zero-radius" : "bounded",
            radiusPerReading: realism.sensor.scale,
            cutoff: 2 * realism.sensor.scale
          };
    policy.reference = "frozen member-specific structured selected-sensor centre";
    policy.interpretation = policy.mode === "hard-equal-noise-two-radius"
      ? "Finite-model scalar endpoint test: confusable when distance is at most two equal hard sensor-noise radii."
      : "No hard-radius endpoint classification is made for a probabilistic selected-sensor declaration.";
    return policy;
  }

  function buildEnsembleDeclaration(forecast, options) {
    validateForecastForEnsemble(forecast);
    const config = options && typeof options === "object" ? options : {};
    const size = config.size === undefined ? 1 : config.size;
    if (!Number.isInteger(size) || size < 1 || size > 5000) throw new RangeError("ensemble size must be an integer from 1 through 5000");
    const masterSeed = config.seed === undefined ? "oig-wind-tunnel-ensemble-v1" : config.seed;
    deriveSeed(masterSeed, "validation");

    const uncertaintySource = config.uncertainty && typeof config.uncertainty === "object" ? config.uncertainty : {};
    const uncertaintyKind = uncertaintySource.kind || "bounded";
    if (!["bounded", "probabilistic"].includes(uncertaintyKind)) throw new RangeError("uncertainty.kind must be bounded or probabilistic");
    const scaleRadians = finiteNonnegative(
      uncertaintySource.scale === undefined
        ? (uncertaintySource.sigma === undefined ? forecast.config.preparationRadius : uncertaintySource.sigma)
        : uncertaintySource.scale,
      "uncertainty.scale"
    );
    const distribution = uncertaintySource.distribution || (uncertaintyKind === "bounded" ? "uniform-disk" : "normal");
    if ((uncertaintyKind === "bounded" && distribution !== "uniform-disk")
      || (uncertaintyKind === "probabilistic" && distribution !== "normal")) {
      throw new RangeError("bounded uncertainty uses uniform-disk; probabilistic uncertainty uses normal");
    }
    const confidenceMultiplier = uncertaintySource.confidenceMultiplier === undefined ? 1.959963984540054 : uncertaintySource.confidenceMultiplier;
    if (!Number.isFinite(confidenceMultiplier) || confidenceMultiplier <= 0) throw new RangeError("confidenceMultiplier must be positive");

    const structuredSource = config.structured && typeof config.structured === "object" ? config.structured : {};
    const law = structuredSource.law || "off";
    if (!ENSEMBLE_LAWS.includes(law)) throw new RangeError("unknown structured law: " + law);
    const alpha = finiteNonnegative(structuredSource.alpha === undefined ? 0 : structuredSource.alpha, "structured.alpha");
    const amplitudeUnit = structuredSource.amplitudeUnit || "radians";
    if (!["radians", "angle-scale-multiple"].includes(amplitudeUnit)) throw new RangeError("structured.amplitudeUnit is invalid");
    const alphaRadians = amplitudeUnit === "radians" ? alpha : alpha * scaleRadians;
    const geometricRate = structuredSource.geometricRate === undefined ? 2 : structuredSource.geometricRate;
    if (!Number.isFinite(geometricRate) || geometricRate <= 0 || geometricRate > 20) throw new RangeError("geometricRate must lie in (0,20]");
    const direction = resolveStructuredDirection(forecast, structuredSource);
    const realism = normalizeRealism(config, uncertaintyKind);
    const gateSource = config.gates && typeof config.gates === "object" ? config.gates : {};
    const gates = {
      maxEnergyDrift: finiteNonnegative(
        gateSource.maxEnergyDrift === undefined ? forecast.config.energyDriftTolerance : gateSource.maxEnergyDrift,
        "gates.maxEnergyDrift"
      ),
      maxRefinementDiscrepancy: finiteNonnegative(
        gateSource.maxRefinementDiscrepancy === undefined
          ? forecast.config.baselineRefinementTolerance
          : gateSource.maxRefinementDiscrepancy,
        "gates.maxRefinementDiscrepancy"
      ),
      maxResponseRefinementDiscrepancy: finiteNonnegative(
        gateSource.maxResponseRefinementDiscrepancy === undefined
          ? forecast.config.responseRefinementTolerance
          : gateSource.maxResponseRefinementDiscrepancy,
        "gates.maxResponseRefinementDiscrepancy"
      ),
      persistentExitSamples: gateSource.persistentExitSamples === undefined ? 3 : gateSource.persistentExitSamples
    };
    if (!Number.isInteger(gates.persistentExitSamples) || gates.persistentExitSamples < 1) {
      throw new RangeError("gates.persistentExitSamples must be a positive integer");
    }
    const solverOptions = Object.assign(
      { rtol: 2e-10, atol: 2e-12, initialStep: 1e-3, maxStep: 0.025 },
      config.solverOptions && typeof config.solverOptions === "object" ? config.solverOptions : {}
    );
    for (const key of ["rtol", "atol", "initialStep", "maxStep"]) {
      if (!Number.isFinite(solverOptions[key]) || solverOptions[key] <= 0) throw new RangeError("solverOptions." + key + " must be positive");
    }

    const legacySingleDirection = size === 1 && uncertaintyKind === "bounded"
      && scaleRadians === forecast.config.preparationRadius && config.legacySingleDirection !== false;
    const endpointClassificationPolicy = makeEndpointClassificationPolicy(
      forecast, legacySingleDirection, law, realism
    );
    const baselineParameters = validateParameters(forecast.config.parameters);
    const fullStateMetric = {
      id: "wrapped-angle-dimensionless-velocity-euclidean-v1",
      formula: "sqrt(wrap(dtheta1)^2 + wrap(dtheta2)^2 + (sqrt(l1/g)*domega1)^2 + (sqrt(l1/g)*domega2)^2)",
      angleDifference: "principal value atan2(sin(delta),cos(delta)) in radians",
      velocityScaleSeconds: Math.sqrt(baselineParameters.l1 / baselineParameters.g),
      attractionThreshold: null,
      interpretation: "Descriptive full-state distance at matched nominal sample indices; no state-attraction classification is declared."
    };

    const members = Array.from({ length: size }, (_, index) => {
      const s = size === 1 ? 0 : -1 + 2 * index / (size - 1);
      const f = structuredLawValue(law, s, geometricRate);
      const structuredOffset = direction.vector.map(value => alphaRadians * f * value);
      return {
        id: "member-" + String(index + 1).padStart(4, "0"),
        index,
        s,
        f,
        structuredOffset,
        memberSeed: deriveSeed(masterSeed, "member", index),
        hiddenDrawCommitment: null
      };
    });
    const declaration = {
      schemaVersion: ENSEMBLE_SCHEMA_VERSION,
      formula: ENSEMBLE_FORMULA,
      sourceSubspace: ENSEMBLE_SOURCE_SUBSPACE.slice(),
      forecastCommitment: computeForecastCommitment(forecast),
      forecastGeometry: frozenForecastGeometry(forecast),
      size,
      masterSeed,
      seedDerivation: "FNV-1a commitment over stable JSON coordinates; independent member/component/sample streams; v1",
      q0: forecast.config.initialState.slice(0, 2),
      uncertainty: {
        kind: uncertaintyKind,
        distribution: actualAngleDistribution(uncertaintyKind, scaleRadians, legacySingleDirection),
        requestedDistribution: distribution,
        scaleRadians,
        confidenceMultiplier,
        ...angleSamplingMetadata(uncertaintyKind, scaleRadians, legacySingleDirection),
        interpretation: uncertaintyKind === "bounded"
          ? "Every hidden initial-angle draw has Euclidean norm at most scaleRadians."
          : "The two hidden initial-angle coordinates are independent centred normal draws with standard deviation scaleRadians."
      },
      structured: {
        law,
        lawFormula: structuredLawFormula(law, geometricRate),
        alphaInput: alpha,
        amplitudeUnit,
        alphaRadians,
        direction: direction.mode,
        directionVector: direction.vector,
        geometricRate
      },
      realism,
      parameterCoordinates: ENSEMBLE_PARAMETER_COORDINATES.slice(),
      clockMap: ENSEMBLE_CLOCK_MAP,
      predictionBoundary: ENSEMBLE_PREDICTION_BOUNDARY,
      endpointClassificationPolicy,
      fullStateMetric,
      gates,
      solverOptions,
      retainTrajectories: config.retainTrajectories === undefined ? size <= 50 : Boolean(config.retainTrajectories),
      legacySingleDirection,
      members
    };
    for (const member of members) {
      member.hiddenDrawCommitment = checksum(stableSerialize(generateMemberDraws(forecast, declaration, member)));
    }
    declaration.declarationId = checksum(stableSerialize(declaration));
    return declaration;
  }

  function scaledDrawVector(seed, component, count, disk) {
    if (component.kind === "off" || component.scale === 0) return Array(count).fill(0);
    let raw;
    if (component.kind === "probabilistic") raw = normalDraws(seed, count);
    else if (disk && count === 2) raw = boundedDiskDraw(seed);
    else raw = boundedComponentDraws(seed, count);
    return raw.map(value => component.scale * value);
  }

  function generateMemberDraws(forecast, declaration, member) {
    const angleScale = declaration.uncertainty.scaleRadians;
    let angleXi;
    if (angleScale === 0) angleXi = [0, 0];
    else if (declaration.legacySingleDirection && member.index === 0 && declaration.uncertainty.kind === "bounded") {
      const legacyDirection = deterministicDirection(forecast.config.initialState);
      const legacyNorm = Math.hypot(legacyDirection[0], legacyDirection[1]);
      angleXi = [legacyDirection[0] / legacyNorm, legacyDirection[1] / legacyNorm];
    } else if (declaration.uncertainty.kind === "bounded") angleXi = boundedDiskDraw(deriveSeed(member.memberSeed, "angle"));
    else angleXi = normalDraws(deriveSeed(member.memberSeed, "angle"), 2);
    const angleOffset = angleXi.map(value => angleScale * value);
    const velocityOffset = scaledDrawVector(deriveSeed(member.memberSeed, "velocity"), declaration.realism.velocity, 2, true);
    const parameterLogOffsets = scaledDrawVector(deriveSeed(member.memberSeed, "parameters"), declaration.realism.parameters, 5, false);
    let clockFraction = 0;
    if (declaration.realism.clock.kind === "bounded" && declaration.realism.clock.scale > 0) {
      clockFraction = declaration.realism.clock.scale * boundedComponentDraws(deriveSeed(member.memberSeed, "clock"), 1)[0];
    } else if (declaration.realism.clock.kind === "probabilistic" && declaration.realism.clock.scale > 0) {
      clockFraction = Math.tanh(declaration.realism.clock.scale * normalDraws(deriveSeed(member.memberSeed, "clock"), 1)[0]);
    }
    let sensorNoise;
    if (declaration.realism.sensor.kind === "off" || declaration.realism.sensor.scale === 0) {
      sensorNoise = Array(forecast.times.length).fill(0);
    } else if (declaration.realism.sensor.kind === "bounded") {
      sensorNoise = boundedComponentDraws(deriveSeed(member.memberSeed, "sensor"), forecast.times.length)
        .map(value => declaration.realism.sensor.scale * value);
    } else {
      sensorNoise = normalDraws(deriveSeed(member.memberSeed, "sensor"), forecast.times.length)
        .map(value => declaration.realism.sensor.scale * value);
    }
    return {
      angleXi,
      angleOffset,
      velocityOffset,
      parameterLogOffsets,
      parameterMultipliers: parameterLogOffsets.map(Math.exp),
      clockFraction,
      sensorNoise
    };
  }

  function quantile(sorted, probability) {
    if (!sorted.length) return null;
    const position = (sorted.length - 1) * probability;
    const lower = Math.floor(position);
    const fraction = position - lower;
    return sorted[lower] + fraction * (sorted[Math.min(sorted.length - 1, lower + 1)] - sorted[lower]);
  }

  function descriptiveStatistics(values) {
    const finite = values.filter(Number.isFinite).slice().sort((a, b) => a - b);
    if (!finite.length) {
      return { count: 0, min: null, p05: null, p25: null, p50: null, p75: null, p95: null, max: null, mean: null, standardDeviation: null, spread90: null };
    }
    const mean = finite.reduce((sum, value) => sum + value, 0) / finite.length;
    const variance = finite.reduce((sum, value) => sum + (value - mean) ** 2, 0) / finite.length;
    const p05 = quantile(finite, 0.05);
    const p95 = quantile(finite, 0.95);
    return {
      count: finite.length,
      min: finite[0],
      p05,
      p25: quantile(finite, 0.25),
      p50: quantile(finite, 0.5),
      p75: quantile(finite, 0.75),
      p95,
      max: finite[finite.length - 1],
      mean,
      standardDeviation: Math.sqrt(variance),
      spread90: p95 - p05
    };
  }

  function timewiseStatistics(series, sampleCount) {
    const fields = ["min", "p05", "p25", "p50", "p75", "p95", "max", "mean", "standardDeviation", "spread90"];
    const result = Object.fromEntries(fields.map(field => [field, []]));
    for (let index = 0; index < sampleCount; index += 1) {
      const statistics = descriptiveStatistics(series.map(row => row[index]));
      for (const field of fields) result[field].push(statistics[field]);
    }
    return result;
  }

  function populationCovariance(rows, width) {
    if (!rows.length) return Array.from({ length: width }, () => Array(width).fill(null));
    const means = Array.from({ length: width }, (_, column) => rows.reduce((sum, row) => sum + row[column], 0) / rows.length);
    return Array.from({ length: width }, (_, left) => Array.from({ length: width }, (_, right) =>
      rows.reduce((sum, row) => sum + (row[left] - means[left]) * (row[right] - means[right]), 0) / rows.length
    ));
  }

  function wilsonInterval(successes, total) {
    if (!(total > 0)) return null;
    const z = 1.959963984540054;
    const proportion = successes / total;
    const denominator = 1 + z * z / total;
    const centre = (proportion + z * z / (2 * total)) / denominator;
    const radius = z * Math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator;
    return { level: 0.95, lower: Math.max(0, centre - radius), upper: Math.min(1, centre + radius), method: "Wilson score interval" };
  }

  function ensembleContext(forecast, declaration) {
    validateForecastForEnsemble(forecast);
    if (!declaration || declaration.schemaVersion !== ENSEMBLE_SCHEMA_VERSION
      || !Array.isArray(declaration.members) || declaration.members.length !== declaration.size) {
      throw new TypeError("invalid ensemble declaration");
    }
    if (declaration.formula !== ENSEMBLE_FORMULA
      || stableSerialize(declaration.sourceSubspace) !== stableSerialize(ENSEMBLE_SOURCE_SUBSPACE)
      || stableSerialize(declaration.q0) !== stableSerialize(forecast.config.initialState.slice(0, 2))
      || declaration.forecastCommitment !== computeForecastCommitment(forecast)
      || stableSerialize(declaration.forecastGeometry) !== stableSerialize(frozenForecastGeometry(forecast))
      || stableSerialize(declaration.parameterCoordinates) !== stableSerialize(ENSEMBLE_PARAMETER_COORDINATES)
      || declaration.clockMap !== ENSEMBLE_CLOCK_MAP
      || declaration.predictionBoundary !== ENSEMBLE_PREDICTION_BOUNDARY) {
      throw new Error("ensemble declaration is not bound to the supplied frozen forecast semantics");
    }
    if (!Number.isInteger(declaration.size) || declaration.size < 1 || declaration.size > 5000
      || !(typeof declaration.masterSeed === "string" || (Number.isSafeInteger(declaration.masterSeed) && declaration.masterSeed >= 0))
      || typeof declaration.retainTrajectories !== "boolean"
      || typeof declaration.legacySingleDirection !== "boolean") {
      throw new Error("ensemble declaration has invalid canonical controls");
    }
    if (!declaration.uncertainty || !["bounded", "probabilistic"].includes(declaration.uncertainty.kind)) {
      throw new Error("ensemble declaration has invalid uncertainty semantics");
    }
    finiteNonnegative(declaration.uncertainty.scaleRadians, "declaration.uncertainty.scaleRadians");
    if (!Number.isFinite(declaration.uncertainty.confidenceMultiplier) || declaration.uncertainty.confidenceMultiplier <= 0) {
      throw new Error("ensemble declaration has invalid confidence multiplier");
    }
    const expectedRequestedDistribution = declaration.uncertainty.kind === "bounded" ? "uniform-disk" : "normal";
    const expectedActualDistribution = actualAngleDistribution(
      declaration.uncertainty.kind,
      declaration.uncertainty.scaleRadians,
      declaration.legacySingleDirection
    );
    if (declaration.uncertainty.requestedDistribution !== expectedRequestedDistribution
      || declaration.uncertainty.distribution !== expectedActualDistribution) {
      throw new Error("ensemble declaration initial-angle distribution is noncanonical");
    }
    const expectedAngleSampling = angleSamplingMetadata(
      declaration.uncertainty.kind,
      declaration.uncertainty.scaleRadians,
      declaration.legacySingleDirection
    );
    if (declaration.uncertainty.samplingLaw !== expectedAngleSampling.samplingLaw
      || declaration.uncertainty.support !== expectedAngleSampling.support) {
      throw new Error("ensemble declaration initial-angle sampling law or support is noncanonical");
    }
    if (!declaration.structured || !ENSEMBLE_LAWS.includes(declaration.structured.law)
      || !ENSEMBLE_DIRECTIONS.includes(declaration.structured.direction)
      || declaration.structured.lawFormula !== structuredLawFormula(declaration.structured.law, declaration.structured.geometricRate)
      || !Number.isFinite(declaration.structured.alphaInput) || declaration.structured.alphaInput < 0
      || !Number.isFinite(declaration.structured.alphaRadians) || declaration.structured.alphaRadians < 0
      || !["radians", "angle-scale-multiple"].includes(declaration.structured.amplitudeUnit)) {
      throw new Error("ensemble declaration has invalid structured-law semantics");
    }
    const expectedAlpha = declaration.structured.amplitudeUnit === "radians"
      ? declaration.structured.alphaInput
      : declaration.structured.alphaInput * declaration.uncertainty.scaleRadians;
    const expectedDirection = resolveStructuredDirection(forecast, {
      direction: declaration.structured.direction,
      customDirection: declaration.structured.directionVector
    }).vector;
    if (Math.abs(expectedAlpha - declaration.structured.alphaRadians) > 1e-15
      || !Array.isArray(declaration.structured.directionVector) || declaration.structured.directionVector.length !== 2
      || declaration.structured.directionVector.some((value, axis) => !Number.isFinite(value) || Math.abs(value - expectedDirection[axis]) > 1e-15)) {
      throw new Error("ensemble declaration structured scale or direction is noncanonical");
    }
    const expectedUnits = {
      velocity: "radians/second",
      parameters: "log multiplicative coordinate",
      clock: "fractional observation time",
      sensor: "selected normalized sensor output"
    };
    for (const name of Object.keys(expectedUnits)) {
      const component = declaration.realism && declaration.realism[name];
      if (!component || !["off", "bounded", "probabilistic"].includes(component.kind)
        || !Number.isFinite(component.scale) || component.scale < 0
        || (component.kind === "off" && component.scale !== 0)
        || component.unit !== expectedUnits[name]) {
        throw new Error("ensemble declaration realism component is noncanonical: " + name);
      }
      const expectedSampling = realismSamplingMetadata(name, component.kind, component.scale);
      if (component.samplingLaw !== expectedSampling.samplingLaw
        || component.support !== expectedSampling.support) {
        throw new Error("ensemble declaration realism sampling law or support is noncanonical: " + name);
      }
    }
    if (declaration.realism.clock.kind === "bounded" && declaration.realism.clock.scale >= 1) {
      throw new Error("ensemble declaration bounded clock scale is unsafe");
    }
    const expectedEndpointPolicy = makeEndpointClassificationPolicy(
      forecast, declaration.legacySingleDirection, declaration.structured.law, declaration.realism
    );
    if (stableSerialize(declaration.endpointClassificationPolicy) !== stableSerialize(expectedEndpointPolicy)) {
      throw new Error("ensemble declaration endpoint classification policy is noncanonical");
    }
    const baselineParameters = validateParameters(forecast.config.parameters);
    if (!declaration.fullStateMetric
      || declaration.fullStateMetric.id !== "wrapped-angle-dimensionless-velocity-euclidean-v1"
      || declaration.fullStateMetric.formula !== "sqrt(wrap(dtheta1)^2 + wrap(dtheta2)^2 + (sqrt(l1/g)*domega1)^2 + (sqrt(l1/g)*domega2)^2)"
      || declaration.fullStateMetric.angleDifference !== "principal value atan2(sin(delta),cos(delta)) in radians"
      || declaration.fullStateMetric.velocityScaleSeconds !== Math.sqrt(baselineParameters.l1 / baselineParameters.g)
      || declaration.fullStateMetric.attractionThreshold !== null) {
      throw new Error("ensemble declaration full-state metric is noncanonical");
    }
    for (const key of ["rtol", "atol", "initialStep", "maxStep"]) {
      if (!declaration.solverOptions || !Number.isFinite(declaration.solverOptions[key]) || declaration.solverOptions[key] <= 0) {
        throw new Error("ensemble declaration solver controls are invalid");
      }
    }
    const declarationCopy = Object.assign({}, declaration);
    delete declarationCopy.declarationId;
    if (declaration.declarationId !== checksum(stableSerialize(declarationCopy))) {
      throw new Error("ensemble declaration commitment mismatch");
    }
    for (const key of ["maxEnergyDrift", "maxRefinementDiscrepancy", "maxResponseRefinementDiscrepancy"]) {
      finiteNonnegative(declaration.gates && declaration.gates[key], "declaration.gates." + key);
    }
    if (!Number.isInteger(declaration.gates.persistentExitSamples) || declaration.gates.persistentExitSamples < 1) {
      throw new RangeError("declaration persistent-exit gate is invalid");
    }
    declaration.members.forEach((member, index) => {
      const expectedS = declaration.size === 1 ? 0 : -1 + 2 * index / (declaration.size - 1);
      const expectedF = structuredLawValue(declaration.structured.law, expectedS, declaration.structured.geometricRate);
      const expectedOffset = declaration.structured.directionVector.map(value => declaration.structured.alphaRadians * expectedF * value);
      if (!member || member.index !== index || member.id !== "member-" + String(index + 1).padStart(4, "0")
        || member.memberSeed !== deriveSeed(declaration.masterSeed, "member", index)
        || !Number.isFinite(member.s) || Math.abs(member.s - expectedS) > 1e-15
        || !Number.isFinite(member.f) || Math.abs(member.f - expectedF) > 1e-15
        || !Array.isArray(member.structuredOffset) || member.structuredOffset.length !== 2
        || member.structuredOffset.some((value, axis) => !Number.isFinite(value) || Math.abs(value - expectedOffset[axis]) > 1e-15)
        || typeof member.hiddenDrawCommitment !== "string"
        || member.hiddenDrawCommitment !== checksum(stableSerialize(generateMemberDraws(forecast, declaration, member)))) {
        throw new Error("noncanonical ensemble member declaration at index " + index);
      }
    });
    const independentBaseline = simulateAdaptive(
      forecast.config.initialState,
      forecast.times,
      forecast.config.parameters,
      declaration.solverOptions
    );
    const refinedBaselineSensor = sensorSeries(forecast.config.sensor, independentBaseline, forecast.config.parameters);
    const refinementDiscrepancy = Math.sqrt(refinedBaselineSensor.reduce(
      (sum, value, index) => sum + (value - forecast.baselineSensor[index]) ** 2,
      0
    ) / forecast.times.length);
    return { forecast, declaration, independentBaseline, refinedBaselineSensor, refinementDiscrepancy };
  }

  function firstPersistentExit(inside, requiredSamples) {
    let outsideRun = 0;
    for (let index = 0; index < inside.length; index += 1) {
      outsideRun = inside[index] ? 0 : outsideRun + 1;
      if (outsideRun >= requiredSamples) return index - requiredSamples + 1;
    }
    return null;
  }

  function wrappedAngleDifference(left, right) {
    const difference = left - right;
    return Math.atan2(Math.sin(difference), Math.cos(difference));
  }

  function scaledFullStateDistance(state, baselineState, velocityScale) {
    const dTheta1 = wrappedAngleDifference(state[0], baselineState[0]);
    const dTheta2 = wrappedAngleDifference(state[1], baselineState[1]);
    const dOmega1 = velocityScale * (state[2] - baselineState[2]);
    const dOmega2 = velocityScale * (state[3] - baselineState[3]);
    return Math.hypot(dTheta1, dTheta2, dOmega1, dOmega2);
  }

  function declaredEnsembleTubeRadius(declaration, index) {
    const geometry = declaration.forecastGeometry;
    const preserveLegacyTube = declaration.size === 1 && declaration.legacySingleDirection
      && declaration.structured.law === "off"
      && Object.values(declaration.realism).every(component => component.kind === "off");
    if (preserveLegacyTube) return geometry.tubeRadius[index];
    const row = geometry.gradients[index];
    const responseNorm = Math.hypot(row[0], row[1]);
    const boundedPart = (declaration.uncertainty.kind === "bounded"
      ? declaration.uncertainty.scaleRadians * responseNorm : 0)
      + (declaration.realism.sensor.kind === "bounded" ? declaration.realism.sensor.scale : 0);
    const probabilisticVariance = (declaration.uncertainty.kind === "probabilistic"
      ? declaration.uncertainty.scaleRadians ** 2 * responseNorm ** 2 : 0)
      + (declaration.realism.sensor.kind === "probabilistic" ? declaration.realism.sensor.scale ** 2 : 0);
    return boundedPart + declaration.uncertainty.confidenceMultiplier * Math.sqrt(probabilisticVariance);
  }

  function evaluateEnsembleMember(context, member) {
    const { forecast, declaration, independentBaseline, refinedBaselineSensor, refinementDiscrepancy } = context;
    const draws = generateMemberDraws(forecast, declaration, member);
    if (checksum(stableSerialize(draws)) !== member.hiddenDrawCommitment) throw new Error("hidden draw commitment mismatch");
    const initialState = forecast.config.initialState.slice();
    initialState[0] += member.structuredOffset[0] + draws.angleOffset[0];
    initialState[1] += member.structuredOffset[1] + draws.angleOffset[1];
    initialState[2] += draws.velocityOffset[0];
    initialState[3] += draws.velocityOffset[1];
    const baseParameters = validateParameters(forecast.config.parameters);
    const parameterNames = ["m1", "m2", "l1", "l2", "g"];
    const parameters = Object.fromEntries(parameterNames.map((name, index) => [name, baseParameters[name] * draws.parameterMultipliers[index]]));
    const memberTimes = forecast.times.map(time => time * (1 + draws.clockFraction));
    const actual = simulateAdaptive(initialState, memberTimes, parameters, declaration.solverOptions);
    const noiselessSensor = sensorSeries(forecast.config.sensor, actual, parameters);
    const actualSeries = noiselessSensor.map((value, index) => value + draws.sensorNoise[index]);
    const structuredCentreSeries = forecast.baselineSensor.map((value, index) =>
      value + forecast.gradients[index][0] * member.structuredOffset[0]
        + forecast.gradients[index][1] * member.structuredOffset[1]
    );
    const predictedSeries = structuredCentreSeries.map((value, index) =>
      value + forecast.gradients[index][0] * draws.angleOffset[0]
        + forecast.gradients[index][1] * draws.angleOffset[1] + draws.sensorNoise[index]
    );
    const preserveLegacyTube = declaration.size === 1 && declaration.legacySingleDirection
      && declaration.structured.law === "off"
      && Object.values(declaration.realism).every(component => component.kind === "off");
    const tubeRadius = forecast.times.map((_, index) => declaredEnsembleTubeRadius(declaration, index));
    const inside = actualSeries.map((value, index) =>
      Math.abs(value - structuredCentreSeries[index]) <= tubeRadius[index] + 1e-12
    );
    const firstExitIndex = inside.findIndex(value => !value);
    const reentryOffset = firstExitIndex < 0 ? -1 : inside.slice(firstExitIndex + 1).findIndex(Boolean);
    const reentryIndex = reentryOffset < 0 ? null : firstExitIndex + 1 + reentryOffset;
    const persistentExitIndex = firstPersistentExit(inside, declaration.gates.persistentExitSamples);
    const fullStateDistanceSeries = actual.states.map((state, index) =>
      scaledFullStateDistance(
        state,
        independentBaseline.states[index],
        declaration.fullStateMetric.velocityScaleSeconds
      )
    );
    const postExitStateDistances = firstExitIndex < 0 ? [] : fullStateDistanceSeries.slice(firstExitIndex);
    const minimumPostExitStateDistance = postExitStateDistances.length ? Math.min(...postExitStateDistances) : null;
    const minimumPostExitStateIndex = minimumPostExitStateDistance === null
      ? null
      : firstExitIndex + postExitStateDistances.indexOf(minimumPostExitStateDistance);
    const angleTotalOffset = member.structuredOffset.map((value, index) => value + draws.angleOffset[index]);
    const angleNorm = Math.hypot(...angleTotalOffset);
    const amplificationDenominator = preserveLegacyTube ? forecast.config.preparationRadius : angleNorm;
    let actualSquare = 0;
    let predictedSquare = 0;
    const projectedDifference = [];
    for (let index = 0; index < forecast.times.length; index += 1) {
      const actualDifference = actualSeries[index] - refinedBaselineSensor[index];
      const predictedDifference = preserveLegacyTube
        ? forecast.config.preparationRadius
          * (forecast.gradients[index][0] * draws.angleXi[0] + forecast.gradients[index][1] * draws.angleXi[1])
        : predictedSeries[index] - forecast.baselineSensor[index];
      actualSquare += actualDifference * actualDifference;
      predictedSquare += predictedDifference * predictedDifference;
      projectedDifference.push(Math.abs(actualSeries[index] - structuredCentreSeries[index]));
    }
    const actualAmplification = amplificationDenominator > 0
      ? Math.sqrt(actualSquare / forecast.times.length) / amplificationDenominator
      : null;
    const predictedAmplification = amplificationDenominator > 0
      ? Math.sqrt(predictedSquare / forecast.times.length) / amplificationDenominator
      : null;
    const peakSeparation = Math.max(...projectedDifference);
    const peakIndex = projectedDifference.indexOf(peakSeparation);
    const postPeak = projectedDifference.slice(peakIndex);
    const minimumPostPeakSeparation = Math.min(...postPeak);
    const reconvergenceIndex = peakIndex + postPeak.indexOf(minimumPostPeakSeparation);
    const energy0 = energy(actual.states[0], parameters);
    const energyScale = Math.max(1, Math.abs(energy0));
    const maxEnergyDrift = Math.max(...actual.states.map(state => Math.abs(energy(state, parameters) - energy0) / energyScale));
    const actualEndpoint = actualSeries[actualSeries.length - 1];
    const structuredCentreEndpoint = structuredCentreSeries[structuredCentreSeries.length - 1];
    const endpointDistance = Math.abs(actualEndpoint - structuredCentreEndpoint);
    const endpointPolicy = declaration.endpointClassificationPolicy;
    const endpointClassification = endpointPolicy.mode === "hard-equal-noise-two-radius"
      ? (endpointDistance <= endpointPolicy.cutoff ? "confusable" : "separated")
      : "unclassified";
    const terminalState = actual.states[actual.states.length - 1].slice();
    const sensorSquareMean = actualSeries.reduce((sum, value) => sum + value * value, 0) / actualSeries.length;
    const compactOutcome = {
      sampleCount: actualSeries.length,
      terminalState,
      terminalSensor: actualEndpoint,
      sensorMinimum: Math.min(...actualSeries),
      sensorMaximum: Math.max(...actualSeries),
      sensorRms: Math.sqrt(sensorSquareMean),
      sensorSeriesDigest: checksum(stableSerialize(actualSeries)),
      terminalStateDigest: checksum(stableSerialize(terminalState)),
      nominalEndTime: forecast.times[forecast.times.length - 1],
      memberEndTime: memberTimes[memberTimes.length - 1]
    };
    const reasons = [];
    if (maxEnergyDrift > declaration.gates.maxEnergyDrift) reasons.push("energy-drift-gate");
    if (refinementDiscrepancy > declaration.gates.maxRefinementDiscrepancy) reasons.push("baseline-refinement-gate");
    if (!Number.isFinite(forecast.responseRefinement.maximumRelativeDiscrepancy)
      || forecast.responseRefinement.maximumRelativeDiscrepancy > declaration.gates.maxResponseRefinementDiscrepancy) {
      reasons.push("response-refinement-gate");
    }
    const record = {
      id: member.id,
      index: member.index,
      memberSeed: member.memberSeed,
      s: member.s,
      f: member.f,
      structuredOffset: member.structuredOffset,
      draws,
      initialState,
      parameters,
      nominalTimes: forecast.times,
      memberTimes,
      predictedCentreDefinition: "Frozen baseline plus the known structured first-order angle response; hidden draws are not used to tailor the centre or tube.",
      audit: {
        coverage: inside.filter(Boolean).length / inside.length,
        inside,
        firstExitIndex: firstExitIndex < 0 ? null : firstExitIndex,
        firstExitTime: firstExitIndex < 0 ? null : forecast.times[firstExitIndex],
        persistentExitIndex,
        persistentExitTime: persistentExitIndex === null ? null : forecast.times[persistentExitIndex],
        amplification: {
          denominatorAngleNormRadians: amplificationDenominator,
          actual: actualAmplification,
          predictedInitialAngleLinearization: predictedAmplification,
          ratio: actualAmplification !== null && predictedAmplification > 0 ? actualAmplification / predictedAmplification : null
        },
        projectedReconvergence: {
          peakSeparation,
          peakTime: forecast.times[peakIndex],
          minimumPostPeakSeparation,
          time: forecast.times[reconvergenceIndex],
          ratio: peakSeparation > 0 ? minimumPostPeakSeparation / peakSeparation : null,
          exitIndex: firstExitIndex < 0 ? null : firstExitIndex,
          exitTime: firstExitIndex < 0 ? null : forecast.times[firstExitIndex],
          reentryIndex,
          reentryTime: reentryIndex === null ? null : forecast.times[reentryIndex],
          exitedThenReenteredTube: reentryIndex !== null,
          withinDeclaredReadoutRadius: reentryIndex !== null,
          interpretation: "Exit from and later return to the declared scalar sensor-output tube only; not state-space convergence, stability, or synchronization."
        },
        fullStateComparison: {
          metricId: declaration.fullStateMetric.id,
          outputReentryStateDistance: reentryIndex === null ? null : fullStateDistanceSeries[reentryIndex],
          outputReentryIndex: reentryIndex,
          outputReentryTime: reentryIndex === null ? null : forecast.times[reentryIndex],
          terminalStateDistance: fullStateDistanceSeries[fullStateDistanceSeries.length - 1],
          minimumPostOutputExitStateDistance: minimumPostExitStateDistance,
          minimumPostOutputExitIndex: minimumPostExitStateIndex,
          minimumPostOutputExitTime: minimumPostExitStateIndex === null ? null : forecast.times[minimumPostExitStateIndex],
          attractionClassification: "not declared",
          interpretation: declaration.fullStateMetric.interpretation
        },
        endpointClassification: {
          actualEndpoint,
          structuredCentreEndpoint,
          distance: endpointDistance,
          radiusPerReading: endpointPolicy.radiusPerReading,
          cutoff: endpointPolicy.cutoff,
          classification: endpointClassification,
          hardRadiusTest: endpointPolicy.mode === "hard-equal-noise-two-radius",
          reference: endpointPolicy.reference,
          interpretation: endpointPolicy.interpretation
        },
        maxEnergyDrift,
        refinementDiscrepancy,
        status: reasons.length ? "unresolved" : "resolved",
        unresolvedReasons: reasons
      }
    };
    record.compactOutcome = compactOutcome;
    record._actualSeries = actualSeries;
    record._predictedSeries = predictedSeries;
    record._structuredCentreSeries = structuredCentreSeries;
    record._tubeRadius = tubeRadius;
    record._terminalState = terminalState;
    record._fullStateDistanceSeries = fullStateDistanceSeries;
    if (declaration.retainTrajectories) {
      record.trajectory = actual;
      record.actualSensorSeries = actualSeries;
      record.predictedSensorSeries = predictedSeries;
      record.structuredCentreSeries = structuredCentreSeries;
      record.tubeRadius = tubeRadius;
      record.fullStateDistanceSeries = fullStateDistanceSeries;
    }
    return record;
  }

  function terminalOutlierSummary(members) {
    const values = members.map(member => ({
      id: member.id,
      index: member.index,
      value: member.compactOutcome
        ? member.compactOutcome.terminalSensor
        : (member._actualSeries || member.actualSensorSeries).at(-1)
    })).filter(item => Number.isFinite(item.value));
    const ordered = values.map(item => item.value).sort((a, b) => a - b);
    const q1 = quantile(ordered, 0.25);
    const q3 = quantile(ordered, 0.75);
    const iqr = q1 === null || q3 === null ? null : q3 - q1;
    const lowerFence = iqr === null ? null : q1 - 1.5 * iqr;
    const upperFence = iqr === null ? null : q3 + 1.5 * iqr;
    const outliers = iqr === null ? [] : values.filter(item => item.value < lowerFence || item.value > upperFence)
      .map(item => Object.assign({}, item, {
        side: item.value < lowerFence ? "low" : "high",
        excessBeyondFence: item.value < lowerFence ? lowerFence - item.value : item.value - upperFence
      }))
      .sort((left, right) => right.excessBeyondFence - left.excessBeyondFence || left.index - right.index);
    return {
      ruleId: "tukey-1.5-iqr-terminal-selected-sensor",
      rule: "Resolved-member terminal selected-sensor values outside [Q1-1.5 IQR, Q3+1.5 IQR].",
      q1,
      q3,
      iqr,
      lowerFence,
      upperFence,
      count: outliers.length,
      memberIds: outliers.map(item => item.id),
      representatives: outliers.slice(0, 12),
      representativeLimit: 12,
      interpretation: "Descriptive finite-ensemble scalar-output outliers only; not anomalous physical systems or proof failures."
    };
  }

  function summarizeEnsemble(forecast, declaration, members, context) {
    validateForecastForEnsemble(forecast);
    if (!Array.isArray(members) || members.length !== declaration.size) throw new TypeError("member records do not match declaration");
    const resolved = members.filter(member => member.audit && member.audit.status === "resolved");
    const actualSeries = resolved.map(member => member._actualSeries || member.actualSensorSeries);
    const predictedSeries = resolved.map(member => member._predictedSeries || member.predictedSensorSeries);
    const sampleCount = forecast.times.length;
    const coverage = Array.from({ length: sampleCount }, (_, index) =>
      resolved.length ? resolved.filter(member => member.audit.inside[index]).length / resolved.length : null
    );
    const survival = Array.from({ length: sampleCount }, (_, index) =>
      resolved.length
        ? resolved.filter(member => member.audit.firstExitIndex === null || member.audit.firstExitIndex > index).length / resolved.length
        : null
    );
    const totalSamples = resolved.length * sampleCount;
    const insideSamples = resolved.reduce((sum, member) => sum + member.audit.inside.filter(Boolean).length, 0);
    const wholeMembers = resolved.filter(member => member.audit.firstExitIndex === null).length;
    const iid = declaration.size > 1
      && resolved.length === declaration.size
      && resolved.length > 0
      && declaration.structured.law === "off"
      && declaration.uncertainty.kind === "probabilistic"
      && (declaration.uncertainty.scaleRadians > 0
        || Object.values(declaration.realism).some(component => component.kind === "probabilistic" && component.scale > 0))
      && Object.values(declaration.realism).every(component => component.kind === "off" || component.kind === "probabilistic");
    const terminalStates = resolved.map(member => member._terminalState || member.trajectory.states[member.trajectory.states.length - 1]);
    const initialAngles = resolved.map(member => member.initialState.slice(0, 2));
    const summary = {
      schemaVersion: ENSEMBLE_SCHEMA_VERSION + "-summary",
      resolvedMemberCount: resolved.length,
      unresolvedMemberCount: members.length - resolved.length,
      timewise: {
        times: forecast.times.slice(),
        actual: timewiseStatistics(actualSeries, sampleCount),
        predicted: timewiseStatistics(predictedSeries, sampleCount),
        coverage,
        survival,
        percentileConvention: "Hyndman-Fan type 7 linear interpolation; descriptive population summaries.",
        predictedInterpretation: "Predicted quantiles couple the frozen linear response and additive selected-sensor law to their declared hidden draws after reveal. They do not propagate velocity, parameter, or clock draws."
      },
      coverage: {
        sampleFraction: totalSamples ? insideSamples / totalSamples : null,
        wholeMemberFraction: resolved.length ? wholeMembers / resolved.length : null,
        wilson95: iid ? Object.assign(wilsonInterval(wholeMembers, resolved.length), {
          event: "whole-horizon member survival (no sampled tube exit)",
          successes: wholeMembers,
          trials: resolved.length
        }) : null,
        intervalInterpretation: iid
          ? "Descriptive Wilson interval under the declared iid probabilistic sampling interpretation."
          : resolved.length !== declaration.size
            ? "No probability interval: unresolved members make the declared iid sample incomplete."
            : "No probability interval: the ensemble is deterministic, structured, bounded-design, zero-variation, or otherwise not declared iid."
      },
      exits: {
        firstExitFraction: resolved.length
          ? resolved.filter(member => member.audit.firstExitIndex !== null).length / resolved.length
          : null,
        persistentExitFraction: resolved.length
          ? resolved.filter(member => member.audit.persistentExitIndex !== null).length / resolved.length
          : null,
        persistentExitDefinition: "The start of the first run of at least " + declaration.gates.persistentExitSamples + " consecutive samples outside the frozen linearized tube; later re-entry does not erase it."
      },
      amplification: {
        actual: descriptiveStatistics(resolved.map(member => member.audit.amplification.actual)),
        predicted: descriptiveStatistics(resolved.map(member => member.audit.amplification.predictedInitialAngleLinearization)),
        ratio: descriptiveStatistics(resolved.map(member => member.audit.amplification.ratio)),
        interpretation: "RMS selected-sensor separation divided by the total initial-angle offset norm; null when that norm is zero."
      },
      projectedReconvergence: {
        ratio: descriptiveStatistics(resolved.map(member => member.audit.projectedReconvergence.ratio)),
        exitedAndReenteredTubeFraction: resolved.length
          ? resolved.filter(member => member.audit.projectedReconvergence.exitedThenReenteredTube).length / resolved.length
          : null,
        withinDeclaredReadoutRadiusFraction: resolved.length
          ? resolved.filter(member => member.audit.projectedReconvergence.withinDeclaredReadoutRadius).length / resolved.length
          : null,
        fullStateAtOutputReentry: descriptiveStatistics(resolved
          .filter(member => member.audit.projectedReconvergence.exitedThenReenteredTube)
          .map(member => member.audit.fullStateComparison.outputReentryStateDistance)),
        terminalFullStateDistanceForOutputReenteredMembers: descriptiveStatistics(resolved
          .filter(member => member.audit.projectedReconvergence.exitedThenReenteredTube)
          .map(member => member.audit.fullStateComparison.terminalStateDistance)),
        interpretation: "Selected-sensor projection only; never a state-space synchronization claim."
      },
      terminalOutliers: terminalOutlierSummary(resolved),
      covariance: {
        initialAngles: populationCovariance(initialAngles, 2),
        terminalState: populationCovariance(terminalStates, 4),
        denominator: "population denominator N over resolved members"
      },
      gates: {
        maxEnergyDrift: declaration.gates.maxEnergyDrift,
        maxRefinementDiscrepancy: declaration.gates.maxRefinementDiscrepancy,
        maxResponseRefinementDiscrepancy: declaration.gates.maxResponseRefinementDiscrepancy,
        responseRefinementTolerance: declaration.gates.maxResponseRefinementDiscrepancy,
        measuredRefinementDiscrepancy: context ? context.refinementDiscrepancy : null,
        measuredResponseRefinementDiscrepancy: forecast.responseRefinement.maximumRelativeDiscrepancy,
        responseRefinementMaximumRelativeDiscrepancy: forecast.responseRefinement.maximumRelativeDiscrepancy,
        energyPassCount: members.filter(member => member.audit
          && Number.isFinite(member.audit.maxEnergyDrift)
          && member.audit.maxEnergyDrift <= declaration.gates.maxEnergyDrift).length,
        refinementPassed: context ? context.refinementDiscrepancy <= declaration.gates.maxRefinementDiscrepancy : null,
        responseRefinementPassed: Number.isFinite(forecast.responseRefinement.maximumRelativeDiscrepancy)
          && forecast.responseRefinement.maximumRelativeDiscrepancy <= declaration.gates.maxResponseRefinementDiscrepancy,
        refinedEvidencePassed: context
          ? context.refinementDiscrepancy <= declaration.gates.maxRefinementDiscrepancy
            && Number.isFinite(forecast.responseRefinement.maximumRelativeDiscrepancy)
            && forecast.responseRefinement.maximumRelativeDiscrepancy <= declaration.gates.maxResponseRefinementDiscrepancy
          : false,
        refinedEvidenceStatus: context
          && context.refinementDiscrepancy <= declaration.gates.maxRefinementDiscrepancy
          && Number.isFinite(forecast.responseRefinement.maximumRelativeDiscrepancy)
          && forecast.responseRefinement.maximumRelativeDiscrepancy <= declaration.gates.maxResponseRefinementDiscrepancy
          ? "refined"
          : "unresolved",
        status: resolved.length === members.length ? "resolved" : "unresolved",
        unresolvedMembers: members.filter(member => !member.audit || member.audit.status !== "resolved")
          .map(member => ({ id: member.id, reasons: member.audit ? member.audit.unresolvedReasons : ["solver-error"] }))
      },
      interpretation: {
        evidence: "Numerical ensemble calibration; no outward enclosure or exact-flow certificate.",
        tube: declaration.predictionBoundary,
        actual: "Each outcome uses an adaptive integrator with exact revealed deterministic draws, but shares the declared browser mechanics.",
        atlas: "Exit, survival, and reconvergence are finite-time selected-sensor statements."
      }
    };
    return summary;
  }

  function publicMemberRecord(record) {
    const result = Object.assign({}, record);
    for (const key of ["_actualSeries", "_predictedSeries", "_structuredCentreSeries", "_tubeRadius", "_terminalState", "_fullStateDistanceSeries"]) delete result[key];
    return result;
  }

  function checkedCallbacks(callbacks) {
    const source = callbacks && typeof callbacks === "object" ? callbacks : {};
    return {
      onProgress: typeof source.onProgress === "function" ? source.onProgress : () => {},
      isCancelled: typeof source.isCancelled === "function" ? source.isCancelled : () => false,
      yieldEvery: Number.isInteger(source.yieldEvery) && source.yieldEvery > 0 ? source.yieldEvery : 2
    };
  }

  function finishEnsemble(context, records) {
    const summary = summarizeEnsemble(context.forecast, context.declaration, records, context);
    const payload = {
      schemaVersion: ENSEMBLE_SCHEMA_VERSION + "-result",
      declaration: context.declaration,
      comparisonBaseline: {
        method: context.independentBaseline.method,
        times: context.independentBaseline.times,
        states: context.independentBaseline.states,
        metricId: context.declaration.fullStateMetric.id
      },
      members: records.map(publicMemberRecord),
      summary
    };
    return Object.assign(payload, { resultId: checksum(stableSerialize(payload)) });
  }

  function replayEnsembleResult(declaration) {
    const geometry = declaration && declaration.forecastGeometry;
    if (!geometry || !geometry.config) throw new TypeError("ensemble result lacks frozen forecast geometry");
    const replayForecast = forecastExperiment(geometry.config);
    if (stableSerialize(frozenForecastGeometry(replayForecast)) !== stableSerialize(geometry)) {
      throw new Error("ensemble frozen forecast scientific payload integrity mismatch");
    }
    const context = ensembleContext(replayForecast, declaration);
    const records = declaration.members.map(member => {
      try {
        return evaluateEnsembleMember(context, member);
      } catch (error) {
        if (error && error.code === "OIG_CANCELLED") throw error;
        return {
          id: member.id,
          index: member.index,
          memberSeed: member.memberSeed,
          draws: generateMemberDraws(replayForecast, declaration, member),
          audit: {
            status: "unresolved",
            unresolvedReasons: ["solver-error"],
            error: String(error && error.message ? error.message : error)
          }
        };
      }
    });
    return finishEnsemble(context, records);
  }

  function verifyEnsembleResult(result) {
    if (!result || result.schemaVersion !== ENSEMBLE_SCHEMA_VERSION + "-result"
      || !result.declaration || !result.comparisonBaseline || !Array.isArray(result.members) || !result.summary) {
      throw new TypeError("invalid ensemble result structure");
    }
    // A public checksum detects accidental changes only when its value is anchored
    // elsewhere. Rebuild every deterministic numerical layer here so a caller cannot
    // alter a scientific field and simply recompute its self-checksum.
    const expected = replayEnsembleResult(result.declaration);
    if (stableSerialize(result.comparisonBaseline) !== stableSerialize(expected.comparisonBaseline)) {
      throw new Error("ensemble comparison baseline scientific payload integrity mismatch");
    }
    if (result.members.length !== expected.members.length) {
      throw new Error("ensemble result member count integrity mismatch");
    }
    result.members.forEach((member, index) => {
      if (stableSerialize(member) !== stableSerialize(expected.members[index])) {
        throw new Error((result.declaration.retainTrajectories
          ? "retained ensemble series"
          : "compact ensemble outcome") + " scientific payload integrity mismatch at index " + index);
      }
    });
    if (stableSerialize(result.summary) !== stableSerialize(expected.summary)) {
      throw new Error("ensemble summary scientific payload integrity mismatch");
    }
    if (result.resultId !== expected.resultId) {
      throw new Error("ensemble resultId does not commit the complete public scientific payload");
    }
    if (stableSerialize(result) !== stableSerialize(expected)) {
      throw new Error("ensemble result contains noncanonical public scientific payload");
    }
    return {
      valid: true,
      verification: "Deterministic same-code forecast, baseline, and member replay plus cross-field integrity; not an outward enclosure, external provenance proof, or physical-model validation.",
      resultId: result.resultId
    };
  }

  function runEnsemble(forecast, declarationOrOptions, callbacks) {
    const declaration = declarationOrOptions && declarationOrOptions.schemaVersion === ENSEMBLE_SCHEMA_VERSION
      ? declarationOrOptions
      : buildEnsembleDeclaration(forecast, declarationOrOptions);
    const controls = checkedCallbacks(callbacks);
    const context = ensembleContext(forecast, declaration);
    const records = [];
    for (let index = 0; index < declaration.members.length; index += 1) {
      if (controls.isCancelled()) throw new CancellationError();
      try {
        records.push(evaluateEnsembleMember(context, declaration.members[index]));
      } catch (error) {
        if (error && error.code === "OIG_CANCELLED") throw error;
        records.push({
          id: declaration.members[index].id,
          index,
          memberSeed: declaration.members[index].memberSeed,
          draws: generateMemberDraws(forecast, declaration, declaration.members[index]),
          audit: { status: "unresolved", unresolvedReasons: ["solver-error"], error: String(error && error.message ? error.message : error) }
        });
      }
      controls.onProgress({ phase: "ensemble-members", completed: index + 1, total: declaration.size, fraction: (index + 1) / declaration.size });
    }
    return finishEnsemble(context, records);
  }

  async function runEnsembleAsync(forecast, declarationOrOptions, callbacks) {
    const declaration = declarationOrOptions && declarationOrOptions.schemaVersion === ENSEMBLE_SCHEMA_VERSION
      ? declarationOrOptions
      : buildEnsembleDeclaration(forecast, declarationOrOptions);
    const controls = checkedCallbacks(callbacks);
    const context = ensembleContext(forecast, declaration);
    const records = [];
    for (let index = 0; index < declaration.members.length; index += 1) {
      if (controls.isCancelled()) throw new CancellationError();
      try {
        records.push(evaluateEnsembleMember(context, declaration.members[index]));
      } catch (error) {
        if (error && error.code === "OIG_CANCELLED") throw error;
        records.push({
          id: declaration.members[index].id,
          index,
          memberSeed: declaration.members[index].memberSeed,
          draws: generateMemberDraws(forecast, declaration, declaration.members[index]),
          audit: { status: "unresolved", unresolvedReasons: ["solver-error"], error: String(error && error.message ? error.message : error) }
        });
      }
      controls.onProgress({ phase: "ensemble-members", completed: index + 1, total: declaration.size, fraction: (index + 1) / declaration.size });
      if ((index + 1) % controls.yieldEvery === 0) await new Promise(resolve => setTimeout(resolve, 0));
    }
    if (controls.isCancelled()) throw new CancellationError();
    return finishEnsemble(context, records);
  }

  function estimateLaboratoryResources(sizes, horizons, laws, amplitudes, repeats, observationStep) {
    const sampleCounts = horizons.map(horizon => Math.max(2, Math.round(horizon / observationStep) + 1));
    const runCount = sizes.length * horizons.length * laws.length * amplitudes.length * repeats;
    const memberRecordCount = sizes.reduce((sum, size) => sum + size, 0)
      * horizons.length * laws.length * amplitudes.length * repeats;
    const aggregateTimeSampleCount = sampleCounts.reduce((sum, count) => sum + count, 0)
      * sizes.length * laws.length * amplitudes.length * repeats;
    const estimatedExportBytes = 65536
      + runCount * 65536
      + memberRecordCount * 5120
      + aggregateTimeSampleCount * 1536;
    return {
      runCount,
      memberRecordCount,
      aggregateTimeSampleCount,
      estimatedExportBytes,
      maximumEstimatedExportBytes: LABORATORY_MAX_ESTIMATED_EXPORT_BYTES,
      model: "Conservative pretty-JSON preflight: 64 KiB study + 64 KiB/run + 5 KiB/compact member + 1.5 KiB/shared time sample.",
      compactMemberPolicy: "No repeated nominal/member time arrays, per-sample sensor-noise arrays, inside masks, or trajectories; omitted deterministic evidence is replayed from seeds and the frozen declaration."
    };
  }

  function validateLaboratorySpec(spec) {
    if (!spec || typeof spec !== "object") throw new TypeError("laboratory spec is required");
    validateForecastForEnsemble(spec.forecast);
    const sizes = spec.sizes === undefined ? [spec.ensembleOptions && spec.ensembleOptions.size || 50] : spec.sizes;
    const horizons = spec.horizons === undefined ? [spec.forecast.config.duration] : spec.horizons;
    const laws = spec.laws === undefined
      ? [spec.ensembleOptions && spec.ensembleOptions.structured && spec.ensembleOptions.structured.law || "off"]
      : spec.laws;
    const amplitudes = spec.amplitudes === undefined
      ? [spec.ensembleOptions && spec.ensembleOptions.structured && spec.ensembleOptions.structured.alpha || 0]
      : spec.amplitudes;
    if (!Array.isArray(sizes) || !sizes.length || sizes.some(value => !Number.isInteger(value) || value < 1 || value > 5000)) {
      throw new RangeError("laboratory sizes must be nonempty integers from 1 through 5000");
    }
    if (!Array.isArray(horizons) || !horizons.length || horizons.some(value => !Number.isFinite(value) || value <= 0 || value > 120)) {
      throw new RangeError("laboratory horizons must lie in (0,120]");
    }
    if (!Array.isArray(laws) || !laws.length || laws.some(value => !ENSEMBLE_LAWS.includes(value))) {
      throw new RangeError("laboratory laws are invalid");
    }
    if (!Array.isArray(amplitudes) || !amplitudes.length || amplitudes.some(value => !Number.isFinite(value) || value < 0)) {
      throw new RangeError("laboratory amplitudes must be finite and nonnegative");
    }
    const repeats = spec.repeats === undefined ? 1 : spec.repeats;
    if (!Number.isInteger(repeats) || repeats < 1 || repeats > 100) throw new RangeError("laboratory repeats must be an integer from 1 through 100");
    const baseSeed = spec.baseSeed === undefined ? "oig-wind-tunnel-laboratory-v1" : spec.baseSeed;
    deriveSeed(baseSeed, "validation");
    const baseStep = spec.observationStep === undefined
      ? spec.forecast.config.duration / (spec.forecast.config.sampleCount - 1)
      : spec.observationStep;
    if (!Number.isFinite(baseStep) || baseStep <= 0) throw new RangeError("observationStep must be positive");
    const resourceEstimate = estimateLaboratoryResources(
      sizes, horizons, laws, amplitudes, repeats, baseStep
    );
    if (resourceEstimate.estimatedExportBytes > LABORATORY_MAX_ESTIMATED_EXPORT_BYTES) {
      throw new RangeError(
        "laboratory estimated compact export exceeds "
          + LABORATORY_MAX_ESTIMATED_EXPORT_BYTES + " bytes; reduce the grid, repeats, N, or T"
      );
    }
    return {
      sizes: sizes.slice(),
      horizons: horizons.slice(),
      laws: laws.slice(),
      amplitudes: amplitudes.slice(),
      repeats,
      baseSeed,
      baseStep,
      resourceEstimate,
      ensembleOptions: spec.ensembleOptions && typeof spec.ensembleOptions === "object" ? spec.ensembleOptions : {},
      retainTrajectories: Boolean(spec.retainTrajectories)
    };
  }

  function laboratoryForecast(baseForecast, horizon, baseStep) {
    const sampleCount = Math.max(2, Math.round(horizon / baseStep) + 1);
    if (sampleCount > 5001) throw new RangeError("fixed-cadence laboratory forecast exceeds 5001 samples");
    return forecastExperiment(Object.assign({}, baseForecast.config, { duration: horizon, sampleCount }));
  }

  function laboratoryRunOptions(config, size, law, amplitude, repeatIndex, horizon) {
    const template = config.ensembleOptions;
    return Object.assign({}, template, {
      size,
      seed: deriveSeed(config.baseSeed, "laboratory", size, horizon, law, amplitude, repeatIndex),
      retainTrajectories: config.retainTrajectories,
      structured: Object.assign({}, template.structured || {}, { law, alpha: amplitude })
    });
  }

  function aggregateLaboratoryRuns(runs) {
    return {
      sampleCoverage: descriptiveStatistics(runs.map(run => run.summary.coverage.sampleFraction)),
      wholeMemberCoverage: descriptiveStatistics(runs.map(run => run.summary.coverage.wholeMemberFraction)),
      firstExitFraction: descriptiveStatistics(runs.map(run => run.summary.exits.firstExitFraction)),
      persistentExitFraction: descriptiveStatistics(runs.map(run => run.summary.exits.persistentExitFraction)),
      actualAmplificationMedian: descriptiveStatistics(runs.map(run => run.summary.amplification.actual.p50)),
      projectedReconvergenceFraction: descriptiveStatistics(runs.map(run => run.summary.projectedReconvergence.withinDeclaredReadoutRadiusFraction)),
      unresolvedMemberFraction: descriptiveStatistics(runs.map(run =>
        run.summary.unresolvedMemberCount / Math.max(1, run.summary.resolvedMemberCount + run.summary.unresolvedMemberCount)
      )),
      interpretation: "Descriptive statistics across independently derived repeat seeds; no inferential interval is implied."
    };
  }

  function compactLaboratoryDrawSummary(draws) {
    const sensorNoise = draws.sensorNoise;
    return {
      angleOffset: draws.angleOffset,
      velocityOffset: draws.velocityOffset,
      parameterLogOffsets: draws.parameterLogOffsets,
      clockFraction: draws.clockFraction,
      sensorNoise: {
        sampleCount: sensorNoise.length,
        minimum: Math.min(...sensorNoise),
        maximum: Math.max(...sensorNoise),
        rms: Math.sqrt(sensorNoise.reduce((sum, value) => sum + value * value, 0) / sensorNoise.length),
        digest: checksum(stableSerialize(sensorNoise))
      }
    };
  }

  function compactLaboratoryAudit(audit) {
    if (!audit || !Array.isArray(audit.inside)) return audit;
    const projected = Object.assign({}, audit.projectedReconvergence);
    delete projected.interpretation;
    const fullState = Object.assign({}, audit.fullStateComparison);
    delete fullState.interpretation;
    const endpoint = Object.assign({}, audit.endpointClassification);
    delete endpoint.reference;
    delete endpoint.interpretation;
    return {
      coverage: audit.coverage,
      sampleCount: audit.inside.length,
      insideSampleCount: audit.inside.filter(Boolean).length,
      insideDigest: checksum(stableSerialize(audit.inside)),
      firstExitIndex: audit.firstExitIndex,
      firstExitTime: audit.firstExitTime,
      persistentExitIndex: audit.persistentExitIndex,
      persistentExitTime: audit.persistentExitTime,
      amplification: audit.amplification,
      projectedReconvergence: projected,
      fullStateComparison: fullState,
      endpointClassification: endpoint,
      maxEnergyDrift: audit.maxEnergyDrift,
      refinementDiscrepancy: audit.refinementDiscrepancy,
      status: audit.status,
      unresolvedReasons: audit.unresolvedReasons
    };
  }

  function compactLaboratoryMember(member) {
    return {
      id: member.id,
      index: member.index,
      memberSeed: member.memberSeed,
      drawSummary: compactLaboratoryDrawSummary(member.draws),
      compactOutcome: member.compactOutcome || null,
      audit: compactLaboratoryAudit(member.audit)
    };
  }

  function compactLaboratoryRun(result) {
    const payload = {
      schemaVersion: ENSEMBLE_SCHEMA_VERSION + "-laboratory-run-v1",
      declaration: result.declaration,
      comparisonBaseline: result.comparisonBaseline,
      sourceFullResultId: result.resultId,
      members: result.members.map(compactLaboratoryMember),
      summary: result.summary
    };
    payload.resultId = checksum(stableSerialize(payload));
    return payload;
  }

  function verifyCompactLaboratoryRun(result) {
    if (!result || result.schemaVersion !== ENSEMBLE_SCHEMA_VERSION + "-laboratory-run-v1"
      || !result.declaration || !Array.isArray(result.members) || !result.summary) {
      throw new TypeError("invalid compact laboratory run structure");
    }
    const expected = compactLaboratoryRun(replayEnsembleResult(result.declaration));
    if (result.members.length !== expected.members.length) {
      throw new Error("compact laboratory member count integrity mismatch");
    }
    result.members.forEach((member, index) => {
      if (stableSerialize(member) !== stableSerialize(expected.members[index])) {
        throw new Error("compact laboratory member scientific payload integrity mismatch at index " + index);
      }
    });
    if (stableSerialize(result.comparisonBaseline) !== stableSerialize(expected.comparisonBaseline)
      || stableSerialize(result.summary) !== stableSerialize(expected.summary)
      || result.sourceFullResultId !== expected.sourceFullResultId) {
      throw new Error("compact laboratory run scientific payload integrity mismatch");
    }
    if (result.resultId !== expected.resultId || stableSerialize(result) !== stableSerialize(expected)) {
      throw new Error("compact laboratory resultId does not commit the canonical scientific payload");
    }
    return { valid: true, resultId: result.resultId, sourceFullResultId: result.sourceFullResultId };
  }

  function runLaboratoryStudy(spec, callbacks) {
    const config = validateLaboratorySpec(spec);
    const controls = checkedCallbacks(callbacks);
    const total = config.sizes.length * config.horizons.length * config.laws.length * config.amplitudes.length * config.repeats;
    const forecastCache = new Map();
    const cellMap = new Map();
    let completed = 0;
    for (const horizon of config.horizons) {
      if (controls.isCancelled()) throw new CancellationError();
      const labForecast = laboratoryForecast(spec.forecast, horizon, config.baseStep);
      forecastCache.set(horizon, labForecast);
      for (const size of config.sizes) for (const law of config.laws) for (const amplitude of config.amplitudes) {
        const key = stableSerialize([size, horizon, law, amplitude]);
        const runs = [];
        for (let repeat = 0; repeat < config.repeats; repeat += 1) {
          if (controls.isCancelled()) throw new CancellationError();
          const options = laboratoryRunOptions(config, size, law, amplitude, repeat, horizon);
          runs.push(compactLaboratoryRun(runEnsemble(labForecast, options)));
          completed += 1;
          controls.onProgress({
            phase: "laboratory-runs", completed, total, fraction: completed / total,
            coordinates: { size, horizon, law, amplitude, repeat }
          });
        }
        cellMap.set(key, { size, horizon, law, amplitude, runs, aggregate: aggregateLaboratoryRuns(runs) });
      }
    }
    const cells = Array.from(cellMap.values());
    const result = {
      schemaVersion: ENSEMBLE_SCHEMA_VERSION + "-laboratory-v1",
      grid: {
        sizes: config.sizes,
        horizons: config.horizons,
        laws: config.laws,
        amplitudes: config.amplitudes,
        repeats: config.repeats
      },
      sampling: {
        requestedObservationStep: config.baseStep,
        rule: "Each horizon uses round(T / requestedObservationStep) + 1 endpoint-inclusive samples.",
        realized: config.horizons.map(horizon => {
          const sampleCount = forecastCache.get(horizon).times.length;
          return { horizon, sampleCount, observationStep: horizon / (sampleCount - 1) };
        })
      },
      seedDerivation: "Each repeat seed is independently derived from baseSeed,size,horizon,law,amplitude,repeat; scheduling and chunking cannot change it.",
      baseSeed: config.baseSeed,
      resourceEstimate: config.resourceEstimate,
      cells
    };
    result.studyId = checksum(stableSerialize(result));
    return result;
  }

  async function runLaboratoryStudyAsync(spec, callbacks) {
    const config = validateLaboratorySpec(spec);
    const controls = checkedCallbacks(callbacks);
    const total = config.sizes.length * config.horizons.length * config.laws.length * config.amplitudes.length * config.repeats;
    const forecastCache = new Map();
    const cells = [];
    let completed = 0;
    for (const horizon of config.horizons) {
      if (controls.isCancelled()) throw new CancellationError();
      const labForecast = laboratoryForecast(spec.forecast, horizon, config.baseStep);
      forecastCache.set(horizon, labForecast);
      for (const size of config.sizes) for (const law of config.laws) for (const amplitude of config.amplitudes) {
        const runs = [];
        for (let repeat = 0; repeat < config.repeats; repeat += 1) {
          if (controls.isCancelled()) throw new CancellationError();
          const options = laboratoryRunOptions(config, size, law, amplitude, repeat, horizon);
          const result = await runEnsembleAsync(labForecast, options, {
            isCancelled: controls.isCancelled,
            yieldEvery: controls.yieldEvery,
            onProgress: memberProgress => {
              const partialRun = memberProgress.total > 0
                ? memberProgress.completed / memberProgress.total
                : 0;
              controls.onProgress({
                phase: "laboratory-members",
                completed: completed + partialRun,
                completedRuns: completed,
                total,
                fraction: (completed + partialRun) / total,
                coordinates: { size, horizon, law, amplitude, repeat },
                memberProgress
              });
            }
          });
          runs.push(compactLaboratoryRun(result));
          completed += 1;
          controls.onProgress({
            phase: "laboratory-runs", completed, total, fraction: completed / total,
            coordinates: { size, horizon, law, amplitude, repeat }
          });
          await new Promise(resolve => setTimeout(resolve, 0));
        }
        cells.push({ size, horizon, law, amplitude, runs, aggregate: aggregateLaboratoryRuns(runs) });
      }
    }
    const result = {
      schemaVersion: ENSEMBLE_SCHEMA_VERSION + "-laboratory-v1",
      grid: { sizes: config.sizes, horizons: config.horizons, laws: config.laws, amplitudes: config.amplitudes, repeats: config.repeats },
      sampling: {
        requestedObservationStep: config.baseStep,
        rule: "Each horizon uses round(T / requestedObservationStep) + 1 endpoint-inclusive samples.",
        realized: config.horizons.map(horizon => {
          const sampleCount = forecastCache.get(horizon).times.length;
          return { horizon, sampleCount, observationStep: horizon / (sampleCount - 1) };
        })
      },
      seedDerivation: "Each repeat seed is independently derived from baseSeed,size,horizon,law,amplitude,repeat; scheduling and chunking cannot change it.",
      baseSeed: config.baseSeed,
      resourceEstimate: config.resourceEstimate,
      cells
    };
    result.studyId = checksum(stableSerialize(result));
    return result;
  }

  function verifyLaboratoryResult(result) {
    if (!result || result.schemaVersion !== ENSEMBLE_SCHEMA_VERSION + "-laboratory-v1"
      || !result.grid || !Array.isArray(result.cells)) {
      throw new TypeError("invalid laboratory result structure");
    }
    for (const key of ["sizes", "horizons", "laws", "amplitudes"]) {
      if (!Array.isArray(result.grid[key]) || !result.grid[key].length
        || new Set(result.grid[key].map(value => stableSerialize(value))).size !== result.grid[key].length) {
        throw new Error("laboratory grid axis is empty or contains duplicates: " + key);
      }
    }
    if (!Number.isInteger(result.grid.repeats) || result.grid.repeats < 1) {
      throw new Error("laboratory repeat declaration is invalid");
    }
    if (!result.sampling || !Number.isFinite(result.sampling.requestedObservationStep)
      || result.sampling.requestedObservationStep <= 0 || !Array.isArray(result.sampling.realized)) {
      throw new Error("laboratory sampling declaration is invalid");
    }
    const expectedRealized = result.grid.horizons.map(horizon => {
      const sampleCount = Math.max(2, Math.round(horizon / result.sampling.requestedObservationStep) + 1);
      return { horizon, sampleCount, observationStep: horizon / (sampleCount - 1) };
    });
    if (stableSerialize(result.sampling.realized) !== stableSerialize(expectedRealized)) {
      throw new Error("laboratory realized sampling grid is noncanonical");
    }
    const expectedResourceEstimate = estimateLaboratoryResources(
      result.grid.sizes,
      result.grid.horizons,
      result.grid.laws,
      result.grid.amplitudes,
      result.grid.repeats,
      result.sampling.requestedObservationStep
    );
    if (stableSerialize(result.resourceEstimate) !== stableSerialize(expectedResourceEstimate)
      || expectedResourceEstimate.estimatedExportBytes > LABORATORY_MAX_ESTIMATED_EXPORT_BYTES) {
      throw new Error("laboratory resource estimate is missing, noncanonical, or exceeds the export cap");
    }
    deriveSeed(result.baseSeed, "validation");
    const expectedCellCount = result.grid.sizes.length * result.grid.horizons.length
      * result.grid.laws.length * result.grid.amplitudes.length;
    if (result.cells.length !== expectedCellCount) throw new Error("laboratory Cartesian grid is incomplete");
    const expectedKeys = new Set();
    for (const size of result.grid.sizes) for (const horizon of result.grid.horizons)
      for (const law of result.grid.laws) for (const amplitude of result.grid.amplitudes) {
        expectedKeys.add(stableSerialize([size, horizon, law, amplitude]));
      }
    const observedKeys = new Set();
    for (const cell of result.cells) {
      const key = stableSerialize([cell.size, cell.horizon, cell.law, cell.amplitude]);
      if (!expectedKeys.has(key) || observedKeys.has(key)) {
        throw new Error("laboratory Cartesian cell is duplicated or outside the declared grid");
      }
      observedKeys.add(key);
      if (!Array.isArray(cell.runs) || cell.runs.length !== result.grid.repeats) {
        throw new Error("laboratory repeat grid is incomplete");
      }
      cell.runs.forEach((run, repeat) => {
        verifyCompactLaboratoryRun(run);
        const expectedSeed = deriveSeed(result.baseSeed, "laboratory", cell.size, cell.horizon, cell.law, cell.amplitude, repeat);
        if (run.declaration.masterSeed !== expectedSeed
          || run.declaration.size !== cell.size
          || run.declaration.structured.law !== cell.law
          || run.declaration.structured.alphaInput !== cell.amplitude
          || run.summary.timewise.times[run.summary.timewise.times.length - 1] !== cell.horizon) {
          throw new Error("laboratory repeat seed or coordinates are noncanonical");
        }
      });
      if (stableSerialize(cell.aggregate) !== stableSerialize(aggregateLaboratoryRuns(cell.runs))) {
        throw new Error("laboratory cell aggregate does not reconstruct from its runs");
      }
    }
    if (observedKeys.size !== expectedKeys.size) throw new Error("laboratory Cartesian key set is incomplete");
    const payload = Object.assign({}, result);
    delete payload.studyId;
    if (result.studyId !== checksum(stableSerialize(payload))) {
      throw new Error("laboratory studyId does not commit the complete public scientific payload");
    }
    return {
      valid: true,
      verification: "Deterministic same-code replay of every laboratory forecast, baseline, and member plus cross-field integrity; not an outward enclosure, external provenance proof, or physical-model validation.",
      studyId: result.studyId
    };
  }

  function checksum(value) {
    const text = typeof value === "string" ? value : JSON.stringify(value);
    let hash = 2166136261;
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(16).padStart(8, "0");
  }

  return {
    DEFAULT_PARAMETERS, SENSORS, rhs, energy, bobPositions, makeTimes,
    simulateRK4, simulateAdaptive, sensorValue, sensorSeries, eigen2x2,
    informationFromGradients, forecastExperiment, runIndependentOutcome,
    recommendNextExperiment, deterministicDirection, checksum,
    ENSEMBLE_SCHEMA_VERSION, ENSEMBLE_LAWS, ENSEMBLE_DIRECTIONS,
    LABORATORY_MAX_ESTIMATED_EXPORT_BYTES,
    CancellationError, stableSerialize, deriveSeed, createSeededPRNG,
    structuredLawValue, computeForecastCommitment,
    buildEnsembleDeclaration, generateMemberDraws,
    runEnsemble, runEnsembleAsync, summarizeEnsemble, verifyEnsembleResult,
    estimateLaboratoryResources, runLaboratoryStudy, runLaboratoryStudyAsync,
    verifyCompactLaboratoryRun, verifyLaboratoryResult
  };
});
