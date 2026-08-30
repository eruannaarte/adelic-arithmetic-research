#!/usr/bin/env node
"use strict";

const assert = require("assert");
const childProcess = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const Release = require("./generate-global-geometry-ii-release.js");
const Reproduce = require("./reproduce-global-geometry-ii.js");
const Compare = require("./compare-global-geometry-ii-certificates.js");

const tests = [];
function test(name, body) { tests.push({ name, body }); }

function clone(value) { return JSON.parse(JSON.stringify(value)); }

function reseal(certificate) {
  delete certificate.contentAddress;
  certificate.contentAddress = Release.contentAddress(certificate);
  return certificate;
}

function baseDarwinCertificate() {
  const emptyDigest = Release.sha256Bytes(Buffer.alloc(0));
  const payload = {
    schema: Reproduce.CERTIFICATE_SCHEMA,
    verifierVersion: Reproduce.VERIFIER_VERSION,
    generatedAtUtc: "2026-08-30T17:00:00.000Z",
    verificationStatus: "PASS",
    readOnlyVerification: "PASS_SOURCE_ARTIFACT_AND_RELEASE_SURFACE_UNCHANGED",
    environment: {
      platform: "darwin",
      architecture: "arm64",
      operatingSystemRelease: "fixture-darwin",
      endianness: "LE",
      nodeVersion: "v22.22.2",
      v8Version: "fixture-v8",
      uvVersion: "fixture-uv",
      logicalCpuCount: 1,
      cpuModel: "Synthetic Darwin fixture CPU",
      totalMemoryBytes: 1
    },
    suites: Release.SUITES.map((suite) => ({
      id: suite.id,
      path: suite.path,
      status: "PASS",
      exitCode: 0,
      durationMs: 0,
      stdoutBytes: 0,
      stdoutSha256: emptyDigest,
      stderrBytes: 0,
      stderrSha256: emptyDigest
    })),
    scientificDigests: {
      manifestContentAddress: Release.contentAddress({ fixture: "manifest" }),
      releaseIndexContentAddress: Release.contentAddress({ fixture: "index" }),
      sourceSnapshotSha256: Release.sha256Bytes(Buffer.from("fixture-source", "utf8")),
      artifacts: [
        { id: "calibration-v1", schema: "ggii.calibration-artifact/1" },
        { id: "atlas-pilot-v1", schema: "ggii.atlas-pilot-artifact/1" },
        { id: "inverse-certificates-v1", schema: "ggii.inverse-certificates-artifact/1" },
        { id: "sheet-hil-v1", schema: "ggii.sheet-hil-artifact/1" }
      ].map((entry) => Object.assign({}, entry, {
        rawSha256: Release.sha256Bytes(Buffer.from("raw:" + entry.id, "utf8")),
        semanticAddress: Release.contentAddress({ fixture: entry.id })
      })),
      reproductionResources: [{
        id: "programmable-sheet-fabrication-package-v1",
        manifestPath: "artifacts/global-geometry-ii/fabrication/fabrication-manifest.json",
        rawSha256: Release.sha256Bytes(Buffer.from("fixture-fabrication-raw", "utf8")),
        semanticAddress: Release.contentAddress({ fixture: "fabrication" }),
        physicalValidation: "NOT_RUN"
      }]
    },
    localReplayObservations: {
      schema: Reproduce.LOCAL_REPLAY_OBSERVATIONS_SCHEMA,
      atlas: {
        policyId: "ggii.atlas-cross-platform-replay/1",
        continuousTolerance: {
          absolute: 1e-12,
          relative: 1e-12,
          formula: "|a-b| <= 1e-12 + 1e-12*max(1,|a|,|b|)"
        },
        pilotValidation: { committed: "PASS", replay: "PASS" },
        exactComparisonCounts: { objects: 1, arrays: 1, exactScalars: 1, exactIntegerNumbers: 1 },
        continuousComparisonCounts: { numbers: 1, differences: 0, toleratedDifferences: 0 },
        mismatchCount: 0,
        derivedFieldCounts: { comparedInternallyOnly: 8, differences: 0 },
        maxima: {
          absoluteDifference: { value: 0, path: null },
          scaledRelativeDifference: { value: 0, path: null },
          toleranceFraction: { value: 0, path: null }
        }
      }
    },
    certification: {
      interpretation: "This is one local execution record. It does not prove equality with any other machine, operating system, or certificate.",
      observedPlatform: "darwin",
      observedPlatformIsRequiredClass: true,
      requiredIndependentPlatforms: ["darwin", "win32"],
      crossPlatformEqualityClaim: "NOT_MADE",
      windowsCertificate: "ABSENT_REQUIRED_INPUT_NOT_SIMULATED",
      releaseGate: "OPEN_PENDING_REVIEWED_INDEPENDENT_DARWIN_AND_WIN32_CERTIFICATES"
    }
  };
  return reseal(payload);
}

