"""Independent outward consumer: centered composition rather than producer Horner.

The kernel replay supplies interval premises; this consumer rebuilds the
continuous-time directional bounds and verifies the complete remainder gates.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial,isqrt
import argparse, hashlib, json, time
from flint import arb, arb_poly, ctx, fmpq
HERE=Path(__file__).resolve().parent
PRIOR=HERE.parents[1]/'transfer_theorem_2026_09/resolution'
BANK=(485,493,499,501,507,515)
H=DG=Q(1,10**8);ETA=Q(3,10**8);RHO=XI=Q(1,10**9)
MU=Q(361,256*10**9);LABEL_RADIUS=Q(13,400000000)
LIMITS={'joint_forward':Q(43,10**11),'joint_inverse':Q(68,10**8),'time_forward':Q(23,1000),'potential_forward':Q(22,1000),'time_inverse':Q(46),'potential_inverse':Q(23)}

def require(ok,message):
    if not ok:raise ValueError(message)
def A(q):
    q=Q(q);return arb(fmpq(q.numerator,q.denominator))
def endpoint(v):
    require(v.is_finite() and v.is_exact(),'finite endpoint required')
    m,e=map(int,v.man_exp());return Q(m*2**e) if e>=0 else Q(m,2**(-e))
def sup(v):return endpoint(abs(v).upper())
def sqrtupper(q):
    q=Q(q);s=10**40;k=isqrt(q.numerator*s*s//q.denominator)
    return Q(k+(Q(k,s)**2<q),s)
def explimit(x):return sum((x**k/factorial(k) for k in range(201)),Q())+x**201/factorial(201)/(1-x/202)
def kernel(path,derivative=False):
    d=json.loads(path.read_text());out=[]
    if derivative:
        require(d['schema']=='potential-derivative-kernel-v1','derivative schema')
        require(d['model']=={'nx':1001,'period':64,'g':'4/5','center':'3/2','order':32,'exponential_degree':80,'maximum_distance':26,'source_modes':[1,2]},'derivative model')
    require(d['coefficient_export_grid']=='1/1000000000000000000000000000000','kernel coefficient grid')
    require(len(d['coefficient_intervals'])==27,'displacements')
    for distance in d['coefficient_intervals']:
        require(len(distance)==2,'source dimension');out.append([])
        for row in distance:
            require(len(row)==33,'Taylor degree');values=[]
            for box in row:
                require(type(box) is list and len(box)==2 and all(type(z)is str for z in box),'exact coefficient interval')
                lo,hi=map(Q,box);require(0<=hi-lo<=Q(1,10**30),'coefficient width');values.append((lo+hi)/2)
            out[-1].append(values)
    return out

def remainders():
    # Full spatial-image tails, not a finite image truncation.
    a=Q(8);V=Q(9,5);image=explimit(2*V*(a+1/a-2))*(a**-38+a**-90)/(1-a**-64)
    require(image<Q(1,10**24),'complete periodic-image remainder')
    gimage=2*(2+a+1/a)*image
    timage=(4+V*(2+a+1/a))*image
    q=Q(28,5);mu=2*q
    boundary=2*mu**491/factorial(491)/(1-mu/492)
    gboundary=16*mu**490/factorial(490)/(1-mu/491)
    tboundary=4*q*mu**490/factorial(490)/(1-mu/491)
    require(max(boundary,gboundary,tboundary)<Q(1,10**490),'complete finite-boundary remainder')
    # Cauchy at complex time |z-3/2|=3/2. Semigroup norm <=1;
    # potential derivative <= |z| ||D|| <=12 throughout the circle.
    taylor=Q(1,2*3**32)
    gtaylor=Q(6,3**32)
    ttaylor=Q(67,2*3**32)
    e0=taylor+image+boundary+Q(2,10**30)
    eg=gtaylor+gimage+gboundary+Q(2,10**30)
    et=ttaylor+timage+tboundary+Q(4,10**30)
    dg_squared=Q(16,9)*12*eg**2
    dt_squared=12*(e0/6+Q(4,3)*et)**2
    derivative_error=Q(1,10**12)
    require(max(dg_squared,dt_squared)<derivative_error**2,'complete derivative approximation error')
    require(Q(4,3)**4>3 and Q(3,2)**4<8 and 2**7>3**4,'normalization derivative bounds')
    # The sequential expansion only needs A_tg at g0. A slightly larger
    # bound also controls the entire parameter rectangle without ambiguity.
    require(Q(56,5)+4*DG<Q(45,4),'generator norm throughout potential rectangle')
    require(Q(1,6)*8+Q(4,3)*(4+Q(45,4)*8)==Q(380,3)<128,'mixed derivative bound')
    require(Q(1,16)+2*Q(1,6)*Q(3,8)+Q(4,3)*Q(9,16)==Q(15,16)<1,'second time derivative bound')
    # ||A_tt|| <= 15/16 <1; ||A_tg|| <128; potential Duhamel Hessian <=256/3.
    remainder=H**2/2+128*H*DG+Q(128,3)*DG**2+(H+DG)*derivative_error
    return {'derivative_operator_error_upper':str(derivative_error),'clock_second_order_radius':str(H**2/2),'clock_potential_cross_radius':str(128*H*DG),'potential_second_order_radius':str(Q(128,3)*DG**2),'derivative_approximation_radius':str((H+DG)*derivative_error),'total_nonlinear_radius':str(remainder),'complete_periodic_and_boundary_tails':True,'g_derivative_operator_error_squared':str(dg_squared),'time_derivative_operator_error_squared':str(dt_squared)}

def consequence(bounds=None,h=H,dg=DG):
    require(type(h) in (Q,int,str) and type(dg) in (Q,int,str),'exact uncertainty radii required')
    require(Q(h)==H and Q(dg)==DG,'fixed certified rectangle required')
    b=LIMITS if bounds is None else bounds
    require(set(b)==set(LIMITS) and all(type(b[k]) in (Q,int,str) and Q(b[k])==LIMITS[k] for k in LIMITS),'fixed certified directional limits required')
    b={k:Q(b[k]) for k in LIMITS}
    rem=remainders();r=Q(rem['total_nonlinear_radius'])
    free=ETA+RHO+XI+r
    total=free+b['joint_forward']
    require(total<LABEL_RADIUS,'enlarged weighted-pair label tube gate')
    remainder_gain=sqrtupper(free*free/MU)
    accuracy=remainder_gain+b['joint_inverse']
    require(accuracy<Q(1,1000),'directional source gate')
    unstructured=sqrtupper(total*total/MU)
    require(Q(4,5)-DG>=0,'entire physical potential family PSD')
    return {'verified':True,'sensor_relative_radius':str(ETA),'clock_radius':str(H),'potential_radius':str(DG),'source_relative_accuracy_target':'1/1000','source_relative_error_upper':str(accuracy),'label_total_relative_radius':str(total),'certified_label_tube_radius':str(LABEL_RADIUS),'source_floor':str(MU),'structured_direction_radius':str(b['joint_forward']),'structured_inverse_radius':str(b['joint_inverse']),'unstructured_remainder_radius':str(free),'global_inverse_source_error_upper':str(unstructured),'global_inverse_gate_also_passes':unstructured<Q(1,1000),'label_separation_verified':True,'source_accuracy_verified':True,'remainders':rem}

def verify(document=None,bits=320):
    started=time.perf_counter();doc=json.loads((HERE/'directions.json').read_text()) if document is None else document
    require(doc['schema']=='spatial-structured-directions-v1' and doc['bank_rows']==list(BANK),'direction schema and bank')
    require(doc['nominal_g']=='4/5' and doc['time_interval']==['1','2'],'physical parameter/time premise')
    require(doc['clock_radius']==str(H) and doc['potential_radius']==str(DG),'fixed uncertainty rectangle')
    require(type(doc['subdivisions'])is int and doc['subdivisions']==128,'time partition')
    require(len(doc['records'])==21*128,'all-target/time cover')
    for path in (PRIOR/'kernel.json',HERE.parents[1]/'structured_transfer_2026_09/resolution/kernel_derivative.json'):
        require(doc['premise_sha256'][str(path.relative_to(HERE.parents[2]))]==hashlib.sha256(path.read_bytes()).hexdigest(),'kernel binding')
    require(set(doc['global_bounds'])==set(LIMITS),'global bounds shape')
    require(all(type(doc['global_bounds'][k]) is str and 0<Q(doc['global_bounds'][k])<=LIMITS[k] for k in LIMITS),'stored global bound')
    with ctx.workprec(bits):
        p=kernel(PRIOR/'kernel.json');q=kernel(HERE.parents[1]/'structured_transfer_2026_09/resolution/kernel_derivative.json',True)
        observed={k:Q() for k in LIMITS};counter=0
        for target in range(490,511):
            P=[[arb_poly([A(c) for c in p[abs(sensor-target)][i]]) for i in (0,1)] for sensor in BANK]
            V=[[arb_poly([A(c) for c in q[abs(sensor-target)][i]]) for i in (0,1)] for sensor in BANK]
            a=sum((r[0]**2 for r in P),arb_poly());b=sum((r[0]*r[1] for r in P),arb_poly());c=sum((r[1]**2 for r in P),arb_poly())
            determinant=a*c-b*b
            inverse_products=[]
            for matrix in ([[v.derivative() for v in row] for row in P],V):
                rhs=[[sum((pr[i]*dr[j] for pr,dr in zip(P,matrix)),arb_poly()) for j in (0,1)] for i in (0,1)]
                inverse_products.append([[c*rhs[0][j]-b*rhs[1][j] for j in (0,1)],[-b*rhs[0][j]+a*rhs[1][j] for j in (0,1)]])
            for cell in range(128):
                lo=Q(1)+Q(cell,128);hi=lo+Q(1,128);center=(lo+hi)/2;radius=(hi-lo)/2
                record=doc['records'][counter];counter+=1
                require(record['target']==target and record['time_cell']==[str(lo),str(hi)],'separate target/time cover')
                require(set(record['bounds'])==set(LIMITS) and all(type(record['bounds'][k]) is str and 0<Q(record['bounds'][k])<=Q(doc['global_bounds'][k]) for k in LIMITS),'record bounds')
                zc=A(center-Q(3,2));r=A(radius)
                def evaluate(poly):
                    translated=poly(arb_poly([zc,arb(1)]))
                    rem=sum((abs(translated[n]).upper()*r**n for n in range(1,len(translated))),arb(0))
                    return translated[0]+arb(0,rem.upper())
                t=A(center)+arb(0,r);beta=1/(4*(1+t));alpha=(1+t).sqrt().sqrt();det=evaluate(determinant)
                require(det>0,'positive nominal Gram throughout cell')
                Ti=[[evaluate(inverse_products[0][i][j])/det+beta*int(i==j) for j in (0,1)] for i in (0,1)]
                Gi=[[evaluate(inverse_products[1][i][j])/det for j in (0,1)] for i in (0,1)]
                Tf=[[alpha*(evaluate(v.derivative())+beta*evaluate(v)) for v in row] for row in P]
                Gf=[[alpha*evaluate(v) for v in row] for row in V]
                def fn(matrix):return sum((abs(v).upper()**2 for row in matrix for v in row),arb(0)).sqrt()
                result={'time_forward':fn(Tf),'potential_forward':fn(Gf),'time_inverse':fn(Ti),'potential_inverse':fn(Gi)}
                for label,tm,gm in (('forward',Tf,Gf),('inverse',Ti,Gi)):
                    result['joint_'+label]=A(max(sup(fn([[A(H)*x+s*A(DG)*y for x,y in zip(trow,grow)] for trow,grow in zip(tm,gm)])) for s in (-1,1)))
                for key,value in result.items():
                    observed[key]=max(observed[key],sup(value))
                    require(sup(value)<=Q(record['bounds'][key]),f'recorded whole-cell {key} bound')
                    require(sup(value)<LIMITS[key],f'whole-cell {key} limit')
        import certify
        pair_check=certify.check()
        result=consequence()
        result['weighted_pair_certificate']=pair_check
        result.update({'independent_centered_consumer_verified':True,'case_cells':counter,'precision_bits':bits,'consumer_global_bounds':{k:str(v) for k,v in observed.items()},'certified_direction_limits':{k:str(v) for k,v in LIMITS.items()},'runtime_seconds':time.perf_counter()-started})
        return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--bits',type=int,default=320);a=p.parse_args()
    result=verify(bits=a.bits)
    if a.write:(HERE/'checked.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('remainders','consumer_global_bounds')},indent=2))
