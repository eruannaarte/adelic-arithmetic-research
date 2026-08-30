"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const G = require("./global-geometry-core.js");

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }
function approx(actual, expected, tolerance = 1e-8, message) {
  assert.ok(Math.abs(actual - expected) <= tolerance, message || `${actual} ≉ ${expected}`);
}
function approxArray(actual, expected, tolerance = 1e-8) {
  assert.strictEqual(actual.length, expected.length);
  actual.forEach((value, i) => approx(value, expected[i], tolerance, `index ${i}: ${value} ≉ ${expected[i]}`));
}
function assertFiniteTree(value, at = "root") {
  if (typeof value === "number") assert.ok(Number.isFinite(value), `${at} is non-finite`);
  else if (Array.isArray(value)) value.forEach((item, i) => assertFiniteTree(item, `${at}[${i}]`));
  else if (value && typeof value === "object") Object.keys(value).forEach(key => assertFiniteTree(value[key], `${at}.${key}`));
}
function relabel(complex, order) {
  const map = new Array(order.length);
  order.forEach((oldIndex, newIndex) => { map[oldIndex] = newIndex; });
  return {
    nodes: order.map(oldIndex => ({ ...complex.nodes[oldIndex], id: map[oldIndex] })),
    edges: complex.edges.map(edge => ({ ...edge, source: map[edge.source], target: map[edge.target] })),
    faces: complex.faces.map(face => face.map(vertex => map[vertex])),
    metadata: { ...complex.metadata }
  };
}

test("UMD module exports in Node and a browser-like global", () => {
  assert.strictEqual(typeof G.createState, "function");
  const source = fs.readFileSync(path.join(__dirname, "global-geometry-core.js"), "utf8");
  const context = { self: {}, Math, JSON, ArrayBuffer, Set, Uint8Array, Object, Number, String, Error, isFinite };
  vm.createContext(context);
  vm.runInContext(source, context);
  assert.strictEqual(typeof context.self.GlobalGeometryCore.createState, "function");
});

test("every preset validates and covers three lenses plus six application families", () => {
  const presets = G.listPresets();
  assert.ok(presets.length >= 9);
  presets.forEach(preset => assert.deepStrictEqual(G.validateConfig(preset.id).errors, []));
  const lenses = new Set(presets.map(p => p.lens));
  ["forward", "inverse", "recognition"].forEach(lens => assert.ok(lenses.has(lens), `missing ${lens}`));
  const applications = new Set(presets.map(p => p.application));
  ["networks", "machine-learning", "morphogenesis", "distributed-robotics", "physics"].forEach(application => assert.ok(applications.has(application), `missing ${application}`));
  assert.ok(applications.has("metamaterials") || applications.has("programmable-materials"));
  Object.values(G.PRESETS).forEach(preset => {
    assert.ok(preset.claims.demonstrates);
    assert.ok(preset.claims.doesNotDemonstrate);
  });
});

test("config validation reports bad generator/model/lens combinations", () => {
  const bad = G.validateConfig({ lens: "sideways", generator: { type: "mystery" }, simulation: { model: "magic" } });
  assert.strictEqual(bad.valid, false);
  assert.ok(bad.errors.length >= 3);
  assert.throws(() => G.createState({ generator: { type: "mystery" } }), /Invalid Global Geometry config/);
});

test("closed config schema rejects unknown, nonfinite, and oversized inputs", () => {
  const unknown = G.validateConfig({ preset: "network-resilience", execute: "alert(1)" });
  assert.strictEqual(unknown.valid, false);
  assert.match(unknown.errors.join(" "), /unknown config field execute/);
  assert.strictEqual(G.validateConfig({ preset: "network-resilience", simulation: { dt: Infinity } }).valid, false);
  assert.strictEqual(G.validateConfig({ preset: "network-resilience", generator: { rows: 41 } }).valid, false);
  assert.strictEqual(G.validateConfig({ preset: "recognition-swiss-roll", generator: { count: 20, k: 20 } }).valid, false);
});

