"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const Base = require("./global-geometry-core.js");
const G2 = require("./global-geometry-ii-core.js");
const Ensembles = require("./global-geometry-ii-ensembles.js");

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }
function approx(actual, expected, tolerance = 1e-10, message) {
  assert.ok(Math.abs(actual - expected) <= tolerance, message || `${actual} ≉ ${expected}`);
}
function stableStructure(complex) {
  const labels = complex.nodes.map(node => node.label);
  const edgeKeys = complex.edges.map(edge => {
    const endpoints = [labels[edge.source], labels[edge.target]].sort();
    return endpoints.join("|");
  }).sort();
  const faceKeys = complex.faces.map(face => face.map(vertex => labels[vertex]).sort().join("|")).sort();
  return { nodeKeys: labels.slice().sort(), edgeKeys, faceKeys };
}
function relabel(complex, order) {
  const oldToNew = new Array(order.length);
  order.forEach((oldIndex, newIndex) => { oldToNew[oldIndex] = newIndex; });
  return {
    nodes: order.map((oldIndex, newIndex) => ({ ...complex.nodes[oldIndex], id: newIndex })),
    edges: complex.edges.map(edge => ({
      ...edge,
      source: oldToNew[edge.source],
      target: oldToNew[edge.target]
    })),
    faces: complex.faces.map(face => face.map(vertex => oldToNew[vertex])),
    metadata: JSON.parse(JSON.stringify(complex.metadata))
  };
}
function edgeWeightMap(complex) {
  const labels = complex.nodes.map(node => node.label);
  const result = new Map();
  complex.edges.forEach(edge => {
    const key = [labels[edge.source], labels[edge.target]].sort().join("|");
    result.set(key, edge.weight);
  });
  return result;
}

test("UMD module loads with the required base and with or without the optional extension", () => {
  assert.strictEqual(typeof Ensembles.generateFamily, "function");
  const source = fs.readFileSync(path.join(__dirname, "global-geometry-ii-ensembles.js"), "utf8");
  [
    { GlobalGeometryCore: Base, GlobalGeometryII: G2 },
    { GlobalGeometryCore: Base }
  ].forEach(globals => {
    const context = {
      self: globals, Math, JSON, Object, Array, Number, String, Error,
      RegExp, isFinite, Infinity
    };
    vm.createContext(context);
    vm.runInContext(source, context);
    assert.strictEqual(typeof context.self.GlobalGeometryIIEnsembles.generateSquareAlternating, "function");
    const generated = context.self.GlobalGeometryIIEnsembles.generateSquareAlternating({ linearSize: 2 });
    assert.strictEqual(generated.metadata.exactValidation.valid, true);
  });
});

