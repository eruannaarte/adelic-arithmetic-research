#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const childProcess = require("child_process");
const { performance } = require("perf_hooks");
const Screening = require("./global-geometry-ii-u2-screening-v2.js");

function relativePath(absolute) { return path.relative(Screening.ROOT, absolute).split(path.sep).join("/"); }
function padChunk(index) { return String(index).padStart(4, "0"); }

function parseArgs(argv) {
  const options = { platformLabel: process.platform === "darwin" ? "macos" : process.platform, sourceBoundary: path.join(Screening.ROOT, "artifacts/global-geometry-ii/u2/screening/screening-v2/source-boundary-v2.json"), sourceMode: null, sourceBoundaryFileSha256: null, sourceBoundarySemanticSha256: null, resume: false, validateOnly: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--platform-label" && argv[index + 1]) options.platformLabel = argv[++index];
    else if (arg === "--source-boundary" && argv[index + 1]) options.sourceBoundary = path.resolve(argv[++index]);
    else if (arg === "--source-mode" && argv[index + 1]) options.sourceMode = argv[++index];
    else if (arg === "--source-boundary-file-sha256" && argv[index + 1]) options.sourceBoundaryFileSha256 = argv[++index];
    else if (arg === "--source-boundary-semantic-sha256" && argv[index + 1]) options.sourceBoundarySemanticSha256 = argv[++index];
    else if (arg === "--resume") options.resume = true;
    else if (arg === "--validate-only") options.validateOnly = true;
    else throw new Error("usage: run-global-geometry-ii-u2-screening-v2.js --source-mode git|portable --source-boundary-file-sha256 HEX --source-boundary-semantic-sha256 HEX [--source-boundary path] [--platform-label label] [--resume|--validate-only]");
  }
  if (!/^[a-z0-9_-]{1,32}$/.test(options.platformLabel)) throw new Error("platform label must match [a-z0-9_-]{1,32}");
  if (options.sourceMode !== "git" && options.sourceMode !== "portable") throw new Error("--source-mode must explicitly be git or portable");
  if (!/^[0-9a-f]{64}$/.test(options.sourceBoundaryFileSha256 || "") || !/^[0-9a-f]{64}$/.test(options.sourceBoundarySemanticSha256 || "")) throw new Error("both exact source-boundary SHA-256 pins are required");
  if (options.resume && options.validateOnly) throw new Error("--resume and --validate-only are mutually exclusive");
  return options;
}

function pathsFor(label) {
  const directory = path.join(Screening.ROOT, "artifacts/global-geometry-ii/u2/screening/screening-v2", label), chunks = path.join(directory, "chunks");
  return {
    directory: directory,
    chunks: chunks,
    raw: path.join(directory, "screening-raw-v2.jsonl"),
    summary: path.join(directory, "screening-summary-v2.json"),
    runtime: path.join(directory, "screening-runtime-v2.json"),
    checkpointManifest: path.join(directory, "screening-checkpoint-manifest-v2.json")
  };
}

function chunkPaths(paths, index) {
  const stem = "chunk-" + padChunk(index);
  return { chunk: path.join(paths.chunks, stem + ".jsonl"), certificate: path.join(paths.chunks, stem + ".certificate.json") };
}

function fsyncDirectory(directory) {
  const descriptor = fs.openSync(directory, "r");
  try { fs.fsyncSync(descriptor); } finally { fs.closeSync(descriptor); }
}

function durableWriteNoReplace(output, bytes) {
  if (!Buffer.isBuffer(bytes)) throw new Error("durable write requires Buffer bytes");
  if (fs.existsSync(output)) throw new Error("refusing to overwrite existing artifact: " + output);
  fs.mkdirSync(path.dirname(output), { recursive: true });
  const temporary = output + ".exclusive-temp";
  if (fs.existsSync(temporary)) throw new Error("temporary-file collision refuses write: " + temporary);
  const descriptor = fs.openSync(temporary, "wx");
  try {
    let offset = 0;
    while (offset < bytes.length) offset += fs.writeSync(descriptor, bytes, offset, bytes.length - offset);
    fs.fsyncSync(descriptor);
  } finally { fs.closeSync(descriptor); }
  try {
    fs.linkSync(temporary, output);
    const finalDescriptor = fs.openSync(output, "r");
    try { fs.fsyncSync(finalDescriptor); } finally { fs.closeSync(finalDescriptor); }
    fsyncDirectory(path.dirname(output));
  } finally {
    if (fs.existsSync(temporary)) fs.unlinkSync(temporary);
  }
  return "CREATED_EXCLUSIVE_FSYNC";
}

function contentAddress(payload) {
  return { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: Screening.sha256JSON(payload), canonicalBytes: Buffer.byteLength(Screening.canonicalStringify(payload), "utf8") };
}

