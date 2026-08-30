#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const childProcess = require("child_process");
const { performance } = require("perf_hooks");
const V3 = require("./global-geometry-ii-u2-screening-execution-v3.js");

function relativePath(absolute) { return path.relative(V3.ROOT, absolute).split(path.sep).join("/"); }
function padChunk(index) { return String(index).padStart(4, "0"); }

function parseArgs(argv) {
  const options = { platformLabel: process.platform === "darwin" ? "macos" : process.platform, sourceBoundary: path.join(V3.ROOT, "artifacts/global-geometry-ii/u2/screening/screening-v3/source-boundary-v3.json"), sourceMode: null, sourceBoundaryFileSha256: null, sourceBoundarySemanticSha256: null, resume: false, validateOnly: false, writerPreflightOnly: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--platform-label" && argv[index + 1]) options.platformLabel = argv[++index];
    else if (arg === "--source-boundary" && argv[index + 1]) options.sourceBoundary = path.resolve(argv[++index]);
    else if (arg === "--source-mode" && argv[index + 1]) options.sourceMode = argv[++index];
    else if (arg === "--source-boundary-file-sha256" && argv[index + 1]) options.sourceBoundaryFileSha256 = argv[++index];
    else if (arg === "--source-boundary-semantic-sha256" && argv[index + 1]) options.sourceBoundarySemanticSha256 = argv[++index];
    else if (arg === "--resume") options.resume = true;
    else if (arg === "--validate-only") options.validateOnly = true;
    else if (arg === "--writer-preflight-only") options.writerPreflightOnly = true;
    else throw new Error("usage: run-global-geometry-ii-u2-screening-execution-v3.js --source-mode git|portable --source-boundary-file-sha256 HEX --source-boundary-semantic-sha256 HEX [--source-boundary path] [--platform-label label] [--writer-preflight-only|--resume|--validate-only]");
  }
  if (!/^[a-z0-9_-]{1,32}$/.test(options.platformLabel)) throw new Error("platform label must match [a-z0-9_-]{1,32}");
  if (options.sourceMode !== "git" && options.sourceMode !== "portable") throw new Error("--source-mode must explicitly be git or portable");
  if (!/^[0-9a-f]{64}$/.test(options.sourceBoundaryFileSha256 || "") || !/^[0-9a-f]{64}$/.test(options.sourceBoundarySemanticSha256 || "")) throw new Error("both exact source-boundary SHA-256 pins are required");
  if ([options.resume, options.validateOnly, options.writerPreflightOnly].filter(Boolean).length > 1) throw new Error("--writer-preflight-only, --resume, and --validate-only are mutually exclusive");
  return options;
}

function pathsFor(label) {
  const directory = path.join(V3.ROOT, "artifacts/global-geometry-ii/u2/screening/screening-v3", label), chunks = path.join(directory, "chunks");
  return {
    directory: directory,
    chunks: chunks,
    raw: path.join(directory, "screening-raw-v3.jsonl"),
    summary: path.join(directory, "screening-summary-envelope-v3.json"),
    runtime: path.join(directory, "screening-runtime-v3.json"),
    checkpointManifest: path.join(directory, "screening-checkpoint-manifest-v3.json"),
    writerCapability: path.join(directory, "writer-capability-v3.json")
  };
}

function chunkPaths(paths, index) {
  const stem = "chunk-" + padChunk(index);
  return { chunk: path.join(paths.chunks, stem + ".jsonl"), certificate: path.join(paths.chunks, stem + ".certificate.json") };
}

function fsyncDirectoryPortable(directory, adapters) {
  const platform = adapters && adapters.platform ? adapters.platform : process.platform;
  if (platform === "win32") return { status: "DIRECTORY_BARRIER_UNAVAILABLE_WIN32", attempted: false, required: false };
  const open = adapters && adapters.openSync ? adapters.openSync : fs.openSync, sync = adapters && adapters.fsyncSync ? adapters.fsyncSync : fs.fsyncSync, close = adapters && adapters.closeSync ? adapters.closeSync : fs.closeSync;
  const descriptor = open(directory, "r");
  try { sync(descriptor); } finally { close(descriptor); }
  return { status: "DIRECTORY_FSYNC_COMPLETED", attempted: true, required: true };
}

function durableWriteNoReplace(output, bytes, adapters) {
  if (!Buffer.isBuffer(bytes)) throw new Error("durable write requires Buffer bytes");
  const io = Object.assign({
    existsSync: fs.existsSync, mkdirSync: fs.mkdirSync, openSync: fs.openSync, writeSync: fs.writeSync,
    fsyncSync: fs.fsyncSync, closeSync: fs.closeSync, linkSync: fs.linkSync,
    readFileSync: fs.readFileSync, unlinkSync: fs.unlinkSync, platform: process.platform
  }, adapters || {});
  if (io.existsSync(output)) throw new Error("refusing to overwrite existing v3 artifact: " + output);
  io.mkdirSync(path.dirname(output), { recursive: true });
  const temporary = output + ".v3-exclusive-temp";
  if (io.existsSync(temporary)) throw new Error("v3 temporary-file collision refuses write: " + temporary);
  let descriptor = null, linked = false, finalDescriptor = null, directoryAfterLink = null, directoryAfterUnlink = null;
  try {
    descriptor = io.openSync(temporary, "wx+");
    let offset = 0;
    while (offset < bytes.length) offset += io.writeSync(descriptor, bytes, offset, bytes.length - offset);
    io.fsyncSync(descriptor);
    io.linkSync(temporary, output); linked = true;
    io.fsyncSync(descriptor);
    finalDescriptor = io.openSync(output, "r+");
    io.fsyncSync(finalDescriptor);
    io.closeSync(finalDescriptor); finalDescriptor = null;
    if (!io.readFileSync(output).equals(bytes)) throw new Error("v3 exact final-byte postflight mismatch: " + output);
    directoryAfterLink = fsyncDirectoryPortable(path.dirname(output), io);
  } finally {
    if (finalDescriptor !== null) io.closeSync(finalDescriptor);
    if (descriptor !== null) io.closeSync(descriptor);
    if (io.existsSync(temporary)) {
      io.unlinkSync(temporary);
      directoryAfterUnlink = fsyncDirectoryPortable(path.dirname(output), io);
    }
  }
  if (!linked) throw new Error("v3 final hard link was not published");
  return {
    status: "CREATED_EXCLUSIVE_HARDLINK_FSYNC_POSTFLIGHT",
    temporaryHandleMode: "wx+",
    finalHandleMode: "r+",
    originalWritableHandleFsyncCount: 2,
    finalWritableHandleFsyncCount: 1,
    exactBytePostflight: true,
    directoryAfterLink: directoryAfterLink,
    directoryAfterTempUnlink: directoryAfterUnlink
  };
}

