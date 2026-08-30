#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const Base = require("./global-geometry-core.js");
const G2 = require("./global-geometry-ii-core.js");
const Claims = require("./global-geometry-ii-claims.js");

function parseOutput(argv) {
  const outputFlags = argv.reduce((indices, value, index) => {
    if (value === "--output") indices.push(index);
    return indices;
  }, []);
  if (!outputFlags.length) {
    if (argv.length) throw new Error("unknown generator argument " + argv[0]);
    return path.resolve(__dirname, "../../artifacts/global-geometry-ii/calibration-v1.json");
  }
  if (outputFlags.length !== 1) throw new Error("--output may be supplied only once");
  const index = outputFlags[0];
  if (index !== 0 || argv.length !== 2 || !argv[1] || argv[1].startsWith("--")) {
    throw new Error("--output requires exactly one explicit file path");
  }
  return path.resolve(argv[1]);
}

function buildPayload() {
  return {
    schema: "ggii.calibration-artifact/1",
    baseCoreVersion: Base.VERSION,
    globalGeometryIICoreVersion: G2.VERSION,
    scientificScope: {
      spectralResult: "finite computational calibration of a profile-equivalence candidate",
      metricResult: "proved-here nonuniversality for the declared one-skeleton graph metrics",
      diffusionResult: "proved-here common Gaussian finite-dimensional limit for the declared square and equilateral-triangular walks",
      robustDiffusionResult: "proved-here uniform finite-dimensional Gaussian limit over bounded centered nondegenerate iid laws after covariance whitening",
      notEstablished: [
        "a common metric-measure-operator limit",
        "bounded-disk or disordered universality",
        "path-space functional convergence in this artifact",
        "semigroup or operator convergence",
        "boundary or disordered-conductance invariance principles",
        "physical material validation"
      ]
    },
    elementaryTheoremLedger: Claims.listClaims(),
    spectralCalibration: G2.runSpectralCalibration(),
    graphMetricControl: G2.graphMetricNonuniversalityControl(),
    diffusionFiniteDimensionalControl: G2.diffusionFiniteDimensionalUniversalityControl(),
    robustWhitenedDiffusionControl: G2.robustWhitenedDiffusionUniversalityControl()
  };
}

function contentAddress(payload) {
  const canonical = G2.stableStringify(payload);
  return {
    algorithm: "sha256",
    canonicalization: "ggii-stable-json-alpha1",
    digest: crypto.createHash("sha256").update(canonical, "utf8").digest("hex"),
    canonicalBytes: Buffer.byteLength(canonical, "utf8")
  };
}

function main() {
  const output = parseOutput(process.argv.slice(2));
  const payload = buildPayload();
  const artifact = { ...payload, contentAddress: contentAddress(payload) };
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, JSON.stringify(artifact, null, 2) + "\n", "utf8");

  const replay = JSON.parse(fs.readFileSync(output, "utf8"));
  const replayAddress = replay.contentAddress;
  delete replay.contentAddress;
  const verified = contentAddress(replay);
  if (verified.digest !== replayAddress.digest || verified.canonicalBytes !== replayAddress.canonicalBytes) {
    throw new Error("calibration artifact failed its post-write content-address check");
  }
  process.stdout.write(JSON.stringify({
    output,
    sha256: verified.digest,
    canonicalBytes: verified.canonicalBytes,
    candidateStatus: artifact.spectralCalibration.candidateStatus,
    metricStatus: artifact.graphMetricControl.status
  }) + "\n");
}

if (require.main === module) main();

module.exports = { buildPayload, contentAddress, parseOutput };
