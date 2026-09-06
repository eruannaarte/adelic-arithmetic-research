from copy import deepcopy
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from math import isqrt
import json
import unittest
import infinite_geometry as q


def value(signs,n):
    out=1;p=2
    while p*p<=n:
        e=0
        while n%p==0:n//=p;e+=1
        if e:out*=sum(signs.get(p,-1)**k for k in range(e+1))
        p+=1
    if n>1:out*=1+signs.get(n,-1)
    return out


class InfiniteTests(unittest.TestCase):
    def test_independent_positive_series_and_sqrt_bounds(self):
        doc=json.loads((Path(__file__).parent/'infinite_geometry.json').read_text())
        self.assertTrue(q.check(doc)['verified'])
        partial=sum((F(1,n**8) for n in range(1,201)),F())
        lo,hi=map(F,doc['zeta8_interval'])
        self.assertLess(lo,partial);self.assertLess(partial+F(1,7*200**7),hi)
        a,b=map(F,doc['critical_closed_radius_interval'])
        self.assertLessEqual(a*a,lo/2500);self.assertGreaterEqual(b*b,hi/2500)

    def test_odd_square_local_parity_and_formal_difference(self):
        for xs in product((-1,0,1),repeat=3):
            signs=dict(zip((2,3,7),xs))
            for m in (1,2,3,6,7,14,21,42):
                self.assertEqual(value(signs,m*m)%2,1)
                for h in range(3):
                    n=5**(2*h+1)*m*m
                    vals=[value({**signs,5:s},n) for s in (-1,0,1)]
                    self.assertEqual(vals[0],0);self.assertEqual(vals[1]%2,1);self.assertEqual(vals[2]%2,0)
        for n in range(1,501):
            m=n;v=0
            while m%5==0:m//=5;v+=1
            indicator=int(v%2==1 and isqrt(m)**2==m)
            self.assertEqual(value({5:0},n)-value({5:-1},n),indicator)

    def test_elementary_split_prime_for_actual_squarefree_radicands(self):
        for d in range(2,101):
            if any(d%(p*p)==0 for p in range(2,isqrt(d)+1)):continue
            z=100*d-1;p=next((p for p in range(2,isqrt(z)+1) if z%p==0),z)
            self.assertNotEqual(p,2);self.assertNotEqual(p,5);self.assertNotEqual(d%p,0)
            self.assertEqual((10*d)**2%p,d%p)
            self.assertEqual(pow(d%p,(p-1)//2,p),1)

    def test_false_endpoint_topology_and_tail_rejected(self):
        original=q.build()
        for field,val in [('infimum_attained_by_field_pair',True),('query_uniqueness_at_critical_closed_radius',False),('distance_squared_infimum','zeta(8)/626')]:
            d=deepcopy(original);d[field]=val
            with self.assertRaises(ValueError):q.check(d)
        d=deepcopy(original);d['approximating_actual_field_pairs'][0]['distance_squared_excess_upper']='0'
        with self.assertRaises(ValueError):q.check(d)


if __name__=='__main__':unittest.main(verbosity=2)