function gitExecutableAvailable(detector) {
  if (detector) return detector() === true;
  const result = childProcess.spawnSync("git", ["--version"], { cwd: V3.ROOT, stdio: "ignore" });
  if (result.error && result.error.code === "ENOENT") return false;
  return true;
}

function assertSourceModePolicy(mode, detector) {
  const available = gitExecutableAvailable(detector);
  if (mode === "portable" && available) throw new Error("portable source mode is refused because Git is available; Git failure never authorizes portable fallback");
  return { gitExecutableAvailable: available, selectedMode: mode };
}

function loadSource(options, adapters) {
  const bytes = (adapters && adapters.readSourceBoundary ? adapters.readSourceBoundary : fs.readFileSync)(options.sourceBoundary), pins = { fileSha256: options.sourceBoundaryFileSha256, semanticSha256: options.sourceBoundarySemanticSha256 };
  const source = V3.sourceBinding(bytes, options.sourceMode, pins, adapters && adapters.sourceAdapters, relativePath(options.sourceBoundary));
  return { bytes: bytes, source: source, artifact: JSON.parse(bytes.toString("utf8")), pins: pins };
}

function resolveHostIdentity(supplied) {
  const identity = supplied || { hostname: os.hostname(), platform: process.platform, arch: process.arch };
  if (!identity || typeof identity.hostname !== "string" || !identity.hostname || typeof identity.platform !== "string" || !identity.platform || typeof identity.arch !== "string" || !identity.arch) throw new Error("host identity requires nonempty hostname, platform, and arch");
  return { hostname: identity.hostname, platform: identity.platform, arch: identity.arch };
}

function buildRunLock(platformLabel, source, operation, runtime) {
  const effective = runtime || {}, payload = {
    schema: "gg.u2.screening.run-lock/3", executionVersion: V3.EXECUTION_VERSION, platformLabel: platformLabel,
    operation: operation, pid: effective.pid === undefined ? process.pid : effective.pid,
    creatorHost: resolveHostIdentity(effective.hostIdentity), sourceBoundary: V3.clone(source), startedAt: effective.startedAt || new Date().toISOString()
  };
  payload.lockToken = V3.sha256JSON(payload);
  return { payload: payload, bytes: V3.serializeJsonArtifact(payload) };
}

function validateRunLockBytes(bytes, platformLabel, source) {
  const report = V3.validateJsonArtifactBytes(bytes), errors = report.errors.slice(), artifact = report.artifact;
  if (!errors.length) {
    if (artifact.schema !== "gg.u2.screening.run-lock/3" || artifact.executionVersion !== V3.EXECUTION_VERSION) errors.push("v3 run lock schema mismatch");
    if (artifact.platformLabel !== platformLabel) errors.push("v3 run lock platform mismatch");
    if (V3.canonicalStringify(artifact.sourceBoundary) !== V3.canonicalStringify(source)) errors.push("v3 run lock source-boundary mismatch");
    if (!["fresh", "resume", "validate-only", "writer-preflight-only"].includes(artifact.operation)) errors.push("v3 run lock operation invalid");
    if (!Number.isSafeInteger(artifact.pid) || artifact.pid <= 0) errors.push("v3 run lock PID invalid");
    try { if (V3.canonicalStringify(artifact.creatorHost) !== V3.canonicalStringify(resolveHostIdentity(artifact.creatorHost))) errors.push("v3 run lock creator host contains unexpected fields"); } catch (error) { errors.push(error.message); }
    if (typeof artifact.startedAt !== "string" || Number.isNaN(Date.parse(artifact.startedAt))) errors.push("v3 run lock start time invalid");
    const payload = V3.clone(artifact), token = payload.lockToken; delete payload.lockToken;
    if (!/^[0-9a-f]{64}$/.test(token || "") || token !== V3.sha256JSON(payload)) errors.push("v3 run lock token mismatch");
  }
  return { valid: errors.length === 0, errors: errors, artifact: artifact };
}

function probePid(pid, adapter) {
  if (adapter) {
    const result = adapter(pid);
    if (!result || !["alive", "dead", "unknown"].includes(result.state) || typeof result.mechanism !== "string") throw new Error("PID probe adapter returned an invalid result");
    return result;
  }
  try { process.kill(pid, 0); return { state: "alive", mechanism: "process.kill(pid,0)", errorCode: null }; }
  catch (error) { return error && error.code === "ESRCH" ? { state: "dead", mechanism: "process.kill(pid,0)", errorCode: "ESRCH" } : { state: "unknown", mechanism: "process.kill(pid,0)", errorCode: error && error.code ? error.code : "UNCLASSIFIED" }; }
}

function recoveryClaimPath(paths) { return path.join(paths.directory, ".run-lock-recovery-claim-v3.json"); }
function staleLockPaths(paths, staleBytes) {
  const digest = V3.sha256Bytes(staleBytes), directory = path.join(paths.directory, ".stale-run-locks-v3");
  return { directory: directory, digest: digest, archive: path.join(directory, digest + ".run-lock.json"), certificate: path.join(directory, digest + ".recovery.json") };
}

