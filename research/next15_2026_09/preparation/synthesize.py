"""Candidate-only LP decoder synthesis; all published bounds are exact rechecks."""
import argparse,json
from fractions import Fraction as Q
from pathlib import Path
import checker as ch
HERE=Path(__file__).resolve().parent

def synthesize(report,nominal,shares,delta=Q(1,10000),eta=Q(1,10000000)):
    import numpy as np
    from scipy.optimize import linprog
    if delta<=0 or eta<0:raise ValueError('invalid target or noise')
    d=ch.ingredients(report,nominal,shares);rho=Q(report['preparation_box_radius']);rows=report['rows'];idx=d['indices'];m=len(idx)
    # Midpoint/radius decompositions are exact, not floating source intervals.
    dm=[];dr=[];pm=[];pr=[]
    for k,j in enumerate(idx):
        jiv=[ch.iv(x) for x in rows[j]['jacobian']]
        dm.append([(lo+hi)/2-d['a'][k][c] for c,(lo,hi) in enumerate(jiv)]);dr.append([(hi-lo)/2 for lo,hi in jiv])
        pfull=[ch.iv(rows[j]['preparation_jacobian'][c]) if g==ch.GROUPS[j] else (Q(0),Q(0)) for g in range(3) for c in range(4)]
        pm.append([(lo+hi)/2 for lo,hi in pfull]);pr.append([(hi-lo)/2 for lo,hi in pfull])
    # t bounds absolute projected centers; z bounds absolute row coefficients.
    tt=[r+s for r,s in zip(dm,pm)];nt=15
    cb=[delta*sum(r,Q(0))+2*rho*sum(q,Q(0))+2*eta*ch.sqrt_upper(1/w) for r,q,w in zip(dr,pr,d['weights'])]
    objective=[0.]*m+[float(delta)]*3+[float(2*rho)]*12+[float(x) for x in cb]
    inequalities=[]
    for c in range(nt):
        for sign in [-1,1]:
            a=[sign*float(tt[k][c]) for k in range(m)]+[0.]*(nt+m);a[m+c]=-1.;inequalities.append(a)
    for j in range(m):
        for sign in [-1,1]:
            a=[0.]*(m+nt+m);a[j]=sign;a[m+nt+j]=-1.;inequalities.append(a)
    equalities=[[float(x) for x in col]+[0.]*(nt+m) for col in zip(*d['a'])]
    out=[];diagnostic=[]
    # Rescaling the objective helps HiGHS with tiny physical tolerances.
    for i in range(3):
        sol=linprog(np.array(objective)/float(delta),A_ub=inequalities,b_ub=np.zeros(len(inequalities)),A_eq=equalities,b_eq=np.eye(3)[i],bounds=[(None,None)]*m+[(0,None)]*(nt+m),method='highs')
        if not sol.success:raise RuntimeError(sol.message)
        b=[Q(float(x)).limit_denominator(10**8) for x in sol.x[:m]]
        residual=[Q(int(i==c))-sum((b[j]*d['a'][j][c] for j in range(m)),Q(0)) for c in range(3)]
        fixed=[b[j]+sum((residual[c]*d['b'][c][j] for c in range(3)),Q(0)) for j in range(m)]
        out.append(fixed);diagnostic.append({'candidate_lp_objective':sol.fun*float(delta),'success':bool(sol.success)})
    exact=ch.ingredients(report,nominal,shares,out);bound=ch.scalar_bound(exact,rho,eta)
    values=[delta*sum(r,Q(0))+2*(rho*sum(h,Q(0))+eta*c) for r,h,c in zip(exact['R'],exact['H'],exact['noise'])]
    return {'shares':list(shares),'ingredients':exact,'bound':bound,'target':delta,'target_row_lhs':values,'target_passes':all(x<=delta for x in values) and bound['kappa']<1,'candidate_diagnostics':diagnostic}

def build(report,nominal,delta=Q(1,10000),eta=Q(1,10000000)):
    return ch.encode({'schema':'preparation-aware-decoder-v1','rho':Q(report['preparation_box_radius']),'eta':eta,'source_radius':Q(report['parameter_box_radius']),'target':delta,'designs':{name:synthesize(report,nominal,shares,delta,eta) for name,shares in ch.DESIGNS.items()},'least_squares':ch.evaluate(report,nominal,eta)})

def verify(report,nominal,doc):
    if doc['schema']!='preparation-aware-decoder-v1':raise ValueError('schema')
    rho=Q(report['preparation_box_radius']);eta=Q(doc['eta']);delta=Q(doc['target'])
    if Q(doc['rho'])!=rho or Q(doc['source_radius'])!=Q(report['parameter_box_radius']) or eta<0 or delta<=0:raise ValueError('source/uncertainty binding')
    if set(doc['designs'])!=set(ch.DESIGNS):raise ValueError('design set')
    for name,v in doc['designs'].items():
        shares=ch.DESIGNS[name]
        if list(map(Q,v['shares']))!=shares:raise ValueError('budget shares')
        d=ch.ingredients(report,nominal,shares,v['ingredients']['b']);b=ch.scalar_bound(d,rho,eta)
        if ch.encode(d)!=v['ingredients'] or ch.encode(b)!=v['bound']:raise ValueError('consequences mismatch')
        lhs=[delta*sum(r,Q(0))+2*(rho*sum(h,Q(0))+eta*c) for r,h,c in zip(d['R'],d['H'],d['noise'])]
        if v['target']!=str(delta) or v['target_row_lhs']!=ch.encode(lhs) or v['target_passes']!=(all(x<=delta for x in lhs) and b['kappa']<1):raise ValueError('target mismatch')
    if doc['least_squares']!=ch.evaluate(report,nominal,eta):raise ValueError('least squares comparison')
    return True

def main():
    ap=argparse.ArgumentParser();ap.add_argument('report');ap.add_argument('nominal');ap.add_argument('--output');ap.add_argument('--verify')
    a=ap.parse_args();r=json.loads(Path(a.report).read_text());n=json.loads(Path(a.nominal).read_text())
    if a.verify:print('PASS' if verify(r,n,json.loads(Path(a.verify).read_text())) else 'FAIL');return
    doc=build(r,n)
    if a.output:
        with Path(a.output).open('x') as f:json.dump(doc,f,indent=2);f.write('\n')
    print(json.dumps({k:{'target_passes':v['target_passes'],'diameter':float(Q(v['bound']['diameter'])),'kappa':float(Q(v['bound']['kappa']))} for k,v in doc['designs'].items()},indent=2))
if __name__=='__main__':main()
