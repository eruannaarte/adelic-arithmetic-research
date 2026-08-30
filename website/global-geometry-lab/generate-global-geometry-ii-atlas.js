#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const Base = require("./global-geometry-core.js");
const G2 = require("./global-geometry-ii-core.js");
const Ensembles = require("./global-geometry-ii-ensembles.js");
const Atlas = require("./global-geometry-ii-atlas.js");

function parseOutput(argv) {
  const index = argv.indexOf("--output");
  if (index < 0) {
    if (argv.length) throw new Error("unknown generator argument " + argv[0]);
    return path.resolve(__dirname, "../../artifacts/global-geometry-ii/atlas-pilot-v1.json");
  }
  if (!argv[index + 1] || argv[index + 1].startsWith("--")) {
    throw new Error("--output requires an explicit file path");
  }
  if (argv.filter((item) => item === "--output").length !== 1) {
    throw new Error("--output may be supplied only once");
  }
  const unknown = argv.filter((item, position) => item !== "--output" && position !== index + 1);
  if (unknown.length) throw new Error("unknown generator argument " + unknown[0]);
  return path.resolve(argv[index + 1]);
}

function buildPayload(spec) {
  const pilot = Atlas.runPilotAtlas(spec);
  const report = Atlas.validatePilotResult(pilot);
  if (!report.valid) throw new Error("refusing to package an invalid pilot: " + report.errors.join("; "));
  return {
    schema: "ggii.atlas-pilot-artifact/1",
    baseCoreVersion: Base.VERSION,
    globalGeometryIICoreVersion: G2.VERSION,
    ensembleVersion: Ensembles.VERSION,
    atlasVersion: Atlas.VERSION,
    scientificScope: {
      established: "deterministic bounded finite preview records under the enclosed closed specification",
      notEstablished: [
        "a scaling window",
        "ensemble uncertainty",
        "a geometric universality class",
        "a continuum limit",
        "material robustness"
      ]
    },
    pilot: pilot
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
    throw new Error("atlas artifact failed its post-write SHA-256 content-address check");
  }
  const pilotReport = Atlas.validatePilotResult(replay.pilot);
  if (!pilotReport.valid) throw new Error("atlas artifact failed its post-write pilot validation: " + pilotReport.errors.join("; "));
  process.stdout.write(JSON.stringify({
    output,
    sha256: verified.digest,
    canonicalBytes: verified.canonicalBytes,
    resultChecksum: replay.pilot.resultDigest,
    runCount: replay.pilot.runs.length,
    cellCount: replay.pilot.cells.length,
    universalityStatus: replay.pilot.universalityStatus
  }) + "\n");
}

if (require.main === module) main();

module.exports = { buildPayload, contentAddress, parseOutput };
