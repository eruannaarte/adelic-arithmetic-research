#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");
const PARENT_PATH = "artifacts/global-geometry-ii/u2/experiment-manifest-v2.json";
const DECISION_PATH = "GLOBAL_GEOMETRY_II_U2_ADVERSARIAL_PREREGISTRATION.md";
const SPEC_PATH = "GLOBAL_GEOMETRY_II_UNIVERSALITY_SPEC.md";
const EXPECTED = Object.freeze({
  parent: "337b22a86b6f7b6b4d842c12d03f3eb580d8097e90746e55f9f1d8456c6cf9c6",
  decision: "faffef2526d16f79b700102057d59745f0a4359ea7c386c318cc0ee4afd0d5dc",
  specification: "d49a4e7b3cf31ed47c6cab462b6340f6dfa15434f56e4df4d7e70737e1afe885"
});

function sha256Bytes(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function canonicalStringify(value) {
  if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isFinite(value) || Object.is(value, -0)) throw new Error("invalid canonical number");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return "[" + value.map(canonicalStringify).join(",") + "]";
  if (!value || typeof value !== "object" || Object.getPrototypeOf(value) !== Object.prototype) {
    throw new Error("canonical values must be plain JSON");
  }
  return "{" + Object.keys(value).sort().map(function (key) {
    return JSON.stringify(key) + ":" + canonicalStringify(value[key]);
  }).join(",") + "}";
}

function fileBinding(relativePath, expectedDigest) {
  const bytes = fs.readFileSync(path.join(ROOT, relativePath));
  const digest = sha256Bytes(bytes);
  if (digest !== expectedDigest) throw new Error(relativePath + " digest differs from the outcome-blind screening binding");
  return { path: relativePath, sha256: digest, bytes: bytes.length };
}

