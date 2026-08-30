/*
 * Global Geometry II — bounded obstruction-aware inverse compiler.
 *
 * This dependency-free slice certifies only finite intrinsic statements.  It
 * deliberately does not turn a Chow–Luo admission into an embedding or a
 * physical-sheet claim.  The closed-surface theorem is applied only after all
 * of its hypotheses have been checked, and an incomplete subset search can
 * never return PASS.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    var optionalG2 = null;
    try { optionalG2 = require("./global-geometry-ii-core.js"); } catch (ignored) { optionalG2 = null; }
    module.exports = factory(require("./global-geometry-core.js"), optionalG2);
  } else {
    root.GlobalGeometryIIInverse = factory(root.GlobalGeometryCore, root.GlobalGeometryII || null);
  }
})(typeof self !== "undefined" ? self : this, function (Base, G2) {
  "use strict";

  if (!Base) throw new Error("Global Geometry II inverse compiler requires GlobalGeometryCore.");

  var VERSION = "0.1.0-alpha.2";
  var SCHEMA_VERSION = 2;
  var PI = Math.PI;
  var TAU = 2 * PI;
  var MACHINE_EPSILON = Number.EPSILON || 2.220446049250313e-16;
  var DIGEST_ALGORITHM = "fnv1a32-ieee754-json-v1";
  var NUMERIC_MAGNITUDE_LIMIT = 1e100;
  var MAX_DATA_ITEMS = 50000;
  var MAX_EXPORTED_SUBSET_ROWS = 1024;
  var LIMITS = Object.freeze({
    maxVertices: 256,
    maxEdges: 1024,
    maxFaces: 1024,
    maxExactSubsetLimit: 18,
    maxSubsetEvaluations: 262142,
    maxExportedSubsetRows: MAX_EXPORTED_SUBSET_ROWS,
    maxIdentifierLength: 128,
    maxSeedLength: 256
  });
  var GATE_NAMES = [
    "schema, units, and finite bounds",
    "complex and surface validity",
    "local curvature upper bounds",
    "Gauss–Bonnet total",
    "Chow–Luo subset inequalities",
    "symmetric disk doubling",
    "metric positivity and triangle margin"
  ];
  var INVERSE_EVIDENCE_BASES = {
    "exact-finite-identity": ["combinatorial-identity", "theorem-instance", "exhaustive-finite-check"],
    "finite-numerical-estimate": ["optimization", "simulation", "refinement-study", "uncertainty-ensemble", "camera-estimate"],
    "research-target": ["continuum-limit", "general-inverse-design", "universality", "physical-validation"],
    "application-analogy": ["programmable-sheet", "growth-metric", "actuated-shell"]
  };

  function isPlainObject(value) {
    if (!value || typeof value !== "object" || Array.isArray(value)) return false;
    var prototype = Object.getPrototypeOf(value);
    if (prototype === null) return true;
    if (Object.getPrototypeOf(prototype) !== null) return false;
    var descriptor = Object.getOwnPropertyDescriptor(prototype, "constructor");
    return !!descriptor && Object.prototype.hasOwnProperty.call(descriptor, "value") &&
      typeof descriptor.value === "function" &&
      descriptor.value.prototype === prototype &&
      Function.prototype.toString.call(descriptor.value) === Function.prototype.toString.call(Object);
  }

  function finite(value) { return typeof value === "number" && isFinite(value); }

  function denseArray(value) {
    if (!Array.isArray(value) || Object.keys(value).length !== value.length) return false;
    for (var index = 0; index < value.length; index += 1) {
      if (!Object.prototype.hasOwnProperty.call(value, index)) return false;
    }
    return true;
  }

  function cloneCanonical(value, path, depth) {
    path = path || "root";
    depth = depth || 0;
    if (depth > 64) throw new Error(path + " exceeds canonical depth 64.");
    if (value === null || typeof value === "string" || typeof value === "boolean") return value;
    if (typeof value === "number") {
      if (!isFinite(value)) throw new Error("Cannot canonicalize a non-finite number.");
      return Object.is(value, -0) ? 0 : value;
    }
    if (Array.isArray(value)) {
      if (!denseArray(value)) throw new Error(path + " must be a dense index-only array.");
      if (value.length > MAX_DATA_ITEMS) throw new Error(path + " exceeds the canonical array bound.");
      return value.map(function (entry, index) { return cloneCanonical(entry, path + "[" + index + "]", depth + 1); });
    }
    if (isPlainObject(value)) {
      var object = {};
      if (Object.keys(value).length > 10000) throw new Error(path + " exceeds the canonical object-field bound.");
      Object.keys(value).sort().forEach(function (key) {
        if (key === "__proto__" || key === "prototype" || key === "constructor") throw new Error(path + " contains a forbidden key.");
        if (typeof value[key] === "undefined" || typeof value[key] === "function") {
          throw new Error("Cannot canonicalize unsupported member " + key + ".");
        }
        object[key] = cloneCanonical(value[key], path + "." + key, depth + 1);
      });
      return object;
    }
    throw new Error("Cannot canonicalize an unsupported value.");
  }

  function stableStringify(value) {
    return JSON.stringify(cloneCanonical(value));
  }

  function fallbackDigest(text) {
    var hash = 2166136261 >>> 0;
    for (var i = 0; i < text.length; i += 1) {
      hash ^= text.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return ("00000000" + (hash >>> 0).toString(16)).slice(-8);
  }

  function digestValue(value) {
    return fallbackDigest(stableStringify(value));
  }

  function deepFreeze(value) {
    if (!value || typeof value !== "object" || Object.isFrozen(value)) return value;
    Object.keys(value).forEach(function (key) { deepFreeze(value[key]); });
    return Object.freeze(value);
  }

  function unknownKeys(object, allowed, path, errors) {
    if (!isPlainObject(object)) return;
    Object.keys(object).sort().forEach(function (key) {
      if (allowed.indexOf(key) < 0) addError(errors, path + "." + key, "SCHEMA_INVALID", "unknown field");
    });
  }

  function addError(errors, path, code, message) {
    errors.push({ path: path, code: code, message: message });
  }

  function preflightData(value) {
    var errors = [], itemCount = 0;
    function visit(item, path, depth) {
      itemCount += 1;
      if (itemCount > MAX_DATA_ITEMS) {
        if (!errors.some(function (error) { return error.code === "RESOURCE_BOUND_EXCEEDED"; })) addError(errors, path, "RESOURCE_BOUND_EXCEEDED", "request data exceeds the bounded item budget " + MAX_DATA_ITEMS);
        return;
      }
      if (depth > 32) { addError(errors, path, "RESOURCE_BOUND_EXCEEDED", "request nesting exceeds depth 32"); return; }
      if (item === null || typeof item === "string" || typeof item === "boolean") return;
      if (typeof item === "number") {
        if (!isFinite(item)) addError(errors, path, "NONFINITE_VALUE", "must be finite");
        return;
      }
      if (Array.isArray(item)) {
        if (!denseArray(item)) { addError(errors, path, "SCHEMA_INVALID", "must be a dense index-only array"); return; }
        if (Object.getOwnPropertySymbols(item).length) { addError(errors, path, "SCHEMA_INVALID", "symbol-keyed fields are not accepted"); return; }
        var descriptors = Object.getOwnPropertyDescriptors(item);
        for (var index = 0; index < item.length && itemCount <= MAX_DATA_ITEMS; index += 1) {
          var descriptor = descriptors[String(index)];
          if (!descriptor || !Object.prototype.hasOwnProperty.call(descriptor, "value")) addError(errors, path + "[" + index + "]", "SCHEMA_INVALID", "accessors are not accepted");
          else visit(descriptor.value, path + "[" + index + "]", depth + 1);
        }
        return;
      }
      if (!isPlainObject(item)) { addError(errors, path, "SCHEMA_INVALID", "must contain only plain data objects"); return; }
      if (Object.getOwnPropertySymbols(item).length) { addError(errors, path, "SCHEMA_INVALID", "symbol-keyed fields are not accepted"); return; }
      var keys = Object.keys(item);
      var objectDescriptors = Object.getOwnPropertyDescriptors(item);
      keys.forEach(function (key) {
        if (key === "__proto__" || key === "prototype" || key === "constructor") {
          addError(errors, path + "." + key, "SCHEMA_INVALID", "forbidden object key");
          return;
        }
        var descriptor = objectDescriptors[key];
        if (!descriptor || !Object.prototype.hasOwnProperty.call(descriptor, "value")) addError(errors, path + "." + key, "SCHEMA_INVALID", "accessors are not accepted");
        else if (itemCount <= MAX_DATA_ITEMS) visit(descriptor.value, path + "." + key, depth + 1);
      });
    }
    visit(value, "root", 0);
    return errors;
  }

  function edgeKey(a, b) { return a < b ? a + ":" + b : b + ":" + a; }

  function compareNumberArrays(a, b) {
    for (var i = 0; i < Math.min(a.length, b.length); i += 1) {
      if (a[i] !== b[i]) return a[i] - b[i];
    }
    return a.length - b.length;
  }

  function bigintAbs(value) { return value < 0n ? -value : value; }

  function bigintGcd(a, b) {
    a = bigintAbs(a); b = bigintAbs(b);
    while (b !== 0n) { var remainder = a % b; a = b; b = remainder; }
    return a || 1n;
  }

  function rational(numerator, denominator) {
    var n = typeof numerator === "bigint" ? numerator : BigInt(numerator);
    var d = typeof denominator === "bigint" ? denominator : BigInt(denominator);
    if (d === 0n) throw new Error("A rational denominator cannot be zero.");
    if (d < 0n) { n = -n; d = -d; }
    var divisor = bigintGcd(n, d);
    return { n: n / divisor, d: d / divisor };
  }

  function rationalAdd(a, b) { return rational(a.n * b.d + b.n * a.d, a.d * b.d); }
  function rationalCompare(a, b) {
    var difference = a.n * b.d - b.n * a.d;
    return difference < 0n ? -1 : difference > 0n ? 1 : 0;
  }
  function rationalNumber(a) { return Number(a.n) / Number(a.d); }
  function rationalJSON(a) {
    var max = BigInt(Number.MAX_SAFE_INTEGER);
    return {
      numerator: bigintAbs(a.n) <= max ? Number(a.n) : a.n.toString(),
      denominator: a.d <= max ? Number(a.d) : a.d.toString()
    };
  }

  function normalizeNode(node, index, errors) {
    var path = "root.target.discretization.complex.nodes[" + index + "]";
    if (!isPlainObject(node)) {
      addError(errors, path, "SCHEMA_INVALID", "node must be an object");
      return { id: index, label: String(index), x: 0, y: 0, z: 0, radius: 1 };
    }
    unknownKeys(node, ["id", "label", "x", "y", "z", "radius", "value", "u", "v"], path, errors);
    ["x", "y", "z", "radius", "value", "u", "v"].forEach(function (field) {
      if (node[field] != null && !finite(node[field])) addError(errors, path + "." + field, "NONFINITE_VALUE", "must be finite");
      else if (finite(node[field]) && Math.abs(node[field]) > NUMERIC_MAGNITUDE_LIMIT) addError(errors, path + "." + field, "ARITHMETIC_UNSAFE", "magnitude exceeds the compiler arithmetic bound");
    });
    if (node.radius != null && finite(node.radius) && node.radius <= 0) addError(errors, path + ".radius", "SCHEMA_INVALID", "must be positive");
    if (node.label != null && (typeof node.label !== "string" || node.label.length > 256)) addError(errors, path + ".label", "SCHEMA_INVALID", "must be a string of at most 256 characters");
    if (node.id != null && typeof node.id !== "string" && !Number.isInteger(node.id)) addError(errors, path + ".id", "SCHEMA_INVALID", "must be a string or integer");
    return {
      id: index,
      label: node.label == null ? String(node.id == null ? index : node.id) : node.label,
      x: finite(node.x) ? node.x : 0,
      y: finite(node.y) ? node.y : 0,
      z: finite(node.z) ? node.z : 0,
      radius: finite(node.radius) && node.radius > 0 ? node.radius : 1
    };
  }

  function normalizeComplex(raw, errors) {
    var path = "root.target.discretization.complex";
    if (!isPlainObject(raw)) {
      addError(errors, path, "SCHEMA_INVALID", "must be an object");
      return null;
    }
    unknownKeys(raw, ["nodes", "vertices", "edges", "faces", "metadata"], path, errors);
    if (raw.nodes != null && raw.vertices != null) addError(errors, path, "SCHEMA_INVALID", "use nodes or vertices, not both");
    var rawNodes = raw.nodes || raw.vertices;
    if (!denseArray(rawNodes) || rawNodes.length === 0) {
      addError(errors, path + ".nodes", "SCHEMA_INVALID", "must be a non-empty dense array");
      return null;
    }
    if (rawNodes.length > LIMITS.maxVertices) addError(errors, path + ".nodes", "RESOURCE_BOUND_EXCEEDED", "vertex count exceeds " + LIMITS.maxVertices);
    var nodes = rawNodes.slice(0, LIMITS.maxVertices).map(function (node, index) { return normalizeNode(node, index, errors); });
    var ids = Object.create(null);
    rawNodes.slice(0, LIMITS.maxVertices).forEach(function (node, index) {
      var id = isPlainObject(node) && node.id != null ? typeof node.id + ":" + String(node.id) : "index:" + index;
      if (ids[id] != null) addError(errors, path + ".nodes[" + index + "].id", "SCHEMA_INVALID", "duplicate node id also used at index " + ids[id]);
      ids[id] = index;
    });
    if (!denseArray(raw.faces)) addError(errors, path + ".faces", "SCHEMA_INVALID", "must be a dense array");
    if (denseArray(raw.faces) && raw.faces.length > LIMITS.maxFaces) addError(errors, path + ".faces", "RESOURCE_BOUND_EXCEEDED", "face count exceeds " + LIMITS.maxFaces);
    var faces = [];
    (denseArray(raw.faces) ? raw.faces.slice(0, LIMITS.maxFaces) : []).forEach(function (face, index) {
      var facePath = path + ".faces[" + index + "]";
      if (!denseArray(face) || face.length !== 3) {
        addError(errors, facePath, "SCHEMA_INVALID", "must contain exactly three vertex indices");
        return;
      }
      var values = face.slice();
      values.forEach(function (vertex, local) {
        if (!Number.isInteger(vertex) || vertex < 0 || vertex >= nodes.length) addError(errors, facePath + "[" + local + "]", "SCHEMA_INVALID", "must be an in-range integer vertex index");
      });
      if (values.every(function (vertex) { return Number.isInteger(vertex) && vertex >= 0 && vertex < nodes.length; })) {
        faces.push(values.slice().sort(function (a, b) { return a - b; }));
      }
    });
    faces.sort(compareNumberArrays);

    var rawEdges = raw.edges;
    var derived = rawEdges == null;
    if (rawEdges != null && !denseArray(rawEdges)) addError(errors, path + ".edges", "SCHEMA_INVALID", "must be a dense array when supplied");
    if (denseArray(rawEdges) && rawEdges.length > LIMITS.maxEdges) addError(errors, path + ".edges", "RESOURCE_BOUND_EXCEEDED", "edge count exceeds " + LIMITS.maxEdges);
    var edgeRecords = [];
    if (denseArray(rawEdges)) {
      rawEdges.slice(0, LIMITS.maxEdges).forEach(function (edge, index) {
        var edgePath = path + ".edges[" + index + "]";
        var a, b, length = 1, weight = 1;
        if (denseArray(edge)) {
          if (edge.length < 2 || edge.length > 4) addError(errors, edgePath, "SCHEMA_INVALID", "edge array must contain two to four values");
          a = edge[0]; b = edge[1];
          if (edge[2] != null) length = edge[2];
          if (edge[3] != null) weight = edge[3];
        } else if (isPlainObject(edge)) {
          unknownKeys(edge, ["source", "target", "length", "weight"], edgePath, errors);
          a = edge.source; b = edge.target;
          if (edge.length != null) length = edge.length;
          if (edge.weight != null) weight = edge.weight;
        } else {
          addError(errors, edgePath, "SCHEMA_INVALID", "edge must be an array or object");
        }
        if (!Number.isInteger(a) || a < 0 || a >= nodes.length) addError(errors, edgePath + ".source", "SCHEMA_INVALID", "must be an in-range integer vertex index");
        if (!Number.isInteger(b) || b < 0 || b >= nodes.length) addError(errors, edgePath + ".target", "SCHEMA_INVALID", "must be an in-range integer vertex index");
        if (!finite(length)) addError(errors, edgePath + ".length", "NONFINITE_VALUE", "must be finite");
        if (!finite(weight)) addError(errors, edgePath + ".weight", "NONFINITE_VALUE", "must be finite");
        if (Number.isInteger(a) && Number.isInteger(b) && a >= 0 && b >= 0 && a < nodes.length && b < nodes.length) {
          edgeRecords.push({ source: Math.min(a, b), target: Math.max(a, b), length: length, weight: weight, originalIndex: index });
        }
      });
    } else {
      var derivedMap = Object.create(null);
      faces.forEach(function (face) {
        [[face[0], face[1]], [face[1], face[2]], [face[2], face[0]]].forEach(function (pair) {
          var key = edgeKey(pair[0], pair[1]);
          if (!derivedMap[key]) derivedMap[key] = { source: Math.min(pair[0], pair[1]), target: Math.max(pair[0], pair[1]), length: 1, weight: 1, originalIndex: Object.keys(derivedMap).length };
        });
      });
      edgeRecords = Object.keys(derivedMap).map(function (key) { return derivedMap[key]; });
      if (edgeRecords.length > LIMITS.maxEdges) {
        addError(errors, path + ".edges", "RESOURCE_BOUND_EXCEEDED", "derived edge count exceeds " + LIMITS.maxEdges);
        edgeRecords = edgeRecords.slice(0, LIMITS.maxEdges);
      }
    }
    edgeRecords.sort(function (a, b) { return a.source - b.source || a.target - b.target || a.originalIndex - b.originalIndex; });
    if (derived) edgeRecords.forEach(function (edge, index) { edge.originalIndex = index; });
    var edges = edgeRecords.map(function (edge) { return { source: edge.source, target: edge.target, length: edge.length, weight: edge.weight }; });
    return {
      complex: { nodes: nodes, edges: edges, faces: faces },
      edgeOriginalIndices: edgeRecords.map(function (edge) { return edge.originalIndex; }),
      edgesDerived: derived
    };
  }

  function normalizeTopology(raw, errors) {
    var path = "root.target.topology";
    if (!isPlainObject(raw)) {
      addError(errors, path, "SCHEMA_INVALID", "must be an object");
      return { surface: "custom", orientable: true, boundaryComponents: 0 };
    }
    unknownKeys(raw, ["surface", "orientable", "boundaryComponents", "expectedBetti"], path, errors);
    var surfaces = ["disk", "sphere", "annulus", "torus", "custom"];
    if (surfaces.indexOf(raw.surface) < 0) addError(errors, path + ".surface", "SCHEMA_INVALID", "unsupported surface label");
    if (typeof raw.orientable !== "boolean") addError(errors, path + ".orientable", "SCHEMA_INVALID", "must be boolean");
    if (!Number.isInteger(raw.boundaryComponents) || raw.boundaryComponents < 0 || raw.boundaryComponents > 64) addError(errors, path + ".boundaryComponents", "SCHEMA_INVALID", "must be an integer in [0, 64]");
    var expectedBetti = null;
    if (raw.expectedBetti != null) {
      if (!denseArray(raw.expectedBetti) || raw.expectedBetti.length !== 3 || raw.expectedBetti.some(function (value) { return !Number.isInteger(value) || value < 0 || value > LIMITS.maxVertices; })) {
        addError(errors, path + ".expectedBetti", "SCHEMA_INVALID", "must be three bounded nonnegative integers");
      } else expectedBetti = raw.expectedBetti.slice();
    }
    var canonicalBySurface = { disk: [1, 0, 0], sphere: [1, 0, 1], annulus: [1, 1, 0], torus: [1, 2, 1] };
    var boundaryBySurface = { disk: 1, sphere: 0, annulus: 2, torus: 0 };
    if (raw.surface === "custom" && !expectedBetti) addError(errors, path + ".expectedBetti", "SCHEMA_INVALID", "is required for custom topology");
    if (canonicalBySurface[raw.surface] && expectedBetti && expectedBetti.some(function (value, index) { return value !== canonicalBySurface[raw.surface][index]; })) addError(errors, path + ".expectedBetti", "TOPOLOGY_MISMATCH", "must agree with named surface Betti numbers " + canonicalBySurface[raw.surface].join(","));
    if (boundaryBySurface[raw.surface] != null && raw.boundaryComponents !== boundaryBySurface[raw.surface]) addError(errors, path + ".boundaryComponents", "TOPOLOGY_MISMATCH", "must agree with named surface boundary count " + boundaryBySurface[raw.surface]);
    if (canonicalBySurface[raw.surface] && raw.orientable !== true) addError(errors, path + ".orientable", "TOPOLOGY_MISMATCH", "the registered named surface is orientable");
    return {
      surface: surfaces.indexOf(raw.surface) >= 0 ? raw.surface : "custom",
      orientable: typeof raw.orientable === "boolean" ? raw.orientable : true,
      boundaryComponents: Number.isInteger(raw.boundaryComponents) ? raw.boundaryComponents : 0,
      expectedBetti: expectedBetti
    };
  }

  function normalizeCurvature(raw, nodeCount, errors) {
    var path = "root.target.curvature";
    if (!isPlainObject(raw)) {
      addError(errors, path, "SCHEMA_INVALID", "is required for intrinsic-curvature targets");
      return null;
    }
    unknownKeys(raw, ["basis", "values", "piCoefficients", "procedural", "parameters"], path, errors);
    var bases = ["vertex", "procedural", "symbolic-pi"];
    if (bases.indexOf(raw.basis) < 0) addError(errors, path + ".basis", "SCHEMA_INVALID", "unsupported curvature basis");
    if (raw.basis === "vertex") {
      if (!denseArray(raw.values) || raw.values.length !== nodeCount) addError(errors, path + ".values", "SCHEMA_INVALID", "must have one value per vertex in a dense array");
      (denseArray(raw.values) ? raw.values : []).forEach(function (value, index) {
        if (!finite(value)) addError(errors, path + ".values[" + index + "]", "NONFINITE_VALUE", "must be finite");
        else if (Math.abs(value) > NUMERIC_MAGNITUDE_LIMIT) addError(errors, path + ".values[" + index + "]", "ARITHMETIC_UNSAFE", "magnitude exceeds the compiler arithmetic bound");
      });
      if (raw.piCoefficients != null || raw.procedural != null || raw.parameters != null) addError(errors, path, "SCHEMA_INVALID", "vertex basis cannot include symbolic or procedural fields");
      return { basis: "vertex", values: denseArray(raw.values) ? raw.values.slice() : [] };
    }
    if (raw.basis === "symbolic-pi") {
      if (!denseArray(raw.piCoefficients) || raw.piCoefficients.length !== nodeCount) addError(errors, path + ".piCoefficients", "SCHEMA_INVALID", "must have one rational coefficient per vertex in a dense array");
      var coefficients = (denseArray(raw.piCoefficients) ? raw.piCoefficients : []).map(function (coefficient, index) {
        var coefficientPath = path + ".piCoefficients[" + index + "]";
        if (!isPlainObject(coefficient)) {
          addError(errors, coefficientPath, "SCHEMA_INVALID", "must be a rational object");
          return { numerator: 0, denominator: 1 };
        }
        unknownKeys(coefficient, ["numerator", "denominator"], coefficientPath, errors);
        if (!Number.isSafeInteger(coefficient.numerator) || Math.abs(coefficient.numerator) > 1000000000) addError(errors, coefficientPath + ".numerator", "SCHEMA_INVALID", "must be a safe integer with magnitude at most 1e9");
        if (!Number.isSafeInteger(coefficient.denominator) || coefficient.denominator <= 0 || coefficient.denominator > 1000000000) addError(errors, coefficientPath + ".denominator", "SCHEMA_INVALID", "must be an integer in [1, 1e9]");
        if (Number.isSafeInteger(coefficient.numerator) && Number.isSafeInteger(coefficient.denominator) && coefficient.denominator > 0) {
          return rationalJSON(rational(coefficient.numerator, coefficient.denominator));
        }
        return { numerator: 0, denominator: 1 };
      });
      if (raw.values != null || raw.procedural != null || raw.parameters != null) addError(errors, path, "SCHEMA_INVALID", "symbolic-pi basis cannot include vertex or procedural fields");
      return { basis: "symbolic-pi", piCoefficients: coefficients };
    }
    if (raw.basis === "procedural") {
      if (raw.procedural !== "uniform") addError(errors, path + ".procedural", "UNSUPPORTED_TARGET_CLASS", "Slice I currently supports only the uniform procedural curvature target");
      if (raw.parameters != null && (!isPlainObject(raw.parameters) || Object.keys(raw.parameters).length)) addError(errors, path + ".parameters", "SCHEMA_INVALID", "uniform procedural curvature takes no parameters");
      if (raw.values != null || raw.piCoefficients != null) addError(errors, path, "SCHEMA_INVALID", "procedural basis cannot include explicit values");
      return { basis: "procedural", procedural: raw.procedural, parameters: {} };
    }
    return null;
  }

  function normalizeBounds(value, path, fallback, errors) {
    if (value == null) return fallback.slice();
    if (!denseArray(value) || value.length !== 2 || !finite(value[0]) || !finite(value[1]) || value[0] <= 0 || value[0] > value[1]) {
      addError(errors, path, "SCHEMA_INVALID", "must be two finite positive ascending bounds in a dense array");
      return fallback.slice();
    }
    if (value[0] < 1 / NUMERIC_MAGNITUDE_LIMIT || value[1] > NUMERIC_MAGNITUDE_LIMIT) {
      addError(errors, path, "ARITHMETIC_UNSAFE", "bounds must lie in [1e-100, 1e100]");
      return fallback.slice();
    }
    return value.slice();
  }

  function normalizeRequest(raw) {
    var errors = [];
    var preflightErrors = preflightData(raw);
    if (preflightErrors.length) {
      preflightErrors.sort(function (a, b) { return a.path.localeCompare(b.path) || a.code.localeCompare(b.code) || a.message.localeCompare(b.message); });
      return { valid: false, errors: preflightErrors, normalized: null };
    }
    if (!isPlainObject(raw)) {
      addError(errors, "root", "SCHEMA_INVALID", "request must be an object");
      return { valid: false, errors: errors, normalized: null };
    }
    unknownKeys(raw, ["schemaVersion", "id", "seed", "target", "models", "constraints", "verification", "fabrication"], "root", errors);
    if (raw.schemaVersion !== SCHEMA_VERSION) addError(errors, "root.schemaVersion", "SCHEMA_INVALID", "must equal 2");
    if (typeof raw.id !== "string" || !/^[a-z0-9][a-z0-9._:-]{2,127}$/i.test(raw.id)) addError(errors, "root.id", "SCHEMA_INVALID", "must be a stable identifier of 3 to 128 characters");
    if (typeof raw.seed !== "string" || raw.seed.length === 0 || raw.seed.length > LIMITS.maxSeedLength) addError(errors, "root.seed", "SCHEMA_INVALID", "must be a non-empty string of at most 256 characters");

    var target = raw.target;
    if (!isPlainObject(target)) {
      addError(errors, "root.target", "SCHEMA_INVALID", "must be an object");
      target = {};
    }
    unknownKeys(target, ["kind", "topology", "discretization", "curvature", "edgeLengths", "embedding", "dimensionProfile"], "root.target", errors);
    var knownKinds = ["intrinsic-curvature", "intrinsic-edge-metric", "extrinsic-embedding", "dimension-profile"];
    if (knownKinds.indexOf(target.kind) < 0) addError(errors, "root.target.kind", "SCHEMA_INVALID", "unknown target kind");
    if (target.kind === "extrinsic-embedding" || target.kind === "dimension-profile") addError(errors, "root.target.kind", "UNSUPPORTED_TARGET_CLASS", "this intrinsic Slice I compiler does not synthesize the requested target class");
    var topology = normalizeTopology(target.topology, errors);
    var discretization = target.discretization;
    if (!isPlainObject(discretization)) {
      addError(errors, "root.target.discretization", "SCHEMA_INVALID", "must be an object");
      discretization = {};
    }
    unknownKeys(discretization, ["generator", "complex"], "root.target.discretization", errors);
    if (discretization.generator != null) addError(errors, "root.target.discretization.generator", "UNSUPPORTED_TARGET_CLASS", "Slice I requires an explicit finite complex");
    var complexInfo = normalizeComplex(discretization.complex, errors);
    var nodeCount = complexInfo ? complexInfo.complex.nodes.length : 0;
    var edgeCount = complexInfo ? complexInfo.complex.edges.length : 0;
    var curvature = target.kind === "intrinsic-curvature" ? normalizeCurvature(target.curvature, nodeCount, errors) : null;
    if (target.kind !== "intrinsic-curvature" && target.curvature != null) addError(errors, "root.target.curvature", "SCHEMA_INVALID", "curvature is only accepted for intrinsic-curvature targets in Slice I");

    var models = raw.models;
    var knownModels = ["circle-packing-tangency", "circle-packing-weighted", "edge-metric", "equilateral-valence", "elastic-shell"];
    if (!denseArray(models) || models.length !== 1) addError(errors, "root.models", "UNSUPPORTED_TARGET_CLASS", "Slice I requires exactly one declared model in a dense array");
    (denseArray(models) ? models : []).forEach(function (model, index) {
      if (knownModels.indexOf(model) < 0) addError(errors, "root.models[" + index + "]", "SCHEMA_INVALID", "unknown model");
      else if (["circle-packing-tangency", "circle-packing-weighted", "edge-metric"].indexOf(model) < 0) addError(errors, "root.models[" + index + "]", "UNSUPPORTED_TARGET_CLASS", "model is outside this exact intrinsic slice");
    });
    var model = denseArray(models) && models.length ? models[0] : null;
    if (target.kind === "intrinsic-curvature" && ["circle-packing-tangency", "circle-packing-weighted"].indexOf(model) < 0) addError(errors, "root.models[0]", "UNSUPPORTED_TARGET_CLASS", "intrinsic-curvature Slice I currently requires Model CP");
    if (target.kind === "intrinsic-edge-metric" && model !== "edge-metric") addError(errors, "root.models[0]", "UNSUPPORTED_TARGET_CLASS", "intrinsic-edge-metric Slice I requires edge-metric model");

    var constraints = raw.constraints;
    if (!isPlainObject(constraints)) {
      addError(errors, "root.constraints", "SCHEMA_INVALID", "must be an object");
      constraints = {};
    }
    unknownKeys(constraints, ["phiByEdge", "radiusBounds", "edgeLengthBounds", "allowedInteriorValences", "allowedBoundaryValences", "maxStrain", "allowTopologyChange"], "root.constraints", errors);
    var radiusBounds = normalizeBounds(constraints.radiusBounds, "root.constraints.radiusBounds", [0.05, 20], errors);
    var edgeLengthBounds = normalizeBounds(constraints.edgeLengthBounds, "root.constraints.edgeLengthBounds", [1e-9, 1e9], errors);
    if (constraints.allowTopologyChange != null && typeof constraints.allowTopologyChange !== "boolean") addError(errors, "root.constraints.allowTopologyChange", "SCHEMA_INVALID", "must be boolean");
    if (constraints.maxStrain != null && (!finite(constraints.maxStrain) || constraints.maxStrain < 0 || constraints.maxStrain > 10)) addError(errors, "root.constraints.maxStrain", "SCHEMA_INVALID", "must be finite and in [0, 10]");
    ["allowedInteriorValences", "allowedBoundaryValences"].forEach(function (field) {
      if (constraints[field] != null && (!denseArray(constraints[field]) || constraints[field].length > 64 || constraints[field].some(function (value) { return !Number.isInteger(value) || value < 1 || value > 1000; }))) addError(errors, "root.constraints." + field, "SCHEMA_INVALID", "must be a bounded dense array of positive integers");
    });
    var phiInput = constraints.phiByEdge;
    if (model === "circle-packing-weighted") {
      if (!denseArray(phiInput) || phiInput.length !== edgeCount) addError(errors, "root.constraints.phiByEdge", "SCHEMA_INVALID", "weighted Model CP requires one angle per canonical edge in a dense array");
    } else if (phiInput != null && (!denseArray(phiInput) || phiInput.length !== edgeCount)) addError(errors, "root.constraints.phiByEdge", "SCHEMA_INVALID", "must have one value per edge in a dense array");
    (denseArray(phiInput) ? phiInput : []).forEach(function (value, index) {
      if (!finite(value)) addError(errors, "root.constraints.phiByEdge[" + index + "]", "NONFINITE_VALUE", "must be finite");
      else if (value < 0 || value > PI / 2) addError(errors, "root.constraints.phiByEdge[" + index + "]", "SCHEMA_INVALID", "must lie in [0, π/2]");
      else if (model === "circle-packing-tangency" && value !== 0) addError(errors, "root.constraints.phiByEdge[" + index + "]", "SCHEMA_INVALID", "tangency requires Phi=0");
    });
    var sortedPhi = new Array(edgeCount).fill(0);
    if (denseArray(phiInput) && complexInfo) complexInfo.edgeOriginalIndices.forEach(function (oldIndex, newIndex) { sortedPhi[newIndex] = phiInput[oldIndex]; });

    var edgeLengths = null;
    if (target.kind === "intrinsic-edge-metric") {
      if (!denseArray(target.edgeLengths) || target.edgeLengths.length !== edgeCount) addError(errors, "root.target.edgeLengths", "SCHEMA_INVALID", "must have one length per edge in a dense array");
      (denseArray(target.edgeLengths) ? target.edgeLengths : []).forEach(function (value, index) {
        if (!finite(value)) addError(errors, "root.target.edgeLengths[" + index + "]", "NONFINITE_VALUE", "must be finite");
        else if (value <= 0) addError(errors, "root.target.edgeLengths[" + index + "]", "SCHEMA_INVALID", "must be positive");
        else if (value < 1 / NUMERIC_MAGNITUDE_LIMIT || value > NUMERIC_MAGNITUDE_LIMIT) addError(errors, "root.target.edgeLengths[" + index + "]", "ARITHMETIC_UNSAFE", "must lie in [1e-100, 1e100]");
      });
      edgeLengths = new Array(edgeCount).fill(0);
      if (denseArray(target.edgeLengths) && complexInfo) complexInfo.edgeOriginalIndices.forEach(function (oldIndex, newIndex) { edgeLengths[newIndex] = target.edgeLengths[oldIndex]; });
    } else if (target.edgeLengths != null) addError(errors, "root.target.edgeLengths", "SCHEMA_INVALID", "edgeLengths is only accepted for intrinsic-edge-metric targets");
    if (target.embedding != null || target.dimensionProfile != null) addError(errors, "root.target", "UNSUPPORTED_TARGET_CLASS", "embedding and dimension-profile payloads are not consumed by Slice I");

    var verification = raw.verification;
    if (!isPlainObject(verification)) {
      addError(errors, "root.verification", "SCHEMA_INVALID", "must be an object");
      verification = {};
    }
    unknownKeys(verification, ["gbTolerance", "chowLuoGuard", "exactSubsetLimit", "optimizerTolerance", "maxIterations", "refinementLevels", "uncertaintySamples", "uncertaintyModel"], "root.verification", errors);
    var gbTolerance = verification.gbTolerance == null ? 0 : verification.gbTolerance;
    if (!finite(gbTolerance) || gbTolerance < 0 || gbTolerance > 1e-6) addError(errors, "root.verification.gbTolerance", "SCHEMA_INVALID", "must be finite and in [0, 1e-6]");
    var chowLuoGuard = verification.chowLuoGuard == null ? 1e-8 : verification.chowLuoGuard;
    if (!finite(chowLuoGuard) || chowLuoGuard <= 0 || chowLuoGuard > 1) addError(errors, "root.verification.chowLuoGuard", "SCHEMA_INVALID", "must be finite and in (0, 1]");
    var exactSubsetLimit = verification.exactSubsetLimit == null ? LIMITS.maxExactSubsetLimit : verification.exactSubsetLimit;
    if (!Number.isInteger(exactSubsetLimit) || exactSubsetLimit < 1) addError(errors, "root.verification.exactSubsetLimit", "SCHEMA_INVALID", "must be a positive integer");
    else if (exactSubsetLimit > LIMITS.maxExactSubsetLimit) addError(errors, "root.verification.exactSubsetLimit", "RESOURCE_BOUND_EXCEEDED", "exceeds bounded exhaustive limit " + LIMITS.maxExactSubsetLimit);
    var optimizerTolerance = verification.optimizerTolerance == null ? 1e-8 : verification.optimizerTolerance;
    if (!finite(optimizerTolerance) || optimizerTolerance <= 0 || optimizerTolerance > 1) addError(errors, "root.verification.optimizerTolerance", "SCHEMA_INVALID", "must be finite and in (0, 1]");
    var maxIterations = verification.maxIterations == null ? 0 : verification.maxIterations;
    if (!Number.isInteger(maxIterations) || maxIterations < 0 || maxIterations > 100000) addError(errors, "root.verification.maxIterations", "SCHEMA_INVALID", "must be an integer in [0, 100000]");
    var refinementLevels = verification.refinementLevels == null ? 0 : verification.refinementLevels;
    if (!Number.isInteger(refinementLevels) || refinementLevels < 0 || refinementLevels > 16) addError(errors, "root.verification.refinementLevels", "SCHEMA_INVALID", "must be an integer in [0, 16]");
    var uncertaintySamples = verification.uncertaintySamples == null ? 0 : verification.uncertaintySamples;
    if (!Number.isInteger(uncertaintySamples) || uncertaintySamples < 0 || uncertaintySamples > 100000) addError(errors, "root.verification.uncertaintySamples", "SCHEMA_INVALID", "must be an integer in [0, 100000]");
    if (verification.uncertaintyModel != null) addError(errors, "root.verification.uncertaintyModel", "UNSUPPORTED_TARGET_CLASS", "uncertainty ensembles are not run in Slice I");
    if (raw.fabrication != null) addError(errors, "root.fabrication", "UNSUPPORTED_TARGET_CLASS", "fabrication is a downstream slice and is not consumed here");

    errors.sort(function (a, b) { return a.path.localeCompare(b.path) || a.code.localeCompare(b.code) || a.message.localeCompare(b.message); });
    if (errors.length) return { valid: false, errors: errors, normalized: null };
    var normalizedTarget = {
      kind: target.kind,
      topology: topology,
      discretization: { complex: complexInfo.complex }
    };
    if (curvature) normalizedTarget.curvature = curvature;
    if (edgeLengths) normalizedTarget.edgeLengths = edgeLengths;
    var normalized = {
      schemaVersion: SCHEMA_VERSION,
      id: raw.id,
      seed: raw.seed,
      target: normalizedTarget,
      models: [model],
      constraints: {
        phiByEdge: sortedPhi,
        radiusBounds: radiusBounds,
        edgeLengthBounds: edgeLengthBounds,
        allowedInteriorValences: (constraints.allowedInteriorValences || []).slice().sort(function (a, b) { return a - b; }),
        allowedBoundaryValences: (constraints.allowedBoundaryValences || []).slice().sort(function (a, b) { return a - b; }),
        maxStrain: constraints.maxStrain == null ? 0.1 : constraints.maxStrain,
        allowTopologyChange: constraints.allowTopologyChange === true
      },
      verification: {
        gbTolerance: gbTolerance,
        chowLuoGuard: chowLuoGuard,
        exactSubsetLimit: exactSubsetLimit,
        optimizerTolerance: optimizerTolerance,
        maxIterations: maxIterations,
        refinementLevels: refinementLevels,
        uncertaintySamples: uncertaintySamples
      }
    };
    return { valid: true, errors: [], normalized: cloneCanonical(normalized) };
  }

  function blankGate(index, status, statement) {
    return {
      id: "G" + index,
      name: GATE_NAMES[index],
      status: status,
      code: status === "NOT_RUN" ? "NOT_RUN" : "NOT_APPLICABLE",
      stage: index <= 3 || index === 6 ? "intrinsic" : "model",
      evidenceClass: status === "NOT_RUN" ? "research-target" : "exact-finite-identity",
      basis: status === "NOT_RUN" ? "general-inverse-design" : "combinatorial-identity",
      statement: statement,
      hypotheses: [],
      witness: null,
      observed: null,
      required: "not evaluated",
      signedMargin: null,
      tolerance: null,
      impossibleInDeclaredModel: false
    };
  }

  function makeGate(index, options) {
    return cloneCanonical({
      id: "G" + index,
      name: GATE_NAMES[index],
      status: options.status,
      code: options.code,
      stage: options.stage || (index <= 3 || index === 6 ? "intrinsic" : "model"),
      evidenceClass: options.evidenceClass || "exact-finite-identity",
      basis: options.basis || "combinatorial-identity",
      statement: options.statement,
      hypotheses: options.hypotheses || [],
      witness: options.witness == null ? null : options.witness,
      observed: options.observed == null ? null : options.observed,
      required: options.required || "declared check",
      signedMargin: options.signedMargin == null ? null : options.signedMargin,
      tolerance: options.tolerance == null ? null : options.tolerance,
      impossibleInDeclaredModel: options.impossibleInDeclaredModel === true
    });
  }

  function safeOwnString(object, key, maximumLength) {
    if (!object || typeof object !== "object") return null;
    var descriptor;
    try { descriptor = Object.getOwnPropertyDescriptor(object, key); }
    catch (error) { return null; }
    return descriptor && Object.prototype.hasOwnProperty.call(descriptor, "value") &&
      typeof descriptor.value === "string" && descriptor.value.length <= maximumLength
      ? descriptor.value : null;
  }

  function malformedReport(raw, validation) {
    var first = validation.errors[0] || { code: "SCHEMA_INVALID" };
    var gate0 = makeGate(0, {
      status: "FAIL",
      code: first.code,
      statement: "The request failed the closed, bounded data schema. No mathematical theorem or optimizer was run.",
      witness: { errors: validation.errors },
      required: "a finite schemaVersion 2 request with no unknown fields",
      impossibleInDeclaredModel: false
    });
    var gates = [gate0];
    for (var i = 1; i <= 6; i += 1) gates.push(blankGate(i, "NOT_RUN", "Stopped by the exact-first compiler after G0 failed."));
    var report = {
      schemaVersion: SCHEMA_VERSION,
      compilerVersion: VERSION,
      digestAlgorithm: DIGEST_ALGORITHM,
      requestId: safeOwnString(raw, "id", LIMITS.maxIdentifierLength),
      requestDigest: null,
      normalizedRequest: null,
      status: "FAIL",
      gates: gates,
      candidates: [],
      selectedCandidateId: null,
      obstructionCertificates: [certificateFromGate(gate0)],
      repairProposals: [],
      refinement: null,
      robustness: null,
      fabricationPackage: null,
      replay: {
        deterministic: true,
        seed: safeOwnString(raw, "seed", LIMITS.maxSeedLength),
        platformIndependentInputsDigest: null,
        methods: ["bounded-closed-schema-validation", "rejected raw inputs are intentionally not recursively digested"]
      },
      claims: {
        demonstrated: ["The supplied request was rejected before mathematical evaluation."],
        notDemonstrated: ["intrinsic compatibility", "model realizability", "extrinsic embeddability", "mechanical selection", "instrument observability"]
      }
    };
    report.reportDigest = digestValue(report);
    return deepFreeze(cloneCanonical(report));
  }

  function uniqueComplexForBase(complex) {
    var edgeMap = Object.create(null);
    complex.edges.forEach(function (edge) {
      if (edge.source !== edge.target && !edgeMap[edgeKey(edge.source, edge.target)]) edgeMap[edgeKey(edge.source, edge.target)] = { source: edge.source, target: edge.target, length: 1, weight: 1 };
    });
    return {
      nodes: complex.nodes.map(function (node, index) { return { id: index, label: node.label, x: 0, y: 0, z: 0, radius: 1 }; }),
      edges: Object.keys(edgeMap).sort().map(function (key) { return edgeMap[key]; }),
      faces: complex.faces.map(function (face) { return face.slice(); })
    };
  }

  function orientationAudit(faces, edgeIncidence) {
    var signs = new Array(faces.length).fill(0);
    var contradiction = null;
    for (var start = 0; start < faces.length && !contradiction; start += 1) {
      if (signs[start]) continue;
      signs[start] = 1;
      var queue = [start];
      while (queue.length && !contradiction) {
        var faceIndex = queue.shift();
        var face = faces[faceIndex];
        [[face[0], face[1]], [face[1], face[2]], [face[2], face[0]]].forEach(function (pair) {
          if (contradiction) return;
          var incident = edgeIncidence[edgeKey(pair[0], pair[1])] || [];
          if (incident.length !== 2) return;
          var current = incident[0].face === faceIndex ? incident[0] : incident[1];
          var other = incident[0].face === faceIndex ? incident[1] : incident[0];
          var required = -signs[faceIndex] * current.direction * other.direction;
          if (!signs[other.face]) { signs[other.face] = required; queue.push(other.face); }
          else if (signs[other.face] !== required) contradiction = { edge: [Math.min(pair[0], pair[1]), Math.max(pair[0], pair[1])], faces: [faceIndex, other.face].sort(function (a, b) { return a - b; }) };
        });
      }
    }
    return { orientable: !contradiction, faceOrientationSigns: signs, contradiction: contradiction };
  }

  function expectedTopology(topology) {
    if (topology.surface === "sphere") return [1, 0, 1];
    if (topology.surface === "torus") return [1, 2, 1];
    if (topology.surface === "disk") return [1, 0, 0];
    if (topology.surface === "annulus") return [1, 1, 0];
    return topology.expectedBetti ? topology.expectedBetti.slice() : null;
  }

  function surfaceGate(request) {
    var complex = request.target.discretization.complex;
    var errors = [];
    var edgeSeen = Object.create(null), uniqueEdges = [];
    complex.edges.forEach(function (edge, index) {
      var key = edgeKey(edge.source, edge.target);
      if (edge.source === edge.target) errors.push({ code: "SURFACE_INVALID", kind: "loop-edge", edgeIndex: index, edge: [edge.source, edge.target] });
      if (edgeSeen[key] != null) errors.push({ code: "SURFACE_INVALID", kind: "duplicate-edge", edgeIndex: index, firstEdgeIndex: edgeSeen[key], edge: [edge.source, edge.target] });
      else { edgeSeen[key] = index; uniqueEdges.push(edge); }
    });
    var faceSeen = Object.create(null);
    complex.faces.forEach(function (face, index) {
      var key = face.join(":");
      if (new Set(face).size !== 3) errors.push({ code: "SURFACE_INVALID", kind: "repeated-face-vertex", faceIndex: index, face: face.slice() });
      if (faceSeen[key] != null) errors.push({ code: "SURFACE_INVALID", kind: "duplicate-face", faceIndex: index, firstFaceIndex: faceSeen[key], face: face.slice() });
      else faceSeen[key] = index;
    });
    var incidence = Object.create(null);
    Object.keys(edgeSeen).forEach(function (key) { incidence[key] = []; });
    complex.faces.forEach(function (face, faceIndex) {
      [[face[0], face[1]], [face[1], face[2]], [face[2], face[0]]].forEach(function (pair) {
        var key = edgeKey(pair[0], pair[1]);
        if (!incidence[key]) {
          errors.push({ code: "SURFACE_INVALID", kind: "missing-face-edge", faceIndex: faceIndex, edge: [Math.min(pair[0], pair[1]), Math.max(pair[0], pair[1])] });
          incidence[key] = [];
        }
        incidence[key].push({ face: faceIndex, direction: pair[0] < pair[1] ? 1 : -1 });
      });
    });
    Object.keys(incidence).sort().forEach(function (key) {
      var count = incidence[key].length;
      if (count === 0) errors.push({ code: "SURFACE_INVALID", kind: "dangling-edge", edge: key.split(":").map(Number) });
      if (count > 2) errors.push({ code: "SURFACE_INVALID", kind: "nonmanifold-edge", edge: key.split(":").map(Number), incidentFaceCount: count });
    });
    var boundaryKeys = Object.keys(incidence).filter(function (key) { return incidence[key].length === 1; }).sort();
    var orientation = orientationAudit(complex.faces, incidence);
    if (request.target.topology.orientable !== orientation.orientable) errors.push({ code: "TOPOLOGY_MISMATCH", kind: "orientability", declared: request.target.topology.orientable, computed: orientation.orientable, witness: orientation.contradiction });
    var baseComplex = uniqueComplexForBase(complex);
    var baseValidity = null, topology = null;
    try {
      baseValidity = Base.surfaceValidity(baseComplex, { metric: "circle-packing" });
      topology = Base.computeBettiNumbers(baseComplex);
      if (!baseValidity.valid) errors.push({ code: "SURFACE_INVALID", kind: "base-surface-gate", details: baseValidity });
    } catch (error) {
      errors.push({ code: "SURFACE_INVALID", kind: "base-surface-exception", message: error.message });
    }
    if (topology) {
      var expected = expectedTopology(request.target.topology);
      if (expected && expected.some(function (value, index) { return value !== topology.betti.array[index]; })) errors.push({ code: "TOPOLOGY_MISMATCH", kind: "betti", declared: expected, computed: topology.betti.array });
      if (request.target.topology.boundaryComponents !== topology.boundary.componentCount) errors.push({ code: "TOPOLOGY_MISMATCH", kind: "boundary-components", declared: request.target.topology.boundaryComponents, computed: topology.boundary.componentCount });
      if ((request.models[0].indexOf("circle-packing") === 0) && topology.connectedComponents !== 1) errors.push({ code: "DISCONNECTED_DOMAIN", kind: "connectedness", computedComponents: topology.connectedComponents });
    }
    errors.sort(function (a, b) { return (a.kind || "").localeCompare(b.kind || "") || stableStringify(a).localeCompare(stableStringify(b)); });
    var status = errors.length ? "FAIL" : "PASS";
    return {
      gate: makeGate(1, {
        status: status,
        code: errors.length ? errors[0].code : "SURFACE_VALID",
        statement: errors.length ? "The supplied finite complex does not satisfy the declared simplicial-surface/topology contract; later curvature theorems were not applied." : "The supplied cells form the declared finite triangular surface. A coherent face orientation exists exactly when the request declares orientability; this is a finite combinatorial statement, not continuum convergence.",
        basis: "combinatorial-identity",
        witness: {
          errors: errors,
          simplexCounts: topology ? topology.simplexCounts : { vertices: complex.nodes.length, edges: uniqueEdges.length, faces: complex.faces.length },
          bettiGF2: topology ? topology.betti.array : null,
          eulerCharacteristic: topology ? topology.eulerCharacteristic : null,
          boundaryComponents: topology ? topology.boundary.componentCount : boundaryKeys.length ? null : 0,
          orientable: orientation.orientable,
          orientationContradiction: orientation.contradiction,
          baseSurfaceValidity: baseValidity
        },
        required: "a finite pure triangular 2-manifold matching the declared topology",
        impossibleInDeclaredModel: false
      }),
      topology: topology,
      baseComplex: baseComplex,
      incidence: incidence,
      orientation: orientation
    };
  }

  function curvatureData(request, topology) {
    var curvature = request.target.curvature;
    var count = request.target.discretization.complex.nodes.length;
    if (curvature.basis === "vertex") return { values: curvature.values.slice(), rationals: null, symbolic: false };
    if (curvature.basis === "symbolic-pi") {
      var rationals = curvature.piCoefficients.map(function (coefficient) { return rational(BigInt(coefficient.numerator), BigInt(coefficient.denominator)); });
      return { values: rationals.map(function (coefficient) { return rationalNumber(coefficient) * PI; }), rationals: rationals, symbolic: true };
    }
    var coefficient = rational(2 * topology.eulerCharacteristic, count);
    var generated = new Array(count).fill(null).map(function () { return coefficient; });
    return { values: generated.map(function (entry) { return rationalNumber(entry) * PI; }), rationals: generated, symbolic: true, procedural: "uniform" };
  }

  function curvatureUpperGate(request, topology, data) {
    var boundary = Object.create(null);
    topology.boundary.vertices.forEach(function (vertex) { boundary[vertex] = true; });
    var failures = [];
    data.values.forEach(function (value, vertex) {
      var boundCoefficient = boundary[vertex] ? 1 : 2;
      var comparison = data.symbolic ? rationalCompare(data.rationals[vertex], rational(boundCoefficient, 1)) : value < boundCoefficient * PI ? -1 : 0;
      if (comparison >= 0) failures.push({
        vertex: vertex,
        boundary: !!boundary[vertex],
        observed: value,
        observedPiCoefficient: data.symbolic ? rationalJSON(data.rationals[vertex]) : null,
        required: "K_" + vertex + " < " + (boundary[vertex] ? "π" : "2π"),
        signedMargin: boundCoefficient * PI - value
      });
    });
    return makeGate(2, {
      status: failures.length ? "FAIL" : "PASS",
      code: failures.length ? "CURVATURE_LOCAL_UPPER_BOUND" : "CURVATURE_LOCAL_BOUNDS_SATISFIED",
      statement: failures.length ? "At least one requested defect reaches or exceeds the strict upper bound of a nondegenerate Euclidean cone. This rejects the requested intrinsic target, not all nearby targets or extrinsic shapes." : "Every target defect is strictly below its boundary-aware Euclidean cone upper bound. These local inequalities are necessary but not sufficient for realizability.",
      evidenceClass: data.symbolic ? "exact-finite-identity" : "finite-numerical-estimate",
      basis: data.symbolic ? "theorem-instance" : "simulation",
      hypotheses: ["nondegenerate Euclidean cone triangles", "interior total angle is positive", "boundary total angle uses the π convention"],
      witness: failures.length ? failures[0] : { checkedVertices: data.values.length, symbolicComparison: data.symbolic },
      observed: failures.length ? failures[0].observed : Math.max.apply(null, data.values),
      required: "K_i < 2π for interior vertices and K_i < π for boundary vertices",
      signedMargin: failures.length ? failures[0].signedMargin : null,
      tolerance: data.symbolic ? 0 : null,
      impossibleInDeclaredModel: data.symbolic && failures.length > 0
    });
  }

  function gaussBonnetGate(request, topology, data) {
    var target = TAU * topology.eulerCharacteristic;
    var sum = data.values.reduce(function (total, value) { return total + value; }, 0);
    var sumAbs = data.values.reduce(function (total, value) { return total + Math.abs(value); }, 0);
    var residual = sum - target;
    var scaleTolerance = 64 * MACHINE_EPSILON * Math.max(1, sumAbs, Math.abs(target));
    var tolerance = Math.max(scaleTolerance, request.verification.gbTolerance);
    var exactSum = null, exactTarget = rational(2 * topology.eulerCharacteristic, 1), status, code, statement;
    if (data.symbolic) {
      exactSum = data.rationals.reduce(function (total, value) { return rationalAdd(total, value); }, rational(0, 1));
      if (rationalCompare(exactSum, exactTarget) === 0) {
        status = "PASS";
        code = "GAUSS_BONNET_TOTAL_SATISFIED";
        statement = "The target total equals 2πχ exactly as a rational multiple of π.";
      } else {
        status = "FAIL";
        code = "GAUSS_BONNET_TOTAL";
        statement = "The symbolic target violates the finite Gauss–Bonnet total exactly. It was not silently projected or repaired.";
      }
      tolerance = 0;
    } else if (Math.abs(residual) <= tolerance) {
      status = "INCONCLUSIVE";
      code = "GAUSS_BONNET_NUMERIC_ONLY";
      statement = "The floating target total lies within the disclosed numerical band, but approximate equality cannot establish exact membership in the curvature-map image. The theorem gate remains closed; use symbolic π coefficients or a separately disclosed projected target.";
    } else {
      status = "FAIL";
      code = "GAUSS_BONNET_NUMERIC_MISMATCH";
      statement = "The floating target total misses 2πχ beyond the disclosed numerical band. This is a finite numerical rejection, not an exact obstruction certificate.";
    }
    return makeGate(3, {
      status: status,
      code: code,
      statement: statement,
      evidenceClass: data.symbolic ? "exact-finite-identity" : "finite-numerical-estimate",
      basis: data.symbolic ? "theorem-instance" : "simulation",
      hypotheses: ["valid compact triangular surface", "interior defect 2π minus incident angles", "boundary defect π minus incident angles"],
      witness: {
        eulerCharacteristic: topology.eulerCharacteristic,
        observedTotal: sum,
        requiredTotal: target,
        unroundedResidual: residual,
        observedPiCoefficient: exactSum ? rationalJSON(exactSum) : null,
        requiredPiCoefficient: data.symbolic ? rationalJSON(exactTarget) : null,
        comparison: data.symbolic ? "exact-rational-multiple-of-pi" : "scale-aware-binary-floating"
      },
      observed: sum,
      required: "Σ K_i = 2πχ = " + target,
      signedMargin: data.symbolic ? (status === "PASS" ? 0 : -Math.abs(residual)) : tolerance - Math.abs(residual),
      tolerance: tolerance,
      impossibleInDeclaredModel: data.symbolic && status === "FAIL"
    });
  }

  function degreeSequence(complex) {
    var degrees = new Array(complex.nodes.length).fill(0), seen = Object.create(null);
    complex.edges.forEach(function (edge) {
      var key = edgeKey(edge.source, edge.target);
      if (!seen[key] && edge.source !== edge.target) { seen[key] = true; degrees[edge.source] += 1; degrees[edge.target] += 1; }
    });
    return degrees;
  }

  function subsetTotalCount(count) {
    var value = (1n << BigInt(count)) - 2n;
    return value <= BigInt(Number.MAX_SAFE_INTEGER) ? Number(value) : value.toString();
  }

  function evaluateSubset(vertices, request, data) {
    var complex = request.target.discretization.complex;
    var selected = Object.create(null);
    vertices.forEach(function (vertex) { selected[vertex] = true; });
    var internalEdges = 0, internalFaces = 0;
    complex.edges.forEach(function (edge) { if (selected[edge.source] && selected[edge.target]) internalEdges += 1; });
    var phiByKey = Object.create(null);
    complex.edges.forEach(function (edge, index) { phiByKey[edgeKey(edge.source, edge.target)] = request.constraints.phiByEdge[index]; });
    var links = [];
    complex.faces.forEach(function (face, faceIndex) {
      var inside = face.filter(function (vertex) { return !!selected[vertex]; });
      if (inside.length === 3) internalFaces += 1;
      if (inside.length === 1) {
        var outside = face.filter(function (vertex) { return !selected[vertex]; }).sort(function (a, b) { return a - b; });
        var key = edgeKey(outside[0], outside[1]);
        var phi = phiByKey[key];
        links.push({ face: faceIndex, vertex: inside[0], edge: outside, phi: phi, weight: PI - phi });
      }
    });
    links.sort(function (a, b) { return a.vertex - b.vertex || compareNumberArrays(a.edge, b.edge) || a.face - b.face; });
    var chi = vertices.length - internalEdges + internalFaces;
    var mass = vertices.reduce(function (sum, vertex) { return sum + data.values[vertex]; }, 0);
    var linkSum = links.reduce(function (sum, link) { return sum + link.weight; }, 0);
    var slack = mass + linkSum - TAU * chi;
    var exact = null;
    if (data.symbolic && links.every(function (link) { return link.phi === 0; })) {
      var massRat = vertices.reduce(function (sum, vertex) { return rationalAdd(sum, data.rationals[vertex]); }, rational(0, 1));
      exact = rationalAdd(rationalAdd(massRat, rational(links.length, 1)), rational(-2 * chi, 1));
    }
    return {
      subset: vertices.slice(),
      cardinality: vertices.length,
      eulerCharacteristicFullSubcomplex: chi,
      internalEdgeCount: internalEdges,
      internalFaceCount: internalFaces,
      targetCurvatureMass: mass,
      linkSum: linkSum,
      linkCount: links.length,
      slack: slack,
      symbolicSlackPiCoefficient: exact ? rationalJSON(exact) : null,
      _exact: exact,
      _links: links
    };
  }

  function subsetComparison(a, b) {
    var sign = a._exact && b._exact ? rationalCompare(a._exact, b._exact) : a.slack < b.slack ? -1 : a.slack > b.slack ? 1 : 0;
    return sign || a.cardinality - b.cardinality || compareNumberArrays(a.subset, b.subset);
  }

  function cleanSubset(entry, includeLinks) {
    var clean = {
      subset: entry.subset,
      cardinality: entry.cardinality,
      eulerCharacteristicFullSubcomplex: entry.eulerCharacteristicFullSubcomplex,
      internalEdgeCount: entry.internalEdgeCount,
      internalFaceCount: entry.internalFaceCount,
      targetCurvatureMass: entry.targetCurvatureMass,
      linkSum: entry.linkSum,
      linkCount: entry.linkCount,
      slack: entry.slack,
      symbolicSlackPiCoefficient: entry.symbolicSlackPiCoefficient
    };
    if (includeLinks) clean.link = entry._links;
    return clean;
  }

  function subsetLedgerDigest(entries) {
    var hash = 2166136261 >>> 0;
    entries.forEach(function (entry) {
      var text = stableStringify(cleanSubset(entry, false)) + "\n";
      for (var index = 0; index < text.length; index += 1) {
        hash ^= text.charCodeAt(index);
        hash = Math.imul(hash, 16777619);
      }
    });
    return ("00000000" + (hash >>> 0).toString(16)).slice(-8);
  }

  function boundedSubsetRows(entries) {
    if (entries.length <= MAX_EXPORTED_SUBSET_ROWS) return entries.map(function (entry) { return cleanSubset(entry, false); });
    var rows = [];
    for (var index = 0; index < MAX_EXPORTED_SUBSET_ROWS; index += 1) {
      var source = Math.floor(index * (entries.length - 1) / (MAX_EXPORTED_SUBSET_ROWS - 1));
      rows.push(cleanSubset(entries[source], false));
    }
    return rows;
  }

  function chowLuoGate(request, topology, data, surface) {
    var model = request.models[0];
    if (model !== "circle-packing-tangency" && model !== "circle-packing-weighted") {
      return blankGate(4, "NOT_APPLICABLE", "The Chow–Luo Model CP theorem is outside the declared edge-metric model.");
    }
    if (topology.boundary.edgeCount !== 0) {
      return blankGate(4, "NOT_APPLICABLE", "The closed-surface Chow–Luo theorem was not applied to a surface with boundary. Symmetric doubling is a separate required gate; no CP realizability or impossibility conclusion is drawn here.");
    }
    if (!data || !data.symbolic) {
      return makeGate(4, {
        status: "INCONCLUSIVE",
        code: "CHOW_LUO_TOTAL_NOT_EXACT",
        evidenceClass: "finite-numerical-estimate",
        basis: "simulation",
        statement: "The closed-surface theorem was not applied because exact Gauss–Bonnet membership was not established for this floating target.",
        hypotheses: ["exact total-curvature membership before open-polytope admission"],
        witness: { symbolicTotalAvailable: !!(data && data.symbolic) },
        required: "an exact symbolic or formally certified total-curvature premise",
        impossibleInDeclaredModel: false
      });
    }
    var complex = request.target.discretization.complex;
    var degrees = degreeSequence(complex);
    var hypothesisFailures = [];
    if (topology.connectedComponents !== 1) hypothesisFailures.push("surface is not connected");
    if (!surface.orientation.orientable || !request.target.topology.orientable) hypothesisFailures.push("this implementation has not admitted a coherently orientable closed surface");
    if (degrees.some(function (degree) { return degree < 3; })) hypothesisFailures.push("a vertex has degree below three");
    if (request.constraints.phiByEdge.some(function (phi) { return phi < 0 || phi > PI / 2; })) hypothesisFailures.push("an intersection angle lies outside [0, π/2]");
    if (hypothesisFailures.length) {
      return makeGate(4, {
        status: "INCONCLUSIVE",
        code: "CHOW_LUO_SEARCH_INCOMPLETE",
        statement: "The theorem hypotheses are not all established, so this compiler withholds both admission and impossibility claims.",
        basis: "theorem-instance",
        hypotheses: ["connected closed simplicial triangulation", "Euclidean Model CP", "Phi in [0, π/2]", "no loops, double edges, low-degree vertices, or duplicate face triples"],
        witness: { unmetHypotheses: hypothesisFailures },
        required: "all declared Chow–Luo hypotheses",
        impossibleInDeclaredModel: false
      });
    }
    var count = complex.nodes.length;
    var exhaustive = count <= request.verification.exactSubsetLimit;
    var subsets = [];
    if (exhaustive) {
      var full = Math.pow(2, count) - 1;
      for (var mask = 1; mask < full; mask += 1) {
        var vertices = [];
        for (var vertex = 0; vertex < count; vertex += 1) if (mask & Math.pow(2, vertex)) vertices.push(vertex);
        subsets.push(evaluateSubset(vertices, request, data));
      }
    } else {
      for (var i = 0; i < count; i += 1) {
        subsets.push(evaluateSubset([i], request, data));
        var complement = [];
        for (var j = 0; j < count; j += 1) if (j !== i) complement.push(j);
        subsets.push(evaluateSubset(complement, request, data));
      }
    }
    subsets.sort(subsetComparison);
    var minimum = subsets[0];
    function subsetRoundoff(entry) {
      return 64 * MACHINE_EPSILON * Math.max(1, Math.abs(entry.targetCurvatureMass), Math.abs(entry.linkSum), Math.abs(TAU * entry.eulerCharacteristicFullSubcomplex));
    }
    var allExact = subsets.every(function (entry) { return !!entry._exact; });
    var violatingEntries = subsets.filter(function (entry) {
      return entry._exact ? rationalCompare(entry._exact, rational(0, 1)) <= 0 : entry.slack < -subsetRoundoff(entry);
    }).sort(subsetComparison);
    var ambiguousEntries = subsets.filter(function (entry) {
      return !entry._exact && Math.abs(entry.slack) <= subsetRoundoff(entry);
    }).sort(subsetComparison);
    var violation = violatingEntries.length > 0;
    var ambiguousZero = !violation && ambiguousEntries.length > 0;
    if (violation) minimum = violatingEntries[0];
    else if (ambiguousZero) minimum = ambiguousEntries[0];
    var roundoff = subsets.reduce(function (maximum, entry) { return entry._exact ? maximum : Math.max(maximum, subsetRoundoff(entry)); }, 0);
    var status, code, statement, impossible = false;
    if (violation) {
      status = "FAIL"; code = "CHOW_LUO_SUBSET"; impossible = true;
      statement = "A displayed vertex subset violates the strict Chow–Luo curvature-polytope inequality. Under the verified hypotheses this target is impossible in the declared Model CP, but this says nothing universal about arbitrary edge metrics, embeddings, or physical sheets.";
    } else if (!exhaustive) {
      status = "INCONCLUSIVE"; code = "CHOW_LUO_SEARCH_INCOMPLETE";
      statement = "The deterministic singleton/complement probe found no obstruction, but the subset search was not exhaustive. This is INCONCLUSIVE and is not an admission certificate.";
    } else if (ambiguousZero) {
      status = "INCONCLUSIVE"; code = "CHOW_LUO_MARGIN";
      statement = "Every subset was evaluated, but the smallest floating slack is indistinguishable from the strict boundary at the disclosed roundoff guard. No PASS or impossibility claim is made.";
    } else if (minimum.slack < request.verification.chowLuoGuard) {
      status = "MARGINAL"; code = "CHOW_LUO_MARGIN";
      statement = "All subset inequalities are strictly positive, but the minimum is below the requested guard. The exact model theorem admits the target while the report marks its proximity to the open-polytope boundary.";
    } else {
      status = "PASS"; code = "CHOW_LUO_SUBSETS_SATISFIED";
      statement = "All nonempty proper vertex subsets were exhaustively evaluated. Under the verified closed, connected, simplicial Euclidean Model CP hypotheses, the Chow–Luo theorem admits the target in the normalized declared circle-packing model. This intrinsic statement does not establish an embedding, material response, actuator program, or physical shape.";
    }
    var witness = minimum ? cleanSubset(minimum, true) : null;
    if (witness) {
      witness.requiredLowerBound = TAU * minimum.eulerCharacteristicFullSubcomplex - minimum.linkSum;
      witness.infimumCurvatureIncreaseForThisSubset = Math.max(0, -minimum.slack);
      witness.strictInequalityNote = "The displayed infimum is not sufficient when equality is attained; add a positive guard and rerun every subset.";
    }
    var orderedEntries = subsets.slice().sort(function (a, b) { return a.cardinality - b.cardinality || compareNumberArrays(a.subset, b.subset); });
    var orderedSlacks = boundedSubsetRows(orderedEntries);
    var ledgerDigest = subsetLedgerDigest(orderedEntries);
    return makeGate(4, {
      status: status,
      code: code,
      evidenceClass: allExact ? "exact-finite-identity" : "finite-numerical-estimate",
      basis: allExact ? (exhaustive ? "exhaustive-finite-check" : "theorem-instance") : "simulation",
      hypotheses: ["connected triangulation of a closed surface", "simplicial complex with no loops/double edges/duplicate triples and minimum degree three", "Euclidean weighted circle-packing metric", "Phi:E→[0,π/2]", "Gauss–Bonnet total already passed"],
      statement: statement,
      witness: {
        exhaustive: exhaustive,
        evaluatedSubsetCount: subsets.length,
        totalProperNonemptySubsetCount: subsetTotalCount(count),
        exactSymbolicTangencyArithmetic: allExact,
        minimum: witness,
        subsetSlacks: orderedSlacks,
        subsetSlacksComplete: orderedSlacks.length === subsets.length,
        exportedSubsetRowCount: orderedSlacks.length,
        subsetLedgerDigestAlgorithm: DIGEST_ALGORITHM,
        subsetLedgerDigest: ledgerDigest
      },
      observed: minimum ? minimum.slack : null,
      required: "Δ_CL(I)>0 for every nonempty proper I⊂V; requested guard " + request.verification.chowLuoGuard,
      signedMargin: minimum ? minimum.slack : null,
      tolerance: allExact ? 0 : roundoff,
      impossibleInDeclaredModel: impossible
    });
  }

  function diskDoublingGate(request, topology) {
    var model = request.models[0];
    if (model !== "circle-packing-tangency" && model !== "circle-packing-weighted") return blankGate(5, "NOT_APPLICABLE", "Symmetric Model CP doubling is outside the declared edge-metric model.");
    if (topology.boundary.edgeCount === 0) return blankGate(5, "NOT_APPLICABLE", "The supplied CP surface is already closed; symmetric disk doubling is unnecessary.");
    return makeGate(5, {
      status: "NOT_RUN",
      code: "DOUBLE_NOT_RUN",
      evidenceClass: "research-target",
      basis: "general-inverse-design",
      statement: "Certified symmetric doubling is deferred in this slice. The compiler has not applied the closed-surface Chow–Luo theorem to this boundary surface, and it draws no CP realizability or impossibility conclusion.",
      hypotheses: ["a valid reflected closed double", "boundary defects mapped to twice their disk values", "reflection-symmetric normalized Model CP solution"],
      witness: { boundaryEdgeCount: topology.boundary.edgeCount, boundaryComponentCount: topology.boundary.componentCount },
      required: "validated symmetric double before a closed-surface theorem is used",
      impossibleInDeclaredModel: false
    });
  }

  function safeGeometricMean(lower, upper) {
    return Math.sqrt(lower) * Math.sqrt(upper);
  }

  function cpLengths(request) {
    var radiusBounds = request.constraints.radiusBounds;
    var edgeBounds = request.constraints.edgeLengthBounds;
    var unitLengths = request.target.discretization.complex.edges.map(function (_, index) {
      return Math.sqrt(2 + 2 * Math.cos(request.constraints.phiByEdge[index]));
    });
    var lower = radiusBounds[0], upper = radiusBounds[1];
    unitLengths.forEach(function (unit) {
      lower = Math.max(lower, edgeBounds[0] / unit);
      upper = Math.min(upper, edgeBounds[1] / unit);
    });
    var scaleFeasible = finite(lower) && finite(upper) && lower <= upper;
    var radius = scaleFeasible ? safeGeometricMean(lower, upper) : safeGeometricMean(radiusBounds[0], radiusBounds[1]);
    var radii = new Array(request.target.discretization.complex.nodes.length).fill(radius);
    var lengths = unitLengths.map(function (unit) { return unit * radius; });
    return {
      radii: radii,
      lengths: lengths,
      unitLengths: unitLengths,
      scaleFeasible: scaleFeasible,
      feasibleScaleInterval: scaleFeasible ? [lower, upper] : null,
      rejectedScaleInterval: scaleFeasible ? null : [lower, upper],
      scale: radius,
      scope: "equal-radius reference ray only; not a solved target radius ratio"
    };
  }

  function positiveDoubleDyadic(value) {
    var buffer = new ArrayBuffer(8), view = new DataView(buffer);
    view.setFloat64(0, value, false);
    var high = view.getUint32(0, false), low = view.getUint32(4, false);
    var exponentBits = (high >>> 20) & 0x7ff;
    var fraction = (BigInt(high & 0xfffff) << 32n) | BigInt(low);
    if (exponentBits === 0) return { mantissa: fraction, exponent: -1074 };
    return { mantissa: (1n << 52n) | fraction, exponent: exponentBits - 1023 - 52 };
  }

  function exactTriangleSign(a, b, c) {
    var values = [a, b, c].slice().sort(function (left, right) { return left - right; });
    var x = positiveDoubleDyadic(values[0]), y = positiveDoubleDyadic(values[1]), z = positiveDoubleDyadic(values[2]);
    var exponent = Math.min(x.exponent, y.exponent, z.exponent);
    var exactGap = (x.mantissa << BigInt(x.exponent - exponent)) +
      (y.mantissa << BigInt(y.exponent - exponent)) -
      (z.mantissa << BigInt(z.exponent - exponent));
    return exactGap < 0n ? -1 : exactGap > 0n ? 1 : 0;
  }

  function triangleGate(request) {
    var complex = request.target.discretization.complex;
    var model = request.models[0], referenceOnly = model !== "edge-metric";
    var radii = null, lengths, cp = null;
    if (!referenceOnly) lengths = request.target.edgeLengths.slice();
    else { cp = cpLengths(request); radii = cp.radii; lengths = cp.lengths; }
    var byKey = Object.create(null);
    complex.edges.forEach(function (edge, index) { byKey[edgeKey(edge.source, edge.target)] = { length: lengths[index], edgeIndex: index }; });
    var nonpositive = [], boundFailures = [], faces = [];
    lengths.forEach(function (length, index) {
      if (!(length > 0) || !isFinite(length)) nonpositive.push({ edgeIndex: index, edge: [complex.edges[index].source, complex.edges[index].target], length: length });
      if (length < request.constraints.edgeLengthBounds[0] || length > request.constraints.edgeLengthBounds[1]) boundFailures.push({ edgeIndex: index, edge: [complex.edges[index].source, complex.edges[index].target], length: length, bounds: request.constraints.edgeLengthBounds });
    });
    complex.faces.forEach(function (face, faceIndex) {
      var entries = [byKey[edgeKey(face[0], face[1])], byKey[edgeKey(face[1], face[2])], byKey[edgeKey(face[2], face[0])]];
      if (entries.some(function (entry) { return !entry || !(entry.length > 0) || !finite(entry.length); })) return;
      var a = entries[0].length, b = entries[1].length, c = entries[2].length;
      var sorted = [a, b, c].sort(function (left, right) { return left - right; });
      var margin = sorted[0] - (sorted[2] - sorted[1]);
      var sign = exactTriangleSign(a, b, c);
      var relative = sign > 0 ? Math.max(0, margin / sorted[2]) : Math.min(0, margin / sorted[2]);
      faces.push({ faceIndex: faceIndex, face: face.slice(), edgeLengths: [a, b, c], margin: margin, relativeMargin: relative, exactDyadicSign: sign });
    });
    faces.sort(function (a, b) { return a.exactDyadicSign - b.exactDyadicSign || a.relativeMargin - b.relativeMargin || a.faceIndex - b.faceIndex; });
    var minimum = faces[0] || null;
    var strictFailure = !!(minimum && minimum.exactDyadicSign <= 0);
    var lowMargin = !!(minimum && minimum.exactDyadicSign > 0 && minimum.relativeMargin < request.verification.optimizerTolerance);
    var referenceUnavailable = referenceOnly && (!cp.scaleFeasible || nonpositive.length || boundFailures.length || strictFailure);
    var directFailure = !referenceOnly && (nonpositive.length || boundFailures.length || strictFailure);
    var status = directFailure ? "FAIL" : referenceUnavailable ? "INCONCLUSIVE" : lowMargin ? "MARGINAL" : "PASS";
    var code = directFailure ? (nonpositive.length ? "NONPOSITIVE_LENGTH" : boundFailures.length ? "EDGE_LENGTH_BOUNDS" : "TRIANGLE_INEQUALITY") :
      referenceUnavailable ? "CP_REFERENCE_NOT_FOUND" : lowMargin ? "TRIANGLE_MARGIN_LOW" : "TRIANGLE_MARGINS_SATISFIED";
    var statement = directFailure
      ? "The supplied edge vector violates a declared hard bound or an exact dyadic strict-triangle predicate. This rejects that finite metric only."
      : referenceUnavailable
        ? "The equal-radius CP reference ray did not produce an in-bound strict metric. Because this is only a reference ray and not a feasibility search over radius ratios, the compiler returns INCONCLUSIVE rather than rejecting the target."
        : status === "MARGINAL"
          ? "Every checked triangle is strictly valid, but the smallest relative margin is below the disclosed numerical guard."
          : referenceOnly
            ? "An analytically intersected global-scale interval yields an in-bound equal-radius CP reference metric. It is a metric-domain witness, not a solved curvature target."
            : "The supplied edge metric has positive bounded lengths and every face passes the exact dyadic strict-triangle predicate.";
    return {
      gate: makeGate(6, {
        status: status,
        code: code,
        evidenceClass: referenceOnly ? "finite-numerical-estimate" : "exact-finite-identity",
        basis: referenceOnly ? "simulation" : "exhaustive-finite-check",
        statement: statement,
        hypotheses: ["finite declared edge vector", "one length per simplicial edge", "strict Euclidean triangle inequalities"],
        witness: {
          nonpositiveLengths: nonpositive,
          hardBoundFailures: boundFailures,
          minimumTriangle: minimum,
          checkedFaceCount: faces.length,
          referenceOnly: referenceOnly,
          referenceScale: cp ? { feasible: cp.scaleFeasible, interval: cp.feasibleScaleInterval, rejectedInterval: cp.rejectedScaleInterval, selected: cp.scale, scope: cp.scope } : null,
          trianglePredicate: "exact sign of the sum of two supplied binary64 dyadics minus the third"
        },
        observed: minimum ? minimum.relativeMargin : null,
        required: "positive lengths and positive relative triangle margin; guard " + request.verification.optimizerTolerance,
        signedMargin: minimum ? minimum.margin : null,
        tolerance: 0,
        impossibleInDeclaredModel: directFailure
      }),
      radii: radii,
      lengths: lengths,
      minimum: minimum,
      referenceOnly: referenceOnly,
      referenceScale: cp
    };
  }

  function angleFromSides(a, b, opposite) {
    var cosine = (a * a + b * b - opposite * opposite) / (2 * a * b);
    return Math.acos(Math.max(-1, Math.min(1, cosine)));
  }

  function defectsForMetric(request, lengths, topology) {
    var complex = request.target.discretization.complex, byKey = Object.create(null);
    complex.edges.forEach(function (edge, index) { byKey[edgeKey(edge.source, edge.target)] = lengths[index]; });
    var sums = new Array(complex.nodes.length).fill(0);
    complex.faces.forEach(function (face) {
      var ab = byKey[edgeKey(face[0], face[1])], bc = byKey[edgeKey(face[1], face[2])], ca = byKey[edgeKey(face[2], face[0])];
      sums[face[0]] += angleFromSides(ab, ca, bc);
      sums[face[1]] += angleFromSides(ab, bc, ca);
      sums[face[2]] += angleFromSides(bc, ca, ab);
    });
    var boundary = Object.create(null);
    topology.boundary.vertices.forEach(function (vertex) { boundary[vertex] = true; });
    return sums.map(function (sum, vertex) { return (boundary[vertex] ? PI : TAU) - sum; });
  }

  function candidateFromTriangle(request, triangle, topology, data) {
    var model = request.models[0];
    if (triangle.gate.status === "FAIL" || (triangle.referenceOnly && ["PASS", "MARGINAL"].indexOf(triangle.gate.status) < 0)) return { candidates: [], selected: null };
    if (model === "edge-metric") {
      return {
        candidates: [{
          id: request.id + ".edge-metric",
          model: model,
          targetUsed: "original",
          preRuntimeCompilation: { localityClass: "L2", operations: ["closed schema normalization", "surface validation", "exhaustive face triangle audit"] },
          runtimeRule: { localityClass: "L0", radius: 0, synchronous: true, stateVariables: ["edge length"], immutableLocalTargets: ["declared edge length"], updateEquation: "ell_e(t+1)=ell_e(t)" },
          topology: request.target.discretization.complex,
          variables: { edgeLengths: triangle.lengths },
          objectiveHistory: [],
          residuals: { minimumTriangleMargin: triangle.minimum ? triangle.minimum.margin : null },
          hardBoundsSatisfied: triangle.gate.status !== "FAIL",
          evidenceClass: "exact-finite-identity",
          caveats: ["This is an intrinsic finite edge metric, not an R3 embedding or a physical sheet."]
        }],
        selected: request.id + ".edge-metric"
      };
    }
    var actual = defectsForMetric(request, triangle.lengths, topology);
    var squared = actual.reduce(function (sum, value, index) { var residual = value - data.values[index]; return sum + residual * residual; }, 0);
    var maxResidual = actual.reduce(function (maximum, value, index) { return Math.max(maximum, Math.abs(value - data.values[index])); }, 0);
    var id = request.id + ".cp-reference";
    return {
      candidates: [{
        id: id,
        model: model,
        targetUsed: "original",
        preRuntimeCompilation: { localityClass: "L2", operations: ["closed schema normalization", "exact intrinsic gates", "deterministic in-bound reference-radius construction"] },
        runtimeRule: { localityClass: "L1", radius: 1, synchronous: true, stateVariables: ["u_i=log(r_i)"], immutableLocalTargets: ["K_i*", "Phi_ij"], updateEquation: "u_i^(n+1)=u_i^n+eta(K_i*-K_i(u^n))" },
        topology: request.target.discretization.complex,
        variables: { radii: triangle.radii, edgeLengths: triangle.lengths },
        objectiveHistory: [0.5 * squared],
        residuals: { maximumCurvatureResidual: maxResidual, rmsCurvatureResidual: Math.sqrt(squared / actual.length), minimumTriangleMargin: triangle.minimum ? triangle.minimum.margin : null },
        hardBoundsSatisfied: triangle.gate.status !== "FAIL",
        evidenceClass: "finite-numerical-estimate",
        caveats: ["This deterministic reference vector is not an optimizer result.", "A Chow–Luo admission proves existence only under its hypotheses; this reference vector realizes the requested curvature only when the disclosed residual is within tolerance.", "No extrinsic embedding or physical response is established."]
      }],
      selected: maxResidual <= request.verification.optimizerTolerance ? id : null
    };
  }

  function certificateFromGate(gate) {
    return cloneCanonical({
      code: gate.code,
      status: gate.status,
      stage: gate.stage,
      evidenceClass: gate.evidenceClass,
      basis: gate.basis,
      impossibleInDeclaredModel: gate.impossibleInDeclaredModel,
      statement: gate.statement,
      hypotheses: gate.hypotheses,
      witness: gate.witness || {},
      observed: gate.observed,
      required: gate.required,
      signedMargin: gate.signedMargin,
      tolerance: gate.tolerance,
      repairHints: ["GAUSS_BONNET_TOTAL", "GAUSS_BONNET_NUMERIC_ONLY", "GAUSS_BONNET_NUMERIC_MISMATCH"].indexOf(gate.code) >= 0 ? ["Create a disclosed Gauss–Bonnet projection candidate; do not overwrite the original target."] : gate.code === "CHOW_LUO_SUBSET" ? ["Redistribute curvature mass away from the violating subset while preserving the total, then rerun every subset inequality."] : gate.code === "CURVATURE_LOCAL_UPPER_BOUND" ? ["Lower the witnessed vertex defect below its strict cone bound and rebalance the total curvature explicitly."] : []
    });
  }

  function overallStatus(gates) {
    if (gates.some(function (gate) { return gate.status === "FAIL"; })) return "FAIL";
    if (gates.some(function (gate) { return gate.status === "INCONCLUSIVE"; })) return "INCONCLUSIVE";
    if (gates[5] && gates[5].status === "NOT_RUN") return "INCONCLUSIVE";
    if (gates.some(function (gate) { return gate.status === "MARGINAL"; })) return "MARGINAL";
    return "PASS";
  }

  function compileInverseDesign(raw) {
    var validation = normalizeRequest(raw);
    if (!validation.valid) return malformedReport(raw, validation);
    var request = validation.normalized;
    var requestDigest = digestValue(request);
    var gates = [makeGate(0, {
      status: "PASS", code: "SCHEMA_VALID", statement: "The request passed the closed, bounded schema and was normalized deterministically; configuration text was treated only as data.", basis: "combinatorial-identity", witness: { limits: LIMITS, normalizedRequestDigest: requestDigest }, required: "schemaVersion 2 finite bounded request"
    })];
    var candidates = [], selected = null, repairProposals = [];
    var surface = surfaceGate(request); gates.push(surface.gate);
    if (surface.gate.status === "FAIL") {
      for (var blocked = 2; blocked <= 6; blocked += 1) gates.push(blankGate(blocked, "NOT_RUN", "Stopped by the exact-first compiler after G1 failed."));
    } else if (request.models[0] === "edge-metric") {
      gates.push(blankGate(2, "NOT_APPLICABLE", "No curvature target was declared for this direct edge-metric request."));
      gates.push(blankGate(3, "NOT_APPLICABLE", "No requested curvature total was declared; the finite metric identity may be measured downstream without being a target gate."));
      gates.push(chowLuoGate(request, surface.topology, null, surface));
      gates.push(diskDoublingGate(request, surface.topology));
      var edgeTriangle = triangleGate(request); gates.push(edgeTriangle.gate);
      var edgeCandidate = candidateFromTriangle(request, edgeTriangle, surface.topology, null);
      candidates = edgeCandidate.candidates; selected = edgeCandidate.selected;
    } else {
      var data = curvatureData(request, surface.topology);
      var upper = curvatureUpperGate(request, surface.topology, data); gates.push(upper);
      if (upper.status === "FAIL") {
        for (var afterUpper = 3; afterUpper <= 6; afterUpper += 1) gates.push(blankGate(afterUpper, "NOT_RUN", "Stopped by the exact-first compiler after G2 failed."));
      } else {
        var gb = gaussBonnetGate(request, surface.topology, data); gates.push(gb);
        if (gb.status !== "PASS") {
          repairProposals.push({ id: request.id + ".gb-projection", status: "PROPOSED_NOT_APPLIED", operation: "Khat_i=K_i-w_i/sum(w)*(sum(K)-2πχ)", preservesOriginalTarget: true });
          for (var afterGb = 4; afterGb <= 6; afterGb += 1) gates.push(blankGate(afterGb, "NOT_RUN", "Stopped by the exact-first compiler because G3 did not establish exact total-curvature membership."));
        } else {
          gates.push(chowLuoGate(request, surface.topology, data, surface));
          gates.push(diskDoublingGate(request, surface.topology));
          var cpTriangle = triangleGate(request); gates.push(cpTriangle.gate);
          var cpCandidate = candidateFromTriangle(request, cpTriangle, surface.topology, data);
          candidates = cpCandidate.candidates; selected = cpCandidate.selected;
        }
      }
    }
    var status = overallStatus(gates);
    var certificates = gates.filter(function (gate) { return ["FAIL", "MARGINAL", "INCONCLUSIVE"].indexOf(gate.status) >= 0 || (gate.id === "G5" && gate.status === "NOT_RUN"); }).map(certificateFromGate);
    var chow = gates[4];
    var demonstrated = ["Closed bounded request normalization and ordered finite intrinsic gates were executed deterministically."];
    if (chow && (chow.status === "PASS" || chow.status === "MARGINAL")) demonstrated.push("The declared Model CP target satisfies every bounded Chow–Luo condition under the verified theorem hypotheses.");
    if (request.models[0] === "edge-metric" && gates[6].status !== "FAIL") demonstrated.push("The supplied finite edge vector defines strict Euclidean triangles within the declared bounds.");
    var report = {
      schemaVersion: SCHEMA_VERSION,
      compilerVersion: VERSION,
      digestAlgorithm: DIGEST_ALGORITHM,
      requestId: request.id,
      requestDigest: requestDigest,
      normalizedRequest: request,
      status: status,
      gates: gates,
      candidates: candidates,
      selectedCandidateId: selected,
      obstructionCertificates: certificates,
      repairProposals: repairProposals,
      refinement: null,
      robustness: null,
      fabricationPackage: null,
      replay: {
        deterministic: true,
        seed: request.seed,
        platformIndependentInputsDigest: requestDigest,
        methods: ["closed-schema-normalization", "release-1-surface-and-GF2-topology", "exact-rational-pi-when-declared", "ordered-local-and-total-curvature-gates", "bounded-Chow-Luo-subset-enumeration", "exhaustive-triangle-margin-audit"]
      },
      claims: {
        demonstrated: demonstrated,
        notDemonstrated: ["continuum convergence", "a constructive CP radius solve except when the reference residual passes", "extrinsic embeddability", "mechanical selection", "instrument observability", "physical validation", "fabrication readiness"]
      }
    };
    report.reportDigest = digestValue(report);
    return deepFreeze(cloneCanonical(report));
  }

  function validateCompilerReport(input) {
    var errors = [];
    var preflight = preflightData(input);
    if (preflight.length) return { valid: false, errors: preflight.map(function (error) { return error.path + ": " + error.message; }) };
    if (!isPlainObject(input)) return { valid: false, errors: ["report must be a plain data object"] };
    var allowed = [
      "schemaVersion", "compilerVersion", "digestAlgorithm", "requestId", "requestDigest",
      "normalizedRequest", "status", "gates", "candidates", "selectedCandidateId",
      "obstructionCertificates", "repairProposals", "refinement", "robustness",
      "fabricationPackage", "replay", "claims", "reportDigest"
    ];
    Object.keys(input).filter(function (key) { return allowed.indexOf(key) < 0; }).sort().forEach(function (key) { errors.push("unknown report field " + key); });
    if (input.schemaVersion !== SCHEMA_VERSION || input.compilerVersion !== VERSION) errors.push("report schema/compiler version mismatch");
    if (input.digestAlgorithm !== DIGEST_ALGORITHM) errors.push("report digest algorithm mismatch");
    if (!/^[0-9a-f]{8}$/.test(input.reportDigest || "")) errors.push("report digest is missing or malformed");
    if (!denseArray(input.gates) || input.gates.length !== 7) errors.push("report must contain seven dense ordered gates");
    else {
      input.gates.forEach(function (gate, index) {
        var gateFields = ["id", "name", "status", "code", "stage", "evidenceClass", "basis", "statement", "hypotheses", "witness", "observed", "required", "signedMargin", "tolerance", "impossibleInDeclaredModel"];
        if (!isPlainObject(gate) || gate.id !== "G" + index) errors.push("gate " + index + " identity/order mismatch");
        if (!gate || ["PASS", "FAIL", "INCONCLUSIVE", "MARGINAL", "NOT_RUN", "NOT_APPLICABLE"].indexOf(gate.status) < 0) errors.push("gate " + index + " has invalid status");
        if (isPlainObject(gate)) {
          Object.keys(gate).filter(function (key) { return gateFields.indexOf(key) < 0; }).forEach(function (key) { errors.push("gate " + index + " has unknown field " + key); });
          if (!INVERSE_EVIDENCE_BASES[gate.evidenceClass] || INVERSE_EVIDENCE_BASES[gate.evidenceClass].indexOf(gate.basis) < 0) errors.push("gate " + index + " has an invalid evidenceClass/basis pair");
          if (!denseArray(gate.hypotheses) || gate.hypotheses.some(function (entry) { return typeof entry !== "string"; })) errors.push("gate " + index + " hypotheses must be a dense string array");
          if (typeof gate.impossibleInDeclaredModel !== "boolean") errors.push("gate " + index + " impossibility flag must be boolean");
        }
      });
      if (input.status !== overallStatus(input.gates)) errors.push("overall status does not match ordered gates");
    }
    if (!denseArray(input.candidates) || !denseArray(input.obstructionCertificates) || !denseArray(input.repairProposals)) errors.push("report candidate/certificate/proposal collections must be dense arrays");
    if (input.normalizedRequest == null) {
      if (input.requestDigest !== null) errors.push("rejected raw report must not bind an unbounded request digest");
      if (!input.gates || !input.gates[0] || input.gates[0].status !== "FAIL") errors.push("report without a normalized request must fail G0");
    } else {
      var normalization = normalizeRequest(input.normalizedRequest);
      if (!normalization.valid) errors.push("normalized request no longer satisfies the closed schema");
      else if (stableStringify(normalization.normalized) !== stableStringify(input.normalizedRequest)) errors.push("normalized request is not in canonical form");
      if (digestValue(input.normalizedRequest) !== input.requestDigest) errors.push("request digest mismatch");
      if (input.requestId !== input.normalizedRequest.id) errors.push("request id does not match normalized request");
      if (normalization.valid) {
        var replayed = compileInverseDesign(input.normalizedRequest);
        if (stableStringify(replayed) !== stableStringify(input)) errors.push("report does not replay from its normalized request");
      }
    }
    if (input.selectedCandidateId != null) {
      if (typeof input.selectedCandidateId !== "string" || !denseArray(input.candidates) || !input.candidates.some(function (candidate) { return isPlainObject(candidate) && candidate.id === input.selectedCandidateId; })) errors.push("selected candidate is not present in the candidate collection");
    }
    if (!isPlainObject(input.replay) || input.replay.platformIndependentInputsDigest !== input.requestDigest) errors.push("replay input binding mismatch");
    try {
      var payload = cloneCanonical(input);
      delete payload.reportDigest;
      if (digestValue(payload) !== input.reportDigest) errors.push("report digest mismatch");
    } catch (error) { errors.push(error.message); }
    return { valid: errors.length === 0, errors: errors };
  }

  function tetrahedronComplex() {
    return {
      nodes: [0, 1, 2, 3].map(function (id) { return { id: id, label: "v" + id, x: 0, y: 0, z: 0, radius: 1 }; }),
      edges: [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]].map(function (edge) { return { source: edge[0], target: edge[1], length: 1, weight: 1 }; }),
      faces: [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]]
    };
  }

  function complexFromFaces(vertexCount, rawFaces) {
    var edgeMap = Object.create(null);
    var faces = rawFaces.map(function (face) { return face.slice(); });
    faces.forEach(function (face) {
      [[face[0], face[1]], [face[1], face[2]], [face[2], face[0]]].forEach(function (pair) {
        var source = Math.min(pair[0], pair[1]), target = Math.max(pair[0], pair[1]);
        edgeMap[edgeKey(source, target)] = { source: source, target: target, length: 1, weight: 1 };
      });
    });
    return {
      nodes: new Array(vertexCount).fill(null).map(function (_, id) { return { id: id, label: "v" + id }; }),
      edges: Object.keys(edgeMap).map(function (key) { return edgeMap[key]; }).sort(function (a, b) { return a.source - b.source || a.target - b.target; }),
      faces: faces
    };
  }

  function triangleDiskComplex() {
    return complexFromFaces(3, [[0, 1, 2]]);
  }

  function annulusComplex(sectors) {
    var faces = [];
    for (var index = 0; index < sectors; index += 1) {
      var next = (index + 1) % sectors;
      var outer = index, outerNext = next;
      var inner = sectors + index, innerNext = sectors + next;
      faces.push([outer, outerNext, inner]);
      faces.push([outerNext, innerNext, inner]);
    }
    return complexFromFaces(2 * sectors, faces);
  }

  function periodicTorusComplex(side) {
    function vertex(column, row) {
      return ((row + side) % side) * side + ((column + side) % side);
    }
    var faces = [];
    for (var row = 0; row < side; row += 1) {
      for (var column = 0; column < side; column += 1) {
        faces.push([vertex(column, row), vertex(column + 1, row), vertex(column, row + 1)]);
        faces.push([vertex(column + 1, row), vertex(column + 1, row + 1), vertex(column, row + 1)]);
      }
    }
    return complexFromFaces(side * side, faces);
  }

  function baseRequest(id, kind, surface, boundaryComponents, complex, model) {
    return {
      schemaVersion: 2,
      id: id,
      seed: "exact-deterministic",
      target: {
        kind: kind,
        topology: { surface: surface, orientable: true, boundaryComponents: boundaryComponents },
        discretization: { complex: complex }
      },
      models: [model],
      constraints: { radiusBounds: [0.5, 2], edgeLengthBounds: [1e-9, 10], allowTopologyChange: false },
      verification: { gbTolerance: 0, chowLuoGuard: 1e-8, exactSubsetLimit: 18, optimizerTolerance: 1e-8, maxIterations: 0, refinementLevels: 0, uncertaintySamples: 0 }
    };
  }

  function representativeRequest(id) {
    var request;
    if (id === "tetra-uniform-pass") {
      request = baseRequest(id, "intrinsic-curvature", "sphere", 0, tetrahedronComplex(), "circle-packing-tangency");
      request.target.curvature = { basis: "symbolic-pi", piCoefficients: [1, 1, 1, 1].map(function (n) { return { numerator: n, denominator: 1 }; }) };
      return request;
    }
    if (id === "triangle-valid-pass") {
      var trianglePass = triangleDiskComplex();
      request = baseRequest(id, "intrinsic-edge-metric", "disk", 1, trianglePass, "edge-metric");
      request.target.edgeLengths = trianglePass.edges.map(function () { return 1; });
      return request;
    }
    if (id === "annulus-valid-pass") {
      var annulus = annulusComplex(5);
      request = baseRequest(id, "intrinsic-edge-metric", "annulus", 2, annulus, "edge-metric");
      request.target.edgeLengths = annulus.edges.map(function () { return 1; });
      return request;
    }
    if (id === "torus-valid-pass") {
      var torus = periodicTorusComplex(3);
      request = baseRequest(id, "intrinsic-edge-metric", "torus", 0, torus, "edge-metric");
      request.target.edgeLengths = torus.edges.map(function () { return 1; });
      return request;
    }
    if (id === "tetra-subset-reject") {
      request = baseRequest(id, "intrinsic-curvature", "sphere", 0, tetrahedronComplex(), "circle-packing-tangency");
      request.target.curvature = { basis: "symbolic-pi", piCoefficients: [{ numerator: -6, denominator: 5 }, { numerator: 26, denominator: 15 }, { numerator: 26, denominator: 15 }, { numerator: 26, denominator: 15 }] };
      return request;
    }
    if (id === "sphere-zero-reject") {
      request = baseRequest(id, "intrinsic-curvature", "sphere", 0, tetrahedronComplex(), "circle-packing-tangency");
      request.target.curvature = { basis: "symbolic-pi", piCoefficients: [0, 0, 0, 0].map(function (n) { return { numerator: n, denominator: 1 }; }) };
      return request;
    }
    if (id === "triangle-equality-reject") {
      var triangle = { nodes: [{ id: 0 }, { id: 1 }, { id: 2 }], edges: [{ source: 0, target: 1 }, { source: 0, target: 2 }, { source: 1, target: 2 }], faces: [[0, 1, 2]] };
      request = baseRequest(id, "intrinsic-edge-metric", "disk", 1, triangle, "edge-metric");
      request.target.edgeLengths = [1, 1, 2];
      return request;
    }
    throw new Error("Unknown representative inverse request: " + id);
  }

  return deepFreeze({
    VERSION: VERSION,
    SCHEMA_VERSION: SCHEMA_VERSION,
    DIGEST_ALGORITHM: DIGEST_ALGORITHM,
    LIMITS: LIMITS,
    stableStringify: stableStringify,
    digestValue: digestValue,
    normalizeRequest: normalizeRequest,
    compileInverseDesign: compileInverseDesign,
    validateCompilerReport: validateCompilerReport,
    representativeRequest: representativeRequest,
    listRepresentativeRequests: function () { return ["tetra-uniform-pass", "triangle-valid-pass", "annulus-valid-pass", "torus-valid-pass", "tetra-subset-reject", "sphere-zero-reject", "triangle-equality-reject"]; }
  });
});
