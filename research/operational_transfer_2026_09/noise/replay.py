"""Replay saved exact proposals against freshly reconstructed physical data.

At 320 bits, verify both residual identities and all coefficient gates. Rebuild
the synthetic observations independently of their saved integer truth fields.
No saved Gram matrix, saved residual, or solver invocation certifies itself.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, json
from physical import PhysicalModel, digest_pairs, parse_pairs, M
from certify import verify
from demo import fixture, ETA, NU

HERE=Path(__file__).resolve().parent


def replay(write=False):
    data={name:json.loads((HERE/('data_'+name+'.json')).read_text()) for name in ('moderate','large')}
    checks=[];model=PhysicalModel('multi',8,320)
    for name,amp,slow in [('moderate',10**6,False),('large',10**20,True)]:
        fresh=fixture(model,amp,slow)
        assert fresh['readings']==data[name]['readings']
        assert fresh['truth_a1_through_a50']==data[name]['truth_a1_through_a50']
        assert fresh['finite_source_coefficients']==data[name]['finite_source_coefficients']
        assert fresh['data_sha256']==data[name]['data_sha256']
        assert Q(fresh['nonpolynomial_remainder_pointwise_upper'])<=NU
        assert Q(fresh['quantization_norm_upper'])<Q(1,10**35)
    for design in ('multi','outer'):
        if design=='outer':model=PhysicalModel(design,8,320)
        for name in data:
            key=design+'_'+name;saved=json.loads((HERE/('result_'+key+'.json')).read_text())
            cert=saved['certificate'];pairs=data[name]['readings'];proposal=saved['proposal']
            assert cert['data_sha256']==digest_pairs(parse_pairs(pairs,M))
            assert cert['proposal_sha256']==digest_pairs(parse_pairs(proposal,58))
            assert (cert['design'],cert['degree'],cert['sensor_radius'],cert['nonpolynomial_drift_radius'])==(design,8,str(ETA),str(NU))
            checked=verify(model,pairs,proposal,ETA,NU,True)
            assert checked['status']=='certified_under_declared_model'
            assert checked['answer_a1_through_a50']==data[name]['truth_a1_through_a50']==cert['answer_a1_through_a50']
            assert Q(checked['normal_residual_upper'])<=Q(cert['normal_residual_upper'])
            checks.append({'case':key,'normal_residual_upper_at_320_bits':checked['normal_residual_upper'],
                           'saved_residual_bound_verified':True,'both_residual_identities_checked':True,
                           'all_49_answers_verified':True,'data_reconstructed_at_320_bits':True})
    result={'verified':True,'physical_readings_per_dataset':M,'working_precision_bits':320,'cases':checks}
    if write:(HERE/'replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();replay(args.write)
