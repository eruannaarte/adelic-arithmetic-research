#!/usr/bin/env node
"use strict";

var assert = require("assert");
var crypto = require("crypto");
var fs = require("fs");
var path = require("path");
var vm = require("vm");
var Sheet = require("./global-geometry-ii-sheet.js");

var passed = 0;
function test(name, body) {
  try {
    body();
    passed += 1;
    process.stdout.write("ok " + passed + " - " + name + "\n");
  } catch (error) {
    process.stderr.write("not ok - " + name + "\n" + (error.stack || error.message) + "\n");
    process.exitCode = 1;
  }
}

function request(type, seq, timeMs, payload, armEpoch, lifetimeMs) {
  return Sheet.createProtocolMessage({
    type: type,
    seq: seq,
    monotonicTimeMs: timeMs,
    deadlineMs: timeMs + (lifetimeMs == null ? 100 : lifetimeMs),
    armEpoch: armEpoch == null ? null : armEpoch,
    payload: payload || {}
  });
}

function measurementFor(emulator, extra) {
  var options = {
    seed: "test-measurement",
    sampleIndex: 7,
    noise: { heightStdMm: 0, hingeStdDeg: 0, dropoutProbability: 0 }
  };
  Object.keys(extra || {}).forEach(function (key) { options[key] = extra[key]; });
  return Sheet.measureVirtualPlant(emulator.snapshot().plant, options);
}

function arm(emulator, seq, timeMs, sessionId) {
  return emulator.receive(request("ARM", seq, timeMs, { sessionId: sessionId || "test-session" }, null));
}

function commandFor(emulator, measurement, armEpoch, seq, timeMs, channels, overrides) {
  var plant = emulator.snapshot().plant;
  var payload = {
    plantId: plant.plantId,
    expectedStateRevision: plant.stateRevision,
    expectedStateDigest: plant.stateDigest,
    observationDigest: measurement.measurementDigest,
    channels: channels || [{ id: "hinge-00", positionDeg: 5, maxRateDegPerSec: 5 }]
  };
  Object.keys(overrides || {}).forEach(function (key) { payload[key] = overrides[key]; });
  return request("COMMAND", seq, timeMs, payload, armEpoch);
}

function mutable(value) { return JSON.parse(JSON.stringify(value)); }
function resealDigest(value, field) { delete value[field]; value[field] = Sheet.digestValue(value); return value; }

