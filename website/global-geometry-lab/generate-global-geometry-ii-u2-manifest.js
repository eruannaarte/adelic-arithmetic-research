#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const Ensembles = require("./global-geometry-ii-ensembles.js");

const ROOT = path.resolve(__dirname, "../..");
const DECISION_CONTRACT = "GLOBAL_GEOMETRY_II_U2_ADVERSARIAL_PREREGISTRATION.md";
const GOVERNING_SPEC = "GLOBAL_GEOMETRY_II_UNIVERSALITY_SPEC.md";
const EXPECTED_DECISION_SHA256 = "faffef2526d16f79b700102057d59745f0a4359ea7c386c318cc0ee4afd0d5dc";
const EXPECTED_SPEC_SHA256 = "d49a4e7b3cf31ed47c6cab462b6340f6dfa15434f56e4df4d7e70737e1afe885";
const FAMILIES = ["square-alternating", "triangular-clipped", "cell-center-fan", "square-hashed-diagonal"];
const SIZES = [16, 24, 36, 54, 81, 120];
const SIGMAS = [0, 0.25, 0.75, Math.log(4)];

function sha256Bytes(buffer) { return crypto.createHash("sha256").update(buffer).digest("hex"); }
function sha256JSON(value) { return sha256Bytes(Buffer.from(canonicalStringify(value), "utf8")); }
function canonicalStringify(value) {
  if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isFinite(value) || Object.is(value, -0)) throw new Error("manifest contains an invalid number");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return "[" + value.map(canonicalStringify).join(",") + "]";
  if (!value || typeof value !== "object" || Object.getPrototypeOf(value) !== Object.prototype) throw new Error("manifest must contain plain JSON objects");
  return "{" + Object.keys(value).sort().map(function (key) { return JSON.stringify(key) + ":" + canonicalStringify(value[key]); }).join(",") + "}";
}

function assertProtocolDigests() {
  const decision = fs.readFileSync(path.join(ROOT, DECISION_CONTRACT));
  const governing = fs.readFileSync(path.join(ROOT, GOVERNING_SPEC));
  if (sha256Bytes(decision) !== EXPECTED_DECISION_SHA256) throw new Error("decision contract digest changed before manifest freeze");
  if (sha256Bytes(governing) !== EXPECTED_SPEC_SHA256) throw new Error("governing specification digest changed before manifest freeze");
  return {
    decisionContract: { id: "u2-decision-v2", path: DECISION_CONTRACT, sha256: EXPECTED_DECISION_SHA256, bytes: decision.length },
    governingSpecification: { path: GOVERNING_SPEC, sha256: EXPECTED_SPEC_SHA256, bytes: governing.length }
  };
}

function resourceRow(familyId, linearSize) {
  const estimate = Ensembles.estimatePreviewResources(familyId, linearSize);
  const logNodes = Math.log2(Math.max(2, estimate.vertices));
  const rootDijkstraOps = Math.ceil(64 * (estimate.edges + estimate.vertices) * logNodes);
  const lazyWalkOps = Math.ceil(64 * estimate.edges * Math.max(8, Math.ceil(linearSize * linearSize / 25)));
  const heatUpperOps = 256 * 64 * estimate.edges;
  const transportUpperOps = 8 * linearSize * estimate.edges;
  const peakBytesEstimate = Math.ceil(
    estimate.vertices * 8 * 18 + estimate.edges * 2 * 8 * 8 + estimate.faces * 3 * 4 + 256 * estimate.vertices * 8
  );
  return {
    familyId: familyId,
    linearSize: linearSize,
    predictedVertices: estimate.vertices,
    predictedEdges: estimate.edges,
    predictedFaces: estimate.faces,
    predictedOperations: {
      volume64RootDijkstraUpperModel: rootDijkstraOps,
      deterministicLazyWalkUpperModel: lazyWalkOps,
      heat256Probe64OrderUpperModel: heatUpperOps,
      transportCg8LIterationUpperModel: transportUpperOps,
      caveat: "operation counts are deterministic planning models, not wall-clock promises"
    },
    predictedPeakBytes: peakBytesEstimate,
    runCounts: {
      positiveConfirmatory: SIGMAS.length * 32,
      calibrationSplit: linearSize <= 36 ? SIGMAS.length * 8 : 0,
      pairedPerturbationMeasurements: linearSize >= 54 ? SIGMAS.length * 32 * 5 : 0
    },
    checkpointLayout: {
      order: "sigma ascending, confirmation replicate ascending, measurement channel lexicographic",
      checkpointEveryMeasurementUnits: 8,
      immutableRecordDirectoryTemplate: "u2-v2/runs/{familyId}/L{linearSize}/{parameterCell}/{runId}.json"
    },
    memoryCaveat: "binary payload estimate excludes JavaScript object headers, allocator fragmentation, runtime, and transient garbage-collection overhead"
  };
}