function acquireRecoveryClaim(paths, platformLabel, source, operation, runtime) {
  if (operation !== "resume") throw new Error("v3 recovery claim is resume-only");
  const effective = runtime || {}, claimPath = recoveryClaimPath(paths), payload = {
    schema: "gg.u2.screening.recovery-claim/3", executionVersion: V3.EXECUTION_VERSION,
    semanticRole: "exclusive local stale-lock recovery mutex; no outcome authority", platformLabel: platformLabel,
    operation: operation, claimantPid: effective.pid === undefined ? process.pid : effective.pid,
    claimantHost: resolveHostIdentity(effective.hostIdentity), sourceBoundary: V3.clone(source), startedAt: effective.startedAt || new Date().toISOString()
  };
  payload.claimToken = V3.sha256JSON(payload);
  const bytes = V3.serializeJsonArtifact(payload);
  durableWriteNoReplace(claimPath, bytes, runtime && runtime.ioAdapters);
  return { path: claimPath, payload: payload, bytes: bytes };
}

function releaseOwnedFile(owned, label, adapters) {
  const io = Object.assign({ existsSync: fs.existsSync, readFileSync: fs.readFileSync, unlinkSync: fs.unlinkSync, platform: process.platform }, adapters || {});
  if (!owned || !io.existsSync(owned.path)) throw new Error("owned " + label + " disappeared before release");
  if (!io.readFileSync(owned.path).equals(owned.bytes)) throw new Error(label + " ownership bytes changed; refusing release");
  io.unlinkSync(owned.path); fsyncDirectoryPortable(path.dirname(owned.path), io);
  return "RELEASED_OWNED_" + label.toUpperCase().replace(/ /g, "_");
}

function archiveExactNoReplace(output, bytes, adapters) {
  const io = Object.assign({ existsSync: fs.existsSync, readFileSync: fs.readFileSync }, adapters || {});
  if (!io.existsSync(output)) return durableWriteNoReplace(output, bytes, adapters);
  if (!io.readFileSync(output).equals(bytes)) throw new Error("v3 stale-lock archive collision: " + output);
  return { status: "EXISTING_IDENTICAL_VALIDATED" };
}

function buildRecoveryCertificate(stalePath, staleBytes, stale, archivePath, platformLabel, source, proof) {
  const payload = {
    schema: "gg.u2.screening.stale-lock-recovery/3", executionVersion: V3.EXECUTION_VERSION,
    semanticRole: "non-scientific crash-recovery audit; no outcome authority", platformLabel: platformLabel,
    sourceBoundary: V3.clone(source),
    staleLock: { originalPath: relativePath(stalePath), archivePath: relativePath(archivePath), bytes: staleBytes.length, sha256: V3.sha256Bytes(staleBytes), pid: stale.pid, creatorHost: V3.clone(stale.creatorHost), operation: stale.operation, startedAt: stale.startedAt, lockToken: stale.lockToken },
    deathProof: { state: proof.state, mechanism: proof.mechanism, errorCode: proof.errorCode === undefined ? null : proof.errorCode },
    recoveryPolicy: "resume-only; exclusive recovery claim; exact platform/source/current-host; local dead-PID proof; archive-before-unlink; replacement lock before claim release",
    outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
  };
  return Object.assign({}, payload, { contentAddress: V3.contentAddress(payload) });
}

function recoverStaleRunLock(paths, platformLabel, source, operation, adapters, phase) {
  const io = Object.assign({ readFileSync: fs.readFileSync, mkdirSync: fs.mkdirSync, unlinkSync: fs.unlinkSync, platform: process.platform }, adapters && adapters.ioAdapters ? adapters.ioAdapters : {}), lockPath = path.join(paths.directory, ".run-lock-v3.json");
  if (operation !== "resume") throw new Error("existing v3 run lock refuses non-resume operation");
  const staleBytes = io.readFileSync(lockPath), report = validateRunLockBytes(staleBytes, platformLabel, source);
  if (!report.valid) throw new Error("stale v3 run lock validation failed: " + report.errors.join("; "));
  const currentHost = resolveHostIdentity(adapters && adapters.hostIdentity);
  if (V3.canonicalStringify(report.artifact.creatorHost) !== V3.canonicalStringify(currentHost)) throw new Error("stale v3 run lock creator host does not match; local PID proof prohibited");
  const proof = probePid(report.artifact.pid, adapters && adapters.pidProbe);
  if (proof.state !== "dead") throw new Error("stale v3 run lock requires definitive dead-PID proof; observed " + proof.state);
  const locations = staleLockPaths(paths, staleBytes), certificate = buildRecoveryCertificate(lockPath, staleBytes, report.artifact, locations.archive, platformLabel, source, proof), certificateBytes = V3.serializeJsonArtifact(certificate);
  io.mkdirSync(locations.directory, { recursive: true });
  const archiveDisposition = archiveExactNoReplace(locations.archive, staleBytes, adapters && adapters.ioAdapters), certificateDisposition = archiveExactNoReplace(locations.certificate, certificateBytes, adapters && adapters.ioAdapters);
  if (!io.readFileSync(lockPath).equals(staleBytes)) throw new Error("stale v3 run lock changed during recovery; refusing unlink");
  io.unlinkSync(lockPath); if (phase) phase.staleUnlinked = true; fsyncDirectoryPortable(paths.directory, io);
  return { staleLockSha256: locations.digest, archivePath: relativePath(locations.archive), certificatePath: relativePath(locations.certificate), archiveDisposition: archiveDisposition, certificateDisposition: certificateDisposition, proof: proof };
}

function acquireRunLock(paths, platformLabel, source, operation, adapters) {
  const io = Object.assign({ existsSync: fs.existsSync, mkdirSync: fs.mkdirSync, readFileSync: fs.readFileSync, platform: process.platform }, adapters && adapters.ioAdapters ? adapters.ioAdapters : {}), lockPath = path.join(paths.directory, ".run-lock-v3.json"), claimPath = recoveryClaimPath(paths);
  io.mkdirSync(paths.directory, { recursive: true });
  if (io.existsSync(claimPath)) throw new Error("existing v3 recovery claim refuses all operations pending manual audit");
  if (!io.existsSync(lockPath)) {
    const built = buildRunLock(platformLabel, source, operation, adapters);
    durableWriteNoReplace(lockPath, built.bytes, adapters && adapters.ioAdapters);
    return { path: lockPath, payload: built.payload, bytes: built.bytes, recovery: null };
  }
  if (operation !== "resume") throw new Error("existing v3 run lock refuses non-resume operation");
  const claim = acquireRecoveryClaim(paths, platformLabel, source, operation, adapters), phase = { staleUnlinked: false, replacementDurable: false }; let claimReleased = false;
  try {
    const recovery = recoverStaleRunLock(paths, platformLabel, source, operation, adapters, phase), built = buildRunLock(platformLabel, source, operation, adapters);
    durableWriteNoReplace(lockPath, built.bytes, adapters && adapters.ioAdapters); phase.replacementDurable = true;
    releaseOwnedFile(claim, "recovery claim", adapters && adapters.ioAdapters); claimReleased = true;
    return { path: lockPath, payload: built.payload, bytes: built.bytes, recovery: recovery };
  } catch (error) {
    if (!claimReleased && !phase.staleUnlinked && io.existsSync(claim.path) && io.readFileSync(claim.path).equals(claim.bytes)) releaseOwnedFile(claim, "recovery claim", adapters && adapters.ioAdapters);
    throw error;
  }
}

