"""Apply the independently verified complete orbit clock to degree eleven."""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json
from check import check
from budget import profile
HERE=Path(__file__).resolve().parent

def run():
    check();e=json.loads((HERE/'evidence.json').read_text());path=HERE.parent/'blocks/orbit_bound.json'
    clock=json.loads(path.read_text());results=[]
    if clock['schema']!='complete-orbit-affine-clock-v1':raise ValueError('orbit clock schema')
    for name in ('multi','outer'):
        cr=next(r for r in clock['records'] if r['design']==name)
        app=next(r for r in e['approximations'] if r['design']==name)
        for amplitude in (4000,500):
            previous=json.loads((HERE/f'result_{name}_B{amplitude}.json').read_text())
            rho=Q(previous['certificate']['normal_residual_upper'])
            if rho>Q(1,10**30):raise ValueError('residual ceiling')
            r=profile(e['designs'][name]['degrees'][0],app,cr,rho,amplitude)
            if r['all_49_strict_rounding_gates']!=(amplitude==500):raise ValueError('combined degree-eleven expected consequences changed')
            results.append(r)
    return {'schema':'degree-eleven-orbit-consequence-v1','orbit_bound_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'meaning':'Same complete degree-eleven inverse/tail and physical residuals; replace only the complete clock allowance by the independently checked orbit bound.',
        'results':results}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();out=run();path=HERE/'orbit_comparison.json'
    if a.write:path.write_text(json.dumps(out,indent=2)+'\n')
    elif json.loads(path.read_text())!=out:raise ValueError('orbit comparison differs')
    for r in out['results']:print(r['design'],r['amplitude_upper'],'Emax',float(Q(r['complete_coefficient_error_maximum'])),'pass',r['passing_gates'])
