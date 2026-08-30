(function () {
  "use strict";

  const Core = window.GlobalGeometryCore;
  const SVG_NS = "http://www.w3.org/2000/svg";
  const $ = id => document.getElementById(id);

  if (!Core) {
    $("configuration-status").textContent = "The Global Geometry core did not load.";
    $("configuration-status").classList.add("is-error");
    return;
  }

  const elements = {
    preset: $("preset-select"),
    seed: $("seed-input"),
    rate: $("rate-input"),
    rateOutput: $("rate-output"),
    disorder: $("disorder-input"),
    disorderOutput: $("disorder-output"),
    scale: $("scale-input"),
    scaleOutput: $("scale-output"),
    run: $("run-button"),
    step: $("step-button"),
    reset: $("reset-button"),
    event: $("event-button"),
    mode: $("mode-badge"),
    question: $("scenario-question"),
    boundary: $("scenario-boundary"),
    topologyValue: $("topology-value"),
    topologyDetail: $("topology-detail"),
    topologyEvidence: $("topology-evidence"),
    curvatureValue: $("curvature-value"),
    curvatureDetail: $("curvature-detail"),
    curvatureEvidence: $("curvature-evidence"),
    dimensionValue: $("dimension-value"),
    dimensionDetail: $("dimension-detail"),
    responseValue: $("response-value"),
    responseDetail: $("response-detail"),
    worldTitle: $("world-title"),
    worldSubtitle: $("world-subtitle"),
    worldKeyLow: $("world-key-low"),
    worldKeyMid: $("world-key-mid"),
    worldKeyHigh: $("world-key-high"),
    world: $("world-view"),
    faceLayer: $("face-layer"),
    edgeLayer: $("edge-layer"),
    nodeLayer: $("node-layer"),
    tooltip: $("world-tooltip"),
    selection: $("selection-detail"),
    profile: $("profile-chart"),
    profileDetail: $("profile-detail"),
    processLocal: $("process-local"),
    processCompose: $("process-compose"),
    processGlobal: $("process-global"),
    compareSeed: $("comparison-seed"),
    compare: $("compare-button"),
    comparisonTopology: $("comparison-topology"),
    comparisonProfile: $("comparison-profile"),
    comparisonSpectrum: $("comparison-spectrum"),
    comparisonStatus: $("comparison-status"),
    config: $("configuration-json"),
    configStatus: $("configuration-status"),
    applyConfig: $("apply-config-button"),
    restoreConfig: $("restore-config-button"),
    exportRun: $("export-button"),
    recordSchema: $("record-schema"),
    recordTime: $("record-time"),
    recordSize: $("record-size"),
    recordMethod: $("record-method"),
    recordReplay: $("record-replay"),
    applicationCards: $("application-cards")
  };

  const applicationFallbacks = {
    theory: {
      title: "Discrete geometry",
      mechanism: "Compatible local lengths, angle defects, and neighbour operators",
      observable: "Homology, Gauss–Bonnet closure, spectrum, and finite-scale profiles",
      boundary: "A finite mathematical model; continuum limits require separate hypotheses and proof."
    },
    materials: {
      title: "Programmable materials",
      mechanism: "Local metric growth and curvature-error feedback",
      observable: "Angle defect, target error, topology, wave/diffusion scales",
      boundary: "An intrinsic sheet model, not a calibrated constitutive material."
    },
    morphogenesis: {
      title: "Morphogenesis",
      mechanism: "Neighbour diffusion coupled to local growth",
      observable: "Scalar pattern scale, connectivity, and intrinsic geometric response",
      boundary: "A mathematical tissue analogy, not identification of a biological mechanism."
    },
    networks: {
      title: "Networks",
      mechanism: "Local diffusion, capacity adaptation, and disclosed damage",
      observable: "Components, cycles, spectral gap, and transport dimension",
      boundary: "A synthetic routing model; curvature does not universally predict fragility."
    },
    learning: {
      title: "Machine learning",
      mechanism: "A local similarity graph sampled from latent data",
      observable: "Finite spectral and volume-growth dimension profiles",
      boundary: "Sampling and graph construction can manufacture apparent geometry."
    },
    swarms: {
      title: "Swarms and robotics",
      mechanism: "Neighbour-only averaging on a fixed proximity graph",
      observable: "Componentwise consensus, connectivity, and Laplacian nullity",
      boundary: "An information-flow toy—not a safe or complete robot controller."
    },
    physics: {
      title: "Emergent-spacetime toy",
      mechanism: "Local adjacency and diffusion on a relational graph",
      observable: "Scale-dependent spectral dimension and correlations",
      boundary: "An undirected graph-geometry toy, not a Lorentzian causal structure or evidence for quantum gravity."
    }
  };

  function canonicalApplicationKey(value) {
    const key = String(value || "theory").toLowerCase();
    const aliases = {
      "programmable-materials": "materials",
      "programmable-material": "materials",
      metamaterials: "materials",
      "machine-learning": "learning",
      "distributed-robotics": "swarms",
      robotics: "swarms"
    };
    return aliases[key] || key;
  }

  let presetEntries = [];
  let currentPreset = null;
  let currentConfig = null;
  let state = null;
  let analysis = null;
  let selectedNodeId = null;
  let running = false;
  let lastFrame = 0;
  let comparisonStep = null;
  let comparisonRecord = null;
  const visibleSeries = { volume: true, spectral: true, walk: true };

  function deepClone(value) {
    if (Core.cloneConfig && value && !value.nodes) return Core.cloneConfig(value);
    if (typeof structuredClone === "function") return structuredClone(value);
    return JSON.parse(JSON.stringify(value));
  }

  function finite(value, fallback = 0) {
    return Number.isFinite(value) ? value : fallback;
  }

  function formatNumber(value, digits = 3) {
    if (!Number.isFinite(value)) return "—";
    if (value !== 0 && Math.abs(value) < 1e-4) return value.toExponential(2);
    if (Math.abs(value) >= 1e4) return value.toExponential(2);
    const fixed = value.toFixed(digits);
    return fixed.includes(".") ? fixed.replace(/0+$/, "").replace(/\.$/, "") : fixed;
  }

  function stableStringify(value) {
    if (Array.isArray(value)) return `[${value.map(stableStringify).join(",")}]`;
    if (value && typeof value === "object") {
      return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(",")}}`;
    }
    return JSON.stringify(value);
  }

  function shortHash(value) {
    const text = stableStringify(value);
    let hash = 2166136261;
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(16).padStart(8, "0");
  }

  function normalizePresetEntries() {
    const listed = typeof Core.listPresets === "function" ? Core.listPresets() : null;
    if (Array.isArray(listed) && listed.length) {
      return listed.map(item => {
        if (typeof item === "string") return { id: item, config: Core.PRESETS[item] };
        const id = item.id || item.key || item.presetId;
        return { id, config: Core.PRESETS && Core.PRESETS[id] ? Core.PRESETS[id] : item, summary: item };
      });
    }
    return Object.entries(Core.PRESETS || {}).map(([id, config]) => ({ id, config }));
  }

  function presetMeta(entry) {
    const config = entry.config || {};
    const meta = { ...(entry.summary || {}), ...(config.metadata || {}), ...(config.meta || {}) };
    const applicationKey = canonicalApplicationKey(config.application || meta.applicationKey || meta.application);
    const fallback = applicationFallbacks[applicationKey] || applicationFallbacks.theory;
    const lens = meta.mode || meta.lens || config.mode || config.lens || "forward";
    const model = config.simulation?.model || "none";
    const modelMechanisms = {
      diffusion: "Synchronous radius-one weighted neighbour diffusion",
      "reaction-diffusion": "Synchronous radius-one reaction and neighbour diffusion",
      "curvature-flow": "Incident-star curvature feedback against a precompiled target",
      hybrid: "Incident-star curvature feedback plus neighbour diffusion",
      none: "Static local relations"
    };
    const runtimeLocality = config.runtimeLocality || config.simulation?.locality || ((model === "curvature-flow" || model === "hybrid") ? "L1 runtime (global scale gauge disclosed)" : "L0 runtime (fixed adjacency, synchronous)");
    const localityText = meta.locality || config.locality || runtimeLocality;
    return {
      id: entry.id,
      title: meta.title || config.title || entry.id.replace(/-/g, " "),
      mode: String(lens).charAt(0).toUpperCase() + String(lens).slice(1),
      applicationKey,
      question: meta.question || config.question || "How do local updates change the global observables?",
      boundary: meta.boundary || meta.caveat || config.boundary || config.claims?.doesNotDemonstrate || fallback.boundary,
      mechanism: meta.mechanism || modelMechanisms[model] || fallback.mechanism,
      observable: meta.observable || fallback.observable,
      locality: String(localityText).includes("L2") ? localityText : `${localityText}; measurements using an eigensolve are L2 analysis`,
      eventLabel: `Declared intervention · ${String(config.event?.type || "none").replace(/-/g, " ")}`
    };
  }

  function fillPresetSelect() {
    presetEntries = normalizePresetEntries();
    elements.preset.replaceChildren();
    presetEntries.forEach(entry => {
      const option = document.createElement("option");
      option.value = entry.id;
      option.textContent = presetMeta(entry).title;
      elements.preset.append(option);
    });
  }

  function setNestedIfPresent(config, paths, value) {
    for (const path of paths) {
      let target = config;
      let found = true;
      for (let index = 0; index < path.length - 1; index += 1) {
        if (!target || typeof target !== "object" || !(path[index] in target)) {
          found = false;
          break;
        }
        target = target[path[index]];
      }
      const key = path[path.length - 1];
      if (found && target && typeof target === "object" && key in target) {
        target[key] = value;
        return true;
      }
    }
    return false;
  }

  function applyControlConfiguration(baseConfig) {
    const config = deepClone(baseConfig);
    config.generator = config.generator || {};
    config.generator.seed = elements.seed.value.trim() || "geometry-1";
    config.generator.disorder = Number(elements.disorder.value);
    return config;
  }

  function normalizeConfig(config) {
    if (typeof Core.validateConfig !== "function") return config;
    const report = Core.validateConfig(config);
    if (report && report.valid === false) throw new Error((report.errors || ["invalid configuration"]).join("; "));
    return report && report.config ? report.config : report;
  }

  function makeState(configOrPreset) {
    const created = Core.createState(configOrPreset);
    return created;
  }

  function loadPreset(id, keepSeed = false) {
    stopRunning();
    const entry = presetEntries.find(candidate => candidate.id === id) || presetEntries[0];
    if (!entry) throw new Error("No Global Geometry presets are available.");
    currentPreset = presetMeta(entry);
    if (!keepSeed) {
      const baseSeed = entry.config && (entry.config.seed || entry.config.generator?.seed);
      elements.seed.value = baseSeed || `${entry.id}-1`;
    }
    const controlled = applyControlConfiguration(entry.config);
    currentConfig = normalizeConfig(controlled);
    state = makeState(currentConfig);
    analysis = state.analysis || Core.analyzeState(state);
    selectedNodeId = null;
    clearComparison();
    elements.preset.value = entry.id;
    elements.event.textContent = currentPreset.eventLabel;
    elements.event.setAttribute("aria-label", `${currentPreset.eventLabel}; this is outside the ordinary synchronous runtime step`);
    refreshAll(true);
  }

  function stopRunning() {
    running = false;
    elements.run.textContent = "Run";
    elements.run.setAttribute("aria-pressed", "false");
  }

  function toggleRunning() {
    running = !running;
    elements.run.textContent = running ? "Pause" : "Run";
    elements.run.setAttribute("aria-pressed", String(running));
    if (running) requestAnimationFrame(frame);
  }

  function performStep(count = 1) {
    const strength = Number(elements.rate.value);
    const overrides = scaledSimulationOverrides(strength);
    for (let index = 0; index < count; index += 1) {
      state = Core.stepState(state, overrides);
    }
    analysis = state.analysis || Core.analyzeState(state);
    state.analysis = analysis;
    markComparisonStale();
    refreshAll(false);
  }

  function scaledSimulationOverrides(strength) {
    const simulation = state?.config?.simulation || currentConfig?.simulation || {};
    const overrides = {};
    if (simulation.model === "curvature-flow" || simulation.model === "hybrid") {
      overrides.rate = finite(simulation.rate, 0.06) * strength;
    }
    if (simulation.model === "diffusion" || simulation.model === "hybrid") {
      overrides.diffusivity = finite(simulation.diffusivity, 0.75) * strength;
    }
    if (simulation.model === "reaction-diffusion") {
      overrides.dt = finite(simulation.dt, 0.5) * strength;
    }
    return overrides;
  }

  function frame(timestamp) {
    if (!running) return;
    if (timestamp - lastFrame >= 90) {
      lastFrame = timestamp;
      performStep(1);
    }
    if (running) requestAnimationFrame(frame);
  }

  function applyLocalEvent() {
    stopRunning();
    if (typeof Core.applyTopologyEvent !== "function") return;
    const event = selectedNodeId == null ? undefined : { index: selectedNodeId };
    state = Core.applyTopologyEvent(state, event);
    analysis = state.analysis || Core.analyzeState(state);
    selectedNodeId = null;
    markComparisonStale(true);
    refreshAll(false);
  }

  function topologyPartsFor(targetAnalysis, targetState) {
    const top = targetAnalysis?.topology || {};
    const betti = top.betti || top.bettiNumbers || top.betas || {};
    const get = index => {
      const value = Array.isArray(betti) ? betti[index] : betti[index] ?? betti[`b${index}`] ?? betti[`beta${index}`] ?? betti[`β${index}`];
      return Number.isInteger(value) && value >= 0 ? value : null;
    };
    const chiRaw = top.eulerCharacteristic ?? top.euler ?? top.chi;
    const chi = Number.isInteger(chiRaw) ? chiRaw : null;
    const b0 = get(0), b1 = get(1), b2 = get(2);
    const residual = top.eulerPoincareResidual;
    const valid = [b0, b1, b2, chi].every(Number.isInteger) && b0 - b1 + b2 === chi && (residual == null || residual === 0);
    return {
      b0, b1, b2, chi, valid,
      simplexEuler: targetState.nodes.length - targetState.edges.length + targetState.faces.length
    };
  }

  function topologyParts() {
    return topologyPartsFor(analysis, state);
  }

  function curvatureParts() {
    const curvature = analysis?.curvature || {};
    const vertices = curvature.vertices || curvature.values || [];
    const targets = curvature.targets || curvature.targetVertices || state.metadata?.targetCurvature || [];
    const vertexMap = new Map((Array.isArray(vertices) ? vertices : []).map((entry, index) => [Number.isInteger(entry?.id) ? entry.id : index, entry]));
    const values = state.nodes.map((node, index) => {
      const raw = Array.isArray(vertices) ? vertexMap.get(index) : vertices[node.id] ?? vertices[String(node.id)];
      if (typeof raw === "number") return raw;
      return finite(raw?.curvature ?? raw?.value ?? raw?.defect, NaN);
    });
    const targetValues = state.nodes.map((node, index) => {
      const vertex = vertexMap.get(index);
      const raw = Array.isArray(targets) ? targets[index] : targets[node.id] ?? targets[String(node.id)];
      if (typeof raw === "number") return raw;
      return finite(raw?.target ?? raw?.value ?? vertex?.target, NaN);
    });
    const errors = values.map((value, index) => Number.isFinite(value) ? value - targetValues[index] : NaN);
    const finiteErrors = errors.filter(Number.isFinite);
    const rms = finite(curvature.rmsError ?? curvature.targetRmsError,
      finiteErrors.length ? Math.sqrt(finiteErrors.reduce((sum, value) => sum + value * value, 0) / finiteErrors.length) : NaN);
    return {
      values, targets: targetValues, errors, rms,
      total: finite(curvature.total ?? curvature.totalCurvature, NaN),
      targetTotal: finite(curvature.targetTotal, NaN),
      residual: finite(curvature.gaussBonnetResidual ?? curvature.residual, NaN),
      identityApplicable: curvature.identityApplicable === true || (
        curvature.available === true &&
        finite(curvature.degenerateFaceCount, 1) === 0 &&
        finite(curvature.nonManifoldEdgeCount, 1) === 0 &&
        analysis?.topology?.manifoldCheck?.isEdgeManifold === true
      )
    };
  }

  function normalizeProfile(raw, kind) {
    if (!raw) return [];
    const source = Array.isArray(raw) ? raw : raw.points || raw.profile || raw.values || [];
    if (!Array.isArray(source)) return [];
    return source.map((point, index) => {
      if (typeof point === "number") return { scale: index + 1, dimension: point };
      return {
        scale: finite(point.scale ?? point.radius ?? point.time ?? point.t ?? point.step, index + 1),
        dimension: finite(point.dimension ?? point.localDimension ?? point.value ?? point.d ?? point[kind], NaN)
      };
    }).filter(point => Number.isFinite(point.scale) && point.scale > 0 && Number.isFinite(point.dimension));
  }

  function dimensionProfilesFor(targetAnalysis) {
    const dimensions = targetAnalysis?.dimensions || {};
    return {
      volume: normalizeProfile(dimensions.volumeGrowth || dimensions.volumeProfile || dimensions.volume, "volume"),
      spectral: normalizeProfile(dimensions.spectralProfile || dimensions.spectral || targetAnalysis?.spectrum?.spectralProfile, "spectral"),
      walk: normalizeProfile(dimensions.walkProfile || dimensions.walk, "walk")
    };
  }

  function dimensionProfiles() {
    return dimensionProfilesFor(analysis);
  }

  function clearComparison() {
    comparisonStep = null;
    comparisonRecord = null;
    elements.comparisonTopology.textContent = "not compared";
    elements.comparisonProfile.textContent = "—";
    elements.comparisonSpectrum.textContent = "—";
    elements.comparisonStatus.textContent = "The comparison is deterministic and matched by preset, parameters, step, and observation schedule.";
    elements.comparisonStatus.classList.remove("is-error");
  }

  function markComparisonStale(intervention = false) {
    if (comparisonStep == null || (!intervention && comparisonStep === state.step)) return;
    elements.comparisonStatus.textContent = intervention
      ? "The state changed through an intervention; compare again to create a matched pair."
      : `Comparison is from step ${comparisonStep}; compare again to match the current step ${state.step}.`;
  }

  function rmsDistance(left, right, limit = Infinity) {
    const count = Math.min(left.length, right.length, limit);
    if (!count) return NaN;
    let squareSum = 0;
    for (let index = 0; index < count; index += 1) {
      const difference = left[index] - right[index];
      squareSum += difference * difference;
    }
    return Math.sqrt(squareSum / count);
  }

  function profileDistance(leftProfiles, rightProfiles) {
    const distances = Object.keys(visibleSeries).map(key => {
      const left = leftProfiles[key].map(point => point.dimension);
      const right = rightProfiles[key].map(point => point.dimension);
      return rmsDistance(left, right);
    }).filter(Number.isFinite);
    return distances.length ? Math.sqrt(distances.reduce((sum, value) => sum + value * value, 0) / distances.length) : NaN;
  }

  function compareWorlds() {
    try {
      stopRunning();
      const alternateConfig = deepClone(currentConfig);
      const comparisonSeed = elements.compareSeed.value.trim();
      if (!comparisonSeed) throw new Error("enter a comparison seed");
      const changed = setNestedIfPresent(alternateConfig, [["seed"], ["generator", "seed"]], comparisonSeed);
      if (!changed) throw new Error("this configuration does not declare a seed field");
      const validated = normalizeConfig(alternateConfig);
      let alternateState = makeState(validated);
      const overrides = scaledSimulationOverrides(Number(elements.rate.value));
      for (let index = 0; index < state.step; index += 1) {
        alternateState = Core.stepState(alternateState, overrides);
      }
      const alternateAnalysis = alternateState.analysis || Core.analyzeState(alternateState);
      const leftTopology = topologyPartsFor(analysis, state);
      const rightTopology = topologyPartsFor(alternateAnalysis, alternateState);
      const topologyMatch = ["b0", "b1", "b2", "chi"].every(key => leftTopology[key] === rightTopology[key]);
      const distanceProfiles = profileDistance(dimensionProfilesFor(analysis), dimensionProfilesFor(alternateAnalysis));
      const leftSpectrum = analysis?.spectrum?.eigenvalues || [];
      const rightSpectrum = alternateAnalysis?.spectrum?.eigenvalues || [];
      const spectrumDistance = rmsDistance(leftSpectrum, rightSpectrum, 16);

      elements.comparisonTopology.textContent = topologyMatch
        ? `match (χ ${formatNumber(leftTopology.chi, 0)})`
        : `different (${formatNumber(leftTopology.chi, 0)} vs ${formatNumber(rightTopology.chi, 0)})`;
      elements.comparisonProfile.textContent = Number.isFinite(distanceProfiles) ? formatNumber(distanceProfiles, 4) : "unresolved";
      elements.comparisonSpectrum.textContent = Number.isFinite(spectrumDistance) ? formatNumber(spectrumDistance, 4) : "unresolved";
      comparisonStep = state.step;
      const identicalSeed = comparisonSeed === (currentConfig.seed || currentConfig.generator?.seed);
      comparisonRecord = {
        step: state.step,
        referenceSeed: currentConfig.seed || currentConfig.generator?.seed,
        comparisonSeed,
        topologyMatch,
        dimensionProfileRms: Number.isFinite(distanceProfiles) ? distanceProfiles : null,
        firstSixteenEigenvalueRms: Number.isFinite(spectrumDistance) ? spectrumDistance : null,
        scaleAlignment: "same preset schedule; each profile compared indexwise at its declared native scales",
        claimBoundary: "finite observable agreement only; not isometry or continuum universality"
      };
      elements.comparisonStatus.textContent = identicalSeed
        ? "Seeds are identical: zero distance is a replay check, not universality evidence."
        : `Finite matched comparison at step ${state.step}. Small signature distance supports only observable agreement for these two worlds.`;
      elements.comparisonStatus.classList.remove("is-error");
    } catch (error) {
      elements.comparisonStatus.textContent = `Comparison failed: ${error.message}`;
      elements.comparisonStatus.classList.add("is-error");
    }
  }

  function sampleRelative(profile, relative) {
    if (!profile.length) return null;
    if (profile.length === 1) return profile[0];
    const logs = profile.map(point => Math.log(point.scale));
    const target = Math.min(...logs) + relative * (Math.max(...logs) - Math.min(...logs));
    return profile.reduce((best, point) => (
      Math.abs(Math.log(point.scale) - target) < Math.abs(Math.log(best.scale) - target) ? point : best
    ), profile[0]);
  }

  function updateScenario() {
    elements.mode.textContent = currentPreset.mode;
    elements.question.textContent = currentPreset.question;
    elements.boundary.textContent = currentPreset.boundary;
    elements.worldTitle.textContent = currentPreset.title;
    const circlePacking = currentConfig.analysis?.curvatureMetric === "circle-packing" || ["curvature-flow", "hybrid"].includes(currentConfig.simulation?.model);
    const metricSource = circlePacking
      ? "intrinsic lengths come from circle radii; the projection is only a view"
      : "stored edge lengths define the finite metric; source coordinates initialize them";
    elements.worldSubtitle.textContent = `${currentPreset.locality} · ${metricSource}.`;
    elements.processLocal.textContent = currentPreset.mechanism;
    elements.processCompose.textContent = state.faces.length ? "edge lengths → paths; angle sums → loop defect" : "edge weights → paths; repeated neighbours → diffusion";
    elements.processGlobal.textContent = currentPreset.observable;
    elements.event.textContent = currentPreset.eventLabel;
    elements.event.setAttribute("aria-label", `${currentPreset.eventLabel}; this is outside the ordinary synchronous runtime step`);
  }

  function updateMeasurements() {
    const topology = topologyParts();
    const curvature = curvatureParts();
    const profiles = dimensionProfiles();
    const relative = Number(elements.scale.value) / 100;
    const volumePoint = sampleRelative(profiles.volume, relative);
    const spectralPoint = sampleRelative(profiles.spectral, relative);
    const walkPoint = sampleRelative(profiles.walk, relative);
    const gap = finite(analysis?.spectrum?.gap ?? analysis?.spectrum?.spectralGap, NaN);

    elements.topologyValue.textContent = topology.valid ? `χ ${formatNumber(topology.chi, 0)}` : "unavailable";
    elements.topologyDetail.textContent = topology.valid
      ? `β₀ ${formatNumber(topology.b0, 0)} · β₁ ${formatNumber(topology.b1, 0)} · β₂ ${formatNumber(topology.b2, 0)}`
      : "exact fields failed Euler–Poincaré validation";
    elements.topologyEvidence.textContent = topology.valid ? "exact" : "withheld";
    elements.topologyEvidence.className = `evidence ${topology.valid ? "exact" : "hypothesis"}`;

    if (state.faces.length && curvature.identityApplicable && Number.isFinite(curvature.residual)) {
      elements.curvatureEvidence.textContent = "identity";
      elements.curvatureEvidence.className = "evidence exact";
      elements.curvatureValue.textContent = `|εGB| ${formatNumber(Math.abs(curvature.residual), 2)}`;
      elements.curvatureDetail.textContent = `angle defect · ΣK ${formatNumber(curvature.total, 4)} · 2πχ ${formatNumber(2 * Math.PI * topology.chi, 4)}`;
    } else if (state.faces.length) {
      elements.curvatureEvidence.textContent = "withheld";
      elements.curvatureEvidence.className = "evidence hypothesis";
      elements.curvatureValue.textContent = "not applicable";
      elements.curvatureDetail.textContent = "exact badge withheld: manifold or triangle-metric validation failed";
    } else {
      elements.curvatureEvidence.textContent = "not applicable";
      elements.curvatureEvidence.className = "evidence numerical";
      elements.curvatureValue.textContent = "graph mode";
      elements.curvatureDetail.textContent = "no angle-defect claim without triangular faces";
    }

    const mainDimension = spectralPoint || volumePoint || walkPoint;
    const mainLabel = spectralPoint ? "dₛ" : volumePoint ? "dᵥ" : "d_w";
    elements.dimensionValue.textContent = mainDimension ? `${mainLabel} ${formatNumber(mainDimension.dimension, 2)}` : "unresolved";
    elements.dimensionDetail.textContent = mainDimension
      ? `finite point estimate · no refinement-supported plateau · dᵥ ${volumePoint ? formatNumber(volumePoint.dimension, 2) : "—"} · dₛ ${spectralPoint ? formatNumber(spectralPoint.dimension, 2) : "—"} · d_w ${walkPoint ? formatNumber(walkPoint.dimension, 2) : "—"}`
      : "no stable finite-scale window";

    const flowReport = state.lastStep?.reports?.find(report => report.model === "curvature-flow");
    const primaryResponse = finite(analysis?.curvature?.targetRmsError ?? flowReport?.energyAfter ?? curvature.rms, NaN);
    if (Number.isFinite(primaryResponse) && state.faces.length) {
      elements.responseValue.textContent = formatNumber(primaryResponse, 4);
      elements.responseDetail.textContent = `target curvature RMS · step ${state.step}`;
    } else {
      elements.responseValue.textContent = Number.isFinite(gap) ? formatNumber(gap, 4) : "—";
      elements.responseDetail.textContent = `normalized-Laplacian spectral gap · step ${state.step}`;
    }
  }

  function observationScaleLabel(value) {
    if (value < 25) return "microscopic";
    if (value < 70) return "mesoscopic";
    return "macroscopic";
  }

  function nodeMetric(index, curvature) {
    const error = curvature.errors[index];
    if (Number.isFinite(error)) return error;
    if (Number.isFinite(curvature.values[index])) return curvature.values[index];
    const node = state.nodes[index];
    return finite(node.value ?? node.v ?? node.u, 0);
  }

  function cssColor(variable) {
    return getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
  }

  function mixColor(value, maximum) {
    const low = cssColor("--low");
    const mid = cssColor("--mid");
    const high = cssColor("--high");
    if (!Number.isFinite(value) || maximum <= 1e-15) return mid;
    const ratio = Math.max(-1, Math.min(1, value / maximum));
    return ratio < -0.18 ? low : ratio > 0.18 ? high : mid;
  }

  function projection() {
    const points = state.nodes.map(node => ({
      x: finite(node.x ?? node.position?.[0], 0),
      y: finite(node.y ?? node.position?.[1], 0) - 0.18 * finite(node.z ?? node.position?.[2], 0)
    }));
    const xs = points.map(point => point.x);
    const ys = points.map(point => point.y);
    let minX = Math.min(...xs);
    let maxX = Math.max(...xs);
    let minY = Math.min(...ys);
    let maxY = Math.max(...ys);
    if (!(maxX > minX)) { minX -= 1; maxX += 1; }
    if (!(maxY > minY)) { minY -= 1; maxY += 1; }
    const width = 760;
    const height = 560;
    const padding = 38;
    const scale = Math.min((width - 2 * padding) / (maxX - minX), (height - 2 * padding) / (maxY - minY));
    return points.map(point => ({
      x: padding + (point.x - minX) * scale + ((width - 2 * padding) - (maxX - minX) * scale) / 2,
      y: height - padding - (point.y - minY) * scale - ((height - 2 * padding) - (maxY - minY) * scale) / 2
    }));
  }

  function svgElement(name, attributes) {
    const element = document.createElementNS(SVG_NS, name);
    Object.entries(attributes || {}).forEach(([key, value]) => element.setAttribute(key, String(value)));
    return element;
  }

  function renderWorld() {
    const points = projection();
    const curvature = curvatureParts();
    const metrics = state.nodes.map((_, index) => nodeMetric(index, curvature));
    const maximum = Math.max(1e-9, ...metrics.filter(Number.isFinite).map(Math.abs));
    const hasTargets = curvature.targets.some(Number.isFinite);
    if (hasTargets) {
      elements.worldKeyLow.textContent = "below target";
      elements.worldKeyMid.textContent = "near target";
      elements.worldKeyHigh.textContent = "above target";
    } else if (state.faces.length) {
      elements.worldKeyLow.textContent = "negative defect";
      elements.worldKeyMid.textContent = "near zero";
      elements.worldKeyHigh.textContent = "positive defect";
    } else {
      elements.worldKeyLow.textContent = "low signal";
      elements.worldKeyMid.textContent = "middle signal";
      elements.worldKeyHigh.textContent = "high signal";
    }
    elements.world.setAttribute("viewBox", "0 0 760 560");
    elements.faceLayer.replaceChildren();
    elements.edgeLayer.replaceChildren();
    elements.nodeLayer.replaceChildren();

    state.faces.forEach(face => {
      if (!Array.isArray(face) || face.length !== 3 || face.some(index => !points[index])) return;
      const value = face.reduce((sum, index) => sum + metrics[index], 0) / 3;
      elements.faceLayer.append(svgElement("polygon", {
        points: face.map(index => `${points[index].x},${points[index].y}`).join(" "),
        fill: mixColor(value, maximum),
        opacity: 0.48,
        class: "geometry-face"
      }));
    });

    state.edges.forEach(edge => {
      const source = Number.isInteger(edge.source) ? edge.source : edge.a ?? edge.u;
      const target = Number.isInteger(edge.target) ? edge.target : edge.b ?? edge.v;
      if (!points[source] || !points[target]) return;
      const weight = finite(edge.weight, 1);
      elements.edgeLayer.append(svgElement("line", {
        x1: points[source].x, y1: points[source].y,
        x2: points[target].x, y2: points[target].y,
        class: `geometry-edge${weight > 1.35 ? " is-strong" : ""}`,
        opacity: Math.max(0.22, Math.min(0.9, 0.32 + 0.22 * weight))
      }));
    });

    state.nodes.forEach((node, index) => {
      const radius = Math.max(4.5, Math.min(12, 5.3 + 2.2 * Math.sqrt(Math.max(0.05, finite(node.radius, 1)))));
      const circle = svgElement("circle", {
        cx: points[index].x,
        cy: points[index].y,
        r: radius,
        fill: mixColor(metrics[index], maximum),
        class: `geometry-node${node.id === selectedNodeId ? " is-selected" : ""}`,
        role: "button",
        tabindex: "0",
        "aria-label": `Vertex ${node.id}; local value ${formatNumber(metrics[index], 3)}`
      });
      const select = () => {
        selectedNodeId = node.id;
        updateSelection(index, metrics[index], curvature);
        renderWorld();
      };
      circle.addEventListener("click", select);
      circle.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          select();
        }
      });
      circle.addEventListener("pointerenter", event => showTooltip(event, node, index, metrics[index]));
      circle.addEventListener("pointermove", event => positionTooltip(event));
      circle.addEventListener("pointerleave", hideTooltip);
      elements.nodeLayer.append(circle);
    });
  }

  function incidentDegree(index) {
    return state.edges.reduce((degree, edge) => {
      const source = Number.isInteger(edge.source) ? edge.source : edge.a ?? edge.u;
      const target = Number.isInteger(edge.target) ? edge.target : edge.b ?? edge.v;
      return degree + (source === index || target === index ? 1 : 0);
    }, 0);
  }

  function updateSelection(index, metric, curvature) {
    const node = state.nodes[index];
    const curvatureValue = curvature.values[index];
    const target = curvature.targets[index];
    const field = finite(node.value ?? node.v ?? node.u, NaN);
    const geometricDetail = Number.isFinite(curvatureValue)
      ? (Number.isFinite(target)
        ? `angle defect ${formatNumber(curvatureValue, 4)}, target ${formatNumber(target, 4)}`
        : `angle defect ${formatNumber(curvatureValue, 4)}`)
      : `local field ${formatNumber(field, 4)}`;
    elements.selection.textContent = `Vertex ${node.id}: degree ${incidentDegree(index)} · radius ${formatNumber(node.radius, 3)} · ${geometricDetail} · displayed signal ${formatNumber(metric, 4)}.`;
  }

  function showTooltip(event, node, index, metric) {
    elements.tooltip.textContent = `Vertex ${node.id} · degree ${incidentDegree(index)} · local value ${formatNumber(metric, 3)}`;
    elements.tooltip.hidden = false;
    positionTooltip(event);
  }

  function positionTooltip(event) {
    const bounds = elements.world.parentElement.getBoundingClientRect();
    elements.tooltip.style.left = `${Math.min(bounds.width - 170, Math.max(8, event.clientX - bounds.left + 12))}px`;
    elements.tooltip.style.top = `${Math.max(8, event.clientY - bounds.top - 34)}px`;
  }

  function hideTooltip() {
    elements.tooltip.hidden = true;
  }

  function renderProfile() {
    const profiles = dimensionProfiles();
    const width = 460;
    const height = 330;
    const margin = { left: 48, right: 20, top: 20, bottom: 44 };
    const plotWidth = width - margin.left - margin.right;
    const plotHeight = height - margin.top - margin.bottom;
    const allDimensions = Object.entries(profiles).flatMap(([key, values]) => visibleSeries[key] ? values.map(point => point.dimension) : []);
    const yMax = Math.max(3, Math.min(8, Math.ceil(Math.max(0, ...allDimensions) * 1.15)));
    elements.profile.setAttribute("viewBox", `0 0 ${width} ${height}`);
    elements.profile.replaceChildren();
    const chartTitle = svgElement("title", { id: "profile-title" });
    chartTitle.textContent = "Finite-scale dimension profile";
    const chartDescription = svgElement("desc", { id: "profile-desc" });
    chartDescription.textContent = "Volume-growth, spectral, and walk dimension estimates across their independently normalized logarithmic scales.";
    elements.profile.append(chartTitle, chartDescription);

    const x = relative => margin.left + relative * plotWidth;
    const y = value => margin.top + plotHeight - Math.max(0, Math.min(yMax, value)) / yMax * plotHeight;
    const logPosition = (profile, point) => {
      const logs = profile.map(item => Math.log(item.scale));
      const minimum = Math.min(...logs), maximum = Math.max(...logs);
      return maximum > minimum ? (Math.log(point.scale) - minimum) / (maximum - minimum) : 0.5;
    };

    for (let tick = 0; tick <= 4; tick += 1) {
      const value = tick * yMax / 4;
      const grid = svgElement("line", { x1: margin.left, x2: width - margin.right, y1: y(value), y2: y(value), stroke: "var(--line)", "stroke-width": 1 });
      elements.profile.append(grid);
      const label = svgElement("text", { x: margin.left - 8, y: y(value) + 4, "text-anchor": "end", fill: "var(--muted)", "font-size": 11 });
      label.textContent = formatNumber(value, 1);
      elements.profile.append(label);
    }

    const axis = svgElement("path", {
      d: `M${margin.left},${margin.top}V${margin.top + plotHeight}H${width - margin.right}`,
      fill: "none", stroke: "var(--ink)", "stroke-width": 1.2
    });
    elements.profile.append(axis);
    const labels = [
      { x: margin.left, anchor: "start", text: "micro" },
      { x: margin.left + plotWidth / 2, anchor: "middle", text: "meso" },
      { x: width - margin.right, anchor: "end", text: "macro" }
    ];
    labels.forEach(item => {
      const label = svgElement("text", { x: item.x, y: height - 18, "text-anchor": item.anchor, fill: "var(--muted)", "font-size": 11 });
      label.textContent = item.text;
      elements.profile.append(label);
    });
    const yLabel = svgElement("text", {
      x: 14, y: margin.top + plotHeight / 2, transform: `rotate(-90 14 ${margin.top + plotHeight / 2})`,
      "text-anchor": "middle", fill: "var(--muted)", "font-size": 11
    });
    yLabel.textContent = "effective dimension";
    elements.profile.append(yLabel);

    const colors = { volume: "var(--series-volume)", spectral: "var(--series-spectral)", walk: "var(--series-walk)" };
    Object.entries(profiles).forEach(([key, values]) => {
      if (!visibleSeries[key] || values.length < 2) return;
      const path = values.map((point, index) => `${index ? "L" : "M"}${x(logPosition(values, point))},${y(point.dimension)}`).join(" ");
      elements.profile.append(svgElement("path", {
        d: path, fill: "none", stroke: colors[key], "stroke-width": 2.4,
        "stroke-linejoin": "round", "stroke-linecap": "round"
      }));
    });

    const relative = Number(elements.scale.value) / 100;
    const guideX = x(relative);
    elements.profile.append(svgElement("line", {
      x1: guideX, x2: guideX, y1: margin.top, y2: margin.top + plotHeight,
      stroke: "var(--ink)", "stroke-width": 1.2, "stroke-dasharray": "4 4"
    }));
    Object.entries(profiles).forEach(([key, values]) => {
      if (!visibleSeries[key]) return;
      const point = sampleRelative(values, relative);
      if (!point) return;
      const marker = svgElement("circle", { cx: x(logPosition(values, point)), cy: y(point.dimension), r: 4.5, fill: colors[key], stroke: "var(--surface)", "stroke-width": 2 });
      elements.profile.append(marker);
    });

    const scaleNames = { volume: "r", spectral: "tₕ", walk: "t_w" };
    const current = Object.entries(profiles).map(([key, values]) => {
      const point = sampleRelative(values, relative);
      return point ? `${key} ${formatNumber(point.dimension, 2)} at ${scaleNames[key]}=${formatNumber(point.scale, 2)}` : null;
    }).filter(Boolean);
    elements.profileDetail.textContent = `${observationScaleLabel(Number(elements.scale.value))} position on each estimator's normalized log scale · ${current.join(" · ") || "no resolved profile at this scale"}. These clocks are not identified with one another; endpoints are not continuum dimensions.`;
  }

  function updateConfigurationRecord(writeEditor) {
    if (writeEditor) elements.config.value = JSON.stringify(currentConfig, null, 2);
    elements.recordSchema.textContent = `${state.version ?? "—"} / ${analysis?.schemaVersion ?? "—"}`;
    elements.recordTime.textContent = `${state.step} / ${formatNumber(state.time, 3)}`;
    elements.recordSize.textContent = `${state.nodes.length} / ${state.edges.length} / ${state.faces.length}`;
    elements.recordMethod.textContent = analysis?.diagnostics?.method || state.metadata?.method || currentPreset.locality;
    elements.recordReplay.textContent = state.metadata?.replayId || `gg-${shortHash({ config: currentConfig, step: state.step, lastEvent: state.lastEvent })}`;
  }

  function renderApplications() {
    const seen = new Set();
    const cards = [];
    presetEntries.forEach(entry => {
      const meta = presetMeta(entry);
      if (meta.applicationKey === "theory") return;
      if (seen.has(meta.applicationKey)) return;
      seen.add(meta.applicationKey);
      const fallback = applicationFallbacks[meta.applicationKey] || {
        title: meta.title, mechanism: meta.mechanism, observable: meta.observable, boundary: meta.boundary
      };
      cards.push({ ...fallback, ...meta });
    });
    Object.entries(applicationFallbacks).forEach(([key, fallback]) => {
      if (key !== "theory" && !seen.has(key)) cards.push({ ...fallback, applicationKey: key });
    });
    elements.applicationCards.replaceChildren();
    cards.slice(0, 6).forEach(card => {
      const article = document.createElement("article");
      const badge = document.createElement("span");
      badge.className = "evidence analogy";
      badge.textContent = "application analogy";
      const title = document.createElement("h3");
      title.textContent = card.title;
      const mechanism = document.createElement("p");
      mechanism.textContent = card.mechanism;
      const observable = document.createElement("p");
      observable.textContent = `Readout: ${card.observable}`;
      const boundary = document.createElement("small");
      boundary.textContent = card.boundary;
      article.append(badge, title, mechanism, observable, boundary);
      elements.applicationCards.append(article);
    });
  }

  function refreshAll(writeEditor) {
    updateScenario();
    updateMeasurements();
    renderWorld();
    renderProfile();
    updateConfigurationRecord(writeEditor);
  }

  function applyConfigurationText() {
    try {
      stopRunning();
      const parsed = JSON.parse(elements.config.value);
      currentConfig = normalizeConfig(parsed);
      state = makeState(currentConfig);
      analysis = state.analysis || Core.analyzeState(state);
      clearComparison();
      const configuredId = currentConfig.id || currentConfig.presetId;
      const matched = presetEntries.find(entry => entry.id === configuredId);
      currentPreset = matched ? presetMeta(matched) : {
        id: "custom", title: "Validated custom configuration", mode: currentConfig.mode || "Forward",
        applicationKey: "materials", question: currentConfig.question || "What global geometry follows from this validated local model?",
        boundary: "Custom finite configuration; no continuum or application adequacy claim.",
        mechanism: "Validated closed-schema local dynamics", observable: "Topology, curvature, spectrum, and finite dimension profiles",
        locality: currentConfig.locality || "locality declared by configuration",
        eventLabel: `Declared intervention · ${String(currentConfig.event?.type || "none").replace(/-/g, " ")}`
      };
      selectedNodeId = null;
      elements.configStatus.textContent = "Configuration accepted and replayed from step zero.";
      elements.configStatus.classList.remove("is-error");
      refreshAll(true);
    } catch (error) {
      elements.configStatus.textContent = `Configuration rejected: ${error.message}`;
      elements.configStatus.classList.add("is-error");
    }
  }

  function exportRun() {
    const payload = {
      kind: "global-geometry-finite-run",
      exportedAt: new Date().toISOString(),
      evidence: {
        exact: ["finite cell-complex homology", "Euler characteristic", "Gauss-Bonnet when applicable"],
        numerical: ["eigenspectrum", "dimension profiles", "local-flow trajectory"],
        researchTarget: ["paired-world observable agreement", "continuum universality", "recognition ambiguity"],
        analogy: currentPreset.applicationKey,
        boundary: currentPreset.boundary
      },
      configuration: currentConfig,
      state,
      analysis,
      comparison: comparisonRecord,
      replayId: elements.recordReplay.textContent
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${currentPreset.id || "global-geometry"}-step-${state.step}.json`;
    document.body.append(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function wireControls() {
    elements.preset.addEventListener("change", () => loadPreset(elements.preset.value));
    elements.run.addEventListener("click", toggleRunning);
    elements.step.addEventListener("click", () => {
      stopRunning();
      performStep(1);
    });
    elements.reset.addEventListener("click", () => loadPreset(elements.preset.value, true));
    elements.event.addEventListener("click", applyLocalEvent);
    elements.rate.addEventListener("input", () => {
      elements.rateOutput.value = Number(elements.rate.value).toFixed(2);
    });
    elements.disorder.addEventListener("input", () => {
      elements.disorderOutput.value = Number(elements.disorder.value).toFixed(2);
    });
    elements.disorder.addEventListener("change", () => loadPreset(elements.preset.value, true));
    elements.seed.addEventListener("change", () => loadPreset(elements.preset.value, true));
    elements.scale.addEventListener("input", () => {
      elements.scaleOutput.value = observationScaleLabel(Number(elements.scale.value));
      updateMeasurements();
      renderProfile();
    });
    document.querySelectorAll("[data-series]").forEach(button => {
      button.addEventListener("click", () => {
        const key = button.dataset.series;
        visibleSeries[key] = !visibleSeries[key];
        button.setAttribute("aria-pressed", String(visibleSeries[key]));
        renderProfile();
      });
    });
    elements.applyConfig.addEventListener("click", applyConfigurationText);
    elements.restoreConfig.addEventListener("click", () => {
      elements.config.value = JSON.stringify(currentConfig, null, 2);
      elements.configStatus.textContent = "Editor restored to the current normalized configuration.";
      elements.configStatus.classList.remove("is-error");
    });
    elements.exportRun.addEventListener("click", exportRun);
    elements.compare.addEventListener("click", compareWorlds);
    window.addEventListener("resize", () => {
      renderWorld();
      renderProfile();
    });
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) stopRunning();
    });
  }

  function initialize() {
    fillPresetSelect();
    if (!presetEntries.length) throw new Error("No validated presets are available.");
    wireControls();
    renderApplications();
    loadPreset(presetEntries[0].id);
  }

  try {
    initialize();
  } catch (error) {
    elements.configStatus.textContent = `Laboratory initialization failed: ${error.message}`;
    elements.configStatus.classList.add("is-error");
  }
}());
