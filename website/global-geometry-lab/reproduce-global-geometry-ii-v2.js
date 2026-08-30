#!/usr/bin/env node
"use strict";

/*
 * Read-only verifier for the Global Geometry II release-v2 checkpoint.
 *
 * Quick mode checks the exact source/registry/compact-artifact snapshot and
 * runs focused deterministic tests.  Deep mode additionally executes the
 * registry-frozen current-artifact validators.  Neither mode writes unless a
 * new --certificate path is explicitly supplied; certificate creation is
 * write-once.
 */

const childProcess = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const Release = require("./generate-global-geometry-ii-release-v2.js");

const VERIFIER_VERSION = "2.0.0";
const CERTIFICATE_SCHEMA = "ggii.local-reproduction-certificate/3";
const MAX_SUITE_OUTPUT_BYTES = 16 * 1024 * 1024;
const QUICK_SUITE_TIMEOUT_MS = 240000;
const LOCAL_INTERPRETATION = "This local record certifies only one release-v2 verification invocation on the observed environment. It does not make a U2 acceptance or rejection decision, prove a universality claim, establish physical validation, or prove equality with another platform.";

function sameJson(left, right) {
  return Release.canonicalStringify(left) === Release.canonicalStringify(right);
}

function isPlainObject(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function assertClosedObject(value, expectedKeys, location) {
  if (!isPlainObject(value)) throw new Error(location + " must be a plain object");
  if (!sameJson(Object.keys(value).sort(), expectedKeys.slice().sort())) {
    throw new Error(location + " has a noncanonical schema");
  }
}

function assertSha256(value, location) {
  if (typeof value !== "string" || !/^[0-9a-f]{64}$/.test(value)) throw new Error(location + " must be a lowercase SHA-256 digest");
}

function parseArgs(argv) {
  if (!Array.isArray(argv)) throw new Error("argv must be an array");
  let verify = false;
  let mode = null;
  let certificate = null;
  let manifest = Release.DEFAULT_MANIFEST;
  let indexPath = Release.DEFAULT_INDEX;
  let manifestSet = false;
  let indexSet = false;
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--verify") {
      if (verify) throw new Error("--verify may be supplied only once");
      verify = true;
      continue;
    }
    if (["--mode", "--certificate", "--manifest", "--index"].includes(token)) {
      const value = argv[index + 1];
      if (typeof value !== "string" || !value || value.startsWith("--")) throw new Error(token + " requires one explicit value");
      if (token === "--mode") {
        if (mode !== null) throw new Error("--mode may be supplied only once");
        if (value !== "quick" && value !== "deep") throw new Error("--mode must be quick or deep");
        mode = value;
      } else if (token === "--certificate") {
        if (certificate !== null) throw new Error("--certificate may be supplied only once");
        certificate = path.isAbsolute(value) ? path.normalize(value) : path.resolve(Release.REPO_ROOT, value);
      } else if (token === "--manifest") {
        if (manifestSet) throw new Error("--manifest may be supplied only once");
        manifest = path.isAbsolute(value) ? path.normalize(value) : path.resolve(Release.REPO_ROOT, value);
        Release.repoRelative(manifest, Release.REPO_ROOT);
        manifestSet = true;
      } else {
        if (indexSet) throw new Error("--index may be supplied only once");
        indexPath = path.isAbsolute(value) ? path.normalize(value) : path.resolve(Release.REPO_ROOT, value);
        Release.repoRelative(indexPath, Release.REPO_ROOT);
        indexSet = true;
      }
      index += 1;
      continue;
    }
    throw new Error("unknown release-v2 reproduction argument " + token);
  }
  if (!verify) throw new Error("--verify is required");
  if (mode === null) throw new Error("--mode quick or --mode deep is required");
  if (manifestSet !== indexSet) throw new Error("--manifest and --index must be supplied together");
  if (path.resolve(manifest) === path.resolve(indexPath)) throw new Error("manifest and index paths must be distinct");
  return { verify: true, mode, certificate, manifest, index: indexPath };
}