function validateContentAddress(artifact) {
  if (!artifact || !artifact.contentAddress) return ["contentAddress missing"];
  const payload = JSON.parse(JSON.stringify(artifact)); const address = payload.contentAddress; delete payload.contentAddress;
  const expected = contentAddress(payload), errors = [];
  if (Screening.canonicalStringify(address) !== Screening.canonicalStringify(expected)) errors.push("contentAddress mismatch");
  return errors;
}

function loadSource(options, adapters) {
  const bytes = (adapters && adapters.readSourceBoundary ? adapters.readSourceBoundary : fs.readFileSync)(options.sourceBoundary);
  const pins = { fileSha256: options.sourceBoundaryFileSha256, semanticSha256: options.sourceBoundarySemanticSha256 };
  const boundaryRelative = relativePath(options.sourceBoundary);
  const source = Screening.sourceBinding(bytes, options.sourceMode, pins, adapters && adapters.sourceAdapters, boundaryRelative);
  return { bytes: bytes, source: source, artifact: JSON.parse(bytes.toString("utf8")), pins: pins };
}

function gitExecutableAvailable(detector) {
  if (detector) return detector() === true;
  const result = childProcess.spawnSync("git", ["--version"], { cwd: Screening.ROOT, stdio: "ignore" });
  if (result.error && result.error.code === "ENOENT") return false;
  return true;
}

function assertSourceModePolicy(mode, detector) {
  const available = gitExecutableAvailable(detector);
  if (mode === "portable" && available) throw new Error("portable source mode is refused because Git is available; Git failure never authorizes portable fallback");
  return { gitExecutableAvailable: available, selectedMode: mode };
}

function resolveHostIdentity(supplied) {
  const identity = supplied || { hostname: os.hostname(), platform: process.platform, arch: process.arch };
  if (!identity || typeof identity.hostname !== "string" || !identity.hostname || typeof identity.platform !== "string" || !identity.platform || typeof identity.arch !== "string" || !identity.arch) throw new Error("host identity requires nonempty hostname, platform, and arch");
  return { hostname: identity.hostname, platform: identity.platform, arch: identity.arch };
}

function buildRunLock(platformLabel, source, operation, runtime) {
  const effective = runtime || {};
  const payload = {
    schema: "gg.u2.screening.run-lock/2",
    platformLabel: platformLabel,
    operation: operation,
    pid: effective.pid === undefined ? process.pid : effective.pid,
    creatorHost: resolveHostIdentity(effective.hostIdentity),
    sourceBoundary: JSON.parse(JSON.stringify(source)),
    startedAt: effective.startedAt || new Date().toISOString()
  };
  payload.lockToken = Screening.sha256JSON(payload);
  return { payload: payload, bytes: Screening.serializeJsonArtifact(payload) };
}

function validateRunLockBytes(bytes, platformLabel, source) {
  const report = Screening.validateJsonArtifactBytes(bytes), errors = report.errors.slice(), artifact = report.artifact;
  if (!errors.length) {
    if (artifact.schema !== "gg.u2.screening.run-lock/2") errors.push("run lock schema mismatch");
    if (artifact.platformLabel !== platformLabel) errors.push("run lock platform mismatch");
    if (Screening.canonicalStringify(artifact.sourceBoundary) !== Screening.canonicalStringify(source)) errors.push("run lock source-boundary mismatch");
    if (!["fresh", "resume", "validate-only"].includes(artifact.operation)) errors.push("run lock operation invalid");
    if (!Number.isSafeInteger(artifact.pid) || artifact.pid <= 0) errors.push("run lock PID invalid");
    try {
      if (Screening.canonicalStringify(artifact.creatorHost) !== Screening.canonicalStringify(resolveHostIdentity(artifact.creatorHost))) errors.push("run lock creator host contains unexpected fields");
    } catch (error) { errors.push("run lock creator host invalid: " + error.message); }
    if (typeof artifact.startedAt !== "string" || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(artifact.startedAt) || Number.isNaN(Date.parse(artifact.startedAt))) errors.push("run lock start time invalid");
    if (!/^[0-9a-f]{64}$/.test(artifact.lockToken || "")) errors.push("run lock token invalid");
    const payload = JSON.parse(JSON.stringify(artifact)); const suppliedToken = payload.lockToken; delete payload.lockToken;
    if (suppliedToken !== Screening.sha256JSON(payload)) errors.push("run lock token mismatch");
  }
  return { valid: errors.length === 0, errors: errors, artifact: artifact };
}

function probePid(pid, adapter) {
  if (adapter) {
    const result = adapter(pid);
    if (!result || !["alive", "dead", "unknown"].includes(result.state) || typeof result.mechanism !== "string") throw new Error("PID probe adapter returned an invalid result");
    return result;
  }
  try {
    process.kill(pid, 0);
    return { state: "alive", mechanism: "process.kill(pid,0)", errorCode: null };
  } catch (error) {
    if (error && error.code === "ESRCH") return { state: "dead", mechanism: "process.kill(pid,0)", errorCode: "ESRCH" };
    return { state: "unknown", mechanism: "process.kill(pid,0)", errorCode: error && error.code ? error.code : "UNCLASSIFIED" };
  }
}

