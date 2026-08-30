#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const Sheet = require("./global-geometry-ii-sheet.js");

function parseOutput(argv) {
  const indices = argv.reduce((found, value, index) => {
    if (value === "--output") found.push(index);
    return found;
  }, []);
  if (!indices.length) {
    if (argv.length) throw new Error("unknown generator argument " + argv[0]);
    return path.resolve(__dirname, "../../artifacts/global-geometry-ii/sheet-hil-v1.json");
  }
  if (indices.length !== 1) throw new Error("--output may be supplied only once");
  if (indices[0] !== 0 || argv.length !== 2 || !argv[1] || argv[1].startsWith("--")) {
    throw new Error("--output requires exactly one explicit file path");
  }
  return path.resolve(argv[1]);
}

function message(type, seq, timeMs, payload, armEpoch) {
  return Sheet.createProtocolMessage({
    type,
    seq,
    monotonicTimeMs: timeMs,
    deadlineMs: timeMs + 100,
    armEpoch: armEpoch == null ? null : armEpoch,
    payload
  });
}

function representativeScenario() {
  const config = {
    seed: "ggii-sheet-artifact-v1",
    plant: { q: 7, seed: "ggii-sheet-plant-v1", backlashDeg: 0, quantizationDeg: 0.1 },
    watchdogTimeoutMs: 250
  };
  const probe = Sheet.createHilEmulator(config);
  const measurement = Sheet.measureVirtualPlant(probe.snapshot().plant, {
    seed: "ggii-sheet-measurement-v1",
    sampleIndex: 1,
    noise: { heightStdMm: 0, hingeStdDeg: 0, dropoutProbability: 0 }
  });
  probe.setObservation(measurement);
  const armMessage = message("ARM", 1, 0, { sessionId: "ggii-artifact-session" }, null);
  const armResponse = probe.receive(armMessage);
  const plant = probe.snapshot().plant;
  const commandMessage = message("COMMAND", 2, 1, {
    plantId: plant.plantId,
    expectedStateRevision: plant.stateRevision,
    expectedStateDigest: plant.stateDigest,
    observationDigest: measurement.measurementDigest,
    channels: [
      { id: "hinge-00", positionDeg: 8, maxRateDegPerSec: 4 },
      { id: "hinge-01", positionDeg: -5, maxRateDegPerSec: 3 }
    ]
  }, armResponse.armEpoch);
  return {
    schemaVersion: Sheet.SCHEMA_VERSION,
    config,
    events: [
      { kind: "OBSERVATION", measurement },
      { kind: "MESSAGE", message: armMessage },
      { kind: "MESSAGE", message: commandMessage },
      { kind: "TICK", timeMs: 80 },
      { kind: "MESSAGE", message: message("HOLD", 3, 80, { reason: "artifact-complete" }, armResponse.armEpoch) }
    ]
  };
}

function buildPayload() {
  const stars = [5, 6, 7].map((q) => Sheet.createQStar(q));
  const scenario = representativeScenario();
  const scenarioResult = Sheet.runHilScenario(scenario);
  if (!Sheet.validateHilTranscript(scenarioResult.transcript).valid) {
    throw new Error("refusing to package an invalid HIL transcript");
  }
  if (!Sheet.validateEmulatorSnapshot(scenarioResult.finalState).valid) {
    throw new Error("refusing to package an invalid HIL final state");
  }
  return {
    schema: "ggii.sheet-hil-artifact/1",
    sheetVersion: Sheet.VERSION,
    sheetSchemaVersion: Sheet.SCHEMA_VERSION,
    protocol: Sheet.PROTOCOL,
    scientificScope: {
      established: [
        "exact finite q-star defect budgets for q=5,6,7",
        "deterministic virtual-plant replay",
        "measurement-to-state-to-command binding",
        "closed observation-bound virtual HIL transcript"
      ],
      notEstablished: [
        "physical fabrication",
        "material calibration",
        "extrinsic shell equilibrium",
        "camera reconstruction accuracy",
        "actuator or operator safety",
        "transport authentication"
      ]
    },
    stars,
    scenario,
    scenarioResult
  };
}

function contentAddress(payload) {
  const canonical = Sheet.stableStringify(payload);
  return {
    algorithm: "sha256",
    canonicalization: "ggii-sheet-jcs-subset-v2",
    digest: crypto.createHash("sha256").update(canonical, "utf8").digest("hex"),
    canonicalBytes: Buffer.byteLength(canonical, "utf8")
  };
}

function validatePayload(payload) {
  const errors = [];
  if (!payload || payload.schema !== "ggii.sheet-hil-artifact/1") errors.push("wrong artifact schema");
  if (!payload || payload.sheetVersion !== Sheet.VERSION || payload.sheetSchemaVersion !== Sheet.SCHEMA_VERSION || payload.protocol !== Sheet.PROTOCOL) errors.push("sheet version/protocol mismatch");
  if (!payload || !Array.isArray(payload.stars) || payload.stars.length !== 3) errors.push("q-star suite is incomplete");
  else payload.stars.forEach((star, index) => {
    const expected = Sheet.createQStar(index + 5);
    if (Sheet.stableStringify(star) !== Sheet.stableStringify(expected)) errors.push("q-star mismatch for q=" + (index + 5));
  });
  if (!payload || !payload.scenario || !payload.scenarioResult) errors.push("scenario package missing");
  else {
    const replay = Sheet.runHilScenario(payload.scenario);
    if (Sheet.stableStringify(replay) !== Sheet.stableStringify(payload.scenarioResult)) errors.push("HIL scenario replay mismatch");
    const transcript = Sheet.validateHilTranscript(payload.scenarioResult.transcript);
    const snapshot = Sheet.validateEmulatorSnapshot(payload.scenarioResult.finalState);
    if (!transcript.valid) errors.push("invalid transcript: " + transcript.errors.join("; "));
    if (!snapshot.valid) errors.push("invalid final state: " + snapshot.errors.join("; "));
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
  const suppliedAddress = replay.contentAddress;
  delete replay.contentAddress;
  const verified = contentAddress(replay);
  const validation = validatePayload(replay);
  if (!validation.valid) throw new Error("sheet artifact failed semantic replay: " + validation.errors.join("; "));
  if (!suppliedAddress || verified.digest !== suppliedAddress.digest || verified.canonicalBytes !== suppliedAddress.canonicalBytes) {
    throw new Error("sheet artifact failed its post-write SHA-256 content-address check");
  }
  process.stdout.write(JSON.stringify({
    output,
    sha256: verified.digest,
    canonicalBytes: verified.canonicalBytes,
    stars: replay.stars.map((star) => ({ q: star.q, centerDefectPiCoefficient: star.intrinsic.center.defectPiCoefficient })),
    finalState: replay.scenarioResult.finalState.state,
    protocol: replay.protocol
  }) + "\n");
}

if (require.main === module) main();

module.exports = { buildPayload, contentAddress, parseOutput, representativeScenario, validatePayload };