test("exports protocol-v2 bounded APIs and standard digest/checksum vectors", function () {
  assert.strictEqual(Sheet.VERSION, "0.2.0-alpha.1");
  assert.strictEqual(Sheet.SCHEMA_VERSION, 2);
  assert.strictEqual(Sheet.PROTOCOL, "ggii-hil/2");
  assert.strictEqual(Sheet.sha256Hex("abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
  assert.strictEqual(Sheet.sha256Hex("geometry-🌐"), crypto.createHash("sha256").update("geometry-🌐", "utf8").digest("hex"));
  assert.strictEqual(Sheet.crc32("123456789"), "cbf43926");
  assert.strictEqual(typeof Sheet.validatePlantSnapshot, "function");
  assert.strictEqual(typeof Sheet.validateProtocolResponse, "function");
  assert.strictEqual(typeof Sheet.validateHilTranscript, "function");
  assert.strictEqual(Sheet.LIMITS.maxChannels, 7);
});

test("UMD browser-side outputs match Node for ordinary bounded inputs", function () {
  var source = fs.readFileSync(path.join(__dirname, "global-geometry-ii-sheet.js"), "utf8");
  var context = { self: {}, Math: Math, JSON: JSON, Object: Object, Number: Number, String: String, Error: Error, RegExp: RegExp, Array: Array, isFinite: isFinite };
  vm.createContext(context);
  vm.runInContext(source, context);
  var Browser = context.self.GlobalGeometryIISheet;
  assert.strictEqual(Browser.optionalDependencies.base, false);
  assert.strictEqual(Browser.stableStringify(Browser.createQStar(7)), Sheet.stableStringify(Sheet.createQStar(7)));
  var raw = { type: "HELLO", seq: 1, monotonicTimeMs: 0, deadlineMs: 100, armEpoch: null, payload: { clientId: "browser-client" } };
  assert.strictEqual(Browser.stableStringify(Browser.createProtocolMessage(raw)), Sheet.stableStringify(Sheet.createProtocolMessage(raw)));
});

test("q=5, 6, and 7 stars have exact signed defects and disk budgets", function () {
  var expected = { 5: { denominator: 3, numerator: 1 }, 6: { denominator: 1, numerator: 0 }, 7: { denominator: 3, numerator: -1 } };
  [5, 6, 7].forEach(function (q) {
    var star = Sheet.createQStar(q);
    assert.deepStrictEqual(star.intrinsic.center.defectPiCoefficient, expected[q]);
    assert.deepStrictEqual(star.intrinsic.totalDefectPiCoefficient, { denominator: 1, numerator: 2 });
    assert.strictEqual(star.intrinsic.exactGaussBonnetIdentity, true);
    star.intrinsic.boundary.forEach(function (entry) { assert.deepStrictEqual(entry.defectPiCoefficient, { denominator: 3, numerator: 1 }); });
    assert.deepStrictEqual(star.counts, { boundaryComponents: 1, edges: 2 * q, eulerCharacteristic: 1, faces: q, vertices: q + 1 });
    assert.strictEqual(star.intrinsic.evidence.evidenceClass, "exact-finite-identity");
    assert.strictEqual(star.designDigest.length, 64);
  });
});

test("closed schemas reject unknown fields, class instances, inherited fields, and nonfinite data", function () {
  assert.throws(function () { Sheet.createQStar(4); }, /integer in \[5, 7\]/);
  assert.throws(function () { Sheet.createQStar(6, { executable: "no" }); }, /unknown field executable/);
  assert.throws(function () { Sheet.createVirtualPlant({ q: 6, serialPort: "COM3" }); }, /unknown field serialPort/);
  function Config() { this.q = 7; }
  assert.throws(function () { Sheet.createVirtualPlant(new Config()); }, /plain object/);
  var inherited = Object.create({ q: 7 });
  assert.throws(function () { Sheet.createVirtualPlant(inherited); }, /plain object|inherited/);
  assert.throws(function () { Sheet.createVirtualPlant({ q: 6, maxPositionDeg: Infinity }); }, /finite/);
});

test("virtual plant state revisions and SHA bindings change only with physical state", function () {
  var plant = Sheet.createVirtualPlant({ q: 7, seed: "plant-replay", embeddingBranch: -1, backlashDeg: 0, quantizationDeg: 0.1 });
  var initial = plant.snapshot();
  assert.strictEqual(Sheet.validatePlantSnapshot(initial).valid, true);
  var timeOnly = plant.stepTo(10);
  assert.strictEqual(timeOnly.stateRevision, initial.stateRevision);
  assert.strictEqual(timeOnly.stateDigest, initial.stateDigest);
  assert.notStrictEqual(timeOnly.snapshotDigest, initial.snapshotDigest);
  assert.strictEqual(plant.setTargets([{ id: "hinge-00", positionDeg: 12, maxRateDegPerSec: 6 }], 10).accepted, true);
  var queued = plant.snapshot();
  assert.ok(queued.stateRevision > initial.stateRevision);
  assert.notStrictEqual(queued.stateDigest, initial.stateDigest);
  var moved = plant.stepTo(1010);
  assert.ok(moved.channels[0].positionDeg > 0);
  assert.strictEqual(Sheet.validatePlantSnapshot(moved).valid, true);
  assert.strictEqual(moved.evidence.physicalValidationClaim, false);
});

test("plant rejects saturation, time overflow, and forged snapshots", function () {
  var plant = Sheet.createVirtualPlant({ q: 6, maxPositionDeg: 20, commandDelayMs: 10 });
  assert.strictEqual(plant.setTargets([{ id: "hinge-00", positionDeg: 21, maxRateDegPerSec: 5 }], 0).code, "SATURATION_LIMIT");
  assert.strictEqual(plant.setTargets([{ id: "hinge-00", positionDeg: 2, maxRateDegPerSec: 5 }], Sheet.LIMITS.maxTimeMs).code, "TIME_HORIZON_LIMIT");
  var forged = mutable(plant.snapshot());
  forged.q = 8;
  assert.strictEqual(Sheet.validatePlantSnapshot(forged).valid, false);
  assert.throws(function () { Sheet.measureVirtualPlant(forged, {}); }, /Invalid virtual plant snapshot/);
});

test("synthetic measurements replay and bind plant identity, revision, state, and evidence", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 5, seed: "measurement-plant" } });
  var options = { seed: "named-noise-seed", sampleIndex: 11, calibration: { id: "frozen-calibration-01", frozen: true, calibratedAtMs: 0, validUntilMs: 1000, heightScale: 1.01, heightOffsetMm: -0.2, hingeScale: 0.99, hingeOffsetDeg: 0.1 }, noise: { heightStdMm: 0.3, hingeStdDeg: 0.2, dropoutProbability: 0 } };
  var first = measurementFor(emulator, options), second = measurementFor(emulator, options);
  assert.strictEqual(Sheet.stableStringify(first), Sheet.stableStringify(second));
  assert.strictEqual(Sheet.validateMeasurement(first).valid, true);
  assert.strictEqual(first.sourcePlantId, emulator.snapshot().plant.plantId);
  assert.strictEqual(first.sourceStateRevision, emulator.snapshot().plant.stateRevision);
  assert.strictEqual(first.sourceStateDigest, emulator.snapshot().plant.stateDigest);
  assert.strictEqual(first.evidenceSeparation.extrinsicMeasurement.synthetic, true);
  assert.strictEqual(first.evidenceSeparation.extrinsicMeasurement.physicalMeasurement, false);
  assert.strictEqual(first.measurementDigest.length, 64);
});

