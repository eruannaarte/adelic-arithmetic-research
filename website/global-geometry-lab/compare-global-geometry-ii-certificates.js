#!/usr/bin/env node
"use strict";

/*
 * Compare one content-addressed Darwin local-reproduction certificate with one
 * content-addressed Windows certificate. The result closes only equality of
 * the declared digest and focused-test surface. It does not compare timings,
 * stdout bytes, floating-point behavior outside addressed artifacts, hardware,
 * physical experiments, publication approval, or the correctness of claims
 * beyond the bounded local verification contract.
 */

const fs = require("fs");
const path = require("path");
const Release = require("./generate-global-geometry-ii-release.js");
const Reproduce = require("./reproduce-global-geometry-ii.js");

const COMPARATOR_VERSION = "1.0.0-alpha.2";
const COMPARISON_SCHEMA = "ggii.cross-platform-reproduction-comparison/2";
const COMPARISON_STATUS = "PASS_FOR_DECLARED_DIGEST_AND_TEST_SURFACE";
const SCOPE_CLOSURE = "CLOSES_ONLY_DARWIN_WIN32_REPRODUCTION_FOR_DECLARED_DIGEST_AND_TEST_SURFACE";
const SCOPE_INTERPRETATION = "The supplied darwin and win32 local certificates have valid content addresses and valid local atlas replay observations, the canonical nine PASS suite identities/paths, and identical declared release/source/scientific/reproduction digests.";
const LOCAL_INTERPRETATION = "This is one local execution record. It does not prove equality with any other machine, operating system, or certificate.";
const MAX_CERTIFICATE_BYTES = 16 * 1024 * 1024;

const EXPECTED_SUITES = Object.freeze(Release.SUITES.map((suite) => Object.freeze({
  id: suite.id,
  path: suite.path
})));

const EXPECTED_ARTIFACTS = Object.freeze([
  Object.freeze({ id: "calibration-v1", schema: "ggii.calibration-artifact/1" }),
  Object.freeze({ id: "atlas-pilot-v1", schema: "ggii.atlas-pilot-artifact/1" }),
  Object.freeze({ id: "inverse-certificates-v1", schema: "ggii.inverse-certificates-artifact/1" }),
  Object.freeze({ id: "sheet-hil-v1", schema: "ggii.sheet-hil-artifact/1" })
]);

const EXPECTED_RESOURCE = Object.freeze({
  id: "programmable-sheet-fabrication-package-v1",
  manifestPath: "artifacts/global-geometry-ii/fabrication/fabrication-manifest.json"
});

const LOCAL_TOP_LEVEL_KEYS = Object.freeze([
  "schema",
  "verifierVersion",
  "generatedAtUtc",
  "verificationStatus",
  "readOnlyVerification",
  "environment",
  "suites",
  "scientificDigests",
  "localReplayObservations",
  "certification",
  "contentAddress"
]);

const CLAIMS_NOT_CLOSED = Object.freeze([
  "suite stdout, stderr, duration, or performance equality",
  "floating-point equality beyond the addressed artifacts and PASS gates",
  "bounded-disk universality or continuum, path-space, operator, or material convergence",
  "correctness or completeness of the mathematical models or scientific claims",
  "camera, actuator, programmable-sheet, or other physical validation",
  "hardware safety, fabrication, purchase, deployment, merge, or publication approval",
  "authentication, organizational independence, or machine identity beyond the two supplied certificate records"
]);

