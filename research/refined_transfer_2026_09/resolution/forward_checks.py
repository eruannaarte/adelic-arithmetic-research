"""Direct million-state finite model diagnostics; not a proof premise."""
from fractions import Fraction as Q
from pathlib import Path
import argparse, importlib.util, json
import numpy as np
from decoder import CertifiedBank

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_finite_graph_response',HERE.parents[1]/'transfer_theorem_2026_09/resolution/forward_checks.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

def run(write=False):
    bank=CertifiedBank('7');rows=bank.summary['direct_rows'];records=[]
    cases=((Q(1),490),(Q(1),496),(Q(1221707459,10**9),493),(Q(3,2),507),(Q(2),510))
    for t,label in cases:
        u=(Q(3,5),Q(4,5));alpha=(1+float(t))**.25
        P=np.array(bank.matrices(t)[label],float)
        actual=old.actual_response(label,list(map(float,u)),float(t))[rows]
        difference=float(np.linalg.norm(actual-alpha*P@np.array(list(map(float,u)))))
        assert difference<1e-9
        # Exercise the largest Euclidean inverse gain at this target and time.
        U,s,_=np.linalg.svd(alpha*P,full_matrices=False)
        data=actual+1e-7*U[:,-1]
        got=bank.decode([format(z/alpha,'.17g') for z in data],t,numerical_relative_radius='1/1000000000')
        assert (got.status,got.feasible_targets)==('unique',(label,))
        error=float(np.linalg.norm([float(a-b) for a,b in zip(got.estimate,u)]))
        assert error<.001
        records.append({'time':str(t),'target':label,'source':list(map(str,u)),
                        'physical_model_difference':difference,'physical_added_noise':1e-7,
                        'noise_direction':'weakest left singular vector, floating diagnostic',
                        'source_relative_error':error,'recovered_target':got.feasible_targets[0]})
    out={'status':'floating full finite-model diagnostics; no certified normalization or arithmetic rounding claim',
         'finite_state_count':1002001,'case_count':len(records),'cases':records,
         'maximum_physical_model_difference':max(r['physical_model_difference'] for r in records),
         'maximum_source_relative_error':max(r['source_relative_error'] for r in records)}
    if write:(HERE/'forward_checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2));return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');run(p.parse_args().write)