function releaseRunLock(lock, adapters) { return releaseOwnedFile(lock, "run lock", adapters); }

function buildWriterCapability(platformLabel, source, observation) {
  const payload = {
    schema: "gg.u2.screening.writer-capability/3", executionVersion: V3.EXECUTION_VERSION,
    platformLabel: platformLabel, sourceBoundary: V3.clone(source), executionSupplementDigest: V3.SUPPLEMENT_DIGEST,
    observation: observation,
    interpretation: { scientificOutcome: false, recordZeroStarted: false, directoryBarrierCompleted: observation.platform !== "win32", powerLossDirectoryPersistenceProved: false, decisionAuthority: "NONE" },
    outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
  };
  return Object.assign({}, payload, { contentAddress: V3.contentAddress(payload) });
}

function runWriterCapabilityPreflight(paths, platformLabel, source, adapters) {
  if (fs.existsSync(paths.writerCapability)) throw new Error("refusing to overwrite existing v3 writer capability");
  const probeDirectory = path.join(paths.directory, ".writer-preflight-v3"), probe = path.join(probeDirectory, "probe.bin"), probeBytes = Buffer.from("ggii-screening-v3-writer-probe\n", "utf8"), collisionBytes = Buffer.from("ggii-screening-v3-collision-sentinel\n", "utf8");
  if (fs.existsSync(probeDirectory)) throw new Error("v3 writer preflight directory collision");
  fs.mkdirSync(probeDirectory, { recursive: true });
  let disposition, existingTargetRefused = false, temporaryNameRefused = false, hardLinkPublicationRefused = false;
  try {
    disposition = durableWriteNoReplace(probe, probeBytes, adapters);
    if (!fs.readFileSync(probe).equals(probeBytes)) throw new Error("v3 writer preflight exact-byte mismatch");

    try { durableWriteNoReplace(probe, Buffer.from("overwrite-attempt\n", "utf8"), adapters); }
    catch (error) { existingTargetRefused = /refusing to overwrite/.test(error.message); }
    if (!existingTargetRefused || !fs.readFileSync(probe).equals(probeBytes)) throw new Error("v3 writer preflight existing-target refusal failed");

    const temporaryCollisionTarget = path.join(probeDirectory, "temporary-collision.bin"), temporaryCollision = temporaryCollisionTarget + ".v3-exclusive-temp";
    fs.writeFileSync(temporaryCollision, collisionBytes, { flag: "wx" });
    try { durableWriteNoReplace(temporaryCollisionTarget, probeBytes, adapters); }
    catch (error) { temporaryNameRefused = /temporary-file collision/.test(error.message); }
    if (!temporaryNameRefused || fs.existsSync(temporaryCollisionTarget) || !fs.readFileSync(temporaryCollision).equals(collisionBytes)) throw new Error("v3 writer preflight temporary-name refusal failed");
    fs.unlinkSync(temporaryCollision);

    const publicationCollisionTarget = path.join(probeDirectory, "publication-collision.bin"), publicationTemporary = publicationCollisionTarget + ".v3-exclusive-temp";
    const collisionAdapters = Object.assign({}, adapters || {}, {
      linkSync: function (source, target) {
        fs.writeFileSync(target, collisionBytes, { flag: "wx" });
        fs.linkSync(source, target);
      }
    });
    try { durableWriteNoReplace(publicationCollisionTarget, probeBytes, collisionAdapters); }
    catch (error) { hardLinkPublicationRefused = error && error.code === "EEXIST"; }
    if (!hardLinkPublicationRefused || !fs.readFileSync(publicationCollisionTarget).equals(collisionBytes) || fs.existsSync(publicationTemporary)) throw new Error("v3 writer preflight hard-link collision refusal failed");
    fs.unlinkSync(publicationCollisionTarget);

    fs.unlinkSync(probe); fsyncDirectoryPortable(probeDirectory, adapters);
    fs.rmdirSync(probeDirectory); fsyncDirectoryPortable(paths.directory, adapters);
  } catch (error) { throw error; }
  const observation = {
    platform: adapters && adapters.platform ? adapters.platform : process.platform,
    arch: process.arch,
    node: process.version,
    writerDisposition: disposition,
    exactProbeBytes: probeBytes.length,
    exactProbeSha256: V3.sha256Bytes(probeBytes),
    collisionRefusals: {
      existingTarget: existingTargetRefused,
      temporaryName: temporaryNameRefused,
      hardLinkPublication: hardLinkPublicationRefused,
      collisionBytesPreserved: true,
      temporaryWriterResidueAbsent: true
    },
    completedBeforeRecord0: true
  };
  const capability = buildWriterCapability(platformLabel, source, observation), bytes = V3.serializeJsonArtifact(capability);
  durableWriteNoReplace(paths.writerCapability, bytes, adapters);
  return { artifact: capability, bytes: bytes };
}

