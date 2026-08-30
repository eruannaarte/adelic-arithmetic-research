#!/usr/bin/env node
"use strict";

/*
 * Outcome-blind throughput probe for the U2 full-evaluation feasibility note.
 *
 * This program deliberately does not import the U2 experiment, generators, or
 * result artifacts.  It builds a synthetic bounded-degree triangularized grid
 * with approximately the vertex/edge count of the largest registered family
 * and times only reusable numerical primitives.  Its output is a hardware
 * resource observation, never a scientific U2 record.
 */

const os = require("os");
const crypto = require("crypto");

function parsePositiveInteger(name, fallback) {
  const prefix = "--" + name + "=";
  const argument = process.argv.find(function (item) { return item.startsWith(prefix); });
  const value = argument ? Number(argument.slice(prefix.length)) : fallback;
  if (!Number.isSafeInteger(value) || value <= 0) throw new Error(name + " must be a positive integer");
  return value;
}

const ROWS = parsePositiveInteger("rows", 171);
const COLS = parsePositiveInteger("cols", 171);
const APPLY_REPEATS = parsePositiveInteger("apply-repeats", 256);
const DIJKSTRA_ROOTS = parsePositiveInteger("dijkstra-roots", 8);
const CG_CAP = parsePositiveInteger("cg-cap", 960);
const EXIT_SIDE = parsePositiveInteger("exit-side", 49);
const EXIT_REPEATS = parsePositiveInteger("exit-repeats", 8);

function nowSeconds() { return Number(process.hrtime.bigint()) / 1e9; }
function round(value, digits) {
  const scale = Math.pow(10, digits === undefined ? 6 : digits);
  return Math.round(value * scale) / scale;
}

function buildGrid(rows, cols) {
  const n = rows * cols;
  const neighbors = Array.from({ length: n }, function () { return []; });
  function id(row, col) { return row * cols + col; }
  function add(a, b, length) {
    neighbors[a].push([b, length]);
    neighbors[b].push([a, length]);
  }
  for (let row = 0; row < rows; row += 1) {
    for (let col = 0; col < cols; col += 1) {
      const here = id(row, col);
      if (col + 1 < cols) add(here, id(row, col + 1), 1);
      if (row + 1 < rows) add(here, id(row + 1, col), 1);
      if (row + 1 < rows && col + 1 < cols) add(here, id(row + 1, col + 1), Math.SQRT2);
    }
  }
  const offsets = new Uint32Array(n + 1);
  for (let i = 0; i < n; i += 1) offsets[i + 1] = offsets[i] + neighbors[i].length;
  const targets = new Uint32Array(offsets[n]);
  const lengths = new Float64Array(offsets[n]);
  for (let i = 0; i < n; i += 1) {
    neighbors[i].sort(function (a, b) { return a[0] - b[0]; });
    for (let j = 0; j < neighbors[i].length; j += 1) {
      targets[offsets[i] + j] = neighbors[i][j][0];
      lengths[offsets[i] + j] = neighbors[i][j][1];
    }
  }
  return { rows: rows, cols: cols, n: n, offsets: offsets, targets: targets, lengths: lengths, undirectedEdges: targets.length / 2 };
}

function applyLazy(graph, input, output) {
  const offsets = graph.offsets, targets = graph.targets;
  for (let i = 0; i < graph.n; i += 1) {
    let sum = 0;
    const start = offsets[i], end = offsets[i + 1];
    for (let p = start; p < end; p += 1) sum += input[targets[p]];
    output[i] = 0.5 * input[i] + 0.5 * sum / (end - start);
  }
}

class MinHeap {
  constructor() { this.nodes = []; this.values = []; }
  push(node, value) {
    let index = this.nodes.length;
    this.nodes.push(node); this.values.push(value);
    while (index > 0) {
      const parent = (index - 1) >> 1;
      if (this.values[parent] <= value) break;
      this.nodes[index] = this.nodes[parent]; this.values[index] = this.values[parent];
      index = parent;
    }
    this.nodes[index] = node; this.values[index] = value;
  }
  pop() {
    if (!this.nodes.length) return null;
    const node = this.nodes[0], value = this.values[0];
    const lastNode = this.nodes.pop(), lastValue = this.values.pop();
    if (this.nodes.length) {
      let index = 0;
      while (true) {
        const left = index * 2 + 1;
        if (left >= this.nodes.length) break;
        const right = left + 1;
        const child = right < this.nodes.length && this.values[right] < this.values[left] ? right : left;
        if (this.values[child] >= lastValue) break;
        this.nodes[index] = this.nodes[child]; this.values[index] = this.values[child];
        index = child;
      }
      this.nodes[index] = lastNode; this.values[index] = lastValue;
    }
    return [node, value];
  }
}