function isPlainObject(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function own(value, key) {
  return Object.prototype.hasOwnProperty.call(value, key);
}

function assertClosedObject(value, keys, location) {
  if (!isPlainObject(value)) throw new Error(location + " must be a plain JSON object");
  const actual = Object.keys(value).sort();
  const expected = keys.slice().sort();
  if (Release.canonicalStringify(actual) !== Release.canonicalStringify(expected)) {
    throw new Error(location + " has a noncanonical schema; expected keys " + expected.join(", "));
  }
}

function assertDenseArray(value, length, location) {
  if (!Array.isArray(value) || value.length !== length) {
    throw new Error(location + " must be a dense array of length " + length);
  }
  for (let index = 0; index < value.length; index += 1) {
    if (!own(value, index)) throw new Error(location + " must be dense");
  }
  if (Object.keys(value).length !== value.length) throw new Error(location + " has non-index properties");
}

function assertString(value, location, maximumLength) {
  if (typeof value !== "string" || value.length === 0 || value.length > (maximumLength || 4096)) {
    throw new Error(location + " must be a non-empty bounded string");
  }
  if (/\u0000/.test(value)) throw new Error(location + " contains a NUL character");
}

function assertSafeInteger(value, location, minimum) {
  if (!Number.isSafeInteger(value) || value < (minimum == null ? 0 : minimum)) {
    throw new Error(location + " must be a safe integer");
  }
}

function assertSha256(value, location) {
  if (typeof value !== "string" || !/^[0-9a-f]{64}$/.test(value)) {
    throw new Error(location + " must be a lowercase SHA-256 digest");
  }
}

function assertContentAddress(value, location, requiredCanonicalization) {
  assertClosedObject(value, ["algorithm", "canonicalization", "digest", "canonicalBytes"], location);
  if (value.algorithm !== "sha256") throw new Error(location + ".algorithm must be sha256");
  assertString(value.canonicalization, location + ".canonicalization", 128);
  if (requiredCanonicalization && value.canonicalization !== requiredCanonicalization) {
    throw new Error(location + ".canonicalization must be " + requiredCanonicalization);
  }
  assertSha256(value.digest, location + ".digest");
  assertSafeInteger(value.canonicalBytes, location + ".canonicalBytes", 1);
}

function sameJson(left, right) {
  return Release.canonicalStringify(left) === Release.canonicalStringify(right);
}

function cloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}

function validateEnvironment(environment, location) {
  assertClosedObject(environment, [
    "platform",
    "architecture",
    "operatingSystemRelease",
    "endianness",
    "nodeVersion",
    "v8Version",
    "uvVersion",
    "logicalCpuCount",
    "cpuModel",
    "totalMemoryBytes"
  ], location);
  ["platform", "architecture", "operatingSystemRelease", "nodeVersion", "v8Version", "uvVersion", "cpuModel"].forEach((field) => {
    assertString(environment[field], location + "." + field, 1024);
  });
  if (environment.platform !== "darwin" && environment.platform !== "win32") {
    throw new Error(location + ".platform must be darwin or win32");
  }
  if (environment.endianness !== "LE" && environment.endianness !== "BE") {
    throw new Error(location + ".endianness must be LE or BE");
  }
  assertSafeInteger(environment.logicalCpuCount, location + ".logicalCpuCount", 1);
  assertSafeInteger(environment.totalMemoryBytes, location + ".totalMemoryBytes", 1);
}

function validateSuite(suite, expected, index, location) {
  assertClosedObject(suite, [
    "id",
    "path",
    "status",
    "exitCode",
    "durationMs",
    "stdoutBytes",
    "stdoutSha256",
    "stderrBytes",
    "stderrSha256"
  ], location);
  if (suite.id !== expected.id || suite.path !== expected.path) {
    throw new Error(location + " must be suite " + index + " (" + expected.id + ", " + expected.path + ")");
  }
  if (suite.status !== "PASS" || suite.exitCode !== 0) {
    throw new Error(location + " must be a zero-exit PASS record");
  }
  if (typeof suite.durationMs !== "number" || !Number.isFinite(suite.durationMs) || suite.durationMs < 0) {
    throw new Error(location + ".durationMs must be a nonnegative finite number");
  }
  assertSafeInteger(suite.stdoutBytes, location + ".stdoutBytes", 0);
  assertSafeInteger(suite.stderrBytes, location + ".stderrBytes", 0);
  assertSha256(suite.stdoutSha256, location + ".stdoutSha256");
  assertSha256(suite.stderrSha256, location + ".stderrSha256");
}

