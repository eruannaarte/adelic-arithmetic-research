#!/usr/bin/env python3
"""Generate full-Neumann/continuum Arb coefficient premises for Path 5."""
import argparse
from fractions import Fraction as F
from pathlib import Path
import json,sys,time,hashlib,platform
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from flint import arb,ctx
import flint
from oig_uniform_lattice_arb_cover import finite_gram_series,continuum_gram_series,_metric_diagonals,_exact_dyadic_fraction
from oig_xi_transfer_certificate import STAGE_X_LOWER_BOUNDS
from check_certificate import raw_remainder,qtext,interval,enc,plus,polynomial_box,choose_norm_upper,check,METRICS

PAIRS=((0,0),(0,1),(1,1))

def box(x):
    if not x.is_finite():raise ArithmeticError('nonfinite coefficient')
    return [_exact_dyadic_fraction(x.lower()),_exact_dyadic_fraction(x.upper())]

def text_box(x):return [qtext(t) for t in box(x)]

def generate_cell(a,b,precision=192,order=18,degree=64,n=1001):
    a,b=F(a),F(b);c=(a+b)/2;r=(b-a)/2
    ctx.prec=precision;started=time.monotonic()
    print(f'Computing finite Taylor coefficients n={n}, centre={c}, order={order}',flush=True)
    finite,trace=finite_gram_series(n,c,order,degree)
    print(f'Computing continuum Taylor coefficients after {time.monotonic()-started:.1f}s',flush=True)
    continuum=continuum_gram_series(c,order,precision)
    rootupper=F(2) if b<=3 else F(3)
    result={'n':n,'precision_bits':precision,'interval':[qtext(a),qtext(b)],'centre':qtext(c),'radius':qtext(r),'order':order,'exponential_degree':degree,'sqrt_normalization_upper':qtext(rootupper),'finite_trace':trace,'metrics':{}}
    for m in METRICS:
        sm,sc=_metric_diagonals(m,n)
        inverses_f=[1/(sm[i]*sm[j]).sqrt() for i,j in PAIRS]
        inverses_c=[1/(sc[i]*sc[j]).sqrt() for i,j in PAIRS]
        differences=[[text_box(finite[k][i][j]*inverses_f[p]-continuum[k][i][j]*inverses_c[p]) for k in range(order+1)] for p,(i,j) in enumerate(PAIRS)]
        remscalar=raw_remainder(order+1,a,b,r,rootupper)
        rem=[remscalar*(box(inverses_f[p])[1]+box(inverses_c[p])[1]) for p in range(3)]
        errors=[plus(polynomial_box(differences[p],(-r,r)),(-rem[p],rem[p])) for p in range(3)]
        U=choose_norm_upper(errors)
        floor=STAGE_X_LOWER_BOUNDS['L2' if m=='L2' else 'H1'][1]
        result['metrics'][m]={'inverse_metric_products_finite':[text_box(x) for x in inverses_f],'inverse_metric_products_continuum':[text_box(x) for x in inverses_c],'difference_coefficients':differences,'entry_remainders':[qtext(x) for x in rem],'error_box':[enc(x) for x in errors],'spectral_error_upper':qtext(U),'transferred_floor':qtext(floor-U)}
        print(m,'error upper',float(U),'floor',float(floor-U),flush=True)
    result['elapsed_seconds']=time.monotonic()-started
    return result

def assemble(paths,output):
    cells=[json.loads(Path(p).read_text()) for p in paths]
    floors={m:qtext(STAGE_X_LOWER_BOUNDS['L2' if m=='L2' else 'H1'][1]) for m in METRICS}
    result={'schema':'path5-resolution-taylor-v1','model':{'n':1001,'K':2,'g':'4/5','target':'exact central cell','normalization':'sqrt(1+tau)','output_metric':'Euclidean modal energy'},'covered_interval':[cells[0]['interval'][0],cells[-1]['interval'][1]],'continuum_floors':floors,'cells':cells,'uniform_bounds':{},'environment':{'python':sys.version,'platform':platform.platform(),'python_flint':flint.__version__},'trusted_components':['Arb outward coefficient and metric enclosures','base finite/continuum Taylor coefficient algorithms: full derivation in appendix','existing Stage X continuum floor theorem, separately rechecked in baseline.json'], 'source_hashes':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['oig_uniform_lattice_arb_cover.py','oig_xi_transfer_certificate.py']}}
    for m in METRICS:
        U=max(F(c['metrics'][m]['spectral_error_upper']) for c in cells)
        result['uniform_bounds'][m]={'error_upper':qtext(U),'floor_lower':qtext(F(floors[m])-U)}
    check(result)
    Path(output).write_text(json.dumps(result,indent=2)+'\n')
    print('Assembled and rationally verified',output)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--interval',nargs=2);p.add_argument('--output',required=True);p.add_argument('--precision',type=int,default=192);p.add_argument('--order',type=int,default=18);p.add_argument('--degree',type=int,default=64);p.add_argument('--n',type=int,default=1001);p.add_argument('--assemble',nargs='+')
    a=p.parse_args()
    if a.assemble:assemble(a.assemble,a.output)
    else:
        r=generate_cell(*a.interval,a.precision,a.order,a.degree,a.n);Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