function staleLockPaths(paths, staleBytes) {
  const digest = Screening.sha256Bytes(staleBytes), directory = path.join(paths.directory, ".stale-run-locks");
  return {
    directory: directory,
    digest: digest,
    archive: path.join(directory, digest + ".run-lock.json"),
    certificate: path.join(directory, digest + ".recovery.json")
  };
}

function recoveryClaimPath(paths) { return path.join(paths.directory, ".run-lock-recovery-claim.json"); }

function acquireRecoveryClaim(paths, platformLabel, source, operation, runtime) {
  if (operation !== "resume") throw new Error("recovery claim is resume-only");
  const effective = runtime || {}, claimPath = recoveryClaimPath(paths), payload = {
    schema: "gg.u2.screening.recovery-claim/2",
    semanticRole: "exclusive local stale-lock recovery mutex; no outcome authority",
    platformLabel: platformLabel,
    operation: operation,
    claimantPid: effective.pid === undefined ? process.pid : effective.pid,
    claimantHost: resolveHostIdentity(effective.hostIdentity),
    sourceBoundary: JSON.parse(JSON.stringify(source)),
    startedAt: effective.startedAt || new Date().toISOString()
  };
  payload.claimToken = Screening.sha256JSON(payload);
  const bytes = Screening.serializeJsonArtifact(payload);
  durableWriteNoReplace(claimPath, bytes);
  return { path: claimPath, payload: payload, bytes: bytes };
}

function releaseRecoveryClaim(claim) {
  if (!claim || !fs.existsSync(claim.path)) throw new Error("owned recovery claim disappeared before release");
  const observed = fs.readFileSync(claim.path);
  if (!observed.equals(claim.bytes)) throw new Error("recovery claim ownership bytes changed; refusing release");
  fs.unlinkSync(claim.path);
  fsyncDirectory(path.dirname(claim.path));
  return "RELEASED_OWNED_RECOVERY_CLAIM";
}

function buildStaleLockRecoveryCertificate(stalePath, staleBytes, staleArtifact, archivePath, platformLabel, source, proof) {
  const payload = {
    schema: "gg.u2.screening.stale-lock-recovery/2",
    semanticRole: "non-scientific crash-recovery audit; no outcome authority",
    platformLabel: platformLabel,
    sourceBoundary: JSON.parse(JSON.stringify(source)),
    staleLock: {
      originalPath: relativePath(stalePath),
      archivePath: relativePath(archivePath),
      bytes: staleBytes.length,
      sha256: Screening.sha256Bytes(staleBytes),
      pid: staleArtifact.pid,
      creatorHost: JSON.parse(JSON.stringify(staleArtifact.creatorHost)),
      operation: staleArtifact.operation,
      startedAt: staleArtifact.startedAt,
      lockToken: staleArtifact.lockToken
    },
    deathProof: { state: proof.state, mechanism: proof.mechanism, errorCode: proof.errorCode === undefined ? null : proof.errorCode },
    recoveryPolicy: "resume-only; exact matching platform and source boundary; definitive dead-PID proof; archive-before-unlink; no replacement",
    outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
  };
  return Object.assign({}, payload, { contentAddress: contentAddress(payload) });
}

function validateStaleLockRecoveryCertificateBytes(bytes, stalePath, staleBytes, staleArtifact, archivePath, platformLabel, source, proof) {
  const report = Screening.validateJsonArtifactBytes(bytes), errors = report.errors.slice();
  if (!errors.length) {
    errors.push.apply(errors, validateContentAddress(report.artifact));
    const expected = buildStaleLockRecoveryCertificate(stalePath, staleBytes, staleArtifact, archivePath, platformLabel, source, proof);
    if (Screening.canonicalStringify(report.artifact) !== Screening.canonicalStringify(expected)) errors.push("stale-lock recovery certificate differs from deterministic rebuild");
  }
  return { valid: errors.length === 0, errors: errors, artifact: report.artifact };
}

function archiveExactNoReplace(output, bytes) {
  if (!fs.existsSync(output)) return durableWriteNoReplace(output, bytes);
  if (!fs.readFileSync(output).equals(bytes)) throw new Error("stale-lock archive collision: " + output);
  return "EXISTING_IDENTICAL_VALIDATED";
}

