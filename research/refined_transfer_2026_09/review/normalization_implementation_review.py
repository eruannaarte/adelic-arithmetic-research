"""Independent adversarial checks of the delivered normalization interface."""
import copy
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_review_normalization',HERE.parent/'normalization/normalize.py')
normalizer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def rejected(operation):
    try:operation()
    except (ValueError,TypeError,KeyError,ZeroDivisionError):return
    raise AssertionError('invalid operation was accepted')


def run():
    eta=Q(3,10**7);xi=Q(1,10**9)
    cases=0
    for t in (Q(1),Q(5,4),Q(3,2),Q(369,256),Q(2)):
        reference=normalizer.normalize([1,-2,4],t,eta,xi)
        charge=normalizer.verify_packet([1,-2,4],reference)
        r=Q(reference['scale']['inverse_normalization'])
        error=Q(reference['scale']['relative_multiplier_error_upper'])
        assert 0<=charge<=xi
        assert (1-error)**4 <= (1+t)*r**4 <= (1+error)**4
        for amplitude in (Q(1,10**100),Q(1),Q(10**100)):
            raw=[amplitude,-2*amplitude,4*amplitude]
            packet=normalizer.normalize(raw,t,eta,xi)
            assert normalizer.verify_packet(raw,packet)==charge
            assert list(map(Q,packet['normalized_data']))==[amplitude*Q(v) for v in reference['normalized_data']]
            cases+=1

    packet=normalizer.normalize([1,-2,4],Q(3,2),eta,xi)
    mutations={
        'negative_multiplier':('inverse_normalization',str(-Q(packet['scale']['inverse_normalization']))),
        'underreported_charge':('charged_physical_relative_radius',str(Q(packet['scale']['charged_physical_relative_radius'])/2)),
        'wrong_gain':('measured_output_gain_upper','4/3'),
        'negative_sensor':('sensor_relative_radius','-1/10'),
        'zero_budget_with_nonzero_error':('numerical_relative_budget','0'),
        'invalid_relative_error':('relative_multiplier_error_upper','1'),
        'time_outside_model':('time','3'),
        'rational_type_confusion':('inverse_normalization',1),
    }
    for label,(key,value) in mutations.items():
        altered=copy.deepcopy(packet);altered['scale'][key]=value
        rejected(lambda p=altered:normalizer.verify_packet([1,-2,4],p))
    altered=copy.deepcopy(packet)
    altered['normalized_data'][0]=str(Q(altered['normalized_data'][0])+Q(1,10**100))
    # Even rebinding the output hash cannot bless an incorrect exact scaling.
    altered['normalized_data_sha256']=normalizer.digest(tuple(map(Q,altered['normalized_data'])))
    rejected(lambda:normalizer.verify_packet([1,-2,4],altered))
    rejected(lambda:normalizer.verify_packet([1,-2,5],packet))
    rejected(lambda:normalizer.normalize([0,0],1,eta,xi))
    rejected(lambda:normalizer.normalize([1.0],1,eta,xi))
    rejected(lambda:normalizer.normalize([True],1,eta,xi))
    rejected(lambda:normalizer.make_scale(1,eta,0))
    rejected(lambda:normalizer.make_scale(1,eta,xi,max_refinements=0))
    exact=normalizer.make_scale(Q(369,256),eta,0)
    assert Q(exact['inverse_normalization'])==Q(4,5)
    assert normalizer.verify_scale(exact)==0
    # Explicit physical error at a rational normalization, checked without
    # quartic comparison or a root approximation.
    alpha=Q(5,4)
    a=normalizer.normalize([Q(5,4),-Q(5,2)],Q(369,256),eta,xi)
    assert [alpha*Q(v)-y for v,y in zip(a['normalized_data'],[Q(5,4),-Q(5,2)])]==[0,0]
    return {'verified':True,'homogeneous_raw_data_cases':cases,
            'receipt_corruptions_rejected':len(mutations),
            'additional_data_domain_and_budget_rejections':7,
            'exact_rational_root_and_zero_budget_verified':True,
            'interface_scope':'scale and packet verifier; bank-specific decoding is checked by the main tests'}


if __name__=='__main__':print(json.dumps(run(),indent=2))
