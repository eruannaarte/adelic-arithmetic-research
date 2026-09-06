#!/usr/bin/env python3
"""Reproduce new model computations, exact consequences, audits, and tests.

--quick omits full model and independent numerical reconstructions; it checks
consequences of their saved enclosures. The default run includes those replays.
Earlier expensive d14 arithmetic-tail enumerations remain inherited premises.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COUNTS = {'framework': 12, 'noise': 10, 'resolution': 9}


def previous_identity_check():
    expected = json.loads((HERE/'PREVIOUS_ARTIFACTS_SHA256.json').read_text())
    changed = [name for name, digest in expected.items()
               if not (ROOT/name).is_file()
               or hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest]
    return {'passed': not changed, 'files_checked': len(expected), 'changed_or_missing': changed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    base = str(HERE.relative_to(ROOT))
    jobs = [
        ('framework.all_applications', ['-S', f'{base}/framework/applications.py', '--all']),
        ('framework.independent_witnesses', ['-S', f'{base}/framework_review/examples.py']),
        ('framework.independent_KKT', ['-S', f'{base}/framework_review/audit_consumer.py']),
        ('noise.core_exact', ['-S', f'{base}/noise/check_certificate.py']),
    ]
    if not args.quick:
        jobs.extend([
            ('noise.core_model_192', [f'{base}/noise/oscillatory_channels.py', '--precision', '192']),
            ('noise.extended_model_192', [f'{base}/noise/oscillatory_channels.py', '--extended', '--precision', '192']),
            ('noise.extended_model_256', [f'{base}/noise/oscillatory_channels.py', '--extended', '--precision', '256']),
            ('noise.independent_model_320', [f'{base}/noise/independent_audit.py']),
            ('resolution.kernel_192', [f'{base}/resolution/kernel.py', '--precision', '192']),
            ('resolution.kernel_256', [f'{base}/resolution/kernel.py', '--precision', '256']),
            ('resolution.independent_bridge', [f'{base}/resolution/independent_audit.py']),
            ('resolution.full_finite_graph_controls', [f'{base}/resolution/forward_checks.py']),
        ])
    for name in COUNTS:
        jobs.append((name+'.tests', ['-m', 'unittest', 'discover', '-s', f'{base}/{name}', '-p', 'test_*.py', '-v']))
    env = os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    started = time.monotonic()
    records, logs = [], []
    for name, tail in jobs:
        begin = time.monotonic()
        command = [sys.executable, *tail]
        run = subprocess.run(command, cwd=ROOT, env=env, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        passed = run.returncode == 0
        record = {'name': name, 'command': command, 'exit_code': run.returncode,
                  'passed': passed, 'seconds': round(time.monotonic()-begin, 3)}
        if name.endswith('.tests'):
            match = re.search(r'Ran (\d+) tests? in', run.stdout)
            count = int(match.group(1)) if match else 0
            record['tests'] = count
            passed = passed and count == COUNTS[name.split('.')[0]]
            record['passed'] = passed
        records.append(record)
        logs.append(f'### {name}\n{run.stdout}\n')
        print(f"{'PASS' if passed else 'FAIL'} {name} ({record['seconds']:.3f}s)", flush=True)
        if not passed:
            print(run.stdout, flush=True)
    preservation = previous_identity_check()
    print(f"{'PASS' if preservation['passed'] else 'FAIL'} previous artifact identities: {preservation['files_checked']} files", flush=True)
    identity = {}
    for path in sorted(HERE.rglob('*')):
        if path.is_file() and path.suffix in {'.py', '.json'} and not (
                args.output and path.resolve() == args.output.resolve()):
            identity[str(path.relative_to(HERE))] = hashlib.sha256(path.read_bytes()).hexdigest()
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'python': platform.python_version(), 'executable': sys.executable,
              'quick': args.quick, 'job_count': len(records),
              'focused_tests': sum(r.get('tests', 0) for r in records),
              'all_passed': all(r['passed'] for r in records) and preservation['passed'],
              'seconds': round(time.monotonic()-started, 3), 'results': records,
              'previous_artifacts': preservation, 'file_identity_sha256': identity,
              'coverage': {'previous_scalar_gates': 687, 'new_polynomial_gates': 392,
                           'conditional_normal_residual_gates': 392,
                           'spatial_individual_cases': 21, 'spatial_pair_cases': 210,
                           'spatial_whole_cell_records': 895,
                           'common_spatial_metric_contracts': 3},
              'scope': 'New model reconstructions, independent audits, and exact transfer consequences. Unchanged expensive d14 finite/remote arithmetic tails remain explicit inherited premises. Physical calibration and deployed numerical residual validation are not claimed.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2)+'\n')
        args.output.with_suffix('.log').write_text('\n'.join(logs))
    print(f"{sum(r['passed'] for r in records)}/{len(records)} jobs; {report['focused_tests']} focused tests; {report['seconds']:.3f}s", flush=True)
    return 0 if report['all_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
