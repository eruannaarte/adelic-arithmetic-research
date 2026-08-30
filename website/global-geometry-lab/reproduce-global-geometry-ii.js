#!/usr/bin/env node
"use strict";

/*
 * Read-only clean-room verifier for Global Geometry II.
 *
 * `--verify` reads the checked-out sources, artifacts, and release metadata,
 * then runs every focused suite in a child Node process.  It writes nothing.
 * `--certificate PATH` is the sole opt-in write: a new file is created only
 * after verification passes, and an existing file is never replaced.
 */

const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");
const childProcess = require("child_process");
const Release = require("./generate-global-geometry-ii-release.js");

const VERIFIER_VERSION = "1.0.0-alpha.2";
const CERTIFICATE_SCHEMA = "ggii.local-reproduction-certificate/2";
const LOCAL_REPLAY_OBSERVATIONS_SCHEMA = "ggii.local-replay-observations/1";
const MAX_SUITE_OUTPUT_BYTES = 16 * 1024 * 1024;
const SUITE_TIMEOUT_MS = 240000;

function parseArgs(argv) {
  if (!Array.isArray(argv)) throw new Error("argv must be an array");
  let verify = false;
  let certificate = null;
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--verify") {
      if (verify) throw new Error("--verify may be supplied only once");
      verify = true;
    } else if (token === "--certificate") {
      if (certificate !== null) throw new Error("--certificate may be supplied only once");
      const value = argv[index + 1];
      if (typeof value !== "string" || !value || value.startsWith("--")) {
        throw new Error("--certificate requires one explicit file path");
      }
      certificate = path.isAbsolute(value) ? path.normalize(value) : path.resolve(Release.REPO_ROOT, value);
      index += 1;
    } else {
      throw new Error("unknown reproduction argument " + token);
    }
  }
  if (!verify) throw new Error("--verify is required");
  if (argv.length !== (certificate === null ? 1 : 3)) throw new Error("ambiguous reproduction arguments");
  return { verify: true, certificate };
}

function addressEquals(left, right) {
  return Release.canonicalStringify(left) === Release.canonicalStringify(right);
}

function loadReleaseMetadata() {
  const manifest = Release.verifyAddressedFile(Release.DEFAULT_MANIFEST, Release.MANIFEST_SCHEMA);
  const index = Release.verifyAddressedFile(Release.DEFAULT_INDEX, Release.INDEX_SCHEMA);
  const currentPayload = Release.buildManifestPayload();
  if (Release.canonicalStringify(manifest.payload) !== Release.canonicalStringify(currentPayload)) {
    throw new Error("reproducibility manifest does not match the current source/artifact snapshot; regenerate it explicitly");
  }
  const expectedIndex = Release.buildIndexPayload(Release.DEFAULT_MANIFEST, manifest.artifact);
  if (Release.canonicalStringify(index.payload) !== Release.canonicalStringify(expectedIndex)) {
    throw new Error("release index does not match the verified manifest");
  }
  if (!addressEquals(index.payload.manifest.contentAddress, manifest.address)) {
    throw new Error("release index points to a different manifest address");
  }
  const manifestRaw = Release.sha256File(Release.DEFAULT_MANIFEST);
  if (index.payload.manifest.rawSha256 !== manifestRaw.sha256 || index.payload.manifest.rawBytes !== manifestRaw.bytes) {
    throw new Error("release index raw-file address does not match the manifest bytes");
  }
  if (manifest.payload.certificationPolicy.crossPlatformEqualityClaim !== "NOT_MADE") {
    throw new Error("manifest must not claim cross-platform equality");
  }
  if (manifest.payload.certificationPolicy.windowsCertificate !== "REQUIRED_EXTERNAL_INPUT_NOT_BUNDLED_OR_SIMULATED") {
    throw new Error("manifest must keep the Windows certificate as a required external input that is not bundled or simulated");
  }
  if (manifest.payload.certificationPolicy.externalComparisonRecord !== Release.EXTERNAL_COMPARISON_RECORD ||
      manifest.payload.certificationPolicy.releaseGate !== "STATUS_DELEGATED_TO_EXTERNAL_COMPARISON_RECORD") {
    throw new Error("manifest must delegate cross-platform release status to the declared external comparison record");
  }
  const indexStatus = index.payload.certificationStatus;
  if (!indexStatus || indexStatus.crossPlatformEqualityClaim !== "NOT_MADE" ||
      indexStatus.windowsCertificate !== "EXTERNAL_NOT_BUNDLED_IN_INDEX" ||
      indexStatus.externalComparisonRecord !== Release.EXTERNAL_COMPARISON_RECORD ||
      indexStatus.releaseGate !== "STATUS_DELEGATED_TO_EXTERNAL_COMPARISON_RECORD") {
    throw new Error("release index must delegate cross-platform status to the external comparison record without bundling it");
  }
  return { manifest, index };
}

