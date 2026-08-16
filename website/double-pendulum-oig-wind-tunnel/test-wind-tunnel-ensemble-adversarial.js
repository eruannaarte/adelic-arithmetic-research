"use strict";

/*
 * Independent hostile checks for the finite-ensemble and calibration-lab UI.
 * This file intentionally does not reuse the production browser tests.  The
 * numerical API tests are appended only after that API is stable; these shell
 * checks already guard the scientific language and cross-file contract.
 */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const directory = __dirname;
const html = fs.readFileSync(path.join(directory, "index.html"), "utf8");
const css = fs.readFileSync(path.join(directory, "wind-tunnel.css"), "utf8");
const app = fs.readFileSync(path.join(directory, "wind-tunnel.js"), "utf8");
const core = require("./wind-tunnel-core.js");

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function close(actual, expected, tolerance = 1e-11, message = "") {
  assert.ok(
    Math.abs(actual - expected) <= tolerance,
    message || `expected ${actual} to be within ${tolerance} of ${expected}`
  );
}

function hostileForecast(overrides = {}) {
  return core.forecastExperiment({
    initialState: [0.73, -0.41, 0.08, -0.03],
    duration: 0.35,
    sampleCount: 9,
    sensor: "tip-x",
    preparationRadius: 2e-4,
    noiseRadius: 3e-6,
    derivativeStep: 2e-5,
    forecastStep: 1 / 240,
    ...overrides
  });
}

function ensembleOptions(overrides = {}) {
  return {
    size: 7,
    seed: "hostile-reproduction-seed",
    uncertainty: { kind: "bounded", scale: 2e-4, distribution: "uniform-disk" },
    structured: { law: "off", alpha: 0, direction: "oig-weakest" },
    realism: {
      velocity: { kind: "off", scale: 0 },
      parameters: { kind: "off", scale: 0 },
      clock: { kind: "off", scale: 0 },
      sensor: { kind: "off", scale: 0 }
    },
    gates: { maxEnergyDrift: 1e-4, maxRefinementDiscrepancy: 1e-4, persistentExitSamples: 3 },
    retainTrajectories: true,
    ...overrides
  };
}

function type7(sorted, probability) {
  const position = (sorted.length - 1) * probability;
  const lower = Math.floor(position);
  const fraction = position - lower;
  return sorted[lower] + fraction * (sorted[Math.min(sorted.length - 1, lower + 1)] - sorted[lower]);
}

function populationCovariance(rows) {
  const width = rows[0].length;
  const means = Array.from({ length: width }, (_, column) =>
    rows.reduce((sum, row) => sum + row[column], 0) / rows.length
  );
  return Array.from({ length: width }, (_, row) => Array.from({ length: width }, (_, column) =>
    rows.reduce((sum, values) => sum + (values[row] - means[row]) * (values[column] - means[column]), 0) / rows.length
  ));
}

function ids(source) {
  return [...source.matchAll(/\bid=["']([^"']+)["']/g)].map(match => match[1]);
}

function attributesFor(id) {
  const escaped = id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = html.match(new RegExp(`<[^>]*\\bid=["']${escaped}["'][^>]*>`, "i"));
  assert.ok(match, `missing element #${id}`);
  return match[0];
}

function attribute(tag, name) {
  const match = tag.match(new RegExp(`\\b${name}=["']([^"']*)["']`, "i"));
  assert.ok(match, `missing ${name} on ${tag}`);
  return match[1];
}

function sectionText(id) {
  const escaped = id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = html.match(new RegExp(`<section[^>]*\\bid=["']${escaped}["'][^>]*>([\\s\\S]*?)</section>`, "i"));
  assert.ok(match, `missing section #${id}`);
  return match[1].replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}

test("ensemble and laboratory IDs are unique and complete", () => {
  const allIds = ids(html);
  assert.equal(new Set(allIds).size, allIds.length, "duplicate HTML ids make UI updates ambiguous");
  const present = new Set(allIds);
  const required = [
    "ensemble-controls", "ensemble-size", "ensemble-control-scope-note", "realism-level", "uncertainty-mode",
    "ensemble-seed", "perturbation-law", "law-amplitude", "perturbation-direction",
    "custom-direction-angle", "realism-endpoints", "realism-dial-help",
    "realism-preparation", "realism-preparation-law", "realism-velocity", "realism-velocity-law",
    "realism-parameter", "realism-parameter-law", "realism-sensor", "realism-sensor-law",
    "realism-clock", "realism-clock-law", "ensemble-results", "ensemble-coverage",
    "ensemble-coverage-interval", "persistent-exits", "survival-endpoint", "ensemble-survival-interval",
    "ensemble-outliers", "ensemble-outlier-members", "projected-reconvergence",
    "full-state-separation-at-reentry", "full-state-separation-note", "ensemble-unresolved",
    "response-refinement-discrepancy", "weakest-gain-shift", "strongest-gain-shift",
    "ensemble-survival-chart", "ensemble-spread-chart", "ensemble-display-policy", "ensemble-member-table",
    "background-laboratory", "laboratory-n-grid", "laboratory-t-grid",
    "laboratory-repeats", "laboratory-amplitudes", "run-laboratory",
    "cancel-laboratory", "laboratory-quick-preset", "laboratory-research-preset",
    "laboratory-job-count", "laboratory-progress",
    "laboratory-chart", "laboratory-table-body"
  ];
  for (const id of required) assert.ok(present.has(id), `missing responsive UI contract #${id}`);
});

test("realism dial names both semantic endpoints and discloses every serialized component law", () => {
  assert.match(html, /id="realism-endpoints"[\s\S]*0[\s\S]*mathematically ideal[\s\S]*100[\s\S]*naturally noisy/i);
  assert.match(html, /id="realism-level"[^>]*aria-describedby="realism-endpoints realism-dial-help"/i);
  for (const component of ["preparation", "velocity", "parameter", "sensor", "clock"]) {
    assert.match(html, new RegExp(`id=["']realism-${component}-law["']`));
  }
  assert.match(app, /component\.samplingLaw/);
  assert.match(app, /component\.support/);
  assert.match(app, /renderRealismLaws/);
  const declaration = core.buildEnsembleDeclaration(hostileForecast(), ensembleOptions({
    uncertainty: { kind: "bounded", scale: 2e-4 },
    realism: {
      velocity: { kind: "bounded", scale: 0.02 },
      parameters: { kind: "probabilistic", scale: 0.01 },
      clock: { kind: "bounded", scale: 0.005 },
      sensor: { kind: "probabilistic", scale: 0.002 }
    }
  }));
  for (const component of [declaration.uncertainty, ...Object.values(declaration.realism)]) {
    assert.equal(typeof component.samplingLaw, "string");
    assert.ok(component.samplingLaw.length > 8);
    assert.equal(typeof component.support, "string");
    assert.ok(component.support.length > 4);
  }
});