function certificateFor(platform) {
  const certificate = baseDarwinCertificate();
  if (platform === "win32") {
    certificate.generatedAtUtc = "2026-08-30T18:00:00.000Z";
    certificate.environment.platform = "win32";
    certificate.environment.architecture = "x64";
    certificate.environment.operatingSystemRelease = "10.0.26100-test-fixture";
    certificate.environment.cpuModel = "Independent Windows fixture CPU";
    certificate.certification.observedPlatform = "win32";
    certificate.certification.windowsCertificate = "THIS_RECORD_IS_A_LOCAL_WINDOWS_CANDIDATE_PENDING_INDEPENDENT_REVIEW";
  } else if (platform !== "darwin") {
    throw new Error("unsupported fixture platform");
  }
  return reseal(certificate);
}

function writeJson(filePath, value) {
  fs.writeFileSync(filePath, JSON.stringify(value, null, 2) + "\n", "utf8");
}

function withTempDirectory(body) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-certificate-comparison-"));
  try {
    return body(directory);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
}

function writePair(directory, darwin, windows, suffix) {
  const tag = suffix || "pair";
  const darwinPath = path.join(directory, tag + "-darwin.json");
  const windowsPath = path.join(directory, tag + "-windows.json");
  writeJson(darwinPath, darwin);
  writeJson(windowsPath, windows);
  return { darwinPath, windowsPath };
}

test("CLI requires exactly one explicit Darwin, Windows, and output path", () => {
  assert.throws(() => Compare.parseArgs([]), /exactly/);
  assert.throws(() => Compare.parseArgs(["--darwin", "a", "--windows", "b"]), /exactly/);
  assert.throws(() => Compare.parseArgs(["--darwin", "a", "--windows", "b", "--other", "c"]), /unknown/);
  assert.throws(() => Compare.parseArgs(["--darwin", "a", "--darwin", "b", "--output", "c"]), /only once/);
  assert.throws(() => Compare.parseArgs(["--darwin", "--windows", "b", "--output", "c", "tail"]), /requires|unknown/);
  assert.throws(() => Compare.parseArgs(["--darwin", "same", "--windows", "same", "--output", "out"]), /distinct/);
  const parsed = Compare.parseArgs(["--output", "out.json", "--windows", "win.json", "--darwin", "mac.json"]);
  assert.deepStrictEqual(parsed, {
    darwin: path.join(Release.REPO_ROOT, "mac.json"),
    windows: path.join(Release.REPO_ROOT, "win.json"),
    output: path.join(Release.REPO_ROOT, "out.json")
  });
});

test("synthetic Darwin fixture passes the closed local-certificate schema and address", () => {
  const verified = Compare.validateLocalCertificate(baseDarwinCertificate(), "Darwin fixture");
  assert.strictEqual(verified.platform, "darwin");
  assert.strictEqual(verified.artifact.suites.length, 9);
  assert.deepStrictEqual(
    verified.artifact.suites.map((suite) => ({ id: suite.id, path: suite.path })),
    Compare.EXPECTED_SUITES
  );
  assert.deepStrictEqual(verified.address, verified.artifact.contentAddress);
});

