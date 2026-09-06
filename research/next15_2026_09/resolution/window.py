"""Restricted observation operator: energy loss and centroid certificate."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json
from localization import tail
HERE=Path(__file__).resolve().parent


def build():
    path=HERE/'placement_certificate.json';base=json.loads(path.read_text())
    floors={m:Q(v['floor_lower']) for m,v in base['metrics'].items()}
    mu=Q(56,5);nu=Q(1,1000);half_prior=10;global_depth=490
    for margin in range(12,491):
        lost=2*tail(mu,margin+1)**2
        if any(lost>=f/100 for f in floors.values()):continue
        kept={m:f-lost for m,f in floors.items()}
        if any(kept[m]<=Q(99,100)*Q(base['metrics'][m]['central_floor']) for m in kept):continue
        boundary=8*mu*tail(mu,global_depth)
        truncation=2*mu*tail(mu,margin)*tail(mu,margin+1)
        beta=(boundary+truncation)/kept['L2']
        size=2*(half_prior+margin)+1
        gamma=(size-1)*(2*nu+nu**2)/(1-nu)**2
        if beta+gamma<Q(1,2):break
    else:raise ValueError('no spatial window certificate')
    result={'schema':'transverse-window-v1','placement_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'model':base['model'],'nominal_target':500,'target_indices':[490,510],
            'global_depth':global_depth,'guard_margin':margin,'window_indices':[500-half_prior-margin,500+half_prior+margin],
            'channel_count':size,'relative_output_noise':str(nu),'information_loss_upper':str(lost),
            'boundary_first_moment_upper':str(boundary),'discarded_first_moment_upper':str(truncation),
            'centroid_bias_upper':str(beta),'noise_centroid_shift_upper':str(gamma),'total_centroid_error_upper':str(beta+gamma),
            'metrics':{}}
    for m,c in kept.items():
        eta=Q(3,10**7 if m=='L2' else 10**8)
        assert eta**2<nu**2*c
        result['metrics'][m]={'floor_lower':str(c),'relative_source_noise':str(eta),
                             'relative_source_error_squared_upper':str(eta**2/c)}
    return result


if __name__=='__main__':
    d=build();(HERE/'window_certificate.json').write_text(json.dumps(d,indent=2)+'\n')
    print('channels',d['channel_count'],'window',d['window_indices'],'loss',float(Q(d['information_loss_upper'])))
    print('centroid total',float(Q(d['total_centroid_error_upper'])))