function validateWriterCapabilityBytes(bytes, platformLabel, source) {
  const report = V3.validateJsonArtifactBytes(bytes), errors = report.errors.slice(), artifact = report.artifact;
  if (!errors.length) {
    errors.push.apply(errors, V3.validateContentAddress(artifact));
    if (artifact.schema !== "gg.u2.screening.writer-capability/3" || artifact.executionVersion !== V3.EXECUTION_VERSION || artifact.platformLabel !== platformLabel) errors.push("v3 writer capability identity mismatch");
    if (V3.canonicalStringify(artifact.sourceBoundary) !== V3.canonicalStringify(source) || artifact.executionSupplementDigest !== V3.SUPPLEMENT_DIGEST) errors.push("v3 writer capability source mismatch");
    if (!artifact.observation || !artifact.observation.completedBeforeRecord0 || !artifact.observation.writerDisposition || !artifact.observation.writerDisposition.exactBytePostflight) errors.push("v3 writer capability did not complete exact postflight before record 0");
    const expectedDirectoryStatus = artifact.observation.platform === "win32" ? "DIRECTORY_BARRIER_UNAVAILABLE_WIN32" : "DIRECTORY_FSYNC_COMPLETED";
    if (artifact.observation.writerDisposition.directoryAfterLink.status !== expectedDirectoryStatus || artifact.observation.writerDisposition.directoryAfterTempUnlink.status !== expectedDirectoryStatus) errors.push("v3 writer directory-capability disclosure mismatch");
    const probeBytes = Buffer.from("ggii-screening-v3-writer-probe\n", "utf8"), disposition = artifact.observation.writerDisposition;
    if (artifact.observation.exactProbeBytes !== probeBytes.length || artifact.observation.exactProbeSha256 !== V3.sha256Bytes(probeBytes)) errors.push("v3 writer capability probe binding mismatch");
    if (disposition.temporaryHandleMode !== "wx+" || disposition.finalHandleMode !== "r+" || disposition.originalWritableHandleFsyncCount !== 2 || disposition.finalWritableHandleFsyncCount !== 1) errors.push("v3 writer writable-handle policy mismatch");
    const expectedCollisionRefusals = { existingTarget: true, temporaryName: true, hardLinkPublication: true, collisionBytesPreserved: true, temporaryWriterResidueAbsent: true };
    if (V3.canonicalStringify(artifact.observation.collisionRefusals) !== V3.canonicalStringify(expectedCollisionRefusals)) errors.push("v3 writer collision-refusal preflight mismatch");
    const expected = buildWriterCapability(platformLabel, source, artifact.observation);
    if (V3.canonicalStringify(artifact) !== V3.canonicalStringify(expected)) errors.push("v3 writer capability differs from deterministic rebuild");
  }
  return { valid: errors.length === 0, errors: errors, artifact: artifact };
}

function buildCheckpointManifest(entries, rawBytes, rawPath, source, platformLabel, capabilityBinding) {
  if (entries.length !== V3.EXPECTED_CHUNKS) throw new Error("v3 checkpoint manifest requires all chunks");
  const payload = {
    schema: "gg.u2.screening.checkpoint-manifest/3", executionVersion: V3.EXECUTION_VERSION,
    semanticPayloadVersion: V3.SEMANTIC_PAYLOAD_VERSION, semanticKernel: V3.semanticKernelBinding(),
    executionSupplementDigest: V3.SUPPLEMENT_DIGEST, platformLabel: platformLabel, sourceBoundary: V3.clone(source), writerCapability: V3.clone(capabilityBinding),
    chunkSizeRecords: V3.CHUNK_SIZE, chunkCount: entries.length, recordCount: V3.EXPECTED_RECORDS,
    chunks: entries.map(function (entry) { return { index: entry.index, chunk: { path: entry.chunkPath, bytes: entry.chunkBytes.length, sha256: V3.sha256Bytes(entry.chunkBytes) }, certificate: { path: entry.certificatePath, bytes: entry.certificateBytes.length, sha256: V3.sha256Bytes(entry.certificateBytes), semanticDigest: entry.certificate.contentAddress.digest } }; }),
    finalAssembly: { path: rawPath, bytes: rawBytes.length, sha256: V3.sha256Bytes(rawBytes), exactCanonicalJsonl: true, exactlyOneTerminalLf: true },
    outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
  };
  return Object.assign({}, payload, { contentAddress: V3.contentAddress(payload) });
}

function validateCheckpointManifestBytes(bytes, entries, rawBytes, rawPath, source, platformLabel, capabilityBinding) {
  const report = V3.validateJsonArtifactBytes(bytes), errors = report.errors.slice();
  if (!errors.length) {
    errors.push.apply(errors, V3.validateContentAddress(report.artifact));
    const expected = buildCheckpointManifest(entries, rawBytes, rawPath, source, platformLabel, capabilityBinding);
    if (V3.canonicalStringify(report.artifact) !== V3.canonicalStringify(expected)) errors.push("v3 checkpoint manifest differs from deterministic full rebuild");
  }
  return { valid: errors.length === 0, errors: errors, artifact: report.artifact };
}

function discoverChunks(paths, source, options) {
  if (!fs.existsSync(paths.chunks)) return { entries: [], records: [] };
  const names = fs.readdirSync(paths.chunks).sort(), allowed = /^chunk-(\d{4})(\.jsonl|\.certificate\.json)$/, pairs = new Map(), errors = [];
  names.forEach(function (name) {
    const match = name.match(allowed);
    if (!match) { errors.push("unknown v3 checkpoint entry: " + name); return; }
    const index = Number(match[1]); if (index < 0 || index >= V3.EXPECTED_CHUNKS) { errors.push("out-of-range v3 checkpoint index: " + name); return; }
    if (!pairs.has(index)) pairs.set(index, {});
    const key = match[2] === ".jsonl" ? "chunk" : "certificate";
    if (pairs.get(index)[key]) errors.push("duplicate v3 checkpoint role for index " + index);
    pairs.get(index)[key] = path.join(paths.chunks, name);
  });
  const indices = Array.from(pairs.keys()).sort(function (a, b) { return a - b; });
  indices.forEach(function (index, position) { const pair = pairs.get(index); if (index !== position) errors.push("v3 checkpoint prefix has a gap at " + position); if (!pair.chunk || !pair.certificate) errors.push("orphan v3 checkpoint pair at " + index); });
  if (errors.length) throw new Error(errors.join("; "));
  const entries = [], records = [];
  indices.forEach(function (index) {
    const pair = pairs.get(index), chunkBytes = fs.readFileSync(pair.chunk), certificateBytes = fs.readFileSync(pair.certificate), chunkPath = relativePath(pair.chunk), certificatePath = relativePath(pair.certificate);
    const report = V3.validateChunk(chunkBytes, certificateBytes, index, chunkPath, source, { remeasure: options.remeasure !== false });
    if (!report.valid) throw new Error("v3 checkpoint " + index + " validation failed: " + report.errors.join("; "));
    const entry = { index: index, chunkPath: chunkPath, certificatePath: certificatePath, chunkBytes: chunkBytes, certificateBytes: certificateBytes, certificate: report.certificate, records: report.records };
    entries.push(entry); records.push.apply(records, report.records);
  });
  return { entries: entries, records: records };
}

