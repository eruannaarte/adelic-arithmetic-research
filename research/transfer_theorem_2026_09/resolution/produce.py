"""Propose rational preconditioners; accept only exact whole-cell inequalities."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse,hashlib,json,time
import numpy as np
from exact import (BANK,TARGETS,SOURCE_FLOOR,PAIR_FLOOR,CENTER_SINGULAR,
                   polynomial_midpoints,shift_kernel,case_columns,midpoint_matrix,
                   preconditioned_bounds,sqrt_upper,ceil_rational)

HERE=Path(__file__).resolve().parent


def build():
    path=HERE/'kernel.json';kernel=json.loads(path.read_text());coeff=polynomial_midpoints(kernel)
    cases=[(j,) for j in TARGETS]+list(combinations(TARGETS,2))
    cells=[];started=time.monotonic();attempts=0
    def visit(a,b,pending,depth=0):
        nonlocal attempts
        shifted=shift_kernel(coeff,(a+b)/2);radius=(b-a)/2
        accepted=[];failed=[]
        for index in pending:
            case=cases[index];columns=case_columns(case,shifted)
            M=np.array(midpoint_matrix(columns),dtype=float)
            G=M.T@M
            try:Rfloat=np.linalg.solve(np.linalg.cholesky(G).T,np.eye(G.shape[0]))
            except np.linalg.LinAlgError:failed.append(index);continue
            R=[[Q(format(v,'.10f')) for v in row] for row in Rfloat]
            defect,e2,r2=preconditioned_bounds(columns,R,radius)
            floor=SOURCE_FLOOR if len(case)==1 else PAIR_FLOOR
            e=sqrt_upper(e2);needed=sqrt_upper(floor*r2)
            attempts+=1
            if defect<1-CENTER_SINGULAR**2 and e+needed<CENTER_SINGULAR:
                accepted.append({'case':list(case),'preconditioner':[[str(v) for v in row] for row in R],
                                 'point_defect_upper':str(ceil_rational(defect)),
                                 'variation_frobenius_upper':str(e),'required_transformed_norm_upper':str(needed)})
            else:failed.append(index)
        if accepted:cells.append({'lower':str(a),'upper':str(b),'records':accepted})
        if depth<=3:print('cell',str(a),str(b),'accepted',len(accepted),'pending',len(failed),'elapsed',round(time.monotonic()-started,1),flush=True)
        del shifted
        if failed:
            if depth>=12:raise ValueError('certificate failed at maximum depth')
            visit(a,(a+b)/2,failed,depth+1);visit((a+b)/2,b,failed,depth+1)
    visit(Q(1),Q(2),list(range(len(cases))))
    return {'schema':'separated-bank-preconditioned-v1','kernel_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'bank_offsets':list(BANK),'target_offsets':list(TARGETS),'time_interval':['1','2'],
            'unnormalized_source_floor':str(SOURCE_FLOOR),'unnormalized_pair_floor':str(PAIR_FLOOR),
            'center_singular_lower':str(CENTER_SINGULAR),'operator_model_error_upper':'1/1000000000',
            'normalization_lower':'19/16','normalization_upper':'4/3',
            'source_metrics':['L2','declared_H1','natural_discrete_H1'],'H1_metric_upper':'41',
            'cells':cells,'case_count':len(cases),'producer_attempts':attempts}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    d=build()
    from check import check
    check(certificate=d)
    if args.write:(HERE/'certificate.json').write_text(json.dumps(d,indent=2)+'\n')
    print('Produced',len(d['cells']),'nonempty time cells and',sum(len(c['records']) for c in d['cells']),'whole-cell records.')