test("matching Darwin and Windows records produce only the bounded deterministic comparison", () => withTempDirectory((directory) => {
  const darwin = certificateFor("darwin");
  const windows = certificateFor("win32");
  windows.suites.forEach((suite, index) => {
    suite.durationMs += 100 + index;
    suite.stdoutSha256 = (index % 2 ? "1" : "2").repeat(64);
    suite.stderrSha256 = (index % 2 ? "3" : "4").repeat(64);
  });
  const windowsAtlas = windows.localReplayObservations.atlas;
  windowsAtlas.continuousComparisonCounts.differences = 1;
  windowsAtlas.continuousComparisonCounts.toleratedDifferences = 1;
  windowsAtlas.derivedFieldCounts.differences = 8;
  windowsAtlas.maxima.absoluteDifference = { value: 1e-14, path: "root.pilot.runs[0].measurements.exact.gaussBonnetResidual" };
  windowsAtlas.maxima.scaledRelativeDifference = { value: 1e-14, path: "root.pilot.runs[0].measurements.exact.gaussBonnetResidual" };
  windowsAtlas.maxima.toleranceFraction = { value: 0.005, path: "root.pilot.runs[0].measurements.exact.gaussBonnetResidual" };
  reseal(windows);
  const paths = writePair(directory, darwin, windows);
  const first = Compare.compareCertificateFiles(paths.darwinPath, paths.windowsPath);
  const second = Compare.compareCertificateFiles(paths.darwinPath, paths.windowsPath);
  assert.strictEqual(first.payload.comparisonStatus, "PASS_FOR_DECLARED_DIGEST_AND_TEST_SURFACE");
  assert.strictEqual(first.payload.scope.closure, Compare.SCOPE_CLOSURE);
  assert.strictEqual(first.payload.scope.allOtherClaims, "OPEN_OR_UNCHANGED");
  assert.deepStrictEqual(first.payload.scope.claimsNotClosed, Compare.CLAIMS_NOT_CLOSED);
  assert.strictEqual(first.payload.suites.length, 9);
  assert.strictEqual(first.payload.localReplayObservations.length, 2);
  first.payload.localReplayObservations.forEach((entry) => {
    assert.strictEqual(Reproduce.validateLocalReplayObservations(entry.observation).valid, true);
  });
  assert.strictEqual(first.payload.localReplayObservations[1].observation.atlas.continuousComparisonCounts.differences, 1);
  assert.deepStrictEqual(first.payload.suites.map((suite) => ({ id: suite.id, path: suite.path })), Compare.EXPECTED_SUITES);
  assert.strictEqual(Release.canonicalStringify(first.payload), Release.canonicalStringify(second.payload));
  assert.ok(!Object.prototype.hasOwnProperty.call(first.payload, "generatedAtUtc"));
  assert.ok(!Object.prototype.hasOwnProperty.call(first.payload, "releaseGate"));
}));

test("comparison output is content-addressed, CLI-writable once, and independently verifiable", () => withTempDirectory((directory) => {
  const paths = writePair(directory, certificateFor("darwin"), certificateFor("win32"), "cli");
  const output = path.join(directory, "comparison.json");
  const child = childProcess.spawnSync(process.execPath, [
    path.join(__dirname, "compare-global-geometry-ii-certificates.js"),
    "--darwin", paths.darwinPath,
    "--windows", paths.windowsPath,
    "--output", output
  ], { cwd: Release.REPO_ROOT, encoding: "utf8" });
  assert.strictEqual(child.status, 0, child.stderr || child.stdout);
  const summary = JSON.parse(child.stdout);
  assert.strictEqual(summary.status, Compare.COMPARISON_STATUS);
  assert.strictEqual(summary.allOtherClaims, "OPEN_OR_UNCHANGED");
  assert.strictEqual(summary.suiteCount, 9);
  const artifact = JSON.parse(fs.readFileSync(output, "utf8"));
  const verified = Compare.validateComparisonArtifact(artifact);
  assert.deepStrictEqual(verified.address, artifact.contentAddress);
  assert.throws(() => Compare.writeComparison(output, verified.payload, [paths.darwinPath, paths.windowsPath]), /EEXIST|exist/i);
  assert.throws(() => Compare.writeComparison(paths.darwinPath, verified.payload, [paths.darwinPath, paths.windowsPath]), /overwrite/);
}));

