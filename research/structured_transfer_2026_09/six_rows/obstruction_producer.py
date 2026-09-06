"""Propose rational ambiguity witnesses, then demand exact physical acceptance."""
from fractions import Fraction as Q
from pathlib import Path
import json,time,hashlib
import numpy as np
from discover import base
import obstruction_check as check
HERE=Path(__file__).resolve().parent

def propose(bank):
    z=base.refine(bank);tau=Q(format(z['time'],'.12f'));labels=z['labels']
    vv=np.polynomial.polynomial.polyval(float(tau)-1.5,base.C)
    matrix=np.concatenate((vv[np.abs(np.array(bank)-labels[0])],-vv[np.abs(np.array(bank)-labels[1])]),axis=1)
    _,_,vh=np.linalg.svd(matrix,full_matrices=False)
    return {'bank_offsets':list(bank),'time':str(tau),'target_offsets':labels,'source_pair':[str(Q(format(x,'.18f'))) for x in vh[-1]]}

def main():
    started=time.monotonic();coeff=check.coefficients();check.physical_error();records=[]
    for i,bank in enumerate(sorted(check.layouts())):
        rec=propose(bank)
        try:result=check.verify_record(rec,coeff)
        except ValueError:
            print('FAILED',bank,rec,flush=True);raise
        records.append(rec)
        if i%25==0:print('verified',i+1,'/',len(check.layouts()),'radius',float(Q(result['collision_radius_upper'])),'seconds',round(time.monotonic()-started,2),flush=True)
    doc={'schema':'seven-deletion-six-row-obstructions-v1','kernel_sha256':hashlib.sha256(check.KERNEL.read_bytes()).hexdigest(),
         'sensor_relative_radius':str(check.ETA),
         'scope':{'deletion_parent':list(check.SEVEN),'time_interval':['1','2'],'target_offsets':[-10,10],'metric':'L2'},'witnesses':records}
    result=check.verify(doc)
    (HERE/'obstructions.json').write_text(json.dumps(doc,indent=2)+'\n')
    (HERE/'checked.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',len(records),'distinct layouts; elapsed',time.monotonic()-started,flush=True)
if __name__=='__main__':main()
