#!/usr/bin/env python3
from pathlib import Path
from fractions import Fraction as F
import json
from check_certificate import interval,raw_remainder,symmetric_error_box,norm_upper_valid,METRICS
HERE=Path(__file__).parent
base=json.loads((HERE/'cell_1_1p5.json').read_text())
ref=json.loads((HERE/'refinement_cell_1_1p5.json').read_text())
checks=0
for m in METRICS:
    b=base['metrics'][m];r=ref['metrics'][m]
    for i in range(3):
        for k in range(base['order']+1):
            x=interval(b['difference_coefficients'][i][k]);y=interval(r['difference_coefficients'][i][k])
            assert max(x[0],y[0])<=min(x[1],y[1]),(m,i,k,'nonoverlap')
            checks+=1
    errors=symmetric_error_box(r,ref)
    assert norm_upper_valid(errors,F(r['spectral_error_upper']))
    assert F(r['spectral_error_upper'])<=F(b['spectral_error_upper'])
summary={'status':'PASS','base_precision_bits':base['precision_bits'],'refinement_precision_bits':ref['precision_bits'],'base_order':base['order'],'refinement_order':ref['order'],'base_exponential_degree':base['exponential_degree'],'refinement_exponential_degree':ref['exponential_degree'],'coefficient_intersections_checked':checks,'metric_bounds_improved':True,'meaning':'independent precision/order/degree replay is consistent; it is not a differential implementation of Arb'}
(HERE/'refinement_validation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