test("triangulated disk has disk homology, Euler characteristic, and boundary Gauss–Bonnet", () => {
  const disk = G.generateTriangulatedDisk({ rings: 2, sectors: 6 });
  assert.deepStrictEqual([disk.nodes.length, disk.edges.length, disk.faces.length], [13, 30, 18]);
  const topology = G.computeBettiNumbers(disk);
  assert.deepStrictEqual(topology.betti.array, [1, 0, 0]);
  assert.strictEqual(topology.eulerCharacteristic, 1);
  assert.strictEqual(topology.eulerPoincareResidual, 0);
  assert.strictEqual(topology.boundary.edgeCount, 6);
  const curvature = G.angleDefectCurvature(disk, { metric: "embedded" });
  approx(curvature.total, 2 * Math.PI, 1e-10);
  approx(curvature.gaussBonnetResidual, 0, 1e-10);
  curvature.vertices.filter(v => !v.boundary).forEach(v => approx(v.defect, 0, 1e-10));
});

test("icosahedral sphere and subdivision have sphere homology and closed Gauss–Bonnet", () => {
  const sphere = G.generateIcosphere({ subdivisions: 0 });
  assert.deepStrictEqual([sphere.nodes.length, sphere.edges.length, sphere.faces.length], [12, 30, 20]);
  assert.deepStrictEqual(G.computeBettiNumbers(sphere).betti.array, [1, 0, 1]);
  const curvature = G.angleDefectCurvature(sphere);
  approx(curvature.total, 4 * Math.PI, 1e-10);
  approx(curvature.gaussBonnetResidual, 0, 1e-10);
  curvature.vertices.forEach(v => approx(v.defect, Math.PI / 3, 1e-10));
  const refined = G.generateIcosphere({ subdivisions: 1 });
  assert.deepStrictEqual([refined.nodes.length, refined.edges.length, refined.faces.length], [42, 120, 80]);
  assert.deepStrictEqual(G.computeBettiNumbers(refined).betti.array, [1, 0, 1]);
});

test("surface validity fails closed for duplicate faces and dangling surface edges", () => {
  const disk = G.generateTriangulatedDisk({ rings: 2, sectors: 6 });
  assert.strictEqual(G.surfaceValidity(disk).valid, true);
  const duplicate = G.cloneState(disk);
  duplicate.faces.push(duplicate.faces[0].slice());
  const duplicateReport = G.surfaceValidity(duplicate);
  assert.strictEqual(duplicateReport.identityApplicable, false);
  assert.ok(duplicateReport.duplicateFaces.length > 0);
  assert.strictEqual(G.angleDefectCurvature(duplicate).identityApplicable, false);

  const dangling = G.cloneState(disk);
  dangling.nodes.push({ id: dangling.nodes.length, x: 3, y: 0, z: 0, radius: 1, value: 0, u: 1, v: 0 });
  dangling.edges.push({ source: 0, target: dangling.nodes.length - 1, weight: 1, length: 3 });
  assert.strictEqual(G.surfaceValidity(dangling).identityApplicable, false);
});

test("ring graph has graph-cycle Betti number and exact Euler–Poincare balance", () => {
  const ring = G.generateGraph({ graphType: "ring", count: 10 });
  const topology = G.computeBettiNumbers(ring);
  assert.deepStrictEqual(topology.betti.array, [1, 1, 0]);
  assert.strictEqual(topology.eulerCharacteristic, 0);
  assert.strictEqual(topology.eulerPoincareResidual, 0);
  assert.strictEqual(G.angleDefectCurvature(ring).available, false);
});

test("Gauss–Bonnet obstruction rejects an incompatible prescribed target", () => {
  const sphere = G.generateIcosphere();
  const rejected = G.validateCurvatureTarget(sphere, { targetTotal: 0 });
  assert.strictEqual(rejected.admissible, false);
  assert.match(rejected.errors[0], /Gauss–Bonnet obstruction/);
  const config = G.validateConfig({ preset: "forward-sphere-curvature", simulation: { targetTotal: 0 } });
  assert.strictEqual(config.valid, false);
  const beforeRadii = sphere.nodes.map(n => n.radius);
  const step = G.curvatureFlowStep(sphere, { targetTotal: 0 });
  assert.strictEqual(step.rejected, true);
  assert.deepStrictEqual(step.complex.nodes.map(n => n.radius), beforeRadii);
  const allowed = G.validateCurvatureTarget(sphere, { targetTotal: 4 * Math.PI });
  assert.strictEqual(allowed.admissible, true);
  assert.strictEqual(allowed.necessaryConditionOnly, true);
});

