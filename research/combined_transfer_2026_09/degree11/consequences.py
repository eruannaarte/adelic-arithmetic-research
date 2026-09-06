from pathlib import Path
from fractions import Fraction as Q
import argparse,json
from check import check
from budget import profile,operation_counts
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def run():
    check();doc=json.loads((HERE/'evidence.json').read_text())
    clock=json.loads((ROOT/'research/structured_transfer_2026_09/arithmetic/clock_bound.json').read_text())
    profiles=[]
    for name in ('multi','outer'):
        record=doc['designs'][name]['degrees'][0]
        app=next(a for a in doc['approximations'] if a['design']==name)
        cr=next(c for c in clock['records'] if c['design']==name)
        profiles.append(profile(record,app,cr))
    return {'schema':'degree-eleven-consequences-v1','fixed_contract':profiles,'cost':operation_counts()}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();out=run();path=HERE/'consequences.json'
    if args.write:path.write_text(json.dumps(out,indent=2)+'\n')
    elif json.loads(path.read_text())!=out:raise ValueError('consequences changed')
    for r in out['fixed_contract']:print(r['design'],'Emax',float(Q(r['complete_coefficient_error_maximum'])),'pass',r['passing_gates'],'B limit',float(Q(r['strict_sufficient_amplitude_limit'])))