function dijkstra(graph, root) {
  const distance = new Float64Array(graph.n);
  distance.fill(Infinity); distance[root] = 0;
  const heap = new MinHeap(); heap.push(root, 0);
  while (heap.nodes.length) {
    const item = heap.pop(), node = item[0], value = item[1];
    if (value !== distance[node]) continue;
    for (let p = graph.offsets[node]; p < graph.offsets[node + 1]; p += 1) {
      const next = graph.targets[p], candidate = value + graph.lengths[p];
      if (candidate < distance[next]) { distance[next] = candidate; heap.push(next, candidate); }
    }
  }
  return distance;
}

function dot(a, b) {
  let sum = 0;
  for (let i = 0; i < a.length; i += 1) sum += a[i] * b[i];
  return sum;
}

function applyDirichlet(graph, input, output) {
  const cols = graph.cols;
  output.fill(0);
  for (let node = 0; node < graph.n; node += 1) {
    const col = node % cols;
    if (col === 0 || col === cols - 1) { output[node] = input[node]; continue; }
    let value = 0;
    for (let p = graph.offsets[node]; p < graph.offsets[node + 1]; p += 1) {
      const next = graph.targets[p];
      value += input[node];
      if (next % cols !== 0 && next % cols !== cols - 1) value -= input[next];
    }
    output[node] = value;
  }
}

function conjugateGradient(graph, cap, tolerance) {
  const n = graph.n, cols = graph.cols;
  const x = new Float64Array(n), b = new Float64Array(n), r = new Float64Array(n), p = new Float64Array(n), ap = new Float64Array(n);
  for (let node = 0; node < n; node += 1) {
    const col = node % cols;
    if (col === 0 || col === cols - 1) continue;
    for (let edge = graph.offsets[node]; edge < graph.offsets[node + 1]; edge += 1) if (graph.targets[edge] % cols === 0) b[node] += 1;
  }
  r.set(b); p.set(r);
  const initial = Math.sqrt(dot(r, r));
  let rr = dot(r, r), iteration = 0;
  for (; iteration < cap && Math.sqrt(rr) > tolerance * Math.max(1, initial); iteration += 1) {
    applyDirichlet(graph, p, ap);
    const denominator = dot(p, ap);
    if (!(denominator > 0)) break;
    const alpha = rr / denominator;
    for (let i = 0; i < n; i += 1) { x[i] += alpha * p[i]; r[i] -= alpha * ap[i]; }
    const next = dot(r, r), beta = next / rr;
    for (let i = 0; i < n; i += 1) p[i] = r[i] + beta * p[i];
    rr = next;
  }
  return { iterations: iteration, relativeResidual: Math.sqrt(rr) / Math.max(1, initial), checksum: round(dot(x, b), 9) };
}

function applyExitDirichlet(graph, input, output) {
  const rows = graph.rows, cols = graph.cols;
  output.fill(0);
  for (let node = 0; node < graph.n; node += 1) {
    const row = Math.floor(node / cols), col = node % cols;
    if (row === 0 || row === rows - 1 || col === 0 || col === cols - 1) { output[node] = input[node]; continue; }
    let value = 0;
    for (let p = graph.offsets[node]; p < graph.offsets[node + 1]; p += 1) {
      const next = graph.targets[p], nextRow = Math.floor(next / cols), nextCol = next % cols;
      value += input[node];
      if (nextRow !== 0 && nextRow !== rows - 1 && nextCol !== 0 && nextCol !== cols - 1) value -= input[next];
    }
    output[node] = value;
  }
}

function conjugateGradientExit(graph, cap, tolerance) {
  const n = graph.n, rows = graph.rows, cols = graph.cols;
  const x = new Float64Array(n), b = new Float64Array(n), r = new Float64Array(n), p = new Float64Array(n), ap = new Float64Array(n);
  for (let node = 0; node < n; node += 1) {
    const row = Math.floor(node / cols), col = node % cols;
    if (row !== 0 && row !== rows - 1 && col !== 0 && col !== cols - 1) b[node] = 2 * (graph.offsets[node + 1] - graph.offsets[node]);
  }
  r.set(b); p.set(r);
  const initial = Math.sqrt(dot(r, r));
  let rr = dot(r, r), iteration = 0;
  for (; iteration < cap && Math.sqrt(rr) > tolerance * Math.max(1, initial); iteration += 1) {
    applyExitDirichlet(graph, p, ap);
    const denominator = dot(p, ap);
    if (!(denominator > 0)) break;
    const alpha = rr / denominator;
    for (let i = 0; i < n; i += 1) { x[i] += alpha * p[i]; r[i] -= alpha * ap[i]; }
    const next = dot(r, r), beta = next / rr;
    for (let i = 0; i < n; i += 1) p[i] = r[i] + beta * p[i];
    rr = next;
  }
  return { iterations: iteration, relativeResidual: Math.sqrt(rr) / Math.max(1, initial), checksum: round(x[Math.floor(n / 2)], 9) };
}

