#!/usr/bin/env python3
"""Build or check the formal Arithmetic Sensing V multiscale certificate."""

from __future__ import annotations

import argparse
import json
import time
from fractions import Fraction
from pathlib import Path

from verified_end_to_end_certificate import VerifiedTimeComponent
from verify_time_ensemble_certificate import (
    artifact_document,
    build_certificate,
    verify_artifact,
)


DIRECTORY = Path(__file__).resolve().parent
REMOTE_PATHS = (
    DIRECTORY
    / "certificates"
    / "arithmetic_sensing_v_multiscale_T510_remote.json",
    DIRECTORY
    / "certificates"
    / "arithmetic_sensing_v_multiscale_T1780_remote.json",
)
DEFAULT_ARTIFACT = (
    DIRECTORY
    / "certificates"
    / "arithmetic_sensing_v_multiscale_end_to_end.json"
)
REFERENCE_COMPONENTS = (
    VerifiedTimeComponent(510, 2_550, Fraction(125, 65_536)),
    VerifiedTimeComponent(1_780, 8_900, Fraction(65_411, 65_536)),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--processes", type=int)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--write", type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    started = time.perf_counter()
    certificate = build_certificate(
        components=REFERENCE_COMPONENTS,
        remote_paths=REMOTE_PATHS,
        processes=arguments.processes,
    )
    if arguments.emit or arguments.write is not None:
        result: dict[str, object] = artifact_document(certificate)
    else:
        with arguments.certificate.open(encoding="utf-8") as handle:
            artifact = json.load(handle)
        result = verify_artifact(artifact, certificate)
        result["elapsed_seconds"] = time.perf_counter() - started
    serialized = json.dumps(result, indent=2, sort_keys=True)
    if arguments.write is not None:
        arguments.write.parent.mkdir(parents=True, exist_ok=True)
        arguments.write.write_text(serialized + "\n", encoding="utf-8")
        print(
            json.dumps(
                {
                    "written": str(arguments.write),
                    "formal_certificate_sha256": result[
                        "formal_certificate_sha256"
                    ],
                    "elapsed_seconds": time.perf_counter() - started,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(serialized)


if __name__ == "__main__":
    main()