test("measurement construction rejects nonboolean calibration state", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  assert.throws(function () { measurementFor(emulator, { calibration: { frozen: "yes" } }); }, /frozen must be boolean/);
});

test("stale calibration and critical dropout produce exactly derived observability failures", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var stale = measurementFor(emulator, { calibration: { id: "stale-cal", frozen: true, calibratedAtMs: 1, validUntilMs: 10 } });
  assert.strictEqual(stale.observability.observable, false);
  assert.deepStrictEqual(stale.observability.reasons, ["calibration-stale"]);
  var dropped = measurementFor(emulator, { criticalFaceIds: ["face-00"], forcedDropoutFaceIds: ["face-00"] });
  assert.strictEqual(dropped.observability.code, "SENSOR_UNOBSERVABLE");
  assert.deepStrictEqual(dropped.observability.missingCriticalFaceIds, ["face-00"]);
  assert.strictEqual(Sheet.validateMeasurement(dropped).valid, true);
});

test("measurement validator rejects duplicate partitions and forged PASS certificates", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var forged = mutable(measurementFor(emulator));
  forged.observedFaceIds = ["face-00", "face-00", "face-00", "face-00", "face-00", "face-00"];
  forged.droppedFaceIds = [];
  forged.observability = { status: "PASS", code: "OBSERVABLE", observable: true, coverageFraction: 1, missingCriticalFaceIds: [], reasons: [] };
  resealDigest(forged, "measurementDigest");
  assert.strictEqual(Sheet.validateMeasurement(forged).valid, false);

  var calibrationForgery = mutable(measurementFor(emulator));
  calibrationForgery.calibration.frozen = false;
  calibrationForgery.observability = { status: "PASS", code: "OBSERVABLE", observable: true, coverageFraction: 1, missingCriticalFaceIds: [], reasons: [] };
  resealDigest(calibrationForgery, "measurementDigest");
  assert.strictEqual(Sheet.validateMeasurement(calibrationForgery).valid, false);
});

test("measurement validator rejects attempts to promote engineering evidence", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var forged = mutable(measurementFor(emulator));
  forged.evidenceSeparation.extrinsicMeasurement = { status: "proved", basis: "theorem", evidenceClass: "physical-validation", synthetic: false, physicalMeasurement: true, uniquenessClaim: true, claimBoundary: "forged" };
  resealDigest(forged, "measurementDigest");
  assert.strictEqual(Sheet.validateMeasurement(forged).valid, false);
});

test("human planner proposes exact sector edits but inhibits nonpositive benefit", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var measurement = measurementFor(emulator);
  var add = Sheet.planSectorAction({ schemaVersion: 2, currentQ: 6, targetQ: 7, measurement: measurement });
  assert.strictEqual(add.recommendedAction, "ADD_SECTOR");
  assert.deepStrictEqual(add.predictedCenterDefectChangePiCoefficient, { denominator: 3, numerator: -1 });
  assert.strictEqual(add.requiresOperatorConfirmation, true);
  assert.strictEqual(add.controllerAssumesActionCompleted, false);
  var costly = Sheet.planSectorAction({ schemaVersion: 2, currentQ: 6, targetQ: 5, measurement: measurement, editCost: 1 });
  assert.strictEqual(costly.status, "NO_IMPROVING_ACTION");
  assert.strictEqual(costly.recommendedAction, "HOLD");
  assert.ok(costly.predictedLossDecrease < 0);
});

