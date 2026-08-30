#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const G2 = require("./global-geometry-ii-core.js");
const Atlas = require("./global-geometry-ii-atlas.js");
const Inverse = require("./global-geometry-ii-inverse.js");
const Sheet = require("./global-geometry-ii-sheet.js");
const CalibrationGenerator = require("./generate-global-geometry-ii-calibration.js");
const AtlasGenerator = require("./generate-global-geometry-ii-atlas.js");
const InverseGenerator = require("./generate-global-geometry-ii-inverse.js");
const SheetGenerator = require("./generate-global-geometry-ii-sheet.js");
const Release = require("./generate-global-geometry-ii-release.js");

const artifactRoot = path.resolve(__dirname, "../../artifacts/global-geometry-ii");
const tests = [];
function test(name, body) { tests.push({ name, body }); }

function readArtifact(name) {
  return JSON.parse(fs.readFileSync(path.join(artifactRoot, name), "utf8"));
}

function verifyAddress(artifact, addressFunction) {
  const supplied = artifact.contentAddress;
  assert.ok(supplied && supplied.algorithm === "sha256");
  const payload = JSON.parse(JSON.stringify(artifact));
  delete payload.contentAddress;
  assert.deepStrictEqual(addressFunction(payload), supplied);
  return payload;
}

test("calibration artifact replays from the current exact and computational controls", () => {
  const artifact = readArtifact("calibration-v1.json");
  const payload = verifyAddress(artifact, CalibrationGenerator.contentAddress);
  assert.strictEqual(G2.stableStringify(payload), G2.stableStringify(CalibrationGenerator.buildPayload()));
  assert.strictEqual(payload.elementaryTheoremLedger.length, 16);
  assert.strictEqual(payload.diffusionFiniteDimensionalControl.evidence.status, "proved");
  assert.strictEqual(payload.robustWhitenedDiffusionControl.theoremEvidence.status, "proved");
  assert.strictEqual(payload.robustWhitenedDiffusionControl.auditEvidence.status, "computational");
  assert.strictEqual(payload.graphMetricControl.status, "proved-nonuniversal-in-graph-metric");
});

test("atlas artifact is semantically closed and remains preview-only", () => {
  const artifact = readArtifact("atlas-pilot-v1.json");
  const payload = verifyAddress(artifact, AtlasGenerator.contentAddress);
  assert.strictEqual(Atlas.validatePilotResult(payload.pilot).valid, true);
  assert.strictEqual(payload.pilot.universalityStatus, "NOT_EVALUATED");
  assert.strictEqual(payload.pilot.runs.length, 48);
  const replay = Release.compareAtlasCrossPlatformReplay(payload, AtlasGenerator.buildPayload());
  assert.strictEqual(replay.valid, true, replay.errors.join("; "));
  assert.strictEqual(replay.policy.id, "ggii.atlas-cross-platform-replay/1");
});

test("inverse certificate artifact replays every representative request and witness", () => {
  const artifact = readArtifact("inverse-certificates-v1.json");
  const payload = verifyAddress(artifact, InverseGenerator.contentAddress);
  assert.strictEqual(InverseGenerator.validatePayload(payload).valid, true);
  assert.deepStrictEqual(payload.cases.map((entry) => entry.report.status), ["PASS", "PASS", "PASS", "PASS", "FAIL", "FAIL", "FAIL"]);
  payload.cases.forEach((entry) => {
    assert.strictEqual(Inverse.validateCompilerReport(entry.report).valid, true);
  });
  assert.strictEqual(Inverse.stableStringify(payload), Inverse.stableStringify(InverseGenerator.buildPayload()));
});

test("sheet artifact replays exact defect budgets and the observation-bound HIL transcript", () => {
  const artifact = readArtifact("sheet-hil-v1.json");
  const payload = verifyAddress(artifact, SheetGenerator.contentAddress);
  assert.strictEqual(SheetGenerator.validatePayload(payload).valid, true);
  assert.deepStrictEqual(payload.stars.map((star) => star.q), [5, 6, 7]);
  assert.strictEqual(payload.scenarioResult.finalState.state, "HOLD");
  assert.strictEqual(Sheet.validateHilTranscript(payload.scenarioResult.transcript).valid, true);
  assert.strictEqual(Sheet.stableStringify(payload), Sheet.stableStringify(SheetGenerator.buildPayload()));
});

test("artifact generators reject ambiguous command-line output arguments", () => {
  [CalibrationGenerator, AtlasGenerator, InverseGenerator, SheetGenerator].forEach((generator) => {
    assert.throws(() => generator.parseOutput(["--unknown"]), /unknown generator argument/);
    assert.throws(() => generator.parseOutput(["--output"]), /requires/);
    assert.throws(() => generator.parseOutput(["--output", "a", "--output", "b"]), /only once|exactly one/);
  });
});

let passed = 0;
for (const entry of tests) {
  try {
    entry.body();
    passed += 1;
    process.stdout.write("ok " + passed + " - " + entry.name + "\n");
  } catch (error) {
    process.stderr.write("not ok - " + entry.name + "\n" + (error.stack || error.message) + "\n");
    process.exitCode = 1;
  }
}
if (!process.exitCode) process.stdout.write("\n1.." + passed + "\nAll Global Geometry II artifact tests passed.\n");
