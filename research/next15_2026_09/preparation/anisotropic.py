"""Finite calibration-box design and exact AM--GM volume certificates."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json,math
import checker as ch
import synthesize
HERE=Path(__file__).resolve().parent

def model(report,nominal,decoders,name,delta,eta):
    if name not in ('selected_AB','uniform_AB'):raise ValueError('equal-access A+B comparison only')
    d=ch.ingredients(report,nominal,ch.DESIGNS[name],decoders['designs'][name]['ingredients']['b'])
    cap=Q(report['preparation_box_radius']);R=d['R'];H=[r[:8] for r in d['H']]
    if any(any(x for x in r[8:]) for r in d['H']):raise ValueError('unexpected preparation incidence')
    k=[sum(r,Q(0)) for r in R]
    if max(k)>=1:raise ValueError('contraction')
    budgets=[(delta*(1-ki)-2*eta*ci)/2 for ki,ci in zip(k,d['noise'])]
    if min(budgets)<=0:raise ValueError('noise exceeds certificate')
    # Dimensionless radii x_j=rho_j/cap; exact feasible set Gx <= 1, 0<x<=1.
    G=[[cap*h/b for h in row] for row,b in zip(H,budgets)]
    return d,G,cap

def exact_certificate(G,cap,x,lam,mu):
    n=8;x=list(map(Q,x));lam=list(map(Q,lam));mu=list(map(Q,mu))
    if cap<=0 or len(G)!=3 or any(len(row)!=n for row in G) or any(q<0 for row in G for q in row):raise ValueError('invalid calibration matrix/cap')
    if len(x)!=n or len(lam)!=3 or len(mu)!=n:raise ValueError('certificate dimension')
    if not all(0<t<=1 for t in x):raise ValueError('outer-box cap or zero radius')
    if min(lam+mu)<0:raise ValueError('negative dual')
    loads=[sum((a*b for a,b in zip(row,x)),Q(0)) for row in G]
    if max(loads)>1:raise ValueError('calibration half-plane violated')
    a=[sum((lam[i]*G[i][j] for i in range(3)),Q(0))+mu[j] for j in range(n)]
    if min(a)<=0:raise ValueError('AM-GM weights must be positive')
    C=sum(lam+mu,Q(0));V=math.prod(x);U=(C/n)**n/math.prod(a)
    if V>U:raise ValueError('inconsistent dual upper bound')
    isotropic=min([Q(1)]+[1/sum(row,Q(0)) for row in G if sum(row,Q(0))>0])
    return {'normalized_radii':x,'physical_radii':[cap*t for t in x],'normalized_constraint_loads':loads,'dual_lambda':lam,'dual_mu':mu,'dual_coordinate_weights':a,'dual_total_budget':C,'normalized_volume':V,'normalized_volume_upper_bound':U,'volume_ratio_lower_bound':V/U,'isotropic_normalized_radius':isotropic,'volume_gain_over_isotropic':V/isotropic**n,'geometric_mean_at_least_8e6':V*cap**n>=Q(8,10**6)**n,'volume_within_one_per_mille_of_optimal':V*1000>=U*999}

def candidate(G,cap):
    import numpy as np
    from scipy.optimize import minimize,nnls
    gf=np.array([[float(x) for x in row] for row in G]);x0=np.repeat(min(1.,min(1/gf.sum(axis=1)))*.95,8)
    sol=minimize(lambda x:-np.log(x).sum(),x0,jac=lambda x:-1/x,bounds=[(1e-8,1)]*8,constraints=[{'type':'ineq','fun':lambda x:1-gf@x,'jac':lambda x:-gf}],method='SLSQP',options={'ftol':1e-13,'maxiter':1000})
    if not sol.success and np.max(gf@sol.x)>1+1e-8:raise RuntimeError(sol.message)
    # Downward rounding and exact common contraction ensure primal feasibility.
    x=[Q(max(1,min(10**10,math.floor(t*10**10))),10**10) for t in sol.x]
    load=max(sum((a*b for a,b in zip(row,x)),Q(0)) for row in G)
    if load>1:x=[t/load for t in x]
    # Fit nonnegative multipliers on the observed active faces; any nonnegative
    # rational multipliers give a valid upper bound, regardless of this fit.
    active=[('row',i) for i,l in enumerate(gf@sol.x) if l>1-1e-7]+[('cap',j) for j,t in enumerate(sol.x) if t>1-1e-7]
    columns=[gf[i] if typ=='row' else np.eye(8)[i] for typ,i in active]
    coeff,_=nnls(np.array(columns).T,1/sol.x)
    lam=[Q(0)]*3;mu=[Q(0)]*8
    for (typ,i),v in zip(active,coeff):
        q=Q(float(v)).limit_denominator(10**8)
        if typ=='row':lam[i]=q
        else:mu[i]=q
    cert=exact_certificate(G,cap,x,lam,mu)
    cert['candidate_diagnostics']={'optimizer_success':bool(sol.success),'message':str(sol.message),'active_faces':active}
    return cert

def build(report,nominal,decoders,delta=Q(1,10000),eta=Q(1,10000000)):
    synthesize.verify(report,nominal,decoders);designs={}
    for name in ['selected_AB','uniform_AB']:
        d,G,cap=model(report,nominal,decoders,name,delta,eta)
        designs[name]={'shares':ch.DESIGNS[name],'constraints_G':G,'outer_preparation_radius':cap,'certificate':candidate(G,cap)}
    return ch.encode({'schema':'anisotropic-calibration-volume-v1','source_radius':Q(report['parameter_box_radius']),'target':delta,'noise':eta,'coordinates':['A.theta1','A.theta2','A.omega1','A.omega2','B.theta1','B.theta2','B.omega1','B.omega2'],'designs':designs})

def verify(report,nominal,decoders,doc):
    synthesize.verify(report,nominal,decoders)
    if doc['schema']!='anisotropic-calibration-volume-v1' or doc['source_radius']!=report['parameter_box_radius']:raise ValueError('source binding')
    if doc['coordinates']!=['A.theta1','A.theta2','A.omega1','A.omega2','B.theta1','B.theta2','B.omega1','B.omega2']:raise ValueError('coordinate contract')
    if set(doc['designs'])!={'selected_AB','uniform_AB'}:raise ValueError('design set')
    delta=Q(doc['target']);eta=Q(doc['noise'])
    if delta<=0 or eta<0:raise ValueError('invalid uncertainty')
    for name,v in doc['designs'].items():
        d,G,cap=model(report,nominal,decoders,name,delta,eta)
        if v['constraints_G']!=ch.encode(G) or v['outer_preparation_radius']!=str(cap) or v['shares']!=ch.encode(ch.DESIGNS[name]):raise ValueError('finite constraints binding')
        c=v['certificate'];fresh=exact_certificate(G,cap,c['normalized_radii'],c['dual_lambda'],c['dual_mu']);saved=dict(c);saved.pop('candidate_diagnostics')
        if ch.encode(fresh)!=saved:raise ValueError('primal/dual consequences mismatch')
    return True

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--verify');ap.add_argument('--output');a=ap.parse_args()
    load=lambda n:json.loads((HERE/n).read_text());r=load('cycle2_region.json');n=load('nominal.json');c=load('cycle2_certificate.json')
    if a.verify:print('PASS' if verify(r,n,c,json.loads(Path(a.verify).read_text())) else 'FAIL');return
    out=build(r,n,c)
    if a.output:
        with Path(a.output).open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({k:{'radii':[float(Q(t)) for t in v['certificate']['physical_radii']],'ratio':float(Q(v['certificate']['volume_ratio_lower_bound'])),'volume_gain':float(Q(v['certificate']['volume_gain_over_isotropic'])),'geometric_mean':float(Q(v['certificate']['normalized_volume']))**(1/8)*float(Q(v['outer_preparation_radius']))} for k,v in out['designs'].items()},indent=2))
if __name__=='__main__':main()
