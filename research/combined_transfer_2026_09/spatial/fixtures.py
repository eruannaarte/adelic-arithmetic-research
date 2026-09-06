"""Actual finite-model potential perturbations, reconstructed before decoding.

Direct full finite-x exponential reconstruction at the true g and time; complete
periodic-image and boundary radii connect these rational packets to the finite
1001 by 1001 generator. No nominal derivative model generates the observations.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial
import argparse, importlib.util, json, time
from flint import arb,ctx
import check
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_potential_base_kernel',check.PRIOR/'kernel.py')
k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)

def physical_enclosure(g,t):
    nx=1001;x=[k.A(Q(2*i+1,2*nx)) for i in range(nx)]
    ports=[[(arb(2)/nx).sqrt()*(m*arb.pi()*xx).cos() for xx in x] for m in (1,2)]
    out=[[arb(0),arb(0)] for _ in range(27)]
    for mode in range(1,33):
        omega=4*(arb.pi()*mode/64).sin()**2
        center=2+(1+k.A(g)/2)*omega;rad=2+k.A(g)*omega/2
        diagonal=[(1 if i in (0,nx-1) else 2)+omega*(1+k.A(g)*xx)-center for i,xx in enumerate(x)]
        states=[p[:] for p in ports];totals=[p[:] for p in ports]
        for degree in range(1,97):
            states=[[k.A(t)*v/degree for v in k.action(row,diagonal)] for row in states]
            totals=[[a+b for a,b in zip(total,state)] for total,state in zip(totals,states)]
        tail=(-k.A(t)*omega).exp()*(k.A(t)*rad)**97/factorial(97)
        amplitudes=[(-k.A(t)*center).exp()*sum(row,arb(0))/arb(nx).sqrt()+arb(0,tail.upper()) for row in totals]
        for distance in range(27):
            weight=arb(2)/64*(2*arb.pi()*mode*distance/64).cos() if mode<32 else k.A(Q((-1)**distance,64))
            for port in (0,1):out[distance][port]+=weight*amplitudes[port]
    return out

def roundq(v):
    q=check.endpoint(v.mid());s=10**40;return Q((2*q.numerator*s+q.denominator)//(2*q.denominator),s)

def complete_physical_radius():
    # Uniform throughout g0 +/- DG, not only at a floating fixture parameter.
    g=Q(4,5)+check.DG;a=Q(8);v=1+g
    image=check.explimit(2*v*(a+1/a-2))*(a**-38+a**-90)/(1-a**-64)
    rate=4+2*g;mu=2*rate
    boundary=2*mu**491/factorial(491)/(1-mu/492)
    assert Q(16,9)*12*(image+boundary)**2<Q(1,10**44)
    return Q(1,10**22)

def build(bits=256):
    started=time.perf_counter();cases=[];radius=complete_physical_radius()
    pairs=[(nominal,true,sign) for nominal,true in [(Q(1),Q(1)+check.H),(Q(3,2),Q(3,2)-check.H),(Q(3,2),Q(3,2)+check.H),(Q(2),Q(2)-check.H)] for sign in (-1,1)]
    sources=[(490,(Q(3,5),Q(4,5)),Q(1,10**8)),(500,(Q(-4,5),Q(3,5)),Q(1)),(510,(Q(0),Q(1)),Q(10**8))]
    with ctx.workprec(bits):
        for nominal,true,sign in pairs:
            g=Q(4,5)+sign*check.DG;kernel=physical_enclosure(g,true);alpha=(1+k.A(true)).sqrt().sqrt()
            for label,direction,scale in sources:
                source=[scale*x for x in direction];raw=[];errors=[]
                for row in check.BANK:
                    enclosed=alpha*sum((kernel[abs(row-label)][port]*k.A(source[port]) for port in (0,1)),arb(0))
                    fixed=roundq(enclosed);raw.append(fixed);errors.append(check.sup(enclosed-k.A(fixed)))
                quant=check.sqrtupper(sum(e*e for e in errors))/scale
                raw[0]+=check.ETA*scale/4
                total=radius+quant+check.ETA/4
                assert total<check.ETA
                cases.append({'nominal_time':str(nominal),'true_time':str(true),'true_g':str(g),'source_label':label,'source':list(map(str,source)),'source_norm':str(scale),'raw_data':list(map(str,raw)),'sensor_relative_radius':str(check.ETA),'direct_periodic_and_boundary_radius':str(radius),'direct_evaluation_rounding_radius':str(quant),'added_sensor_relative_norm':str(check.ETA/4),'actual_raw_sensor_relative_error_upper':str(total)})
    return {'schema':'combined-six-potential-raw-fixtures-v1','status':'synthetic mathematical observations, not laboratory measurements','generator_family':'H(g)=I_y tensor L_x + L_y tensor diag(1+g*x); exact finite paths each have 1001 vertices','working_precision_bits':bits,'true_g_interval':[str(Q(4,5)-check.DG),str(Q(4,5)+check.DG)],'clock_radius':str(check.H),'bank_rows':list(check.BANK),'case_count':len(cases),'cases':cases,'runtime_seconds':time.perf_counter()-started}

def verify(document,bits=320):
    reconstructed=build(bits)
    for key in ('schema','status','generator_family','true_g_interval','clock_radius','bank_rows','case_count'):
        if document[key]!=reconstructed[key]:raise ValueError('fixture premise mismatch: '+key)
    for saved,new in zip(document['cases'],reconstructed['cases']):
        for key in ('nominal_time','true_time','true_g','source_label','source','source_norm','raw_data','sensor_relative_radius','direct_periodic_and_boundary_radius','added_sensor_relative_norm'):
            if saved[key]!=new[key]:raise ValueError('actual physical fixture differs: '+key)
        if Q(new['direct_evaluation_rounding_radius'])>Q(saved['direct_evaluation_rounding_radius']):raise ValueError('rounding radius not replayed')
        promised=Q(saved['actual_raw_sensor_relative_error_upper'])
        if not promised==Q(saved['direct_periodic_and_boundary_radius'])+Q(saved['direct_evaluation_rounding_radius'])+Q(saved['added_sensor_relative_norm'])<check.ETA:raise ValueError('sensor promise')
    if len(document['cases'])!=len(reconstructed['cases']):raise ValueError('fixture count')
    return {'verified':True,'all_true_parameter_raw_data_reconstructed':True,'case_count':len(reconstructed['cases']),'precision_bits':bits,'runtime_seconds':reconstructed['runtime_seconds']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--replay',action='store_true');p.add_argument('--bits',type=int);a=p.parse_args()
    if a.replay:result=verify(json.loads((HERE/'fixtures.json').read_text()),a.bits or 320);path=HERE/'fixtures_replay.json'
    else:result=build(a.bits or 256);path=HERE/'fixtures.json'
    if a.write:path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