function createChunk(paths, index, source, adapters) {
  const census = V3.Semantic.Base.expectedCensus(), start = index * V3.CHUNK_SIZE, records = [];
  for (let offset = 0; offset < V3.CHUNK_SIZE; offset += 1) records.push(V3.buildRecord(census[start + offset]));
  const chunkBytes = V3.Semantic.serializeCanonicalJsonl(records), locations = chunkPaths(paths, index), chunkPath = relativePath(locations.chunk), certificatePath = relativePath(locations.certificate), certificate = V3.buildChunkCertificate(index, records, chunkBytes, chunkPath, source), certificateBytes = V3.serializeJsonArtifact(certificate);
  const preflight = V3.validateChunk(chunkBytes, certificateBytes, index, chunkPath, source, { remeasure: true });
  if (!preflight.valid) throw new Error("new v3 checkpoint " + index + " preflight failed: " + preflight.errors.join("; "));
  const chunkDisposition = durableWriteNoReplace(locations.chunk, chunkBytes, adapters), certificateDisposition = durableWriteNoReplace(locations.certificate, certificateBytes, adapters);
  const postflight = V3.validateChunk(fs.readFileSync(locations.chunk), fs.readFileSync(locations.certificate), index, chunkPath, source, { remeasure: true });
  if (!postflight.valid) throw new Error("new v3 checkpoint " + index + " postflight failed: " + postflight.errors.join("; "));
  return { index: index, chunkPath: chunkPath, certificatePath: certificatePath, chunkBytes: chunkBytes, certificateBytes: certificateBytes, certificate: certificate, records: records, dispositions: { chunk: chunkDisposition, certificate: certificateDisposition } };
}

function ensureFinal(output, expectedBytes, resume, adapters) {
  if (fs.existsSync(output)) {
    if (!resume) throw new Error("existing v3 final artifact refuses non-resume execution: " + output);
    if (!fs.readFileSync(output).equals(expectedBytes)) throw new Error("existing v3 final artifact collision: " + output);
    return { status: "EXISTING_IDENTICAL_VALIDATED" };
  }
  return durableWriteNoReplace(output, expectedBytes, adapters);
}

function finalContext(paths, platformLabel, source, entries, records, capabilityBinding) {
  if (entries.length !== V3.EXPECTED_CHUNKS || records.length !== V3.EXPECTED_RECORDS) throw new Error("v3 final assembly requires all checkpoint records");
  const rawBytes = Buffer.concat(entries.map(function (entry) { return entry.chunkBytes; })), rawPath = relativePath(paths.raw), rawReport = V3.Semantic.parseCanonicalJsonl(rawBytes, { expectedCount: V3.EXPECTED_RECORDS });
  if (!rawReport.valid || V3.canonicalStringify(rawReport.records) !== V3.canonicalStringify(records)) throw new Error("v3 deterministic raw assembly failed: " + rawReport.errors.join("; "));
  const checkpointPath = relativePath(paths.checkpointManifest), checkpoint = buildCheckpointManifest(entries, rawBytes, rawPath, source, platformLabel, capabilityBinding), checkpointBytes = V3.serializeJsonArtifact(checkpoint);
  const checkpointBinding = { path: checkpointPath, bytes: checkpointBytes.length, sha256: V3.sha256Bytes(checkpointBytes), semanticDigest: checkpoint.contentAddress.digest };
  const summaryPath = relativePath(paths.summary), summary = V3.buildSummaryEnvelope(records, { path: rawPath, bytes: rawBytes.length, sha256: V3.sha256Bytes(rawBytes) }, checkpointBinding, source), summaryBytes = V3.serializeJsonArtifact(summary);
  const summaryReport = V3.validateSummaryEnvelopeBytes(summaryBytes, records, rawBytes, rawPath, checkpointBinding, source, { remeasure: false });
  if (!summaryReport.valid) throw new Error("v3 summary preflight failed: " + summaryReport.errors.join("; "));
  return { rawBytes: rawBytes, rawPath: rawPath, checkpoint: checkpoint, checkpointBytes: checkpointBytes, checkpointPath: checkpointPath, checkpointBinding: checkpointBinding, summary: summary, summaryBytes: summaryBytes, summaryPath: summaryPath };
}

function buildRuntimeCertificate(context, metrics) {
  const payload = {
    schema: "gg.u2.screening.runtime-certificate/3", executionVersion: V3.EXECUTION_VERSION, semanticPayloadVersion: V3.SEMANTIC_PAYLOAD_VERSION,
    semanticKernel: V3.semanticKernelBinding(), executionSupplementDigest: V3.SUPPLEMENT_DIGEST,
    platformLabel: context.platformLabel, sourceBoundary: V3.clone(context.source), writerCapability: V3.clone(context.capabilityBinding),
    artifacts: {
      raw: { path: context.rawPath, bytes: context.rawBytes.length, sha256: V3.sha256Bytes(context.rawBytes) },
      summary: { path: context.summaryPath, bytes: context.summaryBytes.length, sha256: V3.sha256Bytes(context.summaryBytes), semanticDigest: context.summary.contentAddress.digest },
      checkpointManifest: { path: context.checkpointPath, bytes: context.checkpointBytes.length, sha256: V3.sha256Bytes(context.checkpointBytes), semanticDigest: context.checkpoint.contentAddress.digest }
    },
    runtime: metrics, outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
  };
  return Object.assign({}, payload, { contentAddress: V3.contentAddress(payload) });
}

