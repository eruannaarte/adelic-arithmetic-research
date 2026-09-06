"""Independent full-vector norm/channel replay from exact physical grid."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json,time
from flint import arb,acb,ctx
from physical import PhysicalModel,ball,upper,dyadic,evaluate
from check import check
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def run(bits=384):
    check();doc=json.loads((HERE/'evidence.json').read_text());results=[]
    prior=json.loads((ROOT/'research/transfer_theorem_2026_09/noise/evidence.json').read_text())
    for name in ('multi','outer'):
        start=time.perf_counter();model=PhysicalModel(name,11,bits);built=time.perf_counter()-start
        print('physical inverse reconstructed',name,bits,flush=True)
        app=next(a for a in doc['approximations'] if a['design']==name)
        channels=prior['designs'][name]['physical_polynomials'];norms=[]
        with ctx.workprec(bits):
            for entry in app['approximants']:
                coeff=list(map(ball,entry['rational_polynomial']));k=entry['order'];n2=arb(0)
                for w,x in zip(model.w,model.x):
                    r=x**k-evaluate(coeff,x);n2+=w*r*r
                bound=Q(entry['weighted_residual_norm_upper'])
                if dyadic(n2.upper())>bound*bound:raise ValueError('full weighted residual norm failed')
                norms.append({'order':k,'verified':True})
            for k in (33,34):
                n2=sum((w*x**(2*k) for w,x in zip(model.w,model.x)),arb(0))
                if dyadic(n2.upper())>Q(app['weighted_monomial_norm_upper'][str(k)])**2:raise ValueError('complete Taylor remainder failed')
            # Full X was constructed by a sequential Gram-Schmidt procedure,
            # different from the old moment/parity producer. Recompute every
            # complete zero-extended channel directly from these actual columns.
            for k in range(1,12):
                r=[w*model.X[j,49+k].real for j,w in enumerate(model.w)]
                l1=sum((abs(a) for a in r),arb(0))
                dif1=[r[0]]+[r[j]-r[j-1] for j in range(1,len(r))]+[-r[-1]]
                dif2=[dif1[0]]+[dif1[j]-dif1[j-1] for j in range(1,len(dif1))]+[-dif1[-1]]
                v2=sum((abs(a) for a in dif2),arb(0))
                if upper(l1)>Q(channels['weighted_l1'][k-1][1]):raise ValueError('complete L1 channel bound')
                if upper(v2)>Q(channels['zero_extended_second_difference_l1'][k-1][1]):raise ValueError('complete second difference bound')
                for n in range(1,51):
                    value=model.G[n-1,49+k]
                    scalar=value.imag if k%2 else value.real
                    lo,hi=map(Q,channels['cross_real_even_imaginary_odd'][n-1][k-1])
                    # The old producer records +sin for odd columns; G uses
                    # conjugate(Phi), so its imaginary sign is likewise +sin.
                    if lo==hi==0:
                        if not scalar.contains(0):raise ValueError('exact zero cross channel')
                    elif not lo<=dyadic(scalar.lower())<=dyadic(scalar.upper())<=hi:raise ValueError('arithmetic cross channel')
        results.append({'design':name,'verified':True,'matrix_reconstruction_seconds':built,
            'complete_channel_count':11,'cross_channel_count':550,'weighted_residual_norm_count':21,
            'complete_Taylor_remainder_count':2,'actual_gram_defect_upper':str(model.actual_gram_defect_upper),
            'wall_seconds':time.perf_counter()-start})
    return {'schema':'degree-eleven-model-replay-v1','bits':bits,'verified':True,'designs':results,
        'scope':'Fresh actual 8900-point weights, degree-11 basis and inverse Gram; complete new tail channels and weighted norms. Unchanged original arithmetic tail enumeration remains a hash-bound inherited premise with its previous replay commands.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bits',type=int,default=384);p.add_argument('--record',action='store_true');args=p.parse_args()
    out=run(args.bits)
    if args.record:(HERE/f'model_replay_{args.bits}.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
