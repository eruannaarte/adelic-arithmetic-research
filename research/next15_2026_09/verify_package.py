#!/usr/bin/env python3
"""Run nonmutating cycle checkers and isolated focused suites.

--deep additionally rebuilds the three nonlinear preparation enclosures.
The expensive unchanged d14 and central-resolution premises are inherited;
this runner does not represent their prior replays as new reconstruction.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COUNTS = {"harmonic": 13, "preparation": 17, "quadratic": 14,
          "noise": 11, "resolution": 11}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deep", action="store_true")
    parser.add_argument("--output", type=Path,
                        help="Optional JSON record; a sibling .log contains full output")
    args = parser.parse_args()
    prefix = str(HERE.relative_to(ROOT))
    commands = []
    for chain in ("harmonic", "noise"):
        for cycle in range(1, 4):
            commands.append((f"{chain}.cycle{cycle}",
                             [f"{prefix}/{chain}/cycle{cycle}.py"]))
    prep_args = [f"{prefix}/preparation/verify.py"]
    if args.deep:
        prep_args += ["--deep"]
    else:
        prep_args.insert(0, "-S")
    commands.append(("preparation.all_cycles", prep_args))
    for script in ("geometry", "infinite_geometry", "conditional_query"):
        commands.append((f"quadratic.{script}",
                         ["-S", f"{prefix}/quadratic/{script}.py"]))
    for script in ("placement", "localization", "window"):
        commands.append((f"resolution.{script}",
                         ["-S", f"{prefix}/resolution/check_{script}.py"]))
    for chain in COUNTS:
        commands.append((f"{chain}.tests", ["-m", "unittest", "discover", "-s",
                         f"{prefix}/{chain}", "-p", "test_*.py", "-v"]))
    env = os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
               PYTHONDONTWRITEBYTECODE="1")
    started = time.monotonic()
    results, logs = [], []
    for name, tail in commands:
        command = [sys.executable, *tail]
        begin = time.monotonic()
        run = subprocess.run(command, cwd=ROOT, env=env, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        count = None
        passed = run.returncode == 0
        if name.endswith(".tests"):
            match = re.search(r"Ran (\d+) tests? in", run.stdout)
            count = int(match.group(1)) if match else 0
            passed = passed and count == COUNTS[name.split(".")[0]]
        result = {"name": name, "command": command, "exit_code": run.returncode,
                  "passed": passed, "seconds": round(time.monotonic() - begin, 3)}
        if count is not None:
            result["tests"] = count
        results.append(result)
        logs.append(f"### {name}\n{run.stdout}\n")
        print(f"{'PASS' if passed else 'FAIL'} {name} ({result['seconds']:.3f}s)", flush=True)
        if not passed:
            print(run.stdout, flush=True)
    # Identity record, never offered as a mathematical proof.
    identity = {}
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and path.suffix in {".py", ".json"}:
            if args.output and path.resolve() == args.output.resolve():
                continue
            identity[str(path.relative_to(HERE))] = hashlib.sha256(path.read_bytes()).hexdigest()
    record = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "executable": sys.executable,
              "deep_preparation_replay": args.deep, "completed_research_cycles": 15,
              "job_count": len(results), "focused_tests": sum(r.get("tests", 0) for r in results),
              "all_passed": all(r["passed"] for r in results),
              "seconds": round(time.monotonic() - started, 3), "results": results,
              "file_identity_sha256": identity,
              "scope": "New cycle computations and consequences; see README for explicitly inherited model-to-certificate premises."}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2) + "\n")
        args.output.with_suffix(".log").write_text("\n".join(logs))
    print(f"{sum(r['passed'] for r in results)}/{len(results)} jobs; "
          f"{record['focused_tests']} focused tests; {record['seconds']:.3f}s", flush=True)
    return 0 if record["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
