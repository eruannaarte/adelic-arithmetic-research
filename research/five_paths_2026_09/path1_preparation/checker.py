"""Independent standard-library exact checker for finite inverse certificates."""
from fractions import Fraction as Q
from math import isqrt
import argparse,json
from pathlib import Path


def matmul(a,b):return [[sum((x*y for x,y in zip(row,col)),Q(0)) for col in zip(*b)] for row in a]
def trans(a):return list(map(list,zip(*a)))
def inverse(a):
    n=len(a);m=[list(row)+[Q(int(i==j)) for j in range(n)] for i,row in enumerate(a)]
    for i in range(n):
        k=next((k for k in range(i,n) if m[k][i]),None)
        if k is None:raise ValueError('singular nominal Jacobian')
        m[i],m[k]=m[k],m[i];p=m[i][i];m[i]=[x/p for x in m[i]]
        for j in range(n):
            if j!=i:
                p=m[j][i];m[j]=[x-p*y for x,y in zip(m[j],m[i])]
    return [r[n:] for r in m]
def iv(a):
    x,y=map(Q,a)
    if x>y:raise ValueError('reversed interval')
    return x,y
def add(a,b):return a[0]+b[0],a[1]+b[1]
def scale(q,a):return (q*a[0],q*a[1]) if q>=0 else (q*a[1],q*a[0])
def maxabs(a):return max(abs(a[0]),abs(a[1]))
def sqrt_upper(q,den=10**12):
    if q<0:raise ValueError('negative square')
    k=isqrt(q.numerator*den*den//q.denominator)
    if Q(k*k,den*den)<q:k+=1
    ans=Q(k,den);assert ans*ans>=q
    return ans

def verify_inputs(report):
    if report['schema']!='finite-preparation-v1':raise ValueError('schema')
    if Q(report['parameter_box_radius'])<0 or Q(report['preparation_box_radius'])<0:raise ValueError('negative radius')
    if report['source_coordinates']!=['u','v','epsilon']:raise ValueError('source coordinates')
    if report['preparation_coordinates']!=['theta1','theta2','scaled_omega1','scaled_omega2']:raise ValueError('preparation coordinates')
    if report['clock_structure']!='one epsilon shared globally; actual time exp(epsilon)*tau':raise ValueError('clock incidence')
    rows=report['rows']
    # Full sensor/cost/launch contract is literal, independent of producer.
    expected=[
        ('A','theta_1','1','1'),('A','theta_2','1','1'),('A','scaled_omega_2','3/2','3/2'),
        ('B','theta_1','3/4','1'),('B','scaled_omega_1','5/4','5/4'),
        ('C','theta_2','1','1'),('C','scaled_omega_2','3/2','3/2')]
    launches={'A':[Q(4,5),Q(-7,20),Q(0),Q(0)],'B':[Q(-3,5),Q(9,10),Q(0),Q(0)],'C':[Q(6,5),Q(2,5),Q(0),Q(0)]}
    if len(rows)!=7:raise ValueError('sensor count')
    for r,(g,s,t,c) in zip(rows,expected):
        if r['sensor']!=s or Q(r['time'])!=Q(t) or Q(r['cost'])!=Q(c):raise ValueError('sensor/time/cost mismatch')
        if list(map(Q,r['launch']))!=launches[g]:raise ValueError('launch mismatch')
        if len(r['jacobian'])!=3:raise ValueError('Jacobian columns')
        for a in r['jacobian']:iv(a)
        if Q(r['preparation_output_bound'])<0:raise ValueError('negative preparation bound')
    return rows


def evaluate(report,nominal,eta=Q(1,10**7)):
    if eta<0:raise ValueError('negative noise radius')
    rows=verify_inputs(report);nr=verify_inputs(nominal)
    if Q(nominal['parameter_box_radius']) or Q(nominal['preparation_box_radius']):raise ValueError('nominal must be exact input')
    result={}
    for name,shares in [('selected_AB',[Q(2,3),Q(1,3),Q(0)]),('uniform_ABC',[Q(1,3)]*3),('uniform_AB',[Q(1,2),Q(1,2),Q(0)])]:
        costs=[Q(7,2),Q(9,4),Q(5,2)];groups=[0,0,0,1,1,2,2]
        indices=[j for j,g in enumerate(groups) if shares[g]>0]
        w=[shares[groups[j]]/costs[groups[j]] for j in indices]
        a=[[(Q(lo)+Q(hi))/2 for lo,hi in nr[j]['jacobian']] for j in indices]
        atw=[[a[j][i]*w[j] for j in range(len(indices))] for i in range(3)]
        b=matmul(inverse(matmul(atw,a)),atw)
        assert matmul(b,a)==[[Q(int(i==j)) for j in range(3)] for i in range(3)]
        deviations=[[(Q(lo)-a[k][c],Q(hi)-a[k][c]) for c,(lo,hi) in enumerate(rows[j]['jacobian'])] for k,j in enumerate(indices)]
        prod=[[sum_intervals([scale(b[i][k],deviations[k][c]) for k in range(len(indices))]) for c in range(3)] for i in range(3)]
        kr=[sum((maxabs(x) for x in row),Q(0)) for row in prod];kappa=max(kr)
        errors=[Q(rows[j]['preparation_output_bound']) for j in indices]
        eb=[sum((abs(v)*e for v,e in zip(row,errors)),Q(0)) for row in b]
        cn=[sqrt_upper(sum((v*v/wi for v,wi in zip(row,w)),Q(0))) for row in b]
        numer=[2*(e+eta*c) for e,c in zip(eb,cn)]
        cert=kappa<1
        result[name]={'shares':[str(x) for x in shares],'weights':[str(x) for x in w],'indices':indices,'fixed_left_inverse':[[str(x) for x in row] for row in b],'jacobian_deviation_row_bounds':[str(x) for x in kr],'kappa':str(kappa),'kappa_decimal':float(kappa),'preparation_bias_rows':[str(x) for x in eb],'noise_gain_rows':[str(x) for x in cn],'noise_radius':str(eta),'certified':cert,'feasible_set_diameter_inf':str(max(numer)/(1-kappa)) if cert else None,'feasible_set_diameter_decimal':float(max(numer)/(1-kappa)) if cert else None,'physical_pair_error_bound':str(max(numer[:2])+max(kr[:2])*max(numer)/(1-kappa)) if cert else None}
    return result

def sum_intervals(xs):
    s=(Q(0),Q(0))
    for x in xs:s=add(s,x)
    return s

def main():
    ap=argparse.ArgumentParser();ap.add_argument('report');ap.add_argument('nominal');ap.add_argument('--noise',default='1/10000000');ap.add_argument('--output')
    a=ap.parse_args();r=evaluate(json.loads(Path(a.report).read_text()),json.loads(Path(a.nominal).read_text()),Q(a.noise))
    if a.output:
        with Path(a.output).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps({k:{f:v[f] for f in ['kappa_decimal','certified','feasible_set_diameter_decimal']} for k,v in r.items()},indent=2))
if __name__=='__main__':main()
