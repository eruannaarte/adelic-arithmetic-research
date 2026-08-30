#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const Generator = require("./generate-global-geometry-ii-physical-preflight.js");

const repoRoot = path.resolve(__dirname, "../..");
const artifactPath = path.join(repoRoot, "artifacts/global-geometry-ii/fabrication/physical-preflight-v1.json");
const profilePath = path.join(repoRoot, "artifacts/global-geometry-ii/fabrication/physical-preflight-profile-v1.json");
const worksheetPath = path.join(repoRoot, "artifacts/global-geometry-ii/fabrication/physical-trial-worksheet-v1.json");
const tests = [];

function test(name, body) { tests.push({ name, body }); }
function clone(value) { return JSON.parse(JSON.stringify(value)); }
function readJson(filePath) { return JSON.parse(fs.readFileSync(filePath, "utf8")); }

test("sanitized printer profile exposes no physical-output claim", () => {
  const profile = readJson(profilePath);
  const validation = Generator.validateProfile(profile);
  assert.strictEqual(validation.valid, true, validation.errors.join("; "));
  assert.strictEqual(profile.hostVolatileIdentifiersRetained, false);
  assert.strictEqual(profile.connectivity, "NOT_EVALUATED");
  assert.strictEqual(profile.physicalOutput, "NOT_RUN");
  assert.deepStrictEqual(profile.supportedResolutionDpi, [300, 600]);
  profile.dryRasterObservations.forEach((entry) => assert.strictEqual(entry.jobSubmitted, false));
});

test("embedded repository paths use a platform-independent POSIX encoding", () => {
  assert.strictEqual(
    Generator.normalizeRepoRelativePath("artifacts\\global-geometry-ii\\fabrication\\physical-preflight-profile-v1.json"),
    "artifacts/global-geometry-ii/fabrication/physical-preflight-profile-v1.json"
  );
  assert.throws(() => Generator.normalizeRepoRelativePath("..\\private.json"), /escapes/);
  const payload = Generator.buildPayload();
  assert.strictEqual(payload.normalizedPrinterProfile.source.path, "artifacts/global-geometry-ii/fabrication/physical-preflight-profile-v1.json");
  assert.strictEqual(payload.operatorWorksheet.path, "artifacts/global-geometry-ii/fabrication/physical-trial-worksheet-v1.json");
});

test("analytic printable box and four-sided clearances are frozen", () => {
  const payload = Generator.buildPayload();
  assert.deepStrictEqual(payload.templates.map((entry) => entry.q), [5, 6, 7]);
  payload.templates.forEach((entry) => {
    assert.deepStrictEqual(entry.requiredPrintableBoxMm, [7.75, 13.75, 202.25, 283.25]);
    assert.deepStrictEqual(entry.availablePrintableBoxMm, [6.35, 12.7, 203.552777777778, 284.338888888889]);
    assert.deepStrictEqual(entry.clearanceMm, {
      left: 1.4,
      top: 1.05,
      right: 1.302777777778,
      bottom: 1.088888888889
    });
    assert.strictEqual(entry.minimumClearanceMm, 1.05);
  });
});

test("renderer-specific foreground remains inside the observed dry raster", () => {
  const payload = Generator.buildPayload();
  assert.deepStrictEqual(payload.rendererClearance300DpiPx, {
    left: 16,
    top: 12,
    right: 15,
    bottom: 16,
    minimum: 12
  });
});

test("preflight payload remains explicitly nonphysical", () => {
  const payload = Generator.buildPayload();
  const validation = Generator.validatePayload(payload);
  assert.strictEqual(validation.valid, true, validation.errors.join("; "));
  assert.strictEqual(payload.evidenceStatus, "PASS_DRIVER_PROFILE_DRY_PREFLIGHT_ONLY");
  assert.strictEqual(payload.physicalValidation, "NOT_RUN");
  assert.strictEqual(payload.cameraValidation, "NOT_RUN");
  assert.strictEqual(payload.printJobSubmitted, false);
});

test("content-addressed artifact has an exact semantic replay", () => {
  const payload = Generator.buildPayload();
  const artifact = { ...payload, contentAddress: Generator.contentAddress(payload) };
  const validation = Generator.validateArtifact(artifact);
  assert.strictEqual(validation.valid, true, validation.errors.join("; "));
});

