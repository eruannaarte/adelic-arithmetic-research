/*
 * Global Geometry II — bounded programmable-sheet and HIL emulator slice.
 *
 * This module contains no serial, USB, camera, network, filesystem, timer, or
 * device-discovery access.  Its q-star curvature budget is an exact finite
 * combinatorial identity.  Its hinge/height response and synthetic sensing are
 * explicitly engineering models: they neither establish a unique embedding nor
 * predict a physical material without later calibration and validation.
 * Protocol-v2 CRC32 detects frame corruption over exact canonical bytes;
 * SHA-256 state/content bindings support replay but are not authentication.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    var base = null, g2 = null, inverse = null;
    try { base = require("./global-geometry-core.js"); } catch (ignoredBase) { base = null; }
    try { g2 = require("./global-geometry-ii-core.js"); } catch (ignoredG2) { g2 = null; }
    try { inverse = require("./global-geometry-ii-inverse.js"); } catch (ignoredInverse) { inverse = null; }
    module.exports = factory(base, g2, inverse);
  } else {
    root.GlobalGeometryIISheet = factory(
      root.GlobalGeometryCore || null,
      root.GlobalGeometryII || null,
      root.GlobalGeometryIIInverse || null
    );
  }
})(typeof self !== "undefined" ? self : this, function (Base, G2, Inverse) {
  "use strict";

  var VERSION = "0.2.0-alpha.1";
  var SCHEMA_VERSION = 2;
  var PROTOCOL = "ggii-hil/2";
  var PI = Math.PI;
  var MESSAGE_TYPES = ["HELLO", "CAPABILITIES", "ARM", "COMMAND", "TELEMETRY", "HOLD", "DISARM", "ESTOP", "FAULT"];
  var STATES = ["DISARMED", "ARMED", "HOLD", "FAULT", "ESTOP"];
  var LIMITS = deepFreeze({
    qMin: 5,
    qMax: 7,
    maxChannels: 7,
    maxTranscriptEvents: 1024,
    maxSeq: 2147483647,
    maxTimeMs: 9007199254740991,
    maxSeedLength: 128,
    maxIdentifierLength: 128,
    maxFrameBytes: 65536,
    maxCanonicalBytes: 67108864,
    maxCanonicalArrayLength: 8192,
    maxCanonicalObjectKeys: 256,
    maxCanonicalStringLength: 65536
  });
  var INTRINSIC_EVIDENCE = deepFreeze({
    evidenceClass: "exact-finite-identity",
    basis: "combinatorial-identity",
    stage: "intrinsic",
    claimBoundary: "Exact only for the declared equilateral finite incidence complex."
  });
  var EXTRINSIC_EVIDENCE = deepFreeze({
    status: "engineering",
    basis: "model",
    evidenceClass: "finite-numerical-estimate",
    stage: "embedding",
    mechanicalUniquenessClaim: false,
    physicalValidationClaim: false,
    claimBoundary: "Bounded virtual hinge/height response only; not a constitutive law, unique mechanics, or physical validation."
  });
  var SYNTHETIC_MEASUREMENT_EVIDENCE = deepFreeze({
    status: "engineering",
    basis: "synthetic-transform",
    evidenceClass: "finite-numerical-estimate",
    synthetic: true,
    physicalMeasurement: false,
    uniquenessClaim: false,
    claimBoundary: "Synthetic virtual-channel observation only; not camera observability, physical calibration, or validation."
  });

  function own(value, key) { return Object.prototype.hasOwnProperty.call(value, key); }

  function safeOwnValue(value, key) {
    try {
      if (!value || (typeof value !== "object" && typeof value !== "function")) return undefined;
      var descriptor = Object.getOwnPropertyDescriptor(value, key);
      return descriptor && own(descriptor, "value") ? descriptor.value : undefined;
    } catch (error) { return undefined; }
  }

  function hasOnlyOrdinaryPrototype(value) {
    var prototype = Object.getPrototypeOf(value);
    if (prototype === null) return true;
    if (Object.getPrototypeOf(prototype) !== null) return false;
    return own(prototype, "constructor") && own(prototype, "hasOwnProperty") && own(prototype, "toString");
  }

  function isPlainObject(value) {
    if (!value || typeof value !== "object" || Array.isArray(value) || Object.prototype.toString.call(value) !== "[object Object]") return false;
    try { return hasOnlyOrdinaryPrototype(value); } catch (error) { return false; }
  }

  function finite(value) { return typeof value === "number" && isFinite(value); }

  function deepFreeze(value) {
    if (!value || typeof value !== "object" || Object.isFrozen(value)) return value;
    Object.keys(value).forEach(function (key) { deepFreeze(value[key]); });
    return Object.freeze(value);
  }

  function assertWellFormedString(value, path, maximumLength) {
    if (value.length > (maximumLength == null ? LIMITS.maxCanonicalStringLength : maximumLength)) throw new Error(path + " exceeds the string bound.");
    for (var i = 0; i < value.length; i += 1) {
      var code = value.charCodeAt(i);
      if (code >= 0xd800 && code <= 0xdbff) {
        if (i + 1 >= value.length) throw new Error(path + " contains an unpaired UTF-16 surrogate.");
        var low = value.charCodeAt(i + 1);
        if (low < 0xdc00 || low > 0xdfff) throw new Error(path + " contains an unpaired UTF-16 surrogate.");
        i += 1;
      } else if (code >= 0xdc00 && code <= 0xdfff) throw new Error(path + " contains an unpaired UTF-16 surrogate.");
    }
    return value;
  }

  function assertOwnDataProperties(value, path) {
    if (Object.getOwnPropertySymbols(value).length) throw new Error(path + " contains symbol properties.");
    Object.getOwnPropertyNames(value).forEach(function (key) {
      if (Array.isArray(value) && key === "length") return;
      var descriptor = Object.getOwnPropertyDescriptor(value, key);
      if (!descriptor || !own(descriptor, "value") || descriptor.enumerable !== true) throw new Error(path + "." + key + " must be an enumerable own data property.");
    });
  }

  function assertDenseArray(value, path, maximumLength) {
    if (!Array.isArray(value)) throw new Error(path + " must be an array.");
    var arrayPrototype = Object.getPrototypeOf(value);
    if (!Array.isArray(arrayPrototype) || arrayPrototype.length !== 0) throw new Error(path + " must use an ordinary array prototype.");
    if (value.length > (maximumLength == null ? LIMITS.maxCanonicalArrayLength : maximumLength)) throw new Error(path + " exceeds the array bound.");
    assertOwnDataProperties(value, path);
    var names = Object.getOwnPropertyNames(value).filter(function (key) { return key !== "length"; });
    if (names.length !== value.length) throw new Error(path + " must be dense and undecorated.");
    for (var i = 0; i < value.length; i += 1) {
      if (!own(value, String(i))) throw new Error(path + " must be dense and undecorated.");
    }
    return value;
  }

  function canonicalValue(value, path, depth, state) {
    path = path || "root";
    depth = depth || 0;
    state = state || { nodes: 0 };
    state.nodes += 1;
    if (state.nodes > 1048576) throw new Error(path + " exceeds the canonical node bound.");
    if (depth > 48) throw new Error(path + " exceeds the serialization depth bound.");
    if (value === null || typeof value === "boolean") return value;
    if (typeof value === "string") return assertWellFormedString(value, path);
    if (typeof value === "number") {
      if (!isFinite(value)) throw new Error(path + " contains a non-finite number.");
      return Object.is(value, -0) ? 0 : value;
    }
    if (Array.isArray(value)) {
      assertDenseArray(value, path);
      return value.map(function (item, index) { return canonicalValue(item, path + "[" + index + "]", depth + 1, state); });
    }
    if (isPlainObject(value)) {
      assertOwnDataProperties(value, path);
      var keys = Object.keys(value);
      if (keys.length > LIMITS.maxCanonicalObjectKeys) throw new Error(path + " exceeds the object-key bound.");
      var result = {};
      keys.sort().forEach(function (key) {
        if (key === "__proto__" || key === "prototype" || key === "constructor") throw new Error(path + " contains a forbidden key.");
        if (typeof value[key] === "undefined" || typeof value[key] === "function") throw new Error(path + "." + key + " is not serializable.");
        result[key] = canonicalValue(value[key], path + "." + key, depth + 1, state);
      });
      return result;
    }
    throw new Error(path + " contains an unsupported value.");
  }

  function clone(value) { return canonicalValue(value); }
  function stableStringify(value) {
    var text = JSON.stringify(canonicalValue(value));
    if (utf8ByteLength(text) > LIMITS.maxCanonicalBytes) throw new Error("Canonical representation exceeds the byte-oriented release bound.");
    return text;
  }

  function sha256Hex(text) {
    assertWellFormedString(text, "sha256 input", LIMITS.maxCanonicalBytes);
    var bytes = utf8Bytes(text), words = [], bitLength = bytes.length * 8;
    bytes.push(0x80);
    while ((bytes.length % 64) !== 56) bytes.push(0);
    var high = Math.floor(bitLength / 4294967296), lowLength = bitLength >>> 0;
    bytes.push((high >>> 24) & 255, (high >>> 16) & 255, (high >>> 8) & 255, high & 255, (lowLength >>> 24) & 255, (lowLength >>> 16) & 255, (lowLength >>> 8) & 255, lowLength & 255);
    var h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    var k = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
    function rotr(value, amount) { return (value >>> amount) | (value << (32 - amount)); }
    for (var offset = 0; offset < bytes.length; offset += 64) {
      for (var i = 0; i < 16; i += 1) words[i] = ((bytes[offset + 4*i] << 24) | (bytes[offset + 4*i + 1] << 16) | (bytes[offset + 4*i + 2] << 8) | bytes[offset + 4*i + 3]) >>> 0;
      for (var wi = 16; wi < 64; wi += 1) {
        var s0 = rotr(words[wi-15],7) ^ rotr(words[wi-15],18) ^ (words[wi-15] >>> 3);
        var s1 = rotr(words[wi-2],17) ^ rotr(words[wi-2],19) ^ (words[wi-2] >>> 10);
        words[wi] = (words[wi-16] + s0 + words[wi-7] + s1) >>> 0;
      }
      var a=h[0],b=h[1],c=h[2],d=h[3],e=h[4],f=h[5],g=h[6],hh=h[7];
      for (var round = 0; round < 64; round += 1) {
        var big1 = rotr(e,6) ^ rotr(e,11) ^ rotr(e,25);
        var choice = (e & f) ^ (~e & g);
        var temp1 = (hh + big1 + choice + k[round] + words[round]) >>> 0;
        var big0 = rotr(a,2) ^ rotr(a,13) ^ rotr(a,22);
        var majority = (a & b) ^ (a & c) ^ (b & c);
        var temp2 = (big0 + majority) >>> 0;
        hh=g; g=f; f=e; e=(d+temp1)>>>0; d=c; c=b; b=a; a=(temp1+temp2)>>>0;
      }
      h[0]=(h[0]+a)>>>0;h[1]=(h[1]+b)>>>0;h[2]=(h[2]+c)>>>0;h[3]=(h[3]+d)>>>0;h[4]=(h[4]+e)>>>0;h[5]=(h[5]+f)>>>0;h[6]=(h[6]+g)>>>0;h[7]=(h[7]+hh)>>>0;
    }
    return h.map(function (value) { return ("00000000" + value.toString(16)).slice(-8); }).join("");
  }

  function digestValue(value) { return sha256Hex(stableStringify(value)); }

  function assertClosedObject(value, allowed, path) {
    if (!isPlainObject(value)) throw new Error(path + " must be a plain object.");
    assertOwnDataProperties(value, path);
    for (var inherited in value) if (!own(value, inherited)) throw new Error(path + " contains inherited enumerable field " + inherited + ".");
    var keys = Object.keys(value);
    if (keys.length > LIMITS.maxCanonicalObjectKeys) throw new Error(path + " exceeds the object-key bound.");
    var unknown = keys.filter(function (key) { return allowed.indexOf(key) < 0; }).sort();
    if (unknown.length) throw new Error(path + " contains unknown field " + unknown[0] + ".");
    return value;
  }

  function assertInteger(value, path, low, high) {
    if (!Number.isInteger(value) || value < low || value > high) throw new Error(path + " must be an integer in [" + low + ", " + high + "].");
    return value;
  }

  function assertFiniteRange(value, path, low, high) {
    if (!finite(value) || value < low || value > high) throw new Error(path + " must be finite in [" + low + ", " + high + "].");
    return value;
  }

  function assertIdentifier(value, path) {
    if (typeof value !== "string" || !/^[a-z0-9][a-z0-9._:-]*$/i.test(value) || value.length > LIMITS.maxIdentifierLength) {
      throw new Error(path + " must be a bounded identifier.");
    }
    return value;
  }

  function assertSeed(value, path) {
    if (typeof value !== "string" || !value.length || value.length > LIMITS.maxSeedLength) throw new Error(path + " must be a named non-empty seed of at most " + LIMITS.maxSeedLength + " characters.");
    return value;
  }

  function fieldOr(value, key, fallback) { return own(value, key) && value[key] != null ? value[key] : fallback; }

  function clamp(value, low, high) { return Math.max(low, Math.min(high, value)); }
  function roundedDisplay(value) { return Number(value.toFixed(9)); }
  function pad2(value) { return ("0" + value).slice(-2); }
  function channelId(index) { return "hinge-" + pad2(index); }
  function faceId(index) { return "face-" + pad2(index); }

  function gcd(a, b) {
    a = Math.abs(a); b = Math.abs(b);
    while (b) { var remainder = a % b; a = b; b = remainder; }
    return a || 1;
  }

  function rational(numerator, denominator) {
    if (!Number.isSafeInteger(numerator) || !Number.isSafeInteger(denominator) || denominator === 0) throw new Error("Invalid exact rational.");
    if (denominator < 0) { numerator = -numerator; denominator = -denominator; }
    var divisor = gcd(numerator, denominator);
    return { numerator: numerator / divisor, denominator: denominator / divisor };
  }

  function rationalAdd(a, b) { return rational(a.numerator * b.denominator + b.numerator * a.denominator, a.denominator * b.denominator); }
  function rationalEqual(a, b) { return a.numerator * b.denominator === b.numerator * a.denominator; }
  function rationalNumber(value) { return value.numerator / value.denominator; }

  function normalizeQStarOptions(options) {
    options = options || {};
    assertClosedObject(options, ["sideLengthMm"], "q-star options");
    return { sideLengthMm: options.sideLengthMm == null ? 60 : assertFiniteRange(options.sideLengthMm, "q-star options.sideLengthMm", 1, 1000) };
  }

  function createQStar(q, options) {
    assertInteger(q, "q", LIMITS.qMin, LIMITS.qMax);
    var selected = normalizeQStarOptions(options);
    var nodes = [{ id: 0, label: "center", role: "interior", x: 0, y: 0, z: 0 }];
    var faces = [], edges = [];
    for (var i = 0; i < q; i += 1) {
      var theta = 2 * PI * i / q;
      nodes.push({ id: i + 1, label: "boundary-" + pad2(i), role: "boundary", x: roundedDisplay(selected.sideLengthMm * Math.cos(theta)), y: roundedDisplay(selected.sideLengthMm * Math.sin(theta)), z: 0 });
      faces.push([0, i + 1, ((i + 1) % q) + 1]);
      edges.push({ id: "radial-" + pad2(i), source: 0, target: i + 1, lengthMm: selected.sideLengthMm, role: "hinge" });
      edges.push({ id: "boundary-" + pad2(i), source: i + 1, target: ((i + 1) % q) + 1, lengthMm: selected.sideLengthMm, role: "boundary" });
    }
    edges.sort(function (a, b) { return a.id < b.id ? -1 : a.id > b.id ? 1 : 0; });

    var center = rational(6 - q, 3);
    var boundary = rational(1, 3);
    var total = center;
    for (var b = 0; b < q; b += 1) total = rationalAdd(total, boundary);
    var expected = rational(2, 1);
    var intrinsic = {
      model: "equilateral-integer-valence",
      angleUnit: "pi-radians",
      center: { vertex: 0, valence: q, defectPiCoefficient: center, defectRadians: rationalNumber(center) * PI },
      boundary: nodes.slice(1).map(function (node) {
        return { vertex: node.id, incidentCorners: 2, defectPiCoefficient: boundary, defectRadians: PI / 3 };
      }),
      totalDefectPiCoefficient: total,
      requiredDiskTotalPiCoefficient: expected,
      exactGaussBonnetIdentity: rationalEqual(total, expected),
      symbolicIdentity: "((6-q)/3 + q/3)pi = 2pi",
      evidence: INTRINSIC_EVIDENCE
    };
    var complex = {
      nodes: nodes,
      edges: edges,
      faces: faces,
      metadata: {
        generator: "ggii-equilateral-q-star-v1",
        topology: "disk",
        q: q,
        intrinsicSideLengthMm: selected.sideLengthMm,
        coordinateCaveat: "Node coordinates are a schematic display placement; declared edge lengths and face incidence are authoritative for q not equal to 6."
      }
    };
    var optionalAudit = {
      method: "closed-form-q-star-incidence",
      surfaceValid: true,
      bettiGF2: [1, 0, 0],
      baseCrossCheck: "optional-non-authoritative"
    };
    if (Base && typeof Base.surfaceValidity === "function" && typeof Base.computeBettiNumbers === "function") {
      var baseComplex = {
        nodes: nodes.map(function (node) { return { id: node.id, label: node.label, x: node.x, y: node.y, z: node.z, radius: 1 }; }),
        edges: edges.map(function (edge) { return { source: edge.source, target: edge.target, length: edge.lengthMm, weight: 1 }; }),
        faces: faces.map(function (face) { return face.slice(); }),
        metadata: { topologyHint: "disk", metricSource: "declared-equilateral-edge-lengths" }
      };
      var checkedSurface = Base.surfaceValidity(baseComplex, { metric: "embedded" });
      var checkedTopology = Base.computeBettiNumbers(baseComplex);
      if (!checkedSurface.valid || stableStringify(checkedTopology.betti.array) !== "[1,0,0]") throw new Error("Optional base cross-check contradicted the exact q-star incidence audit.");
    }
    var result = {
      schemaVersion: SCHEMA_VERSION,
      id: "star-q" + q,
      q: q,
      sideLengthMm: selected.sideLengthMm,
      complex: complex,
      faceLocalGeometryMm: { vertices: [[0, 0], [selected.sideLengthMm, 0], [selected.sideLengthMm / 2, selected.sideLengthMm * Math.sqrt(3) / 2]], authoritativeForIntrinsicFaceShape: true },
      counts: { vertices: q + 1, edges: 2 * q, faces: q, eulerCharacteristic: 1, boundaryComponents: 1 },
      intrinsic: intrinsic,
      optionalDependencyAudit: optionalAudit,
      downstreamClaimsNotEstablished: ["unique extrinsic embedding", "elastic equilibrium", "fabrication accuracy", "camera observability", "physical validation"]
    };
    result.designDigest = digestValue(result);
    return deepFreeze(clone(result));
  }

  function seedHash(seed) {
    var hash = 2166136261 >>> 0;
    for (var i = 0; i < seed.length; i += 1) { hash ^= seed.charCodeAt(i); hash = Math.imul(hash, 16777619); }
    return hash >>> 0;
  }

  function seededRandom(seed) {
    var state = seedHash(seed) || 0x6d2b79f5;
    return function () {
      state += 0x6d2b79f5;
      var t = state;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function gaussian(random) {
    var u = Math.max(random(), 1 / 4294967296);
    var v = random();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * PI * v);
  }

  function normalizePlantConfig(raw) {
    raw = raw || {};
    assertClosedObject(raw, ["schemaVersion", "q", "seed", "sideLengthMm", "embeddingBranch", "maxPositionDeg", "maxRateDegPerSec", "quantizationDeg", "backlashDeg", "heightLimitMm", "commandDelayMs"], "plant config");
    if (raw.schemaVersion != null && raw.schemaVersion !== SCHEMA_VERSION) throw new Error("plant config.schemaVersion must equal " + SCHEMA_VERSION + ".");
    var config = {
      schemaVersion: SCHEMA_VERSION,
      q: assertInteger(fieldOr(raw, "q", 6), "plant config.q", LIMITS.qMin, LIMITS.qMax),
      seed: assertSeed(fieldOr(raw, "seed", "ggii-sheet-plant-default"), "plant config.seed"),
      sideLengthMm: assertFiniteRange(fieldOr(raw, "sideLengthMm", 60), "plant config.sideLengthMm", 1, 1000),
      embeddingBranch: fieldOr(raw, "embeddingBranch", 1),
      maxPositionDeg: assertFiniteRange(fieldOr(raw, "maxPositionDeg", 35), "plant config.maxPositionDeg", 1, 90),
      maxRateDegPerSec: assertFiniteRange(fieldOr(raw, "maxRateDegPerSec", 20), "plant config.maxRateDegPerSec", 0.1, 360),
      quantizationDeg: assertFiniteRange(fieldOr(raw, "quantizationDeg", 0.1), "plant config.quantizationDeg", 0, 5),
      backlashDeg: assertFiniteRange(fieldOr(raw, "backlashDeg", 0.2), "plant config.backlashDeg", 0, 10),
      heightLimitMm: assertFiniteRange(fieldOr(raw, "heightLimitMm", 30), "plant config.heightLimitMm", 1, 500),
      commandDelayMs: assertInteger(fieldOr(raw, "commandDelayMs", 0), "plant config.commandDelayMs", 0, 10000)
    };
    if (config.embeddingBranch !== 1 && config.embeddingBranch !== -1) throw new Error("plant config.embeddingBranch must be -1 or 1.");
    if (config.backlashDeg >= config.maxPositionDeg) throw new Error("plant config.backlashDeg must be less than maxPositionDeg.");
    return deepFreeze(config);
  }

  function computeHeightField(config, channels) {
    var q = config.q, mean = 0;
    channels.forEach(function (channel) { mean += channel.positionDeg; });
    mean /= q;
    var centerBias = config.embeddingBranch * (6 - q) * config.sideLengthMm * 0.08;
    var centerControl = config.embeddingBranch * mean * config.sideLengthMm / 360;
    var center = clamp(centerBias + centerControl, -config.heightLimitMm, config.heightLimitMm);
    var vertices = [{ id: 0, heightMm: center }];
    for (var i = 0; i < q; i += 1) {
      var theta = 2 * PI * i / q;
      var saddleMode = config.embeddingBranch * (q - 6) * config.sideLengthMm * 0.06 * Math.cos(2 * theta);
      var next = channels[(i + 1) % q].positionDeg;
      var localControl = config.embeddingBranch * (channels[i].positionDeg + next) * config.sideLengthMm / 1440;
      vertices.push({ id: i + 1, heightMm: clamp(saddleMode + localControl, -config.heightLimitMm, config.heightLimitMm) });
    }
    var faceHeights = [];
    for (var f = 0; f < q; f += 1) {
      faceHeights.push({ id: faceId(f), heightMm: (vertices[0].heightMm + vertices[f + 1].heightMm + vertices[((f + 1) % q) + 1].heightMm) / 3 });
    }
    var meanHeight = 0;
    vertices.forEach(function (vertex) { meanHeight += vertex.heightMm; });
    meanHeight /= vertices.length;
    var square = 0;
    vertices.forEach(function (vertex) { var difference = vertex.heightMm - meanHeight; square += difference * difference; });
    return { centerHeightMm: center, vertexHeights: vertices, faceHeights: faceHeights, heightRangeMm: Math.max.apply(null, vertices.map(function (v) { return v.heightMm; })) - Math.min.apply(null, vertices.map(function (v) { return v.heightMm; })), planeRmsProxyMm: Math.sqrt(square / vertices.length) };
  }

  function createVirtualPlant(rawConfig) {
    var config = normalizePlantConfig(rawConfig);
    var configDigest = digestValue(config);
    var plantId = "plant-" + configDigest.slice(0, 24);
    var state = {
      timeMs: 0,
      revision: 0,
      channels: [],
      pending: []
    };
    for (var i = 0; i < config.q; i += 1) state.channels.push({ id: channelId(i), positionDeg: 0, targetDeg: 0, activeRateDegPerSec: config.maxRateDegPerSec });

    function incrementRevision() {
      if (state.revision >= LIMITS.maxTimeMs) throw new Error("Virtual plant state revision exhausted.");
      state.revision += 1;
    }

    function applyPendingUntil(timeMs) {
      state.pending.sort(function (a, b) { return a.applyAtMs - b.applyAtMs || (a.id < b.id ? -1 : 1); });
      while (state.pending.length && state.pending[0].applyAtMs <= timeMs) {
        var applyAt = state.pending[0].applyAtMs;
        advancePositions(applyAt);
        var due = state.pending.filter(function (entry) { return entry.applyAtMs === applyAt; });
        state.pending = state.pending.filter(function (entry) { return entry.applyAtMs !== applyAt; });
        due.forEach(function (entry) {
          var channel = state.channels.filter(function (candidate) { return candidate.id === entry.id; })[0];
          channel.targetDeg = entry.positionDeg;
          channel.activeRateDegPerSec = entry.maxRateDegPerSec;
        });
        incrementRevision();
      }
      advancePositions(timeMs);
    }

    function quantize(value) {
      return config.quantizationDeg > 0 ? Math.round(value / config.quantizationDeg) * config.quantizationDeg : value;
    }

    function advancePositions(timeMs) {
      if (timeMs < state.timeMs) throw new Error("Plant time cannot move backward.");
      var dt = (timeMs - state.timeMs) / 1000;
      var changed = false;
      state.channels.forEach(function (channel) {
        var difference = channel.targetDeg - channel.positionDeg;
        if (Math.abs(difference) <= config.backlashDeg) return;
        var maximumStep = channel.activeRateDegPerSec * dt;
        var step = clamp(difference, -maximumStep, maximumStep);
        var proposed = quantize(channel.positionDeg + step);
        proposed = clamp(proposed, channel.positionDeg - maximumStep, channel.positionDeg + maximumStep);
        if (difference > 0) proposed = Math.min(proposed, channel.targetDeg);
        else proposed = Math.max(proposed, channel.targetDeg);
        proposed = clamp(proposed, -config.maxPositionDeg, config.maxPositionDeg);
        if (proposed !== channel.positionDeg) { channel.positionDeg = proposed; changed = true; }
      });
      state.timeMs = timeMs;
      if (changed) incrementRevision();
    }

    function validateCommands(commands) {
      assertDenseArray(commands, "plant commands", config.q);
      if (!commands.length) throw new Error("Plant commands must be a non-empty bounded array.");
      var seen = Object.create(null), normalized = [], violations = [];
      commands.forEach(function (raw, index) {
        assertClosedObject(raw, ["id", "positionDeg", "maxRateDegPerSec"], "plant commands[" + index + "]");
        var id = assertIdentifier(raw.id, "plant commands[" + index + "].id");
        if (!state.channels.some(function (channel) { return channel.id === id; })) throw new Error("Unknown virtual channel " + id + ".");
        if (seen[id]) throw new Error("Duplicate virtual channel " + id + ".");
        seen[id] = true;
        if (!finite(raw.positionDeg)) throw new Error("plant commands[" + index + "].positionDeg must be finite.");
        var rate = fieldOr(raw, "maxRateDegPerSec", config.maxRateDegPerSec);
        if (!finite(rate) || rate <= 0) throw new Error("plant commands[" + index + "].maxRateDegPerSec must be positive and finite.");
        if (Math.abs(raw.positionDeg) > config.maxPositionDeg || rate > config.maxRateDegPerSec) {
          violations.push({ id: id, requestedPositionDeg: raw.positionDeg, boundedPositionDeg: clamp(raw.positionDeg, -config.maxPositionDeg, config.maxPositionDeg), requestedRateDegPerSec: rate, boundedRateDegPerSec: Math.min(rate, config.maxRateDegPerSec) });
        }
        normalized.push({ id: id, positionDeg: raw.positionDeg, maxRateDegPerSec: rate });
      });
      normalized.sort(function (a, b) { return a.id < b.id ? -1 : 1; });
      return { commands: normalized, violations: violations };
    }

    function setTargets(commands, atTimeMs) {
      assertInteger(atTimeMs, "command time", 0, LIMITS.maxTimeMs);
      applyPendingUntil(atTimeMs);
      var checked = validateCommands(commands);
      if (checked.violations.length) return deepFreeze({ accepted: false, code: "SATURATION_LIMIT", violations: clone(checked.violations) });
      if (atTimeMs > LIMITS.maxTimeMs - config.commandDelayMs) return deepFreeze({ accepted: false, code: "TIME_HORIZON_LIMIT", violations: [] });
      checked.commands.forEach(function (command) {
        state.pending = state.pending.filter(function (entry) { return entry.id !== command.id; });
        state.pending.push({ id: command.id, positionDeg: command.positionDeg, maxRateDegPerSec: command.maxRateDegPerSec, applyAtMs: atTimeMs + config.commandDelayMs });
      });
      state.pending.sort(function (a, b) { return a.applyAtMs - b.applyAtMs || (a.id < b.id ? -1 : 1); });
      incrementRevision();
      return deepFreeze({ accepted: true, code: "TARGETS_QUEUED", applyAtMs: atTimeMs + config.commandDelayMs, channels: clone(checked.commands) });
    }

    function hold(atTimeMs) {
      assertInteger(atTimeMs, "hold time", 0, LIMITS.maxTimeMs);
      applyPendingUntil(atTimeMs);
      var changed = state.pending.length > 0;
      state.pending = [];
      state.channels.forEach(function (channel) {
        if (channel.targetDeg !== channel.positionDeg) changed = true;
        channel.targetDeg = channel.positionDeg;
      });
      if (changed) incrementRevision();
    }

    function snapshot() {
      var heights = computeHeightField(config, state.channels);
      var physicalState = {
        plantId: plantId,
        configDigest: configDigest,
        q: config.q,
        stateRevision: state.revision,
        channels: state.channels.map(function (channel) { return clone(channel); }),
        pendingCommands: state.pending.map(function (entry) { return clone(entry); }),
        heights: heights
      };
      var stateDigest = digestValue(physicalState);
      var output = {
        schemaVersion: SCHEMA_VERSION,
        model: "bounded-virtual-q-star-hinge-height-v1",
        plantId: plantId,
        q: config.q,
        seed: config.seed,
        timeMs: state.timeMs,
        config: config,
        configDigest: configDigest,
        stateRevision: state.revision,
        stateDigest: stateDigest,
        channels: physicalState.channels,
        pendingCommands: physicalState.pendingCommands,
        heights: heights,
        intrinsicReference: createQStar(config.q, { sideLengthMm: config.sideLengthMm }).intrinsic,
        evidence: EXTRINSIC_EVIDENCE,
        virtualOnly: true,
        hardwareAccess: false,
        digestAlgorithm: "sha256-jcs-v1"
      };
      output.snapshotDigest = digestValue(output);
      return deepFreeze(clone(output));
    }

    return Object.freeze({
      setTargets: setTargets,
      stepTo: function (timeMs) { assertInteger(timeMs, "plant step time", 0, LIMITS.maxTimeMs); applyPendingUntil(timeMs); return snapshot(); },
      hold: function (timeMs) { hold(timeMs); return snapshot(); },
      snapshot: snapshot,
      config: config,
      plantId: plantId
    });
  }

  function assertDigest(value, path) {
    if (typeof value !== "string" || !/^[0-9a-f]{64}$/.test(value)) throw new Error(path + " must be a SHA-256 hex digest.");
    return value;
  }

  function validatePlantSnapshot(value) {
    var errors = [];
    try {
      assertClosedObject(value, ["schemaVersion", "model", "plantId", "q", "seed", "timeMs", "config", "configDigest", "stateRevision", "stateDigest", "channels", "pendingCommands", "heights", "intrinsicReference", "evidence", "virtualOnly", "hardwareAccess", "digestAlgorithm", "snapshotDigest"], "plant snapshot");
      if (value.schemaVersion !== SCHEMA_VERSION) throw new Error("plant snapshot.schemaVersion mismatch.");
      if (value.model !== "bounded-virtual-q-star-hinge-height-v1") throw new Error("plant snapshot.model mismatch.");
      if (typeof value.plantId !== "string" || !/^plant-[0-9a-f]{24}$/.test(value.plantId)) throw new Error("plant snapshot.plantId malformed.");
      assertInteger(value.q, "plant snapshot.q", LIMITS.qMin, LIMITS.qMax);
      assertSeed(value.seed, "plant snapshot.seed");
      assertInteger(value.timeMs, "plant snapshot.timeMs", 0, LIMITS.maxTimeMs);
      assertInteger(value.stateRevision, "plant snapshot.stateRevision", 0, LIMITS.maxTimeMs);
      var normalizedConfig = normalizePlantConfig(value.config);
      if (normalizedConfig.q !== value.q || normalizedConfig.seed !== value.seed) throw new Error("plant snapshot config identity mismatch.");
      var configDigest = digestValue(normalizedConfig);
      if (configDigest !== value.configDigest) throw new Error("plant snapshot.configDigest mismatch.");
      if (value.plantId !== "plant-" + configDigest.slice(0, 24)) throw new Error("plant snapshot.plantId does not match config.");
      assertDenseArray(value.channels, "plant snapshot.channels", value.q);
      if (value.channels.length !== value.q) throw new Error("plant snapshot.channels must contain exactly q entries.");
      value.channels.forEach(function (channel, index) {
        assertClosedObject(channel, ["id", "positionDeg", "targetDeg", "activeRateDegPerSec"], "plant snapshot.channels[" + index + "]");
        if (channel.id !== channelId(index)) throw new Error("plant snapshot channel order/id mismatch.");
        assertFiniteRange(channel.positionDeg, "plant snapshot channel.positionDeg", -normalizedConfig.maxPositionDeg, normalizedConfig.maxPositionDeg);
        assertFiniteRange(channel.targetDeg, "plant snapshot channel.targetDeg", -normalizedConfig.maxPositionDeg, normalizedConfig.maxPositionDeg);
        assertFiniteRange(channel.activeRateDegPerSec, "plant snapshot channel.activeRateDegPerSec", 0.000000001, normalizedConfig.maxRateDegPerSec);
      });
      assertDenseArray(value.pendingCommands, "plant snapshot.pendingCommands", value.q);
      var pendingSeen = Object.create(null), lastPendingKey = null;
      value.pendingCommands.forEach(function (entry, index) {
        assertClosedObject(entry, ["id", "positionDeg", "maxRateDegPerSec", "applyAtMs"], "plant snapshot.pendingCommands[" + index + "]");
        if (!/^hinge-0[0-6]$/.test(entry.id || "") || Number(entry.id.slice(-2)) >= value.q || pendingSeen[entry.id]) throw new Error("plant snapshot pending command id invalid or duplicated.");
        pendingSeen[entry.id] = true;
        assertFiniteRange(entry.positionDeg, "plant snapshot pending positionDeg", -normalizedConfig.maxPositionDeg, normalizedConfig.maxPositionDeg);
        assertFiniteRange(entry.maxRateDegPerSec, "plant snapshot pending maxRateDegPerSec", 0.000000001, normalizedConfig.maxRateDegPerSec);
        assertInteger(entry.applyAtMs, "plant snapshot pending applyAtMs", value.timeMs, LIMITS.maxTimeMs);
        var pendingKey = String(entry.applyAtMs).padStart(16, "0") + "::" + entry.id;
        if (lastPendingKey != null && pendingKey < lastPendingKey) throw new Error("plant snapshot pending commands are not canonicalized.");
        lastPendingKey = pendingKey;
      });
      var expectedHeights = computeHeightField(normalizedConfig, value.channels);
      if (stableStringify(value.heights) !== stableStringify(expectedHeights)) throw new Error("plant snapshot heights do not match the declared engineering plant.");
      if (stableStringify(value.intrinsicReference) !== stableStringify(createQStar(value.q, { sideLengthMm: normalizedConfig.sideLengthMm }).intrinsic)) throw new Error("plant snapshot intrinsic reference mismatch.");
      if (stableStringify(value.evidence) !== stableStringify(EXTRINSIC_EVIDENCE)) throw new Error("plant snapshot evidence boundary mismatch.");
      if (value.virtualOnly !== true || value.hardwareAccess !== false) throw new Error("plant snapshot virtual-only boundary mismatch.");
      if (value.digestAlgorithm !== "sha256-jcs-v1") throw new Error("plant snapshot digest algorithm mismatch.");
      assertDigest(value.stateDigest, "plant snapshot.stateDigest");
      assertDigest(value.snapshotDigest, "plant snapshot.snapshotDigest");
      var expectedStateDigest = digestValue({ plantId: value.plantId, configDigest: value.configDigest, q: value.q, stateRevision: value.stateRevision, channels: value.channels, pendingCommands: value.pendingCommands, heights: value.heights });
      if (expectedStateDigest !== value.stateDigest) throw new Error("plant snapshot.stateDigest mismatch.");
      var copy = clone(value); delete copy.snapshotDigest;
      if (digestValue(copy) !== value.snapshotDigest) throw new Error("plant snapshot.snapshotDigest mismatch.");
    } catch (error) { errors.push(error.message); }
    return deepFreeze({ valid: errors.length === 0, errors: errors });
  }

  function normalizeMeasurementOptions(raw, plant) {
    raw = raw || {};
    assertClosedObject(raw, ["schemaVersion", "seed", "sampleIndex", "monotonicTimeMs", "calibration", "noise", "criticalFaceIds", "forcedDropoutFaceIds"], "measurement options");
    if (raw.schemaVersion != null && raw.schemaVersion !== SCHEMA_VERSION) throw new Error("measurement options.schemaVersion must equal " + SCHEMA_VERSION + ".");
    var calibration = fieldOr(raw, "calibration", {});
    assertClosedObject(calibration, ["id", "frozen", "calibratedAtMs", "validUntilMs", "heightScale", "heightOffsetMm", "hingeScale", "hingeOffsetDeg"], "measurement options.calibration");
    var noise = fieldOr(raw, "noise", {});
    assertClosedObject(noise, ["heightStdMm", "hingeStdDeg", "dropoutProbability"], "measurement options.noise");
    var critical = fieldOr(raw, "criticalFaceIds", [faceId(0)]);
    var forced = fieldOr(raw, "forcedDropoutFaceIds", []);
    [critical, forced].forEach(function (list, listIndex) {
      assertDenseArray(list, listIndex ? "forcedDropoutFaceIds" : "criticalFaceIds", plant.q);
      var seen = Object.create(null);
      list.forEach(function (id) {
        assertIdentifier(id, "face id");
        if (!/^face-0[0-6]$/.test(id) || Number(id.slice(-2)) >= plant.q) throw new Error("Unknown q-star face " + id + ".");
        if (seen[id]) throw new Error("Duplicate q-star face " + id + ".");
        seen[id] = true;
      });
    });
    var time = assertInteger(fieldOr(raw, "monotonicTimeMs", plant.timeMs), "measurement options.monotonicTimeMs", 0, LIMITS.maxTimeMs);
    var calibratedAt = assertInteger(fieldOr(calibration, "calibratedAtMs", 0), "calibration.calibratedAtMs", 0, LIMITS.maxTimeMs);
    var validUntil = assertInteger(fieldOr(calibration, "validUntilMs", 1000000000000), "calibration.validUntilMs", 0, LIMITS.maxTimeMs);
    if (validUntil < calibratedAt) throw new Error("calibration.validUntilMs must not precede calibratedAtMs.");
    var frozen = fieldOr(calibration, "frozen", true);
    if (typeof frozen !== "boolean") throw new Error("calibration.frozen must be boolean.");
    return {
      schemaVersion: SCHEMA_VERSION,
      seed: assertSeed(fieldOr(raw, "seed", "ggii-sheet-measurement-default"), "measurement options.seed"),
      sampleIndex: assertInteger(fieldOr(raw, "sampleIndex", 0), "measurement options.sampleIndex", 0, 1000000000),
      monotonicTimeMs: time,
      calibration: {
        id: assertIdentifier(fieldOr(calibration, "id", "synthetic-calibration-v1"), "calibration.id"),
        frozen: frozen,
        calibratedAtMs: calibratedAt,
        validUntilMs: validUntil,
        heightScale: assertFiniteRange(fieldOr(calibration, "heightScale", 1), "calibration.heightScale", 0.5, 2),
        heightOffsetMm: assertFiniteRange(fieldOr(calibration, "heightOffsetMm", 0), "calibration.heightOffsetMm", -100, 100),
        hingeScale: assertFiniteRange(fieldOr(calibration, "hingeScale", 1), "calibration.hingeScale", 0.5, 2),
        hingeOffsetDeg: assertFiniteRange(fieldOr(calibration, "hingeOffsetDeg", 0), "calibration.hingeOffsetDeg", -90, 90)
      },
      noise: {
        heightStdMm: assertFiniteRange(fieldOr(noise, "heightStdMm", 0.25), "noise.heightStdMm", 0, 100),
        hingeStdDeg: assertFiniteRange(fieldOr(noise, "hingeStdDeg", 0.1), "noise.hingeStdDeg", 0, 90),
        dropoutProbability: assertFiniteRange(fieldOr(noise, "dropoutProbability", 0), "noise.dropoutProbability", 0, 1)
      },
      criticalFaceIds: critical.slice().sort(),
      forcedDropoutFaceIds: forced.slice().sort()
    };
  }

  function deriveObservability(q, timeMs, calibration, observedFaceIds, criticalFaceIds) {
    var missingCritical = criticalFaceIds.filter(function (id) { return observedFaceIds.indexOf(id) < 0; });
    var coverage = observedFaceIds.length / q;
    var reasons = [];
    if (calibration.frozen !== true) reasons.push("calibration-not-frozen");
    if (timeMs < calibration.calibratedAtMs || timeMs > calibration.validUntilMs) reasons.push("calibration-stale");
    if (coverage < 0.8) reasons.push("marker-coverage-below-80-percent");
    if (missingCritical.length) reasons.push("target-critical-face-missing");
    var observable = reasons.length === 0;
    return {
      status: observable ? "PASS" : "FAIL",
      code: observable ? "OBSERVABLE" : "SENSOR_UNOBSERVABLE",
      observable: observable,
      coverageFraction: coverage,
      missingCriticalFaceIds: missingCritical,
      reasons: reasons
    };
  }

  function measureVirtualPlant(plantSnapshot, rawOptions) {
    var plantReport = validatePlantSnapshot(plantSnapshot);
    if (!plantReport.valid) throw new Error("Invalid virtual plant snapshot: " + plantReport.errors.join("; "));
    var options = normalizeMeasurementOptions(rawOptions, plantSnapshot);
    if (options.monotonicTimeMs !== plantSnapshot.timeMs) throw new Error("Measurement time must equal its source plant snapshot time.");
    var random = seededRandom(options.seed + "::sample=" + options.sampleIndex + "::q=" + plantSnapshot.q);
    var dropped = [], observed = [];
    for (var i = 0; i < plantSnapshot.q; i += 1) {
      var id = faceId(i);
      if (options.forcedDropoutFaceIds.indexOf(id) >= 0 || random() < options.noise.dropoutProbability) dropped.push(id);
      else observed.push(id);
    }
    var observability = deriveObservability(plantSnapshot.q, options.monotonicTimeMs, options.calibration, observed, options.criticalFaceIds);
    var observable = observability.observable;
    var faceTruth = Object.create(null);
    plantSnapshot.heights.faceHeights.forEach(function (entry) { faceTruth[entry.id] = entry.heightMm; });
    var faceEstimates = [];
    observed.forEach(function (id) {
      faceEstimates.push({ id: id, heightMm: faceTruth[id] * options.calibration.heightScale + options.calibration.heightOffsetMm + gaussian(random) * options.noise.heightStdMm });
    });
    var hingeEstimates = plantSnapshot.channels.map(function (channel, index) {
      return { id: channel.id, observed: observed.indexOf(faceId(index)) >= 0, positionDeg: observed.indexOf(faceId(index)) >= 0 ? channel.positionDeg * options.calibration.hingeScale + options.calibration.hingeOffsetDeg + gaussian(random) * options.noise.hingeStdDeg : null };
    });
    var base = {
      schemaVersion: SCHEMA_VERSION,
      measurementId: "measurement-" + digestValue({ sourcePlantId: plantSnapshot.plantId, sourceStateRevision: plantSnapshot.stateRevision, sourceStateDigest: plantSnapshot.stateDigest, seed: options.seed, sampleIndex: options.sampleIndex, monotonicTimeMs: options.monotonicTimeMs }).slice(0, 24),
      sourceModel: plantSnapshot.model,
      sourcePlantId: plantSnapshot.plantId,
      sourceStateRevision: plantSnapshot.stateRevision,
      sourceStateDigest: plantSnapshot.stateDigest,
      sourceSnapshotDigest: plantSnapshot.snapshotDigest,
      seed: options.seed,
      sampleIndex: options.sampleIndex,
      monotonicTimeMs: options.monotonicTimeMs,
      q: plantSnapshot.q,
      calibration: options.calibration,
      noise: options.noise,
      observedFaceIds: observed,
      droppedFaceIds: dropped,
      criticalFaceIds: options.criticalFaceIds,
      observability: observability,
      estimates: {
        faceHeightsMm: faceEstimates,
        hingePositionsDeg: hingeEstimates,
        centerHeightMm: observable ? plantSnapshot.heights.centerHeightMm * options.calibration.heightScale + options.calibration.heightOffsetMm + gaussian(random) * options.noise.heightStdMm : null
      },
      uncertainty: { heightStdMm: options.noise.heightStdMm, hingeStdDeg: options.noise.hingeStdDeg, modelAdequacyBound: null },
      evidenceSeparation: {
        intrinsicReference: plantSnapshot.intrinsicReference,
        extrinsicMeasurement: SYNTHETIC_MEASUREMENT_EVIDENCE
      },
      digestAlgorithm: "sha256-jcs-v1"
    };
    base.measurementDigest = digestValue(base);
    return deepFreeze(clone(base));
  }

  function validateMeasurement(value) {
    var errors = [];
    try {
      assertClosedObject(value, ["schemaVersion", "measurementId", "sourceModel", "sourcePlantId", "sourceStateRevision", "sourceStateDigest", "sourceSnapshotDigest", "seed", "sampleIndex", "monotonicTimeMs", "q", "calibration", "noise", "observedFaceIds", "droppedFaceIds", "criticalFaceIds", "observability", "estimates", "uncertainty", "evidenceSeparation", "digestAlgorithm", "measurementDigest"], "measurement");
      if (value.schemaVersion !== SCHEMA_VERSION) throw new Error("measurement.schemaVersion mismatch.");
      if (value.sourceModel !== "bounded-virtual-q-star-hinge-height-v1") throw new Error("measurement.sourceModel mismatch.");
      assertIdentifier(value.measurementId, "measurement.measurementId");
      if (typeof value.sourcePlantId !== "string" || !/^plant-[0-9a-f]{24}$/.test(value.sourcePlantId)) throw new Error("measurement.sourcePlantId malformed.");
      assertInteger(value.sourceStateRevision, "measurement.sourceStateRevision", 0, LIMITS.maxTimeMs);
      assertDigest(value.sourceStateDigest, "measurement.sourceStateDigest");
      assertDigest(value.sourceSnapshotDigest, "measurement.sourceSnapshotDigest");
      assertSeed(value.seed, "measurement.seed");
      assertInteger(value.sampleIndex, "measurement.sampleIndex", 0, 1000000000);
      assertInteger(value.monotonicTimeMs, "measurement.monotonicTimeMs", 0, LIMITS.maxTimeMs);
      assertInteger(value.q, "measurement.q", LIMITS.qMin, LIMITS.qMax);
      assertClosedObject(value.calibration, ["id", "frozen", "calibratedAtMs", "validUntilMs", "heightScale", "heightOffsetMm", "hingeScale", "hingeOffsetDeg"], "measurement.calibration");
      assertIdentifier(value.calibration.id, "measurement.calibration.id");
      if (typeof value.calibration.frozen !== "boolean") throw new Error("measurement.calibration.frozen must be boolean.");
      assertInteger(value.calibration.calibratedAtMs, "measurement.calibration.calibratedAtMs", 0, LIMITS.maxTimeMs);
      assertInteger(value.calibration.validUntilMs, "measurement.calibration.validUntilMs", value.calibration.calibratedAtMs, LIMITS.maxTimeMs);
      assertFiniteRange(value.calibration.heightScale, "measurement.calibration.heightScale", 0.5, 2);
      assertFiniteRange(value.calibration.heightOffsetMm, "measurement.calibration.heightOffsetMm", -100, 100);
      assertFiniteRange(value.calibration.hingeScale, "measurement.calibration.hingeScale", 0.5, 2);
      assertFiniteRange(value.calibration.hingeOffsetDeg, "measurement.calibration.hingeOffsetDeg", -90, 90);
      assertClosedObject(value.noise, ["heightStdMm", "hingeStdDeg", "dropoutProbability"], "measurement.noise");
      assertFiniteRange(value.noise.heightStdMm, "measurement.noise.heightStdMm", 0, 100);
      assertFiniteRange(value.noise.hingeStdDeg, "measurement.noise.hingeStdDeg", 0, 90);
      assertFiniteRange(value.noise.dropoutProbability, "measurement.noise.dropoutProbability", 0, 1);
      var expectedFaces = [];
      for (var faceIndex = 0; faceIndex < value.q; faceIndex += 1) expectedFaces.push(faceId(faceIndex));
      ["observedFaceIds", "droppedFaceIds", "criticalFaceIds"].forEach(function (field) {
        assertDenseArray(value[field], "measurement." + field, value.q);
        var seen = Object.create(null);
        value[field].forEach(function (id) {
          if (typeof id !== "string" || expectedFaces.indexOf(id) < 0 || seen[id]) throw new Error("measurement." + field + " contains an invalid or duplicate face id.");
          seen[id] = true;
        });
        if (stableStringify(value[field]) !== stableStringify(value[field].slice().sort())) throw new Error("measurement." + field + " must be canonically sorted.");
      });
      var partition = value.observedFaceIds.concat(value.droppedFaceIds).sort();
      if (stableStringify(partition) !== stableStringify(expectedFaces)) throw new Error("measurement observed/dropout lists are not an exact face partition.");
      assertClosedObject(value.observability, ["status", "code", "observable", "coverageFraction", "missingCriticalFaceIds", "reasons"], "measurement.observability");
      assertDenseArray(value.observability.missingCriticalFaceIds, "measurement.observability.missingCriticalFaceIds", value.q);
      assertDenseArray(value.observability.reasons, "measurement.observability.reasons", 8);
      value.observability.reasons.forEach(function (reason) { if (["calibration-not-frozen", "calibration-stale", "marker-coverage-below-80-percent", "target-critical-face-missing"].indexOf(reason) < 0) throw new Error("measurement observability reason invalid."); });
      var derived = deriveObservability(value.q, value.monotonicTimeMs, value.calibration, value.observedFaceIds, value.criticalFaceIds);
      if (stableStringify(value.observability) !== stableStringify(derived)) throw new Error("measurement observability certificate was not derived from its primitive fields.");
      assertClosedObject(value.estimates, ["faceHeightsMm", "hingePositionsDeg", "centerHeightMm"], "measurement.estimates");
      assertDenseArray(value.estimates.faceHeightsMm, "measurement.estimates.faceHeightsMm", value.q);
      if (value.estimates.faceHeightsMm.length !== value.observedFaceIds.length) throw new Error("measurement face-height estimate count mismatch.");
      value.estimates.faceHeightsMm.forEach(function (entry, index) {
        assertClosedObject(entry, ["id", "heightMm"], "measurement.estimates.faceHeightsMm[" + index + "]");
        if (entry.id !== value.observedFaceIds[index]) throw new Error("measurement face-height estimate id mismatch.");
        assertFiniteRange(entry.heightMm, "measurement face height estimate", -1000000, 1000000);
      });
      assertDenseArray(value.estimates.hingePositionsDeg, "measurement.estimates.hingePositionsDeg", value.q);
      if (value.estimates.hingePositionsDeg.length !== value.q) throw new Error("measurement hinge estimate count mismatch.");
      value.estimates.hingePositionsDeg.forEach(function (entry, index) {
        assertClosedObject(entry, ["id", "observed", "positionDeg"], "measurement.estimates.hingePositionsDeg[" + index + "]");
        var expectedObserved = value.observedFaceIds.indexOf(faceId(index)) >= 0;
        if (entry.id !== channelId(index) || entry.observed !== expectedObserved || (expectedObserved ? !finite(entry.positionDeg) : entry.positionDeg !== null)) throw new Error("measurement hinge estimate is inconsistent with observed faces.");
        if (entry.positionDeg !== null) assertFiniteRange(entry.positionDeg, "measurement hinge estimate.positionDeg", -1000000, 1000000);
      });
      if (derived.observable) assertFiniteRange(value.estimates.centerHeightMm, "measurement centerHeightMm", -1000000, 1000000);
      else if (value.estimates.centerHeightMm !== null) throw new Error("measurement centerHeightMm must be null when unobservable.");
      assertClosedObject(value.uncertainty, ["heightStdMm", "hingeStdDeg", "modelAdequacyBound"], "measurement.uncertainty");
      if (value.uncertainty.heightStdMm !== value.noise.heightStdMm || value.uncertainty.hingeStdDeg !== value.noise.hingeStdDeg || value.uncertainty.modelAdequacyBound !== null) throw new Error("measurement uncertainty record mismatch.");
      assertClosedObject(value.evidenceSeparation, ["intrinsicReference", "extrinsicMeasurement"], "measurement.evidenceSeparation");
      assertClosedObject(value.evidenceSeparation.extrinsicMeasurement, ["status", "basis", "evidenceClass", "synthetic", "physicalMeasurement", "uniquenessClaim", "claimBoundary"], "measurement.evidenceSeparation.extrinsicMeasurement");
      if (stableStringify(value.evidenceSeparation.extrinsicMeasurement) !== stableStringify(SYNTHETIC_MEASUREMENT_EVIDENCE)) throw new Error("measurement extrinsic evidence boundary mismatch.");
      if (stableStringify(value.evidenceSeparation.intrinsicReference) !== stableStringify(createQStar(value.q).intrinsic)) throw new Error("measurement intrinsic reference does not match the exact q-star budget.");
      var expectedMeasurementId = "measurement-" + digestValue({ sourcePlantId: value.sourcePlantId, sourceStateRevision: value.sourceStateRevision, sourceStateDigest: value.sourceStateDigest, seed: value.seed, sampleIndex: value.sampleIndex, monotonicTimeMs: value.monotonicTimeMs }).slice(0, 24);
      if (value.measurementId !== expectedMeasurementId) throw new Error("measurement.measurementId mismatch.");
      if (value.digestAlgorithm !== "sha256-jcs-v1") throw new Error("measurement digest algorithm mismatch.");
      assertDigest(value.measurementDigest, "measurement.measurementDigest");
      var copy = clone(value); delete copy.measurementDigest;
      if (digestValue(copy) !== value.measurementDigest) throw new Error("measurement digest mismatch.");
    } catch (error) { errors.push(error.message); }
    return deepFreeze({ valid: errors.length === 0, errors: errors });
  }

  function planSectorAction(raw) {
    assertClosedObject(raw, ["schemaVersion", "currentQ", "targetQ", "measurement", "editCost"], "sector plan request");
    if (raw.schemaVersion !== SCHEMA_VERSION) throw new Error("sector plan request.schemaVersion must equal " + SCHEMA_VERSION + ".");
    var currentQ = assertInteger(raw.currentQ, "sector plan request.currentQ", LIMITS.qMin, LIMITS.qMax);
    var targetQ = assertInteger(raw.targetQ, "sector plan request.targetQ", LIMITS.qMin, LIMITS.qMax);
    var editCost = raw.editCost == null ? 0.05 : assertFiniteRange(raw.editCost, "sector plan request.editCost", 0, 10);
    var measurementReport = validateMeasurement(raw.measurement);
    var observable = measurementReport.valid && raw.measurement.observability.observable === true && raw.measurement.q === currentQ;
    var before = createQStar(currentQ);
    if (!observable) {
      return deepFreeze({
        schemaVersion: SCHEMA_VERSION,
        status: "INHIBITED",
        code: "SENSOR_UNOBSERVABLE",
        currentQ: currentQ,
        targetQ: targetQ,
        recommendedAction: "HOLD",
        requiresOperatorConfirmation: false,
        topologyChange: false,
        measurementAccepted: false,
        validationErrors: measurementReport.errors,
        beforeIntrinsicBudget: before.intrinsic,
        afterIntrinsicBudget: null,
        evidenceSeparation: { actionLogic: INTRINSIC_EVIDENCE, issuedInstructionIsNotAssemblySuccess: true }
      });
    }
    if (currentQ === targetQ) {
      return deepFreeze({
        schemaVersion: SCHEMA_VERSION,
        status: "TARGET_REACHED",
        code: "NO_EDIT_REQUIRED",
        currentQ: currentQ,
        targetQ: targetQ,
        recommendedAction: "NONE",
        requiresOperatorConfirmation: false,
        topologyChange: false,
        measurementAccepted: true,
        beforeIntrinsicBudget: before.intrinsic,
        afterIntrinsicBudget: before.intrinsic,
        evidenceSeparation: { actionLogic: INTRINSIC_EVIDENCE, issuedInstructionIsNotAssemblySuccess: true }
      });
    }
    var adding = targetQ > currentQ;
    var nextQ = currentQ + (adding ? 1 : -1);
    var after = createQStar(nextQ);
    var change = adding ? rational(-1, 3) : rational(1, 3);
    var improvement = Math.abs(targetQ - currentQ) - Math.abs(targetQ - nextQ);
    var predictedBenefit = improvement / 3 - editCost;
    if (predictedBenefit <= 0) {
      return deepFreeze({
        schemaVersion: SCHEMA_VERSION,
        status: "NO_IMPROVING_ACTION",
        code: "NONPOSITIVE_PREDICTED_BENEFIT",
        currentQ: currentQ,
        targetQ: targetQ,
        recommendedAction: "HOLD",
        predictedLossDecrease: predictedBenefit,
        editCost: editCost,
        requiresOperatorConfirmation: false,
        controllerAssumesActionCompleted: false,
        topologyChange: false,
        measurementAccepted: true,
        beforeIntrinsicBudget: before.intrinsic,
        afterIntrinsicBudget: null,
        evidenceSeparation: { actionLogic: INTRINSIC_EVIDENCE, issuedInstructionIsNotAssemblySuccess: true, extrinsicOutcomeNotPredicted: true }
      });
    }
    return deepFreeze({
      schemaVersion: SCHEMA_VERSION,
      status: "ACTION_PROPOSED",
      code: adding ? "ADD_SECTOR" : "REMOVE_SECTOR",
      currentQ: currentQ,
      nextQ: nextQ,
      targetQ: targetQ,
      recommendedAction: adding ? "ADD_SECTOR" : "REMOVE_SECTOR",
      instruction: adding ? "Add one labeled equilateral sector at the open seam, close the seam, then confirm and remeasure." : "Open the labeled seam, remove one sector, close the seam, then confirm and remeasure.",
      affectedRadiusOne: { centerVertex: 0, seamFaces: adding ? [faceId(currentQ - 1), faceId(currentQ)] : [faceId(nextQ - 1), faceId(currentQ - 1)] },
      predictedCenterDefectChangePiCoefficient: change,
      predictedLossDecrease: predictedBenefit,
      editCost: editCost,
      requiresOperatorConfirmation: true,
      controllerAssumesActionCompleted: false,
      topologyChange: false,
      measurementAccepted: true,
      beforeIntrinsicBudget: before.intrinsic,
      afterIntrinsicBudget: after.intrinsic,
      evidenceSeparation: { actionLogic: INTRINSIC_EVIDENCE, issuedInstructionIsNotAssemblySuccess: true, extrinsicOutcomeNotPredicted: true }
    });
  }

  function utf8ByteLength(text) {
    if (typeof text !== "string") throw new Error("UTF-8 input must be a string.");
    assertWellFormedString(text, "UTF-8 input", LIMITS.maxCanonicalBytes);
    var length = 0;
    for (var i = 0; i < text.length; i += 1) {
      var code = text.charCodeAt(i);
      if (code < 0x80) length += 1;
      else if (code < 0x800) length += 2;
      else if (code >= 0xd800 && code <= 0xdbff) { length += 4; i += 1; }
      else length += 3;
    }
    return length;
  }

  function utf8Bytes(text) {
    if (typeof text !== "string") throw new Error("UTF-8 input must be a string.");
    assertWellFormedString(text, "UTF-8 input", LIMITS.maxCanonicalBytes);
    var bytes = [];
    for (var i = 0; i < text.length; i += 1) {
      var code = text.charCodeAt(i);
      if (code < 0x80) bytes.push(code);
      else if (code < 0x800) bytes.push(0xc0 | (code >> 6), 0x80 | (code & 0x3f));
      else if (code >= 0xd800 && code <= 0xdbff) {
        var low = text.charCodeAt(++i);
        var point = 0x10000 + ((code - 0xd800) << 10) + (low - 0xdc00);
        bytes.push(0xf0 | (point >> 18), 0x80 | ((point >> 12) & 0x3f), 0x80 | ((point >> 6) & 0x3f), 0x80 | (point & 0x3f));
      } else bytes.push(0xe0 | (code >> 12), 0x80 | ((code >> 6) & 0x3f), 0x80 | (code & 0x3f));
    }
    return bytes;
  }

  var CRC_TABLE = (function () {
    var table = [];
    for (var n = 0; n < 256; n += 1) {
      var value = n;
      for (var k = 0; k < 8; k += 1) value = (value & 1) ? (0xedb88320 ^ (value >>> 1)) : (value >>> 1);
      table[n] = value >>> 0;
    }
    return table;
  })();

  function crc32(text) {
    var crc = 0xffffffff;
    utf8Bytes(text).forEach(function (byte) { crc = CRC_TABLE[(crc ^ byte) & 0xff] ^ (crc >>> 8); });
    return ("00000000" + ((crc ^ 0xffffffff) >>> 0).toString(16)).slice(-8);
  }

  function unsignedMessage(message) {
    assertClosedObject(message, ["protocol", "type", "seq", "monotonicTimeMs", "deadlineMs", "armEpoch", "payload", "checksum"], "protocol frame");
    ["protocol", "type", "seq", "monotonicTimeMs", "deadlineMs", "armEpoch", "payload"].forEach(function (key) { if (!own(message, key)) throw new Error("protocol frame is missing own field " + key + "."); });
    return { protocol: message.protocol, type: message.type, seq: message.seq, monotonicTimeMs: message.monotonicTimeMs, deadlineMs: message.deadlineMs, armEpoch: message.armEpoch, payload: message.payload };
  }

  function checksumMessage(message) {
    var canonical = stableStringify(unsignedMessage(message));
    if (utf8Bytes(canonical).length > LIMITS.maxFrameBytes) throw new Error("Protocol frame exceeds the encoded frame bound.");
    return crc32(canonical);
  }

  function assertBoundedText(value, path, maximum, nullable) {
    if (nullable && value === null) return value;
    if (typeof value !== "string" || value.length > maximum) throw new Error(path + " must be a bounded string.");
    assertWellFormedString(value, path, maximum);
    return value;
  }

  function assertState(value, path) {
    if (STATES.indexOf(value) < 0) throw new Error(path + " is not a declared state.");
    return value;
  }

  function assertArmEpoch(value, path, nullable) {
    if (nullable && value === null) return value;
    if (typeof value !== "string" || !/^arm-[0-9a-f]{24}$/.test(value)) throw new Error(path + " must be a bounded arm epoch.");
    return value;
  }

  function validateCommandChannels(channels, path) {
    assertDenseArray(channels, path, LIMITS.maxChannels);
    if (!channels.length) throw new Error(path + " must be non-empty.");
    var seen = Object.create(null);
    channels.forEach(function (channel, index) {
      assertClosedObject(channel, ["id", "positionDeg", "maxRateDegPerSec"], path + "[" + index + "]");
      assertIdentifier(channel.id, path + "[" + index + "].id");
      if (seen[channel.id]) throw new Error(path + " contains duplicate channel " + channel.id + ".");
      seen[channel.id] = true;
      if (!finite(channel.positionDeg)) throw new Error(path + " positionDeg must be finite.");
      if (!finite(channel.maxRateDegPerSec) || channel.maxRateDegPerSec <= 0) throw new Error(path + " maxRateDegPerSec must be positive and finite.");
    });
  }

  function validateRequestPayload(type, payload) {
    var allowed = {
      HELLO: ["clientId"], CAPABILITIES: ["request"], ARM: ["sessionId"],
      COMMAND: ["plantId", "expectedStateRevision", "expectedStateDigest", "observationDigest", "channels"],
      TELEMETRY: ["request"], HOLD: ["reason"], DISARM: ["reason"], ESTOP: ["reason"], FAULT: ["code", "detail"]
    }[type] || [];
    assertClosedObject(payload, allowed, "request payload");
    if (type === "HELLO") assertIdentifier(payload.clientId, "HELLO clientId");
    else if (type === "CAPABILITIES" || type === "TELEMETRY") {
      if (typeof payload.request !== "boolean" && typeof payload.request !== "string") throw new Error(type + " request must be boolean or a bounded name.");
      if (typeof payload.request === "string") assertIdentifier(payload.request, type + " request");
    } else if (type === "ARM") assertIdentifier(payload.sessionId, "ARM sessionId");
    else if (type === "COMMAND") {
      if (typeof payload.plantId !== "string" || !/^plant-[0-9a-f]{24}$/.test(payload.plantId)) throw new Error("COMMAND plantId malformed.");
      assertInteger(payload.expectedStateRevision, "COMMAND expectedStateRevision", 0, LIMITS.maxTimeMs);
      assertDigest(payload.expectedStateDigest, "COMMAND expectedStateDigest");
      assertDigest(payload.observationDigest, "COMMAND observationDigest");
      validateCommandChannels(payload.channels, "COMMAND channels");
    } else if (type === "HOLD" || type === "DISARM" || type === "ESTOP") {
      if (own(payload, "reason")) assertBoundedText(payload.reason, type + " reason", 512, false);
    } else if (type === "FAULT") {
      if (own(payload, "code")) assertIdentifier(payload.code, "FAULT code");
      if (own(payload, "detail")) assertBoundedText(payload.detail, "FAULT detail", 1024, false);
    }
  }

  function validateFaultRecord(value, path) {
    if (value === null) return;
    assertClosedObject(value, ["code", "detail", "atMs"], path);
    assertIdentifier(value.code, path + ".code");
    assertBoundedText(value.detail, path + ".detail", 4096, false);
    assertInteger(value.atMs, path + ".atMs", 0, LIMITS.maxTimeMs);
  }

  function validateResponsePayload(type, payload) {
    var allowed = {
      HELLO: ["deviceId", "role", "state"], CAPABILITIES: ["channels", "limits", "virtualOnly", "hardwareAccess", "transport", "evidence", "safetyMode"],
      ARM: ["sessionId", "state"], COMMAND: ["acceptedCount", "state", "preStateRevision", "postStateRevision", "postStateDigest"],
      TELEMETRY: ["state", "plant", "observation", "activeFault"], HOLD: ["reason", "state"], DISARM: ["reason", "state"], ESTOP: ["reason", "state"],
      FAULT: ["code", "detail", "state", "rejectedType", "rejectedSeq"]
    }[type] || [];
    assertClosedObject(payload, allowed, "response payload");
    if (type === "HELLO") {
      assertIdentifier(payload.deviceId, "HELLO response deviceId"); assertIdentifier(payload.role, "HELLO response role"); assertState(payload.state, "HELLO response state");
    } else if (type === "CAPABILITIES") {
      assertDenseArray(payload.channels, "CAPABILITIES response channels", LIMITS.maxChannels);
      if (payload.channels.length < LIMITS.qMin) throw new Error("CAPABILITIES response channel count invalid.");
      payload.channels.forEach(function (id, index) { if (id !== channelId(index)) throw new Error("CAPABILITIES response channels are not canonical."); });
      assertClosedObject(payload.limits, ["maxPositionDeg", "maxRateDegPerSec", "watchdogTimeoutMs"], "CAPABILITIES limits");
      assertFiniteRange(payload.limits.maxPositionDeg, "CAPABILITIES maxPositionDeg", 1, 90); assertFiniteRange(payload.limits.maxRateDegPerSec, "CAPABILITIES maxRateDegPerSec", 0.1, 360);
      assertInteger(payload.limits.watchdogTimeoutMs, "CAPABILITIES watchdogTimeoutMs", 10, 60000);
      if (payload.virtualOnly !== true || payload.hardwareAccess !== false || payload.transport !== "in-memory-only" || payload.safetyMode !== "OBSERVATION_BOUND") throw new Error("CAPABILITIES safety boundary mismatch.");
      if (stableStringify(payload.evidence) !== stableStringify(EXTRINSIC_EVIDENCE)) throw new Error("CAPABILITIES evidence mismatch.");
    } else if (type === "ARM") {
      assertIdentifier(payload.sessionId, "ARM response sessionId"); if (payload.state !== "ARMED") throw new Error("ARM response state mismatch.");
    } else if (type === "COMMAND") {
      assertInteger(payload.acceptedCount, "COMMAND response acceptedCount", 1, LIMITS.maxChannels); if (payload.state !== "ARMED") throw new Error("COMMAND response state mismatch.");
      assertInteger(payload.preStateRevision, "COMMAND response preStateRevision", 0, LIMITS.maxTimeMs); assertInteger(payload.postStateRevision, "COMMAND response postStateRevision", payload.preStateRevision + 1, LIMITS.maxTimeMs); assertDigest(payload.postStateDigest, "COMMAND response postStateDigest");
    } else if (type === "TELEMETRY") {
      assertState(payload.state, "TELEMETRY response state"); var plantReport = validatePlantSnapshot(payload.plant); if (!plantReport.valid) throw new Error("TELEMETRY plant invalid: " + plantReport.errors.join("; "));
      if (payload.observation !== null) {
        assertClosedObject(payload.observation, ["measurementDigest", "observable", "monotonicTimeMs", "consumedByCommand", "sourceStateRevision", "sourceStateDigest"], "TELEMETRY observation");
        assertDigest(payload.observation.measurementDigest, "TELEMETRY observation.measurementDigest"); if (typeof payload.observation.observable !== "boolean" || typeof payload.observation.consumedByCommand !== "boolean") throw new Error("TELEMETRY observation flags invalid.");
        assertInteger(payload.observation.monotonicTimeMs, "TELEMETRY observation.monotonicTimeMs", 0, LIMITS.maxTimeMs); assertInteger(payload.observation.sourceStateRevision, "TELEMETRY observation.sourceStateRevision", 0, LIMITS.maxTimeMs); assertDigest(payload.observation.sourceStateDigest, "TELEMETRY observation.sourceStateDigest");
      }
      validateFaultRecord(payload.activeFault, "TELEMETRY activeFault");
    } else if (type === "HOLD" || type === "DISARM" || type === "ESTOP") {
      assertBoundedText(payload.reason, type + " response reason", 512, false); assertState(payload.state, type + " response state");
      if ((type === "HOLD" && payload.state !== "HOLD") || (type === "DISARM" && payload.state !== "DISARMED") || (type === "ESTOP" && payload.state !== "ESTOP")) throw new Error(type + " response state mismatch.");
    } else if (type === "FAULT") {
      assertIdentifier(payload.code, "FAULT response code"); assertBoundedText(payload.detail, "FAULT response detail", 1024, false); assertState(payload.state, "FAULT response state");
      if (payload.rejectedType !== null && MESSAGE_TYPES.indexOf(payload.rejectedType) < 0) throw new Error("FAULT response rejectedType invalid.");
      if (payload.rejectedSeq !== null) assertInteger(payload.rejectedSeq, "FAULT response rejectedSeq", 0, LIMITS.maxSeq);
    }
  }

  function inspectProtocolMessage(message, direction) {
    var errors = [], normalized = null, code = "SCHEMA_INVALID";
    try {
      direction = direction || "host-to-emulator";
      if (direction !== "host-to-emulator" && direction !== "emulator-to-host") throw new Error("Unknown protocol direction.");
      assertClosedObject(message, ["protocol", "type", "seq", "monotonicTimeMs", "deadlineMs", "armEpoch", "payload", "checksum"], "protocol frame");
      ["protocol", "type", "seq", "monotonicTimeMs", "deadlineMs", "armEpoch", "payload", "checksum"].forEach(function (key) { if (!own(message, key)) throw new Error("protocol frame missing own field " + key + "."); });
      normalized = clone(message);
      if (normalized.protocol !== PROTOCOL) throw new Error("protocol mismatch.");
      if (MESSAGE_TYPES.indexOf(normalized.type) < 0) throw new Error("unknown message type.");
      assertInteger(normalized.seq, "protocol seq", 0, LIMITS.maxSeq);
      assertInteger(normalized.monotonicTimeMs, "protocol monotonicTimeMs", 0, LIMITS.maxTimeMs);
      assertInteger(normalized.deadlineMs, "protocol deadlineMs", normalized.monotonicTimeMs, LIMITS.maxTimeMs);
      assertArmEpoch(normalized.armEpoch, "protocol armEpoch", true);
      if (direction === "host-to-emulator") validateRequestPayload(normalized.type, normalized.payload); else validateResponsePayload(normalized.type, normalized.payload);
      if (direction === "host-to-emulator" && normalized.type === "COMMAND" && normalized.armEpoch === null) throw new Error("COMMAND requires an armEpoch.");
      if (direction === "host-to-emulator" && normalized.type === "ARM" && normalized.armEpoch !== null) throw new Error("ARM request must not supply an armEpoch.");
      if (direction === "emulator-to-host" && (normalized.type === "ARM" || normalized.type === "COMMAND") && normalized.armEpoch === null) throw new Error(normalized.type + " response requires an armEpoch.");
      if (typeof normalized.checksum !== "string" || !/^[0-9a-f]{8}$/.test(normalized.checksum)) throw new Error("checksum malformed.");
      if (checksumMessage(normalized) !== normalized.checksum) { code = "CORRUPT_CHECKSUM"; throw new Error("checksum mismatch."); }
      return deepFreeze({ valid: true, code: "MESSAGE_VALID", errors: [], normalized: normalized, direction: direction });
    } catch (error) { errors.push(error.message); }
    return deepFreeze({ valid: false, code: code, errors: errors, normalized: null, direction: direction || "host-to-emulator" });
  }

  function validateProtocolMessage(message, direction) { return inspectProtocolMessage(message, direction || "host-to-emulator"); }
  function validateProtocolResponse(message) { return inspectProtocolMessage(message, "emulator-to-host"); }

  function sealMessage(type, seq, timeMs, deadlineMs, payload, armEpoch, direction) {
    var output = { protocol: PROTOCOL, type: type, seq: seq, monotonicTimeMs: timeMs, deadlineMs: deadlineMs, armEpoch: armEpoch == null ? null : armEpoch, payload: clone(payload) };
    output.checksum = checksumMessage(output);
    var validation = inspectProtocolMessage(output, direction);
    if (!validation.valid) throw new Error("Invalid " + direction + " protocol frame: " + validation.errors.join("; "));
    return deepFreeze(validation.normalized);
  }

  function createProtocolMessage(raw) {
    assertClosedObject(raw, ["type", "seq", "monotonicTimeMs", "deadlineMs", "armEpoch", "payload"], "protocol message request");
    var message = sealMessage(raw.type, raw.seq, raw.monotonicTimeMs, raw.deadlineMs, fieldOr(raw, "payload", {}), fieldOr(raw, "armEpoch", null), "host-to-emulator");
    return message;
  }

  function corruptProtocolChecksum(message) {
    var output = clone(message);
    output.checksum = message.checksum === "00000000" ? "ffffffff" : "00000000";
    return deepFreeze(output);
  }

  function normalizeEmulatorConfig(raw) {
    raw = raw || {};
    assertClosedObject(raw, ["schemaVersion", "seed", "plant", "watchdogTimeoutMs", "observationTimeoutMs", "requireObservation", "safetyMode"], "emulator config");
    if (raw.schemaVersion != null && raw.schemaVersion !== SCHEMA_VERSION) throw new Error("emulator config.schemaVersion must equal " + SCHEMA_VERSION + ".");
    var config = {
      schemaVersion: SCHEMA_VERSION,
      seed: assertSeed(fieldOr(raw, "seed", "ggii-hil-default"), "emulator config.seed"),
      plant: normalizePlantConfig(fieldOr(raw, "plant", {})),
      watchdogTimeoutMs: assertInteger(fieldOr(raw, "watchdogTimeoutMs", 500), "emulator config.watchdogTimeoutMs", 10, 60000),
      observationTimeoutMs: assertInteger(fieldOr(raw, "observationTimeoutMs", 1000), "emulator config.observationTimeoutMs", 10, 60000),
      requireObservation: fieldOr(raw, "requireObservation", true),
      safetyMode: "OBSERVATION_BOUND"
    };
    if (config.requireObservation !== true) throw new Error("emulator config.requireObservation is fixed to true in protocol v2.");
    if (own(raw, "safetyMode") && raw.safetyMode !== "OBSERVATION_BOUND") throw new Error("emulator config.safetyMode mismatch.");
    return deepFreeze(config);
  }

  function createHilEmulator(rawConfig) {
    var config = normalizeEmulatorConfig(rawConfig);
    var plant = createVirtualPlant(config.plant);
    var configDigest = digestValue(config), initialState = null;
    var machine = {
      state: "DISARMED",
      estopLatched: false,
      nowMs: 0,
      lastSeenSeq: -1,
      lastHeartbeatMs: null,
      observation: null,
      observationConsumed: false,
      activeFault: null,
      events: [],
      armCounter: 0,
      armEpoch: null,
      sessionId: null
    };

    function safeMessageSummary(message) {
      var type = safeOwnValue(message, "type"), seq = safeOwnValue(message, "seq"), monotonicTimeMs = safeOwnValue(message, "monotonicTimeMs"), deadlineMs = safeOwnValue(message, "deadlineMs"), checksum = safeOwnValue(message, "checksum");
      return {
        type: typeof type === "string" && MESSAGE_TYPES.indexOf(type) >= 0 ? type : null,
        seq: Number.isInteger(seq) && seq >= 0 && seq <= LIMITS.maxSeq ? seq : null,
        monotonicTimeMs: Number.isInteger(monotonicTimeMs) && monotonicTimeMs >= 0 && monotonicTimeMs <= LIMITS.maxTimeMs ? monotonicTimeMs : null,
        deadlineMs: Number.isInteger(deadlineMs) && deadlineMs >= 0 && deadlineMs <= LIMITS.maxTimeMs ? deadlineMs : null,
        checksum: typeof checksum === "string" ? checksum.slice(0, 16) : null
      };
    }

    function observationSummary() {
      return machine.observation ? {
        measurementDigest: machine.observation.measurementDigest,
        observable: machine.observation.observability.observable,
        monotonicTimeMs: machine.observation.monotonicTimeMs,
        consumedByCommand: machine.observationConsumed,
        sourceStateRevision: machine.observation.sourceStateRevision,
        sourceStateDigest: machine.observation.sourceStateDigest
      } : null;
    }

    function appendEvent(core, preState, postState) {
      if (machine.events.length >= LIMITS.maxTranscriptEvents) throw new Error("HIL transcript event bound exceeded.");
      var event = {
        index: machine.events.length,
        kind: core.kind,
        direction: fieldOr(core, "direction", null),
        atMs: core.atMs,
        accepted: core.accepted,
        code: core.code,
        normalizedInput: fieldOr(core, "normalizedInput", null),
        response: fieldOr(core, "response", null),
        preState: preState,
        postState: postState,
        previousEventDigest: machine.events.length ? machine.events[machine.events.length - 1].eventDigest : null,
        digestAlgorithm: "sha256-jcs-v1"
      };
      event.eventDigest = digestValue(event);
      machine.events.push(deepFreeze(clone(event)));
    }

    function holdPlant(atMs, code, detail) {
      plant.hold(atMs);
      if (machine.state === "ARMED") machine.state = "HOLD";
      machine.activeFault = { code: code, detail: String(detail || "").slice(0, 4096), atMs: atMs };
    }

    function advanceTo(timeMs) {
      assertInteger(timeMs, "emulator time", 0, LIMITS.maxTimeMs);
      if (timeMs < machine.nowMs) throw new Error("Emulator time cannot move backward.");
      if (machine.state === "ARMED" && machine.lastHeartbeatMs != null && timeMs >= machine.lastHeartbeatMs + config.watchdogTimeoutMs) {
        var timeoutAt = machine.lastHeartbeatMs + config.watchdogTimeoutMs;
        var preTimeout = snapshot();
        plant.stepTo(timeoutAt);
        machine.nowMs = timeoutAt;
        holdPlant(timeoutAt, "WATCHDOG_TIMEOUT", "No accepted command arrived before the watchdog deadline.");
        appendEvent({ kind: "SAFETY", direction: null, atMs: timeoutAt, accepted: false, code: "WATCHDOG_TIMEOUT", normalizedInput: { deadlineMs: timeoutAt }, response: null }, preTimeout, snapshot());
      }
      plant.stepTo(timeMs);
      machine.nowMs = timeMs;
    }

    function response(type, seq, payload, epoch) {
      return sealMessage(type, Math.max(0, Number.isInteger(seq) ? seq : 0), machine.nowMs, Math.min(LIMITS.maxTimeMs, machine.nowMs + config.watchdogTimeoutMs), payload, epoch === undefined ? machine.armEpoch : epoch, "emulator-to-host");
    }

    function faultResponse(code, request, detail) {
      var summary = safeMessageSummary(request);
      return response("FAULT", summary.seq, { code: code, detail: String(detail || "").slice(0, 1024), state: machine.state, rejectedType: summary.type, rejectedSeq: summary.seq });
    }

    function observationUsable() {
      if (!machine.observation) return { usable: false, code: "SENSOR_UNOBSERVABLE" };
      var validation = validateMeasurement(machine.observation);
      if (!validation.valid || machine.observation.observability.observable !== true) return { usable: false, code: "SENSOR_UNOBSERVABLE" };
      if (machine.observation.q !== config.plant.q) return { usable: false, code: "OBSERVATION_MODEL_MISMATCH" };
      if (machine.observationConsumed) return { usable: false, code: "REMEASUREMENT_REQUIRED" };
      if (machine.nowMs - machine.observation.monotonicTimeMs > config.observationTimeoutMs) return { usable: false, code: "OBSERVATION_STALE" };
      var current = plant.snapshot();
      if (machine.observation.sourcePlantId !== current.plantId || machine.observation.sourceStateRevision !== current.stateRevision || machine.observation.sourceStateDigest !== current.stateDigest) return { usable: false, code: "OBSERVATION_STATE_MISMATCH", plant: current };
      return { usable: true, code: "OBSERVABLE", plant: current };
    }

    function receive(rawMessage) {
      var preState = snapshot();
      var validation = inspectProtocolMessage(rawMessage, "host-to-emulator");
      if (!validation.valid) {
        if (machine.state === "ARMED") holdPlant(machine.nowMs, validation.code, validation.errors.join("; "));
        var invalidResponse = faultResponse(validation.code, rawMessage, validation.errors.join("; "));
        appendEvent({ kind: "MESSAGE", direction: "host-to-emulator", atMs: machine.nowMs, accepted: false, code: validation.code, normalizedInput: { invalidFrame: safeMessageSummary(rawMessage) }, response: invalidResponse }, preState, snapshot());
        return invalidResponse;
      }
      var message = validation.normalized;

      if (message.type === "ESTOP") {
        plant.hold(machine.nowMs);
        machine.estopLatched = true;
        machine.state = "ESTOP";
        machine.activeFault = { code: "ESTOP_LATCHED", detail: message.payload.reason || "Emergency stop requested.", atMs: machine.nowMs };
        if (message.seq > machine.lastSeenSeq) machine.lastSeenSeq = message.seq;
        var estopResponse = response("ESTOP", message.seq, { reason: message.payload.reason || "Emergency stop requested.", state: machine.state });
        appendEvent({ kind: "MESSAGE", direction: "host-to-emulator", atMs: machine.nowMs, accepted: true, code: "ESTOP_LATCHED", normalizedInput: message, response: estopResponse }, preState, snapshot());
        return estopResponse;
      }

      if (message.seq <= machine.lastSeenSeq) {
        if (machine.state === "ARMED") holdPlant(machine.nowMs, "STALE_SEQUENCE", "Sequence did not increase strictly.");
        var staleResponse = faultResponse("STALE_SEQUENCE", message, "Sequence did not increase strictly.");
        appendEvent({ kind: "MESSAGE", direction: "host-to-emulator", atMs: machine.nowMs, accepted: false, code: "STALE_SEQUENCE", normalizedInput: message, response: staleResponse }, preState, snapshot());
        return staleResponse;
      }
      machine.lastSeenSeq = message.seq;
      advanceTo(Math.max(machine.nowMs, message.monotonicTimeMs));
      if (machine.nowMs > message.deadlineMs) {
        if (machine.state === "ARMED") holdPlant(machine.nowMs, "MESSAGE_DEADLINE_EXPIRED", "Message arrived after its deadline.");
        var deadlineResponse = faultResponse("MESSAGE_DEADLINE_EXPIRED", message, "Message arrived after its deadline.");
        appendEvent({ kind: "MESSAGE", direction: "host-to-emulator", atMs: machine.nowMs, accepted: false, code: "MESSAGE_DEADLINE_EXPIRED", normalizedInput: message, response: deadlineResponse }, preState, snapshot());
        return deadlineResponse;
      }

      var accepted = true, code = "ACCEPTED", outbound;
      if (message.type === "HELLO") {
        outbound = response("HELLO", message.seq, { deviceId: "ggii-virtual-sheet", role: "in-memory-emulator", state: machine.state });
      } else if (message.type === "CAPABILITIES") {
        outbound = response("CAPABILITIES", message.seq, { channels: plant.snapshot().channels.map(function (channel) { return channel.id; }), limits: { maxPositionDeg: config.plant.maxPositionDeg, maxRateDegPerSec: config.plant.maxRateDegPerSec, watchdogTimeoutMs: config.watchdogTimeoutMs }, virtualOnly: true, hardwareAccess: false, transport: "in-memory-only", evidence: EXTRINSIC_EVIDENCE, safetyMode: config.safetyMode });
      } else if (message.type === "TELEMETRY") {
        outbound = response("TELEMETRY", message.seq, { state: machine.state, plant: plant.snapshot(), observation: observationSummary(), activeFault: machine.activeFault });
      } else if (machine.estopLatched) {
        accepted = false; code = "ESTOP_LATCHED";
        outbound = faultResponse(code, message, "This emulator instance cannot clear its emergency-stop latch.");
      } else if (message.type === "ARM") {
        if (machine.state !== "DISARMED") {
          accepted = false; code = "DISARM_REQUIRED";
          outbound = faultResponse(code, message, "ARM is accepted only from DISARMED.");
        } else if (machine.nowMs > LIMITS.maxTimeMs - config.watchdogTimeoutMs) {
          accepted = false; code = "TIME_HORIZON_LIMIT";
          outbound = faultResponse(code, message, "Insufficient bounded time remains for a watchdog interval.");
        } else {
          machine.state = "ARMED";
          machine.activeFault = null;
          machine.lastHeartbeatMs = machine.nowMs;
          machine.armCounter += 1;
          machine.sessionId = message.payload.sessionId;
          machine.armEpoch = "arm-" + digestValue({ seed: config.seed, armCounter: machine.armCounter, sessionId: machine.sessionId, atMs: machine.nowMs, lastSeenSeq: machine.lastSeenSeq, plantStateDigest: plant.snapshot().stateDigest }).slice(0, 24);
          outbound = response("ARM", message.seq, { sessionId: machine.sessionId, state: machine.state });
        }
      } else if (message.type === "COMMAND") {
        if (machine.state !== "ARMED") {
          accepted = false; code = "COMMAND_WHILE_" + machine.state;
          outbound = faultResponse(code, message, "Motion commands require ARMED state.");
        } else if (machine.nowMs > LIMITS.maxTimeMs - config.watchdogTimeoutMs) {
          accepted = false; code = "TIME_HORIZON_LIMIT";
          holdPlant(machine.nowMs, code, "Insufficient bounded time remains for a watchdog interval.");
          outbound = faultResponse(code, message, "Insufficient bounded time remains for a watchdog interval.");
        } else {
          var usable = observationUsable();
          var currentPlant = usable.plant || plant.snapshot();
          if (message.armEpoch !== machine.armEpoch) { usable = { usable: false, code: "ARM_EPOCH_MISMATCH", plant: currentPlant }; }
          else if (message.payload.plantId !== currentPlant.plantId || message.payload.expectedStateRevision !== currentPlant.stateRevision || message.payload.expectedStateDigest !== currentPlant.stateDigest) { usable = { usable: false, code: "COMMAND_STATE_MISMATCH", plant: currentPlant }; }
          else if (!machine.observation || message.payload.observationDigest !== machine.observation.measurementDigest) { usable = { usable: false, code: "OBSERVATION_BINDING_MISMATCH", plant: currentPlant }; }
          if (!usable.usable) {
            accepted = false; code = usable.code;
            holdPlant(machine.nowMs, code, "A fresh valid observation is required before each bounded command.");
            outbound = faultResponse(code, message, "A fresh valid observation is required before each bounded command.");
          } else {
            var targetResult;
            try { targetResult = plant.setTargets(message.payload.channels, machine.nowMs); }
            catch (error) { targetResult = { accepted: false, code: "COMMAND_SCHEMA_INVALID", violations: [{ detail: error.message }] }; }
            if (!targetResult.accepted) {
              accepted = false; code = targetResult.code;
              holdPlant(machine.nowMs, code, stableStringify(targetResult.violations || []));
              outbound = faultResponse(code, message, "Command exceeded a declared virtual-plant bound or schema.");
            } else {
              machine.lastHeartbeatMs = machine.nowMs;
              machine.observationConsumed = true;
              var postPlant = plant.snapshot();
              outbound = response("COMMAND", message.seq, { acceptedCount: targetResult.channels.length, state: machine.state, preStateRevision: currentPlant.stateRevision, postStateRevision: postPlant.stateRevision, postStateDigest: postPlant.stateDigest });
            }
          }
        }
      } else if (message.type === "HOLD") {
        plant.hold(machine.nowMs);
        machine.state = "HOLD";
        machine.activeFault = { code: "HOST_HOLD", detail: message.payload.reason || "Host hold.", atMs: machine.nowMs };
        code = "HOST_HOLD";
        outbound = response("HOLD", message.seq, { reason: message.payload.reason || "Host hold.", state: machine.state });
      } else if (message.type === "DISARM") {
        plant.hold(machine.nowMs);
        machine.state = "DISARMED";
        machine.activeFault = null;
        machine.lastHeartbeatMs = null;
        machine.armEpoch = null;
        machine.sessionId = null;
        machine.observation = null;
        machine.observationConsumed = false;
        outbound = response("DISARM", message.seq, { reason: message.payload.reason || "Host disarm.", state: machine.state });
      } else if (message.type === "FAULT") {
        plant.hold(machine.nowMs);
        machine.state = "FAULT";
        machine.activeFault = { code: message.payload.code || "REMOTE_FAULT", detail: message.payload.detail || "", atMs: machine.nowMs };
        machine.armEpoch = null;
        machine.sessionId = null;
        code = machine.activeFault.code;
        outbound = response("FAULT", message.seq, { code: code, detail: machine.activeFault.detail, state: machine.state, rejectedType: null, rejectedSeq: null });
      }
      appendEvent({ kind: "MESSAGE", direction: "host-to-emulator", atMs: machine.nowMs, accepted: accepted, code: code, normalizedInput: message, response: outbound }, preState, snapshot());
      return outbound;
    }

    function setObservation(measurement) {
      var preState = snapshot();
      var report = validateMeasurement(measurement);
      if (!report.valid) {
        machine.observation = null;
        machine.observationConsumed = false;
        if (machine.state === "ARMED") holdPlant(machine.nowMs, "SENSOR_UNOBSERVABLE", report.errors.join("; "));
        var invalidMeasurementDigest = safeOwnValue(measurement, "measurementDigest");
        appendEvent({ kind: "OBSERVATION", direction: "sensor-to-emulator", atMs: machine.nowMs, accepted: false, code: "SENSOR_UNOBSERVABLE", normalizedInput: { invalidMeasurementDigest: typeof invalidMeasurementDigest === "string" ? invalidMeasurementDigest.slice(0, 64) : null }, response: null }, preState, snapshot());
        return deepFreeze({ accepted: false, code: "SENSOR_UNOBSERVABLE", errors: report.errors });
      }
      if (measurement.monotonicTimeMs !== machine.nowMs) {
        if (machine.state === "ARMED") holdPlant(machine.nowMs, "OBSERVATION_STALE", "Observation time precedes emulator time.");
        appendEvent({ kind: "OBSERVATION", direction: "sensor-to-emulator", atMs: machine.nowMs, accepted: false, code: "OBSERVATION_STALE", normalizedInput: measurement, response: null }, preState, snapshot());
        return deepFreeze({ accepted: false, code: "OBSERVATION_STALE", errors: [] });
      }
      var currentPlant = plant.snapshot();
      if (measurement.q !== config.plant.q || measurement.sourcePlantId !== currentPlant.plantId) {
        machine.observation = null;
        machine.observationConsumed = false;
        if (machine.state === "ARMED") holdPlant(machine.nowMs, "OBSERVATION_MODEL_MISMATCH", "Observation q does not match the virtual plant q.");
        appendEvent({ kind: "OBSERVATION", direction: "sensor-to-emulator", atMs: machine.nowMs, accepted: false, code: "OBSERVATION_MODEL_MISMATCH", normalizedInput: measurement, response: null }, preState, snapshot());
        return deepFreeze({ accepted: false, code: "OBSERVATION_MODEL_MISMATCH", errors: [] });
      }
      if (measurement.sourceStateRevision !== currentPlant.stateRevision || measurement.sourceStateDigest !== currentPlant.stateDigest || measurement.sourceSnapshotDigest !== currentPlant.snapshotDigest) {
        machine.observation = null;
        machine.observationConsumed = false;
        if (machine.state === "ARMED") holdPlant(machine.nowMs, "OBSERVATION_STATE_MISMATCH", "Observation is not bound to the current virtual plant state.");
        appendEvent({ kind: "OBSERVATION", direction: "sensor-to-emulator", atMs: machine.nowMs, accepted: false, code: "OBSERVATION_STATE_MISMATCH", normalizedInput: measurement, response: null }, preState, snapshot());
        return deepFreeze({ accepted: false, code: "OBSERVATION_STATE_MISMATCH", errors: [] });
      }
      machine.observation = clone(measurement);
      machine.observationConsumed = false;
      var accepted = measurement.observability.observable === true;
      if (!accepted && machine.state === "ARMED") holdPlant(machine.nowMs, "SENSOR_UNOBSERVABLE", measurement.observability.reasons.join("; "));
      appendEvent({ kind: "OBSERVATION", direction: "sensor-to-emulator", atMs: machine.nowMs, accepted: accepted, code: accepted ? "OBSERVABLE" : "SENSOR_UNOBSERVABLE", normalizedInput: measurement, response: null }, preState, snapshot());
      return deepFreeze({ accepted: accepted, code: accepted ? "OBSERVABLE" : "SENSOR_UNOBSERVABLE", errors: [] });
    }

    function injectFault(kind, timeMs) {
      if (["sensor-dropout", "timeout", "saturation", "disconnect", "over-current", "stuck-channel", "corrupt-checksum", "stale-sequence", "estop"].indexOf(kind) < 0) throw new Error("Unknown injected HIL fault " + kind + ".");
      var preState = snapshot();
      advanceTo(timeMs);
      var code;
      if (kind === "timeout") {
        if (machine.state === "ARMED") advanceTo(machine.lastHeartbeatMs + config.watchdogTimeoutMs + 1);
        code = "WATCHDOG_TIMEOUT";
      } else if (kind === "estop") {
        plant.hold(machine.nowMs); machine.estopLatched = true; machine.state = "ESTOP"; code = "ESTOP_LATCHED";
        machine.activeFault = { code: code, detail: "Injected emergency stop.", atMs: machine.nowMs };
      } else {
        code = { "sensor-dropout": "SENSOR_UNOBSERVABLE", saturation: "SATURATION_LIMIT", disconnect: "DISCONNECT", "over-current": "OVER_CURRENT", "stuck-channel": "STUCK_CHANNEL", "corrupt-checksum": "CORRUPT_CHECKSUM", "stale-sequence": "STALE_SEQUENCE" }[kind];
        holdPlant(machine.nowMs, code, "Injected deterministic fault: " + kind + ".");
        if (["disconnect", "over-current", "stuck-channel"].indexOf(kind) >= 0) machine.state = "FAULT";
        if (kind === "sensor-dropout") { machine.observation = null; machine.observationConsumed = false; }
      }
      appendEvent({ kind: "INJECTED_FAULT", direction: null, atMs: machine.nowMs, accepted: false, code: code, normalizedInput: { fault: kind, timeMs: timeMs }, response: null }, preState, snapshot());
      return snapshot();
    }

    function tick(timeMs) {
      var preState = snapshot();
      advanceTo(timeMs);
      var postState = snapshot();
      appendEvent({ kind: "TICK", direction: null, atMs: machine.nowMs, accepted: true, code: "TIME_ADVANCED", normalizedInput: { timeMs: timeMs }, response: null }, preState, postState);
      return postState;
    }

    function snapshot() {
      var output = {
        schemaVersion: SCHEMA_VERSION,
        protocol: PROTOCOL,
        state: machine.state,
        estopLatched: machine.estopLatched,
        monotonicTimeMs: machine.nowMs,
        lastSeenSeq: machine.lastSeenSeq,
        lastHeartbeatMs: machine.lastHeartbeatMs,
        armEpoch: machine.armEpoch,
        armCounter: machine.armCounter,
        sessionId: machine.sessionId,
        activeFault: machine.activeFault,
        observation: observationSummary(),
        plant: plant.snapshot(),
        config: config,
        configDigest: configDigest,
        safetyMode: config.safetyMode,
        virtualOnly: true,
        hardwareAccess: false,
        transport: "in-memory-only",
        digestAlgorithm: "sha256-jcs-v1"
      };
      output.snapshotDigest = digestValue(output);
      return deepFreeze(clone(output));
    }

    function transcript() {
      var base = { schemaVersion: SCHEMA_VERSION, protocol: PROTOCOL, emulatorVersion: VERSION, seed: config.seed, config: config, configDigest: configDigest, safetyMode: config.safetyMode, virtualOnly: true, hardwareAccess: false, initialState: initialState, finalState: snapshot(), events: machine.events, chainHead: machine.events.length ? machine.events[machine.events.length - 1].eventDigest : null, digestAlgorithm: "sha256-jcs-v1" };
      base.transcriptDigest = digestValue(base);
      return deepFreeze(clone(base));
    }

    initialState = snapshot();

    return Object.freeze({
      receive: receive,
      tick: tick,
      setObservation: setObservation,
      injectFault: injectFault,
      snapshot: snapshot,
      transcript: transcript,
      config: config
    });
  }

  function runHilScenario(raw) {
    assertClosedObject(raw, ["schemaVersion", "config", "events"], "HIL scenario");
    if (raw.schemaVersion !== SCHEMA_VERSION) throw new Error("HIL scenario.schemaVersion must equal " + SCHEMA_VERSION + ".");
    assertDenseArray(raw.events, "HIL scenario.events", Math.floor(LIMITS.maxTranscriptEvents / 2));
    var normalizedConfig = normalizeEmulatorConfig(fieldOr(raw, "config", {}));
    var normalizedEvents = raw.events.map(function (event, index) {
      assertClosedObject(event, ["kind", "message", "timeMs", "measurement", "fault"], "HIL scenario.events[" + index + "]");
      var required;
      if (event.kind === "MESSAGE") { required = ["kind", "message"]; var messageReport = inspectProtocolMessage(event.message, "host-to-emulator"); if (!messageReport.valid) throw new Error("Invalid scenario message: " + messageReport.errors.join("; ")); }
      else if (event.kind === "TICK") { required = ["kind", "timeMs"]; assertInteger(event.timeMs, "HIL scenario tick timeMs", 0, LIMITS.maxTimeMs); }
      else if (event.kind === "OBSERVATION") { required = ["kind", "measurement"]; var measurementReport = validateMeasurement(event.measurement); if (!measurementReport.valid) throw new Error("Invalid scenario measurement: " + measurementReport.errors.join("; ")); }
      else if (event.kind === "FAULT") { required = ["kind", "fault", "timeMs"]; assertIdentifier(event.fault, "HIL scenario fault"); assertInteger(event.timeMs, "HIL scenario fault timeMs", 0, LIMITS.maxTimeMs); }
      else throw new Error("Unknown HIL scenario event kind " + event.kind + ".");
      if (stableStringify(Object.keys(event).sort()) !== stableStringify(required.sort())) throw new Error("HIL scenario event contains fields irrelevant to kind " + event.kind + ".");
      return clone(event);
    });
    var scenarioSpec = { schemaVersion: SCHEMA_VERSION, config: normalizedConfig, events: normalizedEvents };
    var scenarioSpecDigest = digestValue(scenarioSpec);
    var emulator = createHilEmulator(normalizedConfig), responses = [];
    normalizedEvents.forEach(function (event) {
      if (event.kind === "MESSAGE") responses.push(emulator.receive(event.message));
      else if (event.kind === "TICK") emulator.tick(event.timeMs);
      else if (event.kind === "OBSERVATION") emulator.setObservation(event.measurement);
      else emulator.injectFault(event.fault, event.timeMs);
    });
    var result = { schemaVersion: SCHEMA_VERSION, scenarioSpec: scenarioSpec, scenarioSpecDigest: scenarioSpecDigest, finalState: emulator.snapshot(), transcript: emulator.transcript(), responses: responses, digestAlgorithm: "sha256-jcs-v1" };
    result.scenarioDigest = digestValue(result);
    return deepFreeze(clone(result));
  }

  function validateEmulatorSnapshot(value) {
    var errors = [];
    try {
      assertClosedObject(value, ["schemaVersion", "protocol", "state", "estopLatched", "monotonicTimeMs", "lastSeenSeq", "lastHeartbeatMs", "armEpoch", "armCounter", "sessionId", "activeFault", "observation", "plant", "config", "configDigest", "safetyMode", "virtualOnly", "hardwareAccess", "transport", "digestAlgorithm", "snapshotDigest"], "emulator snapshot");
      if (value.schemaVersion !== SCHEMA_VERSION || value.protocol !== PROTOCOL) throw new Error("emulator snapshot version/protocol mismatch.");
      assertState(value.state, "emulator snapshot.state");
      if (typeof value.estopLatched !== "boolean") throw new Error("emulator snapshot.estopLatched must be boolean.");
      if (value.estopLatched && value.state !== "ESTOP") throw new Error("emulator snapshot ESTOP latch/state mismatch.");
      assertInteger(value.monotonicTimeMs, "emulator snapshot.monotonicTimeMs", 0, LIMITS.maxTimeMs);
      assertInteger(value.lastSeenSeq, "emulator snapshot.lastSeenSeq", -1, LIMITS.maxSeq);
      if (value.lastHeartbeatMs !== null) assertInteger(value.lastHeartbeatMs, "emulator snapshot.lastHeartbeatMs", 0, value.monotonicTimeMs);
      assertArmEpoch(value.armEpoch, "emulator snapshot.armEpoch", true);
      assertInteger(value.armCounter, "emulator snapshot.armCounter", 0, LIMITS.maxSeq);
      if (value.sessionId !== null) assertIdentifier(value.sessionId, "emulator snapshot.sessionId");
      if (value.state === "ARMED" && (value.armEpoch === null || value.sessionId === null)) throw new Error("armed emulator snapshot lacks session binding.");
      if (value.state === "DISARMED" && (value.armEpoch !== null || value.sessionId !== null)) throw new Error("disarmed emulator snapshot retains an arm binding.");
      validateFaultRecord(value.activeFault, "emulator snapshot.activeFault");
      if (value.observation !== null) {
        assertClosedObject(value.observation, ["measurementDigest", "observable", "monotonicTimeMs", "consumedByCommand", "sourceStateRevision", "sourceStateDigest"], "emulator snapshot.observation");
        assertDigest(value.observation.measurementDigest, "emulator snapshot observation digest"); assertDigest(value.observation.sourceStateDigest, "emulator snapshot observation sourceStateDigest");
        assertInteger(value.observation.monotonicTimeMs, "emulator snapshot observation time", 0, value.monotonicTimeMs); assertInteger(value.observation.sourceStateRevision, "emulator snapshot observation revision", 0, LIMITS.maxTimeMs);
        if (typeof value.observation.observable !== "boolean" || typeof value.observation.consumedByCommand !== "boolean") throw new Error("emulator snapshot observation flags invalid.");
      }
      var plantReport = validatePlantSnapshot(value.plant); if (!plantReport.valid) throw new Error("emulator snapshot plant invalid: " + plantReport.errors.join("; "));
      if (value.plant.timeMs !== value.monotonicTimeMs) throw new Error("emulator/plant time mismatch.");
      var normalizedConfig = normalizeEmulatorConfig(value.config);
      if (stableStringify(normalizedConfig) !== stableStringify(value.config) || digestValue(value.config) !== value.configDigest) throw new Error("emulator snapshot config binding mismatch.");
      if (value.safetyMode !== "OBSERVATION_BOUND" || value.virtualOnly !== true || value.hardwareAccess !== false || value.transport !== "in-memory-only" || value.digestAlgorithm !== "sha256-jcs-v1") throw new Error("emulator snapshot safety/evidence boundary mismatch.");
      assertDigest(value.snapshotDigest, "emulator snapshot.snapshotDigest");
      var copy = clone(value); delete copy.snapshotDigest; if (digestValue(copy) !== value.snapshotDigest) throw new Error("emulator snapshot digest mismatch.");
    } catch (error) { errors.push(error.message); }
    return deepFreeze({ valid: errors.length === 0, errors: errors });
  }

  function validateHilTranscript(value) {
    var errors = [];
    try {
      assertClosedObject(value, ["schemaVersion", "protocol", "emulatorVersion", "seed", "config", "configDigest", "safetyMode", "virtualOnly", "hardwareAccess", "initialState", "finalState", "events", "chainHead", "digestAlgorithm", "transcriptDigest"], "HIL transcript");
      if (value.schemaVersion !== SCHEMA_VERSION || value.protocol !== PROTOCOL || value.emulatorVersion !== VERSION) throw new Error("HIL transcript version mismatch.");
      assertSeed(value.seed, "HIL transcript.seed");
      var normalizedConfig = normalizeEmulatorConfig(value.config);
      if (stableStringify(normalizedConfig) !== stableStringify(value.config) || digestValue(value.config) !== value.configDigest || value.seed !== value.config.seed) throw new Error("HIL transcript config binding mismatch.");
      if (value.safetyMode !== "OBSERVATION_BOUND" || value.virtualOnly !== true || value.hardwareAccess !== false || value.digestAlgorithm !== "sha256-jcs-v1") throw new Error("HIL transcript safety boundary mismatch.");
      var initialReport = validateEmulatorSnapshot(value.initialState), finalReport = validateEmulatorSnapshot(value.finalState);
      if (!initialReport.valid || !finalReport.valid) throw new Error("HIL transcript contains an invalid endpoint state.");
      assertDenseArray(value.events, "HIL transcript.events", LIMITS.maxTranscriptEvents);
      var previous = null;
      value.events.forEach(function (event, index) {
        assertClosedObject(event, ["index", "kind", "direction", "atMs", "accepted", "code", "normalizedInput", "response", "preState", "postState", "previousEventDigest", "digestAlgorithm", "eventDigest"], "HIL transcript.events[" + index + "]");
        if (event.index !== index || typeof event.kind !== "string" || typeof event.accepted !== "boolean" || typeof event.code !== "string") throw new Error("HIL transcript event header invalid.");
        assertInteger(event.atMs, "HIL transcript event.atMs", 0, LIMITS.maxTimeMs);
        if (event.previousEventDigest !== previous || event.digestAlgorithm !== "sha256-jcs-v1") throw new Error("HIL transcript hash chain linkage mismatch.");
        var preReport = validateEmulatorSnapshot(event.preState), postReport = validateEmulatorSnapshot(event.postState); if (!preReport.valid || !postReport.valid) throw new Error("HIL transcript event state invalid.");
        if (event.response !== null) { var responseReport = validateProtocolResponse(event.response); if (!responseReport.valid) throw new Error("HIL transcript response invalid."); }
        assertDigest(event.eventDigest, "HIL transcript event.eventDigest"); var eventCopy = clone(event); delete eventCopy.eventDigest; if (digestValue(eventCopy) !== event.eventDigest) throw new Error("HIL transcript event digest mismatch.");
        previous = event.eventDigest;
      });
      if (value.chainHead !== previous) throw new Error("HIL transcript chain head mismatch.");
      assertDigest(value.transcriptDigest, "HIL transcript.transcriptDigest"); var copy = clone(value); delete copy.transcriptDigest; if (digestValue(copy) !== value.transcriptDigest) throw new Error("HIL transcript digest mismatch.");
    } catch (error) { errors.push(error.message); }
    return deepFreeze({ valid: errors.length === 0, errors: errors });
  }

  return deepFreeze({
    VERSION: VERSION,
    SCHEMA_VERSION: SCHEMA_VERSION,
    PROTOCOL: PROTOCOL,
    MESSAGE_TYPES: MESSAGE_TYPES.slice(),
    STATES: STATES.slice(),
    LIMITS: LIMITS,
    INTRINSIC_EVIDENCE: INTRINSIC_EVIDENCE,
    EXTRINSIC_EVIDENCE: EXTRINSIC_EVIDENCE,
    SYNTHETIC_MEASUREMENT_EVIDENCE: SYNTHETIC_MEASUREMENT_EVIDENCE,
    optionalDependencies: deepFreeze({ base: !!Base, globalGeometryII: !!G2, inverse: !!Inverse }),
    stableStringify: stableStringify,
    digestValue: digestValue,
    sha256Hex: sha256Hex,
    createQStar: createQStar,
    createVirtualPlant: createVirtualPlant,
    validatePlantSnapshot: validatePlantSnapshot,
    measureVirtualPlant: measureVirtualPlant,
    validateMeasurement: validateMeasurement,
    planSectorAction: planSectorAction,
    crc32: crc32,
    checksumMessage: checksumMessage,
    createProtocolMessage: createProtocolMessage,
    corruptProtocolChecksum: corruptProtocolChecksum,
    validateProtocolMessage: validateProtocolMessage,
    validateProtocolResponse: validateProtocolResponse,
    createHilEmulator: createHilEmulator,
    validateEmulatorSnapshot: validateEmulatorSnapshot,
    validateHilTranscript: validateHilTranscript,
    runHilScenario: runHilScenario
  });
});
