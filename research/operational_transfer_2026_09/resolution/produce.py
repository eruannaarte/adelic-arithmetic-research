"""Propose smaller-bank preconditioners, with exact whole-cell acceptance."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse, hashlib, importlib.util, json, time
import numpy as np

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parents[1]/'transfer_theorem_2026_09/resolution'
spec=importlib.util.spec_from_file_location('_prior_spatial_exact',PRIOR/'exact.py')
exact=importlib.util.module_from_spec(spec);spec.loader.exec_module(exact)
# The producer's fixed proposal choices are separately declared in the consumer.
CHOICES={'9':((-15,-12,-8,-4,0,4,8,12,16),Q(65,10**9),Q(1,10**11)),
         '8':((-12,-10,-6,-2,2,6,10,14),Q(4,10**8),Q(1,10**12))}


def build(bank):
    rows,sf,pf=CHOICES[bank]
    exact.BANK=rows # Only this newly loaded module instance; no file mutation.
    path=PRIOR/'kernel.json';coeff=exact.polynomial_midpoints(json.loads(path.read_text()))
    cases=[(j,) for j in exact.TARGETS]+list(combinations(exact.TARGETS,2))
    cells=[];started=time.monotonic();attempts=0
    def visit(a,b,pending,depth=0):
        nonlocal attempts
        shifted=exact.shift_kernel(coeff,(a+b)/2);radius=(b-a)/2
        accepted=[];failed=[]
        for index in pending:
            case=cases[index];columns=exact.case_columns(case,shifted)
            M=np.array(exact.midpoint_matrix(columns),dtype=float)
            G=M.T@M
            try:Rfloat=np.linalg.solve(np.linalg.cholesky(G).T,np.eye(G.shape[0]))
            except np.linalg.LinAlgError:failed.append(index);continue
            R=[[Q(format(v,'.10f')) for v in row] for row in Rfloat]
            defect,e2,r2=exact.preconditioned_bounds(columns,R,radius)
            floor=sf if len(case)==1 else pf
            e=exact.sqrt_upper(e2);needed=exact.sqrt_upper(floor*r2)
            attempts+=1
            if defect<1-exact.CENTER_SINGULAR**2 and e+needed<exact.CENTER_SINGULAR:
                accepted.append({'case':list(case),'preconditioner':[[str(v) for v in row] for row in R],
                                 'point_defect_upper':str(exact.ceil_rational(defect)),
                                 'variation_frobenius_upper':str(e),'required_transformed_norm_upper':str(needed)})
            else:failed.append(index)
        if accepted:cells.append({'lower':str(a),'upper':str(b),'records':accepted})
        if depth<=3:print('bank',bank,'cell',str(a),str(b),'accepted',len(accepted),'pending',len(failed),'elapsed',round(time.monotonic()-started,1),flush=True)
        del shifted
        if failed:
            if depth>=14:raise ValueError('certificate failed at maximum depth')
            visit(a,(a+b)/2,failed,depth+1);visit((a+b)/2,b,failed,depth+1)
    visit(Q(1),Q(2),list(range(len(cases))))
    return {'schema':'operational-separated-bank-v1','kernel_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'bank_offsets':list(rows),'target_offsets':list(exact.TARGETS),'time_interval':['1','2'],
            'unnormalized_source_floor':str(sf),'unnormalized_pair_floor':str(pf),
            'center_singular_lower':str(exact.CENTER_SINGULAR),'operator_model_error_upper':'1/1000000000',
            'normalization_lower':'19/16','normalization_upper':'4/3',
            'source_metrics':['L2','declared_H1','natural_discrete_H1'],'H1_metric_upper':'41',
            'cells':cells,'case_count':len(cases),'producer_attempts':attempts}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bank',choices=['8','9'],required=True);p.add_argument('--write',action='store_true');args=p.parse_args()
    d=build(args.bank)
    from check import check
    result=check(certificate=d,bank=args.bank)
    if args.write:
        (HERE/('certificate_'+args.bank+'.json')).write_text(json.dumps(d,indent=2)+'\n')
        (HERE/('checked_'+args.bank+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',args.bank,'rows;',len(d['cells']),'cells;',sum(len(c['records']) for c in d['cells']),'records',flush=True)
