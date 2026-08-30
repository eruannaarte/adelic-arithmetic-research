#!/usr/bin/env node
"use strict";

/*
 * Compare one Darwin and one Windows release-v2 deep certificate.  The result
 * closes only equality of the declared compact release digests and selected
 * quick/deep PASS suite surface.  Scientific acceptance/rejection,
 * universality, physical validation, and the historical v1 release remain
 * outside this comparison.
 */

const fs = require("fs");
const path = require("path");
const { TextDecoder } = require("util");
const Release = require("./generate-global-geometry-ii-release-v2.js");
const Reproduce = require("./reproduce-global-geometry-ii-v2.js");

const COMPARATOR_VERSION = "2.0.0";
const COMPARISON_SCHEMA = "ggii.cross-platform-reproduction-comparison/3";
const COMPARISON_STATUS = "PASS_FOR_RELEASE_V2_DECLARED_DIGEST_AND_DEEP_TEST_SURFACE";
const SCOPE_CLOSURE = "CLOSES_ONLY_DARWIN_WIN32_RELEASE_V2_REPRODUCTION_FOR_DECLARED_COMPACT_DIGEST_AND_DEEP_TEST_SURFACE";
const SCOPE_INTERPRETATION = "The supplied darwin and win32 release-v2 deep certificates have valid content addresses, the canonical quick suite surface, matching registry-frozen deep PASS suite identities, and identical declared v2 release/source/registry/compact-artifact digests.";
const MAX_CERTIFICATE_BYTES = 16 * 1024 * 1024;

const CLAIMS_NOT_CLOSED = Object.freeze([
  "U2 acceptance, U2 rejection, or any confirmatory universality decision",
  "mathematical correctness or completeness beyond the declared tests and addressed artifacts",
  "floating-point equality outside the declared compact-artifact and PASS-gate surface",
  "suite stdout, stderr, duration, resource use, or performance equality",
  "raw observation, chunk, partial-run, lock, working-checkpoint, transfer-helper, or log equality",
  "camera, actuator, programmable-sheet, fabrication, or other physical validation",
  "hardware safety, purchase, deployment, merge, or publication approval",
  "any claim carried by the historical v1 index or historical v1 comparison"
]);

const TOP_LEVEL_KEYS = Object.freeze([
  "schema",
  "verifierVersion",
  "generatedAtUtc",
  "verificationStatus",
  "verificationMode",
  "readOnlyVerification",
  "environment",
  "suites",
  "releaseDigests",
  "claimBoundary",
  "certification",
  "contentAddress"
]);

function isPlainObject(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function own(value, key) {
  return Object.prototype.hasOwnProperty.call(value, key);
}

function sameJson(left, right) {
  return Release.canonicalStringify(left) === Release.canonicalStringify(right);
}

function cloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}

function assertClosedObject(value, expectedKeys, location) {
  if (!isPlainObject(value)) throw new Error(location + " must be a plain JSON object");
  const actual = Object.keys(value).sort();
  const expected = expectedKeys.slice().sort();
  if (!sameJson(actual, expected)) throw new Error(location + " has a noncanonical schema; expected keys " + expected.join(", "));
}

function assertDenseArray(value, location, expectedLength) {
  if (!Array.isArray(value) || (expectedLength != null && value.length !== expectedLength)) {
    throw new Error(location + " must be a dense array" + (expectedLength == null ? "" : " of length " + expectedLength));
  }
  for (let index = 0; index < value.length; index += 1) {
    if (!own(value, index)) throw new Error(location + " must be dense");
  }
  if (Object.keys(value).length !== value.length) throw new Error(location + " has non-index properties");
}

function assertString(value, location, maximumLength) {
  if (typeof value !== "string" || !value || value.length > (maximumLength || 4096) || /\u0000/.test(value)) {
    throw new Error(location + " must be a non-empty bounded NUL-free string");
  }
}

function assertSafeInteger(value, location, minimum) {
  if (!Number.isSafeInteger(value) || value < (minimum == null ? 0 : minimum)) throw new Error(location + " must be a safe integer");
}

