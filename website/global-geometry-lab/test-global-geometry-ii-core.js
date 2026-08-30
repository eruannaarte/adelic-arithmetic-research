"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const Base = require("./global-geometry-core.js");
const G2 = require("./global-geometry-ii-core.js");
const Claims = require("./global-geometry-ii-claims.js");
const CalibrationArtifact = require("./generate-global-geometry-ii-calibration.js");

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }
function approx(actual, expected, tolerance = 1e-9, message) {
  assert.ok(Math.abs(actual - expected) <= tolerance, message || `${actual} ≉ ${expected}`);
}
function assertFiniteTree(value, at = "root") {
  if (typeof value === "number") assert.ok(Number.isFinite(value), `${at} is non-finite`);
  else if (Array.isArray(value)) value.forEach((item, i) => assertFiniteTree(item, `${at}[${i}]`));
  else if (value && typeof value === "object") Object.keys(value).forEach(key => assertFiniteTree(value[key], `${at}.${key}`));
}

test("UMD extension loads in Node and a browser-like global", () => {
  assert.strictEqual(typeof G2.runSpectralCalibration, "function");
  const source = fs.readFileSync(path.join(__dirname, "global-geometry-ii-core.js"), "utf8");
  const context = {
    self: { GlobalGeometryCore: Base }, Math, JSON, ArrayBuffer, Set,
    Object, Number, String, Error, RegExp, isFinite
  };
  vm.createContext(context);
  vm.runInContext(source, context);
  assert.strictEqual(typeof context.self.GlobalGeometryII.periodicLatticeSpectrum, "function");
});

test("canonical serialization and checksums are key-order invariant", () => {
  const a = { z: [3, { b: 2, a: 1 }], a: true };
  const b = { a: true, z: [3, { a: 1, b: 2 }] };
  assert.strictEqual(G2.stableStringify(a), G2.stableStringify(b));
  assert.strictEqual(G2.digestValue(a), G2.digestValue(b));
  assert.throws(() => G2.stableStringify({ x: Infinity }), /non-finite/);
  [new Date(0), new Set([1]), /x/, new (class Example {})()].forEach(value => {
    assert.throws(() => G2.stableStringify(value), /unsupported value/);
  });
  const sparse = new Array(1);
  assert.throws(() => G2.stableStringify(sparse), /dense index-only array/);
  const decorated = ["x"];
  decorated.extra = "hidden";
  assert.throws(() => G2.stableStringify(decorated), /dense index-only array/);
  assert.throws(() => G2.stableStringify(JSON.parse('{"__proto__":{"polluted":true}}')), /forbidden object key/);
});

test("elementary theorem ledger is complete, unique, and machine-valid", () => {
  const records = Claims.listClaims();
  assert.strictEqual(records.length, 16);
  assert.strictEqual(Claims.validateLedger(records).valid, true);
  assert.strictEqual(new Set(records.map(record => record.id)).size, records.length);
  records.forEach(record => {
    assert.strictEqual(record.status, "proved");
    assert.strictEqual(record.basis, "proved-here");
    assert.strictEqual(G2.validateEvidenceRecord(record).valid, true);
  });
  assert.match(Claims.getClaim("ggii.theorem.p3.4.local-indistinguishability").claim, /observer/);
  const damaged = records.map(record => JSON.parse(JSON.stringify(record)));
  damaged[0].dependencies.push("ggii.theorem.missing");
  assert.strictEqual(Claims.validateLedger(damaged).valid, false);
});

test("evidence records are deterministic, immutable, and mutation-detecting", () => {
  const input = {
    id: "ggii.test.claim",
    claim: "A finite test claim.",
    status: "computational",
    basis: "finite-computation",
    scope: "One deterministic fixture.",
    method: "Evaluate the fixture.",
    falsifier: "The fixture returns false.",
    assumptions: ["finite input"],
    artifacts: ["fixture:test"],
    tests: ["self-test"],
    limitations: ["not a continuum theorem"],
    result: { accepted: true }
  };
  const a = G2.createEvidenceRecord(input);
  const b = G2.createEvidenceRecord({ result: { accepted: true }, ...input });
  assert.deepStrictEqual(a, b);
  assert.ok(Object.isFrozen(a));
  assert.strictEqual(G2.validateEvidenceRecord(a).valid, true);
  const unsigned = JSON.parse(JSON.stringify(a));
  delete unsigned.schemaVersion;
  delete unsigned.digestAlgorithm;
  delete unsigned.digest;
  assert.strictEqual(G2.validateEvidenceRecord(unsigned).valid, false);
  const changed = JSON.parse(JSON.stringify(a));
  changed.claim = "A changed claim.";
  assert.strictEqual(G2.validateEvidenceRecord(changed).valid, false);
  assert.match(G2.validateEvidenceRecord(changed).errors.join(" "), /digest mismatch/);
  assert.throws(() => G2.createEvidenceRecord({ ...input, certainty: "absolute" }), /unknown evidence field certainty/);
  assert.throws(() => G2.createEvidenceRecord({ ...input, status: "proved", basis: "finite-computation" }), /basis does not match status/);
});