function recoverStaleRunLock(paths, platformLabel, source, operation, adapters, phase) {
  const lockPath = path.join(paths.directory, ".run-lock.json");
  if (operation !== "resume") throw new Error("existing run lock refuses non-resume operation");
  const staleBytes = fs.readFileSync(lockPath); if (phase) phase.originalLockBytes = staleBytes;
  const staleReport = validateRunLockBytes(staleBytes, platformLabel, source);
  if (!staleReport.valid) throw new Error("stale run lock validation failed: " + staleReport.errors.join("; "));
  const currentHost = resolveHostIdentity(adapters && adapters.hostIdentity);
  if (Screening.canonicalStringify(staleReport.artifact.creatorHost) !== Screening.canonicalStringify(currentHost)) throw new Error("stale run lock creator host does not match this host; local PID-death proof is prohibited");
  const proof = probePid(staleReport.artifact.pid, adapters && adapters.pidProbe);
  if (proof.state !== "dead") throw new Error("stale run lock cannot be recovered without definitive dead-PID proof; observed " + proof.state);
  const locations = staleLockPaths(paths, staleBytes), certificate = buildStaleLockRecoveryCertificate(lockPath, staleBytes, staleReport.artifact, locations.archive, platformLabel, source, proof), certificateBytes = Screening.serializeJsonArtifact(certificate);
  const certificateReport = validateStaleLockRecoveryCertificateBytes(certificateBytes, lockPath, staleBytes, staleReport.artifact, locations.archive, platformLabel, source, proof);
  if (!certificateReport.valid) throw new Error("stale-lock recovery certificate preflight failed: " + certificateReport.errors.join("; "));
  fs.mkdirSync(locations.directory, { recursive: true });
  const archiveDisposition = archiveExactNoReplace(locations.archive, staleBytes);
  const certificateDisposition = archiveExactNoReplace(locations.certificate, certificateBytes);
  const currentBytes = fs.readFileSync(lockPath);
  if (!currentBytes.equals(staleBytes)) throw new Error("stale run lock changed during recovery; refusing unlink");
  fs.unlinkSync(lockPath);
  if (phase) phase.staleUnlinked = true;
  fsyncDirectory(paths.directory);
  return {
    staleLockSha256: locations.digest,
    archivePath: relativePath(locations.archive),
    certificatePath: relativePath(locations.certificate),
    archiveDisposition: archiveDisposition,
    certificateDisposition: certificateDisposition,
    proof: proof
  };
}

function acquireRunLock(paths, platformLabel, source, operation, adapters) {
  fs.mkdirSync(paths.directory, { recursive: true });
  const lockPath = path.join(paths.directory, ".run-lock.json"), claimPath = recoveryClaimPath(paths);
  if (fs.existsSync(claimPath)) throw new Error("existing stale-lock recovery claim refuses all operations pending manual audit");
  if (!fs.existsSync(lockPath)) {
    const built = buildRunLock(platformLabel, source, operation, adapters);
    durableWriteNoReplace(lockPath, built.bytes);
    return { path: lockPath, payload: built.payload, bytes: built.bytes, recovery: null };
  }
  if (operation !== "resume") throw new Error("existing run lock refuses non-resume operation");
  const claim = acquireRecoveryClaim(paths, platformLabel, source, operation, adapters);
  const phase = { originalLockBytes: null, staleUnlinked: false, replacementDurable: false }; let claimReleased = false;
  try {
    const recovery = recoverStaleRunLock(paths, platformLabel, source, operation, adapters, phase);
    const built = buildRunLock(platformLabel, source, operation, adapters);
    durableWriteNoReplace(lockPath, built.bytes);
    phase.replacementDurable = true;
    releaseRecoveryClaim(claim); claimReleased = true;
    return { path: lockPath, payload: built.payload, bytes: built.bytes, recovery: recovery };
  } catch (error) {
    const originalStillPresent = phase.originalLockBytes && fs.existsSync(lockPath) && fs.readFileSync(lockPath).equals(phase.originalLockBytes);
    if (!claimReleased && !phase.staleUnlinked && originalStillPresent && fs.existsSync(claim.path) && fs.readFileSync(claim.path).equals(claim.bytes)) releaseRecoveryClaim(claim);
    throw error;
  }
}

function releaseRunLock(lock) {
  if (!lock || !fs.existsSync(lock.path)) throw new Error("owned run lock disappeared before release");
  const observed = fs.readFileSync(lock.path);
  if (!observed.equals(lock.bytes)) throw new Error("run lock ownership bytes changed; refusing release");
  fs.unlinkSync(lock.path);
  fsyncDirectory(path.dirname(lock.path));
  return "RELEASED_OWNED_LOCK";
}

function buildCheckpointManifest(entries, rawBytes, rawPath, source, platformLabel) {
  if (entries.length !== Screening.EXPECTED_CHUNKS) throw new Error("checkpoint manifest requires all chunks");
  const payload = {
    schema: "gg.u2.screening.checkpoint-manifest/2",
    screeningVersion: "screening-v2",
    platformLabel: platformLabel,
    supplementDigest: Screening.SUPPLEMENT_DIGEST,
    sourceBoundary: JSON.parse(JSON.stringify(source)),
    chunkSizeRecords: Screening.CHUNK_SIZE,
    chunkCount: entries.length,
    recordCount: Screening.EXPECTED_RECORDS,
    chunks: entries.map(function (entry) {
      return {
        index: entry.index,
        chunk: { path: entry.chunkPath, bytes: entry.chunkBytes.length, sha256: Screening.sha256Bytes(entry.chunkBytes) },
        certificate: { path: entry.certificatePath, bytes: entry.certificateBytes.length, sha256: Screening.sha256Bytes(entry.certificateBytes), semanticDigest: entry.certificate.contentAddress.digest }
      };
    }),
    finalAssembly: { path: rawPath, bytes: rawBytes.length, sha256: Screening.sha256Bytes(rawBytes), exactCanonicalJsonl: true, exactlyOneTerminalLf: true },
    outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
  };
  return Object.assign({}, payload, { contentAddress: contentAddress(payload) });
}

