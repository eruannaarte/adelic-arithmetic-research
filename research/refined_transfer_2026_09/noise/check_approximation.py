"""Independent full-vector consumer for the weighted family certificate.

No producer, projection routine, saved Gram matrix, or saved weights are used.
The physical windows are reconstructed from their original exact binary values.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import argparse, ast, hashlib, json
from flint import arb, ctx, fmpq

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
M=8900


def rational(value):
    if type(value) not in (str,int,Q):raise ValueError('exact rational required')
    return Q(value)


def ball(q):
    q=Q(q);return arb(fmpq(q.numerator,q.denominator))


def endpoint(a):
    if not a.is_finite() or not a.is_exact():raise ValueError('invalid Arb endpoint')
    m,e=map(int,a.man_exp())
    return Q(m*2**e) if e>=0 else Q(m,2**(-e))


def physical_coefficients():
    tree=ast.parse((ROOT/'arithmetic_sensing_iv.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.Assign) and
              any(isinstance(t,ast.Name) and t.id=='REFERENCE_COEFFICIENTS' for t in n.targets))
    values=[Q.from_float(v) for v in ast.literal_eval(node.value.args[0])]
    if len(values)!=8:raise ValueError('physical window dimension')
    return values


def symmetric_window(count):
    if count not in (8900,2550):raise ValueError('window length')
    cc=physical_coefficients()
    # theta_(m-1-j)=2*pi-theta_j, so every cosine mode agrees exactly.
    half=[]
    for j in range(count//2):
        w=arb(1)
        for k,c in enumerate(cc,1):
            w+=2*ball(c)*(arb.pi()*ball(Q(k*(2*j+1),count))).cos()
        w/=count
        if not w>0:raise ValueError('positive physical weights unresolved')
        half.append(w)
    full=half+half[::-1]
    if not sum(full,arb(0)).contains(1):raise ValueError('physical weight mass disagreement')
    return full


def actual_grid(design):
    w=symmetric_window(M)
    if design=='multi':
        alpha=ball(Q(125,65536));w=[(1-alpha)*v for v in w]
        for j,v in enumerate(symmetric_window(2550),3175):w[j]+=alpha*v
    elif design!='outer':raise ValueError('design name')
    # Both centered windows and the grid have exact reflection symmetry.
    if any(not w[j].overlaps(w[-1-j]) for j in range(M//2)):
        raise ValueError('even physical weighting disagreement')
    return w,[ball(Q(2*j+1-M,M)) for j in range(M)]


def family_factor(record,frequency_limit=Q(1)):
    omega=rational(frequency_limit)
    if not 0<=omega<=1:raise ValueError('frequency limit must lie in [0,1]')
    rr={r['order']:rational(r['weighted_residual_norm_upper']) for r in record['approximants']}
    norms={int(k):rational(v) for k,v in record['weighted_monomial_norm_upper'].items()}
    odd=sum((rr[k]*omega**k/factorial(k) for k in range(9,20,2)),Q())+norms[21]*omega**21/factorial(21)
    even=sum((rr[k]*omega**k/factorial(k) for k in range(10,21,2)),Q())+norms[22]*omega**22/factorial(22)
    return max(odd,even)


def drift_radius(record,amplitude,frequency_limit=Q(1)):
    amp=rational(amplitude)
    if amp<0:raise ValueError('nonnegative absolute amplitude bound required')
    return amp*family_factor(record,frequency_limit)


def check_document(doc,bits=320):
    if doc.get('schema')!='weighted-sinusoidal-approximation-v1':raise ValueError('schema')
    if doc.get('measurement_count')!=M or doc.get('degree')!=8 or doc.get('frequency_limit')!='1':raise ValueError('family contract')
    if list(map(rational,doc.get('physical_window_coefficients',[])))!=physical_coefficients():raise ValueError('physical coefficient mismatch')
    if type(bits) is not int or bits<128:raise ValueError('precision')
    records=doc['designs']
    if [r['design'] for r in records]!=['multi','outer']:raise ValueError('design order/count')
    result=[]
    with ctx.workprec(bits):
        for record in records:
            w,x=actual_grid(record['design'])
            powers=[[arb(1)] for _ in x]
            for row,t in zip(powers,x):
                for k in range(1,45):row.append(row[-1]*t)
            entries=record['approximants']
            if [r['order'] for r in entries]!=list(range(9,21)):raise ValueError('approximant coverage')
            rr={}
            for entry in entries:
                k=entry['order'];poly=list(map(rational,entry['rational_polynomial']))
                if len(poly)!=9 or any(c for j,c in enumerate(poly) if j%2!=k%2):raise ValueError('degree or exact parity')
                norm=rational(entry['weighted_residual_norm_upper'])
                if norm<=0:raise ValueError('positive norm bound required')
                norm2=arb(0)
                # Direct power sum is distinct from the producer's Horner form.
                for ww,pp in zip(w,powers):
                    residual=pp[k]-sum((ball(c)*pp[j] for j,c in enumerate(poly)),arb(0))
                    norm2+=ww*residual*residual
                if not (endpoint(norm2.upper())<=norm*norm):raise ValueError('false weighted residual bound')
                rr[k]=norm
            moments=record['weighted_monomial_norm_upper']
            if sorted(moments)!=['21','22','9']:raise ValueError('complete remainder coverage')
            mm={}
            for key,normtext in moments.items():
                k=int(key);norm=rational(normtext)
                norm2=sum((ww*pp[2*k] for ww,pp in zip(w,powers)),arb(0))
                if norm<=0 or endpoint(norm2.upper())>norm*norm:raise ValueError('false full weighted moment bound')
                mm[k]=norm
            odd=sum((rr[k]/factorial(k) for k in range(9,20,2)),Q())+mm[21]/factorial(21)
            even=sum((rr[k]/factorial(k) for k in range(10,21,2)),Q())+mm[22]/factorial(22)
            expected={'pointwise_taylor_factor':Q(1,factorial(9)),
                      'weighted_taylor_factor':mm[9]/factorial(9),
                      'odd_projected_factor':odd,'even_projected_factor':even,
                      'uniform_phase_frequency_factor':max(odd,even)}
            if any(rational(record[k])!=v for k,v in expected.items()):raise ValueError('inconsistent rational consequence')
            factor=max(odd,even);nu=Q(3,100000)
            result.append({'design':record['design'],**{k:str(v) for k,v in expected.items()},
                           'amplitude_20000_radius':str(20000*factor),
                           'amplitude_limit_at_radius_3e_minus_5':str(nu/factor),
                           'pointwise_amplitude_limit_at_same_radius':str(nu*factorial(9)),
                           'weighted_taylor_amplitude_limit_at_same_radius':str(nu/expected['weighted_taylor_factor']),
                           'pointwise_gain':str(expected['pointwise_taylor_factor']/factor),
                           'weighted_taylor_gain':str(expected['weighted_taylor_factor']/factor),
                           'omega_half_factor':str(family_factor(record,Q(1,2)))})
    return {'schema':'weighted-sinusoidal-checked-v1','verified':True,'bits':bits,
            'polynomial_residual_bounds_checked':24,'weighted_moment_bounds_checked':6,
            'exact_parity_and_physical_symmetry_checked':True,'designs':result}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bits',type=int,default=320);p.add_argument('--write',action='store_true')
    a=p.parse_args();path=HERE/'approximation.json';doc=json.loads(path.read_text())
    result=check_document(doc,a.bits);result['certificate_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    if a.write:(HERE/'checked_approximation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