test("normalized Laplacian eigenvalues stay in [0,2] with correct zero multiplicity", () => {
  const ring = G.generateGraph({ graphType: "ring", count: 12 });
  const spectrum = G.normalizedLaplacianSpectrum(ring);
  assert.strictEqual(spectrum.available, true);
  assert.strictEqual(spectrum.zeroMultiplicity, 1);
  spectrum.eigenvalues.forEach(value => assert.ok(value >= -1e-12 && value <= 2 + 1e-12));
  const disconnected = {
    nodes: [{x:0},{x:1},{x:2},{x:3}],
    edges: [[0,1],[2,3]],
    faces: []
  };
  assert.strictEqual(G.normalizedLaplacianSpectrum(disconnected).zeroMultiplicity, 2);
  spectrum.heatTrace.forEach(point => {
    assert.ok(point.trace > 0);
    assert.ok(point.spectralDimension >= 0);
  });
});

test("Betti numbers, normalized spectrum, and circle-packing curvature are relabeling invariant", () => {
  const sphere = G.generateIcosphere();
  sphere.nodes.forEach((node, i) => { node.radius = 0.8 + 0.03 * i; });
  const order = Array.from({ length: sphere.nodes.length }, (_, i) => sphere.nodes.length - 1 - i);
  const renamed = relabel(sphere, order);
  assert.deepStrictEqual(G.computeBettiNumbers(renamed).betti.array, G.computeBettiNumbers(sphere).betti.array);
  approxArray(G.normalizedLaplacianSpectrum(renamed).eigenvalues, G.normalizedLaplacianSpectrum(sphere).eigenvalues, 1e-8);
  const originalDefects = G.angleDefectCurvature(sphere, { metric: "circle-packing" }).vertices.map(v => v.defect).sort((a,b) => a-b);
  const renamedDefects = G.angleDefectCurvature(renamed, { metric: "circle-packing" }).vertices.map(v => v.defect).sort((a,b) => a-b);
  approxArray(renamedDefects, originalDefects, 1e-8);
});

test("display-coordinate changes do not alter combinatorial or circle-packing observables", () => {
  const sphere = G.generateIcosphere();
  sphere.nodes.forEach((node, i) => { node.radius = 0.9 + 0.015 * i; });
  const moved = G.cloneState({ nodes: sphere.nodes, edges: sphere.edges, faces: sphere.faces, metadata: sphere.metadata });
  moved.nodes.forEach((node, i) => { node.x = 10 * Math.sin(i); node.y = -7 * Math.cos(2 * i); node.z = i * i; });
  assert.deepStrictEqual(G.computeBettiNumbers(moved).betti.array, G.computeBettiNumbers(sphere).betti.array);
  approxArray(G.normalizedLaplacianSpectrum(moved).eigenvalues, G.normalizedLaplacianSpectrum(sphere).eigenvalues, 1e-8);
  const a = G.angleDefectCurvature(sphere, { metric: "circle-packing" }).vertices.map(v => v.defect).sort((x,y) => x-y);
  const b = G.angleDefectCurvature(moved, { metric: "circle-packing" }).vertices.map(v => v.defect).sort((x,y) => x-y);
  approxArray(a, b, 1e-8);
});

test("stored intrinsic lengths make embedded curvature and volume display-invariant", () => {
  const disk = G.generateTriangulatedDisk({ rings: 3, sectors: 9 });
  const moved = G.cloneState(disk);
  moved.nodes.forEach((node, i) => { node.x = 100 * Math.sin(i); node.y = 70 * Math.cos(i); node.z = i; });
  const originalCurvature = G.angleDefectCurvature(disk, { metric: "embedded" });
  const movedCurvature = G.angleDefectCurvature(moved, { metric: "embedded" });
  approxArray(originalCurvature.vertices.map(v => v.defect), movedCurvature.vertices.map(v => v.defect), 1e-10);
  const originalVolume = G.volumeGrowthProfile(disk).profile.map(point => point.averageVolume);
  const movedVolume = G.volumeGrowthProfile(moved).profile.map(point => point.averageVolume);
  approxArray(originalVolume, movedVolume, 1e-10);
});