function benchmark() {
  const started = nowSeconds();
  const graph = buildGrid(ROWS, COLS);
  const buildSeconds = nowSeconds() - started;

  let input = new Float64Array(graph.n), output = new Float64Array(graph.n);
  for (let i = 0; i < input.length; i += 1) input[i] = ((i * 2654435761) >>> 0) / 4294967296;
  applyLazy(graph, input, output);
  const applyStarted = nowSeconds();
  for (let repeat = 0; repeat < APPLY_REPEATS; repeat += 1) {
    applyLazy(graph, input, output);
    const swap = input; input = output; output = swap;
  }
  const applySeconds = nowSeconds() - applyStarted;

  let distanceChecksum = 0;
  const dijkstraStarted = nowSeconds();
  for (let root = 0; root < DIJKSTRA_ROOTS; root += 1) {
    const index = Math.floor((root + 1) * graph.n / (DIJKSTRA_ROOTS + 1));
    const distances = dijkstra(graph, index);
    distanceChecksum += distances[(index * 8191 + 17) % graph.n];
  }
  const dijkstraSeconds = nowSeconds() - dijkstraStarted;

  const cgStarted = nowSeconds();
  const cg = conjugateGradient(graph, CG_CAP, 1e-8);
  const cgSeconds = nowSeconds() - cgStarted;

  const exitGraph = buildGrid(EXIT_SIDE, EXIT_SIDE);
  const exitStarted = nowSeconds();
  let exit = null;
  for (let repeat = 0; repeat < EXIT_REPEATS; repeat += 1) exit = conjugateGradientExit(exitGraph, CG_CAP, 1e-8);
  const exitSeconds = nowSeconds() - exitStarted;
  const rss = process.memoryUsage();
  const payload = {
    schema: "ggii.u2.feasibility-benchmark/1",
    scientificOutcome: false,
    purpose: "synthetic numerical-kernel throughput only",
    environment: {
      platform: process.platform,
      arch: process.arch,
      node: process.version,
      cpuModel: os.cpus()[0] ? os.cpus()[0].model : "unknown",
      logicalCpus: os.cpus().length,
      totalMemoryBytes: os.totalmem()
    },
    syntheticGraph: {
      rows: graph.rows,
      cols: graph.cols,
      vertices: graph.n,
      undirectedEdges: graph.undirectedEdges,
      buildSeconds: round(buildSeconds)
    },
    sparseApply: {
      repeats: APPLY_REPEATS,
      seconds: round(applySeconds),
      undirectedEdgeApplicationsPerSecond: round(APPLY_REPEATS * graph.undirectedEdges / applySeconds, 0),
      checksum: round(input[Math.floor(input.length / 2)], 12)
    },
    dijkstra: {
      roots: DIJKSTRA_ROOTS,
      seconds: round(dijkstraSeconds),
      rootsPerSecond: round(DIJKSTRA_ROOTS / dijkstraSeconds),
      checksum: round(distanceChecksum, 9)
    },
    conjugateGradient: {
      cap: CG_CAP,
      seconds: round(cgSeconds),
      iterations: cg.iterations,
      relativeResidual: cg.relativeResidual,
      checksum: cg.checksum
    },
    exitBallSolve: {
      syntheticSide: EXIT_SIDE,
      vertices: exitGraph.n,
      undirectedEdges: exitGraph.undirectedEdges,
      repeats: EXIT_REPEATS,
      seconds: round(exitSeconds),
      solvesPerSecond: round(EXIT_REPEATS / exitSeconds),
      iterationsPerSolve: exit.iterations,
      relativeResidual: exit.relativeResidual,
      checksum: exit.checksum
    },
    processMemory: { rssBytes: rss.rss, heapUsedBytes: rss.heapUsed, externalBytes: rss.external }
  };
  payload.contentDigest = crypto.createHash("sha256").update(JSON.stringify(payload)).digest("hex");
  process.stdout.write(JSON.stringify(payload, null, 2) + "\n");
}

benchmark();