function validateCheckpointManifestBytes(bytes, entries, rawBytes, rawPath, source, platformLabel) {
  const report = Screening.validateJsonArtifactBytes(bytes), errors = report.errors.slice();
  if (!errors.length) {
    const expected = buildCheckpointManifest(entries, rawBytes, rawPath, source, platformLabel);
    if (Screening.canonicalStringify(report.artifact) !== Screening.canonicalStringify(expected)) errors.push("checkpoint manifest differs from deterministic full rebuild");
  }
  return { valid: errors.length === 0, errors: errors, artifact: report.artifact };
}

function discoverChunks(paths, source, options) {
  if (!fs.existsSync(paths.chunks)) return { entries: [], records: [] };
  const names = fs.readdirSync(paths.chunks).sort(), allowed = /^chunk-(\d{4})(\.jsonl|\.certificate\.json)$/;
  const pairs = new Map(), errors = [];
  names.forEach(function (name) {
    const match = name.match(allowed);
    if (!match) { errors.push("unknown checkpoint-directory entry: " + name); return; }
    const index = Number(match[1]);
    if (index < 0 || index >= Screening.EXPECTED_CHUNKS) { errors.push("out-of-range checkpoint index: " + name); return; }
    if (!pairs.has(index)) pairs.set(index, {});
    const key = match[2] === ".jsonl" ? "chunk" : "certificate";
    if (pairs.get(index)[key]) errors.push("duplicate checkpoint role for index " + index);
    pairs.get(index)[key] = path.join(paths.chunks, name);
  });
  const indices = Array.from(pairs.keys()).sort(function (a, b) { return a - b; });
  indices.forEach(function (index, position) {
    if (index !== position) errors.push("checkpoint prefix has a gap at index " + position);
    const pair = pairs.get(index);
    if (!pair.chunk || !pair.certificate) errors.push("orphan checkpoint chunk/certificate at index " + index);
  });
  if (errors.length) throw new Error(errors.join("; "));
  const entries = [], records = [];
  indices.forEach(function (index) {
    const pair = pairs.get(index), chunkBytes = fs.readFileSync(pair.chunk), certificateBytes = fs.readFileSync(pair.certificate), chunkPath = relativePath(pair.chunk), certificatePath = relativePath(pair.certificate);
    const report = Screening.validateChunk(chunkBytes, certificateBytes, index, chunkPath, source, { remeasure: options.remeasure !== false });
    if (!report.valid) throw new Error("checkpoint " + index + " validation failed: " + report.errors.join("; "));
    entries.push({ index: index, chunkPath: chunkPath, certificatePath: certificatePath, chunkBytes: chunkBytes, certificateBytes: certificateBytes, certificate: report.certificate, records: report.records });
    records.push.apply(records, report.records);
  });
  return { entries: entries, records: records };
}

function createChunk(paths, index, source) {
  const census = Screening.Base.expectedCensus(), start = index * Screening.CHUNK_SIZE, records = [];
  for (let offset = 0; offset < Screening.CHUNK_SIZE; offset += 1) records.push(Screening.buildRecord(census[start + offset]));
  const chunkBytes = Screening.serializeCanonicalJsonl(records), locations = chunkPaths(paths, index), chunkPath = relativePath(locations.chunk), certificatePath = relativePath(locations.certificate);
  const certificate = Screening.buildChunkCertificate(index, records, chunkBytes, chunkPath, source), certificateBytes = Screening.serializeJsonArtifact(certificate);
  const preflight = Screening.validateChunk(chunkBytes, certificateBytes, index, chunkPath, source, { remeasure: true });
  if (!preflight.valid) throw new Error("new checkpoint " + index + " preflight failed: " + preflight.errors.join("; "));
  durableWriteNoReplace(locations.chunk, chunkBytes);
  durableWriteNoReplace(locations.certificate, certificateBytes);
  const postflight = Screening.validateChunk(fs.readFileSync(locations.chunk), fs.readFileSync(locations.certificate), index, chunkPath, source, { remeasure: true });
  if (!postflight.valid) throw new Error("new checkpoint " + index + " postflight failed: " + postflight.errors.join("; "));
  return { index: index, chunkPath: chunkPath, certificatePath: certificatePath, chunkBytes: chunkBytes, certificateBytes: certificateBytes, certificate: certificate, records: records };
}

