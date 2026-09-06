"""Default: standard-library exact consequences. --deep: rebuild all ODE boxes."""
import argparse,json,sys
from pathlib import Path
import checker as ch
import synthesize,calibration,anisotropic
HERE=Path(__file__).resolve().parent
load=lambda n:json.loads((HERE/n).read_text())

def check():
    nominal=load('nominal.json');r1=load('cycle1_region.json');r2=load('cycle2_region.json');d2=load('cycle2_certificate.json')
    if ch.evaluate(r1,nominal)!=load('cycle1_certificate.json'):raise ValueError('cycle1 consequences')
    synthesize.verify(r2,nominal,d2)
    if calibration.build(r2,nominal,d2)!=load('cycle2_calibration.json'):raise ValueError('cycle2 calibration')
    anisotropic.verify(r2,nominal,d2,load('cycle3_certificate.json'))
    return nominal,r1,r2

def deep(reports):
    import full_sensitivity as p
    for saved in reports:
        cfg=saved['config'];fresh=p.build(ch.Q(saved['parameter_box_radius']),ch.Q(saved['preparation_box_radius']),ch.Q(cfg['step']),cfg['precision_bits'],cfg['order'])
        a=dict(saved);a.pop('elapsed_seconds');fresh.pop('elapsed_seconds')
        if a!=fresh:raise ValueError('full nonlinear replay mismatch')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--deep',action='store_true');args=ap.parse_args()
    reports=check()
    if args.deep:deep(reports)
    print('PASS: all three adaptive-cycle consequences'+(' and all three full nonlinear ODE replays' if args.deep else ' (conditional on supplied ODE enclosures)'))
