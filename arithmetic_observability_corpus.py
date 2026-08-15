#!/usr/bin/env python3
"""Build and verify the Arithmetic Observability corpus manifest.

This verifier is an index and integrity layer, not a new mathematical proof.
It pins ten manuscripts, eleven formal package triplets, the external proof
objects consumed by the tail branch, and the companion atlas.  It also checks
that a typed dependency DAG, model-boundary declarations, and the
goal-requirement evidence map are internally coherent.

The manifest deliberately separates manuscript theorem claims from finite
formal certificates.  A package entry certifies only its declared finite
scope; merely being indexed here does not mechanize the surrounding paper.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
from typing import Any, Iterable


SCHEMA = "arithmetic-observability-corpus-v1"
PINNED_PAYLOAD_SHA256 = "a64f515f770d316a3d6ecad4b70494af1a5cc90342b4076c7fd783fce0f1c0d6"

DIRECTORY = Path(__file__).resolve().parent
VERIFIER_PATH = DIRECTORY / "arithmetic_observability_corpus.py"
TESTS_PATH = DIRECTORY / "test_arithmetic_observability_corpus.py"
DEFAULT_ARTIFACT_PATH = DIRECTORY / "arithmetic_observability_corpus_manifest.json"

MAX_JSON_BYTES = 1_000_000
MAX_TEXT_BYTES = 100_000
MAX_JSON_DEPTH = 32
MAX_CONTAINER_ITEMS = 200_000
MAX_INTEGER_BITS = 4_096
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


MANUSCRIPTS = (
    {
        "id": "AO-I",
        "path": "ARITHMETIC_OBSERVABILITY_I.md",
        "sha256": "a576fb54f78026151460cb5bfe9b0ed771830330664043ea66cb5b2f141d0ad4",
        "bytes": 40_956,
        "logical_dependencies": [],
        "model_ids": ["theory-kernel", "finite-prime-box", "degree14-tail"],
        "theorem_anchors": {
            "AO-I.2.1": "Definition 2.1",
            "AO-I.2.2": "Definition 2.2",
            "AO-I.2.3": "Theorem 2.3",
            "AO-I.3.1": "Theorem 3.1",
            "AO-I.4.1": "Theorem 4.1",
            "AO-I.4.2": "Theorem 4.2",
            "AO-I.4.3": "Theorem 4.3",
            "AO-I.5.1": "Theorem 5.1",
            "AO-I.6.1": "Theorem 6.1",
            "AO-I.8.1": "Theorem 8.1",
        },
    },
    {
        "id": "AO-II",
        "path": "ARITHMETIC_OBSERVABILITY_II.md",
        "sha256": "d3764f9cad2a5ef65b162918ce952b0e3b157b446d1d2a28e52d2a0d5e35e3a4",
        "bytes": 31_855,
        "logical_dependencies": ["AO-I"],
        "model_ids": ["finite-prime-box", "ambient-linear"],
        "theorem_anchors": {
            "AO-II.3.1": "Theorem 3.1",
            "AO-II.4.1": "Theorem 4.1",
            "AO-II.5.1": "Theorem 5.1",
        },
    },
    {
        "id": "AO-III",
        "path": "ARITHMETIC_OBSERVABILITY_III.md",
        "sha256": "75172cfe6b5948c5e926fa17eb3297be36fe4158972d729ca8e625a1e6caf169",
        "bytes": 25_852,
        "logical_dependencies": ["AO-I", "AO-II"],
        "model_ids": ["finite-prime-box", "multiplicative-geometric", "normalized-product"],
        "theorem_anchors": {
            "AO-III.2.1": "Theorem 2.1",
            "AO-III.4.1": "Theorem 4.1",
            "AO-III.4.2": "Theorem 4.2",
            "AO-III.5.1": "Theorem 5.1",
        },
    },
    {
        "id": "AO-IV",
        "path": "ARITHMETIC_OBSERVABILITY_IV.md",
        "sha256": "a12d6e09cefddbfadbafe142b23167254156259cb4a18d694693a92dcc6c5b17",
        "bytes": 31_507,
        "logical_dependencies": ["AO-III"],
        "model_ids": ["finite-prime-box", "multiplicative-geometric"],
        "theorem_anchors": {
            "AO-IV.2.1": "Theorem 2.1",
            "AO-IV.3.1": "Theorem 3.1",
            "AO-IV.4.1": "Theorem 4.1",
            "AO-IV.5.3": "Theorem 5.3",
            "AO-IV.5.4": "Theorem 5.4",
        },
    },
    {
        "id": "AO-V",
        "path": "ARITHMETIC_OBSERVABILITY_V.md",
        "sha256": "784b0671047c70217b7c88ce7d87dda1fabfcb6f643c3ad651fb24bc61655f4f",
        "bytes": 39_561,
        "logical_dependencies": ["AO-IV"],
        "model_ids": ["finite-prime-box", "multiplicative-geometric"],
        "theorem_anchors": {
            "AO-V.4.1": "Theorem 4.1",
            "AO-V.4.2": "Theorem 4.2",
            "AO-V.5.1": "Theorem 5.1",
            "AO-V.5.3": "Definition 5.3",
            "AO-V.6.2": "Theorem 6.2",
            "AO-V.7.1": "Theorem 7.1",
            "AO-V.8.1": "Theorem 8.1",
            "AO-V.8.2": "Corollary 8.2",
        },
    },
    {
        "id": "AO-VI",
        "path": "ARITHMETIC_OBSERVABILITY_VI.md",
        "sha256": "ee2e6f1f604362d72553073e4e721e7e4a56724c2dba12e4903d8015d0056df4",
        "bytes": 40_910,
        "logical_dependencies": ["AO-I", "AO-III", "AO-IV", "AO-V"],
        "model_ids": ["finite-prime-box", "normalized-product"],
        "theorem_anchors": {
            "AO-VI.3.2": "Theorem 3.2",
            "AO-VI.4.1": "Theorem 4.1",
            "AO-VI.4.2": "Theorem 4.2",
            "AO-VI.6.1": "Theorem 6.1",
            "AO-VI.6.2": "Theorem 6.2",
            "AO-VI.7.2": "Theorem 7.2",
            "AO-VI.7.3": "Theorem 7.3",
            "AO-VI.8.1": "Theorem 8.1",
        },
    },
    {
        "id": "AO-VII",
        "path": "ARITHMETIC_OBSERVABILITY_VII.md",
        "sha256": "7ea892a8dc4e9e6990f97d86a622fb4eeb949eaa33c47fad9948c819ee6c9d00",
        "bytes": 37_557,
        "logical_dependencies": ["AO-I", "EXT-ASV"],
        "model_ids": ["degree14-tail", "separated-query"],
        "theorem_anchors": {
            "AO-VII.2.1": "Theorem 2.1",
            "AO-VII.4.1": "Theorem 4.1",
            "AO-VII.5.1": "Theorem 5.1",
            "AO-VII.7.2": "Theorem 7.2",
            "AO-VII.8.1": "Theorem 8.1",
            "AO-VII.8.2": "Corollary 8.2",
            "AO-VII.9.1": "Theorem 9.1",
        },
    },
    {
        "id": "AO-VIII",
        "path": "ARITHMETIC_OBSERVABILITY_VIII.md",
        "sha256": "136b7e375404ddeee81b01d356f61ad75587b94bc0754dfc939040bbefc69a23",
        "bytes": 40_949,
        "logical_dependencies": ["AO-I", "AO-VII", "EXT-ASV"],
        "model_ids": ["degree14-tail", "continuous-common-box"],
        "theorem_anchors": {
            "AO-VIII.2.1": "Theorem 2.1",
            "AO-VIII.2.2": "Theorem 2.2",
            "AO-VIII.3.1": "Theorem 3.1",
            "AO-VIII.4.1": "Theorem 4.1",
            "AO-VIII.4.2": "Theorem 4.2",
            "AO-VIII.6.1": "Theorem 6.1",
            "AO-VIII.7.1": "Theorem 7.1",
            "AO-VIII.8.1": "Theorem 8.1",
        },
    },
    {
        "id": "AO-IX",
        "path": "ARITHMETIC_OBSERVABILITY_IX.md",
        "sha256": "8cf3d52cf6dbae6dedca2edf132268e56e422cb949f6517a0bb205b839a5c6af",
        "bytes": 47_158,
        "logical_dependencies": ["AO-I", "AO-VIII", "EXT-ASV"],
        "model_ids": ["degree14-tail", "continuous-common-box", "independent-integral-envelope"],
        "theorem_anchors": {
            "AO-IX.2.1": "Theorem 2.1",
            "AO-IX.2.4": "Corollary 2.4",
            "AO-IX.3.1": "Proposition 3.1",
            "AO-IX.3.2": "Theorem 3.2",
            "AO-IX.4.1": "Theorem 4.1",
            "AO-IX.4.2": "Theorem 4.2",
            "AO-IX.6.2": "Theorem 6.2",
            "AO-IX.7.1": "Theorem 7.1",
        },
    },
    {
        "id": "AO-X",
        "path": "ARITHMETIC_OBSERVABILITY_X.md",
        "sha256": "04f9073812bf0c7de4ccd2778773e87f13f730b140f8bf6aab23207ae0b36526",
        "bytes": 52_726,
        "logical_dependencies": ["AO-VIII", "AO-IX", "EXT-ASV"],
        "model_ids": ["degree14-tail", "continuous-common-box", "independent-integral-envelope", "arithmetic-realizability-boundary"],
        "theorem_anchors": {
            "AO-X.2.1": "Theorem 2.1",
            "AO-X.2.2": "Theorem 2.2",
            "AO-X.2.3": "Theorem 2.3",
            "AO-X.3.1": "Lemma 3.1",
            "AO-X.3.2": "Lemma 3.2",
            "AO-X.3.3": "Theorem 3.3",
            "AO-X.4.1": "Theorem 4.1",
            "AO-X.4.2": "Definition 4.2",
            "AO-X.5.3": "Theorem 5.3",
            "AO-X.6.2": "Theorem 6.2",
            "AO-X.6.3": "Theorem 6.3",
            "AO-X.7.2": "Proposition 7.2",
            "AO-X.9.1": "Theorem 9.1",
        },
    },
)


PACKAGES = (
    {
        "id": "PKG-prime-box", "stem": "prime_box",
        "schema": "arithmetic-observability-prime-box-v1",
        "payload_sha256": "3fe7461250815719b4e80c9ad73dc04325f7fb13e8fa0dd83f0906c9505dcc56",
        "hashes": [
            "276a14360474e5276bbcb20273ed1b3a0aaf1a512540a9e6a6e4e2db262cbd75",
            "2adc6774b5f6b550d176b76c77120f58da430bf58f24c72c8b03cfe738444cbc",
            "9230485b5e5df068638a45bfa460951d7bd95c4f29c7d0e4fc36bffb2e494fe1"],
        "sizes": [15_863, 3_020, 6_898], "manuscripts": ["AO-I"],
        "formal_dependencies": [], "runtime": "python-standard-library-exact",
        "artifact_regeneration": "semantic-only-legacy-byte-layout",
        "formal_scope": "Exact finite prime-box response, quotient, and calibrated coefficient-noise geometry; no raw-sample-noise claim.",
    },
    {
        "id": "PKG-asv-bridge", "stem": "asv_bridge",
        "schema": "arithmetic-observability-asv-fibre-bridge-v1",
        "payload_sha256": "bf2e02334d9e2f68942d7ffba394d213c514ddf30c4db0ca277a3263adc8cd58",
        "hashes": [
            "236d079c4b62ac600d3b1fa8ad58d23e048f6c0846f698a2aafe713761715c93",
            "c9096e9de378fdcddc6563fa75e96c66b0b021459bf6c37ac08a4ebed032c374",
            "815346ce249ff06867212b2b4afc493b270d9fade7cc71f8778cb85dc46f3dd0"],
        "sizes": [8_596, 2_648, 6_131], "manuscripts": ["AO-I"],
        "formal_dependencies": ["EXT-ASV"], "runtime": "python-standard-library-exact",
        "artifact_regeneration": "not-asserted-corpus-pins-committed-bytes",
        "formal_scope": "Exact degree-fourteen fibre-distance bracket derived from the pinned Arithmetic Sensing V certificate.",
    },
    {
        "id": "PKG-harmonic-completion", "stem": "harmonic_completion",
        "schema": "arithmetic-observability-harmonic-completion-v1",
        "payload_sha256": "9692367b6b1ad26e713e2da4684726ccc43a9b1b3747f8e1e5f368ad74c70b6a",
        "hashes": [
            "79793078626a2f49ea5c9ca0899714c97cc2294ab3e8772c0ed21b7a032089db",
            "cee9f56340ee4845da936086076dd871b38bffe894424f87404e15505ad4bb9d",
            "5f812f30a4fe4e417b59a64b0b17e7ffeb0c5d94bea1515ac1d793e63e5242b1"],
        "sizes": [33_985, 32_440, 10_863], "manuscripts": ["AO-II"],
        "formal_dependencies": [], "runtime": "python-flint-0.9.0-flint-3.6.0-arb256-one-thread",
        "artifact_regeneration": "not-asserted-corpus-pins-committed-bytes",
        "formal_scope": "Finite 2^a3^b5^c exact-time completion and near-Fourier conditioning; excludes off-box tails, clock jitter, and schedule optimality.",
    },
    {
        "id": "PKG-multiplicative", "stem": "multiplicative",
        "schema": "arithmetic-observability-normalized-product-v1",
        "payload_sha256": "5805a3f385a6b5a0728d38413c9a0cb76d15b59285f671021ff749a6c4ea6a24",
        "hashes": [
            "8a6debaf952abd47d25b7e3bb8b43d39b1694bc5e06210cb1a897dff958295f2",
            "79d42f1a5d5ddf7f305647824918466700bb178ffd016c6fc50cf399c9bdbf6c",
            "84a59d8c5c96c60e8a5649bbf242be3e208c2a546e88dcd8b0d1fc410297b9fd"],
        "sizes": [39_719, 11_293, 18_205], "manuscripts": ["AO-III"],
        "formal_dependencies": [], "runtime": "python-standard-library-exact",
        "artifact_regeneration": "byte-identical-write-tested-upstream",
        "formal_scope": "Exact normalized-product reconstruction, collisions, total-variation bounds, and tangent geometry; excludes raw resonant-noise stability.",
    },
    {
        "id": "PKG-reading-complexity", "stem": "reading_complexity",
        "schema": "arithmetic-observability-reading-complexity-v1",
        "payload_sha256": "4b652c09feb7d68c6eb10c143086c390ee5f48e7618aee694e174d513804ef8e",
        "hashes": [
            "1fe0b19acae202ec9e196555f5cf73d5079ba7d990fbf678fbcc1e798a66ebb9",
            "be668449767cf299295c5ecfc8445ca725e1f3858ce4b9b1e26a5aa52767153b",
            "d343a3d915334702171d9d233193f362db3c7690c240b6e4d6253c0c16f7d4c0"],
        "sizes": [36_407, 25_793, 15_354], "manuscripts": ["AO-IV"],
        "formal_dependencies": [], "runtime": "python-flint-0.9.0-flint-3.6.0-arb256-one-thread",
        "artifact_regeneration": "byte-identical-write-tested-upstream",
        "formal_scope": "Finite Jacobian ranks, resonance, degree, and node separation; global topological/intersection theorems and schedule optimality are not mechanized.",
    },
    {
        "id": "PKG-global-design", "stem": "global_design",
        "schema": "arithmetic-observability-global-design-v1",
        "payload_sha256": "ef58b99b5a1377878a7b9fd770c6a16fa5961bb46af40d74f0697e7f0454f2ab",
        "hashes": [
            "9ecccaed11fb3114fb083a6efce1a97ea98fc7e2a5061c846c5430717b032521",
            "09fdde5f630121329228b8fb57f8ce4cce3b99bf786b53843bf0aa8d793efe37",
            "5e55044c8a4532bf6c671246c8d9dc570053e9982cd396a0e9be7bda63439751"],
        "sizes": [43_479, 28_544, 21_024], "manuscripts": ["AO-V"],
        "formal_dependencies": [], "runtime": "python-flint-0.9.0-flint-3.6.0-arb384-one-thread",
        "artifact_regeneration": "byte-identical-write-tested-upstream",
        "formal_scope": "Certified finite interval/Krawczyk design instances; the general global theorem and schedule optimality remain manuscript mathematics.",
    },
    {
        "id": "PKG-full-segre", "stem": "full_segre",
        "schema": "arithmetic-observability-full-segre-v1",
        "payload_sha256": "02a00b4a1bb18ab366cd1de844f1f23101f5c3f424329b12e268d981b42179fc",
        "hashes": [
            "7fb4e662c02e2bf2854ba491bd00f2d2c9f2c866fe403526e2649140feac1348",
            "2b300bf974b94e8f5f8a6db21360940e174babc316d8481f48082d20268d5c2e",
            "0dc5214d0a2359ed705604bf6e9b2dea1225800887552ca3c306eed6c706589f"],
        "sizes": [26_425, 23_994, 17_681], "manuscripts": ["AO-VI"],
        "formal_dependencies": ["AO-VI"], "runtime": "python-flint-0.9.0-flint-3.6.0-arb384-one-thread",
        "artifact_regeneration": "byte-identical-write-tested-upstream",
        "formal_scope": "Eighteen phase inclusions and canonical six-reading inequalities; general complexity/lower-bound theorems and optimality are not mechanized.",
    },
    {
        "id": "PKG-discrete-queries", "stem": "discrete_queries",
        "schema": "arithmetic-observability-discrete-queries-v1",
        "payload_sha256": "6dc2aa93d6919bd09928768ff6d5592782fdf2867cba50da039b4698be530996",
        "hashes": [
            "202c46df5fe5b0dddd092886a1437d3cff5d2b80d5050a11b51b5d2754247e6e",
            "786b39e7af8041f8a72be6ee291fd2abe105acd373d12a9c2052667c54ba5e87",
            "b58147f7c5b741f9b15db353b342a354b68a4f1e6033fae96a4cf134d618d70a"],
        "sizes": [48_544, 45_955, 25_534], "manuscripts": ["AO-VII"],
        "formal_dependencies": ["EXT-ASV"], "runtime": "python-flint-0.9.0-flint-3.6.0-arb384-one-thread",
        "artifact_regeneration": "byte-identical-write-tested-upstream",
        "formal_scope": "Pinned localized inputs, six-mode Sylvester data, and continuous-tail collision witness; no exact minimax or integral-tail equivalence claim.",
    },
    {
        "id": "PKG-common-nuisance", "stem": "common_nuisance",
        "schema": "arithmetic-observability-common-nuisance-v1",
        "payload_sha256": "96b874899b16e4502d815627c7b722b9ba0332266fb30c8cd4d0579b48ca0cfd",
        "hashes": [
            "2455f901a0f937bea04162b5166e9b62ace4e9a7b473088df2cc3e5a6380f177",
            "1614d880c92d28ed19a40b2679b311a2cafd09033eb895b7f952750e84a2d63c",
            "bad33828fb22ae8a2a7ee995c3acf5d8bf76ff5f4b0648f78a87ccddadefe1fe"],
        "sizes": [44_157, 200_117, 19_350], "manuscripts": ["AO-VIII"],
        "formal_dependencies": ["EXT-ASV"], "runtime": "python-flint-0.9.0-flint-3.6.0-arb512-one-thread",
        "artifact_regeneration": "byte-identical-write-tested-upstream",
        "formal_scope": "Common continuous box, exact finite dual reductions, and integral upper witnesses; no exact global integral minimizer claim.",
    },
    {
        "id": "PKG-alias-circle", "stem": "alias_circle",
        "schema": "arithmetic-observability-alias-circle-v1",
        "payload_sha256": "f97fb3a484bb4e598558b47d8217be05f31b63fe1925a854b43aecf216a66c6f",
        "hashes": [
            "48b21a06c9687a51f1774e802651570813823eb4d9fda29d0eb60e09f7c8dd00",
            "14167ed603a5c003e07f01f6939fea846707693ab0fc81d515267710f4fb95ad",
            "8dd7d601e6242f8c44d08fccab99f9bd67b202d18a9d2de4ce6db016a90db73d"],
        "sizes": [56_351, 122_999, 21_634], "manuscripts": ["AO-IX"],
        "formal_dependencies": ["PKG-common-nuisance", "EXT-ASV", "EXT-MELLIN", "EXT-TRIG"],
        "runtime": "python-flint-0.9.0-flint-3.6.0-gmpy2-2.3.1-mpfr-4.2.2-one-thread",
        "artifact_regeneration": "not-asserted-corpus-pins-committed-bytes",
        "formal_scope": "Fine tail support and global bracket from MPFR192/Arb512 components; exact optimizer, integral equality, and negative quadratic pilot are excluded.",
    },
    {
        "id": "PKG-convexification-gap", "stem": "convexification_gap",
        "schema": "arithmetic-observability-convexification-gap-v1",
        "payload_sha256": "fec0b1e43893794839afb4503975ba4f51b0c9c9980e1e43b38710a690e7348c",
        "hashes": [
            "b98336ed3ff5ea9e9a15e876893a62ff5ba00a0b3ba9268202676535cadd8379",
            "19e0d5fd20674e7191c6de75ced760cc663e3b1cafdc57ad8cd193b2465f11eb",
            "297e6de872100fe07c1d3184bdceb460684799a8664f45a7ee48d8152815fb0e"],
        "sizes": [44_586, 99_015, 25_169], "manuscripts": ["AO-X"],
        "formal_dependencies": ["PKG-common-nuisance", "PKG-alias-circle", "EXT-ASV", "EXT-MELLIN", "EXT-TRIG"],
        "runtime": "python-flint-0.9.0-flint-3.6.0-arb512-one-thread",
        "artifact_regeneration": "byte-identical-write-tested-upstream",
        "formal_scope": "Exact finite prefix/envelope inputs and rank-11, real-profile, and localization computations; analytic convexification theorems remain manuscript mathematics, with no exact optimizer, continuous-integral equality, number-field realization, or coarse-optimizer proof.",
    },
)


EXTERNAL_DEPENDENCIES = (
    {
        "id": "EXT-ASV",
        "path": "certificates/arithmetic_sensing_v_multiscale_end_to_end.json",
        "sha256": "ad03df9d6325512074e6940602c1c888c81abd057a5856d6212f93dc8e780517",
        "bytes": 10_206,
        "schema": "arithmetic-sensing-v-time-ensemble-v1",
        "formal_certificate_sha256": "89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b",
        "role": "Pinned N=50, sigma=2, degree-14 multiscale source measure and certificate.",
    },
    {
        "id": "EXT-MELLIN",
        "path": "verified_mellin_certificate.py",
        "sha256": "27f36ef566ff629bf9f77c649b657be7e672c61ab9ef7a785b90ec01fdf1ac1f",
        "bytes": 25_567,
        "role": "Pinned helper for verified Mellin/log-bin bounds.",
    },
    {
        "id": "EXT-TRIG",
        "path": "exact_trigonometric_positivity.py",
        "sha256": "0ca3f3091a47138179638b0359e7a3b866fbbaddfd4306e84b254455366fb202",
        "bytes": 7_110,
        "role": "Pinned exact trigonometric positivity helper.",
    },
)


# Filled only after the atlas author freezes the one-way companion index.
ATLAS = {
    "path": "ARITHMETIC_OBSERVABILITY_ATLAS.md",
    "sha256": "b381d3f9424de5ed5e6cfe35c27093ee2ce38b08d742299bfe7a1ee7a55db10f",
    "bytes": 23_993,
    "binding_direction": "corpus-payload-to-atlas; atlas names schema and payload key but no corpus artifact hash",
}


MODEL_TAXONOMY = (
    {
        "id": "theory-kernel", "parent": None, "status": "formal-model",
        "scope": "General response fibres, common-subspace quotients, local query factorization, and image lattices.",
    },
    {
        "id": "finite-prime-box", "parent": "theory-kernel", "status": "formal-model",
        "scope": "Finite prime boxes; off-box coefficients are zero unless a mismatch tube is explicitly declared.",
    },
    {
        "id": "ambient-linear", "parent": "finite-prime-box", "status": "formal-model",
        "scope": "Unstructured finite coefficient vectors under harmonic completion.",
    },
    {
        "id": "multiplicative-geometric", "parent": "finite-prime-box", "status": "formal-model",
        "scope": "Rank-one multiplicative factors, with scale conventions stated per theorem.",
    },
    {
        "id": "normalized-product", "parent": "finite-prime-box", "status": "formal-model",
        "scope": "Labelled probability-simplex factors and full Segre products.",
    },
    {
        "id": "degree14-tail", "parent": "theory-kernel", "status": "formal-model",
        "scope": "Pinned Arithmetic Sensing V N=50, sigma=2, degree-14 measure and its infinite coefficient tail.",
    },
    {
        "id": "separated-query", "parent": "degree14-tail", "status": "formal-model",
        "scope": "Individual query labels separated with the declared tail nuisance model.",
    },
    {
        "id": "continuous-common-box", "parent": "degree14-tail", "status": "relaxation-model",
        "scope": "One common compact continuous tail box shared by all labels.",
    },
    {
        "id": "independent-integral-envelope", "parent": "degree14-tail", "status": "relaxation-and-selection-model",
        "scope": "Independent integer coefficient envelopes and their compact integer-selection image; convex hull statements apply only to independent envelopes.",
    },
    {
        "id": "arithmetic-realizability-boundary", "parent": "degree14-tail", "status": "nonclaim-boundary",
        "scope": "Number-field/global arithmetic realization is not implied by membership in the independent integer envelope.",
    },
)


GOAL_REQUIREMENT_EVIDENCE = {
    "definitions": {
        "status": "satisfied",
        "evidence_types": ["framework", "model-boundary"],
        "theorem_ids": ["AO-I.2.1", "AO-I.2.2", "AO-V.5.3", "AO-X.4.2"],
        "package_ids": ["PKG-prime-box", "PKG-convexification-gap"],
        "model_ids": ["theory-kernel", "arithmetic-realizability-boundary"],
        "statement": "Exact equivalence, local identifiability, induced observation metric, and arithmetic defect are explicitly defined.",
    },
    "framework": {
        "status": "satisfied",
        "evidence_types": ["framework", "exact-equivalence", "distinguishability-geometry"],
        "theorem_ids": ["AO-I.2.3", "AO-I.3.1", "AO-VI.6.1", "AO-X.4.1"],
        "package_ids": ["PKG-prime-box", "PKG-full-segre", "PKG-convexification-gap"],
        "model_ids": ["theory-kernel", "normalized-product", "independent-integral-envelope"],
        "statement": "A common fibre/quotient/minimax framework specializes to lattice, near-model, and compact-tail observations.",
    },
    "exact_equivalence": {
        "status": "satisfied",
        "evidence_types": ["exact-equivalence", "model-boundary"],
        "theorem_ids": ["AO-I.2.3", "AO-VI.6.1", "AO-IX.2.1", "AO-X.3.3", "AO-X.4.1"],
        "package_ids": ["PKG-prime-box", "PKG-full-segre", "PKG-alias-circle", "PKG-convexification-gap"],
        "model_ids": ["theory-kernel", "continuous-common-box", "independent-integral-envelope"],
        "statement": "Observational equivalence is quotient equality in deterministic/common-nuisance models; general fibre overlap is recorded separately as confusability and need not be transitive.",
    },
    "stability": {
        "status": "satisfied",
        "evidence_types": ["quantitative-stability", "formal-certificate"],
        "theorem_ids": ["AO-I.2.3", "AO-III.4.2", "AO-V.5.1", "AO-VII.5.1", "AO-VIII.6.1", "AO-IX.2.4"],
        "package_ids": ["PKG-multiplicative", "PKG-global-design", "PKG-discrete-queries", "PKG-common-nuisance", "PKG-alias-circle"],
        "model_ids": ["theory-kernel", "normalized-product", "separated-query", "continuous-common-box"],
        "statement": "Exact inverse moduli, quotient distances, and certified interval lower bounds give falsifiable stability radii in their declared norms.",
    },
    "reconstruction": {
        "status": "satisfied",
        "evidence_types": ["exact-reconstruction", "formal-certificate"],
        "theorem_ids": ["AO-I.5.1", "AO-II.4.1", "AO-III.4.1", "AO-V.6.2", "AO-VI.4.2", "AO-VII.5.1"],
        "package_ids": ["PKG-prime-box", "PKG-harmonic-completion", "PKG-multiplicative", "PKG-global-design", "PKG-full-segre", "PKG-discrete-queries"],
        "model_ids": ["finite-prime-box", "ambient-linear", "multiplicative-geometric", "normalized-product", "separated-query"],
        "statement": "Substantial exact reconstruction theorems cover valuation marginals, harmonic completion, product factors, and four-anchor tail queries.",
    },
    "obstruction": {
        "status": "satisfied",
        "evidence_types": ["matching-obstruction", "model-boundary"],
        "theorem_ids": ["AO-I.3.1", "AO-I.4.1", "AO-I.4.3", "AO-IV.4.1", "AO-VI.4.1", "AO-VI.4.2", "AO-VII.8.2", "AO-VII.9.1", "AO-X.6.3"],
        "package_ids": ["PKG-reading-complexity", "PKG-full-segre", "PKG-discrete-queries", "PKG-convexification-gap"],
        "model_ids": ["theory-kernel", "multiplicative-geometric", "normalized-product", "degree14-tail"],
        "statement": "Rank, symmetry, continuous-tail interior, quantitative blindness, and no-finite-support results match the positive theorems at explicit boundaries.",
    },
    "geometry": {
        "status": "satisfied",
        "evidence_types": ["distinguishability-geometry", "quantitative-stability"],
        "theorem_ids": ["AO-I.6.1", "AO-III.5.1", "AO-V.8.2", "AO-VI.6.2", "AO-IX.2.1", "AO-X.4.1", "AO-X.7.2"],
        "package_ids": ["PKG-prime-box", "PKG-multiplicative", "PKG-full-segre", "PKG-alias-circle", "PKG-convexification-gap"],
        "model_ids": ["finite-prime-box", "normalized-product", "independent-integral-envelope"],
        "statement": "Explicit quotient, tangent, zonoid, Pythagorean-defect, and Voronoi geometries quantify distinguishability.",
    },
    "nontrivial_models": {
        "status": "satisfied",
        "evidence_types": ["exact-reconstruction", "matching-obstruction", "formal-certificate"],
        "theorem_ids": ["AO-I.6.1", "AO-II.4.1", "AO-VI.4.2", "AO-VII.5.1", "AO-VII.9.1", "AO-X.3.3"],
        "package_ids": [
            "PKG-prime-box", "PKG-harmonic-completion", "PKG-multiplicative", "PKG-reading-complexity",
            "PKG-global-design", "PKG-full-segre", "PKG-discrete-queries", "PKG-common-nuisance",
            "PKG-alias-circle", "PKG-convexification-gap", "PKG-asv-bridge"],
        "model_ids": ["finite-prime-box", "degree14-tail"],
        "statement": "The theory is demonstrated on a finite 2^a3^b5^c prime box and the pinned N=50 degree-14 infinite-tail experiment.",
    },
    "reproducibility": {
        "status": "satisfied",
        "evidence_types": ["formal-certificate", "model-boundary"],
        "theorem_ids": ["AO-I.8.1", "AO-V.6.2", "AO-VI.4.2", "AO-VII.5.1", "AO-VIII.6.1", "AO-IX.7.1", "AO-X.3.3"],
        "package_ids": [package["id"] for package in PACKAGES],
        "model_ids": ["finite-prime-box", "degree14-tail"],
        "statement": "Every formal package triplet is byte-pinned and payload-verified; certificates mechanize declared finite instances, not every theorem in the manuscripts.",
    },
}


EVIDENCE_VOCABULARY = (
    "framework", "exact-equivalence", "exact-reconstruction",
    "quantitative-stability", "matching-obstruction",
    "distinguishability-geometry", "model-boundary", "formal-certificate",
)


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _pretty_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False)
        + "\n"
    ).encode("ascii")


def _payload_sha256(payload: object) -> str:
    return hashlib.sha256(_canonical_json(payload)).hexdigest()


def _open_regular(path: Path):
    if path.is_symlink():
        raise ValueError(f"symlink input is forbidden: {path.name}")
    metadata = path.stat(follow_symlinks=False)
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"non-regular input is forbidden: {path.name}")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ValueError(f"regular input could not be opened safely: {path.name}") from exc
    handle = os.fdopen(descriptor, "rb")
    opened = os.fstat(handle.fileno())
    if (opened.st_dev, opened.st_ino) != (metadata.st_dev, metadata.st_ino):
        handle.close()
        raise ValueError(f"input changed before open: {path.name}")
    descriptor_mode = os.fstat(handle.fileno()).st_mode
    if not stat.S_ISREG(descriptor_mode):
        handle.close()
        raise ValueError(f"opened input is not regular: {path.name}")
    return handle


def _read_bounded_regular(path: Path, maximum_bytes: int) -> bytes:
    with _open_regular(path) as handle:
        raw = handle.read(maximum_bytes + 1)
        if len(raw) > maximum_bytes:
            raise ValueError(f"file exceeds byte bound: {path.name}")
        if handle.read(1):
            raise ValueError(f"file grew beyond byte bound: {path.name}")
        if os.fstat(handle.fileno()).st_size != len(raw):
            raise ValueError(f"file changed during bounded read: {path.name}")
    return raw


def _sha256_file(path: Path, maximum_bytes: int = MAX_JSON_BYTES) -> str:
    digest = hashlib.sha256()
    total = 0
    with _open_regular(path) as handle:
        remaining = maximum_bytes + 1
        while True:
            chunk = handle.read(min(65_536, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            total += len(chunk)
            if total > maximum_bytes:
                raise ValueError(f"file exceeds byte bound: {path.name}")
            digest.update(chunk)
        if os.fstat(handle.fileno()).st_size != total:
            raise ValueError(f"file changed during digest: {path.name}")
    return digest.hexdigest()


def _reject_float(_: str) -> object:
    raise ValueError("floating-point JSON values are forbidden")


def _parse_int_limited(text: str) -> int:
    if text == "-0":
        raise ValueError("negative zero is forbidden")
    digits = text[1:] if text.startswith("-") else text
    if len(digits) > 1 and digits.startswith("0"):
        raise ValueError("noncanonical integer")
    if len(digits) > 1_300:
        raise ValueError("integer token exceeds decimal bound")
    value = int(text)
    if value.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("integer exceeds bit bound")
    return value


def _reject_constant(_: str) -> object:
    raise ValueError("non-finite JSON constants are forbidden")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_float_legacy(text: str) -> float:
    if len(text) > 128:
        raise ValueError("legacy decimal token exceeds length bound")
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("legacy decimal is not finite")
    return value


def _validate_json_tree(root: object, *, allow_floats: bool = False) -> None:
    remaining = MAX_CONTAINER_ITEMS
    stack: list[tuple[object, int]] = [(root, 0)]
    while stack:
        value, depth = stack.pop()
        if depth > MAX_JSON_DEPTH:
            raise ValueError("JSON nesting exceeds depth bound")
        if isinstance(value, str):
            if len(value.encode("utf-8")) > MAX_TEXT_BYTES:
                raise ValueError("JSON string exceeds byte bound")
        elif isinstance(value, bool) or value is None or isinstance(value, int):
            pass
        elif allow_floats and isinstance(value, float) and math.isfinite(value):
            pass
        elif isinstance(value, list):
            remaining -= len(value)
            stack.extend((item, depth + 1) for item in value)
        elif isinstance(value, dict):
            remaining -= len(value)
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ValueError("JSON object key is not text")
                if len(key.encode("utf-8")) > MAX_TEXT_BYTES:
                    raise ValueError("JSON key exceeds byte bound")
                stack.append((item, depth + 1))
        else:
            raise ValueError(f"forbidden JSON value type: {type(value).__name__}")
        if remaining < 0:
            raise ValueError("JSON container-item budget exceeded")


def _load_json_strict(path: Path, maximum_bytes: int = MAX_JSON_BYTES) -> tuple[dict[str, object], bytes]:
    raw = _read_bounded_regular(path, maximum_bytes)
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("UTF-8 BOM is forbidden")
    if b"\r" in raw:
        raise ValueError("CR bytes are forbidden; canonical files use LF")
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise ValueError("JSON must end in exactly one LF")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("JSON is not strict UTF-8") from exc
    value = json.loads(
        text,
        object_pairs_hook=_unique_object,
        parse_int=_parse_int_limited,
        parse_float=_reject_float,
        parse_constant=_reject_constant,
    )
    _validate_json_tree(value)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value, raw


def _load_json_legacy_finite(path: Path, maximum_bytes: int = MAX_JSON_BYTES) -> tuple[dict[str, object], bytes]:
    """Bounded compatibility reader for the pre-corpus AS-V decimal JSON."""
    raw = _read_bounded_regular(path, maximum_bytes)
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw:
        raise ValueError("legacy JSON must be BOM-free and LF-normalized")
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise ValueError("legacy JSON must end in exactly one LF")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("legacy JSON is not strict UTF-8") from exc
    value = json.loads(
        text,
        object_pairs_hook=_unique_object,
        parse_int=_parse_int_limited,
        parse_float=_parse_float_legacy,
        parse_constant=_reject_constant,
    )
    _validate_json_tree(value, allow_floats=True)
    if not isinstance(value, dict):
        raise ValueError("legacy top-level JSON value must be an object")
    return value, raw


def _package_paths(package: dict[str, object]) -> list[str]:
    stem = str(package["stem"])
    return [
        f"arithmetic_observability_{stem}.py",
        f"arithmetic_observability_{stem}_certificate.json",
        f"test_arithmetic_observability_{stem}.py",
    ]


def _file_binding(path: str, digest: str, size: int) -> dict[str, object]:
    return {"path": path, "sha256": digest, "bytes": size}


def _manuscript_payload(record: dict[str, object]) -> dict[str, object]:
    return {
        "id": record["id"],
        "file": _file_binding(str(record["path"]), str(record["sha256"]), int(record["bytes"])),
        "logical_dependencies": list(record["logical_dependencies"]),
        "model_ids": list(record["model_ids"]),
        "theorem_ids": sorted(record["theorem_anchors"]),
    }


def _package_payload(record: dict[str, object]) -> dict[str, object]:
    paths = _package_paths(record)
    hashes = list(record["hashes"])
    sizes = list(record["sizes"])
    return {
        "id": record["id"],
        "schema": record["schema"],
        "payload_sha256": record["payload_sha256"],
        "files": {
            role: _file_binding(path, digest, size)
            for role, path, digest, size in zip(
                ("verifier", "certificate", "tests"), paths, hashes, sizes, strict=True
            )
        },
        "manuscript_ids": list(record["manuscripts"]),
        "formal_dependencies": list(record["formal_dependencies"]),
        "runtime": record["runtime"],
        "artifact_regeneration": record["artifact_regeneration"],
        "formal_scope": record["formal_scope"],
        "upstream_artifact_binds_manuscript_hash": record["id"] == "PKG-full-segre",
    }


def expected_payload() -> dict[str, object]:
    manuscript_nodes = [record["id"] for record in MANUSCRIPTS]
    package_nodes = [record["id"] for record in PACKAGES]
    external_nodes = [record["id"] for record in EXTERNAL_DEPENDENCIES]
    logical_edges = [
        [record["id"], dependency]
        for record in MANUSCRIPTS
        for dependency in record["logical_dependencies"]
    ]
    formal_edges = [
        [record["id"], dependency]
        for record in PACKAGES
        for dependency in record["formal_dependencies"]
    ]
    return {
        "corpus": {
            "name": "Arithmetic Observability I-X",
            "schema": SCHEMA,
            "manuscript_count": 10,
            "formal_package_count": 11,
            "triplet_file_count": 33,
            "terminology": {
                "observational_equivalence": "deterministic response equality or equality after a declared common quotient",
                "confusability": "general response-fibre overlap; not asserted to be transitive",
                "tail_set": "compact integer-selection image; not a discrete data-space set",
            },
        },
        "atlas": copy.deepcopy(ATLAS),
        "manuscripts": [_manuscript_payload(record) for record in MANUSCRIPTS],
        "formal_packages": [_package_payload(record) for record in PACKAGES],
        "external_dependencies": copy.deepcopy(list(EXTERNAL_DEPENDENCIES)),
        "dependency_dag": {
            "edge_semantics": "source node depends directly on target node",
            "nodes": sorted(manuscript_nodes + package_nodes + external_nodes),
            "logical_manuscript_edges": sorted(logical_edges),
            "formal_artifact_edges": sorted(formal_edges),
            "schedule_provenance_only_edge": ["AO-VII", "AO-V"],
        },
        "model_taxonomy": copy.deepcopy(list(MODEL_TAXONOMY)),
        "evidence_vocabulary": list(EVIDENCE_VOCABULARY),
        "goal_requirement_evidence": copy.deepcopy(GOAL_REQUIREMENT_EVIDENCE),
        "resource_and_platform_caveats": [
            "The corpus verifier itself uses only the Python standard library and performs no floating-point arithmetic.",
            "Arb/MPFR certificates are conditional on their pinned implementations and are not proof-assistant kernel proofs.",
            "All formal Arb reconstructions require one FLINT thread; relevant packages pin python-flint 0.9.0 and FLINT 3.6.0.",
            "The alias-circle full recomputation additionally pins gmpy2 2.3.1 and MPFR 4.2.2; the recorded reference run is approximately 342 seconds and 3.59 GB.",
            "The corpus pins committed upstream bytes. Prime-box has a legacy byte layout and is required to regenerate semantically, not byte-identically, with its current producer.",
            "Legacy prime-box and ASV-bridge packages do not themselves provide bounded strict JSON parsers; corpus ingestion of their artifacts is bounded and strict.",
            "Canonical corpus output is ASCII JSON with sorted keys, two-space indentation, and exactly one LF; Windows reproduction must preserve LF bytes.",
        ],
        "formal_scope": {
            "claims": [
                "byte integrity and canonical payload digests for every indexed package",
                "presence of every cited theorem identifier in its pinned manuscript",
                "acyclic typed dependency graphs and complete manuscript/package coverage",
                "machine-readable coverage of every requested goal requirement",
            ],
            "nonclaims": [
                "the manifest does not mechanize every theorem in the manuscripts",
                "the manifest does not identify an exact infinite-tail optimizer",
                "convex-hull equality is scoped to independent coefficient envelopes only",
                "continuous-tail equality does not imply integral-tail equality",
                "independent integer selections do not imply number-field or global arithmetic realizability",
                "resource figures are reference-platform caveats, not portable performance guarantees",
            ],
        },
    }


def _assert_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or HEX64.fullmatch(value) is None:
        raise ValueError(f"{label} is not a lowercase SHA-256 digest")
    return value


def _validate_file(
    binding: dict[str, object],
    maximum_bytes: int = MAX_JSON_BYTES,
    *,
    exact_binding: bool = False,
) -> None:
    if not {"path", "sha256", "bytes"} <= set(binding):
        raise ValueError("file binding is incomplete")
    if exact_binding and set(binding) != {"path", "sha256", "bytes"}:
        raise ValueError("file binding keys changed")
    path_text = binding.get("path")
    size = binding.get("bytes")
    digest = _assert_digest(binding.get("sha256"), "file sha256")
    if not isinstance(path_text, str) or Path(path_text).is_absolute() or ".." in Path(path_text).parts:
        raise ValueError("file path is not a safe repository-relative path")
    if not isinstance(size, int) or isinstance(size, bool) or size < 1 or size > maximum_bytes:
        raise ValueError("file byte size is outside its bound")
    path = DIRECTORY / path_text
    if path.is_symlink():
        raise ValueError(f"symlink input is forbidden: {path_text}")
    metadata = path.stat(follow_symlinks=False)
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"non-regular input is forbidden: {path_text}")
    if metadata.st_size != size:
        raise ValueError(f"file byte-size mismatch: {path_text}")
    if _sha256_file(path, maximum_bytes) != digest:
        raise ValueError(f"file SHA-256 mismatch: {path_text}")


def _validate_manuscripts(payload: dict[str, object]) -> None:
    records = payload.get("manuscripts")
    if not isinstance(records, list) or len(records) != 10:
        raise ValueError("manifest must contain exactly ten manuscripts")
    expected = {record["id"]: record for record in MANUSCRIPTS}
    if [record.get("id") for record in records if isinstance(record, dict)] != list(expected):
        raise ValueError("manuscript order or identifiers changed")
    for item in records:
        if not isinstance(item, dict) or item.get("id") not in expected:
            raise ValueError("invalid manuscript record")
        source = expected[item["id"]]
        if item != _manuscript_payload(source):
            raise ValueError(f"manuscript metadata drift: {item['id']}")
        binding = item["file"]
        _validate_file(binding, exact_binding=True)
        raw = _read_bounded_regular(DIRECTORY / str(binding["path"]), MAX_JSON_BYTES)
        if b"\r" in raw or not raw.endswith(b"\n"):
            raise ValueError(f"manuscript is not LF-normalized: {item['id']}")
        text = raw.decode("utf-8", errors="strict")
        if not text.startswith(f"# Arithmetic Observability {item['id'][3:]}\n"):
            raise ValueError(f"manuscript title mismatch: {item['id']}")
        for theorem_id, anchor in source["theorem_anchors"].items():
            if f"### {anchor}" not in text:
                raise ValueError(f"missing theorem anchor {theorem_id}")


def _validate_upstream_artifact(package: dict[str, object]) -> None:
    files = package.get("files")
    if not isinstance(files, dict) or set(files) != {"verifier", "certificate", "tests"}:
        raise ValueError("package triplet is incomplete")
    for binding in files.values():
        if not isinstance(binding, dict):
            raise ValueError("invalid package file binding")
        _validate_file(binding, exact_binding=True)
    certificate_path = DIRECTORY / str(files["certificate"]["path"])
    artifact, _ = _load_json_strict(certificate_path)
    if artifact.get("schema") != package.get("schema"):
        raise ValueError(f"upstream schema mismatch: {package.get('id')}")
    payload = artifact.get("payload")
    payload_digest = _assert_digest(package.get("payload_sha256"), "upstream payload sha256")
    if not isinstance(payload, dict):
        raise ValueError("upstream payload is not an object")
    if artifact.get("payload_sha256") != payload_digest:
        raise ValueError(f"upstream recorded payload mismatch: {package.get('id')}")
    if _payload_sha256(payload) != payload_digest:
        raise ValueError(f"upstream canonical payload mismatch: {package.get('id')}")


def _validate_packages(payload: dict[str, object]) -> None:
    records = payload.get("formal_packages")
    if not isinstance(records, list) or len(records) != 11:
        raise ValueError("manifest must contain exactly eleven formal packages")
    expected = {record["id"]: record for record in PACKAGES}
    if [record.get("id") for record in records if isinstance(record, dict)] != list(expected):
        raise ValueError("package order or identifiers changed")
    seen_files: set[str] = set()
    covered_manuscripts: set[str] = set()
    for item in records:
        if not isinstance(item, dict) or item.get("id") not in expected:
            raise ValueError("invalid formal package record")
        if item != _package_payload(expected[item["id"]]):
            raise ValueError(f"formal package metadata drift: {item['id']}")
        _validate_upstream_artifact(item)
        files = item["files"]
        for binding in files.values():
            path = str(binding["path"])
            if path in seen_files:
                raise ValueError("triplet file occurs in more than one package")
            seen_files.add(path)
        covered_manuscripts.update(item["manuscript_ids"])
    if len(seen_files) != 33:
        raise ValueError("package triplets do not bind exactly 33 distinct files")
    if covered_manuscripts != {record["id"] for record in MANUSCRIPTS}:
        raise ValueError("manuscript/package mapping is incomplete")


def _validate_external_dependencies(payload: dict[str, object]) -> None:
    records = payload.get("external_dependencies")
    if records != list(EXTERNAL_DEPENDENCIES):
        raise ValueError("external dependency metadata drift")
    for item in records:
        _validate_file(item)
    asv_path = DIRECTORY / str(records[0]["path"])
    asv, _ = _load_json_legacy_finite(asv_path)
    if asv.get("schema") != records[0]["schema"]:
        raise ValueError("Arithmetic Sensing V schema mismatch")
    certificate = asv.get("certificate")
    if not isinstance(certificate, dict):
        raise ValueError("Arithmetic Sensing V formal certificate is missing")
    if asv.get("formal_certificate_sha256") != records[0]["formal_certificate_sha256"]:
        raise ValueError("Arithmetic Sensing V recorded formal digest mismatch")
    if _payload_sha256(certificate) != records[0]["formal_certificate_sha256"]:
        raise ValueError("Arithmetic Sensing V formal certificate digest mismatch")


def _assert_acyclic(nodes: Iterable[str], edges: Iterable[list[str]]) -> None:
    node_set = set(nodes)
    adjacency: dict[str, list[str]] = {node: [] for node in node_set}
    indegree = {node: 0 for node in node_set}
    seen: set[tuple[str, str]] = set()
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2 or not all(isinstance(v, str) for v in edge):
            raise ValueError("dependency edge is malformed")
        source, target = edge
        if source not in node_set or target not in node_set:
            raise ValueError("dependency edge names an unknown node")
        if source == target or (source, target) in seen:
            raise ValueError("dependency edge is self-referential or duplicated")
        seen.add((source, target))
        # Reverse for a conventional dependency-first topological traversal.
        adjacency[target].append(source)
        indegree[source] += 1
    queue = sorted(node for node, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        node = queue.pop(0)
        visited += 1
        for successor in sorted(adjacency[node]):
            indegree[successor] -= 1
            if indegree[successor] == 0:
                queue.append(successor)
                queue.sort()
    if visited != len(node_set):
        raise ValueError("dependency graph contains a cycle")


def _validate_dag(payload: dict[str, object]) -> None:
    dag = payload.get("dependency_dag")
    expected = expected_payload()["dependency_dag"]
    if dag != expected or not isinstance(dag, dict):
        raise ValueError("dependency DAG metadata drift")
    nodes = dag["nodes"]
    if not isinstance(nodes, list) or len(nodes) != len(set(nodes)):
        raise ValueError("dependency DAG nodes are duplicated")
    logical = dag["logical_manuscript_edges"]
    formal = dag["formal_artifact_edges"]
    manuscript_ids = {record["id"] for record in MANUSCRIPTS}
    package_ids = {record["id"] for record in PACKAGES}
    external_ids = {record["id"] for record in EXTERNAL_DEPENDENCIES}
    for source, target in logical:
        if source not in manuscript_ids or target not in manuscript_ids | external_ids:
            raise ValueError("logical edge violates manuscript dependency types")
    for source, target in formal:
        manuscript_binding = source == "PKG-full-segre" and target == "AO-VI"
        if source not in package_ids or (target not in package_ids | external_ids and not manuscript_binding):
            raise ValueError("formal edge violates artifact dependency types")
    _assert_acyclic(nodes, logical)
    _assert_acyclic(nodes, formal)
    _assert_acyclic(nodes, [*logical, *formal])


def _validate_models(payload: dict[str, object]) -> None:
    models = payload.get("model_taxonomy")
    if models != list(MODEL_TAXONOMY):
        raise ValueError("model taxonomy drift")
    ids = [item["id"] for item in models]
    if len(ids) != len(set(ids)):
        raise ValueError("model identifiers are duplicated")
    for item in models:
        if item["parent"] is not None and item["parent"] not in ids:
            raise ValueError("model parent is unknown")
    if next(item for item in models if item["id"] == "arithmetic-realizability-boundary")["status"] != "nonclaim-boundary":
        raise ValueError("arithmetic realizability must remain a nonclaim boundary")


def _validate_evidence(payload: dict[str, object]) -> None:
    evidence = payload.get("goal_requirement_evidence")
    required = {
        "definitions", "framework", "exact_equivalence", "stability",
        "reconstruction", "obstruction", "geometry", "nontrivial_models",
        "reproducibility",
    }
    if not isinstance(evidence, dict) or set(evidence) != required:
        raise ValueError("goal-requirement evidence map is incomplete")
    theorem_ids = {
        theorem_id for manuscript in MANUSCRIPTS
        for theorem_id in manuscript["theorem_anchors"]
    }
    package_ids = {package["id"] for package in PACKAGES}
    model_ids = {model["id"] for model in MODEL_TAXONOMY}
    vocabulary = set(EVIDENCE_VOCABULARY)
    for requirement, item in evidence.items():
        if not isinstance(item, dict) or item.get("status") != "satisfied":
            raise ValueError(f"unsatisfied goal requirement: {requirement}")
        if not item.get("theorem_ids") or not set(item["theorem_ids"]) <= theorem_ids:
            raise ValueError(f"unknown or empty theorem evidence: {requirement}")
        if not item.get("package_ids") or not set(item["package_ids"]) <= package_ids:
            raise ValueError(f"unknown or empty package evidence: {requirement}")
        if not item.get("model_ids") or not set(item["model_ids"]) <= model_ids:
            raise ValueError(f"unknown or empty model evidence: {requirement}")
        if not item.get("evidence_types") or not set(item["evidence_types"]) <= vocabulary:
            raise ValueError(f"unknown or empty evidence vocabulary: {requirement}")
        if not isinstance(item.get("statement"), str) or not item["statement"]:
            raise ValueError(f"missing evidence statement: {requirement}")


def validate_payload(payload: dict[str, object], *, validate_files: bool = True) -> None:
    if payload != expected_payload():
        raise ValueError("payload differs from the pinned corpus specification")
    if validate_files:
        _validate_manuscripts(payload)
        _validate_packages(payload)
        _validate_external_dependencies(payload)
        atlas = payload.get("atlas")
        if not isinstance(atlas, dict):
            raise ValueError("atlas binding is missing")
        _validate_file(atlas)
    _validate_dag(payload)
    _validate_models(payload)
    _validate_evidence(payload)
    corpus = payload.get("corpus")
    if not isinstance(corpus, dict) or corpus.get("triplet_file_count") != 33:
        raise ValueError("corpus count metadata is invalid")
    terminology = corpus.get("terminology")
    if not isinstance(terminology, dict):
        raise ValueError("corpus terminology is missing")
    if "not asserted to be transitive" not in str(terminology.get("confusability")):
        raise ValueError("confusability boundary was weakened")
    scope = payload.get("formal_scope")
    if not isinstance(scope, dict) or "convex-hull equality is scoped to independent coefficient envelopes only" not in scope.get("nonclaims", []):
        raise ValueError("independent-envelope convexification boundary is missing")


def build_artifact() -> dict[str, object]:
    payload = expected_payload()
    validate_payload(payload)
    return {
        "schema": SCHEMA,
        "payload": payload,
        "payload_sha256": _payload_sha256(payload),
        "reproduction_files": {
            "verifier": _file_binding(VERIFIER_PATH.name, _sha256_file(VERIFIER_PATH), VERIFIER_PATH.stat().st_size),
            "tests": _file_binding(TESTS_PATH.name, _sha256_file(TESTS_PATH), TESTS_PATH.stat().st_size),
        },
    }


def verify_artifact(path: Path = DEFAULT_ARTIFACT_PATH) -> dict[str, object]:
    artifact, raw = _load_json_strict(path)
    if raw != _pretty_json(artifact):
        raise ValueError("manifest is not strict canonical pretty JSON")
    if set(artifact) != {"schema", "payload", "payload_sha256", "reproduction_files"}:
        raise ValueError("manifest top-level keys changed")
    if artifact.get("schema") != SCHEMA:
        raise ValueError("manifest schema mismatch")
    payload = artifact.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("manifest payload is not an object")
    digest = _payload_sha256(payload)
    if artifact.get("payload_sha256") != digest:
        raise ValueError("manifest payload digest mismatch")
    if digest != PINNED_PAYLOAD_SHA256:
        raise ValueError("manifest payload differs from pinned verifier digest")
    validate_payload(payload)
    reproduction = artifact.get("reproduction_files")
    if not isinstance(reproduction, dict) or set(reproduction) != {"verifier", "tests"}:
        raise ValueError("manifest reproduction bindings are incomplete")
    for role, path_value in (("verifier", VERIFIER_PATH), ("tests", TESTS_PATH)):
        binding = reproduction[role]
        if not isinstance(binding, dict):
            raise ValueError("invalid reproduction-file binding")
        if binding.get("path") != path_value.name:
            raise ValueError("reproduction-file path mismatch")
        _validate_file(binding, exact_binding=True)
    return artifact


def write_artifact(path: Path = DEFAULT_ARTIFACT_PATH) -> dict[str, object]:
    artifact = build_artifact()
    path.write_bytes(_pretty_json(artifact))
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", type=Path, default=DEFAULT_ARTIFACT_PATH)
    parser.add_argument("--write", action="store_true", help="write a freshly reconstructed canonical manifest")
    parser.add_argument("--emit", action="store_true", help="emit the reconstructed manifest to stdout")
    args = parser.parse_args()
    if args.write and args.emit:
        parser.error("--write and --emit are mutually exclusive")
    if args.write:
        artifact = write_artifact(args.artifact)
    elif args.emit:
        artifact = build_artifact()
        print(_pretty_json(artifact).decode("ascii"), end="")
        return
    else:
        artifact = verify_artifact(args.artifact)
    print(f"verified {artifact['schema']} {artifact['payload_sha256']}")


if __name__ == "__main__":
    main()