test("L0 causal cone bounds support of repeated radius-one diffusion", () => {
  const pathComplex = {
    nodes: Array.from({ length: 6 }, (_, i) => ({ x: i, y: 0, z: 0, value: i === 0 ? 1 : 0 })),
    edges: [[0,1],[1,2],[2,3],[3,4],[4,5]],
    faces: []
  };
  const cone = G.causalCone(pathComplex, [0], 2);
  assert.deepStrictEqual(cone.reachable, [0,1,2]);
  let evolved = G.diffusionStep(pathComplex, { dt: 1, diffusivity: 1 }).complex;
  evolved = G.diffusionStep(evolved, { dt: 1, diffusivity: 1 }).complex;
  evolved.nodes.forEach((node, i) => {
    if (i > 2) assert.strictEqual(node.value, 0, `signal escaped to node ${i}`);
  });
  assert.ok(evolved.nodes[2].value > 0);
});

test("curvature-flow step reduces target RMS error for a stable prescribed profile", () => {
  const state = G.createState("forward-sphere-curvature");
  state.edges.forEach(edge => approx(edge.length, state.nodes[edge.source].radius + state.nodes[edge.target].radius, 1e-12));
  const next = G.stepState(state);
  const report = next.lastStep.reports.find(item => item.model === "curvature-flow");
  assert.ok(report.energyAfter < report.energyBefore, `${report.energyAfter} !< ${report.energyBefore}`);
  let evolved = next;
  for (let i = 0; i < 5; i += 1) evolved = G.stepState(evolved);
  assert.ok(evolved.lastStep.reports[0].energyAfter < report.energyBefore);
});

test("curvature targets are explicit only for curvature-programming states", () => {
  const ordinaryDisk = G.createState("forward-disk-boundary");
  assert.strictEqual(Object.prototype.hasOwnProperty.call(ordinaryDisk.analysis.curvature, "targets"), false);
  assert.strictEqual(Object.prototype.hasOwnProperty.call(ordinaryDisk.analysis.curvature, "targetRmsError"), false);
  const inverse = G.createState("inverse-curvature-programming");
  assert.strictEqual(inverse.analysis.curvature.targets.length, inverse.nodes.length);
  assert.ok(Number.isFinite(inverse.analysis.curvature.targetRmsError));
});

test("diffusion obeys a maximum principle for configured stable steps", () => {
  const graph = G.generateGraph({ graphType: "grid", rows: 3, cols: 4 });
  graph.nodes.forEach((node, i) => { node.value = i === 0 ? 1 : 0; });
  const next = G.diffusionStep(graph, { dt: 0.8, diffusivity: 1 }).complex;
  next.nodes.forEach(node => assert.ok(node.value >= -1e-12 && node.value <= 1 + 1e-12));
});

test("reaction–diffusion remains finite and bounded under repeated local steps", () => {
  let complex = G.generateTriangulatedDisk({ rings: 3, sectors: 12 });
  for (let i = 0; i < 30; i += 1) complex = G.reactionDiffusionStep(complex, { dt: 0.5 }).complex;
  complex.nodes.forEach(node => {
    assert.ok(Number.isFinite(node.u) && node.u >= 0 && node.u <= 1.5);
    assert.ok(Number.isFinite(node.v) && node.v >= 0 && node.v <= 1.5);
  });
});

test("puncturing the sphere changes β2 and creates a three-edge boundary", () => {
  const state = G.createState("forward-sphere-curvature");
  const punctured = G.applyTopologyEvent(state, { type: "puncture", faceIndex: 0 });
  assert.deepStrictEqual(state.analysis.topology.betti.array, [1,0,1]);
  assert.deepStrictEqual(punctured.analysis.topology.betti.array, [1,0,0]);
  assert.strictEqual(punctured.analysis.topology.boundary.edgeCount, 3);
  assert.strictEqual(punctured.lastEvent.topologyChanged, true);
  approx(punctured.analysis.curvature.gaussBonnetResidual, 0, 1e-8);
});

test("adding a graph edge deterministically raises graph cycle rank", () => {
  const state = G.createState("network-resilience");
  const changed = G.applyTopologyEvent(state, { type: "add-cycle-edge" });
  assert.strictEqual(changed.analysis.topology.betti.b1, state.analysis.topology.betti.b1 + 1);
  assert.strictEqual(changed.lastEvent.topologyChanged, true);
});