test("certificate byte tampering and coordinated redigest schema widening are rejected", () => withTempDirectory((directory) => {
  const tampered = certificateFor("darwin");
  tampered.environment.architecture = "tampered-without-readdress";
  const tamperedPath = path.join(directory, "tampered.json");
  writeJson(tamperedPath, tampered);
  assert.throws(() => Compare.readLocalCertificate(tamperedPath, "Darwin"), /content address/);

  const widened = certificateFor("darwin");
  widened.unreviewedClaim = "PASS";
  reseal(widened);
  const widenedPath = path.join(directory, "widened.json");
  writeJson(widenedPath, widened);
  assert.throws(() => Compare.readLocalCertificate(widenedPath, "Darwin"), /noncanonical schema/);

  const nested = certificateFor("darwin");
  nested.scientificDigests.artifacts[0].extraDigest = "0".repeat(64);
  reseal(nested);
  const nestedPath = path.join(directory, "nested.json");
  writeJson(nestedPath, nested);
  assert.throws(() => Compare.readLocalCertificate(nestedPath, "Darwin"), /noncanonical schema/);

  const promoted = certificateFor("darwin");
  promoted.certification.interpretation = "This record proves every platform equivalent.";
  reseal(promoted);
  const promotedPath = path.join(directory, "promoted-local-claim.json");
  writeJson(promotedPath, promoted);
  assert.throws(() => Compare.readLocalCertificate(promotedPath, "Darwin"), /claim boundary/);

  const invalidObservation = certificateFor("darwin");
  invalidObservation.localReplayObservations.atlas.mismatchCount = 1;
  reseal(invalidObservation);
  const invalidObservationPath = path.join(directory, "invalid-observation.json");
  writeJson(invalidObservationPath, invalidObservation);
  assert.throws(() => Compare.readLocalCertificate(invalidObservationPath, "Darwin"), /localReplayObservations is invalid/);
}));

test("every declared digest class must match across Darwin and Windows", () => withTempDirectory((directory) => {
  const mutators = [
    ["manifest", (certificate) => { certificate.scientificDigests.manifestContentAddress.digest = "0".repeat(64); }],
    ["release-index", (certificate) => { certificate.scientificDigests.releaseIndexContentAddress.digest = "1".repeat(64); }],
    ["source", (certificate) => { certificate.scientificDigests.sourceSnapshotSha256 = "2".repeat(64); }],
    ["artifact raw", (certificate) => { certificate.scientificDigests.artifacts[0].rawSha256 = "3".repeat(64); }],
    ["artifact semantic", (certificate) => { certificate.scientificDigests.artifacts[1].semanticAddress.digest = "4".repeat(64); }],
    ["resource raw", (certificate) => { certificate.scientificDigests.reproductionResources[0].rawSha256 = "5".repeat(64); }],
    ["resource semantic", (certificate) => { certificate.scientificDigests.reproductionResources[0].semanticAddress.digest = "6".repeat(64); }]
  ];
  mutators.forEach(([label, mutate], index) => {
    const darwin = certificateFor("darwin");
    const windows = certificateFor("win32");
    mutate(windows);
    reseal(windows);
    const paths = writePair(directory, darwin, windows, "mismatch-" + index);
    assert.throws(() => Compare.compareCertificateFiles(paths.darwinPath, paths.windowsPath), /mismatch/, label);
  });
}));