function validateScientificDigests(scientific, location) {
  assertClosedObject(scientific, [
    "manifestContentAddress",
    "releaseIndexContentAddress",
    "sourceSnapshotSha256",
    "artifacts",
    "reproductionResources"
  ], location);
  assertContentAddress(scientific.manifestContentAddress, location + ".manifestContentAddress", Release.ADDRESS_CANONICALIZATION);
  assertContentAddress(scientific.releaseIndexContentAddress, location + ".releaseIndexContentAddress", Release.ADDRESS_CANONICALIZATION);
  assertSha256(scientific.sourceSnapshotSha256, location + ".sourceSnapshotSha256");

  assertDenseArray(scientific.artifacts, EXPECTED_ARTIFACTS.length, location + ".artifacts");
  scientific.artifacts.forEach((entry, index) => {
    const expected = EXPECTED_ARTIFACTS[index];
    const itemLocation = location + ".artifacts[" + index + "]";
    assertClosedObject(entry, ["id", "schema", "rawSha256", "semanticAddress"], itemLocation);
    if (entry.id !== expected.id || entry.schema !== expected.schema) {
      throw new Error(itemLocation + " identity/schema does not match the declared release artifact surface");
    }
    assertSha256(entry.rawSha256, itemLocation + ".rawSha256");
    assertContentAddress(entry.semanticAddress, itemLocation + ".semanticAddress");
  });

  assertDenseArray(scientific.reproductionResources, 1, location + ".reproductionResources");
  const resource = scientific.reproductionResources[0];
  const resourceLocation = location + ".reproductionResources[0]";
  assertClosedObject(resource, ["id", "manifestPath", "rawSha256", "semanticAddress", "physicalValidation"], resourceLocation);
  if (resource.id !== EXPECTED_RESOURCE.id || resource.manifestPath !== EXPECTED_RESOURCE.manifestPath) {
    throw new Error(resourceLocation + " does not match the declared reproduction-resource surface");
  }
  assertSha256(resource.rawSha256, resourceLocation + ".rawSha256");
  assertContentAddress(resource.semanticAddress, resourceLocation + ".semanticAddress", Release.ADDRESS_CANONICALIZATION);
  if (resource.physicalValidation !== "NOT_RUN") {
    throw new Error(resourceLocation + ".physicalValidation must remain NOT_RUN");
  }
}

function validateCertification(certification, platform, location) {
  assertClosedObject(certification, [
    "interpretation",
    "observedPlatform",
    "observedPlatformIsRequiredClass",
    "requiredIndependentPlatforms",
    "crossPlatformEqualityClaim",
    "windowsCertificate",
    "releaseGate"
  ], location);
  if (certification.interpretation !== LOCAL_INTERPRETATION) {
    throw new Error(location + ".interpretation exceeds or changes the local-certificate claim boundary");
  }
  if (certification.observedPlatform !== platform || certification.observedPlatformIsRequiredClass !== true) {
    throw new Error(location + " is not bound to its required-class environment platform");
  }
  assertDenseArray(certification.requiredIndependentPlatforms, 2, location + ".requiredIndependentPlatforms");
  if (!sameJson(certification.requiredIndependentPlatforms, ["darwin", "win32"])) {
    throw new Error(location + ".requiredIndependentPlatforms must be [darwin, win32]");
  }
  if (certification.crossPlatformEqualityClaim !== "NOT_MADE") {
    throw new Error(location + " must remain a local certificate with no cross-platform equality claim");
  }
  const expectedWindowsRecord = platform === "win32"
    ? "THIS_RECORD_IS_A_LOCAL_WINDOWS_CANDIDATE_PENDING_INDEPENDENT_REVIEW"
    : "ABSENT_REQUIRED_INPUT_NOT_SIMULATED";
  if (certification.windowsCertificate !== expectedWindowsRecord) {
    throw new Error(location + ".windowsCertificate is inconsistent with " + platform);
  }
  if (certification.releaseGate !== "OPEN_PENDING_REVIEWED_INDEPENDENT_DARWIN_AND_WIN32_CERTIFICATES") {
    throw new Error(location + ".releaseGate is not the local-certificate open gate");
  }
}