test("completed runs preserve their sealed sampling-law disclosure during control restoration", () => {
  const start = app.indexOf("async function runExperiment()");
  const end = app.indexOf("function startAnimation()", start);
  const run = app.slice(start, end);
  assert.match(run, /let disclosureDeclaration = null/);
  assert.match(run, /disclosureDeclaration = core\.buildEnsembleDeclaration\(state\.forecast, ensembleOptions\)/);
  assert.match(run, /finally[\s\S]*syncEnsembleOutputs\(disclosureDeclaration\)/);
  assert.doesNotMatch(run, /finally[\s\S]*syncEnsembleOutputs\(\);/);
});

test("N=1 frontend declaration ignores inactive ensemble controls and matches the held-out boundary path", () => {
  const start = app.indexOf("function readEnsembleOptions(");
  const end = app.indexOf("function samplingDisclosure(", start);
  assert.ok(start >= 0 && end > start, "readEnsembleOptions source not found");
  const source = app.slice(start, end);
  const input = value => ({ value: String(value) });
  const fakeEnsembleControls = {
    size: input(1), seed: input(999), mode: input("probabilistic"), law: input("geometric"),
    amplitude: input(2), direction: input("strongest"), customAngle: input(137)
  };
  const fakeControls = { preparation: input(0.0125) };
  let fakeRealism = { level: 1, preparation: 0.0125, velocity: 0.2, parameter: 0.02, sensor: 0.03, clock: 0.01 };
  const read = Function("currentRealism", "ensembleControls", "controls", "number",
    `${source}; return readEnsembleOptions;`
  )(() => fakeRealism,
  fakeEnsembleControls, fakeControls, element => Number(element.value));
  const options = read();
  assert.equal(options.size, 1);
  assert.equal(options.seed, "oig-wind-tunnel-n1-legacy-v1");
  assert.equal(options.legacySingleDirection, true);
  assert.deepEqual(options.uncertainty, { kind: "bounded", scale: 0.0125, distribution: "uniform-disk" });
  assert.equal(options.structured.law, "off");
  assert.equal(options.structured.alpha, 0);
  assert.ok(Object.values(options.realism).every(component => component.kind === "off" && component.scale === 0));
  const declaration = core.buildEnsembleDeclaration(hostileForecast({ preparationRadius: 0.0125 }), options);
  assert.equal(declaration.legacySingleDirection, true);
  assert.match(declaration.uncertainty.samplingLaw, /deterministic held-out boundary direction/i);
  assert.match(declaration.uncertainty.support, /\|\|angleOffset\|\|_2 = scaleRadians/);
  fakeEnsembleControls.seed.value = "123456789";
  fakeEnsembleControls.mode.value = "bounded";
  fakeEnsembleControls.law.value = "quadratic";
  fakeEnsembleControls.amplitude.value = "0.75";
  fakeEnsembleControls.direction.value = "custom";
  fakeEnsembleControls.customAngle.value = "-42";
  fakeRealism = { level: 0, preparation: 0, velocity: 0, parameter: 0, sensor: 0, clock: 0 };
  const sameN1 = read();
  assert.deepEqual(sameN1, options, "inactive N=1 controls changed the canonical run declaration");
  assert.equal(core.checksum({ ensembleDeclaration: sameN1 }), core.checksum({ ensembleDeclaration: options }));
  assert.match(html, /realism, distribution, seed, and structured-law controls activate only for N/i);
  assert.match(app, /ensembleActive = options\.size > 1/);
});

test("bounded and sampled-distribution semantics never imply a certified probability law", () => {
  assert.match(html, /Bounded mode:[\s\S]*not a probability guarantee/i);
  assert.match(html, /Seeded distribution sample/i);
  assert.match(html, /not certified probability or physical truth/i);
  assert.match(html, /synthetic, finite, seeded, and numerical/i);
  assert.match(html, /do not establish physical adequacy or certified probability laws/i);
  assert.match(app, /Wilson intervals remain descriptive sample intervals, not certified probability guarantees/i);
  assert.match(
    app,
    /Wilson(?:-style)? 95% descriptive interval[\s\S]*empirical, not certified probability/i
  );
  assert.match(
    app,
    /Interval withheld: bounded, ideal, or law-only design has no declared iid sampled component; finite count only/i
  );
  assert.doesNotMatch(
    sectionText("ensemble-results"),
    /(?:proves?|guarantees?|certifies?)\s+(?:the\s+)?(?:true\s+)?probability/i
  );
});

test("reconvergence is explicitly projected-output return, not state synchronization", () => {
  const ensemble = sectionText("ensemble-results");
  assert.match(ensemble, /Projected output reconvergence/i);
  assert.match(ensemble, /exited and later returned to the output tube/i);
  assert.doesNotMatch(ensemble, /state reconvergence|resynchroni[sz]|state synchronization/i);
});

test("N=1 keeps the legacy detailed outcome and forecast is sealed before any outcome", () => {
  assert.match(html, /N\s*=\s*1 preserves the detailed single-outcome wind tunnel/i);
  const runStart = app.indexOf("async function runExperiment()");
  const runEnd = app.indexOf("function startAnimation()", runStart);
  assert.ok(runStart >= 0 && runEnd > runStart, "runExperiment body not found");
  const run = app.slice(runStart, runEnd);
  assert.match(run, /if \(ensembleOptions\.size === 1\)/);
  assert.match(run, /core\.runIndependentOutcome\(state\.forecast\)/);
  const forecast = run.indexOf("core.forecastExperiment(options)");
  const seal = run.indexOf('seal.dataset.state = "sealed"');
  const singleOutcome = run.indexOf("core.runIndependentOutcome(state.forecast)");
  const ensembleOutcome = run.indexOf("invokeEnsemble(");
  assert.ok(forecast >= 0 && seal > forecast, "forecast was not computed then visibly sealed");
  assert.ok(singleOutcome > seal, "single outcome ran before the forecast seal");
  assert.ok(ensembleOutcome > seal, "ensemble outcome ran before the forecast seal");
});