function verificationPaths(metadata) {
  const paths = new Set([
    Release.DEFAULT_MANIFEST,
    Release.DEFAULT_INDEX
  ]);
  metadata.manifest.payload.sourceManifest.entries.forEach((entry) => paths.add(path.join(Release.REPO_ROOT, entry.path)));
  metadata.manifest.payload.scientificArtifacts.forEach((entry) => paths.add(path.join(Release.REPO_ROOT, entry.path)));
  return Array.from(paths).sort();
}

function snapshotFiles(paths) {
  return paths.map((filePath) => {
    const stat = fs.lstatSync(filePath);
    if (!stat.isFile() || stat.isSymbolicLink()) throw new Error("verification surface requires regular files: " + filePath);
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
  if (Release.canonicalStringify(before) !== Release.canonicalStringify(after)) {
    throw new Error("a source, artifact, or release-metadata file changed during read-only verification");
  }
}

function defaultSuiteRunner(suite) {
  const absolute = path.join(Release.REPO_ROOT, suite.path);
  const started = process.hrtime.bigint();
  const child = childProcess.spawnSync(process.execPath, [absolute], {
    cwd: Release.REPO_ROOT,
    encoding: "utf8",
    env: Object.assign({}, process.env, {
      GGII_REPRODUCTION_CHILD: "1",
      NO_COLOR: "1"
    }),
    maxBuffer: MAX_SUITE_OUTPUT_BYTES,
    timeout: SUITE_TIMEOUT_MS,
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
    status: "PASS",
    exitCode: child.status,
    durationMs: Number(durationMs.toFixed(3)),
    stdoutBytes: Buffer.byteLength(stdout, "utf8"),
    stdoutSha256: Release.sha256Bytes(Buffer.from(stdout, "utf8")),
    stderrBytes: Buffer.byteLength(stderr, "utf8"),
    stderrSha256: Release.sha256Bytes(Buffer.from(stderr, "utf8"))
  };
}

function environmentRecord() {
  const cpus = os.cpus();
  return {
    platform: process.platform,
    architecture: process.arch,
    operatingSystemRelease: os.release(),
    endianness: os.endianness(),
    nodeVersion: process.version,
    v8Version: process.versions.v8,
    uvVersion: process.versions.uv,
    logicalCpuCount: cpus.length,
    cpuModel: cpus.length ? cpus[0].model : "unreported",
    totalMemoryBytes: os.totalmem()
  };
}

function scientificDigestRecord(metadata) {
  return {
    manifestContentAddress: metadata.manifest.address,
    releaseIndexContentAddress: metadata.index.address,
    sourceSnapshotSha256: Release.sha256Bytes(Buffer.from(Release.canonicalStringify(metadata.manifest.payload.sourceManifest.entries), "utf8")),
    artifacts: metadata.manifest.payload.scientificArtifacts.map((entry) => ({
      id: entry.id,
      schema: entry.schema,
      rawSha256: entry.rawSha256,
      semanticAddress: entry.semanticAddress
    })),
    reproductionResources: metadata.manifest.payload.reproductionResources.map((entry) => ({
      id: entry.id,
      manifestPath: entry.manifestPath,
      rawSha256: entry.rawSha256,
      semanticAddress: entry.semanticAddress,
      physicalValidation: entry.physicalValidation
    }))
  };
}

function certificationRecord(platform) {
  const isWindows = platform === "win32";
  const isDarwin = platform === "darwin";
  return {
    interpretation: "This is one local execution record. It does not prove equality with any other machine, operating system, or certificate.",
    observedPlatform: platform,
    observedPlatformIsRequiredClass: isWindows || isDarwin,
    requiredIndependentPlatforms: ["darwin", "win32"],
    crossPlatformEqualityClaim: "NOT_MADE",
    windowsCertificate: isWindows
      ? "THIS_RECORD_IS_A_LOCAL_WINDOWS_CANDIDATE_PENDING_INDEPENDENT_REVIEW"
      : "ABSENT_REQUIRED_INPUT_NOT_SIMULATED",
    releaseGate: "OPEN_PENDING_REVIEWED_INDEPENDENT_DARWIN_AND_WIN32_CERTIFICATES"
  };
}

function exactObjectKeys(value, expected, label, errors) {
  if (!value || typeof value !== "object" || Array.isArray(value) || Object.getPrototypeOf(value) !== Object.prototype) {
    errors.push(label + " must be a plain object");
    return false;
  }
  const actual = Object.keys(value).sort();
  const wanted = expected.slice().sort();
  if (Release.canonicalStringify(actual) !== Release.canonicalStringify(wanted)) {
    errors.push(label + " keys must be exactly [" + wanted.join(", ") + "]");
    return false;
  }
  return true;
}

function buildLocalReplayObservations(options) {
  options = options || {};
  const atlasDefinition = Release.ARTIFACT_DEFINITIONS.find((definition) => definition.id === "atlas-pilot-v1");
  if (!atlasDefinition) throw new Error("atlas-pilot-v1 is not registered for local replay observation");
  let committedPayload = options.committedPayload;
  if (!committedPayload) {
    const artifact = JSON.parse(fs.readFileSync(path.join(Release.REPO_ROOT, atlasDefinition.path), "utf8"));
    const suppliedAddress = artifact.contentAddress;
    committedPayload = Object.assign({}, artifact);
    delete committedPayload.contentAddress;
    const computedAddress = atlasDefinition.generator.contentAddress(committedPayload);
    if (!suppliedAddress || !addressEquals(suppliedAddress, computedAddress)) {
      throw new Error("committed atlas artifact content address failed before local replay observation");
    }
  }
  const replayPayload = options.replayPayload || atlasDefinition.generator.buildPayload();
  const report = Release.compareAtlasCrossPlatformReplay(committedPayload, replayPayload);
  if (!report.valid) throw new Error("local atlas replay observation failed: " + report.errors.join("; "));
  const summary = report.summary;
  const observation = {
    schema: LOCAL_REPLAY_OBSERVATIONS_SCHEMA,
    atlas: {
      policyId: report.policy.id,
      continuousTolerance: {
        absolute: report.policy.continuousTolerance.absolute,
        relative: report.policy.continuousTolerance.relative,
        formula: report.policy.continuousTolerance.formula
      },
      pilotValidation: {
        committed: report.pilotValidation.committed.valid ? "PASS" : "FAIL",
        replay: report.pilotValidation.replay.valid ? "PASS" : "FAIL"
      },
      exactComparisonCounts: {
        objects: summary.objectsCompared,
        arrays: summary.arraysCompared,
        exactScalars: summary.exactScalarsCompared,
        exactIntegerNumbers: summary.exactIntegerNumbersCompared
      },
      continuousComparisonCounts: {
        numbers: summary.continuousNumbersCompared,
        differences: summary.continuousDifferences,
        toleratedDifferences: summary.toleratedContinuousDifferences
      },
      mismatchCount: summary.mismatchCount,
      derivedFieldCounts: {
        comparedInternallyOnly: summary.derivedStringsComparedInternallyOnly,
        differences: summary.derivedStringDifferences
      },
      maxima: {
        absoluteDifference: {
          value: summary.maxAbsoluteDifference.value,
          path: summary.maxAbsoluteDifference.path
        },
        scaledRelativeDifference: {
          value: summary.maxScaledRelativeDifference.value,
          path: summary.maxScaledRelativeDifference.path
        },
        toleranceFraction: {
          value: summary.maxToleranceFraction.value,
          path: summary.maxToleranceFraction.path
        }
      }
    }
  };
  const validation = validateLocalReplayObservations(observation);
  if (!validation.valid) throw new Error("constructed local replay observation is invalid: " + validation.errors.join("; "));
  return observation;
}

function validateLocalReplayObservations(input) {
  const errors = [];
  if (!exactObjectKeys(input, ["schema", "atlas"], "localReplayObservations", errors)) return { valid: false, errors };
  if (input.schema !== LOCAL_REPLAY_OBSERVATIONS_SCHEMA) errors.push("localReplayObservations schema mismatch");
  const atlas = input.atlas;
  if (!exactObjectKeys(atlas, [
    "policyId", "continuousTolerance", "pilotValidation", "exactComparisonCounts",
    "continuousComparisonCounts", "mismatchCount", "derivedFieldCounts", "maxima"
  ], "localReplayObservations.atlas", errors)) return { valid: false, errors };
  const registeredAtlas = Release.ARTIFACT_DEFINITIONS.find((definition) => definition.id === "atlas-pilot-v1");
  if (!registeredAtlas || atlas.policyId !== registeredAtlas.replayPolicy.id) errors.push("atlas policyId is not the registered replay policy");

  if (exactObjectKeys(atlas.continuousTolerance, ["absolute", "relative", "formula"], "continuousTolerance", errors)) {
    if (atlas.continuousTolerance.absolute !== Release.ATLAS_ABSOLUTE_TOLERANCE ||
        atlas.continuousTolerance.relative !== Release.ATLAS_RELATIVE_TOLERANCE ||
        atlas.continuousTolerance.formula !== "|a-b| <= 1e-12 + 1e-12*max(1,|a|,|b|)") {
      errors.push("continuousTolerance does not match the registered atlas policy");
    }
  }
  if (exactObjectKeys(atlas.pilotValidation, ["committed", "replay"], "pilotValidation", errors)) {
    if (atlas.pilotValidation.committed !== "PASS" || atlas.pilotValidation.replay !== "PASS") {
      errors.push("both independent pilot validations must be PASS");
    }
  }

  function validateCounts(value, keys, label) {
    if (!exactObjectKeys(value, keys, label, errors)) return;
    keys.forEach((key) => {
      if (!Number.isSafeInteger(value[key]) || value[key] < 0) errors.push(label + "." + key + " must be a nonnegative safe integer");
    });
  }
  validateCounts(atlas.exactComparisonCounts, ["objects", "arrays", "exactScalars", "exactIntegerNumbers"], "exactComparisonCounts");
  validateCounts(atlas.continuousComparisonCounts, ["numbers", "differences", "toleratedDifferences"], "continuousComparisonCounts");
  validateCounts(atlas.derivedFieldCounts, ["comparedInternallyOnly", "differences"], "derivedFieldCounts");
  if (atlas.continuousComparisonCounts &&
      (atlas.continuousComparisonCounts.differences > atlas.continuousComparisonCounts.numbers ||
       atlas.continuousComparisonCounts.toleratedDifferences !== atlas.continuousComparisonCounts.differences)) {
    errors.push("all and only observed continuous differences must be tolerated in a passing local replay");
  }
  if (atlas.mismatchCount !== 0) errors.push("mismatchCount must be zero");
  if (atlas.derivedFieldCounts &&
      (atlas.derivedFieldCounts.comparedInternallyOnly !== Release.ATLAS_DERIVED_DIGEST_PATHS.length ||
       atlas.derivedFieldCounts.differences > atlas.derivedFieldCounts.comparedInternallyOnly)) {
    errors.push("derivedFieldCounts does not match the closed atlas policy");
  }

  if (exactObjectKeys(atlas.maxima, ["absoluteDifference", "scaledRelativeDifference", "toleranceFraction"], "maxima", errors)) {
    ["absoluteDifference", "scaledRelativeDifference", "toleranceFraction"].forEach((key) => {
      const maximum = atlas.maxima[key];
      if (!exactObjectKeys(maximum, ["value", "path"], "maxima." + key, errors)) return;
      if (typeof maximum.value !== "number" || !Number.isFinite(maximum.value) || maximum.value < 0) {
        errors.push("maxima." + key + ".value must be finite and nonnegative");
      }
      if (!(maximum.path === null || (typeof maximum.path === "string" && maximum.path.startsWith("root.")))) {
        errors.push("maxima." + key + ".path must be null or a rooted atlas path");
      }
      if (maximum.value === 0 && maximum.path !== null) errors.push("zero maxima must use a null path");
      if (maximum.value > 0 && maximum.path === null) errors.push("positive maxima require a path");
    });
    if (atlas.maxima.toleranceFraction && atlas.maxima.toleranceFraction.value > 1) {
      errors.push("passing local replay toleranceFraction may not exceed one");
    }
  }
  return { valid: errors.length === 0, errors };
}

function verifyRepository(options) {
  options = options || {};
  const metadata = loadReleaseMetadata();
  const surfacePaths = verificationPaths(metadata);
  const before = snapshotFiles(surfacePaths);
  const runSuite = options.runSuite || defaultSuiteRunner;
  const suiteResults = metadata.manifest.payload.execution.suites.map((suite) => {
    const result = runSuite(suite);
    if (!result || result.status !== "PASS" || result.id !== suite.id || result.path !== suite.path) {
      throw new Error("suite runner returned an invalid PASS record for " + suite.id);
    }
    return result;
  });
  const localReplayObservations = buildLocalReplayObservations(options.localReplayObservationInputs);
  const after = snapshotFiles(surfacePaths);
  assertUnchanged(before, after);
  const environment = options.environment || environmentRecord();
  return {
    schema: CERTIFICATE_SCHEMA,
    verifierVersion: VERIFIER_VERSION,
    generatedAtUtc: new Date().toISOString(),
    verificationStatus: "PASS",
    readOnlyVerification: "PASS_SOURCE_ARTIFACT_AND_RELEASE_SURFACE_UNCHANGED",
    environment,
    suites: suiteResults,
    scientificDigests: scientificDigestRecord(metadata),
    localReplayObservations,
    certification: certificationRecord(environment.platform)
  };
}

function protectedOutputPaths(metadata) {
  return new Set(verificationPaths(metadata).map((entry) => path.resolve(entry)));
}

function writeCertificate(output, payload) {
  const metadata = loadReleaseMetadata();
  if (!payload || payload.schema !== CERTIFICATE_SCHEMA || payload.verifierVersion !== VERIFIER_VERSION) {
    throw new Error("certificate payload does not use the current closed schema/verifier version");
  }
  const observationValidation = validateLocalReplayObservations(payload.localReplayObservations);
  if (!observationValidation.valid) {
    throw new Error("certificate localReplayObservations are invalid: " + observationValidation.errors.join("; "));
  }
  const resolved = path.resolve(output);
  if (protectedOutputPaths(metadata).has(resolved)) {
    throw new Error("certificate output may not overwrite a source, artifact, manifest, or release-index file");
  }
  const addressed = Object.assign({}, payload, { contentAddress: Release.contentAddress(payload) });
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  const descriptor = fs.openSync(resolved, "wx", 0o644);
  try {
    fs.writeFileSync(descriptor, JSON.stringify(addressed, null, 2) + "\n", "utf8");
  } finally {
    fs.closeSync(descriptor);
  }
  const replay = JSON.parse(fs.readFileSync(resolved, "utf8"));
  const supplied = replay.contentAddress;
  delete replay.contentAddress;
  const computed = Release.contentAddress(replay);
  if (!addressEquals(supplied, computed)) throw new Error("written certificate failed its content-address check");
  return { path: resolved, address: computed };
}

function main() {
  try {
    const args = parseArgs(process.argv.slice(2));
    const result = verifyRepository();
    const certificate = args.certificate ? writeCertificate(args.certificate, result) : null;
    process.stdout.write(JSON.stringify({
      status: result.verificationStatus,
      readOnly: result.readOnlyVerification,
      platform: result.environment.platform,
      suiteCount: result.suites.length,
      manifestSha256: result.scientificDigests.manifestContentAddress.digest,
      scientificArtifacts: result.scientificDigests.artifacts.map((entry) => ({ id: entry.id, sha256: entry.semanticAddress.digest })),
      reproductionResources: result.scientificDigests.reproductionResources.map((entry) => ({ id: entry.id, sha256: entry.semanticAddress.digest })),
      crossPlatformEqualityClaim: result.certification.crossPlatformEqualityClaim,
      windowsCertificate: result.certification.windowsCertificate,
      releaseGate: result.certification.releaseGate,
      certificate: certificate ? { output: certificate.path, sha256: certificate.address.digest } : null
    }) + "\n");
  } catch (error) {
    process.stderr.write("Global Geometry II reproduction failed: " + (error && error.message ? error.message : String(error)) + "\n");
    process.exitCode = 1;
  }
}

if (require.main === module) main();

module.exports = {
  CERTIFICATE_SCHEMA,
  LOCAL_REPLAY_OBSERVATIONS_SCHEMA,
  MAX_SUITE_OUTPUT_BYTES,
  SUITE_TIMEOUT_MS,
  VERIFIER_VERSION,
  assertUnchanged,
  buildLocalReplayObservations,
  certificationRecord,
  defaultSuiteRunner,
  environmentRecord,
  loadReleaseMetadata,
  parseArgs,
  scientificDigestRecord,
  snapshotFiles,
  validateLocalReplayObservations,
  verificationPaths,
  verifyRepository,
  writeCertificate
};
