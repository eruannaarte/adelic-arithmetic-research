"""Independent full finite-grid algorithm, used only as a floating diagnostic."""
from fractions import Fraction as Q
from pathlib import Path
import argparse, importlib.util, json
import numpy as np
from decoder import CertifiedBank

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_full_finite_response',HERE.parents[1]/'transfer_theorem_2026_09/resolution/forward_checks.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)


def run(write=False):
    banks={b:CertifiedBank(b) for b in ('8','9')};records=[]
    for tau in (Q(1),Q(285,256),Q(2)):
        for label,u in ((490,(Q(3,5),Q(4,5))),(507,(Q(-4,5),Q(3,5))),(510,(Q(0),Q(1)))):
            actual=old.actual_response(label,list(map(float,u)),float(tau))
            alpha=(1+float(tau))**.25
            for name,bank in banks.items():
                rows=bank.summary['direct_rows'];P=bank.matrices(tau)[label]
                predicted=alpha*np.array([float(sum((a*b for a,b in zip(row,u)),Q())) for row in P])
                discrepancy=float(np.linalg.norm(actual[rows]-predicted))
                assert discrepancy<1e-9
                for metric,profile in bank.profiles.items():
                    eta=float(Q(profile['sensor_relative_radius']))
                    observation=actual[rows].copy();observation[3]+=eta
                    z=[format(v/alpha,'.17g') for v in observation]
                    got=bank.decode(z,tau,metric,'1/1000000000')
                    assert (got.status,got.feasible_targets)==('unique',(label,))
                    err=np.array([float(a-b) for a,b in zip(got.estimate,u)])
                    if metric.startswith('L2'):S=np.ones(2)
                    elif metric=='declared_H1':S=1+(np.pi*np.array([1,2]))**2
                    else:S=1+4*1001**2*np.sin(np.pi*np.array([1,2])/(2*1001))**2
                    relative=float(np.sqrt(np.sum(S*err*err)/np.sum(S*np.array(list(map(float,u)))**2)))
                    assert relative<float(Q(profile['source_relative_accuracy_target']))
                    records.append({'bank':name,'time':str(tau),'target':label,'source':list(map(str,u)),
                                    'profile':metric,'physical_model_discrepancy':discrepancy,
                                    'relative_source_error':relative,'recovered_target':got.feasible_targets[0]})
    result={'status':'floating direct finite-grid diagnostics, not proof input or verified normalization rounding',
            'finite_state_count':1002001,'case_count':len(records),
            'maximum_physical_model_discrepancy':max(r['physical_model_discrepancy'] for r in records),
            'maximum_relative_source_error':max(r['relative_source_error'] for r in records),'cases':records}
    if write:(HERE/'forward_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2));return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');run(p.parse_args().write)