test("a debounced or in-flight preview cannot overwrite a completed run", () => {
  const previewStart = app.indexOf("async function preparePreview(");
  const previewEnd = app.indexOf("async function runExperiment()", previewStart);
  const runEnd = app.indexOf("function startAnimation()", previewEnd);
  const scheduleStart = app.indexOf("function schedulePreview()", runEnd);
  const scheduleEnd = app.indexOf("function setControls(", scheduleStart);
  assert.ok(previewStart >= 0 && previewEnd > previewStart && runEnd > previewEnd && scheduleEnd > scheduleStart);
  const preview = app.slice(previewStart, previewEnd);
  const run = app.slice(previewEnd, runEnd);
  const schedule = app.slice(scheduleStart, scheduleEnd);
  assert.match(run, /clearTimeout\(state\.previewTimer\)/);
  assert.match(run, /state\.previewGeneration \+= 1/);
  assert.match(preview, /generation !== state\.previewGeneration/g);
  assert.match(preview, /await nextPaint\(\);[\s\S]*generation !== state\.previewGeneration/);
  assert.match(schedule, /const generation = \+\+state\.previewGeneration/);
  assert.match(schedule, /preparePreview\(generation\)/);
});

test("worker requests carry unique channel tokens and stale messages fail closed", () => {
  assert.match(app, /nextRequestToken/);
  assert.match(app, /`experiment:\$\{\+\+state\.nextRequestToken\}`/);
  assert.match(app, /`laboratory:\$\{\+\+state\.nextRequestToken\}`/);
  assert.match(app, /workerRequests\.get\(message\.runId\)/);
  assert.match(app, /if \(!request\) return;[^\n]*Stale or explicitly cancelled work/s);
  assert.match(app, /if \(message\.channel !== request\.channel\) return;/);
  assert.match(app, /if \(runId !== state\.activeRunId\) return;/);
  assert.match(app, /if \(runId !== state\.laboratoryRunId\) return;/);
  assert.match(app, /workerRequests\.delete\(runId\)/);
});