function buildManifest() {
  const parent = fileBinding(PARENT_PATH, EXPECTED.parent);
  const parentArtifact = JSON.parse(fs.readFileSync(path.join(ROOT, PARENT_PATH), "utf8"));
  if (!parentArtifact.contentAddress || parentArtifact.contentAddress.digest !== "80252bca7951da99d9e7de778d98e3ad7147b7b9a76bb585d7ca266ddad348b3") {
    throw new Error("parent manifest semantic content address changed");
  }
  const payload = {
    schema: "gg.u2.screening.experiment/1",
    screeningId: "ggii-u2-v2-screening-v1",
    freezeStatus: {
      status: "FROZEN_BEFORE_SCREENING_OUTCOMES",
      productionOutcomeRecordsReadBeforeFreeze: false,
      criteriaMutableAfterFreeze: false,
      decisionAuthority: "NONE",
      forcedU2Status: "UNRESOLVED"
    },
    bindings: {
      parentExperimentManifest: Object.assign({}, parent, {
        experimentId: "ggii-u2-v2",
        semanticContentAddress: parentArtifact.contentAddress.digest
      }),
      decisionContract: fileBinding(DECISION_PATH, EXPECTED.decision),
      governingSpecification: fileBinding(SPEC_PATH, EXPECTED.specification)
    },
    scope: {
      purpose: "outcome-bearing, lower-cost screening and implementation validation",
      claimLimit: "Screening records cannot PASS or FAIL decision Gates 2-8 and cannot promote or reject U2.",
      positiveMatrix: {
        families: ["square-alternating", "triangular-clipped", "cell-center-fan", "square-hashed-diagonal"],
        sizes: [16, 24, 36, 54, 81, 120],
        sigma: [0, 0.25, 0.75, Math.log(4)],
        replicates: 32,
        recordCount: 3072
      },
      controls: {
        ids: ["comb-trap", "small-world-shortcuts", "vanishing-neck", "perforated-disk"],
        sizes: [16, 24, 36, 54, 81, 120],
        replicates: 32,
        recordCount: 768
      }
    },
    estimators: {
      constructionAudit: {
        coverage: "all positive and control records",
        measurements: ["vertex-count", "edge-count", "face-count-when-simplicial", "component-count", "degree-range", "boundary-edge-incidence", "surface-link-witness-when-applicable", "structure-sha256"],
        topologyLabelRule: "Exact Betti numbers are emitted only after connectedness, edge incidence, boundary-manifold, vertex-link, orientability, and nonempty-boundary witnesses validate; otherwise only the observed witness and graph cycle rank are emitted."
      },
      conductanceAudit: {
        coverage: "all 3072 positive records",
        law: "w_e=exp(sigma*(2*u_e-1))",
        bounds: "[exp(-sigma),exp(sigma)]",
        measurements: ["minimum", "maximum", "arithmetic-mean", "geometric-mean", "strict-positivity", "bound-residual"],
        exactness: "binary64 evaluation of every constructed edge conductance"
      },
      volumeGrowthScreen: {
        coverage: "all 3072 positive records",
        metric: "unweighted graph-hop distance",
        rootCount: 8,
        rootSelection: "eight SHA-256-ranked canonical vertices whose multi-source boundary distance is at least the maximum sampled hop radius",
        rho: [1 / 32, 1 / 24, 1 / 20, 1 / 16, 1 / 12, 1 / 8, 1 / 6, 1 / 5],
        radiusMap: "max(1,floor(rho*realizedEuclideanDiameter)) with duplicates removed",
        fit: "ordinary least squares of log mean ball count on log hop radius when at least three unique radii exist",
        decisionDifference: "8 rather than 64 roots, hop rather than registered intrinsic metric, no hierarchical bootstrap; screening only"
      },
      randomWalkScreen: {
        coverage: "every positive record at L=81 and L=120",
        process: "lazy weighted nearest-neighbor walk with laziness 0.5",
        rootCount: 4,
        walkersPerRoot: 8,
        totalWalkersPerRecord: 32,
        nativeTimes: [8, 16, 32, 64, 128, 256],
        distance: "unweighted graph-hop distance from each starting root",
        fit: "per-root OLS slope of log mean squared displacement on log time; d_w=2/slope when positive",
        interval: "two-sided 95% Student-t interval across four root-block estimates (df=3); sampling error is nonzero and the interval is non-hierarchical",
        decisionDifference: "4 roots x 8 walkers, no exit-time alternate, no hierarchical bootstrap, and no diffusivity calibration; screening only"
      },
      transportScreen: {
        coverage: "every positive record at L=81 and L=120 and vanishing-neck controls",
        observables: {
          linearTrialDirichletEnergy: "sum_e w_e*((x_v-x_u)/(x_max-x_min))^2, a rigorous upper bound for the left-right Dirichlet conductance when the linear trial potential obeys the boundary values",
          layeredSeriesProxy: "reciprocal of the sum over registered half-integer x cuts of reciprocal total crossing conductance",
          minimumCutRatio: "minimum registered cut conductance divided by median registered cut conductance"
        },
        decisionDifference: "No residual-certified Dirichlet solve, calibration normalization, effective-resistance alternate, or hierarchical interval; screening only"
      },
      controlDiscriminants: {
        "comb-trap": "actual axial lazy-walk MSD and occupied-tooth fraction on a backbone with floor(L/4)-long teeth",
        "small-world-shortcuts": "actual accepted shortcut count/separation plus root-ball inflation relative to the same graph with shortcuts removed",
        "vanishing-neck": "actual corridor cross-section and minimum-cut ratio on two comparable triangulated patches joined by a two-cell-wide floor(L/4)-long corridor",
        "perforated-disk": "actual removed mutually separated interior face stars, exact beta_1 only when the surface witness validates, and giant-component fraction"
      }
    },
    randomness: {
      id: "gg-sha256-object-u53-v1",
      streamSeed: "SHA-256(JCS([screeningId,namespace,familyOrControl,size,sigmaIndex,replicate,role]))",
      objectUniform: "top 53 bits of SHA-256(JCS([streamSeed,objectCanonicalKey,counter])) divided by 2^53",
      streamRoles: ["construction", "conductance", "volume-roots", "walk", "control"],
      collisionAudit: "all effective stream seeds; per-record conductance and Monte Carlo u53 outputs; deterministic irrelevance explicitly counted"
    },
    failureSemantics: {
      codes: ["INVALID_CONFIG", "INVALID_COMPLEX", "INSUFFICIENT_BULK_ROOTS", "INSUFFICIENT_VOLUME_WINDOW", "ESTIMATOR_UNDEFINED", "RESOURCE_FAILURE", "INTERNAL_REPLAY_MISMATCH"],
      anyFailureEffect: "record remains present with failure ledger entry; U2 remains UNRESOLVED",
      missingCellLimit: 0.05,
      scientificRejectionAllowed: false
    },
    artifactContract: {
      raw: "newline-delimited canonical JSON records with per-record SHA-256 and a whole-file SHA-256",
      summary: "canonical JSON with census, screening aggregates, failures, seed audit, Merkle root, raw-file binding, and telemetry",
      writePolicy: "write-once: an existing artifact may be accepted only when bytes are identical",
      semanticReplay: "validators reconstruct census identities/seeds, recompute hashes and summaries, and can remeasure selected records",
      expectedRawRecords: 3840,
      outputDirectory: "artifacts/global-geometry-ii/u2/screening"
    },
    resourcePlan: {
      runtimeEstimateMinutesSingleNode: [4, 12],
      rawArtifactEstimateBytes: [5000000, 15000000],
      checkpointEveryRecords: 32,
      maximumResidentGraphs: 1,
      noScientificMatrixReductionAuthorized: true
    }
  };
  const canonical = canonicalStringify(payload);
  return Object.assign({}, payload, {
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
    const expectedArtifact = buildManifest();
    if (canonicalStringify(artifact) !== canonicalStringify(expectedArtifact)) errors.push("manifest differs from deterministic full-payload rebuild");
    if (!artifact || artifact.schema !== "gg.u2.screening.experiment/1" || artifact.screeningId !== "ggii-u2-v2-screening-v1") errors.push("screening identity mismatch");
    if (!artifact.freezeStatus || artifact.freezeStatus.status !== "FROZEN_BEFORE_SCREENING_OUTCOMES" || artifact.freezeStatus.forcedU2Status !== "UNRESOLVED") errors.push("freeze status mismatch");
    if (!artifact.scope || artifact.scope.positiveMatrix.recordCount !== 3072 || artifact.scope.controls.recordCount !== 768) errors.push("screening census mismatch");
    if (!artifact.estimators || artifact.estimators.randomWalkScreen.totalWalkersPerRecord !== 32) errors.push("random-walk screening contract mismatch");
    if (!artifact.contentAddress) errors.push("contentAddress missing");
    else {
      const payload = JSON.parse(JSON.stringify(artifact));
      delete payload.contentAddress;
      const canonical = canonicalStringify(payload);
      if (artifact.contentAddress.digest !== sha256Bytes(Buffer.from(canonical, "utf8")) || artifact.contentAddress.canonicalBytes !== Buffer.byteLength(canonical, "utf8")) errors.push("contentAddress mismatch");
    }
    [artifact.bindings.parentExperimentManifest, artifact.bindings.decisionContract, artifact.bindings.governingSpecification].forEach(function (binding) {
      const bytes = fs.readFileSync(path.join(ROOT, binding.path));
      if (bytes.length !== binding.bytes || sha256Bytes(bytes) !== binding.sha256) errors.push("bound file mismatch: " + binding.path);
    });
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function parseOutput(argv) {
  if (!argv.length) return path.join(ROOT, "artifacts/global-geometry-ii/u2/screening/screening-manifest-v1.json");
  if (argv.length !== 2 || argv[0] !== "--output" || !argv[1]) throw new Error("usage: generate-global-geometry-ii-u2-screening-manifest.js [--output explicit-path]");
  return path.resolve(argv[1]);
}

function writeOnce(output, bytes) {
  if (fs.existsSync(output)) {
    const existing = fs.readFileSync(output);
    if (!existing.equals(bytes)) throw new Error("write-once screening manifest already exists with different bytes");
    return "EXISTING_IDENTICAL";
  }
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, bytes, { flag: "wx" });
  return "CREATED";
}

function main() {
  const output = parseOutput(process.argv.slice(2));
  const manifest = buildManifest();
  const report = validateManifest(manifest);
  if (!report.valid) throw new Error(report.errors.join("; "));
  const disposition = writeOnce(output, Buffer.from(JSON.stringify(manifest, null, 2) + "\n", "utf8"));
  const replay = JSON.parse(fs.readFileSync(output, "utf8"));
  const replayReport = validateManifest(replay);
  if (!replayReport.valid) throw new Error("post-write screening manifest validation failed: " + replayReport.errors.join("; "));
  process.stdout.write(JSON.stringify({ output: output, disposition: disposition, digest: manifest.contentAddress.digest, forcedU2Status: manifest.freezeStatus.forcedU2Status }) + "\n");
}

if (require.main === module) main();
module.exports = { buildManifest: buildManifest, validateManifest: validateManifest, canonicalStringify: canonicalStringify, sha256Bytes: sha256Bytes, parseOutput: parseOutput };