test("run manifests fail closed and replay with stable digests", () => {
  const input = {
    experimentId: "ggii.test.manifest",
    families: ["square", "triangular"],
    refinements: [4, 8],
    seeds: ["exact"],
    observables: ["spectrum"],
    controls: ["cycle"],
    parameters: { times: [1, 2] },
    comparisonContract: { fittedAfterObservation: false }
  };
  const manifest = G2.createRunManifest(input);
  assert.strictEqual(G2.validateRunManifest(manifest).valid, true);
  assert.strictEqual(G2.createRunManifest(input).digest, manifest.digest);
  const changed = JSON.parse(JSON.stringify(manifest));
  changed.refinements.push(16);
  assert.match(G2.validateRunManifest(changed).errors.join(" "), /digest mismatch/);
  assert.throws(() => G2.createRunManifest({ ...input, execute: "code" }), /unknown manifest field execute/);
  assert.throws(() => G2.createRunManifest({ ...input, parameters: { time: NaN } }), /non-finite/);
  const unsigned = JSON.parse(JSON.stringify(manifest));
  delete unsigned.schemaVersion;
  delete unsigned.coreVersion;
  delete unsigned.digestAlgorithm;
  delete unsigned.digest;
  assert.strictEqual(G2.validateRunManifest(unsigned).valid, false);
  const sparseFamilies = new Array(1);
  assert.throws(() => G2.createRunManifest({ ...input, families: sparseFamilies }), /families/);
});

test("periodic square and triangular generators have exact regular degree", () => {
  const square = G2.periodicLatticeGraph({ family: "square", rows: 5, cols: 7 });
  assert.strictEqual(square.nodes.length, 35);
  assert.strictEqual(square.edges.length, 70);
  assert.ok(G2.degreeSequence(square).every(value => value === 4));
  const triangular = G2.periodicLatticeGraph({ family: "triangular", rows: 5, cols: 7 });
  assert.strictEqual(triangular.nodes.length, 35);
  assert.strictEqual(triangular.edges.length, 105);
  assert.ok(G2.degreeSequence(triangular).every(value => value === 6));
  assert.match(triangular.metadata.geometryScope, /no 2-cell topology/);
});

test("closed-form periodic spectra agree with the independent dense eigensolver", () => {
  ["square", "triangular"].forEach(family => {
    const agreement = G2.compareAnalyticAndDenseSpectrum({ family, rows: 4, cols: 5 });
    assert.strictEqual(agreement.available, true);
    assert.strictEqual(agreement.denseSolverConverged, true);
    assert.strictEqual(agreement.analyticZeroMultiplicity, 1);
    assert.strictEqual(agreement.denseZeroMultiplicity, 1);
    assert.ok(agreement.maxAbsolute < 1e-10, `${family}: ${agreement.maxAbsolute}`);
  });
});

test("periodic spectra have one zero mode and normalized-Laplacian bounds", () => {
  ["square", "triangular"].forEach(family => {
    const spectrum = G2.periodicLatticeSpectrum({ family, rows: 12, cols: 13 });
    assert.strictEqual(spectrum.eigenvalues.length, 156);
    assert.strictEqual(spectrum.zeroMultiplicity, 1);
    assert.ok(spectrum.spectralGap > 0);
    assert.ok(spectrum.bounds.min >= -1e-12);
    assert.ok(spectrum.bounds.max <= 2 + 1e-12);
  });
});

