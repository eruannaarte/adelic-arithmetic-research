(() => {
  "use strict";

  const root = document.getElementById("ao-lab");
  if (!root) return;

  const ns = "http://www.w3.org/2000/svg";
  const primes = [2, 3, 5];
  const times = [245943 / 1000, 140531 / 500, 120104 / 125];
  const gridCount = 37;
  const hiddenCount = 19;
  const grid = Array.from({ length: gridCount }, (_, i) => 0.04 + i * 0.92 / (gridCount - 1));
  const hiddenGrid = Array.from({ length: hiddenCount }, (_, i) => 0.04 + i * 0.92 / (hiddenCount - 1));

  const state = {
    target: [0.28, 0.52, 0.76],
    readings: 3,
    tolerance: 0.02,
    cells: [],
    envelope: [],
    nearest: null
  };

  const controls = {
    readings: root.querySelector("#reading-count"),
    shapes: [root.querySelector("#y2"), root.querySelector("#y3"), root.querySelector("#y5")],
    outputs: [root.querySelector("#y2-value"), root.querySelector("#y3-value"), root.querySelector("#y5-value")],
    tolerance: root.querySelector("#tolerance"),
    toleranceOutput: root.querySelector("#tolerance-value")
  };

  const heatSvg = root.querySelector("#heat-chart");
  const envelopeSvg = root.querySelector("#envelope-chart");
  const tooltip = root.querySelector("#tooltip");
  let scheduled = false;

  function css(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function el(name, attrs = {}, text = null) {
    const node = document.createElementNS(ns, name);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, String(value)));
    if (text !== null) node.textContent = text;
    return node;
  }

  function clear(svg) {
    Array.from(svg.children).forEach(child => {
      if (child.tagName !== "title" && child.tagName !== "desc") child.remove();
    });
  }

  function factorReading(y, theta) {
    const u = y / (1 - y);
    const weights = [1, u, u * u, u * u * u];
    const total = weights.reduce((sum, value) => sum + value, 0);
    let re = 0;
    let im = 0;
    for (let a = 0; a < 4; a += 1) {
      re += weights[a] * Math.cos(-a * theta) / total;
      im += weights[a] * Math.sin(-a * theta) / total;
    }
    return [re, im];
  }

  function multiply(left, right) {
    return [
      left[0] * right[0] - left[1] * right[1],
      left[0] * right[1] + left[1] * right[0]
    ];
  }

  function observation(shape, count) {
    return times.slice(0, count).map(time => {
      let value = [1, 0];
      for (let j = 0; j < primes.length; j += 1) {
        value = multiply(value, factorReading(shape[j], time * Math.log(primes[j])));
      }
      return value;
    });
  }

  function observationDistance(left, right) {
    let maximum = 0;
    for (let i = 0; i < left.length; i += 1) {
      maximum = Math.max(maximum, Math.hypot(left[i][0] - right[i][0], left[i][1] - right[i][1]));
    }
    return maximum;
  }

  function shapeDistance(left, right) {
    return Math.max(...left.map((value, index) => Math.abs(value - right[index])));
  }

  function recompute() {
    state.target = controls.shapes.map(input => Number(input.value));
    state.readings = Number(controls.readings.value);
    state.tolerance = Number(controls.tolerance.value);
    controls.outputs.forEach((output, index) => { output.value = state.target[index].toFixed(2); });
    controls.toleranceOutput.value = state.tolerance.toFixed(3);
    root.querySelector("#tolerance-context").textContent = `reading distance ≤ ${state.tolerance.toFixed(3)}`;

    const targetObservation = observation(state.target, state.readings);
    const cells = [];
    for (const x of grid) {
      for (const y of grid) {
        let best = { distance: Infinity, hidden: hiddenGrid[0], shapeDistance: 0 };
        for (const hidden of hiddenGrid) {
          const candidate = [x, y, hidden];
          const distance = observationDistance(targetObservation, observation(candidate, state.readings));
          if (distance < best.distance) {
            best = { distance, hidden, shapeDistance: shapeDistance(candidate, state.target) };
          }
        }
        cells.push({ x, y, ...best });
      }
    }
    state.cells = cells;

    const separated = cells.filter(cell => cell.shapeDistance >= 0.08);
    state.nearest = separated.reduce((best, cell) => cell.distance < best.distance ? cell : best, separated[0]);
    const floor = separated.reduce((best, cell) => Math.min(best, cell.distance / cell.shapeDistance), Infinity);
    const ambiguous = cells.filter(cell => cell.distance <= state.tolerance).length / cells.length;

    const bins = Array.from({ length: 20 }, () => []);
    cells.filter(cell => cell.shapeDistance >= 0.015).forEach(cell => {
      const index = Math.min(19, Math.floor(cell.shapeDistance / 0.05));
      bins[index].push(cell);
    });
    state.envelope = bins.map(bin => {
      if (!bin.length) return null;
      return {
        shapeDistance: bin.reduce((sum, cell) => sum + cell.shapeDistance, 0) / bin.length,
        distance: bin.reduce((best, cell) => Math.min(best, cell.distance), Infinity)
      };
    }).filter(Boolean);

    root.querySelector("#ambiguous").textContent = `${(100 * ambiguous).toFixed(1)}%`;
    root.querySelector("#floor").textContent = floor.toFixed(3);
    root.querySelector("#nearest").textContent = state.nearest.distance.toFixed(4);
    root.querySelector("#detail").textContent =
      `Nearest grid competitor: y = (${state.nearest.x.toFixed(2)}, ${state.nearest.y.toFixed(2)}, ${state.nearest.hidden.toFixed(2)}), compact shape gap ${state.nearest.shapeDistance.toFixed(2)}.`;
    draw();
  }

  function linear(domainMin, domainMax, rangeMin, rangeMax) {
    return value => rangeMin + (value - domainMin) * (rangeMax - rangeMin) / (domainMax - domainMin);
  }

  function logScale(domainMin, domainMax, rangeMin, rangeMax) {
    const lo = Math.log(domainMin);
    const hi = Math.log(domainMax);
    return value => rangeMin + (Math.log(value) - lo) * (rangeMax - rangeMin) / (hi - lo);
  }

  function dimensions(wrapper, minimumHeight = 320) {
    const width = Math.max(300, Math.floor(wrapper.getBoundingClientRect().width));
    return { width, height: Math.max(minimumHeight, Math.min(410, Math.round(width * 0.72))) };
  }

  function addAxes(svg, x, y, xTicks, yTicks, box, xFormat, yFormat, xTitle, yTitle) {
    const { left, top, width, height, outerHeight } = box;
    svg.appendChild(el("rect", { x: left, y: top, width, height, fill: "none", class: "frame" }));
    xTicks.forEach(value => {
      const px = x(value);
      svg.appendChild(el("line", { x1: px, x2: px, y1: top + height, y2: top + height + 5, class: "tick-line" }));
      svg.appendChild(el("text", { x: px, y: top + height + 20, "text-anchor": "middle", class: "muted-label" }, xFormat(value)));
    });
    yTicks.forEach(value => {
      const py = y(value);
      svg.appendChild(el("line", { x1: left, x2: left + width, y1: py, y2: py, class: "grid-line" }));
      svg.appendChild(el("text", { x: left - 9, y: py + 4, "text-anchor": "end", class: "muted-label" }, yFormat(value)));
    });
    svg.appendChild(el("text", { x: left + width / 2, y: outerHeight - 9, "text-anchor": "middle" }, xTitle));
    svg.appendChild(el("text", { x: 15, y: top + height / 2, "text-anchor": "middle", transform: `rotate(-90 15 ${top + height / 2})` }, yTitle));
  }

  function drawHeat() {
    const wrapper = root.querySelector("#heat-wrap");
    const { width, height } = dimensions(wrapper);
    const margin = { top: 16, right: 16, bottom: 54, left: 62 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    const cellWidth = innerWidth / gridCount;
    const cellHeight = innerHeight / gridCount;
    const x = linear(0.04, 0.96, margin.left + cellWidth / 2, margin.left + innerWidth - cellWidth / 2);
    const y = linear(0.04, 0.96, margin.top + innerHeight - cellHeight / 2, margin.top + cellHeight / 2);
    const logs = state.cells.map(cell => Math.log10(cell.distance + 1e-6));
    const logMin = Math.min(...logs);
    const logMax = Math.max(...logs);

    heatSvg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    clear(heatSvg);

    const defs = el("defs");
    const pattern = el("pattern", { id: "ambiguity-hatch", width: 6, height: 6, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" });
    pattern.appendChild(el("rect", { width: 6, height: 6, fill: css("--orange-soft") }));
    pattern.appendChild(el("line", { x1: 0, x2: 0, y1: 0, y2: 6, stroke: css("--orange"), "stroke-width": 2 }));
    defs.appendChild(pattern);
    heatSvg.appendChild(defs);

    state.cells.forEach(cell => {
      const normalized = (Math.log10(cell.distance + 1e-6) - logMin) / Math.max(1e-9, logMax - logMin);
      const lightness = matchMedia("(prefers-color-scheme: dark)").matches ? 30 + normalized * 39 : 88 - normalized * 48;
      const fill = cell.distance <= state.tolerance ? "url(#ambiguity-hatch)" : `hsl(184 52% ${lightness}%)`;
      heatSvg.appendChild(el("rect", {
        x: x(cell.x) - cellWidth / 2,
        y: y(cell.y) - cellHeight / 2,
        width: cellWidth + 0.4,
        height: cellHeight + 0.4,
        fill
      }));
    });

    const tickValues = width < 430 ? [0.1, 0.4, 0.7, 0.9] : [0.1, 0.3, 0.5, 0.7, 0.9];
    addAxes(
      heatSvg, x, y, tickValues, tickValues,
      { left: margin.left, top: margin.top, width: innerWidth, height: innerHeight, outerHeight: height },
      value => value.toFixed(1), value => value.toFixed(1),
      "candidate prime 2 shape y₂", "candidate prime 3 shape y₃"
    );

    const sourceX = x(state.target[0]);
    const sourceY = y(state.target[1]);
    heatSvg.appendChild(el("path", { d: `M${sourceX - 7},${sourceY}H${sourceX + 7}M${sourceX},${sourceY - 7}V${sourceY + 7}`, stroke: css("--purple"), "stroke-width": 2.5, fill: "none" }));
    heatSvg.appendChild(el("circle", { cx: x(state.nearest.x), cy: y(state.nearest.y), r: 6, fill: "none", stroke: css("--purple"), "stroke-width": 2.5 }));

    const overlay = el("rect", { x: margin.left, y: margin.top, width: innerWidth, height: innerHeight, fill: "transparent" });
    overlay.style.cursor = "crosshair";
    overlay.addEventListener("pointermove", event => {
      const box = heatSvg.getBoundingClientRect();
      const svgX = (event.clientX - box.left) * width / box.width;
      const svgY = (event.clientY - box.top) * height / box.height;
      const gx = Math.max(0, Math.min(gridCount - 1, Math.round((svgX - margin.left) / innerWidth * (gridCount - 1))));
      const gy = Math.max(0, Math.min(gridCount - 1, gridCount - 1 - Math.round((svgY - margin.top) / innerHeight * (gridCount - 1))));
      const cell = state.cells[gx * gridCount + gy];
      tooltip.hidden = false;
      tooltip.textContent = `y = (${cell.x.toFixed(2)}, ${cell.y.toFixed(2)}, ${cell.hidden.toFixed(2)}) · reading distance ${cell.distance.toFixed(4)} · shape gap ${cell.shapeDistance.toFixed(2)}`;
      const rootBox = root.getBoundingClientRect();
      tooltip.style.left = `${Math.max(8, Math.min(rootBox.width - 258, event.clientX - rootBox.left + 12))}px`;
      tooltip.style.top = `${Math.max(8, event.clientY - rootBox.top - 52)}px`;
    });
    overlay.addEventListener("pointerleave", () => { tooltip.hidden = true; });
    heatSvg.appendChild(overlay);
  }

  function logTicks(minimum, maximum) {
    const candidates = [0.00001, 0.00003, 0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1];
    const inside = candidates.filter(value => value >= minimum && value <= maximum);
    if (inside.length <= 5) return inside;
    const stride = Math.ceil(inside.length / 5);
    return inside.filter((_, index) => index % stride === 0 || index === inside.length - 1);
  }

  function drawEnvelope() {
    const wrapper = root.querySelector("#envelope-wrap");
    const { width, height } = dimensions(wrapper);
    const margin = { top: 16, right: 18, bottom: 54, left: 68 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    const xValues = state.envelope.map(point => point.shapeDistance);
    const yValues = state.envelope.map(point => point.distance).concat([state.tolerance]);
    const xMin = Math.max(0, Math.min(...xValues) - 0.03);
    const xMax = Math.min(1, Math.max(...xValues) + 0.03);
    const yMin = Math.max(1e-5, Math.min(...yValues) * 0.65);
    const yMax = Math.max(yMin * 10, Math.max(...yValues) * 1.35);
    const x = linear(xMin, xMax, margin.left, margin.left + innerWidth);
    const y = logScale(yMin, yMax, margin.top + innerHeight, margin.top);

    envelopeSvg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    clear(envelopeSvg);
    const xTickCandidates = width < 430 ? [0.1, 0.4, 0.7, 0.9] : [0.1, 0.3, 0.5, 0.7, 0.9];
    const xTicks = xTickCandidates.filter(value => value >= xMin && value <= xMax);
    addAxes(
      envelopeSvg, x, y, xTicks, logTicks(yMin, yMax),
      { left: margin.left, top: margin.top, width: innerWidth, height: innerHeight, outerHeight: height },
      value => value.toFixed(1), value => value < 0.001 ? value.toExponential(0) : value.toFixed(value < 0.1 ? 3 : 1),
      "compact shape distance ‖Δy‖∞", "reading distance ‖ΔH‖∞"
    );

    const cutoffY = y(state.tolerance);
    envelopeSvg.appendChild(el("line", { x1: margin.left, x2: margin.left + innerWidth, y1: cutoffY, y2: cutoffY, stroke: css("--orange"), "stroke-width": 1.8, "stroke-dasharray": "5 4" }));
    envelopeSvg.appendChild(el("text", { x: margin.left + innerWidth - 4, y: cutoffY - 7, "text-anchor": "end", class: "muted-label" }, `pair cutoff ${state.tolerance.toFixed(3)}`));

    const path = state.envelope.map((point, index) => `${index ? "L" : "M"}${x(point.shapeDistance).toFixed(2)},${y(Math.max(yMin, point.distance)).toFixed(2)}`).join(" ");
    envelopeSvg.appendChild(el("path", { d: path, fill: "none", stroke: css("--teal"), "stroke-width": 2.4 }));
    state.envelope.forEach(point => {
      envelopeSvg.appendChild(el("circle", { cx: x(point.shapeDistance), cy: y(Math.max(yMin, point.distance)), r: 3.2, fill: css("--teal") }));
    });
  }

  function draw() {
    tooltip.hidden = true;
    drawHeat();
    drawEnvelope();
  }

  function scheduleRecompute() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      scheduled = false;
      recompute();
    });
  }

  controls.readings.addEventListener("change", scheduleRecompute);
  controls.shapes.forEach(input => input.addEventListener("input", scheduleRecompute));
  controls.tolerance.addEventListener("input", scheduleRecompute);

  const observer = new ResizeObserver(() => draw());
  observer.observe(root.querySelector(".plots"));
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", draw);
  recompute();
})();