test("closed family specs normalize declared defaults and reject malformed input", () => {
  const valid = Ensembles.validateFamilySpec({ familyId: "square-alternating" });
  assert.strictEqual(valid.valid, true);
  assert.strictEqual(valid.spec.schema, Ensembles.FAMILY_SCHEMA);
  assert.strictEqual(valid.spec.linearSize, 4);
  assert.strictEqual(valid.spec.boundaryCondition, "reflecting-disk");
  assert.notStrictEqual(valid.spec.streams.generator, valid.spec.streams.conductance);
  assert.strictEqual(Ensembles.validateFamilySpec({ familyId: "square-alternating", linearSize: 24 }).valid, true);

  const malformed = [
    null,
    [],
    { familyId: "unknown" },
    { familyId: "square-alternating", execute: "code" },
    { familyId: "square-alternating", schema: "open/99" },
    { familyId: "square-alternating", linearSize: 1 },
    { familyId: "square-alternating", linearSize: 25 },
    { familyId: "square-alternating", linearSize: 3.5 },
    { familyId: "square-alternating", level: -1 },
    { familyId: "square-alternating", characteristicSpacing: Infinity },
    { familyId: "square-alternating", sigma: -0 },
    { familyId: "square-alternating", sigma: Math.log(4) + 1e-8 },
    { familyId: "square-alternating", boundaryCondition: "periodic" },
    { familyId: "square-alternating", streams: [] },
    { familyId: "square-alternating", streams: { bootstrap: "wrong-role" } },
    { familyId: "square-alternating", streams: { generator: "same", conductance: "same" } },
    { familyId: "square-alternating", schema: null },
    { familyId: "square-alternating", linearSize: null },
    { familyId: "square-alternating", level: null },
    { familyId: "square-alternating", characteristicSpacing: null },
    { familyId: "square-alternating", sigma: null },
    { familyId: "square-alternating", boundaryCondition: null },
    { familyId: "square-alternating", streams: null },
    { familyId: "square-alternating", streams: { generator: null } },
    { familyId: "square-alternating", streams: { conductance: null } }
  ];
  malformed.forEach(spec => assert.strictEqual(Ensembles.validateFamilySpec(spec).valid, false, JSON.stringify(spec)));
  assert.throws(() => Ensembles.generateFamily({ familyId: "unknown" }), /Invalid filled-disk family spec/);
  assert.throws(() => Ensembles.generateSquareAlternating(null), /plain object/);
  assert.throws(() => Ensembles.coordinateHash("", "cell:0:0"), /streamSeed/);
  assert.throws(() => Ensembles.coordinateHash("seed", ""), /objectCanonicalKey/);

  class FamilySpec {
    constructor() { this.familyId = "square-alternating"; }
  }
  assert.strictEqual(Ensembles.validateFamilySpec(new FamilySpec()).valid, false);
  const inherited = Object.create({ familyId: "square-alternating", linearSize: 2 });
  assert.strictEqual(Ensembles.validateFamilySpec(inherited).valid, false);
});

test("accepted spacing and resource bounds are constructive at both preview extremes", () => {
  assert.strictEqual(Ensembles.MIN_CHARACTERISTIC_SPACING, 1e-5);
  assert.strictEqual(Object.isFrozen(Ensembles.PREVIEW_RESOURCE_POLICY), true);
  assert.strictEqual(Ensembles.validateFamilySpec({
    familyId: "square-alternating",
    characteristicSpacing: Ensembles.MIN_CHARACTERISTIC_SPACING / 2
  }).valid, false);

  Ensembles.FAMILY_IDS.forEach(familyId => {
    [2, Ensembles.MAX_LINEAR_SIZE].forEach(linearSize => {
      const estimate = Ensembles.estimatePreviewResources(familyId, linearSize);
      const report = Ensembles.previewResourceReport(familyId, linearSize);
      assert.strictEqual(report.withinPolicy, true, `${familyId} L=${linearSize}`);
      assert.strictEqual(Object.isFrozen(report), true);
      [Ensembles.MIN_CHARACTERISTIC_SPACING, 100].forEach(characteristicSpacing => {
        const complex = Ensembles.generateFamily({
          familyId,
          linearSize,
          characteristicSpacing,
          sigma: Math.log(4)
        });
        assert.deepStrictEqual(
          [complex.nodes.length, complex.edges.length, complex.faces.length],
          [estimate.vertices, estimate.edges, estimate.faces]
        );
        assert.strictEqual(complex.metadata.resources.withinPolicy, true);
      });
    });
  });

  const overCap = Ensembles.previewResourceReport("cell-center-fan", Ensembles.MAX_LINEAR_SIZE + 1);
  assert.strictEqual(overCap.withinPolicy, false);
  assert.match(overCap.errors.join(" "), /exceeds preview cap/);
});

test("all four filled-disk generators replay deterministically", () => {
  Ensembles.FAMILY_IDS.forEach(familyId => {
    const spec = {
      familyId,
      linearSize: 4,
      sigma: 0.25,
      streams: { generator: "deterministic-generator", conductance: "deterministic-conductance" }
    };
    const first = Ensembles.generateFamily(spec);
    const second = Ensembles.generateFamily(JSON.parse(JSON.stringify(spec)));
    assert.deepStrictEqual(second, first, familyId);
    assert.strictEqual(first.metadata.structureDigest, second.metadata.structureDigest);
    assert.strictEqual(first.metadata.streams.algorithm, Ensembles.PRNG_CONTRACT);
  });
});