test("committed preflight artifact validates against current inputs", () => {
  const validation = Generator.validateArtifactFile(artifactPath);
  assert.strictEqual(validation.valid, true, validation.errors.join("; "));
});

test("rehashing cannot legitimize semantic tampering", () => {
  const basePayload = Generator.buildPayload();
  const mutations = [
    ["printer box", (payload) => { payload.normalizedPrinterProfile.imagingBoxPt.right = 578; }],
    ["claimed clearance", (payload) => { payload.templates[0].minimumClearanceMm = 99; }],
    ["physical validation", (payload) => { payload.physicalValidation = "PASS"; }],
    ["template hash", (payload) => { payload.templates[1].sha256 = "0".repeat(64); }],
    ["worksheet status", (payload) => { payload.operatorWorksheet.templateStatus = "COMPLETE"; }]
  ];
  mutations.forEach(([label, mutate]) => {
    const payload = clone(basePayload);
    mutate(payload);
    const rehashed = { ...payload, contentAddress: Generator.contentAddress(payload) };
    const validation = Generator.validateArtifact(rehashed);
    assert.strictEqual(validation.valid, false, `${label} mutation passed after rehash`);
    assert.ok(validation.errors.some((error) => /does not replay|boundary|worksheet/.test(error)), `${label}: ${validation.errors.join("; ")}`);
  });
});

test("an unrehashed mutation fails the content address", () => {
  const payload = Generator.buildPayload();
  const artifact = { ...payload, contentAddress: Generator.contentAddress(payload) };
  artifact.templates[0].clearanceMm.left = 2;
  const validation = Generator.validateArtifact(artifact);
  assert.strictEqual(validation.valid, false);
  assert.ok(validation.errors.includes("content address mismatch"));
});

test("a printer profile that clips the declared box is rejected", () => {
  const profile = readJson(profilePath);
  profile.imagingBoxPt.right = 570;
  assert.throws(() => Generator.buildPayload({ profile }), /does not fit/);
});

test("renderer clipping is rejected", () => {
  const profile = readJson(profilePath);
  profile.rendererObservation300Dpi.printableOriginPx = [100, 170];
  assert.throws(() => Generator.buildPayload({ profile }), /does not fit/);
});

test("blank worksheet cannot silently claim authorization or a passed gate", () => {
  const worksheet = readJson(worksheetPath);
  assert.strictEqual(Generator.validateWorksheetTemplate(worksheet).valid, true);
  const authorized = clone(worksheet);
  authorized.authorization.printerUseAuthorized = true;
  assert.strictEqual(Generator.validateWorksheetTemplate(authorized).valid, false);
  const passed = clone(worksheet);
  passed.gates.print = "PASS";
  assert.strictEqual(Generator.validateWorksheetTemplate(passed).valid, false);
  const measured = clone(worksheet);
  measured.trialMeasurements.centerDefectRad = 1;
  assert.strictEqual(Generator.validateWorksheetTemplate(measured).valid, false);
});

test("generator CLI separates read-only validation from exclusive generation", () => {
  assert.deepStrictEqual(Generator.parseArguments([]), { mode: "generate", output: artifactPath });
  assert.deepStrictEqual(Generator.parseArguments(["--validate-only"]), { mode: "validate", input: artifactPath });
  assert.throws(() => Generator.parseArguments(["--unknown"]), /expected/);
  assert.throws(() => Generator.parseArguments(["--output"]), /expected/);
  assert.throws(() => Generator.parseArguments(["--output", "a", "--output", "b"]), /expected/);
});

test("exclusive writer cannot replace an existing evidence artifact", () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-physical-preflight-"));
  const output = path.join(directory, "evidence.json");
  try {
    Generator.writeExclusive(output, "first\n");
    assert.throws(() => Generator.writeExclusive(output, "second\n"), /EEXIST/);
    assert.strictEqual(fs.readFileSync(output, "utf8"), "first\n");
  } finally {
    fs.rmSync(directory, { recursive: true });
  }
});

let passed = 0;
for (const entry of tests) {
  try {
    entry.body();
    passed += 1;
    process.stdout.write(`ok ${passed} - ${entry.name}\n`);
  } catch (error) {
    process.stderr.write(`not ok - ${entry.name}\n${error.stack || error.message}\n`);
    process.exitCode = 1;
  }
}
if (!process.exitCode) process.stdout.write(`\n1..${passed}\nAll Global Geometry II physical-preflight tests passed.\n`);
