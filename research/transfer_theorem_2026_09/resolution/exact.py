"""Independent exact polynomial and preconditioned singular-floor arithmetic."""
from fractions import Fraction as Q
from math import comb,isqrt
import json

BANK=(-15,-12,-9,-6,-3,0,3,6,9,12,16)
TARGETS=tuple(range(-10,11))
CENTER=Q(3,2);ORDER=32
SOURCE_FLOOR=Q(7,10**8);PAIR_FLOOR=Q(1,10**11)
CENTER_SINGULAR=Q(999999,10**6)


def ceil_rational(x,digits=18):
    scale=10**digits
    return Q(-(-x.numerator*scale//x.denominator),scale)


def sqrt_upper(x,digits=12):
    if x<0:raise ValueError('negative radicand')
    scale=10**digits
    k=isqrt(x.numerator*scale*scale//x.denominator)
    if Q(k,scale)**2<x:k+=1
    return Q(k,scale)


def polynomial_midpoints(kernel):
    if kernel['schema']!='periodic-transverse-taylor-v1':raise ValueError('kernel schema')
    expected={'nx':1001,'period':64,'source_modes':[1,2],'g':'4/5','center':'3/2','order':32,
              'exponential_degree':80,'maximum_distance':26,
              'output':'unnormalized global-x average; multiply by (1+tau)^(1/4)'}
    if kernel['model']!=expected:raise ValueError('kernel model changed')
    rows=kernel['coefficient_intervals']
    if len(rows)!=27 or any(len(d)!=2 for d in rows):raise ValueError('kernel shape')
    result=[]
    for d in rows:
        result.append([])
        for port in d:
            if len(port)!=33:raise ValueError('Taylor order changed')
            result[-1].append([])
            for box in port:
                if len(box)!=2:raise ValueError('interval shape')
                lo,hi=map(Q,box)
                if lo>hi or hi-lo>Q(1,10**30):raise ValueError('coefficient enclosure too wide')
                result[-1][-1].append((lo+hi)/2)
    return result


def shift_kernel(coefficients,center):
    delta=center-CENTER
    powers=[Q(1)]
    for k in range(ORDER):powers.append(powers[-1]*delta)
    weights=[[Q(comb(k,j))*powers[k-j] for k in range(j,ORDER+1)] for j in range(ORDER+1)]
    return [[[sum((c[k]*w for k,w in zip(range(j,ORDER+1),weights[j])),Q())
              for j in range(ORDER+1)] for c in d] for d in coefficients]


def case_columns(case,shifted):
    columns=[]
    for number,j in enumerate(case):
        for port in range(2):
            columns.append([[((-1)**number)*v for v in shifted[abs(row-j)][port]] for row in BANK])
    return columns


def midpoint_matrix(columns):
    return [[column[row][0] for column in columns] for row in range(len(BANK))]


def preconditioned_bounds(columns,R,radius):
    d=len(R)
    if d not in (2,4) or len(columns)!=d or any(len(row)!=d for row in R):raise ValueError('preconditioner dimensions')
    B=[];variation=Q(0)
    powers=[Q(1)]
    for k in range(ORDER):powers.append(powers[-1]*radius)
    for row in range(len(BANK)):
        b=[]
        for col in range(d):
            polynomial=[sum((columns[k][row][order]*R[k][col] for k in range(d)),Q()) for order in range(ORDER+1)]
            b.append(polynomial[0])
            e=sum((abs(v)*p for v,p in zip(polynomial[1:],powers[1:])),Q())
            variation+=e*e
        B.append(b)
    defect=Q(0)
    for i in range(d):
        row=sum((abs(sum((b[i]*b[j] for b in B),Q())-int(i==j)) for j in range(d)),Q())
        defect=max(defect,row)
    R2=sum((v*v for row in R for v in row),Q())
    return defect,variation,R2
