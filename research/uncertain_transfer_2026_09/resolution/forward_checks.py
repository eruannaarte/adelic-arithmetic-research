"""Direct perturbed million-state finite-model diagnostics; not proof premises."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,ast,importlib.util,json,sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'framework'))
from raw_clock import RawClockBank

# Import only the defining finite uniformization function, avoiding unrelated
# legacy decoder imports. The function remains byte-for-byte the prior source.
path=HERE.parents[1]/'transfer_theorem_2026_09/resolution/forward_checks.py'
parsed=ast.parse(path.read_text())
node=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='actual_response')
namespace={'np':np}
exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),namespace)
actual_response=namespace['actual_response']


def run(write=False):
    bank=RawClockBank();records=[];h=Q(1,2_000_000);lam=Q(1,10**9);eta=Q(11,10**8)
    for t0,t1,label in [(Q(1),Q(1)+h,490),(Q(3,2),Q(3,2)-h,500),(Q(2),Q(2)-h,510)]:
        u=(Q(3,5),Q(4,5));nominal_alpha=(1+float(t0))**.25
        P=np.array(bank.matrices(t0)[label],float)
        actual=np.exp(-float(lam*t1))*actual_response(label,list(map(float,u)),float(t1))[list(bank.rows)]
        nominal=nominal_alpha*P@np.array(list(map(float,u)))
        U,_,_=np.linalg.svd(nominal_alpha*P,full_matrices=False)
        data=actual+float(eta)*U[:,-1]
        got=bank.decode([format(v,'.17g') for v in data],t0,[max(Q(1),t0-h),min(Q(2),t0+h)],eta,lam)
        assert got['status']=='unique' and got['feasible_targets']==[label]
        estimate=list(map(Q,got['source_estimate']))
        error=float(np.linalg.norm([float(a-b) for a,b in zip(estimate,u)]))
        assert error<.001
        records.append({'nominal_time':str(t0),'true_time':str(t1),'source_label':label,
                        'generator_decay_lambda':str(lam),'source':list(map(str,u)),
                        'perturbed_finite_vs_nominal_polynomial_norm':float(np.linalg.norm(actual-nominal)),
                        'physical_sensor_noise':float(eta),'source_relative_error':error,
                        'recovered_label':got['feasible_targets'][0]})
    d={'status':'floating full finite-model diagnostics, not an outward proof or a measured experiment',
       'finite_state_count':1002001,'case_count':len(records),'uniformization_terms':100,
       'maximum_source_relative_error':max(r['source_relative_error'] for r in records),
       'cases':records}
    if write:(HERE/'forward_checks.json').write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(d,indent=2));return d


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');run(p.parse_args().write)
