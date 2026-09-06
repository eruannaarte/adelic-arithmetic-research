"""Outward independent point checks of the seven-row model polynomial floors.

These establish only the listed points. Continuous coverage comes from the
complete exact cell consumer, not from this additional audit.
"""
from fractions import Fraction as Q
import json
from pathlib import Path
from flint import arb,ctx,fmpq

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def ball(x):
    x=Q(x)
    return arb(fmpq(x.numerator,x.denominator))


def lower(x):
    endpoint=x.lower()
    assert endpoint.is_exact() and endpoint.is_finite()
    mantissa,power=map(int,endpoint.man_exp())
    return Q(mantissa*2**power) if power>=0 else Q(mantissa,2**(-power))


def positive_pivots(matrix):
    a=[row[:] for row in matrix];pivots=[]
    for k in range(len(a)):
        pivot=a[k][k]
        if not pivot>0:raise AssertionError('positive-definite point floor unresolved')
        pivots.append(lower(pivot))
        for i in range(k+1,len(a)):
            for j in range(i,len(a)):
                a[j][i]=a[i][j]=a[i][j]-a[i][k]*a[k][j]/pivot
    return pivots


def run():
    cert=json.loads((HERE.parent/'resolution/certificate_7.json').read_text())
    kernel=json.loads((ROOT/'research/transfer_theorem_2026_09/resolution/kernel.json').read_text())
    bank=cert['bank_offsets'];a0=Q(19,16)
    assert bank==[-12,-10,-3,0,4,8,10]
    coeff=[[[sum(map(Q,box))/2 for box in row] for row in d] for d in kernel['coefficient_intervals']]
    cases={(Q(1),(-4,)),(Q(1),(-10,-9))}
    selected=sorted(cert['cells'],key=lambda c:(Q(c['upper'])-Q(c['lower']),Q(c['lower'])))[:4]
    for cell in selected:
        l,r=Q(cell['lower']),Q(cell['upper'])
        case=tuple(cell['records'][0]['case'])
        cases.update((t,case) for t in (l,(l+r)/2,r))
    reports=[]
    with ctx.workprec(320):
        for t,case in sorted(cases):
            h=ball(t-Q(3,2));powers=[h**k for k in range(33)]
            dimension=2*len(case)
            # Direct power evaluation is independent of both existing
            # binomial translation and Horner composition implementations.
            matrix=[[sum((ball(c)*power for c,power in zip(coeff[abs(row-label)][port],powers)),arb(0))*(-1)**side
                     for side,label in enumerate(case) for port in (0,1)] for row in bank]
            floor=Q(cert['unnormalized_source_floor' if dimension==2 else 'unnormalized_pair_floor'])
            alpha2=ball(1+t).sqrt()
            gram=[[alpha2*sum((row[i]*row[j] for row in matrix),arb(0))-
                   ball(a0*a0*floor)*int(i==j) for j in range(dimension)] for i in range(dimension)]
            pivots=positive_pivots(gram)
            reports.append({'time':str(t),'target_offsets':list(case),'dimension':dimension,
                            'physical_approximate_map_floor':str(a0*a0*floor),
                            'minimum_positive_LDL_pivot_lower':str(min(pivots))})
    delta=Q(1,10**7)+Q(2,10**9)
    source=a0*a0*Q(cert['unnormalized_source_floor'])
    pair=a0*a0*Q(cert['unnormalized_pair_floor'])
    assert delta*delta < Q(1,10**6)*source
    assert 2*delta*delta<pair
    return {'verified':True,'working_precision_bits':320,'point_count':len(reports),
            'method':'direct polynomial powers; physical alpha squared; outward LDL positive pivots',
            'source_accuracy_squared_fraction_of_limit':str(delta*delta/(Q(1,10**6)*source)),
            'pair_noise_squared_fraction_of_floor':str(2*delta*delta/pair),
            'points':reports,
            'scope':'listed approximate-map point floors only; whole-time and complete model errors use the separate exact consumer'}


if __name__=='__main__':print(json.dumps(run(),indent=2))