test("exact canonicalization makes every safe-integer millisecond checksum-visible", function () {
  var message = request("HELLO", 1, 1000000000000000, { clientId: "client" }, null, 100);
  var changed = Object.assign({}, message, { monotonicTimeMs: message.monotonicTimeMs + 1 });
  assert.strictEqual(Sheet.validateProtocolMessage(changed).code, "CORRUPT_CHECKSUM");
  assert.notStrictEqual(Sheet.stableStringify({ value: 1 }), Sheet.stableStringify({ value: 1.000000000000001 }));
  assert.throws(function () { Sheet.stableStringify({ text: "\ud800" }); }, /unpaired UTF-16 surrogate/);
});

test("prototype-inherited and accessor payloads cannot enter the checksum domain", function () {
  var inheritedPayload = Object.create({ channels: [{ id: "hinge-00", positionDeg: 10, maxRateDegPerSec: 10 }] });
  var frame = { protocol: Sheet.PROTOCOL, type: "COMMAND", seq: 1, monotonicTimeMs: 0, deadlineMs: 100, armEpoch: "arm-123456789012345678901234", payload: inheritedPayload };
  assert.throws(function () { Sheet.checksumMessage(frame); }, /unsupported|plain object/);
  var accessor = {};
  Object.defineProperty(accessor, "clientId", { enumerable: true, get: function () { return "hidden"; } });
  assert.throws(function () { request("HELLO", 1, 0, accessor, null); }, /data property/);
  var hostileFrame = {};
  Object.defineProperty(hostileFrame, "type", { enumerable: true, get: function () { throw new Error("getter executed"); } });
  var rejected = Sheet.createHilEmulator().receive(hostileFrame);
  assert.strictEqual(rejected.payload.code, "SCHEMA_INVALID");
});

test("sparse and decorated channel arrays are rejected before checksumming", function () {
  var sparse = []; sparse.length = 1;
  var decorated = [{ id: "hinge-00", positionDeg: 1, maxRateDegPerSec: 1 }]; decorated.extra = true;
  var customPrototype = [{ id: "hinge-00", positionDeg: 1, maxRateDegPerSec: 1 }]; Object.setPrototypeOf(customPrototype, { forEach: Array.prototype.forEach });
  var base = { plantId: "plant-123456789012345678901234", expectedStateRevision: 0, expectedStateDigest: "0".repeat(64), observationDigest: "1".repeat(64) };
  assert.throws(function () { request("COMMAND", 1, 0, Object.assign({}, base, { channels: sparse }), "arm-123456789012345678901234"); }, /dense and undecorated/);
  assert.throws(function () { request("COMMAND", 1, 0, Object.assign({}, base, { channels: decorated }), "arm-123456789012345678901234"); }, /dense and undecorated/);
  assert.throws(function () { request("COMMAND", 1, 0, Object.assign({}, base, { channels: customPrototype }), "arm-123456789012345678901234"); }, /ordinary array prototype/);
});

test("direction-specific schemas validate every emitted read-only response", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 5 } });
  var hello = emulator.receive(request("HELLO", 1, 0, { clientId: "client" }, null));
  var capabilities = emulator.receive(request("CAPABILITIES", 2, 0, { request: true }, null));
  var telemetry = emulator.receive(request("TELEMETRY", 3, 0, { request: true }, null));
  [hello, capabilities, telemetry].forEach(function (response) { assert.strictEqual(Sheet.validateProtocolResponse(response).valid, true); });
  assert.strictEqual(capabilities.payload.safetyMode, "OBSERVATION_BOUND");
  assert.strictEqual(capabilities.payload.hardwareAccess, false);
});

test("syntactically valid commands while disarmed are rejected without plant mutation", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var measurement = measurementFor(emulator), before = emulator.snapshot().plant.stateDigest;
  var response = emulator.receive(commandFor(emulator, measurement, "arm-123456789012345678901234", 1, 0));
  assert.strictEqual(response.payload.code, "COMMAND_WHILE_DISARMED");
  assert.strictEqual(emulator.snapshot().state, "DISARMED");
  assert.strictEqual(emulator.snapshot().plant.stateDigest, before);
});