function assertSha256(value, location) {
  if (typeof value !== "string" || !/^[0-9a-f]{64}$/.test(value)) throw new Error(location + " must be a lowercase SHA-256 digest");
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

function validateEnvironment(environment, location) {
  assertClosedObject(environment, [
    "platform",
    "architecture",
    "endianness",
    "nodeVersion",
    "v8Version",
    "uvVersion"
  ], location);
  ["platform", "architecture", "nodeVersion", "v8Version", "uvVersion"].forEach((field) => {
    assertString(environment[field], location + "." + field, 1024);
  });
  if (environment.platform !== "darwin" && environment.platform !== "win32") throw new Error(location + ".platform must be darwin or win32");
  if (environment.endianness !== "LE" && environment.endianness !== "BE") throw new Error(location + ".endianness must be LE or BE");
}

function validateArgs(args, location) {
  assertDenseArray(args, location);
  args.forEach((arg, index) => assertString(arg, location + "[" + index + "]", 4096));
}

function validateSuiteResult(suite, location, tier) {
  assertClosedObject(suite, [
    "id",
    "path",
    "args",
    "tier",
    "coverage",
    "status",
    "exitCode",
    "durationMs",
    "stdoutBytes",
    "stdoutSha256",
    "stderrBytes",
    "stderrSha256"
  ], location);
  assertString(suite.id, location + ".id", 128);
  assertString(suite.path, location + ".path", 4096);
  validateArgs(suite.args, location + ".args");
  if (suite.tier !== tier) throw new Error(location + ".tier mismatch");
  const expectedCoverage = tier === "quick" ? "focused-quick" : null;
  if (expectedCoverage && suite.coverage !== expectedCoverage) throw new Error(location + ".coverage mismatch");
  if (tier === "deep" && !["screening-v3", "strict-partial", "evaluation-index"].includes(suite.coverage)) {
    throw new Error(location + ".coverage is not registered");
  }
  if (suite.status !== "PASS" || suite.exitCode !== 0) throw new Error(location + " must be a zero-exit PASS record");
  if (typeof suite.durationMs !== "number" || !Number.isFinite(suite.durationMs) || suite.durationMs < 0) {
    throw new Error(location + ".durationMs must be finite and nonnegative");
  }
  assertSafeInteger(suite.stdoutBytes, location + ".stdoutBytes", 0);
  assertSafeInteger(suite.stderrBytes, location + ".stderrBytes", 0);
  assertSha256(suite.stdoutSha256, location + ".stdoutSha256");
  assertSha256(suite.stderrSha256, location + ".stderrSha256");
}

function validateQuickSuites(quick, location) {
  assertDenseArray(quick, location, Release.QUICK_SUITES.length);
  quick.forEach((suite, index) => {
    validateSuiteResult(suite, location + "[" + index + "]", "quick");
    const expected = Release.QUICK_SUITES[index];
    if (suite.id !== expected.id || suite.path !== expected.path || !sameJson(suite.args, expected.args)) {
      throw new Error(location + "[" + index + "] does not match the canonical release-v2 quick suite");
    }
  });
}

function validateDeepSuites(deep, location) {
  const expectedSurfaces = Release.REQUIRED_DEEP_VALIDATION_SURFACES;
  assertDenseArray(deep, location, Object.keys(expectedSurfaces).length);
  const ids = new Set();
  const coverage = new Set();
  deep.forEach((suite, index) => {
    validateSuiteResult(suite, location + "[" + index + "]", "deep");
    if (ids.has(suite.id)) throw new Error(location + " contains a duplicate suite id");
    ids.add(suite.id);
    coverage.add(suite.coverage);
    if (!suite.args.some((arg) => Release.SAFE_DEEP_VALIDATION_FLAGS.includes(arg))) {
      throw new Error(location + "[" + index + "] does not select a registered read-only validation mode");
    }
    const expected = expectedSurfaces[suite.coverage];
    if (!expected || suite.id !== expected.id || suite.path !== expected.path || !sameJson(suite.args, expected.args)) {
      throw new Error(location + "[" + index + "] does not match the exact registry-frozen evaluation-index validator");
    }
  });
  Object.keys(expectedSurfaces).forEach((requiredCoverage) => {
    if (!coverage.has(requiredCoverage)) throw new Error(location + " omits required deep coverage " + requiredCoverage);
  });
}

function validateRegistryDigest(record, location) {
  assertClosedObject(record, ["path", "rawSha256", "rawBytes", "semanticAddress"], location);
  assertString(record.path, location + ".path", 4096);
  assertSha256(record.rawSha256, location + ".rawSha256");
  assertSafeInteger(record.rawBytes, location + ".rawBytes", 1);
  assertContentAddress(record.semanticAddress, location + ".semanticAddress", Release.ADDRESS_CANONICALIZATION);
}

function validateArtifactDigest(entry, index, location) {
  const itemLocation = location + "[" + index + "]";
  assertClosedObject(entry, ["id", "path", "role", "platform", "rawSha256", "rawBytes", "semanticAddress", "semanticReplay"], itemLocation);
  ["id", "path", "role", "platform"].forEach((field) => assertString(entry[field], itemLocation + "." + field, 4096));
  if (!Release.ENTRY_ROLES.includes(entry.role)) throw new Error(itemLocation + ".role is not registered");
  if (!["shared", "darwin", "win32"].includes(entry.platform)) throw new Error(itemLocation + ".platform is not registered");
  assertSha256(entry.rawSha256, itemLocation + ".rawSha256");
  assertSafeInteger(entry.rawBytes, itemLocation + ".rawBytes", 1);
  assertString(entry.semanticReplay, itemLocation + ".semanticReplay", 256);
  if (Release.ARCHIVE_ROLES.includes(entry.role)) {
    if (entry.semanticAddress !== null || entry.semanticReplay !== "NOT_APPLICABLE_GZIP_CONVENIENCE_COPY_DECOMPRESSED_ADDRESS_RECORDED_BY_EVALUATION_INDEX") {
      throw new Error(itemLocation + " must keep the gzip convenience archive outside semantic replay");
    }
  } else {
    assertContentAddress(entry.semanticAddress, itemLocation + ".semanticAddress");
    if (!["VERIFIED_SUPPLIED_CONTENT_ADDRESS", "CANONICAL_JSON_ADDRESS_COMPUTED", "UTF8_TEXT_ADDRESS_COMPUTED"].includes(entry.semanticReplay)) {
      throw new Error(itemLocation + ".semanticReplay is not registered");
    }
  }
}

function validateArchiveIndexBindings(bindingRecord, artifacts, location) {
  assertClosedObject(bindingRecord, ["evaluationIndexId", "evaluationIndexPath", "policy", "bindings"], location);
  ["evaluationIndexId", "evaluationIndexPath", "policy"].forEach((field) => assertString(bindingRecord[field], location + "." + field, 4096));
  if (bindingRecord.policy !== "RAW_GZIP_BYTES_ADDRESSED_ONLY; DECOMPRESSED_BYTE_ADDRESS_IMPORTED_FROM_CONTENT_ADDRESSED_EVALUATION_INDEX; NO_GZIP_SEMANTIC_REPLAY") {
    throw new Error(location + ".policy changes the raw-only archive boundary");
  }
  const evaluationIndexes = artifacts.filter((entry) => entry.role === "evaluation-index");
  if (evaluationIndexes.length !== 1 || evaluationIndexes[0].id !== bindingRecord.evaluationIndexId ||
      evaluationIndexes[0].path !== bindingRecord.evaluationIndexPath) {
    throw new Error(location + " is not bound to the registered evaluation index");
  }
  assertDenseArray(bindingRecord.bindings, location + ".bindings", 4);
  const archiveByPath = new Map(artifacts.filter((entry) => Release.ARCHIVE_ROLES.includes(entry.role)).map((entry) => [entry.path, entry]));
  const seen = new Set();
  bindingRecord.bindings.forEach((entry, index) => {
    const itemLocation = location + ".bindings[" + index + "]";
    assertClosedObject(entry, [
      "path",
      "rawSha256",
      "rawBytes",
      "decompressedSha256",
      "decompressedBytes",
      "correspondingSourcePath",
      "correspondingSourceSemanticDigest",
      "sourceKind",
      "scientificAuthority",
      "role"
    ], itemLocation);
    ["path", "correspondingSourcePath", "sourceKind", "scientificAuthority", "role"].forEach((field) => assertString(entry[field], itemLocation + "." + field, 4096));
    ["rawSha256", "decompressedSha256"].forEach((field) => assertSha256(entry[field], itemLocation + "." + field));
    assertSafeInteger(entry.rawBytes, itemLocation + ".rawBytes", 1);
    assertSafeInteger(entry.decompressedBytes, itemLocation + ".decompressedBytes", 1);
    if (entry.sourceKind === "STRICT_PARTIAL_CAMPAIGN") {
      assertSha256(entry.correspondingSourceSemanticDigest, itemLocation + ".correspondingSourceSemanticDigest");
    } else if (entry.sourceKind === "SCREENING_V3_RAW_JSONL") {
      if (entry.correspondingSourceSemanticDigest !== null) throw new Error(itemLocation + ".correspondingSourceSemanticDigest must be null for raw screening JSONL");
    } else {
      throw new Error(itemLocation + ".sourceKind is not registered");
    }
    if (entry.scientificAuthority !== "NONE" || entry.role !== Release.ARCHIVE_ROLE) {
      throw new Error(itemLocation + " promotes a raw-only archive");
    }
    const artifact = archiveByPath.get(entry.path);
    if (!artifact || artifact.rawSha256 !== entry.rawSha256 || artifact.rawBytes !== entry.rawBytes) {
      throw new Error(itemLocation + " does not match a registered raw-only archive");
    }
    const expectedKind = artifact.role === "strict-campaign-archive" ? "STRICT_PARTIAL_CAMPAIGN" : "SCREENING_V3_RAW_JSONL";
    if (entry.sourceKind !== expectedKind) throw new Error(itemLocation + ".sourceKind does not match its registry role");
    if (seen.has(entry.path)) throw new Error(location + " contains a duplicate archive path");
    seen.add(entry.path);
  });
  if (seen.size !== 4 || archiveByPath.size !== 4) throw new Error(location + " does not bind exactly the four registry archives");
}

function validateReleaseDigests(digests, location) {
  assertClosedObject(digests, [
    "manifestContentAddress",
    "releaseIndexContentAddress",
    "inputRegistry",
    "sourceSnapshotSha256",
    "archiveIndexBindings",
    "registeredArtifacts"
  ], location);
  assertContentAddress(digests.manifestContentAddress, location + ".manifestContentAddress", Release.ADDRESS_CANONICALIZATION);
  assertContentAddress(digests.releaseIndexContentAddress, location + ".releaseIndexContentAddress", Release.ADDRESS_CANONICALIZATION);
  validateRegistryDigest(digests.inputRegistry, location + ".inputRegistry");
  assertSha256(digests.sourceSnapshotSha256, location + ".sourceSnapshotSha256");
  assertDenseArray(digests.registeredArtifacts, location + ".registeredArtifacts");
  const ids = new Set();
  const paths = new Set();
  const roleCounts = Object.fromEntries(Release.ENTRY_ROLES.map((role) => [role, 0]));
  const rolePlatforms = Object.fromEntries(Release.REQUIRED_PAIRED_ROLES.map((role) => [role, new Set()]));
  digests.registeredArtifacts.forEach((entry, index) => {
    validateArtifactDigest(entry, index, location + ".registeredArtifacts");
    if (ids.has(entry.id) || paths.has(entry.path)) throw new Error(location + ".registeredArtifacts contains duplicate identity/path");
    ids.add(entry.id);
    paths.add(entry.path);
    roleCounts[entry.role] += 1;
    if (rolePlatforms[entry.role]) rolePlatforms[entry.role].add(entry.platform);
  });
  Object.entries(Release.REQUIRED_ROLE_COUNTS).forEach(([role, required]) => {
    if (roleCounts[role] !== required) throw new Error(location + ".registeredArtifacts must contain exactly " + required + " for role " + role);
  });
  Release.REQUIRED_PAIRED_ROLES.forEach((role) => {
    if (roleCounts[role] !== 2 || !sameJson(Array.from(rolePlatforms[role]).sort(), ["darwin", "win32"])) {
      throw new Error(location + ".registeredArtifacts role " + role + " is not a darwin/win32 pair");
    }
  });
  const principals = digests.registeredArtifacts
    .filter((entry) => entry.role === "principal-artifact")
    .map((entry) => ({ id: entry.id, path: entry.path, platform: entry.platform }))
    .sort((left, right) => left.id.localeCompare(right.id, "en"));
  const expectedPrincipals = Release.PRINCIPAL_ARTIFACTS
    .map((entry) => ({ id: entry.id, path: entry.path, platform: "shared" }))
    .sort((left, right) => left.id.localeCompare(right.id, "en"));
  if (!sameJson(principals, expectedPrincipals)) throw new Error(location + ".registeredArtifacts does not contain the exact principal-artifact surface");
  const physical = digests.registeredArtifacts
    .filter((entry) => entry.role === "physical-preflight")
    .map((entry) => ({ id: entry.id, path: entry.path, platform: entry.platform }));
  if (!sameJson(physical, [{ id: Release.PHYSICAL_PREFLIGHT_ARTIFACT.id, path: Release.PHYSICAL_PREFLIGHT_ARTIFACT.path, platform: "shared" }])) {
    throw new Error(location + ".registeredArtifacts does not contain the exact physical-preflight artifact");
  }
  validateArchiveIndexBindings(digests.archiveIndexBindings, digests.registeredArtifacts, location + ".archiveIndexBindings");
}

function validateClaimBoundary(boundary, location) {
  assertClosedObject(boundary, [
    "checkpointStatus",
    "u2Decision",
    "universalityClaim",
    "fullConfirmatoryEvaluation",
    "physicalValidation",
    "publicationMeaning",
    "interpretation"
  ], location);
  if (!["UNRESOLVED", "NOT_EVALUATED", "NOT_RUN"].includes(boundary.checkpointStatus) ||
      !["UNRESOLVED", "NOT_EVALUATED", "NOT_RUN"].includes(boundary.fullConfirmatoryEvaluation)) {
    throw new Error(location + " promotes an unresolved/not-run checkpoint");
  }
  if (boundary.u2Decision !== "NO_ACCEPTANCE_OR_REJECTION_CLAIM" || boundary.universalityClaim !== "NONE" ||
      boundary.physicalValidation !== "NOT_RUN" ||
      boundary.publicationMeaning !== "SHAREABLE_EVIDENCE_CHECKPOINT_NOT_A_CONFIRMATORY_DECISION") {
    throw new Error(location + " exceeds the release-v2 no-decision/no-physical-validation boundary");
  }
  if (boundary.interpretation !== "This release packages an evidence checkpoint. It makes no U2 acceptance or rejection decision, no universality claim, and no physical-validation claim.") {
    throw new Error(location + ".interpretation changes the frozen release-v2 claim boundary");
  }
}

function validateCertification(certification, platform, location) {
  assertClosedObject(certification, [
    "interpretation",
    "observedPlatform",
    "observedPlatformIsRequiredClass",
    "verificationMode",
    "requiredIndependentPlatforms",
    "crossPlatformEqualityClaim",
    "u2Decision",
    "universalityClaim",
    "physicalValidation",
    "historicalV1",
    "releaseGate"
  ], location);
  if (certification.interpretation !== Reproduce.LOCAL_INTERPRETATION) throw new Error(location + ".interpretation changes the local claim boundary");
  if (certification.observedPlatform !== platform || certification.observedPlatformIsRequiredClass !== true) {
    throw new Error(location + " is not bound to its required-class platform");
  }
  if (certification.verificationMode !== "deep") throw new Error(location + " must be a deep release-v2 certificate");
  assertDenseArray(certification.requiredIndependentPlatforms, location + ".requiredIndependentPlatforms", 2);
  if (!sameJson(certification.requiredIndependentPlatforms, ["darwin", "win32"])) throw new Error(location + ".requiredIndependentPlatforms mismatch");
  if (certification.crossPlatformEqualityClaim !== "NOT_MADE" ||
      certification.u2Decision !== "NO_ACCEPTANCE_OR_REJECTION_CLAIM" ||
      certification.universalityClaim !== "NONE" ||
      certification.physicalValidation !== "NOT_RUN" ||
      certification.historicalV1 !== Release.HISTORICAL_V1_CLASSIFICATION ||
      certification.releaseGate !== "OPEN_PENDING_REVIEWED_INDEPENDENT_DARWIN_AND_WIN32_DEEP_CERTIFICATES") {
    throw new Error(location + " exceeds or changes the release-v2 local-certificate boundary");
  }
}

function validateLocalCertificate(artifact, location) {
  location = location || "certificate";
  assertClosedObject(artifact, TOP_LEVEL_KEYS, location);
  if (artifact.schema !== Reproduce.CERTIFICATE_SCHEMA || artifact.verifierVersion !== Reproduce.VERIFIER_VERSION) {
    throw new Error(location + " schema/verifier mismatch");
  }
  assertString(artifact.generatedAtUtc, location + ".generatedAtUtc", 64);
  const parsed = Date.parse(artifact.generatedAtUtc);
  if (!Number.isFinite(parsed) || new Date(parsed).toISOString() !== artifact.generatedAtUtc) {
    throw new Error(location + ".generatedAtUtc must be a canonical UTC ISO timestamp");
  }
  if (artifact.verificationStatus !== "PASS" || artifact.verificationMode !== "deep" ||
      artifact.readOnlyVerification !== "PASS_SOURCE_REGISTRY_COMPACT_ARTIFACT_AND_RELEASE_SURFACE_UNCHANGED") {
    throw new Error(location + " is not a deep read-only PASS certificate");
  }
  assertContentAddress(artifact.contentAddress, location + ".contentAddress", Release.ADDRESS_CANONICALIZATION);
  const payload = Object.assign({}, artifact);
  delete payload.contentAddress;
  const computed = Release.contentAddress(payload);
  if (!sameJson(artifact.contentAddress, computed)) throw new Error(location + " content address does not verify");
  validateEnvironment(artifact.environment, location + ".environment");
  assertClosedObject(artifact.suites, ["quick", "deep"], location + ".suites");
  validateQuickSuites(artifact.suites.quick, location + ".suites.quick");
  validateDeepSuites(artifact.suites.deep, location + ".suites.deep");
  validateReleaseDigests(artifact.releaseDigests, location + ".releaseDigests");
  validateClaimBoundary(artifact.claimBoundary, location + ".claimBoundary");
  validateCertification(artifact.certification, artifact.environment.platform, location + ".certification");
  return { artifact, payload, address: computed, platform: artifact.environment.platform };
}

function readLocalCertificate(filePath, role) {
  const resolved = path.resolve(filePath);
  const stat = fs.lstatSync(resolved);
  if (!stat.isFile() || stat.isSymbolicLink() || stat.size < 1 || stat.size > MAX_CERTIFICATE_BYTES) {
    throw new Error(role + " certificate must be a bounded regular non-symlink file");
  }
  const raw = fs.readFileSync(resolved);
  if (raw.length >= 3 && raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf) throw new Error(role + " certificate must not contain a byte-order mark");
  let artifact;
  try { artifact = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(raw)); }
  catch (error) { throw new Error(role + " certificate is not valid JSON: " + error.message); }
  const verified = validateLocalCertificate(artifact, role + " certificate");
  verified.path = resolved;
  return verified;
}