test("exact graph-word formulas expose square/triangular metric nonuniversality", () => {
  function bfs(generators, radius) {
    const distances = new Map([["0,0", 0]]);
    const queue = [[0, 0]];
    for (let cursor = 0; cursor < queue.length; cursor += 1) {
      const [m, n] = queue[cursor];
      const d = distances.get(`${m},${n}`);
      if (d === radius) continue;
      generators.forEach(([dm, dn]) => {
        const next = [m + dm, n + dn];
        const key = `${next[0]},${next[1]}`;
        if (!distances.has(key)) { distances.set(key, d + 1); queue.push(next); }
      });
    }
    return distances;
  }
  const squareGenerators = [[1,0],[-1,0],[0,1],[0,-1]];
  const triangularGenerators = squareGenerators.concat([[1,-1],[-1,1]]);
  bfs(squareGenerators, 6).forEach((distance, key) => {
    const [m, n] = key.split(",").map(Number);
    assert.strictEqual(G2.squareWordDistance(m, n), distance);
  });
  bfs(triangularGenerators, 6).forEach((distance, key) => {
    const [m, n] = key.split(",").map(Number);
    assert.strictEqual(G2.triangularWordDistance(m, n), distance);
  });
  const control = G2.graphMetricNonuniversalityControl();
  assert.strictEqual(control.square.unitBallExtremePoints.length, 4);
  assert.strictEqual(control.triangular.unitBallExtremePoints.length, 6);
  assert.strictEqual(control.evidence.status, "proved");
  assert.strictEqual(control.evidence.basis, "proved-here");
  assert.strictEqual(G2.validateEvidenceRecord(control.evidence).valid, true);
  assert.throws(() => G2.squareWordDistance(Number.MAX_SAFE_INTEGER, Number.MAX_SAFE_INTEGER), /safe-integer range/);
  assert.throws(() => G2.triangularWordDistance(Number.MAX_SAFE_INTEGER, 1), /safe-integer range/);
  assert.throws(() => G2.squareWordDistance(Number.MAX_VALUE, 0), /safe integers/);
});

test("square and equilateral-triangular walks share the proved Gaussian finite-dimensional limit", () => {
  const square = G2.latticeStepMoments("square");
  const triangular = G2.latticeStepMoments("triangular");
  [square, triangular].forEach(moment => {
    approx(moment.mean[0], 0, 1e-14);
    approx(moment.mean[1], 0, 1e-14);
    approx(moment.covariance[0][0], 0.5, 1e-14);
    approx(moment.covariance[1][1], 0.5, 1e-14);
    approx(moment.covariance[0][1], 0, 1e-14);
    approx(moment.covariance[1][0], 0, 1e-14);
  });
  assert.notStrictEqual(square.fourthMoments.x, triangular.fourthMoments.x, "microscopic fourth moments should remain distinct");

  const xi = [0.7, -1.1];
  const limit = Math.exp(-(xi[0] * xi[0] + xi[1] * xi[1]) / 4);
  const errors = [100, 1000, 10000].map(n => {
    const scale = 1 / Math.sqrt(n);
    const squareValue = Math.pow(G2.latticeStepCharacteristic("square", xi.map(value => value * scale)), n);
    const triangularValue = Math.pow(G2.latticeStepCharacteristic("triangular", xi.map(value => value * scale)), n);
    return { square: Math.abs(squareValue - limit), triangular: Math.abs(triangularValue - limit), familyGap: Math.abs(squareValue - triangularValue) };
  });
  assert.ok(errors[2].square < errors[0].square);
  assert.ok(errors[2].triangular < errors[0].triangular);
  assert.ok(errors[2].familyGap < errors[0].familyGap);
  assert.ok(errors[2].square < 1e-4);
  assert.ok(errors[2].triangular < 1e-4);

  const times = [0.4, 1.3, 2.7];
  const positionCoefficients = [[0.2, -0.4], [0.7, 0.1], [-0.3, 0.8]];
  const incrementCoefficients = positionCoefficients.map((unused, start) => {
    return positionCoefficients.slice(start).reduce((sum, coefficient) => [
      sum[0] + coefficient[0], sum[1] + coefficient[1]
    ], [0, 0]);
  });
  const jointLimitExponent = incrementCoefficients.reduce((sum, coefficient, index) => {
    const delta = times[index] - (index ? times[index - 1] : 0);
    return sum - delta * (coefficient[0] ** 2 + coefficient[1] ** 2) / 4;
  }, 0);
  const jointLimit = Math.exp(jointLimitExponent);
  ["square", "triangular"].forEach(family => {
    const jointErrors = [200, 2000, 20000].map(n => {
      const value = incrementCoefficients.reduce((product, coefficient, index) => {
        const count = Math.floor(n * times[index]) - Math.floor(n * (index ? times[index - 1] : 0));
        const argument = coefficient.map(component => component / Math.sqrt(n));
        return product * Math.pow(G2.latticeStepCharacteristic(family, argument), count);
      }, 1);
      return Math.abs(value - jointLimit);
    });
    assert.ok(jointErrors[2] < jointErrors[0], family + " joint finite-dimensional error did not decrease");
    assert.ok(jointErrors[2] < 1e-4, family + " joint finite-dimensional error is too large");

    const physicalTime = 0.7;
    const physicalXi = [0.45, -0.2];
    const standardBrownianLimit = Math.exp(-physicalTime * (physicalXi[0] ** 2 + physicalXi[1] ** 2) / 2);
    const clockErrors = [1 / 8, 1 / 16, 1 / 32].map(h => {
      const count = Math.floor(2 * physicalTime / (h * h));
      const value = Math.pow(G2.latticeStepCharacteristic(family, physicalXi.map(component => h * component)), count);
      return Math.abs(value - standardBrownianLimit);
    });
    assert.ok(clockErrors[2] < clockErrors[0], family + " physical-clock error did not decrease");
  });

  const control = G2.diffusionFiniteDimensionalUniversalityControl();
  assert.strictEqual(control.evidence.status, "proved");
  assert.strictEqual(control.evidence.basis, "proved-here");
  assert.strictEqual(G2.validateEvidenceRecord(control.evidence).valid, true);
  assert.match(control.evidence.proofAnchor, /Proposition 8\.2/);
  assert.throws(() => G2.latticeStepCharacteristic("square", [1]), /dense pair/);
  assert.throws(
    () => G2.latticeStepCharacteristic("triangular", [Number.MAX_VALUE, Number.MAX_VALUE]),
    /non-finite characteristic-function phase/
  );
});