test("only an observation of the controlled current plant is accepted", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6, seed: "controlled" } });
  assert.strictEqual(emulator.setObservation(measurementFor(emulator)).accepted, true);
  var other = Sheet.createHilEmulator({ plant: { q: 6, seed: "other" } });
  assert.strictEqual(emulator.setObservation(measurementFor(other)).code, "OBSERVATION_MODEL_MISMATCH");
  assert.strictEqual(emulator.snapshot().observation, null);
});

test("an observation is rejected after the plant state changes", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6, backlashDeg: 0 } });
  var old = measurementFor(emulator);
  var directPlant = Sheet.createVirtualPlant(emulator.snapshot().plant.config);
  directPlant.setTargets([{ id: "hinge-00", positionDeg: 5, maxRateDegPerSec: 5 }], 0);
  var changed = Sheet.measureVirtualPlant(directPlant.snapshot(), { noise: { heightStdMm: 0, hingeStdDeg: 0, dropoutProbability: 0 } });
  assert.notStrictEqual(old.sourceStateDigest, changed.sourceStateDigest);
  assert.strictEqual(emulator.setObservation(changed).code, "OBSERVATION_STATE_MISMATCH");
});

test("fresh bound observation permits exactly one bound command", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6, backlashDeg: 0 }, watchdogTimeoutMs: 200 });
  var measurement = measurementFor(emulator);
  assert.strictEqual(emulator.setObservation(measurement).accepted, true);
  var armed = arm(emulator, 1, 0, "bound-session");
  assert.strictEqual(Sheet.validateProtocolResponse(armed).valid, true);
  var response = emulator.receive(commandFor(emulator, measurement, armed.armEpoch, 2, 1, [{ id: "hinge-00", positionDeg: 10, maxRateDegPerSec: 10 }]));
  assert.strictEqual(response.type, "COMMAND");
  assert.strictEqual(response.payload.preStateRevision, 0);
  assert.ok(response.payload.postStateRevision > response.payload.preStateRevision);
  assert.strictEqual(emulator.snapshot().observation.consumedByCommand, true);
  assert.strictEqual(Sheet.validateProtocolResponse(response).valid, true);
});

test("wrong arm epoch is fail-closed", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var measurement = measurementFor(emulator); emulator.setObservation(measurement);
  var armed = arm(emulator, 1, 0, "epoch-session");
  var response = emulator.receive(commandFor(emulator, measurement, "arm-123456789012345678901234", 2, 1));
  assert.strictEqual(response.payload.code, "ARM_EPOCH_MISMATCH");
  assert.strictEqual(emulator.snapshot().state, "HOLD");
  assert.notStrictEqual(armed.armEpoch, "arm-123456789012345678901234");
});

test("high-sequence commands from an earlier ARM session cannot replay", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var firstMeasurement = measurementFor(emulator); emulator.setObservation(firstMeasurement);
  var firstArm = arm(emulator, 1, 0, "old-session");
  var oldCommand = commandFor(emulator, firstMeasurement, firstArm.armEpoch, 100, 3);
  emulator.receive(request("DISARM", 2, 1, { reason: "end-old" }, firstArm.armEpoch));
  var fresh = measurementFor(emulator); emulator.setObservation(fresh);
  var secondArm = arm(emulator, 3, 2, "new-session");
  assert.notStrictEqual(firstArm.armEpoch, secondArm.armEpoch);
  var replay = emulator.receive(oldCommand);
  assert.strictEqual(replay.payload.code, "ARM_EPOCH_MISMATCH");
  assert.strictEqual(emulator.snapshot().state, "HOLD");
});

test("command state and observation digests are independently bound", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var measurement = measurementFor(emulator); emulator.setObservation(measurement);
  var armed = arm(emulator, 1, 0, "binding-session");
  var badState = emulator.receive(commandFor(emulator, measurement, armed.armEpoch, 2, 1, null, { expectedStateDigest: "0".repeat(64) }));
  assert.strictEqual(badState.payload.code, "COMMAND_STATE_MISMATCH");

  emulator.receive(request("DISARM", 3, 2, { reason: "retry" }, armed.armEpoch));
  var fresh = measurementFor(emulator); emulator.setObservation(fresh); var rearmed = arm(emulator, 4, 2, "binding-session-2");
  var badObservation = emulator.receive(commandFor(emulator, fresh, rearmed.armEpoch, 5, 3, null, { observationDigest: "1".repeat(64) }));
  assert.strictEqual(badObservation.payload.code, "OBSERVATION_BINDING_MISMATCH");
});

