"""Exact rational relative-feasibility decoder; no true-target input.

Data are the eleven real coordinates z=y/(1+tau)^(1/4), in BANK order.
The time and data must be exact rationals. Approximation of a physical datum
or of its normalization must satisfy the separately declared error contract.
"""
from fractions import Fraction as Q
from dataclasses import dataclass
import json
import check as consumer


def exact(value):
    if type(value) not in (int,str,Q):
        raise ValueError('exact integer, rational string, or Fraction required')
    try:return Q(value)
    except (ValueError,ZeroDivisionError) as e:raise ValueError('invalid rational') from e


def solve2(matrix,rhs):
    a,b=matrix[0];c,d=matrix[1];det=a*d-b*c
    if b!=c or a<=0 or det<=0:raise ValueError('positive symmetric matrix required')
    return ((d*rhs[0]-b*rhs[1])/det,(a*rhs[1]-c*rhs[0])/det)


def value(coefficients,tau):
    z=tau-Q(3,2);out=Q(0)
    for c in reversed(coefficients):out=out*z+c
    return out


@dataclass(frozen=True)
class Result:
    status:str
    feasible_targets:tuple
    estimate:tuple|None


class CertifiedBank:
    """Validate the full certificate once; retain immutable polynomial data."""
    def __init__(self):
        kernel=json.loads((consumer.HERE/'kernel.json').read_text())
        self.summary=consumer.check(kernel=kernel)
        self._coeff=tuple(tuple(tuple(row) for row in d) for d in consumer.interval_coefficients(kernel))

    def matrices(self,tau):
        tau=exact(tau)
        if not Q(1)<=tau<=Q(2):raise ValueError('known time outside [1,2]')
        return {500+j:tuple(tuple(value(self._coeff[abs(sensor-j)][port],tau)
                                      for port in (0,1)) for sensor in consumer.BANK)
                for j in consumer.TARGETS}

    def decode(self,data,tau,metric='L2',numerical_relative_radius='0'):
        if metric not in ('L2','declared_H1','natural_discrete_H1'):
            raise ValueError('unknown source/noise calibration')
        xi=exact(numerical_relative_radius)
        if not Q(0)<=xi<=Q(1,10**9):raise ValueError('numerical radius outside certified contract')
        if type(data) not in (list,tuple) or len(data)!=11:raise ValueError('eleven real coordinates required')
        z=tuple(exact(v) for v in data);energy=sum((v*v for v in z),Q())
        if not energy:raise ValueError('zero data outside nonzero-source model')
        factor=1 if metric=='L2' else 41
        eta=Q(3,10**7 if factor==1 else 10**8)
        delta=eta+Q(1,10**9)+xi
        radius2=factor*(delta/consumer.A0)**2
        accepted=[];estimates={}
        for label,P in self.matrices(tau).items():
            G=tuple(tuple(sum((row[i]*row[j] for row in P),Q()) for j in (0,1)) for i in (0,1))
            rhs=tuple(sum((row[i]*y for row,y in zip(P,z)),Q()) for i in (0,1))
            H=tuple(tuple(G[i][j]-radius2*int(i==j) for j in (0,1)) for i in (0,1))
            witness=solve2(H,rhs)
            minimum=energy-sum((a*b for a,b in zip(rhs,witness)),Q())
            if minimum<=0:
                accepted.append(label);estimates[label]=solve2(G,rhs)
        if not accepted:return Result('incompatible',(),None)
        if len(accepted)>1:return Result('abstain',tuple(accepted),None)
        return Result('unique',tuple(accepted),estimates[accepted[0]])
