"""Fresh MPFR remote tails and Arb single-window finite/Gram dependency replay.

The multiscale finite/Gram replay is the separate root verify_multiscale command.
"""
from pathlib import Path
from fractions import Fraction
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from verify_mellin_certificate import build_certificate as remote_build, verify_artifact as remote_check
from verify_end_to_end_certificate import build_certificate as single_build, verify_artifact as single_check


def main():
    started = time.monotonic()
    records = []
    for t in (510, 1780):
        path = ROOT / f'certificates/arithmetic_sensing_v_multiscale_T{t}_remote.json'
        doc = json.loads(path.read_text()); c = doc['certificate']; p = c['parameters']
        fresh = remote_build(degrees=tuple(d['degree'] for d in c['degrees']),
            maximum_norm=50, truncation=1_000_000, bin_width=Fraction(1,100),
            dyadic_bin_bits=96, output_bits=128, mpfr_precision=192,
            include_hybrid_report=False, kernel_bound_method='cancellation',
            observation_time=t, sample_count=t*5, bin_count_override=p['bin_count'])
        record = remote_check(doc, fresh); record['artifact'] = path.name
        records.append(record); print(json.dumps(record), flush=True)
    path = ROOT / 'certificates/arithmetic_sensing_v_multiscale_T1780_single_end_to_end.json'
    doc = json.loads(path.read_text())
    fresh = single_build(degrees=(14,), remote_artifact_path=ROOT / 'certificates/arithmetic_sensing_v_multiscale_T1780_remote.json',
        maximum_norm=50, truncation=1_000_000, observation_time=1780, sample_count=8900,
        arb_precision=128, output_scale_bits=128, processes=4)
    record = single_check(doc, fresh); record['artifact'] = path.name
    records.append(record); print(json.dumps(record), flush=True)
    result = {'verified': True, 'elapsed_seconds': time.monotonic()-started, 'fresh_reconstructions': records}
    (Path(__file__).resolve().parent / 'dependency_rebuild.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__': main()