function comparableSuites(certificate) {
  return {
    quick: certificate.artifact.suites.quick.map((suite) => ({ id: suite.id, path: suite.path, args: suite.args, tier: suite.tier, coverage: suite.coverage, status: suite.status })),
    deep: certificate.artifact.suites.deep.map((suite) => ({ id: suite.id, path: suite.path, args: suite.args, tier: suite.tier, coverage: suite.coverage, status: suite.status }))
  };
}

function assertMatchingSurface(darwin, windows) {
  if (!sameJson(darwin.artifact.releaseDigests, windows.artifact.releaseDigests)) {
    throw new Error("Darwin/Windows release-v2 declared digest surface mismatch");
  }
  if (!sameJson(comparableSuites(darwin), comparableSuites(windows))) {
    throw new Error("Darwin/Windows release-v2 quick/deep PASS suite surface mismatch");
  }
  if (!sameJson(darwin.artifact.claimBoundary, windows.artifact.claimBoundary)) {
    throw new Error("Darwin/Windows release-v2 claim-boundary mismatch");
  }
}

function buildComparisonPayload(darwin, windows) {
  if (!darwin || darwin.platform !== "darwin") throw new Error("--darwin certificate platform must be darwin");
  if (!windows || windows.platform !== "win32") throw new Error("--windows certificate platform must be win32");
  if (sameJson(darwin.address, windows.address)) throw new Error("Darwin and Windows certificates must be distinct records");
  assertMatchingSurface(darwin, windows);
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
    matchedDigests: cloneJson(darwin.artifact.releaseDigests),
    suites: comparableSuites(darwin),
    claimBoundary: cloneJson(darwin.artifact.claimBoundary),
    historicalV1: {
      classification: Release.HISTORICAL_V1_CLASSIFICATION,
      interpretation: "The historical v1 comparison does not certify any release-v2 source, artifact, evaluation, or suite surface."
    }
  };
  validateComparisonPayload(payload);
  return payload;
}