test("covariance whitening yields a proved robust finite-dimensional universality basin", () => {
  function multiply(left, right) {
    return { real: left.real * right.real - left.imaginary * right.imaginary, imaginary: left.real * right.imaginary + left.imaginary * right.real };
  }
  function power(base, exponent) {
    let result = { real: 1, imaginary: 0 };
    let factor = { real: base.real, imaginary: base.imaginary };
    for (let count = exponent; count > 0; count = Math.floor(count / 2)) {
      if (count % 2 === 1) result = multiply(result, factor);
      factor = multiply(factor, factor);
    }
    return result;
  }
  function characteristic(steps, probabilities, xi) {
    return steps.reduce((sum, step, index) => {
      const phase = xi[0] * step[0] + xi[1] * step[1];
      return { real: sum.real + probabilities[index] * Math.cos(phase), imaginary: sum.imaginary + probabilities[index] * Math.sin(phase) };
    }, { real: 0, imaginary: 0 });
  }
  function distanceFromReal(value, target) { return Math.hypot(value.real - target, value.imaginary); }

  const control = G2.robustWhitenedDiffusionUniversalityControl();
  assert.strictEqual(control.theoremEvidence.status, "proved");
  assert.strictEqual(control.theoremEvidence.basis, "proved-here");
  assert.strictEqual(control.auditEvidence.status, "computational");
  assert.strictEqual(G2.validateEvidenceRecord(control.theoremEvidence).valid, true);
  assert.strictEqual(G2.validateEvidenceRecord(control.auditEvidence).valid, true);
  assert.strictEqual(control.analyses.length, 4);
  approx(control.basin.supportBoundM, Math.sqrt(2), 1e-13);
  assert.strictEqual(control.basin.covarianceLowerKappa, 0.3);
  assert.deepStrictEqual(control.sampleSizes, [200, 2000, 20000]);

  control.analyses.forEach((analysis, lawIndex) => {
    const probabilityTotal = analysis.probabilities.reduce((sum, value) => sum + value, 0);
    const mean = analysis.steps.reduce((sum, step, index) => [sum[0] + analysis.probabilities[index] * step[0], sum[1] + analysis.probabilities[index] * step[1]], [0, 0]);
    const covariance = [[0, 0], [0, 0]];
    analysis.steps.forEach((step, index) => {
      const centered = [step[0] - mean[0], step[1] - mean[1]];
      for (let row = 0; row < 2; row += 1) for (let column = 0; column < 2; column += 1) {
        covariance[row][column] += analysis.probabilities[index] * centered[row] * centered[column];
      }
    });
    const discriminant = Math.hypot(covariance[0][0] - covariance[1][1], 2 * covariance[0][1]);
    const eigenvalues = [(covariance[0][0] + covariance[1][1] - discriminant) / 2, (covariance[0][0] + covariance[1][1] + discriminant) / 2];
    const maxSupport = Math.max(...analysis.steps.map(step => Math.hypot(step[0], step[1])));
    approx(probabilityTotal, 1, 2e-13);
    approx(mean[0], 0, 2e-13);
    approx(mean[1], 0, 2e-13);
    assert.ok(maxSupport <= control.basin.supportBoundM + 1e-12, analysis.id + " exits the support basin");
    assert.ok(eigenvalues[0] >= control.basin.covarianceLowerKappa - 1e-12, analysis.id + " exits the lower covariance basin");
    assert.ok(eigenvalues[1] <= control.basin.covarianceUpper + 1e-12, analysis.id + " exits the upper covariance basin");

    const A = analysis.inverseSquareRoot;
    const whitenedCovariance = [[0, 0], [0, 0]];
    for (let row = 0; row < 2; row += 1) for (let column = 0; column < 2; column += 1) {
      for (let left = 0; left < 2; left += 1) for (let right = 0; right < 2; right += 1) {
        whitenedCovariance[row][column] += A[row][left] * covariance[left][right] * A[column][right];
      }
    }
    approx(whitenedCovariance[0][0], 1, 2e-12);
    approx(whitenedCovariance[1][1], 1, 2e-12);
    approx(whitenedCovariance[0][1], 0, 2e-12);
    approx(whitenedCovariance[1][0], 0, 2e-12);

    const whitenedSteps = analysis.steps.map(step => {
      const centered = [step[0] - mean[0], step[1] - mean[1]];
      return [A[0][0] * centered[0] + A[0][1] * centered[1], A[1][0] * centered[0] + A[1][1] * centered[1]];
    });
    const independentErrors = control.sampleSizes.map(n => Math.max(...control.directions.map(direction => {
      const oneStep = characteristic(whitenedSteps, analysis.probabilities, direction.map(value => value / Math.sqrt(n)));
      const finite = power(oneStep, n);
      return distanceFromReal(finite, Math.exp(-(direction[0] ** 2 + direction[1] ** 2) / 2));
    })));
    const productionRow = control.rows[lawIndex];
    independentErrors.forEach((error, index) => approx(error, productionRow.maxCharacteristicErrors[index], 2e-11));
    assert.ok(independentErrors[2] < independentErrors[1] && independentErrors[1] < independentErrors[0], analysis.id + " lacks strict three-size decrease");
    assert.ok(independentErrors[2] < 1e-3, analysis.id + " final error exceeds the audit guard");

    const times = [0.4, 1.1, 2.3];
    const positionWeights = [[0.3, -0.1], [-0.2, 0.5], [0.7, 0.2]];
    const blockWeights = positionWeights.map((unused, start) => positionWeights.slice(start).reduce((sum, weight) => [sum[0] + weight[0], sum[1] + weight[1]], [0, 0]));
    const jointTarget = Math.exp(-blockWeights.reduce((sum, weight, index) => sum + (times[index] - (index ? times[index - 1] : 0)) * (weight[0] ** 2 + weight[1] ** 2) / 2, 0));
    const jointErrors = [2000, 20000].map(n => {
      let value = { real: 1, imaginary: 0 };
      blockWeights.forEach((weight, index) => {
        const count = Math.floor(n * times[index]) - Math.floor(n * (index ? times[index - 1] : 0));
        value = multiply(value, power(characteristic(whitenedSteps, analysis.probabilities, weight.map(component => component / Math.sqrt(n))), count));
      });
      return distanceFromReal(value, jointTarget);
    });
    assert.ok(jointErrors[1] < jointErrors[0], analysis.id + " multi-time Cramer--Wold fixture did not improve");
  });

  const negative = control.auditEvidence.result.unwhitenedAnisotropicControl;
  approx(negative.rawCovariance[0][0], 0.7, 1e-14);
  approx(negative.rawCovariance[1][1], 0.3, 1e-14);
  approx(negative.analyticDifferentLimit, Math.exp(-0.35), 1e-13);
  approx(negative.asymptoticGapFromStandardGaussian, Math.abs(Math.exp(-0.35) - Math.exp(-0.5)), 1e-13);
  assert.ok(negative.finiteNErrorFromAnalyticLimit < 1e-5);
  assert.ok(negative.asymptoticGapFromStandardGaussian > 0.09);
  assert.strictEqual(Claims.getClaim("ggii.theorem.p8.3.robust-whitened-gaussian-fdd").status, "proved");
});

