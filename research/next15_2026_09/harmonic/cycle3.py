"""An interval contraction proof of an interior raw-harmonic collision."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json
from flint import arb,acb,arb_mat,ctx
from cycle1 import ball,endpoint,enclosure
from cycle2 import TIMES

HERE=Path(__file__).resolve().parent

def coefficients():
    return [[[acb(0,-ball(t)*a*arb(p).log()).exp() for a in range(4)] for p in (2,3,5)] for t in TIMES]

def sources(x):
    out=[]
    for side in range(2):
        q=[]
        for j in range(3):
            z=x[9*side+3*j:9*side+3*j+3]
            q.append([1-sum(z,arb(0)),*z])
        out.append(q)
    return out

def response_and_jacobian(x,E,active):
    q,r=sources(x);values=[];jac=[]
    for row in E:
        chars=[[sum((a*b for a,b in zip(row[j],p[j])),acb(0)) for j in range(3)] for p in (q,r)]
        values.append(chars[0][0]*chars[0][1]*chars[0][2]-chars[1][0]*chars[1][1]*chars[1][2])
        columns=[]
        for side in range(2):
            for j in range(3):
                other=[k for k in range(3) if k!=j]
                z=chars[side][other[0]]*chars[side][other[1]]*(1 if side==0 else -1)
                columns.extend(z*(row[j][a]-row[j][0]) for a in range(1,4))
        jac.append([columns[k] for k in active])
    F=[x.real for x in values]+[x.imag for x in values]
    J=[[x.real for x in row] for row in jac]+[[x.imag for x in row] for row in jac]
    return F,J

def proposal():
    discovery=json.loads((HERE/'cycle3_discovery.json').read_text())
    return {'times':list(map(str,TIMES)),'coordinates':discovery['coordinates'],
            'active':discovery['active'],'radius':'1/1000000000',
            'minimum_probability_claim':'7/100','separation_claim':'79/100'}

def build(inputs,precision=256):
    if inputs['times']!=list(map(str,TIMES)):raise ValueError('wrong frozen schedule')
    coordinates=list(map(Q,inputs['coordinates']));active=inputs['active'];rho=Q(inputs['radius'])
    if len(coordinates)!=18 or len(active)!=12 or len(set(active))!=12 or any(type(i) is not int or not 0<=i<18 for i in active) or rho<=0:
        raise ValueError('invalid collision box')
    probclaim=Q(inputs['minimum_probability_claim']);sepclaim=Q(inputs['separation_claim'])
    if probclaim<=0 or sepclaim<=0:raise ValueError('positive source/separation claims required')
    with ctx.workprec(precision):
        E=coefficients();x=[ball(a) for a in coordinates]
        F,J=response_and_jacobian(x,E,active)
        approx=arb_mat(J).inv()
        # Any rational preconditioner is permitted; its interval contraction
        # gate, not its origin as an approximate inverse, is the proof.
        R=[[Q(round(endpoint(approx[i,j].mid())*10**12),10**12) for j in range(12)] for i in range(12)]
        box=[arb(v,ball(rho)) if k in active else v for k,v in enumerate(x)]
        _,JB=response_and_jacobian(box,E,active)
        residual=arb_mat([[ball(v) for v in row] for row in R])*arb_mat([[v] for v in F])
        product=arb_mat([[ball(v) for v in row] for row in R])*arb_mat(JB)
        row_bounds=[]
        for i in range(12):
            row_bounds.append(sum((endpoint((arb(int(i==j))-product[i,j]).abs_upper()) for j in range(12)),Q()))
        L=max(row_bounds);e=max(endpoint(residual[i,0].abs_upper()) for i in range(12))
        if not L<1 or not e+L*rho<rho:raise ValueError('strict contraction/self-map gate failed')
        q,r=sources(box)
        plower=min(endpoint(v.lower()) for side in (q,r) for row in side for v in row)
        # Difference boxes are narrow and may include zero; Arb squaring still
        # encloses every real squared coordinate difference.
        d2=sum(((a-b)**2 for qa,ra in zip(q,r) for a,b in zip(qa,ra)),arb(0))
        dlower=endpoint(d2.lower())
        if not plower>probclaim or not dlower>sepclaim**2:raise ValueError('admissibility/distinctness gate failed')
        return {'schema':'harmonic-cycle3-v1','inputs':inputs,
                'rational_preconditioner':[[str(v) for v in row] for row in R],
                'contraction_row_bounds':[enclosure(ball(v))[1] for v in row_bounds],
                'contraction_norm_upper':enclosure(ball(L))[1],
                'preconditioned_residual_upper':str(e),
                'self_map_radius_upper':str(e+L*rho),'box_radius':str(rho),
                'minimum_probability_lower':enclosure(ball(plower))[0],
                'factor_distance_squared_lower':enclosure(ball(dlower))[0],
                'strict_gates_pass':True,'conclusion':'two distinct strictly interior product distributions have exactly equal six raw complex responses'}

def check(precision=256):
    inputs=json.loads((HERE/'cycle3_inputs.json').read_text());saved=json.loads((HERE/'cycle3_evidence.json').read_text());fresh=build(inputs,precision)
    # Very small exact residual endpoints depend on precision; the proof gates
    # must independently pass and displayed enclosing claims must agree.
    if precision==256:
        if fresh!=saved:raise ValueError('complete interval collision replay mismatch')
    else:
        for k in ('inputs','rational_preconditioner','contraction_row_bounds','contraction_norm_upper','minimum_probability_lower','factor_distance_squared_lower','strict_gates_pass','conclusion'):
            if fresh[k]!=saved[k]:raise ValueError('refinement mismatch: '+k)
    return fresh

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--precision',type=int,default=256);a=p.parse_args()
    if a.write:
        inputs=proposal();(HERE/'cycle3_inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
        (HERE/'cycle3_evidence.json').write_text(json.dumps(build(inputs,a.precision),indent=2)+'\n')
    d=check(a.precision);print('Cycle3 PASS: strict interval contraction proves an interior exact collision')
    print(json.dumps({k:d[k] for k in ('contraction_norm_upper','minimum_probability_lower','factor_distance_squared_lower','box_radius','conclusion')},indent=2))