function validateComparisonPayload(payload) {
  assertClosedObject(payload, [
    "schema",
    "comparatorVersion",
    "comparisonStatus",
    "scope",
    "certificates",
    "matchedDigests",
    "suites",
    "claimBoundary",
    "historicalV1"
  ], "comparison payload");
  if (payload.schema !== COMPARISON_SCHEMA || payload.comparatorVersion !== COMPARATOR_VERSION || payload.comparisonStatus !== COMPARISON_STATUS) {
    throw new Error("comparison payload identity/status mismatch");
  }
  assertClosedObject(payload.scope, ["closure", "interpretation", "allOtherClaims", "claimsNotClosed"], "comparison payload.scope");
  if (payload.scope.closure !== SCOPE_CLOSURE || payload.scope.interpretation !== SCOPE_INTERPRETATION || payload.scope.allOtherClaims !== "OPEN_OR_UNCHANGED") {
    throw new Error("comparison payload scope exceeds or changes its declared boundary");
  }
  assertDenseArray(payload.scope.claimsNotClosed, "comparison payload.scope.claimsNotClosed", CLAIMS_NOT_CLOSED.length);
  if (!sameJson(payload.scope.claimsNotClosed, CLAIMS_NOT_CLOSED)) throw new Error("comparison payload claim exclusions mismatch");
  assertDenseArray(payload.certificates, "comparison payload.certificates", 2);
  payload.certificates.forEach((entry, index) => {
    assertClosedObject(entry, ["platform", "localCertificateContentAddress"], "comparison payload.certificates[" + index + "]");
    if (entry.platform !== ["darwin", "win32"][index]) throw new Error("comparison certificate platform order mismatch");
    assertContentAddress(entry.localCertificateContentAddress, "comparison payload.certificates[" + index + "].localCertificateContentAddress", Release.ADDRESS_CANONICALIZATION);
  });
  validateReleaseDigests(payload.matchedDigests, "comparison payload.matchedDigests");
  assertClosedObject(payload.suites, ["quick", "deep"], "comparison payload.suites");
  validateQuickSuites(payload.suites.quick.map((suite) => Object.assign({
    durationMs: 0,
    stdoutBytes: 0,
    stdoutSha256: Release.sha256Bytes(Buffer.alloc(0)),
    stderrBytes: 0,
    stderrSha256: Release.sha256Bytes(Buffer.alloc(0)),
    exitCode: 0
  }, suite)), "comparison payload.suites.quick");
  validateDeepSuites(payload.suites.deep.map((suite) => Object.assign({
    durationMs: 0,
    stdoutBytes: 0,
    stdoutSha256: Release.sha256Bytes(Buffer.alloc(0)),
    stderrBytes: 0,
    stderrSha256: Release.sha256Bytes(Buffer.alloc(0)),
    exitCode: 0
  }, suite)), "comparison payload.suites.deep");
  validateClaimBoundary(payload.claimBoundary, "comparison payload.claimBoundary");
  assertClosedObject(payload.historicalV1, ["classification", "interpretation"], "comparison payload.historicalV1");
  if (payload.historicalV1.classification !== Release.HISTORICAL_V1_CLASSIFICATION ||
      payload.historicalV1.interpretation !== "The historical v1 comparison does not certify any release-v2 source, artifact, evaluation, or suite surface.") {
    throw new Error("comparison payload promotes or changes the historical v1 boundary");
  }
  return { valid: true };
}

