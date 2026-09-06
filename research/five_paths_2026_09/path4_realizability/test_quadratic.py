"""Exact arithmetic controls independent of the residue-to-prefix producer."""
from itertools import product
from math import gcd,isqrt
from pathlib import Path
from fractions import Fraction as Q
import json
import unittest
import quadratic as q


def trial_factors(n):
    out=[];p=2
    while p*p<=n:
        e=0
        while n%p==0:n//=p;e+=1
        if e:out.append((p,e))
        p+=1
    if n>1:out.append((n,1))
    return out


def polynomial_symbol(d,p):
    D=d if d%4==1 else 4*d
    if D%p==0:return 0
    # Full integral basis polynomial, rather than Legendre exponentiation.
    roots=sum(((x*x-x+(1-d)//4) if d%4==1 else (x*x-d))%p==0 for x in range(p))
    if roots not in (0,2):raise AssertionError('unramified quadratic root count')
    return roots-1


def independent_prefix(d,N):
    out=[]
    for n in range(1,N+1):
        value=1
        for p,e in trial_factors(n):
            s=polynomial_symbol(d,p)
            value*=e+1 if s==1 else (1 if s==0 or e%2==0 else 0)
        out.append(value)
    return out


class QuadraticControls(unittest.TestCase):
    def test_all_81_local_patterns_and_fresh_fields(self):
        for xs in product((-1,0,1),repeat=4):
            signs=dict(zip((2,3,5,7),xs));w=q.realize(signs)
            self.assertEqual(gcd(w['residue'],w['modulus']),1)
            self.assertEqual(w['q']%w['modulus'],w['residue'])
            self.assertEqual(trial_factors(w['q']),[(w['q'],1)])
            self.assertTrue(all(e==1 for _,e in trial_factors(w['d'])))
            self.assertEqual([polynomial_symbol(w['d'],p) for p in signs],list(xs))
            prefix=independent_prefix(w['d'],10)
            self.assertTrue(q.valid_prefix(prefix))
            w2=q.realize(signs,minimum_q=w['q'])
            self.assertNotEqual(w['d'],w2['d'])
            self.assertEqual(prefix,independent_prefix(w2['d'],10))

    def test_stored_witnesses_and_arithmetic_constraints(self):
        rows=json.loads((Path(__file__).parent/'quadratic_examples.json').read_text())
        self.assertEqual(len(rows),27)
        for row in rows:
            a=independent_prefix(row['d'],50)
            self.assertTrue(q.valid_prefix(a))
            self.assertEqual(a[19],a[3]*a[4]);self.assertEqual(a[44],a[8]*a[4])
            changed=a.copy();changed[4]=(a[4]+1)%3
            self.assertFalse(q.valid_prefix(changed))
            for index in (0,3,5,8,19):
                bad=a.copy();bad[index]+=1
                self.assertFalse(q.valid_prefix(bad))

    def test_prime2_and_ramification_boundary(self):
        for d in (2,3,5,13,17,30,453,3165,381):
            for p in (2,3,5,7,11):
                self.assertEqual(q.chi(d,p),polynomial_symbol(d,p))

    def test_prefix_domain_and_bad_primes(self):
        for bad in ([],[0],[1,3],[1,-1],[1,1.0],[1,1,1,0]):
            self.assertFalse(q.valid_prefix(bad))
        self.assertTrue(q.valid_prefix([1]))
        for signs in ({4:1},{2:2},{1:-1}):
            with self.assertRaises(ValueError):q.realize(signs)

    def test_integral_convex_gap_exact_midpoint(self):
        sets=({Q(0),Q(2)},{Q(1),Q(3)})
        self.assertEqual(min(abs(x-y) for x in sets[0] for y in sets[1]),1)
        z=Q(1,2)
        self.assertEqual(abs(z-0),Q(1,2));self.assertEqual(abs(z-1),Q(1,2))
        self.assertTrue(0<=Q(3,2)<=2 and 1<=Q(3,2)<=3)

    def test_refinement_enclosures_and_every_query(self):
        root=Path(__file__).parent
        a=json.loads((root/'certificate.json').read_text());b=json.loads((root/'refinement.json').read_text())
        for key in ('finite_d2_tail_upper','gram_row_upper'):
            self.assertEqual(len(a[key]),50)
            self.assertTrue(all(Q(y)<=Q(x) for x,y in zip(a[key],b[key])))
        for doc in (a,b):
            c=doc['consequence'];eta=Q(c['declared_eta'])
            self.assertGreater(eta,Q(1,50));self.assertTrue(c['all_pass'])
            self.assertEqual({(r['a4'],r['a9']) for r in c['query_cases']},{(1,1),(1,3),(3,1),(3,3)})
            self.assertTrue(all(eta**2<Q(r['admissible_radius_squared']) for r in c['query_cases']))


if __name__=='__main__':unittest.main(verbosity=2)