test("one accepted command consumes its observation and requires remeasurement", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var measurement = measurementFor(emulator); emulator.setObservation(measurement); var armed = arm(emulator, 1, 0, "one-step");
  emulator.receive(commandFor(emulator, measurement, armed.armEpoch, 2, 1));
  emulator.tick(1);
  var second = emulator.receive(commandFor(emulator, measurement, armed.armEpoch, 3, 1, [{ id: "hinge-01", positionDeg: 5, maxRateDegPerSec: 5 }]));
  assert.strictEqual(second.payload.code, "REMEASUREMENT_REQUIRED");
  assert.strictEqual(emulator.snapshot().state, "HOLD");
});

test("watchdog enters HOLD at the exact declared deadline", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 }, watchdogTimeoutMs: 100 });
  arm(emulator, 1, 0, "timeout-session");
  var held = emulator.tick(100);
  assert.strictEqual(held.state, "HOLD");
  assert.strictEqual(held.activeFault.code, "WATCHDOG_TIMEOUT");
  assert.ok(emulator.transcript().events.some(function (event) { return event.code === "WATCHDOG_TIMEOUT" && event.atMs === 100; }));
});

test("stale sequence and corrupt checksum hold an armed emulator", function () {
  var staleEmulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var measurement = measurementFor(staleEmulator); staleEmulator.setObservation(measurement); var armed = arm(staleEmulator, 4, 0, "stale-session");
  var stale = staleEmulator.receive(commandFor(staleEmulator, measurement, armed.armEpoch, 4, 1));
  assert.strictEqual(stale.payload.code, "STALE_SEQUENCE");
  assert.strictEqual(staleEmulator.snapshot().state, "HOLD");

  var corruptEmulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var fresh = measurementFor(corruptEmulator); corruptEmulator.setObservation(fresh); var freshArm = arm(corruptEmulator, 1, 0, "checksum-session");
  var corrupt = corruptEmulator.receive(Sheet.corruptProtocolChecksum(commandFor(corruptEmulator, fresh, freshArm.armEpoch, 2, 1)));
  assert.strictEqual(corrupt.payload.code, "CORRUPT_CHECKSUM");
  assert.strictEqual(corruptEmulator.snapshot().state, "HOLD");
});

test("saturation is a fail-closed HOLD rather than clipped motion", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6, maxPositionDeg: 20 } });
  var measurement = measurementFor(emulator); emulator.setObservation(measurement); var armed = arm(emulator, 1, 0, "saturation-session");
  var rejected = emulator.receive(commandFor(emulator, measurement, armed.armEpoch, 2, 1, [{ id: "hinge-00", positionDeg: 21, maxRateDegPerSec: 5 }]));
  assert.strictEqual(rejected.payload.code, "SATURATION_LIMIT");
  assert.strictEqual(emulator.snapshot().state, "HOLD");
  assert.strictEqual(emulator.snapshot().plant.channels[0].positionDeg, 0);
  assert.strictEqual(emulator.snapshot().plant.channels[0].targetDeg, 0);
});

test("CRC-valid ESTOP has safety priority over stale sequence and latches", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var armed = arm(emulator, 5, 0, "estop-session");
  var stop = emulator.receive(request("ESTOP", 5, 0, { reason: "stale-but-valid-stop" }, armed.armEpoch));
  assert.strictEqual(stop.type, "ESTOP");
  assert.strictEqual(emulator.snapshot().state, "ESTOP");
  assert.strictEqual(emulator.snapshot().estopLatched, true);
  var attemptedClear = emulator.receive(request("DISARM", 6, 1, { reason: "try-clear" }, armed.armEpoch));
  assert.strictEqual(attemptedClear.payload.code, "ESTOP_LATCHED");
  assert.strictEqual(emulator.snapshot().state, "ESTOP");
});