function packageComparison(payload) {
  validateComparisonPayload(payload);
  return Object.assign({}, payload, { contentAddress: Release.contentAddress(payload) });
}

function validateComparisonArtifact(artifact) {
  assertClosedObject(artifact, [
    "schema",
    "comparatorVersion",
    "comparisonStatus",
    "scope",
    "certificates",
    "matchedDigests",
    "suites",
    "claimBoundary",
    "historicalV1",
    "contentAddress"
  ], "comparison artifact");
  const payload = Object.assign({}, artifact);
  delete payload.contentAddress;
  validateComparisonPayload(payload);
  assertContentAddress(artifact.contentAddress, "comparison artifact.contentAddress", Release.ADDRESS_CANONICALIZATION);
  const computed = Release.contentAddress(payload);
  if (!sameJson(artifact.contentAddress, computed)) throw new Error("comparison artifact content address does not verify");
  return { artifact, payload, address: computed };
}

function compareCertificateFiles(darwinPath, windowsPath) {
  const darwin = readLocalCertificate(darwinPath, "Darwin");
  const windows = readLocalCertificate(windowsPath, "Windows");
  const payload = buildComparisonPayload(darwin, windows);
  return { darwin, windows, payload };
}

function writeComparison(outputPath, payload, protectedInputPaths) {
  const resolved = path.resolve(outputPath);
  const protectedPaths = new Set((protectedInputPaths || []).map((entry) => path.resolve(entry)));
  if (protectedPaths.has(resolved)) throw new Error("comparison output may not overwrite an input certificate");
  const artifact = packageComparison(payload);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  const descriptor = fs.openSync(resolved, "wx", 0o644);
  try {
    fs.writeFileSync(descriptor, JSON.stringify(artifact, null, 2) + "\n", "utf8");
    fs.fsyncSync(descriptor);
  }
  finally { fs.closeSync(descriptor); }
  return Object.assign({ path: resolved }, validateComparisonArtifact(JSON.parse(fs.readFileSync(resolved, "utf8"))));
}

