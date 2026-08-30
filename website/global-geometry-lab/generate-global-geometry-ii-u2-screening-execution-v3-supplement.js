#!/usr/bin/env node
"use strict";

/*
 * Outcome-blind semantic-and-execution supplement for screening-execution-v3.
 * The frozen screening-v2 kernel is the bound construction/measurement base.
 * V3 applies one disclosed control-ledger repair and a portable execution
 * container; it does not alter a numerical estimator, threshold, or census.
 */

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");
const BINDINGS = Object.freeze({
  repairAudit: {
    path: "GLOBAL_GEOMETRY_II_EVALUATION_REPAIR_AUDIT.md",
    bytes: 9042,
    fileSha256: "3810154ff591ca42a0e85d4ceb90900c09f85e79a6e3ff403525003bac6e0313",
    semanticSha256: null
  },
  semanticSupplement: {
    path: "artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v3.json",
    bytes: 10114,
    fileSha256: "3bd284f7b19a5c4caa790c3e25a177a603e81e74e265a526cc99407a691b18da",
    semanticSha256: "21d69b11b12277e228e2934e033fd8f366b3c8d5d89f1b8833aa781a36118888"
  },
  semanticKernel: {
    path: "website/global-geometry-lab/global-geometry-ii-u2-screening-v2.js",
    bytes: 18980,
    fileSha256: "3976809ec412580975852540166147d870c354672d055e243861ea7046e19873",
    semanticSha256: null
  },
  semanticSourceBoundary: {
    path: "artifacts/global-geometry-ii/u2/screening/screening-v2/source-boundary-v2.json",
    bytes: 4594,
    fileSha256: "c60331209247fccee700d10d38b9ae03da3f81e9013f19281a1f5918fb9e6c73",
    semanticSha256: "a1b1b9bb525ba9c172be48af60b9881a13ce58ebed9862a60fec18a25f07fae0"
  },
  windowsV2Abort: {
    path: "artifacts/global-geometry-ii/u2/screening/screening-windows-preflight-abort-v2.json",
    bytes: null,
    fileSha256: "7550c5fec0aff5744a51e59e5958c45e363e5e6e0a49946c98307c4c6f1d7528",
    semanticSha256: "50108bc66bf8807772f9fef21baa35eea3e178e621de1958a9b7ddaef7ad6865"
  }
});

const SEMANTIC_IMPLEMENTATION_COMMIT = "1c3373267057b8a018ad5039e0f3b2b4e8eb2b1d";
const SEMANTIC_BOUNDARY_COMMIT = "ed624f4ff42b4e5488a1889c3d55ba1195e5a952";

function sha256Bytes(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function canonicalStringify(value) {
  if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isFinite(value) || Object.is(value, -0)) throw new Error("invalid canonical number");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return "[" + value.map(canonicalStringify).join(",") + "]";
  if (!value || typeof value !== "object" || Object.getPrototypeOf(value) !== Object.prototype) throw new Error("canonical values must be plain JSON");
  return "{" + Object.keys(value).sort().map(function (key) { return JSON.stringify(key) + ":" + canonicalStringify(value[key]); }).join(",") + "}";
}

function bind(entry) {
  const bytes = fs.readFileSync(path.join(ROOT, entry.path));
  if (entry.bytes !== null && bytes.length !== entry.bytes) throw new Error(entry.path + " byte count mismatch");
  if (sha256Bytes(bytes) !== entry.fileSha256) throw new Error(entry.path + " file digest mismatch");
  let semanticContentAddress = null;
  if (entry.semanticSha256) {
    const artifact = JSON.parse(bytes.toString("utf8"));
    if (!artifact.contentAddress || artifact.contentAddress.digest !== entry.semanticSha256) throw new Error(entry.path + " semantic digest mismatch");
    semanticContentAddress = entry.semanticSha256;
  }
  return { path: entry.path, bytes: bytes.length, sha256: entry.fileSha256, semanticContentAddress: semanticContentAddress };
}