function verifyRawManifestLink(indexPayload, manifestArtifact, manifestRaw) {
  if (!indexPayload.manifest || indexPayload.manifest.path !== Release.repoRelative(manifestArtifact.path, Release.REPO_ROOT)) {
    throw new Error("release-v2 index manifest path does not match the selected manifest");
  }
  if (indexPayload.manifest.rawSha256 !== Release.sha256Bytes(manifestRaw) || indexPayload.manifest.rawBytes !== manifestRaw.length) {
    throw new Error("release-v2 index raw manifest address does not verify");
  }
  if (!sameJson(indexPayload.manifest.contentAddress, manifestArtifact.address)) {
    throw new Error("release-v2 index points to a different manifest content address");
  }
}

function loadReleaseMetadata(options) {
  options = options || {};
  const manifestPath = path.resolve(options.manifest || Release.DEFAULT_MANIFEST);
  const indexPath = path.resolve(options.index || Release.DEFAULT_INDEX);
  Release.repoRelative(manifestPath, Release.REPO_ROOT);
  Release.repoRelative(indexPath, Release.REPO_ROOT);
  const manifest = Release.verifyAddressedFile(manifestPath, Release.MANIFEST_SCHEMA);
  manifest.path = manifestPath;
  const index = Release.verifyAddressedFile(indexPath, Release.INDEX_SCHEMA);
  index.path = indexPath;
  if (!manifest.payload.inputRegistry || typeof manifest.payload.inputRegistry.path !== "string") {
    throw new Error("release-v2 manifest omits its input registry path");
  }
  const registryPath = path.resolve(Release.REPO_ROOT, manifest.payload.inputRegistry.path);
  const registryRecord = Release.readRegistry(registryPath);
  const currentPayload = Release.buildManifestPayload({ registryRecord });
  if (!sameJson(manifest.payload, currentPayload)) {
    throw new Error("release-v2 manifest does not match the current source/registry/compact-artifact snapshot");
  }
  const expectedIndex = Release.buildIndexPayload(manifestPath, manifest.artifact);
  if (!sameJson(index.payload, expectedIndex)) throw new Error("release-v2 index does not match the verified manifest");
  verifyRawManifestLink(index.payload, manifest, manifest.raw);
  if (manifest.payload.claimBoundary.u2Decision !== "NO_ACCEPTANCE_OR_REJECTION_CLAIM" ||
      manifest.payload.claimBoundary.universalityClaim !== "NONE" ||
      manifest.payload.claimBoundary.physicalValidation !== "NOT_RUN") {
    throw new Error("release-v2 manifest exceeds its no-decision/no-physical-validation claim boundary");
  }
  if (!manifest.payload.historicalV1 || manifest.payload.historicalV1.classification !== Release.HISTORICAL_V1_CLASSIFICATION) {
    throw new Error("release-v2 manifest fails to classify v1 as historical only");
  }
  return { manifest, index, registryRecord };
}

function verificationPaths(metadata) {
  const paths = new Set([
    metadata.manifest.path,
    metadata.index.path,
    metadata.registryRecord.path
  ]);
  metadata.manifest.payload.sourceManifest.entries.forEach((entry) => paths.add(path.join(Release.REPO_ROOT, entry.path)));
  metadata.manifest.payload.registeredArtifacts.forEach((entry) => paths.add(path.join(Release.REPO_ROOT, entry.path)));
  return Array.from(paths).map((entry) => path.resolve(entry)).sort();
}

function snapshotFiles(paths) {
  return paths.map((filePath) => {
    const stat = fs.lstatSync(filePath);
    if (!stat.isFile() || stat.isSymbolicLink()) throw new Error("release-v2 verification surface requires regular files: " + filePath);
    const digest = Release.sha256File(filePath);
    return {
      path: filePath,
      sha256: digest.sha256,
      bytes: digest.bytes,
      mode: stat.mode & 0o777,
      mtimeMs: stat.mtimeMs
    };
  });
}

function assertUnchanged(before, after) {
  if (!sameJson(before, after)) throw new Error("a release-v2 source, registry, artifact, or metadata file changed during read-only verification");
}

function suiteDefinition(entry, tier) {
  return {
    id: entry.id,
    path: entry.path,
    args: Array.isArray(entry.args) ? entry.args.slice() : [],
    tier,
    coverage: tier === "deep" ? entry.coverage : "focused-quick",
    timeoutMs: tier === "deep" ? entry.timeoutMs : QUICK_SUITE_TIMEOUT_MS
  };
}

