#!/usr/bin/env python3
"""Fresh Arb common-core floor reconstruction, separate from cover generation."""
import json,sys,time
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from flint import arb,ctx
from oig_x_spectral_certificate import _common_core_entry
from oig_xi_transfer_certificate import STAGE_X_LOWER_BOUNDS
from generate_certificate import text_box
from check_certificate import interval,qtext,scale,plus,absmax

ctx.prec=256
H=[_common_core_entry(i,j,F(7,4),256) for i,j in [(1,1),(1,2),(2,2)]]
rows={}
for metric,s in [('L2',[arb(1),arb(1)]),('H1',[1+arb.pi()**2,1+4*arb.pi()**2])]:
    floor=STAGE_X_LOWER_BOUNDS[metric][1]
    from oig_uniform_lattice_arb_cover import _q
    a=H[0]-_q(floor)*s[0];b=H[1];d=H[2]-_q(floor)*s[1]
    assert a>0 and d>0 and a*d-b*b>0
    A,B,D=map(interval,[text_box(a),text_box(b),text_box(d)])
    assert A[0]>0 and D[0]>0 and A[0]*D[0]>absmax(B)**2
    rows[metric]={'floor':qtext(floor),'shift_entries':[text_box(x) for x in (a,b,d)],'strict_principal_minor_lower':qtext(A[0]*D[0]-absmax(B)**2)}
result={'status':'fresh 256-bit Arb common-core floor certification','cutoff':'7/4','core':'sqrt(2) exp(-7/4) H_(7/4)','core_entries':[text_box(x) for x in H],'metrics':rows,'scope':'uniform continuum one-cell lattice tau>=1 by density domination; also inherited resolved/atomic core','normalization':'sqrt(1+tau)','proof':'APPENDIX.md, continuum-floor section'}
Path(__file__).with_name('baseline.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: fresh 256-bit quadrature and independent rational principal-minor checks certify both inherited K=2 floors.')
for m,r in rows.items():print(m,float(F(r['floor'])))