function validateRuntimeBytes(bytes, context) {
  const report = V3.validateJsonArtifactBytes(bytes), errors = report.errors.slice(), artifact = report.artifact;
  if (!errors.length) {
    errors.push.apply(errors, V3.validateContentAddress(artifact));
    const expectedArtifacts = {
      raw: { path: context.rawPath, bytes: context.rawBytes.length, sha256: V3.sha256Bytes(context.rawBytes) },
      summary: { path: context.summaryPath, bytes: context.summaryBytes.length, sha256: V3.sha256Bytes(context.summaryBytes), semanticDigest: context.summary.contentAddress.digest },
      checkpointManifest: { path: context.checkpointPath, bytes: context.checkpointBytes.length, sha256: V3.sha256Bytes(context.checkpointBytes), semanticDigest: context.checkpoint.contentAddress.digest }
    };
    if (artifact.schema !== "gg.u2.screening.runtime-certificate/3" || artifact.executionVersion !== V3.EXECUTION_VERSION || artifact.semanticPayloadVersion !== V3.SEMANTIC_PAYLOAD_VERSION || artifact.platformLabel !== context.platformLabel) errors.push("v3 runtime identity mismatch");
    if (V3.canonicalStringify(artifact.sourceBoundary) !== V3.canonicalStringify(context.source) || V3.canonicalStringify(artifact.writerCapability) !== V3.canonicalStringify(context.capabilityBinding)) errors.push("v3 runtime source/capability mismatch");
    if (V3.canonicalStringify(artifact.artifacts) !== V3.canonicalStringify(expectedArtifacts)) errors.push("v3 runtime artifact bindings mismatch");
    if (!artifact.outcome || artifact.outcome.u2Status !== "UNRESOLVED" || artifact.outcome.decisionAuthority !== "NONE") errors.push("v3 runtime is not fail-closed");
  }
  return { valid: errors.length === 0, errors: errors, artifact: artifact };
}

function validateAllFinals(paths, platformLabel, source, entries, records, capabilityBinding) {
  const context = finalContext(paths, platformLabel, source, entries, records, capabilityBinding), rawBytes = fs.readFileSync(paths.raw), checkpointBytes = fs.readFileSync(paths.checkpointManifest), summaryBytes = fs.readFileSync(paths.summary), runtimeBytes = fs.readFileSync(paths.runtime);
  if (!rawBytes.equals(context.rawBytes)) throw new Error("v3 final raw bytes differ from deterministic chunk assembly");
  const checkpointReport = validateCheckpointManifestBytes(checkpointBytes, entries, rawBytes, context.rawPath, source, platformLabel, capabilityBinding);
  if (!checkpointReport.valid || !checkpointBytes.equals(context.checkpointBytes)) throw new Error("v3 checkpoint final validation failed: " + checkpointReport.errors.join("; "));
  const summaryReport = V3.validateSummaryEnvelopeBytes(summaryBytes, records, rawBytes, context.rawPath, context.checkpointBinding, source, { remeasure: true });
  if (!summaryReport.valid || !summaryBytes.equals(context.summaryBytes)) throw new Error("v3 summary final validation failed: " + summaryReport.errors.join("; "));
  const runtimeContext = { platformLabel: platformLabel, source: source, capabilityBinding: capabilityBinding, rawPath: context.rawPath, rawBytes: rawBytes, summaryPath: context.summaryPath, summaryBytes: summaryBytes, summary: summaryReport.summary, checkpointPath: context.checkpointPath, checkpointBytes: checkpointBytes, checkpoint: checkpointReport.artifact };
  const runtimeReport = validateRuntimeBytes(runtimeBytes, runtimeContext);
  if (!runtimeReport.valid) throw new Error("v3 runtime final validation failed: " + runtimeReport.errors.join("; "));
  return { context: context, runtime: runtimeReport.artifact, runtimeBytes: runtimeBytes };
}

function assertNoV3Outputs(paths) {
  if (!fs.existsSync(paths.directory)) return;
  const allowed = new Set([path.basename(paths.writerCapability), ".run-lock-v3.json"]), entries = fs.readdirSync(paths.directory).filter(function (name) { return !allowed.has(name); });
  if (entries.length) throw new Error("existing screening-v3 output refuses a new non-resume run: " + entries.sort().join(","));
}

function capabilityBinding(paths, bytes, artifact) { return { path: relativePath(paths.writerCapability), bytes: bytes.length, sha256: V3.sha256Bytes(bytes), semanticDigest: artifact.contentAddress.digest }; }