function defaultSuiteRunner(suite) {
  const absolute = path.join(Release.REPO_ROOT, suite.path);
  const started = process.hrtime.bigint();
  const child = childProcess.spawnSync(process.execPath, [absolute].concat(suite.args), {
    cwd: Release.REPO_ROOT,
    encoding: "utf8",
    env: Object.assign({}, process.env, {
      GGII_REPRODUCTION_V2_CHILD: "1",
      GGII_REPRODUCTION_V2_TIER: suite.tier,
      NO_COLOR: "1"
    }),
    maxBuffer: MAX_SUITE_OUTPUT_BYTES,
    timeout: suite.timeoutMs,
    windowsHide: true
  });
  const durationMs = Number(process.hrtime.bigint() - started) / 1e6;
  const stdout = child.stdout || "";
  const stderr = child.stderr || "";
  if (child.error) throw new Error(suite.id + " could not run: " + child.error.message);
  if (child.signal) throw new Error(suite.id + " terminated by signal " + child.signal);
  if (child.status !== 0) {
    const detail = (stderr || stdout).slice(0, 8000);
    throw new Error(suite.id + " failed with exit code " + child.status + "\n" + detail);
  }
  return {
    id: suite.id,
    path: suite.path,
    args: suite.args.slice(),
    tier: suite.tier,
    coverage: suite.coverage,
    status: "PASS",
    exitCode: 0,
    durationMs: Number(durationMs.toFixed(3)),
    stdoutBytes: Buffer.byteLength(stdout, "utf8"),
    stdoutSha256: Release.sha256Bytes(Buffer.from(stdout, "utf8")),
    stderrBytes: Buffer.byteLength(stderr, "utf8"),
    stderrSha256: Release.sha256Bytes(Buffer.from(stderr, "utf8"))
  };
}

function environmentRecord() {
  return {
    platform: process.platform,
    architecture: process.arch,
    endianness: os.endianness(),
    nodeVersion: process.version,
    v8Version: process.versions.v8,
    uvVersion: process.versions.uv
  };
}

function releaseDigestRecord(metadata) {
  const manifestPayload = metadata.manifest.payload;
  return {
    manifestContentAddress: metadata.manifest.address,
    releaseIndexContentAddress: metadata.index.address,
    inputRegistry: Object.assign({}, manifestPayload.inputRegistry),
    sourceSnapshotSha256: Release.sha256Bytes(Buffer.from(Release.canonicalStringify(manifestPayload.sourceManifest.entries), "utf8")),
    archiveIndexBindings: {
      evaluationIndexId: manifestPayload.archiveIndexBindings.evaluationIndexId,
      evaluationIndexPath: manifestPayload.archiveIndexBindings.evaluationIndexPath,
      policy: manifestPayload.archiveIndexBindings.policy,
      bindings: manifestPayload.archiveIndexBindings.bindings.map((entry) => Object.assign({}, entry))
    },
    registeredArtifacts: manifestPayload.registeredArtifacts.map((entry) => ({
      id: entry.id,
      path: entry.path,
      role: entry.role,
      platform: entry.platform,
      rawSha256: entry.rawSha256,
      rawBytes: entry.rawBytes,
      semanticAddress: entry.semanticAddress,
      semanticReplay: entry.semanticReplay
    }))
  };
}

function certificationRecord(platform, mode) {
  return {
    interpretation: LOCAL_INTERPRETATION,
    observedPlatform: platform,
    observedPlatformIsRequiredClass: platform === "darwin" || platform === "win32",
    verificationMode: mode,
    requiredIndependentPlatforms: ["darwin", "win32"],
    crossPlatformEqualityClaim: "NOT_MADE",
    u2Decision: "NO_ACCEPTANCE_OR_REJECTION_CLAIM",
    universalityClaim: "NONE",
    physicalValidation: "NOT_RUN",
    historicalV1: Release.HISTORICAL_V1_CLASSIFICATION,
    releaseGate: mode === "deep"
      ? "OPEN_PENDING_REVIEWED_INDEPENDENT_DARWIN_AND_WIN32_DEEP_CERTIFICATES"
      : "OPEN_QUICK_MODE_IS_NOT_THE_DEEP_CROSS_PLATFORM_RELEASE_SURFACE"
  };
}

function suitesForMode(metadata, mode) {
  const quick = metadata.manifest.payload.execution.quickSuites.map((entry) => suiteDefinition(entry, "quick"));
  const deep = mode === "deep"
    ? metadata.manifest.payload.execution.deepSuites.map((entry) => suiteDefinition(entry, "deep"))
    : [];
  return { quick, deep };
}