test("worker cancellation is not represented by a flag alone", () => {
  assert.match(app, /postMessage\(\{ type: "cancel", runId \}\)/);
  const coreSource = fs.readFileSync(path.join(directory, "wind-tunnel-core.js"), "utf8");
  const interruptibleCore = /await\s+(?:new\s+Promise|yieldToEventLoop|nextChunk)/.test(coreSource)
    && /isCancelled\s*\(\)/.test(coreSource);
  const terminateAndRecreate = /\.terminate\s*\(\)/.test(app)
    && /state\.worker\s*=\s*null/.test(app);
  assert.ok(
    interruptibleCore || terminateAndRecreate,
    "a synchronous member loop cannot receive cancel; chunk/yield or terminate/recreate is required"
  );
  assert.match(app, /core\.runEnsembleAsync\(forecast, declaration/);
  assert.match(app, /core\.runLaboratoryStudyAsync\(spec/);
});

test("interactive and laboratory controls expose the declared scale limits", () => {
  const ensemble = attributesFor("ensemble-size");
  assert.match(ensemble, /\bmin=["']1["']/);
  assert.match(ensemble, /\bmax=["']50["']/);
  assert.match(ensemble, /\bvalue=["']1["']/);
  const repeats = attributesFor("laboratory-repeats");
  assert.match(repeats, /\bmin=["']1["']/);
  assert.match(repeats, /\bmax=["']20["']/);
  assert.match(html, /N\s*=\s*50…1000 and T\s*=\s*1…30/);
  const listLength = id => attribute(attributesFor(id), "value").split(",").filter(value => value.trim()).length;
  const checkedLaws = [...html.matchAll(/<input\b[^>]*data-laboratory-law[^>]*>/gi)]
    .filter(match => /\bchecked\b/i.test(match[0])).length;
  const expectedJobs = listLength("laboratory-n-grid")
    * listLength("laboratory-t-grid")
    * listLength("laboratory-amplitudes")
    * Number(attribute(repeats, "value"))
    * checkedLaws;
  const count = html.match(/<output[^>]*id=["']laboratory-job-count["'][^>]*>([^<]*)<\/output>/i);
  assert.ok(count, "missing initial laboratory job count");
  assert.match(count[1], new RegExp(`\\b${expectedJobs} jobs\\b`));
});

test("laboratory grids reject invalid, empty, and nonfinite tokens instead of filtering them", () => {
  const start = app.indexOf("function parseGridInput(");
  const end = app.indexOf("function readLaboratoryDesign()", start);
  assert.ok(start >= 0 && end > start, "parseGridInput body not found");
  const source = app.slice(start, end);
  assert.doesNotMatch(source, /filter\(Number\.isFinite\)/);
  let current = "50, abc";
  const parse = Function("optional", `${source}; return parseGridInput;`)(() => ({ value: current }));
  assert.throws(() => parse("laboratory-n-grid", 50, 1000, true), /invalid numeric token/i);
  current = "50, ";
  assert.throws(() => parse("laboratory-n-grid", 50, 1000, true), /empty or invalid numeric token/i);
  current = "50, 1e999";
  assert.throws(() => parse("laboratory-n-grid", 50, 1000, true), /nonfinite number/i);
  current = "50, 200, 50";
  assert.deepEqual(parse("laboratory-n-grid", 50, 1000, true), [50, 200]);
});

test("certified provenance requires the exact six-source conjunction and strict bounds round down", () => {
  const start = app.indexOf("function directedLowerDecimal(");
  const end = app.indexOf("function setText(", start);
  assert.ok(start >= 0 && end > start, "certificate guard helpers not found");
  const source = app.slice(start, end);
  const helpers = Function(`${source}; return { directedLowerDecimal, CERTIFIED_PROVENANCE_KEYS, completeVerifiedProvenance };`)();
  assert.equal(helpers.directedLowerDecimal(0.07837316225610753, 7), "0.0783731");
  assert.equal(helpers.directedLowerDecimal(0.0180269, 7), "0.0180269");
  const complete = Object.fromEntries(helpers.CERTIFIED_PROVENANCE_KEYS.map(key => [key, { verified: true }]));
  assert.equal(helpers.completeVerifiedProvenance(complete), true);
  const missing = { ...complete }; delete missing.variational_atlas;
  assert.equal(helpers.completeVerifiedProvenance(missing), false);
  assert.equal(helpers.completeVerifiedProvenance({ ...complete, unexpected: { verified: true } }), false);
  assert.equal(helpers.completeVerifiedProvenance({ ...complete, two_row_floor: { verified: false } }), false);
});

test("mixed gate outcomes cannot promote the refined tier as passed", () => {
  const runStart = app.indexOf("async function runExperiment()");
  const runEnd = app.indexOf("function startAnimation()", runStart);
  const run = app.slice(runStart, runEnd);
  assert.match(run, /resolvedCount === state\.ensembleDeclaration\.size/);
  assert.match(run, /state\.ensembleView\.unresolved === 0/);
  assert.match(run, /&& refinementPassed/);
  assert.match(run, /setTier\("refined-tier", allResolved \? "passed" : "unresolved"/);
  assert.match(run, /Finite ensemble remains unresolved/);
  assert.doesNotMatch(run, /setTier\("refined-tier", "passed", "adaptive integration/);
  assert.match(run, /state\.outcome\.evidenceGates\?\.refinedEvidencePassed === true/);
  assert.match(run, /baseline, response-refinement, and\/or energy gate failed/);
  assert.match(app, /gates\.energyTolerance/);
  assert.match(app, /gates\.energyPassed === true/);
  assert.match(app, /Response h \/ h⁄2 refinement/);
  assert.match(app, /weakestGainRelativeShift/);
  assert.match(app, /strongestGainRelativeShift/);
});

test("N=1 export contains frozen forecast and independently integrated outcome arrays", () => {
  const start = app.indexOf('optional("export-ledger")?.addEventListener');
  const end = app.indexOf('for (const id of ["laboratory-n-grid"', start);
  const source = app.slice(start, end);
  for (const field of [
    "times", "baseline", "baselineSensor", "gradients", "tubeRadius",
    "responseRefinement", "actual", "actualSensor", "independentBaseline",
    "refinedBaselineSensor", "evidenceGates"
  ]) assert.match(source, new RegExp(`\\b${field}:`), `N=1 export omits ${field}`);
  assert.match(source, /forecastFrozenBeforeOutcome: true/);
  assert.match(source, /certifiedArtifactAppliedToThisSliderTrial: false/);
});

test("post-outcome table and adaptive representatives expose authoritative member diagnostics", () => {
  const ensemble = sectionText("ensemble-results");
  assert.match(ensemble, /Tube coverage/i);
  assert.match(ensemble, /First persistent exit/i);
  assert.match(ensemble, /Endpoint classification/i);
  assert.match(ensemble, /Full-state separation at output re-entry/i);
  assert.match(ensemble, /not attraction or synchronization/i);
  assert.match(app, /audit\?\.endpointClassification/);
  assert.match(app, /audit\?\.persistentExitTime/);
  assert.match(app, /summary\.terminalOutliers/);
  assert.match(app, /terminalOutliers\.memberIds\.slice\(\)/);
  assert.match(app, /representativeIndices\(count, representatives, pinnedIndices\)/);
  assert.match(app, /outlierIds\.has\(member\.id\)/);
  assert.match(app, /fullStateAtOutputReentry/);
});

test("ensemble and laboratory layouts have tablet and narrow-phone fallbacks", () => {
  assert.match(css, /@media \(max-width: 900px\)[\s\S]*\.ensemble-plot-grid[^}]*grid-template-columns:\s*1fr/);
  assert.match(css, /@media \(max-width: 700px\)[\s\S]*\.ensemble-primary-controls[^}]*grid-template-columns:\s*1fr/);
  assert.match(css, /@media \(max-width: 700px\)[\s\S]*\.laboratory-controls[^}]*grid-template-columns:\s*1fr/);
  assert.match(css, /@media \(max-width: 440px\)[\s\S]*\.ensemble-metric-grid[^}]*grid-template-columns:\s*1fr/);
});

test("browser assets remain repository-local", () => {
  const references = [...html.matchAll(/\b(?:src|href)=["']([^"']+)["']/g)].map(match => match[1]);
  for (const reference of references) {
    if (reference.startsWith("#") || reference.startsWith("data:")) continue;
    assert.doesNotMatch(reference, /^(?:[a-z][a-z0-9+.-]*:)?\/\//i);
    const target = path.resolve(directory, reference.split(/[?#]/, 1)[0]);
    assert.ok(target.startsWith(path.resolve(directory, "..", "..") + path.sep));
    assert.ok(fs.existsSync(target), `missing local asset ${reference}`);
  }
  const workerPath = path.join(directory, "ensemble-worker.js");
  assert.ok(fs.existsSync(workerPath), "missing dedicated local computation worker");
  const worker = fs.readFileSync(workerPath, "utf8");
  const dependencySource = `${html}\n${css}\n${app}\n${worker}`.replaceAll("http://www.w3.org/2000/svg", "");
  assert.doesNotMatch(dependencySource, /(?:https?:)?\/\/[^\s'"<>)]+/i);
  assert.match(app, /new Worker\(new URL\("ensemble-worker\.js", coreUrl\)\)/);
  assert.match(worker, /importScripts\(["']\.\/wind-tunnel-core\.js["']\)/);
  assert.doesNotMatch(worker, /(?:fetch|XMLHttpRequest|WebSocket|EventSource|navigator\.sendBeacon)\s*\(/);
});

test("seed streams and member draws are deterministic, indexed, and chunk-order invariant", () => {
  const first = core.createSeededPRNG("repeatable-seed");
  const second = core.createSeededPRNG("repeatable-seed");
  const sequence = Array.from({ length: 64 }, () => first());
  assert.deepEqual(sequence, Array.from({ length: 64 }, () => second()));
  assert.ok(sequence.every(value => value >= 0 && value < 1));
  assert.equal(core.deriveSeed("root", { b: 2, a: 1 }), core.deriveSeed("root", { a: 1, b: 2 }));
  assert.notEqual(core.deriveSeed("root", "member", 2), core.deriveSeed("root", "member", 3));

  const forecast = hostileForecast();
  const oneShot = core.buildEnsembleDeclaration(forecast, ensembleOptions({ size: 17 }));
  const restarted = core.buildEnsembleDeclaration(forecast, ensembleOptions({ size: 17 }));
  assert.equal(core.stableSerialize(oneShot), core.stableSerialize(restarted));

  const oneBatch = new Map(oneShot.members.map(member => [
    member.id,
    core.stableSerialize(core.generateMemberDraws(forecast, oneShot, member))
  ]));
  const splitAndReordered = [
    oneShot.members.slice(11),
    oneShot.members.slice(0, 4),
    oneShot.members.slice(4, 11)
  ].flat().reverse();
  for (const member of splitAndReordered) {
    assert.equal(
      core.stableSerialize(core.generateMemberDraws(forecast, oneShot, member)),
      oneBatch.get(member.id),
      `member ${member.id} changed when generated after a split/restart/reorder`
    );
  }
  assert.equal(
    core.stableSerialize(core.runEnsemble(forecast, oneShot)),
    core.stableSerialize(core.runEnsemble(forecast, restarted)),
    "rerunning the same frozen declaration was not bit-for-bit deterministic"
  );
});

test("all six structured laws obey their declared formulas, parity, and coordinate grid", () => {
  const expectedFormula = {
    off: "f(s)=0",
    linear: "f(s)=s",
    quadratic: "f(s)=2s^2-1",
    sinusoidal: "f(s)=sin(pi s)",
    radial: "f(s)=2|s|-1",
    geometric: "f(s)=sign(s) expm1(2|s|)/expm1(2)"
  };
  const odd = new Set(["linear", "sinusoidal", "geometric"]);
  const even = new Set(["off", "quadratic", "radial"]);
  for (const law of core.ENSEMBLE_LAWS) {
    for (const s of [-1, -0.75, -0.25, 0, 0.25, 0.75, 1]) {
      const value = core.structuredLawValue(law, s, 2);
      const reflected = core.structuredLawValue(law, -s, 2);
      close(reflected, odd.has(law) ? -value : value, 3e-15, `${law} has wrong parity at ${s}`);
      assert.ok(Number.isFinite(value));
      assert.ok(Math.abs(value) <= 1 + 1e-15, `${law} left its normalized [-1,1] range`);
    }
    assert.ok(odd.has(law) || even.has(law));
  }

  const forecast = hostileForecast();
  for (const law of core.ENSEMBLE_LAWS) {
    const declaration = core.buildEnsembleDeclaration(forecast, ensembleOptions({
      size: 9,
      structured: { law, alpha: 0.13, direction: "custom", customDirection: [3, 4], geometricRate: 2 }
    }));
    assert.equal(declaration.structured.lawFormula, expectedFormula[law]);
    declaration.members.forEach((member, index) => {
      const expectedS = -1 + 2 * index / 8;
      const expectedF = core.structuredLawValue(law, expectedS, 2);
      close(member.s, expectedS, 1e-15);
      close(member.f, expectedF, 1e-15);
      close(member.structuredOffset[0], 0.13 * expectedF * 3 / 5, 1e-15);
      close(member.structuredOffset[1], 0.13 * expectedF * 4 / 5, 1e-15);
    });
  }
});

test("bounded draws satisfy hard supports while sampled declarations do not masquerade as bounds", () => {
  const forecast = hostileForecast();
  const bounded = core.buildEnsembleDeclaration(forecast, ensembleOptions({
    size: 200,
    realism: {
      velocity: { kind: "bounded", scale: 0.03 },
      parameters: { kind: "bounded", scale: 0.04 },
      clock: { kind: "bounded", scale: 0.02 },
      sensor: { kind: "bounded", scale: 0.005 }
    }
  }));
  for (const member of bounded.members) {
    const draws = core.generateMemberDraws(forecast, bounded, member);
    assert.ok(Math.hypot(...draws.angleOffset) <= bounded.uncertainty.scaleRadians + 1e-15);
    assert.ok(Math.hypot(...draws.velocityOffset) <= bounded.realism.velocity.scale + 1e-15);
    assert.ok(draws.parameterLogOffsets.every(value => Math.abs(value) <= bounded.realism.parameters.scale + 1e-15));
    assert.ok(Math.abs(draws.clockFraction) <= bounded.realism.clock.scale + 1e-15);
    assert.ok(draws.sensorNoise.every(value => Math.abs(value) <= bounded.realism.sensor.scale + 1e-15));
  }
  assert.match(bounded.uncertainty.interpretation, /norm at most/i);

  const sampled = core.buildEnsembleDeclaration(forecast, ensembleOptions({
    size: 200,
    uncertainty: { kind: "probabilistic", sigma: 2e-4, distribution: "normal" }
  }));
  assert.match(sampled.uncertainty.interpretation, /normal draws with standard deviation/i);
  assert.doesNotMatch(sampled.uncertainty.interpretation, /at most|hard bound|guarantee/i);
  assert.ok(sampled.members.some(member => {
    const draw = core.generateMemberDraws(forecast, sampled, member);
    return Math.hypot(...draw.angleOffset) > sampled.uncertainty.scaleRadians;
  }), "normal samples suspiciously behaved like a hard radius bound");
});

test("N=1 reproduces the legacy deterministic launch without changing the frozen forecast", () => {
  const forecast = hostileForecast({ duration: 0.5, sampleCount: 13 });
  const forecastBefore = core.stableSerialize(forecast);
  const options = ensembleOptions({ size: 1, seed: "n1-compatibility", legacySingleDirection: true });
  const declaration = core.buildEnsembleDeclaration(forecast, options);
  const result = core.runEnsemble(forecast, declaration);
  assert.equal(core.verifyEnsembleResult(result).valid, true);
  const legacy = core.runIndependentOutcome(forecast);
  assert.equal(core.stableSerialize(forecast), forecastBefore, "outcome mutated the precommitted forecast");
  assert.equal(result.declaration.legacySingleDirection, true);
  assert.deepEqual(result.members[0].initialState, legacy.actual.states[0]);
  result.members[0].draws.angleXi.forEach((value, axis) => close(value, legacy.direction[axis], 3e-16));
  assert.deepEqual(result.members[0].actualSensorSeries, legacy.actualSensor);
  close(result.members[0].audit.coverage, legacy.coverage, 1e-15);
  close(result.members[0].audit.amplification.actual, legacy.actualAmplification, 1e-15);
  close(result.members[0].audit.amplification.predictedInitialAngleLinearization, legacy.predictedAmplification, 1e-15);
});

test("summary coverage, survival, persistent exits, percentiles, and covariance reconstruct independently", () => {
  const forecast = hostileForecast({ duration: 0.6, sampleCount: 13, noiseRadius: 1e-7 });
  const declaration = core.buildEnsembleDeclaration(forecast, ensembleOptions({
    size: 11,
    uncertainty: { kind: "probabilistic", sigma: 0.015, distribution: "normal" },
    structured: { law: "off", alpha: 0, direction: "oig-weakest" },
    gates: { maxEnergyDrift: 1e-3, maxRefinementDiscrepancy: 1e-3, persistentExitSamples: 3 }
  }));
  const result = core.runEnsemble(forecast, declaration);
  const resolved = result.members.filter(member => member.audit.status === "resolved");
  assert.equal(resolved.length, declaration.size, "hostile reconstruction fixture unexpectedly unresolved");
  const sampleCount = forecast.times.length;
  for (let index = 0; index < sampleCount; index += 1) {
    const inside = resolved.filter(member => member.audit.inside[index]).length;
    const survived = resolved.filter(member => member.audit.firstExitIndex === null || member.audit.firstExitIndex > index).length;
    close(result.summary.timewise.coverage[index], inside / resolved.length, 1e-15);
    close(result.summary.timewise.survival[index], survived / resolved.length, 1e-15);
    const ordered = resolved.map(member => member.actualSensorSeries[index]).sort((a, b) => a - b);
    close(result.summary.timewise.actual.p05[index], type7(ordered, 0.05), 1e-15);
    close(result.summary.timewise.actual.p50[index], type7(ordered, 0.5), 1e-15);
    close(result.summary.timewise.actual.p95[index], type7(ordered, 0.95), 1e-15);
  }
  const insideSamples = resolved.reduce((sum, member) => sum + member.audit.inside.filter(Boolean).length, 0);
  close(result.summary.coverage.sampleFraction, insideSamples / (resolved.length * sampleCount), 1e-15);
  close(
    result.summary.coverage.wholeMemberFraction,
    resolved.filter(member => member.audit.firstExitIndex === null).length / resolved.length,
    1e-15
  );
  close(
    result.summary.exits.persistentExitFraction,
    resolved.filter(member => member.audit.persistentExitIndex !== null).length / resolved.length,
    1e-15
  );
  close(
    result.summary.projectedReconvergence.withinDeclaredReadoutRadiusFraction,
    resolved.filter(member => member.audit.projectedReconvergence.withinDeclaredReadoutRadius).length / resolved.length,
    1e-15
  );
  for (const member of resolved) {
    const inside = member.audit.inside;
    let expected = null;
    for (let start = 0; start <= inside.length - declaration.gates.persistentExitSamples; start += 1) {
      if (inside.slice(start, start + declaration.gates.persistentExitSamples).every(value => !value)) {
        expected = start;
        break;
      }
    }
    assert.equal(member.audit.persistentExitIndex, expected);
    const firstExit = inside.findIndex(value => !value);
    const exitedThenReturned = firstExit >= 0 && inside.slice(firstExit + 1).some(Boolean);
    assert.equal(
      member.audit.projectedReconvergence.withinDeclaredReadoutRadius,
      exitedThenReturned,
      "projected reconvergence must mean an output-tube exit followed by sampled re-entry"
    );
  }
  const initialCovariance = populationCovariance(resolved.map(member => member.initialState.slice(0, 2)));
  const terminalCovariance = populationCovariance(resolved.map(member => member.trajectory.states.at(-1)));
  assert.deepEqual(result.summary.covariance.initialAngles, initialCovariance);
  assert.deepEqual(result.summary.covariance.terminalState, terminalCovariance);
  assert.match(result.summary.covariance.denominator, /population denominator N/i);
  assert.match(result.summary.projectedReconvergence.interpretation, /sensor projection only/i);
  assert.doesNotMatch(result.summary.projectedReconvergence.interpretation, /state-space convergence claim/i);
});

test("descriptive interval is withheld without a nonzero iid sampled component", () => {
  const forecast = hostileForecast();
  const zeroSample = core.runEnsemble(forecast, ensembleOptions({
    size: 5,
    uncertainty: { kind: "probabilistic", sigma: 0, distribution: "normal" }
  }));
  assert.equal(zeroSample.summary.coverage.wilson95, null);
  assert.match(zeroSample.summary.coverage.intervalInterpretation, /no probability interval/i);

  const bounded = core.runEnsemble(forecast, ensembleOptions({ size: 5 }));
  assert.equal(bounded.summary.coverage.wilson95, null);
  const structured = core.runEnsemble(forecast, ensembleOptions({
    size: 5,
    uncertainty: { kind: "probabilistic", sigma: 2e-4, distribution: "normal" },
    structured: { law: "linear", alpha: 0.01, direction: "oig-weakest" }
  }));
  assert.equal(structured.summary.coverage.wilson95, null);
});

test("any displayed Wilson interval names and counts the same Bernoulli event", () => {
  assert.match(app, /summary\.coverage\?\.wilson95/);
  const coreSource = fs.readFileSync(path.join(directory, "wind-tunnel-core.js"), "utf8");
  const eventMetadata = /wilson95Event|intervalEvent|successDefinition/.test(coreSource);
  const terminalInterval = /wilsonInterval\(terminalMembers|wilsonInterval\(terminalSuccess/.test(coreSource);
  const uiNamesWholeHorizon = /Whole-horizon|never-exited[^\n]{0,160}Wilson/i.test(html + "\n" + app);
  assert.ok(
    eventMetadata || terminalInterval || uiNamesWholeHorizon,
    "Wilson interval is computed from whole-horizon survival but displayed as terminal pointwise coverage"
  );
});

test("tampered declarations and hidden-draw evidence fail closed", () => {
  const forecast = hostileForecast();
  const declaration = core.buildEnsembleDeclaration(forecast, ensembleOptions({ size: 3 }));
  for (const mutate of [
    value => { value.declarationId = "00000000"; },
    value => { value.members[1].structuredOffset[0] += 1e-4; },
    value => { value.members[1].memberSeed = "ffffffff"; },
    value => { value.members[1].hiddenDrawCommitment = "ffffffff"; },
    value => { value.gates.persistentExitSamples = 0; }
  ]) {
    const tampered = clone(declaration);
    mutate(tampered);
    assert.throws(() => core.runEnsemble(forecast, tampered), /commitment|noncanonical|invalid/i);
  }
  for (const mutate of [
    value => { value.q0[0] += 0.25; },
    value => { value.structured.lawFormula = "f(s)=a misleading formula"; }
  ]) {
    const selfRecommitted = clone(declaration);
    mutate(selfRecommitted);
    delete selfRecommitted.declarationId;
    selfRecommitted.declarationId = core.checksum(core.stableSerialize(selfRecommitted));
    assert.throws(
      () => core.runEnsemble(forecast, selfRecommitted),
      /noncanonical|forecast|q0|formula|evidence|declaration/i,
      "a self-checksum must not authorize false scientific scope or semantics"
    );
  }
  const result = core.runEnsemble(forecast, declaration);
  assert.equal(result.resultId, core.checksum(core.stableSerialize({
    schemaVersion: result.schemaVersion,
    declaration: result.declaration,
    comparisonBaseline: result.comparisonBaseline,
    members: result.members,
    summary: result.summary
  })), "resultId does not commit the complete public scientific payload");
  const alteredReadout = clone(result);
  alteredReadout.members[0].actualSensorSeries[0] += 0.5;
  assert.notEqual(
    result.resultId,
    core.checksum(core.stableSerialize({
      schemaVersion: alteredReadout.schemaVersion,
      declaration: alteredReadout.declaration,
      comparisonBaseline: alteredReadout.comparisonBaseline,
      members: alteredReadout.members,
      summary: alteredReadout.summary
    })),
    "a changed retained readout did not invalidate the scientific result commitment"
  );
  assert.throws(() => core.verifyEnsembleResult(alteredReadout), /resultId|payload|integrity|reconstruct/i);
  assert.match(result.summary.interpretation.evidence, /no outward enclosure or exact-flow certificate/i);
  assert.doesNotMatch(core.stableSerialize(result.summary), /certified probability|physical truth established/i);
});

test("async ensemble cancellation yields to the event loop and promotes no partial result", async () => {
  const forecast = hostileForecast();
  let completed = 0;
  const promise = core.runEnsembleAsync(forecast, ensembleOptions({ size: 12 }), {
    yieldEvery: 1,
    onProgress(progress) { completed = progress.completed; },
    isCancelled() { return completed >= 2; }
  });
  await assert.rejects(promise, error => error?.code === "OIG_CANCELLED");
  assert.equal(completed, 2);
});

test("Wilson bounds reconstruct from the explicitly named whole-horizon survival event", () => {
  const forecast = hostileForecast({ duration: 0.55, sampleCount: 12, noiseRadius: 2e-7 });
  const result = core.runEnsemble(forecast, ensembleOptions({
    size: 23,
    uncertainty: { kind: "probabilistic", sigma: 0.012, distribution: "normal" },
    gates: { maxEnergyDrift: 1e-3, maxRefinementDiscrepancy: 1e-3, persistentExitSamples: 3 }
  }));
  const interval = result.summary.coverage.wilson95;
  assert.ok(interval, "eligible iid sampled ensemble withheld its descriptive interval");
  const resolved = result.members.filter(member => member.audit.status === "resolved");
  const successes = resolved.filter(member => member.audit.firstExitIndex === null).length;
  assert.equal(interval.event, "whole-horizon member survival (no sampled tube exit)");
  assert.equal(interval.successes, successes);
  assert.equal(interval.trials, resolved.length);
  const z = 1.959963984540054;
  const probability = successes / resolved.length;
  const denominator = 1 + z * z / resolved.length;
  const centre = (probability + z * z / (2 * resolved.length)) / denominator;
  const radius = z * Math.sqrt(
    probability * (1 - probability) / resolved.length + z * z / (4 * resolved.length ** 2)
  ) / denominator;
  close(interval.lower, Math.max(0, centre - radius), 2e-15);
  close(interval.upper, Math.min(1, centre + radius), 2e-15);
});

test("laboratory Cartesian grids, repeat seeds, aggregates, and progress are exact and reproducible", () => {
  const forecast = hostileForecast({ duration: 0.4, sampleCount: 9 });
  const spec = {
    forecast,
    ensembleOptions: ensembleOptions({ size: 2, retainTrajectories: false }),
    sizes: [2, 3],
    horizons: [0.2, 0.4],
    laws: ["off", "linear"],
    amplitudes: [0, 0.01],
    repeats: 2,
    baseSeed: "laboratory-hostile-seed",
    observationStep: 0.1,
    retainTrajectories: false
  };
  const progress = [];
  const result = core.runLaboratoryStudy(spec, { onProgress(update) { progress.push(update); } });
  assert.equal(core.verifyLaboratoryResult(result).valid, true);
  const expectedCells = spec.sizes.length * spec.horizons.length * spec.laws.length * spec.amplitudes.length;
  const expectedRuns = expectedCells * spec.repeats;
  assert.deepEqual(result.grid, {
    sizes: spec.sizes,
    horizons: spec.horizons,
    laws: spec.laws,
    amplitudes: spec.amplitudes,
    repeats: spec.repeats
  });
  assert.equal(result.cells.length, expectedCells);
  assert.equal(progress.length, expectedRuns);
  progress.forEach((update, index) => {
    assert.equal(update.completed, index + 1);
    assert.equal(update.total, expectedRuns);
    close(update.fraction, (index + 1) / expectedRuns, 1e-15);
  });
  assert.equal(progress.at(-1).fraction, 1);
  assert.deepEqual(result.sampling.realized, [
    { horizon: 0.2, sampleCount: 3, observationStep: 0.1 },
    { horizon: 0.4, sampleCount: 5, observationStep: 0.1 }
  ]);

  const runIds = new Set();
  for (const cell of result.cells) {
    assert.equal(cell.runs.length, spec.repeats);
    assert.equal(cell.aggregate.sampleCoverage.count, spec.repeats);
    cell.runs.forEach((run, repeat) => {
      const expectedSeed = core.deriveSeed(
        spec.baseSeed, "laboratory", cell.size, cell.horizon, cell.law, cell.amplitude, repeat
      );
      assert.equal(run.declaration.masterSeed, expectedSeed);
      assert.ok(!runIds.has(run.resultId), "repeat/cell resultId collision");
      runIds.add(run.resultId);
      assert.equal(run.members.some(member => "trajectory" in member), false);
    });
  }

  const reordered = core.runLaboratoryStudy({
    ...spec,
    sizes: spec.sizes.slice().reverse(),
    horizons: spec.horizons.slice().reverse(),
    laws: spec.laws.slice().reverse(),
    amplitudes: spec.amplitudes.slice().reverse()
  });
  const cellMap = value => new Map(value.cells.map(cell => [
    core.stableSerialize([cell.size, cell.horizon, cell.law, cell.amplitude]),
    cell.runs.map(run => run.resultId)
  ]));
  const expected = cellMap(result);
  for (const [key, ids] of cellMap(reordered)) assert.deepEqual(ids, expected.get(key));
  const alteredStudy = clone(result);
  alteredStudy.cells[0].aggregate.sampleCoverage.p50 += 0.01;
  assert.throws(() => core.verifyLaboratoryResult(alteredStudy), /studyId|payload|integrity|aggregate/i);
  for (const mutate of [
    value => { value.cells[1] = clone(value.cells[0]); },
    value => { value.baseSeed = "false-base-seed"; },
    value => { value.cells[0].aggregate.sampleCoverage.p50 += 0.01; }
  ]) {
    const selfRecommitted = clone(result);
    mutate(selfRecommitted);
    delete selfRecommitted.studyId;
    selfRecommitted.studyId = core.checksum(core.stableSerialize(selfRecommitted));
    assert.throws(
      () => core.verifyLaboratoryResult(selfRecommitted),
      /Cartesian|coordinate|seed|aggregate|integrity|mismatch/i,
      "a self-checksum must not authorize an incomplete or statistically false laboratory grid"
    );
  }
});

test("laboratory validation rejects malformed N, T, repeat, law, and amplitude grids", () => {
  const forecast = hostileForecast();
  const base = {
    forecast,
    ensembleOptions: ensembleOptions({ size: 2 }),
    sizes: [2], horizons: [0.2], laws: ["off"], amplitudes: [0], repeats: 1,
    observationStep: 0.1
  };
  for (const invalid of [
    { sizes: [] }, { sizes: [0] }, { sizes: [5001] }, { sizes: [2.5] },
    { horizons: [] }, { horizons: [0] }, { horizons: [121] },
    { repeats: 0 }, { repeats: 101 }, { repeats: 1.5 },
    { laws: [] }, { laws: ["invented"] },
    { amplitudes: [] }, { amplitudes: [-1] }, { observationStep: 0 }
  ]) {
    assert.throws(() => core.runLaboratoryStudy({ ...base, ...invalid }), /laboratory|observationStep/i);
  }
});

test("async laboratory cancellation stops before promotion and reports bounded monotone progress", async () => {
  const forecast = hostileForecast();
  let completed = 0;
  const promise = core.runLaboratoryStudyAsync({
    forecast,
    ensembleOptions: ensembleOptions({ size: 3, retainTrajectories: false }),
    sizes: [3], horizons: [0.2, 0.3], laws: ["off"], amplitudes: [0], repeats: 3,
    baseSeed: "cancel-lab", observationStep: 0.1
  }, {
    yieldEvery: 1,
    onProgress(update) { completed = update.completed; },
    isCancelled() { return completed >= 1; }
  });
  await assert.rejects(promise, error => error?.code === "OIG_CANCELLED");
  assert.equal(completed, 1);
});

test("research-scale performance gates cover N=50,T=30 and N=1000 without retaining trajectories", () => {
  const startLong = performance.now();
  const longForecast = hostileForecast({
    initialState: [0.4, -0.2, 0, 0], duration: 30, sampleCount: 61, forecastStep: 0.05
  });
  const longResult = core.runEnsemble(longForecast, ensembleOptions({
    size: 50,
    retainTrajectories: false,
    solverOptions: { rtol: 1e-6, atol: 1e-8, initialStep: 0.02, maxStep: 0.1 },
    gates: { maxEnergyDrift: 1, maxRefinementDiscrepancy: 1, persistentExitSamples: 3 }
  }));
  const longElapsed = performance.now() - startLong;
  assert.equal(longResult.members.length, 50);
  assert.equal(longResult.members.some(member => "trajectory" in member), false);
  assert.ok(longElapsed < 15_000, `N=50,T=30 exceeded 15 s (${longElapsed.toFixed(1)} ms)`);

  const startWide = performance.now();
  const wideForecast = hostileForecast({ duration: 1, sampleCount: 5, forecastStep: 0.05 });
  const wideResult = core.runEnsemble(wideForecast, ensembleOptions({
    size: 1000,
    retainTrajectories: false,
    solverOptions: { rtol: 1e-6, atol: 1e-8, initialStep: 0.02, maxStep: 0.1 },
    gates: { maxEnergyDrift: 1, maxRefinementDiscrepancy: 1, persistentExitSamples: 3 }
  }));
  const wideElapsed = performance.now() - startWide;
  assert.equal(wideResult.members.length, 1000);
  assert.equal(wideResult.members.some(member => "trajectory" in member), false);
  assert.ok(wideElapsed < 15_000, `N=1000 exceeded 15 s (${wideElapsed.toFixed(1)} ms)`);
});