function buildRuntimeCertificate(context, metrics) {
  const payload = {
    schema: "gg.u2.screening.runtime-certificate/2",
    semanticRole: "non-semantic execution telemetry; excluded from record hashes and scientific summary content address",
    screeningVersion: "screening-v2",
    platformLabel: context.platformLabel,
    supplementDigest: Screening.SUPPLEMENT_DIGEST,
    sourceBoundary: JSON.parse(JSON.stringify(context.source)),
    artifacts: {
      raw: { path: context.rawPath, bytes: context.rawBytes.length, sha256: Screening.sha256Bytes(context.rawBytes) },
      summary: { path: context.summaryPath, bytes: context.summaryBytes.length, sha256: Screening.sha256Bytes(context.summaryBytes), semanticDigest: context.summary.contentAddress.digest },
      checkpointManifest: { path: context.checkpointPath, bytes: context.checkpointBytes.length, sha256: Screening.sha256Bytes(context.checkpointBytes), semanticDigest: context.checkpoint.contentAddress.digest }
    },
    runtime: metrics,
    outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
  };
  return Object.assign({}, payload, { contentAddress: contentAddress(payload) });
}

function validateRuntimeBytes(bytes, context) {
  const report = Screening.validateJsonArtifactBytes(bytes), errors = report.errors.slice(), artifact = report.artifact;
  if (!errors.length) {
    errors.push.apply(errors, validateContentAddress(artifact));
    if (artifact.schema !== "gg.u2.screening.runtime-certificate/2" || artifact.screeningVersion !== "screening-v2" || artifact.platformLabel !== context.platformLabel) errors.push("runtime identity mismatch");
    if (artifact.supplementDigest !== Screening.SUPPLEMENT_DIGEST || Screening.canonicalStringify(artifact.sourceBoundary) !== Screening.canonicalStringify(context.source)) errors.push("runtime source/supplement binding mismatch");
    const expectedArtifacts = {
      raw: { path: context.rawPath, bytes: context.rawBytes.length, sha256: Screening.sha256Bytes(context.rawBytes) },
      summary: { path: context.summaryPath, bytes: context.summaryBytes.length, sha256: Screening.sha256Bytes(context.summaryBytes), semanticDigest: context.summary.contentAddress.digest },
      checkpointManifest: { path: context.checkpointPath, bytes: context.checkpointBytes.length, sha256: Screening.sha256Bytes(context.checkpointBytes), semanticDigest: context.checkpoint.contentAddress.digest }
    };
    if (Screening.canonicalStringify(artifact.artifacts) !== Screening.canonicalStringify(expectedArtifacts)) errors.push("runtime raw/summary/checkpoint bindings mismatch");
    if (!artifact.outcome || artifact.outcome.u2Status !== "UNRESOLVED" || artifact.outcome.decisionAuthority !== "NONE") errors.push("runtime outcome is not fail-closed");
  }
  return { valid: errors.length === 0, errors: errors, artifact: artifact };
}

function ensureFinal(output, expectedBytes, resume) {
  if (fs.existsSync(output)) {
    if (!resume) throw new Error("existing final artifact refuses non-resume execution: " + output);
    const existing = fs.readFileSync(output);
    if (!existing.equals(expectedBytes)) throw new Error("existing final artifact collision: " + output);
    return "EXISTING_IDENTICAL_VALIDATED";
  }
  return durableWriteNoReplace(output, expectedBytes);
}

function finalContext(paths, platformLabel, source, entries, records) {
  if (entries.length !== Screening.EXPECTED_CHUNKS || records.length !== Screening.EXPECTED_RECORDS) throw new Error("final assembly requires all checkpoint records");
  const rawBytes = Buffer.concat(entries.map(function (entry) { return entry.chunkBytes; })), rawPath = relativePath(paths.raw), rawReport = Screening.parseCanonicalJsonl(rawBytes, { expectedCount: Screening.EXPECTED_RECORDS });
  if (!rawReport.valid || Screening.canonicalStringify(rawReport.records) !== Screening.canonicalStringify(records)) throw new Error("deterministic final raw assembly failed: " + rawReport.errors.join("; "));
  const checkpointPath = relativePath(paths.checkpointManifest), checkpoint = buildCheckpointManifest(entries, rawBytes, rawPath, source, platformLabel), checkpointBytes = Screening.serializeJsonArtifact(checkpoint);
  const checkpointReport = validateCheckpointManifestBytes(checkpointBytes, entries, rawBytes, rawPath, source, platformLabel);
  if (!checkpointReport.valid) throw new Error("checkpoint manifest preflight failed: " + checkpointReport.errors.join("; "));
  const checkpointBinding = { path: checkpointPath, bytes: checkpointBytes.length, sha256: Screening.sha256Bytes(checkpointBytes), semanticDigest: checkpoint.contentAddress.digest };
  const summaryPath = relativePath(paths.summary), summary = Screening.buildSummary(records, { path: rawPath, bytes: rawBytes.length, sha256: Screening.sha256Bytes(rawBytes) }, { sourceBoundary: source, checkpointManifest: checkpointBinding }), summaryBytes = Screening.serializeJsonArtifact(summary);
  const summaryReport = Screening.validateSummaryBytes(summaryBytes, records, rawBytes, rawPath, { sourceBoundary: source, checkpointManifest: checkpointBinding }, { remeasure: true });
  if (!summaryReport.valid) throw new Error("summary preflight failed: " + summaryReport.errors.join("; "));
  return { rawBytes: rawBytes, rawPath: rawPath, checkpoint: checkpoint, checkpointBytes: checkpointBytes, checkpointPath: checkpointPath, checkpointBinding: checkpointBinding, summary: summary, summaryBytes: summaryBytes, summaryPath: summaryPath };
}