test("unobservable sensing remains bound but cannot authorize motion", function () {
  var emulator = Sheet.createHilEmulator({ plant: { q: 6 } });
  var dropped = measurementFor(emulator, { forcedDropoutFaceIds: ["face-00"] });
  assert.strictEqual(emulator.setObservation(dropped).code, "SENSOR_UNOBSERVABLE");
  var armed = arm(emulator, 1, 0, "dropout-session");
  var response = emulator.receive(commandFor(emulator, dropped, armed.armEpoch, 2, 1));
  assert.strictEqual(response.payload.code, "SENSOR_UNOBSERVABLE");
  assert.strictEqual(emulator.snapshot().state, "HOLD");
});

test("observation interlock cannot be disabled in protocol v2", function () {
  assert.throws(function () { Sheet.createHilEmulator({ requireObservation: false }); }, /fixed to true/);
});

test("transcript contains full config, normalized inputs, endpoint states, and a valid hash chain", function () {
  var emulator = Sheet.createHilEmulator({ seed: "transcript", plant: { q: 6, seed: "transcript-plant" } });
  var measurement = measurementFor(emulator); emulator.setObservation(measurement); var armed = arm(emulator, 1, 0, "transcript-session");
  emulator.receive(commandFor(emulator, measurement, armed.armEpoch, 2, 1, [{ id: "hinge-00", positionDeg: 8, maxRateDegPerSec: 4 }]));
  emulator.tick(10);
  var transcript = emulator.transcript();
  assert.strictEqual(Sheet.validateHilTranscript(transcript).valid, true);
  assert.strictEqual(transcript.config.requireObservation, true);
  assert.strictEqual(transcript.safetyMode, "OBSERVATION_BOUND");
  var commandEvent = transcript.events.filter(function (event) { return event.normalizedInput && event.normalizedInput.type === "COMMAND"; })[0];
  assert.deepStrictEqual(commandEvent.normalizedInput.payload.channels, [{ id: "hinge-00", maxRateDegPerSec: 4, positionDeg: 8 }]);
  assert.strictEqual(Sheet.validateEmulatorSnapshot(commandEvent.preState).valid, true);
  assert.strictEqual(Sheet.validateEmulatorSnapshot(commandEvent.postState).valid, true);
  var tampered = mutable(transcript);
  commandEvent = tampered.events.filter(function (event) { return event.normalizedInput && event.normalizedInput.type === "COMMAND"; })[0];
  commandEvent.normalizedInput.payload.channels[0].positionDeg = 9;
  assert.strictEqual(Sheet.validateHilTranscript(tampered).valid, false);
});

test("scenario spec, transcript, responses, and final state replay byte-for-byte", function () {
  var config = { seed: "scenario-replay", plant: { q: 6, seed: "scenario-plant" }, watchdogTimeoutMs: 200 };
  var probe = Sheet.createHilEmulator(config);
  var measurement = measurementFor(probe); probe.setObservation(measurement);
  var armMessage = request("ARM", 1, 0, { sessionId: "scenario-session" }, null);
  var armResponse = probe.receive(armMessage);
  var commandMessage = commandFor(probe, measurement, armResponse.armEpoch, 2, 1, [{ id: "hinge-00", positionDeg: 8, maxRateDegPerSec: 4 }]);
  var scenario = { schemaVersion: 2, config: config, events: [
    { kind: "OBSERVATION", measurement: measurement },
    { kind: "MESSAGE", message: armMessage },
    { kind: "MESSAGE", message: commandMessage },
    { kind: "TICK", timeMs: 50 },
    { kind: "MESSAGE", message: request("HOLD", 3, 50, { reason: "scenario-complete" }, armResponse.armEpoch) }
  ] };
  var first = Sheet.runHilScenario(scenario), second = Sheet.runHilScenario(mutable(scenario));
  assert.strictEqual(Sheet.stableStringify(first), Sheet.stableStringify(second));
  assert.strictEqual(first.scenarioSpecDigest.length, 64);
  assert.strictEqual(first.scenarioDigest.length, 64);
  assert.strictEqual(first.finalState.state, "HOLD");
  assert.strictEqual(Sheet.validateHilTranscript(first.transcript).valid, true);
  assert.strictEqual(first.transcript.events.length, 5);
});

if (process.exitCode) {
  process.stderr.write("\nGlobal Geometry II programmable-sheet tests failed.\n");
} else {
  process.stdout.write("\n1.." + passed + "\nAll Global Geometry II programmable-sheet tests passed.\n");
}