function validateSuiteResult(result, suite) {
  if (!result || result.id !== suite.id || result.path !== suite.path || result.tier !== suite.tier ||
      result.coverage !== suite.coverage || !sameJson(result.args, suite.args) || result.status !== "PASS" || result.exitCode !== 0) {
    throw new Error("suite runner returned an invalid PASS record for " + suite.id);
  }
  return result;
}

function verifyRepository(options) {
  options = options || {};
  const mode = options.mode;
  if (mode !== "quick" && mode !== "deep") throw new Error("verifyRepository mode must be quick or deep");
  const metadata = loadReleaseMetadata({ manifest: options.manifest, index: options.index });
  const paths = verificationPaths(metadata);
  const before = snapshotFiles(paths);
  const selected = suitesForMode(metadata, mode);
  const runSuite = options.runSuite || defaultSuiteRunner;
  const quick = selected.quick.map((suite) => validateSuiteResult(runSuite(suite), suite));
  const deep = selected.deep.map((suite) => validateSuiteResult(runSuite(suite), suite));
  const after = snapshotFiles(paths);
  assertUnchanged(before, after);
  const environment = options.environment || environmentRecord();
  return {
    schema: CERTIFICATE_SCHEMA,
    verifierVersion: VERIFIER_VERSION,
    generatedAtUtc: new Date().toISOString(),
    verificationStatus: "PASS",
    verificationMode: mode,
    readOnlyVerification: "PASS_SOURCE_REGISTRY_COMPACT_ARTIFACT_AND_RELEASE_SURFACE_UNCHANGED",
    environment,
    suites: { quick, deep },
    releaseDigests: releaseDigestRecord(metadata),
    claimBoundary: Object.assign({}, metadata.manifest.payload.claimBoundary),
    certification: certificationRecord(environment.platform, mode)
  };
}

function validateCertificatePayload(payload, metadata) {
  assertClosedObject(payload, [
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
    "certification"
  ], "certificate payload");
  if (payload.schema !== CERTIFICATE_SCHEMA || payload.verifierVersion !== VERIFIER_VERSION || payload.verificationStatus !== "PASS" ||
      (payload.verificationMode !== "quick" && payload.verificationMode !== "deep") ||
      payload.readOnlyVerification !== "PASS_SOURCE_REGISTRY_COMPACT_ARTIFACT_AND_RELEASE_SURFACE_UNCHANGED") {
    throw new Error("certificate payload identity/status is invalid");
  }
  if (typeof payload.generatedAtUtc !== "string") throw new Error("certificate payload generatedAtUtc must be a string");
  const parsedTime = Date.parse(payload.generatedAtUtc);
  if (!Number.isFinite(parsedTime) || new Date(parsedTime).toISOString() !== payload.generatedAtUtc) {
    throw new Error("certificate payload generatedAtUtc is not canonical UTC ISO");
  }
  assertClosedObject(payload.environment, [
    "platform", "architecture", "endianness", "nodeVersion", "v8Version", "uvVersion"
  ], "certificate payload.environment");
  if (typeof payload.environment.platform !== "string" || !payload.environment.platform ||
      typeof payload.environment.architecture !== "string" || !payload.environment.architecture) {
    throw new Error("certificate payload environment is invalid");
  }
  assertClosedObject(payload.suites, ["quick", "deep"], "certificate payload.suites");
  const expectedSuites = suitesForMode(metadata, payload.verificationMode);
  ["quick", "deep"].forEach((tier) => {
    const actual = payload.suites[tier];
    const expected = expectedSuites[tier];
    if (!Array.isArray(actual) || actual.length !== expected.length) throw new Error("certificate payload " + tier + " suite count mismatch");
    actual.forEach((result, index) => {
      assertClosedObject(result, [
        "id", "path", "args", "tier", "coverage", "status", "exitCode", "durationMs",
        "stdoutBytes", "stdoutSha256", "stderrBytes", "stderrSha256"
      ], "certificate payload.suites." + tier + "[" + index + "]");
      const definition = expected[index];
      if (result.id !== definition.id || result.path !== definition.path || !sameJson(result.args, definition.args) ||
          result.tier !== definition.tier || result.coverage !== definition.coverage || result.status !== "PASS" || result.exitCode !== 0) {
        throw new Error("certificate payload suite identity/PASS mismatch for " + definition.id);
      }
      if (typeof result.durationMs !== "number" || !Number.isFinite(result.durationMs) || result.durationMs < 0 ||
          !Number.isSafeInteger(result.stdoutBytes) || result.stdoutBytes < 0 ||
          !Number.isSafeInteger(result.stderrBytes) || result.stderrBytes < 0) {
        throw new Error("certificate payload suite metrics are invalid for " + definition.id);
      }
      assertSha256(result.stdoutSha256, "certificate payload suite stdoutSha256");
      assertSha256(result.stderrSha256, "certificate payload suite stderrSha256");
    });
  });
  if (!sameJson(payload.releaseDigests, releaseDigestRecord(metadata))) throw new Error("certificate payload release digests do not match current v2 metadata");
  if (!sameJson(payload.claimBoundary, metadata.manifest.payload.claimBoundary)) throw new Error("certificate payload claim boundary does not match current v2 metadata");
  if (!sameJson(payload.certification, certificationRecord(payload.environment.platform, payload.verificationMode))) {
    throw new Error("certificate payload certification changes the closed local claim boundary");
  }
  return { valid: true };
}