function validateLocalCertificate(artifact, location) {
  location = location || "certificate";
  assertClosedObject(artifact, LOCAL_TOP_LEVEL_KEYS, location);
  if (artifact.schema !== Reproduce.CERTIFICATE_SCHEMA) {
    throw new Error(location + ".schema must be " + Reproduce.CERTIFICATE_SCHEMA);
  }
  if (artifact.verifierVersion !== Reproduce.VERIFIER_VERSION) {
    throw new Error(location + ".verifierVersion must be " + Reproduce.VERIFIER_VERSION);
  }
  assertString(artifact.generatedAtUtc, location + ".generatedAtUtc", 64);
  const parsedTime = Date.parse(artifact.generatedAtUtc);
  if (!Number.isFinite(parsedTime) || new Date(parsedTime).toISOString() !== artifact.generatedAtUtc) {
    throw new Error(location + ".generatedAtUtc must be a canonical UTC ISO timestamp");
  }
  if (artifact.verificationStatus !== "PASS") throw new Error(location + ".verificationStatus must be PASS");
  if (artifact.readOnlyVerification !== "PASS_SOURCE_ARTIFACT_AND_RELEASE_SURFACE_UNCHANGED") {
    throw new Error(location + ".readOnlyVerification is not the declared PASS boundary");
  }

  assertContentAddress(artifact.contentAddress, location + ".contentAddress", Release.ADDRESS_CANONICALIZATION);
  const payload = Object.assign({}, artifact);
  delete payload.contentAddress;
  const computedAddress = Release.contentAddress(payload);
  if (!sameJson(artifact.contentAddress, computedAddress)) {
    throw new Error(location + " content address does not verify");
  }

  validateEnvironment(artifact.environment, location + ".environment");
  assertDenseArray(artifact.suites, EXPECTED_SUITES.length, location + ".suites");
  artifact.suites.forEach((suite, index) => validateSuite(suite, EXPECTED_SUITES[index], index, location + ".suites[" + index + "]"));
  validateScientificDigests(artifact.scientificDigests, location + ".scientificDigests");
  const observationValidation = Reproduce.validateLocalReplayObservations(artifact.localReplayObservations);
  if (!observationValidation.valid) {
    throw new Error(location + ".localReplayObservations is invalid: " + observationValidation.errors.join("; "));
  }
  validateCertification(artifact.certification, artifact.environment.platform, location + ".certification");

  return {
    artifact,
    payload,
    address: computedAddress,
    platform: artifact.environment.platform
  };
}

function readLocalCertificate(filePath, role) {
  const resolved = path.resolve(filePath);
  const stat = fs.lstatSync(resolved);
  if (!stat.isFile() || stat.isSymbolicLink()) throw new Error(role + " certificate must be a regular non-symlink file");
  if (stat.size <= 0 || stat.size > MAX_CERTIFICATE_BYTES) {
    throw new Error(role + " certificate exceeds the bounded file-size policy");
  }
  const raw = fs.readFileSync(resolved, "utf8");
  if (raw.charCodeAt(0) === 0xfeff) throw new Error(role + " certificate must not contain a byte-order mark");
  let artifact;
  try {
    artifact = JSON.parse(raw);
  } catch (error) {
    throw new Error(role + " certificate is not valid JSON: " + error.message);
  }
  const verified = validateLocalCertificate(artifact, role + " certificate");
  verified.path = resolved;
  return verified;
}