function buildManifest() {
  const protocols = assertProtocolDigests();
  const resources = [];
  FAMILIES.forEach(function (family) { SIZES.forEach(function (size) { resources.push(resourceRow(family, size)); }); });
  const manifest = {
    schema: "gg.atlas.experiment/2",
    experimentId: "ggii-u2-v2",
    hypothesis: {
      id: "U2",
      version: 2,
      supersedesForFutureOutcomeProduction: "ggii-u2-v1",
      versionReason: "outcome-blind correction of the internally infeasible L=81 spatial grid, as required by the adopted adversarial preregistration",
      claimClass: "universality-candidate",
      outcomeAtFreeze: "NOT_EVALUATED"
    },
    protocolAdoption: {
      outcomeBlindAtFreeze: true,
      scientificOutcomesReadBeforeFreeze: false,
      criteriaRelaxed: false,
      resourceAmendments: [],
      protocols: protocols
    },
    matrix: {
      families: FAMILIES,
      confirmationSizes: SIZES,
      calibrationSizes: [16, 24, 36],
      sigma: SIGMAS,
      confirmationReplicates: 32,
      calibrationReplicates: 8,
      reflectingDiskPositiveMeasurementUnits: 3072,
      calibrationMeasurementUnits: 384,
      primaryControlMeasurementUnitsMaximum: 768,
      periodicCalibrationInterpretation: "two analytic square/triangular spectral carriers plus capped filled-periodic overlap tests; not a second full factorial boundary mode",
      primaryControls: [
        { id: "comb-trap", parameters: { toothLength: "floor(L/4)" } },
        { id: "small-world-shortcuts", parameters: { shortcutDensity: 0.02, maximumEndpointsPerVertex: 1, minimumIntrinsicEndpointSeparation: "L/3" } },
        { id: "vanishing-neck", parameters: { corridorWidthInH: 2, corridorLength: "floor(L/4)h" } },
        { id: "perforated-disk", parameters: { holeDensity: 0.05, minimumEdgeSeparation: 3 } }
      ]
    },
    independence: {
      experimentalUnit: "weighted construction realization identified by generatorStream, conductanceStream, and structure digest",
      deterministicSigmaZeroGeometryCount: 1,
      nestedMeasurementBatchCount: 32,
      productionBulkRootsPerBatch: 64,
      heatProbePrefixes: [32, 64, 128, 256],
      bootstrapHierarchy: ["construction-realization", "spatial-root-block", "heat-probe"],
      bootstrapReplicates: 4096,
      confidence: 0.95,
      disjointNamespaces: { calibration: "cal/", confirmation: "confirm/" }
    },
    normalization: {
      fittedFrom: "independent calibration split only",
      frozenBeforeConfirmatoryMeasurement: true,
      fields: ["bulk-density", "scalar-or-tensor-diffusivity", "conductivity"],
      confirmatoryOutcomeMayEnterFit: false
    },
    commonGrids: {
      rho: [1 / 32, 1 / 24, 1 / 20, 1 / 16, 1 / 12, 1 / 8, 1 / 6, 1 / 5],
      tau: [1 / 512, 1 / 384, 1 / 256, 1 / 192, 1 / 128, 1 / 96],
      nativeTimeSchedule: "ceil(8*2^(k/2)), duplicates removed, through last bulk-admissible step",
      interpolation: "between two admissible native samples only; no extrapolation"
    },
    gates: {
      decisionContract: "u2-decision-v2 adopted verbatim by SHA-256 binding",
      statuses: ["PASS", "FAIL", "UNRESOLVED"],
      allComparisonsStrict: true,
      acceptedRequiresEveryPositiveAtomPass: true,
      rejectedRequiresReproducedScientificFail: true,
      infrastructureFailureOutcome: "UNRESOLVED",
      missingRecordCellLimit: 0.05,
      alternateEstimatorRequiredForFail: true,
      thresholdsMutableAfterFreeze: false
    },
    perturbations: [
      "one-cell-metric-pulse-v1", "one-percent-weight-defects-v1",
      "root-resampling-v1", "canonical-relabel-v1", "half-cell-crop-v1"
    ],
    inference: {
      familyDistance: "joint-mad-v1 as disambiguated by adopted decision contract",
      constrainedFitDiagnosticOnly: true,
      conservativeThreeLargestSizeRule: true,
      estimatorWindowReselectedInsideEveryBootstrap: true,
      floatComparison: "gg-float-compare-v1"
    },
    resourcePolicy: {
      tier: "batch",
      noSizeReplicateObservableOrControlReductionAuthorized: true,
      checkpointEveryMeasurementUnits: 8,
      dryRunGeneratedBeforeOutcomes: true,
      rows: resources
    },
    sourcePolicy: {
      externalRuntimeDependencies: [],
      implementationLanguage: "dependency-free Node.js standard library plus existing Global Geometry II modules",
      batchRandomness: {
        id: "gg-sha256-object-u53-v1",
        uniform: "top 53 bits of SHA-256(JCS([streamSeed,objectCanonicalKey,counter])) divided by 2^53",
        streamSeed: "SHA-256(JCS([experimentId,hypothesisVersion,namespace,familyId,parameterCell,linearSize,replicate,streamName]))",
        collisionPolicy: "duplicate effective stream seeds and object draws are enumerated and fail validation unless exact deterministic sigma=0 irrelevance is declared",
        previewCompatibilityOnly: "gg-fnv1a32-mulberry32-v1"
      },
      cleanCommitRequiredForGate8: true,
      sourceCommitBoundByPlatformCertificateAfterImplementationFreeze: true
    }
  };
  const canonical = canonicalStringify(manifest);
  return Object.assign({}, manifest, {
    contentAddress: {
      algorithm: "sha256",
      canonicalization: "RFC8785-compatible closed JSON subset",
      digest: sha256Bytes(Buffer.from(canonical, "utf8")),
      canonicalBytes: Buffer.byteLength(canonical, "utf8")
    }
  });
}

