#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const Base = require("./global-geometry-core.js");
const Inverse = require("./global-geometry-ii-inverse.js");

function parseOutput(argv) {
  const outputFlags = argv.reduce((indices, value, index) => {
    if (value === "--output") indices.push(index);
    return indices;
  }, []);
  if (!outputFlags.length) {
    if (argv.length) throw new Error("unknown generator argument " + argv[0]);
    return path.resolve(__dirname, "../../artifacts/global-geometry-ii/inverse-certificates-v1.json");
  }
  if (outputFlags.length !== 1) throw new Error("--output may be supplied only once");
  const index = outputFlags[0];
  if (index !== 0 || argv.length !== 2 || !argv[1] || argv[1].startsWith("--")) {
    throw new Error("--output requires exactly one explicit file path");
  }
  return path.resolve(argv[1]);
}

function buildPayload() {
  const cases = Inverse.listRepresentativeRequests().map((id) => {
    const request = Inverse.representativeRequest(id);
    const report = Inverse.compileInverseDesign(request);
    const validation = Inverse.validateCompilerReport(report);
    if (!validation.valid) {
      throw new Error("refusing to package invalid inverse report " + id + ": " + validation.errors.join("; "));
    }
    return { id, request, report };
  });
  return {
    schema: "ggii.inverse-certificates-artifact/1",
    baseCoreVersion: Base.VERSION,
    inverseCompilerVersion: Inverse.VERSION,
    inverseCompilerSchemaVersion: Inverse.SCHEMA_VERSION,
    scientificScope: {
      established: [
        "a finite exhaustive Chow--Luo admission for the declared tetrahedral Model CP target",
        "an exact Chow--Luo subset obstruction with a minimal displayed witness",
        "an exact Gauss--Bonnet total obstruction",
        "a degenerate-triangle obstruction in the declared edge-metric model"
      ],
      notEstablished: [
        "a general geometry compiler",
        "extrinsic embedding existence or uniqueness",
        "continuum convergence",
        "material or actuator feasibility",
        "physical validation"
      ]
    },
    cases
  };
}

function contentAddress(payload) {
  const canonical = Inverse.stableStringify(payload);
  return {
    algorithm: "sha256",
    canonicalization: "ggii-inverse-ieee754-json-alpha2",
    digest: crypto.createHash("sha256").update(canonical, "utf8").digest("hex"),
    canonicalBytes: Buffer.byteLength(canonical, "utf8")
  };
}

function validatePayload(payload) {
  const errors = [];
  if (!payload || payload.schema !== "ggii.inverse-certificates-artifact/1") errors.push("wrong artifact schema");
  if (!payload || !Array.isArray(payload.cases) || payload.cases.length !== Inverse.listRepresentativeRequests().length) {
    errors.push("representative case set is incomplete");
  } else {
    payload.cases.forEach((entry, index) => {
      const expectedId = Inverse.listRepresentativeRequests()[index];
      if (!entry || entry.id !== expectedId) errors.push("case order/id mismatch at " + index);
      if (!entry || Inverse.stableStringify(entry.request) !== Inverse.stableStringify(Inverse.representativeRequest(expectedId))) {
        errors.push("representative request mismatch for " + expectedId);
      }
      if (entry && entry.report) {
        const validation = Inverse.validateCompilerReport(entry.report);
        if (!validation.valid) errors.push("invalid report for " + expectedId + ": " + validation.errors.join("; "));
      } else errors.push("missing report for " + expectedId);
    });
  }
  return { valid: errors.length === 0, errors };
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
  const validation = validatePayload(replay);
  if (!validation.valid) throw new Error("inverse artifact failed semantic replay: " + validation.errors.join("; "));
  if (!replayAddress || verified.digest !== replayAddress.digest || verified.canonicalBytes !== replayAddress.canonicalBytes) {
    throw new Error("inverse artifact failed its post-write SHA-256 content-address check");
  }
  process.stdout.write(JSON.stringify({
    output,
    sha256: verified.digest,
    canonicalBytes: verified.canonicalBytes,
    cases: replay.cases.map((entry) => ({ id: entry.id, status: entry.report.status }))
  }) + "\n");
}

if (require.main === module) main();

module.exports = { buildPayload, contentAddress, parseOutput, validatePayload };
