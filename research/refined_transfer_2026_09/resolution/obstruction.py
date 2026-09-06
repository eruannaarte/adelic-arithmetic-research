"""Exact upper stability obstruction for one proposed seven-row bank.

This is not a lower bound on all seven-row designs. A rational pair of source
directions and complete model errors prove intersecting physical noise balls.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import isqrt
import argparse, hashlib, json
import numpy as np
import check
from decoder import value

HERE=Path(__file__).resolve().parent
ROWS=(-11,-8,-4,0,4,8,11)
TIME=Q(1221707459,10**9)
LABELS=(-8,-7)


def sqrt_bounds(x):
    scale=10**30;k=isqrt(x.numerator*scale*scale//x.denominator)
    return Q(k,scale),Q(k+1,scale)


def matrix():
    coeff=check.interval_coefficients(json.loads((check.PRIOR/'kernel.json').read_text()))
    return [[(-1)**side*value(coeff[abs(row-j)][p],TIME) for side,j in enumerate(LABELS) for p in (0,1)] for row in ROWS]


def verify(doc):
    check.require(doc['schema']=='seven-row-coarse-grid-obstruction-v1','obstruction schema')
    check.require(check.same_json(doc['bank_offsets'],list(ROWS)),'obstruction rows')
    check.require(doc['time']==str(TIME) and check.same_json(doc['target_offsets'],list(LABELS)),'obstruction case')
    check.require(doc['kernel_sha256']==hashlib.sha256((check.PRIOR/'kernel.json').read_bytes()).hexdigest(),'obstruction kernel binding')
    v=list(map(check.rational,doc['source_pair']))
    check.require(len(v)==4,'source witness dimension')
    ulo,uhi=sqrt_bounds(sum((x*x for x in v[:2]),Q()))
    vlo,vhi=sqrt_bounds(sum((x*x for x in v[2:]),Q()))
    check.require(min(ulo,vlo)>0,'zero source witness')
    response=[sum((a*b for a,b in zip(row,v)),Q()) for row in matrix()]
    _,approx=sqrt_bounds(sum((x*x for x in response),Q()))
    rho=check.model_error_check(len(ROWS));eta=Q(1,10**7)
    upper=check.A1*approx+rho*(uhi+vhi)
    check.require(doc['sensor_relative_radius']==str(eta),'obstruction noise calibration')
    check.require(upper<eta*(ulo+vlo),'physical response balls not proved to intersect')
    return {'verified':True,'scope':'this particular seven-row bank, two targets and two nonzero L2 sources',
            'sensor_relative_radius':str(eta),'physical_difference_upper':str(upper),
            'sum_source_norms_lower':str(ulo+vlo),
            'sufficient_collision_radius_upper':str(upper/(ulo+vlo)),
            'consequence':'at this allowed noise radius, no decoder can always distinguish these two targets'}


def produce():
    _,_,vh=np.linalg.svd(np.array(matrix(),float),full_matrices=False)
    v=[str(Q(format(x,'.16f'))) for x in vh[-1]]
    return {'schema':'seven-row-coarse-grid-obstruction-v1','bank_offsets':list(ROWS),
            'time':str(TIME),'target_offsets':list(LABELS),'source_pair':v,
            'sensor_relative_radius':'1/10000000',
            'kernel_sha256':hashlib.sha256((check.PRIOR/'kernel.json').read_bytes()).hexdigest()}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    doc=produce() if args.write else json.loads((HERE/'coarse_grid_obstruction.json').read_text())
    result=verify(doc)
    if args.write:
        (HERE/'coarse_grid_obstruction.json').write_text(json.dumps(doc,indent=2)+'\n')
        (HERE/'coarse_grid_obstruction_checked.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