test("anisotropy and sample size form a replayable finite-resolution phase map", () => {
  const phase = G2.diffusionAnisotropyPhaseDiagram();
  assert.strictEqual(phase.status, "finite-computational-map");
  assert.deepStrictEqual(phase.axes.horizontalStepProbability, [0.3, 0.4, 0.5, 0.6, 0.7]);
  assert.deepStrictEqual(phase.axes.sampleSize, [200, 632, 2000, 6325, 20000]);
  assert.strictEqual(phase.rows.length, 5);
  assert.match(phase.interpretation, /not a thermodynamic phase transition/i);
  phase.rows.forEach(row => {
    assert.strictEqual(row.cells.length, 5);
    assert.ok(row.covarianceEigenvalues[0] >= 0.3 - 1e-14);
    for (let index = 1; index < row.cells.length; index += 1) {
      assert.ok(row.cells[index].maximumCharacteristicError < row.cells[index - 1].maximumCharacteristicError);
    }
    assert.strictEqual(row.cells[0].classification, "finite-size-above-guard");
    assert.strictEqual(row.cells[4].classification, "within-resolution-guard");
  });
  assert.strictEqual(phase.rows[0].cells[2].classification, "finite-size-above-guard");
  assert.strictEqual(phase.rows[2].cells[2].classification, "within-resolution-guard");

  const p = 0.3, n = 2000;
  const directions = phase.fixedProtocol.directions;
  const independent = Math.max(...directions.map(direction => {
    const oneStep = p * Math.cos(direction[0] / Math.sqrt(n * p)) + (1 - p) * Math.cos(direction[1] / Math.sqrt(n * (1 - p)));
    const finite = Math.pow(oneStep, n);
    const target = Math.exp(-(direction[0] ** 2 + direction[1] ** 2) / 2);
    return Math.abs(finite - target);
  }));
  approx(phase.rows[0].cells[2].maximumCharacteristicError, independent, 2e-12);
  assert.deepStrictEqual(G2.robustWhitenedDiffusionUniversalityControl().phaseDiagram, phase);
});

