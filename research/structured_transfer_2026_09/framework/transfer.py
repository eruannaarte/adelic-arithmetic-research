"""Exact consequence gates for structured inverse and weighted pair transfer."""
from fractions import Fraction as Q


def nonnegative(v):
    if type(v) not in (Q,str,int):
        raise ValueError('exact rational input required')
    q=Q(v)
    if q<0:
        raise ValueError('nonnegative bound required')
    return q


def directional_gate(source_floor,pair_floor,forward,inverse,isotropic,target='1/1000'):
    mu,lam,f,v,r,epsilon=map(nonnegative,(source_floor,pair_floor,forward,inverse,isotropic,target))
    label=lam>2*(f+r)**2
    accuracy=mu>0 and v<epsilon and r*r<(epsilon-v)**2*mu
    uniform=mu>0 and (f+r)**2<epsilon**2*mu
    return {'label_separated':label,'directional_accuracy':accuracy,
            'uniform_accuracy':uniform,'passed':label and accuracy,
            'forward_total':str(f+r)}


def pair_budget(first_radius,second_radius,first_weight,second_weight):
    """Weight check; strict positive Gram difference is a separate premise."""
    a,b,c,d=map(nonnegative,(first_radius,second_radius,first_weight,second_weight))
    if c==0 or d==0:
        raise ValueError('positive block weights required')
    return a*a/c+b*b/d<=1


def integer_gate(n,bias,gram_floor,residual,reading_radius):
    if type(n) is not int or n<2:
        raise ValueError('integer coefficient index required')
    a,f,r,d=map(nonnegative,(bias,gram_floor,residual,reading_radius))
    if f==0:
        raise ValueError('positive Gram floor required')
    margin=Q(1,2)-a-n*n*r/f
    return margin>0 and n**4*d*d<margin*margin*f