function protectedOutputPaths(metadata) {
  return new Set(verificationPaths(metadata).map((entry) => path.resolve(entry)));
}

function writeCertificate(output, payload, options) {
  options = options || {};
  const metadata = loadReleaseMetadata({ manifest: options.manifest, index: options.index });
  validateCertificatePayload(payload, metadata);
  const resolved = path.resolve(output);
  if (protectedOutputPaths(metadata).has(resolved)) throw new Error("certificate output may not overwrite the release-v2 verification surface");
  const addressed = Object.assign({}, payload, { contentAddress: Release.contentAddress(payload) });
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  const descriptor = fs.openSync(resolved, "wx", 0o644);
  try {
    fs.writeFileSync(descriptor, JSON.stringify(addressed, null, 2) + "\n", "utf8");
    fs.fsyncSync(descriptor);
  }
  finally { fs.closeSync(descriptor); }
  const replay = JSON.parse(fs.readFileSync(resolved, "utf8"));
  const supplied = replay.contentAddress;
  delete replay.contentAddress;
  const computed = Release.contentAddress(replay);
  if (!sameJson(supplied, computed)) throw new Error("written release-v2 certificate failed its content-address check");
  return { path: resolved, address: computed };
}

function main() {
  try {
    const args = parseArgs(process.argv.slice(2));
    const result = verifyRepository({ mode: args.mode, manifest: args.manifest, index: args.index });
    const certificate = args.certificate
      ? writeCertificate(args.certificate, result, { manifest: args.manifest, index: args.index })
      : null;
    process.stdout.write(JSON.stringify({
      status: result.verificationStatus,
      mode: result.verificationMode,
      readOnly: result.readOnlyVerification,
      platform: result.environment.platform,
      quickSuiteCount: result.suites.quick.length,
      deepSuiteCount: result.suites.deep.length,
      registeredArtifactCount: result.releaseDigests.registeredArtifacts.length,
      u2Decision: result.certification.u2Decision,
      universalityClaim: result.certification.universalityClaim,
      physicalValidation: result.certification.physicalValidation,
      historicalV1: result.certification.historicalV1,
      releaseGate: result.certification.releaseGate,
      certificate: certificate ? { output: certificate.path, sha256: certificate.address.digest } : null
    }) + "\n");
  } catch (error) {
    process.stderr.write("Global Geometry II release-v2 reproduction failed: " + (error && error.message ? error.message : String(error)) + "\n");
    process.exitCode = 1;
  }
}

if (require.main === module) main();

module.exports = {
  CERTIFICATE_SCHEMA,
  LOCAL_INTERPRETATION,
  MAX_SUITE_OUTPUT_BYTES,
  QUICK_SUITE_TIMEOUT_MS,
  VERIFIER_VERSION,
  assertUnchanged,
  certificationRecord,
  defaultSuiteRunner,
  environmentRecord,
  loadReleaseMetadata,
  parseArgs,
  protectedOutputPaths,
  releaseDigestRecord,
  snapshotFiles,
  suitesForMode,
  verificationPaths,
  validateCertificatePayload,
  verifyRepository,
  writeCertificate
};
