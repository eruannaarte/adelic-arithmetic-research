"""Exact certificate producer for smaller asymmetric transverse banks."""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial
import argparse, hashlib, json, sys
sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]/'next15_2026_09'/'resolution'

def upward(x, digits=35):
    scale=10**digits
    return Q((x.numerator*scale+x.denominator-1)//x.denominator,scale)

def exp_upper(x):
    """Positive Taylor sum through 160 plus a geometric tail."""
    total=Q(1);term=Q(1)
    for k in range(1,161):
        term*=x/k;total+=term
    term*=x/161
    assert x<162
    return upward(total+term/(1-x/162),40)

def build():
    bpath=BASE/'placement_certificate.json';base=json.loads(bpath.read_text())
    floors={m:Q(v['floor_lower']) for m,v in base['metrics'].items()}
    mu=Q(56,5)
    boundary=8*mu*mu**490/Q(factorial(490))/(1-mu/491)
    boundary_up=Q(1,10**400);assert boundary<boundary_up
    banks=[]
    for lo,hi,a,retain in [(476,525,Q(9,2),Q(99,100)),(477,524,Q(4),Q(97,100))]:
        x=Q(36,5)*(a+1/a-2);ex=exp_upper(x);K=2*ex
        losses=[];moments=[]
        for j in range(490,511):
            rl=j-lo+1;rr=hi-j+1
            losses.append(K*(a**(-2*rl)+a**(-2*rr)))
            moments.append(K*(rl*a**(-2*rl)+rr*a**(-2*rr)))
        loss=upward(max(losses));moment=upward(max(moments));nu=Q(1,1000)
        kept={m:floors[m]-loss*(Q(1) if m=='L2' else Q(1,9)) for m in floors}
        bias=upward((boundary_up+moment)/kept['L2'])
        noise=Q(hi-lo)*(2*nu+nu**2)/(1-nu)**2
        banks.append({'indices':list(range(lo,hi+1)),'channel_count':hi-lo+1,'weight_ratio':str(a),
            'exponent':str(x),'exponential_upper':str(ex),'relative_output_noise':str(nu),
            'energy_loss_L2_upper':str(loss),'discarded_moment_L2_upper':str(moment),
            'retained_central_fraction':str(retain),'centroid_bias_upper':str(bias),
            'noise_centroid_shift_upper':str(noise),'total_centroid_error_upper':str(upward(bias+noise)),
            'metrics':{m:{'floor_lower':str(c),'relative_source_noise':str(Q(3,10**7 if m=='L2' else 10**8)),
                          'relative_source_error_squared_upper':str(upward(Q(9,10**14 if m=='L2' else 10**16)/c))}
                       for m,c in kept.items()}})
    return {'schema':'asymmetric-bank-v1','model':base['model'],'target_indices':[490,510],
            'placement_sha256':hashlib.sha256(bpath.read_bytes()).hexdigest(),
            'boundary_moment_upper':str(boundary_up),'source_metric_lower':{'L2':'1','declared_H1':'9','natural_discrete_H1':'9'},
            'banks':banks,'joint_exact_recovery_necessary_channels':4}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    d=build()
    from check import check
    assert check(d)
    if args.write:(HERE/'evidence.json').write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps({'verified':True,'banks':[{**{k:b[k] for k in ['channel_count','retained_central_fraction']},
        'loss_upper':float(Q(b['energy_loss_L2_upper'])),
        'centroid_error_upper':float(Q(b['total_centroid_error_upper']))} for b in d['banks']]},indent=2))