function run(options) {
  V3.loadPrerequisites(); assertSourceModePolicy(options.sourceMode);
  const loaded = loadSource(options), source = loaded.source, paths = pathsFor(options.platformLabel), operation = options.writerPreflightOnly ? "writer-preflight-only" : (options.validateOnly ? "validate-only" : (options.resume ? "resume" : "fresh")), lock = acquireRunLock(paths, options.platformLabel, source, operation);
  try {
    if (options.writerPreflightOnly) {
      if (fs.existsSync(paths.chunks) || fs.existsSync(paths.raw) || fs.existsSync(paths.summary) || fs.existsSync(paths.runtime) || fs.existsSync(paths.checkpointManifest)) throw new Error("writer preflight must precede every v3 scientific artifact");
      const created = runWriterCapabilityPreflight(paths, options.platformLabel, source), report = validateWriterCapabilityBytes(created.bytes, options.platformLabel, source);
      if (!report.valid) throw new Error("v3 writer capability validation failed: " + report.errors.join("; "));
      process.stdout.write(JSON.stringify({ mode: "writer-preflight-only", platformLabel: options.platformLabel, capabilityDigest: created.artifact.contentAddress.digest, recordZeroStarted: false, u2Status: "UNRESOLVED" }) + "\n"); return;
    }
    if (!fs.existsSync(paths.writerCapability)) throw new Error("v3 writer capability is required before record 0");
    const capabilityBytes = fs.readFileSync(paths.writerCapability), capabilityReport = validateWriterCapabilityBytes(capabilityBytes, options.platformLabel, source);
    if (!capabilityReport.valid) throw new Error("v3 writer capability invalid: " + capabilityReport.errors.join("; "));
    const capBinding = capabilityBinding(paths, capabilityBytes, capabilityReport.artifact);
    if (options.validateOnly) {
      const discovered = discoverChunks(paths, source, { remeasure: true });
      if (discovered.entries.length !== V3.EXPECTED_CHUNKS) throw new Error("v3 validate-only requires all chunks");
      const validated = validateAllFinals(paths, options.platformLabel, source, discovered.entries, discovered.records, capBinding);
      process.stdout.write(JSON.stringify({ mode: "validate-only", chunks: discovered.entries.length, records: discovered.records.length, rawSha256: V3.sha256Bytes(validated.context.rawBytes), summaryDigest: validated.context.summary.contentAddress.digest, runtimeDigest: validated.runtime.contentAddress.digest, u2Status: "UNRESOLVED" }) + "\n"); return;
    }
    if (!options.resume) assertNoV3Outputs(paths);
    const started = performance.now(), startWallTime = new Date().toISOString(), recovered = options.resume ? discoverChunks(paths, source, { remeasure: true }) : { entries: [], records: [] }, entries = recovered.entries.slice(), records = recovered.records.slice(); let peakRssBytes = process.memoryUsage().rss;
    for (let index = entries.length; index < V3.EXPECTED_CHUNKS; index += 1) {
      const entry = createChunk(paths, index, source); entries.push(entry); records.push.apply(records, entry.records); peakRssBytes = Math.max(peakRssBytes, process.memoryUsage().rss);
      process.stderr.write(JSON.stringify({ executionVersion: V3.EXECUTION_VERSION, checkpointChunk: index, completedRecords: records.length, totalRecords: V3.EXPECTED_RECORDS, elapsedSeconds: (performance.now() - started) / 1000, peakRssBytes: peakRssBytes }) + "\n");
    }
    const context = finalContext(paths, options.platformLabel, source, entries, records, capBinding), dispositions = {};
    dispositions.checkpointManifest = ensureFinal(paths.checkpointManifest, context.checkpointBytes, options.resume);
    dispositions.raw = ensureFinal(paths.raw, context.rawBytes, options.resume);
    dispositions.summary = ensureFinal(paths.summary, context.summaryBytes, options.resume);
    const runtimeContext = { platformLabel: options.platformLabel, source: source, capabilityBinding: capBinding, rawPath: context.rawPath, rawBytes: context.rawBytes, summaryPath: context.summaryPath, summaryBytes: context.summaryBytes, summary: context.summary, checkpointPath: context.checkpointPath, checkpointBytes: context.checkpointBytes, checkpoint: context.checkpoint };
    if (fs.existsSync(paths.runtime)) {
      if (!options.resume) throw new Error("existing v3 runtime refuses non-resume execution");
      const report = validateRuntimeBytes(fs.readFileSync(paths.runtime), runtimeContext); if (!report.valid) throw new Error("existing v3 runtime collision: " + report.errors.join("; ")); dispositions.runtime = { status: "EXISTING_VALIDATED" };
    } else {
      const metrics = { startWallTime: startWallTime, endWallTime: new Date().toISOString(), elapsedMilliseconds: performance.now() - started, recoveredChunkCount: recovered.entries.length, generatedChunkCount: V3.EXPECTED_CHUNKS - recovered.entries.length, staleLockRecovery: lock.recovery, validationPolicy: "fresh v2-base plus closed v3 adapter replay at chunk and final boundaries", peakRssBytes: peakRssBytes, environment: { platform: process.platform, arch: process.arch, node: process.version, cpuCount: os.cpus().length } }, runtime = buildRuntimeCertificate(runtimeContext, metrics), runtimeBytes = V3.serializeJsonArtifact(runtime), runtimeReport = validateRuntimeBytes(runtimeBytes, runtimeContext);
      if (!runtimeReport.valid) throw new Error("v3 runtime preflight failed: " + runtimeReport.errors.join("; ")); dispositions.runtime = durableWriteNoReplace(paths.runtime, runtimeBytes);
    }
    const final = validateAllFinals(paths, options.platformLabel, source, entries, records, capBinding);
    process.stdout.write(JSON.stringify({ mode: options.resume ? "resume" : "fresh", dispositions: dispositions, chunks: entries.length, records: records.length, rawSha256: V3.sha256Bytes(final.context.rawBytes), summaryDigest: final.context.summary.contentAddress.digest, runtimeDigest: final.runtime.contentAddress.digest, sourceBoundaryDigest: source.semanticDigest, u2Status: "UNRESOLVED" }) + "\n");
  } finally { releaseRunLock(lock); }
}

if (require.main === module) run(parseArgs(process.argv.slice(2)));
module.exports = {
  parseArgs: parseArgs, pathsFor: pathsFor, chunkPaths: chunkPaths, relativePath: relativePath,
  fsyncDirectoryPortable: fsyncDirectoryPortable, durableWriteNoReplace: durableWriteNoReplace,
  gitExecutableAvailable: gitExecutableAvailable, assertSourceModePolicy: assertSourceModePolicy, loadSource: loadSource,
  resolveHostIdentity: resolveHostIdentity, buildRunLock: buildRunLock, validateRunLockBytes: validateRunLockBytes, probePid: probePid,
  recoveryClaimPath: recoveryClaimPath, staleLockPaths: staleLockPaths, acquireRecoveryClaim: acquireRecoveryClaim,
  buildRecoveryCertificate: buildRecoveryCertificate, recoverStaleRunLock: recoverStaleRunLock, acquireRunLock: acquireRunLock, releaseRunLock: releaseRunLock,
  buildWriterCapability: buildWriterCapability, runWriterCapabilityPreflight: runWriterCapabilityPreflight, validateWriterCapabilityBytes: validateWriterCapabilityBytes,
  buildCheckpointManifest: buildCheckpointManifest, validateCheckpointManifestBytes: validateCheckpointManifestBytes,
  discoverChunks: discoverChunks, createChunk: createChunk, ensureFinal: ensureFinal, finalContext: finalContext,
  buildRuntimeCertificate: buildRuntimeCertificate, validateRuntimeBytes: validateRuntimeBytes, validateAllFinals: validateAllFinals,
  assertNoV3Outputs: assertNoV3Outputs, capabilityBinding: capabilityBinding, run: run
};