test("heat profiles remain finite and expose microscopic disagreement", () => {
  const square = G2.heatProfileFromSpectrum(G2.periodicLatticeSpectrum({ family: "square", rows: 32, cols: 32 }), { times: [1, 16, 32] });
  const triangular = G2.heatProfileFromSpectrum(G2.periodicLatticeSpectrum({ family: "triangular", rows: 32, cols: 32 }), { times: [1, 16, 32] });
  assertFiniteTree({ square, triangular });
  assert.ok(Math.abs(square[0].spectralDimension - triangular[0].spectralDimension) > 0.08);
  assert.ok(Math.abs(square[2].spectralDimension - triangular[2].spectralDimension) < 0.002);
  assert.ok(square.every(point => point.zeroModeFraction > 0 && point.zeroModeFraction <= 1));
  assert.ok(triangular.every(point => point.zeroModeFraction > 0 && point.zeroModeFraction <= 1));
  approx(square[2].spectralDimension, 2, 0.04);
  approx(triangular[2].spectralDimension, 2, 0.04);
});

test("profile distance applies only the predeclared matched window", () => {
  const a = [{ time: 1, value: 100 }, { time: 8, value: 2 }, { time: 16, value: 2.1 }];
  const b = [{ time: 1, value: -100 }, { time: 8, value: 2.01 }, { time: 16, value: 2.09 }];
  const result = G2.profileDistance(a, b, "value", time => time >= 8);
  assert.strictEqual(result.count, 2);
  approx(result.rms, 0.01, 1e-12);
});