function assertMatchingSurface(darwin, windows) {
  const left = darwin.artifact.scientificDigests;
  const right = windows.artifact.scientificDigests;
  [
    ["manifest content address", left.manifestContentAddress, right.manifestContentAddress],
    ["release-index content address", left.releaseIndexContentAddress, right.releaseIndexContentAddress],
    ["source snapshot digest", left.sourceSnapshotSha256, right.sourceSnapshotSha256],
    ["scientific artifact digests", left.artifacts, right.artifacts],
    ["reproduction-resource digests", left.reproductionResources, right.reproductionResources]
  ].forEach(([label, first, second]) => {
    if (!sameJson(first, second)) throw new Error("Darwin/Windows " + label + " mismatch");
  });

  const darwinSuites = darwin.artifact.suites.map((suite) => ({ id: suite.id, path: suite.path, status: suite.status }));
  const windowsSuites = windows.artifact.suites.map((suite) => ({ id: suite.id, path: suite.path, status: suite.status }));
  if (!sameJson(darwinSuites, windowsSuites)) {
    throw new Error("Darwin/Windows focused PASS suite identity/path mismatch");
  }

  const darwinAtlas = darwin.artifact.localReplayObservations.atlas;
  const windowsAtlas = windows.artifact.localReplayObservations.atlas;
  [
    ["atlas replay policy", darwinAtlas.policyId, windowsAtlas.policyId],
    ["atlas continuous tolerance", darwinAtlas.continuousTolerance, windowsAtlas.continuousTolerance],
    ["atlas exact comparison counts", darwinAtlas.exactComparisonCounts, windowsAtlas.exactComparisonCounts],
    ["atlas continuous number count", darwinAtlas.continuousComparisonCounts.numbers, windowsAtlas.continuousComparisonCounts.numbers],
    ["atlas internally validated derived-field count", darwinAtlas.derivedFieldCounts.comparedInternallyOnly, windowsAtlas.derivedFieldCounts.comparedInternallyOnly]
  ].forEach(([label, first, second]) => {
    if (!sameJson(first, second)) throw new Error("Darwin/Windows " + label + " mismatch");
  });
}

function buildComparisonPayload(darwin, windows) {
  if (!darwin || darwin.platform !== "darwin") throw new Error("--darwin certificate platform must be darwin");
  if (!windows || windows.platform !== "win32") throw new Error("--windows certificate platform must be win32");
  if (sameJson(darwin.address, windows.address)) {
    throw new Error("Darwin and Windows certificates must be distinct content-addressed records");
  }
  assertMatchingSurface(darwin, windows);

  const scientific = darwin.artifact.scientificDigests;
  const payload = {
    schema: COMPARISON_SCHEMA,
    comparatorVersion: COMPARATOR_VERSION,
    comparisonStatus: COMPARISON_STATUS,
    scope: {
      closure: SCOPE_CLOSURE,
      interpretation: SCOPE_INTERPRETATION,
      allOtherClaims: "OPEN_OR_UNCHANGED",
      claimsNotClosed: CLAIMS_NOT_CLOSED.slice()
    },
    certificates: [
      { platform: "darwin", localCertificateContentAddress: cloneJson(darwin.address) },
      { platform: "win32", localCertificateContentAddress: cloneJson(windows.address) }
    ],
    localReplayObservations: [
      { platform: "darwin", observation: cloneJson(darwin.artifact.localReplayObservations) },
      { platform: "win32", observation: cloneJson(windows.artifact.localReplayObservations) }
    ],
    matchedDigests: {
      manifestContentAddress: cloneJson(scientific.manifestContentAddress),
      releaseIndexContentAddress: cloneJson(scientific.releaseIndexContentAddress),
      sourceSnapshotSha256: scientific.sourceSnapshotSha256,
      artifacts: cloneJson(scientific.artifacts),
      reproductionResources: cloneJson(scientific.reproductionResources)
    },
    suites: EXPECTED_SUITES.map((suite) => ({ id: suite.id, path: suite.path, status: "PASS" }))
  };
  validateComparisonPayload(payload);
  return payload;
}