function buildPayload() {
  return {
    schema: "gg.u2.screening.execution-supplement/3",
    supplementId: "ggii-u2-screening-execution-v3-portability-v1",
    status: {
      frozenBeforeAnyScreeningV3Outcome: true,
      screeningV2ScientificValuesReadBeforeFreeze: false,
      windowsV2FailureStage: "BLOCKED_BEFORE_RECORD_0",
      criteriaMutableAfterFreeze: false,
      forcedU2Status: "UNRESOLVED",
      decisionAuthority: "NONE"
    },
    bindings: {
      governingRepairAudit: bind(BINDINGS.repairAudit),
      semanticSupplement: bind(BINDINGS.semanticSupplement),
      semanticKernel: bind(BINDINGS.semanticKernel),
      semanticSourceBoundary: bind(BINDINGS.semanticSourceBoundary),
      windowsV2Abort: bind(BINDINGS.windowsV2Abort),
      semanticImplementationCommit: SEMANTIC_IMPLEMENTATION_COMMIT,
      semanticBoundaryCommit: SEMANTIC_BOUNDARY_COMMIT
    },
    versionSeparation: {
      semanticBaseVersion: "screening-v2",
      semanticPayloadVersion: "screening-v3",
      semanticRecordSchema: "gg.u2.screening.record/3",
      executionVersion: "screening-v3",
      outputRoot: "artifacts/global-geometry-ii/u2/screening/screening-v3/{platform}",
      invariant: "every v3 raw record is rebuilt by applying the closed v3 small-world ledger adapter to a fresh frozen-v2 base record, followed by v3 identity and hash construction",
      prohibition: "no v2 artifact is overwritten, resumed, assembled into v3, relabeled, or granted new decision authority"
    },
    repairScope: {
      numericalEstimatorChange: "NONE",
      censusSeedThresholdOrControlChange: "NONE",
      semanticRepair: "when the small-world discriminant has no bulk roots, restore targetShortcutCount from construction.metadata, re-evaluate only the small-world shortcut-count shortfall against that target, and recompute declaredParametersRealized",
      semanticRepairReason: "the frozen v2 early-return discriminant omitted targetShortcutCount, so equality against undefined emitted a spurious control-shortfall even when the constructor realized its declared target",
      executionRepairReason: "Windows Node v22.22.2 returned EPERM when fsync was attempted through a read-only final-file handle after hard-link publication",
      allowedChange: "the closed small-world ledger adapter, v3 record identity/hash, execution containment, writable-handle fsync, directory-fsync capability disclosure, and v3 container metadata only",
      comparisonPolicy: "primary cross-platform evidence is a clean macOS v3 run and a clean Windows v3 run from one v3 source boundary"
    },
    portableDurability: {
      algorithm: "write an exclusive temporary file through wx+, fsync its retained writable handle, publish by same-filesystem hard link with no replacement, fsync that retained handle again, reopen the final path through r+ and fsync, verify exact bytes, then remove the temporary name",
      directoryPolicy: {
        posix: "directory fsync is mandatory after final-link publication and temporary-name removal",
        win32: "Node does not portably expose a flushable directory handle; record DIRECTORY_BARRIER_UNAVAILABLE_WIN32, require exact final-byte postflight, and fail closed on every orphan or collision"
      },
      overwritePolicy: "all chunks, certificates, finals, locks, claims, and source boundaries are create-once and never replace existing bytes",
      crashPolicy: "complete chunk/certificate pairs may resume; orphan, partial, unknown, colliding, or noncanonical bytes refuse; a crash-leaked recovery claim requires manual audit",
      productionPreflight: "the exact v3 writer must pass create/fsync/link/postflight/collision tests on each host before record 0"
    },
    containerSchemas: {
      chunkCertificate: "gg.u2.screening.chunk-certificate/3",
      checkpointManifest: "gg.u2.screening.checkpoint-manifest/3",
      summaryEnvelope: "gg.u2.screening.summary-envelope/3",
      runtimeCertificate: "gg.u2.screening.runtime-certificate/3",
      runLock: "gg.u2.screening.run-lock/3",
      recoveryClaim: "gg.u2.screening.recovery-claim/3",
      recoveryCertificate: "gg.u2.screening.stale-lock-recovery/3",
      sourceBoundary: "gg.u2.screening.source-boundary/3"
    },
    requiredTests: [
      "fresh v2-base plus closed v3 adapter replay for every v3 record",
      "small-world no-bulk-root cases restore targetShortcutCount, remove no genuine shortfall, and set declaredParametersRealized exactly",
      "writable final-handle fsync and exact postflight",
      "POSIX directory fsync and explicit win32 directory-capability record",
      "overwrite, hard-link, temporary-name, archive, and certificate collision refusal",
      "orphan/gap/unknown-file refusal",
      "validated-prefix resume byte equality",
      "exclusive run lock, host-bound dead-PID recovery, and recovery-claim serialization",
      "full v3 summary-envelope and checkpoint deterministic rebuild",
      "source-boundary Git and portable mutation rejection"
    ],
    outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
  };
}

function buildSupplement() {
  const payload = buildPayload(), canonical = canonicalStringify(payload);
  return Object.assign({}, payload, { contentAddress: { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: sha256Bytes(Buffer.from(canonical, "utf8")), canonicalBytes: Buffer.byteLength(canonical, "utf8") } });
}

function validateSupplement(artifact) {
  const errors = [];
  try {
    const expected = buildSupplement();
    if (canonicalStringify(artifact) !== canonicalStringify(expected)) errors.push("supplement differs from deterministic full-payload rebuild");
    if (!artifact || !artifact.contentAddress) errors.push("contentAddress missing");
    else {
      const payload = JSON.parse(JSON.stringify(artifact)); delete payload.contentAddress;
      const canonical = canonicalStringify(payload);
      if (artifact.contentAddress.digest !== sha256Bytes(Buffer.from(canonical, "utf8")) || artifact.contentAddress.canonicalBytes !== Buffer.byteLength(canonical, "utf8")) errors.push("contentAddress mismatch");
    }
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

if (require.main === module) process.stdout.write(JSON.stringify(buildSupplement(), null, 2) + "\n");
module.exports = { ROOT: ROOT, BINDINGS: BINDINGS, buildSupplement: buildSupplement, validateSupplement: validateSupplement, canonicalStringify: canonicalStringify, sha256Bytes: sha256Bytes };
