#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");
const BASE_PATH = "artifacts/global-geometry-ii/u2/screening/screening-manifest-v1.json";
const BASE_FILE_SHA256 = "2b60f5ca51bfa37c7de068b92928c17664b36f81ff931a8851316b47f135cc25";
const BASE_SEMANTIC_SHA256 = "25fea0bad6f4b60ae27a75fd13c13be117c28a288a5f6b3bd9e25859c4b1d309";
const PREREGISTRATION_COMMIT = "150e4e7cb96b960a21923f4b2c2b3573e272dcf5";

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

function binding(relativePath, expectedSha256) {
  const bytes = fs.readFileSync(path.join(ROOT, relativePath));
  const digest = sha256Bytes(bytes);
  if (digest !== expectedSha256) throw new Error(relativePath + " differs from the frozen supplement binding");
  return { path: relativePath, sha256: digest, bytes: bytes.length };
}

function payload() {
  const base = binding(BASE_PATH, BASE_FILE_SHA256);
  const baseArtifact = JSON.parse(fs.readFileSync(path.join(ROOT, BASE_PATH), "utf8"));
  if (!baseArtifact.contentAddress || baseArtifact.contentAddress.digest !== BASE_SEMANTIC_SHA256) throw new Error("base screening semantic digest mismatch");
  return {
    schema: "gg.u2.screening.implementation-supplement/2",
    supplementId: "ggii-u2-v2-screening-implementation-v2",
    status: {
      frozenBeforeProductionScreeningOutcomes: true,
      criteriaMutableAfterFreeze: false,
      supplementsWithoutOverwriting: "ggii-u2-v2-screening-v1",
      supersedesOutcomeBlindDraft: "ggii-u2-v2-screening-implementation-v1",
      forcedU2Status: "UNRESOLVED",
      decisionAuthority: "NONE"
    },
    bindings: {
      baseScreeningManifest: Object.assign({}, base, { semanticContentAddress: BASE_SEMANTIC_SHA256 }),
      preregistrationCommit: PREREGISTRATION_COMMIT
    },
    scalablePositiveConstructors: {
      common: {
        storage: "one graph at a time; canonical vertices, oriented triangular faces, deduplicated unoriented edges, adjacency lists",
        topologyPrecondition: "Betti output only after connected 1-skeleton, face-connectedness, edge incidence in {1,2}, two-regular boundary components, valid path/cycle vertex links, coherent adjacent-face orientation, and nonempty boundary all validate",
        structureDigest: "SHA-256 stream over ordered canonical vertices, edges, and oriented faces"
      },
      "square-alternating": "Vertices (x,y) for integer 0<=x,y<=L. Every unit cell has two triangles; southwest-northeast diagonal iff (x+y) mod 2=0, otherwise northwest-southeast.",
      "square-hashed-diagonal": "Same integer square vertices. Cell (x,y) uses southwest-northeast iff gg-sha256-object-u53-v1(constructionStream,'cell:y:x',0)<1/2.",
      "cell-center-fan": "Integer square vertices plus one center (x+1/2,y+1/2) per cell; four counterclockwise triangles join each center to the four cell sides.",
      "triangular-clipped": "Equilateral rows at y=r*sqrt(3)/2, alternating x offset 0 or 1/2; floor(2L/sqrt(3)) strips; the maximal elementary-triangle patch follows the four-loop row-parity algorithm in global-geometry-ii-ensembles.js.",
      previewOverlapTest: {
        referenceModule: "website/global-geometry-lab/global-geometry-ii-ensembles.js",
        sizes: [2, 4, 8, 16, 24],
        sigma: 0,
        deterministicComparison: "For square-alternating, triangular-clipped, and cell-center-fan, after mapping vertices by exact construction coordinates, vertex coordinates, unoriented edge coordinate-pairs, and unoriented face coordinate-triples must match exactly at every size supported by preview resource caps.",
        hashedComparison: "For square-hashed-diagonal, inject one shared cell-indexed diagonal-decision vector into both constructor test harnesses and require exact coordinate/edge/face equality under that common oracle. Native preview FNV32 and production SHA-u53 streams are intentionally not expected to choose the same realization.",
        nativeHashedTests: "Separately require SHA-u53 determinism, canonical-cell locality, both allowed diagonal motifs only, exact V/E/F counts, and equality after canonical relabeling/reconstruction.",
        mismatchEffect: "implementation invalid; production screening prohibited"
      }
    },
    exactControlAlgorithms: {
      "comb-trap": {
        base: "path backbone x=0..L at y=0",
        attachment: "one path tooth at every backbone vertex",
        rounding: "toothLength=floor(L/4)",
        graph: "backbone horizontal edges plus consecutive vertical tooth edges",
        discriminant: "four fixed central backbone roots, eight walkers/root, lazy unweighted axial MSD at the registered implementation times and final tooth occupation"
      },
      "small-world-shortcuts": {
        base: "(L+1)x(L+1) four-neighbor square grid",
        rounding: "targetShortcutCount=ceil(0.02*vertexCount)",
        pairing: "SHA-256-u53 rank all start vertices; for each unused start in rank order, try counters 0..31 mapping u53 to a candidate vertex",
        acceptance: "candidate differs from start, both endpoints unused, and base Manhattan separation >=L/3",
        fallback: "after 32 failed counters skip the start; realized shortfall is retained and reported, never backfilled by a changed rule",
        discriminant: "accepted count/separation and eight-root ball-count ratio against the identical base graph without shortcuts"
      },
      "vanishing-neck": {
        base: "two L-by-L square-cell patches with lower-left x origins 0 and L+floor(L/4)",
        rounding: "corridorLength=floor(L/4), corridorWidth=2 cells, corridor lower y=floor((L-2)/2)",
        triangulation: "parity-alternating diagonal in every occupied cell, followed by edge deduplication",
        discriminant: "actual corridor counts plus linear-trial energy, layered-series proxy, and minimum registered x-cut ratio"
      },
      "perforated-disk": {
        base: "square-alternating triangulated L-by-L disk",
        candidates: "integer vertices with 3<=x,y<=L-3",
        rounding: "targetHoleCount=floor(0.05*candidateCount)",
        selection: "SHA-256-u53 rank candidates; greedy accept while Chebyshev center separation >=3 until target or exhaustion",
        fallback: "realized shortfall is retained and reported; no separation or density relaxation",
        removal: "remove every triangular face incident to an accepted center, then delete vertices unused by remaining faces",
        discriminant: "actual removed stars/faces/separation, validated exact beta_1 when topology preconditions hold, and largest-component fraction"
      }
    },
    independenceReporting: {
      deterministicSigmaZero: {
        families: ["square-alternating", "triangular-clipped", "cell-center-fan"],
        constructionRealizationCountPerCell: 1,
        nestedMeasurementBatchCountPerCell: 32,
        prohibitedLabel: "n=32 independent geometries"
      },
      hashedSigmaZero: {
        family: "square-hashed-diagonal",
        constructionRealizationCountPerCell: 32,
        nestedMeasurementBatchCountPerRealization: 1
      },
      positiveSigma: {
        constructionOrConductanceRealizationCountPerCell: 32
      },
      summaryRequiredCounts: ["constructionRealizationCount", "nestedMeasurementBatchCount", "uniqueStructureDigestCount"]
    },
    estimatorLanguageCorrections: {
      randomWalk: {
        field: "rootBlockDescriptiveTWidth",
        formula: "mean of four root-block d_w descriptors plus/minus 3.182*sampleSD/sqrt(4)",
        label: "descriptive finite-sample t-width only; not a confidence interval and not a coverage guarantee",
        counts: { rootCount: 4, walkersPerRoot: 8, totalWalkers: 32 },
        prohibitedUses: ["decision Gate 2", "decision Gate 4", "coverage-certified interval", "construction-level inference"]
      },
      volumeGrowth: {
        field: "logLogSlopeDescriptor",
        label: "eight-root graph-hop ball-growth smoke descriptor only, not a dimension estimate or exponent confidence interval",
        prohibitedUses: ["d_V decision", "Gate 2", "Gate 3 profile collapse", "continuum dimension claim"]
      },
      transport: {
        label: "linear trial energy is an upper bound; layered-series and minimum-cut quantities are proxies",
        prohibitedConclusion: "No screening transport observable can establish transport noncollapse, Gate 5 PASS, normalized conductivity equivalence, or a Dirichlet-solver result."
      }
    },
    runtimeQualification: {
      estimateFromBaseManifest: [4, 12],
      unit: "minutes-single-node",
      status: "UNVALIDATED_PLANNING_ESTIMATE",
      promise: false,
      productionTelemetryRequired: ["wall-clock milliseconds", "per-record elapsed milliseconds", "peak RSS bytes", "raw bytes", "failure count"]
    },
    semanticValidation: {
      supplementRule: "Validator must deep-compare the entire supplied artifact to a deterministic rebuild, in addition to checking its content address and bound files.",
      recordRule: "Every record is checked against its exact census identity, deterministically rebuilt streams, fail-closed interpretation, and whole-record SHA-256.",
      summaryRule: "Summary validator checks the full census, record Merkle root, raw-file digest/bytes, content address, and forced UNRESOLVED status.",
      tamperCases: ["freshly readdressed estimator mutation", "control substitution", "decision-binding redirect", "walker-count mutation", "favorable U2 outcome", "record identity or measurement mutation"]
    },
    productionGuard: {
      sourceCommitContainingThisSupplementMustPrecedeRun: true,
      previewOverlapTestsMustPass: true,
      adversarialTamperTestsMustPass: true,
      outputWriteOnce: true
    }
  };
}