test("canonical IDs and object hashes are independent of vertex relabeling", () => {
  const generated = Ensembles.generateSquareHashedDiagonal({
    linearSize: 5,
    sigma: 0.5,
    streams: { generator: "coordinate-generator", conductance: "coordinate-conductance" }
  });
  const labels = generated.nodes.map(node => node.label);
  assert.deepStrictEqual(labels, labels.slice().sort());
  generated.nodes.forEach((node, index) => assert.strictEqual(node.id, index));
  assert.deepStrictEqual(generated.metadata.canonicalNodeKeys, labels);

  generated.metadata.construction.motifs.forEach(motif => {
    const expected = Ensembles.coordinateUniform("coordinate-generator", motif.cellKey) < 0.5
      ? "southwest-northeast"
      : "northwest-southeast";
    assert.strictEqual(motif.diagonal, expected);
  });
  assert.strictEqual(
    Ensembles.coordinateHash("coordinate-generator", "cell:000002:000003"),
    Ensembles.coordinateHash("coordinate-generator", "cell:000002:000003")
  );

  const reversed = relabel(generated, Array.from({ length: generated.nodes.length }, (_, i) => generated.nodes.length - 1 - i));
  assert.deepStrictEqual(stableStructure(reversed), stableStructure(generated));
  assert.strictEqual(Ensembles.validateFilledDisk(reversed).valid, true);
  assert.deepStrictEqual(Base.computeBettiNumbers(reversed).betti.array, [1, 0, 0]);

  const originalWeights = edgeWeightMap(generated);
  const relabeledWeights = edgeWeightMap(reversed);
  assert.deepStrictEqual([...relabeledWeights.entries()].sort(), [...originalWeights.entries()].sort());
});

test("every family is a valid one-boundary-component disk with exact-small Gauss--Bonnet balance", () => {
  Ensembles.FAMILY_IDS.forEach(familyId => {
    const complex = Ensembles.generateFamily({ familyId, linearSize: 4 });
    const certificate = complex.metadata.exactValidation;
    assert.strictEqual(certificate.valid, true, familyId);
    assert.strictEqual(certificate.evidenceClass, "mixed-finite-certificate");
    assert.strictEqual(certificate.topology.evidenceClass, "exact-combinatorial-result");
    assert.strictEqual(certificate.surface.evidenceClass, "finite-combinatorial-and-binary64-gate");
    assert.strictEqual(certificate.gaussBonnet.evidenceClass, "binary64-evaluation-of-proved-finite-identity");
    assert.deepStrictEqual(certificate.topology.betti, [1, 0, 0]);
    assert.strictEqual(certificate.topology.eulerCharacteristic, 1);
    assert.strictEqual(certificate.topology.eulerPoincareResidual, 0);
    assert.strictEqual(certificate.topology.boundaryComponents, 1);
    assert.strictEqual(certificate.topology.isEdgeManifold, true);
    assert.strictEqual(certificate.surface.valid, true);
    assert.strictEqual(certificate.surface.invalidVertexLinkCount, 0);
    assert.strictEqual(certificate.surface.degenerateFaceCount, 0);
    assert.strictEqual(certificate.gaussBonnet.identityApplicable, true);
    approx(certificate.gaussBonnet.total, 2 * Math.PI, 1e-10, familyId);
    assert.ok(Math.abs(certificate.gaussBonnet.residual) < certificate.gaussBonnet.tolerance, familyId);

    assert.deepStrictEqual(Base.computeBettiNumbers(complex).betti.array, [1, 0, 0]);
    assert.strictEqual(Base.surfaceValidity(complex).valid, true);
    assert.ok(Math.abs(Base.angleDefectCurvature(complex).gaussBonnetResidual) < 1e-10);
  });
});

