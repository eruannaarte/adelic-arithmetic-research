"""Fresh physical-weight and moment audit of every new drift approximant.

The current producer and consumer are not imported. Reconstructs the cosine
weights from original model literals, exploits proved reflection symmetry,
and evaluates rational residual norm squares with independently accumulated
moments at 384 bits. Every reported Taylor-tail norm is separately checked.
"""
import ast, hashlib, json
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
from flint import arb, ctx, fmpq
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def ball(x):
    x=Q(x);return arb(fmpq(x.numerator,x.denominator))


def coefficients():
    tree=ast.parse((ROOT/'arithmetic_sensing_iv.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(
        isinstance(v,ast.Name) and v.id=='REFERENCE_COEFFICIENTS' for v in n.targets))
    return tuple(Q.from_float(v) for v in ast.literal_eval(node.value.args[0]))


def half_weights(n,c):
    weights=[]
    for j in range(n//2,n):
        angle=arb.pi()*ball(Q(2*j+1,n))
        w=(1+2*sum((ball(a)*(k*angle).cos() for k,a in enumerate(c,1)),arb(0)))/n
        assert w>0
        weights.append(w)
    return weights


def run():
    path=HERE.parent/'noise/approximation.json';doc=json.loads(path.read_text())
    assert doc['schema']=='clocked-weighted-approximation-v1'
    assert doc['measurement_count']==8900 and doc['tested_degrees']==[6,8,10,12]
    cutoff=doc['even_taylor_cutoff'];assert cutoff==32
    coeff=coefficients();assert list(map(str,coeff))==doc['physical_window_coefficients']
    assert doc['frequency_grid']==['1/2','1','2','3']
    ea=Q(doc['clock_and_derivative']['clock_slope_radius']);assert ea==Q(1,10**14)
    assert Q(doc['sensor_radius'])==Q(1,25000) and Q(doc['mismatch_radius'])==Q(1,10**6)
    records=[]
    with ctx.workprec(384):
        outer=half_weights(8900,coeff);inner=half_weights(2550,coeff)
        for design in ('multi','outer'):
            if design=='outer':w=outer[:]
            else:
                alpha=ball(Q(125,65536));w=[(1-alpha)*a for a in outer]
                for j,a in enumerate(inner):w[j]+=alpha*a
            # Reflection gives odd moments exactly zero and doubles positive
            # half contributions. Zeroth moment is reconstructed, not forced.
            moments=[arb(0) for _ in range(2*(cutoff+2)+1)]
            for j,a in enumerate(w,4450):
                x2=ball(Q(2*j+1-8900,8900))**2;power=arb(1)
                for k in range(0,len(moments),2):
                    moments[k]+=2*a*power;power*=x2
            assert moments[0].contains(1)
            selected=[r for r in doc['records'] if r['design']==design]
            assert [r['degree'] for r in selected]==[6,8,10,12]
            for row in selected:
                p=row['degree'];assert len(row['approximants'])==cutoff-p
                normbounds={}
                for k,item in enumerate(row['approximants'],p+1):
                    assert item['order']==k
                    poly=list(map(Q,item['rational_polynomial']))
                    assert len(poly)==p+1 and all(a==0 for i,a in enumerate(poly) if i%2!=k%2)
                    residual=[-a for a in poly]+[Q() for _ in range(k-p)];residual[k]=Q(1)
                    n2=sum((ball(a*b)*moments[i+j] for i,a in enumerate(residual)
                            for j,b in enumerate(residual) if a and b),arb(0))
                    u=Q(item['weighted_residual_norm_upper'])
                    assert n2>0 and ball(u*u)>n2
                    normbounds[k]=u
                tails={int(k):Q(v) for k,v in row['weighted_monomial_norm_upper'].items()}
                assert sorted(tails)==[33,34]
                assert all(ball(tails[k]**2)>moments[2*k] for k in tails)
                factors=[]
                for nominal in map(Q,doc['frequency_grid']):
                    o=(1+ea)*nominal
                    odd=sum((normbounds[k]*o**k/factorial(k) for k in range(p+1,33,2)),Q())+tails[33]*o**33/factorial(33)
                    even=sum((normbounds[k]*o**k/factorial(k) for k in range(p+2,33,2)),Q())+tails[34]*o**34/factorial(34)
                    factors.append({'physical_frequency_bound':str(nominal),'clock_enlarged_frequency_bound':str(o),
                                    'uniform_phase_factor':str(max(odd,even))})
                records.append({'design':design,'degree':p,'checked_rational_approximants':len(normbounds),
                                'checked_complete_remainder_moments':[33,34],'frequency_factors':factors})
    return {'verified':True,'working_precision_bits':384,
            'approximation_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'rational_approximant_count':sum(r['checked_rational_approximants'] for r in records),
            'complete_remainder_norm_count':2*len(records),'records':records}


if __name__=='__main__':print(json.dumps(run(),indent=2))
