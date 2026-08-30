#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");
const BINDINGS = Object.freeze({
  base: {
    path: "artifacts/global-geometry-ii/u2/screening/screening-manifest-v1.json",
    fileSha256: "2b60f5ca51bfa37c7de068b92928c17664b36f81ff931a8851316b47f135cc25",
    semanticSha256: "25fea0bad6f4b60ae27a75fd13c13be117c28a288a5f6b3bd9e25859c4b1d309"
  },
  implementationV2: {
    path: "artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v2.json",
    fileSha256: "5380552dc7c6ee91d6e632b7bfec6a6031d49ab0b98a2aa6f95b71b4c73ab8d6",
    semanticSha256: "7d948db5996eb025c949d1bdfe73ce8cf29b10a77904ca2558b1a6d601301b8c"
  },
  pilotAbort: {
    path: "artifacts/global-geometry-ii/u2/screening/screening-pilot-abort-macos-v1.json",
    fileSha256: "ce1f7100730a68775fcc80f8fa6155f8b97b48dd9c6aa5e64d14461c0dd25228",
    semanticSha256: "8db910463c3fbf0fa0e4610ffdba6e6c4c7b70bf04e99ae91bce2f811e2d9166"
  },
  repairAudit: {
    path: "GLOBAL_GEOMETRY_II_EVALUATION_REPAIR_AUDIT.md",
    fileSha256: "3810154ff591ca42a0e85d4ceb90900c09f85e79a6e3ff403525003bac6e0313",
    semanticSha256: null
  }
});

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
    schema: "gg.u2.screening.implementation-supplement/3",
    supplementId: "ggii-u2-v2-screening-implementation-v3",
    status: {
      frozenBeforeAnyScreeningV2Outcome: true,
      scientificValuesFromAbortedPilotReadBeforeFreeze: false,
      criteriaMutableAfterFreeze: false,
      forcedU2Status: "UNRESOLVED",
      decisionAuthority: "NONE",
      supersedesImplementationSupplement: "ggii-u2-v2-screening-implementation-v2"
    },
    bindings: {
      baseScreeningManifest: bind(BINDINGS.base),
      priorImplementationSupplement: bind(BINDINGS.implementationV2),
      abortedPilotMetadata: bind(BINDINGS.pilotAbort),
      governingRepairAudit: bind(BINDINGS.repairAudit),
      governingRepairAuditCommit: "c2bc19072c29c3e8f76b190dd598307d70f843a3",
      abortedPilotSourceBoundaryCommit: "1fb1f6c100f90dd40f27764689547ed2a47d19dd"
    },
    independenceAccounting: {
      positiveCells: {
        deterministicCarrierFamilies: ["square-alternating", "triangular-clipped", "cell-center-fan"],
        deterministicCarrierCountEveryCell: 1,
        hashedCarrierCountEveryCell: 32,
        deterministicSigmaZero: {
          conductanceRealizationCount: 1,
          jointWeightedRealizationCount: 1,
          randomizedNestedMeasurementBatchCount: 32,
          repeatedDeterministicEvaluationCount: 0
        },
        deterministicPositiveSigma: {
          conductanceRealizationCount: 32,
          jointWeightedRealizationCount: 32,
          randomizedNestedMeasurementBatchCount: 0,
          repeatedDeterministicEvaluationCount: 0
        },
        hashedSigmaZero: {
          conductanceRealizationCount: 1,
          jointWeightedRealizationCount: 32,
          randomizedNestedMeasurementBatchCount: 0,
          repeatedDeterministicEvaluationCount: 0
        },
        hashedPositiveSigma: {
          conductanceRealizationCount: 32,
          jointWeightedRealizationCount: 32,
          randomizedNestedMeasurementBatchCount: 0,
          repeatedDeterministicEvaluationCount: 0
        }
      },
      controls: {
        "comb-trap": { carrierConstructionRealizationCount: 1, randomizedNestedMeasurementBatchCount: 32, repeatedDeterministicEvaluationCount: 0 },
        "vanishing-neck": { carrierConstructionRealizationCount: 1, randomizedNestedMeasurementBatchCount: 0, repeatedDeterministicEvaluationCount: 31 },
        "small-world-shortcuts": { carrierConstructionRealizationCount: 32, randomizedNestedMeasurementBatchCount: 0, repeatedDeterministicEvaluationCount: 0 },
        "perforated-disk": { carrierConstructionRealizationCount: 32, randomizedNestedMeasurementBatchCount: 0, repeatedDeterministicEvaluationCount: 0 }
      },
      requiredSummaryFields: [
        "carrierConstructionRealizationCount",
        "conductanceRealizationCount",
        "jointWeightedRealizationCount",
        "randomizedNestedMeasurementBatchCount",
        "repeatedDeterministicEvaluationCount",
        "measurementBatchCount",
        "uniqueStructureDigestCount",
        "uniqueWeightDigestCount",
        "uniqueJointDigestCount"
      ]
    },
    durableCheckpointContract: {
      outputVersion: "screening-v2",
      chunkSizeRecords: 32,
      chunkCount: 120,
      chunkFiles: "screening-v2/{platform}/chunks/chunk-{0000..0119}.jsonl",
      certificateFiles: "screening-v2/{platform}/chunks/chunk-{0000..0119}.certificate.json",
      durability: "write each chunk and certificate through exclusive temporary files, fsync file, atomic rename without replacement, then fsync parent directory",
      chunkValidation: "exact census ordinals, exact canonical JSON line bytes, exactly one terminal LF, full semantic record replay, chunk SHA-256/bytes/Merkle root, certificate content address, and source-boundary binding",
      resume: "--resume accepts only a contiguous validated prefix of complete chunk/certificate pairs; gaps, unknown files, orphan pairs, collisions, changed source boundary, or invalid bytes refuse execution",
      collisionPolicy: "without --resume any existing v2 checkpoint or final artifact refuses execution; with --resume no existing byte may be replaced",
      exclusiveRunLock: "fresh, resume, and validate-only operations exclusively create and fsync screening-v2/{platform}/.run-lock.json before inspecting platform outputs; locks bind creator hostname, platform, and architecture; an existing lock refuses fresh and validate-only; resume may recover it only while holding a separate no-replace recovery claim, after exact lock validation, exact platform/source/current-host match, and definitive local dead-PID proof; recovery archives the original lock and a content-addressed proof certificate write-once before ownership-checked unlink; the claim remains held until the replacement active lock is durable; a crash-leaked claim fails closed pending manual audit; normal completion verifies ownership, removes the active lock, and fsyncs the directory",
      finalAssembly: "validate all 120 chunks in ordinal order and concatenate their exact bytes deterministically; final raw output is written exclusively and never overwrites"
    },
    validationRepairs: {
      canonicalJsonl: "UTF-8 canonical JSON on every nonempty line, no CR, exactly one LF after the final record, and byte-for-byte reserialization equality",
      recordReplay: "rebuild the full record, compare full canonical supplied and rebuilt payloads, and independently require supplied and rebuilt record hashes",
      controlRealization: "construction.declaredParametersRealized is true exactly when the record failure ledger has no control-shortfall entry, and validators enforce the biconditional",
      summary: "deterministic full-payload rebuild from validated records and raw binding",
      runtime: "validate runtime content address and exact source-boundary, raw path/bytes/SHA-256, summary path/bytes/SHA-256/semantic digest, checkpoint-manifest digest, platform, and forced UNRESOLVED bindings in normal and validate-only modes",
      finalArtifacts: "raw, summary, runtime, checkpoint manifest, every chunk, and every chunk certificate use no-overwrite creation",
      exactJsonArtifactBytes: "summary, runtime, checkpoint manifest, chunk certificates, and source boundary use UTF-8 JSON.stringify(artifact,null,2) followed by exactly one LF; validators compare supplied bytes to that exact serialization in addition to semantic checks"
    },
    portableSourceBoundary: {
      sourceSnapshotVersion: "gg.u2.screening.source-boundary/2",
      generationStage: "after the implementation commit and before any screening-v2 outcome",
      twoStageFreeze: "implementation commit C1 contains source and this supplement; source-boundary artifact then binds C1 plus exact source-file hashes and is frozen before production",
      gitMode: "when Git is available, require C1 to be a commit and require every listed source byte sequence to equal C1:path",
      portableMode: "when Git is unavailable, require every local source/preregistration byte sequence and size to equal the content-addressed source-boundary manifest; retain the exact C1 commit string as provenance",
      portableAvailabilityGuard: "the runner refuses portable mode whenever the Git executable is available; a Git verification failure never authorizes portable fallback",
      prohibitedFallback: "never silently weaken Git verification after a Git command or commit/path check fails",
      sourceBoundaryRequiredForChunksAndFinals: true
    },
    abortedPilotPolicy: {
      partialPath: BINDINGS.pilotAbort.path.replace("screening-pilot-abort-macos-v1.json", "screening-raw-macos-v1.jsonl.partial-950"),
      recordLineCount: 3589,
      scientificParsingProhibited: true,
      resumeOrAssemblyProhibited: true,
      inferentialUse: "NONE"
    },
    testingRequirements: {
      mutationCases: [
        "carrier-versus-conductance-count conflation",
        "vanishing-neck randomized-nested mislabel",
        "checkpoint byte mutation",
        "checkpoint gap/orphan/collision",
        "runtime raw/summary/source redirect",
        "noncanonical JSONL or extra/missing terminal LF",
        "freshly rehashed record payload mutation",
        "portable source-file mutation",
        "Git failure disguised as portable fallback",
        "live, unknown, remote-host, mismatched, colliding, changed-during-probe, or unaudited stale run-lock recovery",
        "competing or crash-leaked exclusive recovery claim",
        "crash after one validated chunk followed by byte-identical resume",
        "final artifact overwrite"
      ],
      productionGuard: "all implementation and adversarial tests pass before a source-boundary artifact is generated; no scientific production is authorized by this supplement alone"
    }
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
module.exports = { ROOT: ROOT, buildSupplement: buildSupplement, validateSupplement: validateSupplement, canonicalStringify: canonicalStringify, sha256Bytes: sha256Bytes };