function resolveExplicitPath(value, flag) {
  if (typeof value !== "string" || !value || value.startsWith("--")) throw new Error(flag + " requires one explicit path");
  return path.isAbsolute(value) ? path.normalize(value) : path.resolve(Release.REPO_ROOT, value);
}

function parseArgs(argv) {
  if (!Array.isArray(argv) || argv.length !== 6) throw new Error("use exactly --darwin PATH --windows PATH --output PATH");
  const allowed = new Set(["--darwin", "--windows", "--output"]);
  const values = {};
  for (let index = 0; index < argv.length; index += 2) {
    const flag = argv[index];
    if (!allowed.has(flag)) throw new Error("unknown comparison argument " + flag);
    if (own(values, flag)) throw new Error(flag + " may be supplied only once");
    values[flag] = resolveExplicitPath(argv[index + 1], flag);
  }
  allowed.forEach((flag) => {
    if (!own(values, flag)) throw new Error(flag + " is required");
  });
  const paths = [values["--darwin"], values["--windows"], values["--output"]];
  if (new Set(paths).size !== 3) throw new Error("Darwin, Windows, and output paths must be distinct");
  return { darwin: paths[0], windows: paths[1], output: paths[2] };
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
      quickSuiteCount: comparison.payload.suites.quick.length,
      deepSuiteCount: comparison.payload.suites.deep.length,
      u2Decision: comparison.payload.claimBoundary.u2Decision,
      physicalValidation: comparison.payload.claimBoundary.physicalValidation,
      historicalV1: comparison.payload.historicalV1.classification,
      output: written.path,
      sha256: written.address.digest
    }) + "\n");
  } catch (error) {
    process.stderr.write("Global Geometry II release-v2 certificate comparison failed: " + (error && error.message ? error.message : String(error)) + "\n");
    process.exitCode = 1;
  }
}

if (require.main === module) main();

module.exports = {
  CLAIMS_NOT_CLOSED,
  COMPARATOR_VERSION,
  COMPARISON_SCHEMA,
  COMPARISON_STATUS,
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
