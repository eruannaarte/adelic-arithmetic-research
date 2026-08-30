(function () {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";
  var Base = window.GlobalGeometryCore;
  var G2 = window.GlobalGeometryII;
  var Claims = window.GlobalGeometryIIClaims;
  var Ensembles = window.GlobalGeometryIIEnsembles;
  var Atlas = window.GlobalGeometryIIAtlas;
  var Inverse = window.GlobalGeometryIIInverse;
  var Sheet = window.GlobalGeometryIISheet;
  var modules = [Base, G2, Claims, Ensembles, Atlas, Inverse, Sheet];
  if (modules.some(function (module) { return !module; })) {
    document.body.setAttribute("data-ggii-load-error", "true");
    throw new Error("Global Geometry II laboratory modules did not all load.");
  }

  var familyLabels = {
    "square-alternating": "Alternating square diagonals",
    "triangular-clipped": "Clipped triangular lattice",
    "cell-center-fan": "Cell-center fan",
    "square-hashed-diagonal": "Seeded hashed diagonals"
  };
  var inverseLabels = {
    "tetra-uniform-pass": "Tetrahedral sphere · admissible Model CP target",
    "triangle-valid-pass": "Triangular disk · valid direct edge metric",
    "annulus-valid-pass": "Five-sector annulus · valid direct edge metric",
    "torus-valid-pass": "Periodic 3 × 3 torus · valid direct edge metric",
    "tetra-subset-reject": "Tetrahedral sphere · Chow–Luo subset obstruction",
    "sphere-zero-reject": "Sphere · Gauss–Bonnet total obstruction",
    "triangle-equality-reject": "Triangular disk · degenerate edge metric"
  };
  var state = { pilot: null, sheetEmulator: null, sheetArmEpoch: null, sheetSeq: 0 };

  function byId(id) { return document.getElementById(id); }
  function svgElement(name, attributes) {
    var element = document.createElementNS(SVG_NS, name);
    Object.keys(attributes || {}).forEach(function (key) { element.setAttribute(key, attributes[key]); });
    return element;
  }
  function clear(element) { while (element.firstChild) element.removeChild(element.firstChild); }
  function text(element, value) { element.textContent = value; }
  function finite(value) { return typeof value === "number" && isFinite(value); }
  function format(value, digits) {
    if (!finite(value)) return "unavailable";
    var absolute = Math.abs(value);
    if ((absolute > 0 && absolute < 1e-4) || absolute >= 1e5) return value.toExponential(digits == null ? 2 : digits);
    return value.toFixed(digits == null ? 3 : digits);
  }
  function slugStatus(value) { return "gate-" + String(value || "unknown").toLowerCase().replace(/_/g, "-"); }
  function rationalPi(coefficient) {
    if (!coefficient) return "—";
    if (coefficient.numerator === 0) return "0";
    var sign = coefficient.numerator < 0 ? "−" : "";
    var numerator = Math.abs(coefficient.numerator);
    if (coefficient.denominator === 1) return sign + (numerator === 1 ? "π" : numerator + "π");
    return sign + (numerator === 1 ? "" : numerator) + "π/" + coefficient.denominator;
  }

  function initializeTabs() {
    var tabs = Array.prototype.slice.call(document.querySelectorAll("[data-ggii-tab]"));
    var panels = Array.prototype.slice.call(document.querySelectorAll("[data-ggii-panel]"));
    function activate(name) {
      tabs.forEach(function (tab) {
        var selected = tab.getAttribute("data-ggii-tab") === name;
        tab.setAttribute("aria-selected", selected ? "true" : "false");
        tab.setAttribute("tabindex", selected ? "0" : "-1");
      });
      panels.forEach(function (panel) { panel.hidden = panel.getAttribute("data-ggii-panel") !== name; });
      if (name === "recognition" && !state.pilot) buildRecognitionPilot();
    }
    tabs.forEach(function (tab, index) {
      tab.addEventListener("click", function () { activate(tab.getAttribute("data-ggii-tab")); });
      tab.addEventListener("keydown", function (event) {
        if (["ArrowRight", "ArrowLeft", "Home", "End"].indexOf(event.key) < 0) return;
        event.preventDefault();
        var next = event.key === "Home" ? tabs[0] : event.key === "End" ? tabs[tabs.length - 1] : tabs[(index + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length];
        next.focus();
        activate(next.getAttribute("data-ggii-tab"));
      });
    });
    var initial = tabs.filter(function (tab) { return tab.getAttribute("aria-selected") === "true"; })[0] || tabs[0];
    activate(initial.getAttribute("data-ggii-tab"));
  }

  function populateSelect(select, values, labels) {
    clear(select);
    values.forEach(function (value) {
      var option = document.createElement("option");
      option.value = value;
      option.textContent = labels[value] || value;
      select.appendChild(option);
    });
  }

  function fitProjector(nodes, width, height, padding) {
    var xs = nodes.map(function (node) { return node.x; });
    var ys = nodes.map(function (node) { return node.y; });
    var minX = Math.min.apply(null, xs), maxX = Math.max.apply(null, xs);
    var minY = Math.min.apply(null, ys), maxY = Math.max.apply(null, ys);
    var spanX = Math.max(maxX - minX, 1e-9), spanY = Math.max(maxY - minY, 1e-9);
    var scale = Math.min((width - 2 * padding) / spanX, (height - 2 * padding) / spanY);
    var offsetX = (width - scale * spanX) / 2;
    var offsetY = (height - scale * spanY) / 2;
    return function (node) { return [offsetX + (node.x - minX) * scale, height - offsetY - (node.y - minY) * scale]; };
  }

  function renderComplex(complex) {
    var svg = byId("ggii-forward-svg");
    var faceLayer = svg.querySelector("[data-layer='faces']");
    var edgeLayer = svg.querySelector("[data-layer='edges']");
    var nodeLayer = svg.querySelector("[data-layer='nodes']");
    clear(faceLayer); clear(edgeLayer); clear(nodeLayer);
    var project = fitProjector(complex.nodes, 960, 540, 28);
    complex.faces.forEach(function (face) {
      var points = face.map(function (id) { return project(complex.nodes[id]).join(","); }).join(" ");
      faceLayer.appendChild(svgElement("polygon", { points: points }));
    });
    complex.edges.forEach(function (edge) {
      var a = project(complex.nodes[edge.source]), b = project(complex.nodes[edge.target]);
      edgeLayer.appendChild(svgElement("line", { x1: a[0], y1: a[1], x2: b[0], y2: b[1] }));
    });
    var radius = complex.nodes.length > 350 ? 1.7 : complex.nodes.length > 150 ? 2.2 : 3;
    complex.nodes.forEach(function (node) {
      var point = project(node);
      nodeLayer.appendChild(svgElement("circle", { cx: point[0], cy: point[1], r: radius }));
    });
  }

  function runForward() {
    var family = byId("ggii-forward-family").value;
    var size = Number(byId("ggii-forward-size").value);
    var sigma = Number(byId("ggii-forward-sigma").value);
    var seed = byId("ggii-forward-seed").value.trim() || "atlas-visible";
    text(byId("ggii-forward-status"), "Generating and validating the finite carrier…");
    try {
      var complex = Ensembles.generateFamily({
        familyId: family,
        linearSize: size,
        characteristicSpacing: 1 / size,
        sigma: sigma,
        streams: { generator: seed + "/generator", conductance: seed + "/conductance" }
      });
      var validation = Ensembles.validateFilledDisk(complex);
      var transport = Atlas.dirichletTransport(complex);
      renderComplex(complex);
      text(byId("ggii-forward-title"), familyLabels[family]);
      text(byId("ggii-forward-counts"), complex.nodes.length + " · " + complex.edges.length + " · " + complex.faces.length);
      text(byId("ggii-forward-counts-detail"), "vertices · edges · triangular faces");
      text(byId("ggii-forward-topology"), "β = (" + validation.topology.betti.join(", ") + ")");
      text(byId("ggii-forward-topology-detail"), "χ=" + validation.topology.eulerCharacteristic + "; boundary components=" + validation.topology.boundaryComponents);
      text(byId("ggii-forward-curvature"), format(validation.gaussBonnet.residual, 2));
      text(byId("ggii-forward-curvature-detail"), "ΣK − 2πχ; binary64 evaluation of P4.3");
      text(byId("ggii-forward-transport"), transport.converged ? format(transport.conductance, 4) : "unresolved");
      text(byId("ggii-forward-transport-detail"), transport.converged ? transport.iterations + " iterations; residual " + format(transport.maximumNormalizedInteriorResidual, 2) : transport.reason || "solver gate failed");
      text(byId("ggii-forward-status"), "Validated " + family + " at L=" + size + ", σ=" + sigma.toFixed(2) + ". This is one finite realization, not a scaling or universality result.");
    } catch (error) {
      text(byId("ggii-forward-status"), "Forward run rejected: " + error.message);
    }
  }

  function appendSvgText(svg, value, x, y, className, anchor) {
    var label = svgElement("text", { x: x, y: y, "class": className || "ggii-chart-label", "text-anchor": anchor || "start" });
    label.textContent = value;
    svg.appendChild(label);
    return label;
  }

  function renderNormBalls() {
    var svg = byId("ggii-norm-balls");
    clear(svg);
    var groups = [
      { label: "square graph", subtitle: "|m| + |n| ≤ 1", cx: 180, points: [[0, -105], [105, 0], [0, 105], [-105, 0]], className: "ggii-series-1" },
      { label: "triangular graph", subtitle: "max(|m|,|n|,|m+n|) ≤ 1", cx: 520, points: [[0, -105], [91, -52.5], [91, 52.5], [0, 105], [-91, 52.5], [-91, -52.5]], className: "ggii-series-2" }
    ];
    groups.forEach(function (group) {
      svg.appendChild(svgElement("line", { x1: group.cx - 125, y1: 165, x2: group.cx + 125, y2: 165, "class": "ggii-axis" }));
      svg.appendChild(svgElement("line", { x1: group.cx, y1: 40, x2: group.cx, y2: 290, "class": "ggii-axis" }));
      var polygon = svgElement("polygon", {
        points: group.points.map(function (point) { return (group.cx + point[0]) + "," + (165 + point[1]); }).join(" "),
        "class": group.className,
        "fill-opacity": "0.12",
        "stroke-width": "3"
      });
      svg.appendChild(polygon);
      group.points.forEach(function (point) { svg.appendChild(svgElement("circle", { cx: group.cx + point[0], cy: 165 + point[1], r: 4, "class": group.className })); });
      appendSvgText(svg, group.label, group.cx, 315, "ggii-chart-label", "middle");
      appendSvgText(svg, group.subtitle, group.cx, 333, "ggii-chart-muted", "middle");
    });
  }

  function renderDiffusionChart() {
    var svg = byId("ggii-diffusion-chart");
    clear(svg);
    var control = G2.robustWhitenedDiffusionUniversalityControl();
    var left = 76, right = 670, top = 88, bottom = 278;
    var allErrors = [];
    control.rows.forEach(function (row) { allErrors = allErrors.concat(row.maxCharacteristicErrors); });
    var minLog = Math.floor(Math.log10(Math.min.apply(null, allErrors))) - 0.2;
    var maxLog = Math.ceil(Math.log10(Math.max.apply(null, allErrors))) + 0.1;
    function x(n) { return left + (Math.log10(n) - Math.log10(200)) / (Math.log10(20000) - Math.log10(200)) * (right - left); }
    function y(error) { return bottom - (Math.log10(error) - minLog) / (maxLog - minLog) * (bottom - top); }
    svg.appendChild(svgElement("line", { x1: left, y1: bottom, x2: right, y2: bottom, "class": "ggii-axis" }));
    svg.appendChild(svgElement("line", { x1: left, y1: top, x2: left, y2: bottom, "class": "ggii-axis" }));
    control.sampleSizes.forEach(function (n) {
      var px = x(n);
      svg.appendChild(svgElement("line", { x1: px, y1: bottom, x2: px, y2: top, "class": "ggii-axis", opacity: "0.45" }));
      appendSvgText(svg, String(n), px, 300, "ggii-chart-muted", "middle");
    });
    for (var exponent = Math.ceil(minLog); exponent <= Math.floor(maxLog); exponent += 1) {
      var py = y(Math.pow(10, exponent));
      svg.appendChild(svgElement("line", { x1: left, y1: py, x2: right, y2: py, "class": "ggii-axis", opacity: "0.45" }));
      appendSvgText(svg, "10^" + exponent, left - 10, py + 4, "ggii-chart-muted", "end");
    }
    control.rows.forEach(function (row, index) {
      var className = "ggii-series-" + (index + 1);
      var path = row.maxCharacteristicErrors.map(function (error, pointIndex) { return (pointIndex ? "L" : "M") + x(control.sampleSizes[pointIndex]) + " " + y(error); }).join(" ");
      svg.appendChild(svgElement("path", { d: path, "class": className, fill: "none", "stroke-width": "2.4" }));
      row.maxCharacteristicErrors.forEach(function (error, pointIndex) { svg.appendChild(svgElement("circle", { cx: x(control.sampleSizes[pointIndex]), cy: y(error), r: 4, "class": className })); });
      var legendX = left + (index % 2) * 300, legendY = 24 + Math.floor(index / 2) * 25;
      svg.appendChild(svgElement("line", { x1: legendX, y1: legendY, x2: legendX + 28, y2: legendY, "class": className, "stroke-width": "3" }));
      appendSvgText(svg, row.law.id.replace(/-/g, " "), legendX + 36, legendY + 4, "ggii-chart-muted", "start");
    });
    appendSvgText(svg, "walk steps n", (left + right) / 2, 328, "ggii-chart-label", "middle");
    appendSvgText(svg, "maximum characteristic error", left, 78, "ggii-chart-label", "start");
  }

  function renderPhaseMap() {
    var svg = byId("ggii-phase-map");
    clear(svg);
    var phase = G2.diffusionAnisotropyPhaseDiagram();
    var left = 142, top = 58, cellWidth = 100, cellHeight = 45;
    phase.axes.sampleSize.forEach(function (sampleSize, column) {
      appendSvgText(svg, String(sampleSize), left + column * cellWidth + cellWidth / 2, 42, "ggii-chart-muted", "middle");
    });
    phase.rows.forEach(function (row, rowIndex) {
      var y = top + rowIndex * cellHeight;
      appendSvgText(svg, "p = " + row.horizontalStepProbability.toFixed(1), left - 18, y + 21, "ggii-chart-label", "end");
      row.cells.forEach(function (cell, column) {
        var resolved = cell.classification === "within-resolution-guard";
        var x = left + column * cellWidth;
        svg.appendChild(svgElement("rect", {
          x: x + 2, y: y + 2, width: cellWidth - 4, height: cellHeight - 4, rx: 6,
          fill: resolved ? "var(--exact)" : "var(--hypothesis)",
          opacity: resolved ? "0.24" : "0.18",
          stroke: resolved ? "var(--exact)" : "var(--hypothesis)",
          "stroke-width": "1.5"
        }));
        appendSvgText(svg, cell.maximumCharacteristicError.toExponential(2), x + cellWidth / 2, y + 27, "ggii-chart-value", "middle");
      });
    });
    appendSvgText(svg, "walk steps n", left + 2.5 * cellWidth, 307, "ggii-chart-label", "middle");
    appendSvgText(svg, "horizontal-step probability p", 12, 26, "ggii-chart-label", "start");
    svg.appendChild(svgElement("rect", { x: left, y: 330, width: 18, height: 18, rx: 3, fill: "var(--exact)", opacity: "0.24", stroke: "var(--exact)" }));
    appendSvgText(svg, "≤ 5e−5 guard", left + 27, 344, "ggii-chart-muted", "start");
    svg.appendChild(svgElement("rect", { x: left + 190, y: 330, width: 18, height: 18, rx: 3, fill: "var(--hypothesis)", opacity: "0.18", stroke: "var(--hypothesis)" }));
    appendSvgText(svg, "> guard · finite-size crossover, not a phase transition", left + 217, 344, "ggii-chart-muted", "start");
  }

  function buildRecognitionPilot() {
    text(byId("ggii-recognition-status"), "Building the closed 48-run preview matrix…");
    window.setTimeout(function () {
      try {
        state.pilot = Atlas.runPilotAtlas();
        text(byId("ggii-recognition-status"), "Preview matrix ready at the fixed query slice L=4, σ=0.75, with two deterministic replicates per cell. Universality remains " + state.pilot.universalityStatus + ".");
        runRecognition();
      } catch (error) {
        text(byId("ggii-recognition-status"), "Recognition preview rejected: " + error.message);
      }
    }, 0);
  }

  function recognitionCell(family) {
    if (!state.pilot) return null;
    return state.pilot.cells.filter(function (cell) { return cell.familyId === family && cell.linearSize === 4 && cell.sigma === 0.75; })[0] ||
      state.pilot.cells.filter(function (cell) { return cell.familyId === family; })[0];
  }

  function featureVector(cell, mask) {
    var firstRun = state.pilot.runs.filter(function (run) { return run.runId === cell.runIds[0]; })[0];
    var summary = cell.summaries;
    var exact = firstRun.measurements.exact;
    var vector = [exact.surfaceValid ? 1 : 0].concat(exact.betti).concat([exact.eulerCharacteristic, exact.boundaryComponents]);
    if (mask === "topology") return vector;
    vector.push(firstRun.complexSummary.vertices, firstRun.complexSummary.edges, firstRun.complexSummary.faces);
    if (mask === "local") return vector;
    vector.push(summary.conductanceMean, summary.spectralGapMean);
    if (mask === "transport") return vector;
    vector.push(summary.signedOneEdgeSensitivityMean);
    ["volume", "spectral", "walk"].forEach(function (key) { vector.push(summary.unvalidatedDimensionDescriptorMeans[key]); });
    return vector;
  }

  function vectorDistance(query, candidate) {
    return Math.sqrt(query.reduce(function (sum, value, index) {
      var other = candidate[index];
      if (!finite(value) || !finite(other)) return sum + 1;
      var scale = Math.max(Math.abs(value), Math.abs(other), 1e-9);
      var difference = (value - other) / scale;
      return sum + difference * difference;
    }, 0) / Math.max(1, query.length));
  }

  function runRecognition() {
    if (!state.pilot) return;
    var queryFamily = byId("ggii-recognition-family").value;
    var mask = byId("ggii-recognition-mask").value;
    var queryCell = recognitionCell(queryFamily);
    var query = featureVector(queryCell, mask);
    var rows = Ensembles.FAMILY_IDS.map(function (family) {
      var cell = recognitionCell(family);
      return { family: family, cell: cell, distance: vectorDistance(query, featureVector(cell, mask)) };
    }).sort(function (a, b) { return a.distance - b.distance || a.family.localeCompare(b.family); });
    var minimum = rows[0].distance;
    var tied = rows.filter(function (row) { return Math.abs(row.distance - minimum) < 1e-10; }).length;
    var container = byId("ggii-recognition-results");
    clear(container);
    rows.forEach(function (row) {
      var article = document.createElement("article");
      article.setAttribute("data-best", Math.abs(row.distance - minimum) < 1e-10 ? "true" : "false");
      var label = document.createElement("span"); label.className = "evidence numerical"; label.textContent = row.distance < 1e-12 ? "indistinguishable" : "finite distance";
      var title = document.createElement("strong"); title.textContent = familyLabels[row.family];
      var score = document.createElement("small"); score.textContent = "normalized descriptor distance " + format(row.distance, 5);
      article.appendChild(label); article.appendChild(title); article.appendChild(score); container.appendChild(article);
    });
    text(byId("ggii-recognition-status"), tied > 1
      ? tied + " families are tied under the selected observation mask. The ambiguity is the result."
      : "The query has one nearest finite preview signature under this mask; no population-level identifiability is claimed.");
  }

  function summarizeGate(gate) {
    if (!gate) return "—";
    if (gate.code && gate.code !== "OK") return gate.code + ": " + gate.statement;
    return gate.statement || gate.code || "completed";
  }

  function runInverse() {
    var id = byId("ggii-inverse-case").value;
    try {
      var report = Inverse.compileInverseDesign(Inverse.representativeRequest(id));
      var validation = Inverse.validateCompilerReport(report);
      if (!validation.valid) throw new Error(validation.errors.join("; "));
      text(byId("ggii-inverse-status"), report.status);
      var badge = byId("ggii-inverse-status-label");
      var applicable = report.gates.filter(function (gate) { return gate.status !== "NOT_RUN" && gate.status !== "NOT_APPLICABLE"; });
      var decisive = report.gates.filter(function (gate) { return gate.status === "FAIL" || gate.status === "MARGINAL" || gate.status === "INCONCLUSIVE"; })[0] || null;
      var hasNumerical = applicable.some(function (gate) { return gate.evidenceClass.indexOf("numerical") >= 0; });
      var decisiveExact = decisive && decisive.evidenceClass.indexOf("exact") >= 0;
      badge.className = "evidence " + (report.status === "FAIL" && decisiveExact ? "exact" : report.status === "PASS" && !hasNumerical ? "exact" : report.status === "PASS" || report.status === "FAIL" ? "numerical" : "hypothesis");
      text(badge, report.status === "PASS" ? (hasNumerical ? "mixed finite admission" : "exact finite admission") : report.status === "FAIL" ? (decisiveExact ? "exact finite obstruction" : "finite obstruction") : "unresolved");
      if (report.status === "PASS") {
        text(byId("ggii-inverse-summary-text"), "Every applicable bounded gate passes in the declared intrinsic " + report.normalizedRequest.models[0] + " scope" + (hasNumerical ? "; at least one supporting gate is numerical." : " using exact finite checks."));
      } else if (decisive) {
        var decisiveIndex = report.gates.indexOf(decisive);
        var later = report.gates.slice(decisiveIndex + 1);
        var notRun = later.filter(function (gate) { return gate.status === "NOT_RUN"; }).length;
        var evaluated = later.filter(function (gate) { return gate.status !== "NOT_RUN" && gate.status !== "NOT_APPLICABLE"; }).length;
        text(byId("ggii-inverse-summary-text"), decisive.id + " is decisive: " + decisive.code + ". After it, " + evaluated + " gate" + (evaluated === 1 ? " was" : "s were") + " evaluated and " + notRun + " remained not run.");
      }
      var body = byId("ggii-inverse-gates"); clear(body);
      report.gates.forEach(function (gate) {
        var row = document.createElement("tr");
        var gateCell = document.createElement("td"); gateCell.textContent = gate.id + " · " + gate.name;
        var statusCell = document.createElement("td"); statusCell.className = slugStatus(gate.status); statusCell.textContent = gate.status;
        var evidenceCell = document.createElement("td"); evidenceCell.textContent = gate.evidenceClass + " / " + gate.basis;
        var findingCell = document.createElement("td"); findingCell.textContent = summarizeGate(gate);
        row.appendChild(gateCell); row.appendChild(statusCell); row.appendChild(evidenceCell); row.appendChild(findingCell); body.appendChild(row);
      });
      var exactAdmission = report.gates.filter(function (gate) { return gate.id === "G4" && gate.status === "PASS" && gate.witness; })[0];
      var certificate = report.obstructionCertificates.length ? report.obstructionCertificates[0] : exactAdmission || report.gates.filter(function (gate) { return gate.status === "PASS" && gate.witness; }).slice(-1)[0];
      byId("ggii-inverse-witness").textContent = JSON.stringify(certificate || { reportDigest: report.reportDigest, note: "No standalone obstruction certificate; inspect the ordered gate report." }, null, 2);
    } catch (error) {
      text(byId("ggii-inverse-status"), "REJECTED");
      byId("ggii-inverse-witness").textContent = error.message;
    }
  }

  function renderQStar(star) {
    var svg = byId("ggii-sheet-svg"); clear(svg);
    var cx = 280, cy = 205, radius = 145;
    var sectorAngle = Math.PI / 3;
    var startAngle = -Math.PI / 2 - star.q * sectorAngle / 2;
    var boundaryPoints = [];
    for (var index = 0; index <= star.q; index += 1) {
      var angle = startAngle + index * sectorAngle;
      boundaryPoints.push([cx + radius * Math.cos(angle), cy + radius * Math.sin(angle)]);
    }
    for (var sector = 0; sector < star.q; sector += 1) {
      var point = boundaryPoints[sector], next = boundaryPoints[sector + 1];
      var overlap = star.q > 6 && sector >= 6;
      svg.appendChild(svgElement("polygon", {
        points: cx + "," + cy + " " + point.join(",") + " " + next.join(","),
        fill: overlap ? "color-mix(in srgb, var(--accent) 30%, transparent)" : "color-mix(in srgb, var(--primary) 12%, transparent)",
        stroke: overlap ? "var(--accent)" : "var(--line)",
        "stroke-width": overlap ? "2.4" : "1.2",
        "stroke-dasharray": overlap ? "7 5" : "none"
      }));
    }
    boundaryPoints.forEach(function (point, index) {
      svg.appendChild(svgElement("line", { x1: cx, y1: cy, x2: point[0], y2: point[1], stroke: index > 6 ? "var(--accent)" : "var(--primary)", "stroke-width": "2" }));
      svg.appendChild(svgElement("circle", { cx: point[0], cy: point[1], r: 5, fill: "var(--surface)", stroke: index > 6 ? "var(--accent)" : "var(--primary)", "stroke-width": "2" }));
    });
    svg.appendChild(svgElement("circle", { cx: cx, cy: cy, r: 9, fill: "var(--accent)" }));
    var seam = star.q < 6 ? "60° gap" : star.q === 6 ? "closed seam" : "60° overlap";
    appendSvgText(svg, "q = " + star.q + " · " + star.q + " × 60° · " + seam, cx, 392, "ggii-chart-label", "middle");
    appendSvgText(svg, "center K = " + rationalPi(star.intrinsic.center.defectPiCoefficient), cx, 30, "ggii-chart-label", "middle");
  }

  function sheetMessage(type, seq, timeMs, payload, armEpoch) {
    return Sheet.createProtocolMessage({ type: type, seq: seq, monotonicTimeMs: timeMs, deadlineMs: timeMs + 100, armEpoch: armEpoch == null ? null : armEpoch, payload: payload });
  }

  function updateSheetReadout(star, snapshot, status) {
    text(byId("ggii-sheet-defect"), rationalPi(star.intrinsic.center.defectPiCoefficient));
    text(byId("ggii-sheet-total"), rationalPi(star.intrinsic.totalDefectPiCoefficient) + " = 2πχ");
    text(byId("ggii-sheet-state"), snapshot ? snapshot.state + " · revision " + snapshot.plant.stateRevision : "not initialized");
    if (snapshot) {
      var positions = snapshot.plant.channels.map(function (channel) { return channel.positionDeg; });
      var targets = snapshot.plant.channels.map(function (channel) { return channel.targetDeg; });
      text(byId("ggii-sheet-actuation"), "hinges " + format(Math.min.apply(null, positions), 2) + "…" + format(Math.max.apply(null, positions), 2) + "°; targets " + format(Math.min.apply(null, targets), 2) + "…" + format(Math.max.apply(null, targets), 2) + "°; center " + format(snapshot.plant.heights.centerHeightMm, 2) + " mm; span " + format(snapshot.plant.heights.heightRangeMm, 2) + " mm");
    } else text(byId("ggii-sheet-actuation"), "not initialized");
    text(byId("ggii-sheet-protocol"), Sheet.PROTOCOL + " · virtual only");
    text(byId("ggii-sheet-status"), status);
  }

  function runSheet() {
    var q = Number(byId("ggii-sheet-q").value);
    var amplitude = Number(byId("ggii-sheet-command").value);
    var star = Sheet.createQStar(q);
    renderQStar(star);
    try {
      var emulator = Sheet.createHilEmulator({ seed: "browser-sheet-session", plant: { q: q, seed: "browser-sheet-plant", backlashDeg: 0 }, watchdogTimeoutMs: 250 });
      var measurement = Sheet.measureVirtualPlant(emulator.snapshot().plant, { seed: "browser-sheet-measurement", sampleIndex: 1, noise: { heightStdMm: 0, hingeStdDeg: 0, dropoutProbability: 0 } });
      emulator.setObservation(measurement);
      var arm = emulator.receive(sheetMessage("ARM", 1, 0, { sessionId: "browser-virtual-session" }, null));
      var plant = emulator.snapshot().plant;
      var channels = plant.channels.slice(0, Math.min(3, plant.channels.length)).map(function (channel, index) {
        return { id: channel.id, positionDeg: (index % 2 ? -1 : 1) * amplitude * 12, maxRateDegPerSec: 6 };
      });
      var command = sheetMessage("COMMAND", 2, 1, { plantId: plant.plantId, expectedStateRevision: plant.stateRevision, expectedStateDigest: plant.stateDigest, observationDigest: measurement.measurementDigest, channels: channels }, arm.armEpoch);
      var response = emulator.receive(command);
      emulator.tick(80);
      state.sheetEmulator = emulator; state.sheetArmEpoch = arm.armEpoch; state.sheetSeq = 2;
      var snapshot = emulator.snapshot();
      var commandCode = response.type === "FAULT" ? response.payload.code : "COMMAND_ACCEPTED";
      updateSheetReadout(star, snapshot, commandCode + "; synthetic measurement bound to state revision " + measurement.sourceStateRevision + ". No hardware command was possible.");
    } catch (error) {
      updateSheetReadout(star, null, "Virtual phase rejected: " + error.message);
    }
  }

  function estopSheet() {
    var q = Number(byId("ggii-sheet-q").value), star = Sheet.createQStar(q);
    if (!state.sheetEmulator) { runSheet(); }
    try {
      var snapshot = state.sheetEmulator.snapshot();
      var time = snapshot.monotonicTimeMs;
      state.sheetSeq += 1;
      var response = state.sheetEmulator.receive(sheetMessage("ESTOP", state.sheetSeq, time, { reason: "browser-virtual-estop" }, state.sheetArmEpoch));
      var estopCode = response.type === "FAULT" ? response.payload.code : "ESTOP_LATCHED";
      updateSheetReadout(star, state.sheetEmulator.snapshot(), estopCode + "; virtual ESTOP is latched for this in-memory session.");
    } catch (error) {
      updateSheetReadout(star, state.sheetEmulator.snapshot(), "Virtual ESTOP rejected safely: " + error.message);
    }
  }

  function renderEvidence() {
    var records = Claims.listClaims();
    text(byId("ggii-proof-count"), String(records.length));
    var body = byId("ggii-evidence-ledger"); clear(body);
    records.forEach(function (record) {
      var row = document.createElement("tr");
      var idCell = document.createElement("td"); idCell.textContent = record.id;
      var claimCell = document.createElement("td"); claimCell.textContent = record.claim;
      var scopeCell = document.createElement("td"); scopeCell.textContent = record.scope + (record.limitations.length ? " Principal limitation: " + record.limitations[0] + "." : "");
      row.appendChild(idCell); row.appendChild(claimCell); row.appendChild(scopeCell); body.appendChild(row);
    });
  }

  function initializeControls() {
    Array.prototype.forEach.call(document.querySelectorAll("form.ggii-controls"), function (form) {
      form.addEventListener("submit", function (event) { event.preventDefault(); });
    });
    populateSelect(byId("ggii-forward-family"), Ensembles.FAMILY_IDS, familyLabels);
    populateSelect(byId("ggii-recognition-family"), Ensembles.FAMILY_IDS, familyLabels);
    populateSelect(byId("ggii-inverse-case"), Inverse.listRepresentativeRequests(), inverseLabels);
    byId("ggii-forward-size").addEventListener("input", function () { text(byId("ggii-forward-size-output"), this.value); });
    byId("ggii-forward-sigma").addEventListener("input", function () { text(byId("ggii-forward-sigma-output"), Number(this.value).toFixed(2)); });
    byId("ggii-sheet-command").addEventListener("input", function () { text(byId("ggii-sheet-command-output"), Number(this.value).toFixed(2)); });
    byId("ggii-forward-run").addEventListener("click", runForward);
    byId("ggii-recognition-run").addEventListener("click", runRecognition);
    byId("ggii-inverse-run").addEventListener("click", runInverse);
    byId("ggii-sheet-run").addEventListener("click", runSheet);
    byId("ggii-sheet-estop").addEventListener("click", estopSheet);
    byId("ggii-sheet-q").addEventListener("change", function () {
      var star = Sheet.createQStar(Number(this.value));
      renderQStar(star); updateSheetReadout(star, null, "Phase selected; run the virtual instrument to bind a synthetic observation and command.");
      state.sheetEmulator = null; state.sheetArmEpoch = null; state.sheetSeq = 0;
    });
  }

  function initialize() {
    initializeTabs();
    initializeControls();
    renderNormBalls();
    renderDiffusionChart();
    renderPhaseMap();
    renderEvidence();
    runForward();
    runInverse();
    var initialStar = Sheet.createQStar(6);
    renderQStar(initialStar);
    updateSheetReadout(initialStar, null, "No virtual command has run.");
  }

  initialize();
})();