test("intrinsic lengths, construction locality, and refinement records are explicit", () => {
  Ensembles.FAMILY_IDS.forEach((familyId, familyIndex) => {
    const spacing = 0.75 + familyIndex * 0.1;
    const complex = Ensembles.generateFamily({
      familyId,
      linearSize: 3,
      level: 2,
      characteristicSpacing: spacing
    });
    complex.edges.forEach(edge => {
      const a = complex.nodes[edge.source], b = complex.nodes[edge.target];
      const embedded = Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
      approx(edge.length, embedded, 1e-12, `${familyId} intrinsic edge`);
    });
    assert.strictEqual(complex.metadata.constructionLocality.class, "L0");
    assert.strictEqual(complex.metadata.constructionLocality.radius, 1);
    assert.strictEqual(complex.metadata.runtimeLocality.class, "L0");
    assert.strictEqual(complex.metadata.analysisLocality, "L2");
    assert.strictEqual(complex.metadata.metricModels.authoritativeEdgeLength, "embedded_euclidean_at_initialization");
    assert.strictEqual(complex.metadata.metricModels.graphObservables, "graph_length");
    assert.strictEqual(complex.metadata.metricModels.surfaceObservables, "piecewise_euclidean");
    assert.strictEqual(complex.metadata.metricModels.observableMustSelectMetric, true);
    assert.strictEqual(complex.metadata.measureModel, "unit_vertex_counting");
    assert.strictEqual(complex.metadata.operatorModels.analysis, "weighted_symmetric_normalized_laplacian");
    assert.strictEqual(complex.metadata.operatorModels.runtime, "lazy_reversible_nearest_neighbor_random_walk");
    assert.strictEqual(complex.metadata.operatorModels.lazyProbability, 0.5);
    assert.strictEqual(complex.metadata.comparisonScope.highestSupportedClaim, "finite_instance_calibration");
    assert.strictEqual(complex.metadata.comparisonScope.universalityStatus, "NOT_EVALUATED");
    assert.ok(complex.metadata.comparisonScope.withheldClaims.includes("universality"));
    assert.strictEqual(complex.metadata.refinement.level, 2);
    assert.strictEqual(complex.metadata.refinement.parentLevel, 1);
    assert.strictEqual(complex.metadata.refinement.linearSize, 3);
    assert.strictEqual(complex.metadata.refinement.characteristicSpacing, spacing);
    assert.strictEqual(complex.metadata.refinement.vertexCount, complex.nodes.length);
    assert.ok(complex.metadata.refinement.domainDiameter > 0);
    assert.strictEqual(complex.metadata.refinement.restrictionMapDigest, null);
    assert.strictEqual(complex.metadata.refinement.prolongationMapDigest, null);
  });
});

test("realized domains distinguish exact square coverage from the triangular interior crop", () => {
  const squareFamilies = ["square-alternating", "cell-center-fan", "square-hashed-diagonal"];
  squareFamilies.forEach(familyId => {
    const complex = Ensembles.generateFamily({ familyId, linearSize: 8, characteristicSpacing: 1 / 8 });
    const domain = complex.metadata.construction.domainDisclosure;
    assert.strictEqual(domain.crop.exactTargetCoverage, true);
    assert.strictEqual(domain.crop.status, "none");
    approx(domain.realized.areaCoverageRatio, 1, 1e-14);
    approx(complex.metadata.refinement.targetDomainDiameter, Math.SQRT2, 1e-14);
    approx(complex.metadata.refinement.realizedDomainDiameter, Math.SQRT2, 1e-14);
  });

  const triangular = Ensembles.generateTriangularClipped({ linearSize: 8, characteristicSpacing: 1 / 8 });
  const domain = triangular.metadata.construction.domainDisclosure;
  assert.strictEqual(domain.crop.exactTargetCoverage, false);
  assert.strictEqual(domain.crop.status, "declared-interior-crop");
  assert.ok(domain.realized.areaCoverageRatio > 0 && domain.realized.areaCoverageRatio < 1);
  assert.ok(domain.crop.maximumBoundaryOffset > 0);
  assert.match(domain.crossFamilyComparison, /common-bulk mask/);
  assert.match(triangular.metadata.comparisonScope.commonDomainRequirement, /common-bulk mask/);
  assert.ok(triangular.metadata.refinement.realizedDomainDiameter < triangular.metadata.refinement.targetDomainDiameter);
  assert.deepStrictEqual(domain.realized.dimensionlessBounds.x, [0, 1]);
});