function validateComparisonPayload(payload) {
  assertClosedObject(payload, ["schema", "comparatorVersion", "comparisonStatus", "scope", "certificates", "localReplayObservations", "matchedDigests", "suites"], "comparison payload");
  if (payload.schema !== COMPARISON_SCHEMA || payload.comparatorVersion !== COMPARATOR_VERSION || payload.comparisonStatus !== COMPARISON_STATUS) {
    throw new Error("comparison payload identity/status mismatch");
  }
  assertClosedObject(payload.scope, ["closure", "interpretation", "allOtherClaims", "claimsNotClosed"], "comparison payload.scope");
  if (payload.scope.closure !== SCOPE_CLOSURE || payload.scope.allOtherClaims !== "OPEN_OR_UNCHANGED") {
    throw new Error("comparison payload scope exceeds the declared boundary");
  }
  if (payload.scope.interpretation !== SCOPE_INTERPRETATION) {
    throw new Error("comparison payload interpretation exceeds or changes the declared boundary");
  }
  assertDenseArray(payload.scope.claimsNotClosed, CLAIMS_NOT_CLOSED.length, "comparison payload.scope.claimsNotClosed");
  if (!sameJson(payload.scope.claimsNotClosed, CLAIMS_NOT_CLOSED)) throw new Error("comparison payload claim boundary mismatch");

  assertDenseArray(payload.certificates, 2, "comparison payload.certificates");
  payload.certificates.forEach((entry, index) => {
    assertClosedObject(entry, ["platform", "localCertificateContentAddress"], "comparison payload.certificates[" + index + "]");
    const expectedPlatform = index === 0 ? "darwin" : "win32";
    if (entry.platform !== expectedPlatform) throw new Error("comparison certificate platform order must be darwin, win32");
    assertContentAddress(entry.localCertificateContentAddress, "comparison payload.certificates[" + index + "].localCertificateContentAddress", Release.ADDRESS_CANONICALIZATION);
  });
  if (sameJson(payload.certificates[0].localCertificateContentAddress, payload.certificates[1].localCertificateContentAddress)) {
    throw new Error("comparison payload certificates must be distinct records");
  }

  assertDenseArray(payload.localReplayObservations, 2, "comparison payload.localReplayObservations");
  payload.localReplayObservations.forEach((entry, index) => {
    assertClosedObject(entry, ["platform", "observation"], "comparison payload.localReplayObservations[" + index + "]");
    const expectedPlatform = index === 0 ? "darwin" : "win32";
    if (entry.platform !== expectedPlatform) throw new Error("comparison replay-observation platform order must be darwin, win32");
    const validation = Reproduce.validateLocalReplayObservations(entry.observation);
    if (!validation.valid) throw new Error("comparison " + expectedPlatform + " replay observation is invalid: " + validation.errors.join("; "));
  });

  validateScientificDigests(payload.matchedDigests, "comparison payload.matchedDigests");
  assertDenseArray(payload.suites, EXPECTED_SUITES.length, "comparison payload.suites");
  payload.suites.forEach((suite, index) => {
    assertClosedObject(suite, ["id", "path", "status"], "comparison payload.suites[" + index + "]");
    if (suite.id !== EXPECTED_SUITES[index].id || suite.path !== EXPECTED_SUITES[index].path || suite.status !== "PASS") {
      throw new Error("comparison payload suite surface mismatch at index " + index);
    }
  });
  return true;
}

function packageComparison(payload) {
  validateComparisonPayload(payload);
  return Object.assign({}, cloneJson(payload), { contentAddress: Release.contentAddress(payload) });
}

function validateComparisonArtifact(artifact) {
  assertClosedObject(artifact, ["schema", "comparatorVersion", "comparisonStatus", "scope", "certificates", "localReplayObservations", "matchedDigests", "suites", "contentAddress"], "comparison certificate");
  assertContentAddress(artifact.contentAddress, "comparison certificate.contentAddress", Release.ADDRESS_CANONICALIZATION);
  const payload = Object.assign({}, artifact);
  delete payload.contentAddress;
  validateComparisonPayload(payload);
  const computed = Release.contentAddress(payload);
  if (!sameJson(artifact.contentAddress, computed)) throw new Error("comparison certificate content address does not verify");
  return { artifact, payload, address: computed };
}