test("exact calibration accepts the scoped 2D profile and rejects a 1D control", () => {
  const result = G2.runSpectralCalibration();
  assert.strictEqual(result.candidateStatus, "calibrated-profile-candidate");
  assert.strictEqual(result.conformsToFrozenProtocol, true);
  assert.strictEqual(result.hypothesis.status, "conjectural");
  assert.strictEqual(result.hypothesis.basis, "falsifiable-hypothesis");
  assert.strictEqual(result.evidence.status, "computational");
  assert.match(result.evidence.scope, /does not assert graph isometry/);
  assert.strictEqual(G2.validateEvidenceRecord(result.evidence).valid, true);
  assert.strictEqual(G2.validateRunManifest(result.manifest).valid, true);
  assert.strictEqual(G2.validateSpectralCalibrationResult(result).valid, true);
  const eligible = result.refinements.filter(item => item.window.valid && item.comparison.available);
  assert.ok(eligible.length >= 4);
  eligible.forEach(item => {
    assert.strictEqual(item.passesCalibrationGate, true);
    assert.ok(item.window.acceptedSampleCount >= 5);
    assert.ok(item.window.acceptedSpan >= 4);
    item.window.acceptedTimes.forEach(time => {
      const squarePoint = item.square.profile.find(point => point.time === time);
      const triangularPoint = item.triangular.profile.find(point => point.time === time);
      assert.ok(squarePoint.zeroModeFraction <= 0.1 + 1e-12);
      assert.ok(triangularPoint.zeroModeFraction <= 0.1 + 1e-12);
    });
    assert.ok(item.comparison.rms <= result.manifest.comparisonContract.rmsThreshold + 1e-12);
    assert.ok(Math.abs(item.ringControl.windowMeanDimension - 2) >= result.manifest.comparisonContract.negativeControlSeparation - 1e-12);
    approx(item.ringControl.windowMeanDimension, 1, result.manifest.comparisonContract.controlTolerance);
  });
  const onePoint = G2.runSpectralCalibration({ sizes: [32, 48, 64, 96], times: [32] });
  assert.strictEqual(onePoint.candidateStatus, "rejected-calibration");
  assert.strictEqual(onePoint.conformsToFrozenProtocol, false);
  const exploratory = G2.runSpectralCalibration({ sizes: [36, 54, 81, 120] });
  assert.strictEqual(exploratory.candidateStatus, "exploratory-calibration-pass");
  assert.strictEqual(exploratory.conformsToFrozenProtocol, false);
  const tampered = JSON.parse(JSON.stringify(result));
  tampered.refinements.find(item => item.window.valid).comparison.rms = 999;
  assert.strictEqual(G2.validateSpectralCalibrationResult(tampered).valid, false);
  assert.match(G2.validateSpectralCalibrationResult(tampered).errors.join(" "), /result digest mismatch/);
  assert.throws(() => G2.runSpectralCalibration({ sizes: [32, 32, 32, 32] }), /unique and strictly increasing/);
  assert.throws(() => G2.runSpectralCalibration({ sizes: [32, 48, 64, 96], times: [8, 8, 16, 32, 64] }), /unique and strictly increasing/);
  assert.throws(() => G2.runSpectralCalibration({ tolerance: 1 }), /unknown calibration option/);
});

test("committed calibration artifact has a reproducible SHA-256 content address", () => {
  const artifactPath = path.resolve(__dirname, "../../artifacts/global-geometry-ii/calibration-v1.json");
  const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));
  assert.strictEqual(G2.validateSpectralCalibrationResult(artifact.spectralCalibration).valid, true);
  const address = artifact.contentAddress;
  delete artifact.contentAddress;
  const replay = CalibrationArtifact.contentAddress(artifact);
  assert.deepStrictEqual(replay, address);
  assert.deepStrictEqual(CalibrationArtifact.contentAddress(CalibrationArtifact.buildPayload()), address);
  assert.match(address.digest, /^[0-9a-f]{64}$/);
  const changed = JSON.parse(JSON.stringify(artifact));
  changed.scientificScope.spectralResult += " changed";
  assert.notStrictEqual(CalibrationArtifact.contentAddress(changed).digest, address.digest);
});

(async () => {
  let passed = 0;
  for (const entry of tests) {
    try {
      await entry.fn();
      passed += 1;
      console.log(`✓ ${entry.name}`);
    } catch (error) {
      console.error(`✗ ${entry.name}`);
      console.error(error && error.stack ? error.stack : error);
      process.exitCode = 1;
      break;
    }
  }
  console.log(`\n${passed}/${tests.length} Global Geometry II tests passed`);
})();
