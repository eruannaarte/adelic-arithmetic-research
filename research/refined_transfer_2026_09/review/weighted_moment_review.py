"""Independent moment-form audit of the rational drift approximants.

No approximation producer, its basis, or full-vector consumer is imported.
Weights are reconstructed from the original model literals. Residual norm
squares are recomputed as moment quadratic forms, not sampled polynomials.
"""
import ast
import json
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
from flint import arb, ctx, fmpq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def ball(x):
    x=Q(x)
    return arb(fmpq(x.numerator,x.denominator))


def model_coefficients():
    tree=ast.parse((ROOT/'arithmetic_sensing_iv.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.Assign) and
              any(isinstance(v,ast.Name) and v.id=='REFERENCE_COEFFICIENTS' for v in n.targets))
    return tuple(Q.from_float(v) for v in ast.literal_eval(node.value.args[0]))


def positive_half_weights(count,coeff):
    # Work in the positive x half. The negative half has exactly the same
    # physical weights by cosine symmetry; this is an identity, not an
    # assertion inferred from overlapping intervals.
    result=[]
    for j in range(count//2,count):
        theta=arb.pi()*ball(Q(2*j+1,count))
        w=(1+2*sum((ball(c)*(theta*k).cos() for k,c in enumerate(coeff,1)),arb(0)))/count
        if not w>0:raise AssertionError('positive physical window unresolved')
        result.append(w)
    return result


def run(bits=320):
    doc=json.loads((HERE.parent/'noise/approximation.json').read_text())
    coeff=model_coefficients()
    assert list(map(str,coeff))==doc['physical_window_coefficients']
    assert doc['measurement_count']==8900 and doc['degree']==8
    outputs=[]
    with ctx.workprec(bits):
        outer=positive_half_weights(8900,coeff)
        inner=positive_half_weights(2550,coeff)
        for record in doc['designs']:
            design=record['design']
            assert design in ('multi','outer')
            if design=='outer':
                w=outer
            else:
                a=ball(Q(125,65536))
                w=[(1-a)*v for v in outer]
                # The inner positive half occupies global indices4450:5725,
                # hence offsets0:1275 within this positive outer half.
                for j,v in enumerate(inner):w[j]+=a*v
            moments=[arb(0) for _ in range(45)]
            for j,weight in enumerate(w,4450):
                x=ball(Q(2*j+1-8900,8900));power=arb(1)
                x2=x*x
                for k in range(0,45,2):
                    moments[k]+=2*weight*power
                    power*=x2
            assert moments[0].contains(1)
            checks=[]
            for item in record['approximants']:
                k=item['order'];p=list(map(Q,item['rational_polynomial']))
                assert 9<=k<=20 and len(p)==9
                assert all(a==0 for j,a in enumerate(p) if j%2!=k%2)
                residual=([Q(0)]*(k+1))
                residual[k]=1
                for j,a in enumerate(p):residual[j]-=a
                # Moment quadratic form, deliberately sensitive to
                # cancellation in a different way from full-vector evaluation.
                norm2=sum((ball(a*b)*moments[i+j] for i,a in enumerate(residual)
                           for j,b in enumerate(residual) if a and b),arb(0))
                upper=Q(item['weighted_residual_norm_upper'])
                assert norm2>0 and ball(upper*upper)>norm2
                checks.append(k)
            assert checks==list(range(9,21))
            norms=record['weighted_monomial_norm_upper']
            for k in (9,21,22):
                upper=Q(norms[str(k)])
                assert ball(upper*upper)>moments[2*k]
            q={i['order']:Q(i['weighted_residual_norm_upper']) for i in record['approximants']}
            odd=sum((q[k]/factorial(k) for k in range(9,20,2)),Q())+Q(norms['21'])/factorial(21)
            even=sum((q[k]/factorial(k) for k in range(10,21,2)),Q())+Q(norms['22'])/factorial(22)
            assert Q(record['odd_projected_factor'])==odd
            assert Q(record['even_projected_factor'])==even
            assert Q(record['uniform_phase_frequency_factor'])==max(odd,even)
            outputs.append({'design':design,'verified_rational_approximants':len(checks),
                            'verified_complete_tail_moments':[9,21,22],
                            'uniform_factor':str(max(odd,even))})
    return {'verified':True,'working_precision_bits':bits,
            'method':'fresh physical cosine weights; moment quadratic forms; exact parity',
            'designs':outputs}


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