test("quenched conductances obey uniform ellipticity and named streams remain separated", () => {
  Ensembles.FAMILY_IDS.forEach(familyId => {
    const sigma = Math.log(4);
    const complex = Ensembles.generateFamily({
      familyId,
      linearSize: 4,
      sigma,
      streams: { generator: "elliptic-generator", conductance: "elliptic-conductance" }
    });
    const [lower, upper] = complex.metadata.disorder.uniformEllipticity;
    approx(lower, 0.25, 1e-14);
    approx(upper, 4, 1e-14);
    complex.edges.forEach(edge => {
      assert.ok(edge.weight >= lower - 1e-14, `${familyId}: ${edge.weight} < ${lower}`);
      assert.ok(edge.weight <= upper + 1e-14, `${familyId}: ${edge.weight} > ${upper}`);
      assert.ok(edge.weight > 0);
    });
    assert.ok(complex.metadata.disorder.observedMinimum >= lower - 1e-14);
    assert.ok(complex.metadata.disorder.observedMaximum <= upper + 1e-14);
    assert.strictEqual(complex.metadata.disorder.strictlyPositive, true);
  });

  const common = { linearSize: 6, sigma: 0.75 };
  const baseline = Ensembles.generateSquareHashedDiagonal({
    ...common,
    streams: { generator: "generator-a", conductance: "conductance-a" }
  });
  const changedGenerator = Ensembles.generateSquareHashedDiagonal({
    ...common,
    streams: { generator: "generator-b", conductance: "conductance-a" }
  });
  const changedConductance = Ensembles.generateSquareHashedDiagonal({
    ...common,
    streams: { generator: "generator-a", conductance: "conductance-b" }
  });
  assert.notDeepStrictEqual(stableStructure(changedGenerator).faceKeys, stableStructure(baseline).faceKeys);
  assert.deepStrictEqual(stableStructure(changedConductance), stableStructure(baseline));

  const baselineWeights = edgeWeightMap(baseline);
  const generatorWeights = edgeWeightMap(changedGenerator);
  let commonEdges = 0;
  generatorWeights.forEach((weight, key) => {
    if (baselineWeights.has(key)) {
      commonEdges += 1;
      assert.strictEqual(weight, baselineWeights.get(key), key);
    }
  });
  assert.ok(commonEdges > 0);
  const conductanceWeights = edgeWeightMap(changedConductance);
  assert.ok([...baselineWeights.keys()].some(key => conductanceWeights.get(key) !== baselineWeights.get(key)));

  const unit = Ensembles.generateSquareAlternating({ linearSize: 3, sigma: 0 });
  assert.ok(unit.edges.every(edge => edge.weight === 1));
});

