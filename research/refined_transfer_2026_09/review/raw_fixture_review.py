"""Independent exact scan of raw physical fixtures and their error claims.

No fixture generator, normalizer, or decoder is imported. Polynomial values
use direct powers. This reuses the established complete model-error premise;
it does not rerun the spatial kernel or all-time lower-floor reconstruction.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BANKS={'7':(-12,-10,-3,0,4,8,10),
       '8':(-12,-10,-6,-2,2,6,10,14),
       '9':(-15,-12,-8,-4,0,4,8,12,16)}
PROFILES={('7','L2'):Q(1,10**7),('8','L2'):Q(23,10**8),
          ('8','L2_original_noise'):Q(3,10**7),('9','L2'):Q(3,10**7),
          **{(b,p):Q(3,10**8) for b in ('8','9') for p in ('declared_H1','natural_discrete_H1')}}


def digest(values):
    return hashlib.sha256(json.dumps(list(map(str,values)),separators=(',',':')).encode()).hexdigest()


def run():
    doc=json.loads((HERE.parent/'normalization/evidence.json').read_text())
    kernel=json.loads((ROOT/'research/transfer_theorem_2026_09/resolution/kernel.json').read_text())
    coeff=[[[sum(map(Q,box))/2 for box in row] for row in d] for d in kernel['coefficient_intervals']]
    expected={(b,p,t,label) for b,p in PROFILES for t in (Q(1),Q(3,2),Q(2)) for label in (490,500,510)}
    seen=set();max_sensor_fraction=Q(0);max_error=Q(0);max_charge=Q(0)
    for row in doc['cases']:
        bank,profile,t,label=row['bank'],row['profile'],Q(row['time']),row['source_label']
        key=(bank,profile,t,label)
        assert key in expected and key not in seen;seen.add(key)
        eta=PROFILES[bank,profile];rho=Q(1,10**9);xi=rho
        u=tuple(map(Q,row['source']));scale=Q(row['source_norm_scale'])
        assert scale>0 and sum(v*v for v in u)==scale*scale
        assert scale=={490:Q(1,10**40),500:Q(1),510:Q(10**40)}[label]
        y=tuple(map(Q,row['raw_readings']));assert len(y)==len(BANKS[bank])
        generation=row['raw_sensor_promise'];r=Q(generation['generation_inverse_normalization'])
        e=Q(generation['generation_multiplier_error_upper'])
        assert r>0 and 0<=e<1 and (1-e)**4<=(1+t)*r**4<=(1+e)**4
        assert Q(4,3)+rho<2*Q(19,16)
        charge=rho+2*e/r+eta/4
        assert charge==Q(generation['actual_raw_sensor_relative_error_upper']) and charge<eta
        max_sensor_fraction=max(max_sensor_fraction,charge/eta)
        powers=[(t-Q(3,2))**k for k in range(33)]
        matrix=[[sum(c*p for c,p in zip(coeff[abs(sensor-(label-500))][port],powers))
                 for port in (0,1)] for sensor in BANKS[bank]]
        expected_raw=[sum(a*b for a,b in zip(p,u))/r for p in matrix]
        expected_raw[0]+=eta*scale/4
        assert tuple(expected_raw)==y

        packet=row['normalization'];receipt=packet['scale']
        assert receipt['schema']=='physical-normalization-scale-v1'
        assert Q(receipt['time'])==t and Q(receipt['sensor_relative_radius'])==eta
        assert Q(receipt['numerical_relative_budget'])==xi
        rr,ee=Q(receipt['inverse_normalization']),Q(receipt['relative_multiplier_error_upper'])
        kk=Q(receipt['measured_output_gain_upper'])
        assert kk==Q(4,3)+eta and rr>0 and 0<=ee<1
        assert (1-ee)**4<=(1+t)*rr**4<=(1+ee)**4
        cc=Q(receipt['charged_physical_relative_radius'])
        assert cc==kk*ee and 0<=cc<=xi;max_charge=max(max_charge,cc)
        z=tuple(map(Q,packet['normalized_data']))
        assert z==tuple(rr*v for v in y)
        assert packet['raw_data_sha256']==digest(y) and packet['normalized_data_sha256']==digest(z)

        # Derive the ordinary exact source estimate afresh from the normalized
        # readings. Feasibility uniqueness uses the independently proved global
        # pair theorem and the just-verified actual raw sensor promise.
        g00=sum(p[0]*p[0] for p in matrix);g01=sum(p[0]*p[1] for p in matrix)
        g11=sum(p[1]*p[1] for p in matrix)
        b0=sum(p[0]*v for p,v in zip(matrix,z));b1=sum(p[1]*v for p,v in zip(matrix,z))
        det=g00*g11-g01*g01;assert g00>0 and det>0
        estimate=((g11*b0-g01*b1)/det,(g00*b1-g01*b0)/det)
        factor=1 if profile.startswith('L2') else 41
        error=factor*sum((a-b)**2 for a,b in zip(estimate,u))/(scale*scale)
        published=Q(row['source_relative_error_squared_upper'])
        accuracy=Q(13,10000) if profile=='L2_original_noise' else Q(1,1000)
        assert Q(row['source_relative_accuracy'])==accuracy
        assert error<=published<accuracy*accuracy
        assert row['unique_recovered_label']==label
        max_error=max(max_error,published)
    assert seen==expected and doc['case_count']==len(seen)==72 and doc['bank_profiles']==8
    assert max_error==Q(doc['maximum_source_relative_error_squared_upper'])
    return {'verified':True,'independently_scanned_raw_cases':len(seen),'bank_profiles':len(PROFILES),
            'exact_raw_reconstructions':len(seen),'independent_quartic_packets':len(seen),
            'independent_least_squares_error_enclosures':len(seen),
            'maximum_sensor_budget_fraction':str(max_sensor_fraction),
            'maximum_normalization_relative_charge':str(max_charge),
            'maximum_source_relative_error_squared_upper':str(max_error),
            'premise':'previously proved full finite-model operator error and spatial floors; this scan reruns no expensive model reconstruction'}


if __name__=='__main__':print(json.dumps(run(),indent=2))