test("same-platform, wrong-role, non-PASS, and altered suite-surface inputs are rejected", () => withTempDirectory((directory) => {
  let paths = writePair(directory, certificateFor("darwin"), certificateFor("darwin"), "same-platform");
  assert.throws(() => Compare.compareCertificateFiles(paths.darwinPath, paths.windowsPath), /win32/);

  paths = writePair(directory, certificateFor("win32"), certificateFor("darwin"), "reversed");
  assert.throws(() => Compare.compareCertificateFiles(paths.darwinPath, paths.windowsPath), /darwin/);

  const failed = certificateFor("win32");
  failed.suites[2].status = "FAIL";
  failed.suites[2].exitCode = 1;
  reseal(failed);
  paths = writePair(directory, certificateFor("darwin"), failed, "failed-suite");
  assert.throws(() => Compare.compareCertificateFiles(paths.darwinPath, paths.windowsPath), /zero-exit PASS/);

  const changedPath = certificateFor("win32");
  changedPath.suites[4].path = "website/global-geometry-lab/a-different-test.js";
  reseal(changedPath);
  paths = writePair(directory, certificateFor("darwin"), changedPath, "changed-path");
  assert.throws(() => Compare.compareCertificateFiles(paths.darwinPath, paths.windowsPath), /must be suite/);

  const missing = certificateFor("win32");
  missing.suites.pop();
  reseal(missing);
  paths = writePair(directory, certificateFor("darwin"), missing, "missing-suite");
  assert.throws(() => Compare.compareCertificateFiles(paths.darwinPath, paths.windowsPath), /length 9/);

  const observationMismatch = certificateFor("win32");
  observationMismatch.localReplayObservations.atlas.exactComparisonCounts.objects += 1;
  reseal(observationMismatch);
  paths = writePair(directory, certificateFor("darwin"), observationMismatch, "observation-surface");
  assert.throws(() => Compare.compareCertificateFiles(paths.darwinPath, paths.windowsPath), /atlas exact comparison counts mismatch/);
}));

test("comparison-certificate tampering and scope promotion cannot be redigested into validity", () => withTempDirectory((directory) => {
  const paths = writePair(directory, certificateFor("darwin"), certificateFor("win32"), "output-tamper");
  const comparison = Compare.compareCertificateFiles(paths.darwinPath, paths.windowsPath);
  const artifact = Compare.packageComparison(comparison.payload);

  const tampered = clone(artifact);
  tampered.scope.allOtherClaims = "CLOSED";
  assert.throws(() => Compare.validateComparisonArtifact(tampered), /scope exceeds|content address/);

  const promoted = clone(artifact);
  delete promoted.contentAddress;
  promoted.scope.allOtherClaims = "CLOSED";
  promoted.contentAddress = Release.contentAddress(promoted);
  assert.throws(() => Compare.validateComparisonArtifact(promoted), /scope exceeds/);

  const rewritten = clone(artifact);
  delete rewritten.contentAddress;
  rewritten.scope.interpretation = "This proves all operating-system behavior and all physical claims.";
  rewritten.contentAddress = Release.contentAddress(rewritten);
  assert.throws(() => Compare.validateComparisonArtifact(rewritten), /interpretation exceeds/);

  const widened = clone(artifact);
  delete widened.contentAddress;
  widened.publicationApproved = true;
  widened.contentAddress = Release.contentAddress(widened);
  assert.throws(() => Compare.validateComparisonArtifact(widened), /noncanonical schema/);
}));

let passed = 0;
for (const entry of tests) {
  try {
    entry.body();
    passed += 1;
    process.stdout.write("ok " + passed + " - " + entry.name + "\n");
  } catch (error) {
    process.stderr.write("not ok - " + entry.name + "\n" + (error.stack || error.message) + "\n");
    process.exitCode = 1;
    break;
  }
}

if (!process.exitCode) {
  process.stdout.write("\n1.." + passed + "\nAll Global Geometry II certificate-comparison tests passed.\n");
}