function buildSupplement() {
  const body = payload(), canonical = canonicalStringify(body);
  return Object.assign({}, body, { contentAddress: { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: sha256Bytes(Buffer.from(canonical, "utf8")), canonicalBytes: Buffer.byteLength(canonical, "utf8") } });
}

function validateSupplement(artifact) {
  const errors = [];
  try {
    const expected = buildSupplement();
    if (canonicalStringify(artifact) !== canonicalStringify(expected)) errors.push("supplement differs from deterministic full-payload rebuild");
    if (!artifact || !artifact.contentAddress) errors.push("contentAddress missing");
    else {
      const body = JSON.parse(JSON.stringify(artifact)); delete body.contentAddress;
      const canonical = canonicalStringify(body);
      if (artifact.contentAddress.digest !== sha256Bytes(Buffer.from(canonical, "utf8")) || artifact.contentAddress.canonicalBytes !== Buffer.byteLength(canonical, "utf8")) errors.push("contentAddress mismatch");
    }
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function parseOutput(argv) {
  if (!argv.length) return path.join(ROOT, "artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v2.json");
  if (argv.length !== 2 || argv[0] !== "--output" || !argv[1]) throw new Error("usage: generate-global-geometry-ii-u2-screening-supplement.js [--output explicit-path]");
  return path.resolve(argv[1]);
}

function writeOnce(output, bytes) {
  if (fs.existsSync(output)) {
    const existing = fs.readFileSync(output);
    if (!existing.equals(bytes)) throw new Error("write-once supplement already exists with different bytes");
    return "EXISTING_IDENTICAL";
  }
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, bytes, { flag: "wx" });
  return "CREATED";
}

function main() {
  const output = parseOutput(process.argv.slice(2)), artifact = buildSupplement(), report = validateSupplement(artifact);
  if (!report.valid) throw new Error(report.errors.join("; "));
  const disposition = writeOnce(output, Buffer.from(JSON.stringify(artifact, null, 2) + "\n", "utf8"));
  const replay = JSON.parse(fs.readFileSync(output, "utf8")), replayReport = validateSupplement(replay);
  if (!replayReport.valid) throw new Error("post-write supplement validation failed: " + replayReport.errors.join("; "));
  process.stdout.write(JSON.stringify({ output: output, disposition: disposition, digest: artifact.contentAddress.digest, forcedU2Status: artifact.status.forcedU2Status }) + "\n");
}

if (require.main === module) main();
module.exports = { buildSupplement: buildSupplement, validateSupplement: validateSupplement, canonicalStringify: canonicalStringify, sha256Bytes: sha256Bytes, parseOutput: parseOutput };