test("point-cloud generation and full state replay are deterministic", () => {
  const cloudA = G.generatePointCloud({ shape: "swiss-roll", count: 32, k: 4, seed: "same" });
  const cloudB = G.generatePointCloud({ shape: "swiss-roll", count: 32, k: 4, seed: "same" });
  assert.deepStrictEqual(cloudA, cloudB);
  let a = G.createState("recognition-swiss-roll");
  let b = G.createState("recognition-swiss-roll");
  a = G.applyTopologyEvent(G.stepState(G.stepState(a)));
  b = G.applyTopologyEvent(G.stepState(G.stepState(b)));
  assert.deepStrictEqual(a, b);
});

test("seeded microscopic disorder is replayable and changes finite signatures", () => {
  const configA = G.cloneConfig("network-resilience");
  configA.generator.seed = "micro-a";
  configA.generator.disorder = 0.3;
  const configB = G.cloneConfig(configA);
  configB.generator.seed = "micro-b";
  const a1 = G.createState(configA);
  const a2 = G.createState(configA);
  const b = G.createState(configB);
  assert.deepStrictEqual(a1, a2);
  assert.notDeepStrictEqual(a1.edges.map(edge => edge.weight), b.edges.map(edge => edge.weight));
  assert.notDeepStrictEqual(a1.analysis.spectrum.eigenvalues, b.analysis.spectrum.eigenvalues);
});

test("volume-growth and spectral-dimension profiles expose documented JSON-safe shapes", () => {
  const state = G.createState("recognition-swiss-roll");
  assert.ok(Array.isArray(state.analysis.dimensions.volumeGrowth));
  assert.ok(Array.isArray(state.analysis.dimensions.spectralProfile));
  assert.ok(Array.isArray(state.analysis.dimensions.walkProfile));
  assert.ok(state.analysis.dimensions.volumeGrowth.some(point => Number.isFinite(point.dimension)));
  assert.ok(state.analysis.dimensions.walkProfile.some(point => Number.isFinite(point.dimension)));
  assert.ok(Array.isArray(state.analysis.spectrum.eigenvalues));
  assert.ok(state.analysis.topology.betti);
  assert.ok(Object.prototype.hasOwnProperty.call(state.analysis.curvature, "available"));
  assert.ok(state.analysis.locality.oneStepConeFromNodeZero.reachable.length > 0);
  assert.doesNotThrow(() => JSON.stringify(state.analysis));
  assertFiniteTree(state.analysis);
});

test("component topology correctly obstructs one global swarm consensus", () => {
  const state = G.createState("swarm-consensus");
  assert.ok(state.analysis.topology.betti.b0 > 1);
  assert.strictEqual(state.analysis.spectrum.zeroMultiplicity, state.analysis.topology.betti.b0);
  assert.match(state.config.question, /componentwise consensus/);
});

test("all preset events and one simulation step produce finite JSON-safe states", () => {
  Object.keys(G.PRESETS).forEach(id => {
    let state = G.createState(id);
    state = G.applyTopologyEvent(state);
    state = G.stepState(state);
    assertFiniteTree(state, id);
    const serialized = JSON.stringify(state);
    assert.ok(!serialized.includes("NaN"));
    assert.ok(!serialized.includes("Infinity"));
  });
});

test("clone helpers isolate mutations", () => {
  const config = G.cloneConfig("network-resilience");
  config.generator.rows = 99;
  assert.notStrictEqual(config.generator.rows, G.PRESETS["network-resilience"].generator.rows);
  const state = G.createState("network-resilience");
  const cloned = G.cloneState(state);
  cloned.nodes[0].value = 123;
  assert.notStrictEqual(cloned.nodes[0].value, state.nodes[0].value);
});

(async function run() {
  const started = Date.now();
  let passed = 0;
  for (const item of tests) {
    try {
      await item.fn();
      passed += 1;
      process.stdout.write(`✓ ${item.name}\n`);
    } catch (error) {
      process.stderr.write(`✗ ${item.name}\n${error.stack}\n`);
      process.exitCode = 1;
      break;
    }
  }
  process.stdout.write(`\n${passed}/${tests.length} tests passed in ${Date.now() - started} ms\n`);
})();