function validateManifest(artifact) {
  const errors = [];
  try {
    assertProtocolDigests();
    if (!artifact || artifact.schema !== "gg.atlas.experiment/2" || artifact.experimentId !== "ggii-u2-v2") errors.push("manifest identity mismatch");
    if (!artifact.hypothesis || artifact.hypothesis.version !== 2 || artifact.hypothesis.outcomeAtFreeze !== "NOT_EVALUATED") errors.push("hypothesis freeze mismatch");
    if (!artifact.protocolAdoption || artifact.protocolAdoption.outcomeBlindAtFreeze !== true || artifact.protocolAdoption.criteriaRelaxed !== false) errors.push("outcome-blind adoption mismatch");
    if (!artifact.matrix || artifact.matrix.reflectingDiskPositiveMeasurementUnits !== 3072 || artifact.matrix.calibrationMeasurementUnits !== 384 || artifact.matrix.primaryControlMeasurementUnitsMaximum !== 768) errors.push("matrix counts mismatch");
    if (!artifact.resourcePolicy || !Array.isArray(artifact.resourcePolicy.rows) || artifact.resourcePolicy.rows.length !== 24) errors.push("dry-run resource table must contain 24 family-size rows");
    if (!artifact.contentAddress) errors.push("content address missing");
    else {
      const payload = JSON.parse(JSON.stringify(artifact)); delete payload.contentAddress;
      const canonical = canonicalStringify(payload);
      if (artifact.contentAddress.digest !== sha256Bytes(Buffer.from(canonical, "utf8")) || artifact.contentAddress.canonicalBytes !== Buffer.byteLength(canonical, "utf8")) errors.push("content address mismatch");
    }
    const expected = buildManifest();
    if (canonicalStringify(artifact) !== canonicalStringify(expected)) {
      errors.push("manifest differs semantically from the independently regenerated frozen manifest");
    }
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function parseOutput(argv) {
  if (!argv.length) return path.join(ROOT, "artifacts/global-geometry-ii/u2/experiment-manifest-v2.json");
  if (argv.length !== 2 || argv[0] !== "--output") throw new Error("usage: generate-global-geometry-ii-u2-manifest.js [--output explicit-path]");
  return path.resolve(argv[1]);
}

function main() {
  const output = parseOutput(process.argv.slice(2));
  const artifact = buildManifest();
  const report = validateManifest(artifact);
  if (!report.valid) throw new Error(report.errors.join("; "));
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, JSON.stringify(artifact, null, 2) + "\n", "utf8");
  const replay = JSON.parse(fs.readFileSync(output, "utf8"));
  const replayReport = validateManifest(replay);
  if (!replayReport.valid) throw new Error("post-write manifest validation failed: " + replayReport.errors.join("; "));
  process.stdout.write(JSON.stringify({ output: output, digest: artifact.contentAddress.digest, resourceRows: artifact.resourcePolicy.rows.length, outcomeAtFreeze: artifact.hypothesis.outcomeAtFreeze }) + "\n");
}

if (require.main === module) main();
module.exports = { buildManifest: buildManifest, validateManifest: validateManifest, resourceRow: resourceRow, canonicalStringify: canonicalStringify, parseOutput: parseOutput };