test("the four registered families expose genuinely distinct microscopic motifs", () => {
  const generated = Object.fromEntries(Ensembles.FAMILY_IDS.map(familyId => [
    familyId,
    Ensembles.generateFamily({
      familyId,
      linearSize: 4,
      streams: { generator: "motif-generator", conductance: "motif-conductance" }
    })
  ]));
  const motifNames = Ensembles.FAMILY_IDS.map(familyId => generated[familyId].metadata.construction.motif);
  assert.strictEqual(new Set(motifNames).size, 4);

  assert.deepStrictEqual(
    [generated["square-alternating"].nodes.length, generated["square-alternating"].faces.length],
    [25, 32]
  );
  assert.deepStrictEqual(
    [generated["triangular-clipped"].nodes.length, generated["triangular-clipped"].faces.length],
    [23, 28]
  );
  assert.deepStrictEqual(
    [generated["cell-center-fan"].nodes.length, generated["cell-center-fan"].faces.length],
    [41, 64]
  );
  assert.notDeepStrictEqual(
    generated["square-hashed-diagonal"].metadata.construction.motifs.map(motif => motif.diagonal),
    generated["square-alternating"].metadata.construction.motifs.map(motif => motif.diagonal)
  );

  const fanCenterCount = generated["cell-center-fan"].metadata.construction.motifs.length;
  assert.strictEqual(fanCenterCount, 16);
  assert.ok(generated["triangular-clipped"].edges.every(edge => Math.abs(edge.length - 1) < 1e-12));
  assert.ok(generated["square-alternating"].edges.some(edge => Math.abs(edge.length - Math.SQRT2) < 1e-12));
  assert.ok(generated["cell-center-fan"].edges.some(edge => Math.abs(edge.length - Math.SQRT1_2) < 1e-12));
});

test("the disk validator fails closed on malformed surface data", () => {
  const valid = Ensembles.generateSquareAlternating({ linearSize: 3 });
  const duplicate = JSON.parse(JSON.stringify(valid));
  duplicate.faces.push(duplicate.faces[0].slice());
  const report = Ensembles.validateFilledDisk(duplicate);
  assert.strictEqual(report.valid, false);
  assert.match(report.errors.join(" "), /duplicates unoriented triangular face/);

  const broken = JSON.parse(JSON.stringify(valid));
  broken.edges[0].source = broken.edges[0].target;
  const brokenReport = Ensembles.validateFilledDisk(broken);
  assert.strictEqual(brokenReport.valid, false);
  assert.match(brokenReport.errors.join(" "), /invalid exact-integer endpoints/);
});

test("digest semantics are identical with and without the optional extension", () => {
  const source = fs.readFileSync(path.join(__dirname, "global-geometry-ii-ensembles.js"), "utf8");
  function load(extension) {
    const globals = { GlobalGeometryCore: Base };
    if (extension) globals.GlobalGeometryII = G2;
    const context = {
      self: globals, Math, JSON, Object, Array, Number, String, Error,
      RegExp, Set, isFinite, Infinity
    };
    vm.createContext(context);
    vm.runInContext(source, context);
    return context.self.GlobalGeometryIIEnsembles;
  }
  const withExtension = load(true);
  const withoutExtension = load(false);
  Ensembles.FAMILY_IDS.forEach(familyId => {
    const spec = {
      linearSize: 4,
      sigma: 0.75,
      streams: { generator: "umd-generator", conductance: "umd-conductance" }
    };
    const first = withExtension.generateFamily(familyId === "square-alternating" ? { ...spec, familyId } : { ...spec, familyId });
    const second = withoutExtension.generateFamily({ ...spec, familyId });
    assert.strictEqual(first.metadata.combinatorialDigest, second.metadata.combinatorialDigest, familyId);
    assert.strictEqual(first.metadata.realizationDigest, second.metadata.realizationDigest, familyId);
    assert.strictEqual(first.metadata.structureDigest, second.metadata.structureDigest, familyId);
    assert.strictEqual(first.metadata.construction.motifDigest, second.metadata.construction.motifDigest, familyId);
  });
  assert.strictEqual(withExtension.coordinateHash("stream", "object"), withoutExtension.coordinateHash("stream", "object"));
});

