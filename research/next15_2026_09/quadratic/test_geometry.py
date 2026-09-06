from copy import deepcopy
from fractions import Fraction as F
from itertools import product,combinations
from pathlib import Path
import json
import unittest
import geometry as g


def alternate_prefix(signs):
    # Independent divisor-sum character expansion, rather than local products.
    def character(n):
        value=1
        for p in g.PRIMES:
            while n%p==0:n//=p;value*=signs[p]
        if n!=1:raise AssertionError('factor cover')
        return value
    return [sum(character(d) for d in range(1,n+1) if n%d==0) for n in range(1,51)]


class GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.doc=json.loads((Path(__file__).parent/'geometry.json').read_text())

    def test_all_81_small_prime_patterns_and_exact_pair_distances(self):
        vectors=[]
        for xs in product((-1,0,1),repeat=4):
            signs={p:-1 for p in g.PRIMES};signs.update(dict(zip((2,3,5,7),xs)))
            a=alternate_prefix(signs);self.assertEqual(a,g.prefix(signs));vectors.append(a)
        mins={key:None for key in ('0-1','1-2','0-2')}
        for a,b in combinations(vectors,2):
            if a[4]==b[4]:continue
            key='-'.join(map(str,sorted((a[4],b[4]))))
            d=sum((F((x-y)**2,n**4) for n,(x,y) in enumerate(zip(a,b),1)),F())
            if mins[key] is None or d<mins[key]:mins[key]=d
        self.assertEqual(mins,{k:F(v) for k,v in g.distances().items()})

    def test_actual_field_witnesses_with_independent_coefficients(self):
        self.assertTrue(g.check(self.doc)['verified'])
        for w in self.doc['witnesses']:
            signs={p:g.symbol(w['D'],p) for p in g.PRIMES}
            self.assertEqual(w['prefix'],alternate_prefix(signs))

    def test_forged_primes_prefixes_and_metric_rejected(self):
        for mutation in ('base','factor','D','prefix','radius'):
            d=deepcopy(self.doc);w=d['witnesses'][0]
            if mutation=='base':d['prime_proofs'][str(w['q'])]['base']=1
            elif mutation=='factor':d['prime_proofs'][str(w['q'])]['factors'][0][1]+=1
            elif mutation=='D':w['D']+=8
            elif mutation=='prefix':w['prefix'][19]+=1
            else:d['universal_radius_squared']='1/100'
            with self.assertRaises(ValueError):g.check(d)

    def test_midpoint_and_nonzero_anchor_obstruction(self):
        left,right=self.doc['witnesses'][:2]
        mid=[F(a+b,2*n*n) for n,(a,b) in enumerate(zip(left['prefix'],right['prefix']),1)]
        for w in (left,right):
            d=sum((abs(F(a,n*n)-z)**2 for n,(a,z) in enumerate(zip(w['prefix'],mid),1)),F())
            self.assertEqual(d,g.J/4)
        self.assertTrue(all(F(x)<F(1,81) for x in g.distances().values()))


if __name__=='__main__':unittest.main(verbosity=2)