function validateAllFinals(paths, platformLabel, source, entries, records) {
  const context = finalContext(paths, platformLabel, source, entries, records);
  const rawBytes = fs.readFileSync(paths.raw), checkpointBytes = fs.readFileSync(paths.checkpointManifest), summaryBytes = fs.readFileSync(paths.summary), runtimeBytes = fs.readFileSync(paths.runtime);
  if (!rawBytes.equals(context.rawBytes)) throw new Error("final raw bytes differ from deterministic chunk assembly");
  const checkpointReport = validateCheckpointManifestBytes(checkpointBytes, entries, rawBytes, context.rawPath, source, platformLabel);
  if (!checkpointReport.valid) throw new Error("checkpoint manifest validation failed: " + checkpointReport.errors.join("; "));
  if (!checkpointBytes.equals(context.checkpointBytes)) throw new Error("checkpoint manifest bytes differ from deterministic rebuild");
  const summaryReport = Screening.validateSummaryBytes(summaryBytes, records, rawBytes, context.rawPath, { sourceBoundary: source, checkpointManifest: context.checkpointBinding }, { remeasure: true });
  if (!summaryReport.valid) throw new Error("summary validation failed: " + summaryReport.errors.join("; "));
  if (!summaryBytes.equals(context.summaryBytes)) throw new Error("summary bytes differ from deterministic rebuild");
  const runtimeContext = { platformLabel: platformLabel, source: source, rawPath: context.rawPath, rawBytes: rawBytes, summaryPath: context.summaryPath, summaryBytes: summaryBytes, summary: summaryReport.summary, checkpointPath: context.checkpointPath, checkpointBytes: checkpointBytes, checkpoint: checkpointReport.artifact };
  const runtimeReport = validateRuntimeBytes(runtimeBytes, runtimeContext);
  if (!runtimeReport.valid) throw new Error("runtime validation failed: " + runtimeReport.errors.join("; "));
  return { context: context, runtime: runtimeReport.artifact, runtimeBytes: runtimeBytes };
}

function assertNoV2Outputs(paths) {
  if (!fs.existsSync(paths.directory)) return;
  const entries = fs.readdirSync(paths.directory).filter(function (name) { return name !== ".run-lock.json"; });
  if (entries.length) throw new Error("existing screening-v2 output refuses a new non-resume run: " + entries.sort().join(","));
}