test("generated carriers are deeply immutable and expose recomputable digest bindings", () => {
  const generated = Ensembles.generateSquareHashedDiagonal({
    linearSize: 5,
    sigma: 0.5,
    streams: { generator: "freeze-generator", conductance: "freeze-conductance" }
  });
  [
    generated,
    generated.nodes,
    generated.nodes[0],
    generated.edges,
    generated.edges[0],
    generated.faces,
    generated.faces[0],
    generated.metadata,
    generated.metadata.construction,
    generated.metadata.exactValidation
  ].forEach(value => assert.strictEqual(Object.isFrozen(value), true));
  assert.throws(() => { generated.edges[0].weight *= 2; }, TypeError);
  assert.throws(() => { generated.faces.push([0, 1, 2]); }, TypeError);

  const recomputed = Ensembles.recomputeFamilyDigests(generated);
  assert.strictEqual(Object.isFrozen(recomputed), true);
  assert.strictEqual(recomputed.combinatorialDigest, generated.metadata.combinatorialDigest);
  assert.strictEqual(recomputed.realizationDigest, generated.metadata.realizationDigest);
  assert.strictEqual(recomputed.structureDigest, generated.metadata.structureDigest);
  assert.strictEqual(recomputed.motifDigest, generated.metadata.construction.motifDigest);
  const verified = Ensembles.verifyFamilyDigests(generated);
  assert.strictEqual(verified.valid, true);
  assert.deepStrictEqual(verified.errors, []);

  const changed = JSON.parse(JSON.stringify(generated));
  changed.edges[0].weight *= 1.01;
  const changedDigests = Ensembles.recomputeFamilyDigests(changed);
  assert.strictEqual(changedDigests.combinatorialDigest, recomputed.combinatorialDigest);
  assert.notStrictEqual(changedDigests.realizationDigest, recomputed.realizationDigest);
  const changedVerification = Ensembles.verifyFamilyDigests(changed);
  assert.strictEqual(changedVerification.valid, false);
  assert.match(changedVerification.errors.join(" "), /realization digest mismatch/);
});

test("strict raw validation rejects repairs, nonfinite metrics, duplicate identities, and digest tampering", () => {
  const baseline = Ensembles.generateSquareAlternating({ linearSize: 3, sigma: 0.3 });
  function invalid(mutator, pattern) {
    const changed = JSON.parse(JSON.stringify(baseline));
    mutator(changed);
    const report = Ensembles.validateFilledDisk(changed);
    assert.strictEqual(report.valid, false, pattern);
    assert.match(report.errors.join(" "), pattern);
  }

  invalid(complex => { complex.edges = []; }, /edges must be a non-empty dense array/);
  invalid(complex => { complex.edges.push({ ...complex.edges[0] }); }, /duplicates unoriented edge/);
  invalid(complex => { complex.edges[0].source = String(complex.edges[0].source); }, /exact-integer endpoints/);
  invalid(complex => { complex.edges[0].weight = 0; }, /conductance must be finite and positive/);
  invalid(complex => { complex.edges[0].weight = null; }, /conductance must be finite and positive/);
  invalid(complex => { complex.edges[0].length = -1; }, /length must be finite and positive/);
  invalid(complex => { delete complex.edges[0].length; }, /length must be finite and positive/);
  invalid(complex => { complex.nodes[1].label = complex.nodes[0].label; }, /duplicates canonical label/);
  invalid(complex => { complex.nodes[0].x = null; }, /must be a finite number/);
  invalid(complex => { complex.faces.push(complex.faces[0].slice()); }, /duplicates unoriented triangular face/);
  invalid(complex => { complex.edges.splice(0, 1); }, /is missing from the declared edge list/);
  invalid(complex => { complex.edges[0].weight *= 1.01; }, /realization digest mismatch/);
  invalid(complex => { complex.metadata.combinatorialDigest = "00000000"; }, /combinatorial digest mismatch/);
  invalid(complex => { complex.metadata.construction.motifDigest = "00000000"; }, /motif digest mismatch/);

  const sparse = JSON.parse(JSON.stringify(baseline));
  delete sparse.faces[0];
  assert.match(Ensembles.validateFilledDisk(sparse).errors.join(" "), /faces must be a non-empty dense array/);

  const classNode = JSON.parse(JSON.stringify(baseline));
  class CustomNode {}
  classNode.nodes[0] = Object.assign(new CustomNode(), classNode.nodes[0]);
  assert.match(Ensembles.validateFilledDisk(classNode).errors.join(" "), /node 0 must be a plain object/);
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
  console.log(`\n${passed}/${tests.length} Global Geometry II ensemble tests passed`);
})();
