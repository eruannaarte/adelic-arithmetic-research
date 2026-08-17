"use strict";

/* global importScripts, OIGWindTunnelCore, self */
importScripts("./wind-tunnel-core.js");

const core = self.OIGWindTunnelCore;
const activeByToken = new Map();
const currentTokenByChannel = new Map();
let generation = 0;

function identity(message) {
  const channel = message.channel === undefined ? "default" : String(message.channel);
  if (!(typeof message.runId === "string" || Number.isSafeInteger(message.runId))) {
    throw new TypeError("worker runId must be a string or safe integer");
  }
  const runId = message.runId;
  return { channel, runId, token: channel + ":" + String(runId) };
}

function emit(type, id, body) {
  self.postMessage(Object.assign({ type, channel: id.channel, runId: id.runId }, body || {}));
}

function cancelState(state, reason) {
  if (!state) return;
  state.cancelled = true;
  state.cancelReason = reason || "cancelled";
}

function emitCancelled(state) {
  if (!state || state.cancelReported) return;
  state.cancelReported = true;
  emit("cancelled", state.id, { reason: state.cancelReason || "cancelled" });
}

async function execute(message) {
  const id = identity(message);
  const priorToken = currentTokenByChannel.get(id.channel);
  if (priorToken && activeByToken.has(priorToken)) {
    cancelState(activeByToken.get(priorToken), "superseded by a newer run on this channel");
  }
  const state = { id, generation: ++generation, cancelled: false, cancelReported: false };
  activeByToken.set(id.token, state);
  currentTokenByChannel.set(id.channel, id.token);
  const controls = {
    yieldEvery: message.payload && message.payload.yieldEvery,
    isCancelled: () => state.cancelled || currentTokenByChannel.get(id.channel) !== id.token,
    onProgress: progress => {
      if (!state.cancelled && currentTokenByChannel.get(id.channel) === id.token) {
        emit("progress", id, { progress });
      }
    }
  };
  try {
    let result;
    if (message.type === "run-ensemble") {
      const payload = message.payload || {};
      if (!payload.forecast) throw new TypeError("run-ensemble payload.forecast is required");
      result = await core.runEnsembleAsync(
        payload.forecast,
        payload.declaration || payload.options || {},
        controls
      );
    } else {
      const payload = message.payload || {};
      if (!payload.spec) throw new TypeError("run-laboratory payload.spec is required");
      result = await core.runLaboratoryStudyAsync(payload.spec, controls);
    }
    if (controls.isCancelled()) {
      cancelState(state, state.cancelReason || "stale result suppressed");
      emitCancelled(state);
    } else {
      emit("result", id, { result });
    }
  } catch (error) {
    if (state.cancelled || (error && error.code === "OIG_CANCELLED")) {
      emitCancelled(state);
    } else {
      emit("error", id, {
        error: {
          name: error && error.name ? String(error.name) : "Error",
          message: error && error.message ? String(error.message) : String(error)
        }
      });
    }
  } finally {
    if (activeByToken.get(id.token) === state) activeByToken.delete(id.token);
    if (currentTokenByChannel.get(id.channel) === id.token) currentTokenByChannel.delete(id.channel);
  }
}

self.addEventListener("message", event => {
  const message = event.data || {};
  if (message.type === "cancel") {
    try {
      const id = identity(message);
      const state = activeByToken.get(id.token);
      if (state) cancelState(state, "cancel requested");
    } catch (error) {
      self.postMessage({
        type: "error",
        channel: message.channel === undefined ? "default" : String(message.channel),
        runId: message.runId,
        error: { name: error.name, message: error.message }
      });
    }
    return;
  }
  if (message.type !== "run-ensemble" && message.type !== "run-laboratory") {
    self.postMessage({
      type: "error",
      channel: message.channel === undefined ? "default" : String(message.channel),
      runId: message.runId,
      error: { name: "RangeError", message: "unknown worker message type" }
    });
    return;
  }
  execute(message);
});