function compareCertificateFiles(darwinPath, windowsPath) {
  const darwin = readLocalCertificate(darwinPath, "Darwin");
  const windows = readLocalCertificate(windowsPath, "Windows");
  return {
    darwin,
    windows,
    payload: buildComparisonPayload(darwin, windows)
  };
}

function writeComparison(outputPath, payload, protectedInputPaths) {
  const resolved = path.resolve(outputPath);
  const protectedPaths = new Set((protectedInputPaths || []).map((entry) => path.resolve(entry)));
  if (protectedPaths.has(resolved)) throw new Error("comparison output may not overwrite either input certificate");
  const artifact = packageComparison(payload);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  const descriptor = fs.openSync(resolved, "wx", 0o644);
  try {
    fs.writeFileSync(descriptor, JSON.stringify(artifact, null, 2) + "\n", "utf8");
  } finally {
    fs.closeSync(descriptor);
  }
  const replay = JSON.parse(fs.readFileSync(resolved, "utf8"));
  const verified = validateComparisonArtifact(replay);
  return { path: resolved, artifact: replay, address: verified.address };
}

function resolveExplicitPath(value, flag) {
  if (typeof value !== "string" || value.length === 0 || value.startsWith("--")) {
    throw new Error(flag + " requires one explicit file path");
  }
  return path.isAbsolute(value) ? path.normalize(value) : path.resolve(Release.REPO_ROOT, value);
}

function parseArgs(argv) {
  if (!Array.isArray(argv)) throw new Error("argv must be an array");
  if (argv.length !== 6) throw new Error("use exactly --darwin PATH --windows PATH --output PATH");
  const values = {};
  const allowed = new Set(["--darwin", "--windows", "--output"]);
  for (let index = 0; index < argv.length; index += 2) {
    const flag = argv[index];
    if (!allowed.has(flag)) throw new Error("unknown certificate-comparison argument " + flag);
    if (own(values, flag)) throw new Error(flag + " may be supplied only once");
    values[flag] = resolveExplicitPath(argv[index + 1], flag);
  }
  ["--darwin", "--windows", "--output"].forEach((flag) => {
    if (!own(values, flag)) throw new Error(flag + " is required");
  });
  const resolved = [values["--darwin"], values["--windows"], values["--output"]];
  if (new Set(resolved).size !== resolved.length) throw new Error("Darwin, Windows, and output paths must be distinct");
  return { darwin: resolved[0], windows: resolved[1], output: resolved[2] };
}

function main() {
  try {
    const args = parseArgs(process.argv.slice(2));
    const comparison = compareCertificateFiles(args.darwin, args.windows);
    const written = writeComparison(args.output, comparison.payload, [args.darwin, args.windows]);
    process.stdout.write(JSON.stringify({
      status: comparison.payload.comparisonStatus,
      scopeClosure: comparison.payload.scope.closure,
      allOtherClaims: comparison.payload.scope.allOtherClaims,
      comparedPlatforms: comparison.payload.certificates.map((entry) => entry.platform),
      suiteCount: comparison.payload.suites.length,
      output: written.path,
      sha256: written.address.digest
    }) + "\n");
  } catch (error) {
    process.stderr.write("Global Geometry II certificate comparison failed: " + (error && error.message ? error.message : String(error)) + "\n");
    process.exitCode = 1;
  }
}

if (require.main === module) main();

module.exports = {
  CLAIMS_NOT_CLOSED,
  COMPARATOR_VERSION,
  COMPARISON_SCHEMA,
  COMPARISON_STATUS,
  EXPECTED_ARTIFACTS,
  EXPECTED_RESOURCE,
  EXPECTED_SUITES,
  MAX_CERTIFICATE_BYTES,
  SCOPE_CLOSURE,
  SCOPE_INTERPRETATION,
  assertMatchingSurface,
  buildComparisonPayload,
  compareCertificateFiles,
  packageComparison,
  parseArgs,
  readLocalCertificate,
  validateComparisonArtifact,
  validateComparisonPayload,
  validateLocalCertificate,
  writeComparison
};