function run(options) {
  Screening.loadPrerequisites();
  assertSourceModePolicy(options.sourceMode);
  const sourceLoaded = loadSource(options), source = sourceLoaded.source, paths = pathsFor(options.platformLabel);
  const operation = options.validateOnly ? "validate-only" : (options.resume ? "resume" : "fresh"), lock = acquireRunLock(paths, options.platformLabel, source, operation);
  try {
    if (options.validateOnly) {
    const discovered = discoverChunks(paths, source, { remeasure: true });
    if (discovered.entries.length !== Screening.EXPECTED_CHUNKS) throw new Error("validate-only requires all 120 checkpoint chunks");
    const validated = validateAllFinals(paths, options.platformLabel, source, discovered.entries, discovered.records);
    process.stdout.write(JSON.stringify({ mode: "validate-only", chunks: discovered.entries.length, records: discovered.records.length, rawSha256: Screening.sha256Bytes(validated.context.rawBytes), summaryDigest: validated.context.summary.contentAddress.digest, runtimeDigest: validated.runtime.contentAddress.digest, u2Status: "UNRESOLVED" }) + "\n");
    return;
    }
    if (!options.resume) assertNoV2Outputs(paths);
    const started = performance.now(), startWallTime = new Date().toISOString(), recovered = options.resume ? discoverChunks(paths, source, { remeasure: true }) : { entries: [], records: [] }, entries = recovered.entries.slice(), records = recovered.records.slice();
    let peakRssBytes = process.memoryUsage().rss;
    for (let index = entries.length; index < Screening.EXPECTED_CHUNKS; index += 1) {
      const entry = createChunk(paths, index, source); entries.push(entry); records.push.apply(records, entry.records); peakRssBytes = Math.max(peakRssBytes, process.memoryUsage().rss);
      process.stderr.write(JSON.stringify({ checkpointChunk: index, completedRecords: records.length, totalRecords: Screening.EXPECTED_RECORDS, elapsedSeconds: (performance.now() - started) / 1000, peakRssBytes: peakRssBytes }) + "\n");
    }
    const context = finalContext(paths, options.platformLabel, source, entries, records), dispositions = {};
    dispositions.checkpointManifest = ensureFinal(paths.checkpointManifest, context.checkpointBytes, options.resume);
    dispositions.raw = ensureFinal(paths.raw, context.rawBytes, options.resume);
    dispositions.summary = ensureFinal(paths.summary, context.summaryBytes, options.resume);
    const runtimeContext = { platformLabel: options.platformLabel, source: source, rawPath: context.rawPath, rawBytes: context.rawBytes, summaryPath: context.summaryPath, summaryBytes: context.summaryBytes, summary: context.summary, checkpointPath: context.checkpointPath, checkpointBytes: context.checkpointBytes, checkpoint: context.checkpoint };
    if (fs.existsSync(paths.runtime)) {
      if (!options.resume) throw new Error("existing runtime certificate refuses non-resume execution");
      const existingRuntime = fs.readFileSync(paths.runtime), report = validateRuntimeBytes(existingRuntime, runtimeContext);
      if (!report.valid) throw new Error("existing runtime certificate collision: " + report.errors.join("; "));
      dispositions.runtime = "EXISTING_VALIDATED";
    } else {
      const metrics = { startWallTime: startWallTime, endWallTime: new Date().toISOString(), elapsedMilliseconds: performance.now() - started, recoveredChunkCount: recovered.entries.length, generatedChunkCount: Screening.EXPECTED_CHUNKS - recovered.entries.length, staleLockRecovery: lock.recovery, validationPolicy: "full semantic replay at chunk preflight/postflight, final assembly, and final post-write validation", peakRssBytes: peakRssBytes, environment: { platform: process.platform, arch: process.arch, node: process.version, cpuCount: os.cpus().length } };
      const runtime = buildRuntimeCertificate(runtimeContext, metrics), runtimeBytes = Screening.serializeJsonArtifact(runtime), runtimeReport = validateRuntimeBytes(runtimeBytes, runtimeContext);
      if (!runtimeReport.valid) throw new Error("runtime certificate preflight failed: " + runtimeReport.errors.join("; "));
      dispositions.runtime = durableWriteNoReplace(paths.runtime, runtimeBytes);
    }
    const final = validateAllFinals(paths, options.platformLabel, source, entries, records);
    process.stdout.write(JSON.stringify({ mode: options.resume ? "resume" : "fresh", dispositions: dispositions, chunks: entries.length, records: records.length, rawSha256: Screening.sha256Bytes(final.context.rawBytes), summaryDigest: final.context.summary.contentAddress.digest, runtimeDigest: final.runtime.contentAddress.digest, sourceBoundaryDigest: source.semanticDigest, u2Status: "UNRESOLVED" }) + "\n");
  } finally {
    releaseRunLock(lock);
  }
}

if (require.main === module) run(parseArgs(process.argv.slice(2)));
module.exports = {
  parseArgs: parseArgs,
  pathsFor: pathsFor,
  chunkPaths: chunkPaths,
  fsyncDirectory: fsyncDirectory,
  durableWriteNoReplace: durableWriteNoReplace,
  gitExecutableAvailable: gitExecutableAvailable,
  assertSourceModePolicy: assertSourceModePolicy,
  resolveHostIdentity: resolveHostIdentity,
  buildRunLock: buildRunLock,
  validateRunLockBytes: validateRunLockBytes,
  probePid: probePid,
  staleLockPaths: staleLockPaths,
  recoveryClaimPath: recoveryClaimPath,
  acquireRecoveryClaim: acquireRecoveryClaim,
  releaseRecoveryClaim: releaseRecoveryClaim,
  buildStaleLockRecoveryCertificate: buildStaleLockRecoveryCertificate,
  validateStaleLockRecoveryCertificateBytes: validateStaleLockRecoveryCertificateBytes,
  recoverStaleRunLock: recoverStaleRunLock,
  acquireRunLock: acquireRunLock,
  releaseRunLock: releaseRunLock,
  loadSource: loadSource,
  buildCheckpointManifest: buildCheckpointManifest,
  validateCheckpointManifestBytes: validateCheckpointManifestBytes,
  discoverChunks: discoverChunks,
  createChunk: createChunk,
  buildRuntimeCertificate: buildRuntimeCertificate,
  validateRuntimeBytes: validateRuntimeBytes,
  ensureFinal: ensureFinal,
  finalContext: finalContext,
  validateAllFinals: validateAllFinals,
  run: run
};
