(function () {
  "use strict";

  const core = globalThis.OIGWindTunnelCore;
  const evidence = globalThis.OIGWindTunnelData;
  const root = document.getElementById("wind-tunnel");
  if (!root || !core || !evidence) return;

  const $ = id => document.getElementById(id);
  const optional = id => $(id);
  const requiredIds = [
    "theta-1", "theta-2", "omega-1", "omega-2", "sensor", "duration",
    "preparation-radius", "noise-radius", "run-experiment", "play-pause",
    "dynamics-canvas", "sensor-chart", "torus-atlas"
  ];
  const missing = requiredIds.filter(id => !$(id));
  if (missing.length) throw new Error(`wind-tunnel markup is missing: ${missing.join(", ")}`);

  const controls = {
    theta1: $("theta-1"), theta2: $("theta-2"), omega1: $("omega-1"), omega2: $("omega-2"),
    sensor: $("sensor"), duration: $("duration"), preparation: $("preparation-radius"), noise: $("noise-radius")
  };
  const ensembleControls = {
    size: optional("ensemble-size"), realism: optional("realism-level"), mode: optional("uncertainty-mode"),
    seed: optional("ensemble-seed"), law: optional("perturbation-law"), amplitude: optional("law-amplitude"),
    direction: optional("perturbation-direction"), customAngle: optional("custom-direction-angle")
  };
  const canvases = { dynamics: $("dynamics-canvas"), chart: $("sensor-chart"), torus: $("torus-atlas") };
  const state = {
    forecast: null, outcome: null, playing: false, playhead: 0, lastFrame: 0,
    animation: null, previewTimer: null, previewGeneration: 0, running: false,
    camera: { yaw: -0.44, pitch: 0.18, zoom: 1 }, torusCamera: { yaw: -0.64, pitch: 0.46, zoom: 1 },
    torusHitTargets: [], atlasSelection: null,
    ensemble: null, ensembleDeclaration: null, ensembleView: null,
    activeRunId: null, laboratoryRunId: null, nextRequestToken: 0, laboratoryResult: null,
    workers: { interactive: null, laboratory: null }, worker: null, workerRequests: new Map(), laboratoryCancelled: false
  };

  function number(input) { return Number(input.value); }
  function format(value, digits = 4) {
    if (!Number.isFinite(value)) return "—";
    const magnitude = Math.abs(value);
    return magnitude !== 0 && (magnitude < 1e-3 || magnitude >= 1e4)
      ? value.toExponential(2)
      : value.toFixed(digits);
  }
  function directedLowerDecimal(value, digits) {
    const scale = 10 ** digits;
    const scaled = value * scale;
    const nearest = Math.round(scaled);
    // Decimal certificate bounds can land one binary ulp below their exact
    // terminating value. Snap only that representation artefact; otherwise
    // retain directed downward rounding for strict lower-bound copy.
    const tolerance = 8 * Number.EPSILON * Math.max(1, Math.abs(scaled));
    const directed = Math.abs(scaled - nearest) <= tolerance ? nearest : Math.floor(scaled);
    return (directed / scale).toFixed(digits);
  }
  const CERTIFIED_PROVENANCE_KEYS = Object.freeze([
    "grouped_clock_floor", "grouped_library", "persistence",
    "state_atlas", "two_row_floor", "variational_atlas"
  ]);
  function completeVerifiedProvenance(provenance) {
    if (!provenance || typeof provenance !== "object") return false;
    const keys = Object.keys(provenance);
    return keys.length === CERTIFIED_PROVENANCE_KEYS.length
      && CERTIFIED_PROVENANCE_KEYS.every(key => Object.hasOwn(provenance, key)
        && provenance[key] && provenance[key].verified === true);
  }
  function setText(id, value) { const node = optional(id); if (node) node.textContent = value; }
  function css(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
  function nextPaint() { return new Promise(resolve => requestAnimationFrame(() => resolve())); }

  function clamp(value, minimum, maximum) { return Math.max(minimum, Math.min(maximum, value)); }
  function quantile(sorted, probability) {
    if (!sorted.length) return NaN;
    const position = clamp(probability, 0, 1) * (sorted.length - 1);
    const lower = Math.floor(position); const upper = Math.ceil(position); const fraction = position - lower;
    return sorted[lower] * (1 - fraction) + sorted[upper] * fraction;
  }

  function currentRealism() {
    const level = ensembleControls.realism ? number(ensembleControls.realism) / 100 : 0.2;
    return {
      level,
      preparation: number(controls.preparation) * level,
      velocity: 0.2 * level,
      parameter: 0.02 * level,
      sensor: number(controls.noise) * level,
      clock: 0.01 * level
    };
  }

  function readEnsembleOptions(sizeOverride) {
    const realism = currentRealism();
    const angle = ensembleControls.customAngle ? number(ensembleControls.customAngle) * Math.PI / 180 : 0;
    const directionValue = ensembleControls.direction?.value || "weakest";
    const directionMap = { weakest: "oig-weakest", strongest: "oig-strongest", custom: "custom" };
    const alphaMultiplier = ensembleControls.amplitude ? number(ensembleControls.amplitude) : 0;
    const size = sizeOverride === undefined ? Math.round(number(ensembleControls.size)) : Math.round(sizeOverride);
    const common = {
      size,
      seed: Math.max(0, Math.trunc(number(ensembleControls.seed))),
      gates: { persistentExitSamples: 3, outlierRule: "terminal 1.5 IQR" }
    };
    if (size === 1) {
      return {
        ...common,
        seed: "oig-wind-tunnel-n1-legacy-v1",
        legacySingleDirection: true,
        uncertainty: { kind: "bounded", scale: number(controls.preparation), distribution: "uniform-disk" },
        structured: {
          law: "off", alpha: 0, alphaMultiplier: 0, amplitudeUnit: "radians",
          direction: "oig-weakest"
        },
        realism: {
          velocity: { kind: "off", scale: 0 }, parameters: { kind: "off", scale: 0 },
          sensor: { kind: "off", scale: 0 }, clock: { kind: "off", scale: 0 }
        }
      };
    }
    return {
      ...common,
      uncertainty: {
        kind: ensembleControls.mode?.value || "bounded",
        scale: realism.preparation,
        distribution: ensembleControls.mode?.value === "probabilistic" ? "normal" : undefined
      },
      structured: {
        law: ensembleControls.law?.value || "off",
        alpha: alphaMultiplier * number(controls.preparation),
        alphaMultiplier,
        amplitudeUnit: "radians",
        direction: directionMap[directionValue] || "oig-weakest",
        customDirection: directionValue === "custom" ? [Math.cos(angle), Math.sin(angle)] : undefined
      },
      realism: {
        velocity: { kind: ensembleControls.mode?.value || "bounded", scale: realism.velocity },
        parameters: { kind: ensembleControls.mode?.value || "bounded", scale: realism.parameter },
        sensor: { kind: ensembleControls.mode?.value || "bounded", scale: realism.sensor },
        clock: { kind: ensembleControls.mode?.value || "bounded", scale: realism.clock }
      }
    };
  }

  function samplingDisclosure(component) {
    if (!component || typeof component.samplingLaw !== "string" || typeof component.support !== "string") {
      return "Unavailable — core declaration did not serialize a sampling law and support.";
    }
    return `${component.samplingLaw}. Support: ${component.support}.`;
  }

  function renderRealismLaws(declaration) {
    const components = {
      preparation: declaration?.uncertainty,
      velocity: declaration?.realism?.velocity,
      parameter: declaration?.realism?.parameters,
      sensor: declaration?.realism?.sensor,
      clock: declaration?.realism?.clock
    };
    Object.entries(components).forEach(([name, component]) => {
      setText(`realism-${name}-law`, samplingDisclosure(component));
    });
  }

  function syncEnsembleOutputs(disclosureDeclaration = null) {
    if (!ensembleControls.size) return;
    const options = readEnsembleOptions(); const realism = currentRealism();
    const ensembleActive = options.size > 1;
    setText("ensemble-size-value", String(options.size));
    setText("realism-level-value", `${Math.round(100 * realism.level)}%${ensembleActive ? "" : " · inactive at N = 1"}`);
    setText("law-amplitude-value", ensembleActive
      ? `${options.structured.alphaMultiplier.toFixed(2)}× = ${options.structured.alpha.toFixed(4)} rad`
      : "inactive at N = 1");
    setText("custom-direction-angle-value", `${Math.round(number(ensembleControls.customAngle))}°`);
    setText("realism-preparation", `${options.uncertainty.scale.toFixed(4)} rad`);
    setText("realism-velocity", `${options.realism.velocity.scale.toFixed(3)} rad/s`);
    setText("realism-parameter", `${(100 * options.realism.parameters.scale).toFixed(2)}%`);
    setText("realism-sensor", options.realism.sensor.scale.toFixed(4));
    setText("realism-clock", `${(100 * options.realism.clock.scale).toFixed(2)}% of T`);
    renderRealismLaws(disclosureDeclaration);
    const lawFormula = {
      off: "f(s) = 0", linear: "f(s) = s", quadratic: "f(s) = 2s² − 1",
      sinusoidal: "f(s) = sin(πs)", radial: "f(s) = 2|s| − 1",
      geometric: "f(s) = sign(s) expm1(2|s|) / expm1(2)"
    }[options.structured.law];
    setText("structured-law-formula", lawFormula || "f(s) unresolved");
    const custom = ensembleActive && ensembleControls.direction?.value === "custom";
    for (const control of [ensembleControls.realism, ensembleControls.mode, ensembleControls.seed,
      ensembleControls.law, ensembleControls.amplitude, ensembleControls.direction, ensembleControls.customAngle]) {
      if (control) control.disabled = !ensembleActive;
    }
    if (ensembleControls.customAngle) ensembleControls.customAngle.disabled = !custom;
    optional("custom-direction-label")?.classList.toggle("is-disabled", !custom);
    if (ensembleControls.amplitude) ensembleControls.amplitude.disabled = !ensembleActive || ensembleControls.law?.value === "off";
    const bounded = options.uncertainty.kind === "bounded";
    setText("uncertainty-mode-explanation", !ensembleActive
      ? "N = 1 legacy mode: one deterministic held-out direction lies on the declared preparation-radius boundary. Ensemble realism, sampled-distribution, seed, and structured-law controls are inactive; the top-level preparation and readout-noise controls remain active."
      : bounded
        ? "Bounded mode: members are deterministic seeded points inside the displayed component bounds. Coverage is an empirical finite-sample count, not a probability guarantee."
        : "Seeded distribution mode: members are reproducible numerical draws from the disclosed declared distribution. Wilson intervals remain descriptive sample intervals, not certified probability guarantees.");
    setText("ensemble-control-scope-note", ensembleActive
      ? "Ensemble realism and structured-law controls are active for this N > 1 declaration."
      : "N = 1 uses the deterministic held-out boundary experiment; realism, distribution, seed, and structured-law controls activate only for N > 1.");
    setText("ensemble-mode-note", options.size === 1
      ? "N = 1 preserves the detailed single-outcome wind tunnel. Increase N to reveal finite-ensemble diagnostics."
      : `N = ${options.size} uses a seeded finite ensemble. The known design law is disclosed; microscopic member draws remain hidden until the outcome.`);
  }

  function readOptions() {
    const duration = number(controls.duration);
    const ensembleSize = ensembleControls.size ? Math.round(number(ensembleControls.size)) : 1;
    const realism = currentRealism();
    return {
      initialState: [number(controls.theta1), number(controls.theta2), number(controls.omega1), number(controls.omega2)],
      duration, sampleCount: Math.max(241, Math.round(40 * duration) + 1), sensor: controls.sensor.value,
      preparationRadius: ensembleSize > 1 ? realism.preparation : number(controls.preparation),
      noiseRadius: ensembleSize > 1 ? realism.sensor : number(controls.noise),
      derivativeStep: 2e-5, forecastStep: 1 / 160,
      parameters: evidence.stateAtlas.parameters
    };
  }

  function makeComputationWorker() {
    if (!("Worker" in globalThis)) return null;
    try {
      const coreUrl = new URL("wind-tunnel-core.js", location.href);
      const worker = new Worker(new URL("ensemble-worker.js", coreUrl));
      worker.onmessage = event => {
        const message = event.data || {}; const request = state.workerRequests.get(message.runId);
        if (!request) return; // Stale or explicitly cancelled work can never mutate the interface.
        if (message.channel !== request.channel) return;
        if (message.type === "progress") { request.onProgress?.(message.progress ?? message.payload?.progress ?? message.payload); return; }
        state.workerRequests.delete(message.runId);
        request.worker.terminate();
        if (state.workers[request.channel] === request.worker) state.workers[request.channel] = null;
        if (message.type === "result") request.resolve(message.result ?? message.payload?.result ?? message.payload);
        else if (message.type === "cancelled") request.reject(new DOMException("Cancelled", "AbortError"));
        else request.reject(new Error(message.message || message.error?.message || String(message.error || "Background computation failed")));
      };
      worker.onerror = event => {
        for (const [runId, request] of state.workerRequests) {
          if (request.worker !== worker) continue;
          state.workerRequests.delete(runId); request.reject(new Error(event.message || "Worker failed"));
          if (state.workers[request.channel] === worker) state.workers[request.channel] = null;
        }
        worker.terminate();
      };
      return worker;
    } catch (_error) { return null; }
  }

  function runWorkerRequest(type, runId, payload, onProgress, channel) {
    const worker = makeComputationWorker();
    if (!worker) return null;
    state.workers[channel] = worker;
    return new Promise((resolve, reject) => {
      state.workerRequests.set(runId, { resolve, reject, onProgress, worker, channel });
      try { worker.postMessage({ type, channel, runId, payload }); }
      catch (error) { state.workerRequests.delete(runId); worker.terminate(); state.workers[channel] = null; reject(error); }
    });
  }

  function cancelWorkerRequest(runId) {
    const request = state.workerRequests.get(runId);
    if (request) {
      try {
        if (request.channel) request.worker.postMessage({ type: "cancel", channel: request.channel, runId });
        else request.worker.postMessage({ type: "cancel", runId });
      } catch (_error) { /* termination below is authoritative */ }
      request.worker.terminate(); state.workerRequests.delete(runId);
      if (state.workers[request.channel] === request.worker) state.workers[request.channel] = null;
      state.worker = null; // Compatibility marker: cancellation always terminates; the channel recreates its worker on demand.
      request.reject(new DOMException("Cancelled", "AbortError"));
    }
  }

  async function invokeEnsemble(forecast, declaration, runId, onProgress) {
    if (typeof core.runEnsemble !== "function") throw new Error("This build does not include the ensemble engine yet; N = 1 remains available.");
    const workerRequest = runWorkerRequest("run-ensemble", runId, { forecast, declaration }, onProgress, "interactive");
    if (workerRequest) return workerRequest;
    setText("run-status", "Worker unavailable: running the ensemble on the main thread; the interface may pause until completion.");
    if (typeof core.runEnsembleAsync !== "function") throw new Error("Worker unavailable and the interruptible ensemble fallback is missing.");
    return core.runEnsembleAsync(forecast, declaration, {
      onProgress,
      isCancelled: () => runId !== state.activeRunId
    });
  }

  async function invokeLaboratory(spec, runId, onProgress) {
    if (typeof core.runLaboratoryStudy !== "function") throw new Error("This build does not include the background laboratory engine yet.");
    const workerRequest = runWorkerRequest("run-laboratory", runId, { spec }, onProgress, "laboratory");
    if (workerRequest) return workerRequest;
    setText("laboratory-status", "Worker unavailable: main-thread fallback may block until the current batch completes.");
    if (typeof core.runLaboratoryStudyAsync !== "function") throw new Error("Worker unavailable and the interruptible laboratory fallback is missing.");
    return core.runLaboratoryStudyAsync(spec, {
      onProgress,
      isCancelled: () => state.laboratoryCancelled || runId !== state.laboratoryRunId
    });
  }

  function trajectoryForMember(member) {
    return member?.trajectory || member?.actual || (member?.states && member?.times ? member : null);
  }

  function seriesForMember(member) {
    return member?.actualSensorSeries || member?.sensorSeries || member?.actualSensor || null;
  }

  function computeEnsembleView(result) {
    const members = Array.isArray(result?.members) ? result.members : [];
    const sampleCount = state.forecast?.times.length || 0;
    const declaredLaw = result?.declaration?.options?.structured?.law
      || state.ensembleDeclaration?.options?.structured?.law
      || state.ensembleDeclaration?.structured?.law || "off";
    const usable = members.filter(member => {
      const series = seriesForMember(member); const trajectory = trajectoryForMember(member);
      return Array.isArray(series) && series.length === sampleCount && trajectory && Array.isArray(trajectory.states);
    });
    const resolvedUsable = usable.filter(member => !member.audit || member.audit.status === "resolved");
    const unresolved = members.length - resolvedUsable.length;
    const coverage = Array.from({ length: sampleCount }, () => 0);
    const survival = Array.from({ length: sampleCount }, () => 0);
    const p05 = []; const p50 = []; const p95 = [];
    let persistentExits = 0; let reconvergence = 0;
    const memberAmplifications = [];
    const terminal = [];
    const terminalRecords = [];
    for (let timeIndex = 0; timeIndex < sampleCount; timeIndex += 1) {
      const values = resolvedUsable.map(member => seriesForMember(member)[timeIndex]).sort((a, b) => a - b);
      p05.push(quantile(values, 0.05)); p50.push(quantile(values, 0.5)); p95.push(quantile(values, 0.95));
    }
    resolvedUsable.forEach(member => {
      const series = seriesForMember(member); let everOutside = false; let outsideRun = 0; let persistent = false; let returned = false;
      const structuredCentre = member.predictedSensorSeries || member.predictedCentreSeries;
      const canUseBaselineFallback = declaredLaw === "off";
      const centre = Array.isArray(structuredCentre) && structuredCentre.length === sampleCount
        ? structuredCentre : canUseBaselineFallback ? state.forecast.baselineSensor : null;
      let square = 0;
      series.forEach((value, index) => {
        if (centre) {
          const inside = Math.abs(value - centre[index]) <= state.forecast.tubeRadius[index] + 1e-12;
          if (inside) { coverage[index] += 1; if (everOutside) returned = true; outsideRun = 0; }
          else { everOutside = true; outsideRun += 1; if (outsideRun >= 3) persistent = true; }
          if (!everOutside) survival[index] += 1;
          const difference = value - centre[index]; square += difference * difference;
        }
      });
      terminal.push(series[series.length - 1]);
      terminalRecords.push({ id: member.id, value: series[series.length - 1] });
      if (member.audit?.persistentExitIndex !== null && member.audit?.persistentExitIndex !== undefined || centre && persistent) persistentExits += 1;
      if (member.audit?.projectedReconvergence?.exitedThenReenteredTube === true || member.reconvergence === true || centre && returned) reconvergence += 1;
      memberAmplifications.push(Number.isFinite(member.audit?.amplification?.actual)
        ? member.audit.amplification.actual
        : Number.isFinite(member.amplification) ? member.amplification
        : centre ? Math.sqrt(square / Math.max(1, series.length)) / Math.max(1e-15, state.forecast.config.preparationRadius) : NaN);
    });
    const denominator = Math.max(1, resolvedUsable.length);
    for (let index = 0; index < sampleCount; index += 1) { coverage[index] /= denominator; survival[index] /= denominator; }
    const sortedTerminal = terminal.slice().sort((a, b) => a - b);
    const q1 = quantile(sortedTerminal, 0.25); const q3 = quantile(sortedTerminal, 0.75); const iqr = q3 - q1;
    const fallbackOutlierIds = terminalRecords
      .filter(record => record.value < q1 - 1.5 * iqr || record.value > q3 + 1.5 * iqr)
      .map(record => record.id);
    const terminalSuccesses = declaredLaw === "off" ? resolvedUsable.filter(member => {
      const series = seriesForMember(member); const index = series.length - 1;
      return Math.abs(series[index] - state.forecast.baselineSensor[index]) <= state.forecast.tubeRadius[index] + 1e-12;
    }).length : 0;
    const sortedAmplifications = memberAmplifications.filter(Number.isFinite).sort((a, b) => a - b);
    const authoritative = result?.summary?.timewise;
    const validCurve = value => Array.isArray(value) && value.length === sampleCount && value.every(Number.isFinite);
    const authoritativeCoverage = validCurve(authoritative?.coverage); const authoritativeSurvival = validCurve(authoritative?.survival);
    const preferredCoverage = authoritativeCoverage ? authoritative.coverage.slice() : declaredLaw === "off" ? coverage : Array(sampleCount).fill(NaN);
    const preferredSurvival = authoritativeSurvival ? authoritative.survival.slice() : declaredLaw === "off" ? survival : Array(sampleCount).fill(NaN);
    const preferredLow = validCurve(authoritative?.actual?.p05) ? authoritative.actual.p05.slice() : p05;
    const preferredMedian = validCurve(authoritative?.actual?.p50) ? authoritative.actual.p50.slice() : p50;
    const preferredHigh = validCurve(authoritative?.actual?.p95) ? authoritative.actual.p95.slice() : p95;
    const predictedLow = validCurve(authoritative?.predicted?.p05) ? authoritative.predicted.p05.slice() : state.forecast.baselineSensor.map((value, index) => value - state.forecast.tubeRadius[index]);
    const predictedMedian = validCurve(authoritative?.predicted?.p50) ? authoritative.predicted.p50.slice() : state.forecast.baselineSensor.slice();
    const predictedHigh = validCurve(authoritative?.predicted?.p95) ? authoritative.predicted.p95.slice() : state.forecast.baselineSensor.map((value, index) => value + state.forecast.tubeRadius[index]);
    const summary = result?.summary || {};
    const aggregateAmplification = summary.amplification || {};
    const stat = (value, fallback) => Number.isFinite(value) ? value : Number.isFinite(value?.p50) ? value.p50 : Number.isFinite(value?.mean) ? value.mean : fallback;
    const terminalOutliers = summary.terminalOutliers;
    const authoritativeOutliers = Number.isInteger(terminalOutliers?.count)
      && Array.isArray(terminalOutliers?.memberIds) && terminalOutliers.memberIds.length === terminalOutliers.count;
    const outlierIds = authoritativeOutliers ? terminalOutliers.memberIds.slice() : fallbackOutlierIds;
    const representativeOutlierIds = authoritativeOutliers && Array.isArray(terminalOutliers.representatives)
      ? terminalOutliers.representatives.map(record => record.id).filter(id => outlierIds.includes(id))
      : outlierIds.slice(0, 6);
    const fullStateAtReentry = summary.projectedReconvergence?.fullStateAtOutputReentry;
    const fallbackFullStateAtReentry = resolvedUsable
      .map(member => member.audit?.fullStateComparison?.outputReentryStateDistance)
      .filter(Number.isFinite).sort((left, right) => left - right);
    const authoritativeFullStateAtReentry = Number.isFinite(fullStateAtReentry?.p50);
    const fullStateAtReentryMedian = authoritativeFullStateAtReentry
      ? fullStateAtReentry.p50 : quantile(fallbackFullStateAtReentry, 0.5);
    const resolvedCount = Number.isInteger(summary.resolvedMemberCount) ? summary.resolvedMemberCount : resolvedUsable.length;
    const unresolvedCount = Number.isInteger(summary.unresolvedMemberCount) ? summary.unresolvedMemberCount : unresolved;
    const preferredPersistent = Number.isFinite(summary.exits?.persistentExitFraction)
      ? Math.round(summary.exits.persistentExitFraction * resolvedCount) : declaredLaw === "off" ? persistentExits : 0;
    const preferredReconvergence = Number.isFinite(summary.projectedReconvergence?.exitedAndReenteredTubeFraction)
      ? Math.round(summary.projectedReconvergence.exitedAndReenteredTubeFraction * resolvedCount) : reconvergence;
    const preferredTerminalSuccesses = authoritativeCoverage
      ? Math.round(preferredCoverage.at(-1) * resolvedCount) : declaredLaw === "off" ? terminalSuccesses : 0;
    const sampleCoverage = Number.isFinite(summary.coverage?.sampleFraction)
      ? summary.coverage.sampleFraction
      : preferredCoverage.filter(Number.isFinite).reduce((sum, value) => sum + value, 0)
        / Math.max(1, preferredCoverage.filter(Number.isFinite).length);
    const wholeMemberSurvival = Number.isFinite(summary.coverage?.wholeMemberFraction)
      ? summary.coverage.wholeMemberFraction : preferredSurvival.at(-1);
    const authoritativeInterval = summary.coverage?.wilson95;
    const intervalEligible = Number.isFinite(authoritativeInterval?.lower) && Number.isFinite(authoritativeInterval?.upper);
    const authoritativeSummaryUsed = Boolean(authoritativeCoverage && authoritativeSurvival
      && validCurve(authoritative?.actual?.p05) && validCurve(authoritative?.actual?.p50)
      && validCurve(authoritative?.actual?.p95) && validCurve(authoritative?.predicted?.p05)
      && validCurve(authoritative?.predicted?.p50) && validCurve(authoritative?.predicted?.p95));
    return {
      members, usable, resolvedUsable, resolvedCount,
      unresolved: unresolvedCount + (!authoritativeCoverage && declaredLaw !== "off" ? usable.length : 0), coverage: preferredCoverage, survival: preferredSurvival,
      p05: preferredLow, p50: preferredMedian, p95: preferredHigh, predictedLow, predictedMedian, predictedHigh,
      persistentExits: preferredPersistent, reconvergence: preferredReconvergence,
      outliers: outlierIds.length, outlierIds, representativeOutlierIds,
      outlierRule: authoritativeOutliers ? terminalOutliers.rule : "interface compatibility fallback: terminal selected-sensor 1.5×IQR",
      authoritativeOutliers,
      fullStateAtReentryMedian,
      authoritativeFullStateAtReentry,
      terminalSuccesses: preferredTerminalSuccesses, sampleCoverage, wholeMemberSurvival,
      interval: intervalEligible ? [authoritativeInterval.lower, authoritativeInterval.upper] : [NaN, NaN], intervalEligible,
      intervalInterpretation: summary.coverage?.intervalInterpretation || "No authoritative probability interval was returned.",
      persistenceDefinition: summary.exits?.persistentExitDefinition || null,
      authoritativeSummaryUsed,
      amplification: {
        predicted: stat(aggregateAmplification.predicted, state.forecast.information.weakestGain),
        p05: Number.isFinite(aggregateAmplification.actual?.p05) ? aggregateAmplification.actual.p05 : quantile(sortedAmplifications, 0.05),
        median: stat(aggregateAmplification.actual, quantile(sortedAmplifications, 0.5)),
        p95: Number.isFinite(aggregateAmplification.actual?.p95) ? aggregateAmplification.actual.p95 : quantile(sortedAmplifications, 0.95)
      }
    };
  }

  function syncControlOutputs() {
    const values = {
      "theta-1-value": `${number(controls.theta1).toFixed(2)} rad`,
      "theta-2-value": `${number(controls.theta2).toFixed(2)} rad`,
      "omega-1-value": `${number(controls.omega1).toFixed(2)} rad/s`,
      "omega-2-value": `${number(controls.omega2).toFixed(2)} rad/s`,
      "duration-value": `${number(controls.duration).toFixed(1)} s`,
      "preparation-radius-value": `${number(controls.preparation).toFixed(3)} rad`,
      "noise-radius-value": number(controls.noise).toFixed(3)
    };
    Object.entries(values).forEach(([id, value]) => setText(id, value));
  }

  function setTier(id, status, detail) {
    const node = optional(id);
    if (!node) return;
    node.dataset.state = status;
    const output = optional(`${id}-status`);
    if (output) output.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    const small = node.querySelector("small"); if (small && detail) small.textContent = detail;
  }

  function resizeCanvas(canvas) {
    const ratio = Math.min(2, globalThis.devicePixelRatio || 1);
    const box = canvas.getBoundingClientRect();
    const width = Math.max(260, Math.round(box.width));
    const height = Math.max(220, Math.round(box.height));
    if (canvas.width !== Math.round(width * ratio) || canvas.height !== Math.round(height * ratio)) {
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
    }
    const ctx = canvas.getContext("2d");
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    return { ctx, width, height };
  }

  function projectPoint(point, camera, width, height, scale) {
    const [x, y, z] = point;
    const cy = Math.cos(camera.yaw); const sy = Math.sin(camera.yaw);
    const cp = Math.cos(camera.pitch); const sp = Math.sin(camera.pitch);
    const rx = cy * x + sy * z;
    const rz = -sy * x + cy * z;
    const ry = cp * y - sp * rz;
    const rz2 = sp * y + cp * rz;
    const perspective = 1 / Math.max(0.45, 1 + 0.15 * rz2);
    return [width / 2 + scale * rx * perspective, height * 0.28 + scale * ry * perspective, rz2];
  }

  function pendulumPoints(pendulumState, parameters, depth = 0) {
    const positions = core.bobPositions(pendulumState, parameters);
    return [positions.pivot, positions.bob1, positions.bob2].map(([x, y]) => [x, y, depth]);
  }

  function drawFloor(ctx, width, height, scale) {
    ctx.save();
    ctx.strokeStyle = css("--wt-grid") || "rgba(110,140,150,.2)";
    ctx.lineWidth = 1;
    for (let index = -4; index <= 4; index += 1) {
      const a = projectPoint([index * 0.5, 2.3, -2], state.camera, width, height, scale);
      const b = projectPoint([index * 0.5, 2.3, 2], state.camera, width, height, scale);
      const c = projectPoint([-2, 2.3, index * 0.5], state.camera, width, height, scale);
      const d = projectPoint([2, 2.3, index * 0.5], state.camera, width, height, scale);
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(c[0], c[1]); ctx.lineTo(d[0], d[1]); ctx.stroke();
    }
    ctx.restore();
  }

  function drawTrail(ctx, trajectory, endIndex, parameters, camera, width, height, scale, color, depth) {
    if (!trajectory) return;
    ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.globalAlpha = 0.5;
    ctx.beginPath();
    const start = Math.max(0, endIndex - 80);
    for (let index = start; index <= endIndex; index += 2) {
      const p = pendulumPoints(trajectory.states[index], parameters, depth)[2];
      const q = projectPoint(p, camera, width, height, scale);
      if (index === start) ctx.moveTo(q[0], q[1]); else ctx.lineTo(q[0], q[1]);
    }
    ctx.stroke(); ctx.restore();
  }

  function drawOnePendulum(ctx, pendulumState, parameters, camera, width, height, scale, style, depth) {
    const points = pendulumPoints(pendulumState, parameters, depth).map(point => projectPoint(point, camera, width, height, scale));
    ctx.save(); ctx.globalAlpha = style.alpha; ctx.lineCap = "round";
    ctx.strokeStyle = style.line; ctx.lineWidth = style.width;
    ctx.beginPath(); ctx.moveTo(points[0][0], points[0][1]); ctx.lineTo(points[1][0], points[1][1]); ctx.lineTo(points[2][0], points[2][1]); ctx.stroke();
    [points[1], points[2]].forEach((point, index) => {
      const radius = index ? 10 : 8;
      const gradient = ctx.createRadialGradient(point[0] - 3, point[1] - 3, 1, point[0], point[1], radius);
      gradient.addColorStop(0, style.highlight); gradient.addColorStop(1, style.fill);
      ctx.fillStyle = gradient; ctx.beginPath(); ctx.arc(point[0], point[1], radius, 0, 2 * Math.PI); ctx.fill();
    });
    ctx.restore();
  }

  function representativeIndices(length, count, pinnedIndices = []) {
    if (length <= count) return Array.from({ length }, (_, index) => index);
    const pinned = [...new Set(pinnedIndices)].filter(index => Number.isInteger(index) && index >= 0 && index < length);
    const target = Math.max(count, pinned.length);
    const result = pinned.slice();
    const candidates = Array.from({ length: Math.max(count, 2) }, (_, index) =>
      Math.round(index * (length - 1) / Math.max(1, count - 1)));
    for (const index of candidates) if (!result.includes(index) && result.length < target) result.push(index);
    for (let index = 0; result.length < target && index < length; index += 1) {
      if (!result.includes(index)) result.push(index);
    }
    return result.sort((left, right) => left - right);
  }

  function drawEnsembleDynamics(ctx, width, height, scale, parameters, index) {
    const members = state.ensembleView?.usable || [];
    if (!members.length) return false;
    const count = members.length;
    const detailed = count <= 8; const representatives = detailed ? count : count <= 24 ? 6 : 10;
    if (!detailed) {
      ctx.save();
      for (const member of members) {
        const trajectory = trajectoryForMember(member); const sample = trajectory.states[Math.min(index, trajectory.states.length - 1)];
        const tip = projectPoint(pendulumPoints(sample, parameters, 0)[2], state.camera, width, height, scale);
        ctx.fillStyle = count > 24 ? "rgba(255,154,98,.08)" : "rgba(255,154,98,.18)";
        ctx.beginPath(); ctx.arc(tip[0], tip[1], count > 24 ? 13 : 7, 0, 2 * Math.PI); ctx.fill();
      }
      ctx.restore();
    }
    const outlierIds = new Set(state.ensembleView?.outlierIds || []);
    const pinnedIndices = members.flatMap((member, memberIndex) => outlierIds.has(member.id) ? [memberIndex] : []);
    const indices = representativeIndices(count, representatives, pinnedIndices);
    indices.forEach((memberIndex, displayIndex) => {
      const member = members[memberIndex]; const trajectory = trajectoryForMember(member);
      const sample = trajectory.states[Math.min(index, trajectory.states.length - 1)];
      const alpha = detailed ? Math.max(0.28, 0.9 - displayIndex * 0.07) : count <= 24 ? 0.28 : 0.18;
      const outlier = outlierIds.has(member.id);
      drawOnePendulum(ctx, sample, parameters, state.camera, width, height, scale,
        { line: outlier ? "#ff6f7d" : "#f5b06f", fill: outlier ? "#b82f4d" : "#e57048", highlight: "#fff2d8", alpha: outlier ? Math.max(alpha, 0.75) : alpha, width: outlier ? 3.2 : detailed ? 2.6 : 1.5 },
        (displayIndex - indices.length / 2) * 0.006);
    });
    drawOnePendulum(ctx, state.forecast.baseline.states[index], parameters, state.camera, width, height, scale,
      { line: "#6ec6c4", fill: "#378e91", highlight: "#e6ffff", alpha: 0.8, width: 3.5 }, -0.045);
    const pinnedNote = pinnedIndices.length ? `; ${pinnedIndices.length} terminal outlier${pinnedIndices.length === 1 ? "" : "s"} pinned` : "";
    const policy = detailed ? `${count} ghost pendulums${pinnedNote}` : count <= 24 ? `${indices.length} representatives + ${count}-tip cloud${pinnedNote}` : `${indices.length} representatives + ${count}-member density cloud${pinnedNote}`;
    setText("ensemble-display-policy", policy);
    setText("animation-status", count <= 8 ? "Ghost ensemble" : count <= 24 ? "Representative cloud" : "Density summary");
    return true;
  }

  function drawDynamics() {
    const { ctx, width, height } = resizeCanvas(canvases.dynamics);
    ctx.clearRect(0, 0, width, height);
    const background = ctx.createLinearGradient(0, 0, 0, height);
    background.addColorStop(0, css("--wt-stage-top") || "#102731");
    background.addColorStop(1, css("--wt-stage-bottom") || "#071216");
    ctx.fillStyle = background; ctx.fillRect(0, 0, width, height);
    const scale = Math.min(width, height) * 0.22 * state.camera.zoom;
    drawFloor(ctx, width, height, scale);
    const parameters = evidence.stateAtlas.parameters;
    if (!state.forecast) {
      drawOnePendulum(ctx, readOptions().initialState, parameters, state.camera, width, height, scale,
        { line: "#7bd7d2", fill: "#36a4a2", highlight: "#eaffff", alpha: 1, width: 5 }, 0);
      return;
    }
    const index = Math.max(0, Math.min(state.forecast.times.length - 1, Math.floor(state.playhead)));
    if (state.ensemble && drawEnsembleDynamics(ctx, width, height, scale, parameters, index)) {
      setText("simulation-time", `${state.forecast.times[index].toFixed(2)} s`);
      const scrubber = optional("animation-scrubber");
      if (scrubber) scrubber.value = String(Math.round(1000 * index / (state.forecast.times.length - 1)));
      return;
    }
    drawTrail(ctx, state.forecast.baseline, index, parameters, state.camera, width, height, scale, "#80dad3", -0.035);
    if (state.outcome) drawTrail(ctx, state.outcome.actual, index, parameters, state.camera, width, height, scale, "#ff9a62", 0.035);
    drawOnePendulum(ctx, state.forecast.baseline.states[index], parameters, state.camera, width, height, scale,
      { line: "#6ec6c4", fill: "#378e91", highlight: "#e6ffff", alpha: 0.42, width: 4 }, -0.035);
    if (state.outcome) {
      drawOnePendulum(ctx, state.outcome.actual.states[index], parameters, state.camera, width, height, scale,
        { line: "#ffd28a", fill: "#ef754b", highlight: "#fff7dc", alpha: 1, width: 5 }, 0.035);
    }
    setText("simulation-time", `${state.forecast.times[index].toFixed(2)} s`);
    const scrubber = optional("animation-scrubber");
    if (scrubber) scrubber.value = String(Math.round(1000 * index / (state.forecast.times.length - 1)));
  }

  function chartCoordinates(width, height) {
    return { left: 54, right: width - 18, top: 18, bottom: height - 38 };
  }

  function drawSensorChart() {
    const svg = canvases.chart;
    const ns = "http://www.w3.org/2000/svg";
    const width = 800; const height = 520;
    const content = optional("sensor-chart-content") || svg;
    content.textContent = "";
    function element(name, attributes, text) {
      const node = document.createElementNS(ns, name);
      Object.entries(attributes || {}).forEach(([key, value]) => node.setAttribute(key, String(value)));
      if (text !== undefined) node.textContent = text;
      return node;
    }
    const box = chartCoordinates(width, height);
    if (!state.forecast) {
      optional("chart-empty-state")?.removeAttribute("hidden");
      return;
    }
    optional("chart-empty-state")?.setAttribute("hidden", "");
    const lower = state.ensembleView?.predictedLow
      || state.forecast.baselineSensor.map((value, index) => value - state.forecast.tubeRadius[index]);
    const upper = state.ensembleView?.predictedHigh
      || state.forecast.baselineSensor.map((value, index) => value + state.forecast.tubeRadius[index]);
    const ensembleValues = state.ensembleView ? state.ensembleView.p05.concat(state.ensembleView.p95).filter(Number.isFinite) : [];
    const values = lower.concat(upper, ensembleValues, state.outcome ? state.outcome.actualSensor : []);
    let lo = Math.min(...values); let hi = Math.max(...values);
    const padding = Math.max(0.04, (hi - lo) * 0.12); lo -= padding; hi += padding;
    const x = index => box.left + index * (box.right - box.left) / (state.forecast.times.length - 1);
    const y = value => box.bottom - (value - lo) * (box.bottom - box.top) / Math.max(1e-12, hi - lo);
    for (let tick = 0; tick <= 4; tick += 1) {
      const py = box.top + tick * (box.bottom - box.top) / 4;
      const value = hi - tick * (hi - lo) / 4;
      content.appendChild(element("line", { x1: box.left, x2: box.right, y1: py, y2: py, class: "grid-line" }));
      content.appendChild(element("text", { x: 8, y: py + 4, class: "muted-label" }, format(value, 2)));
    }
    const upperPath = upper.map((value, index) => `${index ? "L" : "M"}${x(index).toFixed(2)},${y(value).toFixed(2)}`).join(" ");
    const lowerPath = lower.map((value, index) => `L${x(lower.length - 1 - index).toFixed(2)},${y(lower[lower.length - 1 - index]).toFixed(2)}`).join(" ");
    content.appendChild(element("path", { d: `${upperPath} ${lowerPath} Z`, class: "uncertainty-area" }));
    function line(series, className, end) {
      const path = series.slice(0, end + 1).map((value, index) => `${index ? "L" : "M"}${x(index).toFixed(2)},${y(value).toFixed(2)}`).join(" ");
      content.appendChild(element("path", { d: path, class: className, fill: "none" }));
    }
    line(state.ensembleView?.predictedMedian || state.forecast.baselineSensor, "forecast-series", state.forecast.times.length - 1);
    if (state.ensembleView?.usable.length) {
      const end = Math.min(state.forecast.times.length - 1, Math.floor(state.playhead));
      if (state.ensembleView.usable.length <= 8) {
        state.ensembleView.usable.forEach(member => line(seriesForMember(member), "ensemble-member-series", end));
      } else {
        const observedUpper = state.ensembleView.p95;
        const observedLower = state.ensembleView.p05;
        const observedUpperPath = observedUpper.slice(0, end + 1).map((value, index) => `${index ? "L" : "M"}${x(index).toFixed(2)},${y(value).toFixed(2)}`).join(" ");
        const observedLowerPath = observedLower.slice(0, end + 1).reverse().map((value, reverseIndex) => {
          const index = end - reverseIndex; return `L${x(index).toFixed(2)},${y(value).toFixed(2)}`;
        }).join(" ");
        content.appendChild(element("path", { d: `${observedUpperPath} ${observedLowerPath} Z`, class: "ensemble-observed-area" }));
        line(state.ensembleView.p50, "ensemble-median-series", end);
      }
    }
    if (state.outcome) line(state.outcome.actualSensor, "actual-series", Math.min(state.outcome.actualSensor.length - 1, Math.floor(state.playhead)));
    content.appendChild(element("rect", { x: box.left, y: box.top, width: box.right - box.left, height: box.bottom - box.top, fill: "none", class: "axis" }));
    content.appendChild(element("text", { x: box.left, y: height - 12, class: "muted-label" }, "0"));
    content.appendChild(element("text", { x: box.right - 42, y: height - 12, class: "muted-label" }, `${state.forecast.config.duration.toFixed(1)} s`));
  }

  function torusPoint(u, v) {
    const major = 1.35; const minor = 0.54;
    return [(major + minor * Math.cos(v)) * Math.cos(u), minor * Math.sin(v), (major + minor * Math.cos(v)) * Math.sin(u)];
  }

  function colorForGain(value, min, max, resolved) {
    if (!resolved || value === null) return "rgba(218,92,79,.68)";
    const t = Math.max(0, Math.min(1, (Math.log1p(value) - min) / Math.max(1e-9, max - min)));
    const hue = 182 - 142 * t;
    const light = 61 - 13 * t;
    return `hsl(${hue} 68% ${light}%)`;
  }

  function wrappedDistance(a, b) {
    return Math.abs(Math.atan2(Math.sin(a - b), Math.cos(a - b)));
  }

  function nearestAtlasCell(theta1, theta2) {
    const a1 = evidence.variationalAtlas.angles1; const a2 = evidence.variationalAtlas.angles2;
    let row = 0; let column = 0;
    for (let index = 1; index < a1.length; index += 1) if (wrappedDistance(theta1, a1[index]) < wrappedDistance(theta1, a1[row])) row = index;
    for (let index = 1; index < a2.length; index += 1) if (wrappedDistance(theta2, a2[index]) < wrappedDistance(theta2, a2[column])) column = index;
    return [row, column];
  }

  function updateAtlasReadout(row, column) {
    const fields = evidence.variationalAtlas.fields;
    const resolved = fields.resolvedMask[row][column];
    setText("atlas-cell", `(${row}, ${column}) · θ = (${evidence.variationalAtlas.angles1[row].toFixed(2)}, ${evidence.variationalAtlas.angles2[column].toFixed(2)})`);
    setText("atlas-weakest", resolved ? format(fields.weakestGain[row][column], 3) : "unresolved");
    setText("atlas-strongest", resolved ? format(fields.strongestGain[row][column], 3) : "unresolved");
    setText("atlas-status", resolved ? "Tier-1 variational gates passed" : "withheld: declared gates failed");
  }

  function drawTorus() {
    const { ctx, width, height } = resizeCanvas(canvases.torus);
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = css("--wt-chart-bg") || "#f8faf8"; ctx.fillRect(0, 0, width, height);
    const fields = evidence.variationalAtlas.fields;
    const selection = optional("atlas-field-select")?.value || "weakest";
    const fieldMap = {
      weakest: { title: "Weakest local gain", values: fields.weakestGain, resolved: fields.resolvedMask },
      strongest: { title: "Strongest local gain", values: fields.strongestGain, resolved: fields.resolvedMask },
      stretch: { title: "Finite-time grid-edge log stretch", values: evidence.stateAtlas.fields.logStretch, resolved: evidence.stateAtlas.fields.logStretch.map(row => row.map(() => true)) },
      energy: { title: "Initial mechanical energy", values: evidence.stateAtlas.fields.initialEnergy, resolved: evidence.stateAtlas.fields.initialEnergy.map(row => row.map(() => true)) },
      resolved: { title: "Variational resolution status", values: fields.resolvedMask.map(row => row.map(value => value ? 1 : 0)), resolved: fields.resolvedMask.map(row => row.map(() => true)) }
    };
    const chosen = fieldMap[selection] || fieldMap.weakest;
    setText("atlas-field-title", chosen.title);
    const side = chosen.resolved.length;
    const flat = chosen.values.flat().filter(value => value !== null);
    const min = Math.min(...flat.map(Math.log1p)); const max = Math.max(...flat.map(Math.log1p));
    const scale = Math.min(width, height) * 0.23 * state.torusCamera.zoom;
    const project = point => projectPoint(point, state.torusCamera, width, height * 1.18, scale);
    const patches = [];
    state.torusHitTargets = [];
    for (let row = 0; row < side; row += 1) {
      for (let column = 0; column < side; column += 1) {
        const u0 = -Math.PI + 2 * Math.PI * row / side;
        const u1 = -Math.PI + 2 * Math.PI * (row + 1) / side;
        const v0 = -Math.PI + 2 * Math.PI * column / side;
        const v1 = -Math.PI + 2 * Math.PI * (column + 1) / side;
        const points = [torusPoint(u0, v0), torusPoint(u1, v0), torusPoint(u1, v1), torusPoint(u0, v1)].map(project);
        const depth = points.reduce((sum, p) => sum + p[2], 0) / 4;
        patches.push({ row, column, points, depth });
      }
    }
    patches.sort((left, right) => left.depth - right.depth);
    for (const patch of patches) {
      const resolved = chosen.resolved[patch.row][patch.column];
      ctx.beginPath(); patch.points.forEach((p, index) => index ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath();
      ctx.fillStyle = colorForGain(chosen.values[patch.row][patch.column], min, max, resolved); ctx.fill();
      ctx.strokeStyle = "rgba(255,255,255,.22)"; ctx.lineWidth = 0.6; ctx.stroke();
      const cx = patch.points.reduce((sum, p) => sum + p[0], 0) / 4;
      const cy = patch.points.reduce((sum, p) => sum + p[1], 0) / 4;
      state.torusHitTargets.push({ row: patch.row, column: patch.column, x: cx, y: cy });
    }
    const selected = nearestAtlasCell(number(controls.theta1), number(controls.theta2));
    state.atlasSelection = selected;
    const marker = state.torusHitTargets.find(hit => hit.row === selected[0] && hit.column === selected[1]);
    if (marker) {
      ctx.fillStyle = "#fff"; ctx.strokeStyle = "#111"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(marker.x, marker.y, 6, 0, 2 * Math.PI); ctx.fill(); ctx.stroke();
    }
    updateAtlasReadout(selected[0], selected[1]);
    setText("atlas-scale-min", format(Math.min(...flat), 2));
    setText("atlas-scale-max", format(Math.max(...flat), 2));
  }

  function updateForecastReadout() {
    if (!state.forecast) return;
    const info = state.forecast.information;
    const response = state.forecast.responseRefinement;
    setText("weakest-gain", format(info.weakestGain, 4));
    setText("strongest-gain", format(info.strongestGain, 4));
    setText("gain-ratio", info.weakestGain > 0 ? format(info.strongestGain / info.weakestGain, 2) : "∞");
    setText("weakest-direction", `[${info.weakestDirection.map(value => value.toFixed(3)).join(", ")}]`);
    setText("strongest-direction", `[${info.strongestDirection.map(value => value.toFixed(3)).join(", ")}]`);
    setText("response-refinement-discrepancy", Number.isFinite(response?.maximumRelativeDiscrepancy)
      ? `${(100 * response.maximumRelativeDiscrepancy).toFixed(3)}% / ${(100 * response.tolerance).toFixed(1)}% gate`
      : "unresolved");
    setText("weakest-gain-shift", Number.isFinite(response?.weakestGainRelativeShift)
      ? `${(100 * response.weakestGainRelativeShift).toFixed(3)}%` : "unresolved");
    setText("strongest-gain-shift", Number.isFinite(response?.strongestGainRelativeShift)
      ? `${(100 * response.strongestGainRelativeShift).toFixed(3)}%` : "unresolved");
    const r = state.forecast.recommendation;
    setText("recommendation-text", `${r.sensorLabel} at t = ${r.time.toFixed(2)} s; predicted weakest gain ${r.weakestGain.toFixed(3)} (local, cost-free).`);
    setText("recommendation-sensor", r.sensorLabel);
    setText("recommendation-time", `${r.time.toFixed(2)} s`);
    setText("recommendation-floor", format(r.informationFloor, 5));
    const apply = optional("apply-recommendation"); if (apply) apply.disabled = false;
    const weakMeter = optional("weakest-gain-meter"); const strongMeter = optional("strongest-gain-meter");
    if (weakMeter && strongMeter) {
      const ratio = Math.min(1, info.weakestGain / Math.max(1e-12, info.strongestGain));
      weakMeter.setAttribute("aria-valuenow", String(ratio)); strongMeter.setAttribute("aria-valuenow", "1");
      const weakFill = weakMeter.querySelector("i"); const strongFill = strongMeter.querySelector("i");
      if (weakFill) weakFill.style.width = `${100 * ratio}%`; if (strongFill) strongFill.style.width = "100%";
    }
  }

  function updateOutcomeReadout() {
    if (!state.outcome) return;
    setText("tube-coverage", `${(100 * state.outcome.coverage).toFixed(1)}%`);
    setText("predicted-amplification", format(state.outcome.predictedAmplification, 3));
    setText("actual-amplification", format(state.outcome.actualAmplification, 3));
    setText("refinement-error", format(state.outcome.refinementDiscrepancy, 3));
    setText("energy-drift", format(state.outcome.maxEnergyDrift, 3));
    setText("endpoint-classification", state.outcome.classification);
    setText("held-out-direction", `[${state.outcome.direction.map(value => value.toFixed(3)).join(", ")}]`);
    const refinedPassed = state.outcome.evidenceGates?.refinedEvidencePassed === true;
    setText("result-summary", !refinedPassed
      ? "The outcome completed, but at least one baseline, response-refinement, or energy gate failed. This trial remains Live/unresolved and is not promoted to Refined evidence."
      : state.outcome.coverage >= 0.95
        ? "The held-out numerical outcome broadly supports this frozen first-order forecast; inspect the ledger for exact caveats."
        : "The held-out numerical outcome escaped the declared first-order tube. This trial falsifies that live forecast at its chosen scale.");
  }

  function svgElement(name, attributes, text) {
    const node = document.createElementNS("http://www.w3.org/2000/svg", name);
    Object.entries(attributes || {}).forEach(([key, value]) => node.setAttribute(key, String(value)));
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function renderLinePlot(contentId, series, options) {
    const content = optional(contentId); if (!content) return;
    content.textContent = "";
    const width = options.width || 800; const height = options.height || 420;
    const box = { left: 54, right: width - 18, top: 18, bottom: height - 38 };
    const validSeries = series.filter(item => Array.isArray(item.values) && item.values.length && item.values.every(Number.isFinite));
    if (!validSeries.length) {
      content.appendChild(svgElement("text", { x: box.left, y: box.top + 24, class: "muted-label" }, "No resolved numerical curve available."));
      return;
    }
    const length = Math.max(2, ...validSeries.map(item => item.values.length));
    const finite = validSeries.flatMap(item => item.values);
    let lo = options.minimum ?? Math.min(...finite); let hi = options.maximum ?? Math.max(...finite);
    if (!(hi > lo)) { lo -= 0.5; hi += 0.5; }
    const x = index => box.left + index * (box.right - box.left) / (length - 1);
    const y = value => box.bottom - (value - lo) * (box.bottom - box.top) / (hi - lo);
    for (let tick = 0; tick <= 4; tick += 1) {
      const py = box.top + tick * (box.bottom - box.top) / 4; const value = hi - tick * (hi - lo) / 4;
      content.appendChild(svgElement("line", { x1: box.left, x2: box.right, y1: py, y2: py, class: "grid-line" }));
      content.appendChild(svgElement("text", { x: 7, y: py + 4, class: "muted-label" }, options.percent ? `${Math.round(100 * value)}%` : format(value, 2)));
    }
    const areaPairs = new Map();
    validSeries.filter(item => item.area).forEach(item => {
      if (!areaPairs.has(item.area)) areaPairs.set(item.area, []); areaPairs.get(item.area).push(item);
    });
    for (const [areaClass, pair] of areaPairs) {
      if (pair.length !== 2) continue;
      const upper = pair[0].values; const lower = pair[1].values;
      const path = upper.map((value, index) => `${index ? "L" : "M"}${x(index).toFixed(2)},${y(value).toFixed(2)}`).join(" ")
        + " " + lower.slice().reverse().map((value, reverseIndex) => {
          const index = lower.length - 1 - reverseIndex; return `L${x(index).toFixed(2)},${y(value).toFixed(2)}`;
        }).join(" ") + " Z";
      content.appendChild(svgElement("path", { d: path, class: areaClass }));
    }
    validSeries.filter(item => item.className).forEach(item => {
      const path = item.values.map((value, index) => `${index ? "L" : "M"}${x(index).toFixed(2)},${y(value).toFixed(2)}`).join(" ");
      content.appendChild(svgElement("path", { d: path, class: item.className }));
    });
    content.appendChild(svgElement("rect", { x: box.left, y: box.top, width: box.right - box.left, height: box.bottom - box.top, class: "axis" }));
    content.appendChild(svgElement("text", { x: box.left, y: height - 12, class: "muted-label" }, "0"));
    content.appendChild(svgElement("text", { x: box.right - 48, y: height - 12, class: "muted-label" }, `${state.forecast.config.duration.toFixed(1)} s`));
  }

  function renderEnsembleResults() {
    const view = state.ensembleView; if (!view) return;
    const total = view.resolvedCount;
    optional("ensemble-results")?.removeAttribute("hidden"); optional("single-results")?.setAttribute("hidden", "");
    setText("ensemble-coverage", total && Number.isFinite(view.sampleCoverage) ? `${(100 * view.sampleCoverage).toFixed(1)}%` : "unresolved");
    setText("ensemble-coverage-interval", total
      ? "fraction of all resolved member-time samples inside the frozen first-order numerical tube"
      : "No resolved members; coverage unavailable");
    setText("persistent-exits", `${view.persistentExits} / ${total}`);
    const persistentSamples = state.ensembleDeclaration?.gates?.persistentExitSamples || 3;
    setText("persistence-gate-note", `outside for ≥${persistentSamples} consecutive sampled times; Δt = ${(state.forecast.config.duration / (state.forecast.times.length - 1)).toFixed(4)} s`);
    setText("survival-endpoint", total && Number.isFinite(view.wholeMemberSurvival) ? `${(100 * view.wholeMemberSurvival).toFixed(1)}%` : "unresolved");
    setText("ensemble-survival-interval", !total
      ? "No resolved members; interval unavailable"
      : view.intervalEligible
        ? `Whole-horizon no-exit member survival: Wilson-style 95% descriptive interval ${(100 * view.interval[0]).toFixed(1)}–${(100 * view.interval[1]).toFixed(1)}%; empirical, not certified probability`
        : `Interval withheld: bounded, ideal, or law-only design has no declared iid sampled component; finite count only. Whole-horizon no-exit member survival: ${view.intervalInterpretation}`);
    setText("ensemble-outliers", `${view.outliers} / ${total}`);
    const shownOutlierIds = view.representativeOutlierIds;
    const hiddenOutlierCount = Math.max(0, view.outlierIds.length - shownOutlierIds.length);
    setText("ensemble-outlier-members", view.outliers
      ? `Members: ${shownOutlierIds.join(", ")}${hiddenOutlierCount ? ` (+${hiddenOutlierCount} more)` : ""}. ${view.outlierRule}`
      : `No terminal outlier IDs. ${view.outlierRule}`);
    setText("projected-reconvergence", `${view.reconvergence} / ${total}`);
    setText("full-state-separation-at-reentry", Number.isFinite(view.fullStateAtReentryMedian)
      ? `${format(view.fullStateAtReentryMedian, 3)} scaled norm`
      : view.reconvergence ? "unresolved" : "no output re-entry");
    setText("full-state-separation-note", `${view.authoritativeFullStateAtReentry ? "authoritative core median" : "compatibility fallback median"}; not attraction or synchronization`);
    setText("ensemble-unresolved", String(view.unresolved));
    setText("ensemble-predicted-amplification", format(view.amplification.predicted, 3));
    setText("ensemble-observed-amplification", format(view.amplification.median, 3));
    setText("ensemble-percentiles", `${format(view.amplification.p05, 3)} / ${format(view.amplification.median, 3)} / ${format(view.amplification.p95, 3)}`);
    setText("ensemble-statistical-note", view.intervalEligible
      ? `Member-time tube coverage and whole-horizon no-exit survival over ${total} resolved seeded members. The Wilson-style interval applies only to whole-horizon survival; it is not certified probability or physical truth.`
      : `Member-time tube coverage and whole-horizon no-exit survival over ${total} resolved finite members. No probability interval is shown for this bounded, ideal, or law-only declaration.`);
    renderLinePlot("ensemble-survival-content", [
      { values: view.coverage, className: "coverage-series" },
      { values: view.survival, className: "survival-series" }
    ], { minimum: 0, maximum: 1, percent: true });
    const lower = view.predictedLow;
    const upper = view.predictedHigh;
    const all = lower.concat(upper, view.p05, view.p95); const lo = Math.min(...all); const hi = Math.max(...all);
    renderLinePlot("ensemble-spread-content", [
      { values: upper, area: "predicted-area" }, { values: lower, area: "predicted-area" },
      { values: view.predictedMedian, className: "predicted-median-series" },
      { values: view.p95, area: "observed-area" }, { values: view.p05, area: "observed-area" },
      { values: view.p50, className: "median-series" }
    ], { minimum: lo, maximum: hi });
    const memberTable = optional("ensemble-member-table"); const declarations = state.ensembleDeclaration?.members || [];
    if (memberTable) {
      memberTable.textContent = "";
      declarations.slice(0, 50).forEach((member, index) => {
        const outcome = view.members[index] || {}; const row = document.createElement("tr");
        const vector = value => Array.isArray(value) ? `[${value.map(item => format(Number(item), 3)).join(", ")}]` : "—";
        const baseOffset = outcome.draws?.angleOffset;
        const totalOffset = Array.isArray(baseOffset) && Array.isArray(member.structuredOffset)
          ? baseOffset.map((value, axis) => value + member.structuredOffset[axis]) : null;
        const audit = outcome.audit;
        const persistentExit = Number.isFinite(audit?.persistentExitTime)
          ? `${format(audit.persistentExitTime, 3)} s` : audit?.persistentExitIndex === null ? "none" : "unresolved";
        const endpoint = audit?.endpointClassification;
        const endpointLabel = endpoint
          ? endpoint.classification === "unclassified"
            ? "unclassified · no hard endpoint-radius event"
            : `${endpoint.classification} · Δ ${format(endpoint.distance, 3)} / cutoff ${format(endpoint.cutoff, 3)}`
          : Array.isArray(audit?.inside) && typeof audit.inside.at(-1) === "boolean"
            ? `${audit.inside.at(-1) ? "inside" : "outside"} tube at T · compatibility fallback`
            : "unresolved";
        if (view.outlierIds.includes(member.id)) row.dataset.outlier = "true";
        [member.id ?? index, format(Number(member.s), 3), vector(outcome.draws?.angleXi), vector(baseOffset),
          vector(member.structuredOffset), vector(totalOffset), Number.isFinite(audit?.coverage) ? `${(100 * audit.coverage).toFixed(1)}%` : "unresolved",
          persistentExit, endpointLabel, audit?.status || outcome.resolution?.status || outcome.resolution || "unresolved"]
          .forEach(value => { const cell = document.createElement("td"); cell.textContent = String(value); row.appendChild(cell); });
        memberTable.appendChild(row);
      });
      if (!declarations.length) memberTable.innerHTML = '<tr><td colspan="10">Member declarations were not returned; draws remain available only in the exported engine record.</td></tr>';
    }
  }

  function buildEnsembleLedger() {
    const view = state.ensembleView; if (!view) return;
    clearLedger(); const total = view.resolvedCount;
    const gates = state.ensemble?.summary?.gates || {};
    const response = state.forecast.responseRefinement;
    addLedger("Frozen before ensemble", state.forecast.method, `${total} seeded outcomes`, "forecast sealed before microscopic draws were revealed", "pass");
    addLedger("Member-time tube coverage", "first-order numerical tube", Number.isFinite(view.sampleCoverage) ? `${(100 * view.sampleCoverage).toFixed(1)}%` : "unresolved", "empirical numerical count; not certified probability", "neutral");
    addLedger("Whole-horizon no-exit survival", "no tube exit through T", Number.isFinite(view.wholeMemberSurvival) ? `${Math.round(view.wholeMemberSurvival * total)} / ${total}` : "unresolved", view.intervalEligible ? "Wilson interval displayed with survival" : "interval withheld by declaration", "neutral");
    addLedger("Persistent output exits", "3 consecutive outside samples", `${view.persistentExits} / ${total}`, view.persistentExits ? "forecast stress detected" : "none in finite sample", view.persistentExits ? "warn" : "pass");
    addLedger("Projected output reconvergence", "exit followed by later return", `${view.reconvergence} / ${total}`, "output-only numerical classification", "neutral");
    addLedger("Unresolved members", "complete finite trajectories", String(view.unresolved), view.unresolved ? "withheld from resolved counts" : "none", view.unresolved ? "warn" : "pass");
    addLedger("Baseline solver refinement", `< ${format(gates.maxRefinementDiscrepancy, 2)}`, format(gates.measuredRefinementDiscrepancy, 3), gates.refinementPassed === true ? "passed" : "unresolved", gates.refinementPassed === true ? "pass" : "warn");
    addLedger("Response h / h⁄2 refinement", `≤ ${(100 * gates.maxResponseRefinementDiscrepancy).toFixed(1)}% relative`, `${(100 * gates.measuredResponseRefinementDiscrepancy).toFixed(3)}%`, gates.responseRefinementPassed === true ? "passed" : "unresolved", gates.responseRefinementPassed === true ? "pass" : "warn");
    addLedger("Gain convergence", "weakest / strongest relative shift", `${(100 * response.weakestGainRelativeShift).toFixed(3)}% / ${(100 * response.strongestGainRelativeShift).toFixed(3)}%`, "numerical response diagnostic", gates.responseRefinementPassed === true ? "pass" : "warn");
    addLedger("Nuisance boundary", "initial-angle tube only", "parameter / clock / sensor declarations disclosed", "not propagated by this live tube", "neutral");
  }

  function clearLedger() {
    const ledger = optional("audit-ledger"); if (ledger) ledger.textContent = "";
  }
  function addLedger(label, forecast, observed, verdict, tone) {
    const ledger = optional("audit-ledger"); if (!ledger) return;
    const row = document.createElement("tr"); row.className = "ledger-row"; row.dataset.tone = tone;
    [label, forecast, observed, verdict].forEach(text => { const cell = document.createElement("td"); cell.textContent = text; row.appendChild(cell); });
    ledger.appendChild(row);
  }

  function buildLedger() {
    clearLedger();
    const outcome = state.outcome; const forecast = state.forecast;
    const gates = outcome.evidenceGates || {};
    const response = forecast.responseRefinement;
    addLedger("Frozen before outcome", forecast.method, outcome.method, "non-circular solver paths", "pass");
    addLedger("First-order tube", "≥ 95% held-out coverage", `${(100 * outcome.coverage).toFixed(1)}%`, outcome.coverage >= 0.95 ? "supported" : "falsified", outcome.coverage >= 0.95 ? "pass" : "fail");
    const relative = Math.abs(outcome.actualAmplification - outcome.predictedAmplification) / Math.max(1e-12, outcome.actualAmplification);
    addLedger("Directional amplification", format(outcome.predictedAmplification, 4), format(outcome.actualAmplification, 4), relative < 0.15 ? "within 15%" : "mismatch", relative < 0.15 ? "pass" : "warn");
    addLedger("Baseline solver refinement", `< ${format(gates.baselineRefinementTolerance, 2)}`, format(outcome.refinementDiscrepancy, 3), gates.baselineRefinementPassed === true ? "passed" : "unresolved", gates.baselineRefinementPassed === true ? "pass" : "warn");
    addLedger("Response h / h⁄2 refinement", `≤ ${(100 * gates.responseRefinementTolerance).toFixed(1)}% relative`, `${(100 * gates.responseRefinementMaximumRelativeDiscrepancy).toFixed(3)}%`, gates.responseRefinementPassed === true ? "passed" : "unresolved", gates.responseRefinementPassed === true ? "pass" : "warn");
    addLedger("Gain convergence", "weakest / strongest relative shift", `${(100 * response.weakestGainRelativeShift).toFixed(3)}% / ${(100 * response.strongestGainRelativeShift).toFixed(3)}%`, "numerical response diagnostic", gates.responseRefinementPassed === true ? "pass" : "warn");
    addLedger("Energy diagnostic", `scaled drift ≤ ${format(gates.energyTolerance, 2)}`, format(outcome.maxEnergyDrift, 3), gates.energyPassed === true ? "passed" : "unresolved", gates.energyPassed === true ? "pass" : "warn");
    addLedger("Endpoint noise test", `cutoff ${format(2 * forecast.config.noiseRadius, 3)}`, format(outcome.endpointDistance, 3), outcome.classification, "neutral");
    addLedger("Proof boundary", "live/refined are numerical", "same declared RHS", "not physical truth", "neutral");
  }

  function renderCertifiedEvidence() {
    const certificate = evidence.certificates.groupedSharedClock;
    const verified = evidence.generatedFromVerifiedSources === true
      && completeVerifiedProvenance(evidence.provenance);
    const verifiedCount = CERTIFIED_PROVENANCE_KEYS.filter(key => evidence.provenance?.[key]?.verified === true).length;
    const tier = optional("certified-tier");
    if (tier) tier.classList.toggle("is-certified", verified);
    if (verified) {
      setText("certified-floor", `> ${directedLowerDecimal(certificate.floorDecimal, 7)}`);
      setText("certified-exact", certificate.floorExact);
      setText("certificate-scope", "Fixed A+B five-output mixture · u,v physical parameters · one shared local clock nuisance · exact preparation");
      setText("two-row-floor", `> ${directedLowerDecimal(evidence.certificates.twoRowNoNuisance.floorDecimal, 7)}`);
      setText("certified-output-count", String(certificate.mixture.active_output_count));
      setText("certified-nuisance", "one shared local clock direction");
      setText("certificate-integrity", `${verifiedCount} / ${CERTIFIED_PROVENANCE_KEYS.length} source verifiers passed`);
    } else {
      setText("certified-floor", "Unavailable — provenance failed");
      setText("certified-exact", "Unavailable — provenance failed");
      setText("certificate-scope", "Certificate withheld because the complete source-verification conjunction did not pass.");
      setText("certified-output-count", "Unavailable");
      setText("certified-nuisance", "Unavailable");
      setText("certificate-integrity", `${verifiedCount} / ${CERTIFIED_PROVENANCE_KEYS.length} source verifiers passed · unverified`);
    }
    const list = optional("provenance-list");
    if (list) {
      list.textContent = "";
      Object.entries(evidence.provenance).forEach(([name, record]) => {
        const item = document.createElement("li");
        item.textContent = `${record.verified ? "verified" : "unverified"} · ${name.replaceAll("_", " ")} · ${record.sha256.slice(0, 10)}…`;
        item.dataset.verified = String(record.verified); list.appendChild(item);
      });
    }
    const resolution = evidence.persistence.resolution.find(row => row.name === "baseline");
    const shifts = evidence.persistence.shifts.filter(row => row.name !== "baseline");
    const cadence = evidence.persistence.cadence[evidence.persistence.cadence.length - 2];
    setText("persistence-summary", `At threshold 0.5: N=13 vs N=17 Jaccard ${resolution ? resolution.jaccard.toFixed(3) : "—"}; half-cell shifts ${shifts.map(row => row.jaccard.toFixed(3)).join(", ")}; late cadence ${cadence ? cadence.jaccard.toFixed(3) : "—"}. The small marked regions are not yet spatially converged.`);
    setTier("certified-tier", verified ? "proved" : "unresolved",
      verified ? "fixed A+B artifact chain replayed" : "one or more source artifacts unverified");
  }

  async function preparePreview(generation = ++state.previewGeneration) {
    if (state.running || generation !== state.previewGeneration) return;
    syncControlOutputs(); syncEnsembleOutputs();
    setText("run-status", "Preparing live OIG preview…");
    await nextPaint();
    if (state.running || generation !== state.previewGeneration) return;
    try {
      const forecast = core.forecastExperiment(readOptions());
      if (state.running || generation !== state.previewGeneration) return;
      state.forecast = forecast;
      state.outcome = null; state.ensemble = null; state.ensembleView = null; state.ensembleDeclaration = null;
      state.playhead = 0; state.playing = false;
      if (typeof core.buildEnsembleDeclaration === "function") {
        renderRealismLaws(core.buildEnsembleDeclaration(forecast, readEnsembleOptions()));
      }
      optional("ensemble-results")?.setAttribute("hidden", ""); optional("single-results")?.removeAttribute("hidden");
      setText("forecast-id", `preview-${core.checksum(state.forecast.config)}`);
      const seal = optional("forecast-seal"); if (seal) seal.dataset.state = "open";
      setText("forecast-seal-label", "Open — preview changes with controls");
      const size = readEnsembleOptions().size;
      setText("run-status", size === 1
        ? "Live preview ready. Press Run to freeze it before the held-out outcome."
        : `Live preview ready. Press Run to freeze it before generating ${size} hidden member draws.`);
      const runButton = optional("run-experiment");
      if (runButton) runButton.innerHTML = size === 1 ? '<span aria-hidden="true">▶</span> Freeze forecast &amp; run' : `<span aria-hidden="true">▶</span> Freeze &amp; run N = ${size}`;
      setTier("live-tier", "numerical", "unfrozen browser preview");
      setTier("refined-tier", "waiting", "no held-out outcome yet");
      updateForecastReadout(); drawAll();
    } catch (error) {
      setText("run-status", `Preview failed: ${error.message}`);
      setTier("live-tier", "unresolved", "invalid or failed numerical request");
    }
  }

  async function runExperiment() {
    if (state.running) return;
    clearTimeout(state.previewTimer); state.previewTimer = null; state.previewGeneration += 1;
    const runId = `experiment:${++state.nextRequestToken}`; state.activeRunId = runId;
    state.running = true; state.playing = false; state.ensemble = null; state.ensembleView = null; state.ensembleDeclaration = null;
    $("run-experiment").disabled = true;
    [...Object.values(controls), ...Object.values(ensembleControls).filter(Boolean)].forEach(control => { control.disabled = true; });
    if (optional("reset-experiment")) optional("reset-experiment").disabled = true;
    setText("run-status", "Computing and freezing the OIG forecast…");
    setTier("live-tier", "computing", "forecast not yet frozen");
    setTier("refined-tier", "waiting", "outcome hidden");
    clearLedger(); await nextPaint();
    let disclosureDeclaration = null;
    try {
      const options = readOptions(); const ensembleOptions = readEnsembleOptions();
      state.forecast = core.forecastExperiment(options);
      if (typeof core.buildEnsembleDeclaration === "function") {
        disclosureDeclaration = core.buildEnsembleDeclaration(state.forecast, ensembleOptions);
        renderRealismLaws(disclosureDeclaration);
      }
      const forecastId = `OIG-${core.checksum({ options, ensembleDeclaration: ensembleOptions, gram: state.forecast.information.gram, recommendation: state.forecast.recommendation })}`;
      setText("forecast-id", forecastId);
      const seal = optional("forecast-seal"); if (seal) seal.dataset.state = "sealed";
      setText("forecast-seal-label", `Sealed · ${forecastId}`);
      setTier("live-tier", "frozen", "first-order forecast fixed before outcome");
      updateForecastReadout(); drawAll();
      if (ensembleOptions.size === 1) {
        optional("ensemble-results")?.setAttribute("hidden", ""); optional("single-results")?.removeAttribute("hidden");
        setText("run-status", "Forecast frozen. Running the held-out adaptive outcome…");
        await nextPaint();
        state.outcome = core.runIndependentOutcome(state.forecast);
        if (runId !== state.activeRunId) return;
        const refinedPassed = state.outcome.evidenceGates?.refinedEvidencePassed === true;
        setTier("refined-tier", refinedPassed ? "passed" : "unresolved",
          refinedPassed
            ? "baseline, response-refinement, and energy gates passed"
            : "baseline, response-refinement, and/or energy gate failed");
        setText("run-status", refinedPassed
          ? "Outcome complete. Comparing it with the frozen forecast."
          : "Outcome complete, but refinement gates failed; evidence remains Live/unresolved.");
        updateOutcomeReadout(); buildLedger();
        setText("animation-status", "Detailed outcome");
      } else {
        if (typeof core.buildEnsembleDeclaration !== "function" || typeof core.runEnsemble !== "function") {
          throw new Error("ensemble engine unavailable in this build; set N = 1 to use the complete single-outcome path");
        }
        setText("run-status", "Forecast frozen. Canonical member draws are now generated and remain hidden while the finite ensemble runs…");
        await nextPaint();
        state.ensembleDeclaration = disclosureDeclaration
          || core.buildEnsembleDeclaration(state.forecast, ensembleOptions);
        renderRealismLaws(state.ensembleDeclaration);
        const result = await invokeEnsemble(state.forecast, state.ensembleDeclaration, runId, progress => {
          if (runId !== state.activeRunId) return;
          const fraction = typeof progress === "number" ? progress : Number(progress?.fraction ?? progress?.completed / Math.max(1, progress?.total));
          setText("run-status", Number.isFinite(fraction)
            ? `Running seeded finite ensemble… ${Math.round(100 * clamp(fraction, 0, 1))}%`
            : "Running seeded finite ensemble…");
        });
        if (runId !== state.activeRunId) return;
        state.ensemble = result; state.ensembleView = computeEnsembleView(result); state.outcome = null;
        if (ensembleOptions.structured.law !== "off" && !state.ensembleView.authoritativeSummaryUsed) {
          throw new Error("structured-law outcome returned without its member-specific authoritative summary; coverage withheld");
        }
        const refinementGates = result.summary?.gates;
        const refinementPassed = typeof refinementGates?.refinedEvidencePassed === "boolean"
          ? refinementGates.refinedEvidencePassed
          : refinementGates?.refinementPassed === true && state.forecast.responseRefinement?.passed === true;
        const allResolved = state.ensembleView.resolvedCount === state.ensembleDeclaration.size
          && state.ensembleView.unresolved === 0 && refinementPassed;
        setTier("refined-tier", allResolved ? "passed" : "unresolved",
          allResolved
            ? `${state.ensembleView.resolvedCount} independent adaptive outcomes complete`
            : `${state.ensembleView.resolvedCount} resolved; ${state.ensembleView.unresolved} unresolved; refinement ${refinementPassed ? "passed" : "failed"}`);
        setText("run-status", allResolved
          ? `Finite ensemble complete. ${state.ensembleView.resolvedCount} resolved; none unresolved.`
          : `Finite ensemble remains unresolved. ${state.ensembleView.resolvedCount} resolved; ${state.ensembleView.unresolved} unresolved; refinement ${refinementPassed ? "passed" : "failed"}.`);
        renderEnsembleResults(); buildEnsembleLedger();
      }
      state.playhead = 0; state.playing = !matchMedia("(prefers-reduced-motion: reduce)").matches;
      for (const id of ["play-pause", "replay-animation", "animation-scrubber", "export-ledger"]) {
        const node = optional(id); if (node) node.disabled = false;
      }
      $("play-pause").textContent = state.playing ? "Pause" : "Play";
      drawAll();
      if (state.playing) startAnimation();
    } catch (error) {
      if (runId !== state.activeRunId) return;
      setText("run-status", error?.name === "AbortError" ? "Experiment cancelled; no partial ensemble was promoted." : `Experiment unresolved: ${error.message}`);
      setTier("refined-tier", "unresolved", "numerical comparison did not complete");
    } finally {
      if (runId === state.activeRunId) {
        state.running = false; $("run-experiment").disabled = false;
        [...Object.values(controls), ...Object.values(ensembleControls).filter(Boolean)].forEach(control => { control.disabled = false; });
        if (optional("reset-experiment")) optional("reset-experiment").disabled = false;
        syncEnsembleOutputs(disclosureDeclaration);
      }
    }
  }

  function startAnimation() {
    cancelAnimationFrame(state.animation);
    state.lastFrame = performance.now();
    function frame(now) {
      if (!state.playing || !state.forecast) return;
      const elapsed = Math.min(0.08, (now - state.lastFrame) / 1000); state.lastFrame = now;
      const samplesPerSecond = (state.forecast.times.length - 1) / state.forecast.config.duration;
      const speed = optional("animation-speed") ? Number(optional("animation-speed").value) : 1;
      state.playhead += elapsed * samplesPerSecond * speed;
      if (state.playhead >= state.forecast.times.length - 1) { state.playhead = state.forecast.times.length - 1; state.playing = false; $("play-pause").textContent = "Replay"; }
      drawDynamics(); drawSensorChart();
      if (state.playing) state.animation = requestAnimationFrame(frame);
    }
    state.animation = requestAnimationFrame(frame);
  }

  function togglePlayback() {
    if (!state.forecast) return;
    if (state.playhead >= state.forecast.times.length - 1) state.playhead = 0;
    state.playing = !state.playing; $("play-pause").textContent = state.playing ? "Pause" : "Play";
    if (state.playing) startAnimation(); else cancelAnimationFrame(state.animation);
  }

  function drawAll() { drawDynamics(); drawSensorChart(); drawTorus(); }
  function schedulePreview() {
    syncControlOutputs(); drawTorus();
    clearTimeout(state.previewTimer);
    const generation = ++state.previewGeneration;
    state.previewTimer = setTimeout(() => {
      state.previewTimer = null;
      preparePreview(generation);
    }, 180);
  }

  function setControls(values) {
    Object.entries(values).forEach(([key, value]) => { if (controls[key]) controls[key].value = String(value); });
    schedulePreview();
  }

  function parseGridInput(id, minimum, maximum, integers) {
    const raw = optional(id)?.value || "";
    const tokens = raw.split(",").map(value => value.trim());
    const numericToken = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i;
    if (!tokens.length || tokens.some(token => !token || !numericToken.test(token))) {
      throw new Error(`${id.replaceAll("-", " ")} contains an empty or invalid numeric token`);
    }
    const parsed = tokens.map(Number);
    if (parsed.some(value => !Number.isFinite(value))) {
      throw new Error(`${id.replaceAll("-", " ")} contains a nonfinite number`);
    }
    const values = [...new Set(parsed)];
    if (values.some(value => value < minimum || value > maximum || integers && !Number.isInteger(value))) {
      throw new Error(`${id.replaceAll("-", " ")} must stay inside ${minimum}…${maximum}${integers ? " using integers" : ""}`);
    }
    return values.sort((a, b) => a - b);
  }

  function readLaboratoryDesign() {
    const sizes = parseGridInput("laboratory-n-grid", 50, 1000, true);
    const horizons = parseGridInput("laboratory-t-grid", 1, 30, false);
    const amplitudeMultipliers = parseGridInput("laboratory-amplitudes", 0, 2, false);
    const amplitudes = amplitudeMultipliers.map(value => value * number(controls.preparation));
    const repeats = Math.round(number(optional("laboratory-repeats")));
    const laws = [...root.querySelectorAll("[data-laboratory-law]:checked")].map(node => node.value);
    if (!laws.length) throw new Error("select at least one structured law");
    const jobs = sizes.length * horizons.length * amplitudes.length * laws.length * repeats;
    const observationStep = 1 / 40;
    const samplesAcrossHorizons = horizons.reduce((sum, horizon) => sum + Math.round(horizon / observationStep) + 1, 0);
    const memberSamples = sizes.reduce((sum, size) => sum + size, 0) * samplesAcrossHorizons * amplitudes.length * laws.length * repeats;
    return { sizes, horizons, amplitudes, amplitudeMultipliers, laws, repeats, jobs, observationStep, memberSamples };
  }

  function syncLaboratoryDesign() {
    setText("laboratory-repeats-value", optional("laboratory-repeats")?.value || "—");
    try {
      const design = readLaboratoryDesign();
      setText("laboratory-job-count", `${design.jobs.toLocaleString()} jobs · ${design.memberSamples.toLocaleString()} member-samples`);
    } catch (error) { setText("laboratory-job-count", `Design unresolved: ${error.message}`); }
  }

  function laboratoryMetric(summary, names) {
    for (const path of names) {
      let value = summary;
      for (const key of path.split(".")) value = value?.[key];
      if (Number.isFinite(value)) return value;
    }
    return NaN;
  }

  function laboratoryRows(result) {
    const rows = result?.jobs || result?.runs || result?.results || result?.cells || [];
    return Array.isArray(rows) ? rows : [];
  }

  function normalizeLaboratoryRow(row) {
    const config = row.config || row.spec || row.declaration?.options || row;
    const summary = row.aggregate || row.summary || row.result?.summary || row.result || {};
    const aggregateValue = value => Number.isFinite(value?.p50) ? value.p50 : Number.isFinite(value?.mean) ? value.mean : NaN;
    const coverageCurve = summary.timewise?.coverage; const survivalCurve = summary.timewise?.survival;
    const memberTimeCoverage = Number.isFinite(aggregateValue(summary.sampleCoverage))
      ? aggregateValue(summary.sampleCoverage)
      : Array.isArray(coverageCurve) && Number.isFinite(coverageCurve.at(-1))
        ? coverageCurve.at(-1) : laboratoryMetric(summary, ["coverage.sampleFraction", "coverage.terminal", "terminalCoverage", "coverage"]);
    const wholeHorizonSurvival = Number.isFinite(aggregateValue(summary.wholeMemberCoverage))
      ? aggregateValue(summary.wholeMemberCoverage)
      : Array.isArray(survivalCurve) && Number.isFinite(survivalCurve.at(-1))
        ? survivalCurve.at(-1) : laboratoryMetric(summary, ["coverage.wholeMemberFraction", "survival.terminal", "terminalSurvival", "survival"]);
    const unresolvedFraction = Number.isFinite(summary.unresolvedMemberFraction?.max)
      ? summary.unresolvedMemberFraction.max : aggregateValue(summary.unresolvedMemberFraction);
    return {
      size: Number(config.size ?? config.n ?? config.N),
      horizon: Number(config.horizon ?? config.duration ?? config.T),
      law: config.law ?? config.structured?.law ?? "—",
      amplitude: Number(config.amplitude ?? config.alpha ?? config.structured?.alpha),
      repeats: Array.isArray(row.runs) ? row.runs.length : Number(config.repeats ?? config.seed),
      coverage: memberTimeCoverage,
      survival: wholeHorizonSurvival,
      status: row.status || (row.error || Number.isFinite(unresolvedFraction) && unresolvedFraction > 0 ? "unresolved" : "resolved")
    };
  }

  function renderLaboratoryChart(rows) {
    const content = optional("laboratory-chart-content"); if (!content) return;
    content.textContent = "";
    const normalized = rows.map(normalizeLaboratoryRow);
    const sizes = [...new Set(normalized.map(row => row.size).filter(Number.isFinite))].sort((a, b) => a - b);
    const horizons = [...new Set(normalized.map(row => row.horizon).filter(Number.isFinite))].sort((a, b) => a - b);
    if (!sizes.length || !horizons.length) {
      content.appendChild(svgElement("text", { x: 36, y: 70, class: "muted-label" }, "No resolved N-by-T cells were returned.")); return;
    }
    const width = 900; const height = 460; const box = { left: 72, right: 870, top: 30, bottom: 390 };
    const cellWidth = (box.right - box.left) / sizes.length; const cellHeight = (box.bottom - box.top) / horizons.length;
    horizons.forEach((horizon, rowIndex) => {
      sizes.forEach((size, columnIndex) => {
        const values = normalized.filter(row => row.size === size && row.horizon === horizon && Number.isFinite(row.coverage)).map(row => row.coverage);
        const average = values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : NaN;
        const x = box.left + columnIndex * cellWidth; const y = box.top + rowIndex * cellHeight;
        content.appendChild(svgElement("rect", { x, y, width: cellWidth - 2, height: cellHeight - 2, rx: 4, fill: Number.isFinite(average) ? `hsl(${15 + 165 * average} 58% ${54 - 10 * average}%)` : css("--surface-2"), class: "laboratory-cell" }));
        content.appendChild(svgElement("text", { x: x + cellWidth / 2, y: y + cellHeight / 2 + 4, "text-anchor": "middle" }, Number.isFinite(average) ? `${Math.round(100 * average)}%` : "—"));
      });
      content.appendChild(svgElement("text", { x: box.left - 12, y: box.top + (rowIndex + 0.5) * cellHeight + 4, "text-anchor": "end", class: "muted-label" }, `T ${horizon}`));
    });
    sizes.forEach((size, index) => content.appendChild(svgElement("text", { x: box.left + (index + 0.5) * cellWidth, y: box.bottom + 24, "text-anchor": "middle", class: "muted-label" }, `N ${size}`)));
    content.appendChild(svgElement("text", { x: box.left, y: height - 14, class: "muted-label" }, "Mean of cell-median member-time coverage across displayed law / α / seed cells"));
  }

  function renderLaboratoryResult(result) {
    const rows = laboratoryRows(result); const body = optional("laboratory-table-body");
    if (body) {
      body.textContent = "";
      rows.slice(0, 300).forEach(row => {
        const item = normalizeLaboratoryRow(row); const tr = document.createElement("tr");
        [item.size, item.horizon, item.law, format(item.amplitude, 4), item.repeats,
          Number.isFinite(item.coverage) ? `${(100 * item.coverage).toFixed(1)}%` : "—",
          Number.isFinite(item.survival) ? `${(100 * item.survival).toFixed(1)}%` : "—", item.status]
          .forEach(value => { const td = document.createElement("td"); td.textContent = String(value); tr.appendChild(td); });
        body.appendChild(tr);
      });
      if (!rows.length) body.innerHTML = '<tr id="laboratory-empty-row"><td colspan="8">The engine returned no completed cell aggregates.</td></tr>';
    }
    renderLaboratoryChart(rows);
    setText("laboratory-figure-note", `${rows.length} completed cell aggregates. Percentages are empirical numerical counts, not certified probabilities.`);
  }

  async function runLaboratory() {
    if (state.laboratoryRunId && state.workerRequests.has(state.laboratoryRunId)) return;
    let design;
    try { design = readLaboratoryDesign(); }
    catch (error) { setText("laboratory-status", `Design unresolved: ${error.message}`); return; }
    if (design.jobs > 512 || design.memberSamples > 100000000) {
      setText("laboratory-status", "Design withheld: reduce below 512 jobs and 100,000,000 member-samples per launch."); return;
    }
    if ((design.jobs > 64 || design.memberSamples > 5000000)
      && !globalThis.confirm(`Run ${design.jobs.toLocaleString()} jobs comprising about ${design.memberSamples.toLocaleString()} member-samples? This may take a long time.`)) return;
    const runId = `laboratory:${++state.nextRequestToken}`; state.laboratoryRunId = runId; state.laboratoryCancelled = false;
    optional("run-laboratory").disabled = true; optional("cancel-laboratory").disabled = false; optional("export-laboratory").disabled = true;
    const progress = optional("laboratory-progress"); if (progress) progress.value = 0;
    setText("laboratory-progress-value", "0%"); setText("laboratory-status", "Preparing a frozen base declaration…"); await nextPaint();
    try {
      const ensembleTemplate = readEnsembleOptions(design.sizes[0]);
      const baseOptions = Object.assign({}, readOptions(), {
        preparationRadius: ensembleTemplate.uncertainty.scale,
        noiseRadius: ensembleTemplate.realism.sensor.scale
      });
      const baseForecast = core.forecastExperiment(baseOptions);
      const spec = {
        forecast: baseForecast,
        ensembleOptions: ensembleTemplate,
        sizes: design.sizes,
        horizons: design.horizons,
        repeats: design.repeats,
        baseSeed: ensembleTemplate.seed,
        observationStep: design.observationStep,
        retainTrajectories: false,
        laws: design.laws,
        amplitudes: design.amplitudes
      };
      const result = await invokeLaboratory(spec, runId, update => {
        if (runId !== state.laboratoryRunId) return;
        const fraction = typeof update === "number" ? update : Number(update?.fraction ?? update?.completed / Math.max(1, update?.total));
        if (Number.isFinite(fraction)) {
          const value = clamp(fraction, 0, 1); if (progress) progress.value = value;
          setText("laboratory-progress-value", `${Math.round(100 * value)}%`);
        }
        setText("laboratory-status", update?.label || "Running queued N-by-T study…");
      });
      if (runId !== state.laboratoryRunId) return;
      state.laboratoryResult = result; renderLaboratoryResult(result);
      if (progress) progress.value = 1; setText("laboratory-progress-value", "100%");
      setText("laboratory-status", "Study complete. Inspect or export the finite numerical record.");
      optional("export-laboratory").disabled = false;
    } catch (error) {
      if (runId !== state.laboratoryRunId) return;
      setText("laboratory-status", error?.name === "AbortError" ? "Study cancelled. Partial work was not promoted." : `Study unresolved: ${error.message}`);
    } finally {
      if (runId === state.laboratoryRunId) {
        optional("run-laboratory").disabled = false; optional("cancel-laboratory").disabled = true;
      }
    }
  }

  function installDrag(canvas, camera) {
    let active = false; let x = 0; let y = 0;
    canvas.addEventListener("pointerdown", event => { active = true; x = event.clientX; y = event.clientY; canvas.setPointerCapture(event.pointerId); });
    canvas.addEventListener("pointermove", event => {
      if (!active) return;
      camera.yaw += (event.clientX - x) * 0.008; camera.pitch = Math.max(-1.1, Math.min(1.1, camera.pitch + (event.clientY - y) * 0.006));
      x = event.clientX; y = event.clientY; drawAll();
    });
    canvas.addEventListener("pointerup", () => { active = false; });
    canvas.addEventListener("pointercancel", () => { active = false; });
  }

  controls.sensor.innerHTML = "";
  core.SENSORS.forEach(sensor => { const option = document.createElement("option"); option.value = sensor.id; option.textContent = sensor.label; controls.sensor.appendChild(option); });
  controls.sensor.value = "tip-x";
  Object.values(controls).forEach(control => control.addEventListener(control.tagName === "SELECT" ? "change" : "input", schedulePreview));
  Object.values(ensembleControls).filter(Boolean).forEach(control => control.addEventListener(control.tagName === "SELECT" ? "change" : "input", () => {
    syncEnsembleOutputs(); schedulePreview();
  }));
  $("run-experiment").addEventListener("click", runExperiment);
  $("play-pause").addEventListener("click", togglePlayback);
  optional("reset-experiment")?.addEventListener("click", () => {
    setControls({ theta1: 0.8, theta2: -0.35, omega1: 0, omega2: 0, duration: 4, preparation: 0.01, noise: 0.015 });
    const defaults = { size: 1, realism: 20, mode: "bounded", seed: 1729, law: "linear", amplitude: 0.25, direction: "weakest", customAngle: 0 };
    Object.entries(defaults).forEach(([key, value]) => { if (ensembleControls[key]) ensembleControls[key].value = String(value); });
    syncEnsembleOutputs(); schedulePreview();
  });
  optional("apply-recommendation")?.addEventListener("click", () => {
    if (!state.forecast) return;
    controls.sensor.value = state.forecast.recommendation.sensor;
    setText("run-status", `Applied ${state.forecast.recommendation.sensorLabel}. The recommended time remains ${state.forecast.recommendation.time.toFixed(2)} s inside the plotted schedule.`);
    schedulePreview();
  });
  optional("replay-animation")?.addEventListener("click", () => {
    if (!state.forecast) return; state.playhead = 0; state.playing = true; $("play-pause").textContent = "Pause"; startAnimation();
  });
  optional("animation-scrubber")?.addEventListener("input", event => {
    if (!state.forecast) return; state.playing = false; $("play-pause").textContent = "Play";
    state.playhead = Number(event.target.value) * (state.forecast.times.length - 1) / 1000; drawDynamics(); drawSensorChart();
  });
  optional("atlas-field-select")?.addEventListener("change", drawTorus);
  optional("export-ledger")?.addEventListener("click", () => {
    if (!state.forecast || !state.outcome && !state.ensemble) return;
    const record = {
      schemaVersion: "oig-wind-tunnel-ledger-v2",
      forecastId: optional("forecast-id")?.textContent,
      forecastFrozenBeforeOutcome: true,
      declaredConfig: state.forecast.config,
      forecast: {
        config: state.forecast.config,
        times: state.forecast.times,
        baseline: state.forecast.baseline,
        baselineSensor: state.forecast.baselineSensor,
        gradients: state.forecast.gradients,
        tubeRadius: state.forecast.tubeRadius,
        information: state.forecast.information,
        responseRefinement: state.forecast.responseRefinement,
        recommendation: state.forecast.recommendation,
        method: state.forecast.method
      },
      outcome: state.outcome ? {
        actual: state.outcome.actual,
        actualSensor: state.outcome.actualSensor,
        independentBaseline: state.outcome.independentBaseline,
        refinedBaselineSensor: state.outcome.refinedBaselineSensor,
        direction: state.outcome.direction, coverage: state.outcome.coverage,
        predictedAmplification: state.outcome.predictedAmplification, actualAmplification: state.outcome.actualAmplification,
        refinementDiscrepancy: state.outcome.refinementDiscrepancy, maxEnergyDrift: state.outcome.maxEnergyDrift,
        evidenceGates: state.outcome.evidenceGates,
        endpointDistance: state.outcome.endpointDistance, classification: state.outcome.classification, method: state.outcome.method
      } : null,
      ensemble: state.ensemble ? {
        declaration: state.ensembleDeclaration,
        result: state.ensemble,
        interfaceCrossCheck: state.ensembleView,
        empiricalNumericalOnly: true,
        certifiedProbability: false
      } : null,
      certifiedArtifactAppliedToThisSliderTrial: false
    };
    const blob = new Blob([`${JSON.stringify(record, null, 2)}\n`], { type: "application/json" });
    const link = document.createElement("a"); link.href = URL.createObjectURL(blob); link.download = `${record.forecastId || "oig-wind-tunnel"}.json`; link.click(); URL.revokeObjectURL(link.href);
  });
  for (const id of ["laboratory-n-grid", "laboratory-t-grid", "laboratory-repeats", "laboratory-amplitudes"]) {
    optional(id)?.addEventListener(id === "laboratory-repeats" ? "input" : "change", syncLaboratoryDesign);
  }
  root.querySelectorAll("[data-laboratory-law]").forEach(control => control.addEventListener("change", syncLaboratoryDesign));
  optional("run-laboratory")?.addEventListener("click", runLaboratory);
  optional("cancel-laboratory")?.addEventListener("click", () => {
    if (!state.laboratoryRunId) return;
    state.laboratoryCancelled = true; cancelWorkerRequest(state.laboratoryRunId);
    setText("laboratory-status", "Cancelling and discarding partial work…");
  });
  optional("export-laboratory")?.addEventListener("click", () => {
    if (!state.laboratoryResult) return;
    const blob = new Blob([`${JSON.stringify(state.laboratoryResult, null, 2)}\n`], { type: "application/json" });
    const link = document.createElement("a"); link.href = URL.createObjectURL(blob); link.download = "oig-background-laboratory.json"; link.click(); URL.revokeObjectURL(link.href);
  });
  optional("laboratory-quick-preset")?.addEventListener("click", () => {
    optional("laboratory-n-grid").value = "50, 200"; optional("laboratory-t-grid").value = "4, 12";
    optional("laboratory-repeats").value = "2"; optional("laboratory-amplitudes").value = "0, 0.25";
    root.querySelectorAll("[data-laboratory-law]").forEach(node => { node.checked = ["off", "linear"].includes(node.value); }); syncLaboratoryDesign();
  });
  optional("laboratory-research-preset")?.addEventListener("click", () => {
    optional("laboratory-n-grid").value = "50, 200, 1000"; optional("laboratory-t-grid").value = "4, 12, 30";
    optional("laboratory-repeats").value = "3"; optional("laboratory-amplitudes").value = "0, 0.25, 0.75";
    root.querySelectorAll("[data-laboratory-law]").forEach(node => { node.checked = ["off", "linear"].includes(node.value); }); syncLaboratoryDesign();
    setText("laboratory-status", "Research-scale preset loaded. Workload confirmation is required before launch.");
  });
  root.querySelectorAll("[data-preset]").forEach(button => button.addEventListener("click", () => {
    const presets = {
      regular: { theta1: 0.35, theta2: 0.18, omega1: 0, omega2: 0 },
      contrast: { theta1: 0.8, theta2: -0.35, omega1: 0, omega2: 0 },
      energetic: { theta1: 1.95, theta2: -1.15, omega1: 0.35, omega2: -0.2 },
      "launch-a": { theta1: 0.8, theta2: -0.35, omega1: 0, omega2: 0 },
      "launch-b": { theta1: -0.6, theta2: 0.9, omega1: 0, omega2: 0 }
    };
    setControls(presets[button.dataset.preset] || presets.contrast);
  }));
  canvases.torus.addEventListener("click", event => {
    if (!state.torusHitTargets.length) return;
    const box = canvases.torus.getBoundingClientRect(); const ratioX = box.width / Math.max(1, box.width); const ratioY = box.height / Math.max(1, box.height);
    const x = (event.clientX - box.left) / ratioX; const y = (event.clientY - box.top) / ratioY;
    const hit = state.torusHitTargets.reduce((best, item) => {
      const distance = Math.hypot(item.x - x, item.y - y); return !best || distance < best.distance ? { ...item, distance } : best;
    }, null);
    if (hit && hit.distance < 34) {
      controls.theta1.value = evidence.variationalAtlas.angles1[hit.row]; controls.theta2.value = evidence.variationalAtlas.angles2[hit.column]; schedulePreview();
    }
  });
  installDrag(canvases.dynamics, state.camera); installDrag(canvases.torus, state.torusCamera);
  [canvases.dynamics, canvases.torus].forEach((canvas, index) => canvas.addEventListener("wheel", event => {
    event.preventDefault(); const camera = index === 0 ? state.camera : state.torusCamera;
    camera.zoom = Math.max(0.7, Math.min(1.6, camera.zoom * Math.exp(-event.deltaY * 0.001))); drawAll();
  }, { passive: false }));
  const observer = new ResizeObserver(drawAll); Object.values(canvases).forEach(canvas => observer.observe(canvas));
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", drawAll);
  renderCertifiedEvidence(); syncControlOutputs(); syncEnsembleOutputs(); syncLaboratoryDesign(); preparePreview();
})();
